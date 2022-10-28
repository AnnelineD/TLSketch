import dlplan


def show_condition(c: dlplan.BaseCondition, representation: str) -> str:
    match c.str()[:9]:
        case "(:c_b_pos": return representation
        case "(:c_b_neg": return f"¬{representation}"
        case "(:c_n_eq ": return f"{representation}=0"
        case "(:c_n_gt ": return f"{representation}>0"
        case _: return "invalid"  # TODO raise error


def show_effect(e: dlplan.BaseEffect, representation: str) -> str:
    match e.str()[:9]:
        case "(:e_b_pos": return representation
        case "(:e_b_neg": return f"¬{representation}"
        case "(:e_b_bot": return f"{representation}?"
        case "(:e_n_inc": return f"{representation}↑"
        case "(:e_n_dec": return f"{representation}↓"
        case "(:e_n_bot": return f"{representation}?"
        case _: return "invalid"  # TODO raise error
