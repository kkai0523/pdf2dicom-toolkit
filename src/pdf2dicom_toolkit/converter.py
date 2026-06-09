from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import (
    EncapsulatedPDFStorage,
    ExplicitVRLittleEndian,
    generate_uid,
)

from .models import DicomMetadata


def convert_pdf_to_dicom(
    input_pdf: str | Path,
    output_dcm: str | Path,
    metadata: DicomMetadata,
    overwrite: bool = False,
    study_instance_uid: Optional[str] = None,
    series_instance_uid: Optional[str] = None,
) -> Path:
    """Convert a PDF file into a DICOM Encapsulated PDF object."""
    input_pdf = Path(input_pdf)
    output_dcm = Path(output_dcm)

    if not input_pdf.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_pdf}")

    if input_pdf.suffix.lower() != ".pdf":
        raise ValueError(f"Input file must be a PDF: {input_pdf}")

    if output_dcm.exists() and not overwrite:
        return output_dcm

    output_dcm.parent.mkdir(parents=True, exist_ok=True)

    meta = metadata.normalized()
    pdf_bytes = input_pdf.read_bytes()
    if not pdf_bytes.startswith(b"%PDF"):
        raise ValueError(f"Input file does not look like a PDF: {input_pdf}")

    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = EncapsulatedPDFStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = generate_uid(prefix="1.2.826.0.1.3680043.10.999.")

    ds = FileDataset(str(output_dcm), {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    ds.SpecificCharacterSet = "ISO_IR 192"

    ds.SOPClassUID = EncapsulatedPDFStorage
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID

    ds.PatientID = meta.patient_id
    ds.PatientName = meta.patient_name
    if meta.birth_date:
        ds.PatientBirthDate = meta.birth_date
    if meta.sex:
        ds.PatientSex = meta.sex

    ds.StudyInstanceUID = study_instance_uid or generate_uid()
    ds.SeriesInstanceUID = series_instance_uid or generate_uid()
    ds.StudyID = meta.accession_number or "1"
    ds.SeriesNumber = "1"
    ds.InstanceNumber = "1"

    ds.StudyDate = meta.study_date
    ds.StudyTime = meta.study_time
    ds.ContentDate = meta.study_date
    ds.ContentTime = meta.study_time
    ds.AcquisitionDateTime = f"{meta.study_date}{meta.study_time}"

    ds.AccessionNumber = meta.accession_number
    ds.StudyDescription = meta.study_description
    ds.SeriesDescription = meta.study_description
    ds.Modality = meta.modality

    if meta.referring_physician_name:
        ds.ReferringPhysicianName = meta.referring_physician_name
    if meta.institution_name:
        ds.InstitutionName = meta.institution_name

    ds.Manufacturer = meta.manufacturer
    ds.BurnedInAnnotation = "YES"
    ds.DocumentTitle = meta.study_description
    ds.MIMETypeOfEncapsulatedDocument = "application/pdf"
    ds.EncapsulatedDocument = pdf_bytes

    ds.save_as(str(output_dcm), write_like_original=False)
    return output_dcm
