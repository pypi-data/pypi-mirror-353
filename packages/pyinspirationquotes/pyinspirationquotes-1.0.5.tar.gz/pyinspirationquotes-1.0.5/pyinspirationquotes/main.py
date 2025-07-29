import random
import os
import errno

def load_quotes():
    base_dir = os.path.dirname(__file__)
    quotes_file = os.path.join(base_dir, "quotes.txt")

    with open(quotes_file, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]
    return quotes

def load_used_quotes():
    base_dir = os.path.dirname(__file__)
    used_file = os.path.join(base_dir, "used_quotes.txt")
    if not os.path.exists(used_file):
        return set()
    with open(used_file, "r", encoding="utf-8") as f:
        used = set(line.strip() for line in f if line.strip())
    return used

def save_used_quote(quote):
    base_dir = os.path.dirname(__file__)
    used_file = os.path.join(base_dir, "used_quotes.txt")
    used = load_used_quotes()
    if quote not in used:
        with open(used_file, "a", encoding="utf-8") as f:
            f.write(quote + "\n")


def get_inspiration():
    quotes = load_quotes()
    used = load_used_quotes()

    available_quotes = [q for q in quotes if q not in used]

    if not available_quotes:
        base_dir = os.path.dirname(__file__)
        used_file = os.path.join(base_dir, "used_quotes.txt")
        try:
            os.remove(used_file)
        except FileNotFoundError:
            pass  # If file doesn't exist, that's okay
        available_quotes = quotes  # Reset all quotes

    quote = random.choice(available_quotes)
    save_used_quote(quote)
    return quote


