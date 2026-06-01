# FOMO300K — Local workspace

Working copy for exploring and replicating the **minimal preprocessing** described in the FOMO300K paper ([arXiv:2506.14432](https://arxiv.org/pdf/2506.14432)).

## Data location

Raw NIfTI data on this machine:

```text
/data/users/fomo2026/FOMO300K/
```

| Item | Path |
|------|------|
| 36 constituent datasets | `PT001_*` … `PT036_*` |
| Global metadata | `participants.tsv`, `mapping.tsv`, `mri_info.tsv` |
| Hugging Face cache | `/data/users/fomo2026/hf-cache/` |

**Scale (v1.1):** 58,741 subjects · 81,195 sessions · 306,207 scans.

## Dataset layout

Modified BIDS: each scan is a `.nii.gz` under `sub-*/ses-*/` (OpenNeuro uses `ds*` folders under `PT030_OpenNeuro/`).

```
PT001_ClevelandCCF/sub-01/ses-01/t1w.nii.gz
```

Unknown sequence type → `scan.nii.gz`.

On this machine, many sessions are stored as **`sub-XX/ses-YY.zip`** archives (not extracted `.nii.gz`). The preprocessing pipeline reads NIfTI directly from these zips.

## Modalities per constituent dataset

Derived from `mri_info.tsv` filenames (BIDS suffix before `.nii.gz`). The collection is **centered on T1-weighted anatomy** but includes many other sequences; not every file is named `T1w`.

| Dataset | Scans | Explicit `T1w`? | Other modality families |
|---------|------:|-----------------|-------------------------|
| PT001 ClevelandCCF | 31 | Yes (all) | T1w only |
| PT002 Nigerian Clinical | 701 | Yes (397) | T2w, FLAIR, DWI |
| PT003 CUNMET | 173 | Yes (59) | ASL |
| PT004 ACPI | 163 | Yes (all) | T1w only |
| PT005 ADHD-200 | 973 | **No** | `scan` only |
| PT006 AHEAD | 420 | Yes (105) | T1 maps, R1/R2* maps |
| PT007 ATAG | 583 | **No** | MP2RAGE, FLASH |
| PT008 Adolescent Brain Dev | 905 | Yes (226) | T2w, DWI, ASL |
| PT009 BraTS-GEN | 10,448 | Yes (2,612) | T2w, FLAIR, T1c |
| PT010 BrainLat | 2,211 | Yes (1,173) | FLAIR, DWI |
| PT011 CFMM 7T | 160 | **No** | MP2RAGE only |
| PT012 CHBMP | 901 | Yes (203) | DWI |
| PT013 Calgary Preschool | 1,629 | **No** | `scan`, DWI, ASL |
| PT014 CoRR | 5,831 | **No** | `scan`, DWI, ASL |
| PT015 MSD Brain Tumor | 3,000 | Yes (750) | T2w, FLAIR, T1c |
| PT016 GSP | 1,708 | Yes (1,707) | DWI (1 scan) |
| PT017 HBN-SSI | 1,031 | Yes (180) | T2w, DWI |
| PT018 HBN | 26,097 | Yes (8,242) | T2w, PDw, FLAIR, SWI/MTR, DWI |
| PT019 HCP Test-Retest | 1,460 | Yes (75) | T2w, DWI |
| PT020 HCP Wu-Minn | 38,311 | Yes (1,762) | T2w, DWI |
| PT021 IXI | 3,105 | Yes (581) | T2w, PDw, DWI, angio |
| PT022 Beijing Enhanced | 540 | Yes (180) | DWI |
| PT023 Infant Dev Brain | 1,666 | Yes (833) | T2w |
| PT024 M4Raw | 2,230 | Yes (699) | T2w, FLAIR, GRE |
| PT025 age-ility | 1,179 | Yes (131) | DWI |
| PT026 MICA MICs | 649 | Yes (99) | MP2RAGE, T1map, DWI |
| PT027 NKI | 10,658 | Yes (2,456) | T2w, FLAIR, DWI |
| PT028 OASIS1 | 1,688 | Yes (all) | T1w only |
| PT029 OASIS2 | 2,113 | Yes (all) | T1w only |
| PT030 OpenNeuro | 140,389 | Yes (47,290) | T2w, FLAIR, T1c, DWI, ASL, MP2RAGE, PDw, SWI, angio, `scan`, … |
| PT031 SLIM | 3,096 | Yes (1,037) | DWI, some `scan` |
| PT032 Tao Wu | 40 | Yes (all) | T1w only |
| PT033 WAND | 7,132 | Yes (658) | MP2RAGE, T2w, DWI, ASL, angio, GRE |
| PT034 Wayne | 610 | Yes (all) | T1w only |
| PT035 Yale Brain Mets | 33,800 | Yes (171) | Mostly FLAIR, T1c, T2w, `scan` |
| PT036 Yale HighRes | 576 | Yes (all) | T1w only |

**Notes**

- **T1w-only (7):** PT001, PT004, PT028, PT029, PT032, PT034, PT036.
- **No explicit `T1w` suffix (5):** PT005 (`scan`), PT007/PT011 (MP2RAGE/FLASH), PT013/PT014 (`scan` + DWI/ASL). These may still be T1-weighted structurally.
- **T1-like suffixes** (not counted as `T1w` above): `MP2RAGE`, `FLASH`, `gre`, `T1map`, `UNIT1`, etc.
- **PT030** aggregates ~880 OpenNeuro sub-datasets; ~31 sub-datasets have no `T1w` file.

Regenerate this table:

```bash
python scripts/summarize_modalities.py
```

## Minimal preprocessing (paper)

All MRI scans were minimally preprocessed for consistent orientation and comparable 3D dimensionality.

### Common steps (all scans)

1. **RAS reorientation** — Right–Anterior–Superior.
2. **4D → 3D** — 4D volumes are reduced to 3D (sequence-specific rules below).
3. **Slice filter** — Discard volumes with **&lt; 15 slices** (insufficient anatomical coverage).

### DWI

For diffusion data with multiple gradient directions:

1. **b0 reference** — If a b=0 or near-b0 volume exists (**b ≤ 5**), extract and save separately as the non-DW reference.
2. **Shell grouping** — Remaining DW volumes grouped into b-value shells (|**bᵢ − bⱼ**| ≤ **50**).
3. **Axis-aligned selection** — Per shell, pick 3 volumes whose gradient directions are closest to canonical **+x, +y, +z** (cosine similarity).
4. **Two strategies (50% / 50% of scans)** for SSL variability:
   - **Mean:** average the three axis-aligned volumes → one 3D shell image.
   - **Trace ADC:** using b0 reference **S₀** and axis signals **Sᵢ**, b-values **bᵢ**:

     \[
     \text{Trace} = \mathrm{ADC}_x + \mathrm{ADC}_y + \mathrm{ADC}_z,\quad
     \mathrm{ADC}_i = -\frac{1}{b_i}\ln\frac{S_i}{S_0}
     \]

     Voxels included only if **S₀ &gt; 0**, **Sᵢ &gt; 0**, **Sᵢ ≤ S₀**, with **Sᵢ/S₀** clipped to **[10⁻¹⁰, 1.0]** before `log`; others set to 0 for that direction.

5. **No b0** — If no b0/near-b0 exists, **average** the three axis-aligned volumes instead.

Released FOMO300K often stores DWI as separate files (`bval0`, `bval1000`, …) rather than one 4D stack; the pipeline supports both layouts.

### Perfusion (e.g. ASL)

| Channels | Rule |
|----------|------|
| **&gt; 3** | Average all channels (e.g. multiple M0). |
| **2 or 3** | Perfusion-weighted = **last − first** channel. |

### Implementation in this repo

```text
preprocessing/
  config.py          # paths, thresholds
  io_utils.py        # load NIfTI from .nii.gz or ses-XX.zip
  orientation.py     # RAS + slice count
  dwi.py             # shells, axis pick, mean / trace ADC
  perfusion.py       # channel rules
  anatomical.py      # single 3D anatomical volumes
  pipeline.py        # orchestration
scripts/
  run_preprocess.py
  summarize_modalities.py
```

### Quick start

```bash
cd /shared/home/akshatha/FOMO300K
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Dry-run one session
python scripts/run_preprocess.py \
  --input /data/users/fomo2026/FOMO300K/PT001_ClevelandCCF \
  --output /shared/home/akshatha/FOMO300K/preprocessed \
  --limit 5 \
  --dry-run

# Process one dataset (writes preprocessed NIfTI; use .venv/bin/python if venv active)
python scripts/run_preprocess.py \
  --input /data/users/fomo2026/FOMO300K/PT001_ClevelandCCF \
  --output /shared/home/akshatha/FOMO300K/preprocessed
```

Environment overrides: `FOMO300K_DATA_ROOT`, `FOMO300K_OUTPUT_ROOT`.

## Citation

```bibtex
@article{Cerri2026large,
  title={A large-scale heterogeneous 3D magnetic resonance brain imaging dataset for self-supervised learning},
  author={Cerri, Stefano and Munk, Asbj{\o}rn and Llambias, Sebastian N{\o}rgaard and Ambsdorf, Jakob and Machnio, Julia and Nersesjan, Vardan and Hedeager Krag, Christian and Liu, Peirong and Rocamora Garc{\'\i}a, Pablo and Mehdipour Ghazi, Mostafa and Boesen, Mikael and Benros, Michael Eriksen and Iglesias, Juan Eugenio and Nielsen, Mads},
  journal={arXiv preprint arXiv:2506.14432},
  year={2026},
  url={https://arxiv.org/abs/2506.14432}
}
```
