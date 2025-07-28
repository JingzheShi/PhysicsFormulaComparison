import re
DEBUGGING=False
FUNCTION_FOR_ADDING_TIMES_BEFORE_NON_FUNCTIONAL_BRACKETS = True # must be true, just use a if so you can fold it.
if FUNCTION_FOR_ADDING_TIMES_BEFORE_NON_FUNCTIONAL_BRACKETS:
    import regex                            # pip install regex

    EXCLUDED = {'frac', 'sqrt', 'times', 'cdot'}

    # ------------------------------------------------------------
    # 1  Pattern – no more “++” inside the char class
    # ------------------------------------------------------------
    PATTERN = regex.compile(
        r'''
        (\\?[a-zA-Z]\w*)\s*        # 1 – variable or \command
        \(                         #    opening (
            (                      # 2 – balanced contents
                (?:
                    [^()]          #    any non‑paren char  ← now back‑trackable
                | (?R)           #    or another balanced (…)  (recursion)
                )*
            )
        \)                         #    closing )
        ''',
        regex.VERBOSE,
    )

    # ------------------------------------------------------------
    # 2  Helpers
    # ------------------------------------------------------------
    def is_valid_var(v: str) -> bool:
        return v.lstrip('\\') not in EXCLUDED


    def repl(m: regex.Match) -> str:
        var, inner = m.group(1), m.group(2)

        # If the "variable" is actually an excluded command (e.g. \frac),
        # just keep searching inside its parentheses.
        if not is_valid_var(var):
            return f"{var}({regex.sub(PATTERN, repl, inner)})"

        # Only insert × if arithmetic symbols are present inside ( … )
        if regex.search(r'[\+\-\*/]|\\frac|\\cdot|\\times', inner):
            return f"{var} \\times ({inner})"

        return m.group(0)           # leave untouched


    def add_times_before_NonFunctionalbrackets(expr: str) -> str:
        """Keep applying the substitution until nothing changes."""
        prev = None
        counter = 0
        while expr != prev:
            counter += 1
            prev = expr
            expr = regex.sub(PATTERN, repl, expr)
            if counter > 100:
                break
        return expr
else:
    def add_times_before_NonFunctionalbrackets(expr: str) -> str:
        return
    
# -------------------------------------------------------------------
# Debug logging
# -------------------------------------------------------------------
def _log_debug(filepath: str, expr: str):
    """Append expr to filepath if DEBUGGING is True."""
    if not DEBUGGING:
        return
    with open(filepath, "a") as f:
        f.write(expr + "\n")

# -------------------------------------------------------------------
# 1. Remove \left and \right wrappers
# -------------------------------------------------------------------
def _remove_left_right(expr: str) -> str:
    # Strip \left and \right (any amount of whitespace after)
    expr = re.sub(r'\\left\s*', '', expr)
    expr = re.sub(r'\\right\s*', '', expr)
    return expr

# -------------------------------------------------------------------
# 2. Collapse line breaks and hard spaces
# -------------------------------------------------------------------
def _remove_line_breaks(expr: str) -> str:
    # (\\\\) is a LaTeX linebreak, \newline or explicit " \ "  
    return re.sub(r'(\\\\|\\newline|\\\s)', ' ', expr)

# -------------------------------------------------------------------
# 3. Remove spacing commands and tildes
# -------------------------------------------------------------------
def _remove_spacings_and_tildes(expr: str) -> str:
    # Removes \, \; \: \!  and multiple spaces, then strips '~'
    expr = re.sub(r'\\[ ,;:!]', '', expr)
    expr = expr.replace('~', '')
    # collapse any remaining multi‑spaces
    return re.sub(r'\s+', ' ', expr).strip()

# -------------------------------------------------------------------
# 4. Strip common math environments
# -------------------------------------------------------------------
def _remove_environments(expr: str) -> str:
    # Remove \begin{...} and \end{...} for simple env names
    expr = re.sub(r'\\begin\{[a-zA-Z*]+\}', '', expr)
    expr = re.sub(r'\\end\{[a-zA-Z*]+\}',   '', expr)
    return expr

# -------------------------------------------------------------------
# 5. Flatten text macros (\mathrm, \operatorname, etc.)
# -------------------------------------------------------------------
def _flatten_text_macros(expr: str) -> str:
    # \mathrm{foo} → foo
    expr = re.sub(r'\\mathrm\{([^}]*)\}',        r'\1', expr)
    expr = re.sub(r'\\operatorname\{([^}]*)\}',  r'\1', expr)
    expr = re.sub(r'\\text\{([^}]*)\}',          r'\1', expr)
    return expr

# -------------------------------------------------------------------
# 6. Strip trailing punctuation
# -------------------------------------------------------------------
def _strip_trailing_punct(expr: str) -> str:
    # If the end is not a digit or ')', drop trailing comma or period
    expr = re.sub(r'([^\d)])[,\.]\s*$', r'\1', expr)
    return expr.strip()

