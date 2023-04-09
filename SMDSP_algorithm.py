from collections import defaultdict
import time
import random

def optimal_sp(S, x, y, w):
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
        print(f"path = {path}, weighted_cost = {weighted_cost}")

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
    for y in V:
        for x in V:
            if x != y:
                Q.extend(P[(x, y)])


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
                        else:
                            new_path_added[i] = True
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
    
    Q = []
    Q.append((v,))
    while Q:
        pi = Q.pop(0)
        LR = defaultdict(list)
        for value in L[pi]:
            LR[pi].append(value)

        for value in R[pi]:
            LR[pi].append(value)
            
        for pathkey, pathvalue in LR.items():
            for path in pathvalue:

                Q.append(path)
                
                if (path[0], path[-1]) in P and path in P[path[0], path[-1]]:
                    P[path[0], path[-1]].remove(path)

                if path in c:
                    del c[path]

                for subset in range(len(path)-1, 0, -1):
                    if path in L[path[subset:]]:
                        L[path[subset:]].remove(path)

                for subset in range(1, len(path)):
                    if path in R[path[:-subset]]:
                        R[path[:-subset]].remove(path)
    

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

    E_v = [tup for tup in c.keys() if v in tup]
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
                        if c[max_cost][i] < new_path_cost[i]:
                            new_path_added[i] = False
                        else:
                            new_path_added[i] = True
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
                        else:
                            new_path_added[i] = True
                else:
                    new_path_added = [True] * d

                if any(new_path_added):
                    P[(x, y_prime)].append(new_path)
                    L[(y, y_prime)].append(new_path)
                    R[path].append(new_path)
                    Q2.append(new_path)

    return P, L, R, c

# Define the graph, costs, and other parameters
# V = {1, 2, 3, 4, 5, 6}
# E = {(1, 2), (1, 3), (1, 4), (1, 5), (2, 6), (3, 6), (4, 6), (5, 6)}
# c = {
#     (1, 2): (2, 4, 6),
#     (1, 3): (4, 6, 2),
#     (1, 4): (6, 2, 4),
#     (1, 5): (3, 3, 3),
#     (2, 6): (1, 1, 1),
#     (3, 6): (1, 1, 1),
#     (4, 6): (1, 1, 1),
#     (5, 6): (1, 1, 1),
# }

#Vertices:
V = {i for i in range(1, 21)}

#Edges:
E = {(1, i) for i in range(2, 7)} | {(2, 7), (2, 8), (3, 8), (3, 9), (4, 9), (4, 10), (5, 10), (5, 11), (6, 11)} | {(7, 20), (8, 20), (9, 20), (11, 20)}

#Costs:
c = {
(1, 2): (5, 4, 6),
(1, 3): (4, 6, 2),
(1, 4): (6, 2, 4),
(1, 5): (3, 3, 3),
(1, 6): (5, 1, 1),
(2, 7): (1, 5, 1),
(2, 8): (1, 1, 5),
(3, 8): (2, 6, 1),
(3, 9): (6, 1, 2),
(4, 9): (1, 6, 2),
(4, 10): (1, 3, 3),
(5, 10): (3, 1, 3),
(5, 11): (3, 3, 1),
(6, 11): (4, 4, 4),
(7, 20): (1, 3, 2),
(8, 20): (2, 2, 6),
(9, 20): (6, 2, 4),
(11, 20): (5, 5, 5),
}


x, y = 1, 20
weights = (1, 1, 1)
# Compute the single-source paths and find the non-dominated path
P, L, R, c = single_source_paths_generator(V, E, c)
S = ols_every_vertice(V, P)
optimal_path, optimal_path_costs, sum_weighted_costs = optimal_sp(S, x, y, weights)


## Update Test: Run the Dynamic Algorithm
# v = 7
# c_prime = {
#     (2, v): (5, 5, 5),
#     (v, 20): (5, 5, 5),
# }
# P, L, R, c = dynamic_single_source_paths(V, E, c, v, c_prime)
# S = ols_every_vertice(V, P)
# optimal_path_d, optimal_path_costs_d, sum_weighted_costs_d = optimal_sp(S, x, y, weights)

# ## Insertion Test: Run the Dynamic Algorithm
v = 21
c_prime = {
    (2, v): (1, 1, 1),
    (v, 20): (1, 1, 1),
}
V = {i for i in range(1, 22)}
E = E | {(2,v), (v,20)}
P, L, R, c = dynamic_single_source_paths(V, E, c, v, c_prime)
S = ols_every_vertice(V, P)
optimal_path_d, optimal_path_costs_d, sum_weighted_costs_d = optimal_sp(S, x, y, weights)


print(f"[Static] The optimal path is: {optimal_path}, optimal path costs: {optimal_path_costs}, and sum weighted cost: {sum_weighted_costs}")
print(f"[Dynamic1] The optimal path is: {optimal_path_d}, optimal path costs: {optimal_path_costs_d}, and sum weighted cost: {sum_weighted_costs_d}")

# # while(1):
# #     time.sleep(0.5)
# #     v = 4
# #     c_prime = {
# #         (1, v): (1, 1, 1),
# #         (v, 6): (random.randint(3,10), random.randint(3,10), random.randint(3,10)),
# #     }
# #     if(random.randint(1,2) == 1):
# #         v = 3
# #         c_prime = {
# #             (1, v): (1, 2, 3),
# #             (v, 6): (random.randint(3,6), random.randint(3,6), random.randint(3,6)),
# #         }
# #     ## Run the Dynamic SS Algorithm - Second Run Through
# #     P, L, R, c = dynamic_single_source_paths(V, E, c, v, c_prime)
# #     S = ols_every_vertice(V, P)
# #     optimal_path_d2, optimal_path_costs_d2, sum_weighted_costs_d2 = optimal_sp(S, x, y, weights)
# #     print(f"[Dynamic3] The optimal path is: {optimal_path_d2}, optimal path costs: {optimal_path_costs_d2}, and sum weighted cost: {sum_weighted_costs_d2}")
