# Cisco Summer Internship Interview Project
## Hostel Thrift-Swap Matcher

## 1. Working Solution

### What it does
A command-line tool that finds **reciprocal two-person item swaps** among hostel
students. Each student lists one item they're offering and one they want. The
tool finds pairs where each person's offer satisfies the other's request —
not one-directional matches, not multi-party chains.

### Core features implemented
- Menu-driven CLI: load sample data, add / edit / delete a listing, view all
  listings, run the match, filter match results by participant ID, inspect
  any two listings directionally, reset, quit.
- Validation on every add/edit: empty/duplicate IDs (`INVALID_ID`,
  `DUPLICATE_ID`) and out-of-vocabulary category/size/condition tokens
  (`INVALID_LISTING_VALUE`).
- Reciprocal matching: examines each unordered pair once (`i < j`), so no
  reversed duplicates; excludes self-pairs by construction.
- Two-direction pair inspector: shows both directional checks separately,
  with the specific reason(s) a direction fails (category, size, or
  condition mismatch).

### Running instructions
Requires Python 3.8+ and no external libraries (standard library only).

```bash
python hostel_swap_matcher.py
```

You'll see a numbered menu. Start with option `1` (Load sample data) to load
the 5 built-in listings, then explore `6` (Run match) and `8` (Inspect a
pair).

To run the automated test suite:

```bash
python test_hostel_swap_matcher.py
```

### Sample data
Five built-in listings (hardcoded in `SAMPLE_DATA`), matching the problem
statement's example exactly:

| ID | Student | Offers | Wants |
|---|---|---|---|
| S01 | Asha | Calculator/Standard/Good | Textbook/Large/Fair |
| S02 | Bilal | Textbook/Large/Fair | Calculator/Standard/Good |
| S03 | Chen | Lamp/Small/Excellent | Calculator/Standard/Fair |
| S04 | Divya | Calculator/Standard/Good | Lamp/Large/Good |
| S05 | Eshan | Headphones/Standard/Good | Headphones/Standard/Fair |

Expected result: exactly one reciprocal pair, **S01 ↔ S02**.

---

## 2. AI Interaction Documentation

### Prompt history and iteration examples

The process started broad and narrowed with each response, rather than
jumping straight to code:

1. **Broad framing prompt** (after uploading the problem PDF):
   *"start by explaining to me the problem statement in detail"* — used to
   confirm shared understanding of the spec before any design decisions,
   with an explicit steer toward simplicity: *"since this is actually a
   simple problem with a standard solution, our main focus would be on:
   functional core features, running instructions, sample data, practical
   design choices, testing mindset."*

2. **Design phase, kept deliberately AI-guided, not AI-decided**: *"let's
   discuss"* — a standing instruction that the AI should present options and
   ask questions rather than choose the architecture itself. This shaped the
   whole design conversation as a series of forced tradeoff comparisons
   (CLI vs. Streamlit vs. HTML vs. Sheets; dict vs. dataclass; single file
   vs. modules) rather than a single AI-generated recommendation.

