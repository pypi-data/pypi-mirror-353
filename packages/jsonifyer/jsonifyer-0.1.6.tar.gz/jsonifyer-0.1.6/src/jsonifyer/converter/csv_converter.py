import json
import pandas as pd
import os

def convert_file_to_json(input_file, fields=None, delimiter=",", skiprows=0):
    try:
        
        df = pd.read_csv(input_file, delimiter=delimiter, skiprows=skiprows)
        
        if fields:
            df = df[fields]
        
        df.dropna(axis=1, how="all", inplace=True)
        df.dropna(how="all", inplace=True)
        df = df.where(pd.notna(df), None)
        
        data = df.to_dict(orient="records")
        
        return data # Return the list of dictionaries
    except Exception as e:
        raise Exception(f"Error converting {input_file}: {str(e)}")