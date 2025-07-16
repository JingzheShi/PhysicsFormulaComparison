EPSILON_FOR_EQUAL = 1e-5
UNIT_PATTERN = r"\\unit{(.*?)}"
WHOLE_UNIT_PATTERN = r"(\\unit{.*?})"
UNITS_CONVERSION_DICT = {
                        "\\km": "1000*m",
                        "\\ms": "0.001*s",
                        "\\kg": "1000*g",
                    }