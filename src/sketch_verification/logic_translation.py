import pynusmv
import ltl
import ctl

from src.dlplan_utils import repr_feature
from src.logics.feature_vars import BooleanVar, NumericalVar
from pynusmv import prop


def ltl_to_input(f: ltl.LTLFormula) -> pynusmv.prop.Spec:
    match f:
        case ltl.Top(): return prop.true()
        case ltl.Bottom(): return prop.false()
        case BooleanVar(f, v): return prop.atom(f"{repr_feature(f)}={str(v).upper()}")
        case NumericalVar(f, v): return prop.atom(f"{repr_feature(f)}={str(v).upper()}")
        case ltl.Var(s) as x: return prop.atom(f"{s}")  # TODO make a special goal var
        case ltl.Not(p): return prop.not_(ltl_to_input(p))
        case ltl.And(p, q): return ltl_to_input(p) & ltl_to_input(q)
        case ltl.Or(p, q): return ltl_to_input(p) | ltl_to_input(q)
        case ltl.Next(p): return prop.x(ltl_to_input(p))
        case ltl.Until(p, q): return prop.u(ltl_to_input(p), ltl_to_input(q))
        case ltl.Release(p, q): raise NotImplementedError(Release(p, q))
        case ltl.Then(p, q): return prop.imply(ltl_to_input(p), ltl_to_input(q))
        case ltl.Iff(p, q): return prop.iff(ltl_to_input(p), ltl_to_input(q))
        case ltl.Finally(p, bound):
            if not bound: return prop.f(ltl_to_input(p))
            else:
                s, e = bound
                raise NotImplementedError("bound")
        case ltl.Globally(p): return prop.g(ltl_to_input(p))
        case ltl.Weak(p, q):  # = Release(q, Or(p, q))
            raise NotImplementedError("weak")
        case ltl.Strong(p, q):  # = Until(q, And(p, q))
            raise NotImplementedError("strong")
        case ltl.Previous(p):
            spec = ltl_to_input(p)
            s = prop.Spec(pynusmv.node.nsnode.find_node(pynusmv.parser.nsparser.OP_PREC, spec._ptr, None), freeit=False)
            s._car = spec
            return s
        case ltl.Once(p, bound):
            if not bound:
                spec = ltl_to_input(p)
                s = prop.Spec(pynusmv.node.nsnode.find_node(pynusmv.parser.nsparser.OP_ONCE, spec._ptr, None), freeit=False)
                s._car = spec
                return s
            else:
                s, e = bound
                raise NotImplementedError("strong")

        case _: raise NotImplementedError(ltl)


def ctl_to_input(f: ctl.CTLFormula) -> pynusmv.prop.Spec:
    match f:
        case ctl.Top(): return prop.true()
        case ctl.Bottom(): return prop.false()
        case ctl.Var(s) as x: return prop.atom(f"{s}")  # TODO make a special goal var
        case ctl.Not(p): return prop.not_(ctl_to_input(p))
        case ctl.And(p, q): return ctl_to_input(p) & ctl_to_input(q)
        case ctl.Or(p, q): return ctl_to_input(p) | ctl_to_input(q)
        case ctl.EX(p): return prop.ex(ctl_to_input(p))
        case ctl.AX(p): return prop.ax(ctl_to_input(p))
        case ctl.Then(p, q): return prop.imply(ctl_to_input(p), ctl_to_input(q))
        case ctl.Iff(p, q): return prop.iff(ctl_to_input(p), ctl_to_input(q))
        case ctl.EF(p, bound):
            if not bound: return prop.ef(ctl_to_input(p))
            else: NotImplementedError(f)
        case ctl.AF(p, bound):
            if not bound: return prop.af(ctl_to_input(p))
            else: NotImplementedError(f)
        case ctl.EG(p): return prop.eg(ctl_to_input(p))
        case ctl.AG(p): return prop.ag(ctl_to_input(p))
        case _: raise NotImplementedError(f)