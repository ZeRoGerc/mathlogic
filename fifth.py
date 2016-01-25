from expressions import *
import formal_parser
import copy

class Subst:
    parser = formal_parser.Parser()
    temp_axiom = parser.parse('0=0->0=0->0=0')

    @staticmethod
    def __formal_substitute__(expression: Expression, a: Expression, b: Expression=None, c: Expression=None):
        object = type(expression)
        if isinstance(expression, Variable):
            if expression.name == 'a':
                return a
            elif expression.name == 'b':
                return b
            elif expression.name == 'c':
                return c
            else:
                return expression
        elif isinstance(expression, MultiOperation):
            new_args = []
            for i in range(0, len(expression.args)):
                new_args.append(Subst.__formal_substitute__(expression.args[i], a, b, c))

            new_args = tuple(new_args)
            if isinstance(expression, Unary):
                return object(new_args[0])
            elif isinstance(expression, Binary) or isinstance(expression, EqualPredicate):
                return object(new_args[0], new_args[1])
            else:
                return object(expression.name, new_args)
        elif isinstance(expression, Quantifier):
            new_exp = Subst.__formal_substitute__(expression.expression, a, b, c)
            return object(expression.variable, new_exp)

    @staticmethod
    def formal_substitute(expression: Expression, args:tuple):
        if len(args) == 1:
            return Subst.__formal_substitute__(expression, args[0])
        elif len(args) == 2:
            return Subst.__formal_substitute__(expression, args[0], args[1])
        else:
            return Subst.__formal_substitute__(expression, args[0], args[1], args[2])

    @staticmethod
    def axiom_substitute(expression: Expression, args: tuple):
        vars = ('a', 'b', 'c')
        proof = []
        proof.append(expression)
        proof.append(Implication(expression, Implication(Subst.temp_axiom, expression)))
        proof.append(Implication(Subst.temp_axiom, expression))

        # add quantifiers
        current = expression
        for i in range(0, len(args)):
            current = UniQuantifier(Variable(vars[len(args) - i - 1]), current)
            proof.append(Implication(Subst.temp_axiom, current))

        # remove quantifiers
        mod_args = [Variable('a'), Variable('b'), Variable('c')]
        for i in range(0, len(args)):
            mod_args[i] = args[i]
            proof.append(current)
            new_exp = Subst.formal_substitute(current.expression, tuple(mod_args))
            proof.append(Implication(current, new_exp))
            current = new_exp

        proof.append(current)
        return proof


def solve():
    input_file = open('input', 'r')
    output_file = open('output', 'w')
    n1, n2 = map(int, input_file.readline().split(' '))

    print(n1, n2)

    a = Variable('0')
    for i in range(0, n1):
        a = Inc(a)

    proof = []
    temp_input = open('proofs/inverse.proof', 'r')
    for raw_exp in temp_input:
        proof.append(Subst.parser.parse(raw_exp[:-1]))
    temp_input.close()

    proof += Subst.axiom_substitute(Subst.parser.parse("a+0=a"), (a,))

    b = Variable('0')
    # a + b = c or 0'''+0'=0''''
    c = copy.deepcopy(a)

    for i in range(0, n2):
        proof += Subst.axiom_substitute(Subst.parser.parse("a=b->a'=b'"), (Add(a, b), c))
        proof.append(EqualPredicate(Inc(Add(a, b)), Inc(c)))

        proof += Subst.axiom_substitute(Subst.parser.parse("a+b'=(a+b)'"), (a, b))

        proof += Subst.axiom_substitute(Subst.parser.parse("a=b->b=a"), (Add(a, Inc(b)), Inc(Add(a, b))))

        proof.append(EqualPredicate(Inc(Add(a, b)), Add(a, Inc(b))))

        proof += Subst.axiom_substitute(
                Subst.parser.parse("a=b->a=c->b=c"),
                (
                    Inc(Add(a, b)),
                    Add(a, Inc(b)),
                    Inc(c)
                )
        )

        proof.append(Implication(
                    EqualPredicate(Inc(Add(a, b)), Inc(c)),
                    EqualPredicate(Add(a, Inc(b)), Inc(c))
            ))

        proof.append(EqualPredicate(Add(a, Inc(b)), Inc(c)))
        b = Inc(b)
        c = Inc(c)

    written = set()
    for line in proof:
        line = str(line)
        if line not in written:
            written.add(line)
            output_file.write(line+'\n')

solve()

# e = EqualPredicate(Variable('a'), Variable('b'))
#
# print(formal_substitute(e, Inc(Variable('0')), Inc(Inc(Variable('0')))))