from django.shortcuts import render
from ultralytics import YOLO
import os
from django.conf import settings
import cv2

# Charger le modèle
model = YOLO("/Users/apple/Downloads/best.pt")

def home(request):
    context = {
        "uploaded_image": None,
        "result_image": None,
        "full_count": 0,
        "empty_count": 0,
        "status": "⚪ Aucun résultat",
        "detections": [],
        "is_video": False
    }
    
    if request.method == "POST" and request.FILES.get("image"):
        uploaded_file = request.FILES["image"]
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # Enregistrer le fichier
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with open(file_path, "wb+") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        context["uploaded_image"] = uploaded_file.name
        
        # Vérifier si c'est une vidéo
        is_video = file_extension in ['mp4', 'avi', 'mov', 'mkv']
        context["is_video"] = is_video
        
        if is_video:
            # 🎥 TRAITEMENT VIDÉO
            print("🎥 Traitement vidéo en cours...")
            cap = cv2.VideoCapture(file_path)
            
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Vidéo de sortie
            result_name = "result_" + uploaded_file.name
            result_path = os.path.join(settings.MEDIA_ROOT, result_name)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(result_path, fourcc, fps, (width, height))
            
            full_count_total = 0
            empty_count_total = 0
            detections_set = set()
            frames_processed = 0
            
            print(f"📊 FPS: {fps}, Frames: {total_frames}")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Analyser toutes les 15 frames pour accélérer
                if frames_processed % 15 == 0:
                    results = model(frame, verbose=False)
                    annotated_frame = results[0].plot()
                    
                    # Compter les détections
                    for box in results[0].boxes:
                        cls_id = int(box.cls[0])
                        label = model.names[cls_id]
                        confidence = float(box.conf[0])
                        
                        detection_str = f"{label} ({confidence*100:.1f}%)"
                        detections_set.add(detection_str)
                        
                        if "full" in label.lower() or "plein" in label.lower():
                            full_count_total += 1
                        elif "empty" in label.lower() or "vide" in label.lower():
                            empty_count_total += 1
                    
                    out.write(annotated_frame)
                    print(f"✅ Frame {frames_processed}/{total_frames} traité")
                else:
                    out.write(frame)
                
                frames_processed += 1
            
            cap.release()
            out.release()
            
            # Moyenne des détections
            analyzed_frames = frames_processed // 15
            full_count = full_count_total // max(1, analyzed_frames)
            empty_count = empty_count_total // max(1, analyzed_frames)
            
            detections = list(detections_set)
            
            print(f"🎬 Vidéo traitée: {full_count} pleines, {empty_count} vides")
            
        else:
            # 🖼️ TRAITEMENT IMAGE
            results = model(file_path)
            
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
                
                if "full" in label.lower() or "plein" in label.lower():
                    full_count += 1
                elif "empty" in label.lower() or "vide" in label.lower():
                    empty_count += 1
        
        # Mettre à jour le contexte
        context["result_image"] = result_name
        context["full_count"] = full_count
        context["empty_count"] = empty_count
        context["detections"] = detections
        
        # Statut
        if full_count > 0 and empty_count == 0:
            context["status"] = f"🔴 ALERTE - {full_count} Poubelle(s) pleine(s)"
        elif empty_count > 0 and full_count == 0:
            context["status"] = f"🟢 PARFAIT - {empty_count} Poubelle(s) vide(s)"
        elif full_count > 0 and empty_count > 0:
            context["status"] = f"🟠 MIXTE - {full_count} pleine(s) + {empty_count} vides"
        else:
            context["status"] = "⚪ Aucune poubelle détectée"
    
    return render(request, "detection/maison.html", context)