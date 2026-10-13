import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Online Recipe Book",
    page_icon="🍲",
    layout="wide"
)


# LOGIN AND REGISTRATION

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


if not st.session_state.logged_in:
    st.title("🍲 Online Recipe Book")
    st.write("Welcome! Log in or create an account.")

    login_tab, register_tab = st.tabs(
        ["Log In", "Register"]
    )

    # LOGIN
    with login_tab:
        with st.form("login_form"):
            login_username = st.text_input("Username")

            login_password = st.text_input(
                "Password",
                type="password"
            )

            login_button = st.form_submit_button("Log In")

            if login_button:
                try:
                    response = requests.post(
                        f"{API_URL}/auth/login",
                        json={
                            "username": login_username,
                            "password": login_password
                        },
                        timeout=5
                    )

                    if response.ok:
                        user_data = response.json()

                        st.session_state.logged_in = True
                        st.session_state.username = user_data["username"]

                        st.rerun()
                    else:
                        st.error(
                            response.json().get(
                                "detail",
                                "Login failed"
                            )
                        )

                except requests.RequestException:
                    st.error("Could not connect to the API.")

    # REGISTRATION
    with register_tab:
        with st.form("register_form"):
            register_username = st.text_input(
                "Choose a username"
            )

            register_password = st.text_input(
                "Choose a password (at least 8 characters)",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            register_button = st.form_submit_button(
                "Create Account"
            )

            if register_button:
                if not register_username.strip():
                    st.error("Please enter a username.")

                elif len(register_password) < 8:
                    st.error(
                        "Password must contain at least 8 characters."
                    )

                elif register_password != confirm_password:
                    st.error("The passwords do not match.")

                else:
                    try:
                        response = requests.post(
                            f"{API_URL}/auth/register",
                            json={
                                "username": register_username.strip(),
                                "password": register_password
                            },
                            timeout=5
                        )

                        if response.ok:
                            st.success(
                                "Account created successfully! "
                                "You can now log in."
                            )
                        else:
                            st.error(
                                response.json().get(
                                    "detail",
                                    "Registration failed"
                                )
                            )

                    except requests.RequestException:
                        st.error("Could not connect to the API.")

    st.stop()


# MAIN APPLICATION

def get_data(endpoint):
    try:
        response = requests.get(
            f"{API_URL}/{endpoint}/",
            timeout=5
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException:
        st.error(
            "Could not connect to the API. "
            "Make sure python main.py is running."
        )
        return None


st.title("🍲 Online Recipe Book")
st.write(f"Welcome, {st.session_state.username}!")

if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Manage Recipes", "Manage Categories"]
)


# DASHBOARD

if page == "Dashboard":
    st.header("Recipe Dashboard")

    recipes = get_data("recipes")

    if recipes is not None:
        st.metric("Total Recipes", len(recipes))

        if recipes:
            for recipe in recipes:
                with st.container(border=True):
                    st.subheader(recipe["name"])

                    st.image(
                        "https://placehold.co/600x300?text=Recipe",
                        width=300
                    )

                    st.write(
                        f"Ingredients: {recipe['ingredients']}"
                    )
                    st.write(
                        f"Cooking time: {recipe['cooking_time']} minutes"
                    )
                    st.write(
                        f"Difficulty: {recipe['difficulty']}"
                    )
                    st.write(
                        f"Instructions: {recipe['instructions']}"
                    )
                    st.write(
                        f"Category: {recipe.get('category_name') or 'None'}"
                    )

        else:
            st.info("No recipes yet. Add your first recipe!")


# MANAGE RECIPES

elif page == "Manage Recipes":
    st.header("Manage Recipes")

    recipes = get_data("recipes")
    categories = get_data("categories")

    if recipes is not None:
        st.subheader("All Recipes")

        if recipes:
            st.dataframe(
                recipes,
                use_container_width=True,
                hide_index=True
            )

            recipe_options = {
                f"{recipe['name']} (ID: {recipe['id']})": recipe
                for recipe in recipes
            }

            selected_name = st.selectbox(
                "Select a recipe to edit or delete",
                list(recipe_options.keys())
            )

            selected_recipe = recipe_options[selected_name]

            st.subheader("Edit Recipe")

            if categories is not None:
                with st.form("edit_recipe_form"):
                    name = st.text_input(
                        "Recipe name",
                        value=selected_recipe["name"],
                        key="edit_name"
                    )

                    ingredients = st.text_area(
                        "Ingredients",
                        value=selected_recipe["ingredients"],
                        key="edit_ingredients"
                    )

                    instructions = st.text_area(
                        "Instructions",
                        value=selected_recipe["instructions"],
                        key="edit_instructions"
                    )

                    cooking_time = st.number_input(
                        "Cooking time (minutes)",
                        min_value=1,
                        value=max(
                            1,
                            selected_recipe["cooking_time"]
                        ),
                        step=1,
                        key="edit_cooking_time"
                    )

                    difficulties = ["Easy", "Medium", "Hard"]
                    current_difficulty = selected_recipe["difficulty"]

                    difficulty = st.selectbox(
                        "Difficulty",
                        difficulties,
                        index=(
                            difficulties.index(current_difficulty)
                            if current_difficulty in difficulties
                            else 0
                        ),
                        key="edit_difficulty"
                    )

                    category_options = {"No category": None}

                    for category in categories:
                        category_options[category["name"]] = category["id"]

                    current_category = selected_recipe.get("category_id")

                    selected_category = next(
                        (
                            category_name
                            for category_name, category_id
                            in category_options.items()
                            if category_id == current_category
                        ),
                        "No category"
                    )

                    category_name = st.selectbox(
                        "Category",
                        list(category_options.keys()),
                        index=list(category_options.keys()).index(
                            selected_category
                        ),
                        key="edit_category"
                    )

                    update_clicked = st.form_submit_button(
                        "Save Changes"
                    )

                    if update_clicked:
                        if (
                            not name.strip()
                            or not ingredients.strip()
                            or not instructions.strip()
                        ):
                            st.error("Please fill in all recipe fields.")

                        else:
                            updated_recipe = {
                                "name": name.strip(),
                                "ingredients": ingredients.strip(),
                                "instructions": instructions.strip(),
                                "cooking_time": int(cooking_time),
                                "difficulty": difficulty,
                                "category_id": category_options[category_name]
                            }

                            try:
                                response = requests.put(
                                    f"{API_URL}/recipes/{selected_recipe['id']}",
                                    json=updated_recipe,
                                    timeout=5
                                )

                                if response.ok:
                                    st.success("Recipe updated successfully!")
                                    st.rerun()
                                else:
                                    st.error(response.text)

                            except requests.RequestException:
                                st.error("Could not connect to the API.")

            st.subheader("Delete Recipe")

            if st.button(
                "Delete Selected Recipe",
                key="delete_recipe"
            ):
                try:
                    response = requests.delete(
                        f"{API_URL}/recipes/{selected_recipe['id']}",
                        timeout=5
                    )

                    if response.ok:
                        st.success("Recipe deleted successfully!")
                        st.rerun()
                    else:
                        st.error(response.text)

                except requests.RequestException:
                    st.error("Could not connect to the API.")

        else:
            st.info("No recipes have been added yet.")

    st.divider()
    st.subheader("Add a Recipe")

    if categories is not None:
        with st.form("add_recipe_form"):
            name = st.text_input("Recipe name")
            ingredients = st.text_area("Ingredients")
            instructions = st.text_area("Instructions")

            cooking_time = st.number_input(
                "Cooking time (minutes)",
                min_value=1,
                step=1
            )

            difficulty = st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard"]
            )

            category_options = {"No category": None}

            for category in categories:
                category_options[category["name"]] = category["id"]

            category_name = st.selectbox(
                "Category",
                list(category_options.keys())
            )

            submitted = st.form_submit_button("Add Recipe")

            if submitted:
                if (
                    not name.strip()
                    or not ingredients.strip()
                    or not instructions.strip()
                ):
                    st.error("Please fill in all recipe fields.")

                else:
                    recipe_data = {
                        "name": name.strip(),
                        "ingredients": ingredients.strip(),
                        "instructions": instructions.strip(),
                        "cooking_time": int(cooking_time),
                        "difficulty": difficulty,
                        "category_id": category_options[category_name]
                    }

                    try:
                        response = requests.post(
                            f"{API_URL}/recipes/",
                            json=recipe_data,
                            timeout=5
                        )

                        if response.ok:
                            st.success("Recipe added successfully!")
                            st.rerun()
                        else:
                            st.error(response.text)

                    except requests.RequestException:
                        st.error("Could not connect to the API.")


# MANAGE CATEGORIES

elif page == "Manage Categories":
    st.header("Manage Categories")

    categories = get_data("categories")

    if categories is not None:
        if categories:
            st.dataframe(
                categories,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No categories have been added yet.")

        st.subheader("Add a Category")

        with st.form("add_category_form"):
            category_name = st.text_input("Category name")

            submitted = st.form_submit_button("Add Category")

            if submitted:
                if not category_name.strip():
                    st.error("Please enter a category name.")

                else:
                    try:
                        response = requests.post(
                            f"{API_URL}/categories/",
                            json={
                                "name": category_name.strip()
                            },
                            timeout=5
                        )

                        if response.ok:
                            st.success("Category added successfully!")
                            st.rerun()
                        else:
                            st.error(response.text)

                    except requests.RequestException:
                        st.error("Could not connect to the API.")