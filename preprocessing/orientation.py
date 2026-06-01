"""RAS reorientation and slice-count checks."""

from __future__ import annotations

import nibabel as nib
import numpy as np

from preprocessing.config import MIN_SLICES


def reorient_to_ras(img: nib.Nifti1Image) -> nib.Nifti1Image:
    """Return image in closest canonical RAS orientation."""
    return nib.as_closest_canonical(img)


def slice_count(img: nib.Nifti1Image) -> int:
    """Number of slices along the superior axis after RAS canonicalization."""
    data = img.get_fdata()
    if data.ndim < 3:
        return 0
    return int(data.shape[2])


def passes_slice_filter(img: nib.Nifti1Image, min_slices: int = MIN_SLICES) -> bool:
    return slice_count(img) >= min_slices


def squeeze_time_dimension(data: np.ndarray) -> np.ndarray:
    """Collapse trailing singleton or small 4D time dimension via mean."""
    if data.ndim == 3:
        return data
    if data.ndim == 4:
        return np.mean(data, axis=-1)
    raise ValueError(f"Expected 3D or 4D array, got shape {data.shape}")
