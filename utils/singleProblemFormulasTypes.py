inherit_lst = ["to_be_calculated","constants","universe_constants","units","strict_comparing_inequalities","epsilon_for_equal","tolerable_diff_max","tolerable_diff_fraction"]

UNIVERSE_CONSTANTS_WEIGHTS = {r'c':float(300000000*1997/119),}
UNIT_WEIGHTS={r'm':float(1.997),r'\kg':1.1451,r'\g':float(1.1451/1000),r'\cm':0.01997,r's':119,'J':float(1.1451*1.997**2/119**2)}
EPSILON_FOR_EQUAL = 1e-2
TOLERABLE_DIFF_MAX = 5
TOLERABLE_DIFF_FRACTION = 0.6
PRIMES = [461,2089,641,787,4019, 809, 1871, 2969, 3089, 2591, 2129, 2381, 619, 1667, 2657, 2549, 3391, 1289, 3271, 1021, 1223, 3167, 3769, 3433, 2357, 3571, 1451, 4007, 3433, 2927, 3691, 3527, 3329, 2029, 3319, 3109, 2837, 3931, 3217, 2789, 3821, 3791, 2621, 3797, 2437, 3769]

default_dct = {"to_be_calculated":dict(),"constants":dict(),"universe_constants":UNIVERSE_CONSTANTS_WEIGHTS,"units":UNIT_WEIGHTS,
               "strict_comparing_inequalities":False,
               "epsilon_for_equal":EPSILON_FOR_EQUAL,"tolerable_diff_max":TOLERABLE_DIFF_MAX,"tolerable_diff_fraction":TOLERABLE_DIFF_FRACTION}

default_dct = {"to_be_calculated":dict(),"constants":dict(),"universe_constants":dict(),"units":dict(),
               "strict_comparing_inequalities":False,
               "epsilon_for_equal":EPSILON_FOR_EQUAL,"tolerable_diff_max":TOLERABLE_DIFF_MAX,"tolerable_diff_fraction":TOLERABLE_DIFF_FRACTION}

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
                self.utils_dct[item] = kwargs[item].copy()
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
                new_constants_dct[item] = PRIMES[index]
            
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
        assert "points" in dct, "Must assign points to part, solution, formula or floor"

        self.max_points = dct["points"]
        
        counter = 0
        counter += 1 if "solution_1" in dct else 0
        counter += 1 if "part_1" in dct else 0
        counter += 1 if "floor_1" in dct else 0
        assert counter <= 1, "Cannot have more than one of solution_1, part_1 or floor_1 in the same node"
        
        
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

        if "formula_1" in dct:
            self.ChildrenNodeType = "formula"
            s=1
            while ("formula_{}".format(s) in dct):
                self.children_lst.append(Formula(dct["formula_{}".format(s)],self.prefix_str+'+{}'.format(s),"formula",**parse_dct))
                s+=1
                
        

            #assert sum([child.max_points for child in self.children_lst]) == self.max_points, "Points in formulas should be equal to the points in its father"
    def evaluate_points(self,Student_Score_Dct):
        part_score = float(0)
        if self.ChildrenNodeType == "formula":
            for child in self.children_lst:
                if child.TokenStr in Student_Score_Dct:
                    part_score += Student_Score_Dct[child.TokenStr]
            return part_score if part_score <= self.max_points else self.max_points
        elif self.ChildrenNodeType == "part":
            for child in self.children_lst:
                part_score += child.evaluate_points(Student_Score_Dct)
            return part_score if part_score <= self.max_points else self.max_points
        elif self.ChildrenNodeType == "solution":
            part_score = max([child.evaluate_points(Student_Score_Dct) for child in self.children_lst])
            return part_score if part_score <= self.max_points else self.max_points
        elif self.ChildrenNodeType == "floor":
            part_score = min([child.evaluate_points(Student_Score_Dct) for child in self.children_lst])
            return part_score if part_score <= self.max_points else self.max_points
        
        
    
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
    def evaluate(self,Student_Score_Dct):
        return self.root_node.evaluate_points(Student_Score_Dct)



# problemFormulas = build_problem_formula(r"./Formula_Compare/configs/question1_config.py","第一题")
# for key in problemFormulas.Formula_Dct:
#     print("===============================================================")
#     print(problemFormulas.Formula_Dct[key].TokenStr)
#     print(problemFormulas.Formula_Dct[key].describe)
#     print(problemFormulas.Formula_Dct[key].utils_dct)
#     print(problemFormulas.Formula_Dct[key].max_points)
#     print(problemFormulas.Formula_Dct[key].answer_latex)
