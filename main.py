import random
from threading import Thread
import functools
import time
from statistics import median
import matplotlib.pyplot as plt

class Variable:
    def __init__(self, val):
        self.val = val

    def get_value(self):
        return self.val

    def set_value(self, val):
        self.val = val

class Literal:
    def __init__(self, var, negated):
        self.var = var
        self.negated = negated

    def evaluate(self):
        if self.negated:
            return not self.var.get_value()
        else:
            return self.var.get_value()

    def get_var(self):
        return self.var

    #overrides == operator
    def __eq__(self,other):
        return self.var == other.var and self.negated == other.negated

class Clause:
    def __init__(self, literals):
        self.literals = literals

    def evaluate(self):
        for literal in self.literals:
            if literal.evaluate():
                return True
        return False

    #overrides [] operator
    def __getitem__(self, item):
        return self.literals[item]

    def get_literals(self):
        return self.literals

    #overrides == operator
    def __eq__ (self, other):
        for literal in self.literals:
            if literal not in other.literals:
                return False
        return True


#Choose randomly from list, list can be a list of vars or a list of clauses
def pick_randomly(list):
    return random.choice(list)

#randomly returns boolean
def random_boolean():
    return random.choice([True, False])

#Create a random clause from variables in vars
def create_random_clause(vars):
    literals = []
    for i in range(3): literals.append(Literal(pick_randomly(vars), random_boolean()))
    return Clause(literals)

#Randomly create and assign N vars
def initializeVars(N):
    vars = []
    for n in range(N): vars.append(Variable(None))
    return vars

def shuffle_vars(vars):
    for var in vars: var.set_value(random_boolean())

def create_3sat(C, vars):
    clauses = []
    while (len(clauses) < C):
        clause = create_random_clause(vars)
        if clause not in clauses: clauses.append(clause)
    return clauses

def evaluate_3sat(clauses):
    for clause in clauses:
        if not clause.evaluate(): # if any clause is false
            return False
    return True

def count_satisfied(clauses):
    count = 0
    for clause in clauses:
        if clause.evaluate():
            count += 1
    return count

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print ('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

# This function will run indefinitely until a solution is found,
# outside process should time out appropriately when calling this function
# if a solution is found, num_flips is returned
@timeout(10)
def walk_sat(clauses, vars):
    shuffle_vars(vars)
    num_flips = 0
    while(1):
        if evaluate_3sat(clauses):
            return (num_flips) #normally we want to return vars, but here we want
                             # to know number of flips, we put that in q
        else:
            clause = pick_randomly(clauses)
            if random_boolean(): #If true, random flip
                literal = pick_randomly(clause.get_literals())
                var = literal.get_var()
                var.set_value(not var.get_value())
                num_flips += 1
            else: #else greedy
                literals = clause.get_literals()
                count_list = []
                for literal in literals:
                    var = literal.get_var()
                    var.set_value(not var.get_value())
                    count_list.append(count_satisfied(clauses))
                    var.set_value(not var.get_value()) #undo flip

                index_max = count_list.index(max(count_list))
                literal_to_flip = literals[index_max]
                var_to_flip = literal_to_flip.get_var()
                var_to_flip.set_value(not var_to_flip.get_value()) #flip greedy variable
                num_flips += 1


def graph(x, y, ylabel):
    # Note that even in the OO-style, we use `.pyplot.figure` to create the Figure.
    fig, ax = plt.subplots(figsize=(10, 5), layout='constrained')
    ax.plot(x, y, label=ylabel, marker='o', color='royalblue', mfc='orange')  # Plot some data on the Axes.
    ax.set_xlabel('C/N')  # Add an x-label to the Axes.
    ax.set_ylabel(ylabel)  # Add a y-label to the Axes.
    ax.set_title(ylabel + ' vs C/N')  # Add a title to the Axes.
    for i in range(len(x)):
        ax.annotate(f'({x[i]},{y[i]})', xy=(x[i],y[i]),xycoords='data',xytext=(-20,10),textcoords='offset points')

    plt.legend()
    plt.show()


#Testing functions
def testClauseEquality():
    a = Variable(True)
    b = Variable(False)

    clause = Clause([Literal(a, True), Literal(a, False)])
    clause2 = Clause([Literal(a, True), Literal(a, True)])

    clauses = [clause2]
    # print(clause == clause2)
    # print(clause in clauses)
    print(clause.evaluate())
    print(clause2.evaluate())
    # print(l1 == l2)
    # print(l1, l2)
    # print(clause.literals, clause2.literals)

def testVars():
    a = Variable(True)
    b = Variable(False)

    vars = [a, b]
    rand = pick_randomly(vars)
    print (rand,  vars)


def foo(i, q):
    time.sleep(2)
    q.put(i + 20)


def test_walk_sat():
    N = 3
    vars = initializeVars(N)
    problem = create_3sat(2, vars)
    try:
        num_flip = walk_sat(problem, vars)
        print(num_flip)

    except:
        print('fail')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #Create Problems
    N = 20
    vars = initializeVars(N)
    problems_dict = { } #key is c/n and value is an array of 50 problems

    for c in range(20, 201, 20):
        problems = []
        for i in range(50): problems.append(create_3sat(c, vars))
        problems_dict[c/N] = problems

    #Solve problems with walk_sat
    num_success = []
    median_flips = []
    for i in problems_dict:
        success = 0
        flips = []
        problems = problems_dict[i]

        j = 0
        for problem in problems:
            try:
                num_flip = walk_sat(problem, vars)
                print(f'i: {i}, j: {j}, num_flips: {num_flip}')
                success += 1
                flips.append(num_flip)
                j += 1
            except :
                print(f'i: {i}, j: {j}, Timeout!')
                j += 1

        num_success.append(success)
        if len(flips) == 0:
            median_flips.append(0)
        else:
            median_flips.append(median(flips))

    #graph result
    x = list(problems_dict.keys())
    graph(x, num_success, 'Num of Success')
    graph(x, median_flips, 'Median Flips')

    print(len(x))
    print(len(num_success))
    print(len(median_flips))

    print(x)
    print(num_success)
    print(median_flips)

