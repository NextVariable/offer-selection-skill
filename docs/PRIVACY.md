# Privacy

This Skill has no telemetry, analytics service, author-operated backend, or
credential requirement. Its installers copy a fixed runtime allowlist and do
not install development audits, evaluations, archives, local caches, or Git
history.

The Skill does ask for sensitive decision context: academic background, exact
offers, scholarships, budget, experience, and career goals. That information is
processed by the Agent host the user chooses. Storage, retention, training, and
enterprise logging are controlled by that host and account, not by this
repository.

External research must use minimal public identifiers only: programme,
institution, employer, jurisdiction, role, and operative date. Names, student
IDs, emails, exact grades, offer-letter identifiers, private scholarship terms,
family finances, and other identifying intake must never be included in search
queries or sent to third-party tools.

Public bug reports, examples, and public evaluation cases must be synthetic or
anonymized. Do not attach offer letters, transcripts, résumés, screenshots
containing identifiers, or financial records. Real names, student IDs, e-mails,
exact grades, offer-letter identifiers, and family-finance figures must never
appear in GitHub issues, PRs, examples, or any public evaluation fixture.
Report security problems through the private channel in `SECURITY.md`.

## Development repository vs. public release

The full development repository is **not** the public release. It contains
internal behavioral evidence (`evals/`), audits (`internal/audits/`), historical
provenance (`internal/archive/`), machine-local absolute paths, a personal author e-mail,
and a private conversation-derived provenance document
(`internal/source-of-truth.md`). None of these belong in a public repository.

The public release is produced by `maintenance/build_release_snapshot.sh` as a clean
snapshot: it carries only the runtime skill, installers, developer docs, and
CI, and excludes every internal directory and machine-local file. The snapshot
is intended to be initialized as a **fresh Git repository** (new history) with
the author set to a **GitHub `noreply` e-mail**, so no personal e-mail or
development commit history is published. The development repository is never
pushed as-is.

### Privacy scan scope (dated, limited)

The snapshot builder performs a pattern scan for a **defined** set of
credential and identity shapes — private-key PEM headers, AWS access keys,
GitHub personal-access-token and OpenAI-style token prefixes, and the known
personal e-mail / local-path strings. This is a scope-limited pattern scan, not
a proof that no secret or personal datum exists anywhere in any form; it is a
dated, mechanical check of the snapshot only, and does not inspect the
development history.
