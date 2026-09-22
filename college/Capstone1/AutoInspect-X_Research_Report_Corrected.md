# **AutoInspect-X: Photo-First Vehicle Damage Segmentation with Evidence-Labelled Confidence**

## **1\. Executive Summary**

**AutoInspect-X** is a **viable and defensible AI capstone project** whose scope is
a **photograph-first vehicle-damage inspection system**: a photograph is
uploaded, a *capture-quality gate* accepts or rejects it, a segmentation model
produces a pixel-level damage mask, and the system explains its findings — and
its confidence — honestly. The research contribution is a **CNN + Transformer
hybrid segmentation model** compared against a plain U-Net baseline on the CarDD
dataset, with an explicit honesty contract: every mask is labelled a *model
prediction*, every low-confidence result is flagged, and no fabrication of
physical area, repair action, hidden damage, or cost appears anywhere.

This is a **scope change** from the earlier version of this report. That version
framed AutoInspect-X as multimodal joint modeling (segmentation + vehicle
metadata → repair action + calibrated cost intervals). That framing was removed
because it was not backed by real ground truth: CarDD carries no repair-cost,
repair-action, or vehicle-metadata annotations, and a rule-generated cost table
is a SYNTHETIC LABEL, not evidence (ADR 0004). The change is recorded in ADR
0011 (photo-first scope) and ADR 0010 (CarddHybrid model), and this report has
been rewritten to match the implemented and honest system.

```
+---------------------------------------------------------------------------+
|                          AUTOINSPECT-X PIPELINE (PHOTO-FIRST)             |
+---------------------------------------------------------------------------+
|  [Photograph]  --->  [Capture-Quality Gate]  --->  (FAIL) retake guidance  |
|       |                  luminance -> glare -> blur -> contrast             |
|       |                    (status = QUALITY_FAILED, never a mask)          |
|       v                                                                     |
|  (PASS)                                                                     |
|       v                                                                     |
|  [Damage Segmentation]   CarddHybrid (CNN+Transformer) against             |
|              \           CarddUNet baseline; argmax over 7 classes          |
|               v                                                            |
|  [Evidence Payload]   predicted mask + per-class image-denominator area     |
|       |               ratios (DERIVED FEATURE, not cm2) + confidence +      |
|       |               low_confidence flag + overlay PNG                     |
|       v                                                                    |
|  [Honest Explanation]  LangChain ChatGroq (or offline stub) grounded in     |
|       |               the persisted evidence; never cost/quote fields        |
|       v                                                                    |
|  [Optional consent]  --->  stored training sample (MODEL_SUGGESTED only)     |
|       v                                                                    |
|  [Follow-up chat]  inline in the assistant composer                         |
+---------------------------------------------------------------------------+
```

### **Key Analytical Findings**

> 1. **Academic Viability:** **YES, WITH HONESTY CONSTRAINTS.** Pure visual
>    damage classification/detection is saturated in the literature. The
>    defensible contribution is a **CNN + Transformer hybrid segmentation model
>    with an evidence-labelling honesty contract** — a self-contained, data real
>    question that can actually be answered with the CarDD dataset.
> 2. **Dataset Reality:** CarDD (4,000 images, 9,000+ instances, six damage
>    classes) supports segmentation training and honest segmentation evidence.
>    CarDD does **not** contain vehicle metadata, repair actions, or repair cost;
>    anything built on those would be synthetic and mislabelled as evidence.
> 3. **Primary Novelty (kept):** a compact bottleneck-transformer segmentation
>    architecture trained end-to-end on CarDD under softmax cross-entropy (ADR
>    0008), with arch-tagged self-describing checkpoints and an engine that
>    refuses to present predicted masks as verified damage.

## **2\. Scope Change: Why Photo-First**

Prior version of this report and the bootstrap brief proposed a multimodal
repair-cost pipeline: `Instance Segmentation → Physical Area Mapping (cm²) →
Joint Multimodal Fusion (vision + metadata) → Repair Action + Hidden Risk +
Quantile Cost [P10/P50/P90]`. That design was **not implemented as a real
research core** because it was blocked by missing data, and the supervisor cut
cost/repair from scope (ADR 0011, accepted 2026-09-21):

| Removed (ADR 0011) | Reason |
|---|---|
| Repair-cost prediction | No observed cost labels anywhere; rule tables are SYNTHETIC LABEL (ADR 0004) |
| Repair-action prediction | No action ground truth; a rule is a "preliminary demonstration rule", not data |
| Questionnaire-driven conversation flow (incident → part → city → insurance) | Existed only to feed the cost model; removed with it |
| P10/P50/P90 quantile cost estimates | Demo-only structure; removed so no API/UI surface can mislabel cost |
| `ALLOW_SYNTHETIC_ESTIMATE` flag and all cost/quote/amount fields | Enforced absent by tests (`_assert_no_forbidden_fields`) |
| Multi-panel dashboard UI | Replaced by a ChatGPT-style chat with inline photo attachment |

**What stays and what replaces it:**

- **Kept:** capture-quality validation, real segmentation inference, honest
  confidence/low-confidence labelling, consent-gated training samples, LangChain
  ChatGroq explanation (or offline stub), evidence-labelled UI.
- **Replaced:** the cost/fusion model is replaced by the research core question
  of this report — whether a **CNN + Transformer hybrid (CarddHybrid)** improves
  damage-segmentation quality and confidence honesty over the **plain U-Net
  baseline (CarddUNet)**.

## **3\. AutoInspect-X Problem Definition (Photo-First)**

The core objective is to move automated vehicle inspection from "is there
damage" to **"where is the damage, how confident can we honestly be, and can we
show our evidence"** — a decision-support system, not a quotation.

```
+--------------------+     +------------------------+     +---------------------+
| [Photograph]       | --> | [Damage Segmentation]  | --> | [Evidence Payload]  |
| one uploaded photo |     | 5-stage CNN encoder +  |     | mask / class areas  |
+--------------------+     | transformer bottleneck |     | ratio / confidence  |
                           | + decoder with skips   |     | / overlay / honesty  |
                           +------------------------+     +---------------------+
      +------------------------------------------------------------------+
      |  [Explain / Chat]  honest narrative + retake guidance + consent  |
      +------------------------------------------------------------------+
```

