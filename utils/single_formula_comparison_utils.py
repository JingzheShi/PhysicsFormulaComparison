import re
from sympy import *
from sympy.parsing.latex import parse_latex 
from sympy import latex
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*use of fork.*")

units_latex={r'\kg':r'\kg',r's':r's',r'm':r'm',r'A':r'A',r'K':r'K',r'g':r'0.001*\kg'}
UNITS_LATEX = units_latex
UNITS_EXPRESSION = {parse_latex(x):units_latex[x] for x in units_latex}
EPSILON_FOR_EQUAL = 1e-5
RELA_EPSILON_FOR_ALMOST_CONSTANT_EVAL = 1e-5
TOLERABLE_DIFF_MAX = 5
TOLERABLE_DIFF_FRACTION = 0.6
TIMEOUT = 0.6

ONLY_PRINT_WHEN_CALLED_FOR_DEBUG = False
if __name__ == "__main__":
    ONLY_PRINT_WHEN_CALLED_FOR_DEBUG = True


# import sympy as sp
# import stopit
# def solve_with_timeout(eq, var, timeout=1.0):
#     result = None
#     with stopit.ThreadingTimeout(timeout) as tt:
#         result = sp.solve(eq, var)
#     return result

import sympy as sp
import os
import pickle
import tempfile


def solve_with_timeout(eq, var, timeout=0.6):
    eq_str = str(eq)
    var_str = str(var)

    # Temporary file to transfer result
    import random
    import string
    # generate a random string suffix, 15-char, each char is a-z, A-Z, 0-9.
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
    with tempfile.NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
        pid = os.fork()

        if pid == 0:
            # Child process
            try:
                eq = sp.sympify(eq_str)
                var = sp.symbols(var_str)
                result = sp.solve(eq, var)
                with open(tmp.name, 'wb') as f:
                    pickle.dump(result, f)
            except Exception as e:
                with open(tmp.name, 'wb') as f:
                    pickle.dump(e, f)
            os._exit(0)

        else:
            # Parent process
            import time
            start = time.time()
            while True:
                pid_done, status = os.waitpid(pid, os.WNOHANG)
                if pid_done != 0:
                    break
                if time.time() - start > timeout:
                    os.kill(pid, 9)
                    os.waitpid(pid, 0)
                    return None
                time.sleep(0.01)

            # Retrieve result
            try:
                with open(tmp.name, 'rb') as f:
                    result = pickle.load(f)
                if isinstance(result, Exception):
                    return None
                return result
            except Exception:
                return None















# import sys

# def ignore_unraisable_exception(unraisable):
#     # You can also log it if you wish
#     pass

# sys.unraisablehook = ignore_unraisable_exception


import sympy as sp
import numpy as np
np.seterr(all='ignore') 
if __name__ != "__main__":
    from utils.data_utils import simplify_latex_expr
else:
    from data_utils import simplify_latex_expr

if 0:
    # deprecated, but kept for reference. DO NOT USE NOR DELETE!
    def is_almost_constant(expr, variables, tol=RELA_EPSILON_FOR_ALMOST_CONSTANT_EVAL, n_samples=30, minNumber = 20, max_counter = 40, sample_range=(-20, 20), if_print = False):
        
        """
        Checks if expr (sympy expression) is almost a constant function of the given variables.
        Evaluates at n_samples random points and checks if std/max variation is below tol.
        """
        # Lambdify for fast numeric evaluation
        f = sp.lambdify(list(variables), expr, 'numpy')
        values = []
        real_vals = []
        complex_vals = []
        InvalidValue_flag = False
        rng = np.random.default_rng()
        counter = 0
        for _ in range(n_samples):
            sample = [rng.uniform(*sample_range) for _ in variables]
            try:
                val = f(*sample)
                # Check for nan or inf
                if isinstance(val, (float, int, np.floating, np.integer)):
                    if np.isnan(val) or np.isinf(val):
                        InvalidValue_flag = True
                        continue
                    real_vals.append(float(np.real(val)))
                elif isinstance(val, complex):
                    # Handle complex nan/inf
                    if np.isnan(val.real) or np.isnan(val.imag) or np.isinf(val.real) or np.isinf(val.imag):
                        InvalidValue_flag = True
                        continue
                    complex_vals.append(complex(val))
                else:
                    # Some unexpected type
                    InvalidValue_flag = True
                    continue
            except Exception:
                # Catches things like sqrt(-1) for real-valued functions, division by zero, etc.
                InvalidValue_flag = True
                continue
        if (not real_vals) and (not complex_vals):
            return False, "Cannot evaluate expression at given range, all values are invalid."
        if (real_vals or complex_vals):
            while (len(real_vals) < minNumber) and (len(complex_vals) < minNumber) and (counter < max_counter):
                counter += 1
                sample = [rng.uniform(*sample_range) for _ in variables]
                try:
                    val = f(*sample)
                    if isinstance(val, (float, int, np.floating, np.integer)):
                        if np.isnan(val) or np.isinf(val):
                            continue
                        real_vals.append(float(np.real(val)))
                    elif isinstance(val, complex):
                        if np.isnan(val.real) or np.isnan(val.imag) or np.isinf(val.real) or np.isinf(val.imag):
                            continue
                        complex_vals.append(complex(val))
                    else:
                        continue
                except Exception:
                    continue
        if (real_vals and complex_vals):
            while (len(real_vals) < minNumber) or (len(complex_vals) < minNumber) and (counter < max_counter):
                counter += 1
                sample = [rng.uniform(*sample_range) for _ in variables]
                try:
                    val = f(*sample)
                    if isinstance(val, (float, int, np.floating, np.integer)):
                        if np.isnan(val) or np.isinf(val):
                            continue
                        real_vals.append(float(np.real(val)))
                    elif isinstance(val, complex):
                        if np.isnan(val.real) or np.isnan(val.imag) or np.isinf(val.real) or np.isinf(val.imag):
                            continue
                        complex_vals.append(complex(val))
                    else:
                        continue
                except Exception:
                    continue
        
        real_absmean = np.mean(np.abs(real_vals)) if real_vals else 0
        complex_absmean = np.mean([np.abs(c) for c in complex_vals]) if complex_vals else 0
        real_maxMinusmin = np.max(real_vals) - np.min(real_vals) if real_vals else 0
        complex_maxdiffeval = ((np.max(np.real(complex_vals)) - np.min(np.real(complex_vals)))**2 + (np.max(np.imag(complex_vals)) - np.min(np.imag(complex_vals)))**2)**0.5 if complex_vals else 0
        
        identicalFlag = True
        if real_vals:
            if real_maxMinusmin < tol * real_absmean:
                pass
            else:
                identicalFlag = False
            compare_str = f"max-min={real_maxMinusmin}, absmean={real_absmean}"
        if complex_vals:
            if complex_maxdiffeval < tol * complex_absmean:
                pass
            else:
                identicalFlag = False
            compare_str = f"maxdiff={complex_maxdiffeval}, absmean={complex_absmean}"


        if if_print:
            print(f"Checking if {expr} is almost constant with respect to {variables} within range {sample_range} and tolerance {tol}. Result: {real_vals, complex_vals}, {compare_str}")
        return identicalFlag






