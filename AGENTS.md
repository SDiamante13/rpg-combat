# GUIDELINES

ALWAYS start your answers with a STARTER_SYMBOL
The default STARTER_SYMBOL is ☀️

- Be proactive and flag issues before they become a problem
- When reporting information to me, be extremely concise and sacrifice grammar for the sake of concision
- Write readable and expressive code that does not need redundant comments or reasoning why something changed
- Follow Single Responsibility Principle
- Methods should be no longer than 25 lines
- Prefer Value Objects in an Object-Oriented Codebase
- Prefer strong types and pure functions in Functional Codebases
- Prefer small reusable functions and pure functions unless handling outer shell I/O dependencies
- Proactively scan available skills and invoke relevant ones for each task
- After completing tasks that used skills, suggest improvements to those skills
- Refactoring approach: "Make the change easy, then make the easy change" (Kent Beck). When adding new integrations, first refactor existing code to be generic (separate commit), then add the feature cleanly.
- When I give a short or ambiguous request, ask ONE clarifying question immediately rather than guessing. Do not attempt multiple interpretations in sequence.

The skills and the philosophy behind this harness are documented in [README.md](./README.md).

# CONVENTIONS & DECISIONS

Record durable conventions and decisions here — version-controlled and visible to anyone working in this repo. Do NOT keep them in private/hidden agent memory.

## Refactoring

- Refactor continually as we go — the Refactor step of red→green→refactor is not optional or deferred. After each test goes green, look for duplication, unclear names, long methods, and accidental complexity in BOTH the test and the production code, and clean them up while the bar is green.
- Keep refactorings on their own commits, separate from behavior changes (ACN `. t` / `. r`), so each commit is either new behavior or a provable structure change — never both.

## Tests

- Follow Arlo Belshee's [readable-test standards](https://arlobelshee.com/what-makes-a-good-test-suite/arlo-belshee/): builder names reveal intent, never bare magic-number arguments. Prefer `aCharacterAtLevel(6)` over `aCharacter(6)`; keep an argless `aCharacter()` when the value is irrelevant.
- One test per acceptance criterion — do not consolidate away spec value.
- Place any local helper functions at the bottom of the test file, ordered by first call.
- Character tests are split by capability area: `Character.combat.test.ts`, `Character.healing.test.ts`, `Character.leveling.test.ts`, `Character.factions.test.ts`. Add a new test to the file for its area. Shared builders (`aCharacter`, `aCharacterAtLevel`, `aCharacterDamagedBy`, `aDeadCharacter`) live in `src/character-builders.ts` — import them, don't redefine.
