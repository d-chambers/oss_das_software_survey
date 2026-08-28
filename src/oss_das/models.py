"""Validated records shared by collection, analysis, and rendering scripts."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CatalogStatus(StrEnum):
    INCLUDED = "included"
    WATCHLIST = "watchlist"
    EXCLUDED = "excluded"


class ForgeKind(StrEnum):
    """The API dialect a code host speaks, not the host itself.

    One kind covers many hosts: every GitLab instance answers the same
    ``/api/v4`` calls, and Gitea and Codeberg share ``/api/v1``. Keeping kind
    and host separate is what lets a self-hosted institutional forge be
    catalogued without a bespoke client per university.
    """

    GITHUB = "github"
    GITLAB = "gitlab"
    GITEA = "gitea"


#: The public host each dialect defaults to when a project does not name one.
DEFAULT_FORGE_HOSTS = {
    ForgeKind.GITHUB: "github.com",
    ForgeKind.GITLAB: "gitlab.com",
    ForgeKind.GITEA: "codeberg.org",
}


class LicenseClass(StrEnum):
    """How freely a catalogued code can actually be reused.

    Licensing is treated as a measured property of the ecosystem rather than
    as an entry gate. Excluding non-OSI code would answer "how much OSI
    software exists" with a list built by excluding everything else, which
    cannot then be used to say what share of the ecosystem is open.
    """

    #: An OSI-approved license, or a public-domain dedication such as CC0.
    OSI_APPROVED = "osi-approved"
    #: Published source under terms that fail the Open Source Definition,
    #: typically a NonCommercial clause or an academic/commercial split.
    SOURCE_AVAILABLE = "source-available"
    #: Public source with no license file, which grants no reuse rights at all.
    UNLICENSED = "unlicensed"
    #: Terms exist but could not be resolved to either class on review.
    UNKNOWN = "unknown"


class MissingReason(StrEnum):
    NOT_APPLICABLE = "not_applicable"
    NOT_PUBLISHED = "not_published"
    UNAVAILABLE = "unavailable"
    FETCH_ERROR = "fetch_error"
    UNKNOWN = "unknown"


class PublicationRef(BaseModel):
    doi: str
    role: Literal["canonical", "related"] = "related"
    note: str | None = None

    @field_validator("doi")
    @classmethod
    def normalize_doi(cls, value: str) -> str:
        value = value.strip().lower()
        for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
            if value.startswith(prefix):
                value = value.removeprefix(prefix)
        if "/" not in value:
            raise ValueError("DOI must contain a slash")
        return value


class RegistryIds(BaseModel):
    pypi: list[str] = Field(default_factory=list)
    conda: list[str] = Field(default_factory=list)
    julia: list[str] = Field(default_factory=list)


class Forge(BaseModel):
    """Where a project's source actually lives.

    Defaulting to GitHub keeps existing entries unchanged, but the field is
    explicit so that "GitHub" is a recorded finding about a project rather
    than an assumption baked into every URL the pipeline builds.
    """

    model_config = ConfigDict(extra="forbid")

    kind: ForgeKind = ForgeKind.GITHUB
    host: str | None = None

    @field_validator("host")
    @classmethod
    def validate_host(cls, value: str | None) -> str | None:
        if value is None:
            return None
        host = value.strip().rstrip("/")
        if "://" in host or "/" in host:
            raise ValueError("forge host must be a bare hostname")
        if not host:
            raise ValueError("forge host must not be empty")
        return host

    @model_validator(mode="after")
    def apply_default_host(self) -> Forge:
        if self.host is None:
            self.host = DEFAULT_FORGE_HOSTS[self.kind]
        return self


class ProjectRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    name: str
    repository: str
    repository_url: str | None = None
    homepage: str | None = None
    description: str
    status: CatalogStatus
    decision_reason: str
    primary_category: str
    capabilities: list[str] = Field(default_factory=list)
    license_spdx: str | None = None
    license_class: LicenseClass = LicenseClass.UNKNOWN
    forge: Forge = Field(default_factory=Forge)
    registries: RegistryIds = Field(default_factory=RegistryIds)
    publications: list[PublicationRef] = Field(default_factory=list)

    @field_validator("repository")
    @classmethod
    def validate_repository(cls, value: str) -> str:
        """Accept the nested groups that GitLab allows and GitHub does not."""
        parts = [part for part in value.strip("/").split("/") if part]
        if len(parts) < 2 or len(parts) != len(value.strip("/").split("/")):
            raise ValueError("repository must be a namespace/name path")
        return "/".join(parts)

    @property
    def derived_url(self) -> str:
        return f"https://{self.forge.host}/{self.repository}"

    @property
    def owner(self) -> str:
        """The account or top-level group that publishes the repository.

        Recorded as its own field rather than left implicit in the path,
        because who builds an ecosystem is a claim the dataset should be able
        to state and be checked on — including where one organization, this
        study's own included, accounts for an outsized share of it.
        """
        return self.repository.split("/")[0]

    @property
    def forge_key(self) -> str:
        """The identity used to detect duplicate catalog entries.

        Two forges can host the same ``owner/name`` path for unrelated
        projects, so the host has to be part of the key.
        """
        return f"{self.forge.host}/{self.repository}".lower()

    @field_validator("capabilities")
    @classmethod
    def unique_capabilities(cls, value: list[str]) -> list[str]:
        return sorted(set(value))

    @model_validator(mode="after")
    def fill_repository_url(self) -> ProjectRecord:
        """Keep the written link and the repository path from disagreeing.

        The URL is stored so a reader has the address in front of them, but a
        stored copy of a derived value goes stale the moment someone corrects
        the path it came from. Rather than trust it, a mismatch is rejected at
        load time — a wrong link in a catalog is worse than no link.
        """
        if self.repository_url is None:
            self.repository_url = self.derived_url
        elif self.repository_url.rstrip("/") != self.derived_url:
            raise ValueError(
                f"repository_url {self.repository_url!r} does not match "
                f"{self.derived_url!r}"
            )
        return self

    @model_validator(mode="after")
    def validate_license_class(self) -> ProjectRecord:
        """Keep the license class and the identifier from contradicting each other."""
        if self.license_class == LicenseClass.UNLICENSED and self.license_spdx:
            raise ValueError("an unlicensed project must not carry an SPDX id")
        classified = {LicenseClass.OSI_APPROVED, LicenseClass.SOURCE_AVAILABLE}
        if self.license_class in classified and not self.license_spdx:
            raise ValueError(f"{self.license_class} requires a license_spdx")
        return self

    @model_validator(mode="after")
    def validate_canonical_publication(self) -> ProjectRecord:
        canonical = [item for item in self.publications if item.role == "canonical"]
        if len(canonical) > 1:
            raise ValueError("a project may have at most one canonical publication")
        dois = [item.doi for item in self.publications]
        if len(dois) != len(set(dois)):
            raise ValueError("publication DOIs must be unique within a project")
        return self


class MetricObservation(BaseModel):
    project_id: str
    metric: str
    value: float | int | None = None
    unit: str
    window_start: str | None = None
    window_end: str | None = None
    source_url: str
    fetched_at: str
    missing_reason: MissingReason | None = None

    @model_validator(mode="after")
    def validate_value_or_reason(self) -> MetricObservation:
        if (self.value is None) == (self.missing_reason is None):
            raise ValueError("exactly one of value and missing_reason is required")
        return self


class PublicationRecord(BaseModel):
    project_id: str
    doi: str
    role: Literal["canonical", "related"]
    title: str | None = None
    publication_year: int | None = None
    work_type: str | None = None
    cited_by_count: int | None = None
    openalex_id: str | None = None
    source_url: str
    fetched_at: str
    missing_reason: MissingReason | None = None


class CapabilityRecord(BaseModel):
    project_id: str
    capability: str
    present: bool = True
    source: str = "curated"


class SnapshotManifest(BaseModel):
    schema_version: str = "1"
    snapshot_date: str
    generated_at: str
    project_count: int
    included_count: int
    files: dict[str, str]
    source_notes: dict[str, Any] = Field(default_factory=dict)
