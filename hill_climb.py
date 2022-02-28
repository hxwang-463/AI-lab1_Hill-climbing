import argparse
import json
from collections import Counter
import heapq
import random


class Basic_hill_climb:
    def __init__(self, initial, random_start, para, goal, error, neighbors, verbose, sideways, restarts):
        self.init_state = initial
        self.random_start = random_start
        self.para = para
        self.goal_function = goal
        self.error_function = error
        self.neighbors_function = neighbors
        self.verbose = verbose
        self.sideways = sideways
        self.restarts = restarts
    def run(self):
        state = self.init_state
        print("Start: " + str(state) + " = " + str(self.error_function(state, self.para)))
        sideways_tmp = self.sideways
        sideways_vl = [] # visited list
        while not self.goal_function(state, self.para):
            neighbors = []
            for s in self.neighbors_function(state, self.para):
                if self.verbose:
                    print(str(s) + " = " + str(self.error_function(s, self.para)))
                heapq.heappush(neighbors, (self.error_function(s, self.para), s))
            if neighbors[0][0] >= self.error_function(state, self.para):
                if neighbors[0][0] == self.error_function(state, self.para) and sideways_tmp > 0:
                    # go sideway
                    flag = 0
                    for _ in range(len(neighbors)):
                        temp_state = heapq.heappop(neighbors)
                        if temp_state[0] > self.error_function(state, self.para):
                            break
                        if temp_state[1] in sideways_vl:
                            continue
                        state = temp_state[1]
                        sideways_vl.append(state)
                        sideways_tmp -= 1
                        print("Choose(sideways): " + str(state) + " = " + str(self.error_function(state, self.para)))
                        flag=1
                        break
                    if flag==1:
                        continue
                if self.restarts > 0:
                    # restart
                    self.restarts -= 1
                    sideways_tmp = self.sideways
                    state = self.random_start(self.para)
                    print("Restarting with: " + str(state) + " = " + str(self.error_function(state, self.para)))
                    sideways_vl = [state]
                    continue
                # no found.
                print("Cannot restart. Search fail.")
                quit()
            state = neighbors[0][1]
            sideways_tmp = self.sideways
            print("Choose: " + str(state) + " = " + str(neighbors[0][0]))
            sideways_vl = [state]
        print("Goal: " + str(state) + " = " + str(self.error_function(state, self.para)))


def error_nqueen(state, _):
    error = 0
    same_row = dict(Counter(state))
    for _, value in same_row.items():
        if value > 1:
            error += value*(value-1)/2
    state_1 = [state[i]+i for i in range(len(state))]
    same_row = dict(Counter(state_1))
    for _, value in same_row.items():
        if value > 1:
            error += value*(value-1)/2
    state_2 = [state[i]-i for i in range(len(state))]
    same_row = dict(Counter(state_2))
    for _, value in same_row.items():
        if value > 1:
            error += value*(value-1)/2
    return error

def error_knapsack(state, data):
    value = 0
    weight = 0
    for item in state:
        value += data["Items"][item]["V"]
        weight += data["Items"][item]["W"]
    return max(weight - data["M"], 0) + max(data["T"] - value, 0)


def goal_nqueen(state, _):
    if error_nqueen(state, _) == 0:
        return True
    else:
        return False

def goal_knapsack(state, data):
    if error_knapsack(state, data) == 0:
        return True
    else:
        return False


def neighbors_nqueen(state, _):
    neighbors = []
    for i in range(len(state)):
        for j in range(len(state)):
            if j == state[i]:
                continue
            neighbor = state[:]
            neighbor[i] = j
            neighbors.append(neighbor)
    return neighbors

def neighbors_knapsack(state, data):
    neighbors = []
    # delete
    for i in range(len(state)):
        temp = state[:]
        del temp[i]
        neighbors.append(temp)
    # Add
    for item in data["Items"]:
        if not item in state:
            temp = state[:]
            temp.append(item)
            neighbors.append(temp)
    # replace
    for i in range(len(state)):
        for item in data["Items"]:
            temp = state[:]
            if not item in state:
                del temp[i]
                temp.append(item)
                neighbors.append(temp)
    return neighbors

def rondom_start_nqueen(num):
    state = [i for i in range(num)]
    random.shuffle(state)
    return state

def rondom_start_knapsack(data):
    state = []
    for item in data["Items"]:
        if random.randint(0,1):
            state.append(item)
    return state



def run_nqueen(num_queen, verbose, sideways, restarts):
    initial_state = [i for i in range(num_queen)]
    hill_climb = Basic_hill_climb(initial_state, rondom_start_nqueen, num_queen, goal_nqueen, error_nqueen, neighbors_nqueen, verbose, sideways, restarts)
    hill_climb.run()


def run_knapsack(data, verbose, sideways, restarts):
    initial_state = data["Start"]
    hill_climb = Basic_hill_climb(initial_state, rondom_start_knapsack, data, goal_knapsack, error_knapsack, neighbors_knapsack, verbose, sideways, restarts)
    hill_climb.run()




if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-N", type=int)
    group.add_argument("jsonfile", nargs='?')
    parser.add_argument("-verbose", help="verbose mode", action="store_true")
    parser.add_argument("-sideways", type=int, default=0)
    parser.add_argument("-restarts", type=int, default=0)
    args = parser.parse_args()

    if args.verbose:
        verbose = True
    else:
        verbose = False
    sideways = args.sideways
    restarts = args.restarts

    if args.N:
        num_queen = args.N
        run_nqueen(num_queen, verbose, sideways, restarts)
    else:
        try:
            with open(args.jsonfile, "r") as fp:
                json_data = json.load(fp)
            trans_data = {"T": json_data["T"], "M": json_data["M"]}
            if "Start" in json_data:
                trans_data["Start"] = json_data["Start"]
            else:
                trans_data["Start"] = []
            trans_data["Items"] = {}
            for item in json_data["Items"]:
                trans_data["Items"][item["name"]] = {"V":item["V"], "W":item["W"]}
        except:
            print("Bad file.")
            quit()

        run_knapsack(trans_data, verbose, sideways, restarts)



