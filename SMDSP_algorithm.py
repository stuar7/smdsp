from collections import defaultdict
import time
import random

def optimal_sp(x, y, w):
    if (x, y) not in S:
        return None, None, None

    non_dominated_paths = S[(x, y)]
    min_weighted_cost = float('inf')
    optimal_path = None

    for path in non_dominated_paths:
        path_cost = c[path]
        weighted_cost = sum(cost * weight for cost, weight in zip(path_cost, w))

        if weighted_cost < min_weighted_cost:
            min_weighted_cost = weighted_cost
            optimal_path = path

    optimal_path_costs = c[optimal_path]
    sum_weighted_costs = min_weighted_cost
    return optimal_path, optimal_path_costs, sum_weighted_costs

def dominates(cost1, cost2):
    better_or_equal = all(a <= b for a, b in zip(cost1, cost2))
    strictly_better = any(a < b for a, b in zip(cost1, cost2))
    return better_or_equal and strictly_better

def ols(paths):
    non_dominated = []
    
    for path in paths:
        path_cost = c[path]
        if not any(dominates(c[other_path], path_cost) for other_path in paths):
            non_dominated.append(path)

    return non_dominated

def ols_every_vertice(V, paths):
    S = {}
    for x_v in V:
        for y_v in V:
            if x_v != y_v:
                S[(x_v, y_v)] = ols(paths[(x_v, y_v)])
    return S

def single_source_paths_generator(V, E, c):
    d = len(next((value for key, value in c.items())))
    P = defaultdict(list)
    L = defaultdict(list)
    R = defaultdict(list)

    for u in V:
        for v in V:
            if u != v:
                if (u, v) in c and c[(u, v)]:
                    if (u, v) not in P[(u, v)]:
                        P[(u, v)].append((u, v))
                        L[(v,)].append((u, v))
                        R[(u,)].append((u, v))
                if (v, u) in c and c[(v, u)]:
                    if (v, u) not in P[(v, u)]:
                        P[(v, u)].append((v, u))
                        L[(u,)].append((v, u))
                        R[(v,)].append((v, u))

    Q = []
    Q.extend(P)

    while Q:
        path = Q.pop(0)
        x, y = path[0], path[-1]
        for y_prime in V:
            if y_prime != x and (y, y_prime) in E:
                new_path = path + (y_prime,)
                new_path_added = [False] * d

                new_path_cost = tuple(a + b for a, b in zip(c[path], c[(y, y_prime)]))
                if new_path not in c:
                    c[new_path] = new_path_cost

                if bool(P[(x, y_prime)]):
                    for i in range(d):
                        max_cost = max(P[(x, y_prime)], key=lambda p: c[p][i])
                        if c[max_cost][i] < new_path_cost[i]:
                            new_path_added[i] = False
                            pass
                        else:
                            new_path_added[i] = True
                            pass
                else:
                    new_path_added = [True] * d

                if any(new_path_added):                    
                    P[(x, y_prime)].append(new_path)
                    L[(y, y_prime)].append(new_path)
                    R[path].append(new_path)
                    Q.append(new_path)
    return P, L, R, c

def dynamic_single_source_paths(V, E, c, v, c_prime):
    d = len(next((value for key, value in c.items())))
    E_v = [tup for tup in c.keys() if v in tup]
    Q = []
    Q.append((v,))
    while Q:
        pi = Q.pop(0)
        LR = defaultdict(list)
        for value in L[pi]:            
            if set((v,)).issubset(set(pi)):
                LR[pi].append(value)

        for value in R[pi]:            
            if set((v,)).issubset(set(pi)):
                LR[pi].append(value)

        for pathkey, pathvalue in LR.items():
            for path in pathvalue:

                Q.append(path)

                if pathkey in P and path in P[pathkey]:
                    P[pathkey].remove(path)
                
                if (path[0], path[-1]) in P and path in P[path[0], path[-1]]:
                    P[path[0], path[-1]].remove(path)
                 
                for subset in range(len(path)-1, 0, -1):
                    if path in L[path[subset:]]:
                        L[path[subset:]].remove(path)

                for subset in range(1, len(path)):
                    if path in R[path[:-subset]]:
                        R[path[:-subset]].remove(path)
    
        for k in list(L.keys()): 
            if not L[k]:
                L.pop(k, None) 

        for k in list(R.keys()): 
            if not R[k]:
                R.pop(k, None) 

    keys_to_delete = [e for e in c.keys() if v in e]
    for key in keys_to_delete:
        del c[key]
        if key in P:
            del P[key]

    for e in E:
        if(v in e):
            if v == e[0]:
                u = e[-1]
                c[(v, u)] = c_prime[(v, u)]
                P[(v, u)].append(e)
                L[(u,)].append(e)
                R[(v,)].append(e)
            else:
                u = e[0]
                u = e[0]
                c[(u, v)] = c_prime[(u, v)]
                P[(u, v)].append(e)
                L[(v,)].append(e)
                R[(u,)].append(e)

    Q1 = []
    Q2 = []

    for y in V:
        for x in V:
            if x != y:
                Q1.extend(P[(x, y)])

    while Q1:
        path = Q1.pop(0)
        x, y = path[0], path[-1]
        for y_prime in V:
            if y_prime != x and (y, y_prime) in E_v:
                new_path = path + (y_prime,)
                new_path_added = [False] * d
                new_path_cost = tuple(a + b for a, b in zip(c[path], c[(y, y_prime)]))
                if new_path not in c:
                    c[new_path] = new_path_cost
           
                if bool(P[(x, y_prime)]):
                    for i in range(d):
                        max_cost = max(P[(x, y_prime)], key=lambda p: c[p][i])
                        #print(f"max_cost: {max_cost}")
                        if c[max_cost][i] < new_path_cost[i]:
                            new_path_added[i] = False
                            pass
                        else:
                            new_path_added[i] = True
                            pass
                else:
                    new_path_added = [True] * d

                if any(new_path_added):
                    P[(x, y_prime)].append(new_path)
                    L[(y, y_prime)].append(new_path)
                    R[path].append(new_path)
                    Q2.append(new_path)

    while Q2:
        path = Q2.pop(0)
        x, y = path[0], path[-1]
        for y_prime in V:
            if y_prime != x and (y, y_prime) in E:
                new_path = path + (y_prime,)
                new_path_added = [False] * d

                new_path_cost = tuple(a + b for a, b in zip(c[path], c[(y, y_prime)]))
                if new_path not in c:
                    c[new_path] = new_path_cost

                if bool(P[(x, y_prime)]):
                    for i in range(d):
                        max_cost = max(P[(x, y_prime)], key=lambda p: c[p][i])
                        if c[max_cost][i] < new_path_cost[i]:
                            new_path_added[i] = False
                            pass
                        else:
                            new_path_added[i] = True
                            pass
                else:
                    new_path_added = [True] * d

                if any(new_path_added):
                    P[(x, y_prime)].append(new_path)
                    L[(y, y_prime)].append(new_path)
                    R[path].append(new_path)
                    Q2.append(new_path)

    return P, L, R, c

