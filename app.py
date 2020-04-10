import os
from pydub import AudioSegment
from flask import Flask, flash, request, redirect, url_for, send_file, render_template
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import librosa, librosa.display
import matplotlib.pyplot as plt
import io
from pydub.utils import which

IMAGE_FOLDER = os.path.join('static', 'image')
UPLOAD_FOLDER = os.path.join('static', 'audio')  # 'uploads'
ALLOWED_EXTENSIONS = {'mp3'}
AudioSegment.converter = which("ffmpeg")

app = Flask(__name__)

Bootstrap(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
# @app.route('/<file>', methods=['GET', 'POST'])
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
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(audio_path)
            app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER
            hop_length = 512
            n_fft = 2048
            song = AudioSegment.from_file(audio_path, format="mp3")
            wav_way = os.path.join('static', 'audio') + "/" + filename[0::-4] + '.wav'
            song.export(wav_way, format="wav")
            filepath = app.config['UPLOAD_FOLDER'] + '/' + filename
            x, sr = librosa.load(wav_way)
            X = librosa.stft(x, n_fft=n_fft, hop_length=hop_length)
            S = librosa.amplitude_to_db(abs(X))
            plt.figure(figsize=(15, 5))
            librosa.display.specshow(librosa.amplitude_to_db(S), hop_length=hop_length, sr=sr, x_axis='time',
                                     y_axis='linear')
            plt.colorbar(format='%+2.0f dB')
            bytes_image = io.BytesIO()
            fname = filename[:-4] + ".png"
            plt.savefig(os.path.join('static', 'image') + "/" + fname)  # app.config['UPLOAD_FOLDER'] + "/" + fname)
            bytes_image.seek(0)
            full_filename = os.path.join(app.config['UPLOAD_FOLDER'], fname)
            return render_template("mp3.html", user_image=full_filename, audio_path=audio_path, audio_name=filename)
    return render_template("mp3.html")


if __name__ == '__main__':
    app.run()
