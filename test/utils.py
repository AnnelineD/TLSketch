def ass_same_elements(l1: list, l2: list):
    if ((len(l1) == len(l2)) and
            (all(i in l1 for i in l2))):
        return True
    return False