3. **Iteration example — stack choice refined by constraint injection**: the
   first-pass stack comparison was fairly neutral. After the fuller rubric
   text was shared (a mid-conversation constraint addition: *"this is what
   is required btw:"* followed by the full deliverables list), the AI
   re-evaluated the same four options against the new, more specific
   criteria ("prioritize simplicity and familiar tools," "technology
   familiarity: use technologies you can explain and debug confidently").
   This is a direct example of a broad initial answer being refined by
   adding more specific requirements.

4. **Iteration example — decision reversed once real constraint surfaced**:
   initial lean was ambiguous ("ig cli") reasoned from unfamiliarity with
   Streamlit alone. The AI pushed back, distinguishing "I don't know it"
   from "I've decided against it," and asked two direct questions (time
   budget, live-demo comfort) before accepting the final CLI decision — an
   example of AI helping pressure-test a choice rather than just accepting
   the first answer.

5. **Problem-solving / self-correction example**: the AI proposed clearing
   the pair-inspector display whenever a fresh "Match" was run, treating it
   as a design ambiguity worth deciding. The user correctly pointed out this
   was a non-issue for a CLI (each menu action just prints its own output;
   nothing persists on-screen to "clear"). The AI acknowledged the
   over-thought framing and adjusted, rather than defending the original
   proposal — an example of a design assumption being corrected through
   discussion rather than assumed correct.

6. **Scope correction example**: a plan step labeled "data + validation
   layer" was mistaken by the user for a request to build validation as a
   separate architectural layer, when the actual requirement was just
   sample data for testing. The AI clarified the distinction explicitly
   (validation checks are still required by the acceptance criteria, e.g.
   `DUPLICATE_ID`, but don't need their own module) before writing code —
   an example of confirming scope before generating a large code block,
   rather than silently guessing.

### AI-assisted debugging
After the full script was generated, the AI ran it against real Python
(rather than only visually reviewing it) to catch runtime issues before
declaring it done — importing the module and executing `find_reciprocal_pairs`
and `inspect_pair` directly against the sample data to confirm output matched
the two required example scenarios (S01↔S02 oracle match, S03/S04
one-directional result) before moving to the full test suite.

---

## 3. Design Summary

### Architecture decisions

| Decision | Choice | Why |
|---|---|---|
| Platform | Python CLI | Matches the spec's explicit allowance for a "CLI that produces a clear visual or tabular report"; fastest to build and test; avoids learning a new UI framework (Streamlit) under time pressure |
| Interaction model | Menu loop | More comfortable for a live demo than remembering command-line flags |
| Data representation | List of plain dicts | Familiar, zero setup, transparent for debugging; a dataclass was considered but rejected as not worth the added concept for a short-lived script with a fixed, simple schema |
| File structure | Single file, separate functions | The application is small (under ~350 lines); splitting into modules was judged unnecessary layering for this scope, and the rubric explicitly warns against over-engineering |
| Output style | Plain aligned prints | No external formatting library (e.g. `tabulate`) — keeps "quick startup" true with zero extra installs |
| Sample data | Hardcoded in-script | Matches the built-in example directly; no file I/O needed for the required demo case |
| Validation | Inline in add/edit functions | Still required by the acceptance criteria (`DUPLICATE_ID`, `INVALID_ID`, `INVALID_LISTING_VALUE`), but implemented inline rather than as a separate validation module, per an explicit scope correction during design |

### AI influence on design
The AI's role was restricted (by explicit instruction) to presenting options,
tradeoffs, and clarifying questions rather than making the calls directly.
Concretely, the AI:
- Surfaced tradeoffs the user might not have framed on their own (e.g., that
  the rubric text itself nudges toward "familiar tools" over "impressive
  tools," which reframed the CLI vs. Streamlit decision).
- Distinguished a real ambiguity in the source spec (what happens to the
  pair inspector on a fresh Match) from what turned out to be a non-issue
  once the CLI's actual execution model was considered.
- Flagged a scope-boundary risk (dropping validation logic entirely) before
  writing code, rather than silently complying with an ambiguous
  instruction that could have violated a required acceptance criterion.

### Trade-offs — what was prioritized vs. deferred
**Prioritized:**
- Correctness against the explicit oracle scenarios (S01↔S02, S03/S04
  inspection, edited-S04 case) — these were tested first and are the load-
  bearing evidence of correctness.
- Debuggability and familiarity over visual polish — a deliberate trade
  given the "technologies you can explain and debug confidently" rubric
  emphasis.

**Deferred / consciously not built:**
- Persistent storage (all listings live in memory for the session, matching
  the "in-memory data structures" allowance in the spec — no database or
  file save/load was built, since it wasn't required).
- Any accounts, payments, chat, or multi-party swap cycles — explicitly
  out of scope per the problem statement.
- Automated tests for the `input()`-driven menu functions themselves (add,
  edit, delete, and the menu loop) — only the pure logic functions
  underneath them are covered by automated tests, since testing
  interactive `input()` calls would require stdin-mocking infrastructure
  disproportionate to the scope. A manual walkthrough of the live menu is
  the intended supplement to this gap.

---

## 4. Test Evidence

### Test plan
Automated tests (`test_hostel_swap_matcher.py`) target the pure logic
functions directly (`satisfies`, `find_reciprocal_pairs`, `inspect_pair`,
`validate_listing`), since these carry all the actual business rules and
don't require simulating keyboard input. The plan covers:

1. **Built-in oracle** — loading the 5 sample listings produces exactly one
   reciprocal pair, S01 ↔ S02.
2. **Directional inspection** — S03 vs S04 shows a one-way nonmatch, with
   the SMALL vs LARGE size mismatch surfaced as the failure reason.
3. **Live-modification scenario** — editing only S04's requested size from
   LARGE to SMALL produces two pairs in order: S01↔S02, then S03↔S04.
4. **Self-pair exclusion** — S05 technically satisfies its own request, but
   never appears paired with itself in results.
5. **Duplicate ID rejection** — adding a second "S01" reports `DUPLICATE_ID`.
6. **Invalid ID rejection** — blank/whitespace-only ID reports `INVALID_ID`.
7. **Invalid value rejection** — an out-of-vocabulary token (e.g.
   `BICYCLE`) reports `INVALID_LISTING_VALUE`.
8. **Boundary sizes** — an empty list and a single-row list both produce
   zero pairs (not an error).
9. **Edit-in-place edge case** — re-validating a listing against itself
   during an edit (same ID, unchanged) does not falsely trigger
   `DUPLICATE_ID`.

### Test results
All 17 checks pass:

```
Test 1: Built-in oracle -- exactly S01 <-> S02
  PASS: exactly one reciprocal pair found
  PASS: the pair is S01 <-> S02, in that order

Test 2: S03 vs S04 -- one-way nonmatch
  PASS: S03 -> S04 direction fails
  PASS: S04 -> S03 direction passes
  PASS: failure reason mentions SMALL vs LARGE size mismatch

Test 3: Edited S04 (requested size LARGE -> SMALL) -- two pairs, in order
  PASS: exactly two reciprocal pairs found after the edit
  PASS: first pair is S01 <-> S02
  PASS: second pair is S03 <-> S04

Test 4: Self-pair exclusion -- S05 never paired with itself
  PASS: no pair matches a listing with itself
  PASS: S05 does technically satisfy its own request (sanity check)
  PASS: ...but S05 never appears paired with itself in results

Test 5: Duplicate ID rejected
  PASS: adding a second S01 reports DUPLICATE_ID

Test 6: Empty and whitespace-only ID rejected
  PASS: blank/whitespace ID reports INVALID_ID

Test 7: Unknown token rejected
  PASS: unknown category token (BICYCLE) reports INVALID_LISTING_VALUE

Test 8: Empty list and single-row list produce zero pairs
  PASS: empty list produces zero pairs
  PASS: single-row list (S05 alone) produces zero pairs

Test 9: Editing a listing's own ID doesn't falsely trigger DUPLICATE_ID
  PASS: re-validating S01 against itself during an edit passes (no false duplicate)

==================================================
TOTAL: 17 passed, 0 failed
==================================================
```

### Known gap (documented, not hidden)
The menu/CLI wiring itself (`action_add`, `action_edit`, `action_delete`,
the main loop) is not covered by the automated suite, since these rely on
`input()`. A manual run through the live menu — loading sample data, editing
S04's size, deleting a listing, and hitting each validation error on purpose
— is the recommended supplement before presenting, to catch any prompt-
wiring issues the automated tests wouldn't surface.

---

## 5. Development Environment Readiness

- Runs with plain `python hostel_swap_matcher.py` — no install step, no
  dependencies beyond the Python standard library.
- All logic lives in named, single-purpose functions (`satisfies`,
  `find_reciprocal_pairs`, `inspect_pair`, `validate_listing`,
  `action_*`), so a live modification (e.g., adding a new category, or
  changing the condition ranking) means editing one function, not
  hunting across files.
- Test suite re-runs in under a second, so any live change can be
  immediately re-verified against the 17 existing checks before making a
  second change.
