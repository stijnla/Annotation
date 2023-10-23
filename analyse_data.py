import os
import matplotlib.pyplot as plt
import yaml

def get_configuration(yaml_file):
    with open(yaml_file, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def main():
    config = get_configuration("config.yaml")

    path_to_datasets_directory = config['path_to_datasets_directory']
    if path_to_datasets_directory:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path_to_datasets_directory, 'datasets', 'supermarket_dataset')
    else:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets', 'supermarket_dataset')
    label_paths = []
    for filename in os.listdir(os.path.join(path, 'labels')):
        f = os.path.join(os.path.join(path, 'labels'), filename)
        # checking if it is a file
        if os.path.isfile(f):
            label_paths.append(f)


    label_instances = dict()
    label_image_occurances = dict()
    for label_path in label_paths:
        with open(label_path, 'r') as f:
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

if __name__ == main():
    main()