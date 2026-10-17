import json
import shutil
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


# fetch_bird_dev: the network is replaced by a fake download that copies a small local archive
# laid out like the real one (dated top folder with a nested dev_databases.zip).


@pytest.fixture
def fake_bird(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Serve a small fake BIRD archive and pin its SHA-256. Returns the list of downloaded URLs."""
    (tmp_path / "source").mkdir()
    source = make_dev_dir(tmp_path / "source", ["a", "b"])
    nested = tmp_path / "dev_databases.zip"
    with zipfile.ZipFile(nested, "w") as zf:
        for db in (source / "dev_databases").rglob("*.sqlite"):
            zf.write(db, db.relative_to(source).as_posix())
    archive = tmp_path / "fake_dev.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for name in ("dev.json", "dev_tables.json", "dev.sql"):
            zf.write(source / name, download_bird.ARCHIVE_PREFIX + name)
        zf.write(nested, download_bird.ARCHIVE_PREFIX + download_bird.NESTED_DB_ZIP)
        zf.writestr("__MACOSX/._dev.json", "junk")

    calls: list[str] = []

    def fake_download(url: str, target: Path) -> None:
        calls.append(url)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(archive, target)

    real_verify = download_bird.verify_dataset
    monkeypatch.setattr(download_bird, "download", fake_download)
    monkeypatch.setattr(download_bird, "BIRD_DEV_SHA256", sha256_of(archive))
    monkeypatch.setattr(
        download_bird,
        "verify_dataset",
        lambda dev_dir: real_verify(dev_dir, expected_questions=4, expected_databases=2),
    )
    return calls


def test_fetch_downloads_extracts_and_cleans_up(tmp_path: Path, fake_bird: list[str]) -> None:
    dest = tmp_path / "bird"
    dev = download_bird.fetch_bird_dev(dest)
    assert fake_bird == [download_bird.BIRD_DEV_URL]
    assert (dev / "dev_databases" / "b" / "b.sqlite").is_file()
    assert not (dest / "dev.zip").exists()
    assert not (dev / download_bird.NESTED_DB_ZIP).exists()


def test_fetch_skips_download_when_dataset_verifies(tmp_path: Path, fake_bird: list[str]) -> None:
    dest = tmp_path / "bird"
    download_bird.fetch_bird_dev(dest)
    marker = dest / "dev" / "dev.sql"
    marker.write_text("untouched\n")

    download_bird.fetch_bird_dev(dest)

    assert len(fake_bird) == 1
    assert marker.read_text() == "untouched\n"


def test_fetch_force_redownloads_and_reextracts(tmp_path: Path, fake_bird: list[str]) -> None:
    dest = tmp_path / "bird"
    download_bird.fetch_bird_dev(dest)
    stray = dest / "dev" / "stray.txt"
    stray.write_text("old")

    download_bird.fetch_bird_dev(dest, force=True)

    assert len(fake_bird) == 2
    assert not stray.exists()
    download_bird.verify_dataset(dest / "dev")


def test_fetch_rejects_checksum_mismatch(
    tmp_path: Path, fake_bird: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(download_bird, "BIRD_DEV_SHA256", "0" * 64)
    dest = tmp_path / "bird"
    with pytest.raises(VerificationError, match="SHA-256 mismatch"):
        download_bird.fetch_bird_dev(dest)
    assert not (dest / "dev").exists()


def test_main_reports_checksum_mismatch_in_one_line(
    tmp_path: Path,
    fake_bird: list[str],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(download_bird, "BIRD_DEV_SHA256", "0" * 64)
    assert download_bird.main(["--dest", str(tmp_path / "bird")]) == 1
    err = capsys.readouterr().err
    assert err.startswith("error: SHA-256 mismatch") and err.count("\n") == 1
