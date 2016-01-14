__author__ = 'ZeRoGerc'

from expressions import *


class ParseError(Exception):
    def __init__(self):
        super(ParseError, self).__init__("parse error")

def __get_vars__(expression: Expression, bound_vars: set=None, variables: dict=None):
    if bound_vars is None:
        bound_vars = set()
    if variables is None:
        variables = {}

    if isinstance(expression, Variable):
        if expression.name not in bound_vars:
            variables[expression.name] = "free"
        elif expression.name not in variables.keys():
            variables[expression.name] = "bound"
    elif isinstance(expression, MultiOperation):
        for exp in expression.args:
            variables = __get_vars__(exp, bound_vars.copy(), variables)
    elif isinstance(expression, Quantifier):
        bound_copy = bound_vars.copy()
        bound_copy.add(expression.variable.name)
        variables = __get_vars__(expression.expression, bound_copy, variables)

    return variables


def get_bound_vars(expression: Expression):
    vars = __get_vars__(expression)
    result = set()
    for key, value in vars.items():
        if value == "bound":
            result.add(str(key))

    return result


def get_free_vars(expression: Expression, bound_vars: set=None):
    if bound_vars is None:
        bound_vars = set()

    result = set()
    if isinstance(expression, Variable):
        if expression.name not in bound_vars:
            result.add(expression.name)
    elif isinstance(expression, MultiOperation):
        for exp in expression.args:
            result = result.union(get_free_vars(exp, bound_vars.copy()))
    elif isinstance(expression, Quantifier):
        bound_copy = bound_vars.copy()
        bound_copy.add(expression.variable.name)
        result = get_free_vars(expression.expression, bound_copy)

    return result


def __is_substitution__(shape: Expression, expression: Expression, variable: Variable, bound_vars: set=None):
    if bound_vars is None:
        bound_vars = set()

    if isinstance(shape, Variable):
        if shape.name != variable.name:
            return bool(shape == expression), None
        elif shape.name in bound_vars:
            if isinstance(expression, Variable):
                return bool(shape == expression), expression
            else:
                return False, expression
        else:
            free = get_free_vars(expression)
            if len(set.intersection(free, bound_vars)) == 0:
                return True, expression
            else:
                return False, expression

    elif isinstance(shape, MultiOperation) and isinstance(expression, MultiOperation):
        if (shape.get_name() != expression.get_name()) or (len(shape.args) != len(expression.args)):
            return False, None

        result = None
        result_ok = True
        for i in range(0, len(shape.args)):
            is_ok, replace = __is_substitution__(shape.args[i], expression.args[i], variable, bound_vars.copy())

            if not is_ok:
                result_ok = False

            if result is None:
                result = replace
            elif (replace is not None) and (result != replace):
                return False, None

        return result_ok, result

    elif isinstance(shape, Quantifier) and isinstance(expression, Quantifier):
        if shape.variable != expression.variable:
            return False, None

        bound_copy = bound_vars.copy()
        bound_copy.add(shape.variable.name)

        return __is_substitution__(shape.expression, expression.expression, variable, bound_copy)

    return False, None


def is_substitution(shape: Expression, expression: Expression, variable: Variable):
    is_ok, replace = __is_substitution__(shape, expression, variable)
    return is_ok, replace


