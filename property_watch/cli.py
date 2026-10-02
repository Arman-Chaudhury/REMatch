import sys
from property_watch.store import store_rows
from property_watch.fetch import fetch_all
from property_watch.db import init_schema



def main(argv: list[str]) -> None:
    command = argv[0] if argv else "help"
    if command == "init":
        init_schema()
        print("schema ready")
    elif command == "load":
            print("stored", load_year(int(argv[1])))
    elif command == "diff":
        from property_watch.diff import find_changes
        from property_watch.changes import save_changes
        year = int(argv[1])
        changes = find_changes(year - 1, year)
        print("changes found:", len(changes))
        print("new records:", save_changes(changes, year))
    elif command == "update":
        from datetime import date
        from property_watch.diff import find_changes
        from property_watch.changes import save_changes
        year = date.today().year
        stored = load_year(year)
        if stored == 0:
            print(f"{year} roll not published yet")
        else:
            changes = find_changes(year - 1, year)
            print(f"{year}: {len(changes)} changes, {save_changes(changes, year)} new records")
    elif command == "watch" and argv[1:2] == ["add"]:
        from property_watch.match import add_watch
        email, address = argv[2], argv[3]
        town = argv[4] if len(argv) > 4 else None
        print("watch id:", add_watch(email, address, town))
    elif command == "match":
        from property_watch.match import run_matching
        print("new notifications:", run_matching())
    elif command == "pending":
        from property_watch.match import pending
        for n in pending():
            print(f"[{n['impact']}] {n['email']}: {n['title']}")
    elif command == "sales":
        from property_watch.lrv import fetch_sales, save_sales, watched_sold_parcels
        keys = argv[1:] or watched_sold_parcels()
        if not keys:
            print("no watched parcels have changed owner; run match first")
        for key, sales in fetch_sales(keys):
            print(f"{key}: {len(sales)} sales, {save_sales(key, sales)} new")
            for s in sales:
                price = f"${s['price']:,}" if s["price"] else "n/a"
                print(f"  {s['sale_date']}  {price}  {s['condition'] or ''}")
    else:
        print('commands: init, load YEAR, diff YEAR, update, '
              'watch add EMAIL "ADDRESS" [TOWN], match, pending, sales [PRINT_KEY ...]')

def load_year(roll_year: int, batch: int = 5000) -> int:
    total, buffer = 0, []
    for row in fetch_all(roll_year, page_size= batch):
        buffer.append(row)
        if len(buffer) >= batch:
            total += store_rows(buffer)
            buffer = []
            print(f"  {roll_year}: {total} rows stored", flush=True)
    if buffer:
        total += store_rows(buffer)
    return total
    
if __name__=="__main__" :
    main(sys.argv[1:])