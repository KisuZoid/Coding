# AutoInspect-X — CNN–Transformer Hybrid Segmentation Architecture

**Version 3 — implementation-ready architecture and methodology specification**

---

## 1. Architecture Intent

### System Objective

AutoInspect-X takes a vehicle image and produces:

1. detected vehicle-damage class(es),
2. pixel-level segmentation of the visible damage,
3. visual flagging/highlighting of the damaged region,
4. a per-prediction confidence/uncertainty signal,
5. a structured inspection result that is converted into a professional natural-language description by a downstream conversational layer.

The primary computer-vision problem is therefore:

> **Accurate, confidence-aware vehicle-damage segmentation and localization from a single vehicle image.**

The conversational LLM is a downstream explanation and interaction layer. It is not the primary damage detector, and it does not decide *whether* damage is present — it narrates and clarifies what the vision model already decided.

Repair-cost estimation and repair-action prediction are explicitly **out of scope**. The system's contribution ends at damage detection, segmentation, and professional explanation of that evidence.

---

## 2. Core Design Principle

Human visual inspection provides the architectural inspiration.

A human generally does not inspect every image region independently. The process is closer to:

```text
Observe the whole vehicle
        ↓
Build a global understanding of the scene
        ↓
Notice a visual discrepancy
        ↓
Focus attention on the suspicious region
        ↓
Inspect local visual details
        ↓
Determine whether the discrepancy represents damage
```

The model should not be described as literally "understanding the car like a human" or as reconstructing a perfect undamaged vehicle.

The engineering interpretation is:

> **The model jointly captures global vehicle context and local visual features to improve pixel-level damage segmentation.**

This is the central architectural principle.

---

## 3. Why a Hybrid Architecture

Vehicle damage contains information at different spatial/contextual scales.

### Local information

Damage can be defined by small visual cues such as:

- edges,
- texture changes,
- cracks,
- scratches,
- dents,
- local shading and shape irregularities.

CNNs are well suited to extracting these local and hierarchical visual features.

### Global information

The interpretation of a local irregularity benefits from its surrounding context:

- surrounding vehicle geometry,
- neighboring structures,
- larger surface patterns,
- spatial relationships between image regions,
- overall scene/view context.

Transformer-based attention provides a mechanism for modelling relationships across spatial regions.

### Combined principle

```text
Local visual detail
        +
Global contextual information
        ↓
Better representation of suspicious regions
        ↓
Pixel-level damage segmentation
```

The hybrid model is therefore not being introduced simply because "Transformers are modern." The Transformer has a defined architectural role: **global contextual modelling**. The CNN has a defined role: **local and hierarchical visual feature extraction**.

---

## 4. Proposed Model Concept

### High-Level Architecture

```text
                         INPUT IMAGE
                         512 × 512
                              │
                              ▼
                  PRETRAINED CNN ENCODER
                 (ImageNet-initialized)
                  Local visual features
                              │
                              ▼
                    Feature representation
                              │
                              ▼
                 LIGHTWEIGHT TRANSFORMER
                  (on bottleneck features)
                  Global contextual modelling
                              │
                              ▼
                       FEATURE FUSION
                Global context + local detail
                              │
                              ▼
                 SEGMENTATION DECODER
           (U-Net style, skip connections,
              deep supervision at two stages)
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
        7-CHANNEL MASK OUTPUT      PER-PIXEL CONFIDENCE
       (segmentation classes)        (uncertainty map)
                │                           │
                └─────────────┬─────────────┘
                              ▼
                Vehicle-damage segmentation
                  + confidence signal
```

The core CNN backbone, Transformer placement, and primary fusion operation are now fixed for the first implementation. Only explicitly listed items in Section 19 remain open for small feasibility experiments.

---

## 5. Functional Role of Each Component

### 5.1 CNN Encoder

The CNN encoder extracts hierarchical local features from the image.

Expected responsibilities:

