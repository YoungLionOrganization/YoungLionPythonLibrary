# Manual PyPI publishing

Normal publication is automated. See [Publishing and recovery](publishing.md).
Use this procedure only to recover the exact original verified release bundle.

1. Download the final release-bundle artifact from the GitHub Actions run.
2. Extract locally.
3. Validate the bundle/checksums.
4. Enter `pypi/`.
5. Verify existing PyPI filenames have the same SHA-256 hashes, then upload only
   missing distributions. For an entirely unpublished version:

```bash
python -m twine check *
python -m twine upload *
```

Normal Actions publication uses the organization `PYPI_API_TOKEN` secret.
Keep any manual credentials local. Do not upload `experimental/`.
