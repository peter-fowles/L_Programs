import re
from godel_numbers import natural_number, length_natural, factor_godel

LABELLED = re.compile(r'\[(\w+)\]')
COMMAND = re.compile(r'IF (\w+) != 0 GOTO (\w+)|(\w+) <- (\w+)($|\n| ([+-]) (\d+))')

GROUPS = {
    'instruction':0,
    'ifvar':1,
    'iflabel':2,
    'v1':3,
    'v2':4,
    'op':6,
    'val':7
}

class L_Program:
    def __init__(self, filename:str=None, lines:list=None):
        self.variables = []
        self.labels = []
        self.instructions = []
        self.longest_label = 0
        if filename is not None:
            if lines is not None:
                raise ValueError('Cannot have a filename and a list of lines')
            with open(filename, 'r') as f:
                for line in f:    
                    ins = self.Instruction(line)
                    if ins.variable not in self.variables:
                        self.variables.append(ins.variable)
                    if ins.label and ins.label not in self.labels:
                        self.labels.append(ins.label)
                        self.longest_label = max(len(ins.label), self.longest_label)
                    self.instructions.append(ins)
        elif lines is None:
            raise ValueError('No arguments were given')
        else:
            for line in lines:
                    ins = self.Instruction(line)
                    if ins.variable not in self.variables:
                        self.variables.append(ins.variable)
                    if ins.label and ins.label not in self.labels:
                        self.labels.append(ins.label)
                        self.longest_label = max(len(ins.label), self.longest_label)
                    self.instructions.append(ins)
        self.program_length = len(self.instructions)

    def __encode_instruction(self, ins):
        if ins.label is not None:
            a = self.labels.index(ins.label) + 1
        else:
            a = 0
        if ins.groups[GROUPS['iflabel'] - 1] is not None:
            b = self.labels.index(ins.groups[GROUPS['iflabel'] - 1]) + 3
        elif ins.groups[GROUPS['op'] - 1] == '+':
            b = 1
        elif ins.groups[GROUPS['op'] - 1] == '-':
            b = 2
        else:
            b = 0
        c = self.variables.index(ins.variable) + 1

        right = 2**b * (2 * c + 1) - 1
        return 2**a * (2 * right + 1) - 1
    
    def encode(self):
        return natural_number(self.godel_number()) - 1
    
    def godel_number(self):
        num_p = []
        for ins in self.instructions:
            num_p.append(self.__encode_instruction(ins))
        return num_p

    def __repr__(self):
        s = []
        line_num = 1
        for ins in self.instructions:
            if ins.label is None and self.longest_label > 0:
                s.append(str(line_num) + '.'  + ' ' * (len(str(self.program_length)) - len(str(line_num))) + ' ' + ' ' * (self.longest_label + 3) + str(ins))
            else:
                s.append(str(line_num) + '.' + ' ' * (len(str(self.program_length)) - len(str(line_num))) + ' ' + str(ins))
            line_num += 1
        return '\n'.join(s)

    class Instruction:
        def __init__(self, line:str):
            self.variable = None
            self.label = None

            labelled = LABELLED.search(line)
            cmd = COMMAND.search(line)
            var = None

            if cmd is None or not cmd.group():
                raise SyntaxError(f'Invalid Instruction \"{line.strip()}\"')
            if labelled is not None:
                self.label = labelled.group(0)[1:-1]
            if cmd.group(GROUPS['ifvar']):
                var = cmd.group(GROUPS['ifvar'])
            elif cmd.group(GROUPS['v1']) != cmd.group(GROUPS['v2']):
                raise ValueError("Only one variable may be referenced per instruction")
            else:
                var = cmd.group(GROUPS['v1'])

            self.variable = var
            self.text = line.strip()
            self.groups = cmd.groups()

        def __repr__(self):
            return self.text
        
        def latex(self):
            s = f'[{self.label}] ' if self.label else ''
            if self.groups[GROUPS['iflabel'] - 1]:
                return s + f'IF {self.groups[GROUPS["ifvar"] - 1]} \\neq 0 GOTO {self.groups[GROUPS["iflabel"] - 1]}'
            else:
                return s + f'{self.groups[GROUPS["v1"] - 1]} \\gets {self.groups[GROUPS["v2"] - 1]}' + \
                    (f' {self.groups[GROUPS["op"] - 1]} {self.groups[GROUPS["val"] - 1]}' if self.groups[GROUPS["op"] - 1] else '')


