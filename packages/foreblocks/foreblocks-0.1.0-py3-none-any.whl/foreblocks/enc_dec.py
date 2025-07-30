from typing import Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor


class EncoderBase(nn.Module):
    def __init__(self):
        super(EncoderBase, self).__init__()

    def forward(self, x, hidden=None):
        raise NotImplementedError("Subclasses must implement forward method")


class DecoderBase(nn.Module):
    def __init__(self):
        super(DecoderBase, self).__init__()

    def forward(self, x, hidden=None):
        raise NotImplementedError("Subclasses must implement forward method")


################################################
# LSTM
################################################


class LSTMEncoder(EncoderBase):
    def __init__(
        self, input_size, hidden_size, num_layers=1, dropout=0.0, bidirectional=False
    ):
        super(LSTMEncoder, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
            batch_first=True,
        )

    def forward(
        self, x: Tensor, hidden: Optional[Tuple[Tensor, Tensor]] = None
    ) -> Tuple[Tensor, Tuple[Tensor, Tensor]]:
        outputs, hidden = self.lstm(x, hidden)
        return outputs, hidden


class LSTMDecoder(DecoderBase):
    def __init__(self, input_size, hidden_size, output_size, num_layers=1, dropout=0.0):
        super(LSTMDecoder, self).__init__()
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
        )
        self.output_layer = nn.Linear(hidden_size, output_size)

    def forward(
        self, x: torch.Tensor, hidden: Optional[Tuple[Tensor, Tensor]] = None
    ) -> Tuple[Tensor, Tuple[Tensor, Tensor]]:
        if x.dim() == 2:
            x = x.unsqueeze(1)
        lstm_out, hidden = self.lstm(x, hidden)
        output = self.output_layer(lstm_out.squeeze(1))
        return output, hidden


###################################################
# GRU
###################################################


class GRUEncoder(EncoderBase):
    def __init__(
        self, input_size, hidden_size, num_layers=1, dropout=0.0, bidirectional=False
    ):
        super(GRUEncoder, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
            batch_first=True,
        )

    def forward(self, x, hidden=None):
        outputs, hidden = self.gru(x, hidden)
        return outputs, hidden


class GRUDecoder(DecoderBase):
    def __init__(self, input_size, hidden_size, output_size, num_layers=1, dropout=0.0):
        super(GRUDecoder, self).__init__()
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.num_layers = num_layers
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
        )
        self.output_layer = nn.Linear(hidden_size, output_size)

    def forward(self, x, hidden=None):
        if x.dim() == 2:
            x = x.unsqueeze(1)
        gru_out, hidden = self.gru(x, hidden)
        output = self.output_layer(gru_out.squeeze(1))
        return output, hidden


###############


# === Variational Encoder Wrapper ===
class VariationalEncoderWrapper(nn.Module):
    def __init__(self, base_encoder: nn.Module, latent_dim: int):
        super().__init__()
        self.base_encoder = base_encoder
        self.latent_dim = latent_dim
        self.hidden_size = base_encoder.hidden_size

        # Properly registered projection layers
        self.hidden_to_mu = nn.Linear(self.hidden_size, latent_dim)
        self.hidden_to_logvar = nn.Linear(self.hidden_size, latent_dim)

    def forward(self, x):
        encoder_outputs, encoder_hidden = self.base_encoder(x)

        # Works for LSTM (tuple) and GRU (tensor)
        if isinstance(encoder_hidden, tuple):
            h = encoder_hidden[0][-1]  # Last layer's hidden state
        else:
            h = encoder_hidden[-1]

        mu = self.hidden_to_mu(h)
        logvar = self.hidden_to_logvar(h)
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        z = mu + eps * std  # Reparameterization trick

        return encoder_outputs, (z, mu, logvar)


# === Latent-aware Decoder Wrapper ===
class LatentConditionedDecoder(nn.Module):
    def __init__(
        self,
        base_decoder: nn.Module,
        latent_dim: int,
        hidden_size: int,
        num_layers: int = 1,
        rnn_type="lstm",
    ):
        super().__init__()
        self.base_decoder = base_decoder
        self.latent_to_hidden = nn.Linear(latent_dim, hidden_size * num_layers)
        self.latent_to_cell = (
            nn.Linear(latent_dim, hidden_size * num_layers)
            if rnn_type == "lstm"
            else None
        )

        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = base_decoder.output_size
        self.rnn_type = rnn_type.lower()

    def forward(self, x, latent):
        if latent.dim() == 3 and latent.size(0) == self.num_layers:
            latent = latent[-1]

        batch_size = latent.size(0)
        h0 = self.latent_to_hidden(latent).view(
            self.num_layers, batch_size, self.hidden_size
        )

        if self.rnn_type == "lstm":
            c0 = self.latent_to_cell(latent).view(
                self.num_layers, batch_size, self.hidden_size
            )
            return self.base_decoder(x, (h0, c0))
        else:
            return self.base_decoder(x, h0)


def compute_kl_divergence(mu, logvar):
    """
    KL divergence between N(mu, sigma^2) and N(0,1)
    """
    return -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp()) / mu.size(0)


def vae_loss_function(recon_x, target, mu, logvar):
    """
    VAE loss = reconstruction loss + KL divergence
    """
    recon_loss = F.mse_loss(recon_x, target, reduction="mean")
    kl = compute_kl_divergence(mu, logvar)
    return recon_loss + kl, recon_loss, kl
