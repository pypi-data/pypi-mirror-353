from readyapi import ReadyAPI

app = ReadyAPI()


@app.get("/")

def read_root():

    return {"Hello": "World"}