# -------------------------------------------------------------------
# 7. Replace common LaTeX constructs
# -------------------------------------------------------------------
def _replace_common_patterns(expr: str) -> str:
    # Change \approx to =
    expr = re.sub(r'\\approx', '=', expr)
    # \ddot{X} → \ddot_X
    expr = re.sub(r'\\ddot\{([^\{\}]+)\}', r'\\ddot_\1', expr)
    return expr

# -------------------------------------------------------------------
# Main entry — unchanged
# -------------------------------------------------------------------
def simplify_latex_expr(expr: str) -> str:
    # input logging
    _log_debug("org_expr.txt", expr)

    expr = _remove_left_right(expr)
    expr = _remove_line_breaks(expr)
    expr = _remove_spacings_and_tildes(expr)
    expr = _remove_environments(expr)
    expr = _flatten_text_macros(expr)
    expr = _strip_trailing_punct(expr)
    expr = _replace_common_patterns(expr)

    # finally, insert explicit times “×”
    expr = add_times_before_NonFunctionalbrackets(expr)

    # output logging
    _log_debug("ex_expr.txt", expr)
    return expr


if __name__ == "__main__":
    # 测试不同的表达式
    test_exprs = [
        r'a(b+c)',         # 普通变量后跟括号 - 应该匹配
        r'\alpha(x+y)',    # LaTeX符号后跟括号 - 应该匹配
        r'\frac(a+b)',     # \frac后跟括号 - 不应该匹配
        r'\sqrt(x+y)',     # \sqrt后跟括号 - 不应该匹配
        r'm(n)',           # 普通变量后跟括号但内部没有计算符号 - 不应该匹配
        r'\frac(a+b) (c+d)', # 复杂表达式 - 第二部分应该匹配，第一部分不应该
        r'E_1 = \frac{1}{2}m \left(\frac{e^2}{4\pi\varepsilon_0 m r_0}\right) - \frac{e^2}{4\pi\varepsilon_0 r_0}',
        r'E_2 = \frac{1}{2}m \left(\frac{2e^2}{4\pi\varepsilon_0 m r_0}\right) - \frac{2e^2}{4\pi\varepsilon_0 r_0}',
        r'r_{min} = a(1 - e)',
        r'r_{max} = a(1 + e)',
        r'\Delta E = \frac{1}{2}\left(v_J^2 + v_{\text{rel}}^2\right) - \frac{1}{2}v_i^2',
        r'\Delta E = \frac{1}{2}\left(v_J^2 + v_i^2 + v_J^2\right) - \frac{1}{2}v_i^2',
        r'\frac{G m_e m_m}{a^2} = \left( \frac{m_e m_m}{m_e + m_m} \right)a \omega^2',
        r'G(m_e + m_m) = \frac{4\pi^2 a^3}{T^2}',
        r'a = a_1 - \frac{R_e (\sin \alpha_2 - \sin \alpha_1)}{\alpha_2 - \alpha_1 - \lambda_2 + \lambda_1}',
        r'\frac{G m_e m_m}{a^2} = ( \frac{m_e m_m}{m_e + m_m} )a \omega^2',
        r'G \cdot (m_e + m_m) = \frac{4\pi^2 a^3}{T^2}',
        r'a = a_1 - \frac{R_e \cdot (\sin \alpha_2 - \sin \alpha_1)}{\alpha_2 - \alpha_1 - \lambda_2 + \lambda_1}',
        r'F = m_m \left(\frac{2\pi}{T}\right)^2 a',
        r'G \frac{m_e m_m}{a^2} = m_m \left(\frac{2\pi}{T}\right)^2 a',
        r'a = \frac{a_1 R_e (\sin \alpha_2 \cos \lambda_1 - \sin \alpha_1 \cos \lambda_2)}{\sin \alpha_1 \sin \alpha_2 (\cos \lambda_1 - \cos \lambda_2)}',
        r'r = \frac{mv^2}{q(k_e + vB)}',
        r'$$F = m ( \ddot{r} - r \dot{\theta}^2 )$$',
        r'$$V(r) = - \int_{\infty}^{r} F(r) dr$$',
        r'$$V(r) = \int_{\infty}^r \frac{m h^2}{r^3} dr$$',
        r'$$V(r) = \left[ -\frac{m h^2}{2 r^2} \right]_{\infty}^{r}$$',
        r'$$V(r) = -\frac{m h^2}{2 r^2}$$',
        r'F = m \cdot ( \ddot_{r} - r \dot{\theta}^2 )',
        r'0 = m \cdot ( r \ddot_{\theta} + 2 \dot{r} \dot{\theta} )',
        r'\frac{G(a+b)}{c+d}'
        r'$$0 = m ( r \ddot{\theta} + 2 G(a(b+c(d)))m(\frac{q}{b})\dot{r} \dot{\theta} )$$',
    ]

    for expr in test_exprs:
        print(f"\n测试: {expr}")
        result = simplify_latex_expr(expr)
        # result = re.sub(pattern, repl, expr)
        # result = re.sub(pattern, repl, result)
        print(f"结果: {result}")