# Some Infos and Ideas:
# The kartisian space calculated from the drivingTime Matrix is n-1 dimensional.
# I have tryed to write my own algorithems to get the Problem down to 2 Dimensions: (__distanceMatrixToPoints_onlyFirstThree and __distanceMatrixToPoints_midEuclid)
# The mid Euclid dose not work really well (maybe because the first points set in 2d are completely wrong, or an error in the code (i havend completely checked its correctness))
# The onlyFirstThree Alg. works suprisingly better, although it only considered the distances to the first three points
# I found the Problem under the Name "Distance geometry problem with inaccurate distances":
# Maybe the Alg. "Solving the molecular distance geometry problem with inaccurate distance data" is better, but it looks pretty complicated: https://bit.ly/2H9bMGX (minimize Function with SciPy: https://bit.ly/2qHJ58P)
# Other possible techniques: Hierarchical method and  SOM and Gas NN (= Neural gas) (Algs. from https://bit.ly/2HKDS8j)
import numpy as np
import copy
import random
import matplotlib.pyplot as plt
from sklearn.metrics import pairwise_distances_argmin
#from sklearn.cluster import KMeans
#from sklearn.cluster import AgglomerativeClustering
'''
    File name: Clustering.py
    Author: Sebastian Nichtern
    Date created: 13.04.2018
    Date last modified: 26.06.2018
    Python Version: 3.6.3
'''


#############   GLOBAL VARS   #############
optimalSecondPoint = None
PLOT_HERE = False


'''   DIMENSION REDUCTION   '''

def __distanceMatrixToPointsIfExact(A):
    # https://math.stackexchange.com/questions/156161/finding-the-coordinates-of-points-from-distance-matrix
    # this dose not work in this case because the matrix consists of Travletimes, not distances
    M = (np.square(A[0, :]) + np.square(np.transpose([A[:,0]])) - np.square(A)) / 2
    u, s, v = np.linalg.svd(M) # Singulärwertezerlegung
    rank = np.sum(s > 1e-10) # Alternative: np.linalg.matrix_rank(M).  1e-10 = Threshold where it counts as a zero
    # rank2 =
    points = []
    for i, singu in enumerate(s):
        if singu > 1e-10:
            points.append((singu*v[i]))
    points = np.array(points)
    return points

def __distanceMatrixToPoints_onlyFirstThree(A, secondPoint=1):
    # Using 2 initial Points and locate them in space, calculate all other point locations using there distances
    points = np.zeros((A.shape[1],2))
    # first fixed point is 0,0 (it's the Lab)
    # Second point as far away as possible from the first one: (https://bit.ly/2qHwZg4)
    # secondPoint = 1 # second fixed point at (x=0, y= 1 or distance to doc whos farest away)
    # if farestPoint:
    #     secondPoint = np.argmax(A[0,1:])+1 # exclude first zero for argmin # argmax for index (armax for value)
    points[secondPoint] = [0,A[0,secondPoint]]

    for p in range(1,len(points)): # from third point to last point
        if p == secondPoint: # this Point has allready been used above
            continue
        d13 = A[0,p] # point 3 changes each loop -> used p instead of 3
        d23 = A[secondPoint,p]
        x1 = 0
        y1 = 0
        x2 = 0 # actually not needed
        y2 = A[0,secondPoint] # distance to the second Point = y2-coordinate
        # Calculate y3 and x3 (formulars generated with wolfram Alpha):
        y3 = np.divide((-np.square(d13)+np.square(d23)+np.square(y1)-np.square(y2)), 2*(y1-y2))
        x3 = x1+np.sqrt(-np.square(y3)+np.square(d13)+2*y3*y1-np.square(y1))

        # decide if x3 is negative or positive. It depends on the best Distance (+ or -) to the Distence in A:
        if p > 2: # only now the third point is defined
            dPositive = np.sqrt(np.square(x3 - points[2][0]) + np.square(y3 - points[2][1]))
            dNegative = np.sqrt(np.square(-x3 - points[2][0]) + np.square(y3 - points[2][1]))
            dPositive_DiffToA = np.abs(dPositive - A[2,p])
            dNagative_DiffToA = np.abs(dNegative - A[2,p])
            if dNagative_DiffToA < dPositive_DiffToA:
                x3 = -x3
        # and save the calculated location:
        points[p] = [x3,y3]
    return points

