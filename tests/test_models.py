import pytest

from pdf2dicom_toolkit.models import DicomMetadata


def test_metadata_defaults():
    metadata = DicomMetadata(patient_id="", patient_name="").normalized()
    assert metadata.patient_id == "UNKNOWN"
    assert metadata.patient_name == "Anonymous^Patient"
    assert metadata.study_date


def test_invalid_date():
    with pytest.raises(ValueError):
        DicomMetadata(patient_id="P001", patient_name="Test^Patient", birth_date="1980-01-01").normalized()


def test_invalid_sex():
    with pytest.raises(ValueError):
        DicomMetadata(patient_id="P001", patient_name="Test^Patient", sex="X").normalized()
