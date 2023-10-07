# Make plots regarding sketch generation and verification
# We used these plots to show and compare data from
#   experiment 1: generate and verify sketches with one rule and max one feature
#   experiment 2: generate and verify sketches with one rule and max two features

import json
import matplotlib.pyplot as plt
import numpy as np

from src.logics.rules import Sketch


def works(l: list[tuple[int, int]]) -> bool:
    """
    Return whether a sketch worked or not
    :param l: for each instance a tuple with the time it took to model-check the sketch on that instance and whether it
    was good on that instance (1), not good (0), or timed out (-1).
    :return: True if the sketch is good on all instances, False otherwise
    """
    return all(w == 1 for t, w in l)


def get_bounds(feature_valuations) -> dict[str, (int, int)]:
    """
    For each feature, return the lowest and highest value it can have over all states of an instance
    :param feature_valuations: For each feature its value per state
    :return: For each feature its (lower, upper)-bound pair
    """
    return {f_name: (min(feature_valuations[f_name]), max(feature_valuations[f_name]))
            for f_name in feature_valuations.keys() if f_name.startswith('n_')}


def get_total_time_per_sketch(timings: list[list[tuple[int, int]]], instance_idxs: list[int] = None) -> list[float]:
    """
    Calculate the total time it took to verify a sketch on given instances. If no instances are provided, return the
    time it took to verify a sketch on all instances.
    :param timings: A list with for each sketch a list with for each instance the time it took to verify the sketch on
    this instance and an index that indicates whether the sketch is good on this instance or not
      timings sketch 1               timings sketch 2              ...
        instance1   instance2          instance1  instance2
    [[(t11, w11), (t12, w12), ...], [(t21, w21), (t22, w22), ...], ...]
    :param instance_idxs: the indices of the instances we want to take into account
    :return: A list with for each sketch, the total time it took to verify it on all given instances
            Sum({tij | j ∈ intance_idxs})
    """
    if not instance_idxs:
        return [sum([time for time, worked in sketch]) / 1000_000_000 for sketch in timings]
    else:
        return [sum([time for i, (time, worked) in enumerate(sketch) if i in instance_idxs]) / 1000_000_000 for sketch
                in timings]


def get_timings_instances(domain_name, complexity, n_features, n_rules):
    """ Retrieve the timings of an experiment (verifying sketches over instances) and the instances used from the
    cached files"""
    with open(
            f"../../generated_final/{domain_name}/{'_'.join([str(complexity)] * 5)}_180_10000_{n_features}/rules_{n_rules}.json") as f:
        info = json.load(f)
        timings = info["timings"]
        instances = info["instance_files"]

    return timings, instances


def get_num_states(domain_name, instance):
    """For an instance of a domain, retrieve the number of states its transition system has from the cached transition
    system file"""
    with open(f"../../cache_final/{domain_name}/transition_systems/{instance.removesuffix('.pddl')}.json") as f:
        info = json.load(f)
        states = info["states"]
    return len(states)


def get_avg_time_per_good_sketch_for_common_instances(domain_name: str, complexity_1: int, complexity_2: int) -> tuple[
    list[float], list[float]]:
    """
    For each 'good' sketch, get the average time it took to verify it over an instances, taking only the instances that
    were used both in both experiments into account.
    :param domain_name:
    :param complexity_1: max feature complexity in experiment 1
    :param complexity_2: max feature complexity in experiment 2
    :return: list with for each good sketch the average time in took to verify it over an instance in experiment 1, and
           a list with for each good sketch the average time in took to verify it over an instance in experiment 2
    """
    with open(f"../../generated_final/{domain_name}/{'_'.join([str(complexity_2)] * 5)}_180_10000_2/rules_2.json") as f:
        info_2 = json.load(f)
        good_timings_2 = [t for t in info_2["timings"] if works(t)]
        instances_2 = info_2["instance_files"]

    with open(f"../../generated_final/{domain_name}/{'_'.join([str(complexity_1)] * 5)}_180_10000_1/rules_1.json") as f:
        info_1 = json.load(f)
        good_timings_1 = [t for t in info_1["timings"] if works(t)]
        instances_1: list[str] = info_1["instance_files"]

    instances = set(instances_2).intersection(set(instances_1))

    # For a fair comparison we only want the timings of the instances that we used for both experiments
    total_sketch_times_1 = get_total_time_per_sketch(good_timings_1, [instances_1.index(inst) for inst in instances])
    total_sketch_times_2 = get_total_time_per_sketch(good_timings_2, [instances_2.index(inst) for inst in instances])

    return [t / len(instances) for t in total_sketch_times_1], [t / len(instances) for t in total_sketch_times_2]


