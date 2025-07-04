from argparse import ArgumentParser
from utils import Formula
from utils import build_problem_formula,build_Student_AnswersAndScores_for_SingleProblem_from_pth, build_Student_AnswersAndScores_for_MultiProblem_from_dict
from utils import multiStudents_compare_oneProblem, multiStudent_compare_multiProblem
from utils import build_problem_formulas_for_multiProblems, build_Student_AnswersAndScores_for_MultiProblem_from_dict
import json
import os


def parse_arguements():
    parser = ArgumentParser()
    parser.add_argument('--problem_formulas_location', type=str, default='problemFormulas/questions_config.json')
    parser.add_argument('--students_answers_location', type=str, default='studentsAnswers/students_answers.json')
    parser.add_argument('--N_process',type=int,default=14)
    
    return parser.parse_args()
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
if __name__ == '__main__':
    args = parse_arguements()
    print("args:")
    print(args)
    
    problemFormulas = json.load(open(args.problem_formulas_location,'r',encoding='utf-8'))
    studentsAnswers = json.load(open(args.students_answers_location,'r',encoding='utf-8'))
    
    problemsList = build_problem_formulas_for_multiProblems(problemFormulas)
    studentsAnswersAndScores = build_Student_AnswersAndScores_for_MultiProblem_from_dict(problemsList,studentsAnswers)

    multiStudent_compare_multiProblem(problemsList, studentsAnswersAndScores, args.N_process)

    for studentID, student_answersAndScores_for_problems in studentsAnswersAndScores.items():
        # print("studentID: ", studentID)
        for problemID, this_student_answerAndScore_for_singleProblem in student_answersAndScores_for_problems.items():
            # print("problemID: ", problemID)
            # print("points: ", this_student_answerAndScore_for_singleProblem.points)
            # print("studentScoreDct: ", this_student_answerAndScore_for_singleProblem.studentScoreDct)
            # print("points: ", this_student_answerAndScore_for_singleProblem.points)
            print(f"Student {studentID} Problem {problemID} Points: {this_student_answerAndScore_for_singleProblem.points}")
    
    
    
    
    
    