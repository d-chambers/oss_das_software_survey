"""Validated records shared by the numbered scripts."""

from __future__ import annotations

import re
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

    Licensing is a measured property of the ecosystem rather than an entry
    gate: excluding non-OSI code would make "what share is open" unanswerable.
    """

    #: An OSI-approved license, or a public-domain dedication such as CC0.
    OSI_APPROVED = "osi-approved"
    #: Published source under terms that fail the Open Source Definition.
    SOURCE_AVAILABLE = "source-available"
    #: Public source with no license file, which grants no reuse rights at all.
    UNLICENSED = "unlicensed"
    #: Terms exist but could not be resolved to either class on review.
    UNKNOWN = "unknown"


class DasFocus(StrEnum):
    """What the project is for; distinct from ``status``, which is scope."""

    #: Distributed acoustic sensing is the reason the project exists.
    DAS_NATIVE = "das-native"
    #: Fiber sensing, but temperature or strain rather than acoustic.
    OTHER_FIBER = "other-fiber"
    #: A general tool that supports DAS among other data types.
    DAS_SUPPORTING = "das-supporting"
    #: "DAS" expands to something else entirely.
    NOT_DAS = "not-das"


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
            value = value.removeprefix(prefix)
        if "/" not in value:
            raise ValueError("DOI must contain a slash")
        return value


class RegistryIds(BaseModel):
    pypi: list[str] = Field(default_factory=list)
    conda: list[str] = Field(default_factory=list)
    julia: list[str] = Field(default_factory=list)

    @field_validator("pypi")
    @classmethod
    def normalize_pypi(cls, value: list[str]) -> list[str]:
        """PEP 503 names, so ``Foo_Bar`` and ``foo-bar`` are measured once."""
        return sorted({re.sub(r"[-_.]+", "-", name).lower() for name in value})

    @field_validator("conda")
    @classmethod
    def normalize_conda(cls, value: list[str]) -> list[str]:
        out = set()
        for item in value:
            if "/" not in item:
                raise ValueError(f"conda id {item!r} must be channel/name")
            out.add(item.lower())
        return sorted(out)

    @field_validator("julia")
    @classmethod
    def unique_julia(cls, value: list[str]) -> list[str]:
        return sorted(set(value))


class Forge(BaseModel):
    """Where a project's source lives; recorded, not assumed."""

    model_config = ConfigDict(extra="forbid")

    kind: ForgeKind = ForgeKind.GITHUB
    host: str | None = None

    @field_validator("host")
    @classmethod
    def validate_host(cls, value: str | None) -> str | None:
        if value is None:
            return None
        host = value.strip().rstrip("/")
        if "://" in host or "/" in host or not host:
            raise ValueError("forge host must be a bare hostname")
        return host

    @model_validator(mode="after")
    def apply_default_host(self) -> Forge:
        if self.host is None:
            self.host = DEFAULT_FORGE_HOSTS[self.kind]
        return self


class ProjectRecord(BaseModel):
    """One catalogue entry: the frontmatter of ``data/curated/<id>.md``.

    The same schema is what an agent proposes in ``data/enriched/`` and what a
    reviewer approves in ``data/curated/``; ``sources`` and ``reviewed_at``
    are what the review step adds.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    name: str
    #: ``owner/name`` path on the forge; None for a registry-only package.
    repository: str | None = None
    repository_url: str | None = None
    homepage: str | None = None
    description: str
    status: CatalogStatus
    decision_reason: str
    primary_category: str
    capabilities: list[str] = Field(default_factory=list)
    das_focus: DasFocus = DasFocus.DAS_NATIVE
    license_spdx: str | None = None
    license_class: LicenseClass = LicenseClass.UNKNOWN
    forge: Forge = Field(default_factory=Forge)
    registries: RegistryIds = Field(default_factory=RegistryIds)
    publications: list[PublicationRef] = Field(default_factory=list)
    #: Candidate keys merged into this project: the map from findings to ids.
    sources: list[str] = Field(default_factory=list)
    reviewed_at: str | None = None
    #: Agent provenance carried over from the enriched proposal, if any.
    provenance: dict[str, Any] | None = None

    @field_validator("repository")
    @classmethod
    def validate_repository(cls, value: str | None) -> str | None:
        """Accept the nested groups that GitLab allows and GitHub does not."""
        if value is None:
            return None
        parts = [part for part in value.strip("/").split("/") if part]
        if len(parts) < 2 or len(parts) != len(value.strip("/").split("/")):
            raise ValueError("repository must be a namespace/name path")
        return "/".join(parts)

    @field_validator("capabilities", "sources")
    @classmethod
    def unique_sorted(cls, value: list[str]) -> list[str]:
        return sorted(set(value))

    @property
    def derived_url(self) -> str | None:
        if self.repository is None:
            return None
        return f"https://{self.forge.host}/{self.repository}"

    @property
    def owner(self) -> str | None:
        return None if self.repository is None else self.repository.split("/")[0]

    @property
    def forge_key(self) -> str | None:
        """``host/owner/name``, lowercased; the candidate key of the repository."""
        if self.repository is None:
            return None
        return f"{self.forge.host}/{self.repository}".lower()

    @property
    def key(self) -> str:
        """Identity used to detect duplicate catalogue entries."""
        if self.forge_key:
            return self.forge_key
        if self.registries.pypi:
            return f"pypi/{self.registries.pypi[0].lower()}"
        return f"id/{self.id}"

    @model_validator(mode="after")
    def fill_repository_url(self) -> ProjectRecord:
        """A stored link that disagrees with the path it came from is rejected."""
        derived = self.derived_url
        if self.repository_url is None:
            self.repository_url = derived
        elif derived is None:
            raise ValueError("repository_url given without a repository")
        elif self.repository_url.rstrip("/") != derived:
            raise ValueError(
                f"repository_url {self.repository_url!r} does not match {derived!r}"
            )
        return self

    @model_validator(mode="after")
    def validate_license_class(self) -> ProjectRecord:
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
