# Bounding box annotation tool
This repository implements a bounding box annotation tool

## Requirements
pytorch (preferably with cuda)
ultralytics
pynput
opencv
numpy

## Setup
Make sure to add your images (your zip file) to the 'captured images' folder, and rename it to 'data'
Also, install all dependencies
Now you can run the main.py file

## Interface
**First** step is to check / draw the bounding boxes. 
A model is supplied that suggests bounding boxes.

The two steps below can be repeated until you press 'enter' when all bounding boxes are visible (which means you are done and can go to the classification step!)
 - Look at the results: press 'e' to edit
 - When done or when you want to check, press 'esc'
    To draw a bounding box, press your middle mouse button (wheel). To zoom in, roll the middel mouse button (wheel)


The **second** step is to classify each bounding box
Use the left and right arrows to switch between selected labels, the selected label is visualized in the terminal
Press 'enter' to label selected bounding box with the selected label
Press 'c' to not assign a label (= faulty bounding box)
Press 'z' to undo your previous label, if you made a mistake
Press 'esc' to finish the annotation early when you are sure the other bounding boxes are faulty