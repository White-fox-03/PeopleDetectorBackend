import base64
import cv2
import numpy as np
import imutils
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from logging import Logger

# Importaciones de tus módulos
from peopledetectorbackend.model.detection import Detection


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
        
        # ---> GIRA LA IMAGEN 180 GRADOS PARA ENDEREZARLA <---
        frame = cv2.rotate(frame, cv2.ROTATE_180)

        # 2. Extraer los datos mediante la lógica importada
        resultados = detector(frame)
        conteo = len(resultados)

        # 3. Censurar destructivamente a las personas detectadas (Cumplimiento legal)
        for (xA, yA, xB, yB) in resultados:
            # Asegurar que las coordenadas no excedan los límites de la imagen
            # para evitar crashes en OpenCV
            h_img, w_img = frame.shape[:2]
            xA, yA = max(0, xA), max(0, yA)
            xB, yB = min(w_img, xB), min(h_img, yB)
            
            # Extraer la región de interés (ROI) de la persona
            roi = frame[yA:yB, xA:xB]
            
            # Validar que el recorte tiene dimensiones válidas
            if roi.shape[0] > 0 and roi.shape[1] > 0:
                # Aplicar un filtro gaussiano severo. 
                # (99, 99) es el tamaño del kernel. Si se requiere más difuminado, usa valores impares más altos como (149, 149)
                roi_blurred = cv2.GaussianBlur(roi, (99, 99), 50)
                
                # Sobrescribir los píxeles originales en la memoria
                frame[yA:yB, xA:xB] = roi_blurred
                
                # Dibujar el rectángulo sobre la zona censurada
                cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

        # 4. Volver a convertir el frame (ya censurado) a Base64
        _, img_encoded = cv2.imencode('.jpg', frame)
        frame_procesado_b64 = base64.b64encode(img_encoded).decode('utf-8')

        # 5. Sobrescribir el estado global en memoria
        current_state["count"] = conteo
        current_state["image_b64"] = frame_procesado_b64
        
        logger.info(f"Conteo actualizado a {current_state['count']} personas (Frame anonimizado)")
        return {"message": "Conteo actualizado exitosamente", "count": conteo}
        
    except Exception as e:
        logger.error(f"Fallo en procesamiento de imagen: {e}")
        raise HTTPException(status_code=500, detail="Error interno procesando el frame")

@router.get("/", response_class=HTMLResponse)
async def get_dashboard():
    html = f"""
    <html>
        <head><title>People Detector Dashboard</title></head>
        <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
            <h1>Personas detectadas: {current_state.get('count', 0)}</h1>
            <img src="data:image/jpeg;base64,{current_state.get('image_b64', '')}"
style="border: 2px solid #333; border-radius: 8px; max-height: 80vh; width: auto; background-color: #f0f0f0;" />
            <script>
                setTimeout(function(){{ window.location.reload(1); }}, 2000);
            </script>
        </body>
    </html>
    """
    return html