import os
import cv2


directory_path = "../datasets/supermarket_dataset/images"
images = []
for filename in os.listdir(directory_path):
    f = os.path.join(directory_path, filename)
    # checking if it is a file
    if os.path.isfile(f):
        images.append(f)

train = []
val = []
test = []
for i, image in enumerate(images):
    
    if i < 100:
        train.append('./images' + image.replace(directory_path, ''))
    elif i < 110:
        val.append('./images' + image.replace(directory_path, ''))
    else:
        test.append('./images' + image.replace(directory_path, ''))


with open('train.txt', 'w') as f:
    for t in train:
        f.writelines(t + '\n')

with open('test.txt', 'w') as f:
    for t in test:
        f.writelines(t + '\n')

with open('val.txt', 'w') as f:
    for t in val:
        f.writelines(t + '\n')