import sympy as sp
import numpy as np
from sympy.core.function import AppliedUndef

def replace_all_functions_to_freevars(expr):
    applied_functions = list(expr.atoms(AppliedUndef))
    applied_functions_args_dict = dict()
    for f in applied_functions:
        if f not in applied_functions_args_dict:
            applied_functions_args_dict[f] = [str(arg) for arg in f.args]
            # sort the arguments to ensure consistent naming.
    applied_functions_args_dict = {f: sorted(args) for f, args in applied_functions_args_dict.items()}
    
    repl = {
        f: sp.Symbol(f"{f.func.__name__}_which_is_a_var_of_"+"_AND_".join(applied_functions_args_dict[f]))
        for f in applied_functions
    }
    expr_replaced = expr.subs(repl)
    return expr_replaced

def is_almost_equivalent(eq1, eq2, variables=None, tol=1e-6, n_trials=15, sample_range=(-20, 20), if_print=False,
                         max_trials = 20, atleast_trial_when_possible=10, maxmaxtrial=40):
    """
    Compare if two sympy equations eq1 and eq2 are almost equivalent by checking their roots numerically.
    Handles multi-root cases by sorting and pairwise comparison.
    """
    if if_print:
        print(f"Comparing using tol {tol} and n_trials {n_trials} for {eq1} and {eq2}")
    if variables is None:
        eq1 = replace_all_functions_to_freevars(eq1)
        eq2 = replace_all_functions_to_freevars(eq2)
        # functions1 = set(eq1.atoms(AppliedUndef))
        # functions2 = set(eq2.atoms(AppliedUndef))
        # functions_set = functions1.union(functions2)
        variables = list(eq1.free_symbols.union(eq2.free_symbols)) # + list(functions_set)
    if not variables:
        return False, f'no free variable when comparing is_almost_equivalent for {eq1} and {eq2}'
    rng = np.random.default_rng()
    passed_trials = 0
    ineq_trials = 0
    failed_trials = 0
    
    trial = 0
    
    indicator_str = f"{eq1} COMPARING_WITH {eq2} with tol={tol}, n_trials={n_trials}, sample_range={sample_range}, variables={variables} for is_almost_equivalent"
    timeout_var_list = []
    while (passed_trials + ineq_trials <= n_trials):
        trial += 1
        if trial > max_trials and (passed_trials + ineq_trials == 0):
            # already reached max_trials, but all trials failed.
            break
        elif trial > max_trials and (passed_trials + ineq_trials != 0):
            # already reached max_trials, but some trials passed.
            if passed_trials + ineq_trials > atleast_trial_when_possible: # 
                break
            if trial > maxmaxtrial:
                break
        if len(timeout_var_list) == len(variables):
            # All variables have been tried and timed out, no point in continuing
            indicator_str = "Time Out when solving for variables " + str(timeout_var_list) + ", so stopping trials." + indicator_str
            if if_print:
                print(f"All variables {variables} have timed out, stopping trials.")
            break
        left_vars = [v for v in variables if v not in timeout_var_list]
        solve_var = rng.choice(left_vars)
        subst_vars = [v for v in variables if v != solve_var]
        subs = {v: float(rng.uniform(*sample_range)) for v in subst_vars}
        try:
            eq1_sub = eq1.subs(subs)
            eq2_sub = eq2.subs(subs)
            
            sol1 = solve_with_timeout(eq1_sub, solve_var)
            sol2 = solve_with_timeout(eq2_sub, solve_var)

            if sol1 is None or sol2 is None:
                timeout_var_list.append(solve_var)
                if if_print:
                    print(f"Trial {trial}: {solve_var} | sol1={sol1}, sol2={sol2}, which timed out, so this trial failed")
                failed_trials += 1
                continue
            

            # Convert solutions to complex, skip if any is not a number
            try:
                vals1 = [complex(s.evalf()) for s in sol1]
                vals2 = [complex(s.evalf()) for s in sol2]
            except Exception:
                failed_trials += 1
                continue

            continue_flag = False

            if len(vals1) != len(vals2):
                ineq_trials += 1
                if if_print:
                    print(f"Trial {trial}: {solve_var} | sol1={vals1}, sol2={vals2}, which are NOT considered equivalent. Vars equal to: {variables}, subs={subs}")
                continue_flag = True
            elif len(vals1) == 0:
                failed_trials += 1
                if if_print:
                    print(f"Trial {trial}: {solve_var} | sol1={vals1}, sol2={vals2}, which are all empty, so failed trial. Vars equal to: {variables}, subs={subs}")
                continue_flag = True
            if continue_flag:
                continue

            # Any nan/inf in roots means skip this trial
            def invalid(v):
                return (np.isnan(v.real) or np.isnan(v.imag) or 
                        np.isinf(v.real) or np.isinf(v.imag))
            if any(invalid(v) for v in vals1) or any(invalid(v) for v in vals2):
                failed_trials += 1
                continue

            # Sort by real, then imag part
            vals1_sorted = sorted(vals1, key=lambda v: (v.real, v.imag))
            vals2_sorted = sorted(vals2, key=lambda v: (v.real, v.imag))
            diff_list = []
            
            all_match = True
            for v1, v2 in zip(vals1_sorted, vals2_sorted):
                mean_val = (abs(v1) + abs(v2)) / 2.0
                if mean_val == 0:
                    rel_diff = abs(v1 - v2)
                else:
                    rel_diff = abs(v1 - v2) / mean_val
                diff_list.append(rel_diff)
                if rel_diff >= tol:
                    all_match = False
                    break
            if if_print:
                print(f"Trial {trial}: {solve_var} | sol1={vals1_sorted}, sol2={vals2_sorted}, all_match={all_match}: relaDiff = {diff_list} (when sol=0, this is Diff). Vars equal to: {variables}, subs={subs}")
            if all_match:
                passed_trials += 1
            else:
                ineq_trials += 1
        except Exception as e:
            failed_trials += 1
            if if_print:
                print(f"Trial {trial}: Exception {e}")
            continue
    if passed_trials + ineq_trials == 0:
        if if_print:
            print(False, f"No passed trials when comparing is_almost_equivalent for {eq1} and {eq2}, failed_trials={failed_trials} " + indicator_str)
        return False, f"No passed trials when comparing is_almost_equivalent for {eq1} and {eq2}, failed_trials={failed_trials} " + indicator_str
    if ineq_trials == 0 and passed_trials + ineq_trials >= min([atleast_trial_when_possible, n_trials]):
        if if_print:
            print(True, f"Passed {passed_trials} trials, ineq {ineq_trials} trials, unsuccessful {failed_trials} trials. " + indicator_str)
        return True, f"Passed {passed_trials} trials, ineq {ineq_trials} trials, unsuccessful {failed_trials} trials. " + indicator_str
    else:
        if if_print:
            print(False, f"Only passed {passed_trials}, ineq {ineq_trials} trials, failed_trials {failed_trials}. " + indicator_str)
        return False, f"Only passed {passed_trials}, ineq {ineq_trials} trials, failed_trials {failed_trials}. " + indicator_str












