from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class DicomMetadata:
    patient_id: str
    patient_name: str
    birth_date: str = ""
    sex: str = ""
    study_date: str = ""
    study_time: str = ""
    accession_number: str = ""
    study_description: str = "PDF Report"
    referring_physician_name: str = ""
    modality: str = "OT"
    institution_name: str = ""
    manufacturer: str = "PDF2DICOM Toolkit"

    def normalized(self) -> "DicomMetadata":
        now = datetime.now()
        return DicomMetadata(
            patient_id=(self.patient_id or "UNKNOWN").strip(),
            patient_name=(self.patient_name or "Anonymous^Patient").strip(),
            birth_date=_date_or_empty(self.birth_date),
            sex=_sex_or_empty(self.sex),
            study_date=_date_or_empty(self.study_date) or now.strftime("%Y%m%d"),
            study_time=_time_or_empty(self.study_time) or now.strftime("%H%M%S"),
            accession_number=(self.accession_number or "").strip(),
            study_description=(self.study_description or "PDF Report").strip(),
            referring_physician_name=(self.referring_physician_name or "").strip(),
            modality=(self.modality or "OT").strip().upper(),
            institution_name=(self.institution_name or "").strip(),
            manufacturer=(self.manufacturer or "PDF2DICOM Toolkit").strip(),
        )


def _date_or_empty(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if len(value) == 8 and value.isdigit():
        return value
    raise ValueError(f"Invalid DICOM date: {value}. Expected YYYYMMDD.")


def _time_or_empty(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    if len(value) in {2, 4, 6} and value.isdigit():
        return value
    raise ValueError(f"Invalid DICOM time: {value}. Expected HH, HHMM, or HHMMSS.")


def _sex_or_empty(value: str) -> str:
    value = (value or "").strip().upper()
    if value in {"", "M", "F", "O"}:
        return value
    raise ValueError(f"Invalid Patient Sex: {value}. Expected M, F, O, or empty.")
