__author__ = 'ZeRoGerc'

from parser import *
import time


class PropositionalChecker:
    def __init__(self):
        self.parser = Parser()
        self.axioms = (
            (self.parser.parse('A->B->A'), 1),
            (self.parser.parse('(A->B)->(A->B->C)->(A->C)'), 2),
            (self.parser.parse('A->B->A&B'), 3),
            (self.parser.parse('A&B->A'), 4),
            (self.parser.parse('A&B->B'), 5),
            (self.parser.parse('A->A|B'), 6),
            (self.parser.parse('B->A|B'), 7),
            (self.parser.parse('(A->C)->(B->C)->(A|B->C)'), 8),
            (self.parser.parse('(A->B)->(A->!B)->!A'), 9),
            (self.parser.parse('!!A->A'), 10),
        )

    @staticmethod
    def get_formatted(line: tuple):
        result = ""
        result += '(' + str(line[0]) + ') '
        result += str(line[1]) + ' ('
        result += str(line[2])
        if len(line) > 3:
            result += ' ' + str(line[3])
        if len(line) > 4:
            result += ', ' + str(line[4])
        result += ')\n'
        return result

    def check(self, string, proof):
        """
        string it's a title
        :type proof list
        :type string: str
        """
        # alpha_str = string[(string.find('|-') + 2):] # expression that we need to proof
        # alpha_exp, variables  = self.parser.parse(alpha_str, variables)

        proposals = []
        number = 1 # number that we need in formatted output
        # fill proposals
        temp = string[:(string.find('|-'))].split(',')
        if temp[0] != '':
            for expression in temp:
                obj_exp = self.parser.parse(expression)
                proposals.append((obj_exp, number))
                number += 1

        proofed = [] # expressions that we already proofed
        proofed_dict = {} # same as proofed but has faster access
        number = 1
        # proof.append(alpha_str) # we append alpha to proof to see if it's derivable from proof
        for str_exp in proof:
            if len(str_exp) == 0:
                break
            expression = self.parser.parse(str_exp) # get parsed object by string
            accept_expression = False

            # Check if it's axiom
            for axiom, idx in self.axioms:
                if has_same_shape(axiom, expression):
                    accept_expression = True
                    output_file.write(PropositionalChecker.get_formatted((number, str_exp, 'Сх. акс.', idx)))

            if not accept_expression:
                # Check if it's proposal
                for prop, idx in proposals:
                    if expression == prop:
                        accept_expression = True
                        output_file.write(PropositionalChecker.get_formatted((number, str_exp, 'Предп.', idx)))
                        break

            if not accept_expression:
                # Check if it's the result of Modus Ponens
                for prf, idx1 in reversed(proofed):
                    if isinstance(prf, Implication) and prf.right() == expression and prf.left() in proofed_dict:
                            accept_expression = True
                            output_file.write(PropositionalChecker.get_formatted((number, str_exp, 'M.P.', proofed_dict[prf.left()], idx1)))
                            break

            if accept_expression:
                proofed_dict[expression] = number
                proofed.append((expression, number))
            else:
                output_file.write(PropositionalChecker.get_formatted((number, str_exp, 'Не доказано')))

            number += 1


def solve():
    t1 = time.time()

    flag = False
    proof = []
    title = ""

    for line in input_file:
        if not flag:
                title = line[:-1]
                flag = True
        else:
            if line[-1] == '\n':
                proof.append(line[:-1])
            else:
                proof.append(line)

    checker = PropositionalChecker()
    checker.check(title, proof)

    t2 = time.time()

    print(t2 - t1)



# input_file = open('logic2014/tests/HW1/good6.in', 'r')
input_file = open('output', 'r')
output_file = open('input', 'w')
solve()