def whether_data_with_unit(expression, units_expression):
    free_variables = expression.free_symbols
    org_count = len(free_variables)
    for item in units_expression:
        if item in free_variables:
            org_count -= 1
    if org_count <= 1:
        return True
    else:
        return False

def get_unit_and_free_variable(expression,units_expression):
    free_variables = expression.free_symbols
    org_count = len(free_variables)
    unit_lst=[]
    for item in units_expression:
        if item in free_variables:
            org_count -= 1
            unit_lst.append(item)
    #assert org_count==1, "You need to ensure the expression is a data_with_unit one."
    free_variable_lst = list(free_variables - set(unit_lst))
    return free_variable_lst,unit_lst
    
# import Eq

def show_details(var,name):
    print("============================")
    print("Name:", name)
    print("Type:", type(var))
    print("Value:", var)
    print("============================")

def same_rel_metric(div,org_rel_diff,left_minus_right, **kwargs):
    if "epsilon_for_equal" in kwargs:
        epsilon_for_equal = kwargs["epsilon_for_equal"]
    else:
        epsilon_for_equal = EPSILON_FOR_EQUAL
    
    if "epsilon_for_equal_for_randomlySample" in kwargs:
        assert False, 'this is deprecated and should be parsed in with `epsilon_for_equal`'
        epsilon_for_equal_for_randomlySample = kwargs["epsilon_for_equal_for_randomlySample"]
    else:
        epsilon_for_equal_for_randomlySample = RELA_EPSILON_FOR_ALMOST_CONSTANT_EVAL
    epsilon_for_equal_for_randomlySample = epsilon_for_equal
    # if if_print:
    # print(epsilon_for_equal_for_randomlySample, 'aw;oefiaweoi')
    def my_measure(expr):
        POW = Symbol('POW')
        # Discourage powers by giving POW a weight of 10
        count = count_ops(expr, visual=True).subs(POW, 10)
        # Every other operation gets a weight of 1 (the default)
        count = count.replace(Symbol, type(S.One))
        return count
    # div = simplify(div, measure=my_measure)
    # # print(div)
    # div_count = count_ops(div, visual=False)
    # org_count = count_ops(org_rel_diff)
    return is_almost_equivalent(org_rel_diff, left_minus_right, tol=epsilon_for_equal_for_randomlySample,
                if_print=ONLY_PRINT_WHEN_CALLED_FOR_DEBUG,)
    # if whether_data_with_unit(org_rel_diff,units_expression) and 0:
    #     #So the original equation is like : M_A = 1\kg
    #     if whether_data_with_unit(div,units_expression):
    #         free_var_lst, unit_var_lst = get_unit_and_free_variable(div,units_expression=units_expression)
    #         assert len(free_var_lst) == 1, "In the data with unit case there should be exactly one free variable."
    #         free_var = free_var_lst[0]
    #         #first, set the units to be 1, and the actual free variable to be 0.

    #         dct={unit_var: units_expression_weight[unit_var] for unit_var in unit_var_lst}
    #         left_minus_right.subs(dct)
    #         sol1 = solve(left_minus_right,free_var)
    #         org_rel_diff.subs(dct)
    #         sol2 = solve(org_rel_diff,free_var)
    #         if sol1 and sol2:
    #             div = sol1[0]/sol2[0]
    #             if abs(div-1) <= epsilon_for_equal:
    #                 return True,"Almost_Same_Value_Differing less than {}".format(epsilon_for_equal)
    #             else:
    #                 return False, "Different Value differing by more than {}".format(epsilon_for_equal)
    #         elif sol2 and (not sol1):
    #             return False, "Different Value"
    #         else:
    #             assert False, "Cannot solve for free variable."
    #     else:
    #         return False, "The answer is a constant, but the student's answer is not."
    # else:
    #     return is_almost_equivalent(org_rel_diff, left_minus_right, tol=epsilon_for_equal_for_randomlySample, if_print=False)
        
    #     # deprecated
    #     if is_almost_constant(div, div.free_symbols, tol=epsilon_for_equal_for_randomlySample, if_print=False):
    #         return True, f"(eq1lhs-eq1rhs)/(eq2lhs-eq2rhs) is {div}, which is almost constant"
    #     else:
    #         pass
            # we have already substitude all constants and units in comparing_rel, so no need to check again!
            # print(org_rel_diff, 'awaefjaoweife')
            # print(left_minus_right, 'bawoefijaweiof')
            # return is_almost_equivalent(org_rel_diff, left_minus_right, tol=epsilon_for_equal_for_randomlySample, if_print=True)
            #     return True, f"(eq1lhs-eq1rhs) is {org_rel_diff}, (eq2lhs-eq2rhs) is {left_minus_right}, which are almost equivalent"
            # else:
            #     return False, f"(eq1lhs-eq1rhs)/(eq2lhs-eq2rhs) is {div}, which is NOT considered constant"
        # else:
        #     return False, f"(eq1lhs-eq1rhs)/(eq2lhs-eq2rhs) is {div}, which is NOT considered constant"
        
        
        
        # #So the original equation is like: E=B*c^2. If the student is answering B=E/c^2, they should be correct.
        # if div_count < max([tolerable_diff_max,tolerable_diff_fraction*org_count]):
        #     return True, "Almost same Equation? Not very sure."
        # else:
        #     return False, f"Not same Equation, differ by {div_count} vs {org_count} operations."
    
    
    
    
