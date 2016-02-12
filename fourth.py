__author__ = 'ZeRoGerc'

from expressions import *
import formal_parser
import parser
import checkers
from converters import FormalConverter


def solve():
    import time
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

    checker = checkers.FormalChecker()
    proof = checker.check(title, proof)
    if proof[0]:
        print("correct")
        if proof[2] is None:
            output_file.write(title + '\n')
            for temp in proof[1]:
                output_file.write(str(temp[0]) + '\n')
        else:
            d = title.find('|-')
            i = d - 1
            while i > 0 and title[i] != ',':
                i -= 1
            if i == 0:
                title = '|-(' + title[:d] + ')->' + title[(d + 2):]
            else:
                title = title[:i] + '|-' + title[i + 1:d] + '->' + title[(d + 2):]

            output_file.write(title + '\n')
            c = FormalConverter()
            converted = c.get_converted(proof[1], proof[2])
            for line in converted:
                output_file.write(line + '\n')
    else:
        output_file.write(proof[1])

    t2 = time.time()

    print(t2 - t1)


p = formal_parser.Parser()


# input_file = open('proofs/exist_quantifier_rule.proof', 'r')
input_file = open('logic2014/tests/HW4/incorrect11.in', 'r')
# input_file = open('input', 'r')
output_file = open('output', 'w')
solve()