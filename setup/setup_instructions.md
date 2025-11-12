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

Two windows will appear...

---