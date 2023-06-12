import os

import run


def blocks_on_1_1():
    domain_name = "blocks_4_on"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))
    files_3 = list(filter(lambda x: x.startswith('p-3'), files))
    files_4 = list(filter(lambda x: x.startswith('p-4'), files))
    files_5 = list(filter(lambda x: x.startswith('p-5'), files))

    complexity = 4
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, instance_files, generator_params, max_features, max_rules)


def blocks_clear_1_1():
    domain_name = "blocks_4_clear"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))
    files_3 = list(filter(lambda x: x.startswith('p-3'), files))
    files_4 = list(filter(lambda x: x.startswith('p-4'), files))
    files_5 = list(filter(lambda x: x.startswith('p-5'), files))

    complexity = 4
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, instance_files, generator_params, max_features, max_rules)


def gripper_1_1():
    domain_name = "gripper"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))

    complexity = 4
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, instance_files, generator_params, max_features, max_rules)


def reward_1_1():
    domain_name = "reward"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('instance'), files))

    complexity = 4
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, instance_files, generator_params, max_features, max_rules)


def delivery_1_1():
    domain_name = "delivery"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('instance'), files))

    complexity = 5
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, instance_files, generator_params, max_features, max_rules)


def miconic_1_1():
    domain_name = "miconic"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))

    complexity = 4
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, instance_files, generator_params, max_features, max_rules)


def spanner_1_1():
    domain_name = "spanner"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))

    complexity = 5
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, instance_files, generator_params, max_features, max_rules)


def visitall_1_1():
    domain_name = "visitall"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))

    complexity = 4
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, instance_files, generator_params, max_features, max_rules)


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
    run.run_on_multiple_instances(directory, domain_file, instance_files, generator_params, max_features, max_rules)


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
    # Run with graph cashing
    # blocks_clear_1_1()
    blocks_on_1_1()

    # Run without graph cashing
    # gripper_1_1()
    # delivery_1_1()        # wacht nog even met deze
    # miconic_1_1()
    # reward_1_1()
    # spanner_1_1()
    # visitall_1_1()
