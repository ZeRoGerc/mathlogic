__author__ = 'ZeRoGerc'

from parser import *
from constructor import Constructor


def define_variables(exp, variables):
    """
    :return: map variables changed to proper define of variables:
        for example A:1 B:0 C:2
    """
    if isinstance(exp, Variable):
        if not(exp.name in variables):
            variables[exp.name] = len(variables)
    elif isinstance(exp, Unary):
        define_variables(exp.expression(), variables)
    else:
        define_variables(exp.left(), variables)
        define_variables(exp.right(), variables)


def next_mask(mask):
    id = 0

    while id < len(mask):
        if mask[id] == 0:
            mask[id] = 1
            return mask
        else:
            mask[id] = 0
        id += 1
    return None


def check(mask, exp, variables):
    if isinstance(exp, Variable):
        return mask[variables[exp.name]]
    elif isinstance(exp, Nor):
        return not check(mask, exp.expression(), variables)
    elif isinstance(exp, And):
        return check(mask, exp.left(), variables) and check(mask, exp.right(), variables)
    elif isinstance(exp, Or):
        return check(mask, exp.left(), variables) or check(mask, exp.right(), variables)
    else:
        if not check(mask, exp.left(), variables):
            return 1
        else:
            return check(mask, exp.right(), variables)


def formatted(mask, variables):
    """
    :param mask: mask of variables that indicates which variables are truth and which are false
    :param variables: map of defined variables
    :return: formatted output
    """
    output = []
    for (key, value) in variables.items():
        if mask[value]:
            output.append(str(key) + '=И')
        else:
            output.append(str(key) + '=Л')
    return 'Высказывание ложно при ' + ','.join(output)


def get_proof(exp):
    pass


def solve():
    input_file = open('input', 'r')
    output_file = open('output', 'w')

    parser = Parser()
    str_expression = input_file.read()
    expression = parser.parse(str_expression)

    variables = {}
    define_variables(expression, variables)

    mask = [0] * len(variables)
    while not mask is None:
        if not check(mask, expression, variables):
            output_file.write(formatted(mask, variables))
            break
        mask = next_mask(mask)

    if mask is None:
        constructor = Constructor()
        proof = constructor.get_proof(expression, variables)

        for exp in proof:
            output_file.write(str(exp) + '\n')


solve()