import json
from typing import Tuple, List

import matplotlib.pyplot as plt
import numpy as np

from src.logics.rules import Sketch


def works(l):
    return all(w == 1 for t, w in l)


def get_bounds(feature_valuations) -> dict[str, (int, int)]:
    return {f_name: (min(feature_valuations[f_name]), max(feature_valuations[f_name]))
            for f_name in feature_valuations.keys() if f_name.startswith('n_')}


def avg_time_per_instance_size(domain_name, complexity, num_f, num_rules):
    for domain_name, complexity in [("blocksworld", 4),
               ("blocksworld-on", 4),
               ("delivery", 5),
               ("gripper-strips", 4),
               ("miconic", 2),
               ("reward-strips", 2),
               ("spanner", 6),
               ("grid-visit-all", 2)]:
        with open(f"../../generated_final/{domain_name}/{'_'.join([str(complexity)]*5)}_180_10000_{num_f}/rules_{num_rules}.json") as f:
            info = json.load(f)
            sum_per_sketch = lambda l: sum([t for t, w in l])
            timings = info["timings"]
            instances = [(idx, i) for idx, i in enumerate(info["instance_files"])]
            n_tested = info["number_tested"]

        num_states = []

        for i in instances:
            with open(f"../../cache/{domain_name}/transition_systems/{i[1].removesuffix('.pddl')}.json") as f:
                info = json.load(f)
                num_states.append(len(info["states"]))

        sorted_instances = {n: [] for n in num_states}
        for i, n in zip(instances, num_states):
            sorted_instances[n].append(i[0])

        def works(l):
            return all(w == 1 for t, w in l)

        working = [s for s in timings if works(s)]
        def get_average(idxs):
            return sum([s[i][0] for s in working for i in idxs])/len(idxs)/len(working)

        sorted_sorted_instances = sorted(sorted_instances.items(), key=lambda x: x[0])
        x = [i[0] for i in sorted_sorted_instances]
        y = [get_average(idxs[1])/1000000000 for idxs in sorted_sorted_instances]
        e = [np.std(idxs[1])/1000000000 for idxs in sorted_sorted_instances]

        plt.errorbar(x, y, e, "-X", label=domain_name)
    plt.legend()
    plt.show()


def avg_time_per_num_rules(domains):
    for domain_name, complexity, num_f, num_rules in domains:
        with open(f"../../generated_final/{domain_name}/{'_'.join([str(complexity)]*5)}_180_10000_{num_f}/rules_{num_rules}.json") as f:
            info = json.load(f)
            sketches = info["working"]
            timings = info["timings"]
            instances = [(idx, i) for idx, i in enumerate(info["instance_files"])]

        all_bounds = []

        for i in instances:
            with open(
                    f"../../cache_final/{domain_name}/features/{'_'.join([str(complexity)] * 5)}_180_10000/{i[1].removesuffix('.pddl')}.json") as f:
                feature_vals = json.load(f)

                def get_bounds(feature_valuations) -> dict[str, (int, int)]:
                    return {f_name: (min(feature_valuations[f_name]), max(feature_valuations[f_name]))
                            for f_name in feature_valuations.keys() if f_name.startswith('n_')}

                bounds = get_bounds(feature_vals)
                all_bounds.append(bounds)

        working_times = [[i[0]/1000000000 for i in s] for s in timings if works(s)]
        num_rules_times = [(Sketch.deserialize(s).expand(all_bounds[i]).n_rules(), t[i]) for i in range(len(instances)) for s, t in zip(sketches, working_times)]


        sorted_rules = {r: [] for r, t in num_rules_times}
        for r, t in num_rules_times:
            sorted_rules[r].append(t)

        sorted_sorted_rules = sorted(sorted_rules.items(), key=lambda x: x[0])
        y = [sum(t)/len(t) for r, t in sorted_sorted_rules]
        x = [r for r,t in sorted_sorted_rules]
        # err = [np.std([i for i in idxs[1]]) for idxs in sorted_sorted_rules]

    # plt.errorbar(x, y, err, fmt="-X", label=domain_name)

        plt.plot(x, y, "-X", label=f"{domain_name}")
    plt.xlabel("# expanded rules")
    plt.ylabel('avg time (s)')
    plt.title('_'.join(domain_name for domain_name, _, _, _ in domains))
    plt.legend()
    plt.savefig(f"../../figures/rule_size/{'_'.join(domain_name for domain_name, _, _, _ in domains)}.png")
    plt.show()

