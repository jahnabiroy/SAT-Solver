import random
import sys
import time
from read_cnf import read_input_cnf


class ImplicationNode:
    def __init__(self, variable, value, level) -> None:
        self.variable = variable
        self.value = value
        self.level = level
        self.predecessors = []
        self.successors = []


class ImplicationGraph:
    def __init__(self) -> None:
        self.adjacency_level_list = {}

    def add_node(self, node):
        if node.level not in self.adjacency_level_list:
            self.adjacency_level_list[node.level] = []
        self.adjacency_level_list[node.level].append(node)

    def add_predecessor(self, node1, node2):
        node1.predecessors.append(node2)
        node2.successors.append(node1)

    def get_adjacency_list(self):
        return self.adjacency_level_list

    def print_graph(self):
        for keys in self.adjacency_level_list.keys():
            for values in self.adjacency_level_list[keys]:
                print(values.variable, values.value, values.level, " ", end=" ")
            print()

    def print_pred_succ(self):
        for keys in self.adjacency_level_list.keys():
            for values in self.adjacency_level_list[keys]:
                print(
                    "Variable: ",
                    values.variable,
                )
                print("Predecessors: ", end=" ")
                for pred in values.predecessors:
                    print(pred.variable, pred.value, pred.level, " ", end=" ")
                print("Successors: ", end=" ")
                for succ in values.successors:
                    print(succ.variable, succ.value, succ.level, " ", end=" ")
                print()


