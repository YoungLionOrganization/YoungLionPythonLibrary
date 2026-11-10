#!/usr/bin/env python3
"""Stage immutable release assets, publish pending files and verify registry bytes.

Release tooling runs on Python 3.11+; the library itself supports Python 3.10+.
PyPI credentials are handled by the publishing action, never by this script.
"""
from __future__ import annotations

import argparse
import ast
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import tomllib
import urllib.error
import urllib.request
import zipfile
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def metadata(root: Path = ROOT) -> dict[str, str]:
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = project["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Publication requires a stable MAJOR.MINOR.PATCH version")
    tree = ast.parse((root / "src/YoungLion/__init__.py").read_text(encoding="utf-8"))
    runtime = next(ast.literal_eval(node.value) for node in tree.body
                   if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets))
    if runtime != version:
        raise ValueError("Runtime and project versions differ")
    release_notes(root, version)
    return {"name": project["name"], "version": version, "tag": f"v{version}"}


def release_notes(root: Path, version: str) -> str:
    text = (root / "Releases.md").read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(version)}\s+[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match or not match.group(1).strip():
        raise ValueError(f"Missing release notes for {version}")
    repo = os.environ.get("GITHUB_REPOSITORY", "YoungLionOrganization/YoungLionPythonLibrary")
    return match.group(1).strip().replace("](docs/", f"](https://github.com/{repo}/blob/v{version}/docs/") + "\n"


def validate_ref(info: dict[str, str]) -> None:
    if os.environ.get("PUBLISH_RELEASE", "false").lower() != "true":
        return
    ref = os.environ.get("GITHUB_REF", "")
    main = os.environ.get("DEFAULT_BRANCH", "main")
    if ref not in {f"refs/heads/{main}", f"refs/tags/{info['tag']}"}:
        raise ValueError("Publish from the default branch or the matching version tag")


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def distributions(bundle: Path, info: dict[str, str], sha: str | None = None) -> list[Path]:
    manifest = json.loads((bundle / "checksums/MANIFEST.json").read_text(encoding="utf-8"))
    if manifest["version"] != info["version"] or manifest["project"] != info["name"]:
        raise ValueError("Release manifest identity/version mismatch")
    if sha and manifest["git_sha"] != sha:
        raise ValueError("Release artifacts were built from a different commit")
    files = []
    for row in manifest["files"]:
        relative = Path(row["file"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Invalid manifest path")
        path = bundle / relative
        if path.stat().st_size != row["size"] or digest(path) != row["sha256"]:
            raise ValueError(f"Release file checksum mismatch: {relative}")
        if row["channel"] != "pypi":
            continue
        if relative.parent != Path("pypi"):
            raise ValueError("Stable distributions must be directly inside pypi/")
        if path.suffix == ".whl":
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                headers = [name for name in names if name.endswith(".dist-info/METADATA")]
                if len(headers) != 1:
                    raise ValueError(f"Invalid wheel metadata: {path.name}")
                data = archive.read(headers[0])
                resources = [*(ROOT / "src/YoungLion").rglob("*.pyi"),
                             *(ROOT / "src/YoungLion").rglob("*.py")]
                for source in resources:
                    resource = source.relative_to(ROOT / "src").as_posix()
                    if resource not in names or archive.read(resource) != source.read_bytes():
                        raise ValueError(f"Missing/stale wheel resource: {resource}")
                if "YoungLion/py.typed" not in names or any(name.endswith((".cpp", ".inc")) for name in names):
                    raise ValueError(f"Invalid wheel source/typing layout: {path.name}")
                if not any(name.startswith("YoungLion/_native.") and name.endswith((".so", ".pyd")) for name in names):
                    raise ValueError(f"Missing native extension: {path.name}")
        elif path.name.endswith(".tar.gz"):
            with tarfile.open(path) as archive:
                headers = [member for member in archive.getmembers()
                           if member.name.endswith("/PKG-INFO") and member.name.count("/") == 1]
                if len(headers) != 1:
                    raise ValueError(f"Invalid sdist metadata: {path.name}")
                data = archive.extractfile(headers[0]).read()
        else:
            raise ValueError(f"Unexpected stable file: {path.name}")
        package = BytesParser().parsebytes(data)
        if package["Name"].lower() != info["name"].lower() or package["Version"] != info["version"]:
            raise ValueError(f"Distribution metadata mismatch: {path.name}")
        files.append(path)
    if not any(path.suffix == ".whl" for path in files) or sum(path.name.endswith(".tar.gz") for path in files) != 1:
        raise ValueError("Release requires wheels and exactly one source distribution")
    actual = {path.name for path in (bundle / "pypi").iterdir() if path.is_file()}
    if actual != {path.name for path in files}:
        raise ValueError("Stable directory differs from its manifest")
    return sorted(files)


def published_files(info: dict[str, str]) -> dict[str, str]:
    try:
        with urllib.request.urlopen(
                f"https://pypi.org/pypi/{info['name']}/{info['version']}/json", timeout=30) as response:
            data = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return {}
        raise
    return {row["filename"]: row["digests"]["sha256"] for row in data["urls"]}


def pending_files(files: list[Path], published: dict[str, str]) -> list[Path]:
    pending = []
    for path in files:
        if path.name in published:
            if published[path.name] != digest(path):
                raise ValueError(f"Published bytes differ for {path.name}; use a new version")
        else:
            pending.append(path)
    return pending


def verify_pypi(files: list[Path], info: dict[str, str]) -> None:
    for attempt in range(8):
        missing = pending_files(files, published_files(info))
        if not missing:
            print(f"Verified {len(files)} PyPI filenames and SHA-256 digests.")
            return
        if attempt < 7:
            time.sleep(min(2 ** attempt, 15))
    raise ValueError(f"PyPI is missing {len(missing)} expected distributions")


def gh(*args: str, optional: bool = False) -> str | None:
    result = subprocess.run(["gh", *args], text=True, capture_output=True)
    if result.returncode:
        if optional and any(marker in result.stderr.lower() for marker in ("not found", "http 404")):
            return None
        raise RuntimeError(result.stderr.strip())
    return result.stdout


def ensure_tag(info: dict[str, str], repo: str, sha: str, *, create: bool) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("A full source commit SHA is required")
    result = gh("api", f"repos/{repo}/git/ref/tags/{info['tag']}", optional=True)
    if result is None:
        if not create:
            raise ValueError("Release tag is missing")
        gh("api", f"repos/{repo}/git/refs", "--method", "POST",
           "-f", f"ref=refs/tags/{info['tag']}", "-f", f"sha={sha}")
        return
    target = json.loads(result)["object"]
    for _ in range(8):
        if target["type"] == "commit":
            break
        if target["type"] != "tag":
            raise ValueError("Release tag must point to a commit")
        target = json.loads(gh("api", f"repos/{repo}/git/tags/{target['sha']}"))["object"]
    if target["type"] != "commit" or target["sha"] != sha:
        raise ValueError("Release tag points to another commit; it will not be moved")


def read_release(info: dict[str, str], repo: str) -> dict | None:
    result = gh("release", "view", info["tag"], "--repo", repo, "--json", "apiUrl", optional=True)
    if result is None:
        return None
    return json.loads(gh("api", json.loads(result)["apiUrl"]))


def upload_assets(info: dict[str, str], repo: str, release: dict, files: list[Path]) -> None:
    assets = {asset["name"]: asset for asset in release["assets"]}
    for path in files:
        existing = assets.get(path.name)
        if existing:
            known = existing.get("digest")
            if not known:
                with tempfile.TemporaryDirectory() as directory:
                    gh("release", "download", info["tag"], "--repo", repo,
                       "--pattern", path.name, "--dir", directory)
                    known = "sha256:" + digest(Path(directory) / path.name)
            if known != "sha256:" + digest(path):
                raise ValueError(f"Existing GitHub asset bytes differ: {path.name}")
        else:
            if not release["draft"]:
                raise ValueError("Published GitHub release is missing a staged asset")
            gh("release", "upload", info["tag"], str(path), "--repo", repo)


def stage(bundle: Path, files: list[Path], info: dict[str, str], repo: str, sha: str) -> None:
    ensure_tag(info, repo, sha, create=True)
    release = read_release(info, repo)
    if release is None:
        with tempfile.TemporaryDirectory() as directory:
            notes = Path(directory) / "notes.md"
            notes.write_text(release_notes(ROOT, info["version"]), encoding="utf-8")
            gh("release", "create", info["tag"], "--repo", repo, "--verify-tag",
               "--target", sha, "--draft", "--title", f"YoungLion {info['tag']}",
               "--notes-file", str(notes))
        release = read_release(info, repo)
    assets = [*files, bundle / "checksums/MANIFEST.json", bundle / "checksums/SHA256SUMS.txt"]
    upload_assets(info, repo, release, assets)
    print(f"Staged {len(assets)} verified assets for {info['tag']}.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["metadata", "notes", "pending", "verify-pypi", "stage", "finalize"])
    parser.add_argument("--bundle", type=Path, default=Path("release-bundle"))
    parser.add_argument("--output", type=Path, default=Path("pending"))
    args = parser.parse_args()
    info = metadata()
    if args.command == "metadata":
        validate_ref(info)
        print(json.dumps(info))
        return
    if args.command == "notes":
        print(release_notes(ROOT, info["version"]), end="")
        return
    sha = os.environ.get("GITHUB_SHA")
    files = distributions(args.bundle, info, sha)
    if args.command == "pending":
        pending = pending_files(files, published_files(info))
        args.output.mkdir(parents=True, exist_ok=True)
        if any(args.output.iterdir()):
            raise ValueError("Pending upload directory must be empty")
        for path in pending:
            shutil.copyfile(path, args.output / path.name)
        if output := os.environ.get("GITHUB_OUTPUT"):
            with open(output, "a", encoding="utf-8") as stream:
                stream.write(f"has_files={str(bool(pending)).lower()}\n")
        print(f"{len(pending)} distributions need uploading; {len(files) - len(pending)} already verified.")
    elif args.command == "verify-pypi":
        verify_pypi(files, info)
    else:
        repo = os.environ["GITHUB_REPOSITORY"]
        if args.command == "stage":
            validate_ref(info)
            stage(args.bundle, files, info, repo, sha or "")
        else:
            ensure_tag(info, repo, sha or "", create=False)
            verify_pypi(files, info)
            release = read_release(info, repo)
            if not release:
                raise ValueError("Expected staged GitHub release")
            upload_assets(info, repo, release, files)
            if release["draft"]:
                gh("release", "edit", info["tag"], "--repo", repo, "--draft=false", "--latest")
            print(f"Published https://github.com/{repo}/releases/tag/{info['tag']}")


if __name__ == "__main__":
    main()
