def read_input_cnf(filename):
    variables = []
    clauses = []

    with open(filename, "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("c"):
                continue
            elif line.startswith("p cnf"):
                l = line.split()
                for i in range(int(l[2])):
                    variables.append(i + 1)
            elif line.endswith("0\n"):
                l = line.split()
                clause = []
                for i in l:
                    if i == "0":
                        break
                    clause.append(int(i))
                clauses.append(clause)

    return variables, clauses