"""
def avg_time_per_num_rules_one_domain(domain_name, complexity_1, complexity_2):
    with open(f"../../generated_final/{domain_name}/{'_'.join([str(complexity_2)]*5)}_180_10000_2/rules_2.json") as f:
        info_2 = json.load(f)
        sketches_2 = info_2["working"]
        timings_2 = info_2["timings"]
        instances_2 = [(idx, i) for idx, i in enumerate(info_2["instance_files"])]

    with open(f"../../generated_final/{domain_name}/{'_'.join([str(complexity_1)]*5)}_180_10000_1/rules_1.json") as f:
        info_1 = json.load(f)
        sketches_1 = info_1["working"]
        timings_1 = info_1["timings"]
        # For a fair comparison we only want the timings of the instances that we used for both experiments
        instances_1 = [(idx, i) for idx, i in enumerate(info_1["instance_files"]) if i in info_2["instance_files"]]

        all_bounds = []

    for e, (complexity, instances, sketches, timings) \
            in enumerate([(complexity_1, instances_1, sketches_1, timings_1),
                          (complexity_2, instances_2, sketches_2, timings_2)]):
        for i in instances:
            with open(
                    f"../../cache_final/{domain_name}/features/{'_'.join([str(complexity)] * 5)}_180_10000/{i[1].removesuffix('.pddl')}.json") as f:
                feature_vals = json.load(f)

                bounds = get_bounds(feature_vals)
                all_bounds.append(bounds)

        # avg_per_good_sketch = [np.mean(i[0] for i in ts_sketch)/1000_000_000 for ts_sketch in timings if works(ts_sketch)]
        # print(working_times)
        working_times = [[i / 1000000000 for e, inst in enumerate(sketch) if e in ] for sketch in timings if works(sketch)]
        num_rules_times = [(Sketch.deserialize(s).expand(all_bounds[i]).n_rules(), t[i]) for i in range(len(instances)) for s, t in zip(sketches, working_times)]


        sorted_rules = {r: [] for r, t in num_rules_times}
        for r, t in num_rules_times:
            sorted_rules[r].append(t)

        sorted_sorted_rules = sorted(sorted_rules.items(), key=lambda x: x[0])
        y = [np.mean(t) for r, t in sorted_sorted_rules]
        x = [r for r,t in sorted_sorted_rules]

        for r, t in sorted_sorted_rules:
            for i in t:
                if i <= 0:
                    print("GODVERDOMME")

        # err = [np.std(t) for r, t in sorted_sorted_rules]

        # plt.errorbar(x, y, err, fmt="-X", label=f"{e + 1} rules")

        plt.plot(x, y, "-X", label=f"{e} rules")

    plt.xlabel("# expanded rules")
    plt.ylabel('avg time (s)')
    plt.title(domain_name)
    plt.legend()
    plt.savefig(f"../../figures/rule_size/{domain_name}.png")
    plt.show()
"""

def get_total_time_per_sketch(timings: list[list[tuple[int, int]]], instance_idxs: list[int] = None) -> list[float]:
    if not instance_idxs:
        return [sum([time for time, worked in sketch])/1000_000_000 for sketch in timings]
    else:
        return [sum([time for i, (time, worked) in enumerate(sketch) if i in instance_idxs])/1000_000_000 for sketch in timings]


def get_timings_instances(domain_name, complexity, n_features, n_rules):
    with open(f"../../generated_final/{domain_name}/{'_'.join([str(complexity)] * 5)}_180_10000_{n_features}/rules_{n_rules}.json") as f:
        info = json.load(f)
        timings = info["timings"]
        instances = info["instance_files"]

    return timings, instances


def get_num_states(domain_name, instance):
    with open(f"../../cache_final/{domain_name}/transition_systems/{instance.removesuffix('.pddl')}.json") as f:
        info = json.load(f)
        states = info["states"]
    return len(states)


def get_average_good_time_for_common_instances(domain_name, complexity_1, complexity_2) -> tuple[
    list[float], list[float]]:
    with open(f"../../generated_final/{domain_name}/{'_'.join([str(complexity_2)] * 5)}_180_10000_2/rules_2.json") as f:
        info_2 = json.load(f)
        good_timings_2 = [t for t in info_2["timings"] if works(t)]
        instances = info_2["instance_files"]

    with open(f"../../generated_final/{domain_name}/{'_'.join([str(complexity_1)] * 5)}_180_10000_1/rules_1.json") as f:
        info_1 = json.load(f)
        good_timings_1 = [t for t in info_1["timings"] if works(t)]
        instances_1: list[str] = info_1["instance_files"]

    # For a fair comparison we only want the timings of the instances that we used for both experiments
    total_sketch_times_1 = get_total_time_per_sketch(good_timings_1, [instances_1.index(inst) for inst in instances])
    total_sketch_times_2 = get_total_time_per_sketch(good_timings_2)
    return total_sketch_times_1, total_sketch_times_2


