import re


def next_sequential_id(existing_ids, prefix: str, pad: int = 4, start: int = 1) -> str:
    """Given the existing IDs already in a sheet/column (e.g. ["TRX_1001",
    "TRX_1002"]) and a prefix (e.g. "TRX_"), returns the next ID in the same
    format: prefix + zero-padded number one higher than the current max.

    This is what every service module uses to generate new keys, so no
    matter which sheet or which page in the app is doing the writing, IDs
    always come out matching the convention already established in that
    sheet (ACC_001, CAT_001, TRX_1001, BDG_202608_001, etc.) instead of a
    random/UUID-style ID that would look out of place next to the existing
    data.

    If nothing matches the prefix yet, starts at `start` (default 1).
    Never re-uses a number, even if earlier rows were voided/deleted, since
    it always looks at the current max - so IDs stay unique even as data
    changes over time.
    """
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
    max_n = start - 1
    for existing in existing_ids:
        match = pattern.match(str(existing).strip())
        if match:
            max_n = max(max_n, int(match.group(1)))
    return f"{prefix}{str(max_n + 1).zfill(pad)}"
