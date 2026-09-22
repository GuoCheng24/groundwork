#!/usr/bin/env python3
"""proofground — one entry point over the gates.

    proofground gate    ...   should this direction be started at all
    proofground prereg  ...   is the pre-registration real, and older than the results
    proofground cluster ...   where is the idle capacity, and how to split across it

Each subcommand is a standalone script under tools/ and can be run directly.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "tools"))

COMMANDS = {"gate": "gate", "prereg": "prereg", "cluster": "cluster"}

USAGE = """usage: proofground {gate,prereg,cluster} ...

  gate     refuse a direction whose ceiling, baseline or controls already answer it
  prereg   scaffold, seal and verify a pre-registration - including that it was
           committed before the results it governs
  cluster  survey idle GPUs across nodes, pick the ones that fit, plan shards

`proofground <command> --help` for each."""


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(USAGE)
        return 0 if argv else 2
    cmd = argv.pop(0)
    if cmd not in COMMANDS:
        print(f"unknown command {cmd!r}\n\n{USAGE}", file=sys.stderr)
        return 2
    mod = __import__(COMMANDS[cmd])
    return mod.main(argv)


if __name__ == "__main__":
    sys.exit(main())
