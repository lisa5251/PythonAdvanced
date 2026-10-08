from fastapi import FastAPI

from database import create_tables
from routers.categories import router as categories_router
from routers.recipes import router as recipes_router


create_tables()

app = FastAPI(
    title="Online Recipe Book",
    description="API for managing recipes and categories",
    version="1.0.0"
)


app.include_router(categories_router)
app.include_router(recipes_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to the Online Recipe Book API!"
    }
