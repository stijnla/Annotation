from ultralytics import YOLO
import cv2
import os
import copy
from pynput import keyboard
import torch
import numpy as np


class Keyboard_interpreter():
    def __init__(self):

        self.listener = keyboard.Listener(
                    on_press=self.on_press,
                    on_release=self.on_release)
        

        self.command = []

        self.listener.start()

    def on_press(self, key):
        try:
            if key.char == 'z':
                self.command.append('z')
            if key.char == 'c':
                self.command.append('c')    
            if key.char == 'e':
                self.command.append('e')

        except AttributeError:
            if key == keyboard.Key.esc:
                self.command.append('esc')
            if key == keyboard.Key.left:
                self.command.append('left')
            if key == keyboard.Key.right:
                self.command.append('right')
            if key == keyboard.Key.enter:
                self.command.append('enter')
            

    def on_release(self, key):
        pass
            

    def join(self):
        self.listener.join()

    def stop(self):
        self.listener.stop()

    def get_command(self):
        command = self.command
        self.command = [] # empty command queue
        return command
    


class Bounding_box_classification_annotation_tool:

    def __init__(self, path_to_model, image, name, classes):
        # Load YOLO model trained for 10 epochs on SKU-110K-VS dataset
        self.model = YOLO(path_to_model)

        # Get all images that need annotation
        self.image = image

        self.classes = classes
        self.classified_bounding_boxes = []
        self.selected_label = 0
        
        # load keyboard interpreter
        self.keyboard_interpreter = Keyboard_interpreter()
        self.undo = False
        self.done = False
        self.name = name


    @staticmethod
    def update_image_screen(image):
        cv2.imshow('Image screen', image)
        # resizee here as well
        cv2.waitKey(1)

    @staticmethod
    def update_bounding_box_screen(image, bounding_box):
        cv2.imshow('Bounding Box Screen', cv2.resize(image[int(bounding_box[1]):int(bounding_box[3]), int(bounding_box[0]):int(bounding_box[2])], [3*(int(bounding_box[2]) - int(bounding_box[0])), 3*(int(bounding_box[3]) - int(bounding_box[1]))]))
        # resize here as well
        cv2.waitKey(1)
    
    def classify_bounding_box(self, image, bounding_box):
        
        image_with_current_bounding_box = cv2.imread(image)
        cv2.rectangle(image_with_current_bounding_box, (int(bounding_box[0]), int(bounding_box[1])), (int(bounding_box[2]), int(bounding_box[3])), (0,0,255), 2)
        
        
        self.update_image_screen(image_with_current_bounding_box)
        self.update_bounding_box_screen(cv2.imread(image), bounding_box)
        
        command = self.keyboard_interpreter.get_command()
        if len(command) > 0:
            if command[0] == 'enter':
                return self.selected_label, False

            if command[0] == 'c':
                return None, False
            
            if command[0] == 'right':
                if self.selected_label < len(self.classes) - 1:
                    self.selected_label = self.selected_label + 1
                else:
                    self.selected_label = 0
            if command[0] == 'left':
                if self.selected_label == 0:
                    self.selected_label = len(self.classes) - 1
                else:
                    self.selected_label = self.selected_label - 1
            if command[0] == 'esc':
                self.done = True

            if command[0] == 'z':
                self.undo = True

        return None, True
        

        

    def get_bounding_boxes_image(self, image):
        # Perform object detection on an image using the model
        results = self.model.predict(source=image, show=False, save=False)

        # Get bounding boxes defined as (x, y, widht, height)
        bounding_boxes_normalized = results[0].boxes.xywhn
        bounding_boxes = results[0].boxes.xyxy


        return bounding_boxes.cpu().numpy(), bounding_boxes_normalized.cpu().numpy()

    def classify_bounding_boxes_image(self, image):
        

        bounding_box_index = 0

        while bounding_box_index < len(self.bounding_boxes_xyxy):
            
            if self.done:
                    break
            
            
            
            object_class_not_determined = True
            previous_selected_label = None
            while object_class_not_determined:


                if previous_selected_label != self.selected_label:
                    print('                                                                           ', end='\r', flush=True)
                    print('selected label: "' + str(self.classes[self.selected_label]).replace('\n', '') + '"', end='\r', flush=True)
                
                bounding_box = self.bounding_boxes_xyxy[bounding_box_index]

                label, object_class_not_determined = self.classify_bounding_box(image, bounding_box)
                if self.undo:
                    if len(self.classified_bounding_boxes) > 0:
                        bounding_box_index = bounding_box_index - 1
                        self.classified_bounding_boxes.pop() # remove the latest label from list
                        self.undo = False
                    else:
                        self.undo = False

                if self.done:
                    break

            
            self.classified_bounding_boxes.append(label)
            # annotate the next bounding box
            bounding_box_index = bounding_box_index + 1




    def inspect_image_with_bounding_boxes(self, image):
        image_with_all_bounding_boxes = cv2.imread(image)
        for bounding_box in self.bounding_boxes_xyxy:
            cv2.rectangle(image_with_all_bounding_boxes, (int(bounding_box[0]), int(bounding_box[1])), (int(bounding_box[2]), int(bounding_box[3])), (0,0,255), 2)
        


        command = self.keyboard_interpreter.get_command()
        if len(command) > 0 and command[0] == 'e':
            # edit image bounding boxes
            editing = True

            while editing:
                editing = self.edit_image_bounding_boxes()


        if len(command) > 0 and command[0] == 'enter':
            return False
        
        self.update_image_screen(image_with_all_bounding_boxes)
        return True

    def edit_image_bounding_boxes(self):
        editing = True
        self.new_bounding_boxes = []
        editing = self.draw_new_bounding_box(editing)

        # add the new bounding boxes to the bounding boxes
        if len(self.new_bounding_boxes) > 0:
            self.bounding_boxes_xyxy = np.concatenate([self.new_bounding_boxes, self.bounding_boxes_xyxy])
         
        return editing

    def convert_xyxy_to_xywhn(self):
        image = cv2.imread(self.image)
        bounding_boxes_xywhn = []

        for bounding_box_xyxy in self.bounding_boxes_xyxy:
            
            width_normalized = (bounding_box_xyxy[2]-bounding_box_xyxy[0])/image.shape[1]
            height_normalized = (bounding_box_xyxy[3]-bounding_box_xyxy[1])/image.shape[0]

            x_normalized = (bounding_box_xyxy[0] + bounding_box_xyxy[2])/(2*image.shape[1])
            y_normalized = (bounding_box_xyxy[1] + bounding_box_xyxy[3])/(2*image.shape[0])

            bounding_box_xywhn = np.array([x_normalized, y_normalized, width_normalized, height_normalized])
            bounding_boxes_xywhn.append(bounding_box_xywhn)

        return np.array(bounding_boxes_xywhn, dtype=np.float32)
    
    
    def annotate(self):
        # TODO: inspect first, then later we should start to classify, 
        # TODO: inspect with ability to add bounding boxes with a clear view!
        self.bounding_boxes_xyxy, self.bounding_boxes_xywh_normalized = self.get_bounding_boxes_image(self.image)

        inspecting = True

        while inspecting:
            inspecting = self.inspect_image_with_bounding_boxes(self.image)

        self.classify_bounding_boxes_image(self.image)
        
        bounding_boxes_xywhn = self.convert_xyxy_to_xywhn()
        
        # convert to labels
        self.make_labels(bounding_boxes_xywhn)
        self.save_labels()
        #cv2.destroyAllWindows()



    def make_labels(self, bounding_boxes_xywhn):
        self.labels = []

        for i, classified_bounding_box in enumerate(self.classified_bounding_boxes):
            if classified_bounding_box != None:
                
                bounding_boxes = [round(coordinate, 5) for coordinate in bounding_boxes_xywhn[i].tolist()]
                bounding_boxes.insert(0, classified_bounding_box)
                label = ' '.join(str(e) for e in bounding_boxes) + '\n'
                self.labels.append(label)
        
      
    def save_labels(self): 
        with open(os.path.join(os.path.dirname(__file__), 'labels', str(self.name) + '.txt'), 'w') as f:
            f.writelines(self.labels)
            
    def contain_bounding_box_within_frame(self, x, y, image):
        # make sure bounding box stays within bounds
        # image shape openCV: (height, width, channels)
        if x < 0:
            x = 0
        elif x > image.shape[1]:
            x = image.shape[1]
        if y < 0:
            y = 0
        elif y > image.shape[0]:
            y = image.shape[0]
        
        return x, y

    def annotate_bounding_box(self, event, mouse_x, mouse_y, flags, param):
 
        # start drawing bounding box
        if event == cv2.EVENT_MBUTTONDOWN:
            self.drawing = True
            self.initial_bbox_x = mouse_x
            self.initial_bbox_y = mouse_y
            end_bbox_x = mouse_x
            end_bbox_y = mouse_y
        
        # check mouse while drawing bounding box
        if event == cv2.EVENT_MOUSEMOVE:
            if self.drawing == True:
                
                end_bbox_x = mouse_x
                end_bbox_y = mouse_y

                # contain bounding box within frame
                end_bbox_x, end_bbox_y = self.contain_bounding_box_within_frame(end_bbox_x, end_bbox_y, self.drawing_image)

        # stop drawing bounding box
        if event == cv2.EVENT_MBUTTONUP:
            
            
            end_bbox_x = mouse_x
            end_bbox_y = mouse_y

            
            # contain bounding box within frame
            end_bbox_x, end_bbox_y = self.contain_bounding_box_within_frame(end_bbox_x, end_bbox_y, self.drawing_image)

            # save annotation
            
            if end_bbox_x > self.initial_bbox_x and end_bbox_y > self.initial_bbox_y:
                new_bounding_box = np.array([self.initial_bbox_x, self.initial_bbox_y, end_bbox_x, end_bbox_y])
            elif end_bbox_x < self.initial_bbox_x and end_bbox_y > self.initial_bbox_y:
                new_bounding_box = np.array([end_bbox_x, self.initial_bbox_y, self.initial_bbox_x, end_bbox_y])
            elif end_bbox_x > self.initial_bbox_x and end_bbox_y < self.initial_bbox_y:
                new_bounding_box = np.array([self.initial_bbox_x, end_bbox_y, end_bbox_x, self.initial_bbox_y])
            else:
                new_bounding_box = np.array([end_bbox_x, end_bbox_y, self.initial_bbox_x, self.initial_bbox_y])
            self.new_bounding_boxes.append(new_bounding_box)
            self.drawing = False

        if True:
            self.draw_new_bounding_boxes(self.new_bounding_boxes)
            self.drawing_image = self.draw_helper_lines(mouse_x, mouse_y, self.drawing_image)
            
        if self.drawing:
            self.draw_current_bounding_box(end_bbox_x, end_bbox_y)
        
    def draw_new_bounding_boxes(self, new_bounding_boxes):
        for bounding_box in new_bounding_boxes:
            cv2.rectangle(self.drawing_image, (bounding_box[0], bounding_box[2]), (bounding_box[1], bounding_box[3]), (0,0,185), 1)

    def draw_current_bounding_box(self, end_bbox_x, end_bbox_y):
        
        cv2.rectangle(self.drawing_image, (self.initial_bbox_x, self.initial_bbox_y), (end_bbox_x, end_bbox_y), (0,0,255), 2)

    def draw_helper_lines(self, mouse_x, mouse_y, image):
        image_with_lines = cv2.imread(self.image)
        image_with_lines = cv2.line(image_with_lines, (mouse_x, 0), (mouse_x, image_with_lines.shape[0]), (255,0,0), 1)
        image_with_lines = cv2.line(image_with_lines, (0, mouse_y), (image_with_lines.shape[1], mouse_y), (255,0,0), 1)
        return image_with_lines


    def draw_new_bounding_box(self, editing):
        # Connect the mouse button to our callback function
        

        self.drawing = False
        self.initial_bbox_x, self.initial_bbox_y = -1, -1
        self.draw_with_clear_view = False
        self.drawing_image = cv2.imread(self.image)
        cv2.setMouseCallback("Image screen", self.annotate_bounding_box)

        # display the window
        while editing:            
            self.update_image_screen(self.drawing_image)
            
            command = self.keyboard_interpreter.get_command()

            if len(command) > 0 and command[0] == 'esc':
                editing = False
        
        return editing