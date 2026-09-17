from fastapi import FastAPI

app =FastAPI()

@app.get("/")

def root():
    return {
  "name":"Alice",
  "age":35,
  "address":{
    "street":"pashko vasa",
    "city":"prishtine",
    "country":"Kosove"
  },
  "contacts":[
    {
      "type":"email",
      "value":"donjeta@gmail.com"
    },
    {
      "type": "phone",
      "value": "55-123-4567"
    }
  ]
}

@app.get("/users/")
def read_root():
  return {
    "message":"hello there"
  }