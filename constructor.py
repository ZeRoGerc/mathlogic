__author__ = 'ZeRoGerc'

from parser import *
from converter import *
from proof import Proof
from converter import Converter
import os
import copy

def get_a_not_not_a_proof(alpha) :
    proof = []
    from_a = Implication(alpha, Nor(alpha))
    from_not_a = Implication(Nor(alpha), alpha)

    proof.append(alpha)
    proof.append(Implication(alpha, from_not_a)) # a->!a->a
    proof.append(from_not_a)
    proof.append( # (!a->a)->(!a->a->!a)->(!a->!a)
        Implication(
            from_not_a,
            Implication(
                Implication(Nor(alpha), from_a),
                Implication(Nor(alpha), Nor(alpha))
            )
        )
    )
    proof.append( # (!a->a->!a)->(!a->!a)
        Implication(
                Implication(Nor(alpha), from_a),
                Implication(Nor(alpha), Nor(alpha))
            )
    )

    proof.append(Implication(Nor(alpha), from_a)) # !a->a->!a
    proof.append(Implication(Nor(alpha), Nor(alpha))) # !a->!a
    proof.append( # (!a->a)->(!a->!a)->!!a
        Implication(
            from_not_a,
            Implication(
                Implication(Nor(alpha), Nor(alpha)),
                Nor(Nor(alpha))
            )
        )
    )
    proof.append( #(!a->!a)->!!a
        Implication(
                Implication(Nor(alpha), Nor(alpha)),
                Nor(Nor(alpha))
            )
    )
    proof.append(Nor(Nor(alpha))) #!!a

    return proof


def construct_atomic_proof(input_name):
    """
    :type input_name: str
    """
    str_proof = []
    input_file = open(input_name)
    for line in input_file:
        if len(line) > 1:
            if line[-1] is '\n':
                str_proof.append(line[:-1])
            else:
                str_proof.append(line)

    amount_var = 1
    if input_name.find('b') != -1:
        amount_var = 2

    return Proof(str_proof, amount_var)


def next_mask(mask):
    id = 0
    new_mask = []
    for c in mask:
        new_mask.append(c)
    while id < len(mask):
        if mask[id] == 0:
            new_mask[id] = 1
            return tuple(new_mask)
        else:
            new_mask[id] = 0
        id += 1

    return None

def get_title(variables, mask, expression):
    """
    :type variables: dict
    :return:
    """
    result = []
    for cur_id in range(0, len(mask)):
        for var, idx in variables.items():
            if idx == cur_id:
                if mask[idx]:
                    result.append(str(var))
                else:
                    result.append('!' + str(var))

    result = ','.join(result)

    result = result + '|-' + str(expression)
    return result