The system processes a single vehicle photograph through a unified,
honesty-constrained sequence:

$$\\text{Photo } (I) \\longrightarrow \\{\\mathcal{S}_{\\text{damage}}, A_{\\text{ratio}}, C_{p}, \\text{low\\_conf}, \\text{Overlay}, \\text{Explanation}\\}$$

where $\\mathcal{S}_{\\text{damage}}$ is the predicted per-pixel mask (MODEL
PREDICTION), $A_{\\text{ratio}}$ is the image-denominator damaged-pixel ratio
(DERIVED FEATURE, a normalized ratio — never cm$^2$), $C_{p}$ is the mean pixel
confidence, and `low_conf` is the honest low-confidence flag that gates how
findings may be presented.

## **4\. Industry Problem**

Vehicle damage assessment in the automotive and insurance industries suffers
from structural inefficiencies (industry context, not a research claim):

+--------------------------------------------------------------------------------------------------+
|                                REAL-WORLD INDUSTRY PAIN POINTS                                   |
+--------------------------------------------------------------------------------------------------+
|  1. High Manual Overhead     | Field appraiser visits are scheduled, costly, and slow.            |
|  2. Severe Processing Delays | Multiple business days between first photo and assessment.          |
|  3. Estimation Inconsistency | Subjective severity scoring differs between assessors.              |
|  4. Fraud / Leakage          | Inflated quotes and fake claims cost the industry annually.         |
|  5. Hidden Structural Risks  | Surface photos cannot reveal internal damage; teardown is required.  |
+--------------------------------------------------------------------------------------------------+

Such pain points ARE the motivation for automated photo-first inspection. They do
**not** license fabricated outputs: because the damage is assessed from one
uncontrolled photograph, the system must say what it can measure (predicted
mask, normalized area ratio, confidence) and what it cannot measure (physical
area, hidden damage, repair cost).

## **5\. Literature Review: Automated Vehicle Damage Detection and Segmentation**

This section is new for this revision (2026-09-21). It replaces the previous
"Top 15 relevant papers" list, which mixed verified sources with entries that
could not be independently confirmed. **Citation policy for this review:** each
work's bibliographic data and headline claims were checked against publisher or
arXiv records during this revision; claims that are only inferred by this paper,
rather than stated by the source, are flagged as *(inference)*. Any previously
cited entry that could not be verified is explicitly marked UNVERIFIED and is
not used as evidence.

### 5.1 Scope and method

The review covers: (a) public datasets and benchmarks for vehicle damage, (b)
CNN segmentation architectures, (c) transformer and CNN+Transformer hybrid
segmentation, (d) detection frameworks used in applied damage work, and (e)
uncertainty/confidence methods that motivate the honesty contract. It is a
targeted review for a bounded capstone, not an exhaustive survey; readers
interested in a systematic landscape should consult Hasan et al. (2025) [20], a
systematic literature review that screened 55 selected papers, tabulated their
public datasets, and grouped methods by task (classification, detection,
segmentation) and by application context (insurance claim, traffic, post-accident).

Selection criterion for this review: works either (i) define the working dataset
or baseline of this project (CarDD, U-Net, the CE/argmax training rule), (ii)
are directly comparable architectures for the research question (transformer and
hybrid segmentation), or (iii) supply the uncertainty vocabulary the honesty
contract relies on. Recent 2025 applied work that reports cross-dataset numbers
is included where verifiable, but cross-paper numbers are **not** treated as
comparable benchmarks *(inference)*, because the studies differ in dataset,
split policy, and evaluation code.

### 5.2 Datasets and benchmarks

**CarDD (Wang, Li, Wu, 2023)** — *sourced.* The CarDD dataset ([1]) is the first
publicly available large-scale dataset for vision-based car damage detection and
segmentation: 4,000 high-resolution images with over 9,000 annotated instances
across six damage categories (dent, scratch, crack, glass shatter, lamp broken,
tire flat). It supports object detection, instance segmentation, and salient
object detection. CarDD is the dataset used throughout this project; the
official splits are preserved (train 2,816 images / 6,211 instances, val 810 /
1,744, test 374 / 785 — MEASURED from the local audit). CarDD contains damage
masks only: no vehicle-part masks, no vehicle metadata, and no repair-cost or
repair-action annotations *(inference from the schema; confirmed in
`archive/docs/cost-multimodal-data-readiness.md`)*. That is precisely why the multimodal
cost framing of the earlier report version could not be built honestly.

**VehiDE (Huynh et al., 2023)** — *sourced.* The VehiDE dataset [2] is a
publicly released, large-scale resource for segmenting and detecting automotive
damage: 13,945 high-resolution photos with more than 32,000 annotated damage
instances across eight damage categories, supporting classification, object
detection, instance segmentation, and salient object detection. A follow-up
study in the *Journal of Information and Telecommunication* [3] benchmarks
state-of-the-art segmentation on it. Verification note: the earlier report
listed "VeHIDE (12,000 images, 61 parts, 26 damage types)" under that name; the
verified VehiDE figures above (13,945 / 32,000+ / 8) do **not** match those
numbers, and the "12,000/61/26" set instead matches the dataset described by the
ALBERT model paper [7]. The 12,000/61/26 figure is therefore treated as
UNVERIFIED and is not used as evidence here.

**CrashCar101 (Parslov, Riise, Papadopoulos, 2024)** — *sourced.* A
procedurally generated dataset of 101,050 car-crash images with part and damage
segmentation masks and structural severity levels [4], intended to overcome the
cost and licensing problems of real crash imagery. Because its imagery is
synthetic, it is a *complement* to real datasets such as CarDD for
augmentation/pre-training, not a substitute *(inference)*.

**CDA-Net (Bhogale et al., 2023)** — *sourced.* Introduces two datasets from the
Indian automotive market — a car-make/model dataset and an 11,380-image damage
dataset with annotations — and a YOLOv5-based severity-assessment pipeline [5].

