from peopledetectorbackend.model.detection import Detection
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from logging import Logger

from peopledetectorbackend.main import current_state

logger = Logger("router")
router = APIRouter()


@router.post("/api/count")
async def update_count(data: Detection):
    current_state["count"] = data.count
    current_state["image_b64"] = data.image_b64
    logger.info(f"Count updated to {current_state['count']}")
    return {"message": "Count updated successfully"}

@router.get("/", response_class=HTMLResponse)
async def get_dashboard():

    html = f"""
    <html>
        <head><title>People Detector Dashboard</title></head>
        <body>People detected: {current_state['count']}<br>
        <img src="data:image/png;base64,{current_state['image_b64']}"
        style="border: 2px solid #333; border-radius: 8px; width: 640px; height: auto;" />
            <script>
                setTimeout(function(){{ window.location.reload(1); }}, 2000);
            </script>
        </body>
    </html>
    """
    return html