class Parser:
    import re

    is_variable = re.compile('[a-z][0-9]*')
    is_predicate = re.compile('[A-Z][0-9]*')
    is_function = re.compile('[a-z][0-9]*\(')

    def __init__(self):
        self.main_string = ''
        self.index = 0

    def __parse_multiplied__(self):
        result = None
        if self.main_string[self.index] == '0':
            self.index += 1
            result = Variable('0')
        elif self.main_string[self.index] == '(':
            self.index += 1  # skip (
            result = self.__parse_term__()
            if self.main_string[self.index] != ')':
                raise ParseError()
            else:
                self.index += 1  # skip )
        else:
            matched = self.is_variable.match(self.main_string, pos=self.index)
            if matched is None:
                raise ParseError()
            if matched.end() != len(self.main_string) and self.main_string[matched.end()] == '(':  # It's function
                self.index = matched.end() + 1  # skip f(
                result = Function(matched.group(), self.__parse_args__())
                self.index += 1  # skip )
            else:  # It's variable
                self.index = matched.end()
                result = Variable(matched.group())

        while self.index < len(self.main_string) and self.main_string[self.index] == "'":
            self.index += 1
            result = Inc(result)

        return result

    def __parse_addendum__(self):
        left = self.__parse_multiplied__()
        while self.index < len(self.main_string) and self.main_string[self.index] == '*':
            self.index += 1  # skip *
            left = Multiply(left, self.__parse_multiplied__())
        return left

    def __parse_term__(self):
        left = self.__parse_addendum__()
        while self.index < len(self.main_string) and self.main_string[self.index] == '+':
            self.index += 1  # skip +
            left = Add(left, self.__parse_addendum__())
        return left

    def __parse_args__(self):
        args = [self.__parse_term__()]

        while self.index < len(self.main_string) and self.main_string[self.index] == ',':
            self.index += 1
            args.append(self.__parse_term__())

        return tuple(args)

    def __parse_predicate__(self):
        matched = self.is_predicate.match(self.main_string, pos=self.index)
        if matched is None:  # It's predicate of type term=term
            left = self.__parse_term__()
            if self.main_string[self.index] != '=':
                raise ParseError()
            else:
                self.index += 1  # skip =
            return EqualPredicate(left, self.__parse_term__())
        else:
            name = matched.group()
            args = tuple()
            self.index = matched.end()
            if matched.end() < len(self.main_string) and self.main_string[matched.end()] == '(':  # It's predicate of type P(x,y,....)
                self.index += 1
                args = self.__parse_args__()
                if self.index >= len(self.main_string):
                    print(self.main_string)
                if self.main_string[self.index] != ')':
                    raise ParseError()
                else:
                    self.index += 1  # skip )

            return Predicate(name, args)

    def __parse_unary__(self):
        if self.index >= len(self.main_string):
            print(self.main_string)
        if self.main_string[self.index] == '!':
            self.index += 1
            return Nor(self.__parse_unary__())

        prev_index = self.index
        try:
            return self.__parse_predicate__()
        except ParseError:
            self.index = prev_index

        if self.main_string[self.index] == '(':
            self.index += 1  # skip (
            result = self.__parse_expression__()
            self.index += 1  # skip )

            return result

        if self.main_string[self.index] == '@' or self.main_string[self.index] == '?':
            quantifier = self.main_string[self.index]
            self.index += 1
            matched = self.is_variable.match(self.main_string, pos=self.index)
            self.index = matched.end()
            if quantifier == '@':
                return UniQuantifier(Variable(matched.group()), self.__parse_unary__())
            else:
                return ExistQuantifier(Variable(matched.group()), self.__parse_unary__())

    def __parse_conjunction__(self):
        left = self.__parse_unary__()
        while self.index < len(self.main_string) and self.main_string[self.index] == '&':
            self.index += 1  # skip &
            left = And(left, self.__parse_unary__())
        return left

    def __parse_disjunction__(self):
        left = self.__parse_conjunction__()
        while self.index < len(self.main_string) and self.main_string[self.index] == '|':
            self.index += 1  # skip |
            left = Or(left, self.__parse_conjunction__())
        return left

    def __parse_expression__(self):
        left = self.__parse_disjunction__()
        if self.index < len(self.main_string) and self.main_string[self.index] == '-':  # it's implication
            self.index += 2  # skip ->
            if self.index >= len(self.main_string):
                print(self.main_string)
            temp = Implication(left, self.__parse_expression__())
            return temp
        else:
            return left

    def parse(self, expression: str):
        self.main_string = expression
        self.index = 0
        return self.__parse_expression__()

    def part_parse(self, expression: str, pos: int):
        self.main_string = expression
        self.index = pos
        result = self.__parse_expression__()
        return result, self.index



# p = Parser()
# print(p.parse("A->A&B->@xC"))
#
# e1 = p.parse("@yP(y,x,z,a,f(z0))&Q(x,z,a,f(y0))")
# e2 = p.parse("@yP(f(y,x),f(y,x))")
#
# print(get_bound_vars(e1))
# print(get_bound_vars(e2))
# print(get_free_vars(e1))
# print(get_free_vars(e2))

# print(p.parse("((x)'+y=(x+y)')->((((x)'+y=(x+y)')->((x)'+y=(x+y)'))->((x)'+y=(x+y)'))"))

# is_ok, replace = is_substitution(e1, e2, Variable('x'))
# print(is_ok, replace)