- low-level edges and textures,
- intermediate visual structures,
- local damage patterns,
- spatially detailed feature maps,
- multi-scale feature representations.

The CNN should retain sufficiently high-resolution features so that small damage is not lost during downsampling.

**Upgrade — pretrained initialization.** The encoder is initialized with ImageNet-pretrained weights rather than trained from scratch. The existing baseline was trained from a random initialization and reached near-zero IoU on three of six classes; a randomly initialized encoder on ~2,800 training images is not expected to learn reliable low-level features in the available training budget. Pretraining is treated as a prerequisite for the hybrid model to be a fair test of the Transformer's contribution, not an optional enhancement.

---

### 5.2 Lightweight Transformer

The Transformer operates on a lower-resolution feature representation produced by the CNN.

Its purpose is to model broader spatial relationships without applying expensive attention directly to the full-resolution image.

Conceptually:

```text
512 × 512 image
      ↓
CNN downsampling
      ↓
smaller feature map
      ↓
Transformer attention
      ↓
global contextual representation
```

This is important for computational feasibility and for preserving the CNN's role in extracting fine spatial detail. Applying attention only at the bottleneck is treated as a fixed design choice rather than an open experimental variable, given the project's GPU memory constraints (Section 14).

---

### 5.3 Feature Fusion

The model combines:

```text
CNN local features
        +
Transformer global context
```

The fusion stage should allow the decoder to use both sources of information.

Conceptually:

```text
Local representation ───────┐
                            ├──→ fused representation
Global representation ──────┘
```

The exact implementation is now fixed as **projected element-wise addition at
the bottleneck**. The alternatives remain secondary feasibility questions, not
variables in the current catalogue:

```text
CNN C5:  [B, 512, 16, 16]
              │
          1×1 conv
              │
              ▼
           [B, 256, 16, 16]
              +
Transformer: [B, 256, 16, 16]
              │
              ▼
Fused:      [B, 256, 16, 16]
```

This is intentionally simple so that the core comparison isolates the effect of adding global contextual modelling rather than introducing a second complex fusion mechanism.


---

### 5.4 Segmentation Decoder

The decoder converts the fused representation back into a high-resolution spatial prediction.

A U-Net-style decoder with skip connections is appropriate conceptually because damage boundaries and small regions require recovery of spatial detail.

**Upgrade — deep supervision.** Auxiliary segmentation heads are attached at two
intermediate decoder resolutions, each contributing a down-weighted auxiliary
loss term summed with the main loss. This is a standard, low-cost technique for
improving recovery of small objects, which directly targets the project's
stated secondary research focus (Section 8).

The decoder produces a seven-channel segmentation representation:

```text
0 = background
1 = dent
2 = scratch
3 = crack
4 = glass shatter
5 = lamp broken
6 = tire flat
```

These classes correspond to the existing CarDD task definition.

---

### 5.5 Confidence / Uncertainty Signal

**No separate trainable confidence head is used in the first implementation.** Confidence is derived from the segmentation logits so that it does not require additional confidence labels, which CarDD does not provide.

The confidence signal connects the vision model to the product-level requirement
that the chatbot guide the user when a prediction is uncertain. It is computed
from the model's output distribution and exposed with a deterministic
`low_confidence` flag. Calibration and reliability measurement are planned RQ2
work, not completed behaviour of the current catalogue.

---

## 6. Important Scope Boundary: Vehicle Structure vs Damage

The architecture is informed by the idea that a human understands the overall vehicle structure before focusing on an abnormal region.

However, the current CarDD dataset contains damage masks, not ground-truth masks for vehicle parts such as:

- hood,
- bumper,
- door,
- fender,
- roof.

Therefore, the model should **not claim explicit vehicle-part segmentation** unless an additional labelled part dataset is introduced. The system also does **not** maintain a per-make/model reference image database to diff against — global context is a learned representation produced by the Transformer component, not an explicit reference comparison. This avoids depending on data (clean per-model reference photography, pose alignment) that does not currently exist for this project.

