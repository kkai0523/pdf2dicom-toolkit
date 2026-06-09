from __future__ import annotations

import argparse
import sys

from .batch import batch_convert
from .converter import convert_pdf_to_dicom
from .models import DicomMetadata
from .pacs import PacsConfig, send_dicom_to_pacs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdf2dicom",
        description="Convert PDF reports into DICOM Encapsulated PDF objects.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    convert = sub.add_parser("convert", help="Convert one PDF to one DICOM file.")
    convert.add_argument("input_pdf")
    convert.add_argument("output_dcm")
    add_metadata_args(convert)
    add_pacs_args(convert)
    convert.add_argument("--overwrite", action="store_true", help="Overwrite output DICOM if exists.")

    batch = sub.add_parser("batch", help="Batch convert PDFs using metadata.csv.")
    batch.add_argument("input_dir")
    batch.add_argument("output_dir")
    batch.add_argument("metadata_csv")
    add_pacs_args(batch)
    batch.add_argument("--overwrite", action="store_true", help="Overwrite output DICOM if exists.")

    return parser


def add_metadata_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--patient-id", required=True)
    parser.add_argument("--patient-name", required=True)
    parser.add_argument("--birth-date", default="")
    parser.add_argument("--sex", default="")
    parser.add_argument("--study-date", default="")
    parser.add_argument("--study-time", default="")
    parser.add_argument("--accession-number", default="")
    parser.add_argument("--study-description", default="PDF Report")
    parser.add_argument("--referring-physician-name", default="")
    parser.add_argument("--modality", default="OT")
    parser.add_argument("--institution-name", default="")
    parser.add_argument("--manufacturer", default="PDF2DICOM Toolkit")


def add_pacs_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--send", action="store_true", help="Send generated DICOM to PACS.")
    parser.add_argument("--pacs-host", default="")
    parser.add_argument("--pacs-port", type=int, default=0)
    parser.add_argument("--calling-ae", default="PDF2DCM")
    parser.add_argument("--called-ae", default="PACS")
    parser.add_argument("--timeout", type=int, default=30)


def pacs_config_from_args(args: argparse.Namespace) -> PacsConfig | None:
    if not args.send:
        return None
    if not args.pacs_host or not args.pacs_port:
        raise ValueError("--pacs-host and --pacs-port are required when --send is used.")
    return PacsConfig(
        host=args.pacs_host,
        port=args.pacs_port,
        calling_ae=args.calling_ae,
        called_ae=args.called_ae,
        timeout=args.timeout,
    )


def run(args: argparse.Namespace) -> int:
    if args.command == "convert":
        metadata = DicomMetadata(
            patient_id=args.patient_id,
            patient_name=args.patient_name,
            birth_date=args.birth_date,
            sex=args.sex,
            study_date=args.study_date,
            study_time=args.study_time,
            accession_number=args.accession_number,
            study_description=args.study_description,
            referring_physician_name=args.referring_physician_name,
            modality=args.modality,
            institution_name=args.institution_name,
            manufacturer=args.manufacturer,
        )
        output = convert_pdf_to_dicom(
            args.input_pdf,
            args.output_dcm,
            metadata,
            overwrite=args.overwrite,
        )
        print(f"Created: {output}")

        if args.send:
            config = pacs_config_from_args(args)
            assert config is not None
            send_dicom_to_pacs(output, config)
            print("Sent to PACS.")

        return 0

    if args.command == "batch":
        config = pacs_config_from_args(args)
        result = batch_convert(
            args.input_dir,
            args.output_dir,
            args.metadata_csv,
            overwrite=args.overwrite,
            send=args.send,
            pacs_config=config,
        )
        print(
            f"Batch complete. converted={result.converted}, skipped={result.skipped}, "
            f"sent={result.sent}, failed={result.failed}"
        )
        return 1 if result.failed else 0

    raise ValueError(f"Unknown command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
