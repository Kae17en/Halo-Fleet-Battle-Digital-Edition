from abc import *
from classes.loadouts import *


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


class Weapons():
    """
    Cette classe est la superclasse permettant de définir toutes les armes.
    """
    def __init__(self,WType,ShortRange,LongRange,Dice,Arcs,Tag,Loadouts):
        self.__WType=WType
        self.__ShortRange=ShortRange
        self.__LongRange=LongRange
        self.__Dice=Dice
        self.__Arcs=Arcs
        self.__Tag=Tag
        self.__Loadouts=Loadouts

    @property
    def WType(self):
        return self.__WType

    @property
    def DisplayRanges(self):
        return "{}/{}".format(self.__ShortRange,self.__LongRange)
    @property
    def DisplayDice(self):
        return self.__Dice
    @property
    def DisplayWType(self):
        return self.__WType
    @property
    def Shortrange(self):
        return self.__ShortRange
    @property
    def LongRange(self):
        return self.__LongRange

    @property
    def __str__(self):
        return self.__Tag
    @property
    def angles(self):
        arcs = []
        L=self.__Arcs
        for e in L:
            if e == front:
                arcs.append(intervalle(-45, 45))
            elif e == starboard:
                arcs.append(intervalle(45, 135))
            elif e == port:
                arcs.append(intervalle(-135, -45))
            elif e == aft:
                arcs.append(intervalle(-135, -180))
                arcs.append(intervalle(135, 180))
        return arcs
    @property
    def loadouts(self):
        return self.__Loadouts

