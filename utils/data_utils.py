import re



FUNCTION_FOR_ADDING_TIMES_BEFORE_NON_FUNCTIONAL_BRACKETS = True # must be true, just use a if so you can fold it.
if FUNCTION_FOR_ADDING_TIMES_BEFORE_NON_FUNCTIONAL_BRACKETS:
    import regex                            # pip install regex

    EXCLUDED = {'frac', 'sqrt', 'times', 'cdot'}

    # ------------------------------------------------------------
    # 1  Pattern – no more “++” inside the char class
    # ------------------------------------------------------------
    PATTERN = regex.compile(
        r'''
        (\\?[a-zA-Z]\w*)\s*        # 1 – variable or \command
        \(                         #    opening (
            (                      # 2 – balanced contents
                (?:
                    [^()]          #    any non‑paren char  ← now back‑trackable
                | (?R)           #    or another balanced (…)  (recursion)
                )*
            )
        \)                         #    closing )
        ''',
        regex.VERBOSE,
    )

    # ------------------------------------------------------------
    # 2  Helpers
    # ------------------------------------------------------------
    def is_valid_var(v: str) -> bool:
        return v.lstrip('\\') not in EXCLUDED


    def repl(m: regex.Match) -> str:
        var, inner = m.group(1), m.group(2)

        # If the "variable" is actually an excluded command (e.g. \frac),
        # just keep searching inside its parentheses.
        if not is_valid_var(var):
            return f"{var}({regex.sub(PATTERN, repl, inner)})"

        # Only insert × if arithmetic symbols are present inside ( … )
        if regex.search(r'[\+\-\*/]|\\frac|\\cdot|\\times', inner):
            return f"{var} \\times ({inner})"

        return m.group(0)           # leave untouched


    def add_explicit_times(expr: str) -> str:
        """Keep applying the substitution until nothing changes."""
        prev = None
        counter = 0
        while expr != prev:
            counter += 1
            prev = expr
            expr = regex.sub(PATTERN, repl, expr)
            if counter > 100:
                break
        return expr

    add_times_before_NonFunctionalbrackets = add_explicit_times

    if __name__ == "__main__":
        # 测试不同的表达式
        test_exprs = [
            r'a(b+c)',         # 普通变量后跟括号 - 应该匹配
            r'\alpha(x+y)',    # LaTeX符号后跟括号 - 应该匹配
            r'\frac(a+b)',     # \frac后跟括号 - 不应该匹配
            r'\sqrt(x+y)',     # \sqrt后跟括号 - 不应该匹配
            r'm(n)',           # 普通变量后跟括号但内部没有计算符号 - 不应该匹配
            r'\frac(a+b) (c+d)', # 复杂表达式 - 第二部分应该匹配，第一部分不应该
            r'E_1 = \frac{1}{2}m \left(\frac{e^2}{4\pi\varepsilon_0 m r_0}\right) - \frac{e^2}{4\pi\varepsilon_0 r_0}',
            r'E_2 = \frac{1}{2}m \left(\frac{2e^2}{4\pi\varepsilon_0 m r_0}\right) - \frac{2e^2}{4\pi\varepsilon_0 r_0}',
            r'r_{min} = a(1 - e)',
            r'r_{max} = a(1 + e)',
            r'\Delta E = \frac{1}{2}\left(v_J^2 + v_{\text{rel}}^2\right) - \frac{1}{2}v_i^2',
            r'\Delta E = \frac{1}{2}\left(v_J^2 + v_i^2 + v_J^2\right) - \frac{1}{2}v_i^2',
            r'\frac{G m_e m_m}{a^2} = \left( \frac{m_e m_m}{m_e + m_m} \right)a \omega^2',
            r'G(m_e + m_m) = \frac{4\pi^2 a^3}{T^2}',
            r'a = a_1 - \frac{R_e (\sin \alpha_2 - \sin \alpha_1)}{\alpha_2 - \alpha_1 - \lambda_2 + \lambda_1}',
            r'\frac{G m_e m_m}{a^2} = ( \frac{m_e m_m}{m_e + m_m} )a \omega^2',
            r'G \cdot (m_e + m_m) = \frac{4\pi^2 a^3}{T^2}',
            r'a = a_1 - \frac{R_e \cdot (\sin \alpha_2 - \sin \alpha_1)}{\alpha_2 - \alpha_1 - \lambda_2 + \lambda_1}',
            r'F = m_m \left(\frac{2\pi}{T}\right)^2 a',
            r'G \frac{m_e m_m}{a^2} = m_m \left(\frac{2\pi}{T}\right)^2 a',
            r'a = \frac{a_1 R_e (\sin \alpha_2 \cos \lambda_1 - \sin \alpha_1 \cos \lambda_2)}{\sin \alpha_1 \sin \alpha_2 (\cos \lambda_1 - \cos \lambda_2)}',
            r'r = \frac{mv^2}{q(k_e + vB)}',
            r'$$F = m ( \ddot{r} - r \dot{\theta}^2 )$$',
            r'$$V(r) = - \int_{\infty}^{r} F(r) dr$$',
            r'$$V(r) = \int_{\infty}^r \frac{m h^2}{r^3} dr$$',
            r'$$V(r) = \left[ -\frac{m h^2}{2 r^2} \right]_{\infty}^{r}$$',
            r'$$V(r) = -\frac{m h^2}{2 r^2}$$',
            r'F = m \cdot ( \ddot_{r} - r \dot{\theta}^2 )',
            r'0 = m \cdot ( r \ddot_{\theta} + 2 \dot{r} \dot{\theta} )',
            r'\frac{G(a+b)}{c+d}'
            r'$$0 = m ( r \ddot{\theta} + 2 G(a(b+c(d)))m(\frac{q}{b})\dot{r} \dot{\theta} )$$',
        ]

        for expr in test_exprs:
            print(f"\n测试: {expr}")
            result = add_explicit_times(expr)
            # result = re.sub(pattern, repl, expr)
            # result = re.sub(pattern, repl, result)
            print(f"结果: {result}")

