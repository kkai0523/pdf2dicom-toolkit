# PDF2DICOM Toolkit

PDF2DICOM Toolkit is an open-source command-line tool for converting PDF reports into **DICOM Encapsulated PDF Storage** objects.

It is designed for hospitals, clinics, imaging centers, health checkup providers, and healthcare IT teams that need to archive PDF reports into PACS or DICOM-compatible systems.

> ⚠️ This project does not include real patient data. Do not commit PHI/PII or production credentials to GitHub.

## Features

- Convert a single PDF into a DICOM Encapsulated PDF object
- Batch convert PDFs using `metadata.csv`
- Generate valid DICOM identifiers:
  - Study Instance UID
  - Series Instance UID
  - SOP Instance UID
- Support common patient/study metadata:
  - Patient ID
  - Patient Name
  - Patient Birth Date
  - Patient Sex
  - Study Date
  - Study Time
  - Accession Number
  - Study Description
  - Referring Physician Name
- Support UTF-8 patient names with DICOM `Specific Character Set`
- Optional PACS upload by DICOM C-STORE
- Docker support
- GitHub Actions CI
- pytest test suite

## Install

### Local Python install

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

pip install .
```

For development:

```bash
pip install -e ".[dev]"
```

## CLI Usage

### Convert one PDF

```bash
pdf2dicom convert examples/input/sample.pdf examples/output/sample.dcm \
  --patient-id P001 \
  --patient-name "Test^Patient" \
  --birth-date 19800101 \
  --sex O \
  --study-date 20260101 \
  --accession-number ACC001 \
  --study-description "Example PDF Report"
```

### Convert one PDF with PACS upload

```bash
pdf2dicom convert examples/input/sample.pdf examples/output/sample.dcm \
  --patient-id P001 \
  --patient-name "Test^Patient" \
  --pacs-host 127.0.0.1 \
  --pacs-port 11112 \
  --calling-ae PDF2DCM \
  --called-ae PACS \
  --send
```

### Batch convert

Prepare a CSV file:

```csv
input_pdf,output_dcm,patient_id,patient_name,birth_date,sex,study_date,accession_number,study_description
sample.pdf,sample.dcm,P001,Test^Patient,19800101,O,20260101,ACC001,Example PDF Report
```

Run:

```bash
pdf2dicom batch examples/input examples/output examples/metadata.csv
```

Overwrite existing output:

```bash
pdf2dicom batch examples/input examples/output examples/metadata.csv --overwrite
```

Batch convert and send to PACS:

```bash
pdf2dicom batch examples/input examples/output examples/metadata.csv \
  --pacs-host 127.0.0.1 \
  --pacs-port 11112 \
  --calling-ae PDF2DCM \
  --called-ae PACS \
  --send
```

## Docker

Build:

```bash
docker build -t pdf2dicom-toolkit .
```

Run single conversion:

```bash
docker run --rm -v "$PWD/examples:/data" pdf2dicom-toolkit \
  pdf2dicom convert /data/input/sample.pdf /data/output/sample.dcm \
  --patient-id P001 \
  --patient-name "Test^Patient"
```

Run batch:

```bash
docker run --rm -v "$PWD/examples:/data" pdf2dicom-toolkit \
  pdf2dicom batch /data/input /data/output /data/metadata.csv
```

## Docker Compose

```bash
docker compose run --rm pdf2dicom \
  pdf2dicom batch /data/input /data/output /data/metadata.csv
```

## Metadata CSV Columns

Required:

| Column | Description |
|---|---|
| `input_pdf` | Input PDF filename or path |
| `output_dcm` | Output DICOM filename or path |
| `patient_id` | Patient ID |
| `patient_name` | DICOM PN format, e.g. `Family^Given` |

Optional:

| Column | Description |
|---|---|
| `birth_date` | `YYYYMMDD` |
| `sex` | `M`, `F`, `O`, or empty |
| `study_date` | `YYYYMMDD` |
| `study_time` | `HHMMSS` |
| `accession_number` | Accession number |
| `study_description` | Study description |
| `referring_physician_name` | Referring physician |
| `modality` | Default: `OT` |
| `institution_name` | Institution name |
| `manufacturer` | Default: `PDF2DICOM Toolkit` |

## DICOM Notes

This project creates DICOM Encapsulated PDF Storage objects using:

- SOP Class UID: `1.2.840.10008.5.1.4.1.1.104.1`
- MIME Type: `application/pdf`
- Modality: defaults to `OT`

For names containing non-ASCII characters, the toolkit sets:

```text
Specific Character Set = ISO_IR 192
```

which represents UTF-8.

## Privacy and Safety

Do not publish:

- Real PDF reports
- Real names
- Real IDs
- Internal IPs
- PACS AE Titles
- Credentials
- Hospital-specific internal paths

Use synthetic examples only.

## Limitations

- This is an initial open-source toolkit.
- It does not parse patient metadata from PDF content.
- It does not validate every local PACS vendor-specific requirement.
- C-STORE upload depends on the remote PACS accepting Encapsulated PDF Storage.

## License

MIT License.
