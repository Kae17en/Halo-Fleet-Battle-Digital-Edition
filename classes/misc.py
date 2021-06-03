from abc import *
from classes.units import *
from classes.weapons import *
import random
import numpy as np
import vectors2d as vct
from unittest import *


class Intervalle():

    """
    This class is a simple interval class making range checks easier for the game logic. It simply takes an inf and sup as arguments.

    - isin allows to check if the given parameter x is in the interval


    """

    def __init__(self,inf,sup):
        self.inf=inf
        self.sup=sup
    def isin(self,x):
        if x>=inf and x<=sup:
            return True
        else:
            return False
    @property
    def inf(self):
        return self.inf
    @inf.setter
    def inf(self, inf):
        self.inf = inf

    @property
    def sup(self):
        return self.sup

    @sup.setter
    def sup(self, sup):
        self.sup = sup


class MacFiringSolution():
    """
        MAC (Magnetic Acceleration Cannon) has particular rules in the game. Any firing solution made with MAC cannons can apply bonus critical
        damage. This class will be a subclass of the "Firing Solution" class, to handle easily the additional rules
        The parameter required is L, which is the list of all weapons taking part in the firing solution.

        /!\ THIS PART OF THE CODE IS NOT FINISHED YET AND IS SUBJECT TO SUBSEQUENT CHANGES IN THE FUTURE /!\

        """

    def __init__(self,L):
        m=sum(l.loadouts.__MACValue for l in L)
        d=sum(l.__Dice for l in L)
        self.__MacBonus=m
        self.__dice=d

    @property
    def dice(self):
        return self.__dice

    @property
    def MacBonus(self):
        return self.MacBonus


def Damage_Dice_Roll(n,fp):

    """
    :param n: The number of dice that need to be rolled
    :param fp: The firepower rating used to calculate the number of successes
    :return: (Success,Skulls) where Success is the number of successes of the roll, and skulls the number of critical
             fails remaining among the dice pool

    This function is able to calculate any dice roll in the game. The firepower rating (fp parameter) should be
    calculated while creating the Firing Solution linked to the dice roll with the calc_fp function, or simply given
    according to the situation and the rulebook.
    """

    if fp<1 or fp>5:
        raise ValueError("Invalid Firepower")
    r=0
    success=0
    pool=[random.randint(1,7) for i in range(n)]
    critical=pool.count(6)
    if fp==1:
        print("Impossible Roll")
        print("Rerolls:{}".format(r))
        skull=pool.count(1)
        return int(success),skull
    elif fp==2:
        for e in pool:
            if e==4 or e==5 or e==6:
                success+=1
        print("Weakened Roll")
        print("Rerolls:{}".format(r))
        skull = pool.count(1)
        return success,skull

    elif fp==3:
        for e in pool:
            if e in [4,5]:
                success+=1
            elif e==6:
                success+=2
        skull = pool.count(1)
        print("Crushing Roll!")
        print("Rerolls:{}".format(r))
        return int(success),skull


    elif fp==4:
        c=critical
        skull=pool.count(1)
        for e in pool:
            if e==6:
                success+=2
            elif e==4 or e==5:
                success+=1
            elif e==3 or e==2:
                if c!=0:
                    r+=1
                    reroll=random.choice([0,0.1,0.1,1,1,2])
                    success+=np.floor(reroll)
                    if reroll==0:
                        skull+=1
                    elif reroll==2:
                        c+=1
                    c-=1
        print("Exploding Roll!")
        print("Rerolls:{}".format(r))
        return int(success),skull

    elif fp==5:
        c=critical
        skull=pool.count(1)
        for e in pool:
            if e==6:
                success+=2
            elif e==4 or e==5:
                success+=1
            elif e==3 or e==2:
                if c!=0:
                    r+=1
                    reroll=random.choice([0,0.1,0.1,1,1,2])
                    success+=np.floor(reroll)
                    if reroll==2:
                        c+=1
                    elif reroll==0:
                        skull+=1
                    c-=1
            elif e==1:
                if c!=0:
                    r+=1
                    skull-=1
                    reroll=random.choice([0,0.1,0.1,1,1,2])
                    success+=np.floor(reroll)
                    if reroll==2:
                        c+=1
                    elif reroll==0:
                        skull+=1
                    c-=1
        print("Devastating Roll!!")
        print("Rerolls:{}".format(r))
        return int(success),skull


