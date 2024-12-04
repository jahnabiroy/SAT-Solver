import random


def frange(start, stop, step):
    while start < stop:
        yield round(start, 10)
        start += step


def generate_3sat_formula(N, r):
    L = int(r * N)

    clauses = []

    for _ in range(L):
        variables = random.sample(range(1, N + 1), 3)

        clause = [var if random.random() < 0.5 else -var for var in variables]
        clauses.append(clause)

    return clauses


def write_cnf_file(clauses, N, L, filename):
    with open(filename, "w") as f:
        f.write(f"p cnf {N} {L}\n")
        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")


N = 150
r_values = [round(r, 1) for r in frange(0, 6.0, 0.2)]

count = 0
for r in r_values:
    clauses = generate_3sat_formula(N, r)
    filename = f"test_{r}.cnf"
    write_cnf_file(clauses, N, len(clauses), filename)
    print(f"Generated CNF file: {filename}")
    count += 1
