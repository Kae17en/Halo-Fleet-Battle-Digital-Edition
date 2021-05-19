from abc import *
from classes.units import *
from classes.weapons import *
import random
import numpy as np
import vectors2d as vct


class Intervalle():
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
    @property
    def sup(self):
        return self.sup


class MacFiringSolution():                            #Avec L la liste de weapons participant à la salve
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
        return success,skull
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
        return success,skull


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
                    success+=floor(reroll)
                    if reroll==0:
                        skull+=1
                    elif reroll==2:
                        c+=1
                    c-=1
        print("Exploding Roll!")
        print("Rerolls:{}".format(r))
        return success,skull

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
                    success+=floor(reroll)
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
                    success+=floor(reroll)
                    if reroll==2:
                        c+=1
                    elif reroll==0:
                        skull+=1
                    c-=1
        print("Devastating Roll!!")
        print("Rerolls:{}".format(r))
        return success,skull


def dist(a,b):
    return np.sqrt((a.xpos-b.xpos)**2+(a.ypos-b.ypos)**2)

def get_closest_target(unit,board,angles):   #avec angles un objet de classe intervalle
    a=unit.aim
    d=10000
    for e in board:
        v2=vct.Vector2D(e.xpos-unit.xpos,e.ypos-unit.ypos)              #Vecteur entre les deux éléments
        if e.faction!=unit.faction:
            if dist(e, unit)<d and dist(e, unit)!=0 and angles.inf <= vct.get_angle(a, v2) * np.pi / 180 <= angles.sup:
                d=dist(e,unit)
    return d



def get_valid_targets(unit,board,weapon):
    a=unit.aim
    dmin=weapon.ShortRange
    dmax=weapon.LongRange
    Targets=[]
    A=weapons.angles
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
    LongRange=False
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