class Constructor:
    def __init__(self):
        self.parser = Parser()
        self.converter = Converter()

        self.atomic_proofs = {}
        parent_dir = os.getcwd()

        self.atomic_proofs['and'] = {}
        self.atomic_proofs['and'][False] = {}
        self.atomic_proofs['and'][True] = {}
        os.chdir(parent_dir + '/proofs/and')

        self.atomic_proofs['and'][False][False] = (False, construct_atomic_proof('nanb.proof'))
        self.atomic_proofs['and'][False][True] = (False, construct_atomic_proof('nab.proof'))
        self.atomic_proofs['and'][True][False] = (False, construct_atomic_proof('anb.proof'))
        self.atomic_proofs['and'][True][True] = (True, construct_atomic_proof('ab.proof'))

        self.atomic_proofs['cons'] = {}
        self.atomic_proofs['cons'][False] = {}
        self.atomic_proofs['cons'][True] = {}
        os.chdir(parent_dir + '/proofs/cons')

        self.atomic_proofs['cons'][False][False] = (True, construct_atomic_proof('nanb.proof'))
        self.atomic_proofs['cons'][False][True] = (True, construct_atomic_proof('nab.proof'))
        self.atomic_proofs['cons'][True][False] = (False, construct_atomic_proof('anb.proof'))
        self.atomic_proofs['cons'][True][True] = (True, construct_atomic_proof('ab.proof'))

        self.atomic_proofs['or'] = {}
        self.atomic_proofs['or'][False] = {}
        self.atomic_proofs['or'][True] = {}
        os.chdir(parent_dir + '/proofs/or')

        self.atomic_proofs['or'][False][False] = (False, construct_atomic_proof('nanb.proof'))
        self.atomic_proofs['or'][False][True] = (True, construct_atomic_proof('nab.proof'))
        self.atomic_proofs['or'][True][False] = (True, construct_atomic_proof('anb.proof'))
        self.atomic_proofs['or'][True][True] = (True, construct_atomic_proof('ab.proof'))

        os.chdir(parent_dir + '/proofs')
        self.a_or_nor_a = construct_atomic_proof('ana.proof')
        os.chdir(parent_dir)

    def get_proof_in_proposal(self, expression, mask, variables):
        proof = []
        if isinstance(expression, Variable):
            if mask[variables[expression.name]]:
                proof.append(expression)
                return expression, True, proof
            else:
                proof.append(Nor(expression))
                return expression, False, proof
        elif isinstance(expression, Nor):
            get_res = self.get_proof_in_proposal(expression.expression(), mask, variables)
            proof = proof + get_res[2]
            if get_res[1]:
                proof = proof + get_a_not_not_a_proof(expression.expression())
                return expression, False, proof
            else:
                return expression, True, proof
        elif isinstance(expression, Binary):
            left = self.get_proof_in_proposal(expression.left(), mask, variables)
            right = self.get_proof_in_proposal(expression.right(), mask, variables)
            proof = left[2] + right[2]
            key = 'and'
            if isinstance(expression, And):
                key = 'and'
            elif isinstance(expression, Or):
                key = 'or'
            elif isinstance(expression, Implication):
                key = 'cons'

            atomic_proof = self.atomic_proofs[key][left[1]][right[1]]
            exp1 = left[0]
            exp2 = right[0]

            proof = proof + atomic_proof[1].get_def_proof(exp1, exp2).proof

            if (atomic_proof[0]):
                return expression, True, proof
            else:
                return expression, False, proof

    def get_proof(self, expression, variables):
        mask = tuple([0] * len(variables))

        proof_in_proposal = {}

        while not mask is None:
            proof_in_proposal[mask] = self.get_proof_in_proposal(expression, mask, variables)
            proof_in_proposal[mask] = proof_in_proposal[mask][2]
            mask = next_mask(mask)

        for l in range(len(variables) - 1, -1, -1):
            mask = tuple([0] * l)

            alpha = ''
            for var, idx in variables.items():
                if idx == l:
                    alpha = var

            while not mask is None:
                proof1 = self.converter.deduction(get_title(variables, mask + (0,), expression), proof_in_proposal[mask + (0,)])
                proof2 = self.converter.deduction(get_title(variables, mask + (1,), expression), proof_in_proposal[mask + (1,)])

                proof = proof1 + proof2

                proof.append(self.parser.parse(
                    '(' + alpha + '->' + '(' + str(expression) + ')' + ')->' +
                    '(!' + alpha + '->' + '(' + str(expression) + ')' + ')->' +
                    ('(' + '(' + alpha + '|!(' + alpha + '))->(' + str(expression) + ')' + ')')))

                proof.append(self.parser.parse(
                    '(!' + alpha + '->' + '(' + str(expression) + ')' + ')->' +
                    ('(' + '(' + alpha + '|!(' + alpha + '))->(' + str(expression) + ')' + ')')))

                proof.append(self.parser.parse(
                    ('(' + '(' + alpha + '|!(' + alpha + '))->(' + str(expression) + ')' + ')')))

                proof3 = self.a_or_nor_a.get_def_proof(Variable(alpha)).proof
                proof = proof + proof3
                proof.append(expression)

                proof_in_proposal[mask] = copy.deepcopy(proof)

                mask = next_mask(mask)

        return proof_in_proposal[()]
