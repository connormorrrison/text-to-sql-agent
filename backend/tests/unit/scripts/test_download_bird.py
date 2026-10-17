import json
import sqlite3
import urllib.error
import zipfile
from pathlib import Path

import pytest

from scripts import download_bird
from scripts.download_bird import VerificationError, safe_extract, sha256_of, verify_dataset


def make_dev_dir(root: Path, db_ids: list[str], questions_per_db: int = 2) -> Path:
    dev = root / "dev"
    dev.mkdir()
    questions = [
        {"question": f"q{i}", "SQL": "SELECT 1", "db_id": db_id}
        for db_id in db_ids
        for i in range(questions_per_db)
    ]
    (dev / "dev.json").write_text(json.dumps(questions))
    (dev / "dev_tables.json").write_text("[]")
    (dev / "dev.sql").write_text("SELECT 1\n")
    for db_id in db_ids:
        db_dir = dev / "dev_databases" / db_id
        db_dir.mkdir(parents=True)
        sqlite3.connect(db_dir / f"{db_id}.sqlite").execute("CREATE TABLE t (x)").connection.close()
    return dev


def test_verify_accepts_complete_dataset(tmp_path: Path) -> None:
    dev = make_dev_dir(tmp_path, ["a", "b"])
    verify_dataset(dev, expected_questions=4, expected_databases=2)


def test_verify_rejects_wrong_question_count(tmp_path: Path) -> None:
    dev = make_dev_dir(tmp_path, ["a", "b"])
    with pytest.raises(VerificationError, match="expected 5 questions"):
        verify_dataset(dev, expected_questions=5, expected_databases=2)


def test_verify_rejects_missing_file(tmp_path: Path) -> None:
    dev = make_dev_dir(tmp_path, ["a"])
    (dev / "dev_tables.json").unlink()
    with pytest.raises(VerificationError, match="Missing file"):
        verify_dataset(dev, expected_questions=2, expected_databases=1)


def test_verify_rejects_missing_database(tmp_path: Path) -> None:
    dev = make_dev_dir(tmp_path, ["a", "b"])
    (dev / "dev_databases" / "b" / "b.sqlite").unlink()
    with pytest.raises(VerificationError, match="Missing database"):
        verify_dataset(dev, expected_questions=4, expected_databases=2)


def test_verify_rejects_non_sqlite_database(tmp_path: Path) -> None:
    dev = make_dev_dir(tmp_path, ["a"])
    (dev / "dev_databases" / "a" / "a.sqlite").write_bytes(b"not a database")
    with pytest.raises(VerificationError, match="Not a SQLite file"):
        verify_dataset(dev, expected_questions=2, expected_databases=1)


def test_verify_rejects_entry_missing_keys(tmp_path: Path) -> None:
    dev = make_dev_dir(tmp_path, ["a"])
    (dev / "dev.json").write_text(json.dumps([{"question": "q", "db_id": "a"}] * 2))
    with pytest.raises(VerificationError, match="missing \\['SQL'\\]"):
        verify_dataset(dev, expected_questions=2, expected_databases=1)


def test_safe_extract_strips_prefix_and_skips_macos_junk(tmp_path: Path) -> None:
    archive = tmp_path / "dev.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("dev_20240627/dev.json", "[]")
        zf.writestr("dev_20240627/sub/file.txt", "x")
        zf.writestr("__MACOSX/dev_20240627/._dev.json", "junk")
        zf.writestr("dev_20240627/.DS_Store", "junk")
    out = tmp_path / "out"
    safe_extract(archive, out, strip_prefix="dev_20240627/")
    files = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    assert files == ["dev.json", "sub/file.txt"]


def test_safe_extract_rejects_path_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "evil.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("../escaped.txt", "x")
    with pytest.raises(VerificationError, match="Unsafe path"):
        safe_extract(archive, tmp_path / "out")
    assert not (tmp_path / "escaped.txt").exists()


def test_sha256_of(tmp_path: Path) -> None:
    f = tmp_path / "f"
    f.write_bytes(b"hello")
    assert sha256_of(f) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_main_reports_network_error_in_one_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def failing_download(url: str, target: Path) -> None:
        raise urllib.error.URLError("timed out")

    monkeypatch.setattr(download_bird, "download", failing_download)
    assert download_bird.main(["--dest", str(tmp_path)]) == 1
    err = capsys.readouterr().err
    assert err == "error: <urlopen error timed out>\n"
