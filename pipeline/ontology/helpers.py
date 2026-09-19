import pandas as pd

CSV = 'csv'
XLSX = 'xlsx'

def assert_type(var,datatype):
    try:
        assert isinstance(var,datatype) == True
    except TypeError as e:
        raise f"TypeError: {var} should be type of {datatype} but got {type(var)}"

def assert_params(kwargs):
    if kwargs.get("path"):
        assert_type(kwargs["path"],str)
    if kwargs.get("format"):
        assert_type(kwargs["format"],str)

def get_df(path:str,
           format:str,
           **kwargs
           ) -> pd.DataFrame:
    if format == CSV:
        return pd.read_csv(path, **kwargs)    
    if format == XLSX:
        return pd.read_excel(path,**kwargs)