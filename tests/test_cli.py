from pdf2dicom_toolkit.cli import main
from .conftest import create_sample_pdf


def test_cli_convert(tmp_path):
    pdf = create_sample_pdf(tmp_path / "input.pdf")
    dcm = tmp_path / "output.dcm"

    exit_code = main(
        [
            "convert",
            str(pdf),
            str(dcm),
            "--patient-id",
            "P001",
            "--patient-name",
            "Test^Patient",
        ]
    )

    assert exit_code == 0
    assert dcm.exists()
