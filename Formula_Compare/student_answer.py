from problem_answer import ProblemAnswer
from problem_answer import build_Problem_Answer
from problem_answer import Node
class StudentAnswer_for_SingleProblem():
    def __init__(self,studentID,problemName,problemID,latexList):
        self.studentId = studentID
        self.problemID = problemID
        self.problemName = problemName
        self.studentLatexLst = latexList
        self.points = -1
        self.studentScoreDct = dict()
        problem_answer = build_Problem_Answer(problemID,problemName)
        def build_dct(node:Node):
            if node.ChildrenNodeType == "formula":
                for child in node.children_lst:
                    self.studentScoreDct[child.TokenStr] = 0
            else:
                for child_node in node.children_lst:
                    build_dct(child_node)
        build_dct(problem_answer.root_node)
        
        
        