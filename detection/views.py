from django.shortcuts import render
from ultralytics import YOLO
import os
from django.conf import settings
import cv2

# Utiliser YOLOv8n (nano) - beaucoup plus léger
MODEL_PATH = 'yolov8n.pt'  # Seulement 6MB vs 100MB
model = YOLO(MODEL_PATH)
print("✅ Modèle YOLOv8n chargé!")

def home(request):
    context = {
        "uploaded_image": None,
        "result_image": None,
        "full_count": 0,
        "empty_count": 0,
        "status": "⚪ Aucun résultat",
        "detections": []
    }
    
    if request.method == "POST" and request.FILES.get("image"):
        uploaded_file = request.FILES["image"]
        
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with open(file_path, "wb+") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        context["uploaded_image"] = uploaded_file.name
        
        # Traitement image seulement (pas vidéo pour économiser RAM)
        results = model(file_path, imgsz=320)  # Image plus petite = moins de RAM
        
        annotated_img = results[0].plot()
        result_name = "result_" + uploaded_file.name
        result_path = os.path.join(settings.MEDIA_ROOT, result_name)
        cv2.imwrite(result_path, annotated_img)
        
        full_count = 0
        empty_count = 0
        detections = []
        
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            confidence = float(box.conf[0])
            detections.append(f"{label} ({confidence*100:.1f}%)")
            
            if "bottle" in label.lower() or "cup" in label.lower():
                full_count += 1
            else:
                empty_count += 1
        
        context.update({
            "result_image": result_name,
            "full_count": full_count,
            "empty_count": empty_count,
            "detections": detections
        })
        
        if full_count > 0:
            context["status"] = f"🔴 {full_count} objet(s) détecté(s)"
        else:
            context["status"] = "🟢 Aucun objet détecté"
    
    return render(request, "detection/maison.html", context)
