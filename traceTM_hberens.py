#!/usr/bin/env python3
import csv
from collections import deque, defaultdict
import os 

# tape class 
class Tape(object): 
    def __init__(self, state, left = [], head = '_', right = []): 
        self.curr_state = state 
        self.left = left 
        self.head = head
        self.right = right

    # str method for printing formating 
    def __str__(self):
        return ''.join(self.left) + ',' + self.curr_state + ',' + self.head + ',' + ''.join(self.right)


# turing machine class 
class NonDeterministicTuringMachine:
    def __init__(self, file_path):
        self.file = file_path

        # dictionary for the tape configurations
        self.TM_Tape = {}
 
        # open and read csv file 
        with open(file_path, "r") as file:
            reader = csv.reader(file)
            rows = list(reader)

        # parse machine data given the csv format 
        self.name = rows[0][0]  # name
        self.states = set(rows[1])  # states
        self.sigma = set(rows[2])  # input symbols
        self.gamma = set(rows[3])   # gamma
        self.start_state = rows[4][0]   # start state
        self.accept_state = rows[5][0]  # accept state
        self.reject_state = rows[6][0]  # reject state

        # get the transitions from the rest of the csv file 
        for row in rows[7:]:
            if len(row) < 5:
                continue
            # format of the transition 
            current_state, read_symbol, next_state, write_symbol, direction = row
            
            # if that state isn't in the tape, intialize a dictionary for it
            if current_state not in self.TM_Tape:
                self.TM_Tape[current_state] = {}
            # if that sigma character isn't in the current state dictionary initialize it
            if read_symbol not in self.TM_Tape[current_state]:
                self.TM_Tape[current_state][read_symbol] = []

            # add that transition to the dictionary as a list of tuples 
            self.TM_Tape[current_state][read_symbol].append((next_state, write_symbol, direction))


    def append_transitions(self, t):

        current_state = t.curr_state
        head = t.head

        # check if head isn't in the tape's current state 
        if head not in self.TM_Tape[current_state]:
            return None
        else: 
            new = [] 

            # go through the transitions in the tape dictionary in curent state dictionary at the head input 
            for transition in self.TM_Tape[current_state][head]:
                # get the next state, write_symbol and direciton from that tuple
                next, write_symbol, direction = transition

                # replace the head with the new symbol
                head = write_symbol
                left = t.left
                right = t.right

                # alter head and string based on direciton 
                if (direction == 'R'):
                    if len(t.right) == 0:
                        right = ['_']   # go to a blank when finished 
                    # move the head over
                    n = Tape(next, left+[head], right[0], right[1:])

                else:   # left direction 
                    if len(t.left) == 0: 
                        left = ['_']
                    n = Tape(next, left[:-1], left[-1], [head]+right)
                
                # append the new configuration 
                new.append(n)
            return new

    # function to trace the input string 
    def trace_string(self, input_string, max_depth, output):

        # make the string a list- if the string is the empty strint just make it a _
        strlist = []
        if input_string == "": 
            strlist.append('_')
            string = '_'
        else: 
            strlist = list(input_string)
            string = input_string
        # create a tape from the class with the head at the first character and the right as the 2nd character 
        tape = Tape(state=self.start_state, head=strlist[0], right=strlist[1:])

        # initialize some tracking variables and a queue
        q = deque([(tape, 0, [tape])])
        visited = {} 
        step = 0 
        accepted = False 
    
        # Initialize tracking variables
        transitions_per_level = {}
        non_leaves_per_level = {}

        # while there are still inputs, and we haven't reached the max_depth, loop
        while len(q) > 0 and step < max_depth:
            current, level, path = q.popleft()

            # check if in visited, and add it 
            if level not in visited: 
                visited[level] = []
            visited[level].append(tape)

            # check if the current state is an accept, and stop it so, if it s areject continue to the next level
            if (current.curr_state in self.accept_state):
                accepted = True 
                break 
            if (current.curr_state in self.reject_state):
                continue

            # apply the transition using the append_transition method
            next = self.append_transitions(current)

            # Track outgoing transitions and non-leaf nodes
            if level not in transitions_per_level:
                transitions_per_level[level] = 0
                non_leaves_per_level[level] = 0

            if next:  # If outgoing transitions exist
                transitions_per_level[level] += len(next)
                non_leaves_per_level[level] += 1

            # if there is None, skip
            if next==None: 
                continue
            
            # go through and append the tape, and level and path to the queue 
            for tape in next:
                q.append((tape, level+1, path+[tape]))
            step += 1

        # Calculate degree of nondeterminism

        total_transitions = sum(transitions_per_level.values())
        total_non_leaves = sum(non_leaves_per_level.values())

        if total_non_leaves > 0:
            degree_of_nondeterminism = total_transitions / total_non_leaves
        else:
            degree_of_nondeterminism = 0

        # print info to the terminal and write it to an output file 
        print(f'Tree configuration depth: {max(visited.keys())}')
        output.write(f'Tree configuration depth: {max(visited.keys())}\n')

        print(f"Total transitions taken: {step}")
        output.write((f"Total transitions taken: {step}\n"))

        print(f"Degree of nondeterminism: {degree_of_nondeterminism:.2f}")
        output.write(f"Degree of nondeterminism: {degree_of_nondeterminism:.2f}\n")


        # different messages depending on whether the string was accepted or not
        if (accepted == True):
            print(f"String {string} accepted in {level} transitions.")
            output.write(f"String {string} accepted in {level} transitions.\n")
            output.write('Transitions to accept:\n')
            for tape in path: 
                print(tape)
                output.write(f'{tape}\n')
        else:
            if step < max_depth:
                print(f'String {string} rejected in {max(visited.keys())} transitions.')
                output.write(f'String {string} rejected in {max(visited.keys())} transitions.\n')
            
            # if the max_depth was surpassed 
            else:
                print(f'Execution stopped after {max_depth} depth limit')
                output.write(f'Execution stopped after {max_depth} depth limit.\n')
        
    


# Main execution
def main():
    
    # ask for turing machine name and ask until they put in a valid one
    ntm_file = (input("Input the Turing Machine csv file name: ")).strip()
    while not os.path.exists(ntm_file):
        print(f'csv file {ntm_file} does not exist')
        ntm_file = input("Input the Turing Machine csv file name: ").strip()

    # Load NTM from CSV
    ntm = NonDeterministicTuringMachine(ntm_file)

    # create output file and write TM name to it 
    output = open('output-'+ntm_file.replace('.csv','')+'.txt', 'a')
    output.write(f'Name of machine: {ntm.name}\n')

    count = 0
    while (True): 
        count += 1
        string = input("Input a string to run through the Turing machine. To end input input 'quit': ").strip()

        # if its a flag break 
        if string == "quit":
            break

        if string == "":
            input_string = '_'
        else: 
            input_string = string

        # ask for max_depth 
        max_depth = int(input("Input the max depth allowed: "))

        # print some info to the terminal 
        print()
        print(f'Name of machine: {ntm.name}')
        print(f'String {count} input: {input_string}')
        output.write(f'String {count} input: {input_string}\n')

        # call trace on the user input 
        ntm.trace_string(string, max_depth, output)
        print()
        output.write('\n')

    output.close()

if __name__ == '__main__':
    main()
    