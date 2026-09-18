import os
import re
import json
from pathlib import Path
from utils import GraphDB
from .ontology import ReviewsOntology
from typing import Dict, Any

type conf = Dict[str,Any]

parent_dir = Path(__file__).resolve().parent
reviews_path = parent_dir / "data" / "reviews_data"
ontology = parent_dir / "conf"/ "ontology.conf"
import json
import re


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
        else:
            # It's a standard Cypher query string or plain parameter string
            config[key] = value

    return config


URI = os.environ["URI"]
username = os.environ["USERNAME"]
password = os.environ["PASSWORD"]
default_db = os.environ["DEFAULT_DB"]
config = load_conf(ontology)


driver = GraphDB(URI=URI,
                 AUTH=(username,password),
                 default_db=default_db
                 )

reviews_loader = ReviewsOntology(ontology=config["reviews_ontology"],
                                 datapath=reviews_path,
                                 driver=driver,
                                 embedder_model=config['embedder_model'],
                                 embedd_query=config['reviews_embed_query'],
                                 vector_index_query=config['reviews_vector_index']
                                 )
reviews_loader()
