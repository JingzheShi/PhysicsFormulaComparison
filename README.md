# GradePhyX

## Install

```bash
pip install gradePhyX
```
or
```bash
pip3 install gradePhyX
```

***Important: This Only works on Linux/WSL! Not Working on Windows!***

## Usage

This package contains two main features,
1. A Formula Comparison Engine for comparing whether two equations (with Physics Quantities) are equivalent.
2. A pipeline to evaluate multiple 'student answers' of multiple 'problems', and obtain each 'student's' score, in which the scoring structure of a problem can be tree-based. This pipeline supports multiprocessing.

You can find examples of them at `gradePhyX/scoring.py`.





## Formula Comparison Engine：tech report



## 1. How it works

Comparing two Physics Formulas in this engine takes three steps: Non-Constant Variable Identity Check, Constant Variable Substitution, and Equivalent Check by Solving in Random Conditions.

Take this as an example.

```python
whether_rel_latex_correct_with_only_one_dict_parameter({
    "rel_latex":      r"x = x_0 e^{-t/10 * Hz} + t*30000000m/s + 1m", # parsed in as equation to be judged
    "answer_latex":   r"x = x_0 e^{-t/(10*s)} + 0.1 c_0 t + x_f", # parsed in as answer equation
    "constants_latex_expression":{"e": np.e,             # supports number value
                                  "c_0": "300000000*m/s" # Physics Value with units also works
                                  "\\tau": "10.0*s",
                                  "x_f": "1m",
                                  # "m": "m",   # parsing in units are no longer needed after update 0711
                                  # "s": "s"    # parsing in units are no longer needed after update 0711
                                  }}
)
```

For a pair of equations, to compare whether they are equivalent, we go through these steps:



1. **Constant Variable Substitution**. All vars (detected in **both equations**) that is parsed in as `constants_latex_expression` will be converted (**Only Once**, **no recursive conversion**). This is designed for and can support (but not limited to) these cases:

   1. **Unit Conversion**. e.g. frequency unit $Hz=s^{-1}$ (time unit), so in this example, $-t/10*Hz = -t/(10*s)$, they are equivalent. Other cases related to Univt Conversion might be, for example, $1g=0.001kg$.

   2. **Given Value** of the problem. e.g. $x_f=1m$.

   3. **Math Constants**. e.g. Sympy by default view $e$ as a variable instead of the exponential constant, so need to parse in "e": np.e.

   4. **Universe Constants**. e.g. $c_0=300000000m/s$. Other cases might include, for example, $k=\frac{1}{4\pi \epsilon_0}$, so using $k$ or $\epsilon_0$ to represent Coulomb force are both valid.

   5. **Small amount specification**. In some problems some constant value is assigned as a small number, but in Step 2 each variable is substituted as a random float sampled from default range **$[-20,+20]$**, which might violate the problem's requirement, say, some particular constant $\alpha$ is very small, In such case, one could use **"\\\\alpha": "0.001\\\\alpha"** to restrict the range to **$[-0.02, + 0.02]$**; other executable things also include "\\\\alpha": "|\\\\alpha|" to restrict its value positive.

      **Mark. Is this the best way for small amount specification? Would it be better to support modifying sample ranges?**

   **Note 1**: **(No Longer Necessary)** Previously step 2 was before step 1, so one needed to parse in unit themselves, or in Step 2 will have some false negative results; this is solved in update 0711, same variable check is moved after parsing in constants, so no need to parse in units like "s":"s" any more.
   
   **Note 2**: The logic here is, actually, to parse-in str-value constants first then to parse-in float/int-value constants. Therefore, such arg:
   ```python
        "constants_latex_expression":{"e": np.e,             # exponential constant
                                        "some_value": "e^{-1}*s" # some_value = 1 second / exponential constant
                                        # "s":"s" # time unit; after update on 0711, parsing in units is no longer necessary!
                                        }
   ```
    works, because we first substitude string-values ("s" and "some_value") then substitude "e" to the exponential constant.
