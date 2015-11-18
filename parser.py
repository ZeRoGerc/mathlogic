__author__ = 'ZeRoGerc'

import re

is_variable = re.compile("[A-Z][A-Z0-9]*")

def __has_same_shape__(shape_exp, full_exp, def_variables=None):
    """
    :type dict: dictionary
    """
    if def_variables is None:
        def_variables = {}

    if isinstance(shape_exp, Variable):
        if shape_exp.name in def_variables.keys():
            if full_exp == def_variables[shape_exp.name]:
                return True, def_variables
            else:
                return False, def_variables
        else:
            def_variables[shape_exp.name] = full_exp
            return True, def_variables
    elif shape_exp.name != full_exp.name:
        return False, def_variables
    elif shape_exp.name == '!':
        return __has_same_shape__(shape_exp.expression, full_exp.expression, def_variables)
    else:
        is_ok, def_variables = __has_same_shape__(shape_exp.left, full_exp.left, def_variables)
        if not is_ok:
            return False, def_variables
        is_ok, def_variables = __has_same_shape__(shape_exp.right, full_exp.right, def_variables)
        if not is_ok:
            return False, def_variables
        return True, def_variables


def has_same_shape(shape_exp, full_exp):
    is_ok, def_variables = __has_same_shape__(shape_exp, full_exp)
    return is_ok


class Variable:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, Variable):
            return False
        else:
            return self.name == other.name

    def __str__(self):
        return str(self.name)

    def __hash__(self):
        return hash(self.name)


class Nor:
    def __init__(self, expression):
        self.expression = expression
        self.name = '!'

    def __eq__(self, other):
        if not isinstance(other, Nor):
            return False
        else:
            return self.expression == other.expression

    def __str__(self):
        return '!(' + str(self.expression) + ')'

    def __hash__(self):
        return hash((self.name, self.expression))


class Operation:
    def __init__(self, left, right, name):
        self.left = left
        self.right = right
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, Operation):
            return False
        else:
            return self.left == other.left and self.right == other.right and self.name == other.name

    def __str__(self):
        return '(' + str(self.left) + ')' + str(self.name) + '(' + str(self.right) + ')'

    def __hash__(self):
        return hash((self.name, self.left, self.right))

class And(Operation):
    def __init__(self, left, right):
        super(And, self).__init__(left, right, '&')


class Or(Operation):
    def __init__(self, left, right):
        super(Or, self).__init__(left, right, '|')


class Implication(Operation):
    def __init__(self, left, right):
        super(Implication, self).__init__(left, right, '->')


class Parser:
    """
    :type self.main_string: str
    """
    def __init__(self):
        self.main_string = ""
        self.index = 0

    def parse_negation(self):
        matched = is_variable.match(self.main_string, pos=self.index)
        if matched:
            self.index = matched.end()
            temp = matched.group()
            return Variable(temp)
        elif self.main_string[self.index] == '!':
            self.index += 1 # skip !
            return Nor(self.parse_negation())
        else:
            self.index += 1 # skip (
            temp = self.parse_expression()
            self.index += 1 # skip )
            return temp

    def parse_conjunction(self):
        left = self.parse_negation()
        while self.index < len(self.main_string) and self.main_string[self.index] == '&':
            self.index += 1 # skip &
            left = And(left, self.parse_negation())
        return left

    def parse_disjunction(self):
        left = self.parse_conjunction()
        while self.index < len(self.main_string) and self.main_string[self.index] == '|':
            self.index += 1 # skip |
            left = Or(left, self.parse_conjunction())
        return left

    def parse_expression(self):
        left = self.parse_disjunction()
        if self.index < len(self.main_string) and self.main_string[self.index] == '-': # it's implication
            self.index += 2 # skip ->
            temp = Implication(left, self.parse_expression())
            return temp
        else:
            return left

    def parse(self, string):
        self.main_string = string
        self.index = 0
        return self.parse_expression()