def dist(a,b):
    """
    Gives the on-board distance between to tokens (wings or element) on the board
    :param a: Must be a wing or an element
    :param b: Must be a wing or an element
    :return: Float number, distance between a and b

    """
    return np.sqrt((a.xpos-b.xpos)**2+(a.ypos-b.ypos)**2)

def get_closest_target(unit,board,angles,maxrange):

    """

    :param unit: Object of a TheoryElement's subclass you want to know the closest targets to
    :param board: List of all elements on the board (only Theory Elements subclasses)
    :param angles: Interval-class object modelling in degrees the maximum and minimum angles you want your targets in. The "0"
           angle is defined by the bow of selected element "unit"
    :param: max: Maximum range you want your closest target to be from the unit
    :return: Returns the closest enemy element within the limit angles


    This function is useful for some loadouts such as "Missile Barrage" which, according to the game's rulebook, can only target the closest
    enemy in range
    """

    a=unit.aim
    d=10000
    for e in board:
        v2=vct.Vector2D(e.xpos-unit.xpos,e.ypos-unit.ypos)              #Vecteur entre les deux éléments
        if e.faction!=unit.faction:
            if dist(e, unit)<d and dist(e, unit)!=0 and angles.inf <= vct.get_angle(a, v2) * np.pi / 180 <= angles.sup:
                d=dist(e,unit)
    if d<=maxrange:
        return d
    else:
        return "No close target in the engagement range"



def get_valid_targets(unit,board,weapon):

    """

    :param unit: Unit selected
    :param board: Other units on the board, excluding wings
    :param weapon: Weapon selected to check ranges. The weapon should be one of the selected unit's weapon
    :return: Return a list of on board units matching the weapon's range and angle requirements

    This function is useful while creating a FiringSolution, as all weapons taking part in the attack should have the target in their
    range and angles of attack.

    """

    a=unit.aim
    dmin=weapon.ShortRange
    dmax=weapon.LongRange
    Targets=[]
    A=weapon.angles
    for e in board:
        a = unit.aim
        v=vct.Vector2D(e.xpos-unit.xpos,e.ypos-unit.ypos)
        alpha=vct.get_angle(a,v)*np.pi/180
        c=0
        for a in A:
            if a.isin(alpha)==True:
                c+=1
        if e.faction!=unit.faction and dist(unit,e)<dmax and c!=0:
            Targets.append(e)
    return Targets

def calc_fp(Target,Attacker,Weapon):

    """

    :param Target: The unit attacked by the attacker (Instance of a TheoryElement subclass)
    :param Attacker: The unit attacking (Instance of a TheoryElement subclass)
    :param Weapon: The weapon selected to conduct the attack. It gives information about how to calculate the firepower,
                   according to the game's rulebook
    :return: the firepower of the attack, a number between 1 and 5

    This function is used to calculate any firepower value the gamelogic needs to resolve an attack. On each element
    (i.e instance of any TheoryElement subclass), all loadouts have an attribute "fpmodifier" that will modify or not
    the firepower under certain circumstances. Loadouts that have nothing to do with attacks or weapons have a fp
    modifier equal to zero. Therefore, each loadout of the element can be called in this function, and only some of
    them will really modify the firepower rating. As loadouts lists are always short (<15 elements), this method doesn't
    affect significantly the overall complexity of the code.

    """

    LongRange=False
    fp = None
    if dist(Target,Attacker)>=Weapon.Shortrange:
        LongRange=True
    elif Weapon.Wtype=="Plasma Beam":
        fp=5
    else:
        fp=4
    for e in Target.loadouts:
        fp+=e.modifyfp(LongRange)
    for l in Weapon.loadouts:
        fp+=l.modifyfp(LongRange)
    return fp

