from classes.units import *
import vectors2d as vct
import random as rd
from classes.misc import *
import pickle

class Player():
    def __init__(self, type):
        self.tokens = []
        self.type = type

    def addToken(self, token):
        self.tokens.append(token)


class MainGame():
    def __init__(self, UI):
        self.UI = UI
        self.turn = 0
        self.currentPhase = 0
        self.phaseOrder = [self.wing_movement, self.wing_attack, self.battle_moovement, self.battle_attack, self.turn_end]
        self.toResolveWings = []
        self.moved = []
        self.movable = []

    def startGameFromSituation(self, UNSC, Covenant):
        self.UNSC = UNSC
        self.Covenant = Covenant
        UNSCstart = rd.randint(0, 1)
        self.currentPhase = -1
        self.nextPhase()
        if(UNSCstart == 1):
            self.CurrentPlayer = UNSC
        else:
            self.CurrentPlayer = Covenant
        self.UI.setGameState(self.UNSC, self.Covenant, (self.currentPhase, self.turn, self.CurrentPlayer))


    def nextPhase(self):
        self.currentPhase += 1
        if self.currentPhase == 5:
            self.turn += 1
            self.currentPhase = 0
        if(self.currentPhase == 0):
            self.movable = [unit for unit in self.UNSC.tokens if issubclass(type(unit), Spacecraft)] + [unit for unit in self.Covenant.tokens if issubclass(type(unit), Spacecraft)]
        if(self.currentPhase == 2):
            self.movable = [unit for unit in self.UNSC.tokens if issubclass(type(unit), TheoryElement)] + [unit for unit in self.Covenant.tokens if issubclass(type(unit),TheoryElement)]
        else:
            self.movable = []
        self.UI.setMovable = self.movable


    def wing_movement(self, object, mooveLocation):
        if(self.currentPhase == 0 and object in self.CurrentPlayer.tokens and object not in self.moved and not object.locked):
            object.set_pos(mooveLocation)
                #Unit Have been mooved
            object.engage(self.CurrentPlayer.tokens)
                #Engagement dealed
            self.moved.append(choosedUnit)
            self.CurrentPlayer = self.nextPlayer()
        if (len(self.moved) == len(self.movable)):
            self.moved = []
            self.movable = []
            self.nextPhase()


    def requestMove(self, unit, pos):
        if(issubclass(type(unit), Spacecraft)):
            self.wing_movement(unit, pos)

    def nextPlayer(self):
        if(self.CurrentPlayer.type == "UNSC"):
            self.CurrentPlayer = self.Covenant
        else:
            self.CurrentPlayer = self.UNSC
        self.UI.setGameState(self.UNSC, self.Covenant, (self.currentPhase, self.turn, self.CurrentPlayer))

    def wing_attack(self):
        toResolve = []
        [(toResolve.append((unit, unit.opponent)) for opponent in unit.engagements if ((unit, unit.opponent) not in toResolve and (unit.opponent, unit) not in toResolve)) for unit in self.UNSC.tokens if issubclass(type(unit), Spacecraft)]

        self.nextPhase()

    def battle_moovement(self):

        self.nextPhase()

    def battle_attack(self):

        self.nextPhase()

    def turn_end(self):

        self.nextPhase()







if __name__ == "__main__":
    Game = MainGame(interface())

    UNSC = Player("UNSC")
    Covenant = Player("Covenant")

    UNSC.addToken(UNSC_Paris_Frigate_Arrow((18, 16), vct.vector_from_dots((11.8, 11.6), (18, 16))))
    Covenant.addToken(Covenant_CCS_Battlecruiser((6, 8), vct.vector_from_dots((12.7,1.3),(6,8))))

    Game.startGameFromSituation(UNSC, Covenant)



