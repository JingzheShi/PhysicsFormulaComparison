from argparse import ArgumentParser
from utils import Formula
from utils import build_problem_formula,build_Student_AnswersAndScores_for_SingleProblem_from_pth
from utils import multiStudents_compare_oneProblem
def parse_arguements():
    parser = ArgumentParser()
    parser.add_argument('--problem_formulas_location', type=str, default='problemFormulas/question1_config.py')
    parser.add_argument('--students_answers_location', type=str, default='studentsAnswers/students_answers_for_question1.pth')
    parser.add_argument('--problemName',type=str,default='question1')
    parser.add_argument('--problemID',type=str,default="question1ID_test1sodifa;e")
    parser.add_argument('--N_process',type=int,default=8)
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguements()
    print("args:")
    print(args)
    
    problemFormulas = build_problem_formula(args.problem_formulas_location,args.problemName,problemID = args.problemID)
    studentsAnswersAndScores = build_Student_AnswersAndScores_for_SingleProblem_from_pth(problemFormulas,args.students_answers_location)
    # The studentsAnswersAndScores should be a list of type dict.
    # The items of this dict is:
    # studentID: studentID
    # latexList: a list of latex string, of this student.
    
    print("Now start to compare the answers of students with the formulas of the problem, using multiprocessing")
    multiStudents_compare_oneProblem(problemFormulas,studentsAnswersAndScores,args.N_process)
    print("Finishing comparing using multiprocessing.")
    for studentID, this_student_answerAndScore_for_singleProblem in studentsAnswersAndScores.items():
        print("studentID: ",studentID)
        print("points: ",this_student_answerAndScore_for_singleProblem.points)
        print("studentScoreDct: ",this_student_answerAndScore_for_singleProblem.studentScoreDct)
        print("points: ",this_student_answerAndScore_for_singleProblem.points)
    
    
    
    
    