The current research problem remains:

> **learn useful global vehicle context and local visual detail for damage segmentation.**

It is not:

> "first segment every vehicle part with 100% certainty," nor
> "compare the input image against a stored reference vehicle image."

Global context is treated as a learned visual representation, not as an explicitly supervised perfect vehicle-part map or a stored reference.

---

## 7. Damage Interpretation

A local visual irregularity is not automatically damage.

The conceptual decision process is:

```text
Global context
     +
Local evidence
     ↓
Is the region consistent with a learned damage pattern?
     ↓
Yes → predict damage class + mask + confidence
No  → suppress as non-damage/background
```

This distinction is important because normal vehicle structure, reflections, curves, highlights, and shadows can also produce strong local visual patterns.

The research objective is therefore not simple pixel anomaly detection. It is **context-aware, confidence-scored damage segmentation**.

---

## 8. Research Hypothesis

### Primary Hypothesis

> **Combining global contextual information from a lightweight Transformer with local hierarchical visual features from a CNN can improve vehicle-damage segmentation compared with a conventional CNN-based segmentation baseline.**

### Secondary Focus

The study should pay particular attention to **small and visually subtle damage**, because small regions may be poorly represented by a model that relies primarily on coarse semantic features.

### Secondary Hypotheses (supporting techniques)

These are evaluated as contributing factors, not as the primary contribution:

- Boundary-aware loss improves IoU specifically on thin/elongated damage classes (crack, scratch).
- Deep supervision improves recovery of small-area damage instances.
- Test-time augmentation and calibration are optional secondary analyses;
  their value is not assumed.

The research should test all of the above empirically rather than assuming any of them will improve performance.

---

## 9. Experimental Methodology

### 9.1 Controlled Research Baseline

Use a ResNet34-U-Net as the controlled CNN baseline. The older compact CarddUNet checkpoint remains a historical/smoke-test artifact, not the primary research comparator.

```text
Input
  ↓
CNN/U-Net
  ↓
7-channel damage segmentation
```

**Current controlled baseline.** The current catalogue uses
`ResNet34UNet` under the same dataset, preprocessing, optimizer, EMA,
augmentation, and deep-supervision contract as `HybridSegmentation`. The
current trainer uses the Dice + Focal objective documented in ADR 0013; the
historical CE decision in ADR 0008 applies to earlier runs. The old compact
`CarddUNet` checkpoint remains a historical smoke-test artifact and is not a
current comparator.

The controlled comparison is therefore between two current records under the
same training procedure:

- ImageNet-pretrained ResNet34 encoder,
- foreground soft Dice + multiclass Focal loss,
- class-aware sampling,
- a 60-epoch target schedule with early stopping,
- identical augmentation and EMA policy.

Only the Transformer, additive fusion, and their resulting parameterization
should differ between the current baseline and the proposed model.

---

### 9.2 Proposed Hybrid Model

Train the custom hybrid:

```text
Pretrained CNN Encoder
      +
Lightweight Transformer
      +
Feature Fusion
      +
Segmentation Decoder (with deep supervision)
       +
      Logit-derived confidence signal
```

The proposed model should be evaluated using the same dataset protocol, preprocessing assumptions, and evaluation metrics as the corrected baseline so that the comparison remains controlled.

---

### 9.3 Optional Practical Comparator

YOLO11-seg may be evaluated as a practical pretrained segmentation framework if resources and project time permit, after the primary baseline-vs-hybrid comparison is complete. Its role is comparative, not the primary research contribution. It should not be presented as the project's custom hybrid architecture.

---

### 9.4 Mask2Former

Mask2Former should primarily inform the literature and architectural analysis of Transformer-based segmentation. Fine-tuning a pretrained Mask2Former can be considered as an optional advanced comparison if compute and time permit, only after the primary comparison and the optional YOLO11-seg comparison are complete. Training Mask2Former from scratch remains outside the preferred methodology.

