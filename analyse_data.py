import os
import matplotlib.pyplot as plt

directory_path = "../datasets/supermarket_dataset/labels"
labels = []
for filename in os.listdir(directory_path):
    f = os.path.join(directory_path, filename)
    # checking if it is a file
    if os.path.isfile(f):
        labels.append(f)


label_instances = dict()
label_image_occurances = dict()
for label in labels:
    with open(label, 'r') as f:
        lines = f.readlines()
        
        for line in lines:
            
            key = line.split(' ')[0]

            if key in label_instances:
                count = label_instances[key]
                count = count + 1
                label_instances[key] = count
                label_image_occurances[key] = 1
            else:
                label_instances[key] = 1
                

print(len(label_image_occurances))
print(len(label_instances))


keys = list(label_instances.keys())
keys = [int(k) for k in keys]
keys.sort()
keys = [str(k) for k in keys]
label_instances = {i: label_instances[i] for i in keys}
 

classes = list(label_instances.keys())
values = list(label_instances.values())
  
fig = plt.figure(figsize = (10, 5))
 
# creating the bar plot
plt.bar(classes, values, color ='maroon',
        width = 1)
 
plt.xlabel("classes")
plt.ylabel("appearances in dataset")
plt.title("Appearances of classes is the dataset")
plt.show()