class CDCLSolver:
    def __init__(self, variables, F, m) -> None:
        self.variables = variables
        self.F = F
        self.model = m
        self.conflicts = 0
        self.backtrack_history = {}
        self.score_of_literals = {}
        self.clause_learnt = []
        self.current_model = m
        self.conflict_level = 0
        self.repeating_learnt_clauses = 0
        self.random_time = 0

    def unit_propagation(self, g):
        """
        remove all clauses with pure literals and if unit clause then remove all clauses with that literal
        this function is like the cleaner function. dont include in the implication graph.
        """
        unit_literals = []
        for clause in self.F:
            if len(clause) == 1:
                unit_literals.append(clause[0])

        for unit in unit_literals:
            if unit > 0 and self.model[unit][1] == "U":
                g.add_node(ImplicationNode(unit, 1, 1))
                self.model[abs(unit)] = [1, "FORCED", 1]
            elif unit < 0 and self.model[abs(unit)][1] == "U":
                g.add_node(ImplicationNode(-unit, 0, 1))
                self.model[abs(unit)] = [0, "FORCED", 1]

        literals = []
        for clause in self.F:
            for var in clause:
                if var not in literals:
                    literals.append(var)

        pure_literals = []
        for literal in literals:
            if literal in literals and -literal not in literals:
                pure_literals.append(literal)

        for l in pure_literals:
            if l > 0 and self.model[l][1] == "U":
                g.add_node(ImplicationNode(l, 1, 1))
                self.model[l] = [1, "FORCED", 1]
            if l < 0 and self.model[abs(l)][1] == "U":
                g.add_node(ImplicationNode(-l, 0, 1))
                self.model[abs(l)] = [0, "FORCED", 1]

        for clause in self.F:
            if len(clause) == 1:
                if [-clause[0]] in self.F:
                    return None, True

        return None, False

    def variable_ordering(self, count):
        if count == 256:
            for keys in self.score_of_literals.keys():
                self.score_of_literals[keys] /= 2
            count = 0
        if count == 1:
            all_vars = [item for sublist in self.F for item in sublist]
            all_vars_set = set(all_vars)
            for vars in all_vars_set:
                self.score_of_literals[vars] = all_vars.count(vars)

            sorted_vars = sorted(
                self.score_of_literals.items(), key=lambda x: x[1], reverse=True
            )

            for var, _ in sorted_vars:
                if self.model[abs(var)][1] == "U":
                    if var > 0:
                        self.model[var][0] = 1
                    else:
                        self.model[-var][0] = 0
                    self.model[abs(var)][1] = "A"

            sorted_variables = [abs(var) for var, _ in sorted_vars]
            sorted_variables = list(set(sorted_variables))
            return sorted_variables

        else:
            recent_learnt_clause = self.clause_learnt[-1]
            for var in recent_learnt_clause:
                self.score_of_literals[var] += 1

            sorted_vars = sorted(
                self.score_of_literals.items(), key=lambda x: x[1], reverse=True
            )

            for var, _ in sorted_vars:
                if self.model[abs(var)][1] == "U":
                    if var > 0:
                        self.model[var][0] = 1
                    else:
                        self.model[-var][0] = 0
                    self.model[abs(var)][1] = "A"

            sorted_variables = [abs(var) for var, _ in sorted_vars]
            sorted_variables = list(set(sorted_variables))
            return sorted_variables

    def random_ordering(self):
        vars_list = self.variables.copy()
        random.shuffle(vars_list)
        bin_list = [0, 1]
        for var in vars_list:
            if self.model[var][1] == "U":
                self.model[var][0] = random.choice(bin_list)
                self.model[var][1] = "A"

        return vars_list

    def get_learnt_clauses(self, uip_node):
        learnt_clauses = []
        successors_for_uip_node = []
        while uip_node.successors:
            for succ in uip_node.successors:
                successors_for_uip_node.append(succ.variable)
                for pred in succ.predecessors:
                    if self.model[pred.variable][0] == 1:
                        if (
                            -pred.variable not in learnt_clauses
                            and pred.variable not in successors_for_uip_node
                        ):
                            learnt_clauses.append(-pred.variable)
                    else:
                        if (
                            pred.variable not in learnt_clauses
                            and pred.variable not in successors_for_uip_node
                        ):
                            learnt_clauses.append(pred.variable)
            uip_node = succ
        return learnt_clauses

    def add_learnt_clauses(self, clause):
        self.clause_learnt.append(clause)
        self.F.append(clause)

    def print_model(self):
        m = []
        for key in self.model.keys():
            if self.model[key][0] == 1:
                m.append(key)
            else:
                m.append(-key)

        return m

    def forced_ordering(self):
        variables = [7, 8, 9, 1, 2, 4, 5, 3, 6]
        self.model[7] = [0, "A", 0]
        self.model[8] = [0, "A", 0]
        self.model[9] = [0, "A", 0]
        self.model[1] = [0, "A", 0]
        self.model[2] = [0, "A", 0]
        self.model[4] = [0, "A", 0]
        self.model[5] = [0, "A", 0]
        self.model[3] = [0, "A", 0]
        self.model[6] = [0, "A", 0]
        return variables

    def find_paths_to_root(self, graph, node, path=[], all_paths=[]):
        path.append(node.variable)
        if not node.predecessors:
            all_paths.append(list(path))
        else:
            for parent in node.predecessors:
                if parent.level == node.level:
                    self.find_paths_to_root(graph, parent, path, all_paths)

        path.pop()
        return all_paths

    def find_intersection(self, all_paths):
        if not all_paths:
            return []
        intersection_result = set(all_paths[0])
        for path in all_paths[1:]:
            intersection_result.intersection_update(path)
        return list(intersection_result)

    def find_UIP(self, graph, level, conflict_clause):
        conflict_nodes = []
        for node in graph[level]:
            for var in conflict_clause:
                if node.variable == abs(var):
                    conflict_nodes.append(node)

        all_paths = []
        for nodes in conflict_nodes:
            paths = self.find_paths_to_root(graph, nodes, [], [])
            all_paths.extend(paths)

        intersection = self.find_intersection(all_paths)
        uip_nodes = []
        for vars in intersection:
            for nodes in graph[level]:
                if nodes.variable == vars:
                    uip_nodes.append(nodes)
        return uip_nodes

    def backtrack(self, graph, level, conflict_clause):
        stack = []
        for node in graph[level]:
            stack.append(node)
        visited = set()

        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)

            if not node.predecessors:
                conflict_clause.append(node)
            else:
                for pred in node.predecessors:
                    if pred not in visited:
                        stack.append(pred)

        return conflict_clause

    def log_to_file(self, sat, content):
        with open("output_two_clause.log", "a") as file:
            file.write(sat + "\n")
            file.write(str(content) + "\n")

    def solve_cdcl(self):
        count = 0
        while True:
            count += 1
            model, conflict = self.cdcl(count)

            if model is None:
                if conflict:
                    self.log_to_file("UNSAT (TIME EXCEEDED)", [])
                    return None
                print("UNSAT")
                self.log_to_file("UNSAT", [])
                return None

            self.current_model = model

            if not conflict:
                print("SAT")
                print(self.print_model())
                m = self.print_model()
                self.log_to_file("SAT", m)
                return model

    def two_clause(self):
        variables_in_two_clauses = {}
        for clause in self.F:
            if len(clause) == 2:
                for var in clause:
                    if var in variables_in_two_clauses:
                        variables_in_two_clauses[var] += 1
                    else:
                        variables_in_two_clauses[var] = 1

        sorted_vars = sorted(variables_in_two_clauses.items(), key=lambda x: x[1])
        for vars, count in sorted_vars:
            if self.model[abs(vars)][1] == "U":
                if vars > 0:
                    self.model[vars][0] = 1
                else:
                    self.model[-vars][0] = 0
                self.model[abs(vars)][1] = "A"

        sorted_variables = [abs(var) for var, _ in sorted_vars]
        sorted_variables = list(set(sorted_variables))

        all_vars = [item for sublist in self.F for item in sublist]
        all_vars_set = set(all_vars)
        for vars in all_vars_set:
            self.score_of_literals[vars] = all_vars.count(vars)

        sorted_vars = sorted(
            self.score_of_literals.items(), key=lambda x: x[1], reverse=True
        )

        for var, _ in sorted_vars:
            if abs(var) not in sorted_variables:
                sorted_variables.append(abs(var))
            if self.model[abs(var)][1] == "U":
                if var > 0:
                    self.model[var][0] = 1
                else:
                    self.model[-var][0] = 0
                self.model[abs(var)][1] = "A"
        return sorted_variables

    def cdcl(self, count):
        m = {key: [0, "U", 0] for key in self.variables}
        self.conflict_level = 0
        self.model = m
        g = ImplicationGraph()
        _, conflict = self.unit_propagation(g)
        if conflict:
            return None, False

        variables_ordered = self.two_clause()

        level = 0
        flag = False
        direct_conflict_clause = []
        for i in range(len(variables_ordered)):
            if (
                self.model[variables_ordered[i]][1] != "DONE"
                and self.model[variables_ordered[i]][1] != "FORCED"
            ):
                level += 1
                x = ImplicationNode(
                    variables_ordered[i], self.model[variables_ordered[i]][0], level
                )
                self.model[variables_ordered[i]][2] = level
                self.model[variables_ordered[i]][1] = "DONE"
                g.add_node(x)

            for clause in self.F:
                ans = 0
                count_vars = 0
                for vars in clause:
                    if (
                        self.model[abs(vars)][1] == "DONE"
                        or self.model[abs(vars)][1] == "FORCED"
                    ):
                        if vars > 0:
                            ans = ans or self.model[abs(vars)][0]
                        else:
                            ans = ans or (self.model[abs(vars)][0] ^ 1)
                        count_vars += 1
                if count_vars == len(clause) - 1 and ans == 0:
                    predecessors = []
                    forced_decision = 0
                    max_level = level
                    for vars in clause:
                        if (
                            self.model[abs(vars)][1] == "DONE"
                            or self.model[abs(vars)][1] == "FORCED"
                        ):
                            node_level = self.model[abs(vars)][2]
                            current_graph = g.get_adjacency_list()
                            node1 = next(
                                (
                                    x
                                    for x in current_graph[node_level]
                                    if x.variable == abs(vars)
                                ),
                                None,
                            )
                            if node1 != None:
                                if max_level == level:
                                    max_level = node1.level
                                max_level = max(max_level, node1.level)
                                predecessors.append(node1)
                        if (
                            self.model[abs(vars)][1] != "DONE"
                            and self.model[abs(vars)][1] != "FORCED"
                        ):
                            forced_decision = vars
                    if forced_decision > 0:
                        self.model[abs(forced_decision)] = [1, "FORCED", max_level]
                    else:
                        self.model[abs(forced_decision)] = [0, "FORCED", max_level]
                    x = ImplicationNode(
                        abs(forced_decision),
                        self.model[abs(forced_decision)][0],
                        max_level,
                    )
                    g.add_node(x)
                    for pred in predecessors:
                        g.add_predecessor(x, pred)

                if count_vars == len(clause) and ans == 0:
                    flag = True
                    self.conflicts += 1

                    for vars in clause:
                        if self.model[abs(vars)][1] == "FORCED":
                            self.conflict_level = max(
                                self.conflict_level, self.model[abs(vars)][2]
                            )
                    direct_conflict_clause = clause
                    if self.conflicts == 10000:
                        print("Limit Exceeded")
                        return None, True
                    break
            if flag:
                break
        if flag:
            graph = g.get_adjacency_list()
            uip_nodes = self.find_UIP(
                graph, self.conflict_level, direct_conflict_clause
            )

            if not uip_nodes:
                conflict_clause = []
                conflict_clause = self.backtrack(
                    graph, self.conflict_level, conflict_clause
                )
                learnt_clause = []

                for clause in conflict_clause:
                    if clause.value == 1:
                        learnt_clause.append(-clause.variable)
                    else:
                        learnt_clause.append(clause.variable)

                if learnt_clause in self.F:
                    self.repeating_learnt_clauses += 1
                if learnt_clause == []:
                    return None, False
                self.add_learnt_clauses(learnt_clause)
                return self.model, True

            first_uip = uip_nodes[0]
            last_uip = uip_nodes[-1]
            learnt_clause = self.get_learnt_clauses(last_uip)
            learnt_clause_first = self.get_learnt_clauses(first_uip)

            if learnt_clause in self.F and learnt_clause_first in self.F:
                self.repeating_learnt_clauses += 1
                if self.repeating_learnt_clauses == 10:
                    self.repeating_learnt_clauses = 0
            if learnt_clause == [] and learnt_clause_first == []:
                print("Got Empty Clause")
                return None, False
            if learnt_clause == []:
                learnt_clause = learnt_clause_first
            if learnt_clause in self.F:
                if learnt_clause_first != [] and self.repeating_learnt_clauses < 5:
                    learnt_clause = learnt_clause_first
            self.add_learnt_clauses(learnt_clause)

            return self.model, True
        return self.model, False


def main(filename):
    variables, F = read_input_cnf(filename)
    default_value = 0
    m = {key: [default_value, "U", 0] for key in variables}
    solved = CDCLSolver(variables, F, m)
    solved.solve_cdcl()
    # print(solved.solve_cdcl())


if __name__ == "__main__":
    # for i in range(29):
    #     start_time = time.time()
    #     main(f"test_{i}.cnf")
    #     end_time = time.time()
    #     print(f"Time taken for test_{i}.cnf: {end_time - start_time} seconds")
    main(sys.argv[1])
