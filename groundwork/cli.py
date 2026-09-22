#!/usr/bin/env python3
"""groundwork — one entry point over the gates.

    groundwork gate    ...   should this direction be started at all
    groundwork prereg  ...   is the pre-registration real, and older than the results
    groundwork cluster ...   where is the idle capacity, and how to split across it

Each subcommand is a standalone script under tools/ and can be run directly.
"""
import importlib
import sys

COMMANDS = {"gate": "gate", "prereg": "prereg", "cluster": "cluster", "reach": "reach",
            "lit": "lit", "ledger": "ledger"}

USAGE = """usage: groundwork {gate,prereg,cluster,reach,lit,ledger} ...

  gate     refuse a direction whose ceiling, baseline or controls already answer it
  prereg   scaffold, seal and verify a pre-registration - including that it was
           committed before the results it governs
  cluster  survey idle GPUs across nodes, pick the ones that fit, plan shards
  reach    classify what this machine can actually fetch, and through which door
  lit      literature grounding and occupancy search that can be checked
  ledger   record what died and what got through, and roll it up

`groundwork <command> --help` for each."""


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(USAGE)
        return 0 if argv else 2
    cmd = argv.pop(0)
    if cmd not in COMMANDS:
        print(f"unknown command {cmd!r}\n\n{USAGE}", file=sys.stderr)
        return 2
    mod = importlib.import_module("." + COMMANDS[cmd], __package__)
    return mod.main(argv)


if __name__ == "__main__":      # pragma: no cover
    sys.exit(main())
