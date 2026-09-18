import json
from tqdm import tqdm
from typing import Dict
from utils import GraphDB
from .helpers import get_df
from .base_ontology import BaseOntology
from neo4j_graphrag.embeddings import OllamaEmbeddings

FORMATS = ["csv","xls"]
# NODE_NAME = "Reviews"
# CREATE_PREFIX = "MERGE(n:{NODE_NAME} {"
# CREATE_POSTFIX = " })"
# _GET_TEXT = lambda record: ','.join({f'{k}:${str(k)}' for k in record.keys()})

class ReviewsOntology(BaseOntology):
    def __init__(self,
                 ontology:str,
                 datapath:str,
                 driver: GraphDB,
                 embedder_model:str,
                 embedd_query:Dict[str,str],
                 vector_index_query:str
                 ) -> None:
        super().__init__(
            ontology=ontology,
            datapath = datapath,
            driver = driver
        )
        self.embedder = embedder_model
        print(embedd_query)
        self.embedd_query = embedd_query
        self.vector_index_query = vector_index_query
    def extract(self) -> None:
        self.files = set()
        for file in self.datapath.iterdir():
            format = file.name.split('.')[-1]
            if format in FORMATS and file.is_file():
                self.files.add(file)

    def load(self) -> None:
        for file in tqdm(list(self.files)):
            format = file.name.split('.')[-1]
            df = get_df(path = file,
                        format = format
                        )
            df = df.iloc[:500]
            df = df.fillna("")
            
            self.driver.query_hook(self.ontology,
                                   rows=df.to_dict("records")
                                   )
        embedder = OllamaEmbeddings(model=self.embedder)
        print("-"*5+"Loading Embeddings"+5*"-")
        for k,query in tqdm(self.embedd_query.items()):
            # query = json.loads(query)
            if query.get('embed_query'):
                records = self.driver.query_hook(query['embed_query'])
                for r in tqdm(records):
                    vec = embedder.embed_query(r['text'])
                    if query.get('add_embed_query'):
                        self.driver.query_hook(query['add_embed_query'],
                                               id=r['id'],
                                               vec = vec
                                               )
                    else: print(f"{k} doesn't has 'add_embed_query' key")
            else:print(f"{k} doesn't has 'embed_query'")
        self.driver.query_hook(self.vector_index_query)

    def __call__(self) -> None:
        self.extract()
        self.load()
        self.driver.close()
