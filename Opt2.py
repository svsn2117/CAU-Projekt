import numpy as np
import itertools as it
import random
import math

'''
    File name: Opt2.py
    Author: Hendrik E.
    Date created: 13.04.2018
    Date last modified: 20.04.2018
    Python Version: 3.6.3
'''

def opt2(DRIVING_TIMES, fidelity):
    merken = True
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
    mintime = compute_total_distance(Route, DRIVING_TIMES)
    Route = np.array(Route)
    RouteSlice = Route[1:(len(Route) - 1)]
    RouteOut = np.copy(Route)
    if(fidelity):
        entity = 25
    else:
        entity = 1
    for i in range (0,entity):
        # print(i)
        np.random.shuffle(RouteSlice)
        NewRoute = start_opt2(Route, DRIVING_TIMES, fidelity, merken)
        newmintime = compute_total_distance(NewRoute, DRIVING_TIMES)
        if(newmintime < mintime):
            mintime = newmintime
            RouteOut = np.copy(NewRoute)
    return RouteOut, mintime





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
    new_map = np.copy(best_map)
    new_map[i:j] = new_map[i:j][::-1]
    return new_map


def opt2Main(best_map, driving_map):
    distance = compute_total_distance(best_map, driving_map)
    _map = np.copy(best_map)
    for i in range(1, len(best_map)):
        for j in range(i + 1, len(best_map)):
            new_map = opt2Hilf(_map, i, j)
            new_distance = compute_total_distance(new_map, driving_map)
            if new_distance < distance:
                distance = new_distance
                _map = np.copy(new_map)
    return _map


def annealing(best_map, best_distance, driving_map, t0, tolerance, fidelity, merken):
    meandiff = tolerance + 1
    meandiffArr = np.array((best_map.shape[0]*best_map.shape[0]) * [1000])
    counter = 0
    ArrCounter = 0
    RandomArray = (np.shape(best_map)[0] * [0])
    temp = t0
    ran1 = -1
    ran2 = -1
    RanArrCount = -1
    tolerance = tolerance  / (np.dot((np.shape(best_map)[0]), (np.shape(best_map)[0])))

    while meandiff > tolerance:
        if(merken):
            randomConct = -1

            while randomConct in RandomArray:
                ran1 = np.random.randint(1, len(best_map))
                ran2 = np.random.randint(1, len(best_map))
                if ran1 > ran2:
                    swap = ran1
                    ran1 = ran2
                    ran2 = swap
                randomConct = int(str(ran1) + str(ran2))
            if RanArrCount > (len(RandomArray) - 2):
                RanArrCount = 0
            else:
                RanArrCount += 1
            RandomArray[RanArrCount] = randomConct
        else:
            ran1 = np.random.randint(1, len(best_map))
            ran2 = np.random.randint(1, len(best_map))
            if ran1 > ran2:
                swap = ran1
                ran1 = ran2
                ran2 = swap
        ran_map = opt2Hilf(best_map, ran1, ran2)
        ran_distance = compute_total_distance(ran_map, driving_map)
        #if (tuple(best_map) == tuple(np.array([0, 5, 2, 4, 8, 3, 6, 7, 9, 10, 1, 0]))):
            #print(ran1, ran2, ran_map, ran_distance, best_distance)
        delta = ran_distance - best_distance
        if(temp > 0.000000001):
            try:
                diff = 1 / (1 + math.exp((delta)/temp))
                if (fidelity):
                    temp = t0 * np.power(0.9, counter)
                    #temp = t0 / (math.log(counter + 2))
                else:
                    #temp = t0 * np.power(0.99, counter)
                    #temp = t0 / (math.log(counter + 2))
                    temp = t0 * np.power(0.8, counter)
            except OverflowError:
                if delta < 0:
                    diff = 1
                else:
                   diff = 0
        else:
            if delta < 0:
                diff = 1
            else:
                diff = 0
        counter += 1

        meandiff = (np.divide(np.sum(meandiffArr), meandiffArr.shape[0]))
        if diff > random.randrange(0, 1):
            meandiffArr[ArrCounter] = np.abs(delta)#meandiffArr[ArrCounter - 1] - delta)
            best_map = np.copy(ran_map)
            best_distance = ran_distance
        else:
            meandiffArr[ArrCounter] = 0

        if(ArrCounter < (meandiffArr.shape[0] - 1)):
            ArrCounter += 1
        else:
            ArrCounter = 0

    return best_map


def start_opt2(best_map, driving_map, fidelity, merken):
    best_map = opt2Main(best_map, driving_map)
    distance = compute_total_distance(best_map, driving_map)

    best_map = annealing(best_map, distance, driving_map, 10, 0.1, fidelity, merken)
    return best_map




def compute_total_distance(Route, driving_map):
    Totel_Time = 0
    for i in range(0, (len(Route) - 1)):
        Totel_Time += driving_map[Route[i]][Route[i+1]]

    return Totel_Time
