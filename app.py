from os import path
from flask import Flask, render_template, request, redirect
import keras
import numpy as np
import cv2
from predict import *
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from dominate.tags import img
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from dominate.tags import img
from firebase import firebase


firebase = firebase.FirebaseApplication(
    'https://stolen-vehicle-19f06-default-rtdb.asia-southeast1.firebasedatabase.app', None)


logo = img(src='./static/img/logo.png', height="50",
           width="50", style="margin-top:-15px")
topbar = Navbar(logo,
                View('Find', 'find'),
                View('Register', 'submit'),

                )

# registers the "top" menubar
nav = Nav()
nav.register_element('top', topbar)

app = Flask(__name__)
Bootstrap(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    return(render_template('index.html'))


# find num plate

@app.route('/find', methods=["GET", "POST"])
def find():
    transcript = ""
    if request.method == "POST":
        print("FORM DATA RECEIVED")

        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        print(file.filename)
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save('images/'+filename)
            image_np = cv2.imread('images/'+filename, 1)

            path = 'plate_char_recognition.h5'
            loaded_model = keras.models.load_model(path)

            plate_img, plate = extract_plate(image_np)
            char = segment_characters(plate)
            plate_number = show_results(char, loaded_model)

            num = plate_number

            transcript = num.upper()

    return render_template('find.html', transcript=transcript)


@app.route('/register', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST' and len(dict(request.form)) > 0:
        userdata = dict(request.form)
        name = userdata["name"][0]
        address = userdata["address"][0]
        new_data = {"name": name, "address": address}
        firebase.post("/", new_data)
    return(render_template('register.html'))


nav.init_app(app)


if __name__ == '__main__':
    app.run(debug=True)
