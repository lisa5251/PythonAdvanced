from pydantic import BaseModel


class RecipeCreate(BaseModel):
    name: str
    ingredients: str
    instructions: str
    cooking_time: int
    difficulty: str
    category_id: int | None = None


class Recipe(RecipeCreate):
    id: int