def barchart_avg_time_two_experiments():
    """
    Method to plot a barchart with average time to check a sketch for experiment one and two over different domains
    Only the timings of the common instances are used
    :return:
    """
    domains = (("blocksworld-on", 4, 4), ("delivery", 5, 4), ("gripper-strips", 4, 4), ("miconic", 2, 2))
    names = ["Blocksworld-On", "Delivery", "Gripper", "Miconic"]

    total_sketch_times = [get_average_good_time_for_common_instances(domain_name, complexity_1, complexity_2)
                for domain_name, complexity_1, complexity_2 in domains]

    total_times_1 = [a[0] for a in total_sketch_times]
    total_times_2 = [a[1] for a in total_sketch_times]

    x = np.arange(len(domains))  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in zip(["experiment 1", "experiment 2"], [total_times_1, total_times_2]):
        offset = width * multiplier
        rects = ax.bar(x + offset, [np.mean(a) for a in measurement], width, label=attribute)
        # ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Average time to check a good sketch (s)')
    ax.set_title('')
    ax.set_xticks(x + width, names)
    ax.legend(loc='upper left', ncols=2)
    #ax.set_ylim(0, 250)

    plt.savefig(f"../../figures/barchart/{'_'.join(names)}.png")
    plt.show()


def avg_time_two_experiments_per_instace(domain_name, compl_1, compl_2, title):
    timings_1, instances_1 = get_timings_instances(domain_name, compl_1, 1, 1)
    timings_2, instances_2 = get_timings_instances(domain_name, compl_2, 2, 2)

    working_1 = [t for t in timings_1 if works(t)]
    working_2 = [t for t in timings_2 if works(t)]

    sorted_instances_2 = sorted(instances_2, key=lambda inst: get_num_states(domain_name, inst))

    instance_1_idx = [instances_1.index(inst) for inst in sorted_instances_2]
    instance_2_idx = [instances_2.index(inst) for inst in sorted_instances_2]

    avg_per_instance_1 = [np.mean([sketch[i][0] for sketch in working_1])/1_000_000_000 for i in instance_1_idx]
    avg_per_instance_2 = [np.mean([sketch[i][0] for sketch in working_2])/1_000_000_000 for i in instance_2_idx]

    plt.plot(avg_per_instance_1, '-o', label="experiment1")
    plt.plot(avg_per_instance_2, '-o', label="experiment2")
    plt.xlabel = "instance"
    plt.ylabel = "average time (s)"
    plt.title(f"{title}")
    plt.legend()
    plt.savefig(f"../../figures/per_instance/{domain_name}.png")
    plt.show()



def add_to_plot_rule_size_time(domain_name, complexity, num_f, num_rules, instance, label):
    with open(
            f"../../generated_final/{domain_name}/{'_'.join([str(complexity)] * 5)}_180_10000_{num_f}/rules_{num_rules}.json") as f:
        info = json.load(f)
        sketches = info["working"]
        timings = info["timings"]
        instance_idx: int = info["instance_files"].index(instance)


        with open(
                f"../../cache_final/{domain_name}/features/{'_'.join([str(complexity)] * 5)}_180_10000/{instance.removesuffix('.pddl')}.json") as f:
            feature_vals = json.load(f)
            bounds = get_bounds(feature_vals)

        working_times = [sketch_timings[instance_idx][0] / 1000000000 for sketch_timings in timings if works(sketch_timings)]
        num_rules_times = [(Sketch.deserialize(s).expand(bounds).n_rules(), t) for s, t in zip(sketches, working_times)]

        sorted_rules = {r: [] for r, t in num_rules_times}
        for r, t in num_rules_times:
            sorted_rules[r].append(t)

        sorted_sorted_rules = sorted(sorted_rules.items(), key=lambda x: x[0])
        y = [sum(t) / len(t) for r, t in sorted_sorted_rules]
        x = [r for r, t in sorted_sorted_rules]
        # err = [np.std([i for i in idxs[1]]) for idxs in sorted_sorted_rules]

        # plt.errorbar(x, y, err, fmt="-X", label=domain_name)
        plt.plot(x, y, '-o', label=label)


def plot_rule_size_time_for_domain(domain_name, complexity_1, complexity_2, instance, title):

    add_to_plot_rule_size_time(domain_name, complexity_2, 2, 2, instance, "experiment2")
    add_to_plot_rule_size_time(domain_name, complexity_1, 1, 1, instance, "experiment1")

    plt.legend()
    plt.ylabel("average time (s)")
    plt.xlabel("number of expanded rules")
    plt.title(f"{title}")
    plt.savefig(f"../../figures/rule_size/{domain_name}.png")
    plt.show()



