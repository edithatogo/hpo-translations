# Stage 0 Synthetic Operational Rehearsal

This directory contains the payload-free Phase 4 Stage 0 rehearsal. It uses
private-use language tag `x-stage0`, synthetic concept identifiers, synthetic
candidate text, and synthetic agent slots. It contains no empirical HPO term
text, translation, source payload, model and role identifier, or explicit maintainer decision.

Run `pixi run run-stage-0-rehearsal`. The command validates the plan and run
manifest, deterministically randomizes four candidate conditions, creates three
synthetic assignments per candidate, exercises agreement and adjudication,
tests all go/revise/stop branches, checks blinding and redaction, exports packets
to a temporary directory, and compares their hashes with `receipt.json`.

The blinding check is artifact-level: the agent-facing export contains no
candidate-method or provenance field. An empirical run must additionally use
role-separated distribution so agents cannot access the internal condition
mapping or generation workspace.

Passing this rehearsal establishes operational readiness only. It does not close
the agent-time budget, source, license, ethics, privacy, language-working-group,
community, prospective-freeze, or external-registration gates.