def filter_and_convert(problem: dict):
    """
    Remove subquestions whose solutions do not contain $$ equations
    Also filter out invalid problems
    """
    #check the required fields
    if "id" not in problem:
        return None
    
    if "context" not in problem:
        print(f"Problem {problem['id']} is missing context.")
        return None
    
    if "subquestions" not in problem:
        if problem.get("solution"):
            problem["subquestions"] = [{
                "letter": "a",
                "subproblem": problem["context"],
                "solution": problem["solution"]
            }]
            problem["context"] = "Read the following problem and provide your answer."
        else:
            print(f"Problem {problem['id']} is missing subquestions or solution.")
            return None
    
    #check all solutions in subquestions
    contain_equation = False
    for subquestion in problem["subquestions"]:
        if "solution" not in subquestion or not isinstance(subquestion["solution"], str):
            print(f"Subquestion in problem {problem['id']} is missing solution or solution is not a string.")
            return None
        #check if the solution contains any $$ equations
        if "$$" in subquestion["solution"]:
            contain_equation = True
    if not contain_equation:
        print(f"Problem {problem['id']} does not contain any $$ equations in solutions.")
        return None       
    valid_subquestions = problem["subquestions"]
    
    #check if the problem or subproblem context contains $ or numerical numbers
    if "$" not in problem["context"] and not any(
        "$" in subquestion.get("subproblem", "") for subquestion in valid_subquestions
    ) and not any(
        any(char.isdigit() for char in subquestion.get("solution", "")) for subquestion in valid_subquestions
    ):
        print(f"Problem {problem['id']} does not contain any $ or numerical numbers in context or subquestions.")
        return None
    
    problem["subquestions"] = valid_subquestions
    return problem

DEBUGGING = False
if __name__ == "__main__":
    DEBUGGING = True

if DEBUGGING:
    with open("org_expr.txt", "w") as f:
        f.write("")
    with open("ex_expr.txt", "w") as f:
        f.write("")
def simplify_latex_expr(expr: str) -> str:
    if DEBUGGING:
        org_txt = open("org_expr.txt", "r").read()
        if expr not in org_txt:
            with open("org_expr.txt", "a") as f:
                f.write(expr + "\n")
            
    # Remove \left and \right
    expr = re.sub(r'\\left\s*', '', expr)
    expr = re.sub(r'\\right\s*', '', expr)
    
    # Remove line breaks
    expr = re.sub(r'(\\\\|\\newline| \\ )', ' ', expr)
    
    # Remove spacings including \, \; \: \! and multiple spaces
    expr = re.sub(r'\\[ ,;:!]', '', expr)
    expr = expr.strip()
    
    # Remove environments like align, equation*, etc.
    expr = re.sub(r'\\begin\{[a-zA-Z*]+\}', '', expr)
    expr = re.sub(r'\\end\{[a-zA-Z*]+\}', '', expr)
    
    # Handle \text{...}, \mathrm{...}, \operatorname{...}
    expr = re.sub(r'\\mathrm\{([^}]*)\}', r'\1', expr)
    expr = re.sub(r'\\operatorname\{([^}]*)\}', r'\1', expr)

    # Optional: strip trailing punctuation like commas or periods
    expr = expr.strip()
    expr = re.sub(r'([^\d)])[,\.]\s*$', r'\1', expr)  # end of expression
    expr = re.sub(r'\s+', ' ', expr)
    
    # (0) Modify \approx to =.
    expr = re.sub(r'\\approx', r'=', expr)

    # (1) Modify \ddot{something} to \ddot_{something}
    expr = re.sub(r'\\ddot\{([^\{\}]+)\}', r'\\ddot_{\1}', expr)

    # (2) Add \cdot before brackets after variable/function if contents look like multiplication

    expr = add_times_before_NonFunctionalbrackets(expr)
    
    
    if DEBUGGING:
        ex_expr = open("ex_expr.txt", "r").read()
        if expr not in ex_expr:
            with open("ex_expr.txt", "a") as f:
                f.write(expr + "\n")
    return expr