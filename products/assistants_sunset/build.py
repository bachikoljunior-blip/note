#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

FILES = ["README.md", "MIGRATION.md", "LICENSE.txt", "scan.py", "codemod.py", "test_scan.py"]
EPOCH = (2020, 1, 1, 0, 0, 0)


def main() -> int:
    root = Path(__file__).resolve().parent
    output = root / "assistants-api-sunset-migration-kit-v1.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in FILES:
            data = (root / name).read_bytes()
            info = zipfile.ZipInfo(name, EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"{output.name} {output.stat().st_size} bytes sha256:{digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
