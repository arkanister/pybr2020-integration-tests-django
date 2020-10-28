import itertools
import random
import string


def generate_strong_password():
    """
    Generate a password that matches with policies.
    """
    allowed_chars = [string.ascii_lowercase, string.ascii_uppercase, string.digits, string.punctuation]
    chars = list(itertools.chain(*[random.sample(chars, 2) for chars in allowed_chars]))
    return ''.join(random.sample(chars, len(chars)))
