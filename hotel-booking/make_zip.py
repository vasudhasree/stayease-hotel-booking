from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "hotel-booking.zip"
with ZipFile(OUT, "w", ZIP_DEFLATED) as z:
    for path in ROOT.rglob("*"):
        if path.is_file() and path.name != "hotel-booking.zip" and "__pycache__" not in path.parts and "node_modules" not in path.parts:
            z.write(path, path.relative_to(ROOT.parent))
print(f"Created: {OUT}")
