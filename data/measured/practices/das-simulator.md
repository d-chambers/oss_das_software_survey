---
id: das-simulator
source: practices
scanned_at: '2026-08-29T06:15:20+00:00'
ref: main
tip: aeaae649f2e6af5fdaa73a789f2b9e08fae62002
files: 87
practices:
  readme: true
  license_file: true
  packaging: true
  tests: true
  ci: true
  coverage: false
  docs: false
  examples: false
  changelog: false
  contributing: false
  lint: false
  typed: false
evidence:
  ci: .github/workflows/maven-build.yml
  license_file: LICENSE
  packaging: pom.xml
  readme: readme.adoc
  tests: das-producer/src/test/java/com/equinor/DasProducerTest.java
error: ''
missing: {}
---
