import os

def load_classes(dir):
    """
    Load the garbage classes from the given directory.
    The file name corresponds to the class.
    The file contains one object and its CO2 mass per line, separated by tab.

    :param dir: directory containing garbage classes
    :return: dictionary mapping garbage classes to objects and their CO2 mass.
    """
    class_dict = {}
    for file_name in os.listdir(dir):
        class_name = file_name.split(".txt")[0]
        class_dict[class_name] = []
        with open(dir+'/'+file_name, 'r') as f:
            for line in f:
                splitted = line.strip().split()
                obj = splitted[0]
                co = splitted[-1]
                class_dict[class_name].append((obj, co))
    return class_dict