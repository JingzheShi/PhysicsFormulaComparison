EPSILON_FOR_EQUAL = 1e-5
UNIT_PATTERN = r"\\unit{(.*?)}"
WHOLE_UNIT_PATTERN = r"(\\unit{.*?})"
UNITS_CONVERSION_DICT = {
                        "\\km": "1000*m",
                        "\\ms": "0.001*s",
                        "\\kg": "1000*g",
                    }

# default epsilon_for_equal = EPSILON_FOR_EQUAL, can be modified by specifying this hyperparameter in questions_config.json.
# default unit_pattern = UNIT_PATTERN, can be modified by specifying this hyperparameter in questions_config.json.
# default whole_unit_pattern = WHOLE_UNIT_PATTERN, can be modified by specifying this hyperparameter in questions_config.json.
# default units_conversion_dict = UNITS_CONVERSION_DICT, can be modified by specifying this hyperparameter in questions_config.json.