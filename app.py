from flask import Flask, render_template, request, send_from_directory
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os
import sqlite3
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load trained AI model
model = load_model("model/deepshield_model.keras")


# -----------------------------
# Upload Image Route
# -----------------------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# -----------------------------
# Home Page
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    prediction = None
    confidence = None
    image_name = None

    if request.method == "POST":

        file = request.files["image"]

        if file:

            image_name = file.filename
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
            file.save(filepath)

            # Image preprocessing
            img = image.load_img(filepath, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = img_array / 255.0

            # AI Prediction
            pred = model.predict(img_array)[0][0]

            if pred > 0.5:
                prediction = "REAL"
                confidence = round(pred * 100, 2)
            else:
                prediction = "FAKE"
                confidence = round((1 - pred) * 100, 2)

            # Save prediction in SQLite database
            conn = sqlite3.connect("deepshield.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO predictions
                (image_name, prediction, confidence)
                VALUES (?, ?, ?)
                """,
                (image_name, prediction, confidence),
            )

            conn.commit()
            conn.close()

    return render_template(
        "index.html",
        prediction=prediction,
        confidence=confidence,
        image_name=image_name,
    )


# -----------------------------
# Prediction History
# -----------------------------


@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("deepshield.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction='REAL'")
    real = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction='FAKE'")
    fake = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(confidence) FROM predictions")
    avg = cursor.fetchone()[0]

    if avg is None:
        avg = 0

    avg = round(avg,2)

    conn.close()

    return render_template(
        "dashboard.html",
        total=total,
        real=real,
        fake=fake,
        average=avg
    )
@app.route("/download_report")
def download_report():

    conn = sqlite3.connect("deepshield.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT image_name, prediction, confidence
        FROM predictions
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return "No prediction available."

    image_name, prediction, confidence = row

    pdf_file = "DeepShield_Report.pdf"

    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>DeepShield AI Image Analysis Report</b>", styles["Title"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(f"<b>Image Name:</b> {image_name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Prediction:</b> {prediction}", styles["Normal"]))
    story.append(Paragraph(f"<b>Confidence:</b> {confidence:.2f}%", styles["Normal"]))

    risk = "LOW"
    if prediction == "FAKE" and confidence >= 90:
        risk = "HIGH"
    elif confidence >= 70:
        risk = "MEDIUM"

    story.append(Paragraph(f"<b>Risk Level:</b> {risk}", styles["Normal"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph("<b>Overall Assessment</b>", styles["Heading2"]))

    story.append(Paragraph(
        f"The uploaded image has been classified as <b>{prediction}</b> "
        f"with a confidence score of <b>{confidence:.2f}%</b> "
        "using the trained MobileNetV2 deep learning model.",
        styles["Normal"]
    ))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph("<b>Recommendation</b>", styles["Heading2"]))

    story.append(Paragraph(
        "This prediction is AI-assisted. Verify the original source before "
        "using the image for important purposes.",
        styles["Normal"]
    ))

    doc.build(story)

    return send_file(pdf_file, as_attachment=True)
@app.route("/history")
def history():

    conn = sqlite3.connect("deepshield.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, image_name, prediction, confidence
        FROM predictions
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return render_template("history.html", rows=rows)
# -----------------------------
# Run Flask
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)