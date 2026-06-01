# Data

## Local path

```text
/data/users/fomo2026/FOMO300K/
```

| | |
|--|--|
| Constituent datasets | `PT001_*` … `PT036_*` (36 folders) |
| Metadata | `participants.tsv`, `mapping.tsv`, `mri_info.tsv` |
| Scale (v1.1) | 58,741 subjects · 81,195 sessions · 306,207 scans |

## Layout

Modified BIDS. Sessions are often **`sub-XX/ses-YY.zip`** (NIfTI inside); the preprocessor reads zips directly.

```
PT001_ClevelandCCF/sub-01/ses-01.zip  →  …/anat/sub-01_ses-01_T1w.nii.gz
```

Unknown sequence → `scan.nii.gz`. OpenNeuro: `PT030_OpenNeuro/ds*/`.

## Modalities per dataset

From `mri_info.tsv` filenames. T1-weighted–centric, but not every scan is named `T1w`.

| Dataset | Scans | `T1w`? | Other families |
|---------|------:|--------|----------------|
| PT001 ClevelandCCF | 31 | All | — |
| PT002 Nigerian Clinical | 701 | 397 | T2w, FLAIR, DWI |
| PT003 CUNMET | 173 | 59 | ASL |
| PT004 ACPI | 163 | All | — |
| PT005 ADHD-200 | 973 | No | `scan` only |
| PT006 AHEAD | 420 | 105 | T1/R1/R2* maps |
| PT007 ATAG | 583 | No | MP2RAGE, FLASH |
| PT008 Adolescent Brain Dev | 905 | 226 | T2w, DWI, ASL |
| PT009 BraTS-GEN | 10,448 | 2,612 | T2w, FLAIR, T1c |
| PT010 BrainLat | 2,211 | 1,173 | FLAIR, DWI |
| PT011 CFMM 7T | 160 | No | MP2RAGE |
| PT012 CHBMP | 901 | 203 | DWI |
| PT013 Calgary Preschool | 1,629 | No | `scan`, DWI, ASL |
| PT014 CoRR | 5,831 | No | `scan`, DWI, ASL |
| PT015 MSD Brain Tumor | 3,000 | 750 | T2w, FLAIR, T1c |
| PT016 GSP | 1,708 | 1,707 | DWI (1) |
| PT017 HBN-SSI | 1,031 | 180 | T2w, DWI |
| PT018 HBN | 26,097 | 8,242 | T2w, PDw, FLAIR, SWI, DWI |
| PT019 HCP Test-Retest | 1,460 | 75 | T2w, DWI |
| PT020 HCP Wu-Minn | 38,311 | 1,762 | T2w, DWI |
| PT021 IXI | 3,105 | 581 | T2w, PDw, DWI, angio |
| PT022 Beijing Enhanced | 540 | 180 | DWI |
| PT023 Infant Dev Brain | 1,666 | 833 | T2w |
| PT024 M4Raw | 2,230 | 699 | T2w, FLAIR, GRE |
| PT025 age-ility | 1,179 | 131 | DWI |
| PT026 MICA MICs | 649 | 99 | MP2RAGE, T1map, DWI |
| PT027 NKI | 10,658 | 2,456 | T2w, FLAIR, DWI |
| PT028 OASIS1 | 1,688 | All | — |
| PT029 OASIS2 | 2,113 | All | — |
| PT030 OpenNeuro | 140,389 | 47,290 | T2w, FLAIR, T1c, DWI, ASL, … |
| PT031 SLIM | 3,096 | 1,037 | DWI, `scan` |
| PT032 Tao Wu | 40 | All | — |
| PT033 WAND | 7,132 | 658 | MP2RAGE, T2w, DWI, ASL, angio |
| PT034 Wayne | 610 | All | — |
| PT035 Yale Brain Mets | 33,800 | 171 | FLAIR, T1c, T2w, `scan` |
| PT036 Yale HighRes | 576 | All | — |

**T1w-only:** PT001, PT004, PT028, PT029, PT032, PT034, PT036.

Regenerate: `python scripts/summarize_modalities.py`
