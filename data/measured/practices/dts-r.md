---
id: dts-r
source: practices
scanned_at: '2026-08-29T06:15:20+00:00'
ref: master
tip: 589bd247848229b2be5b2e8919855642c67f782c
files: 181
practices:
  readme: true
  license_file: false
  packaging: true
  tests: true
  ci: true
  coverage: true
  docs: true
  examples: false
  changelog: false
  contributing: false
  lint: false
  typed: false
evidence:
  ci: .github/workflows/R-CMD-check.yaml
  coverage: codecov.yml
  docs: man/dts.Rd
  packaging: NAMESPACE
  readme: README.md
  tests: tests/testthat.R
error: ''
missing: {}
---