---

## 10. Dataset Protocol

CarDD-COCO is the current dataset.

Verified split:

```text
Training   = 2,816 images
Validation =   810 images
Testing    =   374 images
```

The splits are already separated in the dataset.

### Training

Use the training split for parameter learning, augmentation, and optimization.

**Optional secondary augmentation — not part of the current run contract.**
For the classes with the lowest instance counts (tire flat: 225 instances;
crack; lamp broken), a future copy-paste experiment may crop damage instances
using their existing ground-truth masks and composite them onto other training
images at plausible scale/location. Any image containing a copy-pasted
instance must be tagged as synthetic-augmented in the training manifest,
consistent with the project's existing REAL/WEAK/SYNTHETIC/DERIVED labelling
discipline. This technique augments the training set only and must never be
applied to validation or test data.

### Validation

Use the validation split for model selection, hyperparameter selection, checkpoint selection, early stopping, and architecture decisions (including the feasibility experiments in Section 19).

### Testing

Keep the test split untouched during development. Use it for the final evaluation after the architecture and training configuration have been fixed.

### Optional final retraining

A final model may be retrained on training + validation after the development configuration is frozen, followed by one final evaluation on the untouched test set. The project should not train on validation data while simultaneously presenting it as an independent validation result.

---

## 11. Evaluation Methodology

### Overall segmentation quality

- mean IoU (mIoU)
- mean Dice
- pixel accuracy

### Per-class performance

Report IoU/Dice separately for dent, scratch, crack, glass shatter, lamp broken, tire flat. This is important because the CarDD dataset is class-imbalanced.

### Small-damage analysis

Where the annotation data supports it, group damage instances by mask area (small / medium / large) and compare performance across groups. This allows the research to determine whether the hybrid model is particularly useful for small/fine-grained damage.

### Statistical robustness — current limitation

The current catalogue contains two available seeds (`42` and `1337`) for
both architectures. This supports a controlled two-seed record, but not a
completed three-seed study or a statistical-superiority claim. A third seed and
an aggregate summary remain open work.

### Evaluation-time techniques — current decision

The current controlled records use EMA weights for validation and checkpoint
selection. TTA is not part of the recorded primary evaluation; it may be tested
as a separate future experiment.

### Confidence calibration (planned)

RQ2 still requires a locked operational definition and calibration/reliability
analysis. The current engine reports softmax-derived confidence and a
`low_confidence` flag; neither is a validated real-world reliability measure by
itself.

### Efficiency

Also record parameter count, inference latency, training time, and GPU memory usage. This prevents a higher accuracy score from being presented without considering computational cost.

---

## 12. Ablation Strategy

The active catalogue comparison uses two current arms:

```text
Experiment B42/B1337:
ResNet34UNet baseline (seed 42/1337)

Experiment H42/H1337:
HybridSegmentation (seed 42/1337)
```

Both arms use the same data, split, optimizer, Dice + Focal objective,
augmentation, EMA policy, and checkpoint-selection rule. The difference is the
Transformer and additive fusion path.

Boundary loss, copy-paste augmentation, TTA, and additional deep-supervision
variants are future ablations, not measured current catalogue arms. No claim is
made that any of those future variants improved performance.

---

## 13. Training Strategy

The training implementation remains separated from the product inference code.

```text
Training
    ↓
model checkpoint
    ↓
inference interface
    ↓
AutoInspect-X API
```

Training code should be runnable independently on local development hardware and Colab. The dataset root should be configurable rather than hardcoded to a specific platform:

```text
Local:
datasets/CarDD_COCO

Colab:
/content/.../CarDD_COCO
```

The training code itself should remain unchanged across environments. Kaggle portability is treated as a secondary, non-essential capability (see Section 14) and should not be engineered for unless Colab compute is exhausted.

### Training-time upgrades (apply to both baseline and hybrid where architecture-independent)

