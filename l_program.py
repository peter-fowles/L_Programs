import re
from godel_numbers import natural_number, factor_godel

LABELLED = re.compile(r'\[(\w+)\]')
COMMAND = re.compile(r'IF (\w+) != 0 GOTO (\w+)|(\w+) <- (\w+)($|\n| ([+-]) (\d+))')
IGNORE = re.compile(r'#.*')

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
            lines = open(filename, 'r')
        elif lines is None:
            raise ValueError('No arguments were given')
        for line in lines:
            if not line.strip() or IGNORE.match(line) is not None:
                continue 
            ins = self.Instruction(line)
            if ins.variable not in self.variables:
                self.variables.append(ins.variable)
            if ins.label and ins.label not in self.labels:
                self.labels.append(ins.label)
                self.longest_label = max(len(ins.label), self.longest_label)
            self.instructions.append(ins)
        self.program_length = len(self.instructions)

    def run(self, input_values:dict, show_snapshots:bool=False) -> int:
        var_values = {'Y':0}
        if 'Y' in input_values and input_values['Y'] != 0:
            raise ValueError('The output variable \"Y\" cannot be initialized to anything other than 0')
        for v in self.variables:
            if v in input_values:
                if not isinstance(input_values[v], int) or input_values[v] < 0:
                    raise ValueError("All input variables must be natural numbers")
                var_values[v] = input_values[v]
            else:
                var_values[v] = 0
        done = False
        curr_index = 0
        while not done:
            if show_snapshots:
                print(f'({curr_index + 1}, {{{",".join([v + ':' + str(var_values[v]) for v in var_values])}}})')
            curr_instruction = self.instructions[curr_index]
            if curr_instruction.goto is not None and var_values[curr_instruction.variable] != 0:
                if curr_instruction.goto not in self.labels:
                    done = True
                else:
                    for i in range(len(self.instructions)):
                        if self.instructions[i].label == curr_instruction.goto:
                            curr_index = i
                            break
            else: 
                if curr_instruction.op is not None:
                    if curr_instruction.op == '+':
                        var_values[curr_instruction.variable] += 1
                    elif var_values[curr_instruction.variable] > 0:
                        var_values[curr_instruction.variable] -= 1
                curr_index += 1
        if show_snapshots:
            print(f'({self.program_length + 1}, {{{",".join([v + ':' + str(var_values[v]) for v in var_values])}}})')
        return var_values['Y']
    
    def source_number(self) -> int:
        return self.program_number() + 1

    def __encode_instruction(self, ins) -> int:
        if ins.label is not None:
            a = self.labels.index(ins.label) + 1
        else:
            a = 0
        if ins.groups[GROUPS['iflabel'] - 1] is not None:
            iflabel = ins.groups[GROUPS['iflabel'] - 1]
            if iflabel not in self.labels:
                b = len(self.labels) + 2
            else:
                b = self.labels.index(iflabel) + 3
        elif ins.groups[GROUPS['op'] - 1] == '+':
            b = 1
        elif ins.groups[GROUPS['op'] - 1] == '-':
            b = 2
        else:
            b = 0
        c = self.variables.index(ins.variable) + 1

        right = 2**b * (2 * c + 1) - 1
        return 2**a * (2 * right + 1) - 1
    
    def program_number(self) -> int:
        return natural_number(self.godel_number()) - 1
    
    def godel_number(self) -> list:
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
            self.goto = cmd.group(GROUPS['iflabel'])
            self.op = cmd.group(GROUPS['op'])
            self.text = line.strip()
            self.groups = cmd.groups()

        def __repr__(self):
            return self.text
        
        def latex(self):
            s = f'[{self.label}] ' if self.label else ''
            if self.goto:
                return s + f'IF {self.variable} \\neq 0 GOTO {self.goto}'
            else:
                return s + f'{self.variable} \\gets {self.variable}' + \
                    (f' {self.op} 1' if self.op else '')


def program_from_number(program_num:int) -> L_Program:
    source_num = program_num + 1
    instruction_nums = factor_godel(source_num)
    for ins_num in instruction_nums:
        pass