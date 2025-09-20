from flask import Flask, request, send_file, jsonify
import io
import img2pdf

app = Flask(__name__)

@app.route("/img2pdf", methods=["POST"])
def images_to_pdf():
    """
    Espera imágenes enviadas como multipart/form-data:
      files[] = 0.png, 1.png, 2.png ...
    Devuelve un único PDF con las imágenes en orden.
    """
    try:
        if "files" not in request.files:
            return jsonify({"error": "No se encontraron archivos en la petición"}), 400

        files = request.files.getlist("files")
        if not files:
            return jsonify({"error": "La lista de archivos está vacía"}), 400

        # Ordenar por número en el nombre (0.png, 1.png, ...)
        files.sort(key=lambda f: int(f.filename.split(".")[0]))

        # Crear PDF en memoria
        pdf_bytes = img2pdf.convert([f.read() for f in files])
        pdf_buffer = io.BytesIO(pdf_bytes)

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="documento.pdf"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
