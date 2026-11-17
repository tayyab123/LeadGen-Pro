def remove_duplicates(leads):
    seen, output = set(), []
    for lead in leads:
        key = lead.get("place_id") or (
            (lead.get("name") or "").strip().lower(),
            (lead.get("address") or "").strip().lower()
        )
        if key not in seen:
            seen.add(key)
            output.append(lead)
    return output
