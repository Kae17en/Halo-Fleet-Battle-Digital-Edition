from classes.units import *
import vectors2d as vct
import random as rd
from classes.misc import *
import pickle

class Player():
    def __init__(self, type):
        self.tokens = []
        self.type = type
        self.turnEnded = False

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

        if(UNSCstart == 1):
            self.CurrentPlayer = UNSC
            self.NotCurrentPlayer = Covenant
        else:
            self.CurrentPlayer = Covenant
            self.NotCurrentPlayer = UNSC
        self.UI.setGameState(self.UNSC, self.Covenant, [self.currentPhase, self.turn, self.CurrentPlayer])
        self.nextPhase()


    def nextPhase(self):
        self.moved = []
        self.UNSC.turnEnded = False
        self.Covenant.turnEnded = False
        if self.currentPhase == 3:
            self.turn += 1
            self.currentPhase = 0
        else:
            self.currentPhase += 1
        if(self.currentPhase == 0):
            self.UI.HUD.enableUserControl()
            self.movable = [unit for unit in self.UNSC.tokens if issubclass(type(unit), Spacecraft)] + [unit for unit in self.Covenant.tokens if issubclass(type(unit), Spacecraft)]
        elif(self.currentPhase == 1):
            self.UI.HUD.disableUserControl()
            self.wing_attack()
        elif(self.currentPhase == 2):
            self.UI.HUD.enableUserControl()
            self.movable = [unit for unit in self.UNSC.tokens if issubclass(type(unit), TheoryElement)] + [unit for unit in self.Covenant.tokens if issubclass(type(unit),TheoryElement)]
        elif(self.currentPhase == 3):
            self.UI.HUD.disableUserControl()
            self.battle_attack()
        else:
            self.movable = []
        self.UI.setMovable = self.movable
        self.UI.setGameState(self.UNSC, self.Covenant, [self.currentPhase, self.turn, self.CurrentPlayer])


    def wing_movement(self, object, mooveLocation):
        if(not object.locked and object not in self.moved and object in self.movable):
            object.set_pos(mooveLocation)
                #Unit Have been mooved
            object.engage(self.NotCurrentPlayer.tokens)
                #Engagement dealed
            self.moved.append(object)
            self.nextPlayer()
            return True
        return False

    def endTurn(self):
        self.CurrentPlayer.turnEnded = True
        self.nextPlayer()


    def requestMove(self, unit, pos):
        if(issubclass(type(unit), Spacecraft)):
            self.wing_movement(unit, pos)

    def requestObjectSelect(self,unit):
        isSelectable = (unit in self.CurrentPlayer.tokens)
        movable = False
        canDeploy = False
        if isSelectable:
            movable = (unit in self.movable and unit not in self.moved)
            canDeploy = (issubclass(type(unit), TheoryElement) and unit.Hangars > 0 and self.currentPhase == 0 and len(unit.docked) > 0)
        return isSelectable, movable, canDeploy

    def deployWing(self, wing, fromShip):
        fromShip.deployWing(wing)
        self.CurrentPlayer.tokens.append(wing)
        self.movable.append(wing)

    def nextPlayer(self):
        if (self.UNSC.turnEnded and self.Covenant.turnEnded):
            self.nextPhase()
        if(self.CurrentPlayer.type == "UNSC" and self.Covenant.turnEnded == False):
            self.CurrentPlayer = self.Covenant
            self.NotCurrentPlayer = self.UNSC
            self.UI.setPlayer(self.Covenant)
        elif(self.CurrentPlayer.type == "Covenant" and self.UNSC.turnEnded == False):
            self.CurrentPlayer = self.UNSC
            self.NotCurrentPlayer = self.Covenant
            self.UI.setPlayer(self.UNSC)



    def wing_attack(self):
        toResolve = []
        [(toResolve.append((unit, unit.opponent)) for opponent in unit.engagements if ((unit, unit.opponent) not in toResolve and (unit.opponent, unit) not in toResolve)) for unit in self.UNSC.tokens if issubclass(type(unit), Spacecraft)]

        self.nextPhase()

    def battle_moovement(self):
        pass

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



