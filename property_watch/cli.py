import sys

from property_watch.db import init_schema


def main(argv: list[str]) -> None:
    command = argv[0] if argv else "help"
    if command == "init":
        init_schema()
        print("schema ready")
    else:
        print("commands: init")



if __name__=="__main__" :
    main(sys.argv[1:])