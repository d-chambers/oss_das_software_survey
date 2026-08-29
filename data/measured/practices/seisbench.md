---
id: seisbench
source: practices
scanned_at: '2026-08-29T06:15:21+00:00'
ref: main
tip: afac5f1ee200c00f9994410517f85c646095e56c
files: 216
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
  contributing: true
  lint: true
  typed: false
evidence:
  ci: .github/workflows/main_push.yml
  contributing: CONTRIBUTING.md
  docs: .readthedocs.yaml
  examples: examples/02a_deploy_model_on_streams_example.ipynb
  license_file: LICENSE
  lint: .pre-commit-config.yaml
  packaging: setup.py
  readme: README.md
  tests: tests/conftest.py
error: ''
missing: {}
---
