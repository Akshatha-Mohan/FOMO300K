# FOMO300K

**[FOMO26](https://zenodo.org/records/19714192)** (MICCAI 2026) — SSL pretraining on [FOMO300K](https://huggingface.co/datasets/FOMO-MRI/FOMO300K), then finetune for **segmentation**, **classification**, and **regression**.

| Stage | Path | Status |
|-------|------|--------|
| Preprocessing | [`preprocessing/`](preprocessing/) | In progress |
| SSL pretraining | `ssl/` | Planned |
| Downstream | `downstream/` | Planned |

**Data (this machine):** `/data/users/fomo2026/FOMO300K/` · [layout & modalities](docs/DATA.md)

## Quick start

```bash
cd /shared/home/<USERNAME>/FOMO300K
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python scripts/run_preprocess.py \
  --input /data/users/fomo2026/FOMO300K/PT001_ClevelandCCF \
  --output ./preprocessed --limit 5
```

Details: [`preprocessing/README.md`](preprocessing/README.md)

## Links

- Challenge: [FOMO26](https://zenodo.org/records/19714192) · [FOMO25](https://fomo25.github.io/)
- Paper: [arXiv:2506.14432](https://arxiv.org/abs/2506.14432)

## Cite

```bibtex
@article{Cerri2026large,
  title={A large-scale heterogeneous 3D magnetic resonance brain imaging dataset for self-supervised learning},
  author={Cerri, Stefano and others},
  journal={arXiv preprint arXiv:2506.14432},
  year={2026}
}
```
