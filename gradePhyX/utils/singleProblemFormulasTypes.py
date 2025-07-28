inherit_lst = ["to_be_calculated","constants","universe_constants","units","strict_comparing_inequalities","epsilon_for_equal","unit_pattern","whole_unit_pattern","units_conversion_dict"]

from .default_hyperparams import EPSILON_FOR_EQUAL, UNIT_PATTERN, WHOLE_UNIT_PATTERN, UNITS_CONVERSION_DICT, DEFAULT_UNIVERSE_CONSTANTS

DESCRIPTION = {
    "formula": "(sum)",
    "floor": "(min)",
    "part": "(sum)",
    "solution": "(max)",
    "prevsumnode": "(sum of previous nodes for correct ones)",
}

default_dct = {"to_be_calculated":dict(),"constants":dict(),"universe_constants":DEFAULT_UNIVERSE_CONSTANTS,"units":dict(),
               "strict_comparing_inequalities":False,
               "epsilon_for_equal":EPSILON_FOR_EQUAL,
               "unit_pattern":UNIT_PATTERN,
               "whole_unit_pattern":WHOLE_UNIT_PATTERN,
               "units_conversion_dict":UNITS_CONVERSION_DICT
               }

from copy import deepcopy

class Formula():
    def __init__(self,dct,prefix_str,type,**kwargs):
        assert type == "formula", "Formula type need to be formula"
        self.type = type
        self.max_points = dct["points"]
        self.TokenStr = prefix_str
        self.answer_latex = dct['answer_latex']
        self.utils_dct = dict()
        if "formula_describe" in dct:
            self.describe = str(dct["formula_describe"])
        else:
            self.describe = self.TokenStr
        for item in inherit_lst:
            if item in dct:
                self.utils_dct[item] = dct[item]
            elif item in kwargs:
                self.utils_dct[item] = deepcopy(kwargs[item])#.copy()
            else:
                self.utils_dct[item] = default_dct[item]
        self.utils_dct["universe_constants"] = self.utils_dct["universe_constants"].copy()
        self.utils_dct["units"] = self.utils_dct["units"].copy()
        for item in self.utils_dct["to_be_calculated"]:
            if item in self.utils_dct["universe_constants"]:
                self.utils_dct["universe_constants"].pop(item)
            if item in self.utils_dct["units"]:
                self.utils_dct["units"].pop(item)
        new_constants_dct = dict()
        # print(self.utils_dct["constants"])
        for index,item in enumerate(self.utils_dct["constants"]):
            if item in self.utils_dct["universe_constants"]:
                self.utils_dct["universe_constants"].pop(item)
            if item in self.utils_dct["units"]:
                self.utils_dct["units"].pop(item)
            if isinstance(self.utils_dct["constants"], dict):
                new_constants_dct[item] = self.utils_dct["constants"][item]
            else:
                new_constants_dct[item] = item
            
        self.utils_dct["constants"] = new_constants_dct
        # print(self.utils_dct["universe_constants"])
        # print(self.utils_dct["constants"])
        
            
            
            
        