def my_measure(expr):
    DIV = Symbol('DIV')
    # Discourage powers by giving DIV a weight of 10
    count = count_ops(expr, visual=True).subs(DIV, 10)
    # Every other operation gets a weight of 1 (the default)
    count = count.replace(Symbol, type(S.One))
    return count


def comparing_eqs(eq1,eq2, **kwargs):
    expr1 = simplify(eq1.lhs - eq1.rhs)
    expr2 = simplify(eq2.lhs - eq2.rhs)
    if expr1 == 0 and expr2 != 0:
        return False, "The first equation is an identity, but the second is not."
    elif expr2 == 0 and expr1 != 0:
        return False, "The second equation is an identity, but the first is not."
    
    eq3 = expr1/expr2
    # print(eq3)
    # w = Symbol("w")
    # sol = solve(eq3-w,w)
    sol=[None]
    
    if len(sol) >= 1:
        return same_rel_metric(sol[0],expr2,expr1, **kwargs)
        # if sol[0].is_constant():
        #     return True, "Same_Equality"
        
        # else:
        #     return same_rel_metric(sol[0],expr2,expr1, **kwargs)
            # print(sol, 'aweuifhawope9ifawe')
            #return False, "Different_Equality"
    else:
        return False, "Different_Equation"

def comparing_geq_or_leq(rel1_lhs,rel1_rhs,rel2_lhs,rel2_rhs, **kwargs):
    geq3 = (rel1_lhs - rel1_rhs)/(rel2_lhs - rel2_rhs)
    w = Symbol("w")
    sol = solve(geq3-w, w)
    if len(sol) >= 1:
        if sol[0].is_constant():
            if sol[0] > 0:
                return True, "Same_Inequality"
            else:
                return False, "False_Direction_Of_Inequality"
        else:
            return same_rel_metric(sol[0],simplify(rel2_lhs-rel2_rhs),simplify(rel1_lhs-rel1_rhs),**kwargs)
            #return False, "Wrong_Inequality"
    else:
        return False, "Wrong_Equation"
    
