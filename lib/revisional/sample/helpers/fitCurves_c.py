#
from __future__ import print_function
from numpy import *
import bezier
#
# Fit one Bezier curve to a set of points
def fitCurve(points, maxError):
    #
    return fitCubic(points, maxError)
    #
def fitCubic(points, error):
    #
    # Use heuristic if region only has two points in it
    if (len(points) == 2):
        dist = linalg.norm(points[0] - points[1]) / 1.0
        bezCurve = [points[0], points[0], points[1], points[1]]
        return [bezCurve]
    #
    # Parameterize points, and attempt to fit curve
    u = chordLengthParameterize(points)
    #
    bezCurve = [points[0], points[0], points[-1], points[-1]]
    # Find max deviation of points to fitted curve
    maxError, splitPoint = computeMaxError(points, bezCurve, u)
    #
    if maxError < error:
        return [bezCurve]
    #
    beziers = []
    #
    beziers += fitCubic(points[:splitPoint+1], error)
    beziers += fitCubic(points[splitPoint:], error)
    #
    return beziers

def chordLengthParameterize(points):
    #
    u = [0.0]
    for i in range(1, len(points)):
        u.append(u[i-1] + linalg.norm(points[i] - points[i-1]))

    for i, _ in enumerate(u):
        u[i] = u[i] / u[-1]

    return u

def computeMaxError(points, bez, parameters):
    maxDist = 0.0
    splitPoint = len(points)/2
    for i, (point, u) in enumerate(zip(points, parameters)):
        #
        print("----")
        print(bezier.q(bez, u))
        #
        dist = linalg.norm(bezier.q(bez, u)-point)**1.4
        if dist > maxDist:
            maxDist = dist
            splitPoint = i

    return maxDist, splitPoint


def normalize(v):
    return v / linalg.norm(v)