**MVA-CDD (Peng et al., 2025)** — *sourced.* A multi-view car-damage detection
model (Feature Split, Feature Fusion, Image…) published in an IEEE venue [6].
Multi-view fusion is beyond this project's single-photo scope but confirms the
active research interest in combining views.

**Three-quarter-view Car Damage dataset (Lee, Lee, Park, 2024)** — *sourced.*
A public dataset of car-damage photos taken from the three-quarter viewpoint,
introduced with deep-learning classification experiments in *Heliyon* [21]; it
is a severity/classification resource (a "three-quarter view" captures a whole
car side in a single frame) and complements the segmentation-oriented CarDD.

*(inference, dataset landscape):* Four dataset families recur across this
literature — (i) *real, segmentation-annotated* (CarDD, VehiDE), (ii)
*synthetic/procedural with perfect masks* (CrashCar101), (iii) *severity
classification* (three-quarter-view; small severity sets), and (iv)
*closed commercial* (unreleased insurer data). Only family (i) with CarDD is
verifiable, licence-clear, and large enough for deep segmentation in this
capstone; the others are cited for context or as future extension routes, never
as a training source here.

**UNVERIFIED entries retained from the earlier report:**

- **"CDD (2025)"** — the prior report's dataset table listed "CDD (2025): 12,000
  images, 26 damage types, 61 vehicle parts." No peer-reviewed dataset by that
  name matching that description could be verified in this revision; the damage
  (26) and part (61) counts match the ALBERT dataset description [7], and the
  12,000-image figure is uncorroborated. Retained as a name only, **flagged
  UNVERIFIED**, and not used in any claim. *(If this turns out to be a real,
  current dataset, it should be adopted via its own ADR with licence and label
  mapping — AGENTS.md §4.)*
- **"Insurance-Damage-v2"** — no academic citation could be verified; if it
  exists it is an open disaggregated image resource of the Kaggle/Roboflow
  style, with unknown licence and labelling provenance. **Flagged UNVERIFIED.**
  Not used as evidence.

### 5.3 CNN segmentation architectures

**U-Net (Ronneberger, Fischer, Brox, 2015)** — *sourced.* The encoder–decoder
with skip connections [8] is the canonical small-data segmentation architecture
and the direct ancestor of this project's baseline `CarddUNet` (ADR 0006), which
implements `_DoubleConv` blocks, max-pool downsampling, transposed-convolution
upsampling, and skip connects.

**DeepLabv3 (Chen, Papandreou, Schroff, Adam, 2017)** — *sourced.* Atrous
convolution with multiple dilation rates and an atrous spatial pyramid pooling
design [9]; a widely reused semantic-segmentation backbone.

**Mask R-CNN (He, Gkioxari, Dollár, Girshick, 2017)** — *sourced (well-known
foundational work).* Extends Faster R-CNN with a parallel mask branch for
instance segmentation [10]; it is the primary reference model in the CarDD paper
itself [1].

**HRNet (Wang et al., 2020)** — *sourced.* Maintains high-resolution
representations throughout the network by fusing parallel multi-resolution
branches, preserving spatial detail relevant to thin, spread-out damage [11].

*(inference, CNN stage analysis):* The CNN family gives the field its
spatial-sensitive vocabulary — skip connections (U-Net), atrous multi-scale
context (DeepLabv3), instance-level masks (Mask R-CNN), and HR fusion — but
each pays most of its capacity to local structure. Damage evidence, however,
also lives in global relations: a dent on the door and a displaced panel on the
A-pillar are far apart yet causally linked. That gap is what the transformer
stage targets.

### 5.4 Transformer and CNN + Transformer hybrid segmentation

**ViT (Dosovitskiy et al., 2021)** — *sourced.* Treats an image as a sequence of
patches processed by a standard transformer encoder [12]; the basis of the
segmentation transformers below.

**SETR (Zheng et al., 2021)** — *sourced.* Uses a ViT as an encoder for semantic
segmentation with progressive upsampling decoders [13].

**SegFormer (Xie et al., 2021)** — *sourced.* A hierarchical transformer with a
positional-encoding-free decoder that unifies semantic and panoptic
segmentation; the prior report recommended it as a candidate vision backbone
[14].

**TransUNet (Chen et al., 2021)** — *sourced.* A medical-image architecture that
hybridizes CNN and transformer, using the transformer as a self-attention layer
at the bottleneck before a CNN decoder with skip connections [15]. This is the
direct methodological antecedent of **CarddHybrid** (ADR 0010): a CNN encoder
produces downscaled feature maps, a compact transformer attends globally at the
bottleneck, and the decoder upsamples with the original skips.

**ALBERT (Panboonyuen, 2025)** — *sourced.* An automotive-instance-segmentation
model based on bidirectional encoder representations with multi-branch
classification over a large annotated automotive dataset: 26 real damage types,
7 fake-damage artifacts, and 61 distinct car parts [7]. Its described dataset is
the likely origin of the "26 damage types / 61 parts" figures that the earlier
report attached to "CDD (2025)" and "VeHIDE" *(inference)*.

**C-DiffDet+ (Sellam et al., 2025)** — *sourced.* An applied framework combining
a diffusion-based inpainting module with a YOLOv8 detection stage and a
severity classifier, evaluated against the 2022 Daedalus dataset and other
sources [22]. It is diffusion-focused rather than pure segmentation, but it
confirms the 2024–2025 trend: generative models for anomaly/segmentation and
task-specific classifiers for severity are converging in applied damage
research.

*(inference, this project):* CNN+Transformer hybrids at the bottleneck are a
standard, low-risk upgrade pattern that addresses a real weakness seen in the
baseline `cardd_baseline_ce` (val mIoU ~0.0475): a small U-Net underfits and
misses thin, spread-out damage (FN-dominated; small-damage slice ≈ 0). A global
attention stage at the 32×32 bottleneck is the chosen way to give the model
global context without the GPU cost of a full ViT. This is the rationale
recorded in ADR 0010; it was a working hypothesis, now tested by the trained
`cardd_hybrid_ce` run (§10 H1) with a weak positive aggregate but no
small-damage improvement — **evidence, not a settled result**.

