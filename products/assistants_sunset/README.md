# Assistants API Sunset Migration Kit

OpenAI's Assistants API is scheduled to shut down on **2026-08-26**. Its recommended replacements are the Responses API and Conversations API.

This kit helps you inventory legacy usage, preview the small subset that can be rewritten safely, and work through the remaining migration decisions without pretending that endpoint renames are a complete migration.

## Included

- `scan.py`: read-only inventory across Python, JavaScript, TypeScript and common source formats
- `codemod.py`: dry-run unified diff; only empty `threads.create()` calls are rewritten automatically
- `MIGRATION.md`: ordered checklist based on the official migration guide
- `test_scan.py`: offline scanner and codemod safety tests

## Quick start

```bash
python scan.py /path/to/your/project --json
python codemod.py /path/to/your/project
python codemod.py /path/to/your/project --apply
python test_scan.py
```

`codemod.py` is a dry run unless `--apply` is supplied. Apply mode writes a `.bak` file beside every changed source file.

## Important limits

This kit does not create dashboard prompts, migrate remote stored objects, run an application test suite, or guarantee a production-ready migration. Runs, streaming, polling, tool loops, stored IDs, file search, code interpreter, and assistant configuration require human decisions. Review every diff and run your own tests.

Official sources:

- https://developers.openai.com/api/docs/deprecations
- https://developers.openai.com/api/docs/assistants/migration
