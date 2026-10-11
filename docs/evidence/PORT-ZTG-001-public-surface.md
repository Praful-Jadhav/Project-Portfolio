# Evidence Packet — Public Portfolio Integrity Gate

Task ID: PORT-ZTG-001
Status: IN_PROGRESS
Accountable owner: Portfolio maintainer
Risk tier: R1

## Claim and risk
Add static integrity and source-controlled evidence checks to the public portfolio, which is a market-facing trust asset.

## Scope and acceptance criteria
In scope: public-claims contract, page integrity checker, tests, CI workflow and this packet. Out of scope: automated external URL scraping, factual certification of capability claims, and any changes to personal profile or client data.

## Verification plan and results
CI runs HTML structure/local-reference tests and the evidence packet gate against the exact candidate revision. Inspect the complete diff and record the exact commit and run status once available.

## Validation plan and results
A human must still open the rendered page and verify mobile/responsive presentation, accessible navigation, readability, content accuracy and that no capability is overstated. Static parsing is not user acceptance.

## Public safety and privacy
Only approved public professional information, public repository links and non-sensitive contact paths belong here. No private client records, secrets or invented testimonials are allowed.

## Limitations and open items
The gate does not validate external links or prove the truth of capability statements. Browser/render validation remains required after any material visual change.

## Recovery and rollback
Revert the checker/workflow change if valid page markup is rejected or real local-link/anchor errors are missed. Keep the last known-good public artifact available.

## Evidence and tested revision
Record the exact workflow run and tested SHA after CI completes. Status remains IN_PROGRESS until the diff, checks and rendered result are reviewed.
