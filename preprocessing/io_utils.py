"""Load NIfTI from extracted files or per-session ZIP archives."""

from __future__ import annotations

import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

import nibabel as nib


@dataclass
class ScanRef:
    """Reference to one scan inside a session (file or zip member)."""

    source: Path
    member: str | None  # zip internal path
    name: str  # basename for suffix detection


def list_session_scans(session_dir: Path) -> list[ScanRef]:
    """List scans in a session directory (extracted NIfTI or ses-XX.zip)."""
    scans: list[ScanRef] = []
    for nii in sorted(session_dir.glob("*.nii.gz")):
        scans.append(ScanRef(session_dir, None, nii.name))
    for sub in sorted(session_dir.rglob("*.nii.gz")):
        if sub.parent == session_dir:
            continue
        scans.append(ScanRef(session_dir, None, str(sub.relative_to(session_dir))))

    for zpath in sorted(session_dir.glob("*.zip")):
        with zipfile.ZipFile(zpath) as zf:
            for name in sorted(zf.namelist()):
                if name.endswith(".nii.gz"):
                    scans.append(ScanRef(zpath, name, Path(name).name))

    return scans


def _load_bytes(data: bytes) -> nib.Nifti1Image:
    """Load .nii.gz bytes via a temporary file (nibabel-compatible)."""
    tmp = tempfile.NamedTemporaryFile(suffix=".nii.gz", delete=False)
    try:
        tmp.write(data)
        tmp.close()
        img = nib.load(tmp.name)
        # Materialize in memory so the temp file can be removed immediately.
        return nib.Nifti1Image(img.get_fdata(), img.affine, img.header)
    finally:
        Path(tmp.name).unlink(missing_ok=True)


def load_nifti(ref: ScanRef) -> nib.Nifti1Image:
    if ref.source.suffix == ".zip":
        with zipfile.ZipFile(ref.source) as zf:
            member = ref.member
            if member is None:
                names = [n for n in zf.namelist() if n.endswith(".nii.gz")]
                member = names[0]
            return _load_bytes(zf.read(member))
    path = ref.source if ref.member is None else ref.source / ref.member
    return nib.load(str(path))
