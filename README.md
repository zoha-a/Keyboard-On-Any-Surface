# Keyboard On Any Surface
A very common physical limitation is that keyboards require a separate hardware device in PCs and an integrated one in laptops, which make them bulky. What if your laptop came with a camera that automatically creates the surface beneath it into a keyboard?

Computer Vision allows us to completely change that. By leveraging computer vision techniques in a Raspberry Pi 4 with Camera module, the system detects and tracks finger movements on a surface, enabling users to type without a physical keyboard. The project integrates image processing algorithms to recognize gestures and translate them into text inputs, providing a novel, touch-free typing solution. This technology has potential applications in accessibility, gaming, and interactive installations.

If you run into any problems, or have suggestions for improving the design, assembly, or code to run the camera, please feel free to open an issue.

## Parts required
- Raspberry Pi 4 model B (2 GB RAM or better)
- Raspberry Pi Camera Module 3 (Other camera modules should work too!)
- SanDisk Extreme 64GB microSD card
- Paper printout of a keyboard

## Step 1: Raspberry Pi OS Setup
Flash the latest version of Raspberry Pi OS (64-bit preferred) to a fresh microSD card, and insert the microSD card (at least 64GB) into your Pi, and boot it up. I configured over SSH using PuTTY and RealVNC Viewer. Run the following commands on your PuTTY after booting:
```
sudo apt-get update
```
```
sudo apt-get install realvnc-vnc-server realvnc-vnc-viewer
```
```
ifconfig
```
```
check wlan0 inet address
```
```
sudo raspi-config
```
Then, go to Interface Options and select Enable VNC. Add your hostname.local on VNC Viewer. On VNC Viewer, run:
```
sudo apt update
```
```
sudo apt install python3-picamzero
```
This will save a video from your Pi Camera to your desktop.
```
rpicam-still -o ~/Desktop/image.jpg
```
This will save a video of 10,000 milliseconds.
```
rpicam-vid -t 10000 --codec libav --libav-format mp4 -o ~/Desktop/video.mp4
```

## Step 2: Print Out The Keyboard
Print out the jpg file titled Keyboard.
![Keyboard](https://github.com/user-attachments/assets/4c6eb456-a976-47c2-bce3-9709ba35b8dc)

## Step 3: Run The Code
Lastly, it is time to test the code. Either set up the camera facing the printout, run the .py file on your Raspberry Pi OS. Or you can film a video typing out anything and run the video in the .py file.

## License
GPL-3.0

## Author
[Zoha Ahmed](https://github.com/zoha-a)