def graph_for_instance_group(domain_name, complexity, num_f, num_rules, instances):
    with open(
            f"../../generated_final/{domain_name}/{'_'.join([str(complexity)] * 5)}_180_10000_{num_f}/rules_{num_rules}.json") as f:
        info = json.load(f)
        sketches = info["working"]
        timings = info["timings"]
        instance_idx: list[int] = [info["instance_files"].index(instance) for instance in instances]

        for instance in instances:
            with open(
                    f"../../cache_final/{domain_name}/features/{'_'.join([str(complexity)] * 5)}_180_10000/{instance.removesuffix('.pddl')}.json") as f:
                feature_vals = json.load(f)
                bounds = get_bounds(feature_vals)


        working_times = [sketch_timings[instance_idx][0] / 1000000000 for sketch_timings in timings if works(sketch_timings)]
        num_rules_times = [(Sketch.deserialize(s).expand(bounds).n_rules(), t) for s, t in zip(sketches, working_times)]

        sorted_rules = {r: [] for r, t in num_rules_times}
        for r, t in num_rules_times:
            sorted_rules[r].append(t)

        sorted_sorted_rules = sorted(sorted_rules.items(), key=lambda x: x[0])
        y = [sum(t) / len(t) for r, t in sorted_sorted_rules]
        x = [r for r, t in sorted_sorted_rules]
        err = [np.std([i for i in idxs[1]]) for idxs in sorted_sorted_rules]

        plt.errorbar(x, y, err, fmt="-X", label=domain_name)

        # plt.plot(x, y, "-X", label=f"{domain_name}")
    plt.xlabel("# expanded rules")
    plt.ylabel('avg time (s)')
    plt.title('_'.join(domain_name))
    plt.legend()
    plt.savefig(f"../../figures/rule_size/{'_'.join(domain_name)}.png")
    plt.show()



if __name__ == '__main__':
    # avg_time_per_num_rules_one_domain("blocksworld-on", 4, 4)
    # avg_time_per_num_rules_one_domain("miconic", 2, 2)      # TODO
    # avg_time_per_num_rules_one_domain("delivery", 5, 4)
    # avg_time_per_num_rules_one_domain("gripper-strips", 4, 4)  # TODO
    """
    avg_time_per_num_rules([("blocksworld", 4, 1, 1),
                            ("grid-visit-all", 2, 1, 1),
                            ("spanner", 6, 1, 1),
                            ("reward-strips", 2, 1, 1)])
    """
    # avg_time_per_num_rules([("blocksworld", 4, 1, 1)])
    # avg_time_per_num_rules([("grid-visit-all", 2, 1, 1)])
    # avg_time_per_num_rules([("spanner", 6, 1, 1)])
    # avg_time_per_num_rules([("reward-strips", 2, 1, 1)])
    """
    avg_time_per_num_rules([("blocksworld-on", 4, 2, 2),
                            ("miconic", 2, 2, 2),
                            ("delivery", 4, 2, 2),
                            ("gripper-strips", 4, 2, 2)])
    """

    #graph_for_one_instance("blocksworld", 4, 1, 1, "p-3-0.pddl")
    #graph_for_one_instance("blocksworld-on", 4, 2, 2, "p-3-0.pddl")
    #graph_for_one_instance("miconic", 2, 2, 2, "p-2-2-0.pddl")
    #graph_for_one_instance("delivery", 4, 2, 2, "instance_2_1_0.pddl")
    #graph_for_one_instance("blocksworld-on", 4, 2, 2, "p-3-0.pddl")

    barchart_avg_time_two_experiments()

    avg_time_two_experiments_per_instace("blocksworld-on", 4, 4, "Blocksworld-On")
    avg_time_two_experiments_per_instace("miconic", 2, 2, "Delivery")
    avg_time_two_experiments_per_instace("delivery", 5, 4, "Gripper")
    avg_time_two_experiments_per_instace("gripper-strips", 4, 4, "Miconic")

    plot_rule_size_time_for_domain("blocksworld-on", 4, 4, "p-3-0.pddl", "Blocksworld-On")
    plot_rule_size_time_for_domain("delivery", 5, 4, "instance_2_2_0.pddl", "Delivery")
    plot_rule_size_time_for_domain("gripper-strips", 4, 4, "p-2-0.pddl", "Gripper")
    plot_rule_size_time_for_domain("miconic", 2, 2, "p-4-2-0.pddl", "Miconic")