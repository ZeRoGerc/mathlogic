from converter import *

__author__ = 'ZeRoGerc'

def solve():
    input_file = open('input', 'r')
    output_file = open('output', 'w')

    flag = False
    proof = []
    title = ""

    for line in input_file:
        if line[-1] is '\n':
            line = line[:-1]
        if not flag:
            title = line
            flag = True
        else:
            proof.append(line)

    # format first line
    proposals = title[:(title.find('|-'))].split(',')
    alpha = proposals[-1] # Г, alpha |- beta
    beta = title[(title.find('|-') + 2):]
    proposals.pop()
    output_file.write(','.join(string for string in proposals))
    output_file.write('|-')
    output_file.write(alpha + '->' + beta + '\n')

    converter = Converter()
    result = converter.deduction(title, proof)

    for line in result:
        output_file.write(str(line) + '\n')


solve()