*(inference, design choice):* Three practical constraints favour the bottleneck
location over a full ViT backbone or SegFormer encoder for this capstone: (a)
VRAM budget (the observed peak is 2.85 GB for the U-Net; the hybrid's
1.7×-bigger parameter count must stay within 4 GB), (b) the CNN decoder's skip
connections are still needed to recover small-damage detail, and (c) the
transformer needs only 32×32 spatial resolution at the bottleneck to model
inter-patch attention; a full-patch ViT at 224×224 is unnecessary cost.

### 5.5 Detection frameworks used in applied damage work

**YOLOv8 (Jocher, Chaurasia, Qiu, 2023)** — *sourced (software, not a paper).*
Ultralytics YOLOv8 is an open-source object detection and segmentation model
released as software in January 2023 [16]; it has no peer-reviewed paper, so it
must be cited as a software release. The prior report recommended YOLOv8-Seg as
a vision backbone; ADR 0006 declined it as the primary framework and kept it only
as a potential future comparison baseline, because a raw-PyTorch U-Net/hybrid
keeps the loss, metrics, and class decoding under our control on the same splits
and seeds.

### 5.6 Uncertainty, confidence, and the honesty contract

**Kendall & Gal (2017)** — *sourced.* Introduces the distinction between
*aleatoric* (data) and *epistemic* (model) uncertainty for vision problems [17].
This taxonomy is the vocabulary of the honesty contract: a low-confidence flag
must be readable as "the model itself is uncertain", which is epistemic, and not
as evidence about the vehicle.

**MC Dropout (Gal & Ghahramani, 2016)** — *sourced.* Approximates Bayesian
inference by keeping dropout active at test time and averaging stochastic
forward passes [18]; a cheap way to obtain an epistemic uncertainty estimate.

**Deep Ensembles (Lakshminarayanan, Pritzel, Blundell, 2017)** — *sourced.*
Trains an ensemble of independently-seeded networks and uses the variance across
members as a calibrated uncertainty estimate [19].

*(inference):* regardless of the UQ estimator, the integrity-relevant property is
*calibration* — that claimed confidence matches observed accuracy. None of the
commercial damage tools surveyed publish calibration curves; a system that
reports softmax mean confidence, as implemented here, is only honest if it also
flags low confidence loudly (the `low_confidence` flag). That is why the honesty
contract (§16.1, RQ2) is framed as a measurable agreement-disagreement
separation rather than as an assumed property of the softmax.

*(inference, this project):* The implemented engine uses a simpler, deterministic
honesty signal — softmax mean confidence plus a `low_confidence` flag below
thresholds (`min_mean_confidence`, `min_damage_fraction`) — rather than MC
Dropout or ensembles. The stated reason is honest scope: the demonstration-grade
baseline labels itself "Demo-grade baseline (CarDD, underfit), validation mIoU
~0.0475" and sets `low_confidence` honestly and frequently. MC Dropout / Deep
Ensembles remain listed extensions (see §16.6) and would be ADR'd before use, in
accordance with the ground-truth policy.

### 5.7 The research gap this project targets

*(inference, argued from the reviewed sources):*

1. **Detection and classification are saturated.** A 2025 systematic review
   ([20]) confirms a large applied literature on damage detection and
   classification; commercial systems (Tractable, Qapter, CCC, Mitchell — 
   *report content, not independently evaluated here*) are closed-source.

2. **Segmentation is the active front.** CarDD [1], VehiDE [2]/[3], CrashCar101
   [4], and MVA-CDD [6] show that pixel-level and part-level segmentation is
   where the field is moving; ALBERT [7] shows transformer-based automotive
   segmentation with damage+part+real-vs-fake branches.

3. **The honest, data-real opening is segmentation quality + confidence
   honesty.** Public damage datasets supply masks but not financial or vehicle
   metadata ground truth. Reports describing cost prediction either use private
   datasets or synthetic price rules — neither is reproducible, verifiable
   ground truth here. The defensible niche for this capstone is therefore: a
   reproducible CNN+Transformer hybrid segmentation benchmark on CarDD, with a
   contract that separates MODEL PREDICTION from any claim of verified physical
   extent. This is the claim this project proposes to test (RQ in §9) and it is
   answerable with data that actually exists.

### 5.8 Literature matrix (verified)

| Reference | Task / method | Dataset | Relevant claim (sourced or verified) |
|---|---|---|---|
| CarDD [1] | detection + instance seg | CarDD (4,000 img / 9k+ inst) | First public large-scale car damage seg dataset; 6 classes |
| VehiDE [2][3] | seg + detection + SOD | VehiDE (13,945 img / 32k+ inst / 8 classes) | Public large-scale damage seg dataset |
| CrashCar101 [4] | part + damage seg | 101,050 synthetic crash imgs | Procedural synthetic masks; real-data complement |
| CDA-Net [5] | detection + severity | 11,380 damage imgs (IN market) | Applied YOLOv5 severity pipeline |
| MVA-CDD [6] | multi-view detection | (per paper) | Active multi-view damage research |
| Three-quarter-view [21] | severity classification | three-quarter-view car damage | Public severity/classification damage resource |
| C-DiffDet+ [22] | anomaly + YOLOv8 + severity | 2022 Daedalus, others | 2024–2025 generative + detector trend |
| ALBERT [7] | transformer instance seg | 26 damage / 7 fake / 61 parts | Transformer automotive seg with fake-damage disambiguation |
| U-Net [8] | seg encoder-decoder | — | Canonical small-data seg architecture; our baseline's ancestor |
| DeepLabv3 [9] | seg with atrous conv | — | Widely reused seg backbone |
| Mask R-CNN [10] | instance seg | — | CarDD paper's reference model |
| HRNet [11] | high-res multi-branch | — | Spatial-detail-preserving backbone |
| ViT [12] | patch-sequence transformer | — | Basis of segmentation transformers |
| SETR [13] | transformer seg encoder | — | ViT-as-encoder segmentation |
| SegFormer [14] | hierarchical transformer seg | — | Prior report's suggested vision backbone |
| TransUNet [15] | CNN+transformer hybrid | — | Bottleneck-transformer hybrid; direct antecedent of CarddHybrid |
| YOLOv8 [16] | detection + seg (software) | — | Open-source software; no peer-reviewed paper |
| Kendall & Gal [17] | aleatoric vs epistemic UQ | — | Uncertainty taxonomy used by the honesty contract |
| MC Dropout [18] | epistemic UQ | — | Test-time dropout uncertainty approximation |
| Deep Ensembles [19] | epistemic UQ | — | Ensemble-variance uncertainty |
| Hasan et al. [20] | systematic review (55 papers) | — | Confirms saturated detection/classification literature |

