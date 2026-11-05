import math
import re

# Keep this list and the one in base.html (bvStrength) in sync.
COMMON_PASSWORDS = {
    "password", "password1", "password123", "12345678", "123456789",
    "1234567890", "qwertyuiop", "qwerty123", "iloveyou", "admin123",
    "letmein123", "welcome123",
}


def password_strength(password):
    """Return "weak", "medium" or "strong".

    Same rules as the strength meter in the browser (bvStrength in
    base.html), so the dashboard summary agrees with what users saw
    while typing.
    """
    pool = 0
    if re.search(r"[a-z]", password):
        pool += 26
    if re.search(r"[A-Z]", password):
        pool += 26
    if re.search(r"[0-9]", password):
        pool += 10
    if re.search(r"[^A-Za-z0-9]", password):
        pool += 32

    bits = len(password) * math.log2(pool) if pool else 0
    if len(set(password)) < len(password) / 2:
        bits *= 0.5  # lots of repeated characters

    if len(password) < 8 or bits < 45 or password.lower() in COMMON_PASSWORDS:
        return "weak"
    if bits < 70 or len(password) < 12:
        return "medium"
    return "strong"
