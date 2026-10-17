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
- No attribution trailers in commits or PRs.

## Proposals (agents write here, Arman decides)
<!-- Format: - [ ] Short title. Why it helps. Rough size (S/M/L). Links to inspiration if any. -->
<!-- Arman moves an item to "Decisions made" to approve it, or deletes it to reject. -->

## Log (newest first, agents append one line per iteration)
<!-- Format: YYYY-MM-DD. What was done. PR link or branch. Open question if any. -->