*(inference):* table rows beyond the sourced claims are the project's own
integration of these works into RQ and design, not claims made by the sources.

### 5.9 Synthesis for this project

*(inference, argued from the reviewed sources):*

1. **Data, not method, is the honest constraint.** Every benchmark worth
   reproducing here — CarDD, VehiDE, CrashCar101 — is segmentation or
   detection-shaped, and public. No public, licence-clear dataset carries
   observed repair costs or part masks; so the honest research question must be
   *where is the damage and how sure can we be*, not *what will it cost*
   (§9 RQ1/RQ2, ADR 0011).
2. **The hybrid direction is contemporary and bounded.** TransUNet-style
CNN+transformer hybrids [15], ALBERT [7], and diffusion-plus-detector
    frameworks [22] all signal that attention at a bottleneck is an accepted,
    GPU-bounded upgrade; this is exactly the CarddHybrid design (ADR 0010),
    now trained and measured (val mIoU 0.0504 / test 0.0586, §10 H1) but still
    underfit — a hypothesis with first evidence, not a settled result.
3. **Confidence honesty is the differentiator the field does not publish.**
   Detectors and classifiers are saturated (Hasan et al. [20]); calibration and
   failure—flagging are under-reported. The low_confidence flag (§5.6, §16.1) is
   a small, testable, honest contribution a capstone can actually measure.

## **6\. Research Landscape**

+--------------------------------------+--------------------------------------+
|  Computer Vision Segmentation        |  Uncertainty / Confidence Labelling |
|  (U-Net, SegFormer, TransUNet,       |  (MC Dropout, Deep Ensembles,       |
|  CarDD, VehiDE, CrashCar101)         |  Kendall & Gal taxonomy)            |
+------------------+-------------------+------------------+-------------------+
|  "Where is the   |  ----> proposed contribution ---->   | "How honest can  |
|   damage?"       |  CNN+Transformer hybrid (CarddHybrid)  |  we be?"         |
|  (saturated)     |  vs U-Net baseline, with honest labels |  (active)        |
+------------------+---------------------------------------+------------------+

- **Saturated sub-domains:** single-image damage classification (scratch vs dent
  via a pre-trained classifier); bounding-box detection.
- **Active / developing:** pixel-level damage segmentation (CarDD [1], VehiDE
  [2]), part+damage segmentation (ALBERT [7]), synthetic crash data
  (CrashCar101 [4]).
- **Gap this project pursues:** a reproducible, GPU-bounded CNN+Transformer
  hybrid segmentation benchmark on CarDD with an honesty contract that never
  over-claims. *(inference.)*

## **7\. Dataset Analysis**

+-------------------------------------------------------------------------------------------------------+
|                                    PUBLIC DATASET BENCHMARK SUMMARY                                    |
+--------------------+---------+----------------------------+--------------------------------+-----------+
| Dataset Name       | Images  | Annotation Type            | Primary Classes                | Verified? |
+--------------------+---------+----------------------------+--------------------------------+-----------+
| CarDD (2023) [1]   | 4,000   | Polygon instance mask      | Dent, Scratch, Crack, Glass,   | **YES**   |
|                    |         |                            | Lamp, Tire                     |           |
| VehiDE (2023) [2]  | 13,945  | Detection + seg + SOD      | 8 damage categories            | **YES**   |
| CrashCar101 (2024) | 101,050 | Synthetic pixel mask       | Part + damage, severity levels | **YES**   |
| [4]                |         |                            |                                |           |
| "CDD (2025)"       | 12,000  | Polygon mask               | 26 damage, 61 parts            | **NO**    |
| (as previously     |         |                            |                                | (restated, |
| listed)            |         |                            |                                | UNVERIFIED)|
| "Insurance-        | n/a     | open image resource        | damage types                   | **NO**    |
| Damage-v2"         |         | (Kaggle/Roboflow style)    |                                | (UNVERIFIED)|
+--------------------+---------+----------------------------+--------------------------------+-----------+

### Dataset construction protocol (this project)

> 1. **Visual ground truth:** CarDD-COCO only (REAL GROUND TRUTH). Official
>    split policy: train 2,816 / val 810 / test 374, preserved exactly; test
>    split touched once at the end.
> 2. **Metadata / cost augmentation:** **not done.** CarDD has no make, model,
>    year, repair action, or observed cost. Adding a synthetic price table would
>    be a SYNTHETIC LABEL and is out of scope (ADR 0011).
> 3. **Damage representation:** image-denominator area ratio
>    `damaged_pixels / total_image_pixels` per class (DERIVED FEATURE, ADR 0005 /
>    0009). Physical cm² requires part masks and calibration that do not exist.

## **8\. Recommended ML/DL Architecture**

                                  [Input Photo 512x512]
                                         |
                                         v
                         +-------------------------------+
                         |  CNN Encoder (4 stages)       |
                         |  base 32 -> 32, 64, 128, 256  |
                         |  blocks enc1..enc4            |
                         +---------------+---------------+
                                         |
                                         v  (32x32 feature map)
                         +-------------------------------+
                         |  Transformer Bottleneck       |
                         |  d_model = base*8 = 256,      |
                         |  4 heads, 2 layers,           |
                         |  sinusoidal pos. encoding     |
                         +---------------+---------------+
                                         |
                                         v
                         +-------------------------------+
                         |  CNN Decoder with skips       |
                         |  dec4/dec3/dec2/dec1          |
                         |  1x1 head -> 7 classes        |
                         +---------------+---------------+
                                         |
                                         v
                         +-------------------------------+
                         |  argmax mask + softmax conf.  |
                         |  -> Evidence payload +        |
                         |  low_confidence honesty flag  |
                         +-------------------------------+

