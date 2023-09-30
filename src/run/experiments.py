# All the experiments I ran for my master thesis Generating and Verifying Planning Sketches using Temporal Logic.
# Each method is called "'domain name'_'the maximum amount of features'_'the maximum amount of rules'".
# The instance files used are the same files from Drexler et al.s Learning sketches for decomposing planning problems
# into subproblems of bounded width, after removing all duplicate files with the remove_duplicate_domains method.
# The feature complexities used are the maximum feature complexities of the sketches found in Drexler et al.

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
    instance_files_2 = list(filter(lambda x: x.startswith('instance_2x2'), files))
    instance_files_3 = list(filter(lambda x: x.startswith('instance_3x3'), files))

    complexity = 2
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, instance_files_2 + instance_files_3, generator_params,
                                  max_features, max_rules)


def delivery_1_1():
    domain_name = "delivery"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('instance'), files))
    drexler_instances = list(filter(lambda x: x.startswith('instance_2'), files))

    complexity = 5
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, drexler_instances, generator_params, max_features, max_rules)


def miconic_1_1():
    domain_name = "miconic"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files_2 = list(filter(lambda x: x.startswith('p-2-'), files))
    instance_files_3 = list(filter(lambda x: x.startswith('p-3-'), files))
    instance_files_4 = list(filter(lambda x: x.startswith('p-4-'), files))

    complexity = 2
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, instance_files_2 + instance_files_3 + instance_files_4,
                                  generator_params, max_features, max_rules)


