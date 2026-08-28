#!/usr/bin/env python3
"""Build the methodology, limitations, and reproducibility page."""

from __future__ import annotations

from oss_das.cli import resolve_snapshot_date, snapshot_parser
from oss_das.site import render_page

BODY = """
<h2>Inclusion policy</h2>
<p>The catalog contains public repositories whose primary reusable functionality handles, processes, models, visualizes, evaluates, stores, or analyzes DAS data, and which expose a usable library, command-line interface, or application. Licensing is <em>not</em> an entry condition. Every such code is catalogued and its reuse terms are recorded as a separate property, because a list assembled by discarding non-open code cannot afterwards be used to say what share of the ecosystem is open. Tutorials, data-only repositories, paper-figure scripts, cross-host duplicates, generic tools merely applied to DAS, and unrelated projects that share the acronym remain discoverable but excluded, each with a recorded reason.</p>
<p>The watchlist no longer means “license unclear”. It now marks projects whose <em>scope or reusability</em> is unresolved: distributed temperature and strain sensing packages, which are fiber-optic sensing but not acoustic, and repositories whose usable interface could not be established.</p>

<h2>License classes</h2>
<p>Each project carries one reviewed class alongside its SPDX identifier.</p>
<ul>
  <li><strong>osi-approved:</strong> an OSI-approved license or a public-domain dedication. This is the count that answers “how much of this ecosystem is open source”.</li>
  <li><strong>source-available:</strong> source is published under terms that fail the Open Source Definition, typically a NonCommercial clause or an academic/commercial split.</li>
  <li><strong>unlicensed:</strong> public source with no license file. Default copyright applies, so no reuse rights are granted at all — a materially different situation from a permissive license, and one that is common in this ecosystem.</li>
  <li><strong>unknown:</strong> terms exist but could not be resolved to either class, such as a content license applied to a code repository.</li>
</ul>

<h2>Discovery and curation</h2>
<p><code>a010_discover_projects.py</code> probes several code hosts and records what each probe saw.</p>
<ul>
  <li><strong>Paged GitHub search</strong> over fifteen queries. Earlier runs issued a single request per query and therefore silently kept only the first hundred of several hundred matches; the search is now paged, and each query records the total GitHub claims alongside the number actually retrieved, so a truncated query is visible in <code>discovery_coverage.csv</code> instead of invisible.</li>
  <li><strong>Vocabulary beyond the acronym.</strong> Queries cover both fiber spellings, the physics names (<code>phase-sensitive OTDR</code>, <code>φ-OTDR</code>), the neighbouring modalities, the interrogator vendors, and explicit MATLAB, Julia, and R language filters. Interrogator-adjacent tooling frequently never writes the words “distributed acoustic sensing” anywhere a phrase search would reach it.</li>
  <li><strong>Non-GitHub hosts.</strong> GitLab (gitlab.com, GFZ, USGS, Helmholtz) and Gitea/Forgejo (Codeberg, the Pyrocko forge) are searched through their own APIs. This is what surfaces GEOFON's <code>dastools</code>, which is not on GitHub at all.</li>
  <li><strong>Organization enumeration.</strong> Every owner already in the catalog has its full repository list walked, which finds new work before its description contains any searchable phrase.</li>
</ul>
<p>Sources searched by hand that returned nothing reusable are worth stating too: the MATLAB File Exchange has no DAS submissions; the Journal of Open Source Software has published no DAS paper; CRAN carries no DAS package; and the Julia General registry contains no DAS package, so the Julia entries here install by URL only. Zenodo software records were searched and yielded only paper-companion code already reachable from its repository. Discovery never changes the registry; a person reviews identity, scope, license class, capabilities, registry names, and publication associations in <code>data/projects/</code>, one markdown file per project whose <code>curated</code> frontmatter block no script writes.</p>

<h2>Metric definitions</h2>
<ul>
  <li><strong>Repository:</strong> point-in-time stars, forks, contributors, releases, dates, language, archive state, and default-branch path signals, taken from whichever host holds the project. Continuous integration is probed per host, since a GitLab project keeps its pipeline in <code>.gitlab-ci.yml</code> rather than in GitHub's workflow directory.</li>
  <li><strong>Contributors are not strictly comparable across hosts.</strong> GitHub counts linked accounts with bots removed; GitLab reports commit identities, deduplicated here by author name. Each record states which basis produced it.</li>
  <li><strong>Neither is last activity.</strong> GitHub publishes a last-push timestamp. GitLab publishes only last activity, which also moves on issue and merge-request traffic, so a GitLab project can look more recently touched than its code actually is.</li>
  <li><strong>PyPI:</strong> last-30-day and available daily download history from PyPI Stats with known mirrors excluded. Automated installations remain.</li>
  <li><strong>Conda:</strong> cumulative download counts summed across artifacts in each explicitly declared Anaconda.org channel. These are not combined with PyPI.</li>
  <li><strong>Julia:</strong> Julia publishes no download counts, so the only verifiable claim is General-registry membership, which is checked per declared package and reported as registered or unregistered.</li>
  <li><strong>Citations:</strong> OpenAlex <code>cited_by_count</code> for manually associated DOIs. Overview charts use one canonical work per project; related works stay as separate publication rows.</li>
  <li><strong>Capabilities:</strong> manually reviewed tags describing intended functionality, not benchmark results.</li>
</ul>

<h2>Missingness and limitations</h2>
<p>A blank value is accompanied by a reason in the tidy metrics table and never means zero. Search coverage differs by host: GitHub indexes README text, while GitLab and Gitea search only names and descriptions, so a smaller non-GitHub result count reflects a narrower question rather than a smaller ecosystem. Star counts across different hosts measure differently sized audiences and should not be ranked against each other without that caveat. Registry downloads are influenced by release automation, CI, teaching, mirrors, and channel availability. Stars measure expressed repository interest, not installation or scientific correctness. Citation databases have coverage and matching limitations. Repository path checks show that files exist but cannot establish their quality. License classes are a reviewer's reading of the published terms, not legal advice.</p>

<h2>Reproduce</h2>
<p>Install with <code>uv sync</code>. Collect a fresh dated snapshot with <code>uv run python scripts/a000_run_all.py --snapshot-date YYYY-MM-DD --collect</code>, or rebuild from recorded source files with <code>--offline</code>. The snapshot manifest records checksums and retrieval context. Credentials are read only from <code>GITHUB_TOKEN</code> and <code>OPENALEX_API_KEY</code>; the non-GitHub hosts are read anonymously.</p>
"""


def main() -> None:
    args = snapshot_parser(__doc__).parse_args()
    snapshot_date = resolve_snapshot_date(args.snapshot_date, prefer_latest=True)
    render_page(
        "methodology.html",
        title="Methodology",
        heading="How this evidence was assembled",
        lede=(
            "Transparent boundaries matter more than pretending that an ecosystem "
            "search is complete. This page documents what counts, what does not, "
            "and how every metric should be interpreted."
        ),
        snapshot_date=snapshot_date,
        body=BODY,
    )


if __name__ == "__main__":
    main()
