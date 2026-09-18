# Security Policy

## Supported versions

| Version | Status |
|---|---|
| v0.3.2 (release candidate) | Supported — pre-release, under review |
| v0.3.1 | Supported (latest released) |
| v0.3.0 | Supported |
| v0.2.x and earlier | End of support |

The current release line is declared in `.claude-plugin/plugin.json`
(`version`) and mirrored in `skills/offer-selection-skill/SKILL.md` frontmatter. Only the listed versions
receive security fixes.

## Reporting a vulnerability

**Do not open a public issue for a vulnerability.** Use GitHub's private
vulnerability reporting: the repository's **Security** tab →
**Report a vulnerability** (Security Advisories / private vulnerability
reporting). If the project is not yet on GitHub, contact the maintainer
directly through the private channel they publish — never a public issue.

Reports should include:

- the file and line involved (repo-relative path);
- what an attacker or a user could do with it;
- a minimal reproducer if one exists;
- whether any real student data may be affected.

Do **not** post real names, grades, offer letters, student IDs, email
addresses, financial information, or other private material anywhere public —
including in security reports unless the private channel requires them for
reproduction (in which case redact everything that is not strictly needed).

## What this project handles (and what it must not)

The skill, at runtime, researches **public web pages** (tuition, ranking,
visa/credential rules, employer policy, programme details). It also asks a
user for **private intake**: undergraduate background, exact offers,
scholarship terms, budget, experience, and goals.

- Public research output is fine in this repository.
- **Private user intake must never be committed** to this repository, to
  examples, to issues, or to PRs. Examples are synthetic and anonymized by
  design. If a real run produced something sensitive, keep it out of the repo
  and report it through the private channel so it can be cleaned up.
- The project's own provenance records may reference conversation IDs and
  maintainer details; anything that could identify a third-party student is
  out of scope for the repository.

## Scope

This repository contains rules, documentation, and evaluation tooling. It does
not store user data, credentials, or secrets. If you find a real secret
(API key, token, private key, credential) in the tree, treat it as a
vulnerability: report it privately, do not print it in an issue, and do not
include it in any diff.
