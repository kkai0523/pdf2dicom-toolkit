from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .converter import convert_pdf_to_dicom
from .models import DicomMetadata
from .pacs import PacsConfig, send_dicom_to_pacs


@dataclass
class BatchResult:
    converted: int = 0
    skipped: int = 0
    sent: int = 0
    failed: int = 0


def batch_convert(
    input_dir: str | Path,
    output_dir: str | Path,
    metadata_csv: str | Path,
    overwrite: bool = False,
    send: bool = False,
    pacs_config: PacsConfig | None = None,
) -> BatchResult:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    metadata_csv = Path(metadata_csv)

    if not metadata_csv.exists():
        raise FileNotFoundError(f"Metadata CSV not found: {metadata_csv}")

    result = BatchResult()

    with metadata_csv.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"input_pdf", "output_dcm", "patient_id", "patient_name"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"metadata.csv missing required columns: {sorted(missing)}")

        for row_no, row in enumerate(reader, start=2):
            try:
                input_pdf = _resolve_path(input_dir, row["input_pdf"])
                output_dcm = _resolve_path(output_dir, row["output_dcm"])

                existed = output_dcm.exists()
                metadata = DicomMetadata(
                    patient_id=row.get("patient_id", ""),
                    patient_name=row.get("patient_name", ""),
                    birth_date=row.get("birth_date", ""),
                    sex=row.get("sex", ""),
                    study_date=row.get("study_date", ""),
                    study_time=row.get("study_time", ""),
                    accession_number=row.get("accession_number", ""),
                    study_description=row.get("study_description", "") or "PDF Report",
                    referring_physician_name=row.get("referring_physician_name", ""),
                    modality=row.get("modality", "") or "OT",
                    institution_name=row.get("institution_name", ""),
                    manufacturer=row.get("manufacturer", "") or "PDF2DICOM Toolkit",
                )

                convert_pdf_to_dicom(input_pdf, output_dcm, metadata, overwrite=overwrite)
                if existed and not overwrite:
                    result.skipped += 1
                else:
                    result.converted += 1

                if send:
                    if pacs_config is None:
                        raise ValueError("PACS config is required when --send is used.")
                    send_dicom_to_pacs(output_dcm, pacs_config)
                    result.sent += 1

            except Exception as exc:
                result.failed += 1
                print(f"[ERROR] row {row_no}: {exc}")

    return result


def _resolve_path(base_dir: Path, value: str) -> Path:
    path = Path((value or "").strip())
    if path.is_absolute():
        return path
    return base_dir / path
