def generateFocusKey(index: int, key: str) -> str:
    return f"{key}_{index}"


def extractIndexFromKey(key_string: str) -> int:
    try:
        return int(key_string.rsplit("_", 1)[-1])
    except (ValueError, IndexError):
        raise ValueError(f"Invalid key format: '{key_string}'")
