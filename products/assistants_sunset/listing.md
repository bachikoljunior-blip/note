# Gumroad listing draft

## Product name

Assistants API Sunset Migration Kit

## Price

Solo $29 / Team $149 / Organization $399

## Short description

Audit legacy Assistants API usage, preview conservative code changes, and migrate toward Responses + Conversations before the 2026-08-26 shutdown.

## Description

OpenAI lists 2026-08-26 as the Assistants API shutdown date. This compact offline kit helps you find legacy usage and separate safe mechanical edits from changes that still need engineering judgment.

You get a read-only scanner, a conservative dry-run codemod with unified diffs and `.bak` backups, an ordered migration checklist, and offline safety tests. The codemod intentionally does not claim that Runs, streaming, tool loops, stored IDs, Assistant configuration, or hosted tools can be migrated by blind search-and-replace.

No API key is required to scan or preview changes. Python 3.10+ is recommended. Review all changes and run your own application tests before deployment.

This is an independent developer utility and is not an official OpenAI product.

Choose the license that matches your internal use. Every version contains the same self-service download and no consulting or ongoing support:

- Solo: one purchaser, one internal repository.
- Team: one organization, up to 10 internal repositories.
- Organization: one legal organization, unlimited internal repositories.

Redistribution, resale, sublicensing, client delivery of the source kit, and use as a competing downloadable product are not included in any version.

Official shutdown and migration references:
https://developers.openai.com/api/docs/deprecations
https://developers.openai.com/api/docs/assistants/migration
