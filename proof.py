__author__ = 'ZeRoGerc'

from parser import *
import copy


def define_var(expression, def_a, def_b):
    if isinstance(expression, Variable):
        if expression.name is 'A':
            return def_a
        else:
            return def_b

    if isinstance(expression, Unary):
        return Nor(define_var(expression.expression(), def_a, def_b))

    if isinstance(expression, Binary):
        left = define_var(expression.left(), def_a, def_b)
        right = define_var(expression.right(), def_a, def_b)

        if isinstance(expression, And):
            return And(left, right)
        elif isinstance(expression, Or):
            return Or(left, right)
        else:
            return Implication(left, right)


class Proof:
    def __init__(self, str_proof, var_amount):
        self.proof = []
        self.var_amount = var_amount
        self.parser = Parser()
        for line in str_proof:
            self.proof.append(self.parser.parse(line))

    def get_def_proof(self, def_a, def_b=None):
        if (def_b is None) and (self.var_amount == 2):
            print('Check get_def_proof!!!')

        result = copy.deepcopy(self)

        for i in range(0, len(self.proof)):
            result.proof[i] = define_var(result.proof[i], def_a, def_b)

        return result
