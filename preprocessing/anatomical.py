"""Single-volume anatomical preprocessing."""

from __future__ import annotations

import nibabel as nib
import numpy as np

from preprocessing.orientation import passes_slice_filter, reorient_to_ras, squeeze_time_dimension


def process_anatomical(img: nib.Nifti1Image) -> nib.Nifti1Image | None:
    """RAS reorient, 4D->3D, slice filter."""
    img = reorient_to_ras(img)
    data = squeeze_time_dimension(img.get_fdata())
    out = nib.Nifti1Image(data.astype(np.float32), img.affine, img.header)
    if not passes_slice_filter(out):
        return None
    return out
