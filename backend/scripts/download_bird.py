"""Download the BIRD dev set into data/bird/ and verify it.

Usage (from backend/):
    uv run python -m scripts.download_bird [--dest PATH] [--force]

Resulting layout:
    data/bird/dev/dev.json                       questions + gold SQL
    data/bird/dev/dev_tables.json                schema metadata
    data/bird/dev/dev.sql, dev_tied_append.json
    data/bird/dev/dev_databases/<db_id>/<db_id>.sqlite

The script is idempotent: if the dataset already verifies, it does nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

BIRD_DEV_URL = "https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip"
# MD5 of the 2024-06-27 dev release. Pinned so a changed upstream file is caught, not trusted.
BIRD_DEV_MD5 = "04b4af221c9186361f09b16abfd917ec"
ARCHIVE_PREFIX = "dev_20240627/"
NESTED_DB_ZIP = "dev_databases.zip"

EXPECTED_QUESTIONS = 1534
EXPECTED_DATABASES = 11
REQUIRED_FILES = ("dev.json", "dev_tables.json", "dev.sql")
SQLITE_HEADER = b"SQLite format 3\x00"

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DEST = REPO_ROOT / "data" / "bird"

CHUNK_SIZE = 1024 * 1024


class VerificationError(Exception):
    """The downloaded dataset is missing files or does not match expectations."""


def md5_of(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, target: Path) -> None:
    """Stream `url` to `target`, writing to a temp file first so partial downloads never linger."""
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".part")
    with urllib.request.urlopen(url) as response, partial.open("wb") as out:
        total = int(response.headers.get("Content-Length", 0))
        done = 0
        while chunk := response.read(CHUNK_SIZE):
            out.write(chunk)
            done += len(chunk)
            if total:
                print(f"\r  {done / 1e6:7.1f} / {total / 1e6:.1f} MB", end="", flush=True)
    print()
    partial.replace(target)


def safe_extract(archive: Path, dest: Path, strip_prefix: str = "") -> list[Path]:
    """Extract `archive` into `dest`, skipping macOS junk and refusing paths that escape `dest`."""
    dest = dest.resolve()
    extracted: list[Path] = []
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            name = info.filename
            parts = PurePosixPath(name).parts
            if not parts or parts[0] == "__MACOSX" or parts[-1] == ".DS_Store":
                continue
            if strip_prefix:
                if not name.startswith(strip_prefix):
                    continue
                name = name[len(strip_prefix) :]
            if not name or info.is_dir():
                continue
            out = (dest / name).resolve()
            if not out.is_relative_to(dest):
                raise VerificationError(f"Unsafe path in archive: {info.filename}")
            out.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, out.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            extracted.append(out)
    return extracted


def verify_dataset(
    dev_dir: Path,
    expected_questions: int = EXPECTED_QUESTIONS,
    expected_databases: int = EXPECTED_DATABASES,
) -> None:
    """Raise VerificationError unless `dev_dir` holds a complete BIRD dev set."""
    for name in REQUIRED_FILES:
        if not (dev_dir / name).is_file():
            raise VerificationError(f"Missing file: {dev_dir / name}")

    questions = json.loads((dev_dir / "dev.json").read_text(encoding="utf-8"))
    if not isinstance(questions, list) or len(questions) != expected_questions:
        count = len(questions) if isinstance(questions, list) else "not a list"
        raise VerificationError(f"dev.json: expected {expected_questions} questions, got {count}")
    for i, q in enumerate(questions):
        missing = {"question", "SQL", "db_id"} - set(q)
        if missing:
            raise VerificationError(f"dev.json entry {i} is missing {sorted(missing)}")

    db_ids = sorted({q["db_id"] for q in questions})
    if len(db_ids) != expected_databases:
        raise VerificationError(f"Expected {expected_databases} databases, found {len(db_ids)}")
    for db_id in db_ids:
        db_path = dev_dir / "dev_databases" / db_id / f"{db_id}.sqlite"
        if not db_path.is_file():
            raise VerificationError(f"Missing database: {db_path}")
        with db_path.open("rb") as f:
            if f.read(len(SQLITE_HEADER)) != SQLITE_HEADER:
                raise VerificationError(f"Not a SQLite file: {db_path}")


def fetch_bird_dev(dest: Path, force: bool = False) -> Path:
    dev_dir = dest / "dev"
    if not force:
        try:
            verify_dataset(dev_dir)
        except VerificationError:
            pass
        else:
            print(f"BIRD dev set already present and verified at {dev_dir}")
            return dev_dir

    if dev_dir.exists():
        shutil.rmtree(dev_dir)
    archive = dest / "dev.zip"
    if force or not archive.is_file() or md5_of(archive) != BIRD_DEV_MD5:
        print(f"Downloading {BIRD_DEV_URL}")
        download(BIRD_DEV_URL, archive)

    print("Checking MD5")
    actual = md5_of(archive)
    if actual != BIRD_DEV_MD5:
        raise VerificationError(f"MD5 mismatch for {archive}: {actual} != {BIRD_DEV_MD5}")

    print(f"Extracting to {dev_dir}")
    safe_extract(archive, dev_dir, strip_prefix=ARCHIVE_PREFIX)
    nested = dev_dir / NESTED_DB_ZIP
    safe_extract(nested, dev_dir)
    nested.unlink()

    verify_dataset(dev_dir)
    archive.unlink()
    print(f"BIRD dev set ready at {dev_dir}")
    return dev_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST, help="default: %(default)s")
    parser.add_argument("--force", action="store_true", help="re-download and re-extract")
    args = parser.parse_args(argv)
    try:
        fetch_bird_dev(args.dest, force=args.force)
    except VerificationError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