def __distanceMatrixToPoints_midEuclid(A):
    # Places point after point in the 2D space at the location with mid best fitting Range to all places points
    # can use random points and optimization using the __pointsToDistanceMatrix() and __matrixDifference() functions

    # Problem mit diesem Alg: Punkte werden stueck fuer stueck hinzugefuegt, nur Abstaende zu bereits
    # gesetzten Punkten werden somit beruecksichtigt. Neu gesetzte Punkte beruecksichtigen dann zwar
    # die position der alten, wenn diese aber schon voellig falsch liegen nuetzt das auch nichts mehr

    points = np.zeros((A.shape[1], 2))
    order = list(range(1,A.shape[1]))
    random.shuffle(order) # random order in witch points are added
    points[1] = [0, A[0,order[-1]]] # first point (Lab) was (0,0), second point now placed

    for lastAddedPoint, newPoint in enumerate(order[1:]):
        # lastAddesPoint+2 is needed for the number of elements in points that are used for the approximation
        # 1. Suchraum bestimmen (Abstand * 1.5 von allen Punkten aus)
        xSearchSpace = [0,0] # min and max x
        ySearchSpace = [0,0] # min and max y
        ENLARGING_FACTOR = 1.5
        for oldPoint in range(lastAddedPoint+2):
            # distance to toPoint from element * 1,5
            xMin = (points[oldPoint][0] - A[newPoint,oldPoint]) * ENLARGING_FACTOR
            xMax = (points[oldPoint][0] + A[newPoint,oldPoint]) * ENLARGING_FACTOR
            yMin = (points[oldPoint][1] - A[newPoint,oldPoint]) * ENLARGING_FACTOR
            yMax = (points[oldPoint][1] + A[newPoint,oldPoint]) * ENLARGING_FACTOR
            if xSearchSpace[0] >= xMin:
                xSearchSpace[0] = xMin
            if xSearchSpace[1] <= xMax:
                xSearchSpace[1] = xMax
            if ySearchSpace[0] >= yMin:
                ySearchSpace[0] = yMin
            if ySearchSpace[1] <= yMax:
                ySearchSpace[1] = yMax

        # 2. Im suchraum minimum der Funktion (Abstaende zu allen nachbarn) Finden
        # Entweder brute force oder monte carlo oder Alternativer ansatz:
        # Diskretisierung in 100ter schritte und dort wo die besten ergebnisse gefunden
        # wurden anschließend nochmal mit kleineren schritten (z.b. 1ner) suchen

        # Discreted Brute Force (STEPSIZE):
        STEPSIZE = 200 # higher = faster
        bestPosition = [xSearchSpace[0], ySearchSpace[0]]
        lowermostDistanceSum = 10000000000
        for x in np.arange(xSearchSpace[0],xSearchSpace[1],STEPSIZE):
            for y in np.arange(ySearchSpace[0],ySearchSpace[1],STEPSIZE):
                distances = [] # distances to all already set points
                for oldPoint in range(lastAddedPoint + 2):
                    d = np.sqrt(np.square(x - points[oldPoint][0]) + np.square(y - points[oldPoint][1]))
                    if d < A[newPoint,oldPoint]: # if the distance is gone below the min distance from A
                        d += 1.5*(A[newPoint,oldPoint] - d) # then add the overstepped part to the distance. -> pseudodistance
                        # this way, going nearer to points dose not count as better solutions
                    distances.append(d)

                if sum(distances) < lowermostDistanceSum:
                    bestPosition = [x,y]
                    lowermostDistanceSum = sum(distances)
        print(str(lastAddedPoint+2) + ": " + str(bestPosition))
        points[lastAddedPoint+2] = bestPosition

        # Alternativer alg (Einfacher und ungenauer):
        # 2 zufaellige nachbarn auswaehlen und von diesen über den Abstand mit der formel aus
        # __distanceMatrixToPoints_onlyFirstTwo die Position bestimmen.

    return points

def __pointsToDistanceMatrix(p):
    dist = np.zeros((p.shape[0],p.shape[0])).astype(np.int)
    for i in range(dist.shape[0]):
        for j in range(dist.shape[1]):
            dist[i,j] = np.round(np.sqrt(np.square(p[j,0]-p[i,0])+np.square(p[j,1]-p[i,1])),0).astype(np.int)
    return dist

def __matrixDifference(A,B):
    # Only for 2D arrays!
    # Hint this module: works only if the points have the same order in both matreces
    err = 0
    if(A.shape == B.shape):
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                err += np.abs(A[i,j]-B[i,j])
    else:
        print("A and B must have the same shape (in __matrixDifference(A,B))")
    return err