def resolvebomberrun(element,bomber):

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

    a=element.pointdefencedamage
    kills=floor(a / bomber.DT)
    initialflight=bomber.FS
    bomber.FS-=kills
    if bomber.FS==0:
        print("Devastating blow! All bombers intercepted!")
        return 2
    elif kills>initialflight//2:
        print("{} Bombers down, some of them went throught, Brace yourself!".format(kills))
    elif kills<=initialflight//2:
        print(("Only {} Bombers down, others went throught! Prepare for impact!".format(kills)))
    n=bomber.FS*bomber.vs_elem_dice
    success=Damage_Dice_Roll(n,4)[0]
    d=0
    for e in element.ld:
        d+=e.defencedicepool
    dmg=success-d
    if element.CDT[0]<=dmg:
        print("Ennemy hit, we pierced their hull!")
        dmg-=element.CDT[0]
        element.CDT.pop(0)
    else:
        print("No significant damage dealt")
        return 0
    if element.CDT[0]<=dmg:
        print("Ennemy critically damaged!")
        dmg-=element.CDT[0]
        element.CDT.pop(0)
    else:
        return 0
    if element.CDT[0]<=dmg:
        print("Hull critically damaged, multiple explosions on the target. Kill confirmed!")
        dmg-=element.CDT[0]
        element.CDT.pop(0)
        return 1



def resolvedogfight(unitA,unitB):
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
    nb=unitB.FS*unitB.vs_wing_dice
    if unitA.WingType=="Interceptor":
        fpa=5
    else:
        fpa=3
    if unitB.WingType=="Interceptor":
        fpb=5
    else:
        fpb=3
    damagetoA=Damage_Dice_Roll(nb,fpb)[0]
    damagetoB=Damage_Dice_Roll(na,fpa)[0]
    unitA.FS-=floor(damagetoA/(unitA.FS*unitA.DT))
    unitB.FS-=floor(damagetoB/(unitB.FS*unitB.DT))

    if damagetoA>damagetoB and unitB.FS>0:
        pool = [random.randint(1, 7) for i in range(unitB.FS)]
        unitA.FS-=pool.count(6)
    if damagetoB>damagetoA and unitA.FS>0:
        pool = [random.randint(1, 7) for i in range(unitA.FS)]
        unitB.FS -= pool.count(6)

    if unitA.FS<=0:
        #lancer l'animation de destruction ici
        return 1
    elif unitB.FS<=0:
        #lancer l'animation de destruction ici
        return 2
    elif unitB.FS<=0 and unitA.FS<=0:
        return 3
    else:
        return 0


def resolvewingfights(L):

    """
    This function is called each time a fight involving at least one wing token needs to be resolved. It only determines
    what type of wing fight has to be resolved, and redirect to the appropriate function.

    :param L: A list or tuple of two tokens
    :return: A call to the appropriate function to resolve the fight. See ResolveDogfight and Resolvebomberrun docs for
             further informations
    """

    for e in L:
        if e[0].Type=="Element" or e[1].Type=="Element":
            if e[0].Type=="Element":
                return resolvebomberrun(e[0],e[1])
            else:
                return resolvebomberrun(e[1],e[0])
        else:
            return resolvedogfight(e[0],e[1])



def bulletdirection(unitA,unitB,ref):

    """
    This function is used to orient weapons animations towards the ennemy, for a more immersive gameplay

    :param unitA: A token object, either a wing or an element
    :param unitB: A token object, either a wing or an element
    :param ref: The reference vector of our board (~"x axis")
    :return: a vectors2d vector
    """

    v1=vct.vector_from_dots((unitA.xpos,unitA.ypos),(unitB.xpos,unitB.ypos))
    return vct.get_angle(v1,ref)


