__author__ = 'ZeRoGerc'


class Expression:
    def get_name(self):
        return 'exp'


class Variable(Expression):
    def __init__(self, name: str):
        super(Variable, self).__init__()
        self.name = name

    def __eq__(self, other: Expression):
        if not isinstance(other, Variable):
            return False
        else:
            return self.name == other.name

    def __str__(self):
        return str(self.name)

    def __hash__(self):
        return hash(self.name)

    def get_name(self):
        return 'var'


class MultiOperation(Expression):
    def __init__(self, name: str, args: tuple):
        super(MultiOperation, self).__init__()
        self.args = args
        self.name = name

    def __eq__(self, other: Expression):
        if not isinstance(other, MultiOperation):
            return False
        else:
            return self.name == other.name and self.args == other.args

    def __str__(self):
        if len(self.args) == 0:
            return str(self.name)
        else:
            return str(self.name) + '(' + ','.join(map(str, self.args)) + ')'

    def __hash__(self):
        return hash((self.name, self.args))

    def get_name(self):
        return str(self.name)


class Unary(MultiOperation):
    def __init__(self, expression: Expression, name: str):
        super(Unary, self).__init__(name, (expression,))
        self.name = name

    def expression(self):
        return self.args[0]


class Binary(MultiOperation):
    def __init__(self, left: Expression, right: Expression, name: str):
        super(Binary, self).__init__(name, (left, right))

    def __str__(self):
        return '(' + str(self.left()) + ')' + str(self.name) + '(' + str(self.right()) + ')'

    def left(self):
        return self.args[0]

    def right(self):
        return self.args[1]


class Inc(Unary):
    def __init__(self, expression: Expression):
        super(Inc, self).__init__(expression, "'")

    def __str__(self):
        if isinstance(self.expression(), Inc):
            return str(self.expression()) + "'"
        else:
            return '(' + str(self.expression()) + ")'"


class Nor(Unary):
    def __init__(self, expression: Expression):
        super(Nor, self).__init__(expression, '!')


class And(Binary):
    def __init__(self, left: Expression, right: Expression):
        super(And, self).__init__(left, right, '&')


class Or(Binary):
    def __init__(self, left: Expression, right: Expression):
        super(Or, self).__init__(left, right, '|')


class Implication(Binary):
    def __init__(self, left: Expression, right: Expression):
        super(Implication, self).__init__(left, right, '->')


class Add(Binary):
    def __init__(self, left: Expression, right: Expression):
        super(Add, self).__init__(left, right, '+')


class Multiply(Binary):
    def __init__(self, left: Expression, right: Expression):
        super(Multiply, self).__init__(left, right, '*')


class Predicate(MultiOperation):
    def __init__(self, name: str, args: tuple):
        super(Predicate, self).__init__(name, args)


class EqualPredicate(Predicate):
    def __init__(self, left: Expression, right: Expression):
        super(EqualPredicate, self).__init__('=', (left, right))

    def __str__(self):
        return '(' + str(self.left()) + ')' + '=(' + str(self.right()) + ')'

    def left(self):
        return self.args[0]

    def right(self):
        return self.args[1]


class Function(MultiOperation):
    def __init__(self, name: str, args: tuple):
        super(Function, self).__init__(name, args)


class Quantifier(Expression):
    def __init__(self, name: str, var: Variable, exp: Expression):
        self.name = name
        self.variable = var
        self.expression = exp

    def __eq__(self, other: Expression):
        if not isinstance(other, Quantifier):
            return False
        else:
            return self.name == other.name and self.variable == other.variable and self.expression == other.expression

    def __str__(self):
        return str(self.name) + str(self.variable) + '(' + str(self.expression) + ')'

    def __hash__(self):
        return hash((self.name, self.variable, self.expression))

    def get_name(self):
        return str(self.name)


class UniQuantifier(Quantifier):
    def __init__(self, var: Variable, exp: Expression):
        super(UniQuantifier, self).__init__('@', var, exp)


class ExistQuantifier(Quantifier):
    def __init__(self, var: Variable, exp: Expression):
        super(ExistQuantifier, self).__init__('?', var, exp)