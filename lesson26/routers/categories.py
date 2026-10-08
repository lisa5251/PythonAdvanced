from fastapi import APIRouter, HTTPException
from models.category import CategoryCreate
from database import get_connection

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get("/")
def get_categories():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    connection.close()

    return [dict(category) for category in categories]


@router.get("/{category_id}")
def get_category(category_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM categories WHERE id = ?",
        (category_id,)
    )

    category = cursor.fetchone()
    connection.close()

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return dict(category)


@router.post("/")
def create_category(category: CategoryCreate):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO categories (name) VALUES (?)",
            (category.name,)
        )

        connection.commit()

        category_id = cursor.lastrowid

    except Exception:
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    connection.close()

    return {
        "id": category_id,
        "name": category.name
    }


@router.put("/{category_id}")
def update_category(
    category_id: int,
    category: CategoryCreate
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM categories WHERE id = ?",
        (category_id,)
    )

    existing = cursor.fetchone()

    if existing is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    cursor.execute(
        """
        UPDATE categories
        SET name = ?
        WHERE id = ?
        """,
        (category.name, category_id)
    )

    connection.commit()
    connection.close()

    return {
        "id": category_id,
        "name": category.name
    }


@router.delete("/{category_id}")
def delete_category(category_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM categories WHERE id = ?",
        (category_id,)
    )

    category = cursor.fetchone()

    if category is None:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    cursor.execute(
        "DELETE FROM categories WHERE id = ?",
        (category_id,)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Category deleted successfully"
    }