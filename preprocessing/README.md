# Preprocessing

Stage 1 for **[FOMO26](https://zenodo.org/records/19714192)**: paper-aligned minimal preprocessing → consistent RAS 3D volumes for SSL.

```text
Raw FOMO300K → preprocessing/ → SSL (planned) → downstream seg / cls / reg (planned)
```

## Run

```bash
# from repo root, venv active
python scripts/run_preprocess.py \
  --input /data/users/fomo2026/FOMO300K/PT001_ClevelandCCF \
  --output ../preprocessed \
  --limit 5 --dry-run
```

Env: `FOMO300K_DATA_ROOT`, `FOMO300K_OUTPUT_ROOT`

## Paper rules (summary)

| Step | Rule |
|------|------|
| All scans | RAS orientation; 4D→3D; drop if &lt; 15 slices |
| DWI | Extract b0 (b≤5); group shells (Δb≤50); pick 3 axis-aligned directions; 50% mean of 3 vols, 50% trace ADC; no b0 → mean |
| Perfusion | &gt;3 channels → mean; 2–3 channels → last − first |

Trace ADC: \(\text{Trace} = \sum_i -\frac{1}{b_i}\ln(S_i/S_0)\) with \(S_i/S_0 \in [10^{-10}, 1]\), valid voxels only.

Full spec: [dataset paper](https://arxiv.org/pdf/2506.14432).

## Modules

| File | Role |
|------|------|
| `config.py` | Paths, thresholds |
| `io_utils.py` | `.nii.gz` and `ses-XX.zip` |
| `orientation.py` | RAS, slice filter |
| `anatomical.py` | Structural 3D |
| `dwi.py` | Shells, mean / trace ADC |
| `perfusion.py` | ASL/CBF |
| `pipeline.py` | Orchestration + manifest |

## Status

- [x] RAS, slices, zip I/O, anatomical / DWI / perfusion logic
- [ ] Gradient JSON from BIDS
- [ ] Full-scale run over all `PT*`
- [ ] SSL `Dataset` + augmentations

## Output

```text
preprocessed/<PTxxx>/<sub>/<ses>/*.nii.gz
preprocessed/<PTxxx>/preprocess_manifest.json
```
