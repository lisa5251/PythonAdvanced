from fastapi import APIRouter, HTTPException
from models.recipe import RecipeCreate
from database import get_connection

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)


@router.get("/")
def get_recipes():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            recipes.id,
            recipes.name,
            recipes.ingredients,
            recipes.instructions,
            recipes.cooking_time,
            recipes.difficulty,
            recipes.category_id,
            categories.name AS category_name
        FROM recipes
        LEFT JOIN categories
        ON recipes.category_id = categories.id
    """)

    recipes = cursor.fetchall()

    connection.close()

    return [dict(recipe) for recipe in recipes]


@router.get("/{recipe_id}")
def get_recipe(recipe_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            recipes.id,
            recipes.name,
            recipes.ingredients,
            recipes.instructions,
            recipes.cooking_time,
            recipes.difficulty,
            recipes.category_id,
            categories.name AS category_name
        FROM recipes
        LEFT JOIN categories
        ON recipes.category_id = categories.id
        WHERE recipes.id = ?
    """, (recipe_id,))

    recipe = cursor.fetchone()

    connection.close()

    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found"
        )

    return dict(recipe)


@router.post("/")
def create_recipe(recipe: RecipeCreate):
    connection = get_connection()
    cursor = connection.cursor()

    # Check category
    if recipe.category_id is not None:
        cursor.execute(
            "SELECT * FROM categories WHERE id = ?",
            (recipe.category_id,)
        )

        category = cursor.fetchone()

        if category is None:
            connection.close()
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

    cursor.execute("""
        INSERT INTO recipes (
            name,
            ingredients,
            instructions,
            cooking_time,
            difficulty,
            category_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        recipe.name,
        recipe.ingredients,
        recipe.instructions,
        recipe.cooking_time,
        recipe.difficulty,
        recipe.category_id
    ))

    connection.commit()

    recipe_id = cursor.lastrowid

    connection.close()

    return {
        "id": recipe_id,
        **recipe.model_dump()
    }


@router.put("/{recipe_id}")
def update_recipe(
    recipe_id: int,
    recipe: RecipeCreate
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    )

    existing = cursor.fetchone()

    if existing is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Recipe not found"
        )

    cursor.execute("""
        UPDATE recipes
        SET
            name = ?,
            ingredients = ?,
            instructions = ?,
            cooking_time = ?,
            difficulty = ?,
            category_id = ?
        WHERE id = ?
    """, (
        recipe.name,
        recipe.ingredients,
        recipe.instructions,
        recipe.cooking_time,
        recipe.difficulty,
        recipe.category_id,
        recipe_id
    ))

    connection.commit()
    connection.close()

    return {
        "id": recipe_id,
        **recipe.model_dump()
    }


@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    )

    recipe = cursor.fetchone()

    if recipe is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Recipe not found"
        )

    cursor.execute(
        "DELETE FROM recipes WHERE id = ?",
        (recipe_id,)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Recipe deleted successfully"
    }