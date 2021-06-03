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


