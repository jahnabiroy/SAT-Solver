from pysat.formula import CNF
from pysat.solvers import Solver


def solve_cnf(cnf_file):
    # Load the CNF file in DIMACS format
    cnf = CNF(from_file=cnf_file)

    # Create a SAT solver instance
    with Solver(bootstrap_with=cnf.clauses) as solver:
        if solver.solve():
            # If satisfiable, return the satisfying assignment
            model = solver.get_model()
            print("SATISFIABLE")
            print("Assignment:", model)
            return ("SAT", model)
        else:
            # If unsatisfiable, output UNSAT
            print("UNSATISFIABLE")
            return ("UNSAT", [])


def log_to_file(sat, content):
    with open("check.log", "a") as file:
        file.write(sat + "\n")
        file.write(str(content) + "\n")

    # Replace 'input.cnf' with the path to your .cnf file
    # for i in range(29):


cnf_file_path = f"test_28.cnf"
sat, model = solve_cnf(cnf_file_path)
log_to_file(sat, model)
