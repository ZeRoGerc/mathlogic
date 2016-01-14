__author__ = 'ZeRoGerc'

import formal_parser
import parser
from expressions import *


class Error:
    not_free = 1
    is_free = 2
    quantifier_rule = 3
    unspecified = 4


class FormalChecker:
    def __init__(self):
        self.proof = []  # expressions that we already proofed
        self.proofed = set()  # same as proofed but has faster access
        self.proofed_implications = [] # for fast implementing of modus ponens
        self.proposals = []
        self.banned_vars = set()  # variables included in alpha as free vars

        self.parser = formal_parser.Parser()
        temp_parser = parser.Parser()
        self.prop_axioms = (
            temp_parser.parse('A->B->A'),
            temp_parser.parse('(A->B)->(A->B->C)->(A->C)'),
            temp_parser.parse('A->B->A&B'),
            temp_parser.parse('A&B->A'),
            temp_parser.parse('A&B->B'),
            temp_parser.parse('A->A|B'),
            temp_parser.parse('B->A|B'),
            temp_parser.parse('(A->C)->(B->C)->(A|B->C)'),
            temp_parser.parse('(A->B)->(A->!B)->!A'),
            temp_parser.parse('!!A->A'),
        )
        self.formal_axioms = (
            self.parser.parse("a=b->a'=b'"),
            self.parser.parse("a=b->a=c->b=c"),
            self.parser.parse("a'=b'->a=b"),
            self.parser.parse("!(a'=0)"),
            self.parser.parse("a+b'=(a+b)'"),
            self.parser.parse("a+0=a"),
            self.parser.parse("a*0=0"),
            self.parser.parse("a*b'=a*b+a"),
        )

    def __is_proposal__(self, expression: Expression):
        for proposal in self.proposals:
            if expression == proposal:
                return "ok"
        return None

    def __is_prop_axiom__(self, expression: Expression):
        for axiom in self.prop_axioms:
            if parser.has_same_shape(axiom, expression):
                return "ok"
        return None

    def __is_formal_axiom__(self, expression: Expression):
        for axiom in self.formal_axioms:
            if axiom == expression:
                return "ok"
        return None

    def __get_formatted_error__(self, error_type: int, args: tuple):
        if error_type is Error.not_free:
            return "терм " + str(args[0]) + " не свободен для подстановки в формулу " + str(args[1]) + \
                   " вместо переменной " + str(args[2])
        elif error_type is Error.is_free:
            return "переменная " + str(args[0]) + " входит свободно в формулу " + str(args[1])
        elif error_type is Error.quantifier_rule:
            return "используется " + str(args[0]) + " c квантором по переменной " + str(args[1]) + \
                   ", входящей свободно в допущение " + str(self.proposals[-1])
        else:
            return "неизвестная ошибка"

    def __is_quantifier_axiom__(self, expression: Expression):
        if not isinstance(expression, Implication):
            return None

        left = expression.left()
        right = expression.right()

        message = None
        if isinstance(left, UniQuantifier):  # check @x(v)->(v[x:=T])
            if left.variable.name in self.banned_vars:
                message = self.__get_formatted_error__(Error.quantifier_rule, ("схема аксиом", left.variable.name))
            else:
                is_ok, replace = formal_parser.is_substitution(left.expression, right, left.variable)
                if is_ok:
                    return "ok"
                elif replace is not None:
                    message = self.__get_formatted_error__(Error.not_free, (replace, left.expression, left.variable))

        if isinstance(right, ExistQuantifier):  # check (v[x:=T])->?x(v)
            if right.variable.name in self.banned_vars:
                message = self.__get_formatted_error__(Error.quantifier_rule, ("схема аксиом", right.variable.name))
            else:
                is_ok, replace = formal_parser.is_substitution(right.expression, left, right.variable)
                if is_ok:
                    return "ok"
                elif replace is not None:
                    message = self.__get_formatted_error__(Error.not_free, (replace, right.expression, right.variable))

        if isinstance(left, And):  # check f[x:=0]&@x(f->f[x:=x'])->f
            if isinstance(left.right(), Quantifier):
                variable = left.right().variable

                # f->f[x:=x']
                impl = left.right().expression
                if not isinstance(impl, Implication):
                    return message

                # f
                if not impl.left() == right:
                    return message

                # check if f contains x as free variable
                free = formal_parser.get_free_vars(right)
                if variable.name not in free:
                    return message

                # f[x:=0]
                is_ok, replace = formal_parser.is_substitution(right, left.left(), variable)
                if not (is_ok and replace == Variable('0')):
                    return message

                # f[x:=x']
                is_ok, replace = formal_parser.is_substitution(right, impl.right(), variable)
                if is_ok and (replace == Inc(variable)):
                    if variable in self.banned_vars:
                        message = self.__get_formatted_error__(Error.quantifier_rule, ("схема аксиом", variable))
                    else:
                        return "ok"

        return message

    def __check_derivation_rule__(self, expression: Expression):
        # Modus Ponens
        for impl in reversed(self.proofed_implications):
            if (impl.right() == expression) and (impl.left() in self.proofed):
                self.add_proofed(expression, "MP", impl.left())
                return "ok"

        message = None
        if isinstance(expression, Implication):
            left = expression.left()
            right = expression.right()

            # v->u ---> v->@x(u) if x is not free in v
            if isinstance(right, UniQuantifier):
                if Implication(left, right.expression) in self.proofed:
                    free = formal_parser.get_free_vars(left)
                    if right.variable.name not in free:
                        if right.variable.name in self.banned_vars:
                            message = self.__get_formatted_error__(Error.quantifier_rule, ("правило", right.variable.name))
                        else:
                            self.add_proofed(expression, "UQR")
                            return "ok"
                    else:
                        message = self.__get_formatted_error__(Error.is_free, (right.variable.name, left))

            # v->u ---> ?x(v)->u if x is not free in u
            if isinstance(left, ExistQuantifier):
                if Implication(left.expression, right) in self.proofed:
                    free = formal_parser.get_free_vars(right)
                    if left.variable.name not in free:
                        if left.variable.name in self.banned_vars:
                            message = self.__get_formatted_error__(Error.quantifier_rule, ("правило", left.variable.name))
                        else:
                            self.add_proofed(expression, "EQR")
                            return "ok"
                    else:
                        message = self.__get_formatted_error__(Error.is_free, (left.variable.name, right))

        return message

    def add_proofed(self, expression: Expression, annotation: str, additional=None):
        self.proof.append((expression, annotation, additional))
        self.proofed.add(expression)
        if isinstance(expression, Implication):
            self.proofed_implications.append(expression)

    def check(self, title: str, proof: list):
        self.proof = []  # expressions that we already proofed
        self.proofed = set()  # same as proofed but has faster access
        self.proofed_implications = [] # for fast implemeting of
        self.proposals = []

        # fill proposals
        x = title.find('|-')
        if x != -1:
            title = title[:x]
            index = 0
            while index < len(title):
                expression, index = self.parser.part_parse(title, index)
                self.proposals.append(expression)

                index += 1  # skip ,

        alpha = None
        if len(self.proposals) != 0:
            self.banned_vars = formal_parser.get_free_vars(self.proposals[-1])
            alpha = self.proposals[-1]

        number = 0
        for raw_exp in proof:
            expression = self.parser.parse(raw_exp)
            number += 1
            message = None

            temp = self.__is_proposal__(expression)
            if temp == "ok":
                if expression == alpha:
                    self.add_proofed(expression, "alpha")
                else:
                    self.add_proofed(expression, "axiom")
                continue

            temp = self.__is_prop_axiom__(expression)
            if temp == "ok":
                self.add_proofed(expression, "axiom")
                continue

            temp = self.__is_formal_axiom__(expression)
            if temp == "ok":
                self.add_proofed(expression, "axiom")
                continue

            temp = self.__is_quantifier_axiom__(expression)
            if temp == "ok":
                self.add_proofed(expression, "axiom")
                continue
            elif temp is not None:
                message = temp

            temp = self.__check_derivation_rule__(expression)
            if temp != "ok":
                if temp is not None:
                    message = temp

                if message is None:
                    return False, "Вывод некорректен начиная с формулы номер " + str(number) + ' [неизвестная ошибка]'
                else:
                    return False, "Вывод некорректен начиная с формулы номер " + str(number) + ' [' + str(message) + ']'

        return True, self.proof, alpha
