from flask import Flask, render_template, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def home():

    image_name = None

    if request.method == "POST":

        image = request.files["image"]

        if image.filename != "":
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image.filename))
            image_name = image.filename

    return render_template("index.html", image_name=image_name)

if __name__ == "__main__":
    app.run(debug=True)