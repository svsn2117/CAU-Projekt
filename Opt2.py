import numpy as np
import itertools as it
import random
import math


def opt2(DRIVING_TIMES):

    NumberOfDest = np.shape(DRIVING_TIMES)[0]
    DRIVING_TIMES_COPY = np.array(DRIVING_TIMES).astype(np.int16)
    DELETE_ARRAY = [0]*(NumberOfDest)
    Route = [0]


    Index_Of_Lab = find_nearest_above(DRIVING_TIMES_COPY[0],0)
    Route.append(Index_Of_Lab)
    DRIVING_TIMES_COPY[:,0] = DELETE_ARRAY


    To_Find_Dest = NumberOfDest - 2

    while To_Find_Dest > 0:
        DRIVING_TIMES_COPY[:, Index_Of_Lab] = DELETE_ARRAY
        Index_Of_Lab = find_nearest_above(DRIVING_TIMES_COPY[Index_Of_Lab],0)

        Route.append(Index_Of_Lab)
        To_Find_Dest -= 1
    Route.append(0)

    print(compute_total_distance(Route, DRIVING_TIMES), "simple")

    Route1 = start_opt2(Route, DRIVING_TIMES)
    counter = 0
    supcounter = 0
    minTime = compute_total_distance(Route1, DRIVING_TIMES)
    print(minTime, "adv")
    # Route = [1,2,3,4,5,6,7,8,9,10]

    # for perm in it.permutations(Route):
    #    newRoute = [0] + list(perm) + [0]
     #   newtime = compute_total_distance(newRoute, DRIVING_TIMES)
     ##   counter += 1
      #  if newtime < minTime:
      #      minTime = newtime

       # if (counter > 100000):
       #     supcounter += 1
       #     counter = 0

   # print(minTime, "min")






def find_nearest_above(my_array, target):
    diff = my_array - target
    mask = np.ma.less_equal(diff, 0)
    # We need to mask the negative differences and zero
    # since we are looking for values above
    if np.all(mask):
        return None # returns None if target is greater than any value
    masked_diff = np.ma.masked_array(diff, mask)
    return masked_diff.argmin()


def opt2Hilf(best_map, i, j):
    new_map = best_map[:]
    new_map[i:j] = new_map[i:j][::-1]
    return new_map


def start_opt2(road_map, driving_map):
    best_map = road_map[:]
    best_distance = compute_total_distance(best_map, driving_map)
    new_distance = 0
    new_map = []
    coolingTemp = 1
    while coolingTemp >= 0.001:

        for i in range(1, len(best_map)):
            for j in range(i+1, len(best_map)):
                new_map = opt2Hilf(best_map, i, j)
                new_distance = compute_total_distance(new_map, driving_map)

            if new_distance < best_distance:
                best_distance = new_distance
                best_map = new_map

        ran1 = random.randint(1, len(best_map))
        ran2 = random.randint(1, len(best_map))
        if ran1 < ran2:
            new_map = opt2Hilf(best_map, ran1, ran2)
            new_distance = compute_total_distance(new_map, driving_map)
            print(new_distance, best_distance, new_distance * math.exp(-coolingTemp), "1")

            if (new_distance * math.exp(-coolingTemp)) < best_distance:
               # print("1>2")
                best_map = new_map
        else:
            #print(new_distance, best_distance, "2")
            new_map = opt2Hilf(best_map, ran2, ran1)
            new_distance = compute_total_distance(new_map, driving_map)
            if (new_distance * math.exp(-coolingTemp)) < best_distance:
                #print("2>1")
                best_map = new_map

        coolingTemp = coolingTemp * 0.999

    return best_map


def compute_total_distance(Route, driving_map):
    Totel_Time = 0
    for i in range(0, (len(Route) - 1)):
        Totel_Time += driving_map[Route[i]][Route[i+1]]

    return Totel_Time
