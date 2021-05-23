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

    def startGameFromSituation(self, UNSC, Covenant):
        self.UNSC = UNSC
        self.Covenant = Covenant
        self.UI.setGameState(self.UNSC, self.Covenant)
        self.prepare()

    def prepare(self):
        #do preparation
        return None

    def nextPhase(self):
        self.currentPhase += 1
        if self.currentPhase == 5:
            self.turn += 1
            self.currentPhase = 0


    def wing_movement(self):
        UNSCstart = rd.randint(0,1)
        toMoveUNSC = [unit for unit in self.UNSC.tokens if issubclass(type(unit), Spacecraft)]
        toMoveCovenant = [unit for unit in self.Covenant.tokens if issubclass(type(unit), Spacecraft)]
        moved = []
        while(len(moved) != len(toMoveUNSC) + len(toMoveCovenant)):
            if(UNSCstart):
                choosedUnit = self.UI.multipleChoice([unit for unit in toMoveUNSC if unit not in moved and not unit.locked], "MAPSELECT")
                mooveLocation = self.UI.posRequest(choosedUnit)

                while(not choosedUnit.moove_unit(mooveLocation)):
                    self.UI.error("Invalid Location")
                    mooveLocation = self.UI.posRequest(choosedUnit)
                #Unit Have been mooved
                choosedUnit.engage(Covenant.tokens)
                #Engagement dealed

                moved.append(choosedUnit)

                choosedUnit = self.UI.multipleChoice([unit for unit in toMoveCovenant if unit not in moved and not unit.locked], "MAPSELECT")
                mooveLocation = self.UI.posRequest(choosedUnit)
                while (not choosedUnit.moove_unit(mooveLocation)):
                    self.UI.error("Invalid Location")
                    mooveLocation = self.UI.posRequest(choosedUnit)
                # Unit Have been mooved
                choosedUnit.engage(UNSC.tokens)
                # Engagement dealed

                moved.append(choosedUnit)
            else:
                choosedUnit = self.UI.multipleChoice([unit for unit in toMoveCovenant if unit not in moved and not unit.locked], "MAPSELECT")
                mooveLocation = self.UI.posRequest(choosedUnit)
                while (not choosedUnit.moove_unit(mooveLocation)):
                    self.UI.error("Invalid Location")
                    mooveLocation = self.UI.posRequest(choosedUnit)
                # Unit Have been mooved
                choosedUnit.engage(UNSC.tokens)
                # Engagement dealed
                moved.append(choosedUnit)
                self.UI.UpdateGameState()
                choosedUnit = self.UI.multipleChoice([unit for unit in toMoveUNSC if unit not in moved and not unit.locked], "MAPSELECT")
                while (not choosedUnit.moove_unit(mooveLocation)):
                    self.UI.error("Invalid Location")
                    mooveLocation = self.UI.posRequest(choosedUnit)
                # Unit Have been mooved
                choosedUnit.engage(Covenant.tokens)
                # Engagement dealed
                self.UI.UpdateGameState()
                moved.append(choosedUnit)

        self.nextPhase()

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