def is_numeric(some_expr):
    try:
        numeric_value = float(some_expr)
        return True
    except Exception:
        return False
    assert False, "This line should not be called, as it is not implemented yet. Please implement it if you need to use it."

def comparing_rel(rel1, rel2, strict_comparing_inequalities = False,  **kwargs):
    if rel1 == None or rel2 == None:
        return False, "None_Equation"
    if "constants_expression" in kwargs.keys():
        units_expression = kwargs["constants_expression"].keys()
    else:
        units_expression = UNITS_EXPRESSION.keys()
    if "constants_expression" in kwargs.keys():
        units_expression_weight = kwargs["constants_expression"]
    else:
        units_expression_weight = UNITS_EXPRESSION
    if not len(rel2.free_symbols - set(units_expression)) >= 1:
        return False, "The answer is composed of constants."
    if "direct_string_replace" in kwargs:
        direct_string_replace = kwargs["direct_string_replace"]
    else:
        direct_string_replace = {}
    if direct_string_replace:
        # convert eq to latex.
        rel1_latex = latex(rel1)
        rel2_latex = latex(rel2)
        for k, v in direct_string_replace.items():
            rel1_latex = rel1_latex.replace(k, v)
            rel2_latex = rel2_latex.replace(k, v)
        print(rel1_latex, rel2_latex, 'before direct string replace')
        rel1 = parse_latex(rel1_latex)
        rel2 = parse_latex(rel2_latex)
        print(rel1, rel2, 'after direct string replace')
    if "num_constant_change_iter" in kwargs:
        num_constant_change_iter = kwargs["num_constant_change_iter"]
    else:
        num_constant_change_iter = 1

    for _ in range(num_constant_change_iter):
        _, unit_var_lst_1 = get_unit_and_free_variable(rel1,units_expression=units_expression)
        dct_1={unit_var: units_expression_weight[unit_var] for unit_var in unit_var_lst_1}
        
        _,unit_var_lst_2 = get_unit_and_free_variable(rel2,units_expression=units_expression)
        dct_2 = {unit_var: units_expression_weight[unit_var] for unit_var in unit_var_lst_2}
        
        # print(rel1, rel2, dct_1, dct_2, 'bqwpeiufhqwfiouawef')
        
        dct_1_numeric = {k: v for k, v in dct_1.items() if not is_numeric(v)}
        dct_2_numeric = {k: v for k, v in dct_2.items() if not is_numeric(v)}
        dct_1_str = {k: v for k, v in dct_1.items() if is_numeric(v)}
        dct_2_str = {k: v for k, v in dct_2.items() if is_numeric(v)}
        
        if len(dct_1_str) > 0 or len(dct_2_str) > 0:
            if len(dct_1_str) > 0:
                dct_1_sympy = {k: sp.sympify(v) for k, v in dct_1_str.items()}
            if len(dct_2_str) > 0:
                dct_2_sympy = {k: sp.sympify(v) for k, v in dct_2_str.items()}
            rel1 = rel1.subs(dct_1_sympy)
            rel2 = rel2.subs(dct_2_sympy)
            # check again for unit expressions. For example, if we substitde "kg=1000*g", while "g=114514", we have to substitute "g" again.
            _, unit_var_lst_1 = get_unit_and_free_variable(rel1,units_expression=units_expression)
            _, unit_var_lst_2 = get_unit_and_free_variable(rel2,units_expression=units_expression)
            dct_1 = {unit_var: units_expression_weight[unit_var] for unit_var in unit_var_lst_1}
            dct_2 = {unit_var: units_expression_weight[unit_var] for unit_var in unit_var_lst_2}
            dct_1_numeric = {k: v for k, v in dct_1.items() if not is_numeric(v)}
            dct_2_numeric = {k: v for k, v in dct_2.items() if not is_numeric(v)}

        if len(dct_1_numeric) > 0:
            rel1 = rel1.subs(dct_1_numeric)
        if len(dct_2_numeric) > 0:
            rel2 = rel2.subs(dct_2_numeric)
        
    if (rel1.free_symbols) != (rel2.free_symbols):
        return False, f"Different_Free_Variables: {rel1.free_symbols} vs {rel2.free_symbols}; {rel1}, {rel2}. ====={units_expression}"
    
        
    
    # # plug in dct_1_str and dct_2_str to rel1 and rel2.
    # if 
    
    # print(dct_1, 'awefiawjeo;fijawef')
    # print(dct_2, 'bweo;ifawoleiawfe')
    # print(units_expression, 'cawpeofijawpeioe')
    # print(units_expression_weight, 'dawiefjawoleif')
    # print(rel1, rel2, 'eljkfghls')
    
    if type(rel1) == Equality:
        if type(rel2) == Equality:
            return comparing_eqs(rel1, rel2,  **kwargs)
        else:
            return False, "Different_Relation_Type"
    elif type(rel1) == StrictLessThan:
        if type(rel2) == StrictLessThan:
            return comparing_geq_or_leq(rel1.lhs, rel1.rhs, rel2.lhs, rel2.rhs, **kwargs)
        elif type(rel2) == StrictGreaterThan:
            return comparing_geq_or_leq(rel1.rhs, rel1.lhs,rel2.lhs, rel2.rhs, **kwargs)
        elif type(rel2) == LessThan:
            if strict_comparing_inequalities:
                return False, "Different_Relation_Type"
            else:
                return comparing_geq_or_leq(rel1.lhs, rel1.rhs, rel2.lhs, rel2.rhs, **kwargs)
        elif type(rel2) == GreaterThan:
            if strict_comparing_inequalities:
                return False, "Different_Relation_Type"
            else:
                return comparing_geq_or_leq(rel1.rhs, rel1.lhs,rel2.lhs, rel2.rhs, **kwargs)
        else:
            return False, "Different_Relation_Type"
    elif type(rel1) == LessThan:
        if type(rel2) == LessThan:
            return comparing_geq_or_leq(rel1.lhs, rel1.rhs, rel2.lhs, rel2.rhs, **kwargs)
        elif type(rel2) == GreaterThan:
            return comparing_geq_or_leq(rel1.rhs, rel1.lhs, rel2.lhs, rel2.rhs, **kwargs)
        elif type(rel2) == StrictLessThan:
            if strict_comparing_inequalities:
                return False, "Different_Relation_Type"
            else:
                return comparing_geq_or_leq(rel1.lhs, rel1.rhs, rel2.lhs, rel2.rhs, **kwargs)
        elif type(rel2) == StrictGreaterThan:
            if strict_comparing_inequalities:
                return False, "Different_Relation_Type"
    elif type(rel1) == StrictGreaterThan:
        if type(rel2) == StrictGreaterThan:
            return comparing_geq_or_leq(rel1.lhs, rel1.rhs, rel2.lhs, rel2.rhs, **kwargs)
        elif type(rel2) == StrictLessThan:
            return comparing_geq_or_leq(rel1.rhs, rel1.lhs,rel2.lhs, rel2.rhs, **kwargs)
        elif type(rel2) == GreaterThan:
            if strict_comparing_inequalities:
                return False, "Different_Relation_Type"
            else:
                return comparing_geq_or_leq(rel1.lhs, rel1.rhs, rel2.lhs, rel2.rhs, **kwargs)
        elif type(rel2) == LessThan:
            if strict_comparing_inequalities:
                return False, "Different_Relation_Type"
            else:
                return comparing_geq_or_leq(rel1.rhs, rel1.lhs,rel2.lhs, rel2.rhs, **kwargs)
    elif type(rel1) == GreaterThan:
        if type(rel2) == GreaterThan:
            return comparing_geq_or_leq(rel1.lhs, rel1.rhs, rel2.lhs, rel2.rhs, **kwargs)
        elif type(rel2) == LessThan:
            return comparing_geq_or_leq(rel1.rhs, rel1.lhs, rel2.lhs, rel2.rhs, **kwargs)
        elif type(rel2) == StrictGreaterThan:
            if strict_comparing_inequalities:
                return False, "Different_Relation_Type"
            else:
                return comparing_geq_or_leq(rel1.lhs, rel1.rhs, rel2.lhs, rel2.rhs, **kwargs)
        elif type(rel2) == StrictLessThan:
            if strict_comparing_inequalities:
                return False, "Different_Relation_Type"
            else:
                return comparing_geq_or_leq(rel1.lhs,rel1.rhs,rel2.rhs,rel2.lhs, **kwargs)
    

