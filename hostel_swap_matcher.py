"""
Hostel Thrift-Swap Matcher
--------------------------
A CLI tool that finds reciprocal two-person item swaps among hostel students.

Run with:  python hostel_swap_matcher.py
"""

# ---------------------------------------------------------------------------
# Constants (allowed values per the problem contract)
# ---------------------------------------------------------------------------
CATEGORIES = {"CALCULATOR", "TEXTBOOK", "LAMP", "HEADPHONES"}
SIZES = {"SMALL", "STANDARD", "LARGE"}
CONDITION_RANK = {"FAIR": 0, "GOOD": 1, "EXCELLENT": 2}

FIELDS = [
    "student",
    "offered_category", "offered_size", "offered_condition",
    "requested_category", "requested_size", "min_condition",
]

VALUE_FIELDS = {
    "offered_category": CATEGORIES,
    "requested_category": CATEGORIES,
    "offered_size": SIZES,
    "requested_size": SIZES,
    "offered_condition": CONDITION_RANK.keys(),
    "min_condition": CONDITION_RANK.keys(),
}

SAMPLE_DATA = [
    {"id": "S01", "student": "Asha",  "offered_category": "CALCULATOR", "offered_size": "STANDARD",
     "offered_condition": "GOOD",      "requested_category": "TEXTBOOK",   "requested_size": "LARGE",
     "min_condition": "FAIR"},
    {"id": "S02", "student": "Bilal",  "offered_category": "TEXTBOOK",   "offered_size": "LARGE",
     "offered_condition": "FAIR",      "requested_category": "CALCULATOR", "requested_size": "STANDARD",
     "min_condition": "GOOD"},
    {"id": "S03", "student": "Chen",   "offered_category": "LAMP",       "offered_size": "SMALL",
     "offered_condition": "EXCELLENT", "requested_category": "CALCULATOR", "requested_size": "STANDARD",
     "min_condition": "FAIR"},
    {"id": "S04", "student": "Divya",  "offered_category": "CALCULATOR", "offered_size": "STANDARD",
     "offered_condition": "GOOD",      "requested_category": "LAMP",       "requested_size": "LARGE",
     "min_condition": "GOOD"},
    {"id": "S05", "student": "Eshan",  "offered_category": "HEADPHONES", "offered_size": "STANDARD",
     "offered_condition": "GOOD",      "requested_category": "HEADPHONES", "requested_size": "STANDARD",
     "min_condition": "FAIR"},
]

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
listings = []          # list of listing dicts, the source of truth
last_matches = None    # list of (listing_i, listing_j) tuples, or None if stale
last_inspection = None # dict result of last inspect_pair call, or None if stale


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_listing(listing, existing, editing_id=None):
    """
    Returns None if valid, else an error code string:
    'INVALID_ID', 'DUPLICATE_ID', or 'INVALID_LISTING_VALUE'.
    `editing_id` excludes the listing's own current ID from the duplicate check
    (used when editing an existing listing in place).
    """
    listing_id = listing["id"].strip()
    listing["id"] = listing_id  # store the trimmed version

    if not listing_id:
        return "INVALID_ID"

    for other in existing:
        if other["id"] == listing_id and listing_id != editing_id:
            return "DUPLICATE_ID"

    for field, allowed in VALUE_FIELDS.items():
        if listing[field] not in allowed:
            return "INVALID_LISTING_VALUE"

    return None


# ---------------------------------------------------------------------------
# Matching logic (pure functions, no I/O -- easy to test in isolation)
# ---------------------------------------------------------------------------
def satisfies(offerer, requester):
    """Does offerer's offered item satisfy requester's request?"""
    return (
        offerer["offered_category"] == requester["requested_category"]
        and offerer["offered_size"] == requester["requested_size"]
        and CONDITION_RANK[offerer["offered_condition"]] >= CONDITION_RANK[requester["min_condition"]]
    )


def find_reciprocal_pairs(all_listings):
    """Return list of (a, b) tuples for every reciprocal match, i < j order."""
    pairs = []
    n = len(all_listings)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = all_listings[i], all_listings[j]
            if satisfies(a, b) and satisfies(b, a):
                pairs.append((a, b))
    return pairs


def _direction_result(offerer, requester):
    passed = satisfies(offerer, requester)
    reasons = []
    if offerer["offered_category"] != requester["requested_category"]:
        reasons.append(
            f"category mismatch: offers {offerer['offered_category']}, "
            f"needs {requester['requested_category']}"
        )
    elif offerer["offered_size"] != requester["requested_size"]:
        reasons.append(
            f"size mismatch: offers {offerer['offered_size']}, "
            f"needs {requester['requested_size']}"
        )
    elif CONDITION_RANK[offerer["offered_condition"]] < CONDITION_RANK[requester["min_condition"]]:
        reasons.append(
            f"condition too low: offers {offerer['offered_condition']}, "
            f"needs at least {requester['min_condition']}"
        )
    return {"offerer": offerer["id"], "requester": requester["id"], "passed": passed, "reasons": reasons}


def inspect_pair(a, b):
    """Return both directional results with pass/fail + reason for failure."""
    return {
        "a_to_b": _direction_result(a, b),
        "b_to_a": _direction_result(b, a),
    }

# ---------------------------------------------------------------------------
# Helpers for menu actions
# ---------------------------------------------------------------------------
def find_listing(listing_id):
    for listing in listings:
        if listing["id"] == listing_id:
            return listing
    return None


def clear_results():
    global last_matches, last_inspection
    last_matches = None
    last_inspection = None