def barchart_avg_time_two_experiments():
    """
    Method to plot a barchart with average time to check a sketch for experiment one and two over different domains
    Only the timings of the instances used in both experiments are taken into account in the plot.
    The following domains are used: "Blocksworld-On", "Delivery", "Gripper", "Miconic"
    :return: The plot is shown and saved to a file named "../../figures/barchart/domain1_domain2_....png"
    """
    # domain_name, max feature complexity for experiment 1, max feature complexity for experiment 2
    domains = (("blocksworld-on", 4, 4), ("delivery", 5, 4), ("gripper-strips", 4, 4), ("miconic", 2, 2))
    names = ["Blocksworld-On", "Delivery", "Gripper", "Miconic"]

    # for each domain, for each good sketch, get the average time it took to verify a the good sketch, taking only into
    # account the instances that were used both in both experiments
    avg_sketch_times = [get_avg_time_per_good_sketch_for_common_instances(domain_name, complexity_1, complexity_2)
                          for domain_name, complexity_1, complexity_2 in domains]

    avg_times_1 = [a[0] for a in avg_sketch_times]  # the average times for experiment 1 of each domain
    avg_times_2 = [a[1] for a in avg_sketch_times]  # the average times for experiment 2 of each domain

    x = np.arange(len(domains))  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in zip(["experiment 1", "experiment 2"], [avg_times_1, avg_times_2]):
        offset = width * multiplier
        rects = ax.bar(x + offset, [np.mean(a) for a in measurement], width, label=attribute)
        # ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.set_ylabel('Average time to check a good sketch (s)')
    ax.set_title('')
    ax.set_xticks(x + width / 2, names)
    ax.legend(loc='upper left', ncols=2)
    # ax.set_ylim(0, 250)

    plt.savefig(f"../../figures/barchart/{'_'.join(names)}.png")
    plt.show()


def avg_time_two_experiments_per_instace(domain_name, compl_1, compl_2, title):
    """
    For experiment one and experiment two of a domain, plot for each used instance how long it took on average to verify
    a sketch on that instance. The instances on the x-axis are sorted on the number of states they have in their
    transition system
    :param domain_name: name of the planning domain. The experiment data should be under generated_final/'domain_name"
    :param compl_1: the maximum feature complexity used in experiment 1
    :param compl_2: the maximum feature complexity used in experiment 2
    :param title: title of the plot
    :return: None, plot the graphs and save them to figures/per_instance/'domain_name'.png
    """
    timings_1, instances_1 = get_timings_instances(domain_name, compl_1, 1, 1)
    timings_2, instances_2 = get_timings_instances(domain_name, compl_2, 2, 2)

    working_1 = [t for t in timings_1 if works(t)]
    working_2 = [t for t in timings_2 if works(t)]

    sorted_instances_2 = sorted(instances_2, key=lambda inst: get_num_states(domain_name, inst))

    instance_1_idx = [instances_1.index(inst) for inst in sorted_instances_2]
    instance_2_idx = [instances_2.index(inst) for inst in sorted_instances_2]

    avg_per_instance_1 = [np.mean([sketch[i][0] for sketch in working_1]) / 1_000_000_000 for i in instance_1_idx]
    avg_per_instance_2 = [np.mean([sketch[i][0] for sketch in working_2]) / 1_000_000_000 for i in instance_2_idx]

    plt.plot(avg_per_instance_1, '-o', label="experiment1")
    plt.plot(avg_per_instance_2, '-o', label="experiment2")
    plt.xlabel = "instance"
    plt.ylabel = "average time (s)"
    plt.title(f"{title}")
    plt.legend()
    plt.savefig(f"../../figures/per_instance/{domain_name}.png")
    plt.show()


def avg_time_two_experiments_per_instace_size(domain_name, compl_1, compl_2, title):
    """
    Plot the average time it takes to verify a good sketch per instance size for experiment 1 and 2.
    The size of an instance is equal to the amount of states it has.
    :param domain_name:
    :param compl_1: max feature complexity in experiment 1
    :param compl_2: max feature complexity in experiment 1
    :param title: Title of the plot
    :return: Show and save the graph in "figures/per_state_size/{domain_name}.png"
    """
    timings_1, instances_1 = get_timings_instances(domain_name, compl_1, 1, 1)
    timings_2, instances_2 = get_timings_instances(domain_name, compl_2, 2, 2)

    working_1 = [t for t in timings_1 if works(t)]
    working_2 = [t for t in timings_2 if works(t)]

    num_states_1 = [get_num_states(domain_name, inst) for inst in instances_1]
    num_states_2 = [get_num_states(domain_name, inst) for inst in instances_2]

    # sorted_instances_2 = sorted(instances_2, key=lambda inst: get_num_states(domain_name, inst))
    # sorted_instances_1 = sorted(instances_1, key=lambda inst: get_num_states(domain_name, inst))

    # instance_1_idx = [instances_1.index(inst) for inst in sorted_instances_1]
    # instance_2_idx = [instances_2.index(inst) for inst in sorted_instances_2]

    avg_per_instance_1 = [np.mean([sketch[i][0] for sketch in working_1]) / 1_000_000_000 for i, inst in
                          enumerate(instances_1)]
    avg_per_instance_2 = [np.mean([sketch[i][0] for sketch in working_2]) / 1_000_000_000 for i, inst in
                          enumerate(instances_2)]

    zip(num_states_1, avg_per_instance_1)
    zip(num_states_2, avg_per_instance_2)

    avg_time_per_state_size_1 = {ns: [] for ns, t in zip(num_states_1, avg_per_instance_1)}
    for ns, t in zip(num_states_1, avg_per_instance_1):
        avg_time_per_state_size_1[ns].append(t)

    avg_time_per_state_size_2 = {ns: [] for ns, t in zip(num_states_2, avg_per_instance_2)}
    for ns, t in zip(num_states_2, avg_per_instance_2):
        avg_time_per_state_size_2[ns].append(t)

    sorted_per_state_size_1 = sorted(avg_time_per_state_size_1.items(), key=lambda x: x[0])
    y1 = [sum(t) / len(t) for r, t in sorted_per_state_size_1]
    x1 = [r for r, t in sorted_per_state_size_1]

    sorted_per_state_size_2 = sorted(avg_time_per_state_size_2.items(), key=lambda x: x[0])
    y2 = [sum(t) / len(t) for r, t in sorted_per_state_size_2]
    x2 = [r for r, t in sorted_per_state_size_2]

    plt.plot(x1, y1, '-o', label="experiment1")
    plt.plot(x2, y2, '-o', label="experiment2")
    plt.xlabel("number of states")
    plt.ylabel("average time (s)")
    plt.title(f"{title}")
    plt.legend()
    plt.savefig(f"../../figures/per_state_size/{domain_name}.png")
    plt.show()


