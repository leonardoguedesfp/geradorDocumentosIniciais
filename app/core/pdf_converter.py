"""Convert .docx files to .pdf using LibreOffice headless or docx2pdf."""

import shutil
import subprocess
import sys
from pathlib import Path


def _find_libreoffice() -> str | None:
    """Find LibreOffice executable."""
    candidates = ["libreoffice", "soffice"]
    if sys.platform == "win32":
        candidates.extend([
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ])
    for cmd in candidates:
        if shutil.which(cmd):
            return cmd
    return None


def convert_to_pdf(docx_path: str, output_dir: str | None = None) -> str:
    """Convert a .docx file to .pdf.

    Tries LibreOffice headless first, falls back to docx2pdf.
    Returns the path to the generated PDF.
    """
    docx_path = Path(docx_path)
    if output_dir is None:
        output_dir = str(docx_path.parent)

    # Try LibreOffice headless
    lo = _find_libreoffice()
    if lo:
        try:
            result = subprocess.run(
                [lo, "--headless", "--convert-to", "pdf", "--outdir", output_dir, str(docx_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                pdf_path = Path(output_dir) / (docx_path.stem + ".pdf")
                if pdf_path.exists():
                    return str(pdf_path)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Fallback to docx2pdf
    try:
        from docx2pdf import convert
        pdf_path = Path(output_dir) / (docx_path.stem + ".pdf")
        convert(str(docx_path), str(pdf_path))
        return str(pdf_path)
    except ImportError:
        raise RuntimeError(
            "Nenhum conversor PDF disponível. Instale o LibreOffice ou docx2pdf."
        )
    except Exception as e:
        raise RuntimeError(f"Falha na conversão para PDF: {e}")
