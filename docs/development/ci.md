# Continuous integration

YoungLion v0.1 uses two workflows with deliberately separate responsibilities.

## `native-ci.yml` — source correctness

Runs on pushes to `main`, pull requests, and manual dispatches. It validates:

- native C++ builds on Ubuntu x86_64/ARM64, Windows, macOS Intel and Apple Silicon;
- the oldest and newest supported CPython lines used by the fast source matrix;
- strict compiler diagnostics (`-Werror` / `/WX`);
- Python syntax, smoke tests, pytest, and public stub coverage;
- clean PEP 517 source installs inside Debian, Arch Linux, Fedora, Rocky Linux 9,
  openSUSE Tumbleweed, and Alpine containers;
- an opt-in Windows ARM64 preview job when manually dispatched.

The distribution-container jobs intentionally install with `pip install .` in a
fresh virtual environment. They **must not** call `setup.py` with the distro's
preinstalled setuptools, because `pyproject.toml` is the authoritative source of
build requirements.

## `build-artifacts.yml` — candidates and verified publication

This workflow is manual (`workflow_dispatch`) and also runs for version tags.
Matching tags publish automatically; manual runs publish only when
`publish_release=true`. Its first job is a release preflight gate that verifies:

1. a tag, when present, exactly matches `v<project.version>`;
2. the obsolete pre-v0.1 automatic release workflow is absent;
3. strict native compilation succeeds;
4. smoke tests, pytest, syntax checks, stub coverage and semantic typing pass;
5. runtime/project versions agree and versioned release notes exist;
6. publication is requested from the default branch or matching version tag.

Only after preflight succeeds are the sdist and wheel matrices allowed to start.
The final job downloads the component artifacts and produces one
`YoungLion-<version>-release-bundle` artifact.

## macOS deployment target

The native extension uses C++17 `std::filesystem`. YoungLion therefore sets a
macOS deployment floor that is high enough for the libc++ filesystem APIs:

- Intel build fallback: macOS 10.15;
- Apple Silicon native fallback: macOS 11;
- cibuildwheel configuration: `MACOSX_DEPLOYMENT_TARGET = "10.15"`, which the
  wheel builder raises when the selected architecture requires a newer floor.

Do not remove this setting merely to produce an older-looking wheel tag; the
binary must never claim compatibility with an OS whose C++ runtime cannot load
features used by the extension.

## Release policy

After stable builds and bundle validation, publication stages a draft GitHub
Release, uploads only unpublished stable files to PyPI with the organization
`PYPI_API_TOKEN`, verifies every registry SHA-256 digest, then publishes the
GitHub Release. Existing assets must have identical bytes; tags are never moved.
See [Publishing and recovery](publishing.md). Artifact-only manual runs remain
available with `publish_release=false`.
