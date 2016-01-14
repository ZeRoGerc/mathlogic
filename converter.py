__author__ = 'ZeRoGerc'

from parser import *


class Converter:
    def __init__(self):
        self.parser = Parser()
        self.axioms = (
            self.parser.parse('A->B->A'),
            self.parser.parse('(A->B)->(A->B->C)->(A->C)'),
            self.parser.parse('A->B->A&B'),
            self.parser.parse('A&B->A'),
            self.parser.parse('A&B->B'),
            self.parser.parse('A->A|B'),
            self.parser.parse('B->A|B'),
            self.parser.parse('(A->C)->(B->C)->(A|B->C)'),
            self.parser.parse('(A->B)->(A->!B)->!A'),
            self.parser.parse('!!A->A')
        )

    def is_axiom(self, expression):
        for axiom in self.axioms:
            if has_same_shape(axiom, expression):
                return True
        return False

    def include(self, expression, list):
        for line in list:
            if expression == line:
                return True
        return False

    def deduction(self, title, proof):
        """
        :param title: string looks like A,B,......C|-D
        :param proof: proof of title
        :return: proof of A,B, ......|-C->D
        """
        proposals = []
        proofed = [] # need this for fast search in M.P.
        result = []


        raw_proposals = title[:(title.find('|-'))].split(',')
        beta = self.parser.parse(title[(title.find('|-') + 2):])
        for raw_expression in raw_proposals:
            object_expression = self.parser.parse(raw_expression)
            proposals.append(object_expression)

        alpha = proposals[-1] # Г, alpha |- beta
        proposals.pop()

        for raw_expression in proof:
            expression = None
            if isinstance(raw_expression, str):
                expression = self.parser.parse(raw_expression)
            else:
                expression = raw_expression

            if (self.include(expression, proposals)) or (self.is_axiom(expression)):
                result.append(expression)
                result.append(Implication(expression, Implication(alpha, expression)))
                result.append(Implication(alpha, expression))
            elif expression == alpha:
                t1 = Implication(alpha, Implication(Implication(alpha, alpha), alpha))
                t2 = Implication(alpha, Implication(alpha, alpha))
                result.append(t1)
                result.append(t2)
                result.append(Implication(t2, Implication(t1, Implication(alpha, alpha))))
                result.append(Implication(t1, Implication(alpha, alpha)))
                result.append(Implication(alpha, alpha))
            else:
                mp_exp1, mp_exp2 = (0, 1)
                already_find = False
                for exp1 in reversed(proofed):
                    if isinstance(exp1, Implication) and exp1.right() == expression:
                        for exp2 in reversed(proofed):
                            if exp2 == exp1.left():
                                already_find = True
                                mp_exp1 = exp2
                                mp_exp2 = exp1
                                break
                    if already_find:
                        break

                t1 = Implication(alpha, mp_exp1)
                t2 = Implication(alpha, Implication(mp_exp1, expression))
                t3 = Implication(alpha, expression)

                result.append(Implication(t1, Implication(t2, t3)))
                result.append(Implication(t2, t3))
                result.append(t3)

            proofed.append(expression)
        return result
