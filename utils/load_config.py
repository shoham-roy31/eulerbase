import re
import json
def load_conf(path: str) -> dict:
    with open(path, "r") as file:
        content = file.read()

    config = dict()

    # Regex breaks the file into pairs: (Key Name) = (Everything until the next key or end of file)
    # ^([a-zA-Z0-9_]+) matches the variable name at the start of a line
    # \s*=\s*(.*?) matches the value across lines lazily
    # (?=^[a-zA-Z0-9_]+\s*=|\Z) stops matching when a new key starts or at the end of the file (\Z)
    pattern = r"^([a-zA-Z0-9_]+)\s*=\s*(.*?)(?=^[a-zA-Z0-9_]+\s*=|\Z)"
    matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)

    for key, value in matches:
        value = value.strip()  # Clean up trailing spaces/newlines

        # Check if the text block looks like a JSON dictionary or list
        if value.startswith(("{", "[")):
            try:
                config[key] = json.loads(value)
            except json.JSONDecodeError:
                # If JSON parsing fails, fall back to leaving it as a raw string
                config[key] = value
        elif key.startswith("#"): continue
        else:
            # It's a standard Cypher query string or plain parameter string
            config[key] = value

    return config