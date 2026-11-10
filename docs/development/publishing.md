# Automated publishing and recovery

The distribution workflow builds, tests and publishes the exact stable files
recorded in its release manifest. The organization Actions secret must be named
`PYPI_API_TOKEN` and must grant this repository access. Its value is used only by
the pinned PyPA publishing action; no token belongs in source or release assets.
GitHub Releases use the workflow's `GITHUB_TOKEN` with job-scoped contents-write
permission. No personal access token is required.

## Publish a version

1. Update `project.version` in `pyproject.toml`, `YoungLion.__version__`, README
   and the versioned section in `Releases.md`. Commit the complete release to
   the default branch.
2. Either push the matching `vMAJOR.MINOR.PATCH` tag, or manually run
   **Build Distribution Artifacts** on the default branch with
   `publish_release=true`. The manual path creates the matching tag after builds
   succeed; the tag is never moved to another commit.
3. The workflow runs strict native compilation, runtime tests, structural and
   semantic typing checks. It builds the sdist and stable CPython 3.10–3.14 wheels
   on Linux x86_64/ARM64, Windows x64 and macOS Intel/Apple Silicon. Installed
   stable wheels run the complete applicable pytest suite.
4. The validated bundle is staged as a draft GitHub Release. All stable
   distributions and the checksum manifest are attached. Experimental targets
   remain in the downloadable Actions bundle and are never selected for PyPI.
5. The PyPI job verifies any existing filenames against their SHA-256 digests,
   uploads only unpublished distributions using `PYPI_API_TOKEN`, and verifies
   the complete registry set. Different bytes under an existing filename fail.
6. A final job verifies the registry and staged assets again, then makes the
   GitHub Release public and marks it latest.

A normal manual run with `publish_release=false` builds artifacts without
publishing. Publication from another branch is rejected. A tag must exactly match
the project version. Release jobs use the source commit from the triggering event
and verify it against the artifact manifest and tag target.

## Recover a partial publication

Use **Re-run failed jobs** on the original workflow run. This reuses the original
component/bundle artifacts rather than rebuilding a different set of bytes under
the same version. Identical existing PyPI filenames and GitHub assets are verified
and retained; missing files are uploaded. A GitHub Release stays a draft until
all expected PyPI filenames and hashes are present.

If the secret check fails, share the organization `PYPI_API_TOKEN` with this
repository in organization Actions settings, then rerun the failed jobs. Secret
listing permissions in an external GitHub integration are separate from access
inside Actions. A project-scoped PyPI token must permit the YoungLion project.

Do not delete/re-upload registry files or force-move a published tag. If the
source or an existing asset's contents need to change, use a new version.
Rebuilding all jobs after some files have already been published can produce
different native binaries or archive timestamps, which correctly fails the
hash checks.

For exceptional manual recovery, download the exact original bundle, run
`tools/validate_release_bundle.py`, compare existing registry hashes, and upload
only missing files from `pypi/`. Do not include `experimental/`. The automation
normally performs these steps without local credentials.
