import cv2
import os

def get_labels():
    path = '../datasets/supermarket_dataset/labels'
    labels = []
    for filename in os.listdir(path):
        f = os.path.join(path, filename)
        # checking if it is a file
        if os.path.isfile(f):
            labels.append(f)

    return labels


def get_images():

    path = "../datasets/supermarket_dataset/images"
    images = []
    for filename in os.listdir(path):
        f = os.path.join(path, filename)
        # checking if it is a file
        if os.path.isfile(f):
            images.append(f)

    return images

def get_label(image, labels):
    for label in labels:
        label_name = str(label).replace('.txt', '').replace('labels', '')
        image_name = str(image).replace('.jpg', '').replace('images', '')
        
        if image_name == label_name:
            return label
    
    return None
images = get_images()
labels = get_labels()

with open('../datasets/supermarket_dataset/classes.txt') as f:
    classes = f.readlines()
    
for image in images:
    label = get_label(image, labels)

    if label:
        visualized_image = cv2.imread(image)
        with open(label) as f:
            yolo_labels = f.readlines()
        for yolo_label in yolo_labels:
            yolo_label = [float(x) for x in yolo_label.split(' ')]
            product_class = int(yolo_label[0])
            
            yolo_label = yolo_label[1:]
            x1 = int(yolo_label[0]*visualized_image.shape[1] - 0.5*yolo_label[2]*visualized_image.shape[1])
            y1 = int(yolo_label[1]*visualized_image.shape[0] - 0.5*yolo_label[3]*visualized_image.shape[0])
            x2 = int(yolo_label[0]*visualized_image.shape[1] + 0.5*yolo_label[2]*visualized_image.shape[1])
            y2 = int(yolo_label[1]*visualized_image.shape[0] + 0.5*yolo_label[3]*visualized_image.shape[0])
            
            cv2.rectangle(visualized_image, (x1, y1), (x2, y2), (0,0,255), 2)
            
            cv2.putText(visualized_image, classes[product_class].replace('\n', ''), (int(x1), int(y1)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow('image', visualized_image)
        cv2.waitKey(0)
