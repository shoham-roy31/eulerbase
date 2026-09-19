import os
from .graph_db import GraphDB
from neo4j_graphrag.llm import OllamaLLM
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.embeddings import OllamaEmbeddings
from neo4j_graphrag.message_history import InMemoryMessageHistory


class graphRAG:
    def __init__(self,
                 llm:str,
                 embedding_model:str,
                 index_name:str,
                 driver:GraphDB
                 ) -> None:
        self.llm = OllamaLLM(model_name = llm)
        self.driver = driver
        self.index_name = index_name
        self.embedding_model = OllamaEmbeddings(model = embedding_model)
        self.retriver = VectorRetriever(driver = self.driver.driver,
                                        index_name = self.index_name,
                                        embedder = self.embedding_model
                                        )
        self.history = InMemoryMessageHistory()
        self.rag = GraphRAG(retriever= self.retriver,
                            llm = self.llm
                            )
    def sreach(self,
               query_text:str
               ) -> str:
        
        res = self.rag.search(query_text = query_text,
                              message_history = self.history,
                              return_context = True).answer
        self.history.add_message({"role":"user","content":query_text})
        self.history.add_message({"role":"assistant","content": res})
        return res
    
if __name__ == "__main__":
    URI = os.environ["URI"]
    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]
    default_db = os.environ["DEFAULT_DB"]
    db = GraphDB(URI = URI,
                       AUTH = (username,password)
                       )
    index_name = "dataProductIndex"
    llm = "gemma4:31b-cloud"
    embedding_model = "qwen3-embedding:0.6b"
    kB = graphRAG(
        llm = llm,
        embedding_model = embedding_model,
        index_name = index_name,
        driver = db
    )
    while True:
        print("Enter q to Quit")
        val = input("Query: ")
        if val.lower() == "q": break
        res = kB.sreach(query_text = val)    
        print(f"Answer: {res}")