"""KinectEye - live Kinect V1 streaming with tilt and mode control over the LAN.

A single background thread owns the Kinect (libfreenect context + device).
It runs the libfreenect event loop, encodes every frame to JPEG once and
executes the commands (tilt / mode change) queued by the web handlers.
Flask threads only read the latest JPEG, so any number of browsers can watch
without fighting over the USB device.
"""

import argparse
import queue
import socket
import threading
import time

import cv2
import freenect
import numpy as np
from flask import Flask, Response, jsonify, render_template, request

MODES = ("rgb", "ir", "depth")
TILT_MIN, TILT_MAX, TILT_STEP = -27, 27, 5  # hardware limit is about +/-27 degrees
RECONNECT_DELAY = 2.0  # seconds between attempts to (re)open the Kinect


class Kinect:
    """Owns the Kinect device in a dedicated thread."""

    def __init__(self, jpeg_quality=80):
        self.jpeg_quality = jpeg_quality
        self.mode = "rgb"
        self.tilt = 0
        self.connected = False
        self.error = "Starting..."
        self.fps = 0.0

        self._commands = queue.Queue()
        self._frame = None
        self._frame_id = 0
        self._frame_cond = threading.Condition()
        self._fps_count = 0
        self._fps_since = time.monotonic()
        self._running = True
        self._thread = threading.Thread(target=self._run, name="kinect", daemon=True)

    # ------------------------------------------------------------------ public API
    # Called from Flask threads: never touch the device here, only queue commands.

    def start(self):
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join(timeout=5)

    def set_mode(self, mode):
        self._commands.put(("mode", mode))

    def tilt_step(self, action):
        if action == "up":
            target = self.tilt + TILT_STEP
        elif action == "down":
            target = self.tilt - TILT_STEP
        else:
            target = 0
        target = max(TILT_MIN, min(TILT_MAX, target))
        self.tilt = target
        self._commands.put(("tilt", target))
        return target

    def status(self):
        return {
            "connected": self.connected,
            "error": self.error,
            "mode": self.mode,
            "tilt": self.tilt,
            "tilt_min": TILT_MIN,
            "tilt_max": TILT_MAX,
            "fps": round(self.fps, 1),
        }

    def frames(self):
        """Yield every new JPEG frame (blocks until one is available)."""
        last_id = -1
        while self._running:
            with self._frame_cond:
                self._frame_cond.wait_for(lambda: self._frame_id != last_id, timeout=1.0)
                if self._frame_id == last_id or self._frame is None:
                    continue
                last_id, frame = self._frame_id, self._frame
            yield frame

    # --------------------------------------------------------------- kinect thread

    def _run(self):
        while self._running:
            ctx = freenect.init()
            dev = freenect.open_device(ctx, 0) if ctx else None
            if not dev:
                self.connected = False
                self.error = "Kinect not found: is it plugged in and powered?"
                if ctx:
                    freenect.shutdown(ctx)
                time.sleep(RECONNECT_DELAY)
                continue

            self.connected, self.error = True, None
            print("Kinect opened.")
            try:
                self._loop(ctx, dev)
            except Exception as exc:  # keep the server alive, retry later
                self.error = f"Kinect error: {exc}"
                print(self.error)
            finally:
                self.connected = False
                self._stop_streams(dev)
                freenect.set_led(dev, freenect.LED_RED)
                freenect.close_device(dev)
                freenect.shutdown(ctx)
            if self._running:
                if self.error is None:
                    self.error = "Kinect disconnected"
                print(f"{self.error}, retrying...")
                time.sleep(RECONNECT_DELAY)

    def _loop(self, ctx, dev):
        freenect.set_video_callback(dev, self._on_video)
        freenect.set_depth_callback(dev, self._on_depth)
        freenect.set_led(dev, freenect.LED_GREEN)
        freenect.set_tilt_degs(dev, self.tilt)
        self._start_stream(dev, self.mode)

        while self._running:
            if freenect.process_events(ctx) < 0:
                self.error = "USB error (Kinect unplugged?)"
                return
            self._run_commands(dev)

    def _run_commands(self, dev):
        while True:
            try:
                cmd, value = self._commands.get_nowait()
            except queue.Empty:
                return
            if cmd == "tilt":
                freenect.set_tilt_degs(dev, value)
            elif cmd == "mode" and value != self.mode:
                self._stop_streams(dev)
                self._start_stream(dev, value)
                self.mode = value
                print(f"Mode: {value}")

    @staticmethod
    def _start_stream(dev, mode):
        # Only one stream at a time: it halves the USB bandwidth and the
        # Kinect cannot send RGB and IR together anyway.
        if mode == "depth":
            freenect.set_depth_mode(dev, freenect.RESOLUTION_MEDIUM, freenect.DEPTH_11BIT)
            freenect.start_depth(dev)
        else:
            fmt = freenect.VIDEO_RGB if mode == "rgb" else freenect.VIDEO_IR_8BIT
            freenect.set_video_mode(dev, freenect.RESOLUTION_MEDIUM, fmt)
            freenect.start_video(dev)

    @staticmethod
    def _stop_streams(dev):
        freenect.stop_video(dev)
        freenect.stop_depth(dev)

    # The arrays passed to the callbacks point into libfreenect's buffers,
    # so they are encoded immediately and never kept.

    def _on_video(self, dev, data, timestamp):
        if data.ndim == 3:
            data = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
        self._publish(data)

    def _on_depth(self, dev, data, timestamp):
        # 11-bit raw depth: 2047 = no reading. Near = warm colors, far = cold.
        invalid = data >= 2047
        gray = 255 - (np.clip(data, 0, 1023) >> 2).astype(np.uint8)
        image = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
        image[invalid] = 0
        self._publish(image)

    def _publish(self, image):
        ok, jpeg = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
        if not ok:
            return
        with self._frame_cond:
            self._frame = jpeg.tobytes()
            self._frame_id += 1
            self._frame_cond.notify_all()

        self._fps_count += 1
        now = time.monotonic()
        if now - self._fps_since >= 1.0:
            self.fps = self._fps_count / (now - self._fps_since)
            self._fps_count, self._fps_since = 0, now


