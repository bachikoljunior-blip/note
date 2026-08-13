# Assistants Migration Checker — Product Hunt visual sources

These SVG files are the reconstructible source of the two 1270×760 Product Hunt gallery graphics. They preserve only claims verified in `handoff/PRODUCT_HUNT_ASSISTANTS_MIGRATION_DRAFT.md`.

The same directory also contains the upload-ready 240×240 PNG thumbnail and two 1270×760 PNG gallery images. Keep these versioned binaries private until the account holder authorizes a draft attachment or final launch.

## Render

```sh
npx --yes sharp-cli -i gallery-01.svg -o gallery-01.png
npx --yes sharp-cli -i gallery-02.svg -o gallery-02.png
```

Expected output dimensions: 1270×760 PNG.

## Validation checkpoint (2026-08-13)

- `gallery-01.svg`: SHA-256 `0e0fc1365c8184d9df678d05ac815cfa62842d0b9b50ec2895c3ceb8401bcbd0`
- rendered `gallery-01.png`: SHA-256 `98117f462baba9d63e8301331657fd612a29c09c94a5bc00bddcbe1a0a54aa50`
- `gallery-02.svg`: SHA-256 `fa1845470c0f5737f588034621fb72c232ac3378067f8f2ef892e46b58324229`
- rendered `gallery-02.png`: SHA-256 `be9d034cd90d977cd2be271102baf1e00687d62a9ced4406effb63b63a5316e9`
- Both rendered images were visually inspected after one clipping correction.
- `thumbnail-240.png`: SHA-256 `f8c331e283df736d0c61d0df4dc37ddc7b0e5fe331496194f3c9bdd9d623d6a5`
- The upload-ready PNG assets and their dimensions/hashes are fail-closed inputs to `scripts/check_product_hunt_preflight.py`.

## Truth constraints

Do not add customer, outcome, endorsement, ranking, sales, guaranteed-correctness, or official-OpenAI-affiliation claims. Do not submit, schedule, or publish merely because these sources render successfully.
