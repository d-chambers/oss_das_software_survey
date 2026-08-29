---
id: dasstore
source: practices
scanned_at: '2026-08-29T06:15:20+00:00'
ref: main
tip: 14075158b25b1be6fb7ba4caa2a9262846e289ff
files: 45
practices:
  readme: true
  license_file: true
  packaging: true
  tests: true
  ci: true
  coverage: true
  docs: false
  examples: true
  changelog: false
  contributing: false
  lint: true
  typed: false
evidence:
  ci: .github/workflows/test.yaml
  coverage: codecov.yml
  examples: tutorials/tutorial_client_zarr_backend_SeaDAS.ipynb
  license_file: LICENSE
  lint: .flake8
  packaging: pyproject.toml
  readme: README.md
  tests: tests/test_zarr.py
error: ''
missing: {}
---
