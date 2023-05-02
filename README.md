# Walabot 3D Cool Tool
An OpenGL 3D voxel graphic visualizer for the Walabot
### What is the Walabot?
The Walabot is a USB radar device with a phased array antenna.
https://cdn.sparkfun.com/assets/learn_tutorials/7/2/4/walabot-tech-brief-416.pdf
The scan results can be accessed via a Python API:
https://api.walabot.com/
### What is the Walabot 3D Cool Tool?
The Walabot 3D Cool Tool was made for:
1. visualizing the Walabot output in a graphically pleasing way
2. using the Walabot for detecting and marking objects

### How does it Work?
##### Point Cloud
The Walabot 3D Cool Tool lets the Walabot generate a *point cloud*. This is an array of "reflection intensities" of spatial points from a scan area in front of the Walabot. This scan area can exactly configured: 180° maximum angle spread on the x- and y-axis, a range spread from one centimeter to 10 meters. The resolution can be set to as little as one milimeter. Accordingly, a point cloud can contain just a handful of elements, or tens of thousands.

The Walabot 3D Cool Tool now takes the point cloud and displays it in 3D, each point inked in a color that represents its reflection intensity (heat map).

##### Object Dectection
Also, the Walabot 3D Cool Tool uses a cluster search algorithm to find objects (agglomerations of points with high reflection intensities). It marks them and tracks them over time, allowing you to make more sense of the radar echos, which can otherwise be quite confusing.
![object_detection](https://user-images.githubusercontent.com/39830230/235746023-08709ddf-d785-42fc-931a-aa523556c4cf.png)
### How to Use?
As soon as the Walabot 3D Cool Tool runs, it waits until you connect the Walabot to your computer. Once detected, it begins to fetch data and to display it as a voxel graphic. You can now:

- Move and rotate the camera with **mouse, arrow keys, WASD and PgUp/PgDn**
- Enlarge the scan area with **H, V, R** (horizontal, vetical, range)
- Shrink down the scan area with **SHIFT - H, V, R**
- Alter the resolution with **CTRL - (SHIFT) - H, V, R**
- Calibrate the Walabot by pressing **SPACE**
- Turn on/off _Sensor Targets_, Walabot's hardware object detection, with **T**
- Switch to object detection mode, by hitting **TAB**
- Alter the object detection threshold with **(SHIFT) - C**

### Requirementes
The Walabot 3D Cool Tool uses pygame, pyopengl and the walabot api package.
The Walabot API doesn't work on Macs.

_Martin Hüdepohl_
