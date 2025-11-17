import freenect
import cv2
import numpy as np
from flask import Flask, Response, request
import threading
import time

# --- Variabili globali per l'accesso sicuro tra thread ---
app = Flask(__name__)
device = None
lock = threading.Lock()  # Lock per proteggere l'accesso al dispositivo

# Variabile per conservare l'ultimo frame catturato dal Kinect
latest_frame = None
# Variabile per controllare la modalità video corrente
current_mode = freenect.VIDEO_RGB

# --- Thread in background per l'elaborazione dei dati del Kinect ---
def kinect_thread():
    global latest_frame, current_mode, device
    
    last_mode_applied = None

    while True:
        with lock:
            if not device:
                time.sleep(0.1)
                continue

            # Controlla se la modalità è cambiata e la applica
            if current_mode != last_mode_applied:
                freenect.set_video_mode(device, current_mode)
                last_mode_applied = current_mode
            
            # Ottieni un frame dal Kinect
            if current_mode == freenect.VIDEO_RGB:
                frame, _ = freenect.sync_get_video()
                # freenect fornisce i frame in formato RGB, ma OpenCV si aspetta BGR per l'encoding
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:  # Modalità IR
                frame, _ = freenect.sync_get_video(format=freenect.VIDEO_IR_8BIT)
                # Converte l'immagine IR a 8 bit in un formato visualizzabile
                frame = frame.astype(np.uint8)
            
            # Codifica il frame in formato JPEG
            _, jpeg = cv2.imencode('.jpg', frame)
            latest_frame = jpeg.tobytes()
        
        # Una piccola pausa per evitare di consumare il 100% della CPU
        time.sleep(1/30)  # Punta a circa 30fps

# --- Route di Flask ---

# Generatore di frame per lo stream video
def gen_frames():
    global latest_frame
    while True:
        frame_to_send = None
        with lock:
            if latest_frame is not None:
                frame_to_send = latest_frame
        
        if frame_to_send:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_to_send + b'\r\n\r\n')
        # Pausa per non intasare la rete se non ci sono nuovi frame
        time.sleep(1/30)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_tilt', methods=['POST'])
def set_tilt():
    global device
    tilt_action = request.form.get('tilt')
    
    angle = 0
    if tilt_action == 'up':
        angle = 15
    elif tilt_action == 'down':
        angle = -15
    # Non è necessario un caso 'reset', l'angolo 0 è il default
    
    with lock:
        if device:
            freenect.set_tilt_degs(device, angle)
    
    return '', 204

@app.route('/mode_ir')
def mode_ir():
    global current_mode
    with lock:
        current_mode = freenect.VIDEO_IR_8BIT
    return '', 204

@app.route('/mode_rgb')
def mode_rgb():
    global current_mode
    with lock:
        current_mode = freenect.VIDEO_RGB
    return '', 204

# --- Esecuzione Principale ---
if __name__ == '__main__':
    ctx = None
    try:
        # Inizializza il contesto e il dispositivo in modo sicuro
        ctx = freenect.init()
        device = freenect.open_device(ctx, 0)
        if not device:
            raise RuntimeError("Error: Could not open device. Is Kinect connected and drivers installed?")
            
        print("Kinect device opened successfully.")
        freenect.set_led(device, freenect.LED_GREEN) # LED verde per indicare che è pronto

        # Avvia il thread in background per il Kinect
        k_thread = threading.Thread(target=kinect_thread)
        k_thread.daemon = True  # Permette di chiudere il programma anche se il thread è in esecuzione
        k_thread.start()

        # Avvia l'app Flask (la modalità threaded è fondamentale!)
        app.run(host='0.0.0.0', port=5000, threaded=True)

    except Exception as e:
        print(e)
    finally:
        # Questa parte viene eseguita quando fermi lo script (es. con Ctrl+C)
        print("Shutting down...")
        if device:
            freenect.set_led(device, freenect.LED_RED)
            freenect.close_device(device)
        if ctx:
            freenect.shutdown(ctx)
        print("Shutdown complete.")