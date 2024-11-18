import re
from godel_numbers import natural_number, factor_godel, split_natural_number

LABELLED = re.compile(r'\[(([A-E])(\d+))\]')
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
# TODO Create a universal mapping for all variables and labels instead of just the ones in use
class L_Program:
    def __init__(self, filename:str=None, lines:list=None):
        self.label_lines = dict()
        self.instructions = []
        self.longest_label = 0
        if filename is not None:
            if lines is not None:
                raise ValueError('Cannot have a filename and a list of lines')
            lines = open(filename, 'r')
        elif lines is None:
            raise ValueError('No arguments were given')
        line_num = 1
        for line in lines:
            if not line.strip() or IGNORE.match(line) is not None:
                continue 
            ins = self.Instruction(line)
            if ins.label:
                self.label_lines[ins.label] = line_num
                self.longest_label = max(len(ins.label), self.longest_label)
            self.instructions.append(ins)
            line_num += 1
        self.program_length = len(self.instructions)

    def run(self, input_values:dict, show_snapshots:bool=False) -> int:
        # Initialize Variables
        var_values = {'Y':0}
        if 'Y' in input_values and input_values['Y'] != 0:
            raise ValueError('The output variable \"Y\" cannot be initialized to anything other than 0')
        for v in input_values:
            if v not in var_values:
                var_values[v] = input_values[v]

        done = False
        curr_index = 0
        while not done:
            if show_snapshots:
                print(f'({curr_index + 1}, {{{",".join([v + ':' + str(var_values[v]) for v in var_values])}}})')
            curr_instruction = self.instructions[curr_index]
            if curr_instruction.variable not in var_values:
                var_values[curr_instruction.variable] = 0
            if curr_instruction.goto is not None and var_values[curr_instruction.variable] != 0:
                if curr_instruction.goto not in self.label_lines:
                    done = True
                else:
                    curr_index = self.label_lines[curr_instruction.goto] - 1
            else: 
                if curr_instruction.op is not None:
                    if curr_instruction.op == '+':
                        var_values[curr_instruction.variable] += 1
                    elif var_values[curr_instruction.variable] > 0:
                        var_values[curr_instruction.variable] -= 1
                curr_index += 1
                if curr_index >= self.program_length:
                    done = True
        if show_snapshots:
            print(f'({self.program_length + 1}, {{{",".join([v + ':' + str(var_values[v]) for v in var_values])}}})')
        return var_values['Y']
    
    def source_number(self) -> int:
        return self.program_number() + 1
    
    def program_number(self) -> int:
        return natural_number(self.godel_number()) - 1
    
    def godel_number(self) -> list:
        num_p = []
        for ins in self.instructions:
            num_p.append(ins.encode())
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
        
        def encode(self):
            if self.label is not None:
                a = label_number(self.label)
            else:
                a = 0
            if self.groups[GROUPS['iflabel'] - 1] is not None:
                iflabel = self.groups[GROUPS['iflabel'] - 1]
                b = label_number(iflabel) + 2
            elif self.groups[GROUPS['op'] - 1] == '+':
                b = 1
            elif self.groups[GROUPS['op'] - 1] == '-':
                b = 2
            else:
                b = 0
            c = variable_number(self.variable) - 1

            right = 2**b * (2 * c + 1) - 1
            return 2**a * (2 * right + 1) - 1


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
    lines = []
    for ins_num in instruction_nums:
        a, bc = split_natural_number(ins_num)
        b, c = split_natural_number(bc)
        if a == 0:
            label = None
        else:
            label = f'A{a}'
        if c + 1 == 1:
            variable = 'Y'
        else:
            variable = f'X{c + 1}'
        instruction = '' if label is None else f'[{label}] '
        if b == 0:
            instruction = f'{instruction}{variable} <- {variable}'
        elif b == 1:
            instruction = f'{instruction}{variable} <- {variable} + 1'
        elif b == 2:
            instruction = f'{instruction}{variable} <- {variable} - 1'
        else:
            instruction = f'{instruction}IF {variable} != 0 GOTO A{b - 2}'
        lines.append(instruction)
    return L_Program(lines=lines)

def label_number(label:str) -> int:
    label_components = re.compile(r'([A-E])(\d+)')
    label_match = label_components.search(label)
    letter = label_match.group(1)
    number = label_match.group(2)
    return (ord(letter) - 64) + (5 * (int(number) - 1))

def label_from_number(num:int) -> str:
    return ['A', 'B', 'C', 'D', 'E'][(num - 1) % 5] + str((num - 1) // 5 + 1)

def var_from_number(num:int) -> str:
    if num == 1:
        return 'Y'
    return ['X', 'Z'][(num - 2) % 2] + str((num - 3) // 2 + 1)

def variable_number(variable:str) -> int:
    if variable == 'Y':
        return 1
    variable_components = re.compile(r'([XZ])(\d+)')
    var_match = variable_components.search(variable)
    letter = var_match.group(1)
    number = var_match.group(2)
    if letter == 'X':
        return 2 + (2 * (int(number) - 1))
    return 3 + (2 * (int(number) - 1))
