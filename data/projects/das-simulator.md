---
curated:
  id: das-simulator
  name: fiberoptics-das-simulator
  repository: equinor/fiberoptics-das-simulator
  repository_url: https://github.com/equinor/fiberoptics-das-simulator
  homepage: null
  description: Reference implementation of a real-time DAS producer for interrogator interfaces.
  status: included
  decision_reason: Reusable DAS reference implementation under Apache-2.0; the only catalogued project
    written in Java.
  primary_category: modeling
  capabilities:
  - interoperability
  - simulation
  - streaming
  license_spdx: Apache-2.0
  license_class: osi-approved
  forge:
    kind: github
    host: github.com
  registries:
    pypi: []
    conda: []
    julia: []
  publications: []
collected:
  scanned_at: '2026-08-18T06:37:17+00:00'
  snapshot: '2026-08-17'
  visibility: public
  language: Java
  stars: 2
  forks: 3
  contributors: 5
  releases: 4
  commits: 230
  last_commit_at: '2026-02-17T10:13:52Z'
  created_at: '2020-11-13T08:11:44Z'
  latest_release_at: '2021-10-12T08:30:27Z'
  archived: false
  lines_of_code_estimate: 9771
  loc_basis: language bytes / 32, notebooks excluded
  dependencies: []
  has_docs: false
  has_tests: false
  has_ci: true
  unavailable:
    pypi_downloads_total: no free source publishes all-time PyPI totals
    conda_downloads_180d: anaconda.org publishes a cumulative count only, with no time series
summary:
  agent: das-summarizer
  models:
  - claude-haiku-4-5-20251001
  - claude-sonnet-5
  ran_at: 2026-08-20 08:09:25+00:00
  duration_seconds: 23.0
  turns: 3
  input_tokens: 13091
  output_tokens: 1584
  cache_read_tokens: 110630
  cache_write_tokens: 1855
  total_tokens: 127160
  api_list_cost_usd: 0.0762
  provenance: token counts and model identity come from the API response, not from the agent's self-report
---

# fiberoptics-das-simulator

Source: [equinor/fiberoptics-das-simulator](https://github.com/equinor/fiberoptics-das-simulator)

## Summary

fiberoptics-das-simulator is a reference implementation that emulates a physical DAS (Distributed Acoustic Sensing) interrogator talking to Equinor's internal DAS streaming platform. It generates synthetic amplitude data sized to a configurable fiber loci count, batches samples into "fiber vector shots," and attempts to reproduce the timing of a real interrogator's data transmission, publishing the result to Kafka. It ships two variants: one producing random data and one replaying static, known test data for repeatable testing. A remote-control mode lets an external caller start, pause, and stop acquisition via REST calls, with profile switching. This is infrastructure for testing and developing downstream DAS ingestion and streaming pipelines against something that behaves like a real interrogator, rather than a scientific processing or analysis toolkit — its users would be engineers building or validating Equinor's DAS data platform, not researchers analyzing fiber-sensing signals.

## Details

- **Interface:** service/CLI — a Java application packaged as a JAR, deployed via Docker Compose, exposing REST endpoints (start, apply, stop) for acquisition control
- **Data formats:** ProdML 2.0-compliant acquisition metadata; JSON for acquisition handshakes/configuration; Kafka Avro serialization via Schema Registry
- **Key dependencies:** Java 21, Kafka, Confluent Schema Registry, Docker/Docker Compose, Maven (build), optional Kafka UI for inspection
- **Scope signals:** small project (~230 commits, 2 stars, 3 forks), Apache 2.0 licensed, not open to external contributions, includes health checks and graceful shutdown suggesting internal production/testing use rather than a general community tool
- **Source visible:** yes — full source present, with directories including das-producer, simulator-box-unit, simulator-common, static-data-unit, dependson-services, and remote-control-profiles
- **Sources read:** https://github.com/equinor/fiberoptics-das-simulator
