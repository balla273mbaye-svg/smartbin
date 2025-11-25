# detection/views.py
from django.shortcuts import render
from ultralytics import YOLO
import os, tempfile, sys
from django.conf import settings
import cv2

# Assure que le dossier MEDIA existe
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

# Fix pour Ultralytics (répertoire de config)
YOLO_CONFIG_DIR = os.path.join(tempfile.gettempdir(), "yolo_config")
os.environ["YOLO_CONFIG_DIR"] = YOLO_CONFIG_DIR
os.makedirs(YOLO_CONFIG_DIR, exist_ok=True)

# Chemin du modèle
MODEL_PATH = os.path.join(settings.BASE_DIR, "detection", "models", "best.pt")
print("DEBUG: MODEL_PATH =", MODEL_PATH, file=sys.stderr)

# Chargement du modèle
model = None
try:
    if os.path.exists(MODEL_PATH):
        model = YOLO(MODEL_PATH)
        print("✅ Modèle YOLO chargé", file=sys.stderr)
    else:
        print("⚠️ best.pt introuvable à", MODEL_PATH, file=sys.stderr)
except Exception as e:
    print("❌ Erreur chargement YOLO:", e, file=sys.stderr)
    model = None


def home(request):
    context = {
        "uploaded_image": None,
        "result_image": None,
        "full_count": 0,
        "empty_count": 0,
        "status": "⚪ Aucun résultat",
        "detections": [],
    }

    # Si le modèle n'a pas pu être chargé
    if model is None:
        context["status"] = "❌ Modèle d'IA indisponible"
        return render(request, "detection/maison.html", context)

    # Lorsqu'une image est envoyée
    if request.method == "POST" and request.FILES.get("image"):
        uploaded_file = request.FILES["image"]
        print("DEBUG: Fichier reçu :", uploaded_file.name, file=sys.stderr)

        # Sauvegarde dans MEDIA
        upload_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with open(upload_path, "wb+") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        context["uploaded_image"] = uploaded_file.name

        # Lecture OpenCV
        img = cv2.imread(upload_path)
        if img is None:
            context["status"] = "❌ Erreur : Impossible de lire l'image"
            return render(request, "detection/maison.html", context)

        # Redimensionner (sécurité RAM)
        max_size = 720
        h, w = img.shape[:2]
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))

        # Prédiction YOLO
        try:
            results = model.predict(img, device='cpu', verbose=False)
        except Exception as e:
            print("❌ Erreur durant la prédiction :", e, file=sys.stderr)
            context["status"] = "❌ Analyse impossible"
            return render(request, "detection/maison.html", context)

        # Image annotée
        annotated = results[0].plot()
        result_name = "result_" + uploaded_file.name
        result_path = os.path.join(settings.MEDIA_ROOT, result_name)
        cv2.imwrite(result_path, annotated)
        context["result_image"] = result_name

        # Comptage
        full = empty = 0
        detected = []

        for box in results[0].boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            conf = float(box.conf[0])
            detected.append(f"{label} ({conf*100:.1f}%)")

            if label.lower() in ["full", "pleine", "plein"]:
                full += 1
            elif label.lower() in ["empty", "vide"]:
                empty += 1

        context["full_count"] = full
        context["empty_count"] = empty
        context["detections"] = detected

        # Message d'état
        if full > 0 and empty == 0:
            context["status"] = f"🔴 ALERTE - {full} poubelle(s) pleine(s)"
        elif empty > 0 and full == 0:
            context["status"] = f"🟢 PARFAIT - {empty} vide(s)"
        elif full > 0 and empty > 0:
            context["status"] = f"🟠 MIXTE - {full} pleine(s) + {empty} vide(s)"
        else:
            context["status"] = "⚪ Aucune poubelle détectée"

    return render(request, "detection/maison.html", context)
