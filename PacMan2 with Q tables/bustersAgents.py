# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters

class NullGraphics:
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent:
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__(self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True, epsilon=0.5, alpha=0.5, gamma=1):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable

        #not sure
        self.epsilon = float(epsilon)
        self.gamma = float(gamma)
        self.alpha = float(alpha)

    def registerInitialState(self, gameState):

        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True


    def observeTransition(self, state,action,nextState,deltaReward):
        self.episodeRewards += deltaReward
        self.update(state,action,nextState,deltaReward)

    def observationFunction(self, gameState):#, action, gameNextState, deltaReward):
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        return Directions.STOP


class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        print(gameState.getPacmanPosition())
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)

from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys




class QLearningAgent(BustersAgent):

    def __init__(self, **args):
        BustersAgent.__init__(self, **args)
        self.actions = {"North": 0, "East": 1, "South": 2, "West": 3}
        self.table_file = open("qtable.txt", "r+")
        self.q_table = self.readQtable()
        self.epsilon = 0.05
        self.alpha = 0.05
        self.discount = 0.05

    def registerInitialState(self, state):
        BustersAgent.registerInitialState(self, state)
        self.distancer = Distancer(state.data.layout, False)
        self.countActions = 0


    def createQtable(self):
        first_char = self.table_file.read(1)
        print(first_char)
        if first_char != "0":
            for i in range(15*8):
                s = ""
                for j in range(4):
                    s += "0.0 "
                self.table_file.write(s)
                self.table_file.write("\n")

    def readQtable(self):
        table = self.table_file.readlines()
        q_table = []

        for i, line in enumerate(table):
            row = line.split()
            row = [float(x) for x in row]
            q_table.append(row)
        return q_table

    def writeQtable(self):
        self.table_file.seek(0)
        self.table_file.truncate()

        for line in self.q_table:
            for item in line:
                self.table_file.write(str(item) + " ")
            self.table_file.write("\n")

    def computePosition(self, state):
        pacman = state.getPacmanPosition()
        d = state.data.ghostDistances
        positions = state.getGhostPositions()
        food = positions[d.index(min(i for i in d if i is not None))]

        if food[1] > pacman[1]:
            if food[0] > pacman[0]:
                b=1
            if food[0] < pacman[0]:
                b=2
        if food[1] < pacman[1]:
            if food[0] > pacman[0]:
                b=4
            if food[0] < pacman[0]:
                b=3
        if food[0] == pacman[0]:
            if food[1] > pacman[1]:
                b=5
            if food[1] < pacman[1]:
                b=6
        if food[1] == pacman[1]:
            if food[0] > pacman[0]:
                b=7
            if food[0] < pacman[0]:
                b=8


        l = state.getLegalActions()

        x = 0
        while x < 1:
            if "North" in l:
                if "South" in l:
                    if "East" in l:
                        if "West"  in l:
                            a = 15
                            break
                        a = 11
                        break
                    a = 5
                    if "West" in l:
                        a=12
                    break
                a = 1
                if "West" in l:
                    a = 7
                    if "East" in l:
                        a = 13
                        break
                if "East" in l:
                    a=6
                break
            if "South" in l:
                if "East" in l:
                    if "West" in l:
                        a = 14
                        break
                    a = 8
                    break
                a = 2
                if "West" in l:
                    a = 9
                break
            if "East" in l:
                if "West" in l:
                    a = 10
                    break
                a = 3
                break
            if "West" in l:
                a = 4
                break
        return (((b-1)*15+a)-1)

    def getQValue(self, state, action):
        if action=="Stop":
            legalActions = state.getLegalActions()
            for j in legalActions:
                if j == 'Stop':
                    legalActions.remove(j)
            action=random.choice(legalActions)


        position = self.computePosition(state)
        action_column = self.actions[action]
        if (self.q_table[position][action_column] == None):
            return self.q_table[3][3]
        return self.q_table[position][action_column]

    def computeValueFromQValues(self, state):
        legalActions = state.getLegalActions()
        for j in legalActions:
            if j == 'Stop':
                legalActions.remove(j)
        if len(legalActions) == 0:
            return 0
        return max(self.q_table[self.computePosition(state)])

    def computeActionFromQValues(self, state):
        legalActions = state.getLegalActions()
        for j in legalActions:
            if j == 'Stop':
                legalActions.remove(j)
        if len(legalActions) == 0:
            return None


        best_actions = [legalActions[0]]
        best_value = self.getQValue(state, legalActions[0])
        for action in legalActions:
            value = self.getQValue(state, action)
            if value == best_value:
                best_actions.append(action)
            if value > best_value:
                best_actions = [action]
                best_value = value
        return random.choice(best_actions)

    def getAction(self, state):
        legalActions = state.getLegalActions()
        action = None
        for j in legalActions:
            if j == 'Stop':
                legalActions.remove(j)
        if len(legalActions) == 0:
            return action

        flip = util.flipCoin(self.epsilon)

        if flip:
            return random.choice(legalActions)
        return self.getPolicy(state)

    def update(self, state, action, nextState, reward):
        legalActions = state.getLegalActions()
        pos = self.computePosition(state)
        legal = legalActions
        action = self.actions[action]


        if len(legal) == 0:
            self.q_table[pos][action] = (1 - self.alpha)  * self.q_table[pos][action] + self.alpha * (reward + 0)
        if len(legal) != 0:
            self.q_table[pos][action] = (1 - self.alpha)  * self.q_table[pos][action] + self.alpha * (reward + self.discount * self.getValue(nextState))

        if self.q_table[pos][action] > 0:
            print(pos,action)
            print(self.q_table[pos][action])

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)

    def getNextState(self, state, action):
        Game.state = state
        return Game.state.generateSuccessor(0, action)

    def getReward(self, state, nextState):
        reward=0
        move = nextState.getPacmanPosition()
        d = state.data.ghostDistances
        ghosts = state.getGhostPositions()
        closest_ghost = ghosts[d.index(min(i for i in d if i is not None))]
        if move==closest_ghost:
            return 1
        return reward
