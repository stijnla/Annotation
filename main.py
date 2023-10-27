import os
import cv2
from manual_bbox_annotation import image_bounding_box_annotation, key_checker
from bbox_class_annotation import Bounding_box_classification_annotation_tool



def main():
    directory_path = "captured_images/data"
    classes_path = "captured_images"
    images = []
    values = []
    PATH_TO_MODEL = 'product_detection_weights.pt'


    with open(os.path.join(classes_path, 'classes.txt')) as f:
        classes = f.readlines()
    
    for filename in os.listdir(directory_path):
        f = os.path.join(directory_path, filename)
        # checking if it is a file
        if os.path.isfile(f) and (f.endswith('.jpg')):
            images.append(f)
            values.append(int(f.replace('.jpg','').replace(directory_path,'').replace('/','')))

    images = [i[1] for i in sorted(zip(values, images))]
    processed_images = [f for f in os.listdir('processed') if os.path.isfile(os.path.join('processed', f)) and f.endswith('.jpg')]

    num = len(processed_images) # resume annotation
    
    for i in range(len(images)):
        image = images[i+num]
        name = str(i+num)
        new_annotation = Bounding_box_classification_annotation_tool(PATH_TO_MODEL, image, name, classes)
        new_annotation.annotate()
        cv2.imwrite(os.path.join('processed', name+'.jpg'), cv2.imread(image))


if __name__ == '__main__':
    main()