from classes.units import *
import vectors2d as vct
import random as rd
from classes.misc import *

class interface():
    def dialog(self, req):
        pass

    def multipleChoice(self, req, type = None):
        print("Ships to move :")
        for i in range(len(req)):
            print(req[i] + " [" + str(i) + "]\r\n")
        i = -1;
        while(not int(i) and i not in range(len(req))):
            i = input("Choisissez une entree")
        return req[i]

    def posRequest(self, object):
        t = -1
        while(not tuple(t) and  np.sqrt((t[0] - object.xpos) ** 2 + (t[1] - object.ypos) ** 2) > object.MoveRange):
            t = tuple([eval(x) for x in input("Chose a new position for : " + object + " in range : " + str(object.MoveRange)).split(',')])
        return t

    def UpdateGameState(self):
        for object in self.UNSC.tokens:
            toprint = "UNSC has " + str(object) + " at position (" + str(object.xpos) + "," + str(object.ypos) + ")\r\n"
            print(toprint)
        for object in self.Covenant.tokens:
            toprint = "Covenant has " + str(object) + " at position (" + str(object.xpos) + "," + str(object.ypos) + ")\r\n"
            print(toprint)

    def setGameState(self, UNSC, Covenant):
        self.UNSC = UNSC
        self.Covenant = Covenant


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

    def startGameFromSituation(self, UNSC, Covenant):
        self.UNSC = UNSC
        self.Covenant = Covenant
        self.UI.setGameState(self.UNSC, self.Covenant)
        self.UI.UpdateGameState()
        self.prepare()

    def prepare(self):
        #do preparation
        self.phaseOrder[self.currentPhase]()

    def nextPhase(self):
        self.currentPhase += 1
        if self.currentPhase == 5:
            self.turn += 1
            self.currentPhase = 0
        self.phaseOrder[self.currentPhase]()

    def wing_movement(self):
        UNSCstart = rd.randint(0,1)
        toMoveUNSC = [unit for unit in self.UNSC.tokens if issubclass(type(unit), Spacecraft)]
        toMoveCovenant = [unit for unit in self.Covenant.tokens if issubclass(type(unit), Spacecraft)]
        moved = []
        while(len(moved) != len(toMoveUNSC) + len(toMoveCovenant)):
            if(UNSCstart):
                choosedUnit = self.UI.multipleChoice([unit for unit in toMoveUNSC if unit not in moved], "MAPSELECT")
                mooveLocation = self.UI.posRequest(choosedUnit)
                while(!choosedUnit.moove_unit(mooveLocation)){
                    self.UI.error("Invalid Location")
                    mooveLocation = self.UI.posRequest(choosedUnit)
                }
                self.UI.UpdateGameState()
                moved.append(choosedUnit)
                choosedUnit = self.UI.multipleChoice([unit for unit in toMoveCovenant if unit not in moved], "MAPSELECT")
                mooveLocation = self.UI.posRequest(choosedUnit)
                while (!choosedUnit.moove_unit(mooveLocation)){
                self.UI.error("Invalid Location")
                mooveLocation = self.UI.posRequest(choosedUnit)
                }
                self.UI.UpdateGameState()
                moved.append(choosedUnit)
            else:
                choosedUnit = self.UI.multipleChoice([unit for unit in toMoveCovenant if unit not in moved], "MAPSELECT")
                mooveLocation = self.UI.posRequest(choosedUnit)
                while (!choosedUnit.moove_unit(mooveLocation)){
                    self.UI.error("Invalid Location")
                    mooveLocation = self.UI.posRequest(choosedUnit)
                }
                moved.append(choosedUnit)
                self.UI.UpdateGameState()
                choosedUnit = self.UI.multipleChoice([unit for unit in toMoveUNSC if unit not in moved], "MAPSELECT")
                while (!choosedUnit.moove_unit(mooveLocation)){
                    self.UI.error("Invalid Location")
                    mooveLocation = self.UI.posRequest(choosedUnit)
                }
                self.UI.UpdateGameState()
                moved.append(choosedUnit)

        self.nextPhase()

    def wing_attack(self):
        toResolve = [unit for unit in self.UNSC.tokens if issubclass(type(unit), Spacecraft)]
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



