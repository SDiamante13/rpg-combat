# RPG Combat

An RPG Combat kata, used here as a workbench for a **self-contained agentic coding harness** — every skill, hook, and rule the agent uses lives inside this repo, so it's transparent what's shaping the agent's behavior.

```bash
npm install
npm test
```

## Why this repo exists

This is a research setup for technical coaches. The point isn't the kata — it's that the whole harness is in plain sight. Open `.claude/` and `AGENTS.md` and you can see exactly which skills are available, which rules apply, and where the TDD gate bites. No hidden global config, no surprise plugins.

## Philosophy

Less is more. The agent instructions (`AGENTS.md`) are intentionally lean — enough to establish core principles without bloat. The power comes from specialized skills that activate specific workflows when you need them.

### Claude as pair programmer

With 8+ years of pair programming experience, I treat Claude as a true collaborator — not a code generator. That means:

- **Planning together** — `/interview` to probe requirements, challenge assumptions, explore tradeoffs
- **Challenging each other** — pushing back on solutions to reach better abstractions and maintainable designs
- **Iterating on quality** — continuous refactoring cycles that improve expressiveness
- **Small vertical slices** — `/split` work into independently deliverable pieces with clear value

The goal isn't just working code — it's **maintainable code that delights customers**.

### Core beliefs

- Code craft matters — write readable, expressive code that doesn't need comments
- Continuous refactoring — quality is built in, not bolted on
- Small vertical slices — deliver value incrementally with clear acceptance criteria
- TDD discipline — tests drive design and provide feedback loops

This harness comes out of the work I share in [*Software Craftsmanship for Coding Agents: Taming the Dragon*](https://youtu.be/nd2fXYHK4vc) and the [Augmented Coding Patterns](https://lexler.github.io/augmented-coding-patterns/talk/) by Lada Kessler.

## Skills in this repo

All under `.claude/skills/`:

| Skill                     | What it does                                                                                                                                          |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/tdd`                    | Strict outside-in red→green→refactor. One failing test per turn, hardcode-first, triangulate. Required before any code edit (see gate below).         |
| `/interview`              | Deep requirements probing — technical, UI/UX, risks, tradeoffs — before writing a spec.                                                               |
| `/split`                  | Slice a story into smaller, independently deliverable pieces using SPIDR.                                                                             |
| `/refactor-tests`         | Improve behavioral coverage and clarity of tests; remove implementation-detail and low-value tests.                                                   |
| `/retroactive-test-check` | Backfilling a test for existing behavior? Mutation-verify it — break the production code to confirm the test fails for the right reason.              |
| `/tidy`                   | Refactor production code under green tests.                                                                                                           |
| `/sweep`                  | Review the codebase for structural smells (file/method length, accidental complexity, test readability), then fix them with provable micro-refactors. |
| `/review`                 | Comprehensive review for quality, maintainability, and security.                                                                                      |
| `/commit`                 | Quality-checked commits — status review, staged-diff inspection, run tests, clear message.                                                            |

## TDD hard gate

A PreToolUse hook (`.claude/hooks/tdd-gate.sh`) **denies code-file edits until `/tdd` is invoked this session.** It's a hard gate, not a reminder — every code change must trace to a failing test.

- Invoke `/tdd` before your first edit on a code file.
- Exempt: `.claude/`, `skills/`, build output, fixtures, `*.d.ts` (see `.claude/hooks/enforce-tdd.md`).
- Emergency bypass: `SKIP_TDD_GATE=1` in the environment — leaves no audit trail, use sparingly.

State lives in `.claude/.tdd-state/` so the whole loop stays inside the repo.

## Starter characters

A visual signal of which mode the agent is in — and a context-health canary. If the agent stops emitting the starter character, the context window is running low; wrap up or start fresh.

| Character | Mode                                     |
|-----------|------------------------------------------|
| ☀️        | Default collaboration                    |
| 🔴        | TDD — writing a failing test             |
| 🌱        | TDD — minimal code to pass               |
| 🌀        | TDD — refactor without changing behavior |

## Isolating the harness for a demo

Claude Code always loads personal (`~/.claude/skills`) and plugin skills alongside this repo's — there's no native per-project allowlist. To run a session with **only** these skills:

```bash
bash .claude/demo-isolate.sh    # moves your personal skills aside + disables global plugins (backs up first)
# relaunch claude in this repo   ← only the repo skills load now
# ... run the demo ...
bash .claude/demo-restore.sh    # restores everything
```
