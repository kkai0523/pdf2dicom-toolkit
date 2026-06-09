from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pydicom
from pynetdicom import AE
from pynetdicom.sop_class import EncapsulatedPDFStorage


@dataclass
class PacsConfig:
    host: str
    port: int
    calling_ae: str = "PDF2DCM"
    called_ae: str = "PACS"
    timeout: int = 30


def send_dicom_to_pacs(dicom_path: str | Path, config: PacsConfig) -> None:
    """Send one DICOM file to PACS using C-STORE."""
    dicom_path = Path(dicom_path)
    if not dicom_path.exists():
        raise FileNotFoundError(f"DICOM file not found: {dicom_path}")

    ds = pydicom.dcmread(str(dicom_path))

    ae = AE(ae_title=config.calling_ae)
    ae.add_requested_context(EncapsulatedPDFStorage)

    assoc = ae.associate(
        config.host,
        int(config.port),
        ae_title=config.called_ae,
        max_pdu=16382,
        ext_neg=None,
    )

    if not assoc.is_established:
        raise ConnectionError(
            f"Could not establish DICOM association to {config.host}:{config.port} "
            f"called AE={config.called_ae}"
        )

    try:
        status = assoc.send_c_store(ds)
        if status is None:
            raise RuntimeError("No C-STORE response received.")
        if status.Status not in {0x0000, 0xB000, 0xB006, 0xB007}:
            raise RuntimeError(f"C-STORE failed with status 0x{status.Status:04X}")
    finally:
        assoc.release()