def whether_rel_latex_correct(rel_latex,answer_latex,
                               constants_latex_expression=None,
                               strict_comparing_inequalities=False,
                               epsilon_for_equal=1e-5,
                               tolerable_diff_fraction = TOLERABLE_DIFF_FRACTION,
                               tolerable_diff_max = TOLERABLE_DIFF_MAX,
                               **kwargs):
    rel_latex = simplify_latex_expr(rel_latex)
    answer_latex = simplify_latex_expr(answer_latex)
    rel = parse_latex(rel_latex)
    answer = parse_latex(answer_latex)
    constants_expression = dict()
    if constants_latex_expression is not None:
        for x, val in constants_latex_expression.items():
            new_key = parse_latex(x)
            if isinstance(val, str):
                new_val = parse_latex(val)
            elif  isinstance(val, int) or isinstance(val, float):
                new_val = val
            else:
                # print(x,val,'aweofijapwo;eif')
                new_val = val
            constants_expression[new_key] = new_val
    else:
        constants_expression = dict()
    # print(constants_expression,'aweofiajweoifajwe')
    # constants_expression = {parse_latex(x):constants_latex_expression[x] for x in constants_latex_expression}
    return comparing_rel(rel,answer,strict_comparing_inequalities=strict_comparing_inequalities, epsilon_for_equal=epsilon_for_equal,tolerable_diff_fraction = tolerable_diff_fraction,tolerable_diff_max = tolerable_diff_max,constants_expression = constants_expression,
                         **kwargs)

