"""Release integrity tests do not contact GitHub/PyPI or use credentials."""
from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import tarfile
import zipfile

import pytest

pytest.importorskip("tomllib", reason="Release tooling runs on Python 3.11+")
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("younglion_release", ROOT / "tools/release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


@pytest.fixture
def bundle(tmp_path):
    info = release.metadata()
    stable = tmp_path / "pypi"
    stable.mkdir()
    headers = f"Metadata-Version: 2.4\nName: YoungLion\nVersion: {info['version']}\n\n".encode()
    wheel = stable / f"younglion-{info['version']}-cp312-cp312-linux_x86_64.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(f"younglion-{info['version']}.dist-info/METADATA", headers)
        for suffix in ("*.pyi", "*.py"):
            for path in (ROOT / "src/YoungLion").rglob(suffix):
                archive.write(path, path.relative_to(ROOT / "src").as_posix())
        archive.writestr("YoungLion/py.typed", b"")
        archive.writestr("YoungLion/_native.cpython-312-test.so", b"test binary")
    source = stable / f"younglion-{info['version']}.tar.gz"
    with tarfile.open(source, "w:gz") as archive:
        member = tarfile.TarInfo(f"younglion-{info['version']}/PKG-INFO")
        member.size = len(headers)
        archive.addfile(member, io.BytesIO(headers))
    manifest = {"project": "YoungLion", "version": info["version"], "git_sha": "a" * 40,
                "files": [{"file": "pypi/" + path.name, "size": path.stat().st_size,
                           "sha256": release.digest(path), "channel": "pypi"}
                          for path in (wheel, source)]}
    (tmp_path / "checksums").mkdir()
    (tmp_path / "checksums/MANIFEST.json").write_text(json.dumps(manifest))
    return tmp_path, info, wheel


def test_metadata_agrees_with_runtime_and_notes():
    from YoungLion import __version__
    info = release.metadata()
    assert info["version"] == __version__ and info["tag"] == "v" + __version__
    notes = release.release_notes(ROOT, info["version"])
    assert len(notes) > 100 and not notes.startswith("## ")


def test_notes_extract_only_the_requested_version(tmp_path):
    (tmp_path / "Releases.md").write_text(
        "## 1.2.3 — New\nNew notes: [docs](docs/page.md)\n\n## 1.2.2 — Old\nOld notes\n",
        encoding="utf-8")
    notes = release.release_notes(tmp_path, "1.2.3")
    assert "Old notes" not in notes
    assert "/blob/v1.2.3/docs/page.md" in notes
    with pytest.raises(ValueError, match="Missing release notes"):
        release.release_notes(tmp_path, "1.2.4")


def test_publication_rejects_other_branches(monkeypatch):
    monkeypatch.setenv("PUBLISH_RELEASE", "true")
    monkeypatch.setenv("DEFAULT_BRANCH", "main")
    monkeypatch.setenv("GITHUB_REF", "refs/heads/topic")
    with pytest.raises(ValueError, match="default branch"):
        release.validate_ref(release.metadata())
    monkeypatch.setenv("GITHUB_REF", "refs/tags/" + release.metadata()["tag"])
    release.validate_ref(release.metadata())


def test_distribution_integrity_and_commit_identity(bundle):
    folder, info, wheel = bundle
    assert wheel in release.distributions(folder, info, "a" * 40)
    with pytest.raises(ValueError, match="different commit"):
        release.distributions(folder, info, "b" * 40)
    wheel.write_bytes(wheel.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="checksum mismatch"):
        release.distributions(folder, info)


def test_unlisted_stable_files_are_rejected(bundle):
    folder, info, _ = bundle
    (folder / "pypi/unlisted.whl").write_bytes(b"not in manifest")
    with pytest.raises(ValueError, match="differs from its manifest"):
        release.distributions(folder, info)


def test_manifest_version_and_paths_are_checked(bundle):
    folder, info, _ = bundle
    manifest = folder / "checksums/MANIFEST.json"
    data = json.loads(manifest.read_text())
    data["version"] = "0.0.0"
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="version mismatch"):
        release.distributions(folder, info)
    data["version"] = info["version"]
    data["files"][0]["file"] = "../outside.whl"
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="Invalid manifest path"):
        release.distributions(folder, info)


def test_only_exact_existing_registry_bytes_are_skipped(tmp_path):
    existing = tmp_path / "existing.whl"
    new = tmp_path / "new.whl"
    existing.write_bytes(b"original")
    new.write_bytes(b"new")
    assert release.pending_files([existing, new], {existing.name: release.digest(existing)}) == [new]
    with pytest.raises(ValueError, match="use a new version"):
        release.pending_files([existing], {existing.name: "0" * 64})


def test_registry_verification_requires_every_distribution(tmp_path, monkeypatch):
    path = tmp_path / "file.whl"
    path.write_bytes(b"original")
    states = iter([{}, {path.name: release.digest(path)}])
    monkeypatch.setattr(release, "published_files", lambda _: next(states))
    monkeypatch.setattr(release.time, "sleep", lambda _: None)
    release.verify_pypi([path], release.metadata())


def test_existing_tags_are_never_moved(monkeypatch):
    monkeypatch.setattr(release, "gh", lambda *a, **kw: json.dumps({"object": {"type": "commit", "sha": "b" * 40}}))
    with pytest.raises(ValueError, match="will not be moved"):
        release.ensure_tag(release.metadata(), "owner/repo", "a" * 40, create=True)


def test_existing_github_assets_are_never_overwritten(tmp_path, monkeypatch):
    path = tmp_path / "asset.whl"
    path.write_bytes(b"verified")
    calls = []
    monkeypatch.setattr(release, "gh", lambda *a, **kw: calls.append(a))
    draft = {"draft": True, "assets": [{"name": path.name, "digest": "sha256:" + release.digest(path)}]}
    release.upload_assets(release.metadata(), "owner/repo", draft, [path])
    assert not calls
    draft["assets"][0]["digest"] = "sha256:" + "0" * 64
    with pytest.raises(ValueError, match="bytes differ"):
        release.upload_assets(release.metadata(), "owner/repo", draft, [path])
    assert not calls
