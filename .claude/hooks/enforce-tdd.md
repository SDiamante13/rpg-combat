# Test-Driven Development Enforcement

**CRITICAL: When writing new code, fixing bugs, or adding features, you MUST follow the TDD cycle.**

## Red → Green → Refactor

### 1. RED: Write Failing Test First
- Write the test BEFORE any implementation code
- Run the test to verify it FAILS
- Confirm the failure message is correct

### 2. GREEN: Write Minimal Code
- Write only enough code to make the test pass
- No extra features or "future-proofing"
- Run the test to verify it PASSES

### 3. REFACTOR: Improve Code Quality
- Clean up the code while tests are green
- Extract constants, improve naming, remove duplication
- Run tests to ensure they still pass

## When TDD Applies

✅ **ALWAYS use TDD for:** new functions/methods, new features, bug fixes (write a test that reproduces the bug first), refactoring, API changes.

❌ **Skip TDD for:** UI styling tweaks, config changes, docs, build scripts, and behavior-free code — trivial getters/setters, plain DTOs/value objects, field-only builders/constructors. The test arrives when the accessor gains logic (computation, validation, a side effect). Do NOT write a getter/setter test just to satisfy the gate.

## Critical Rules
1. **Tests MUST fail first** — if a test passes before implementation, it's a false positive
2. **One test per requirement** — keep tests focused and clear
3. **Run full test suite before commit** — ensure no regressions
4. **NEVER skip failing tests** — fix or remove, never ignore

## Hard Gate (tdd-gate.sh)

This repo ships a PreToolUse hook on `Edit|Write|MultiEdit` that **denies code-file edits until the `tdd` skill has been invoked this session.** This is a hard gate, not a reminder.

- Invoke `/tdd` (or use the Skill tool with `skill: tdd`) before the first Edit/Write on a code file. The companion `tdd-mark.sh` hook records the load to `.claude/.tdd-state/<session_id>`.
- Gated extensions: `.ts/.tsx/.mts/.cts/.js/.jsx/.mjs/.cjs/.py/.java/.rb/.go/.rs/.kt/.swift/.scala/.c/.cc/.cpp/.cxx/.h/.hh/.hpp/.hxx/.cs/.m/.mm`.
- Exempt: anything inside `.claude/`, `skills/`, `node_modules/`, `dist/`, `build/`, `coverage/`, `__fixtures__/`, `target/`, `.next/`, `.venv/`, plus `*.d.ts`.
- Emergency bypass: `SKIP_TDD_GATE=1` in the environment. Leaves no audit trail; use sparingly.
