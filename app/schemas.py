from typing import Optional, List

from pydantic import BaseModel

class APIPARAMTERS(BaseModel):
    motion : List[str]
    image : str
    image_url : List[str]