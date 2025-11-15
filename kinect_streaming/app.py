import freenect
import cv2
from flask import Flask, render_template, request, Response

app = Flask(__name__)

# Inizializza il dispositivo Kinect
def init_device():
    # L'ID del dispositivo è 0, e il secondo parametro è gestito automaticamente da freenect
    device = freenect.open_device(0)  # 0 è l'ID del dispositivo Kinect
    return device

device = init_device()  # Inizializza il dispositivo al caricamento

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

# Rotta per controllare il tilt
@app.route('/set_tilt', methods=['POST'])
def set_tilt():
    tilt_action = request.form.get('tilt')
    
    if tilt_action == 'up':
        freenect.set_tilt_degs(device, 15)  # Alza il Kinect a 15 gradi
    elif tilt_action == 'down':
        freenect.set_tilt_degs(device, -15)  # Abbassa il Kinect a -15 gradi
    elif tilt_action == 'reset':
        freenect.set_tilt_degs(device, 0)  # Reset del Kinect (inclinazione a 0 gradi)
    
    return '', 204  # Risposta vuota per indicare che tutto è andato a buon fine

# Rotte per il controllo della modalità
@app.route('/mode_ir')
def mode_ir():
    # Cambia la modalità video in IR
    freenect.set_video_mode(device, freenect.VIDEO_IR_8BIT)
    return '', 204

@app.route('/mode_rgb')
def mode_rgb():
    # Cambia la modalità video in RGB
    freenect.set_video_mode(device, freenect.VIDEO_RGB)
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
