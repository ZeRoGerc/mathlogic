
from expressions import *
import formal_parser
import copy


def convert_axiom(expression: Expression, alpha: Expression):
    result = [
        str(expression),
        str(Implication(expression, Implication(alpha, expression))),
        str(Implication(alpha, expression))
    ]
    return result


def convert_alpha(alpha: Expression):
    t1 = Implication(alpha, Implication(Implication(alpha, alpha), alpha))
    t2 = Implication(alpha, Implication(alpha, alpha))
    result = [
        str(t1),
        str(t2),
        str(Implication(t2, Implication(t1, Implication(alpha, alpha)))),
        str(Implication(t1, Implication(alpha, alpha))),
        str(Implication(alpha, alpha))
    ]
    return result


def convert_modus_ponens(expression: Expression, left_mp_exp: Expression, alpha: Expression):
    t1 = Implication(alpha, left_mp_exp)
    t2 = Implication(alpha, Implication(left_mp_exp, expression))
    t3 = Implication(alpha, expression)

    result = [
        str(Implication(t1, Implication(t2, t3))),
        str(Implication(t2, t3)),
        str(t3)
    ]
    return result


class FormalConverter:
    def __init__(self):
        self.converted = []
        self.parser = formal_parser.Parser()
        self.uni_proof = self.__read_proof__(open('proofs/uni_quantifier_rule.proof', 'r'))
        self.exist_proof = self.__read_proof__(open('proofs/exist_quantifier_rule.proof', 'r'))


    def __read_proof__(self, input_file):
        result = []
        for line in input_file:
            result.append(self.parser.parse(line))

        return result

    def __exp_subst__(self, exp: Expression, a: Expression, b: Expression, c: Expression, x: Variable):
        object = type(exp)
        if isinstance(exp, Quantifier):
            new_exp = self.__exp_subst__(exp.expression, a, b, c, x)
            return object(x, new_exp)
        elif isinstance(exp, Predicate) and len(exp.args) == 0:
            if exp.name == 'A':
                return copy.deepcopy(a)
            elif exp.name == 'B':
                return copy.deepcopy(b)
            elif exp.name == 'C':
                return copy.deepcopy(c)
            else:
                print("exp_subst fails")
        elif isinstance(exp, MultiOperation):
            new_args = list(exp.args)
            for i in range(0, len(exp.args)):
                new_args[i] = self.__exp_subst__(exp.args[i], a, b, c, x)

            if isinstance(exp, Unary):
                return object(new_args[0])
            elif isinstance(exp, Binary) or isinstance(exp, EqualPredicate):
                return object(new_args[0], new_args[1])
            else:
                return object(exp.name, new_args)
        else:
            print("exp_subst fails")

        return exp

    def __substitute__(self, proof: list, a: Expression, b: Expression, c: Expression, x: Variable):
        result = []
        for exp in proof:
            result.append(str(self.__exp_subst__(exp, a, b, c, x)))
        return result

    def convert_uqr(self, expression: Implication, alpha: Expression):
        right = expression.right()
        assert isinstance(right, UniQuantifier)

        return self.__substitute__(self.uni_proof, alpha, expression.left(), right.expression, right.variable)

    def convert_eqr(self, expression: Implication, alpha: Expression):
        left = expression.left()
        assert isinstance(left, ExistQuantifier)

        return self.__substitute__(self.exist_proof, alpha, left.expression, expression.right(), left.variable)

    def get_converted(self, proof: list, alpha: Expression):
        self.converted = []

        for temp in proof:
            if temp[1] == "axiom":
                self.converted += convert_axiom(temp[0], alpha)
            elif temp[1] == "alpha":
                self.converted += convert_alpha(alpha)
            elif temp[1] == "MP":
                self.converted += convert_modus_ponens(temp[0], temp[2], alpha)
            elif temp[1] == "UQR":
                self.converted += self.convert_uqr(temp[0], alpha)
            elif temp[1] == "EQR":
                self.converted += self.convert_eqr(temp[0], alpha)

        return self.converted