- **Proposed model `CarddHybrid`** (ADR 0010, `ml/models/cardd_hybrid.py`):
  CNN encoder → transformer bottleneck → CNN decoder with skips; ~3.2 M params
  (measured 3,206,855); same contract as the U-Net baseline.
- **Baseline `CarddUNet`** (ADR 0006, `ml/models/cardd_unet.py`): plain U-Net,
  same API, ~1.93 M params at base 32 (baseline run used base 64).
- Both decode with **softmax cross-entropy over the argmax class target** (ADR
  0008 — the objective and metric decode are identical).
- **Honesty layer:** the engine labels masks MODEL PREDICTION, attaches measured
  mean confidence, sets `low_confidence` below thresholds, and refuses to claim
  severity or physical area.

## **9\. Research Questions**

> 1. **RQ1 (segmentation quality):** Does the CNN+Transformer hybrid
>    (`CarddHybrid`) achieve higher damage-segmentation quality (mIoU, Dice,
>    pixel accuracy, small-damage slice) than the plain U-Net baseline
>    (`CarddUNet`) on CarDD, on identical splits, seed, and training schedule?
> 2. **RQ2 (confidence honesty):** How honestly can the models label their own
>    confidence — how well does the `low_confidence` / mean-confidence signal
>    separate images where the predicted mask agrees with CarDD ground truth
>    from images where it does not? *(Operational measure to be defined and
>    locked in the experiment config before any claim.)*
> 3. **RQ3 (representation honesty):** Can the system describe its evidence —
>    per-class image-denominator area ratios and predicted-mask overlays —
>    without claiming physical area, hidden damage, repair action, or cost?

The previous RQs (physical-area-driven cost MAE; cross-attention metadata
fusion; hidden-damage likelihood; quantile-loss coverage) are **rescinded** with
the photo-first scope (ADR 0011) because they required data that does not exist
outside SYNTHETIC LABEL.

## **10\. Hypotheses**

* **H1 (tested, 2026-09-21, `cardd_hybrid_ce`):** `CarddHybrid` improves
  validation mean IoU over the `cardd_baseline_ce` numbers (val mIoU 0.0475,
  MEASURED) on the same schedule. Measured after a 5-epoch run on the same
  harness: **val mIoU 0.0504 / test mIoU 0.0586** (MEASURED, `registry.json`
  id `cardd_hybrid_ce-20260921-162128`). That is a weak positive on the
  aggregate, but the hybrid remains clearly underfit and the small-damage
  slice is ≈ 0; the model is **not** presented as ready damage evidence.
* **H2 (method, not result):** small-damage IoU (slice ≤ train p25 ≈ 3,013.5 px
  @512, MEASURED) is the binding constraint on damage-feature trust for both
  architectures; improvements should be reported on that slice explicitly.
  Measured slice IoU for the hybrid: val 0.0002 / test 0.0003 — the constraint
  binds for both architectures.
* **H3 (open):** whether the hybrid's added capacity changes the honesty
  trade-off (precision vs confidence) is an empirical question, not a prior.

> **Addendum — 2026-09-22 15-epoch pilots (preliminary validation, not a
> conclusion).** The legacy `cardd_hybrid_ce` demo checkpoint is superseded by
> the architecture-spec v3 research models. Two 15-epoch pilots (seed 0, full
> official CarDD splits, identical schedule) were run as an intermediate check:
> `pilot15_baseline` (`ResNet34UNet`) reached **foreground mIoU 0.6127 /
> mDice 0.7440 / pixel accuracy 0.8979**, and `pilot15_hybrid`
> (`HybridSegmentation`) reached **foreground mIoU 0.5963 / mDice 0.7320 /
> pixel accuracy 0.8873** (@ epoch 14, both still improving; EMA weights; seeds
> 0/1/2 not yet run). These are preliminary validation observations only — they
> do **not** establish that either architecture is superior, and no statistical
> significance is claimed. The planned full comparison remains the 60-epoch,
> 3-seed experiment (Task 24). The demo default is `pilot15_hybrid` per the
> research plan; `pilot15_baseline` is retained as the controlled baseline arm.

## **11\. Baselines**

> 1. **Baseline 1 (vision-only segmentation, current):** `CarddUNet` trained
>    with softmax CE on CarDD (5 epochs, seed 0, official splits) — best val
>    mIoU 0.0475 / test 0.0500 (MEASURED, underfit).
> 2. **Baseline 2 (same harness, more epochs):** the U-Net extended beyond 5
>    epochs on the same harness, to separate "architecture effect" from
>    "underfitting effect" before comparing with the hybrid.
> 3. **Proposed / measured contrast (A3):** `CarddHybrid` trained under the same
>    harness, schedule, seed, and split policy. Measured val mIoU 0.0504 /
>    test mIoU 0.0586 (see H1 above). The hybrid narrowly beats the CE
>    baseline on aggregate; several minority classes remain at IoU 0.