def spanner_1_1():
    domain_name = "spanner"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))
    used = ['p-3-3-3-0', 'p-3-3-3-1', 'p-3-3-3-2', 'p-3-3-3-3', 'p-3-3-3-4', 'p-3-3-3-5', 'p-3-3-3-6', 'p-3-3-3-7',
            'p-3-3-3-8', 'p-3-3-3-9', 'p-3-3-3-10', 'p-3-3-3-11', 'p-3-3-3-12', 'p-3-3-3-13', 'p-3-3-3-14',
            'p-3-3-3-15', 'p-3-3-3-16', 'p-3-3-3-17', 'p-3-3-3-18', 'p-3-3-3-19', 'p-3-3-4-0', 'p-3-3-4-1', 'p-3-3-4-2',
            'p-3-3-4-3', 'p-3-3-4-4', 'p-3-3-4-5', 'p-3-3-4-6', 'p-3-3-4-7', 'p-3-3-4-8', 'p-3-3-4-9', 'p-3-3-4-10',
            'p-3-3-4-11', 'p-3-3-4-12', 'p-3-3-4-13', 'p-3-3-4-14', 'p-3-3-4-15', 'p-3-3-4-16', 'p-3-3-4-17',
            'p-3-3-4-18', 'p-3-3-4-19', 'p-3-3-5-0', 'p-3-3-5-1', 'p-3-3-5-2', 'p-3-3-5-3', 'p-3-3-5-4', 'p-3-3-5-5',
            'p-3-3-5-6', 'p-3-3-5-7', 'p-3-3-5-8', 'p-3-3-5-9', 'p-3-3-5-10', 'p-3-3-5-11', 'p-3-3-5-12', 'p-3-3-5-13',
            'p-3-3-5-14', 'p-3-3-5-15', 'p-3-3-5-16', 'p-3-3-5-17', 'p-3-3-5-18', 'p-3-3-5-19', 'p-3-4-4-0',
            'p-3-4-4-1', 'p-3-4-4-2', 'p-3-4-4-3', 'p-3-4-4-4', 'p-3-4-4-5', 'p-3-4-4-6', 'p-3-4-4-7', 'p-3-4-4-8',
            'p-3-4-4-9', 'p-3-4-4-10', 'p-3-4-4-11', 'p-3-4-4-12', 'p-3-4-4-13', 'p-3-4-4-14', 'p-3-4-4-15',
            'p-3-4-4-16', 'p-3-4-4-17', 'p-3-4-4-18', 'p-3-4-4-19', 'p-3-4-5-0', 'p-3-4-5-1', 'p-3-4-5-2', 'p-3-4-5-3',
            'p-3-4-5-4', 'p-3-4-5-5', 'p-3-4-5-6', 'p-3-4-5-7', 'p-3-4-5-8', 'p-3-4-5-9', 'p-3-4-5-10', 'p-3-4-5-11',
            'p-3-4-5-12', 'p-3-4-5-13', 'p-3-4-5-14', 'p-3-4-5-15', 'p-3-4-5-16', 'p-3-4-5-17', 'p-3-4-5-18',
            'p-3-4-5-19', 'p-3-5-5-0', 'p-3-5-5-1', 'p-3-5-5-2', 'p-3-5-5-3', 'p-3-5-5-4', 'p-3-5-5-5', 'p-3-5-5-6',
            'p-3-5-5-7', 'p-3-5-5-8', 'p-3-5-5-9', 'p-3-5-5-10', 'p-3-5-5-11', 'p-3-5-5-12', 'p-3-5-5-13', 'p-3-5-5-14',
            'p-3-5-5-15', 'p-3-5-5-16', 'p-3-5-5-17', 'p-3-5-5-18', 'p-3-5-5-19', 'p-4-3-3-0', 'p-4-3-3-1', 'p-4-3-3-2',
            'p-4-3-3-3', 'p-4-3-3-4', 'p-4-3-3-5', 'p-4-3-3-6', 'p-4-3-3-7', 'p-4-3-3-8', 'p-4-3-3-9', 'p-4-3-3-10',
            'p-4-3-3-11', 'p-4-3-3-12', 'p-4-3-3-13', 'p-4-3-3-14', 'p-4-3-3-15', 'p-4-3-3-16', 'p-4-3-3-17',
            'p-4-3-3-18', 'p-4-3-3-19', 'p-4-3-4-0', 'p-4-3-4-1', 'p-4-3-4-2', 'p-4-3-4-3', 'p-4-3-4-4', 'p-4-3-4-5',
            'p-4-3-4-6', 'p-4-3-4-7', 'p-4-3-4-8', 'p-4-3-4-9', 'p-4-3-4-10', 'p-4-3-4-11', 'p-4-3-4-12', 'p-4-3-4-13',
            'p-4-3-4-14', 'p-4-3-4-15', 'p-4-3-4-16', 'p-4-3-4-17', 'p-4-3-4-18', 'p-4-3-4-19', 'p-4-3-5-0',
            'p-4-3-5-1', 'p-4-3-5-2', 'p-4-3-5-3', 'p-4-3-5-4', 'p-4-3-5-5', 'p-4-3-5-6', 'p-4-3-5-7', 'p-4-3-5-8',
            'p-4-3-5-9', 'p-4-3-5-10', 'p-4-3-5-11', 'p-4-3-5-12', 'p-4-3-5-13', 'p-4-3-5-14', 'p-4-3-5-15',
            'p-4-3-5-16', 'p-4-3-5-17', 'p-4-3-5-18', 'p-4-3-5-19', 'p-4-4-4-0', 'p-4-4-4-1', 'p-4-4-4-2', 'p-4-4-4-3',
            'p-4-4-4-4', 'p-4-4-4-5', 'p-4-4-4-6', 'p-4-4-4-7', 'p-4-4-4-8', 'p-4-4-4-9', 'p-4-4-4-10', 'p-4-4-4-11',
            'p-4-4-4-12', 'p-4-4-4-13', 'p-4-4-4-14', 'p-4-4-4-15', 'p-4-4-4-16', 'p-4-4-4-17', 'p-4-4-4-18',
            'p-4-4-4-19', 'p-4-4-5-0', 'p-4-4-5-1', 'p-4-4-5-2', 'p-4-4-5-3', 'p-4-4-5-4', 'p-4-4-5-5', 'p-4-4-5-6',
            'p-4-4-5-7', 'p-4-4-5-8', 'p-4-4-5-9', 'p-4-4-5-10', 'p-4-4-5-11', 'p-4-4-5-12', 'p-4-4-5-13', 'p-4-4-5-14',
            'p-4-4-5-15', 'p-4-4-5-16', 'p-4-4-5-17', 'p-4-4-5-18', 'p-4-4-5-19', 'p-4-5-5-0', 'p-4-5-5-1', 'p-4-5-5-2',
            'p-4-5-5-3', 'p-4-5-5-4', 'p-4-5-5-5', 'p-4-5-5-6', 'p-4-5-5-7', 'p-4-5-5-8', 'p-4-5-5-9', 'p-4-5-5-10',
            'p-4-5-5-11', 'p-4-5-5-12', 'p-4-5-5-13', 'p-4-5-5-14', 'p-4-5-5-15', 'p-4-5-5-16', 'p-4-5-5-17',
            'p-4-5-5-18', 'p-4-5-5-19', 'p-5-3-3-0', 'p-5-3-3-1', 'p-5-3-3-2', 'p-5-3-3-3', 'p-5-3-3-4', 'p-5-3-3-5',
            'p-5-3-3-6', 'p-5-3-3-7', 'p-5-3-3-8', 'p-5-3-3-9', 'p-5-3-3-10', 'p-5-3-3-11', 'p-5-3-3-12', 'p-5-3-3-13',
            'p-5-3-3-14', 'p-5-3-3-15', 'p-5-3-3-16', 'p-5-3-3-17', 'p-5-3-3-18', 'p-5-3-3-19', 'p-5-3-4-0',
            'p-5-3-4-1', 'p-5-3-4-2', 'p-5-3-4-3', 'p-5-3-4-4', 'p-5-3-4-5', 'p-5-3-4-6', 'p-5-3-4-7', 'p-5-3-4-8',
            'p-5-3-4-9', 'p-5-3-4-10', 'p-5-3-4-11', 'p-5-3-4-12', 'p-5-3-4-13', 'p-5-3-4-14', 'p-5-3-4-15',
            'p-5-3-4-16', 'p-5-3-4-17', 'p-5-3-4-18', 'p-5-3-4-19', 'p-5-3-5-0', 'p-5-3-5-1', 'p-5-3-5-2', 'p-5-3-5-3',
            'p-5-3-5-4', 'p-5-3-5-5', 'p-5-3-5-6', 'p-5-3-5-7', 'p-5-3-5-8', 'p-5-3-5-9', 'p-5-3-5-10', 'p-5-3-5-11',
            'p-5-3-5-12', 'p-5-3-5-13', 'p-5-3-5-14', 'p-5-3-5-15', 'p-5-3-5-16', 'p-5-3-5-17', 'p-5-3-5-18',
            'p-5-3-5-19', 'p-5-4-4-0', 'p-5-4-4-1', 'p-5-4-4-2', 'p-5-4-4-3', 'p-5-4-4-4', 'p-5-4-4-5', 'p-5-4-4-6',
            'p-5-4-4-7', 'p-5-4-4-8', 'p-5-4-4-9', 'p-5-4-4-10', 'p-5-4-4-11', 'p-5-4-4-12', 'p-5-4-4-13', 'p-5-4-4-14',
            'p-5-4-4-15', 'p-5-4-4-16', 'p-5-4-4-17', 'p-5-4-4-18', 'p-5-4-4-19', 'p-5-4-5-0', 'p-5-4-5-1', 'p-5-4-5-2',
            'p-5-4-5-3', 'p-5-4-5-4', 'p-5-4-5-5', 'p-5-4-5-6', 'p-5-4-5-7', 'p-5-4-5-8', 'p-5-4-5-9', 'p-5-4-5-10',
            'p-5-4-5-11', 'p-5-4-5-12', 'p-5-4-5-13', 'p-5-4-5-14', 'p-5-4-5-15', 'p-5-4-5-16', 'p-5-4-5-17',
            'p-5-4-5-18', 'p-5-4-5-19', 'p-5-5-5-0', 'p-5-5-5-1', 'p-5-5-5-2', 'p-5-5-5-3', 'p-5-5-5-4', 'p-5-5-5-5',
            'p-5-5-5-6', 'p-5-5-5-7', 'p-5-5-5-8', 'p-5-5-5-9', 'p-5-5-5-10', 'p-5-5-5-11', 'p-5-5-5-12', 'p-5-5-5-13',
            'p-5-5-5-14', 'p-5-5-5-15', 'p-5-5-5-16', 'p-5-5-5-17', 'p-5-5-5-18', 'p-5-5-5-19']
    used_instances = list(filter(lambda x: x.removesuffix('.pddl') in used, files))
    complexity = 6
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, used_instances, generator_params, max_features, max_rules)