import re

def format_units_latex(unit_expression):
    # """
    # Formats a unit expression by prepending '\' to multi-character units.
    
    # Args:
    #     unit_expression (str): Input unit string (e.g., "km*kg/s^2").
    
    # Returns:
    #     str: Formatted LaTeX-like units (e.g., "\km*\kg/\s^2").
    # """
    # Split into parts (units and operators)
    parts = re.split(r'([*/^])', unit_expression)
    
    processed_parts = []
    for part in parts:
        if part in {'*', '/', '^'}:  # Keep operators unchanged
            processed_parts.append(part)
        else:
            # Split into sub-units and exponents (e.g., "s^2" -> ["s", "^2"])
            sub_parts = re.split(r'(\^[0-9]+)', part)
            for sub in sub_parts:
                if sub.startswith('^'):  # Exponents (e.g., "^2")
                    processed_parts.append(sub)
                elif sub:  # Actual unit (e.g., "km", "s")
                    processed_parts.append(f'\\{sub}' if len(sub) > 1 else sub)
    
    return ''.join(processed_parts)
def whether_rel_latex_correct_with_units(rel_latex,answer_latex,
                                         constants_latex_expression=None,
                                         strict_comparing_inequalities=False,
                                         epsilon_for_equal=1e-5,
                                         tolerable_diff_fraction = TOLERABLE_DIFF_FRACTION,
                                         tolerable_diff_max = TOLERABLE_DIFF_MAX,
                                         unit_pattern = r"\\unit{(.*?)}",
                                         whole_unit_pattern = r"(\\unit{.*?})",
                                         units_conversion_dict = {
                                             "\\km": "1000*m",
                                             "\\ms": "0.001*s",
                                             "g": "0.001*\\kg",
                                             "\\Hz": "1/s",
                                         },
                                         unit_notation = [r"\U_{relstrunitnotation}", r"\U_{ansstrunitnotation}"],
                                         **kwargs):
    # get unit pattern in rel_latex.
    p = re.compile(unit_pattern)
    units_in_rel = p.findall(rel_latex)
    units_in_answer = p.findall(answer_latex)
    if len(units_in_rel) == len(units_in_answer) and len(units_in_rel) == 0:
        return whether_rel_latex_correct(rel_latex, answer_latex,
                                         constants_latex_expression=constants_latex_expression,
                                         strict_comparing_inequalities=strict_comparing_inequalities,
                                         epsilon_for_equal=epsilon_for_equal,
                                         tolerable_diff_fraction=tolerable_diff_fraction,
                                         tolerable_diff_max=tolerable_diff_max,
                                         **kwargs)
    elif len(units_in_rel) == len(units_in_answer) and len(units_in_rel) == 1:
        units_in_rel = units_in_rel[0]
        units_in_answer = units_in_answer[0]
        # replace the \\unit{(.*?)} in rel_latex as r"\unitsInRelLatex", and in answer_latex as r"\unitsInAnswerLatex"
        # units_in_rel is like 'm/s^2', but I want rel_latex_matched to be like "\units{m/s^2}", to replace what's in the original str.
        p_whole = re.compile(whole_unit_pattern)
        rel_latex_matched = p_whole.findall(rel_latex)[0]
        rel_latex = rel_latex.replace(rel_latex_matched, unit_notation[0])
        answer_latex_matched = p_whole.findall(answer_latex)[0]
        answer_latex = answer_latex.replace(answer_latex_matched, unit_notation[1])
        constants_latex_expression = constants_latex_expression or dict()
        # units_in_rel is like: "km/s^2"
        # convert it into an expression of sympy, e.g. "1000*m/s^2".
        units_in_rel = format_units_latex(units_in_rel)
        units_in_answer = format_units_latex(units_in_answer)
        units_in_rel_sp = parse_latex(units_in_rel)
        units_in_answer_sp = parse_latex(units_in_answer)
        # check if keys in units_conversion_dict are in units_in_rel_sp and units_in_answer_sp.
        for key in units_conversion_dict:
            if key in units_in_rel_sp.free_symbols:
                units_in_rel_sp = units_in_rel_sp.subs(key, parse_latex(units_conversion_dict[key]))
            if key in units_in_answer_sp.free_symbols:
                units_in_answer_sp = units_in_answer_sp.subs(key, parse_latex(units_conversion_dict[key]))
        # now units_in_rel_sp and units_in_answer_sp are sympy expressions.
        constants_latex_expression[unit_notation[0]] = units_in_rel_sp
        constants_latex_expression[unit_notation[1]] = units_in_answer_sp
        for k,v in units_conversion_dict.items():
            if k not in constants_latex_expression:
                constants_latex_expression[k] = v
        # now we can call whether_rel_latex_correct.
        # print(rel_latex, answer_latex, constants_latex_expression, 'awelifaweliwe')
        return whether_rel_latex_correct(rel_latex, answer_latex,
                                            constants_latex_expression=constants_latex_expression,
                                            strict_comparing_inequalities=strict_comparing_inequalities,
                                            epsilon_for_equal=epsilon_for_equal,
                                            tolerable_diff_fraction=tolerable_diff_fraction,
                                            tolerable_diff_max=tolerable_diff_max,
                                            num_constant_change_iter = 2,
                                            **kwargs)
    else:
        return False, "The number of units in rel_latex and answer_latex should be the same, and should be 0 or 1."
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
def whether_rel_latex_correct_with_only_one_dict_parameter(dct):
    '''
    The keys in dct should be:
        rel_latex
        answer_latex
        constants_latex_expression
        strict_comparing_inequalities
        epsilon_for_equal
        tolerable_diff_fraction
        tolerable_diff_max
    '''
    assert "rel_latex" in dct and "answer_latex" in dct, "rel_latex and answer_latex must be in dct"
    return whether_rel_latex_correct(**dct)

