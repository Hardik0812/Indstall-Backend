import secrets
import string


def generate_strong_password(length: int = 12) -> str:
    """
    Generates a strong password with letters, digits, and punctuation,
    ensuring at least one char from each category.
    """
    if length < 8:
        length = 8

    alphabet_upper = string.ascii_uppercase
    alphabet_lower = string.ascii_lowercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{}"  # avoid ambiguous/unsafe punctuation

    # Ensure minimum complexity
    must_have = [
        secrets.choice(alphabet_upper),
        secrets.choice(alphabet_lower),
        secrets.choice(digits),
        secrets.choice(symbols),
    ]

    pool = alphabet_upper + alphabet_lower + digits + symbols
    remaining = [secrets.choice(pool) for _ in range(length - len(must_have))]
    chars = must_have + remaining
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)
