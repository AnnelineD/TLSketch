import dlplan
import tarski.fstrips

#from .tarski import TarskiTransitionSystem
from .tarski_manipulation import sort_constants, typed_permutations
from .types import *
from .transition_system import StateStr, TransitionSystem


def dlvocab_from_tarski(domain_lan: tarski.fol.FirstOrderLanguage, add_goals=True) -> dlplan.core.VocabularyInfo:
    v = dlplan.core.VocabularyInfo()
    for p in domain_lan.predicates:
        if isinstance(p.name, str):
            v.add_predicate(str(p.name), p.arity, False)
            if add_goals:
                v.add_predicate(str(p.name) + '_g', p.arity, True)
    for c in domain_lan.constants():
        v.add_constant(c.name)
    return v


def dlinstance_from_tarski(domain: tarski.fstrips.Problem, instance: tarski.fstrips.Problem) -> dlplan.core.InstanceInfo:
    v: dlplan.core.VocabularyInfo = dlvocab_from_tarski(domain.language)
    i = dlplan.core.InstanceInfo(v)
    d: dict[TSort, list[TConstant]] = sort_constants(instance.language)
    goal = instance.goal

    for p in domain.language.predicates:
        if isinstance(p.name, str):
            if not p.sort:
                i.add_atom(p.name, [])
            else:
            # TODO delete the on(b1, b1)
                combs: list[tuple[TConstant]] = typed_permutations(p.sort, d)
                for c in combs:
                    i.add_atom(p.name, [obj.name for obj in c])

    def add_goal(g):
        match g:
            case tarski.syntax.Atom(): i.add_static_atom(g.predicate.name + '_g', [a.name for a in g.subterms])
            case tarski.syntax.CompoundFormula():
                match g.connective:
                    case tarski.syntax.Connective.And:
                        for s in g.subformulas: add_goal(s)
                    case _:
                        raise NotImplementedError(g.connective)
            case _: raise NotImplementedError

    add_goal(goal)
    return i

def functional_to_sexpr_many(s: str, sep: str = "\n") -> str:
    """
    Convert functional notation to S-expressions, for one or more
    whitespace-separated expressions in `s`.

      c_all(r_primitive(on-disk_g,0,1),c_projection(r_primitive(on-disk,0,1),0))
      -> (c_all (r_primitive on-disk_g 0 1) (c_projection (r_primitive on-disk 0 1) 0))

    Multiple expressions are separated by `sep` in the output (default newline).
    Whitespace is ignored anywhere inside expressions. At top level, expressions
    must be separated by whitespace.
    """
    n = len(s)
    i = 0
    out = []
    first_top = True

    def peek() -> str:
        return s[i] if i < n else ""

    def adv() -> str:
        nonlocal i
        ch = s[i]
        i += 1
        return ch

    def skip_ws():
        nonlocal i
        while i < n and s[i].isspace():
            i += 1

    def error(msg: str):
        # Show a short context around the error position
        start = max(0, i - 20)
        end = min(n, i + 20)
        context = s[start:end].replace("\n", "\\n")
        raise SyntaxError(f"{msg} at pos {i}. Context: {context!r}")

    def read_ident() -> str:
        nonlocal i
        # [A-Za-z_][A-Za-z0-9_-]*
        if i >= n or not (s[i].isalpha() or s[i] == "_"):
            error("Expected identifier")
        start = i
        j = i + 1
        while j < n and (s[j].isalnum() or s[j] in "_-"):
            j += 1
        ident = s[start:j]
        i = j
        return ident

    def read_number() -> str:
        # -? [0-9]+ (.[0-9]+)?
        nonlocal i
        start = i
        if s[i] == "-":
            if i + 1 >= n or not s[i + 1].isdigit():
                error("'-' must be followed by a digit for a number")
            i += 1
        if not s[i].isdigit():
            error("Expected digit")
        while i < n and s[i].isdigit():
            i += 1
        if i < n and s[i] == ".":
            if i + 1 >= n or not s[i + 1].isdigit():
                error("Expected digit after '.' in number")
            i += 1
            while i < n and s[i].isdigit():
                i += 1
        return s[start:i]

    def parse_term():
        """
        term := IDENT '(' [args] ')' | IDENT | NUMBER
        args := term (',' term)*
        Writes directly into `out`.
        """
        skip_ws()
        ch = peek()
        if not ch:
            error("Unexpected end of input while parsing term")

        if ch.isalpha() or ch == "_":
            name = read_ident()
            skip_ws()
            if peek() == "(":
                adv()  # '('
                # Start function call
                out.append("(")
                out.append(name)
                skip_ws()
                if peek() == ")":
                    adv()  # ')'
                    out.append(")")
                    return
                # args
                while True:
                    out.append(" ")
                    parse_term()
                    skip_ws()
                    ch2 = peek()
                    if ch2 == ",":
                        adv()
                        skip_ws()
                        continue
                    elif ch2 == ")":
                        adv()
                        out.append(")")
                        return
                    else:
                        error("Expected ',' or ')' in argument list")
            else:
                # bare identifier atom
                out.append(name)
                return

        elif ch == "-" or ch.isdigit():
            # number (only treat '-' as number if followed by digit)
            if ch == "-" and (i + 1 >= n or not s[i + 1].isdigit()):
                error("Stray '-' not part of a number")
            num = read_number()
            out.append(num)
            return

        else:
            error(f"Unexpected character {ch!r}")

    # Parse multiple top-level expressions separated by whitespace
    while True:
        skip_ws()
        if i >= n:
            break
        if not first_top:
            out.append(sep)
        parse_term()
        skip_ws()
        # require that the next non-ws at top-level is EOF or ws (enforced by loop)
        first_top = False

    return "".join(out)


def space_from_ts(ts: TransitionSystem, file):
    for i, s in enumerate(ts.states):
        for f in s:
            print(f"(holds {functional_to_sexpr_many(f)} {i})", file=file)
    for i, (nbs, acts) in enumerate(ts.graph.adj):
        for (j, act) in zip(nbs, acts):
            print(f"(transition {i} {functional_to_sexpr_many(act)} {j})", file=file)
    print(f"(init {ts.init})", file=file)
    for g in ts.goals:
        print(f"(goal {g})", file=file)


if __name__ == "__main__":
    # Single expression
    ex1 = "c_all(r_primitive(on-disk_g,0,1),c_projection(r_primitive(on-disk,0,1),0))"
    print(functional_to_sexpr_many(ex1))
    # Multiple expressions (whitespace-separated at top level)
    ex2 = "f(a, 1)\n   g ( b , c)\t h_1(on-disk, -2, 3.5)"
    print("---")
    print(functional_to_sexpr_many(ex2))