- **Loss:** 0.50 foreground soft Dice + 0.50 multiclass Focal, with the recorded class weights and reduced background weight (ADR 0013). Boundary loss is not part of the current primary experiment.
- **Sampling:** class-aware sampling on the training split only.
- **Augmentation:** random horizontal flip, small affine rotation/scale jitter, and mild brightness/contrast jitter; no copy-paste augmentation is part of the current run contract.
- **Deep supervision:** auxiliary losses at 1/4 and 1/8 resolution with weights `0.75 / 0.15 / 0.10`.
- **EMA:** maintained throughout training and used for validation, checkpoint selection, and the saved artifact.
- **Mixed precision:** used during training to fit the controlled models within available GPU memory.
- **Checkpointing:** periodic snapshots are written during training, while active experiment storage retains only the best checkpoint and run record.
- **Metric tracking:** per-class IoU and Dice are recorded during validation; the existing controlled records do not contain a separate small-damage-slice field.

---

## 14. Compute Strategy

### Local laptop

Primary use: development, debugging, dataset validation, smoke tests, inference testing, and lightweight experiments on a small data subset before committing to full cloud training runs.

The current machine has an RTX 3050 Laptop with approximately 4 GB VRAM.

### Cloud training

Primary use: full training runs, architecture experiments, multi-seed repeated experiments, and longer training schedules.

**Colab Pro is the primary training environment**, given confirmed project access. Priority GPU allocation, longer uninterrupted sessions, and greater available VRAM make it the practical home for the pretrained-encoder + Transformer + deep-supervision configuration, and for the multi-seed evaluation protocol in Section 11.

Kaggle remains available as a secondary/overflow environment (approximately 30 free GPU-hours/week) if Colab Pro compute is exhausted mid-project, but the project should not invest engineering effort in Kaggle-specific portability beyond the environment-agnostic dataset-path pattern already described in Section 13.

The architecture should be designed to operate within moderate GPU memory rather than assuming unlimited compute, since the final inference deployment target remains modest hardware.

---

## 15. Product Integration Boundary

The computer-vision system and conversational system remain separate.

```text
                    VEHICLE IMAGE
                           │
                           ▼
          CLASSICAL IMAGE-QUALITY GATE
        (blur / exposure / framing checks —
         rule-based, not a learned model)
                           │
                 ┌─────────┴─────────┐
                 │                   │
               FAIL                 PASS
                 │                   │
                 ▼                   ▼
      auto chatbot: retake      HYBRID SEGMENTATION
         guidance                    │
                                     ▼
                          structured findings
                        (class, mask, location,
                           confidence)
                                     │
                       ┌─────────────┴─────────────┐
                       │                            │
                 confidence LOW              confidence OK
                       │                            │
                       ▼                            ▼
           auto chatbot: ask for            LLM (LangChain, professional
           clearer photo / more info          persona) generates description
                                                     │
                                                     ▼
                                          main chat available for
                                          user follow-up questions
```

### Vision model responsibility (the evidence layer)

- damage class,
- damage mask,
- localization,
- per-prediction confidence.

### Image-quality gate — upgrade, explicitly separated from the segmentation model

Bad-photo detection (blur, poor exposure, wrong framing) is handled by lightweight, classical, rule-based checks (e.g. Laplacian-variance blur detection, brightness histogram analysis) run **before** the image reaches the segmentation model — not by asking the segmentation model to double as a quality classifier. This keeps the two failure modes separable and debuggable: a rejected photo is rejected for a stated, inspectable reason, not because a black-box model produced a low-confidence damage prediction for an unrelated cause.

### Conversational layer responsibility (the explanation layer)

- professional narration of the structured findings — produced automatically, every time segmentation succeeds, using LangChain with a professional-inspector persona rather than a hand-written template,
- automatic retake guidance when the image-quality gate fails,
- automatic clarification prompts when the confidence signal reports low confidence,
- open-ended follow-up conversation, user-initiated.

