"""Hybrid CNN + Transformer segmentation network for CarDD (ADR 0010).

CarddHybrid combines a convolutional encoder-decoder (good inductive bias,
local texture cues) with a compact self-attention bottleneck (global context,
long-range part-to-part relationship). The 512 x 512 input is downsampled to a
32 x 32 feature map, processed by two transformer encoder layers with fixed
sinusoidal position embeddings, then decoded back to full resolution with
learned transpose-convolutions and four skip connections. The output is a
7-channel logit map matching the CarDD class contract (background + 6 damage
classes).

The module keeps the CarddUNet constructor contract (``in_channels`` /
``num_classes`` / ``base``) so the training harness and inference engine can
dispatch on an ``model_arch`` checkpoint key without special-casing.

Run inside the `ai` conda environment.
"""

from __future__ import annotations

import math
from typing import cast

import torch
import torch.nn as nn
from torch import Tensor


class _DoubleConv(nn.Module):
    """(conv3x3 -> BN -> ReLU) x2."""

    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: Tensor) -> Tensor:
        return cast(Tensor, self.block(x))


def _fourier_pos(seq_len: int, d_model: int) -> Tensor:
    """Fixed sinusoidal position embeddings (PreNet-style, non-learned)."""
    positions = torch.arange(seq_len, dtype=torch.float32).unsqueeze(1)
    div = torch.exp(
        torch.arange(0, d_model, 2, dtype=torch.float32) * (-math.log(10_000.0) / d_model)
    )
    pos = torch.zeros(seq_len, d_model, dtype=torch.float32)
    pos[:, 0::2] = torch.sin(positions * div)
    pos[:, 1::2] = torch.cos(positions * div)
    return pos


class CarddHybrid(nn.Module):
    """CNN encoder-decoder with a compact transformer bottleneck.

    Encoder stages halve the spatial size four times (512 -> 32). At the
    32 x 32 bottleneck a positional-encoded token sequence passes through two
    transformer encoder layers (d_model = 8*base, 4 heads), injecting global
    context before decoding. Each decoder level merges the matching encoder
    skip map before the next up-convolution. Parameters ~3.1 M for
    ``base=32`` (fits a 4 GB GPU during training at batch size 2, 512 x 512
    inputs).
    """

    def __init__(self, in_channels: int = 3, num_classes: int = 7, base: int = 32) -> None:
        super().__init__()
        hidden = base * 8  # bottleneck / transformer channel dim
        self.base = base
        self.num_classes = num_classes

        # Encoder: 512 -> 256 -> 128 -> 64 -> 32, four skip maps.
        self.enc1 = _DoubleConv(in_channels, base)
        self.enc2 = _DoubleConv(base, base * 2)
        self.enc3 = _DoubleConv(base * 2, base * 4)
        self.enc4 = _DoubleConv(base * 4, hidden)
        self.pool = nn.MaxPool2d(2)

        # Transformer bottleneck: (B, H*W, hidden) tokens, sinusoidal pos.
        layer = nn.TransformerEncoderLayer(
            d_model=hidden,
            nhead=4,
            dim_feedforward=hidden * 2,
            dropout=0.1,
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(layer, num_layers=2)

        # Decoder: 32 -> 64 -> 128 -> 256 -> 512, skipping each encoder level.
        self.up4 = nn.ConvTranspose2d(hidden, base * 4, kernel_size=2, stride=2)
        self.up3 = nn.ConvTranspose2d(base * 4, base * 2, kernel_size=2, stride=2)
        self.up2 = nn.ConvTranspose2d(base * 2, base, kernel_size=2, stride=2)
        self.up1 = nn.ConvTranspose2d(base, base, kernel_size=2, stride=2)
        self.dec4 = _DoubleConv(base * 4 + hidden, base * 4)
        self.dec3 = _DoubleConv(base * 2 + base * 4, base * 2)
        self.dec2 = _DoubleConv(base + base * 2, base)
        self.dec1 = _DoubleConv(base * 2, base)
        self.out_conv = nn.Conv2d(base, num_classes, kernel_size=1)

    def forward(self, x: Tensor) -> Tensor:
        enc1 = self.enc1(x)
        enc2 = self.enc2(self.pool(enc1))
        enc3 = self.enc3(self.pool(enc2))
        enc4 = self.enc4(self.pool(enc3))
        bottleneck = self.pool(enc4)

        batch, channels, height, width = bottleneck.shape
        tokens = bottleneck.flatten(2).transpose(1, 2)  # (B, H*W, C)
        pos = _fourier_pos(tokens.shape[1], channels).to(tokens.device)
        context = self.transformer(tokens + pos)  # global-context tokens
        bottleneck = context.transpose(1, 2).reshape(batch, channels, height, width)

        x = self.up4(bottleneck)
        x = torch.cat([x, enc4], dim=1)
        x = self.dec4(x)
        x = self.up3(x)
        x = torch.cat([x, enc3], dim=1)
        x = self.dec3(x)
        x = self.up2(x)
        x = torch.cat([x, enc2], dim=1)
        x = self.dec2(x)
        x = self.up1(x)
        x = torch.cat([x, enc1], dim=1)
        x = self.dec1(x)

        return cast(Tensor, self.out_conv(x))
