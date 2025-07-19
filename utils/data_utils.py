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