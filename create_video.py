import cv2
import os

# 🔹 Paramètres vidéo
fps = 5
width, height = 640, 480
output_dir = "videos"
os.makedirs(output_dir, exist_ok=True)

# 🔹 Dossiers contenant les images
categories = ["pleine", "vide"]
dataset_dir = "/Users/apple/Downloads/dataset_scrape/train"  # <-- chemin complet vers ton dossier train

for category in categories:
    image_folder = os.path.join(dataset_dir, category)
    output_path = os.path.join(output_dir, f"{category}.avi")  # extension AVI

    image_files = sorted([f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    if not image_files:
        print(f"⚠️ Aucun fichier trouvé dans {image_folder}, skip.")
        continue

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Codec MJPG pour macOS
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not video.isOpened():
        print(f"❌ Impossible de créer la vidéo {output_path}")
        continue

    for i, img_name in enumerate(image_files):
        img_path = os.path.join(image_folder, img_name)
        frame = cv2.imread(img_path)

        if frame is None:
            print(f"⚠️ Image ignorée (lecture impossible) : {img_name}")
            continue

        frame = cv2.resize(frame, (width, height))

        # Ajouter chaque image 10 fois pour ~2 secondes à 5 fps
        for _ in range(10):
            video.write(frame)

        print(f"[{i+1}/{len(image_files)}] {img_name} ajouté à la vidéo {category}")

    video.release()
    print(f"\n✅ Vidéo créée : {output_path}")
    print(f"🎥 {len(image_files)*10} frames (~{len(image_files)*2} secondes)")
