#returns a number from 1 to N (inclusive), denoting which variable to pick
import random

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

def initializeVars(N):
    vars = []
    for n in range(N): vars.append(Variable(random_boolean()))
    return vars

def create_3sat(C,N):
    vars = initializeVars(N)
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

# def walk_sat(clauses):



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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # testClauseEquality()
    testVars()


