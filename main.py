import itertools
import xml.dom.minidom
import sys
from itertools import product
from read import *
import random
from collections import defaultdict, deque

class variable():
    # Constructor
    def __init__(self, name, values, parents,cpt):
        self.name = name
        self.values = [str(val).lower() for val in values]  #'true'/'false'
        self.parents = parents
        self.cpt = cpt

def parse_table(var, entries, bayes_net):
    distribution = {}
    if not var.parents:
        for i, val in enumerate(var.values):
            if () not in distribution:
                distribution[()] = {}
            distribution[()][val] = float(entries[i])
    else:
        value_lists = [bayes_net[par].values for par in var.parents]
        value_lists.append(var.values)
        tuple_list = list(product(*value_lists))
        for i, tup in enumerate(tuple_list):
            parent_assignments = tuple(tup[:-1])
            value = tup[-1]
            if parent_assignments not in distribution:
                distribution[parent_assignments] = {}
            distribution[parent_assignments][value] = float(entries[i])
    return distribution

# Exact enumeration from textbook pseudocode
# function ENUMERATION-ASK(X, e, bn) returns a distribution over X
# inputs: X, the query variable
#         e, observed values for variables E
#        bn, a Bayes net with variables vars
# Q(X)←a distribution over X, initially empty
# for each value xi of X do
#     Q(xi)←ENUMERATE-ALL(vars, exi )
#     where exi is e extended with X = xi
# return NORMALIZE(Q(X))

def enumeration_ask(X, e, bn):
    Q = {}

    for xi in bn[X].values:
        extended_e = e.copy()
        extended_e[X] = xi
        Q[xi] = enumerate_all(list(bn.keys()), extended_e, bn)
    return normalize(Q)

# function ENUMERATE-ALL(vars, e) returns a real number
#   if EMPTY?(vars) then return 1.0
#   V←FIRST(vars)
#   if V is an evidence variable with value v in e
#        then return P(v| parents(V)) × ENUMERATE-ALL(REST(vars), e)
#        else return Σv P(v| parents(V)) × ENUMERATE-ALL(REST(vars), ev)
#           where ev is e extended with V = v

def enumerate_all(vars, e,bn):
    if not vars:
        return 1.0

    V = vars[0]
    rest_vars = vars[1:]
    variable=bn[V]
    if V in e:
        value = e[V]
        parent_values = tuple(e[parent] for parent in variable.parents) if variable.parents else ()
        prob = variable.cpt.get(parent_values, {}).get(value, 0)
        return prob * enumerate_all(rest_vars, e,bn)
    else:
        total = 0
        for value in variable.values:
            extended_e = e.copy()
            extended_e[V] = value
            parent_values = tuple(extended_e[parent] for parent in variable.parents) if variable.parents else ()
            prob = variable.cpt.get(parent_values, {}).get(value, 0)
            total += prob * enumerate_all( rest_vars, extended_e,bn)
        return total

def normalize(Q):
    total = sum(Q.values())
    if total == 0:
        print("Error: Total probability is zero. Likely an issue with probability retrieval or assignments.")
        return

    # Normalize probabilities
    normalizedQ={}
    for key,value in Q.items():
        normalizedQ[key] =value/ total
    return normalizedQ

#Page438 pseudocode
def rejection_sampling(X, e, bayes_net, N, sorted_vars):
    counts = {value: 0 for value in bayes_net[X].values}  #initialize counts
    valid_samples = 0

    for i in range(N):
        sample = prior_sample(bayes_net, sorted_vars)  #generate sample
        if is_consistent(sample, e):  #check consistency with evidence
            counts[sample[X]] += 1
            valid_samples += 1
    # # Debugging
    # print(f"Total valid samples: {valid_samples} / {N}")
    # print(f"Counts before normalization: {counts}")
    return normalize(counts)

def prior_sample(bayes_net, sorted_vars):
    sample = {}
    for var in sorted_vars:
        variable = bayes_net[var]
        parent_values = tuple(sample[parent] for parent in variable.parents) if variable.parents else ()
        prob_dist = variable.cpt[parent_values]
        sample[var] = weighted_sample(prob_dist)
    return sample

def weighted_sample(prob_dist):
    r = random.random()
    cumulative = 0.0
    for value, prob in prob_dist.items():
        cumulative += prob
        if r <= cumulative:
            return value
    return list(prob_dist.keys())[-1]

def is_consistent(sample, evidence):
    for var, value in evidence.items():
        if sample.get(var) != value:
            return False
    return True

#sort on the bn variables.
def topological_sort(bayes_net):
    #Compute in-degree for each variable
    in_degree = {var: 0 for var in bayes_net}
    for var in bayes_net:
        for parent in bayes_net[var].parents:
            in_degree[var] += 1
    #Initialize queue with nodes having in-degree 0
    queue = deque([var for var in bayes_net if in_degree[var] == 0])
    sorted_vars = []

    while queue:
        current = queue.popleft()
        sorted_vars.append(current)
        for var in bayes_net:
            if current in bayes_net[var].parents:
                in_degree[var] -= 1
                if in_degree[var] == 0:
                    queue.append(var)
    if len(sorted_vars) != len(bayes_net):
        raise ValueError("Cycle detected in Bayesian network.")

    return sorted_vars

def main():
    if len(sys.argv) < 2:
        print("Error: No XML file provided.")
        sys.exit(1)

    doc = xml.dom.minidom.parse(sys.argv[1])

    (vars, domains) = vars_and_domains(doc)
    (tables, parents) = tables_and_parents(doc)

    #print("Tables for all variables:")
    #for var, table in tables.items():
        #print(f"{var}: {table}")

    bayes_net = {}
    for var in vars:
        values = domains[var]
        parent_list = parents[var] if parents[var] is not None else []
        bayes_net[var] = variable(var, values, parent_list, None)  #Initialize without CPT

    for var in vars:
        bayes_net[var].cpt = parse_table(bayes_net[var], tables[var], bayes_net)

    sorted_vars = topological_sort(bayes_net)
    # print(f"Topological order of variables: {sorted_vars}")  #Debugging info

    query_var = input("Enter the query variable (e.g., 'B'): ").strip()
    evidence = {}
    print("Enter evidence variables and values one by one (e.g., J=true, M=false). Leave blank and press enter to finish.")
    while True:
        evidence_input = input("Evidence (Variable=Value): ").strip()
        if not evidence_input:
            break
        var, value = evidence_input.split('=')
        evidence[var.strip()] = value.strip().lower()

    method = input("Choose inference method: (1) Exact (2) Approximate (Rejection Sampling): ").strip()

    if method == "1":
        result = enumeration_ask(query_var, evidence, bayes_net)
        result_str = ', '.join(f"{key}: {round(value, 4)}" for key, value in result.items())
        print(
            f"Exact Inference: P({query_var} | {', '.join(f'{k}={v}' for k, v in evidence.items())}): {{{result_str}}}")
    elif method == "2":
        num_samples = int(input("Enter the number of samples for rejection sampling: ").strip())
        result = rejection_sampling(query_var, evidence, bayes_net, num_samples, sorted_vars)
        result_str = ', '.join(f"{key}: {round(value, 4)}" for key, value in result.items())
        print(
            f"Approximate Inference (Rejection Sampling): P({query_var} | {', '.join(f'{k}={v}' for k, v in evidence.items())}): {{{result_str}}}")
    else:
        print("Invalid choice. Please choose 1 or 2.")

if __name__ == "__main__":
    main()