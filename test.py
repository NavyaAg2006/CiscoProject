"""
Test suite for the Hostel Thrift-Swap Matcher.

No external test framework -- plain assert statements, run directly:
    python test_hostel_swap_matcher.py

Tests the pure logic functions directly (satisfies, find_reciprocal_pairs,
inspect_pair, validate_listing) since those carry all the actual business
rules and don't require simulating keyboard input.
"""

import copy
import hostel_swap_matcher as m

passed_count = 0
failed_count = 0


def check(condition, description):
    global passed_count, failed_count
    if condition:
        passed_count += 1
        print(f"  PASS: {description}")
    else:
        failed_count += 1
        print(f"  FAIL: {description}")


def fresh_sample():
    """Return a deep copy of the built-in sample data so tests don't share state."""
    return copy.deepcopy(m.SAMPLE_DATA)


# ---------------------------------------------------------------------------
print("Test 1: Built-in oracle -- exactly S01 <-> S02")
# ---------------------------------------------------------------------------
data = fresh_sample()
pairs = m.find_reciprocal_pairs(data)
check(len(pairs) == 1, "exactly one reciprocal pair found")
if pairs:
    a, b = pairs[0]
    check(a["id"] == "S01" and b["id"] == "S02", "the pair is S01 <-> S02, in that order")


# ---------------------------------------------------------------------------
print("\nTest 2: S03 vs S04 -- one-way nonmatch")
# ---------------------------------------------------------------------------
data = fresh_sample()
s03 = next(x for x in data if x["id"] == "S03")
s04 = next(x for x in data if x["id"] == "S04")
result = m.inspect_pair(s03, s04)
check(result["a_to_b"]["passed"] is False, "S03 -> S04 direction fails")
check(result["b_to_a"]["passed"] is True, "S04 -> S03 direction passes")
check(
    any("SMALL" in r and "LARGE" in r for r in result["a_to_b"]["reasons"]),
    "failure reason mentions SMALL vs LARGE size mismatch",
)


# ---------------------------------------------------------------------------
print("\nTest 3: Edited S04 (requested size LARGE -> SMALL) -- two pairs, in order")
# ---------------------------------------------------------------------------
data = fresh_sample()
s04 = next(x for x in data if x["id"] == "S04")
s04["requested_size"] = "SMALL"
pairs = m.find_reciprocal_pairs(data)
check(len(pairs) == 2, "exactly two reciprocal pairs found after the edit")
if len(pairs) == 2:
    (a1, b1), (a2, b2) = pairs
    check(a1["id"] == "S01" and b1["id"] == "S02", "first pair is S01 <-> S02")
    check(a2["id"] == "S03" and b2["id"] == "S04", "second pair is S03 <-> S04")


# ---------------------------------------------------------------------------
print("\nTest 4: Self-pair exclusion -- S05 never paired with itself")
# ---------------------------------------------------------------------------
data = fresh_sample()
pairs = m.find_reciprocal_pairs(data)
check(
    all(a["id"] != b["id"] for a, b in pairs),
    "no pair matches a listing with itself",
)
s05 = next(x for x in data if x["id"] == "S05")
check(m.satisfies(s05, s05) is True, "S05 does technically satisfy its own request (sanity check)")
check(
    not any(a["id"] == "S05" and b["id"] == "S05" for a, b in pairs),
    "...but S05 never appears paired with itself in results",
)


# ---------------------------------------------------------------------------
print("\nTest 5: Duplicate ID rejected")
# ---------------------------------------------------------------------------
data = fresh_sample()
new_listing = {
    "id": "S01", "student": "Someone Else",
    "offered_category": "LAMP", "offered_size": "SMALL", "offered_condition": "GOOD",
    "requested_category": "TEXTBOOK", "requested_size": "LARGE", "min_condition": "FAIR",
}
error = m.validate_listing(new_listing, data)
check(error == "DUPLICATE_ID", "adding a second S01 reports DUPLICATE_ID")


# ---------------------------------------------------------------------------
print("\nTest 6: Empty and whitespace-only ID rejected")
# ---------------------------------------------------------------------------
data = fresh_sample()
blank_listing = {
    "id": "   ", "student": "Nobody",
    "offered_category": "LAMP", "offered_size": "SMALL", "offered_condition": "GOOD",
    "requested_category": "TEXTBOOK", "requested_size": "LARGE", "min_condition": "FAIR",
}
error = m.validate_listing(blank_listing, data)
check(error == "INVALID_ID", "blank/whitespace ID reports INVALID_ID")


# ---------------------------------------------------------------------------
print("\nTest 7: Unknown token rejected")
# ---------------------------------------------------------------------------
data = fresh_sample()
bad_listing = {
    "id": "S06", "student": "Farah",
    "offered_category": "BICYCLE", "offered_size": "SMALL", "offered_condition": "GOOD",
    "requested_category": "TEXTBOOK", "requested_size": "LARGE", "min_condition": "FAIR",
}
error = m.validate_listing(bad_listing, data)
check(error == "INVALID_LISTING_VALUE", "unknown category token (BICYCLE) reports INVALID_LISTING_VALUE")


# ---------------------------------------------------------------------------
print("\nTest 8: Empty list and single-row list produce zero pairs")
# ---------------------------------------------------------------------------
check(m.find_reciprocal_pairs([]) == [], "empty list produces zero pairs")
s05_only = [next(x for x in fresh_sample() if x["id"] == "S05")]
check(m.find_reciprocal_pairs(s05_only) == [], "single-row list (S05 alone) produces zero pairs")


# ---------------------------------------------------------------------------
print("\nTest 9: Editing a listing's own ID doesn't falsely trigger DUPLICATE_ID")
# ---------------------------------------------------------------------------
data = fresh_sample()
s01 = next(x for x in data if x["id"] == "S01")
unchanged_copy = dict(s01)  # same ID, simulating a no-op edit
error = m.validate_listing(unchanged_copy, data, editing_id="S01")
check(error is None, "re-validating S01 against itself during an edit passes (no false duplicate)")


# ---------------------------------------------------------------------------
print(f"\n{'=' * 50}")
print(f"TOTAL: {passed_count} passed, {failed_count} failed")
print("=" * 50)
if failed_count:
    raise SystemExit(1)