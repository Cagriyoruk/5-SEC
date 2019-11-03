# app.py
import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from shutil import copyfile
import ffmpy
from video2tfrecord import convert_videos_to_tfrecord
import cv2
import inference
import subprocess

os.environ['PATH'] = 'D:/Anaconda3/envs/tensorflow/python.exe'
project_root = os.path.dirname(__file__)
template_path = os.path.join(project_root, './')
app = Flask(__name__, template_folder=template_path, static_folder='static')
UPLOAD_FOLDER = 'D:/uploads'
DOWNLOAD_FOLDER = 'D:/PycharmProjects/5sec/static'
TFRECORD_FOLDER = 'D:/tfrecord'
ALLOWED_EXTENSIONS = {'mp4', 'wmv', 'avi', 'tfrecord','jpg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['TFRECORD_FOLDER'] = TFRECORD_FOLDER


@app.route("/video")
def video():
    return '111'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            process_file(app.config['UPLOAD_FOLDER'], filename)
            return redirect(url_for('download', filename=filename))
    return render_template('template.html')


def process_file(path, filename):
    seg(path, filename)


'''
input_file = Image.open(os.path.join(path, filename))
input_file.save(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), 'PNG')
'''

def infer(filename, newpath):
    file,extension = filename.split('.')
    subprocess.run(['python', 'inference.py', '--train_dir','D:/PycharmProjects/5sec/yt8mmodel',
                    '--output_file=D:/PycharmProjects/5sec/inferenceoutput/out.csv',
                    '--input_data_pattern=' + os.path.join(app.config['UPLOAD_FOLDER'], filename),
                    '--segment_labels'])


def seg(path, filename):
    newpath = 'D:/tfrecord/'+filename
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    # convert_videos_to_tfrecord(app.config['UPLOAD_FOLDER'], os.path.join(app.config['TFRECORD_FOLDER'],filename), 1, 1, filename)
    infer(filename, newpath)
    # inference.inference(train_,.join(app.config['DOWNLOAD_FOLDER'], filename))


@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    if request.method == 'POST':
        return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename=filename, as_attachment=True)
    return render_template('download.html', filename=filename)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == "__main__":
    app.run()