from ultralytics import YOLO

modelo_yolo = YOLO("yolov8s.pt")  # Cargar el modelo YOLOv8 preentrenado




def detector(image):
    """
    Recibe un frame de OpenCV y devuelve un array con las coordenadas 
    de las personas detectadas en formato [x_inicial, y_inicial, x_final, y_final].
    """
    # Ejecutar inferencia con YOLO
    # classes=[0] filtra estrictamente solo "personas" (ID 0 en el dataset COCO)
    # conf=0.5 requiere un 50% de certeza para evitar falsos positivos con sillas/objetos
    # verbose=False evita que llene la consola del servidor con logs por cada frame
    resultados = modelo_yolo.predict(image, classes=[0], conf=0.28, iou=0.3, verbose=False)
    
    coordenadas_personas = []
    
    # Procesar el resultado de Ultralytics al formato que espera router.py
    for resultado in resultados:
        cajas = resultado.boxes
        for caja in cajas:
            # Extraer coordenadas y convertir a enteros
            x1, y1, x2, y2 = caja.xyxy[0].cpu().numpy().astype(int)
            coordenadas_personas.append([x1, y1, x2, y2])
            
    return coordenadas_personas