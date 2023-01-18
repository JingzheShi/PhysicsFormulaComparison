import torch
from .singleStudentAnswerTypes import Student_AnswersAndScores_for_SingleProblem
from .singleProblemFormulasTypes import ProblemFormulas



def _build_Problem_Dict(config_file_location):
    # config_file is a python file, recording the problem information.
    # This is like the config file in mmdetection.
    with open(config_file_location, 'r') as file:
        content = file.read()
        exec(content)

    for name, value in locals().items():
        if isinstance(value, dict):
            #print(name, value)
            return value


def build_problem_formula(config_file_location,problemName:None,problemID:None):
    problem_dct = _build_Problem_Dict(config_file_location)
    if problemID is None:
        problemID = problem_dct['problemID']
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
    studentsAnswers_dcts_lst = torch.load(studentsAnswers_dcts_lst_location)
    return _build_Student_AnswersAndScores_for_SingleProblem_from_lst(problemFormulas,studentsAnswers_dcts_lst)