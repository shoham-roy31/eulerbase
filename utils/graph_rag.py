from .graph_db import GraphDatabase
from neo4j_graphrag.embeddings import OllamaEmbeddings
from neo4j_graphrag.llm import OllamaLLM
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.generation import GraphRAG

class graphRAG:
    def __init__(self,
                 llm:str,
                 embedding_model:str,
                 index_name:str,
                 driver:GraphDatabase
                 ) -> None:
        self.llm = OllamaLLM(model_name = llm)
        self.driver = driver
        self.index_name = index_name
        self.embedding_model = OllamaEmbeddings(model = embedding_model)
        self.retriver = VectorRetriever(driver = self.driver,
                                        index_name = self.index_name,
                                        embedder = self.embedding_model
                                        )
        self.rag = GraphRAG(retriever= self.retriver,
                            llm = self.llm
                            )
    def sreach(self,
               query_text:str
               ) -> str:
        return self.rag.search(query_text = query_text).answer
