# Getting started — from nothing to an agent doing your research

Written for somebody who has never used a coding agent, and specifically for the
case that defeats most tutorials: **a shared cluster node with no direct route
to the internet.** Every trap below cost somebody a day.

If your machine has ordinary internet access, do Part 1 and skip Part 2.

---

## Part 0 — What you actually need

1. **A laptop** with a normal internet connection.
2. **An account** for at least one agent. The two mature command-line agents are
   Anthropic's **Claude Code** and OpenAI's **Codex CLI**. Either works with
   everything here; having both is genuinely better, because the most useful
   review is from a model that did not write the thing.
3. **SSH access** to wherever your data and GPUs are.
4. A terminal. Not an IDE, to start with — the IDE integration adds a failure
   mode you do not need on day one (Part 2.6 explains why).

You do **not** need root anywhere. Nothing in this guide installs anything
system-wide.

---

## Part 1 — A machine with normal internet

```bash
# Claude Code
npm install -g @anthropic-ai/claude-code
claude          # first run walks you through signing in

# Codex CLI
npm install -g @openai/codex
codex           # same
```

No npm? Both ship standalone installers; check their documentation rather than
installing a system-wide Node.

Then, in any project directory:

```bash
cd ~/my-project
claude
```

Type what you want in plain language. The agent reads your files, proposes
changes, and asks before running anything that matters. **Start by asking it to
explain code you already understand** — it is the fastest way to calibrate how
much to trust it.

---

## Part 2 — A cluster node with no direct internet

This is the situation on most academic HPC systems: the login node may reach the
internet, the compute nodes do not, and you cannot change that.

### 2.1 The shape of the fix

Your laptop has internet. Your compute node has your data. **Carry the
connection from the laptop to the node** with a reverse tunnel, opened by the
same SSH command you already use:

```bash
# on your LAPTOP, in ~/.ssh/config
Host mycluster
    HostName <the address you already use>
    User <your username>
    RemoteForward 18080 127.0.0.1:1080      # <-- the line that matters
    ExitOnForwardFailure yes
    ServerAliveInterval 20
    ServerAliveCountMax 3
    TCPKeepAlive yes
```

`RemoteForward 18080 127.0.0.1:1080` means: *anything the cluster sends to its
own port 18080 comes out of my laptop's port 1080.* Point the second number at
whatever gives your laptop internet — a local proxy client, or `127.0.0.1:1080`,
or whatever you already use. Pick any free port for the first number; it is
yours alone.

The three `Alive`/`ExitOnForward` lines are not optional. Without them the
tunnel dies silently on the first network hiccup and everything above it fails
with errors that look like something else entirely.

### 2.2 Tell the node to use it

On the **cluster**, in `~/.bashrc`:

```bash
# only set the proxy if the tunnel is actually up
if timeout 1 bash -c ': < /dev/tcp/127.0.0.1/18080' 2>/dev/null; then
    export http_proxy=http://127.0.0.1:18080
    export https_proxy=$http_proxy
    export no_proxy=localhost,127.0.0.1
else
    echo "tunnel down — reconnect your ssh session before downloading anything"
fi
```

### 2.3 The trap that costs everybody a day

> **`no_proxy` is why `git clone` hangs.**

Many site-wide profiles put `github.com` into `no_proxy`, reasoning that an
internal mirror serves it. On a node with no direct route, that means git
bypasses the only working path and hangs on a socket that will never open. The
error says "connection timed out", which sounds like the proxy is broken. It is
not; the proxy was never used.

```bash
# force it, per command, when something that "should work" hangs
no_proxy="" NO_PROXY="" git clone <url>
no_proxy="" NO_PROXY="" gh api repos/<owner>/<repo>
```

Check your own with `echo $no_proxy` before believing any diagnosis.

### 2.4 Two protocols on one port, and when to use which

A mixed-mode proxy usually speaks **both** HTTP and SOCKS on the same port:

```bash
curl -x http://127.0.0.1:18080       -L https://example.org      # usually fine
curl -x socks5h://127.0.0.1:18080    -L https://example.org      # the fallback
```

Use `socks5h` when a hostname **fails to resolve**. The `h` means the *remote*
end does the DNS lookup, which fixes the common case where the compute node's
resolver knows nothing about the outside world. Several hosts that appear
completely unreachable are simply unresolvable locally.

```bash
# python, needs PySocks
proxies = {"http": "socks5h://127.0.0.1:18080", "https": "socks5h://127.0.0.1:18080"}
# git, bypassing a no_proxy exclusion as well
no_proxy="" git -c http.proxy=socks5h://127.0.0.1:18080 clone <url>
```

Tools that only understand HTTP proxies — several downloaders among them — must
use the `http://` form, and then the target host must not be in `no_proxy`.

### 2.5 Verify before you trust it

```bash
python -m groundwork reach --targets github.com api.openai.com api.anthropic.com \
                                      pypi.org api.openalex.org arxiv.org
```

Read the tiers, and read `CHALLENGE` especially: the request succeeded and the
body is a bot wall. Anything that checks only a status code will treat it as
content. A site that answers `CHALLENGE` is a site an automated step must not
consume.

### 2.6 Use the CLI, not the IDE panel, over a tunnel

