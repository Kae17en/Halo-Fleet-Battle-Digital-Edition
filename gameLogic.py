from classes.units import *
import vectors2d as vct
import random as rd
from classes.misc import *
import pickle

class Player():
    """
    This class models a player. "Players" and "Faction" are in direct link, has each player has the name of a faction,
    either Covenant or UNSC (the "type" parameter). This make communication between game logic and HUD easier. A player has:

    - a certain number of token, either wings or elements, listed in the .tokens list
    - a boolean value .turnEnded to know if the player has decided to withdraw from the current phase and let his
      opponent finish the current phase

    :parameter: type: A string being either "Covenant" or "UNSC"

    The addToken method is used to implement a new token under the player's control

    """
    def __init__(self, type):
        self.tokens = []
        self.type = type
        self.turnEnded = False

    def addToken(self, token):
        self.tokens.append(token)


class MainGame():

    """
    This class contains all informations about the game state progress, HUD and how to interact with it

    :parameter: UI: All graphic elements needed to display the in game informations, menus and tokens.
    """

    def __init__(self, UI):
        self.UI = UI
        self.turn = 0
        self.currentPhase = 0
        self.phaseOrder = [self.wing_movement, self.wing_attack, self.battle_moovement, self.battle_attack, self.turn_end]
        self.toResolveWings = []
        self.moved = []
        self.movable = []

    def startGameFromSituation(self, UNSC, Covenant, GameState):
        self.UNSC = UNSC
        self.Covenant = Covenant
        UNSCstart = rd.randint(0, 1)
        self.currentPhase = GameState[0]-1
        self.turn = GameState[1]
        if(UNSCstart == 1 or GameState[2] == 0):
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
            return 0
        elif(object in self.moved):
            return 1
        else:
            return 2

    def endTurn(self):
        self.CurrentPlayer.turnEnded = True
        self.nextPlayer()

    def getAbsoluteAngleBetweenOpponents(self, opponent1, opponent2):
        return (atan2(1,0) - atan2((opponent2.pos[1] - opponent1.pos[1]), (opponent2.pos[0] - opponent1.pos[0])))


    def requestMove(self, unit, pos):
        if(issubclass(type(unit), Spacecraft)):
            return self.wing_movement(unit, pos)

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
        self.toResolve = []

        for unit in self.UNSC.tokens:
            if issubclass(type(unit), Spacecraft):
                for opponent in unit.engagements:
                    if ((unit, opponent) not in self.toResolve and (opponent, unit) not in self.toResolve):
                        self.toResolve.append((unit, opponent))
        for unit in self.Covenant.tokens:
            if issubclass(type(unit), Spacecraft):
                for opponent in unit.engagements:
                    if ((unit, opponent) not in self.toResolve and (opponent, unit) not in self.toResolve):
                        self.toResolve.append((unit, opponent))

        if self.toResolve != []:
            fighting = self.toResolve[0][0], self.toResolve[0][1]
            self.fightResult =self.resolveFightForWingAttack((self.toResolve[0][0], self.toResolve[0][1]))
            self.UI.showGraphicalFight(self.toResolve[0][0], self.toResolve[0][1], self.fightResult)
        else:
            self.nextPhase()

    def fightEnd(self, fighting):
        i = self.toResolve.index(fighting)
        self.toResolve.pop(i)
        if (self.fightResult > 0):
            if self.fightResult == 3:
                toDelList = [fighting[0], fighting[1]]
            else:
                toDelList = [fighting[self.fightResult - 1]]
            for toDel in toDelList:
                if toDel in self.UNSC.tokens:
                    i = self.UNSC.tokens.index(toDel)
                    self.UNSC.tokens.pop(i)
                    toDel.destroySelf()
                elif toDel in self.Covenant.tokens:
                    i = self.Covenant.tokens.index(toDel)
                    self.Covenant.tokens.pop(i)
                    toDel.destroySelf()
        if self.toResolve != []:
            self.fightResult = self.resolveFightForWingAttack((self.toResolve[0][0], self.toResolve[0][1]))
            self.UI.showGraphicalFight(self.toResolve[0][0], self.toResolve[0][1], self.fightResult)
        else:
            self.nextPhase()


    def resolvebomberrun(self, element, bomber):

        """
        :param element: Any element on the board
        :param bomber: The wing attacking the element. Type is a Spacecraft subclass instance that has the "Bomber" type.
        :return: A integrer between 0 and 2 included. This value will never be seen by the player, but the game logic will
                 use it to determine animations and board state modifications to conduct. It return:
                 - 0 if the ship is not destroyed
                 - 2 if all bombers are destroyed
                 - 1 if the element is destroyed
        This function also prints different sentences, according to what is happening during the run. Those messages will
        surely be shown to the players and voice-acted in the future.
        """

        a = element.pointdefencedamage
        kills = floor(a / bomber.DT)
        initialflight = bomber.FS
        bomber.FS -= kills
        if bomber.FS == 0:
            print("Devastating blow! All bombers intercepted!")
            return 2
        elif kills > initialflight // 2:
            print("{} Bombers down, some of them went throught, Brace yourself!".format(kills))
        elif kills <= initialflight // 2:
            print(("Only {} Bombers down, others went throught! Prepare for impact!".format(kills)))
        n = bomber.FS * bomber.vs_elem_dice
        success = Damage_Dice_Roll(n, 4)[0]
        d = 0
        for e in element.ld:
            d += e.defencedicepool
        dmg = success - d
        if element.CDT[0] <= dmg:
            print("Ennemy hit, we pierced their hull!")
            dmg -= element.CDT[0]
            element.CDT.pop(0)
        else:
            print("No significant damage dealt")
            return 0
        if element.CDT[0] <= dmg:
            print("Ennemy critically damaged!")
            dmg -= element.CDT[0]
            element.CDT.pop(0)
        else:
            return 0
        if element.CDT[0] <= dmg:
            print("Hull critically damaged, multiple explosions on the target. Kill confirmed!")
            dmg -= element.CDT[0]
            element.CDT.pop(0)
            return 1

    def resolvedogfight(self, unitA, unitB):
        """
        This function is used to resolve any engaged fight between to wings

        :param unitA: A wing-type unit on board
        :param unitB: A wing-type unit on board
        :return: A integrer between 0 and 3 included. This value will never be seen by the player, but the game logic will
                 use it to determine animations and board state modifications to conduct. It return:
                 - 0 if both wings survive the fight
                 - 1 if unitA gets killed
                 - 2 if unitB gets killed
                 - 3 if both units gets killed

        Voice acting may be added in future update to make the game more immersive

        """
        na = unitA.FS * unitA.vs_wing_dice
        nb = unitB.FS * unitB.vs_wing_dice
        if unitA.WingType == "Interceptor":
            fpa = 5
        else:
            fpa = 3
        if unitB.WingType == "Interceptor":
            fpb = 5
        else:
            fpb = 3
        damagetoA = Damage_Dice_Roll(nb, fpb)[0]
        damagetoB = Damage_Dice_Roll(na, fpa)[0]
        unitA.FS -= floor(damagetoA / (unitA.FS * unitA.DT))
        unitB.FS -= floor(damagetoB / (unitB.FS * unitB.DT))

        if damagetoA > damagetoB and unitB.FS > 0:
            pool = [random.randint(1, 7) for i in range(unitB.FS)]
            unitA.FS -= pool.count(6)
        if damagetoB > damagetoA and unitA.FS > 0:
            pool = [random.randint(1, 7) for i in range(unitA.FS)]
            unitB.FS -= pool.count(6)

        if unitA.FS <= 0:
            # lancer l'animation de destruction ici
            return 1
        elif unitB.FS <= 0:
            # lancer l'animation de destruction ici
            return 2
        elif unitB.FS <= 0 and unitA.FS <= 0:
            return 3
        else:
            return 0

    def resolveFightForWingAttack(self,F):

        """
        This function is called each time a fight involving at least one wing token needs to be resolved. It only determines
        what type of wing fight has to be resolved, and redirect to the appropriate function.

        :param L: A list or tuple of two tokens
        :return: A call to the appropriate function to resolve the fight. See ResolveDogfight and Resolvebomberrun docs for
                 further informations
        """

        if F[0].Type == "Element" or F[1].Type == "Element":
            if F[0].Type == "Element":
                return self.resolvebomberrun(F[0], F[1])
            else:
                return self.resolvebomberrun(F[1], F[0])
        else:
            return self.resolvedogfight(F[0], F[1])

    def getFightCenter(self, fighting):
        return ((fighting[0].pos[0]+ fighting[1].pos[0])/2, (fighting[0].pos[1] + fighting[1].pos[1])/2)

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



