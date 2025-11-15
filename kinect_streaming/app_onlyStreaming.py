import freenect
import cv2
from flask import Flask, Response

app = Flask(__name__)

# Funzione per generare il flusso video MJPEG dal Kinect
def gen():
    while True:
        # Ottieni un frame dalla videocamera Kinect (RGB)
        rgb, _ = freenect.sync_get_video()

        # Converte il frame in JPEG
        _, jpeg = cv2.imencode('.jpg', rgb)
        frame = jpeg.tobytes()

        # Genera il flusso MJPEG
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Rotta che restituisce il flusso MJPEG come risposta HTTP
@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Rotta per la home page che fornisce un collegamento al flusso video
@app.route('/')
def index():
    return '''
        <h1>Flusso Video Kinect</h1>
        <img src="/video_feed" />
    '''

# Rotte per il controllo del Kinect (tilt e modalità)
@app.route('/tilt_up')
def tilt_up():
    # Inclinare verso l'alto (positivo)
    freenect.set_tilt_degs(15)  # Inclinazione di 15 gradi
    return 'Tilt Up!'

@app.route('/tilt_down')
def tilt_down():
    # Inclinare verso il basso (negativo)
    freenect.set_tilt_degs(-15)  # Inclinazione di -15 gradi
    return 'Tilt Down!'

@app.route('/mode_ir')
def mode_ir():
    # Cambia la modalità video in IR
    freenect.set_video_mode(freenect.VIDEO_IR_8BIT)
    return 'IR Mode Activated!'

@app.route('/mode_rgb')
def mode_rgb():
    # Cambia la modalità video in RGB
    freenect.set_video_mode(freenect.VIDEO_RGB)
    return 'RGB Mode Activated!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
