from fastapi import FastAPI


app = FastAPI()

@app.get("/")
def root():
    return {"message":"Hello, World!"}

@app.get("/items/")
def read_items():
    return  {"items":["kursi1","kursi2","kursi3"]}

@app.get("/items/{items_id}")
def read_items(item_id:int):
    return {"item_id":item_id}

@app.get("/users/{user_id}")
def read_items(user_id:int):
    return {"user_id":user_id, "name": "Eglandini"}

@app.put("/items/{item_id}")
def update_item(item_id:int,name:str,price:float):
    return {"item_id":item_id, "item_name":name,"item_price":price}

@app.delete("/user/{user_id}")
def delete_item(item_id:int):
    return {"message":"u fshie me sukses"}