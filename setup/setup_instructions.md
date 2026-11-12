## Installation & First Run

Follow these commands step-by-step to set up the environment and visualize the Kinect RGB + Depth streams.

> Run the commands in a normal terminal. Do **not** prefix them with `!`: in bash `!` negates the exit status, so `! cmd1 && cmd2` silently skips `cmd2`.

### 1️⃣ System update
```bash
sudo apt update
sudo apt upgrade -y
```
If apt says *"Could not get lock /var/lib/dpkg/lock-frontend … held by process … (unattended-upgr)"*, the automatic updates are running in the background: wait a few minutes until they finish.

### 2️⃣ Enable required repositories

If you get “Unable to locate package” errors:
```bash
sudo apt install -y software-properties-common
sudo add-apt-repository -y universe
sudo add-apt-repository -y multiverse
sudo apt update
```

### 3️⃣ Base tools, Python libraries and Kinect drivers (libfreenect)
```bash
sudo apt install -y build-essential cmake git python3-pip python3-dev cython3 \
    python3-opencv python3-numpy python3-flask \
    libusb-1.0-0-dev libfreenect0.5 libfreenect-dev libfreenect-bin
```

### 4️⃣ Install Python binding for libfreenect
Ubuntu 24.04+ restricts system Python writes; use this flag:
```bash
pip3 install freenect --break-system-packages
python3 -c "import freenect, cv2, numpy, flask; print('all OK')"
```
Alternative (isolated virtualenv, builds the binding from the libfreenect sources):
```bash
./setup/install.sh
```
In that case start the server with `.venv/bin/python kinect_streaming/app.py`.

### 5️⃣ Disable the kernel webcam driver (`gspca_kinect`) ⚠️
Ubuntu ships a kernel driver that grabs the Kinect camera as a generic webcam (`/dev/videoX`).
While it is loaded, libfreenect cannot open the camera and the app fails with:
```
Failed to claim camera interface: LIBUSB_ERROR_BUSY
Segmentation fault (core dumped)
```
Unload it now and blacklist it so it is not loaded again at boot:
```bash
sudo modprobe -r gspca_kinect
echo "blacklist gspca_kinect" | sudo tee /etc/modprobe.d/blacklist-kinect.conf
```
Check: `lsmod | grep gspca_kinect` must print nothing.

### 6️⃣ USB permissions (run without sudo)
```bash
sudo tee /etc/udev/rules.d/66-kinect.rules > /dev/null <<'EOF'
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02b0", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ad", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ae", MODE="0666"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```
Then unplug and replug the Kinect USB cable.

### 7️⃣ Check device detection
Connect the Kinect power adapter first, then the USB cable.
```bash
lsusb | grep -i microsoft
dmesg | tail -n 20
```
You should see three entries: 045e:02b0 (motor), 045e:02ad (audio) and 045e:02ae (camera).

### 8️⃣ Test native viewer
```bash
freenect-glview
```

Two windows will appear (RGB and depth). Keyboard commands → [basic_commands.md](basic_commands.md).

### 9️⃣ Start the web app
→ [kinect_streaming/README.md](../kinect_streaming/README.md)

---
