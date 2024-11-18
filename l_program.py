import re
from godel_numbers import natural_number_of_godel, factor_godel, split_natural_number

LABELLED = re.compile(r'\[(([A-E])(\d+))\]')
COMMAND = re.compile(r'IF (\w+) != 0 GOTO (\w+)|(\w+) <- (\w+)($|\n| ([+-]) (\d+))')
IGNORE = re.compile(r'#.*')

COMMAND_GROUPS = {
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
        """
        Constructs an executable L-Program

        Keyword Arguments (only use one):
        filename -- a file containing an L-Program to interpret
        lines -- a list of strings where each string is an instruction in an L-program to interpret
        """
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
        """
        Runs the program

        Positional Arguments:
        input_values -- A dictionary mapping state variables to their initial values

        Keyword Arguments:
        show_snapshots -- A boolean indicating whether to print each snapshot of the computation
        """
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
        """
        returns the source number of the program
        (source number is the program number + 1)
        """
        return self.program_number() + 1
    
    def program_number(self) -> int:
        """
        returns the program number of the program as a natural number
        """
        return natural_number_of_godel(self.godel_number()) - 1
    
    def godel_number(self) -> list:
        """
        returns the godel number for the program
        """
        num_p = []
        for ins in self.instructions:
            num_p.append(ins.encode())
        return num_p
    
    def split_numerical_repr(self) -> str:
        """
        returns the natural number of the program, represented with its godel number, 
        with each instruction number split into a, b, c such that the instruction number = <a, <b, c>>
        """
        result = []
        for num in self.godel_number():
            a, bc = split_natural_number(num)
            b, c = split_natural_number(bc)
            result.append(f'<{a},<{b},{c}>>')
        return f'[{", ".join(result)}] - 1'

    def __repr__(self) -> str:
        """
        returns the program's instructions
        """
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
            """
            Constructor for an Instruction object
            Contains data for a single instruction in an L-program

            positional arguments:
            line -- a single line, or the text of a single instruction, of an L-program
            """
            self.label = None

            labelled = LABELLED.search(line)
            cmd = COMMAND.search(line)
            var = None

            if cmd is None or not cmd.group():
                raise SyntaxError(f'Invalid Instruction \"{line.strip()}\"')
            if labelled is not None:
                self.label = labelled.group(0)[1:-1]
            if cmd.group(COMMAND_GROUPS['ifvar']):
                var = cmd.group(COMMAND_GROUPS['ifvar'])
            elif cmd.group(COMMAND_GROUPS['v1']) != cmd.group(COMMAND_GROUPS['v2']):
                raise ValueError("Only one variable may be referenced per instruction")
            else:
                var = cmd.group(COMMAND_GROUPS['v1'])

            self.variable = var
            self.goto = cmd.group(COMMAND_GROUPS['iflabel'])
            self.op = cmd.group(COMMAND_GROUPS['op'])
            self.text = line.strip()
            self.groups = cmd.groups()

        def __repr__(self) -> str:
            """
            returns the text for the instruction
            """
            return self.text
        
        def encode(self) -> int:
            """
            encodes the instruction into its natural number representation
            """
            if self.label is not None:
                a = label_number(self.label)
            else:
                a = 0
            if self.groups[COMMAND_GROUPS['iflabel'] - 1] is not None:
                iflabel = self.groups[COMMAND_GROUPS['iflabel'] - 1]
                b = label_number(iflabel) + 2
            elif self.groups[COMMAND_GROUPS['op'] - 1] == '+':
                b = 1
            elif self.groups[COMMAND_GROUPS['op'] - 1] == '-':
                b = 2
            else:
                b = 0
            c = variable_number(self.variable) - 1

            right = 2**b * (2 * c + 1) - 1
            return 2**a * (2 * right + 1) - 1


        def latex(self) -> str:
            """
            returns a mathematical representation of the instruction in LaTeX syntax
            """
            s = f'[{self.label}] ' if self.label else ''
            if self.goto:
                return s + f'IF {self.variable} \\neq 0 GOTO {self.goto}'
            else:
                return s + f'{self.variable} \\gets {self.variable}' + \
                    (f' {self.op} 1' if self.op else '')


def program_from_number(program_num:int) -> L_Program:
    """
    constructs the L-program associated with a natural number
    returns the L-program

    positional arguments:
    program_num -- a natural number to be decoded into an L-program
    """
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
    """
    gets the number mapped to a given label

    returns the number (> 0) mapped to the label

    positional arguments:
    label -- a valid label for an L-program 
    """
    label_components = re.compile(r'([A-E])(\d+)')
    label_match = label_components.search(label)
    letter = label_match.group(1)
    number = label_match.group(2)
    return (ord(letter) - 64) + (5 * (int(number) - 1))

def label_from_number(num:int) -> str:
    """
    gets the label mapped to a given number

    returns the L-program label mapped to the given number

    positional arguments:
    num -- a natural number (> 0) to extract the label for
    """
    if num < 1:
        raise ValueError('Labels can only be mapped to numbers greater than or equal to 1')
    return ['A', 'B', 'C', 'D', 'E'][(num - 1) % 5] + str((num - 1) // 5 + 1)

def var_from_number(num:int) -> str:
    """
    gets the variable mapped to a given number

    returns the L-program variable mapped to the given number

    positional arguments:
    num -- a natural number (> 0) to extract the variable for
    """
    if num == 1:
        return 'Y'
    elif num < 1:
        raise ValueError('Variables can only be mapped to numbers greater than or equal to 1')
    return ['X', 'Z'][(num - 2) % 2] + str((num - 3) // 2 + 1)

def variable_number(variable:str) -> int:
    """
    gets the number mapped to a given variable

    returns the number (> 0) mapped to the variable

    positional arguments:
    variable -- a valid variable for an L-program 
    """
    if variable == 'Y':
        return 1
    variable_components = re.compile(r'([XZ])(\d+)')
    var_match = variable_components.search(variable)
    letter = var_match.group(1)
    number = var_match.group(2)
    if letter == 'X':
        return 2 + (2 * (int(number) - 1))
    return 3 + (2 * (int(number) - 1))
