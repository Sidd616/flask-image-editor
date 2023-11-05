from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import os


UPLOAD_FOLDER = 'flask-image-editor-main/uploads'
PROCESS_FOLDER = 'flask-image-editor-main/static'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def processImage(filename, operation):
    print(f"the operation is {operation} and filename is {filename}")
    img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename = os.path.join(PROCESS_FOLDER, filename)
            cv2.imwrite(newFilename, imgProcessed)
            new = f"static/{filename}"
            return new

        case "crotate":
            angle = int(request.form.get("angle"))
            rows, cols, _ = img.shape
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
            # Calculate the new dimensions to ensure no cropping
            cos = np.abs(M[0, 0])
            sin = np.abs(M[0, 1])
            new_cols = int((rows * sin) + (cols * cos))
            new_rows = int((rows * cos) + (cols * sin))
            # Adjust the transformation matrix for the new dimensions
            M[0, 2] += (new_cols / 2) - (cols / 2)
            M[1, 2] += (new_rows / 2) - (rows / 2)
            # Rotate the image without cropping
            img = cv2.warpAffine(img, M, (new_cols, new_rows),
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
            newFilename = os.path.join(PROCESS_FOLDER, filename)
            cv2.imwrite(newFilename, img)
            new = f"static/{filename}"
            return new

        case "cresize":
            scale = float(request.form.get("scale"))
            img = cv2.resize(img, None, fx=scale, fy=scale)
            newFilename = os.path.join(PROCESS_FOLDER, filename)
            cv2.imwrite(newFilename, img)
            new = f"static/{filename}"
            return new

        case "cwebp":
            newFilename = f"flask-image-editor-main/static\{filename.split('.')[0]}.webp"
            cv2.imwrite(newFilename, img)
            new = f"static/{filename.split('.')[0]}.webp"
            return new

        case "cjpg":
            newFilename = f"flask-image-editor-main/static\{filename.split('.')[0]}.jpg"
            cv2.imwrite(newFilename, img)
            new = f"static/{filename.split('.')[0]}.jpg"
            return new

        case "cpng":
            newFilename = f"flask-image-editor-main/static\{filename.split('.')[0]}.png"
            cv2.imwrite(newFilename, img)
            new = f"static/{filename.split('.')[0]}.png"
            return new

    pass


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/poster")
def manual():
    return render_template("manual.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print("Current working directory:", os.getcwd())
            print("File path to save:", os.path.join(
                app.config['UPLOAD_FOLDER'], filename))

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = processImage(filename, operation)
            print(new)

            flash(
                f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a>")

    return render_template("index.html")


app.run(debug=True, port=5001)
