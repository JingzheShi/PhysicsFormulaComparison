from .singleStudentAnswerTypes import Student_AnswersAndScores_for_SingleProblem
from .singleProblemFormulasTypes import ProblemFormulas


def _build_Problem_Dict(config_file_location):
    print(f"Loading problem configuration from {config_file_location}")
    namespace = {}
    with open(config_file_location, 'r') as file:
        content = file.read()
        exec(content, namespace)
    print("Done!")

    # Find the first dictionary in the namespace and return it
    for name, value in namespace.items():
        
        if isinstance(value, dict) and name.startswith('question'):
            return value


def build_problem_formula(config_file_location,problemName:None,problemID:None):
    problem_dct = _build_Problem_Dict(config_file_location)
    if problemID is None:
        problemID = problem_dct['problemID']
    # print(problem_dct)
    # assert False
    problemFormulas = ProblemFormulas(problem_dct,problemName,problemID,config_file_location)
    
    return problemFormulas








def _build_Student_AnswersAndScores_for_SingleProblem_from_lst(problemFormulas:ProblemFormulas,studentsAnswers_dcts_lst):
    built_dct=dict()
    problemID = problemFormulas.problemID
    
    for studentAnswers_dct in studentsAnswers_dcts_lst:
        studentID = studentAnswers_dct['studentID']
        student_latexList = studentAnswers_dct['latexList']
        student_AnswersAndScores_for_SingleProblem = Student_AnswersAndScores_for_SingleProblem(studentID,problemID,student_latexList,problemFormulas)
        built_dct[str(studentID)]=student_AnswersAndScores_for_SingleProblem
    
    return built_dct


def build_Student_AnswersAndScores_for_SingleProblem_from_pth(problemFormulas:ProblemFormulas,studentsAnswers_dcts_lst_location):
    import torch
    studentsAnswers_dcts_lst = torch.load(studentsAnswers_dcts_lst_location)
    return _build_Student_AnswersAndScores_for_SingleProblem_from_lst(problemFormulas,studentsAnswers_dcts_lst)


def convert_constant_lists_to_sets(d):
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, dict):
                convert_constant_lists_to_sets(v)
            elif 'constant' in k and isinstance(v, list):
                d[k] = set(v)
    elif isinstance(d, list):
        for item in d:
            convert_constant_lists_to_sets(item)
def build_problem_formulas_for_multiProblems(problemDict:dict):
    convert_constant_lists_to_sets(problemDict)
    return_dict = dict()
    return_list = list()
    for problemID, content in problemDict.items():
        
        if 'problemID' not in content:
            content['problemID'] = problemID
        else:
            assert content['problemID'] == problemID, f"Problem ID mismatch: {content['problemID']} != {problemID}"
        if 'problemName' in content:
            problemName = content['problemName']
            # delete content['problemName'].
            del content['problemName']
        else:
            problemName = problemID

        # print(content)
        problemFormulas = ProblemFormulas(content, problemName, problemID, None)
        return_dict[problemID] = problemFormulas
        return_list.append(problemFormulas)
    return return_list




def build_Student_AnswersAndScores_for_MultiProblem_from_dict(problemFormulasList:list, studentsAnswers_dict: dict):
    # studentsAnswers dict: key is studentID, value is dict,
        # whose key is problemID, value is a list of latex strings.
    built_dct = dict()
    for problemFormulas in problemFormulasList:
        problemID = problemFormulas.problemID
        for studentID, studentAnswers_for_multiProblem in studentsAnswers_dict.items():
            if problemID not in studentAnswers_for_multiProblem:
                continue
            assert problemID in studentAnswers_for_multiProblem, f"Problem ID {problemID} not found in student answers and scores for student {studentID}"
            student_Answers_latex_list = studentAnswers_for_multiProblem[problemID]
            if str(studentID) not in built_dct:
                built_dct[str(studentID)] = dict()
            if problemID not in built_dct[str(studentID)]:
                built_dct[str(studentID)][problemID] = Student_AnswersAndScores_for_SingleProblem(
                    studentID, problemID, student_Answers_latex_list, problemFormulas
                )

    return built_dct