def visitall_1_1():
    domain_name = "visitall"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    used_by_drexler = [f"p-{unavail}-{pct}-{grid_size}-{seed}.pddl" for unavail in range(1, 3) for pct in [0.5, 1.0] for
                       grid_size in range(2, 4) for seed in range(0, 50)]
    ill_defined = ["p-2-0.5-2-29.pddl",
                   "p-2-0.5-3-6.pddl",
                   "p-2-0.5-3-14.pddl",
                   "p-2-0.5-3-39.pddl",
                   "p-2-0.5-3-41.pddl",
                   "p-2-0.5-3-46.pddl",
                   "p-2-1.0-3-6.pddl",
                   "p-2-1.0-3-14.pddl",
                   "p-2-1.0-3-19.pddl",
                   "p-2-1.0-3-39.pddl",
                   "p-2-1.0-3-46.pddl",
                   ]

    instance_files = list(filter(lambda x: x.startswith('p-'), files))
    used_files = list(filter(lambda x: x in used_by_drexler and x not in ill_defined, files))

    complexity = 2
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, used_files, generator_params, max_features, max_rules)


def childsnack_1_1():
    domain_name = "childsnack"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))
    # filter all instances with < 10000 states as in Drexler
    small_state_space = [f"p-2-1.0-{gfactor}-{trays}-{seed}.pddl" for gfactor in [0.0, 0.5, 1.0] for
                         trays in range(1, 3) for seed in range(0, 5)] + \
                        [f"p-3-1.0-{gfactor}-{trays}-{seed}.pddl" for gfactor in [0.0, 0.5, 1.0] for
                         trays in range(1, 2) for seed in range(0, 5)]
    used_files = list(filter(lambda x: x in small_state_space, files))

    complexity = 6
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, used_files, generator_params, max_features, max_rules)


