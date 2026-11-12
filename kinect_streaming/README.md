## Overview

The **Kinect streaming system** captures the video feed from the Kinect V1 sensor and streams it in real time to any browser on the local network, using **Flask** and **OpenCV**. From the same page you can move the tilt motor and switch the video mode.

A single background thread owns the Kinect (libfreenect context + device): it runs the event loop, encodes each frame to JPEG once and executes the tilt / mode commands sent by the web page. This avoids the USB conflicts (`LIBUSB_ERROR_BUSY`) of the older versions and lets several browsers watch at the same time.

## Main Features

- **Video Streaming**: real-time MJPEG stream, shared by all viewers. (**AVAILABLE**)
- **Motor Control**: tilt in 5° steps, limited to the hardware range of ±27°. (**AVAILABLE**)
- **Video modes**: Color (RGB), Infrared and Depth. (**AVAILABLE**)
- **Web UI**: HUD overlay (mode, clock, tilt, fps), tilt gauge, snapshot download, fullscreen, dark/light theme, phone-friendly layout. (**AVAILABLE**)

## Requirements

Complete the setup first → [setup/setup_instructions.md](../setup/setup_instructions.md).
In particular the `gspca_kinect` kernel driver must be disabled, otherwise the camera is busy and the app crashes.

## Starting the Stream

From the repository root:

```bash
python3 kinect_streaming/app.py
```
(if you used `setup/install.sh`: `.venv/bin/python kinect_streaming/app.py`)

At startup the server prints the addresses to use:
```
KinectEye running on:
  http://localhost:5000
  http://<LAN IP>:5000  (other devices on the same network)
```
Open `http://localhost:5000` on the Kinect computer, or the LAN address from a phone / PC on the same network. Find the LAN IP with `hostname -I` (it depends on the computer and the network).

Options:

| Option | Default | Description |
|--------|---------|-------------|
| `--port` | `5000` | HTTP port |
| `--host` | `0.0.0.0` | address to listen on (`127.0.0.1` = this computer only) |
| `--quality` | `80` | JPEG quality 1-100 (lower = less bandwidth) |

Stop the server with `Ctrl+C`.

## Keyboard shortcuts (in the web page)

| Key | Action |
|-----|--------|
| **↑ / ↓** | Tilt up / down by 5° |
| **R** | Reset tilt to 0° |
| **1 / 2 / 3** | Color / Infrared / Depth mode |
| **S** | Download a snapshot |
| **F** | Fullscreen |

## HTTP API

| Method | Path | Body (JSON) | Description |
|--------|------|-------------|-------------|
| GET | `/video_feed` | — | MJPEG stream |
| GET | `/api/status` | — | current mode, tilt and limits |
| POST | `/api/tilt` | `{"action": "up" \| "down" \| "reset"}` | move the motor |
| POST | `/api/mode` | `{"mode": "rgb" \| "ir" \| "depth"}` | change video mode |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `LIBUSB_ERROR_BUSY` + `Segmentation fault` | `gspca_kinect` is loaded or another program (e.g. `freenect-glview`) is using the Kinect. See setup step 5. |
| `NO SIGNAL` in the page | Kinect not connected or not powered: check `lsusb \| grep -i microsoft`. |
| Works only with `sudo` | udev rules missing, see setup step 6. |
