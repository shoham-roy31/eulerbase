from utils import GraphDB

def assert_params(kwargs):
    if kwargs.get("ontology"):
        try:
            assert isinstance(kwargs["ontology"],str) == True
        except TypeError as e:
            raise f"TypeError: ontology should be type str got {type(kwargs["ontology"])}"
    if kwargs.get("datapath"):
        try:
            assert isinstance(kwargs["datapath"],str) == True
        except TypeError as e:
            raise f"TypeError: datapath should be type str got {type(kwargs["datapath"])}"
    if kwargs.get("driver"):
        try:
            assert isinstance(kwargs["driver"],GraphDB) == True
        except TypeError as e:
            raise f"TypeError: driver should be instance of GraphDB got {type(kwargs["driver"])}"


class BaseOntology:
    def __init__(self,
                 ontology:str,
                 datapath:str,
                 driver: GraphDB
                 ) -> None:
        params = locals()
        #assert_params(params)
        self.ontology = ontology
        self.datapath = datapath
        self.driver = driver

    def extract(self) -> None:
        raise NotImplementedError("Method needs to be implmented")
    
    def load(self) -> None:
        raise NotImplementedError("Method needs to be implemented")

    def transformation(self) -> None:
        pass

    def __call__(self) -> None:
        raise NotImplementedError("Method needs to be implemented")