def add_to_plot_rule_size_time(domain_name, complexity, num_f, num_rules, instance, label):
    """
    Add the average time to verify a good sketch over one specific instance per number of expanded sketch rules for
    one experiment to the existing plot.
    :param domain_name:
    :param complexity: the maximum complexity a feature could have in this experiment
    :param num_f: maximum number of features of the experiment
    :param num_rules: the number of rules a sketch can have in this experiment
    :param instance: the name of the pddl file of the instance that we want to use
    :param label: the name of this plot-line in the legend of the full plot
    :return: None, add the graph line to the existing plot
    """
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

        working_times = [sketch_timings[instance_idx][0] / 1000000000 for sketch_timings in timings if
                         works(sketch_timings)]
        num_rules_times = [(Sketch.deserialize(s).expand(bounds).n_rules(), t) for s, t in zip(sketches, working_times)]

        sorted_rules = {r: [] for r, t in num_rules_times}
        for r, t in num_rules_times:
            sorted_rules[r].append(t)

        sorted_sorted_rules = sorted(sorted_rules.items(), key=lambda x: x[0])
        y = [sum(t) / len(t) for r, t in sorted_sorted_rules]
        x = [r for r, t in sorted_sorted_rules]
        # err = [np.std([i for i in idxs[1]]) for idxs in sorted_sorted_rules]

        # plt.errorbar(x, y, err, fmt="-X", label=domain_name)
        plt.plot(x, y, '-o', label=label, zorder=10 - num_rules)


def plot_rule_size_time_for_domain(domain_name, complexity_1, complexity_2, instance, title):
    """
    Plot the average time to verify a good sketch over one specific instance per number of expanded sketch rules for
    experiment 1 and 2.
    :param domain_name:
    :param complexity_1: Maximum feature complexity used in experiment 1
    :param complexity_2: Maximum feature complexity used in experiment 2
    :param instance: The instance on which we verify
    :param title: Title of the plot
    :return:
    """
    add_to_plot_rule_size_time(domain_name, complexity_1, 1, 1, instance, "experiment1")
    add_to_plot_rule_size_time(domain_name, complexity_2, 2, 2, instance, "experiment2")

    plt.legend()
    plt.ylabel("average time (s)")
    plt.xlabel("number of expanded rules")
    plt.title(f"{title}")
    plt.savefig(f"../../figures/rule_size/{domain_name}.png")
    plt.show()


if __name__ == '__main__':
    # avg_time_two_experiments_per_instace("blocksworld-on", 4, 4, "Blocksworld-On")
    # avg_time_two_experiments_per_instace("delivery", 5, 4, "Delivery")
    # avg_time_two_experiments_per_instace("gripper-strips", 4, 4, "Gripper")
    # avg_time_two_experiments_per_instace("miconic", 2, 2, "Miconic")

    barchart_avg_time_two_experiments()

    avg_time_two_experiments_per_instace_size("blocksworld-on", 4, 4, "Blocksworld-On")
    avg_time_two_experiments_per_instace_size("delivery", 5, 4, "Delivery")
    avg_time_two_experiments_per_instace_size("gripper-strips", 4, 4, "Gripper")
    avg_time_two_experiments_per_instace_size("miconic", 2, 2, "Miconic")

    plot_rule_size_time_for_domain("blocksworld-on", 4, 4, "p-3-0.pddl", "Blocksworld-On")
    plot_rule_size_time_for_domain("delivery", 5, 4, "instance_2_2_0.pddl", "Delivery")
    plot_rule_size_time_for_domain("gripper-strips", 4, 4, "p-2-0.pddl", "Gripper")
    plot_rule_size_time_for_domain("miconic", 2, 2, "p-4-2-0.pddl", "Miconic")
