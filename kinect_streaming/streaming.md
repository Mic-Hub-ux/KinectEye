## Overview

The **Kinect streaming system** allows capturing the video feed from the Kinect V1 sensor, processing it, and transmitting it in real time through a web server. Using **Flask** and **OpenCV**, the video data can be displayed directly in the browser — currently only in local mode.

## Main Features

- **Video Streaming**: Real-time acquisition and display of video streams from the Kinect. (**AVAILABLE**)  
- **Motor Control**: Adjusting the Kinect tilt angle through web commands. (**IN DEVELOPMENT**)  
- **Depth and RGB Support**: Visualization of both RGB and depth data. (**IN DEVELOPMENT**)

## Starting the Stream

To start the video streaming server, run the following Python script:

```bash
python3 app.py
```
Then open a web browser and enter:
```bash
http://localhost:5000
```
Note:
This script currently includes only Video Streaming — motor control and depth/RGB support are not yet implemented.