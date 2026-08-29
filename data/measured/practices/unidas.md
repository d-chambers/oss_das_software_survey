---
id: unidas
source: practices
scanned_at: '2026-08-29T06:15:21+00:00'
ref: main
tip: 3af371f3cbd56c558de805f852c94c14c66f4652
files: 16
practices:
  readme: true
  license_file: true
  packaging: true
  tests: true
  ci: true
  coverage: true
  docs: false
  examples: false
  changelog: false
  contributing: true
  lint: true
  typed: false
evidence:
  ci: .github/workflows/lint.yml
  contributing: .github/ISSUE_TEMPLATE/bug_report.md
  coverage: README badge
  license_file: LICENSE
  lint: .pre-commit-config.yaml
  packaging: pyproject.toml
  readme: README.md
  tests: test/conftest.py
error: ''
missing: {}
---
