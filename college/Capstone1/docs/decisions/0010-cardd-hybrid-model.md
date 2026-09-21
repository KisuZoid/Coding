# ADR 0010 — CarddHybrid: CNN + Transformer segmentation model with arch-tagged checkpoints

Status: **Accepted** (2026-09-21).

## Context

Phase 9 needed a research-contribution segmentation architecture distinct from
the plain U-Net baseline (`CarddUNet`), while keeping the same inference
contract, evaluation harness, loss, and checkpoint pipeline. The prior
baselines (`cardd_baseline_ce`, val mIoU ~0.0475 on CarDD) showed that a small
U-Net alone struggles with global context for fine, spread-out damage. A
bottleneck transformer is a standard, low-risk upgrade: CNN encoder produces
downscaled feature maps, a compact transformer attends globally at the
bottleneck, and the decoder upsamples with the original skip connections.

Checkpoints must also be self-describing: the engine needs to know which
architecture a checkpoint belongs to without guessing, because the two models
share the same state-dict contract surface (keys `model_state`, `base`,
`epoch`) but different parameter shapes.

## Decision

1. **Model** (`ml/models/cardd_hybrid.py::CarddHybrid`):
   - Same public API as `CarddUNet`: `__init__(in_channels, num_classes, base)`,
     forward takes `(B, 3, H, W)` and returns `(B, 7, H, W)` logits.
   - 4-stage encoder (base 32 → 32·2⁰, 32·2¹, 32·2², 32·2³ down to 32×32) with
     `enc{1..4}` block names for skip reuse, mirrored by the decoder
     (`dec4`/`dec3`/`dec2`/`dec1`; dec1 also gets the pool-2 branch). The 1×1
     head maps to 7 classes.
   - Transformer bottleneck at 32×32: `d_model = base * 8` (256 at base 32),
     4 heads, 2 encoder layers, `dim_feedforward = hidden * 2`, fixed sinusoidal
     positional encoding, `batch_first`. Parameter count ≈ 3.2 M (measured
     3,206,855).
2. **Checkpoint contract extension**: `best_checkpoint.pt` gains a `model_arch`
   key (`"cardd_hybrid"` or `"cardd_unet"`). Legacy checkpoints without the key
   still load as `cardd_unet`.
3. **Engine dispatch** (`ml/inference/engine.py::SegmentationEngine.from_checkpoint`):
   - `ModelMetadata.arch` new field (default `"cardd_unet"`, included in
     `to_dict()`).
   - `_build_model(arch, base, num_classes)` maps `cardd_hybrid`/`CarddHybrid` →
     CarddHybrid, empty/`cardd_unet`/`CarddUNet` → CarddUNet, anything else →
     `ModelVersionError`.
   - `SegmentationEngine.__init__` now takes a raw `torch.nn.Module` plus
     `ModelMetadata`; `from_checkpoint` loads state dict into the dispatched
     model and reports the resolved arch in metadata.
4. **Training CLI** (`ml/training/train.py`): `--model cardd_unet|cardd_hybrid`
   (default `cardd_hybrid`), `TrainingConfig.model_arch`, checkpoint saved with
   `model_arch`, evaluation record `model` string updated.
5. **Container** (`apps/api/container.py`): reads `base` and `model_arch`
   straight from the checkpoint artefact (never guessed), asserts the built
   engine's arch matches the advertised one, and points the demo default at
   `ml/experiments/cardd_hybrid_ce/best_checkpoint.pt`.

## Consequences

- The demo/inference path automatically serves whichever architecture the
  trained artefact advertises; no config drift between training and serving.
- A base mismatch is still a loud `ModelVersionError` (ADR 0003 contract).
- `CarddHybrid` inherits the documented argmax-overlap limitation on stacked
  CarDD masks (same loss/decode as ADR 0008) and the honesty boundary: masks
  are model predictions, never verified damage extent.
- Honest-training rule holds: `cardd_hybrid_ce` was trained and its inference
  verified real on 2026-09-21 (val mIoU 0.0504 / test 0.0586, MEASURED, see the
  run registry and the real-engine test gate at
  `tests/test_e2e_integration.py::test_full_journey_happy_path_with_real_engine`
  and the Playwright inspection-journey spec). Claim level stays capped at the
  measured numbers; the A1-vs-A3 write-up and RQ2 metric remain open.