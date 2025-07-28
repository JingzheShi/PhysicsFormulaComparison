from .singleProblemFormulasTypes import ProblemFormulas
from .singleProblemFormulasTypes import Node
class Student_AnswersAndScores_for_SingleProblem():
    def __init__(self,studentID,problemID,latexList,problem_formula:ProblemFormulas):
        self.studentId = studentID
        self.problemID = problemID
        self.studentLatexLst = latexList
        self.points = 0
        self.detailed_score = None
        self.studentScoreDct = dict()
        def build_dct(node:Node):
            if node.ChildrenNodeType == "formula":
                for child in node.children_lst:
                    self.studentScoreDct[child.TokenStr] = 0
            else:
                for child_node in node.children_lst:
                    build_dct(child_node)
        build_dct(problem_formula.root_node)
        