The graphical panels of these agents generally hold a **long-lived WebSocket**;
the command-line tools use ordinary HTTP requests. A reverse tunnel across a
home connection interrupts a long-lived socket far more often than it
interrupts a request, and the panel has a low internal retry limit you cannot
raise.

Symptom: *"stream disconnected before completion"*, repeatedly, in the panel,
while the CLI in a terminal on the same machine works fine.

This is not fixable from the cluster side. **Use the CLI.** If retries are
configurable for the CLI, raise them — a longer idle timeout and more stream
retries turn a bad evening into a slow one.

### 2.7 Never run a second bridge on your private port

If a helper script ever binds your reverse-forward port with something that is
*not* your tunnel, the port looks open to every naive check and nothing works.
Diagnosing this is miserable because every test reports "port is listening".

Two rules:

- **a port-open check is not a proxy-works check.** Test with an actual request;
- keep the reverse-forward port for the reverse forward, exclusively. If it is
  down, reconnect the SSH session. Do not start something else on it.

And do not silently fall back to a colleague's shared bridge. If your tunnel is
down, fail loudly.

---

## Part 3 — Your first session

```bash
cd ~/my-project
claude            # or: codex
```

Four things worth knowing on day one:

- **It reads before it writes.** Ask "what does this repository do?" first.
- **It asks before running.** Read the command it proposes. You will catch
  mistakes, and you will learn what it is thinking.
- **It remembers within a session.** Long conversations are fine; the context is
  managed for you.
- **Interrupting is normal.** If it goes the wrong way, say so. You do not need
  to start over.

A good first task: *"read this script and tell me what would break if the input
file were empty."*

---

## Part 4 — Using it for a whole project

This is the part most guides skip. The agent is strongest when it is pointed at
one stage at a time.

| stage | ask for | the tool |
|---|---|---|
| deciding what to work on | the ceiling, the tuned baseline, a random arm, a positive control | [`groundwork gate`](../groundwork/groundwork/skills/00-gate/) |
| the literature | who already occupies this claim, and can you tell | [`groundwork lit`](../groundwork/skills/10-direction/) |
| the experiment | a sealed pre-registration, then a launch across idle GPUs | [`groundwork prereg`](../groundwork/skills/20-experiment/), `cluster` |
| the claims | three layers that are blind to different defects | [`doubleblind`](https://github.com/GuoCheng24/doubleblind) |
| the paper | claims first, figures audited, tables generated | [`40-write`](../groundwork/skills/40-write/) |
| submission | hard specs as a file that fails; the rebuttal | [`50-submit`](../groundwork/skills/50-submit/) |

The single highest-value habit: **ask it to do the cheap thing that could end
the project, first.** An agent will happily spend your week building something
whose ceiling was closed on day one — not because it is careless, but because
nothing asked.

---

## Part 5 — Things that will bite you

**A long job dies with your terminal.** Launch detached, confirm it is alive at
ninety seconds, and read the head of the log where the configuration is echoed:

```bash
nohup python train.py > run.log 2>&1 &
sleep 90 && head -20 run.log && ps -p $! >/dev/null && echo alive
```

**A watch set up inside a session dies with the session.** "Check on this in an
hour" is not durable. Put it in the system scheduler and have it write a **flag
file**, then name that file in your project notes as the first thing to check.
One watch set up the session-local way went unread for forty hours.

**Your conversation survives a dropped connection.** These tools append the
transcript to disk as they go. Reconnect and continue; if the process died, the
`--continue` / `--resume` flags rebuild it. Only the in-flight request is lost.

**A configuration file can be corrupted by two sessions at once.** If the agent
starts behaving strangely, check its settings file is still valid JSON. Keep it
minimal.

**Package installs.** If the public package index is unreachable, use a mirror:

```bash
pip install -i <your local mirror> <package>
```

And be careful which conda channels you use — some distributions' default
channels are **not** free for institutional use, and the licensing follows the
repository you download from, not the domain you download through. A mirror of a
restricted channel is still that restricted channel. Community channels and the
public package index are safe.

**The environment is a silent variable.** Record the versions that produced a
result, from the runtime rather than from memory — see
[`../skills/20-experiment/hardware.md`](../groundwork/skills/20-experiment/hardware.md),
where the same weights and the same seed on two different GPUs scored 1.48
points apart.

---

## Part 6 — Sharing the machine

Somebody else is on that node.

```bash
python -m groundwork cluster survey --nodes gpu01 gpu02 gpu03
```

- **Never hard-code a device.** Pick the idlest card at start-up.
- **Do not default a small model to the CPU to be polite.** The CPU is shared
  too, and it is slower.
- **Check host memory, not just GPU memory**, before launching anything
  concurrent. The kernel's out-of-memory killer names the process that asked for
  memory last, not the one holding the most — so neither plead guilty on seeing
  your name nor claim innocence. Check the whole-node ranking.
- **Leave a card.** `cluster pick` holds one idle card per node back by default.

---

## Where to go next

- [`../README.md`](../README.md) — what this repository is for.
- [`../groundwork/skills/00-gate/SKILL.md`](../groundwork/groundwork/skills/00-gate/SKILL.md) — the four numbers
  that decide whether a direction is worth a week. Read this one before you
  start anything.
- [`../archive/causes-of-death.json`](../archive/causes-of-death.json) — ten ways
  a research direction dies, and the cheap test that catches each.