def whether_rel_latex_correct_with_units_with_only_one_dict_parameter(dct):
    '''
    The keys in dct should be:
        rel_latex
        answer_latex
        constants_latex_expression
        strict_comparing_inequalities
        epsilon_for_equal
        tolerable_diff_fraction
        tolerable_diff_max
    '''
    assert "rel_latex" in dct and "answer_latex" in dct, "rel_latex and answer_latex must be in dct"
    return whether_rel_latex_correct_with_units(**dct)


# for _ in tqdm(range(Number_Of_Missions)):
#     whether_rel_latex_correct("E=M c^2","M=E/(3*10^8 m/s^2)^2",constants_latex_expression={'c':float(300000000*7)/(float(11)**2), 'm':7, 's':11,'M':1997})

if (__name__=="__main__"):
    import time
    from tqdm import tqdm
    from multiprocessing import Pool
    Number_Of_Missions = 1
    units_latex['c'] = '30 m / s'
    # # param_list = [{"rel_latex":"E>M c^2","answer_latex":"M<E/(c)^2","constants_latex_expression":{'c':float(300000000*7)/(float(11)**2), 'm':7, 's':11,'M':1997}}]*Number_Of_Missions
    # param_list = [{"rel_latex":"E = \\sqrt{(m_{min} + \\mu_b)} * c^2 + mhg","answer_latex":"(E-mhg) / c^2 = ( m_{min} + \\mu_b )^0.5","constants_latex_expression":dict(m=3)}, ] * Number_Of_Missions
    #             #   {"rel_latex":"E / c^2 = ( - m_{a2} + \\mu_b )^0.5","answer_latex":"E = (-m_{a2} + \\mu_b)^0.5 c^2","constants_latex_expression":{'c': float(300000000)}}]
    # # param_list = [{"rel_latex":"E = m","answer_latex":"0.1E - m/10 = 0","constants_latex_expression":dict(m=3)}, ] * Number_Of_Missions
    
    Number_Of_Missions = 4
    param_list = [
        {
            "rel_latex": r"x = \frac{m}{b} \ln ( 1 + \frac{b V_0 t}{m} )",
            "answer_latex": r"\frac{b}{m}x = \ln(1 + \frac{bV_0}{m}t)",
            "constants_latex_expression": {"\\kg": "1000*g","e": np.e},
            # kg = 1000 g
            # e = 2.718281828459045
            # u = 1/r
        },
    ] * Number_Of_Missions
    # param_list = [
    #     {
    #         "rel_latex": r"x = 1",
    #         "answer_latex": r"x=1+1-1",
    #         "constants_latex_expression": {"\\kg": "1000*g","e": np.e},
    #         # kg = 1000 g
    #         # e = 2.718281828459045
    #         # u = 1/r
    #     },
    # ] * 10
    
    
    # param_list = [{"rel_latex":"P_{1}=\\frac{U^{2}} {R_{0}} \\sin( w t )^{2} \\unit{m/s^2}","answer_latex":"P_{1}(t)=\\frac{U^{2}} {R_{0}} \\sin^{2}( w t ) \\unit{0.001*km/s^2}",
    #                "constants_latex_expression":{"\\P_{1}(t)": "P_{1}"}, "direct_string_replace": {"P_{1}{\\left(t \\right)}": "P_{1}"}} ] * Number_Of_Missions
                                        # constant number  # univ const    # unit
    # param_list = [{"rel_latex":"m_a = - m_b + \\kg / (3000000000m/s)^2","answer_latex":"m_a = - m_b + \\kg / (300000000m/s)^2",
    #                "constants_latex_expression":{"e": np.e, "t": "1*s", "s": "s"}}, ] * Number_Of_Missions
                                        
    start = time.time()
    for param in tqdm(param_list[:1], desc='testing'):
        # print(param)
        # print(whether_rel_latex_correct(**param))
        print(whether_rel_latex_correct_with_units_with_only_one_dict_parameter(param))
    # print(whether_rel_latex_correct_with_only_one_dict_parameter(param_list))
    end = time.time()
    print("Time for one mission: ", end-start)
    
    N_Thread = 4
    start = time.time()
    with Pool(N_Thread) as p:
        r = list(tqdm(p.map(whether_rel_latex_correct_with_only_one_dict_parameter, param_list), total=len(param_list), desc='testing'))
    end = time.time()
    print("Time for N_Thread = {0} and N_mission = {1}: ".format(N_Thread, Number_Of_Missions), end-start)
    # # save r into json file.
    # import json
    # # use 4 as tab indent.
    # with open("result.json", "w") as f:
    #     json.dump(r, f, indent=4)
    # print(r)
