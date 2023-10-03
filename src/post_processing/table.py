# Create tables for reporting results of the sketch generation and verification

import json
from numpy import round


def get_table(domains: list[tuple[str, int]], experiment_idx) -> str:
    """
    Report data of generating and verifying sketches experiments in a table. For each domain, following numbers are
    reported:
        The amount of instances used to verify the sketches,
        The maximum complexity of the features used in the candidate sketches,
        The amount of features that were generated and used in the candidate sketches,
        The amount of candidate sketches that were generated,
        The amount of candidate sketches that were verified as 'good',
        The average time it takes to verify that a candidate sketch is not good,
        The average time it takes to verify a candidate sketch (over all instances) that is good,
        The average time it takes to verify a candidate sketch that is good on one instance,
        The total time it took to verify all candidate sketches.
    For experiment 1, all times are in seconds
    For experiment 2, the total time is stated in hours, all other times are in seconds
    :param domains: list of domain names and the maximum features used for that domain. For each domain, all data files
    regarding the generated sketches (sketches and timings) should be stored in the directory
    generated_final/'domain_name'/...
    Additionally, the features should be cached in cache/'domain_name'/features
    :param experiment_idx: 1 for experiment 1: generating and verifying sketches with one rule and max one feature,
                           2 for experiment 2: generating and verifying sketches with two rules and max two features
    :return: The table in Latex code
    """
    heads = ["", "$\\vert I \\vert$", "C", "$\\vert F \\vert $", "$\\vert CS \\vert$", "$\\vert GS \\vert$",
             "$\\overline{t_{failed}}$", "$\\overline{t_{good}}$", "$\\overline{t_{good}}/I$",
             "$t_{total}$" + f" {'(h)' if experiment_idx == 2 else ''} "]

    def time_rounding(t):
        """Convert time from nanoseconds to seconds, and round to two decimals"""
        return round(t / 1_000_000_000, 2)

    def get_line(name, compl, experiment_num):
        """Get one row of the table. i.e., For one domain, get the full row with all numbers that need to be reported"""
        data = get_data(name, compl, experiment_num, experiment_num)
        return [name, data["n_instances"], compl, data["n_features"], data["n_tested"], data["n_working"],
                time_rounding(data["avg_time_not_working_ns"]), time_rounding(data["avg_time_working_ns"]),
                time_rounding(data["avg_time_working_ns"] / data["n_instances"]),
                time_rounding(data["total_time"]) if experiment_idx == 1 else time_rounding(data["total_time"] / 3600)]

    lines = [' & '.join(map(str, get_line(name, compl, experiment_idx))) for name, compl in domains]

    return ' & '.join(heads) + "\\\ \hline \n" \
        + '\\\ \n'.join(lines)


def get_data(domain_name: str, complexity: int, num_f: int, num_rules: int) -> dict:
    """
    For one domain, retrieve all data saved when generating and verifying sketches with features of maximum complexity,
    n rules and maximum n features.
    :param domain_name: Name of the domain.
    The data files regarding the generated sketches should be stored in the directory
    generated_final/'domain_name'/'complexity_..._num_f'/rules_'num_rules'.
    The data files with the timings should be stored in
    generated_final/'domain_name'/timers/'complexity_..._num_f'/rules_'num_rules'.
    Additionally, the features should be cached in cache/'domain_name'/features
    :param complexity: The maximum complexity of the features that are generated to use in the candidate sketches
    :param num_f: The maximum number of features a sketch can use
    :param num_rules: The number of rules a sketch can use
    :return: A dictionary with
            "complexity": The maximum complexity of the features used in the candidate sketches
            "n_tested": The number of candidate sketches that were generated and verified
            "n_working": The number of candidate sketches that were good
            "n_features": The total number of features of maximum complexity that were generated
            "n_instances": The number of instances that were used to verify the candidate sketches
            "n_timed_out": The number of sketches that took too long to verify and were skipped
            "avg_time_working_ns": The average time it took to verify a good sketch in nanoseconds
            "avg_time_not_working_ns": The average time it took to verify a non-good sketch in nanoseconds
            "total_time": The total time it took to generate and verify the candidate sketches in nanoseconds

    """
    with open(
            f"../../generated_final/{domain_name}/{'_'.join([str(complexity)] * 5)}_180_10000_{num_f}/rules_{num_rules}.json") as f:
        info = json.load(f)
        n_working = len(info["working"])
        n_tested = info["number_tested"]
        n_timed_out = len(info["timed_out"])
        sum_per_sketch = lambda l: sum([t for t, w in l])
        n_instances = len(info["instance_files"])
        n_tested = info["number_tested"]

    with open(f"../../cache/{domain_name}/features/{'_'.join([str(complexity)] * 5)}_180_10000.json") as f:
        features = json.load(f)
        n_features = len(
            [f for f in features if (f.startswith("n_") or f.startswith("b_")) and f not in ["b_empty(c_top)",
                                                                                             "b_empty(c_bot)",
                                                                                             "n_count(c_top)",
                                                                                             "n_count(c_bot)"]])

    with open(
            f"../../generated_final/{domain_name}/timers/{'_'.join([str(complexity)] * 5)}_180_10000_{num_f}/rules_{num_rules}.json") as f:
        total_time = json.load(f)
    print(domain_name, n_timed_out)

    def works(l: tuple[int, int]) -> bool:
        """for a sketch, return true if it is good, false otherwise"""
        return all(w == 1 for t, w in l)

    def failed(l: tuple[int, int]) -> bool:
        """for a sketch, return true if it is not good, false otherwise (good or timed-out)"""
        return any(w == 0 for t, w in l)

    return {"complexity": complexity,
            "n_tested": n_tested,
            "n_working": n_working,
            "n_features": n_features,
            "n_instances": n_instances,
            "n_timed_out": n_timed_out,
            "avg_time_working_ns": sum([sum_per_sketch(sk) for sk in info["timings"] if works(sk)]) / n_working,
            "avg_time_not_working_ns": sum([sum_per_sketch(sk) for sk in info["timings"] if failed(sk)]) / (
                        n_tested - n_working - n_timed_out),
            "total_time": total_time
            # "total_time": sum([sum_per_sketch(sk) for sk in info["timings"]])
            }


if __name__ == '__main__':
    domains = [("blocksworld", 4),
               ("blocksworld-on", 4),
               # ("child-snack", 6),
               ("delivery", 5),
               ("gripper-strips", 4),
               ("miconic", 2),
               ("reward-strips", 2),
               ("spanner", 6),
               ("grid-visit-all", 2)]
    print(get_table(domains, 1))
    print()
    domains = [
               ("blocksworld-on", 4),
               ("delivery", 4),
               ("gripper-strips", 4),
               ("miconic", 2)]
    print(get_table(domains, 2))
