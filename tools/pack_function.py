#!/usr/bin/env python3
"""Pack the gallery-api Catalyst function into catalyst/gallery-api.zip.

The ZIP is for creating or updating the function in the Catalyst web console
(Serverless > Functions > Create Function > File Upload) without the CLI. The files sit
at the top of the ZIP. tools/check_site.py fails if the ZIP is out of date, so run this
after editing anything in catalyst/functions/gallery-api/.

Usage: python3 tools/pack_function.py
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "catalyst" / "functions" / "gallery-api"
ZIP = ROOT / "catalyst" / "gallery-api.zip"
FILES = ["index.js", "package.json", "catalyst-config.json"]


def expected():
    return {name: (SRC / name).read_bytes() for name in FILES}


def is_current():
    try:
        with zipfile.ZipFile(ZIP) as z:
            return {n: z.read(n) for n in z.namelist()} == expected()
    except (OSError, zipfile.BadZipFile, KeyError):
        return False


def main():
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in expected().items():
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))  # fixed: same code, same ZIP
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    print(f"Wrote {ZIP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
