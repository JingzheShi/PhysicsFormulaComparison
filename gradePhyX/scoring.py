from argparse import ArgumentParser
from utils import Formula
from utils import build_problem_formula,build_Student_AnswersAndScores_for_SingleProblem_from_pth, build_Student_AnswersAndScores_for_MultiProblem_from_dict
from utils import multiStudent_compare_multiProblem, whether_rel_latex_correct_with_units_with_only_one_dict_parameter
from utils import build_problem_formulas_for_multiProblems, build_Student_AnswersAndScores_for_MultiProblem_from_dict, compare_multiple_formula_pairs
import json
import os


def parse_arguements():
    parser = ArgumentParser()
    parser.add_argument('--problem_formulas_location', type=str, default='examples/questions_config.json')
    parser.add_argument('--students_answers_location', type=str, default='examples/students_answers.json')
    parser.add_argument('--N_process',type=int,default=6)
    
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguements()
    print("args:")
    print(args)
    
    problemFormulas = json.load(open(args.problem_formulas_location,'r',encoding='utf-8'))
    studentsAnswers = json.load(open(args.students_answers_location,'r',encoding='utf-8'))
    
    problemsList = build_problem_formulas_for_multiProblems(problemFormulas)
    studentsAnswersAndScores = build_Student_AnswersAndScores_for_MultiProblem_from_dict(problemsList,studentsAnswers)

    multiStudent_compare_multiProblem(problemsList, studentsAnswersAndScores, args.N_process, return_detailed_score=True,
                                      compare_function=whether_rel_latex_correct_with_units_with_only_one_dict_parameter)

    for studentID, student_answersAndScores_for_problems in studentsAnswersAndScores.items():
        # print("studentID: ", studentID)
        for problemID, this_student_answerAndScore_for_singleProblem in student_answersAndScores_for_problems.items():
            # print("problemID: ", problemID)
            # print("points: ", this_student_answerAndScore_for_singleProblem.points)
            # print("studentScoreDct: ", this_student_answerAndScore_for_singleProblem.studentScoreDct)
            # print("points: ", this_student_answerAndScore_for_singleProblem.points)
            print(f"Student {studentID} Problem {problemID} Points: {this_student_answerAndScore_for_singleProblem.points}")
            print(f"Student {studentID} Problem {problemID} Detailed score: {this_student_answerAndScore_for_singleProblem.detailed_score.checkScores()}")
    
    
    
    
    
# if __name__ == "__main__":
#     pairs = [
#         dict(
#             rel_latex = 'a+b=1',
#             answer_latex='a=1-b',
#             constants_latex_expression = {
#                 'u':'1/r'
#             },
#             strict_comparing_inequalities = False,
#             epsilon_for_equal = 1e-2,
#             unit_pattern = r'\\unit{(.*?)}',
#             whole_unit_pattern = r'(\\unit{.*?})',
#             units_conversion_dict = {
#                 'm': 'm','km':'1000*m'
#             },
#         ),
#         dict(
#             rel_latex = 'a+b=1',
#             answer_latex='a=1-b',
#             constants_latex_expression = {
#                 'u':'1/r'
#             },
#             strict_comparing_inequalities = False,
#             epsilon_for_equal = 1e-2,
#             unit_pattern = r'\\unit{(.*?)}',
#             whole_unit_pattern = r'(\\unit{.*?})',
#             units_conversion_dict = {
#                 'm': 'm','km':'1000*m'
#             },
#         ),
#     ]
    
#     print(compare_multiple_formula_pairs(pairs, 2))