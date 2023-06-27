import json

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
        instances = instances

        for i in instances:
            with open(
                    f"../../cache_final/{domain_name}/features/{'_'.join([str(complexity)] * 5)}_180_10000/{i[1].removesuffix('.pddl')}.json") as f:
                feature_vals = json.load(f)

                def get_bounds(feature_valuations) -> dict[str, (int, int)]:
                    return {f_name: (min(feature_valuations[f_name]), max(feature_valuations[f_name]))
                            for f_name in feature_valuations.keys() if f_name.startswith('n_')}

                bounds = get_bounds(feature_vals)
                all_bounds.append(bounds)

        def works(l):
            return all(w == 1 for t, w in l)

        # print(len(sketches))
        # print(timings)
        working_times = [[i[0]/1000000000 for i in s] for s in timings if works(s)]
        # print(working_times)
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



if __name__ == '__main__':
    avg_time_per_num_rules_one_domain("blocksworld-on", 4, 4)
    avg_time_per_num_rules_one_domain("miconic", 2, 2)      # TODO
    avg_time_per_num_rules_one_domain("delivery", 5, 4)
    avg_time_per_num_rules_one_domain("gripper-strips", 4, 4)  # TODO
    """
    avg_time_per_num_rules([("blocksworld", 4, 1, 1),
                            ("grid-visit-all", 2, 1, 1),
                            ("spanner", 6, 1, 1),
                            ("reward-strips", 2, 1, 1)])
    """
    avg_time_per_num_rules([("blocksworld", 4, 1, 1)])
    avg_time_per_num_rules([("grid-visit-all", 2, 1, 1)])
    avg_time_per_num_rules([("spanner", 6, 1, 1)])
    avg_time_per_num_rules([("reward-strips", 2, 1, 1)])
    """
    avg_time_per_num_rules([("blocksworld-on", 4, 2, 2),
                            ("miconic", 2, 2, 2),
                            ("delivery", 4, 2, 2),
                            ("gripper-strips", 4, 2, 2)])
    """