def blocks_on_2_1(time_limit_h):
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
    max_features = 2
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, files_3[:10] + files_4[:10], generator_params, max_features,
                                  max_rules, time_limit_h * 3600)


def blocks_on_2_2(time_limit_h):
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
    max_features = 2
    max_rules = 2

    run.run_on_multiple_instances(directory, domain_file, files_3, generator_params, max_features, max_rules,
                                  time_limit_h * 3600)


def gripper_2_1(time_limit_h):
    domain_name = "gripper"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))

    complexity = 4
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 2
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, instance_files[:4], generator_params, max_features, max_rules,
                                  time_limit_h * 3600)


def gripper_2_2(time_limit_h):
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

    run.run_on_multiple_instances(directory, domain_file, instance_files[:2], generator_params, max_features, max_rules,
                                  time_limit_h * 3600)


def delivery_2_2(time_limit_h):
    domain_name = "delivery"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('instance'), files))
    drexler_instances = list(filter(lambda x: x.startswith('instance_2'), files))

    complexity = 4
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 2
    max_rules = 2

    run.run_on_multiple_instances(directory, domain_file, drexler_instances, generator_params, max_features, max_rules,
                                  time_limit_h * 3600)


def miconic_2_2(time_limit_h):
    domain_name = "miconic"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files_2 = [inst for i in range(2, 4) for inst in
                        list(filter(lambda x: x.startswith(f'p-2-{i}'), files))[:5]]
    instance_files_3 = [inst for i in range(2, 3) for inst in
                        list(filter(lambda x: x.startswith(f'p-3-{i}'), files))[:5]]
    instance_files_4 = [inst for i in range(2, 3) for inst in
                        list(filter(lambda x: x.startswith(f'p-4-{i}'), files))[:5]]

    complexity = 2
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 2
    max_rules = 2

    run.run_on_multiple_instances(directory, domain_file, instance_files_2 + instance_files_3 + instance_files_4,
                                  generator_params, max_features, max_rules, time_limit_h * 3600)


