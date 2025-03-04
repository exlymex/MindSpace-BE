from typing import List, Optional
from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int

    class Config:
        orm_mode = True

class MaterialBase(BaseModel):
    title: str
    content: str
    type: str
    image_url: Optional[str] = None

class MaterialCreate(MaterialBase):
    category_ids: List[int]

class MaterialOut(MaterialBase):
    id: int
    categories: List[CategoryOut]

    class Config:
                from_attributes = True