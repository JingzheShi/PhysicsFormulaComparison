from .singleProblemFormulasTypes import ProblemFormulas,Formula
from .singleStudentAnswerTypes import Student_AnswersAndScores_for_SingleProblem
from .single_formula_comparison_utils import whether_rel_latex_correct_with_units_with_only_one_dict_parameter
import multiprocessing
def compare_problemFormula_with_studentAnswer(dct):
    # The keys in dct should be:
    # problemID, studentID, formulaToken, problemFormula, studentAnswerLatex
    parsing_dct = dict(
        rel_latex = dct['problemFormula'].answer_latex,
        answer_latex = dct['studentAnswerLatex'],
        constants_latex_expression = {**dct['problemFormula'].utils_dct['constants'],
                                    **dct['problemFormula'].utils_dct['universe_constants'],
                                    **dct['problemFormula'].utils_dct['units']},
        strict_comparing_inequalities = dct['problemFormula'].utils_dct['strict_comparing_inequalities'],
        epsilon_for_equal = dct['problemFormula'].utils_dct['epsilon_for_equal'],
        # tolerable_diff_fraction = dct['problemFormula'].utils_dct['tolerable_diff_fraction'], deprecated.
        # tolerable_diff_max = dct['problemFormula'].utils_dct['tolerable_diff_max'], deprecated.
        unit_pattern = dct['problemFormula'].utils_dct['unit_pattern'],
        whole_unit_pattern = dct['problemFormula'].utils_dct['whole_unit_pattern'],
        units_conversion_dict = dct['problemFormula'].utils_dct['units_conversion_dict']
    )
    # print(f"units_conversion_dict: {parsing_dct['units_conversion_dict']}")
    whether_correct, description = whether_rel_latex_correct_with_units_with_only_one_dict_parameter(parsing_dct)
    return dict(
        studentID = dct['studentID'],
        problemID = dct['problemID'],
        formulaToken = dct['formulaToken'],
        whether_correct = whether_correct,
        obtained_points = dct['problemFormula'].max_points if whether_correct else 0,
        description = description   
    )
    
    

def multiStudent_compare_multiProblem(problemFormulasList:list,studentsAnswersAndScores:dict,N_process:int):
    #studentsAnswersAndScores: dict, key is studentID, value is dict,
        # whose key is problemID, value is of type Student_AnswersAndScores_for_SingleProblem
    
    
    # parsing_dcts_lst_root = []
    parsing_dcts_lst = []
    
    for studentID,studentAnswersAndScores in studentsAnswersAndScores.items():
        for problemformula_for_oneproblem in problemFormulasList:
            problemID = problemformula_for_oneproblem.problemID
            if problemID not in studentAnswersAndScores:
                continue
            assert problemID in studentAnswersAndScores, f"Problem ID {problemID} not found in student answers and scores for student {studentID}"
            studentAnswersAndScoresForThisProblem = studentAnswersAndScores[problemID]
            for formulaToken, formula in problemformula_for_oneproblem.Formula_Dct.items():
                for studentAnswerLatex in studentAnswersAndScoresForThisProblem.studentLatexLst:
                    parsing_dcts_lst.append(dict(
                        studentID = studentID,
                        problemID = problemID,
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
        problemID = parsing_dct['problemID']
        formulaToken = parsing_dct['formulaToken']
        point = parsing_dct['obtained_points']
        if point > studentsAnswersAndScores[studentID][problemID].studentScoreDct[formulaToken]:
            studentsAnswersAndScores[studentID][problemID].studentScoreDct[formulaToken]=point

    for problemFormulas in problemFormulasList:
        problemID = problemFormulas.problemID
        for studentID, student_answersAndScores_for_SingleProblem in studentsAnswersAndScores.items():
            if problemID in student_answersAndScores_for_SingleProblem:
                if problemID not in student_answersAndScores_for_SingleProblem:
                    continue
                assert problemID in student_answersAndScores_for_SingleProblem, f"Problem ID {problemID} not found in student answers and scores for student {studentID}"
                student_answersAndScores_for_SingleProblem[problemID].points = problemFormulas.evaluate(
                    student_answersAndScores_for_SingleProblem[problemID].studentScoreDct
                )
    
    
    return
    
    
    
    
    
       
        
    