2. **Non-Constant Variable Identity Check**. All vars that are not in `constants_latex_expression` will be checked to see whether they are the same in the two equations. If not, return false. **At update on 0711, this step is moved after Constant Variable Substitution. Hence, in the past one needs to parse in unit themselves (like "m":"m" and "s":"s") in `constants_latex_expression`, but this is no longer necessary**.
3. **Equivalent Check by Solving in Random Conditions**. For an equation with $N$ free variables, the big idea (not equal to the exact code) of this step is like:

   ```python
   default_range=(-20.0,20.0)
   eq_trial_num = 0
   ineq_trial_num = 0
   fail_trial_num = 0
   trial_counter = 0
   
   SUCCESS_TRIAL_NUM = 10
   MAX_TRIAL_WHEN_ENOUGH_SUCCESS = 20
   MAX_TRIAL_NUM = 40
   RELATIVE_ERROR_TOLERANCE = 1e-5
   TIME_LIMIT = 0.3 # smaller value, e.g., 0.1, might cause the program to stuck.
   
   while True:
       trial_counter += 1
       target_id = random.randint(0, len(freevars)-1)
   	target_var = freevars[target_id]
       other_vars = []
       for var in freevars:
           if var != target_var:
               var.val = randomsample(default_range)
               other_vars.append(var)
   	try:
           solutions1 = solve(eq1, target_var, other_vars, TIME_LIMIT)
           solutions2 = solve(eq2, target_var, other_vars, TIME_LIMIT)
           assert solutions1.nonempty() and solutions2.nonempty()
           if all_eq(solutions1, solutions2, RELATIVE_ERROR_TOLERANCE):
               eq_trial_num += 1
   		else:
               ineq_trial_num += 1
   	except TimeOutError, EmptySolutionError, OtherErrors as e:
           fail_trial_num += 1
           
           if e == TimeOutError:
               def some_corner_logics_here():
                    WE_DO_NOT_SAMPLE_TARGET_VAR_IN_LATER_ITERATIONS()
                    if NO_VAR_LEFT_CAN_BE_SAMPLED():
                        return False, "No enough vars can be sampled"
               some_corner_logics_here()
       
       success_trial_num = eq_trial_num + ineq_trial_num
       if trial_counter > MAX_TRIAL_WHEN_ENOUGH_SUCCESS and success_trial_num > MIN_SUCCESS_TRIAL_NUM:
           break
       elif trial_counter > MAX_TRIAL_NUM:
           break
       
   if (eq_trial_num) >= min_eq_req and ineq_trial_num == 0:
       return "Equivalent Equations!"
   else:
       return "Not Equivalent Equations, or equivalent equations that we just identify as non equivalent equations because not enough trials made for comparison!"
               
   ```

## 2. Failure Cases Analysis

### 2.0. Program Always terminates thanks to TimeLimit and MAX_TRIAL_NUM

So thankfully it always halts.

### 2.1. False Negatives

You see, there are possibly **false negatives** in these cases,

1. RELATIVE\_ERROR\_TOLERANCE is set to be too small.

   1. Calculation Error. float64 is used by sympy by default, which might lead to relative error of around $1e-10$.
   2. Special Calculation Error. For example, some equations might be solved to somewhere around $1e-6$ relative error, idk why.

   Hence here it is set to $1e-5$.

2. Too many failure cases, for example, all vars time-out. This might include things like this:

   $x^(2.56297805587187) - 0.319381238834767=0$.

   I don't know why this naive simple equation might times out, but it just did.

### 2.2. False Positives

There might be False Positives introduced by these reasons,