def print_listing(listing):
    print(
        f"  {listing['id']} ({listing['student']}): "
        f"offers {listing['offered_category']}/{listing['offered_size']}/{listing['offered_condition']} "
        f"-> wants {listing['requested_category']}/{listing['requested_size']}/{listing['min_condition']}+"
    )


def print_listings():
    if not listings:
        print("No listings loaded.")
        return
    print(f"\nCurrent listings ({len(listings)}):")
    for listing in listings:
        print_listing(listing)


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------
def action_load_sample():
    global listings
    listings = [dict(row) for row in SAMPLE_DATA]  # deep-ish copy of each row
    clear_results()
    print("Loaded 5 built-in sample listings.")
    print_listings()


def action_add():
    print("\nAdd a new listing. Allowed values:")
    print(f"  categories: {sorted(CATEGORIES)}")
    print(f"  sizes: {sorted(SIZES)}")
    print(f"  conditions: {sorted(CONDITION_RANK, key=CONDITION_RANK.get)}")

    listing_id = input("ID: ")
    new_listing = {"id": listing_id}
    new_listing["student"] = input("Student name: ")
    new_listing["offered_category"] = input("Offered category: ").strip().upper()
    new_listing["offered_size"] = input("Offered size: ").strip().upper()
    new_listing["offered_condition"] = input("Offered condition: ").strip().upper()
    new_listing["requested_category"] = input("Requested category: ").strip().upper()
    new_listing["requested_size"] = input("Requested size: ").strip().upper()
    new_listing["min_condition"] = input("Minimum requested condition: ").strip().upper()

    error = validate_listing(new_listing, listings)
    if error:
        clear_results()
        print(f"ERROR: {error}")
        return

    listings.append(new_listing)
    clear_results()
    print(f"Added {new_listing['id']}.")


def action_edit():
    listing_id = input("ID of listing to edit: ").strip()
    listing = find_listing(listing_id)
    if listing is None:
        print(f"No listing with ID '{listing_id}' found.")
        return

    print("Press Enter to keep the current value for any field.")
    updated = dict(listing)  # work on a copy in case validation fails

    new_id = input(f"ID [{listing['id']}]: ").strip()
    if new_id:
        updated["id"] = new_id

    for field in FIELDS:
        current = listing[field]
        prompt_val = input(f"{field} [{current}]: ").strip()
        if prompt_val:
            updated[field] = prompt_val.upper() if field in VALUE_FIELDS else prompt_val

    error = validate_listing(updated, listings, editing_id=listing_id)
    if error:
        clear_results()
        print(f"ERROR: {error}")
        return

    listing.update(updated)
    clear_results()
    print(f"Updated {listing['id']}.")


def action_delete():
    listing_id = input("ID of listing to delete: ").strip()
    listing = find_listing(listing_id)
    if listing is None:
        print(f"No listing with ID '{listing_id}' found.")
        return
    listings.remove(listing)
    clear_results()
    print(f"Deleted {listing_id}.")


def action_match():
    global last_matches
    last_matches = find_reciprocal_pairs(listings)
    if not last_matches:
        print("\nNo reciprocal pairs found.")
        return
    print(f"\nFound {len(last_matches)} reciprocal pair(s):")
    for idx, (a, b) in enumerate(last_matches, start=1):
        print(f"  Pair {idx}: {a['id']} ({a['student']}) <-> {b['id']} ({b['student']})")


def action_filter_matches():
    if last_matches is None:
        print("No match results yet. Run Match first.")
        return
    participant_id = input("Filter by participant ID: ").strip()
    filtered = [(a, b) for (a, b) in last_matches if a["id"] == participant_id or b["id"] == participant_id]
    if not filtered:
        print(f"No matches involving {participant_id}.")
        return
    print(f"Matches involving {participant_id}:")
    for (a, b) in filtered:
        print(f"  {a['id']} ({a['student']}) <-> {b['id']} ({b['student']})")


def action_inspect():
    global last_inspection
    id_a = input("First ID: ").strip()
    id_b = input("Second ID: ").strip()
    a, b = find_listing(id_a), find_listing(id_b)

    if a is None or b is None:
        print("One or both IDs not found.")
        return
    if id_a == id_b:
        print("A student can never be paired with themself.")
        return

    last_inspection = inspect_pair(a, b)
    print(f"\nInspecting {id_a} <-> {id_b}:")
    for key, label in [("a_to_b", f"{id_a} -> {id_b}"), ("b_to_a", f"{id_b} -> {id_a}")]:
        result = last_inspection[key]
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  {label}: {status}")
        for reason in result["reasons"]:
            print(f"    - {reason}")


def action_reset():
    global listings
    listings = []
    clear_results()
    print("Reset complete. All listings cleared.")


def action_quit():
    print("Goodbye.")
    raise SystemExit


MENU = {
    "1": ("Load sample data", action_load_sample),
    "2": ("Add a listing", action_add),
    "3": ("Edit a listing", action_edit),
    "4": ("Delete a listing", action_delete),
    "5": ("View listings", print_listings),
    "6": ("Run match", action_match),
    "7": ("Filter last match results by participant ID", action_filter_matches),
    "8": ("Inspect a pair", action_inspect),
    "9": ("Reset", action_reset),
    "0": ("Quit", action_quit),
}


def print_menu():
    print("\n" + "=" * 50)
    print("Hostel Thrift-Swap Matcher")
    print("=" * 50)
    for key, (label, _) in MENU.items():
        print(f"  {key}. {label}")


def main():
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        action = MENU.get(choice)
        if action is None:
            print("Invalid option, try again.")
            continue
        action[1]()


if __name__ == "__main__":
    main()