app = Flask(__name__)
kinect = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    def stream():
        for jpeg in kinect.frames():
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"

    return Response(stream(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/status")
def api_status():
    return jsonify(kinect.status())


@app.route("/api/tilt", methods=["POST"])
def api_tilt():
    action = (request.get_json(silent=True) or {}).get("action")
    if action not in ("up", "down", "reset"):
        return jsonify(error="action must be up, down or reset"), 400
    kinect.tilt_step(action)
    return jsonify(kinect.status())


@app.route("/api/mode", methods=["POST"])
def api_mode():
    mode = (request.get_json(silent=True) or {}).get("mode")
    if mode not in MODES:
        return jsonify(error=f"mode must be one of {', '.join(MODES)}"), 400
    kinect.set_mode(mode)
    return jsonify(kinect.status() | {"mode": mode})


def lan_ip():
    """Best guess of this machine's LAN address (no packet is actually sent)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def main():
    parser = argparse.ArgumentParser(description="KinectEye web server")
    parser.add_argument("--host", default="0.0.0.0", help="address to listen on (default: all interfaces)")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--quality", type=int, default=80, help="JPEG quality 1-100 (default: 80)")
    args = parser.parse_args()

    global kinect
    kinect = Kinect(jpeg_quality=args.quality)
    kinect.start()

    print(f"KinectEye running on:\n  http://localhost:{args.port}\n  http://{lan_ip()}:{args.port}  (other devices on the same network)")
    try:
        app.run(host=args.host, port=args.port, threaded=True)
    finally:
        kinect.stop()


if __name__ == "__main__":
    main()
