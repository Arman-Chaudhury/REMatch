# REMatch (Property Watch)

Every year New York State publishes the assessment roll for every county: one
row per parcel with the owner's name, the address, and what the assessor thinks
the property is worth. For Nassau County that is about 444,000 rows. It is
public, but nobody reads it, so when the house next door quietly changes hands
or your own assessment jumps 15%, you find out months later, if at all.

REMatch watches that roll for you. Tell it an address, and when next year's
roll comes out it compares every parcel against the year before, works out what
changed (new owner, assessment up or down by more than 10%, parcel appeared or
disappeared), and emails the people watching that address. When an owner
changes, it also pulls the recorded sale from the Nassau County Land Records
Viewer so the email says what the place sold for.

I built it because I live in Nassau County and wanted to know these things
without checking a government website every few months.

## How it works

```
data.ny.gov (Socrata API)  ->  parcels table, one row per parcel per year
                           ->  diff this year against last year
                           ->  changes table (owner, assessment, new, gone)
                           ->  match changes to watched addresses
                           ->  fetch sale price from lrv.nassaucountyny.gov
                           ->  email the watcher
```

- `fetch.py` pages through the Socrata API 5,000 rows at a time with retries.
- `store.py` upserts into Postgres on `(swis_code, print_key_code, roll_year)`,
  so re-running a load is safe.
- `diff.py` self-joins the two years and `classify()` turns each pair into
  zero or more `Change` records. It is a pure function, so the tests run
  without a database.
- `address.py` normalizes spellings so `26 Crow Lane` matches `26 CROW LN`.
- `match.py` joins changes to watches at the same normalized address.
- `lrv.py` scrapes the Land Records Viewer for sale date, price, and condition.
- `notify.py` builds one email per watcher. It prints instead of sending unless
  you pass `--send`.

## Run it

Needs Python 3.11+ and a Postgres database in `DATABASE_URL` (a `.env` file works).

```bash
python -m venv venv && venv/bin/pip install -r requirements.txt
venv/bin/python -m property_watch.cli init                  # create tables
venv/bin/python -m property_watch.cli load 2024             # ~444k rows, a few minutes
venv/bin/python -m property_watch.cli load 2025
venv/bin/python -m property_watch.cli diff 2025             # 2024 vs 2025
venv/bin/python -m property_watch.cli watch add you@example.com "26 Crow Lane" Levittown
venv/bin/python -m property_watch.cli match
venv/bin/python -m property_watch.cli pending               # what would be sent
venv/bin/python -m property_watch.cli notify --send
```

`update` does the whole thing for the current year in one go (load, diff,
match, sales), which is what a monthly cron job runs. Until the new roll is
published it just says so and exits.

## Tests

```bash
venv/bin/python -m pytest
```

The tests cover address normalization, the change classifier (owner change,
assessment threshold, new and removed parcels), the sales page parser, and
email building. None of them need a database or the network.

## Data sources

- NYS Assessment Rolls: https://data.ny.gov/resource/7vem-aaz7.json
- Nassau County Land Records Viewer: https://lrv.nassaucountyny.gov
