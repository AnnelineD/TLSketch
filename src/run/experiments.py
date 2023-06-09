import os

import run


def all_blocks_on():
    domain_name = "blocks_4_on"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    files_3 = list(filter(lambda x: x.startswith('p-3'), files))
    files_4 = list(filter(lambda x: x.startswith('p-4'), files))

    complexity = 4
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 2
    max_rules = 2

    file_dir = f"../../generated/{domain_name}/"
    if not os.path.isdir(file_dir):
        os.mkdir(file_dir)
    run.run_on_multiple_instances(domain_file, files_3[:10] + files_4[:10], generator_params, max_features, max_rules)


def all_gripper():
    domain_name = "gripper"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))

    complexity = 4
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 2
    max_rules = 2

    file_dir = f"../../generated/{domain_name}/"
    if not os.path.isdir(file_dir):
        os.mkdir(file_dir)
    run.run_on_multiple_instances(domain_file, instance_files, generator_params, max_features, max_rules)


"""https://www.geeksforgeeks.org/finding-duplicate-files-with-python/"""
def remove_duplicate_domains(path):
    # Importing Libraries
    import os
    from pathlib import Path
    from filecmp import cmp

    # list of all documents
    DATA_DIR = Path(path)
    files = sorted(os.listdir(DATA_DIR))

    # List having the classes of documents
    # with the same content
    duplicateFiles = []

    # comparison of the documents
    print(len(files))
    for file_x in files:

        if_dupl = False

        for class_ in duplicateFiles:
            # Comparing files having same content using cmp()
            # class_[0] represents a class having same content
            if_dupl = cmp(
                DATA_DIR / file_x,
                DATA_DIR / class_[0],
                shallow=False
            )
            if if_dupl:
                class_.append(file_x)
                os.remove(DATA_DIR / file_x)
                break

        if not if_dupl:
            duplicateFiles.append([file_x])

    # Print results
    print(duplicateFiles)
    print(len(duplicateFiles))


if __name__ == '__main__':
    all_blocks_on()
    #all_gripper()
