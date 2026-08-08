# Gumroad listing draft

## Product name

Assistants API Sunset Migration Kit

## Price

$9 launch price

## Short description

Audit legacy Assistants API usage, preview conservative code changes, and migrate toward Responses + Conversations before the 2026-08-26 shutdown.

## Description

OpenAI lists 2026-08-26 as the Assistants API shutdown date. This compact offline kit helps you find legacy usage and separate safe mechanical edits from changes that still need engineering judgment.

You get a read-only scanner, a conservative dry-run codemod with unified diffs and `.bak` backups, an ordered migration checklist, and offline safety tests. The codemod intentionally does not claim that Runs, streaming, tool loops, stored IDs, Assistant configuration, or hosted tools can be migrated by blind search-and-replace.

No API key is required to scan or preview changes. Python 3.10+ is recommended. Review all changes and run your own application tests before deployment.

This is an independent developer utility and is not an official OpenAI product.

Official shutdown and migration references:
https://developers.openai.com/api/docs/deprecations
https://developers.openai.com/api/docs/assistants/migration
