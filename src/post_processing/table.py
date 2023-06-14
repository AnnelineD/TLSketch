import json
from numpy import round


def get_table(domains: list[tuple[str, int]]):
    heads = ["", "#I", "C", "#F", "#CS", "#GS",
             "#Timed out",
             "avg time failed", "avg time good", "total time"]

    def time_rounding(t):
        return round(t/1_000_000_000, 2)

    def get_line(name, compl):
        data = get_data(name, compl, 1,1)
        return [name, data["n_instances"], compl, data["n_features"], data["n_tested"], data["n_working"],
                data["n_timed_out"],
                time_rounding(data["avg_time_not_working_ns"]), time_rounding(data["avg_time_working_ns"]), time_rounding(data["total_time"])]

    lines = [' & '.join(map(str, get_line(name, compl))) for name, compl in domains]

    return ' & '.join(heads) + "\\\ \n" \
        + '\\\ \n'.join(lines)


def get_data(domain_name, complexity, num_f, num_rules) -> dict:
    with open(f"../../generated/{domain_name}/{'_'.join([str(complexity)]*5)}_180_10000_{num_f}/rules_{num_rules}.json") as f:
        info = json.load(f)
        n_working = len(info["working"])
        n_tested = info["number_tested"]
        n_timed_out = len(info["timed_out"])
        sum_per_sketch = lambda l: sum([t for t, w in l])
        n_instances = len(info["instance_files"])
        n_tested = info["number_tested"]

    with open(f"../../cache/{domain_name}/features/{'_'.join([str(complexity)]*5)}_180_10000.json") as f:
        features = json.load(f)
        n_features = len([f for f in features if (f.startswith("n_") or f.startswith("b_")) and f not in ["b_empty(c_top)",
                                                                 "b_empty(c_bot)",
                                                                 "n_count(c_top)",
                                                                 "n_count(c_bot)"]])

    def works(l):
        return all(w == 1 for t, w in l)

    def failed(l):
        return any(w == 0 for t, w in l)
    return {"complexity": complexity,
            "n_tested": n_tested,
            "n_working": n_working,
            "n_features": n_features,
            "n_instances": n_instances,
            "n_timed_out": n_timed_out,
            "avg_time_working_ns": sum([sum_per_sketch(sk) for sk in info["timings"] if works(sk)])/n_working,
            "avg_time_not_working_ns": sum([sum_per_sketch(sk) for sk in info["timings"] if failed(sk)])/(n_tested - n_working - n_timed_out),
            "total_time": sum([sum_per_sketch(sk) for sk in info["timings"]])
            }


if __name__ == '__main__':
    domains = [("blocksworld", 4),
               ("blocksworld-on", 4),
               # ("child-snack", 4),
               ("delivery", 5),
               ("gripper-strips", 4),
               ("miconic", 4),
               ("reward-strips", 4),
               ("spanner", 6),
               ("grid-visit-all", 4)]
    print(get_table(domains))
