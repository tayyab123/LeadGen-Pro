def clean_text(value, max_length=180):
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_length]
