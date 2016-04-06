
#About

This is an add-on for [Blender](https://www.blender.org/) (an open source 3D modeling program) which exports models in a file format which I created to load models into my [game engine](https://github.com/adeshar00/GameEngine).  It's pretty limited at the moment; so far it just stores vertex and triangle data (no animation or texture or normal data yet), but it's relatively easy to parse, and it's compact compared to plaintext formats like .obj.


#How to use it

To download Blender on a Debian system, run the following command:

```
sudo apt-get install blender
```

To set up the add-on in Blender:
* Change one of the windows to "user preferences" mode
* Click on the "Add-ons" tab at the top of the window
* Click the "Install from File" button at the bottom
* Select the "export.py" file and install it
* Click on the "Import-Export" button on the left
* Find the bar in the middle that says "Import-Export: CSMF Exporter", and click on the checkbox at the far right side of it

Now, if you go to "File > Export", there should be an option to export as a Compact Simple Model File.

(Note: the game engine parser currently ignores files with multiple objects, as well as translation rotation and scale data)


#Format

The data is stored as a series of fixed-point numbers and unsigned integers, each number being represented with two bytes.  Fixed-point numbers can represent anything within the range of -128 to 128 with a precision of 1/256; unsigned integers can represent any integer within the range of 0 to ~65k.  Both types are little-endian.

First 2 bytes are a uint for the object count  
Per object:  
&nbsp;&nbsp;2 byte uint for the vertex count   
&nbsp;&nbsp;2 byte uint for the triangle count  
&nbsp;&nbsp;6 bytes for object translations (2 byte fixed-point number per x, y, and z)  
&nbsp;&nbsp;6 bytes for object rotation (2 byte fixed-point number per pitch, yaw, roll)  
&nbsp;&nbsp;6 bytes for object scale (2 byte fixed-point number per x, y, and z)  
&nbsp;&nbsp;Per vertex:  
&nbsp;&nbsp;&nbsp;&nbsp;2 byte fixed-point number for x coordinate  
&nbsp;&nbsp;&nbsp;&nbsp;2 byte fixed-point number for y coordinate  
&nbsp;&nbsp;&nbsp;&nbsp;2 byte fixed-point number for z coordinate  
&nbsp;&nbsp;Per triangle:  
&nbsp;&nbsp;&nbsp;&nbsp;2 byte uint for index of first vertex  
&nbsp;&nbsp;&nbsp;&nbsp;2 byte uint for index of second vertex  
&nbsp;&nbsp;&nbsp;&nbsp;2 byte uint for index of third vertex  
