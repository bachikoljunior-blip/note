# Gumroad iPhone Safari end-to-end handoff

Status: authenticated Safari product creation is in progress.

Use this runbook to finish the listing in one continuous Safari session. Do not wait for another chat reply between ordinary product-editing screens. The official CLI draft path remains available later, but the authenticated Safari session is the shortest current route after device OAuth token exchange returned HTTP 429.

## Secret handling

- Enter passwords, one-time codes, legal name, address, tax details, payout details, and identity documents only on Gumroad or its embedded verification provider.
- Do not send passwords, one-time codes, cookies, callback URLs, access tokens, tax data, banking data, or identity documents in chat or GitHub.
- Stop and send a screenshot only if the screen asks for an unexpected payment, changes the product type, or shows an error. Hide personal data first.
- Final publication remains a user-only action.

## Download once before continuing

Download [Gumroad_iPhone_Listing_Pack_v1.1.zip](../dist/Gumroad_iPhone_Listing_Pack_v1.1.zip?raw=1) from this private repository and expand only this outer ZIP once.

Inside it:

- upload the product file `Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip` without expanding it;
- use the four PNG files for the cover, previews, and thumbnail;
- copy the prepared title, summary, description, tags, and refund text from the included files or `START_HERE.html`.

Never upload the outer listing-pack ZIP as the customer product.

## Finish without waiting for another chat reply

Gumroad labels can move slightly on mobile. Match by the field purpose below; do not invent values for identity, payout, tax, or legal fields.

### 1. Current Price screen

The product name and `Digital product` selection are already complete. Do not re-enter the name.

1. Enter `12` in the USD price field.
2. Tap the keyboard checkmark / Done control.
3. Scroll to the top and tap `Next: Customize`.

### 2. Product / Customize screen

Use these exact prepared values:

- Name: `Non-Repetitive AI Trivia Shorts Kit: 100 Topic Prompts + 12 Formats`
- Price: `US$12`
- Custom URL suffix: `non-repetitive-ai-trivia-shorts-kit`
- Summary: `100 topic prompts, 12 format-specific hooks, 25 visual patterns, 9 workflow prompts, and one worked 55-second example.`
- Description: copy all of `description.md`
- Cover: `gumroad_cover_main.png`
- Preview images, if the screen permits more images:
  - `gumroad_cover_sample.png`
  - `gumroad_cover_workflow.png`
- Thumbnail: `gumroad_thumbnail.png`

Save changes if Gumroad shows a Save button. Do not use claims such as guaranteed views, guaranteed revenue, or guaranteed monetization.

### 3. Content screen

1. Open the product's `Content` tab.
2. Add exactly one customer download: `Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip`.
3. Do not expand this ZIP and do not upload `Gumroad_iPhone_Listing_Pack_v1.1.zip`.
4. Wait until the upload finishes and the filename is visible.
5. Save changes.

### 4. Product settings and refund policy

Where Gumroad shows product settings:

- select a 7-day refund period;
- paste all of `refund_fine_print.txt` into the optional fine-print field;
- leave recurring membership, pay-what-you-want, license keys, variants, and physical shipping off;
- do not enable an upsell or third-party integration for this first launch.

### 5. Share screen

1. Open the `Share` tab.
2. Confirm the custom URL suffix is `non-repetitive-ai-trivia-shorts-kit`.
3. Add the prepared tags from `tags.txt`.
4. Choose the most specific truthful creator-tools / video / education category Gumroad offers; do not choose an unrelated category just for reach.
5. Keep ratings enabled if offered.
6. Copy the product URL when Gumroad makes it available.

Discover eligibility is not required for the first direct sale. Gumroad's current help says Discover additionally depends on payout settings, genuine sales, account review, a category, ratings, and at least one successful sale. Do not delay direct publication merely to wait for Discover eligibility.

### 6. Pre-publication check

Before pressing Publish, confirm all seven:

1. The name exactly matches the prepared title.
2. The price is US$12.
3. The product type is digital and not a membership.
4. The customer download is the inner product ZIP, not the outer listing pack.
5. The main cover and thumbnail are present.
6. The description, 7-day refund policy, and fine print are present.
7. The custom URL suffix is correct.

If all seven pass, press `Publish`. This is the final user-controlled publication action.

### 7. Verify delivery without paying yourself

While still logged in:

1. Open the published product page.
2. Use Gumroad's `Test purchase` flow; do not buy your own product with a real card.
3. Confirm the checkout marks the payment method as a test card.
4. Complete the test purchase.
5. Confirm the inner ZIP can be downloaded and opens to the expected English kit files.
6. Return to the product dashboard or `Share` tab and tap `Copy URL`.

Send only the public Gumroad product URL as the completion signal. Do not send account, payment, payout, tax, or identity details.

## If Gumroad interrupts with seller or payout verification

Complete only your own truthful details inside Gumroad. For an individual account, use the legal identity and physical address Gumroad requests. Upload identity documents only to the verification page, never to chat or GitHub. If a choice would create a contract, charge, subscription, or materially change payout handling and is unclear, stop before confirming and send a redacted screenshot.

## Canonical prepared values

- Price: `US$12`
- Custom permalink: `non-repetitive-ai-trivia-shorts-kit`
- Summary: `100 topic prompts, 12 format-specific hooks, 25 visual patterns, 9 workflow prompts, and one worked 55-second example.`
- Description: `content/gumroad/description.md`
- Tags: `content/gumroad/tags.txt`
- Product ZIP: `dist/Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip`
- ZIP SHA-256: `3adb147dc55b671d99141281cc9849e3530a8865def543d341c326a54bcf0113`
- Outer iPhone pack: `dist/Gumroad_iPhone_Listing_Pack_v1.1.zip`
- Outer pack SHA-256: `c61595a1d167209dd357930242a3cdf0d439a872b5bad8246b05c2ae10d137ec`
- Cover: `dist/gumroad_visuals/gumroad_cover_main.png`
- Preview images:
  - `dist/gumroad_visuals/gumroad_cover_sample.png`
  - `dist/gumroad_visuals/gumroad_cover_workflow.png`
- Thumbnail: `dist/gumroad_visuals/gumroad_thumbnail.png`
- Refund period: 7 days
- Refund fine print: `content/gumroad/refund_fine_print.txt`

## Official references checked on 2026-08-07

- Adding and publishing a product: https://gumroad.com/help/article/149-adding-a-product
- Product URL: https://gumroad.com/help/article/136-find-your-products-url
- Refund policy: https://gumroad.com/help/article/335-custom-refund-policy
- Test purchase: https://gumroad.com/help/article/62-testing-a-purchase
- Discover category and tags: https://gumroad.com/help/article/79-gumroad-discover
- Payout and identity settings: https://gumroad.com/help/article/260-your-payout-settings-page
