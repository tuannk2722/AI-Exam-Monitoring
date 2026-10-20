"""Import explicit owner decisions without treating unrendered recrops as approved."""

import json
import re
from collections import Counter

from intake import HERE, dump


def main():
    queue = json.loads((HERE / "intake-ledger.json").read_text(encoding="utf-8"))
    result = []
    for r in queue:
        owner = r["owner_review"]
        comments = owner["owner_comments"] if owner else []
        text = " | ".join(comments).strip(" |")
        state = r["parent_states"]
        decision = "needs_interpretation"
        authority = "owner_written_comment"
        action = r["parent_action"]
        if r["owner_default_approval"]:
            decision = (
                "approved_existing"
                if action == "keep"
                else "approved_exclusion"
                if action == "exclude"
                else "approved_recrop_request"
            )
            authority = "owner_default_approval_chat_20261019"
        elif re.fullmatch(
            r"(exclude|exlcude)(\s*\|\s*exclude)?", text, flags=re.I
        ) or text.lower().startswith(("exclude,", "loại,")):
            if r["id"] != "V7-OE-S023-A01":
                action, decision = "exclude", "approved_exclusion"
        else:
            # Bare labels are unambiguous. Prose mixed with geometry needs visual resolution.
            m = re.fullmatch(r"([PNU])/([PNU])", text)
            if m:
                state = list(m.groups())
                if action == "keep":
                    decision = "approved_existing"
                elif action == "recrop":
                    decision = "approved_recrop_request"
                else:
                    decision = "owner_reinclude_needs_qa"
        if r["audit"] == "youtube71" and owner:
            m = re.fullmatch(r"([PNU])/([PNU])", comments[0])
            if m and r["id"] != "Y01-A09-F00037":
                state = list(m.groups())
                decision = "approved_existing"
        result.append(
            {
                **r,
                "owner_import_status": decision,
                "owner_authority": authority,
                "owner_interpreted_action": action,
                "owner_interpreted_states": state,
                "visual_audit_complete": False,
                "needs_owner_review_now": False,
                "note": (
                    "Approval imported; duplicate/source/geometry audit remains in progress. "
                    "No release enrollment."
                ),
            }
        )
    dump(HERE / "consolidated-ledger.json", result)
    summary = dict(Counter(r["owner_import_status"] for r in result))
    dump(HERE / "owner-import-summary.json", summary)
    print(summary)


if __name__ == "__main__":
    main()
