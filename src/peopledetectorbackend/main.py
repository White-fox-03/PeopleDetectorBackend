from fastapi import FastAPI

app = FastAPI()

current_state = {
    "count": 0,
    "image_b64": ""
}

def start():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start()