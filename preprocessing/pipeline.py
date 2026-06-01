"""End-to-end preprocessing orchestration."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import nibabel as nib

from preprocessing.anatomical import process_anatomical
from preprocessing.config import BVAL_PREFIX, DWI_SUFFIXES, OUTPUT_ROOT, PERFUSION_SUFFIXES
from preprocessing.dwi import DWIVolume, parse_bval_suffix, process_dwi_session
from preprocessing.io_utils import ScanRef, list_session_scans, load_nifti
from preprocessing.orientation import passes_slice_filter, reorient_to_ras
from preprocessing.perfusion import process_perfusion_stack


def scan_suffix(ref: ScanRef) -> str:
    name = ref.name.lower()
    if name.endswith(".nii.gz"):
        name = name[: -len(".nii.gz")]
    if "_" in name:
        return name.rsplit("_", 1)[-1]
    return name


def is_dwi_ref(ref: ScanRef) -> bool:
    s = scan_suffix(ref)
    return s in DWI_SUFFIXES or s.startswith(BVAL_PREFIX) or "bval" in s


def is_perfusion_ref(ref: ScanRef) -> bool:
    return scan_suffix(ref) in PERFUSION_SUFFIXES


def discover_sessions(dataset_dir: Path) -> dict[str, list[ScanRef]]:
    """
    Group scans by session.

    Supports:
    - sub-XX/ses-YY/*.nii.gz (extracted)
    - sub-XX/ses-YY.zip (one zip per session)
    - sub-XX/ses-YY/ (directory with ses-YY.zip inside)
    """
    sessions: dict[str, list[ScanRef]] = {}

    # One zip per subject: sub-XX/ses-01.zip
    for zpath in sorted(dataset_dir.glob("sub-*/ses-*.zip")):
        sub = zpath.parent.name
        key = f"{sub}/{zpath.stem}"
        with zipfile.ZipFile(zpath) as zf:
            for name in sorted(zf.namelist()):
                if name.endswith(".nii.gz"):
                    sessions.setdefault(key, []).append(
                        ScanRef(zpath, name, Path(name).name)
                    )

    # Session directories: sub-XX/ses-YY/
    for ses_dir in sorted(dataset_dir.glob("sub-*/ses-*")):
        if not ses_dir.is_dir():
            continue
        key = str(ses_dir.relative_to(dataset_dir))
        scans = list_session_scans(ses_dir)
        if scans:
            sessions[key] = scans

    # OpenNeuro: dsXXXXX/...
    for ds_dir in sorted(dataset_dir.glob("ds*")):
        if not ds_dir.is_dir():
            continue
        for ses_dir in sorted(ds_dir.glob("sub-*/ses-*")):
            key = str(ses_dir.relative_to(dataset_dir))
            scans = list_session_scans(ses_dir)
            if scans:
                sessions[key] = scans
        for zpath in sorted(ds_dir.glob("sub-*/ses-*.zip")):
            sub = zpath.parent.name
            key = f"{ds_dir.name}/{sub}/{zpath.stem}"
            with zipfile.ZipFile(zpath) as zf:
                for name in sorted(zf.namelist()):
                    if name.endswith(".nii.gz"):
                        sessions.setdefault(key, []).append(
                            ScanRef(zpath, name, Path(name).name)
                        )

    return sessions


def _save_nifti(path: Path, img: nib.Nifti1Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(img, str(path))


def process_session(
    session_key: str,
    scans: list[ScanRef],
    output_dir: Path,
    dry_run: bool = False,
) -> dict:
    """Process one BIDS session."""
    log: dict = {"session": session_key, "written": [], "skipped": []}

    dwi_refs = [r for r in scans if is_dwi_ref(r)]
    perf_refs = [r for r in scans if is_perfusion_ref(r)]
    anat_refs = [r for r in scans if r not in dwi_refs and r not in perf_refs]

    if dwi_refs:
        volumes: list[DWIVolume] = []
        for ref in dwi_refs:
            img = reorient_to_ras(load_nifti(ref))
            data = img.get_fdata()
            if data.ndim == 4:
                for t in range(data.shape[-1]):
                    b = parse_bval_suffix(ref.name) or 0.0
                    volumes.append(DWIVolume(data=data[..., t], b_value=b))
            else:
                b = parse_bval_suffix(ref.name)
                if b is None:
                    b = 1000.0 if "dwi" in ref.name.lower() else 0.0
                volumes.append(DWIVolume(data=data, b_value=b))

        b0, processed = process_dwi_session(volumes, session_key)
        if processed is not None:
            ref_affine = reorient_to_ras(load_nifti(dwi_refs[0])).affine
            out_path = output_dir / session_key / "dwi_preprocessed.nii.gz"
            if not dry_run:
                _save_nifti(out_path, nib.Nifti1Image(processed, ref_affine))
            log["written"].append(str(out_path))
            if b0 is not None:
                b0_path = output_dir / session_key / "b0_reference.nii.gz"
                if not dry_run:
                    _save_nifti(b0_path, nib.Nifti1Image(b0.astype("float32"), ref_affine))
                log["written"].append(str(b0_path))

    for ref in perf_refs:
        img = reorient_to_ras(load_nifti(ref))
        try:
            processed = process_perfusion_stack(img.get_fdata())
        except ValueError as e:
            log["skipped"].append({ref.name: str(e)})
            continue
        out = nib.Nifti1Image(processed, img.affine, img.header)
        if not passes_slice_filter(out):
            log["skipped"].append({ref.name: "fewer than 15 slices"})
            continue
        out_path = output_dir / session_key / Path(ref.name).name
        if not dry_run:
            _save_nifti(out_path, out)
        log["written"].append(str(out_path))

    for ref in anat_refs:
        out_img = process_anatomical(load_nifti(ref))
        if out_img is None:
            log["skipped"].append({ref.name: "fewer than 15 slices"})
            continue
        out_path = output_dir / session_key / Path(ref.name).name
        if not dry_run:
            _save_nifti(out_path, out_img)
        log["written"].append(str(out_path))

    return log


def run_dataset(
    input_dir: Path,
    output_dir: Path,
    limit: int | None = None,
    dry_run: bool = False,
) -> list[dict]:
    sessions = discover_sessions(input_dir)
    logs = []
    for i, (key, scans) in enumerate(sorted(sessions.items())):
        if limit is not None and i >= limit:
            break
        logs.append(process_session(key, scans, output_dir, dry_run=dry_run))
    return logs


def run(
    input_dir: Path,
    output_dir: Path | None = None,
    limit: int | None = None,
    dry_run: bool = False,
) -> Path:
    output_dir = output_dir or OUTPUT_ROOT
    out = output_dir / input_dir.name
    logs = run_dataset(input_dir, out, limit=limit, dry_run=dry_run)
    if not dry_run:
        out.mkdir(parents=True, exist_ok=True)
        (out / "preprocess_manifest.json").write_text(json.dumps(logs, indent=2))
    return out
