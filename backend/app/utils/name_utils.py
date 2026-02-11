def split_fullname(fullname: str):
    if not fullname:
        return "Inconnu", ""

    parts = fullname.strip().split()
    if len(parts) >= 2:
        return parts[0], " ".join(parts[1:])

    return fullname, ""
