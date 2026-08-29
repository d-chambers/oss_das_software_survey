---
id: lightguide
source: practices
scanned_at: '2026-08-29T06:15:21+00:00'
ref: main
tip: e5084944281cf0cdf9152a1e55fd8a60dbcd8e46
files: 44
practices:
  readme: true
  license_file: true
  packaging: true
  tests: true
  ci: true
  coverage: false
  docs: true
  examples: true
  changelog: false
  contributing: false
  lint: true
  typed: false
evidence:
  ci: .github/workflows/lint.yml
  docs: doc/source/conf.py
  examples: examples/1-import-data.ipynb
  license_file: LICENSE
  lint: .pre-commit-config.yaml
  packaging: setup.py
  readme: README.md
  tests: tests/test_gf.py
error: ''
missing: {}
---