The LLM must not independently invent a damage class or confidence level unsupported by the vision model's structured output. The confidence signal (Section 5.5) is what allows the "guide the user if the photo is not clear" requirement to be driven by the model's own uncertainty rather than by separate, duplicated logic in the conversational layer.

---


# 15A. Exact Confidence Calculation

At inference:

```text
logits
  ↓
softmax
  ↓
per-pixel class probabilities
```

For each predicted damage region:

```text
region confidence =
mean probability of the predicted class
over pixels belonging to that region
```

For the current implementation, the product exposes the mean predicted-class
probability for each connected region and a deterministic low-confidence count.
Temperature scaling and reliability measurement are planned RQ2 work and are
not part of the current primary run. The test set is never used to select or
calibrate a confidence threshold.

A low-confidence prediction means:

> the model's segmentation evidence is uncertain

It does **not** automatically mean:

> the photograph itself is poor quality.


## 16. Architecture Claims to Avoid

Do not describe the system as:

> "The model understands the entire car with 100% probability."

Do not describe the model as:

> "The model reconstructs the perfect undamaged vehicle," or
> "The model compares the input against a stored reference image of the same make/model."

Do not claim:

> "The Transformer guarantees better detection."

Do not claim explicit vehicle-part recognition unless corresponding supervision exists.

Do not claim that the confidence signal is a validated measure of real-world
reliability unless calibration has actually been measured (Section 11).

The defensible statement is:

> **The model jointly captures global vehicle context and local visual features to improve pixel-level damage segmentation, and reports its own confidence in that prediction.**

---

## 17. Research Contribution Definition

The project contribution should be framed as an **experimental architectural investigation**, not the invention of CNNs or Transformers.

### Proposed contribution

A lightweight CNN–Transformer hybrid segmentation architecture tailored to vehicle-damage segmentation on CarDD, evaluated against a controlled ResNet34-U-Net baseline under an identical training procedure, with explicit analysis of:

- overall segmentation quality,
- per-damage-class performance,
- small-damage performance,
- planned analysis of supporting techniques through future ablations,
- statistical robustness across multiple seeds,
- computational efficiency.

The current catalogue establishes a controlled two-architecture comparison;
it does not yet establish ablation attribution or architecture superiority.
The research contribution is therefore the **design, controlled evaluation, and
planned analysis** of the hybrid approach for this specific task.

---

## 18. Current Architectural Decision

### Selected direction

**Custom lightweight CNN–Transformer hybrid segmentation model, with confidence-aware output**

### Locked architectural decisions

- CNN backbone: ImageNet-pretrained ResNet34
- Transformer placement: bottleneck only
- Transformer input: 16×16 feature map
- Transformer projection dimension: 256
- Transformer depth: 4 encoder blocks
- Attention heads: 4
- FFN dimension: 1024
- Activation: GELU
- Normalization: pre-LayerNorm
- Dropout: 0.10
- Positional encoding: learned 2-D positional embedding
- Primary fusion: projected CNN bottleneck + Transformer output by element-wise addition
- Decoder: U-Net-style, bilinear upsampling + convolution blocks
- Deep supervision: auxiliary heads at 1/4 and 1/8 resolution
- Core loss: 0.50 Dice + 0.50 multiclass Focal (ADR 0013)
- Confidence: derived from segmentation logits; no separate trainable confidence head
- Primary test evaluation: single-scale, single forward pass
- EMA: enabled identically for baseline and hybrid
- TTA: secondary experiment only

### Baseline

**Current controlled `ResNet34UNet` baseline**, trained under the shared
current procedure (Section 9.1). The earlier compact `CarddUNet` checkpoint is
historical provenance, not a valid current baseline result.

### Optional comparator

**YOLO11-seg fine-tuning** (secondary priority, after the primary controlled comparison)

### Advanced literature/reference architecture

**Mask2Former** (literature reference; fine-tuning only as a stretch goal)

