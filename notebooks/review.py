import marimo

__generated_with = "0.24.0"
app = marimo.App(width="full", app_title="DAS catalogue review")


@app.cell
def _():
    import json

    import marimo as mo

    from oss_das.core import PATHS, load_projects, load_rejections, read_csv
    from oss_das.review import (
        REJECT_REASONS,
        accept,
        append_human_verdict,
        curated_body,
        curated_record,
        load_candidate,
        load_proposals,
        not_das_sample,
        pending,
        reject,
        vocabulary,
    )

    return (
        PATHS,
        REJECT_REASONS,
        accept,
        append_human_verdict,
        curated_body,
        curated_record,
        json,
        load_candidate,
        load_projects,
        load_proposals,
        load_rejections,
        mo,
        not_das_sample,
        pending,
        read_csv,
        reject,
        vocabulary,
    )


@app.cell
def _(mo):
    # A write to data/ bumps the tick so the pending list is re-read from disk;
    # the log keeps what each button did, since the button itself is rebuilt.
    get_tick, set_tick = mo.state(0)
    get_log, set_log = mo.state([])
    return get_log, get_tick, set_log, set_tick


@app.cell
def _(get_tick, load_projects, load_proposals, load_rejections, pending, vocabulary):
    get_tick()
    projects = load_projects()
    proposals = pending(load_proposals(), projects, load_rejections())
    capability_vocab = vocabulary(projects, "capabilities")
    category_vocab = vocabulary(projects, "primary_category")
    return capability_vocab, category_vocab, proposals


@app.cell
def _(mo, proposals):
    labels = {
        f"[{p.status}] {p.id} — {p.proposed.get('name', '')}": p.id for p in proposals
    }
    chooser = mo.ui.dropdown(
        options=labels,
        value=next(iter(labels), None),
        label=f"Pending proposals ({len(proposals)})",
        searchable=True,
        full_width=True,
    )
    mo.vstack([mo.md("# DAS catalogue review"), chooser])
    return (chooser,)


@app.cell
def _(chooser, proposals):
    selected = next((p for p in proposals if p.id == chooser.value), None)
    return (selected,)


@app.cell
def _(capability_vocab, category_vocab, json, mo, selected):
    def _options(vocab, current):
        current = current if isinstance(current, list) else [current]
        return sorted(set(vocab) | {c for c in current if c})

    form = None
    if selected is not None:
        p = selected.proposed
        form = mo.ui.dictionary(
            {
                "id": mo.ui.text(value=p.get("id", ""), label="id"),
                "name": mo.ui.text(value=p.get("name", ""), label="name"),
                "repository_url": mo.ui.text(
                    value=p.get("repository_url") or "",
                    label="repository_url",
                    full_width=True,
                ),
                "homepage": mo.ui.text(
                    value=p.get("homepage") or "", label="homepage", full_width=True
                ),
                "description": mo.ui.text(
                    value=p.get("description", ""), label="description", full_width=True
                ),
                "status": mo.ui.dropdown(
                    ["included", "watchlist", "excluded"],
                    value=p.get("status"),
                    label="status",
                ),
                "decision_reason": mo.ui.text(
                    value=p.get("decision_reason", ""),
                    label="decision_reason",
                    full_width=True,
                ),
                "primary_category": mo.ui.dropdown(
                    _options(category_vocab, p.get("primary_category")),
                    value=p.get("primary_category"),
                    label="primary_category",
                ),
                "capabilities": mo.ui.multiselect(
                    _options(capability_vocab, p.get("capabilities", [])),
                    value=p.get("capabilities", []),
                    label="capabilities",
                ),
                "das_focus": mo.ui.dropdown(
                    ["das-native", "other-fiber", "das-supporting", "not-das"],
                    value=p.get("das_focus", "das-native"),
                    label="das_focus",
                ),
                "license_spdx": mo.ui.text(
                    value=p.get("license_spdx") or "", label="license_spdx"
                ),
                "license_class": mo.ui.dropdown(
                    ["osi-approved", "source-available", "unlicensed", "unknown"],
                    value=p.get("license_class", "unknown"),
                    label="license_class",
                ),
                "registries": mo.ui.text_area(
                    value=json.dumps(p.get("registries", {}), indent=1),
                    label="registries (JSON)",
                    rows=4,
                ),
                "publications": mo.ui.text_area(
                    value=json.dumps(p.get("publications", []), indent=1),
                    label="publications (JSON)",
                    rows=4,
                ),
                "notes": mo.ui.text_area(
                    value="", label="reviewer notes (body)", rows=3
                ),
            }
        )
    return (form,)


