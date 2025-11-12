# Basic Kinect Commands

When you launch `freenect-glview`, you can control the Kinect sensor directly from your keyboard.  
Below is the complete list of available commands.

---
## Movement and Tilt

| Key | Action | Notes |
|-----|---------|-------|
| **w** | Tilt up (+5°) | Increases camera angle upward |
| **x** | Tilt down (−5°) | Decreases camera angle downward |
| **s** | Reset tilt | Centers the motor position to 0° |

---
## LED CONTROL

| Key | Action (changes LED behavior)|
|-----|--------|
| **0** |LED OFF |
| **1**|Green|
|**2**| Red|
|**3**|Orange|
|**4**|Flashing Green|
|**5**|Flashing Red|
|**6**|Red/Green alternation|

---

## Video and Depth Modes

| Key | Action | Description |
|-----|---------|-------------|
| **m** | Toggle video format | Switch between RGB / IR video modes |
| **n** | Enable near mode *(Kinect for Windows only)* | Activates near-depth mode |
| **r** | Raw color mode | Shows raw RGB feed |
| **b** | White balance mode | Adjusts color balance automatically |

---

## Tips

- If packets are lost (`Invalid magic` or `Lost packets`), try reconnecting the sensor or using a powered USB port.
- The **accelerometer values** are shown on-screen whenever the tilt is changed.

---
