import os
import cv2
from manual_bbox_annotation import image_bounding_box_annotation, key_checker
from bbox_class_annotation import Bounding_box_classification_annotation_tool

def main():
    directory_path = "raw_images"
    images = []


    with open(os.path.join(directory_path, 'classes.txt')) as f:
        classes = f.readlines()
    for filename in os.listdir(directory_path):
        f = os.path.join(directory_path, filename)
        # checking if it is a file
        if os.path.isfile(f):
            images.append(f)

    for i, image in enumerate(images):
        name = str(i) + "_rgb"
        new_annotation = image_bounding_box_annotation(image, name, classes)
        new_annotation.annotate()
    

def main2():
    directory_path = "captured_images"
    images = []
    values = []
    PATH_TO_MODEL = 'product_detection_weights.pt'


    with open(os.path.join(directory_path, 'classes.txt')) as f:
        classes = f.readlines()
    
    for filename in os.listdir(directory_path):
        f = os.path.join(directory_path, filename)
        # checking if it is a file
        if os.path.isfile(f) and (f.endswith('.jpg')):
            images.append(f)
            values.append(int(f.replace('.jpg','')))

    images = [i[1] for i in sorted(zip(values, images))]
    num = 0 # resume annotation
    
    for i in range(len(images)):
        print(i+num) # +1 due to classes.txt
        image = images[i+num+1]
        name = str(i+num)
        new_annotation = Bounding_box_classification_annotation_tool(PATH_TO_MODEL, image, name, classes)
        new_annotation.annotate()
        cv2.imwrite(name, cv2.imread(image))


if __name__ == '__main__':
    main2()