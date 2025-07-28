import numpy as np
EPSILON_FOR_EQUAL = 1e-5
UNIT_PATTERN = r"\\unit{(.*?)}"
WHOLE_UNIT_PATTERN = r"(\\unit{.*?})"
UNITS_CONVERSION_DICT = {
                        "\\km": "1000*m",
                        "\\ms": "0.001*s",
                        "\\kg": "1000*g",
                        "\\Hz": "1/s",
                        "N": "kg*m/s^2",
                        "J": "kg*m^2/s^2",
                        "W": "kg*m^2/s^3",
                        "\\Pa": "kg/(m*s^2)",
                        "V": "kg*m^2/(s^3*A)",
                        "C": "A*s",
                        "F": "s^4*A^2/(kg*m^2)",
                        "\\Ohm": "kg*m^2/(s^3*A^2)",
                    }
DEFAULT_UNIVERSE_CONSTANTS = {
    "e": np.e,
    "\\pi": np.pi,
    "c": "299792458*m/s",  # Speed of light in vacuum
}


# default epsilon_for_equal = EPSILON_FOR_EQUAL, can be modified by specifying this hyperparameter in questions_config.json.
# default unit_pattern = UNIT_PATTERN, can be modified by specifying this hyperparameter in questions_config.json.
# default whole_unit_pattern = WHOLE_UNIT_PATTERN, can be modified by specifying this hyperparameter in questions_config.json.
# default units_conversion_dict = UNITS_CONVERSION_DICT, can be modified by specifying this hyperparameter in questions_config.json.