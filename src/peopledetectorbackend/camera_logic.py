import cv2
import numpy as np
from imutils.object_detection import non_max_suppression

# Inicializar el modelo HOG + SVM una sola vez al cargar este módulo en memoria
HOGCV = cv2.HOGDescriptor()
HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def detector(image):
    """
    Recibe un frame de OpenCV y devuelve un array con las coordenadas 
    de las personas detectadas.
    """
    # 1. Detectar posibles siluetas humanas
    (rects, weights) = HOGCV.detectMultiScale(
        image, 
        winStride=(4, 4), 
        padding=(8, 8), 
        scale=1.05
    )
    
    # Si no se detecta nada, devolver un array vacío rápidamente
    if len(rects) == 0:
        return []

    # 2. Convertir el formato (x, y, ancho, alto) a (x_inicial, y_inicial, x_final, y_final)
    rects_array = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    
    # 3. Aplicar Non-Maxima Suppression (NMS) para limpiar cuadros duplicados 
    # sobre una misma persona
    resultados = non_max_suppression(rects_array, probs=None, overlapThresh=0.65)
    
    return resultados