def childsnack_2_2(time_limit_h):
    domain_name = "childsnack"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))
    # filter all instances with < 10000 states as in Drexler
    small_state_space = [f"p-2-1.0-{gfactor}-{trays}-{seed}.pddl" for gfactor in [0.0, 0.5, 1.0] for
                         trays in range(1, 3) for seed in range(0, 3)]  # + \
    # [f"p-3-1.0-{gfactor}-{trays}-{seed}.pddl" for gfactor in [0.0, 0.5, 1.0] for
    # trays in range(1, 2) for seed in range(0, 5)]
    used_files = list(filter(lambda x: x in small_state_space, files))

    complexity = 6
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 2
    max_rules = 2

    run.run_on_multiple_instances(directory, domain_file, used_files, generator_params, max_features, max_rules,
                                  time_limit_h * 3600)


def childsnack_2_1(time_limit_h):
    domain_name = "childsnack"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = run.sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))
    # filter all instances with < 10000 states as in Drexler
    small_state_space = [f"p-2-1.0-{gfactor}-{trays}-{seed}.pddl" for gfactor in [0.0, 0.5, 1.0] for
                         trays in range(1, 3) for seed in range(0, 2)]  # + \
    # [f"p-3-1.0-{gfactor}-{trays}-{seed}.pddl" for gfactor in [0.0, 0.5, 1.0] for
    # trays in range(1, 2) for seed in range(0, 5)]
    used_files = list(filter(lambda x: x in small_state_space, files))

    complexity = 6
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 2
    max_rules = 1

    run.run_on_multiple_instances(directory, domain_file, used_files, generator_params, max_features, max_rules,
                                  time_limit_h * 3600)


def remove_duplicate_domains(path) -> None:
    """
    This method is copied from https://www.geeksforgeeks.org/finding-duplicate-files-with-python/ on the
    9th of June 2023.
    Given the path to a directory, if multiple files in that directory have the same content, only keep one and delete
    the others

    :param path: the path to a directory containing multiple files
    :return:
    """
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


if __name__ == '__main__':
    """
    All experiments that we ran. Some may take long so recommended to run them one by one or run them in parallel.
    Caching is used so be sure to delete or rename the files that contain generated sketches if desired to recalculate 
    them (found in the directory "generated". Same goes for the transition systems, features and feature valuations, 
    which can be found for each domain in the directory "cache". 
    """
    # blocks_clear_1_1()
    # blocks_on_1_1()
    # gripper_1_1()
    # delivery_1_1()
    # miconic_1_1()
    # reward_1_1()
    # spanner_1_1()
    # visitall_1_1()
    # childsnack_1_1()

    max_time_h = 24

    # blocks_on_2_2(max_time_h)
    # gripper_2_2(max_time_h)
    # delivery_2_2(max_time_h)
    # miconic_2_2(max_time_h)
    # childsnack_2_2(max_time_h)
