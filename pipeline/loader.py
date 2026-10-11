import os
import ast
from pathlib import Path
from utils import (
    GraphDB,
    load_conf
)
from .ontology import (
    ReviewsOntology,
    DataProductOntology
)

parent_dir = Path(__file__).resolve().parent
reviews_path = parent_dir / "data" / "reviews_data"
data_product_path = parent_dir / "data" / "data_product"
ontology = parent_dir / "conf"/ "ontology.conf"
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
# reviews_loader()

data_product_loader = DataProductOntology(
    ontology=config["data_products_ontology"],
    datapath=data_product_path,
    driver = driver,
    embedder_model = config["embedder_model"],
    embedd_query = config["data_products_embed_query"],
    vector_index_query = config["data_products_index"],
)

data_product_loader(header = 0, names= ast.literal_eval(config["data_products_columns"]))