### Explicitly not preferred

**Training Mask2Former from scratch**

---

## 19. Remaining Technical Decisions

The primary architecture and training decisions are now fixed by the current
catalogue. The following remain possible secondary ablations, not unresolved
requirements for the active model:

1. Boundary-aware loss as a separate experiment.
2. Copy-paste or stronger augmentation for the rarest classes.
3. Test-time augmentation and calibration analysis.
4. Whether YOLO11-seg is worth including as an optional comparator.

The current RQ2 confidence-honesty operational definition remains open in the
research plan; it is not resolved by the architecture specification.

These decisions should be driven by:

```text
segmentation quality
+
small-damage performance
+
GPU memory
+
training stability
+
inference efficiency
```

rather than model popularity alone.

---


# 19A. Exact Training Objective

The core objective is fixed as:

```text
L_total =
0.50 × L_Dice
+
0.50 × L_Focal
```

### Dice

Compute soft multi-class Dice over the six foreground classes.

Use:

```text
smooth = 1e-6
```

Background is excluded from the Dice mean.

### Focal

Use multi-class focal loss:

```text
gamma = 2.0
```

The six foreground class weights are calculated from training-set pixel frequencies using inverse-square-root frequency weighting and normalized so that their mean foreground weight is 1.0.

Background uses a fixed reduced weight to prevent the dominant background class from overwhelming the objective.

### Deep supervision

For the two auxiliary outputs:

```text
Main loss       × 0.75
Auxiliary 1     × 0.15
Auxiliary 2     × 0.10
```

Each auxiliary prediction uses the same Dice + Focal formulation against a nearest-neighbour resized target.

### Boundary loss

Boundary loss is **not part of the primary experiment**.

It is evaluated only as a separate optional ablation.

## 20. Summary of Upgrades Over the Original Design

For traceability, this version adds the following over the original architecture document:

| Area | Current decision | Rationale |
|---|---|---|
| Encoder | ImageNet-pretrained ResNet34 | Shared encoder for the controlled baseline and hybrid |
| Loss | 0.50 Dice + 0.50 multiclass Focal (ADR 0013) | Matches the current trainer and deep-supervised run contract |
| Decoder | Deep supervision at intermediate stages | Shared by both current arms |
| Output | Softmax confidence and deterministic `low_confidence` flag | Avoids a separate trainable confidence head without calibration labels |
| Sampling | Class-aware sampling | Makes rare classes visible during training without changing split policy |
| Data | No copy-paste augmentation in the current run contract | Keeps the existing controlled records interpretable |
| Evaluation | EMA for validation/checkpoint selection; single-scale inference | Identical evaluation procedure for both current arms |
| Evaluation | Two available seeds (`42`, `1337`) | Current evidence; not a completed three-seed study |
| Methodology | Explicit `ResNet34UNet` comparator | Isolates the current hybrid's Transformer/fusion contribution |
| Product boundary | Classical quality gate, separate from segmentation | Keeps bad-photo detection independent of the damage model |
| Scope | Cost, repair action, and physical-area claims removed | Aligns with ADR 0011 and available evidence |

---

## 21. Final Architecture Statement

> **AutoInspect-X uses `HybridSegmentation`, in which a pretrained ResNet34
> encoder preserves local visual detail while a four-block Transformer at the
> 16×16 bottleneck captures broader spatial relationships. The projected CNN
> and Transformer features are added and decoded with deep supervision into
> pixel-level masks for six CarDD damage categories. The current catalogue
> compares this arm with `ResNet34UNet` under the same two-seed, Dice + Focal
> contract; it does not establish architecture superiority or a completed
> multi-seed result. The engine exposes an uncalibrated softmax-derived
> confidence signal and deterministic low-confidence flag, while a separate
> classical image-quality gate drives photo-quality clarification.**

The remaining technical choices in Section 19 are planned follow-up work, not
claims about the current catalogue.
