# claude-skills

The Claude Code skills I use. Two groups:

- **My own skills**: how I write measured books and run agents and long jobs. They are written for
  my machine, so they name paths such as `~/claude/ml-book` as reference implementations. Read a
  skill before you install it, and change the paths.
- **Skills from Matt Pocock**: picked from [mattpocock/skills](https://github.com/mattpocock/skills)
  (MIT, see [LICENSE-mattpocock](LICENSE-mattpocock)), copied unchanged from upstream commit `5beb35b`
  (2026-10-21). I removed only the `agents/openai.yaml` files, because they are for Codex.

"By itself" means that the skill description stays in the context on every turn, so the agent
can start the skill without you. "Only `/name`" skills have `disable-model-invocation: true`:
they cost no context, and only you can start them.

## My own skills

| Skill | Starts | What it does |
|---|---|---|
| [measured-writing](measured-writing/SKILL.md) | by itself, for a book, guide or README | The pattern for a book: every claim is measured by code that ships with the text, every chapter is named after a thing the reader builds, and a checker fails the build when prose and code disagree. |
| [check-what-you-write](check-what-you-write/SKILL.md) | by itself, when text states a number, name or command | The audit before a chapter is done: numbers, identifiers, claims and assumptions, each checked against what the machine printed. |
| [programming-book-depth](programming-book-depth/SKILL.md) | by itself, for a book about a library or API | Every chapter gets a "How it works" section and a "Reference" section with signatures printed by `inspect` and a row for every parameter. |
| [simplified-technical-english](simplified-technical-english/SKILL.md) | by itself, for technical documentation or "STE" | Writes in ASD-STE100 Simplified Technical English, with a checker script. MIT for the skill text; the word list is from the ASD dictionary, see its [NOTICE](simplified-technical-english/NOTICE.md). |
| [freeze-during-sweep](freeze-during-sweep/SKILL.md) | by itself, while a checker or test run is busy | Edit nothing that a running verification reads, and discard the run if you did. |
| [long-run-heartbeat](long-run-heartbeat/SKILL.md) | by itself, for a job of more than a few minutes | Report a rate every 7 minutes, never block and never go silent. |
| [work-the-queue](work-the-queue/SKILL.md) | by itself, on "do all of X" or "continue" | Work an agreed list to the end without asking between items, and report once. |
| [validate-before-paid-calls](validate-before-paid-calls/SKILL.md) | by itself, before a run that bills model inference | Prove the judge, the plumbing and the runner for free before the first paid call. |
| [agent-harness](agent-harness/SKILL.md) | by itself, for a tool-calling agent or its evaluation | How to build and measure an agent loop: validated tools, failures as observations, a cached client, a trace per run, tasks that code can grade. Includes the failures measured on small local Ollama models. |
| [desktop-control](desktop-control/SKILL.md) | by itself, to click or read a desktop app | Drives desktop applications by control name through AT-SPI, which works under Wayland. Includes [desktop.py](desktop-control/scripts/desktop.py). |
| [app-walkthrough](app-walkthrough/SKILL.md) | by itself, to demo an app or prove a procedure | A numbered screenshot walkthrough that proves a claim, with the failures included. Uses `desktop-control`. |

## Skills from Matt Pocock

| Skill | Starts | What it does | Why I keep it |
|---|---|---|---|
| [grilling](grilling/SKILL.md) | by itself, on "grill" | Interviews you about a plan in numbered rounds. Each question has a recommended answer, so "yes" accepts it. It looks up facts itself and asks you only for decisions. | Turns a vague plan into a set of agreed decisions before any work starts. |
| [grill-me](grill-me/SKILL.md) | only `/grill-me` | A three-line wrapper that calls `grilling`. | The short name to type. |
| [writing-for-agents](writing-for-agents/SKILL.md) | by itself, when a skill, `CLAUDE.md` or `AGENTS.md` is edited | How to write text that an agent reads: trigger wording, what goes in the main file versus a linked file, prompting the wanted behavior instead of forbidding the unwanted one, and cutting instructions that change nothing. [SKILL-MECHANICS.md](writing-for-agents/SKILL-MECHANICS.md) covers frontmatter and invocation. | I keep many skills and a large `CLAUDE.md`. These rules are the author's experience, not measurements, so test them where it matters. |
| [diagnosing-bugs](diagnosing-bugs/SKILL.md) | by itself, on "debug" or a broken/slow report | First build one fast, repeatable command that fails on the exact symptom. Then shrink the case, rank 3–5 testable hypotheses, change one thing at a time, and add a regression test. | Measure before you guess. It also covers bugs that occur only sometimes, which is normal with LLM pipelines. |
| [retro](retro/SKILL.md) | only `/retro` | Reviews a session and suggests changes to the setup: navigation hints, automatic checks in place of written rules, instructions that do nothing, expensive tool calls. | Audits the environment instead of only the code. |
| [handoff](handoff/SKILL.md) | only `/handoff` | Writes a handoff document to `/tmp` so a fresh session can continue the work. | For work that is longer than one session. |
| [wait-what](wait-what/SKILL.md) | only `/wait-what` | Asks the agent to explain its last message again, with context, in ASD-STE100 Simplified Technical English. | For when an answer did not make sense. |

`diagnosing-bugs` reads `GLOSSARY.md` and ADRs if a repo has them, and `wait-what` uses the words
from `GLOSSARY.md`. If they are not there, nothing happens.

## Install

Clone the repo, then link the skills you want into `~/.claude/skills` and start a new session:

```bash
git clone https://github.com/johandeclercqdemocon/claude-skills ~/claude/utilities/skills
```

```bash
for s in ~/claude/utilities/skills/*/; do ln -sfn "${s%/}" ~/.claude/skills/; done
```

The loop links all of them. Every "by itself" skill adds its description to every turn, so link
only the ones you use.

## Where the source is

My own skills are maintained in my private environment repo, and this repo holds a published copy.
The Pocock skills are updated from upstream:

```bash
git clone --depth 1 https://github.com/mattpocock/skills /tmp/mps
diff -r --exclude=agents /tmp/mps/skills/productivity/grilling ~/claude/utilities/skills/grilling
```

The upstream folders are `skills/productivity/` for grill-me, grilling, writing-for-agents,
handoff and wait-what, and `skills/engineering/` for diagnosing-bugs and retro. Change the commit
hash at the top of this file when you copy a new version.

## What is not here

- Two of my skills hold personal data: a cover-letter skill and a list of my repositories.
- The LangChain, LangGraph and Deep Agents skills, and Anthropic's own skills: they belong to
  their publishers. Get them from the source.
- From Matt Pocock's repo: the issue-tracker workflow (`to-spec`, `to-tickets`, `triage`,
  `wayfinder`, `implement*`, `setup-matt-pocock-skills`), which is made for a team that works from
  tickets; `code-review`, which has the same name as the Claude Code built-in `/code-review`; the
  TypeScript and Node tools, because I work in Python; `research`, because `deep-research` already
  does it; and `skills/in-progress/*`, which upstream marks as not finished.
