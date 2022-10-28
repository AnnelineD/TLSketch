import dlplan


def show_condition(c: dlplan.BaseCondition, representation: str = None) -> str:
    match c.str()[:9]:
        case "(:c_b_pos": return representation if representation else f"b{c.get_index()}"
        case "(:c_b_neg": return f"¬{representation}" if representation else f"¬b{c.get_index()}"
        case "(:c_n_eq ": return f"{representation}=0" if representation else f"n{c.get_index()}=0"
        case "(:c_n_gt ": return f"{representation}>0" if representation else f"n{c.get_index()}>0"
        case _: return "invalid"  # TODO raise error


def show_effect(e: dlplan.BaseEffect, representation: str = None) -> str:
    match e.str()[:9]:
        case "(:e_b_pos": return representation if representation else f"b{e.get_index()}"
        case "(:e_b_neg": return f"¬{representation}" if representation else f"¬b{e.get_index()}"
        case "(:e_b_bot": return f"{representation}?" if representation else f"b{e.get_index()}?"
        case "(:e_n_inc": return f"{representation}↑" if representation else f"n{e.get_index()}↑"
        case "(:e_n_dec": return f"{representation}↓" if representation else f"n{e.get_index()}↓"
        case "(:e_n_bot": return f"{representation}?" if representation else f"n{e.get_index()}?"
        case _: return "invalid"  # TODO raise error
