import re


def slugify(name: str) -> str:
    snake_case = (name[0] + re.sub(r"([A-Z])", r"-\1", name[1:])).lower()
    no_underscores_spaces = re.sub(r"[-_ ]+", "-", snake_case)
    no_double_dashes = re.sub(r"--+", "-", no_underscores_spaces)
    no_leading_trailing_dashes = re.sub(r"^-|-$", "", no_double_dashes)
    no_invalid_characters = re.sub(r"[^a-z0-9-]", "", no_leading_trailing_dashes)
    return no_invalid_characters
