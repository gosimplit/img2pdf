import os
import io
import json
from flask import Flask, request, send_file, jsonify
from PIL import Image, UnidentifiedImageError

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.post("/crop")
def crop_image():
    """
    Espera:
      - file: imagen original (binario, multipart/form-data)
      - coords: JSON como string, por ejemplo:
        {
          "id":"img-0.jpeg",
          "top_left_x":289,
          "top_left_y":667,
          "bottom_right_x":1132,
          "bottom_right_y":891
        }
    Devuelve:
      - La imagen recortada en binario (JPEG).
    """
    if "file" not in request.files:
        return jsonify({"error": "Falta la imagen en 'file'"}), 400
    coords_raw = request.form.get("coords")
    if not coords_raw:
        return jsonify({"error": "Faltan las coordenadas en 'coords'"}), 400

    try:
        coords = json.loads(coords_raw)
    except Exception as e:
        return jsonify({"error": f"coords inválido: {e}"}), 400

    # Abrir imagen
    try:
        img_file = request.files["file"]
        img = Image.open(img_file.stream).convert("RGB")
    except UnidentifiedImageError:
        return jsonify({"error": "Formato de imagen no reconocido"}), 400

    # Recortar
    try:
        x1 = int(coords["top_left_x"])
        y1 = int(coords["top_left_y"])
        x2 = int(coords["bottom_right_x"])
        y2 = int(coords["bottom_right_y"])
    except Exception:
        return jsonify({"error": "Coordenadas incompletas o no numéricas"}), 400

    crop = img.crop((x1, y1, x2, y2))

    # Devolver
    buf = io.BytesIO()
    crop.save(buf, format="JPEG", quality=92)
    buf.seek(0)

    return send_file(
        buf,
        mimetype="image/jpeg",
        as_attachment=True,
        download_name=coords.get("id", "crop.jpeg")
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)