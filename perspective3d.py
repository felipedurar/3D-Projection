# Coded by Felipe Durar
# Nov 20, 2022
# This application renders a rotating 3D cube making all the geometric transformations in the code

import pygame
import numpy as np
import math

# Model Definition (Cube)
# The cubeZbuffer is used for the Painter's Algorithm
# https://en.wikipedia.org/wiki/Painter%27s_algorithm
cubeVertices = [
    (0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1),
    (0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)
]
cubeFaces = [
    (0, 1, 2, 3), (0, 4, 5, 1), (1, 2, 6, 5), (3, 2, 6, 7),
    (0, 3, 7, 4), (4, 5, 6, 7)
]
cubeFaceColors = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), 
    (0, 255, 255), (255, 0, 255)
]
# The first item is the cubeFaces's index, the second item is the last Z distance from the camera pinpoint
cubeZbuffer = [ 
    [0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]
]

# Camera Definition
cameraPos = (0, 0, -10)
cameraOrientation = (0, 0, 0)
displaySurface = (0, 0, 0)
modelRotation = (0, 0, 0)

# For rotation
thetaRot = 0

# define a main function
def main():
    global screen
    global WINDOW_W
    global WINDOW_H
    global displaySurface

    WINDOW_W = 800
    WINDOW_H = 600

    # initialize the pygame module
    pygame.init()

    # Set Caption
    pygame.display.set_caption("Perspective 3D")

    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)

    # define a variable to control the main loop
    running = True

    # Calculate the Viewport and FOV
    setFov(45)

    # main loop
    while running:
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
        draw()

def setFov(fovDeg):
    global displaySurface
    displaySurface = (0, 0, -math.tan(1 / ((fovDeg * math.pi) / 180)) * 2)
    return

def draw():
    global cameraOrientation
    global modelRotation
    global thetaRot

    screen.fill((0, 0, 0))

    thetaRot += 0.001
    cubeTransform = np.identity(4).dot(createXYZRotationMatrix((thetaRot, thetaRot, 0))).dot(createTranslationMatrix((-0.5, -0.5, -0.5)))

    drawModel(cubeVertices, cubeFaces, cubeFaceColors, cubeZbuffer, cubeTransform)

    pygame.display.flip()
    return

def drawModel(vertices, faces, colors, zBuffOrder, modelTransformation = None):
    if (modelTransformation is None):
        modelTransformation = np.identity(4)

    # Order by the Z distance
    zBuffOrder.sort(key=lambda x: x[1], reverse=True)

    for cFaceInBuffer in zBuffOrder:
        cFace = faces[cFaceInBuffer[0]]
        cFaceColor = colors[cFaceInBuffer[0]]
        projectedPoints = []
        for vtxIndex in cFace:
            cVtx = vertices[vtxIndex]
            projCoord = projectCoordinate(cVtx, modelTransformation)
            projectedPoints.append(projCoord)

        avgZ = (projectedPoints[0][2] + projectedPoints[1][2] + projectedPoints[2][2] + projectedPoints[3][2]) / 4
        cFaceInBuffer[1] = avgZ

        pygame.draw.polygon(screen, cFaceColor, [(projectedPoints[0][0], projectedPoints[0][1]), (projectedPoints[1][0], projectedPoints[1][1]), (projectedPoints[2][0], projectedPoints[2][1]), (projectedPoints[3][0], projectedPoints[3][1])])
    return

def createXYZRotationMatrix(eulerAngle):
    transformationRotX = np.array([
        [1, 0, 0, 0],
        [0, math.cos(eulerAngle[0]), math.sin(eulerAngle[0]), 0],
        [0, -math.sin(eulerAngle[0]), math.cos(eulerAngle[0]), 0],
        [0, 0, 0, 1]
        ])
    transformationRotY = np.array([
        [math.cos(eulerAngle[1]), 0, -math.sin(eulerAngle[1]), 0],
        [0, 1, 0, 0], 
        [math.sin(eulerAngle[1]), 0, math.cos(eulerAngle[1]), 0],
        [0, 0, 0, 1]
        ])
    transformationRotZ = np.array([
        [math.cos(eulerAngle[2]), math.sin(eulerAngle[2]), 0, 0],
        [-math.sin(eulerAngle[2]), math.cos(eulerAngle[2]), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
        ])
    return transformationRotX.dot(transformationRotY).dot(transformationRotZ)

def createTranslationMatrix(translation):
    translationMatrix = np.array([
        [1, 0, 0, translation[0]], 
        [0, 1, 0, translation[1]], 
        [0, 0, 1, translation[2]],
        [0, 0, 0, 1]
        ])
    return translationMatrix
    

def projectCoordinate(coordinate, modelTransformation):
    global cameraPos
    global cameraOrientation
    global displaySurface
    global WINDOW_W
    global WINDOW_H

    coordMat = np.array([[coordinate[0]], [coordinate[1]], [coordinate[2]], [1]])
    camPos = np.array([[cameraPos[0]], [cameraPos[1]], [cameraPos[2]], [1]])
    
    coordTransformed = modelTransformation.dot(coordMat)
    cameraCoordDiff = np.subtract(coordTransformed, camPos);
    cameraTransform = createXYZRotationMatrix(cameraOrientation).dot(cameraCoordDiff)

    fHomogeneousCoordinates = np.array([
        [1, 0, displaySurface[0] / displaySurface[2], 0],
        [0, 1, displaySurface[1] / displaySurface[2], 0],
        [0, 0, 1 / displaySurface[2], 0],
        [0, 0, 0, 1]
        ]).dot(cameraTransform)

    bx = fHomogeneousCoordinates[0][0] / fHomogeneousCoordinates[2][0]
    by = fHomogeneousCoordinates[1][0] / fHomogeneousCoordinates[2][0]

    remappedX = ((bx + 1) * WINDOW_W) / 2 # -1 to 1
    remappedY = ((by + 1) * WINDOW_H) / 2 # -1 to 1

    return (remappedX, remappedY, cameraTransform[2])



# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()