def __to2D(A):
    # Iterate through all Points and choose the best second Point:
    global optimalSecondPoint
    if not optimalSecondPoint: # if its not allready calculated for this problem...
        optimalSecondPoint = 1
        minErr = 100000000000
        for secondPoint in range(1, A.shape[1]):
            points = __distanceMatrixToPoints_onlyFirstThree(A, secondPoint)  # n-1 Dimensions to 2D (err(10) = 146060, err(30) = 2223666)
            D = __pointsToDistanceMatrix(points)  # Distances in the model ([n-1]D to 2D)
            err = __matrixDifference(A, D)  # compare original distances and projected distances in 2D
            # print("Point: "+str(secondPoint)+" err: " + str(err))
            # plt.scatter(points[:,0],points[:,1], c=np.random.rand(3,)) # Plot from all Points as second Points
            # plt.scatter(0,0,color="red")
            # plt.annotate("Lab",(0,0))
            if err < minErr:
                minErr = err
                optimalSecondPoint = secondPoint
                # plt.scatter(points[:, 0], points[:, 1], c=np.random.rand(3, ))
                # for i,p in enumerate(points):
                #     plt.annotate(str(i), (p[0], p[1]))
                # plt.annotate("err: "+str(err),(points[2, 0], points[2, 1]))
                # plt.annotate("Lab",(0,0))
        # plt.show()
    points = __distanceMatrixToPoints_onlyFirstThree(A, optimalSecondPoint)
    # print("Optimal Point: "+str(optimalSecondPoint)) # +", minimal err: " + str(minErr))

    # plt.scatter(points[:,0],points[:,1], c=np.random.rand(3,))
    # plt.scatter(0,0,color="red")
    # plt.annotate("Lab",(0,0))
    # plt.show()
    return points


'''   CLUSTERING   '''

def labelsToSets(labels, CLUSTER_COUNT):
    clusterSets = [[] for _ in range(CLUSTER_COUNT)]
    for i, label in enumerate(labels):
        clusterSets[label].append(i)
    # DONT wunder about the "array" keword when you print out the return. Its because the Elements dont have the same size!!!
    return np.array([cluster for cluster in clusterSets])

def approximateTimeNeededWithKNN(A, cluster):
    placesLeft = copy.deepcopy(list(cluster))
    placesLeft = np.array(np.trim_zeros(placesLeft)) # if the start node is in this cluster, remove it
    path = [0] # first node is the Laboratory
    distanceSum = 0

    for _ in range(len(placesLeft)):
        lowestDist = 1000000000
        nearestNeighbor = 0
        currentPlace = path[-1]
        for neighbor in placesLeft:
            dist = A[currentPlace, neighbor]
            if dist < lowestDist:
                lowestDist = dist
                nearestNeighbor = neighbor
        distanceSum += lowestDist
        path.append(nearestNeighbor)
        placesLeft = np.delete(placesLeft, np.argwhere(placesLeft == nearestNeighbor))
        # print("places Left "+str(placesLeft))
        # print("nearest neighbor: "+str(nearestNeighbor))

    # go back to the start:
    distanceSum += A[path[-1], 0]
    path.append(0)

    return distanceSum, path

