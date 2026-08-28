"""HTTP clients for public ecosystem metadata sources."""

from oss_das.clients.forge import ForgeClient
from oss_das.clients.gitea import GiteaClient
from oss_das.clients.github import GitHubClient
from oss_das.clients.gitlab import GitLabClient
from oss_das.clients.julia import JuliaRegistryClient
from oss_das.clients.openalex import OpenAlexClient
from oss_das.clients.packages import CondaClient, PyPIClient, PyPIStatsClient

__all__ = [
    "CondaClient",
    "ForgeClient",
    "GitHubClient",
    "GitLabClient",
    "GiteaClient",
    "JuliaRegistryClient",
    "OpenAlexClient",
    "PyPIClient",
    "PyPIStatsClient",
]
