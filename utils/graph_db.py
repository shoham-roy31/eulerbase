import os
from neo4j import GraphDatabase
from typing import List, Optional, Dict, Any, Tuple
type Username = str
type Password = str
type Auth = Tuple[Username,Password]
DEFAULT_DB = 'neo4j'

class GraphDB:
    def __init__(self,
                 URI:str,
                 AUTH:Auth,
                 default_db: Optional[str] = DEFAULT_DB
                 ) -> None:
        self.driver = GraphDatabase.driver(
            URI,
            auth = AUTH
        )
        self.default_db = default_db
        try:
            self.driver.verify_connectivity()
        except Exception as e:
            raise e

    def query_hook(self,
              query:str,
              parameters:Optional[Dict[str,Any]] = {},
              db_name:Optional[str] = None,
              **kwargs
              ) -> List[Any]:
        db_name = db_name if db_name else self.default_db
        with self.driver.session(database = db_name) as session:
            result = session.run(query,parameters,**kwargs)
            return [_ for _ in result]

    def close(self) -> None:
        self.driver.close()
        print('-'*5+"Driver Closed"+5*"-")

if __name__ == "__main__":
    URI = os.environ["URI"]
    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]
    db_name = os.environ["DEFAULT_DB"]
    db = GraphDB(URI,AUTH=(username,password))
    while True:
        print("Type q to quit")
        text = str(input("Query: "))
        if text.lower() == 'q':
            db.close()
            break
        results = db.query_hook(
            query=text,
            db_name = db_name
        )
        print(results)
