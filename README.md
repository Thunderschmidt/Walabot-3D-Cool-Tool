# Walabot 3D Cool Tool
An OpenGL 3D voxel graphic visualizer for the Walabot

![walaphoto](https://user-images.githubusercontent.com/39830230/236703648-03760324-b672-4137-96d1-289086614597.png)


![screens](https://user-images.githubusercontent.com/39830230/235932224-c9dcb5e5-7da8-4041-aad0-304647196038.png)



### What is the Walabot?
The Walabot is a USB radar device with a phased array antenna:

https://cdn.sparkfun.com/assets/learn_tutorials/7/2/4/walabot-tech-brief-416.pdf

The Walabot's scan results can be accessed via a Python API:

https://api.walabot.com/



### What is the Walabot 3D Cool Tool?
The Walabot 3D Cool Tool was made for:
1. visualizing the Walabot output in a graphically pleasing way
2. using the Walabot for detecting, marking and tracking objects

### How does it Work?
#### Point Cloud
The Walabot 3D Cool Tool lets the Walabot generate a *point cloud*. A point cloud is an array of "reflection intensities" of spatial points from a scan area in front of the Walabot. How big this scan area is and how densely it is filled with points can be exactly configured: A Walabot point cloud can contain just a handful of elements, or thousands. The bigger the point cloud, the lower the frame rate.

The maximal scan area the Walabot can is a hemisphere of 10 meters radius in the direction of its antenna array. The Walabot can measure the reflection intensities of 100.000 points two or three times a second or some thousand points up to 20 times a second. Its finest range resolution is at 1 milimeter.

https://www.youtube.com/watch?v=S_Uthvuah8U

The Walabot 3D Cool Tool takes the point cloud and displays it in 3D, each point inked in a color that represents its reflection intensity (heat map).

#### Object Dectection
Also, the Walabot 3D Cool Tool uses a cluster search algorithm to find objects (agglomerations of points with high reflection intensities). It marks them, gives them a identity and tracks them over time. 

### How to Use?
As soon as the Walabot 3D Cool Tool runs, it waits until you connect the Walabot USB Device to your computer. Once detected, it begins to fetch data and to display it as a voxel graphic. You can now:

- Move and rotate the camera with **mouse, arrow keys, WASD and PgUp/PgDn**
- Enlarge the scan area with **H, V, R** (horizontal, vetical, range)
- Shrink down the scan area with **SHIFT - H, V, R**
- Alter the resolution with **CTRL - (SHIFT) - H, V, R**
- Calibrate the Walabot by pressing **SPACE**
- Turn on/off "Sensor Targets" (hardware object detection) with **T**
- Switch to object detection mode, by hitting **TAB**
- Alter the object detection threshold with **(SHIFT) - C**
- Switch the voxel shape ⬜/⚪with **Q**



### Requirementes
The Walabot 3D Cool Tool uses pygame, pyopengl and the walabot api package.
The Walabot API doesn't work on Mac computers.

_Martin Hüdepohl_
