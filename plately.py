import re
import random as pyrandom

"""
TODO: maybe types
    - random but sampling all! {! 1,2,3 !} has len 3
    - change {.1,2,3.} to {.1,2,3.} -> . is more product
"""


class Parser:
    def __init__(self, variables=None):
        self.variables = {} if variables is None else variables

    @staticmethod
    def split(string, start, end):
        return [string[0:start], string[start:end], string[end:]]

    def parse(first=None, second="", variables=None):
        if variables is None:
            variables = {}
        if isinstance(first, Parser):
            self = first
            variables = dict(self.variables, **variables)
            input_str = second
        elif isinstance(first, str):
            variables = second
            if variables == "":
                variables = {}
            input_str = first
        else:
            raise TypeError("first argument must be Parser or str")

        pattern = re.compile(r'{(.*?)}')
        idxs = []

        for m in re.finditer(pattern, input_str):
            idxs += [m.span()]

        rest = input_str
        elements = []
        for start, end in reversed(idxs):
            rest, element_str, string = Parser.split(rest, start, end)
            element = Parser.parse_element(element_str)
            elements = [element, identity(string)] + elements

        elements = [rest] + elements
        out_container = Container(*elements)
        out_container.variables = variables
        return out_container

    @staticmethod
    def parse_element(element_str):
        assert element_str[0] == "{" and element_str[-1] == "}"
        element_str = element_str[1:-1]
        command_symbol = element_str[0] + element_str[-1]
        inside = element_str[1:-1]

        # check for default_pattern
        default_pattern = ""
        if "|" in inside:
            inside, default_pattern = inside.split("|")

        if command_symbol == "  ":
            return identity(inside, default_pattern=default_pattern)
        elif command_symbol == "..":
            return product(*inside.split(","), default_pattern=default_pattern)
        elif command_symbol == "[]":
            return iteration(*inside.split(","), default_pattern=default_pattern)
        elif command_symbol == "()":
            tmp = inside.split(",")
            if len(tmp) == 1:
                return variable(tmp[0], default_pattern=default_pattern)
            else:
                return variable(tmp[0], default=tmp[1], default_pattern=default_pattern)
        elif command_symbol == "??":
            return random(*inside.split(","))
        elif command_symbol == "--":
            values, interval = inside.split(";")
            return interval_iterator(*values.split(","), interval=int(interval), default_pattern=default_pattern)
        elif command_symbol == "oo":
            tmp = inside.split(",")
            if len(tmp) == 1:
                return infinte_iteration()
            else:
                return infinte_iteration(step=int(tmp[0]), start=int(tmp[1]), default_pattern=default_pattern)


        return identity(inside, default_pattern=default_pattern)  # ?


class Container:
    # todo: better name?
    def __init__(self, *elements, **kwargs):
        # todo: kwargs and container
        assert all(isinstance(x, str) or issubclass(type(x), BaseIterator) for x in elements)
        self.elements = [x if isinstance(x, BaseIterator) else identity(x, container=self) for x in elements]
        for element in self.elements:
            element.container = self

        multiplier = 1
        for x in reversed(self.elements):
            if isinstance(x, product):
                x.interval *= multiplier
                multiplier = len(x)

        self.variables = kwargs
        self.counter = -1
        self.max = max([0] + [len(x) for x in self.elements])

        # todo: chek interval of
        # todo: find out max iteration
        # todo: allow autoreset?

    def __next__(self):
        # todo: ?
        self.counter += 1
        if self.counter == self.max:
            raise StopIteration
        return self[self.counter]

    def reset(self):
        # todo: reset iterator object
        raise NotImplementedError

    def __iter__(self):
        for i in range(self.max):
            yield self[i]
        # self.reset()  # todo: not implemented

    def __getitem__(self, item):
        return "".join(str(x[item]) for x in self.elements)


class BaseIterator:
    def __init__(self, container=None, default_pattern=""):
        self.container = container
        self.default_pattern = default_pattern

    @staticmethod
    def paste(string, pattern):
        i = len(pattern) - len(string)
        if i > 0:
            return pattern[0:i] + string
        return string

    def __next__(self):
        raise NotImplementedError

    def __getitem__(self, item):
        if not isinstance(item, int):
            raise TypeError

    def __len__(self):
        raise NotImplementedError


class identity(BaseIterator):
    def __init__(self, value, container=None, default_pattern=""):
        super().__init__(container, default_pattern)
        self.value = value

    def __next__(self):
        return self.value

    def __getitem__(self, item):
        super().__getitem__(item)
        return self.paste(self.value, self.default_pattern)

    def __len__(self):
        return 1


class iteration(BaseIterator):
    def __init__(self, *values, container=None, default_pattern=""):
        super().__init__(container, default_pattern)
        self.values = values
        self.idx = -1

    def __next__(self):
        self.idx += 1
        self.idx %= len(self.values)
        return self.values[self.idx]

    def __getitem__(self, item):
        super().__getitem__(item)
        return self.paste(str(self.values[item % len(self.values)]), self.default_pattern)

    def __len__(self):
        return len(self.values)


class infinte_iteration(BaseIterator):
    def __init__(self, start=0, step=1, container=None, default_pattern=""):
        super().__init__(container, default_pattern)
        self.start = start
        self.step = step
        self.last = start - step

    def __next__(self):
        self.last += self.step
        return self.last

    def __getitem__(self, item):
        super().__getitem__(item)
        return item*self.step + self.start

    def __len__(self):
        return 1


class random(BaseIterator):
    def __init__(self, *values, container=None, default_pattern=""):
        super().__init__(container, default_pattern)
        self.values = values

    def __next__(self):
        return self.values[pyrandom.randint(0, len(self.values) - 1)]

    def __getitem__(self, item):
        super().__getitem__(item)
        return self.paste(self.values[pyrandom.randint(0, len(self.values) - 1)], self.default_pattern)

    def __len__(self):
        return 1


class interval_iterator(BaseIterator):
    def __init__(self, *values, interval=1, container=None, default_pattern=""):
        super().__init__(container, default_pattern)
        self.values = values
        self.interval = interval
        self.counter = 0
        self.idx = -1

    def __next__(self):
        if self.counter % self.interval == 0:
            self.idx += 1
        self.counter += 1
        if self.idx == len(self.values):
            self.counter = 1
            self.idx = 0
            return self.values[0]
        return self.values[self.idx]

    def __getitem__(self, item):
        super().__getitem__(item)
        return self.paste(str(self.values[(item // self.interval) % len(self.values)]), self.default_pattern)

    def __len__(self):
        return len(self.values) * self.interval


class variable(BaseIterator):
    def __init__(self, name, container=None, default="", default_pattern=""):
        super().__init__(container, default_pattern)
        self.name = name
        self.default = default

    def __next__(self):
        if self.container is None:
            raise Exception("container not defined in variable")
        return self.container.variables.get(self.name, self.default)

    def __getitem__(self, item):
        if self.container is None:
            raise Exception("container not defined in variable")
        super().__getitem__(item)
        return self.paste(self.container.variables.get(self.name, self.default), self.default_pattern)

    def __len__(self):
        if self.container is None:
            raise Exception("container not defined in variable")
        return 1


class product(interval_iterator):
    def __init__(self, *values, interval=1, container=None, default_pattern=""):
        super().__init__(*values, interval=interval, container=container, default_pattern=default_pattern)

    def set_interval(self, interal):
        self.interval = interal
