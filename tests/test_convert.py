import pydicom

from pdf2dicom_toolkit.converter import convert_pdf_to_dicom
from pdf2dicom_toolkit.models import DicomMetadata

from .conftest import create_sample_pdf


def test_convert_pdf_to_dicom(tmp_path):
    pdf = create_sample_pdf(tmp_path / "input.pdf")
    dcm = tmp_path / "output.dcm"

    convert_pdf_to_dicom(
        pdf,
        dcm,
        DicomMetadata(
            patient_id="P001",
            patient_name="Test^Patient",
            birth_date="19800101",
            sex="O",
            study_date="20260101",
            accession_number="ACC001",
            study_description="Example PDF Report",
        ),
    )

    ds = pydicom.dcmread(dcm)
    assert ds.PatientID == "P001"
    assert str(ds.PatientName) == "Test^Patient"
    assert ds.MIMETypeOfEncapsulatedDocument == "application/pdf"
    assert ds.EncapsulatedDocument.startswith(b"%PDF")
    assert ds.SOPClassUID == "1.2.840.10008.5.1.4.1.1.104.1"


def test_convert_skip_existing(tmp_path):
    pdf = create_sample_pdf(tmp_path / "input.pdf")
    dcm = tmp_path / "output.dcm"
    metadata = DicomMetadata(patient_id="P001", patient_name="Test^Patient")

    convert_pdf_to_dicom(pdf, dcm, metadata)
    before = dcm.stat().st_mtime
    convert_pdf_to_dicom(pdf, dcm, metadata, overwrite=False)
    after = dcm.stat().st_mtime

    assert before == after
