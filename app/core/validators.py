"""Validation utilities: CPF, CEP, name normalization, etc."""

import re
import unicodedata


def validate_cpf(cpf: str) -> bool:
    """Validate CPF check digits. Returns True if valid."""
    digits = re.sub(r"\D", "", cpf)
    if len(digits) != 11:
        return False
    if digits == digits[0] * 11:
        return False
    # First check digit
    total = sum(int(digits[i]) * (10 - i) for i in range(9))
    rest = total % 11
    d1 = 0 if rest < 2 else 11 - rest
    if int(digits[9]) != d1:
        return False
    # Second check digit
    total = sum(int(digits[i]) * (11 - i) for i in range(10))
    rest = total % 11
    d2 = 0 if rest < 2 else 11 - rest
    if int(digits[10]) != d2:
        return False
    return True


def normalize_cep(cep: str) -> str:
    """Normalize CEP to NNNNN-NNN format."""
    digits = re.sub(r"\D", "", cep)
    if len(digits) == 8:
        return f"{digits[:5]}-{digits[5:]}"
    return cep.strip()


def normalize_name(name: str) -> str:
    """Apply Title Case preserving lowercase prepositions."""
    prepositions = {"da", "de", "do", "das", "dos", "e"}
    words = name.strip().split()
    result = []
    for i, word in enumerate(words):
        lower = word.lower()
        if i > 0 and lower in prepositions:
            result.append(lower)
        else:
            result.append(word.capitalize())
    return " ".join(result)


def normalize_filename(name: str) -> str:
    """Normalize a name for use in filenames: remove accents, replace spaces with _."""
    # Remove accents
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Replace spaces with underscores
    ascii_text = ascii_text.replace(" ", "_")
    # Remove special characters (keep letters, digits, underscores)
    ascii_text = re.sub(r"[^a-zA-Z0-9_]", "", ascii_text)
    return ascii_text


def strip_fields(data: dict[str, str]) -> dict[str, str]:
    """Strip whitespace from all string values in a dict."""
    return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}
