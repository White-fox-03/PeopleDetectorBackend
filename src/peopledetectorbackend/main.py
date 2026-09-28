from fastapi import FastAPI
from peopledetectorbackend.router.router import router

app = FastAPI()

current_state = {
    "count": 0,
    "image_b64": ""
}

app.include_router(router)

def start():
    import uvicorn
    uvicorn.run("peopledetectorbackend.main:app", host="0.0.0.0", port=8001, reload=True)
if __name__ == "__main__":
    start()