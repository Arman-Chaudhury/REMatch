# Direction

This file steers every Claude session and subagent working on this repo. Read it before doing anything.
Agents may edit only the "Proposals" and "Log" sections. Arman owns the rest.

## Current goal
<!-- Arman: one or two sentences on what "better" means for this project right now. -->
Turn REMatch from a working script into something a Nassau County neighbor could sign up for and trust: reliable yearly diffs, accurate sale lookups, clear emails, and a simple way to add a watch. One reviewable change at a time. Baseline on 2026-10-16: 19 tests passing, no CI, ruff reports 12 lint errors and 11 unformatted files.

## Decisions made
<!-- Arman: settled choices. Agents never reopen these. -->
- Keep the current language and framework choices (Python, Postgres, Socrata API).
- No new paid services or API keys without approval.
- First task: add a GitHub Actions CI workflow that runs pytest and ruff, and fix the existing lint and formatting findings so it passes.
- Scrapers and email code must stay test-covered with recorded fixtures, never live calls in tests.

## Rules for agents
- Work on a branch in a worktree. Never commit to main. Never merge. Never force-push.
- Every change ships as a small draft PR with a plain-language description and passing tests.
- Debug first: if tests or CI fail, fixing that is the first task of the iteration.
- Only act on items in "Decisions made" or "Current goal". Anything else goes in "Proposals".
- Inspiration is welcome: look at comparable GitHub projects, products, papers, or ideas, and cite links in the proposal. Never copy code with an incompatible license.

## Proposals (agents write here, Arman decides)
<!-- Format: - [ ] Short title. Why it helps. Rough size (S/M/L). Links to inspiration if any. -->
<!-- Arman moves an item to "Decisions made" to approve it, or deletes it to reject. -->
- [ ] Split/merge heuristic before emitting "parcel removed". ORPTS tracks splits and merges only in the Assessor's Report Part 2 (shared split/merge number plus prior-roll SBL), which is not in the open dataset; so when a parcel key disappears, look for new keys in the same swis_code whose section.block prefix, address, deed book/page or owner match, and classify those as renumbered rather than removed. Size M. Links: https://www.tax.ny.gov/research/property/equal/assessrpt/g_instr2.htm, https://data.ny.gov/api/views/7vem-aaz7.json
- [ ] Track Socrata rowsUpdatedAt per roll year and re-diff when it changes. The dataset metadata shows the 2026 roll was published in January but rows updated again in April, so a year can change after first load; store a row count and hash per pull (git-scraping style) and refuse to classify "removed" when a year's count drops far below the prior pull. Size S. Links: https://data.ny.gov/api/views/7vem-aaz7.json, https://github.com/simonw/csv-diff, https://simonwillison.net/2021/Dec/7/git-history/
- [ ] Fix five confirmed diff/notify bugs found by review. (a) A new parcel with a null assessment crashes the whole diff run (`describe()` does `int("None")`), and since `save_changes` is one transaction nothing is committed. (b) Parcels that disappear from the roll are never detected: PAIR_SQL is a LEFT JOIN from the new year, and there is no "removed" kind, although the README advertises it. (c) `diff`/`update` do not check the prior year is loaded, so a first run would flag all ~444k parcels as new and email every watcher. (d) `pending` ignores `sent_at`, so it lists already-sent notifications forever. (e) Emails never include the scraped sale price; the `sales` table is never read. Each is a few lines plus a test. Size M total, could be split into S PRs. Open question: should "parcel removed" be its own change kind, and do you want (a) through (e) as one PR or five?
- [ ] Use NYS ORPTS SalesWeb (official RP-5217 transfer data, weekly updates, Excel export, no login) as the primary sale-price source, keeping the Land Records Viewer scraper as fallback for sales newer than its reporting lag. One bulk Nassau pull keyed on SWIS plus parcel ID replaces per-parcel scraping. Size M. Links: https://www.tax.ny.gov/research/property/assess/sales/salesweb.htm, https://tax.ny.gov/pit/property/munidataportal.htm
- [ ] Record Land Records Viewer and Socrata HTTP fixtures with pytest-recording (VCR.py, supports httpx) and run tests with --block-network so CI can never hit live sites; cassettes live in tests/cassettes. respx is hand-written mocks only, so it fits parser unit tests but not recorded fixtures. Size S. Links: https://github.com/kiwicom/pytest-recording, https://vcrpy.readthedocs.io/en/latest/installation.html
- [ ] Make a silent monthly failure visible: ping healthchecks.io (free tier, 20 checks) with start/success/fail from the `update` job, and add a sanity gate that refuses to diff or email when the new roll's row count deviates more than a few percent from last year or too many parcels vanish (a partial load would otherwise send thousands of false alerts). Size S. Links: https://healthchecks.io/docs/python/, https://data.ny.gov/Government-Finance/Property-Assessment-Data-from-Local-Assessment-Rol/7vem-aaz7
- [ ] Double opt-in watch signup with a POST-based confirm button (GET confirm links get eaten by corporate link scanners) and a per-watch unsubscribe token in every email; a tiny Flask/FastAPI form or a `watch confirm <token>` CLI, no paid service. Also link the free, name-based Nassau County Clerk Property Fraud Alert in every email so REMatch's yearly, parcel-based scope is honest next to the Clerk's near-real-time one. Size M. Links: https://flaviocopes.com/software/waiting-lists/, https://nassauclerk.com/?p=10522

## Log (newest first, agents append one line per iteration)
<!-- Format: YYYY-MM-DD. What was done. PR link or branch. Open question if any. -->
- 2026-10-17. Fixed the confirmed crash on a new parcel with a null assessment (bug 1a) with three tests; 22 tests pass. Branch fix-null-assessment-crash, draft PR. Smallest step toward reliable diffs since nothing new was in Decisions. Proposals now exceed five, so the loop stops until Arman triages.
- 2026-10-16. Added GitHub Actions CI (ruff check, ruff format --check, pytest) and fixed all 12 lint errors and 11 unformatted files; 19 tests pass. PR: ci-pytest-ruff, stacked on PR #1. Review found 5 confirmed bugs, listed in Proposals. Open question: are proposal items 1(a)-(e) one PR or five?