@app.cell
def _(form, json, load_candidate, mo, selected):
    def _evidence(key):
        loaded = load_candidate(key)
        if loaded is None:
            return mo.md(f"`{key}`: no candidate file")
        front, body = loaded
        meta = {k: v for k, v in front.items() if k not in {"probes", "found_by"}}
        parts = [
            mo.md(
                "```json\n" + json.dumps(meta, indent=1, ensure_ascii=False) + "\n```"
            )
        ]
        if body:
            parts.append(mo.md(body))
        return mo.vstack(parts)

    if selected is None:
        _view = mo.md(
            "Nothing pending: every enriched proposal has a curated counterpart."
        )
    else:
        _view = mo.vstack(
            [
                mo.md(
                    f"## {selected.id}  \nsources: {', '.join(f'`{k}`' for k in selected.sources)}"
                ),
                mo.hstack(
                    [
                        mo.vstack([mo.md("### Proposal"), form]),
                        mo.vstack(
                            [
                                mo.md("### Agent summary"),
                                mo.md(selected.body),
                                mo.md("### Provenance"),
                                mo.md(
                                    "```json\n"
                                    + json.dumps(selected.provenance, indent=1)
                                    + "\n```"
                                ),
                            ]
                        ),
                    ],
                    widths=[1, 1],
                    align="start",
                ),
                mo.md("### Candidate evidence"),
                mo.accordion({key: _evidence(key) for key in selected.sources}),
            ]
        )
    mo.output.append(_view)
    return


@app.cell
def _(REJECT_REASONS, mo):
    reject_reason = mo.ui.dropdown(
        list(REJECT_REASONS), value=REJECT_REASONS[0], label="reject reason"
    )
    reject_note = mo.ui.text(value="", label="reject note", full_width=True)
    return reject_note, reject_reason


@app.cell
def _(
    accept,
    curated_body,
    curated_record,
    form,
    json,
    mo,
    reject,
    reject_note,
    reject_reason,
    selected,
    set_log,
    set_tick,
):
    def _fields():
        values = dict(form.value)
        notes = values.pop("notes", "")
        for key in ("registries", "publications"):
            values[key] = json.loads(values[key]) if values[key].strip() else None
        for key in ("repository_url", "homepage", "license_spdx"):
            values[key] = values[key].strip() or None
        # The proposal's forge kind travels along so a self-hosted GitLab keeps
        # its dialect; the host itself is re-derived from the edited URL.
        values["forge"] = selected.proposed.get("forge")
        if values["registries"] is None:
            values.pop("registries")
        values["publications"] = values["publications"] or []
        return values, notes

    def _accept(_):
        try:
            values, notes = _fields()
            record = curated_record(
                values, sources=selected.sources, provenance=selected.provenance
            )
            target = accept(record, curated_body(selected.summary, notes))
            message = f"accepted {record.id} -> {target}"
        except Exception as error:
            failure = f"ACCEPT FAILED: {error}"
            set_log(lambda log: [*log, failure])
            return
        set_log(lambda log: [*log, message])
        set_tick(lambda tick: tick + 1)

    def _reject(_):
        entries = reject(selected.sources, reject_reason.value, reject_note.value)
        set_log(
            lambda log: [*log, f"rejected {', '.join(entries)} ({reject_reason.value})"]
        )
        set_tick(lambda tick: tick + 1)

    accept_button = mo.ui.button(
        label="Accept", kind="success", on_click=_accept, disabled=selected is None
    )
    reject_button = mo.ui.button(
        label="Reject", kind="danger", on_click=_reject, disabled=selected is None
    )
    mo.hstack(
        [accept_button, reject_button, reject_reason, reject_note],
        justify="start",
        align="end",
    )
    return


@app.cell
def _(get_log, mo):
    mo.md("\n".join(f"- {line}" for line in get_log()[-10:]) or "_no actions yet_")
    return


@app.cell
def _(mo):
    resample = mo.ui.button(label="Resample", value=0, on_click=lambda v: v + 1)
    mo.vstack([mo.md("## Spot-check: random `not-das` verdicts"), resample])
    return (resample,)


@app.cell
def _(PATHS, load_candidate, mo, not_das_sample, read_csv, resample):
    sample_rows = []
    for row in not_das_sample(read_csv(PATHS.triage), size=20, seed=resample.value):
        loaded = load_candidate(row["key"])
        front = loaded[0] if loaded else {}
        sample_rows.append(
            {
                "key": row["key"],
                "name": front.get("name", ""),
                "description": (front.get("description") or "")[:160],
                "rule": row.get("rule", ""),
                "reason": row.get("reason", ""),
            }
        )
    mo.ui.table(sample_rows, selection=None)
    return (sample_rows,)


@app.cell
def _(append_human_verdict, mo, sample_rows, set_log):
    override_key = mo.ui.dropdown(
        [row["key"] for row in sample_rows], label="key to mark as das"
    )
    override_reason = mo.ui.text(value="", label="reason", full_width=True)

    def _override(_):
        if not override_key.value:
            return
        append_human_verdict(override_key.value, override_reason.value)
        set_log(
            lambda log: [*log, f"triage override: {override_key.value} -> das (human)"]
        )

    override_button = mo.ui.button(
        label="Append human verdict: das", kind="warn", on_click=_override
    )
    mo.hstack(
        [override_key, override_reason, override_button], justify="start", align="end"
    )
    return


if __name__ == "__main__":
    app.run()
