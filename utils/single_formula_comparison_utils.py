from sympy import *
from sympy.parsing.latex import parse_latex
units_latex={r'\kg':3,r'\s':7,r'\m':11,r'\A':13,r'\K':17,r'\g':0.003}
UNITS_EXPRESSION = {parse_latex(x):units_latex[x] for x in units_latex}
EPSILON_FOR_EQUAL = 1e-2
TOLERABLE_DIFF_MAX = 5
TOLERABLE_DIFF_FRACTION = 0.6






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
    if "tolerable_diff_max" in kwargs:
        tolerable_diff_max = kwargs["tolerable_diff_max"]
    else:
        tolerable_diff_max = TOLERABLE_DIFF_MAX
    if "tolerable_diff_fraction" in kwargs:
        tolerable_diff_fraction = kwargs["tolerable_diff_fraction"]
    else:
        tolerable_diff_fraction = TOLERABLE_DIFF_FRACTION
    if "constants_expression" in kwargs.keys():
        units_expression = kwargs["constants_expression"].keys()
    else:
        units_expression = UNITS_EXPRESSION.keys()
    if "constants_expression" in kwargs.keys():
        units_expression_weight = kwargs["constants_expression"]
    else:
        units_expression_weight = UNITS_EXPRESSION

    def my_measure(expr):
        POW = Symbol('POW')
        # Discourage powers by giving POW a weight of 10
        count = count_ops(expr, visual=True).subs(POW, 10)
        # Every other operation gets a weight of 1 (the default)
        count = count.replace(Symbol, type(S.One))
        return count
    div = simplify(div, measure=my_measure)
    div_count = count_ops(div, visual=False)
    org_count = count_ops(org_rel_diff)
    if whether_data_with_unit(org_rel_diff,units_expression):
        #So the original equation is like : M_A = 1\kg
        if whether_data_with_unit(div,units_expression):
            free_var_lst, unit_var_lst = get_unit_and_free_variable(div,units_expression=units_expression)
            assert len(free_var_lst) == 1, "In the data with unit case there should be exactly one free variable."
            free_var = free_var_lst[0]
            #first, set the units to be 1, and the actual free variable to be 0.

            dct={unit_var: units_expression_weight[unit_var] for unit_var in unit_var_lst}
            left_minus_right.subs(dct)
            sol1 = solve(left_minus_right,free_var)
            org_rel_diff.subs(dct)
            sol2 = solve(org_rel_diff,free_var)
            if sol1 and sol2:
                div = sol1[0]/sol2[0]
                if abs(div-1) <= epsilon_for_equal:
                    return True,"Almost_Same_Value_Differing less than {}".format(epsilon_for_equal)
                else:
                    return False, "Different Value differing by more than {}".format(epsilon_for_equal)
            elif sol2 and (not sol1):
                return False, "Different Value"
            else:
                assert False, "Cannot solve for free variable."
        else:
            return False, "The answer is a constant, but the student's answer is not."
    else:
        #So the original equation is like: E=B*c^2. If the student is answering B=E/c^2, they should be correct.
        if div_count < max([tolerable_diff_max,tolerable_diff_fraction*org_count]):
            return True, "Almost same Equation? Not very sure."
        else:
            return False, "Not same Equation"
    
    
    
    
def my_measure(expr):
    DIV = Symbol('DIV')
    # Discourage powers by giving DIV a weight of 10
    count = count_ops(expr, visual=True).subs(DIV, 10)
    # Every other operation gets a weight of 1 (the default)
    count = count.replace(Symbol, type(S.One))
    return count


def comparing_eqs(eq1,eq2, **kwargs):
    eq3 = (eq1.lhs - eq1.rhs)/(eq2.lhs - eq2.rhs)
    w = Symbol("w")
    sol = solve(eq3-w,w)
    #print(sol)
    if len(sol) >= 1:
        if sol[0].is_constant():
            return True, "Same_Equality"
        else:
            return same_rel_metric(sol[0],simplify(eq2.lhs-eq2.rhs),eq1.lhs-eq1.rhs, **kwargs)
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
            return same_rel_metric(sol[0],simplify(rel2_lhs-rel2_rhs),rel1_lhs-rel1_rhs,**kwargs)
            #return False, "Wrong_Inequality"
    else:
        return False, "Wrong_Equation"

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

    if (rel1.free_symbols-set(units_expression)) != (rel2.free_symbols-set(units_expression)):
        return False, "Different_Free_Variables"
    
    _, unit_var_lst_1 = get_unit_and_free_variable(rel1,units_expression=units_expression)
    dct_1={unit_var: units_expression_weight[unit_var] for unit_var in unit_var_lst_1}
    
    _,unit_var_lst_2 = get_unit_and_free_variable(rel2,units_expression=units_expression)
    dct_2 = {unit_var: units_expression_weight[unit_var] for unit_var in unit_var_lst_2}
    
    rel1 = rel1.subs(dct_1)
    rel2 = rel2.subs(dct_2)
    
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
                               constants_latex_expression={r'\kg':3,r'\s':7,r'\m':11,r'\A':13,r'\K':17,r'\g':0.003},
                               strict_comparing_inequalities=False,
                               epsilon_for_equal=1e-2,
                               tolerable_diff_fraction = TOLERABLE_DIFF_FRACTION,
                               tolerable_diff_max = TOLERABLE_DIFF_MAX,):
    rel = parse_latex(rel_latex)
    answer = parse_latex(answer_latex)
    constants_expression = {parse_latex(x):constants_latex_expression[x] for x in constants_latex_expression}
    return comparing_rel(rel,answer,strict_comparing_inequalities=strict_comparing_inequalities, epsilon_for_equal=epsilon_for_equal,tolerable_diff_fraction = tolerable_diff_fraction,tolerable_diff_max = tolerable_diff_max,constants_expression = constants_expression)
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




# for _ in tqdm(range(Number_Of_Missions)):
#     whether_rel_latex_correct("E=M c^2","M=E/(3*10^8 m/s^2)^2",constants_latex_expression={'c':float(300000000*7)/(float(11)**2), 'm':7, 's':11,'M':1997})

if (__name__=="__main__"):
    import time
    from tqdm import tqdm
    from multiprocessing import Pool
    Number_Of_Missions = 400
    param_list = [{"rel_latex":"E>M c^2","answer_latex":"M<E/(3.1*10^8 m/s^2)^2","constants_latex_expression":{'c':float(300000000*7)/(float(11)**2), 'm':7, 's':11,'M':1997}}]*Number_Of_Missions
    print(whether_rel_latex_correct_with_only_one_dict_parameter(param_list[0]))
    
    N_Thread = 8
    start = time.time()
    with Pool(N_Thread) as p:
        r = list(tqdm(p.map(whether_rel_latex_correct_with_only_one_dict_parameter, param_list), total=len(param_list), desc='testing'))
    end = time.time()
    print("Time for N_Thread = {}: ".format(N_Thread), end-start)
    print(r)
