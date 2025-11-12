# KinectEye

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
| **Goal** | Local and remote visualization of the Kinect video stream |

---
## Hardware required
**Kinect V1** <br>
**Linux computer** <br>
**Kinect AC Adapter with USB supply** available on [Amazon](https://www.amazon.it/dp/B0776NDZJ6?ref=ppx_yo2ov_dt_b_fed_asin_title) <br>

---
For the detailed installation procedure → [setup/setup_instructions.md](setup/setup_instructions.md)
<br>
For basic commands available after installation → [setup/basic_commands.md](setup/basic_commands.md)

