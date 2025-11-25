import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image

# 🔹 Charger le modèle YOLO
model = YOLO("best.pt")  # chemin vers ton modèle entraîné

# Configuration de la page
st.set_page_config(page_title="♻️ Smart Bin Detector", layout="wide")

# CSS personnalisé
st.markdown("""
<style>
.header {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    padding: 40px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
.header h1 { font-size: 3em; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
.header p { font-size: 1.2em; opacity: 0.9; }
.card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin: 15px 0; border-left: 4px solid #11998e; }
.stButton>button { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; font-size: 1.2em; padding: 15px 40px; border-radius: 10px; font-weight: 600; box-shadow: 0 5px 20px rgba(17,153,142,0.4); transition: all 0.3s ease; }
.stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(17,153,142,0.6); }
.footer { text-align: center; padding: 30px; color: #666; margin-top: 40px; border-top: 2px solid #e0e0e0; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header">
    <h1>♻️ SMART BIN DETECTOR</h1>
    <p>Système intelligent de détection d'état des poubelles par IA</p>
    <p style="font-size: 0.9em; opacity: 0.8;">Propulsé par YOLOv8 • Détection en temps réel • Gestion automatisée</p>
</div>
""", unsafe_allow_html=True)

# Layout en deux colonnes
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
        <h3>📤 ÉTAPE 1 : Upload</h3>
        <p>Importez une image de la poubelle</p>
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["jpg","jpeg","png"])
    analyze_btn = st.button("🔍 ANALYSER LA POUBELLE")

    st.markdown("""
    <div class="card">
        <h4>ℹ️ Comment utiliser</h4>
        <ol style="line-height:1.8;">
            <li>📸 Prenez une photo de la poubelle</li>
            <li>⬆️ Uploadez l'image (JPG, PNG)</li>
            <li>🔍 Cliquez sur "Analyser"</li>
            <li>✅ Obtenez le résultat instantanément</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h3>📊 ÉTAPE 2 : Résultats</h3>
        <p>État détecté de la poubelle</p>
    </div>
    """, unsafe_allow_html=True)
    status_placeholder = st.empty()
    image_placeholder = st.empty()
    details_placeholder = st.empty()

# Détection fonction
def detect_trash_bin(image_pil):
    image = np.array(image_pil)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    results = model.predict(image, conf=0.5)
    annotated_img = results[0].plot()
    annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
    annotated_pil = Image.fromarray(annotated_img)

    boxes = results[0].boxes
    if len(boxes) > 0:
        predictions = []
        pleine_count = 0
        for i, box in enumerate(boxes, 1):
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = results[0].names[class_id]
            if "plein" in class_name.lower() or "full" in class_name.lower():
                pleine_count += 1
                emoji = "🗑️"
            else:
                emoji = "✅"
            predictions.append(f"{emoji} Poubelle {i}: {class_name} - Confiance: {confidence:.2%}")
        result_text = "\n".join(predictions)
        status = f"🔴 ALERTE - {pleine_count} poubelle(s) pleine(s) détectée(s) !" if pleine_count>0 else "🟢 OK - Toutes les poubelles sont vides"
    else:
        status = "⚪ Aucune poubelle détectée"
        result_text = "Aucune détection"
    return annotated_pil, status, result_text

# Action du bouton
if analyze_btn and uploaded_file:
    image = Image.open(uploaded_file)
    annotated_img, status, details = detect_trash_bin(image)
    status_placeholder.markdown(f"### {status}")
    image_placeholder.image(annotated_img, caption="🎯 Image annotée", use_column_width=True)
    details_placeholder.markdown(f"**Détails :**\n{details}")

# Footer
st.markdown("""
<div class="footer">
    <p>♻️ Smart Bin Detector</p>
    <p>Développé avec ❤️ pour une gestion intelligente des déchets</p>
    <p style="font-size:0.9em; color:#999;">🌱 Contribuez à un environnement plus propre et durable</p>
</div>
""", unsafe_allow_html=True)