def my_special_KMeans(X, n_clusters, startAngleRange=120, rseed=0):
    # TODO: I think Clusters can be also be found in (n-1)d space, not only 2d.
    # 1. Randomly choose clusters # Instead I calculate meaningfull centroid points.
    # rng = np.random.RandomState(rseed)
    # i = rng.permutation(X.shape[0])[:n_clusters]
    # print(i)
    # centers = X[i]
    if n_clusters > X.shape[0]: # just in case
        print("You want more Clusters then Points. Thats not possible (Func: my_special_KMeans)")

    absoluteCenter = X.mean(0)
    startAngle = np.arcsin(np.divide(absoluteCenter[0],np.sqrt(np.square(absoluteCenter[0])+np.square(absoluteCenter[1])))) * 57.2958 # rad->deg: * 57,2958
    # startAngle: add this angle to put the start Points in the right direction.
    alpha = startAngleRange/n_clusters
    radius = absoluteCenter[1] # set radius to mean y of all datapoints
    centers = []
    # Seperating the Points between the positive and the negative axis:
    if n_clusters & 0x1: # odd (ungerade)
        factor = (n_clusters-1)/2
    else:
        factor = n_clusters/2 - 0.5
    for i in range(n_clusters):
        currentalpha = (-factor+i*factor)/(n_clusters/2)*alpha + startAngle # can be optimized
        centers.append([radius*np.sin(0.0174533*currentalpha), radius*np.cos(0.0174533*currentalpha)]) # Numpy takes Rad, not degree -> *0.0174533
    centers = np.array(centers)
    # plt.scatter(X[:, 0], X[:, 1])
    # plt.scatter([c[0] for c in centers], [c[1] for c in centers], color="red")
    # plt.show()

    while True:
        # TODO: I think Clusters can be also be found in (n-1)d space, not only 2d.
        labels = pairwise_distances_argmin(X, centers) # Assign labels based on closest center
        new_centers = np.zeros(centers.shape)
        for i in range(n_clusters): # Find new centers from means of points
            clusterPoints = np.array(X[labels == i])
            # withLab = np.vstack([clusterPoints,[0,0]]) # always consider the Lab
            # moves the mean in the direction of the Lab, not always good!
            # withLab = np.vstack([withLab,[0,0]]) # double Lab
            if clusterPoints.size != 0: # there are no nearest neighbors
                new_centers[i] = clusterPoints.mean(0)
            else:
                new_centers[i] = X[random.randrange(X.shape[0])]
        # new_centers = np.array([X[labels == i].mean(0) for i in range(n_clusters)])

        if np.all(centers == new_centers): # Check for convergence
            break
        centers = new_centers

    for i in list(range(n_clusters)):
        if i not in labels.tolist():
            print("One Cluster hase no points in it")

    # plt.scatter([c[0] for c in centers], [c[1] for c in centers], color="red")
    # for c in centers:
    #     plt.annotate("Center",(c[0],c[1]))
    return centers, labels


'''   PLOTTING   '''

def plot(points, clusterSets, DRIVING_TIMES=None, paths=None):
    for clusterNr, cluster in enumerate(clusterSets):
        clusterPoints = [points[p] for p in cluster]
        # Plot:
        plt.scatter([pp[0] for pp in clusterPoints], [pp[1] for pp in clusterPoints])
        for i,p in enumerate(clusterPoints):
            plt.annotate(str(i), (p[0], p[1]))
            # plt.annotate(str(clusterNr), (p[0], p[1]))

        # Plot Path:
        if paths:
            path = paths[clusterNr]
            lastP = None
            for p in path:
                if lastP is None:
                    lastP = p
                    continue
                plt.plot([points[p][0],points[lastP][0]], [points[p][1],points[lastP][1]],c="black")
                lastP = p

    plt.annotate("Lab",(0,0))
    plt.axis('off')
    plt.show()


'''   EXECUTION   '''

def cluserting(DRIVING_TIMES, CLUSTER_COUNT):
    # print("Finding best 2D fit...")
    points = __to2D(DRIVING_TIMES)
    # CLUSTER_COUNT = 5 # for testing
    # labels = spectral_clustering(DRIVING_TIMES.astype(np.float64), CLUSTER_COUNT) # Produces a different result every time

    ''' Find Clusters '''
    # print("Clustering...")
    # labels = KMeans(CLUSTER_COUNT, random_state=0).fit_predict(points)
    # labels = AgglomerativeClustering(CLUSTER_COUNT).fit_predict(points)
    centers, labels = my_special_KMeans(points,CLUSTER_COUNT)
    # print(labels)
    # TODO: Finding a more problem specific way of clustering

    ''' How many points are in each cluster: '''
    unique, counts = np.unique(labels, return_counts=True)
    # print("Points in Cluster x: "+str(dict(zip(unique, counts))))

    ''' labels -> sets of points (The real Clusters) '''
    clusterSets = labelsToSets(labels, CLUSTER_COUNT)

    if PLOT_HERE:
        # EXAMPLE Path finder (KNN):
        times = []
        paths = []
        for cluster in clusterSets:
            # print("__________________________________")
            # print("Cluster: "+str(cluster))
            time, path = approximateTimeNeededWithKNN(DRIVING_TIMES, cluster)
            times.append(time)
            paths.append(path)
            # print("path: "+str(path))
            # print("Cluster: "+str(clusterNr)+" time KNN: "+str(time))
        plot(points,clusterSets,DRIVING_TIMES,paths)

    return points, clusterSets


# Other Alorithms (Not feasible for this problem):
# 1. Random Projection to reduce Dimensions is only for labeled data -> (Training set, target Values) (X : numpy array of shape [n_samples, n_features], y : numpy array of shape [n_samples])
# Use of that Alg.: http://scikit-learn.org/stable/modules/random_projection.html
