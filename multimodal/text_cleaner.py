import re


def clean_text(text):

    text = text.lower()

    # Remove garbage characters
    text = re.sub(r"[^a-zA-Z0-9\s:/.-]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    # Remove tiny meaningless words
    words = []

    for word in text.split():

        if len(word) > 2 or word.isdigit():
            words.append(word)

    cleaned = " ".join(words)

    return cleaned