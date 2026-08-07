# Gumroad iPhone Safari manual handoff

Status: authenticated Safari product creation is in progress.

This is the fallback path after the official CLI device OAuth token exchange returned HTTP 429 and browser OAuth could not bridge an iPhone Safari session through a localhost callback. The ChatGPT cloud browser is not an authentication bridge and does not share Safari cookies.

## Secret handling

- Enter passwords and one-time codes only in Gumroad.
- Do not send passwords, one-time codes, cookies, callback URLs, access tokens, tax data, banking data, or identity documents in chat or GitHub.
- Final publication remains a user-only action.

## Current screen: Price required

The product name and `Digital product` selection are already complete. Do not re-enter the product name.

1. Enter `12` in the USD price field.
2. Tap the keyboard checkmark / Done control.
3. Scroll to the top and tap `Next: Customize`.
4. Send only a screenshot of the Customize screen, without passwords, codes, tax, payout, or identity information.

Repository checkpoint: `state/gumroad_manual_checkpoint.json`.

## Canonical prepared values

- Price: `US$12`
- Custom permalink: `non-repetitive-ai-trivia-shorts-kit`
- Summary: `100 topic prompts, 12 format-specific hooks, 25 visual patterns, 9 workflow prompts, and one worked 55-second example.`
- Description: `content/gumroad/description.md`
- Tags: `content/gumroad/tags.txt`
- Product ZIP: `dist/Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip`
- ZIP SHA-256: `3adb147dc55b671d99141281cc9849e3530a8865def543d341c326a54bcf0113`
- Cover: `dist/gumroad_visuals/gumroad_cover_main.png`
- Preview images:
  - `dist/gumroad_visuals/gumroad_cover_sample.png`
  - `dist/gumroad_visuals/gumroad_cover_workflow.png`
- Thumbnail: `dist/gumroad_visuals/gumroad_thumbnail.png`
- Refund period: 7 days
- Refund fine print: `content/gumroad/refund_fine_print.txt`

## Screen-by-screen control

At each screen, provide only a screenshot without secrets. The assistant should return the exact fields for that screen and verify them before moving forward. Do not select Publish until the final pre-publication check confirms name, price, digital file, visuals, refund terms, and public URL expectations.

## Completion signals

- Draft/configuration progress: a screenshot of the next Gumroad screen.
- Final publication: the public Gumroad product URL, without any account or payment details.
