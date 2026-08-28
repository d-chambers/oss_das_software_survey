---
key: pypi/das-setup-helper
source: pypi
name: das-setup-helper
package: das-setup-helper
description: Public helper to setup crawlers and manage acquisitions in WIHP (EUROSTAT)
registry_url: https://pypi.org/project/das-setup-helper/
version: 0.1.0
last_release: '2026-08-22'
repository_url: null
repository_declared_in_metadata: false
license_stated: EUPL-1.2
author: Basile MANGOG
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# DAS Setup Helper

A Python CLI tool to set up crawlers and manage acquisitions in WIHP (EUROSTAT).
It provides three pipelines: creating crawlers, triggering acquisitions, and stopping them.

---

## Requirements

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) — fast Python package and project manager

Install uv (once, globally):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Installation

### From PyPI (recommended)

```bash
# Create a project directory
mkdir das-setup-helper && cd das-setup-helper

# Install the package in an isolated environment
uv add das-setup-helper
```

All three CLI commands (`das-setup-crawler`, `das-create-acq`, `das-stop-acq`) are then available via `uv run`.

### From source (contributors)

```bash
# Clone the repository
git clone <repo-url>
cd das-setup-helper

# Install all dependencies including dev tools
make sync
# or directly:
uv sync --extra dev
```

---

## Configuration

Copy the template and fill in your values:
```bash
cp env.sh.template env.sh
# edit env.sh with your settings
```

Key variables:

| Variable | Description |
|---|---|
| `STORAGE_BACKEND` | `local` (default) or `s3` |
| `USE_SECRET_MANAGER` | `false` (default, uses env vars) or `true` (uses AWS Secrets Manager) |
| `AWS_SECRET_MANAGER_NAME` | Secret name in Secrets Manager — only needed if `USE_SECRET_MANAGER=true` |
| `S3_AWS_WIHP_CONFIG_DIRECTORY` | Path to the config directory (local path or S3 prefix) |
| `S3_AWS_WIHP_INPUT_SOURCES_TO_CREATE` | Path to the input CSV file with sources to create |
| `S3_AWS_WHIP_READY_FOR_CRAWLING_DIRECTORY` | Directory where crawler outputs are written |
| `WIHP_API_URL` | WIHP API base URL |
| `WIHP_TOKEN_URL` | WIHP OAuth token endpoint |
| `WIHP_API_KEY` | WIHP API key |
| `WIHP_GROUP` | WIHP group (e.g. `/MNE`) |

### Local storage

When `STORAGE_BACKEND=local`, paths are local filesystem paths.
The `local_storage/` directory mirrors the S3 structure:

```
local_storage/
├── config/                   # input files
├── ready_for_crawling/       # crawler outputs
├── ready_to_export/
├── done/
└── staging/
"" source to create directory"
```

The only input file required to run `das-setup-crawler`:
```
local_storage/MNE/config/dashelper/sources_to_create.csv
```

Format (semicolon-separated):
```csv
mne_name;wikipedia_url
Airbus;https://en.wikipedia.org/wiki/Airbus
TotalEnergies;https://en.wikipedia.org/wiki/TotalEnergies
```

---

## Running the pipelines

Load your environment variables then run a pipeline:

```bash
source env.sh

# 1. Create a crawler from the input CSV
uv run das-setup-crawler
# or: make run-crawler

# 2. Trigger acquisitions for existing crawlers
uv run das-create-acq
# or: make run-acq

# 3. Stop running acquisitions
uv run das-stop-acq
# or: make run-stop
```

Pipeline order: **setup-crawler → create-acq → stop-acq**

---

## Development

```bash
# Run tests
make test

# Format code
make lint

# Refresh dependency lock (without upgrading)
make lock

# Upgrade all dependencies
make lock-upgrade
```

Available `make` targets:
```bash
make info
```

---

## Deployment (prod/staging)

In production (MWAA / Lambda), set:
```bash
USE_SECRET_MANAGER=true
AWS_SECRET_MANAGER_NAME=prod/DASHelper
STORAGE_BACKEND=s3
```

All other variables are loaded automatically from AWS Secrets Manager.
The IAM role must have `secretsmanager:GetSecretValue` permission on the secret.

---

## Release

```bash
# Build the package
make build

# Publish a development build to TestPyPI
make publish-test

# Publish a release build to PyPI
make publish
```

The package version is derived from Git tags and follows Python package versioning conventions (PEP 440):

- Tagged releases use stable versions such as `v1.2.3`.
- Untagged branch builds produce development versions such as `1.2.4.dev5`.

GitLab CI release flow:

- Branch `develop`: manual job `publish-internal` publishes the current branch build to the internal Python repository.
- Branch `test`: manual job `publish-testpypi` publishes the current branch build to TestPyPI.
- Branch `main`: manual jobs `prepare-release-patch`, `prepare-release-minor`, and `prepare-release-major` create the next Git tag.
- Tag pipeline `vX.Y.Z`: manual job `publish-pypi` publishes that tagged release to PyPI.

SonarQube runs in the `quality` stage for merge requests and for the `develop` and `main` branches.

To allow the release-tag job to push tags from CI, define these GitLab CI/CD variables:

- `REPO_PUSH_USER`
- `REPO_PUSH_TOKEN`

Also define the repository tokens used for publishing:

- `DOCKER_REGISTRY_USER`
- `DOCKER_REGISTRY_PASSWORD`
- `TEST_PYPI_TOKEN`
- `PYPI_TOKEN`

For SonarQube, also define:

- `SONAR_TOKEN`

## License

This project is distributed under the European Union Public Licence v1.2
(EUPL-1.2). The full licence text is available in [LICENSE](LICENSE) and on the
European Commission website:
https://commission.europa.eu/about/departments-and-executive-agencies/digital-services/open-source-strategy-history/european-union-public-licence_en

## Test and Deploy

Use the built-in continuous integration in GitLab.

* [Get started with GitLab CI/CD](https://docs.gitlab.com/ci/quick_start/)
* [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/user/application_security/sast/)
* [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/topics/autodevops/requirements/)
* [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/user/clusters/agent/)
* [Set up protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions fo
