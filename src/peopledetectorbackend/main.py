from fastapi import FastAPI

app = FastAPI()

current_state = {
    "count": 0,
    "image_b64": ""
}

def start():
    import uvicorn
    uvicorn.run("peopledetectorbackend.main:app", host="0.0.0.0", port=8001, reload=True)
if __name__ == "__main__":
    start()