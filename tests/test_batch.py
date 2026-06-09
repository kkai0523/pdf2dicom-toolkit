import csv

import pydicom

from pdf2dicom_toolkit.batch import batch_convert
from conftest import create_sample_pdf


def test_batch_convert(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    create_sample_pdf(input_dir / "sample.pdf")

    metadata_csv = tmp_path / "metadata.csv"
    with metadata_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "input_pdf",
                "output_dcm",
                "patient_id",
                "patient_name",
                "birth_date",
                "sex",
                "study_date",
                "accession_number",
                "study_description",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "input_pdf": "sample.pdf",
                "output_dcm": "sample.dcm",
                "patient_id": "P001",
                "patient_name": "Test^Patient",
                "birth_date": "19800101",
                "sex": "O",
                "study_date": "20260101",
                "accession_number": "ACC001",
                "study_description": "Example PDF Report",
            }
        )

    result = batch_convert(input_dir, output_dir, metadata_csv)

    assert result.converted == 1
    assert result.failed == 0
    ds = pydicom.dcmread(output_dir / "sample.dcm")
    assert ds.PatientID == "P001"