# Define the graph, costs, and other parameters
V = {1, 2, 3, 4, 5, 6}
E = {(1, 2), (1, 3), (1, 4), (2, 6), (2, 5), (3, 5), (4, 5), (5,6)}
c = {
    (1, 2): (1, 2, 3),
    (1, 3): (1, 2, 3),
    (1, 4): (1, 2, 3),
    (2, 5): (4, 5, 6),
    (3, 5): (5, 6, 4),
    (4, 5): (6, 4, 5),
    (2, 6): (13, 13, 13),
    (5, 6): (1, 1, 1),
}

# Compute the single-source paths and find the non-dominated path
P, L, R, c = single_source_paths_generator(V, E, c)
S = ols_every_vertice(V, P)

x, y = 1, 5
weights = (1, 1, 1)
optimal_path, optimal_path_costs, sum_weighted_costs = optimal_sp(x, y, weights)
v = 2
c_prime = {
    (1, 2): (5, 11, 5),
    (2, 5): (10, 12, 14),
    (2, 6): (1, 1, 1),
}

## Run the Dynamic SS Algorithm
P, L, R, c = dynamic_single_source_paths(V, E, c, v, c_prime)
S = ols_every_vertice(V, P)
weights = (1, 1, 1)
optimal_path_d, optimal_path_costs_d, sum_weighted_costs_d = optimal_sp(x, y, weights)
v = 4
c_prime = {
    (1, 4): (1, 1, 1),
    (4, 5): (3, 6, 6),
}

## Run the Dynamic SS Algorithm - Second Run Through
P, L, R, c = dynamic_single_source_paths(V, E, c, v, c_prime)
S = ols_every_vertice(V, P)

print(f"[Static] The optimal path is: {optimal_path}, optimal path costs: {optimal_path_costs}, and sum weighted cost: {sum_weighted_costs}")
print(f"[Dynamic1] The optimal path is: {optimal_path_d}, optimal path costs: {optimal_path_costs_d}, and sum weighted cost: {sum_weighted_costs_d}")
optimal_path_d2, optimal_path_costs_d2, sum_weighted_costs_d2 = optimal_sp(x, y, weights)
print(f"[Dynamic2] The optimal path is: {optimal_path_d2}, optimal path costs: {optimal_path_costs_d2}, and sum weighted cost: {sum_weighted_costs_d2}")

while(1):
    time.sleep(0.5)
    v = 4
    c_prime = {
        (1, 4): (1, 1, 1),
        (4, 5): (random.randint(3,10), random.randint(3,10), random.randint(3,10)),
    }
    if(random.randint(1,2) == 1):
        v = 3
        c_prime = {
            (1, 3): (1, 2, 3),
            (3, 5): (random.randint(3,6), random.randint(3,6), random.randint(3,6)),
        }
    ## Run the Dynamic SS Algorithm - Second Run Through
    P, L, R, c = dynamic_single_source_paths(V, E, c, v, c_prime)
    S = ols_every_vertice(V, P)
    optimal_path_d2, optimal_path_costs_d2, sum_weighted_costs_d2 = optimal_sp(x, y, weights)
    print(f"[Dynamic3] The optimal path is: {optimal_path_d2}, optimal path costs: {optimal_path_costs_d2}, and sum weighted cost: {sum_weighted_costs_d2}")
