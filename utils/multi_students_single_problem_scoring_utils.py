from .singleProblemFormulasTypes import ProblemFormulas,Formula
from .singleStudentAnswerTypes import Student_AnswersAndScores_for_SingleProblem
from .single_formula_comparison_utils import whether_rel_latex_correct_with_only_one_dict_parameter
import multiprocessing
def compare_problemFormula_with_studentAnswer(dct):
    # The keys in dct should be:
    # studentID, formulaToken, problemFormula, studentAnswerLatex
    parsing_dct = dict(
        rel_latex = dct['problemFormula'].answer_latex,
        answer_latex = dct['studentAnswerLatex'],
        constants_latex_expression = {**dct['problemFormula'].utils_dct['constants'],
                                    **dct['problemFormula'].utils_dct['universe_constants'],
                                    **dct['problemFormula'].utils_dct['units']},
        strict_comparing_inequalities = dct['problemFormula'].utils_dct['strict_comparing_inequalities'],
        epsilon_for_equal = dct['problemFormula'].utils_dct['epsilon_for_equal'],
        tolerable_diff_fraction = dct['problemFormula'].utils_dct['tolerable_diff_fraction'],
        tolerable_diff_max = dct['problemFormula'].utils_dct['tolerable_diff_max']
    )
    whether_correct, description = whether_rel_latex_correct_with_only_one_dict_parameter(parsing_dct)
    return dict(
        studentID = dct['studentID'],
        formulaToken = dct['formulaToken'],
        whether_correct = whether_correct,
        obtained_points = dct['problemFormula'].max_points if whether_correct else 0,
        description = description   
    )
    
    

def multiStudents_compare_oneProblem(problemFormulas:ProblemFormulas,studentsAnswersAndScores:dict,N_process:int):
    #studentsAnswersAndScores: dict, key is studentID, value is of type Student_AnswersAndScores_for_SingleProblem
    formulas_dct = problemFormulas.Formula_Dct
    # parsing_dcts_lst_root = []
    parsing_dcts_lst = []
    
    for studentID in studentsAnswersAndScores.keys():
    #     parsing_dcts_lst_root.append([studentID])

    # def generate_answer_compare_lst(input_lst):
    #     studentID = input_lst[0]
        for studentAnswerLatex in studentAnswersAndScores.studentLatexLst:
            parsing_dcts_lst.append(dict(
        # for formulaToken, formula in formulas_dct.items():
        #     for studentAnswerLatex in studentsAnswersAndScores[studentID].studentLatexLst:
        #         input_lst.append(dict(
                    studentID = studentID,
                    formulaToken = formulaToken,
                    problemFormula = formula,
                    studentAnswerLatex = studentAnswerLatex
                ))

    # with multiprocessing.Pool(processes=N_process) as pool:
    #     output_compare_lst = pool.map(generate_answer_compare_lst, parsing_dcts_lst_root,chunksize=5)

    # for lst in output_compare_lst:
    #     del(lst[0])
    #     parsing_dcts_lst.extend(lst)
                
    with multiprocessing.Pool(processes=N_process) as pool:
        output_lst = pool.map(compare_problemFormula_with_studentAnswer, parsing_dcts_lst,chunksize=5)
    
    for parsing_dct in output_lst:
        studentID = parsing_dct['studentID']
        formulaToken = parsing_dct['formulaToken']
        point = parsing_dct['obtained_points']
        if point > studentsAnswersAndScores[studentID].studentScoreDct[formulaToken]:
            studentsAnswersAndScores[studentID].studentScoreDct[formulaToken]=point
    
    for student_answersAndScores_for_SingleProblem in studentsAnswersAndScores.values():
        student_answersAndScores_for_SingleProblem.points = problemFormulas.evaluate(student_answersAndScores_for_SingleProblem.studentScoreDct)
    
    return
    
    
    
    
    
       
        
    