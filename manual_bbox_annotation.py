# import required libraries
import cv2
from copy import deepcopy
import os
from pynput import keyboard

# TODO: always update screen, not only when mouse callback is called!

class key_checker():
    def __init__(self) -> None:
        # Collect events until released

        """with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            listener.join()"""

        # ...or, in a non-blocking fashion:
        self.listener = keyboard.Listener(
                    on_press=self.on_press,
                    on_release=self.on_release)
        self.listener.start()

        self.command = []

    def on_press(self, key):
        try:
            if key.char == 'z':
                print("undo")
                self.command.append('undo')
            if key.char == 'c':
                print("clear view")
                self.command.append('clear_view')
            
        except AttributeError:
            if key == keyboard.Key.esc:
                print("escape: done annotating image")
                self.command.append('done')
            if key == keyboard.Key.left:
                print("previous label")
                self.command.append('prev')
            if key == keyboard.Key.right:
                print("next label")
                self.command.append('next')

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


class image_bounding_box_annotation():

    def __init__(self, image, name, classes) -> None:
        
        assert(type(name) == str) # name should be a string

        self.drawing = False
        self.image_cache = []
        self.visible_image = cv2.imread(image) # read image
        self.initial_bbox_x, self.initial_bbox_y = -1, -1
        assert(len(self.visible_image.shape) == 3) # check if valid image
        assert(self.visible_image.shape[2] == 3) # rgb channels should be last in image -> shape = (height, width, channels)

        self.image_cache.append(self.visible_image) # append first image to cache
        self.annotation_file_name = name + '.txt'
        self.image_name = name + '.jpg'
        self.selected_label = 0
        self.classes = classes # possible labels in image
        self.draw_with_clear_view = False


        # check keyboard input
        self.key_check = key_checker()

        # create new annotation file
        with open(os.path.join('labels', self.annotation_file_name), 'x') as f:
            pass

    def write_bounding_box_data(self, start_coordinate, end_coordinate, label, format='yolo'):
        if format == 'yolo':
            # calculate bounding box center, width and height

            bbox_center = ((start_coordinate[0] + end_coordinate[0])/2, (start_coordinate[1] + end_coordinate[1])/2)
            bbox_width, bbox_height = (abs(start_coordinate[0] - end_coordinate[0]), abs(start_coordinate[1] - end_coordinate[1]))
            
            # normalize bounding box values (required for yolo)
            image_width = self.image_cache[0].shape[1]
            image_height = self.image_cache[0].shape[0]
            
            normalized_bbox_center = (bbox_center[0]/image_width, bbox_center[1]/image_height)
            normalized_bbox_width = bbox_width/image_width
            normalized_bbox_height = bbox_height/image_height

            # formulate bounding box annotation line
            line = str(label) + ' ' + str(normalized_bbox_center[0]) + ' ' + str(normalized_bbox_center[1]) + ' ' + str(normalized_bbox_width) + ' ' + str(normalized_bbox_height) + '\n'
            
            with open(os.path.join('labels', self.annotation_file_name), 'a') as f:
                f.write(line)
            
    def contain_bbox_within_frame(self, x, y, image):
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

    # define mouse callback function to draw rectangle
    def annotate_bounding_box(self, event, mouse_x, mouse_y, flags, param):
        self.visible_image = self.draw_helper_lines(mouse_x, mouse_y, self.image_cache[-1])
        self.visible_image = self.draw_selected_label(self.visible_image, self.classes[self.selected_label])

        # start drawing bounding box
        if event == cv2.EVENT_MBUTTONDOWN:
            self.image_cache.append(deepcopy(self.image_cache[-1]))
            self.drawing = True
            self.initial_bbox_x = mouse_x
            self.initial_bbox_y = mouse_y
        
        # check mouse while drawing bounding box
        if event == cv2.EVENT_MOUSEMOVE:
            if self.drawing == True:
                
                end_bbox_x = mouse_x
                end_bbox_y = mouse_y

                # contain bounding box within frame
                end_bbox_x, end_bbox_y = self.contain_bbox_within_frame(end_bbox_x, end_bbox_y, self.visible_image)


                # draw rectangle without artifacts on screen
                
                if self.draw_with_clear_view:
                    image_tmp = deepcopy(self.image_cache[0])
                else:
                    image_tmp = deepcopy(self.image_cache[-1])

                
                cv2.rectangle(image_tmp, (self.initial_bbox_x, self.initial_bbox_y), (end_bbox_x, end_bbox_y),(0, 255, 255), 1)
                
                self.visible_image = image_tmp

        # stop drawing bounding box
        if event == cv2.EVENT_MBUTTONUP:
            self.drawing = False
            self.visible_image = self.image_cache[-1]
            
            end_bbox_x = mouse_x
            end_bbox_y = mouse_y

            # contain bounding box within frame
            end_bbox_x, end_bbox_y = self.contain_bbox_within_frame(end_bbox_x, end_bbox_y, self.visible_image)

            # draw final image
            print(self.classes[self.selected_label])
            cv2.putText(self.visible_image, self.classes[self.selected_label].replace('\n',''), (self.initial_bbox_x, self.initial_bbox_y + 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0, 0, 255), 1)
            cv2.rectangle(self.visible_image, (self.initial_bbox_x, self.initial_bbox_y), (end_bbox_x, end_bbox_y), (0, 0, 255), 1)

            # save annotation
            self.write_bounding_box_data((self.initial_bbox_x, self.initial_bbox_y), (end_bbox_x, end_bbox_y), self.selected_label)


    def undo_previous(self):
        # undo the previously determined bounding box
        # can be done until all bounding boxes are removed
        
        # remove rectangle from screen
        if len(self.image_cache) > 1:
            self.image_cache.pop(-1)
            self.visible_image = self.image_cache[-1]
        else:
            print("Cannot undo previous since there is no previous")

        # remove label from file
        with open(os.path.join('labels', self.annotation_file_name), 'r') as f:
            lines = f.readlines() # read annotations
        
        if len(lines) > 0:
            lines.pop(-1) # remove previous annotation

            print("Undo")
            with open(os.path.join('labels', self.annotation_file_name), 'w') as f:
                for line in lines:
                    f.write(line) # overwrite file


    def draw_helper_lines(self, mouse_x, mouse_y, image):
        image_with_lines = deepcopy(image)
        image_with_lines = cv2.line(image_with_lines, (mouse_x, 0), (mouse_x, image_with_lines.shape[0]), (255,0,0), 1)
        image_with_lines = cv2.line(image_with_lines, (0, mouse_y), (image_with_lines.shape[1], mouse_y), (255,0,0), 1)
        return image_with_lines

    def draw_selected_label(self, image, label):
        return cv2.putText(image, label.replace('\n',''), (50, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 1)



    def annotate(self):

        # Create a window and bind the function to window
        cv2.namedWindow("Annotation Window")

        # Connect the mouse button to our callback function
        cv2.setMouseCallback("Annotation Window", self.annotate_bounding_box)

        # display the window
        while True:
            cv2.imshow("Annotation Window", self.visible_image)
            
            command = self.key_check.get_command()

            
            if command != []:

                command = command[0] # grab first command only


                if command == 'done':
                    print("Escape pressed...")
                    print("Finished annotating current image, label saved in 'labels' folder, origninal image in 'images' folder")
                    cv2.imwrite(os.path.join("images", self.image_name), self.image_cache[0])
                    break
                if command == 'undo':
                    self.undo_previous()
                    
                if command == 'clear_view':
                    # trigger clear view for drawing
                    # this removes all bounding boxes from images when drawing
                    # for a clearer view of the image
                    if self.draw_with_clear_view:
                        print("Draw with clear view disabled")
                        self.draw_with_clear_view = False
                    else:
                        print("Draw with clear view enabled")
                        self.draw_with_clear_view = True
                if command == 'next':
                    if self.selected_label < len(self.classes) - 1:
                        self.selected_label = self.selected_label + 1
                    else:
                        self.selected_label = 0
                    print("selected next label")
                if command == 'prev':
                    if self.selected_label > 0:
                        self.selected_label = self.selected_label - 1
                    else:
                        self.selected_label = len(self.classes) - 1
                    print("selected previous label")
            cv2.waitKey(10)
        # shut down correctly 
        cv2.destroyAllWindows()
        self.key_check.stop()