class Node():
    def __init__(self,dct,prefix_str,type,**kwargs):
        
        self.type=type
        parse_dct=dict()
        for inherit_key in inherit_lst:
            if inherit_key in dct:
                parse_dct[inherit_key] = dct[inherit_key]
            elif inherit_key in kwargs:
                parse_dct[inherit_key] = kwargs[inherit_key]
        self.prefix_str = prefix_str
        self.children_lst = []
        assert "points" in dct, "Must assign points to part, solution, formula, floor or prevsumnode"

        self.max_points = dct["points"]
        self.student_points = -1.0
        
        counter = 0
        counter += 1 if "solution_1" in dct else 0
        counter += 1 if "part_1" in dct else 0
        counter += 1 if "floor_1" in dct else 0
        counter += 1 if "prevsumnode_1" in dct else 0
        assert counter <= 1, "Cannot have more than one of solution_1, part_1, floor_1 or prevsumnode_1 in the same node"
        
        
        if "solution_1" in dct:
            assert ("formula_1" not in dct), "If you use solution, then all formulas should be inside solution"
            self.ChildrenNodeType = "solution"
            s=1
            while ("solution_{}".format(s) in dct):

                self.children_lst.append(Node(dct["solution_{}".format(s)],self.prefix_str+'-{}'.format(s),"solution", **parse_dct)      )
                #assert self.children_lst[-1].max_points <= self.max_points, "Points in solution_{} cannot be more than points in its father".format(s)
                s=s+1
        if "part_1" in dct:

            assert ("formula_1" not in dct), "If you use part, then all formulas should be inside part"
            self.ChildrenNodeType = "part"
            s=1
            while ("part_{}".format(s) in dct):
                self.children_lst.append(Node(dct["part_{}".format(s)],self.prefix_str+'+{}'.format(s),"part",**parse_dct)) 
                s=s+1
                
            #assert sum([child.max_points for child in self.children_lst]) == self.max_points, "Points in parts should be equal to the points in its father"

        if "floor_1" in dct:
            self.ChildrenNodeType = "floor"
            s=1
            while ("floor_{}".format(s) in dct):
                self.children_lst.append(Node(dct["floor_{}".format(s)],self.prefix_str+'*{}'.format(s),"floor",**parse_dct))
                s=s+1
            
        if "prevsumnode_1" in dct:
            self.ChildrenNodeType = "prevsumnode"
            s=1
            while ("prevsumnode_{}".format(s) in dct):
                self.children_lst.append(Node(dct["prevsumnode_{}".format(s)],self.prefix_str+'~{}'.format(s),"prevsumnode",**parse_dct))
                s=s+1

        if "formula_1" in dct:
            self.ChildrenNodeType = "formula"
            s=1
            while ("formula_{}".format(s) in dct):
                self.children_lst.append(Formula(dct["formula_{}".format(s)],self.prefix_str+'+{}'.format(s),"formula",**parse_dct))
                s+=1
                
        

            #assert sum([child.max_points for child in self.children_lst]) == self.max_points, "Points in formulas should be equal to the points in its father"
    def evaluate_points(self,Student_Score_Dct, whether_modify_self_student_points=True):
        part_score = float(0)
        
        if self.ChildrenNodeType == "formula":
            for child in self.children_lst:
                if child.TokenStr in Student_Score_Dct:
                    part_score += Student_Score_Dct[child.TokenStr]
        elif self.ChildrenNodeType == "part":
            for child in self.children_lst:
                part_score += child.evaluate_points(Student_Score_Dct, whether_modify_self_student_points)
        elif self.ChildrenNodeType == "solution":
            part_score = max([child.evaluate_points(Student_Score_Dct, whether_modify_self_student_points) for child in self.children_lst])
        elif self.ChildrenNodeType == "floor":
            part_score = min([child.evaluate_points(Student_Score_Dct, whether_modify_self_student_points) for child in self.children_lst])
        elif self.ChildrenNodeType == "prevsumnode":
            child_scores = [child.evaluate_points(Student_Score_Dct, whether_modify_self_student_points) for child in self.children_lst]
            child_max_points = [child.max_points for child in self.children_lst]
            is_correct = [child_score >= child_max_point - 1e-4 for (child_score, child_max_point) in zip(child_scores, child_max_points)]
                                                        # - 1e-4 is used to avoid floating point precision issues.

            # find the largest index of which is correct is True.
            if any(is_correct):
                last_correct_index = max([i for i, correct in enumerate(is_correct) if correct])
                all_correct_score_sum = sum(child_max_points[:last_correct_index + 1])
                other_correct_score_sum = sum(child_scores[last_correct_index + 1:]) if last_correct_index + 1 < len(child_scores) else 0.0
                part_score = all_correct_score_sum + other_correct_score_sum
            else:
                last_correct_index = -1
                part_score = sum(child_scores)
        
        if whether_modify_self_student_points:
            self.student_points = part_score if part_score <= self.max_points else self.max_points
        
        
        return part_score if part_score <= self.max_points else self.max_points

    def checkScores(self):
        assert self.type == 'root', "This function should only be called on root node."
        children_max_scores = [child.max_points for child in self.children_lst]
        children_student_scores = [child.student_points for child in self.children_lst]
        return dict(
            problem_max_score = self.max_points,
            problem_student_score = self.student_points,
            subproblems_score_aggregatelogic = self.ChildrenNodeType+DESCRIPTION[self.ChildrenNodeType],
            subproblems_max_scores = children_max_scores,
            subproblems_student_scores = children_student_scores
        )

    
class ProblemFormulas():
    def __init__(self,dct,problemName,problemID,problemLocation = 'unspecified'):
        # it is recommanded that you use location of config file as PID.
        self.problemName = problemName
        self.problemID = problemID
        self.problemLocation = problemLocation
        self.root_node = Node(dct,'PID:'+str(problemID)+'___PLC:'+str(problemLocation)+'_______ProblemName:'+str(problemName)+'____________________FORMULAID_','root')
        self.Formula_Dct = dict()
        def Go_Through_Tree(node:Node):
            #print("A")
            if node.ChildrenNodeType == "formula":
                for child in node.children_lst:
                    self.Formula_Dct[child.TokenStr] = child
            else:
                for child_node in node.children_lst:
                    Go_Through_Tree(child_node)
        Go_Through_Tree(self.root_node)
        
    def evaluate(self,Student_Score_Dct, whether_modify_self_student_points=False):
        return self.root_node.evaluate_points(Student_Score_Dct, whether_modify_self_student_points)
    
    def evaluate_copying_node(self, Student_Score_Dct, whether_modify_self_student_points=True):
        # this function is used to evaluate the problem formulas without modifying the student points
        rootnode_copy = deepcopy(self.root_node)
        rootnode_copy.evaluate_points(Student_Score_Dct, whether_modify_self_student_points)
        return rootnode_copy



# problemFormulas = build_problem_formula(r"./Formula_Compare/configs/question1_config.py","第一题")
# for key in problemFormulas.Formula_Dct:
#     print("===============================================================")
#     print(problemFormulas.Formula_Dct[key].TokenStr)
#     print(problemFormulas.Formula_Dct[key].describe)
#     print(problemFormulas.Formula_Dct[key].utils_dct)
#     print(problemFormulas.Formula_Dct[key].max_points)
#     print(problemFormulas.Formula_Dct[key].answer_latex)
