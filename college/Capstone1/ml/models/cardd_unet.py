"""Small U-Net for CarDD damage segmentation (Phase 3, ADR 0006).

A deliberately small encoder-decoder so the ~4 GB RTX 3050 can run a smoke
training loop (Phase 3). This is a machinery-verification model, not the final
architecture; a later phase replaces it.

Run inside the `ai` conda environment.
"""

from __future__ import annotations

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


class CarddUNet(nn.Module):
    """Compact U-Net with one encoder/decoder level per scale.

    Parameters: ~2.9 M for base 64 (small enough for a 4 GB GPU smoke run).
    """

    def __init__(self, in_channels: int = 3, num_classes: int = 7, base: int = 64) -> None:
        super().__init__()
        self.base = base

        self.enc1 = _DoubleConv(in_channels, base)
        self.enc2 = _DoubleConv(base, base * 2)
        self.enc3 = _DoubleConv(base * 2, base * 4)
        self.pool = nn.MaxPool2d(2)
        self.bottleneck = _DoubleConv(base * 4, base * 8)

        self.up3 = nn.ConvTranspose2d(base * 8, base * 4, kernel_size=2, stride=2)
        self.dec3 = _DoubleConv(base * 8, base * 4)
        self.up2 = nn.ConvTranspose2d(base * 4, base * 2, kernel_size=2, stride=2)
        self.dec2 = _DoubleConv(base * 4, base * 2)
        self.up1 = nn.ConvTranspose2d(base * 2, base, kernel_size=2, stride=2)
        self.dec1 = _DoubleConv(base * 2, base)

        self.out_conv = nn.Conv2d(base, num_classes, kernel_size=1)

    def forward(self, x: Tensor) -> Tensor:
        enc1 = self.enc1(x)
        enc2 = self.enc2(self.pool(enc1))
        enc3 = self.enc3(self.pool(enc2))
        bottleneck = self.bottleneck(self.pool(enc3))

        x = self.up3(bottleneck)
        x = torch.cat([x, enc3], dim=1)
        x = self.dec3(x)
        x = self.up2(x)
        x = torch.cat([x, enc2], dim=1)
        x = self.dec2(x)
        x = self.up1(x)
        x = torch.cat([x, enc1], dim=1)
        x = self.dec1(x)

        return cast(Tensor, self.out_conv(x))
