# Gumroad Channel Research — 2026-08-07

## Decision

Prepare a standalone English-language download product for Gumroad, but do not claim it is published until the authenticated seller completes account, payout, tax, upload, and final publication steps.

This channel was selected because it has no monthly listing fee, supports one-time digital downloads, accepts files far larger than this product, and can expose an English edition to buyers outside the current Japanese note channel.

## Official information checked

1. **Fees**
   - Direct sales on Gumroad's website: 10% + USD 0.50 per transaction.
   - Card processing is listed separately at 2.9% + USD 0.30.
   - Gumroad Discover marketplace sales: 30%, including processing.
   - Source: https://gumroad.com/help/article/66-gumroads-fees.html

2. **File size**
   - Products priced above USD 0.99 can include a single file up to 20 GB.
   - Free products have a 250 MB limit.
   - Source: https://gumroad.com/help/article/289-file-size-limits-on-gumroad.html

3. **Product type and price**
   - Digital products can be sold as one-time purchases.
   - Published products can be priced from free up to USD 5,000.
   - Source: https://gumroad.com/help/article/149-adding-a-product

4. **Terms and seller obligations**
   - Gumroad acts as merchant of record for eligible digital products.
   - Sellers must have the rights to their products, provide accurate product documentation and license terms, and provide public-facing contact information and fulfillment timelines.
   - Digital files must be delivered through Gumroad for Gumroad transactions.
   - Source: https://gumroad.com/terms

5. **Prohibited products**
   - The current prohibited-products page was last revised July 6, 2026.
   - It prohibits certain external AI services, spam tools, unlawful products, and other restricted categories.
   - This prepared product is a downloadable template and research workflow delivered inside Gumroad, not external access to an AI service.
   - Source: https://gumroad.com/prohibited

## Pricing model

Prepared launch price: **USD 12**.

Estimated direct-sale deductions before tax, refunds, payout costs, PayPal differences, or currency conversion:

- Gumroad fee: 10% of USD 12 + USD 0.50 = USD 1.70
- Listed card-processing estimate: 2.9% of USD 12 + USD 0.30 = USD 0.648
- Total estimated deduction: USD 2.348
- Estimated remainder: **USD 9.652**

For a marketplace-discovery sale at 30%, the estimated remainder is USD 8.40 before other individual conditions.

These are estimates, not guaranteed payouts. The authenticated dashboard is the final source for actual deductions.

## Automation review

Automated:
- English product ZIP creation and integrity validation
- title, description, tags, price, license, disclaimer, and delivery wording
- official-source record
- direct-sale and marketplace estimate calculation
- mobile copy launcher
- CI checks for ZIP contents, product wording, placeholders, and fee formula

Cannot be automated with current permissions:
- seller registration and acceptance of Gumroad terms
- identity, tax, payout, and public contact settings
- selecting and uploading the ZIP from the authenticated account
- final publication
- post-publication checkout and delivery verification

No password, cookie, government ID, tax data, bank details, or payment credentials are stored in this repository.
