from student_answer import StudentAnswer_for_SingleProblem
from problem_answer import ProblemAnswer
from problem_answer import build_Problem_Answer
from single_formula_compare import whether_rel_latex_correct_with_only_one_dict_parameter
from problem_answer import Formula

# Initialize information for the whole test
STUDENTS_ID_SET = set()
PID_DICT = dict() # This dictionary should be like {PID:"ProblemName"}

# Initialize information for the specific problem
problem_id = str()
problem_name = PID_DICT[problem_id]
problem_answer = build_Problem_Answer(problem_id,problem_name)
latexLists_dict = dict() # students' answers dictionary, such as {studentID:latexLists}
All_Students_All_Answer_dict = dict()
for student_id in STUDENTS_ID_SET:
    All_Students_All_Answer_dict[student_id] = StudentAnswer_for_SingleProblem(student_id,problem_name,problem_id,latexLists_dict[student_id])

# Multi-processing
All_Students_All_Answer_lst = list()
for formula_Tokenstr, formula in problem_answer.Formula_Dct.items():
    for student_id in STUDENTS_ID_SET:
        for stu_answer_latex in latexLists_dict[student_id]:
            All_Students_All_Answer_lst.append({"rel_latex":formula.answer_latex,"answer_latex":stu_answer_latex,"student_id":student_id,"formula_Tokenstr":formula_Tokenstr,"correct":False,"max_points":formula.max_points})
for dct in All_Students_All_Answer_lst:
    dct["correct"] = whether_rel_latex_correct_with_only_one_dict_parameter(dct)
for dct in All_Students_All_Answer_lst:
    ((All_Students_All_Answer_dict[dct["student_id"]]).studentScoreDct)["formula_Tokenstr"] = (((All_Students_All_Answer_dict[dct["student_id"]]).studentScoreDct)["formula_Tokenstr"] or dct["correct"]) * dct["max_points"]
    
# Adding points

for student_id in STUDENTS_ID_SET:
    All_Students_All_Answer_dict[student_id].points = problem_answer.evaluate(All_Students_All_Answer_dict[student_id].studentScoreDct)    
