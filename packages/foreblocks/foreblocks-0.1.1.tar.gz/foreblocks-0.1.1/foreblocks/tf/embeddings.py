import math
from typing import Any, Dict, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


class PositionalEncoding(nn.Module):
    """
    Optimized positional encoding with support for:
    - Standard sinusoidal encoding
    - Scaled injection
    - Dynamic dimension handling
    """

    def __init__(
        self,
        d_model: int,
        dropout: float = 0.1,
        max_len: int = 10000,
        scale: float = 1.0,
    ):
        super().__init__()
        self.d_model = d_model
        self.scale = scale
        self.max_len = max_len

        # Use nn.Dropout with inplace for memory efficiency
        self.dropout = nn.Dropout(p=dropout, inplace=True) if dropout > 0 else None

        # Precompute sinusoidal encoding with better numerical stability
        self._build_pe_cache(d_model, max_len)

        # Cache for dynamic dimensions
        self._pe_cache: Dict[int, torch.Tensor] = {}

    def _build_pe_cache(self, d_model: int, max_len: int):
        """Build positional encoding cache with optimized computation"""
        # Use log-space computation for better numerical stability
        position = torch.arange(max_len, dtype=torch.float32).unsqueeze(1)

        # Optimized div_term computation
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float32)
            * (-math.log(10000.0) / d_model)
        )

        # Pre-allocate with correct size
        sinusoid = torch.empty(max_len, d_model, dtype=torch.float32)

        # Vectorized sine/cosine computation
        angles = position * div_term
        sinusoid[:, 0::2] = torch.sin(angles)
        if d_model % 2 == 1:
            # Handle odd dimensions
            sinusoid[:, 1::2] = torch.cos(angles[:, :-1])
            sinusoid[:, -1] = 0  # Set last dimension to 0 for odd d_model
        else:
            sinusoid[:, 1::2] = torch.cos(angles)

        self.register_buffer("pe", sinusoid.unsqueeze(0), persistent=False)

    def _create_pe_for_dim(
        self, d_model: int, seq_len: int, device: torch.device
    ) -> torch.Tensor:
        """Create PE for different dimensions with caching"""
        cache_key = d_model

        if cache_key not in self._pe_cache:
            # Create PE for this dimension
            position = torch.arange(
                seq_len, dtype=torch.float32, device=device
            ).unsqueeze(1)
            div_term = torch.exp(
                torch.arange(0, d_model, 2, dtype=torch.float32, device=device)
                * (-math.log(10000.0) / d_model)
            )

            pe = torch.empty(seq_len, d_model, dtype=torch.float32, device=device)
            angles = position * div_term
            pe[:, 0::2] = torch.sin(angles)

            if d_model % 2 == 1:
                pe[:, 1::2] = torch.cos(angles[:, :-1])
                pe[:, -1] = 0
            else:
                pe[:, 1::2] = torch.cos(angles)

            # Cache only if reasonable size
            if d_model <= 2048:  # Prevent memory explosion
                self._pe_cache[cache_key] = pe.unsqueeze(0)

            return pe.unsqueeze(0)

        cached_pe = self._pe_cache[cache_key]
        if cached_pe.size(1) >= seq_len:
            return cached_pe[:, :seq_len]
        else:
            # Need to extend cache
            return self._create_pe_for_dim(d_model, seq_len, device)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Optimized forward with minimal overhead"""
        B, T, D = x.shape

        if D == self.d_model and T <= self.max_len:
            # Fast path: use pre-computed PE
            pe = self.pe[:, :T]
        else:
            # Slow path: create PE on-demand
            pe = self._create_pe_for_dim(D, T, x.device)

        # Use fused operation
        x = x.add_(pe, alpha=self.scale)  # In-place addition with scaling

        return self.dropout(x) if self.dropout is not None else x


class InformerTimeEmbedding(nn.Module):
    """Optimized time embedding with better memory efficiency"""

    def __init__(self, d_model: int):
        super().__init__()
        self.d_model = d_model

        # Use smaller embedding dimensions and project up
        embed_dim = min(d_model // 4, 64)  # Adaptive embedding size

        self.hour_embed = nn.Embedding(24, embed_dim)
        self.weekday_embed = nn.Embedding(7, embed_dim)
        self.day_embed = nn.Embedding(32, embed_dim)
        self.month_embed = nn.Embedding(13, embed_dim)

        # Project to full dimension if needed
        if embed_dim * 4 != d_model:
            self.projection = nn.Linear(embed_dim * 4, d_model)
        else:
            self.projection = None

        # Normalization factor
        self.norm_factor = 1.0 / math.sqrt(4.0)  # Pre-compute for efficiency

        # Initialize embeddings
        self._init_embeddings()

    def _init_embeddings(self):
        """Better initialization for time embeddings"""
        for embed in [
            self.hour_embed,
            self.weekday_embed,
            self.day_embed,
            self.month_embed,
        ]:
            nn.init.normal_(embed.weight, mean=0, std=0.02)

    def forward(self, time_feats: torch.Tensor) -> torch.Tensor:
        """
        Optimized forward with vectorized operations
        time_feats: [B, T, 4] - month, weekday, hour, day
        """
        # Clamp inputs to valid ranges (safety check)
        month = torch.clamp(time_feats[:, :, 0].long(), 0, 12)
        weekday = torch.clamp(time_feats[:, :, 1].long(), 0, 6)
        hour = torch.clamp(time_feats[:, :, 2].long(), 0, 23)
        day = torch.clamp(time_feats[:, :, 3].long(), 0, 31)

        # Vectorized embedding lookup
        month_emb = self.month_embed(month)
        weekday_emb = self.weekday_embed(weekday)
        hour_emb = self.hour_embed(hour)
        day_emb = self.day_embed(day)

        # Concatenate embeddings
        embs = torch.cat([month_emb, weekday_emb, hour_emb, day_emb], dim=-1)

        # Project to target dimension if needed
        if self.projection is not None:
            embs = self.projection(embs)

        # Apply normalization
        return embs * self.norm_factor


class LearnablePositionalEncoding(nn.Module):
    def __init__(
        self,
        d_model: int,
        max_len: int = 5000,
        dropout: float = 0.1,
        initialization: str = "normal",
        scale_strategy: str = "fixed",  # ["fixed", "learnable", "none"]
        scale_value: Optional[float] = None,
        use_layer_norm: bool = True,
        norm_strategy: str = "pre_add",  # or "post_add"
        low_rank_dim: Optional[int] = None,
    ):
        super().__init__()
        self.d_model = d_model
        self.max_len = max_len
        self.low_rank_dim = low_rank_dim
        self.norm_strategy = norm_strategy

        # Learnable PE
        if low_rank_dim is None:
            self.pe = nn.Parameter(self._init_pe(initialization, (1, max_len, d_model)))
        else:
            self.pe_proj_U = nn.Parameter(
                self._init_pe(initialization, (1, max_len, low_rank_dim))
            )
            self.pe_proj_V = nn.Parameter(
                self._init_pe(initialization, (1, low_rank_dim, d_model))
            )

        if scale_strategy == "learnable":
            self.scale = nn.Parameter(torch.tensor(scale_value or 1.0))
        elif scale_strategy == "fixed":
            self.scale = scale_value or math.sqrt(d_model)
        else:
            self.scale = 1.0

        self.dropout = nn.Dropout(dropout) if dropout > 0 else None
        self.layer_norm = nn.LayerNorm(d_model) if use_layer_norm else None

    def _init_pe(self, mode, shape):
        if mode == "normal":
            return torch.randn(shape) * math.sqrt(2.0 / shape[-1])
        elif mode == "uniform":
            bound = math.sqrt(6.0 / shape[-1])
            return torch.empty(shape).uniform_(-bound, bound)
        elif mode == "zero":
            return torch.zeros(shape)
        else:
            return torch.randn(shape) * 0.02

    def forward(self, x, positions: Optional[torch.Tensor] = None):
        B, T, _ = x.shape

        if self.low_rank_dim is None:
            pe = (
                self.pe[:, :T]
                if positions is None
                else F.embedding(positions, self.pe.squeeze(0))
            )
        else:
            U = (
                self.pe_proj_U[:, :T]
                if positions is None
                else F.embedding(positions, self.pe_proj_U.squeeze(0))
            )
            pe = torch.bmm(
                U.expand(B, -1, -1), self.pe_proj_V.expand(B, -1, -1)
            )  # [B, T, d_model]

        if self.norm_strategy == "pre_add" and self.layer_norm:
            x = self.layer_norm(x)

        x = (
            x + pe * self.scale
            if isinstance(self.scale, torch.Tensor)
            else x + pe * self.scale
        )

        if self.norm_strategy == "post_add" and self.layer_norm:
            x = self.layer_norm(x)

        return self.dropout(x) if self.dropout else x


class RotaryEmbedding(nn.Module):
    """
    Optimized Rotary position embeddings (RoPE) with better caching.
    """

    def __init__(self, dim: int, base: int = 10000, max_seq_len: int = 8192):
        super().__init__()
        self.dim = dim
        self.base = base
        self.max_seq_len = max_seq_len

        # Pre-compute and cache frequencies for common sequence lengths
        self._precompute_freqs(max_seq_len)

    def _precompute_freqs(self, max_seq_len: int):
        """Pre-compute frequencies for better performance"""
        theta = 1.0 / (self.base ** (torch.arange(0, self.dim, 2) / self.dim))
        seq_idx = torch.arange(max_seq_len).float().unsqueeze(1)
        freqs = seq_idx * theta

        # Pre-compute cos and sin
        cos_freqs = freqs.cos()
        sin_freqs = freqs.sin()

        # Store as buffers for automatic device handling
        self.register_buffer("cos_cached", cos_freqs, persistent=False)
        self.register_buffer("sin_cached", sin_freqs, persistent=False)

    def _get_freqs(self, seq_len: int, device: torch.device):
        """Get frequencies with fallback for longer sequences"""
        if seq_len <= self.max_seq_len:
            return self.cos_cached[:seq_len], self.sin_cached[:seq_len]
        else:
            # Fallback for longer sequences
            theta = 1.0 / (
                self.base ** (torch.arange(0, self.dim, 2, device=device) / self.dim)
            )
            seq_idx = torch.arange(seq_len, device=device).float().unsqueeze(1)
            freqs = seq_idx * theta
            return freqs.cos(), freqs.sin()

    @staticmethod
    def apply_rotary_pos_emb(
        x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor
    ) -> torch.Tensor:
        """Optimized rotary embedding application"""
        # Reshape for broadcasting
        cos = cos.unsqueeze(0).unsqueeze(0)  # [1, 1, seq_len, dim/2]
        sin = sin.unsqueeze(0).unsqueeze(0)

        # Split into even and odd
        x1, x2 = x[..., 0::2], x[..., 1::2]

        # Apply rotation
        rotated_x1 = x1 * cos - x2 * sin
        rotated_x2 = x1 * sin + x2 * cos

        # Interleave back
        rotated_x = torch.empty_like(x)
        rotated_x[..., 0::2] = rotated_x1
        rotated_x[..., 1::2] = rotated_x2

        return rotated_x

    def forward(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        q_pos: Optional[torch.Tensor] = None,
        k_pos: Optional[torch.Tensor] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Optimized forward pass
        q, k: [batch, heads, seq_len, head_dim]
        """
        *_, q_len, head_dim = q.shape
        _, _, k_len, _ = k.shape

        # Only apply to rotary dimensions
        rotary_dim = min(head_dim, self.dim)

        if rotary_dim == head_dim:
            # Full rotation
            q_rot, k_rot = q, k
            q_pass = k_pass = None
        else:
            # Partial rotation
            q_rot, q_pass = q[..., :rotary_dim], q[..., rotary_dim:]
            k_rot, k_pass = k[..., :rotary_dim], k[..., rotary_dim:]

        # Get frequencies
        max_len = max(q_len, k_len)
        cos_freqs, sin_freqs = self._get_freqs(max_len, q.device)

        # Handle custom positions
        if q_pos is not None:
            q_cos = cos_freqs[q_pos]
            q_sin = sin_freqs[q_pos]
        else:
            q_cos = cos_freqs[:q_len]
            q_sin = sin_freqs[:q_len]

        if k_pos is not None:
            k_cos = cos_freqs[k_pos]
            k_sin = sin_freqs[k_pos]
        else:
            k_cos = cos_freqs[:k_len]
            k_sin = sin_freqs[:k_len]

        # Apply rotary embedding
        q_rot = self.apply_rotary_pos_emb(q_rot, q_cos, q_sin)
        k_rot = self.apply_rotary_pos_emb(k_rot, k_cos, k_sin)

        # Concatenate with non-rotated parts if needed
        if q_pass is not None:
            q_out = torch.cat([q_rot, q_pass], dim=-1)
            k_out = torch.cat([k_rot, k_pass], dim=-1)
        else:
            q_out, k_out = q_rot, k_rot

        return q_out, k_out

    def clear_cache(self):
        """Clear dynamic cache to free memory"""
        # Only persistent buffers remain
        pass
