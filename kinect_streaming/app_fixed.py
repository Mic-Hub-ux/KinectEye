import freenect
import cv2
import numpy as np
from flask import Flask, render_template, request, Response

app = Flask(__name__)

# Global variables
ctx = freenect.init()
# We do NOT open the device here for tilt. 
# We will use the sync functions or open/close briefly to avoid USB conflicts.

# Default mode
current_fmt = freenect.VIDEO_RGB



def get_video():
    """Helper to handle IR vs RGB data fetching"""
    global current_fmt
    
    # freenect.sync_get_video returns (data, timestamp)
    # The second argument is the format (0 for RGB, 2 for IR_8BIT)
    image, _ = freenect.sync_get_video(0, current_fmt)
    
    if current_fmt == freenect.VIDEO_RGB:
        # OpenCV uses BGR, Kinect gives RGB. Convert it.
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    elif current_fmt == freenect.VIDEO_IR_8BIT:
        # IR comes in as a single channel, usually looks fine as is, 
        # but grayscale conversion ensures compatibility.
        # Sometimes normalization helps visibility.
        pass 
        
    return image

def gen():
    while True:
        try:
            # Get frame based on current global format
            frame = get_video()

            if frame is None:
                continue

            # Convert to JPEG
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
                
            frame_bytes = jpeg.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
        except Exception as e:
            print(f"Error in video loop: {e}")
            break

@app.route('/')
def index():
    # REQUIRED: Route to serve the HTML file
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_tilt', methods=['POST'])
def set_tilt():
    tilt_action = request.form.get('tilt')
    
    # NOTE: Opening the device strictly for the motor command 
    # and closing it immediately helps avoid conflicts with the video stream.
    try:
        dev = freenect.open_device(ctx, 0)
        
        if tilt_action == 'up':
            freenect.set_tilt_degs(dev, 20) 
        elif tilt_action == 'down':
            freenect.set_tilt_degs(dev, -20)
        elif tilt_action == 'reset':
            freenect.set_tilt_degs(dev, 0)
            
        freenect.close_device(dev)
    except Exception as e:
        print(f"Tilt Error: {e}")
    
    return '', 204

@app.route('/mode_ir')
def mode_ir():
    global current_fmt
    current_fmt = freenect.VIDEO_IR_8BIT
    print("Switched to IR Mode")
    return '', 204

@app.route('/mode_rgb')
def mode_rgb():
    global current_fmt
    current_fmt = freenect.VIDEO_RGB
    print("Switched to RGB Mode")
    return '', 204

if __name__ == '__main__':
    # Threaded=True is usually required for streaming + controls
    app.run(host='0.0.0.0', port=5000, threaded=True)