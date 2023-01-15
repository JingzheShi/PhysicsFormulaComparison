# CPHOSS_Formula_Comparison
the formula comparison part of Centralized Physics Olympiad Scoring System

## 大致思路（限定在一道题中）
下面Answer指学生answer，Formula指标答formula

1. 将所有学生的所有Answer字符串放到一个字典或者列表里面。例如说你用列表的话，也许可以实现成这样子：
``type(All_Students_All_Answer_Strs_lst[0]) = dict``，其中
``One_Student_One_Answer_Str_lst = All_Student_Answer_Str_lst[0]``
``One_Student_One_Answer_Str_lst['StudentID']=...``
``One_Student_One_Answer_Str_lst['AnswerLatexStr']=...``
2. 另一边，通过``problem.Formula_Dct``,获得这个题所有的标答的formula，其中``problem``是``ProblemAnswer``类的一个实例
3. 生成一个``All_Students_All_Formula_Scores_Dct``，其中
``One_Student_All_Formula_Score = All_Students_All_Formula_Scores_Dct[StudentID]``
``type(One_Student_All_Formula_Score) = dict``
``One_Student_All_Formula_Score[TokenStr_of_any_formula] = 0 # initialized to 0``
4. 对``All_Students_All_Answer_Strs_lst``和``Formula_Dct``里面的每一对匹配``(answer,formula)``，计算它们匹不匹配，然后去更新``All_Students_All_Formula_Scores_Dct[StudentId][FormulaID]``
在这里，做multiprocessing！！！
5. 上面那一步做完以后，我们就获得了最终的``All_Students_All_Formula_Scores_dct``，然后我们拿这个里头的每一个``One_Student_All_Formula_Score``，再加上``Node``类下面的``evaluate_points``函数，就获得了这个学生这个题目的分数了捏


## 公式对比函数（``single_formula_compare.py``）使用
```python
def whether_rel_latex_correct(rel_latex,answer_latex,
                               constants_latex_expression={r'\kg':3,r'\s':7,r'\m':11,r'\A':13,r'\K':17,r'\g':0.003},
                               strict_comparing_inequalities=False,
                               epsilon_for_equal=1e-2,
                               tolerable_diff_fraction = TOLERABLE_DIFF_FRACTION,
                               tolerable_diff_max = TOLERABLE_DIFF_MAX,):
```

1. rel_latex: str，学生某式答案，latex

2. answer_latex:str，标答latex

3. constants_latex_expression:字典。key的类型是str，value的类型是float或者int。这是啥意思？就是说我比对的时候，会把key代入成value。比如说，如果这个字典里面，r'\kg':3,r'\g':0.003，那么我比较M=1kg和M=1000g这两个式子是不是一样？嗷，我先把kg和g作为常熟代入，我知道了M=1kg表示 eq(M,3), M=1000g表示 eq(M,3)，那么他们俩就一样了！

4. strict_comparing_inequalities:bool, default to false

	小于写成小于等于算不算对？

5. epsilon_for_equal E=1000和E=1001，算不算对？（对应case1）

6. tolerable_diff_fraction E=mc\^2和E/c\^2=m 是一样的吧

	那么这两个式子一样吗？
	$$
	(114514x^5+1919x^4+810x^3+123x)(x+1) = (114514x^5+1919x^4+810x^3+123x)(y)
	$$

	$$
	x+1=y
	$$

	如果两式之商中算符的个数小于max(Tolerable_diff_max, tolerable_diff_fraction*标答中算符个数)，算对。（对应case2）

注意：

1. case1 如果说，一个式子，它除了constants_latex_expression以外只剩一个未知量，那么比较是否相等的方法就是把那个未知量解出来，和标答比较。
2. case2 如果说，一个式子，它有两个以上未知量，那么就先化简，然后看（它左右两边的差和标答左右两边的差的商）是否足够简洁。



一般而言呢，对于每一对(studentAnswer, correctFormula)，或者说对于一个correctFormula，我们都有一些可以视作常量的变量，比如知道杠杆一段加一个力f，求另一端的力F，使得力臂平衡，如果力臂之比是2:1. 那么答案是不是F=2f? 那么这时候，我们在这个式子的config.py里面，写上constants={'f'}，那么我们生成problemAnswer的时候，会把它改成一个字典:constants={'f':461}例如说，同时呢传入上面那个函数的字典可以是{'f':461}，表示我们这里把f看成是像m，kg，N一样的常数，计算时会带入461. 461是一个质数。

但是，如果看成常数的是小方块质量m怎么办？这不是和米冲突了？那我们就把表示米的m从传入字典里删了，再加一个表示小方块质量的m。

事实上，我给出了三种常量，可以在题目里定义。

1. constants
2. universe_constants
3. units

以上三个，如果题目里面没有定义，就用default的。

除了constants如上介绍，其他两个顾名思义

我们最终传入constants_latex_expression的，应当是这三部分的综合考虑。**你大概需要考虑一下应该传什么。当然，你也可以修正一下这套逻辑。**

## 主程序部分使用（``multiStudents_compare_oneProblem.py``）
1. 初始化考试信息，将所有学生ID填入``STUDENTS_ID_SET``中，将所有problem ID，problem Name的pair填入``PID_DICT``中。
2. 最终程序会生成一个``All_Students_All_Answer_dict``，其中``All_Students_All_Answer_dict[studentID]``为一个``StudentAnswer_for_SingleProblem``类对象，包含有学生的作答（``studentLatexLst``），该题总分（``points``），每条式子（对应标答）得分（``studentScoreDct``）。
