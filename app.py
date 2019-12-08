# app.py
import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
import subprocess
from moviepy.editor import VideoFileClip

project_root = os.path.dirname(__file__)
template_path = os.path.join(project_root, './')
app = Flask(__name__, template_folder=template_path, static_folder='static')
UPLOAD_FOLDER = '/home/zeyu/Desktop/5sec/uploads'
DOWNLOAD_FOLDER = '/home/zeyu/Desktop/5sec/static'
TFRECORD_FOLDER = '/home/zeyu/Desktop/5sec/tfrecord'
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


def getlength(filename):
    clip = VideoFileClip('/home/zeyu/Desktop/5sec/uploads/' + filename)
    return clip.duration


def infer(filename, newpath):
    file,extension = filename.split('.')
    subprocess.run(['python', '/home/zeyu/Desktop/5sec/youtube-8m-master/inference.py', '--train_dir','/home/zeyu/Desktop/5sec/yt8mmodel',
                    '--output_file=/inferenceoutput/out.csv',
                    '--input_data_pattern=' + os.path.join(app.config['UPLOAD_FOLDER'], filename),
                    '--segment_labels'])


def featureextract(filename,videopath):
    time = getlength(filename)
    subprocess.run(['python', '-m',
                    'mediapipe.examples.desktop.youtube8m.generate_input_sequence_example',
                    '--path_to_input_video=/home/zeyu/Desktop/5sec/uploads/' + filename,
                    '--clip_end_time_sec=' + str(int(time))])
    GLOG_logtostderr=1
    subprocess.run(['bazel-bin/mediapipe/examples/desktop/youtube8m/extract_yt8m_features', \
		'--calculator_graph_config_file=/home/zeyu/Desktop/mediapipe/mediapipe/graphs/youtube8m/feature_extraction.pbtxt', \
		'--input_side_packets=input_sequence_example=/tmp/mediapipe/metadata.pb', \
		'--output_side_packets=output_sequence_example=/tmp/mediapipe/features.pb'])
    subprocess.run(['bazel-bin/mediapipe/examples/desktop/youtube8m/model_inference', \
    	'--calculator_graph_config_file=mediapipe/graphs/youtube8m/local_video_model_inference.pbtxt', \
    	'--input_side_packets=input_sequence_example_path=/tmp/mediapipe/features.pb,input_video_path=/home/zeyu/Desktop/test.mp4,output_video_path=/home/zeyu/Desktop/5sec/static/annotated.avi,segment_size=5,overlap=4'])



def seg(path, filename):
	videopath = '/home/zeyu/Desktop/5sec/annotated/'+filename
	if not os.path.exists(videopath):
		os.makedirs(videopath)
	newpath = '/home/zeyu/Desktop/5sec/tfrecord/'+filename
	if not os.path.exists(newpath):
		os.makedirs(newpath)
    # convert_videos_to_tfrecord(app.config['UPLOAD_FOLDER'], os.path.join(app.config['TFRECORD_FOLDER'],filename), 1, 5, filename)
	# infer(filename, newpath)
	featureextract(filename,videopath)
    # inference.inference(train_,.join(app.config['DOWNLOAD_FOLDER'], filename))


@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    if request.method == 'POST':
        return send_from_directory('/home/zeyu/Desktop/5sec/static', filename='annotated.avi', as_attachment=True)
    return render_template('download.html', filename=filename)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == "__main__":
    app.run()
