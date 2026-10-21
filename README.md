# claude-skills

Claude Code skills that I picked from Matt Pocock's [mattpocock/skills](https://github.com/mattpocock/skills)
(MIT, see [LICENSE](LICENSE)). The files are copied unchanged from upstream commit `5beb35b`
(2026-10-21). I removed only the `agents/openai.yaml` files, because they are for Codex.

## The skills

| Skill | Starts | What it does | Why I keep it |
|---|---|---|---|
| [grilling](grilling/SKILL.md) | by itself, on "grill" | Interviews you about a plan in numbered rounds. Each question has a recommended answer, so "yes" accepts it. It looks up facts itself and asks you only for decisions. | Turns a vague plan into a set of agreed decisions before any work starts. |
| [grill-me](grill-me/SKILL.md) | only `/grill-me` | A three-line wrapper that calls `grilling`. | The short name to type. |
| [writing-for-agents](writing-for-agents/SKILL.md) | by itself, when a skill, `CLAUDE.md` or `AGENTS.md` is edited | How to write text that an agent reads: trigger wording, what goes in the main file versus a linked file, prompting the wanted behavior instead of forbidding the unwanted one, and cutting instructions that change nothing. [SKILL-MECHANICS.md](writing-for-agents/SKILL-MECHANICS.md) covers frontmatter and invocation. | I keep many skills and a large `CLAUDE.md`. These rules are the author's experience, not measurements, so test them where it matters. |
| [diagnosing-bugs](diagnosing-bugs/SKILL.md) | by itself, on "debug" or a broken/slow report | First build one fast, repeatable command that fails on the exact symptom. Then shrink the case, rank 3–5 testable hypotheses, change one thing at a time, and add a regression test. | Measure before you guess. It also covers bugs that occur only sometimes, which is normal with LLM pipelines. |
| [retro](retro/SKILL.md) | only `/retro` | Reviews a session and suggests changes to the setup: navigation hints, automatic checks in place of written rules, instructions that do nothing, expensive tool calls. | Audits the environment instead of only the code. |
| [handoff](handoff/SKILL.md) | only `/handoff` | Writes a handoff document to `/tmp` so a fresh session can continue the work. | For work that is longer than one session. |
| [wait-what](wait-what/SKILL.md) | only `/wait-what` | Asks the agent to explain its last message again, with context, in ASD-STE100 Simplified Technical English. | For when an answer did not make sense. |

"By itself" means that the skill description stays in the context on every turn, so the agent
can start the skill without you. "Only `/name`" skills have `disable-model-invocation: true`:
they cost no context, and only you can start them.

`diagnosing-bugs` reads `GLOSSARY.md` and ADRs if a repo has them, and `wait-what` uses the words
from `GLOSSARY.md`. If they are not there, nothing happens.

## Install

Link each skill into `~/.claude/skills`, then start a new session:

```bash
for s in ~/claude/utilities/skills/*/; do ln -sfn "${s%/}" ~/.claude/skills/; done
```

Clone it there first if you do not have it:

```bash
git clone https://github.com/johandeclercqdemocon/claude-skills ~/claude/utilities/skills
```

## Update from upstream

```bash
git clone --depth 1 https://github.com/mattpocock/skills /tmp/mps
diff -r --exclude=agents /tmp/mps/skills/productivity/grilling ~/claude/utilities/skills/grilling
```

The upstream folders are `skills/productivity/` for grill-me, grilling, writing-for-agents,
handoff and wait-what, and `skills/engineering/` for diagnosing-bugs and retro. Change the commit
hash at the top of this file when you copy a new version.

## What I did not take

- The issue-tracker workflow (`to-spec`, `to-tickets`, `triage`, `wayfinder`, `implement*`,
  `setup-matt-pocock-skills`): it is made for a team that works from tickets.
- `code-review`: it has the same name as the Claude Code built-in `/code-review`.
- The TypeScript and Node tools (`migrate-to-shoehorn`, `setup-ts-deep-modules`, `setup-pre-commit`,
  `scaffold-exercises`): I work in Python.
- `research`: `deep-research` already does this.
- `skills/in-progress/*`: upstream marks these as not finished.
