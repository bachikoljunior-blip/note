# Assistants API Sunset Migration Kit — iPhone Gumroad handoff

This handoff reduces the separate US$9 product completion to one private artifact download and one authenticated Gumroad session. Final publication, identity, tax, payout, banking, and contract decisions remain user-only.

## Download once

In the private `note` repository, open the latest successful **Validate and analyze** run for the relevant pull request and download its `note-validated-outputs-*` artifact. Expand that Actions artifact once, then select:

`dist/Assistants_API_Sunset_Gumroad_iPhone_Pack_v1.zip`

Expand only this outer iPhone pack once and open `START_HERE.html` in Safari. Keep `Assistants_API_Sunset_Migration_Kit_v1.zip` compressed; it is the buyer download.

The artifact expires after the configured seven-day retention period. If it has expired, rerun the repository validation workflow to regenerate the same deterministic pack instead of copying a paid ZIP into git.

## One authenticated Gumroad session

1. Create a separate digital product named `Assistants API Sunset Migration Kit`.
2. Set the launch price to `US$9` and the custom permalink to `assistants-api-sunset-migration-kit`.
3. Copy the summary, description, tags, and refund fine print from the pack.
4. Upload only `Assistants_API_Sunset_Migration_Kit_v1.zip` as buyer content and wait for the filename to appear.
5. Add the provided cover. If Gumroad does not accept SVG, open it in Safari, take a screenshot, and crop it square without changing the claims.
6. Save, then use Gumroad's creator `Test purchase`; do not buy the product with a real card.
7. Confirm the buyer can download and open the inner ZIP, then make the final publication decision.

Send back only the public product URL after completion. Never send passwords, one-time codes, cookies, access tokens, legal identity, tax, payout, or banking information to chat or GitHub.
