import os
from .load_config import load_conf
from langchain_neo4j import Neo4jGraph
from langchain_ollama import ChatOllama
from langchain_neo4j import GraphCypherQAChain

graph = Neo4jGraph(
    url = os.environ["URI"],
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"],
    database = os.environ["DEFAULT_DB"]
)

llm = ChatOllama(
    model = "gemma4:31b-cloud",
    temperature = 0.5
)

chain = GraphCypherQAChain.from_llm(
    llm = llm,
    graph = graph,
    verbose = True,
    allow_dangerous_requests = True
)

while True:
    print("Enter q to Quit")
    query = str(input("Query: "))
    if query.lower() == 'q':break
    response = chain.invoke({
        "query": query
    })
    print(f"Answer: {response["result"]}")
    