1. RELATIVE\_ERROR\_TOLERANCE is set to be too large.

   One may think, $1e-5$ is a small enough tolerance. However, in Physics quantities can be large.

   Take this pair of formula as example,

   ```python
   "m_a = - m_b + \\kg / (3000000000m/s)^2"
   "m_a = - m_b + \\kg / (300000000m/s)^2"
   ```

   We see this result:

   ```txt
   False Only passed 7, ineq 9 trials, failed_trials 0. -g*s**2/(9000000000000000*m**2) + m_{a} + m_{b} COMPARING_WITH (g*s**2 - 90000000000000.0*m**2*(m_{a} + m_{b}))/s**2 with tol=1e-05, n_trials=15, sample_range=(-20, 20), variables=[s, m_{b}, m_{a}, m, g] for is_almost_equivalent
   ```

   It gives the correct answer (they are inequivalent), but we see it passes $7$ trials. In detail,

   ```python
   Trial 7: m | sol1=[-7.291274708608026e-08j, 7.291274708608026e-08j], sol2=[-7.291274708608033e-07j, 7.291274708608033e-07j], all_match=False: relaDiff = [1.6363636363636365] (when sol=0, this is Diff)
           
   ...     
   Trial 8: m_{a} | sol1=[(4.49878818829607+0j)], sol2=[(4.498788188417161+0j)], all_match=True: relaDiff = [2.6916488649111113e-11] (when sol=0, this is Diff)
   ...
   Trial 13: m_{a} | sol1=[(-12.7786498596803+0j)], sol2=[(-12.778649859680959+0j)], all_match=True: relaDiff = [5.157261484226657e-14] (when sol=0, this is Diff)
   ```

   We see trial 8, trial 13 give false positive when they solve for $m_a$. **This is because when they solve for $m_a$, $m_b$ and $kg$ is substituted using random number sampled in $[-20,20]$, hence the difference this error introduces in m_a is very little, way less than 1e-5**, which might cause false positive for $m_a$. Fortunately in this case, when solving for $m$, a difference in the coefficient of $m$ result in large difference so false positive is avoided in this case. **But there are indeed other similar cases where there might be false positive.** In this example, if there are 2 vars, targeting one would lead to FP and another would not, then the $p-value$ of False Positive would be $1/1024=0.1pct$ for $10$ trials in total. However, some other cases might have $p$ values larger than this.

2. To Be Added.

## 3. Performance Analysis

Common equations takes around $0.5s$.

```python
{"rel_latex":"m_a = - m_b + \\kg / (3000000000m/s)^2","answer_latex":"m_a = - m_b + \\kg / (300000000m/s)^2","constants_latex_expression":{}} # 0.5s
```

Equations with $3$ vars time-out takes around $2.7s$.

```python
{"rel_latex":r"m/b *(e^{b/m*x}-1)=V_0 s","answer_latex":r"e^{b /m *x} = 1 + {b V_0}/m*t",
 "constants_latex_expression":{"e": np.e, "t": "1*s", "s": "s"}} # 2.7s
```

(of which m,x,b timed-out)



## 4. Updates supporting units.

The function `whether_rel_latex_correct_with_units_with_only_one_dict_parameter` and `whether_rel_latex_correct_with_units` supports comparison with units. Let's see:

```python
def whether_rel_latex_correct_with_units(rel_latex,answer_latex,
    constants_latex_expression=None,
    strict_comparing_inequalities=False,
    epsilon_for_equal=1e-2,
    tolerable_diff_fraction = TOLERABLE_DIFF_FRACTION,
    tolerable_diff_max = TOLERABLE_DIFF_MAX,
    unit_pattern = r"\\units{(.*?)}",
    whole_unit_pattern = r"(\\units{.*?})",
    units_conversion_dict = {
    "\\km": "1000*m",
    "\\ms": "0.001*s",
    "\\kg": "1000*g",
    },
    unit_notation = [r"\U_{relstr}", r"\U_{ansstr}"],
    **kwargs):
```

This function finds `unit_pattern` in both strs, and substitude them with `U_{relstr}` and `U_{ansstr}`. It then adds "U\_{relstr}" and "U\_{ansstr}" as constants, whose value is the (not-unified) units, to the `constant_latex_expression`. These things are modified as well:

1. Add a `num_constant_change_iter` argument in `def comparing_rel`. This is set to 1 by default, and 2 when there are comparison with units, to support twice-substitution (e.g. U\_{relstr}->kg/s^2->g/s^2).











## 5. Multiprocessing

**This function can be wrapped into multiprocessing** (examples of which can be found at [https://github.com/JingzheShi/CPHOSS_Formula_Comparison](https://github.com/JingzheShi/CPHOSS_Formula_Comparison)).

