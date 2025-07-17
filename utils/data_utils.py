import re

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

    # (1) Modify \ddot{something} to \ddot_{something}
    expr = re.sub(r'\\ddot\{([^\{\}]+)\}', r'\\ddot_{\1}', expr)

    # (2) Add \cdot before brackets after variable/function if contents look like multiplication
    def repl(match):
        var = match.group(1)
        inner = match.group(2)
        # If there is already * or \cdot or \times after var, skip
        if re.match(r'.*(\*|\\cdot|\\times)\s*$', var):
            return match.group(0)
        # If inner contains +, -, *, /, or \frac, it's multiplication
        if re.search(r'[\+\-\*/]|\\frac', inner):
            return f"{var} \\cdot ({inner})"
        else:
            return match.group(0)
    # Only match ( not at start of string, after variable
    pattern = r'(?<![\w\\])([a-zA-Z][a-zA-Z0-9_]*)\s*\(([^()]*)\)'
    expr = re.sub(pattern, repl, expr)
    if DEBUGGING:
        ex_expr = open("ex_expr.txt", "r").read()
        if expr not in ex_expr:
            with open("ex_expr.txt", "a") as f:
                f.write(expr + "\n")
    return expr