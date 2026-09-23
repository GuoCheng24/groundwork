# Adapters — the same stages, whichever agent you use

The stages under [`skills/`](../groundwork/skills/) are plain Markdown and the tools are
shell commands, so there is nothing to install into an agent. What differs is
how you hand a stage to it, and — for the claim stage — how you get a reviewer
that is genuinely a *different* model.

## Claude Code

```bash
# attach every stage to a project
mkdir -p .claude/skills
for d in /path/to/groundwork/skills/*/; do
  ln -s "$d" ".claude/skills/groundwork-$(basename "$d")"
done
```

Then ask for a stage by name, or invoke the tools directly. For the claim
stage's zero-context reviewer, a sub-agent starts with no conversation history
by construction — so only the model has to be chosen explicitly:

```python
Agent(subagent_type='general-purpose',
      model='<not the model that produced the artifact>',
      run_in_background=False,
      prompt=open('packet.md').read())
```

## Codex CLI

```bash
codex exec --skip-git-repo-check < groundwork/skills/00-gate/SKILL.md
codex exec --skip-git-repo-check < packet.md        # the claim stage's reviewer
```

`exec` starts a fresh session. Do not use `codex resume` for a review — the
point is that the reviewer has not seen the work.

## DeepSeek

```bash
curl -s https://api.deepseek.com/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" -H 'Content-Type: application/json' \
  -d "$(jq -Rs '{model:"deepseek-reasoner",messages:[{role:"user",content:.}]}' packet.md)"
```

## Kimi / Moonshot

```bash
curl -s https://api.moonshot.cn/v1/chat/completions \
  -H "Authorization: Bearer $MOONSHOT_API_KEY" -H 'Content-Type: application/json' \
  -d "$(jq -Rs '{model:"kimi-k2-turbo-preview",messages:[{role:"user",content:.}]}' packet.md)"
```

## Anything OpenAI-compatible

```bash
curl -s "$OPENAI_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" -H 'Content-Type: application/json' \
  -d "$(jq -Rs '{model:"'"$MODEL"'",messages:[{role:"user",content:.}]}' packet.md)"
```

One request, one message. Sending history is the thing you are avoiding.

## Whichever you use

Record, next to any review verdict, the **model id that answered** and the
**sha256 of the packet it was given** (`doubleblind review` prints it). Without
both, "a different model checked it" is a claim about a conversation nobody can
inspect — and `groundwork` deliberately cannot prove it for you, because it has
no access to your session.
