# KinectEye
# Kinect V1 Remote Surveillance System (Linux + Python)

This repository contains the full setup and implementation of a **remote surveillance system** using a **Microsoft Kinect V1** sensor connected to a **Linux (Lubuntu 24.04)** computer.  
The project enables **local visualization**, **motor control**, and **remote video streaming** via a lightweight Python Flask server.

---

## Project Overview

| Component | Description |
|------------|-------------|
| **Kinect V1** | RGB + Depth sensor with tilt motor and microphone array |
| **OS** | Lubuntu 24.04 LTS (clean install) |
| **Drivers** | libfreenect (open-source driver for Kinect V1) |
| **Language** | Python 3.12 |
| **Main Libraries** | `libfreenect`, `opencv-python`, `numpy`, `flask` |
| **Goal** | Local and remote visualization of the Kinect video stream + tilt motor control |

---
## Hardware required
**Kinect V1** <br>
**Linux computer** <br>
**Kinect AC Adapter with USB supply** available on: [Amazon](https://www.amazon.it/dp/B0776NDZJ6?ref=ppx_yo2ov_dt_b_fed_asin_title) <br>

---
## Installation & First Run

Follow these commands step-by-step to set up the environment and visualize the Kinect RGB + Depth streams.

### 1️⃣ System update
```bash
sudo apt update
sudo apt upgrade -y
```
### 2️⃣ Base tools and Python environment
```bash
sudo apt install -y build-essential cmake git python3-pip python3-opencv python3-numpy
```
### 3️⃣ Enable required repositories

If you get “Unable to locate package” errors:
```bash
sudo apt install -y software-properties-common
sudo add-apt-repository -y universe
sudo add-apt-repository -y multiverse
sudo apt update
```

### 4️⃣ Install Kinect drivers (libfreenect)
```bash
sudo apt install -y libusb-1.0-0-dev libfreenect0.5 libfreenect-dev libfreenect-bin
```
### 5️⃣ Install Python binding for libfreenect
Ubuntu 24.04+ restricts system Python writes; use this flag:
```bash
pip3 install freenect --break-system-packages
```
### 6️⃣ Check device detection
```bash
lsusb | grep -i microsoft
dmesg | tail -n 20
```
You should see entries like 045e:02ad, 045e:02ae, or 045e:02b0.

### 7️⃣ Test native viewer
```bash
sudo freenect-glview
```

Two windows appear:

RGB (color feed)

Depth (false-color depth map)
Close with ESC or q.

---
