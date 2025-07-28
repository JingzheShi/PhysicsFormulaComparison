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
    
    compare_function = dct.get('compare_function', None)
    # print(f"units_conversion_dict: {parsing_dct['units_conversion_dict']}")
    try:
        whether_correct, description = compare_function(parsing_dct)
    except Exception as e:
        whether_correct = False
        description = f"Error in comparing: {e}"
    return dict(
        studentID = dct['studentID'],
        problemID = dct['problemID'],
        formulaToken = dct['formulaToken'],
        whether_correct = whether_correct,
        obtained_points = dct['problemFormula'].max_points if whether_correct else 0,
        description = description   
    )
    
    
def compare_multiple_formula_pairs(formulaPairDictList:list,N_process:int, compare_function = whether_rel_latex_correct_with_units_with_only_one_dict_parameter, return_reason=False):
    '''
        formulaPairDictList: each item should be a dict, with these keys:
            rel_latex: str
            answer_latex: str
            constants_latex_expression: dict(
                'u':'1/r'
            )
            strict_comparing_inequalities: False
            epsilon_for_equal: epsilon for equal
            unit_pattern: r'\\unit{(.*?)}'
            whole_unit_pattern: r'(\\unit{.*?})'
            units_conversion_dict: dict(
                'm': 'm','km':'1000*m'
            )
    '''
    with multiprocessing.Pool(processes=N_process) as p:
        output_list = p.map(whether_rel_latex_correct_with_units_with_only_one_dict_parameter, formulaPairDictList)
    if return_reason:
        return output_list
    else:
        return [x[0] for x in output_list]
    

def multiStudent_compare_multiProblem(problemFormulasList:list,studentsAnswersAndScores:dict,N_process:int,multiprocess_chunksize:int=2, return_detailed_score = False, show_progress=True,
                                      compare_function = whether_rel_latex_correct_with_units_with_only_one_dict_parameter):
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
                        studentAnswerLatex = studentAnswerLatex,
                        compare_function = compare_function
                    ))

    # with multiprocessing.Pool(processes=N_process) as pool:
    #     output_compare_lst = pool.map(generate_answer_compare_lst, parsing_dcts_lst_root,chunksize=5)

    # for lst in output_compare_lst:
    #     del(lst[0])
    #     parsing_dcts_lst.extend(lst)
    
    if not show_progress:
        with multiprocessing.Pool(processes=N_process) as pool:
            output_lst = pool.map(compare_problemFormula_with_studentAnswer, parsing_dcts_lst,chunksize=multiprocess_chunksize)
    else:
        from tqdm import tqdm
        from multiprocessing import Pool
        with Pool(processes=N_process) as pool:
            output_lst = list(
                tqdm(
                    pool.imap(compare_problemFormula_with_studentAnswer, parsing_dcts_lst, chunksize=multiprocess_chunksize),
                    total=len(parsing_dcts_lst),
                    desc="multi-student multi-problem scoring",
                )
            )
    
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
                # assert problemID in student_answersAndScores_for_SingleProblem, f"Problem ID {problemID} not found in student answers and scores for student {studentID}"
                student_answersAndScores_for_SingleProblem[problemID].points = problemFormulas.evaluate(
                    student_answersAndScores_for_SingleProblem[problemID].studentScoreDct
                )
                if return_detailed_score:
                    student_answersAndScores_for_SingleProblem[problemID].detailed_score = problemFormulas.evaluate_copying_node(
                        student_answersAndScores_for_SingleProblem[problemID].studentScoreDct
                    )

    return
    
    
    
    
    
       
        
    