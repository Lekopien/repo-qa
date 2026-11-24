import argparse

import uvicorn

from .indexer import index_repo


def main() -> None:
    p = argparse.ArgumentParser(prog="repoqa")
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("index", help="Index a GitHub repo")
    i.add_argument("url")
    sub.add_parser("serve", help="Start the web UI on :8000")
    args = p.parse_args()

    if args.cmd == "index":
        n = index_repo(args.url)
        print(f"Indexed {n} chunks into repoqa.db")
    else:
        uvicorn.run("repoqa.server:app", port=8000)


if __name__ == "__main__":
    main()
