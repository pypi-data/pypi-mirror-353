import os 
import re 
import json 
from typing import Union, Dict 
import copy 

class CJson:
    def __init__(self, file: str = ""):
        self.__file = file 
        self.__data = dict() 
    
    def set_file(self, file):
        self.__file = file 

    def load_dic(self, dic):
        self.__data = copy.deepcopy(dic) 
    
    def dump_dic(self):
        return copy.deepcopy(self.__data)
    
    def update_data(self, dic):
        self.__data.update(dic)
    
    def load(self, file=None): 
        file = self.__file if file is None else file 
        
        data = dict() 
        try:
            with open(file, "r") as f:
                data = json.load(f)
        except:
            pass 
        self.__data = data 

    def dump(self, file=None):
        if file is None:
            file = self.__file 
        
        with open(file, "w") as f:
            json.dump(self.__data, f, indent=2, ensure_ascii=False) 
    

    
    def get(self, key, dval=None):
        keys = re.split("[/\.]+", key)
        if len(keys) < 1:
            return dval 
        d = self.__data 
        for k in keys[:-1]:
            d = d.get(k, None) 
            if isinstance(d, dict):
                continue 
            else:
                return dval 
        return d.get(keys[-1], dval)  

    
    def set(self, key, val=None):
        keys = re.split("[/\.]+", key)
        if len(keys) < 1:
            return 
        
        d = self.__data 
        for k in keys[:-1]:
            d[k] = d.get(k, dict())
            d = d[k]
        d[keys[-1]] = d.get(keys[-1], dict())
        d[keys[-1]] = val 
        return 

    # @staticmethod 
    # def getd(d, key, dval) -> Union[Dict, None]:
    #     """ """

    def dumps(self, indent=2):
        return json.dumps(self.__data, indent=indent, ensure_ascii=False)

    def print(self):
        print(json.dumps(self.__data, indent=2, ensure_ascii=False))

    def get_str(self):
        return json.dumps(self.__data, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    cjson = CJson() 
    a = cjson.get("a.b/c", 123)
    print(f"a: {a}")

    cjson.set("a.b", 123)
    cjson.set("a/c/c", 234)

    cjson.print()

    cjson.dump("build/a.json")

    cjson.load("build/a.json")

    cjson.print()
