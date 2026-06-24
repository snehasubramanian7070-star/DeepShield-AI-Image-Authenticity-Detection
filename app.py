from flask import Flask, render_template, request
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load trained model
model = load_model("model/deepshield_model.keras")

@app.route("/", methods=["GET", "POST"])
def index():

    prediction = None
    confidence = None
    filename = None

    if request.method == "POST":

        file = request.files["image"]

        if file:
            filename = file.filename
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Preprocess image
            img = image.load_img(filepath, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = img_array / 255.0

            # Prediction
            pred = model.predict(img_array)[0][0]

            if pred > 0.5:
                prediction = "REAL"
                confidence = round(pred * 100, 2)
            else:
                prediction = "FAKE"
                confidence = round((1 - pred) * 100, 2)

    return render_template(
        "index.html",
        prediction=prediction,
        confidence=confidence,
        filename=filename
    )

if __name__ == "__main__":
    app.run(debug=True)