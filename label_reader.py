import os

with open('datasets/supermarket_dataset/classes.txt', 'r') as f:

    classes = f.readlines()
lines = []

for i, c in enumerate(classes):
        line = '  ' + str(i) + ': ' + str(c) 
        lines.append(line)

with open('labels.txt', 'w') as f:
    for line in lines:
        f.writelines(line)