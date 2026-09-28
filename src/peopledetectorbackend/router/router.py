import base64
import cv2
import numpy as np
import imutils
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from logging import Logger

# Importaciones de tus módulos
from peopledetectorbackend.model.detection import Detection
from peopledetectorbackend.camera_logic import detector


current_state = {
    "count": 0,
    "image_b64": ""
}

logger = Logger("router")
router = APIRouter()

@router.post("/api/count")
async def update_count(data: Detection):
    try:
        # 1. Decodificar la imagen Base64 entrante a un formato legible por OpenCV
        img_bytes = base64.b64decode(data.image_b64)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Imagen inválida o corrupta")

        # Mantener el límite de tamaño para evitar saturar el CPU del servidor
        frame = imutils.resize(frame, width=min(400, frame.shape[1]))

        # 2. Extraer los datos mediante la lógica importada
        resultados = detector(frame)
        conteo = len(resultados)

        # 3. Dibujar los rectángulos de detección visual sobre la imagen
        for (xA, yA, xB, yB) in resultados:
            cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

        # 4. Volver a convertir el frame (ya procesado con cuadros) a Base64
        _, img_encoded = cv2.imencode('.png', frame)
        frame_procesado_b64 = base64.b64encode(img_encoded).decode('utf-8')

        # 5. Sobrescribir el estado global en memoria
        current_state["count"] = conteo
        current_state["image_b64"] = frame_procesado_b64
        
        logger.info(f"Conteo actualizado a {current_state['count']} personas")
        return {"message": "Conteo actualizado exitosamente", "count": conteo}
        
    except Exception as e:
        logger.error(f"Fallo en procesamiento de imagen: {e}")
        raise HTTPException(status_code=500, detail="Error interno procesando el frame")

@router.get("/", response_class=HTMLResponse)
async def get_dashboard():
    # Uso de .get() por seguridad inicial si el diccionario está vacío
    html = f"""
    <html>
        <head><title>People Detector Dashboard</title></head>
        <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
            <h1>Personas detectadas: {current_state.get('count', 0)}</h1>
            <img src="data:image/png;base64,{current_state.get('image_b64', '')}"
            style="border: 2px solid #333; border-radius: 8px; width: 640px; height: auto; background-color: #f0f0f0;" />
            <script>
                // Actualiza cada 2 segundos
                setTimeout(function(){{ window.location.reload(1); }}, 2000);
            </script>
        </body>
    </html>
    """
    return html