Former baselines ("object detector + fixed heuristic cost", "vision + MLP
concat + metadata", "cross-attention fusion") are removed with the cost scope.

## **12\. Experimental Design**

The locked configuration in `archive/docs/segmentation-experiment-config.md`
(Phase 6, historical) governs the original baseline; the architecture spec
`docs/architecture/cnn-transformer-segmentation.md` (v3) supersedes it, and the
15-epoch pilot runs record their own (identical-schedule) config per experiment:

| Item | Value |
|---|---|
| Dataset / splits | CarDD-COCO official train/val/test (2,816 / 810 / 374) |
| Input | RGB 512×512, batch 2 (VRAM-measured: base 64 @ batch 2 = 2.85 GB peak) |
| Loss | softmax cross-entropy over argmax class target (ADR 0008) |
| Optimizer / scheduler | Adam lr 1e-3, wd 1e-5; CosineAnnealingLR |
| Augmentation (train only) | hflip + mild brightness/contrast; none on val/test |
| Seed / epochs | seed 0; 5 epochs (extendable on the same harness) |
| Checkpoint rule | best validation mean IoU; checkpoint carries `model_arch` |
| Test protocol | test197 split evaluated once, after selection |
| Records | `run_record.json` + `registry.json` (git-ignored); commit docs reference IDs |

Trail: `cardd_hybrid_ce` (ACTIVE, trained 2026-09-21, val mIoU 0.0504 /
test mIoU 0.0586) has been compared against `cardd_baseline_ce` (SUPERSEDED).
The written `research_summary.md` for the head-to-head is still pending; the
claim level above is limited to the MEASURED numbers.

## **13\. Ablation Study Design**

+-----+----------------------------------------------+--------------------------+
| Exp | Configuration                                 | Target insight           |
+-----+----------------------------------------------+--------------------------+
| A1  | CarddUNet, 5 ep (existing `cardd_baseline_ce`) | Baseline reference       |
| A2  | CarddUNet, extended schedule                  | Underfit vs architecture |
| A3  | CarddHybrid, same schedule as A1              | Hybrid effect (isolate)  |
|     |                                            — (DONE 2026-09-21: val mIoU 0.0504, test 0.0586) |
| A4  | CarddHybrid, extended schedule                | Best affordable run      |
| A5  | (optional) transformer bottleneck ablated     | Contribution of attention|
+-----+----------------------------------------------+--------------------------+

Each ablation: same splits, seed, metric harness, honesty flags. No ablation is
claimed until its run exists in the registry.

## **14\. Evaluation Metrics**

+----------------------------+-----------------------+-------------------------------+
| Task / Module              | Primary Metric        | Secondary Metric              |
+----------------------------+-----------------------+-------------------------------+
| Damage segmentation        | val/test mean IoU     | per-class IoU/Dice, mDice     |
| Small-damage slice         | slice IoU (≤ p25)     | slice Dice / P / R            |
| Pixel-level discrimin.     | pixel accuracy        | per-class precision/recall    |
| Confidence honesty (RQ2)   | agreed-vs-disagreed   | low-flag rate; separation     |
|                            | confidence separation | (operational metric, RQ2)     |
| Qualitative               | input / GT / prediction / overlay montages | error-analysis report |

Labels: masks = MODEL PREDICTION; ratios = DERIVED FEATURE; background excluded
from mean scores; absent classes score 0.0. No cost/severity metric exists
because no such task exists.

## **15\. Limitations and Risks**

> 1. **Domain shift & capture quality:** glare, blur, darkness, low contrast can
>    fail the quality gate or degrade masks — the gate exists, and its rejection
>    path returns `QUALITY_FAILED` guidance rather than a fake mask.
> 2. **Underfitting / small damage:** the 5-epoch baseline misses most small
>    damage (slice ≈ 0, MEASURED); both models are expected to underperform on
>    crack/dent until trained properly.
> 3. **No physical ground truth:** one uncontrolled photo has no scale; physical
>    area (cm²), hidden damage, repair action, and cost are permanently out of
>    scope unless real labelled data arrives (ADR 0004/0011).
> 4. **Synthetic-data caveat:** CrashCar101-class procedurally generated data can
>    augment training but is not real-world validation evidence.
> 5. **Single-photo scope:** multi-view (MVA-CDD [6]) and 3-D reconstructions are
>    out of scope.

## **16\. Ground-Truth and Honesty Policy**

Categories (ADR 0004) MUST stay distinct in code, data, docs, and UI:

| Category | Meaning | Examples in this project |
|---|---|---|
| REAL GROUND TRUTH | Measured/verified by trusted source | CarDD COCO mask labels |
| WEAK LABEL | Approximate, noisy/indirect source | (none in current data) |
| SYNTHETIC LABEL | Rule/simulation/model-generated | none remaining in the API after ADR 0011 |
| DERIVED FEATURE | Computed, not observed | `damaged_pixels / total_image_pixels` |
| MODEL PREDICTION | Model output | segmentation mask, confidence, `low_confidence` |
| ASSUMPTION | Team choice, not evidence | part-ratio limitation (ADR 0005/0009) |

Enforced facts: a rule-generated cost table is **not** real cost ground truth;
a synthetic repair-price or damage label is **not** validated evidence; physical
area in cm² is never claimed from uncontrolled photos; the overlay is always the
*predicted* mask; consent samples store only MODEL_SUGGESTED provenance and a
placeholder mask, never validated extent.

### 16.1 Confidence honesty (RQ2) — design intent

*(inference/proposal, to be locked):* the honest signal is the engine's mean
pixel-confidence and the `low_confidence` flag below thresholds
(`min_mean_confidence`, `min_damage_fraction`). The proposed operational
definition for RQ2 is the separation between the confidence distribution over
images where the predicted mask agrees with CarDD ground truth and the
distribution over images where it does not. This operationalization is PLANNED
and must be written into the locked experiment config before any number is
reported.

## **17\. Publication / Capstone Status**

- **Capstone deliverables:** research report + `AutoInspect-X_Capstone.pptx`
  (2026-09-07) + `AUTOINspectX_PROJECT_STATE.md` + this repo.
- **Demo product:** complete to Phase R (photo-first chat UI + API + engine +
  storage + CI), with the honesty contract enforced by tests.
- **Academic experiment:** `cardd_hybrid_ce` trained and verified end-to-end
  2026-09-21 (val mIoU 0.0504 / test mIoU 0.0586, MEASURED). The head-to-head
  `research_summary.md` and the RQ2 operational definition remain open; no
  publication-facing quality claim is made beyond the measured numbers. Not
  submitted anywhere (UNVERIFIED / not claimed).

## **18\. Recommended Final Scope**

Focus the student capstone on **single-photo passenger-vehicle exterior damage
segmentation**, comparing a **CNN+Transformer hybrid (CarddHybrid)** against the
**plain U-Net baseline (CarddUNet)** on the CarDD dataset under a locked,
reproducible schedule, evaluated on segmentation quality **and** confidence
honesty, and presented through a photo-first chat demo whose interface separates
MODEL PREDICTION from anything else.

## **19\. Final Verdict**

### A. Is AutoInspect-X worth pursuing?

**YES, WITH HONESTY CONSTRAINTS.**

### B. Why?

The defensible contribution is a reproducible CNN+Transformer hybrid
segmentation benchmark on CarDD with an evidence-labelling honesty contract — 
a question that is answerable with data that exists, on a 4 GB GPU, and that
cannot be falsely presented as repair-cost truth. The earlier multimodal-cost
version was high-ambition but data-blocked; the photo-first version is
high-integrity and completable.

## **References**

Verified during the 2026-09-21 revision against publisher / arXiv / project
pages unless flagged:

- [1] Wang, X., Li, W., Wu, Z. "CarDD: A New Dataset for Vision-Based Car Damage
  Detection." *IEEE Transactions on Intelligent Transportation Systems*, vol. 24,
  no. 7, pp. 7202–7214, July 2023. DOI 10.1109/TITS.2023.3258480; arXiv:2211.00945.
  (Note: the previous version of this report cited a different DOI,
  TITS.2022.3225828, pointing at a GitHub page; the correct DOI is the one above
  — verified against the CarDD project page. Material correction.)
- [2] Huynh, N. T., Tran, N. N. D., Huynh, A. T., Hoang, V.-D., Nguyen, H. D.
  "VehiDE Dataset: New Dataset for Automatic Vehicle Damage Detection in Car
  Insurance." 15th Int. Conf. on Knowledge and Systems Engineering (KSE), 2023,
  pp. 1–6.
- [3] Hoang, V.-D., Huynh, N. T., et al. "Powering AI-driven car damage
  identification based on VeHIDE dataset." *Journal of Information and
  Telecommunication*, vol. 9, no. 1 (2025). DOI 10.1080/24751839.2024.2367387.
- [4] Parslov, J., Riise, E., Papadopoulos, D. P. "CrashCar101: Procedural Crash
  Car Dataset for Damage Detection and Segmentation." *WACV 2024*. arXiv:2311.06536.
- [5] Bhogale, S., et al. "CDA-Net: Computer Vision based Automatic Car Damage
  Analysis." ACM ICC3, 2023. DOI 10.1145/3627631.3627662.
- [6] Peng, J., et al. "Car Damage Detection Based on Multi-View Fusion …"
  IEEE, 2025.
- [7] Panboonyuen, T. "ALBERT: Advanced Localization and Bidirectional Encoder
  Representations from Transformers for Automotive Damage Evaluation."
  arXiv:2506.10524, 2025.
- [8] Ronneberger, O., Fischer, P., Brox, T. "U-Net: Convolutional Networks for
  Biomedical Image Segmentation." MICCAI 2015. arXiv:1505.04597.
- [9] Chen, L.-C., Papandreou, G., Schroff, F., Adam, H. "Rethinking Atrous
  Convolution for Semantic Image Segmentation." arXiv:1706.05587, 2017.
- [10] He, K., Gkioxari, G., Dollár, P., Girshick, R. "Mask R-CNN." ICCV 2017.
  arXiv:1703.06870.
- [11] Wang, J., et al. "Deep High-Resolution Representation Learning for Visual
  Recognition." *IEEE TPAMI*, 2020. arXiv:1908.07919.
- [12] Dosovitskiy, A., et al. "An Image is Worth 16×16 Words: Transformers for
  Image Recognition at Scale." ICLR 2021. arXiv:2010.11929.
- [13] Zheng, S., et al. "Rethinking Semantic Segmentation from a Sequence-to-Sequence
  Perspective with Transformers (SETR)." CVPR 2021. arXiv:2012.15840.
- [14] Xie, E., Wang, W., Yu, Z., Anandkumar, A., Alvarez, J. M., Luo, P.
  "SegFormer: Simple and Efficient Design for Semantic Segmentation with
  Transformers." NeurIPS 2021. arXiv:2105.15203.
- [15] Chen, J., Lu, Y., Yu, Q., et al. "TransUNet: Transformers Make Strong
  Encoders for Medical Image Segmentation." arXiv:2102.04306, 2021.
- [16] Jocher, G., Chaurasia, A., Qiu, J. "Ultralytics YOLOv8." Software,
  GitHub: ultralytics/ultralytics, released 2023-01-10. (Software release, not
  a peer-reviewed paper.)
- [17] Kendall, A., Gal, Y. "What Uncertainties Do We Need in Bayesian Deep
  Learning for Computer Vision?" NeurIPS 2017. arXiv:1703.04977.
- [18] Gal, Y., Ghahramani, Z. "Dropout as a Bayesian Approximation:
  Representing Model Uncertainty in Deep Learning." ICML 2016. arXiv:1506.02142.
- [19] Lakshminarayanan, B., Pritzel, A., Blundell, C. "Simple and Scalable
  Predictive Uncertainty Estimation using Deep Ensembles." NeurIPS 2017.
  arXiv:1612.01474.
- [20] Hasan, M. J., et al. "Vehicle Damage Detection Using Artificial
  Intelligence: A Systematic Literature Review." *WIREs Data Mining and
  Knowledge Discovery*, vol. 15, no. 2, e70027, 2025. DOI 10.1002/widm.70027.
- [21] Lee, D., Lee, J., Park, E. "Automated vehicle damage classification using
  the three-quarter view car damage dataset and deep learning approaches."
  *Heliyon*, vol. 10, no. 14, e34016, 2024. DOI 10.1016/j.heliyon.2024.e34016.
- [22] Sellam, M., et al. "C-DiffDet+: Unsupervised Anomaly Detection and
  Detection of Vehicle Damage." arXiv:2509.00578, 2025.

**Retained but UNVERIFIED (do not cite as evidence):** "CDD (2025)" — the
12,000-image / 61-part / 26-damage dataset as previously listed could not be
verified; its damage/part counts coincide with ALBERT's dataset description [7].
"Insurance-Damage-v2" — no academic citation could be verified.