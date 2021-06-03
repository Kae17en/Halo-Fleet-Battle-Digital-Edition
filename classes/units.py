import numpy as np
from abc import *
import classes.weapons
import classes.loadouts as loads
import vectors2d as vct
from config import *
from math import *
import random
import unittest


#----------------------------------------------#Vaisseaux#-----------------------------------------------

#Superclasse vaisseau
from classes import weapons


class TheoryElement(metaclass=ABCMeta):

    """
    This class is a theoric class that is the base for all elements (i.e spaceships) in the game. All sub-classes
    will have nearly every argument set by default according to element's sheets given in the rulebook. The only
    arguments that actually need to be given by the user while creating tokens are its position and aim.

    - DisplayDamageTrack can be used to show the element DT to the user by including it in the IHM as a string

    - CDamageTrack is the current DT of the element, eventually modified by enemy attacks or miscellaneous effects
      It is a list of 3 numbers at maximum

    - DamageTrack is the initial DT of the element, depending on what is written on its token caracteristics sheet.
      It is a list of exactly 3 numbers that should NEVER be modified

    - pos is the current position of the token on board as a tuple of two coordinates (xpos, ypos)

    - aim is the current direction aim by the bow of the spaceship, given as a vector from vectors2d library

    - str(self) overloads str to display to the user the name of the element

    - primary, secondary, primarybis,secondarybis are weapons class objects imported from the weapons.py file.
      They are the  weaponry that can be used by the element against enemies

    - MoveRange is a number modeling the maximum distance that can be travelled by the token in 1 Turn

    - Faction should only be either "Covenant" or "UNSC". It also gives informations about which player controls
      the token.

    - loadouts is a list of loadouts-type objects from the loadouts file. It is all the equipments mounted on the
     the spaceship

    - activated and locked are booleans values used by the game logic to determine wether or not some actions can
      be done by the element.

    - engagements is a list of enemy wings that are involved in a dogfight or bomber run with this token

    - add_engagement is a method taking an opponent as argument to add it to the "engagements" list

    - Sizefactor is a number between 0 and 1 used to scale the element's token on the battlefield

    - Type is either "Element" or "Wing" and is simply used to determine the type of token
    """
    def __init__(self,pos,DT,CDT,Hangars,BR,Movement,Tag,Capital,Size,BC,faction,ld, docked, SizeFactor):
        self.__DamageTrack=DT        #liste contenant 3 entiers positifs,damage track initiale
        self._CDamageTrack=DT      #Damage track actuelle, relative à l'attribut
        self.__Hangars=Hangars       #entier représentant le nombre de hangars de l'élément
        self._BuildRating=BR         #entier entre 0 et 6, coût d'ajout de l'élément au groupe
        self._MoveRange=Movement     #distance de mouvement maximale
        self.Tag=Tag                 #Nom de l'élément(str)
        self._Capital=Capital        #Booléen valant True si l'élément est capital
        self._Size=Size              #Taille de l'élément,Small,Medium,Large,Gigantic
        self._BuildCost=BC           #Cout d'ajout à la flotte
        self.__Faction=faction        #Faction à laquelle appartient l'élément. Aussi joueur controleur
        self.__Loadouts=ld           #Liste d'équipements
        self.xpos = pos[0]                #Position en x
        self.ypos = pos[1]            #Position en y
        self.set_aim((0,0))                       #Direction pointée par l'unité
        self.primary=None          #Arme primaire
        self.secondary=None           #Arme Secondaire
        self.primarybis=None         #En cas d'arme primaire double
        self.secondarybis=None        #En cas d'arme secondaire double
        self.docked = docked                            #En cas d'arme secondaire double
        self.activated=False
        self.locked=False
        self.engagements=[]
        self.image = ""
        self.sizeFactor = SizeFactor
        self.weaponsPos= []
        self.explosionLocation = []
        self.weaponsRange = []
        self.Type = "Element"
        self.ClickUNSC = ['Assets/Sounds/Ship_Click/UNSC/Ship_Click_1', 'Assets/Sounds/Ship_Click/UNSC/Ship_Click_2',
                          'Assets/Sounds/Ship_Click/UNSC/Ship_Click_3'
            , 'Assets/Sounds/Ship_Click/UNSC/Ship_Click_4', 'Assets/Sounds/Ship_Click/UNSC/Ship_Click_5',
                          'Assets/Sounds/Ship_Click/UNSC/Ship_Click_6'
            , 'Assets/Sounds/Ship_Click/UNSC/Ship_Click_7', 'Assets/Sounds/Ship_Click/UNSC/Ship_Click_8']
        self.ClickCovenant = ['Assets/Sounds/Ship_Click/Covenant/Ship_Click_1',
                              'Assets/Sounds/Ship_Click/Covenant/Ship_Click_2',
                              'Assets/Sounds/Ship_Click/Covenant/Ship_Click_3'
            , 'Assets/Sounds/Ship_Click/Covenant/Ship_Click_4', 'Assets/Sounds/Ship_Click/Covenant/Ship_Click_5',
                              'Assets/Sounds/Ship_Click/Covenant/Ship_Click_5'
            , 'Assets/Sounds/Ship_Click/Covenant/Ship_Click_6', 'Assets/Sounds/Ship_Click/Covenant/Ship_Click_7',
                              'Assets/Sounds/Ship_Click/Covenant/Ship_Click_8']


    def __del__(self):
        for target in self.engagements:
            target.del_engagement(self)

    def destroySelf(self):
        for target in self.engagements:
            target.del_engagement(self)

    #Gestion de la Damage Track---------------------------
    @property
    def weapons(self):
        txt = ''
        if self.primary != None:
            txt += '-' + str(self.primary) + '\r\n'
        print(self.primary)
        if self.primarybis != None:
            txt += '-' + str(self.primarybis) + '\r\n'
        if self.secondary != None:
            txt += '-' + str(self.secondary) + '\r\n'
        if self.secondarybis != None:
            txt += '-' + str(self.secondarybis) + '\n'
        return txt

    @property
    def DisplayCDamageTrack(self):   #Permet d'afficher proprement la DT
        return "{}/{}/{}".format(self._CDamageTrack[0],self._CDamageTrack[1],self._CDamageTrack[2])

    @property
    def CDamageTrack(self):        #Récupère la DT pour calculs internes
        return self._CDamageTrack
    @property
    def DamageTrack(self):
        return self.__DamageTrack

    @CDamageTrack.setter
    def CDamageTrack(self,L):            #Avec L la liste de 3 entiers, nouvelle DT
        self._DamageTrack=L

    #Gestion de la position-------------------------------
    def deployWing(self,unit):
        i = self.docked.index(unit)
        self.docked.pop(i)
    @property
    def faction(self):
        return self.__Faction


    @property
    def pos(self):
        return (self.xpos,self.ypos)

    @property
    def aim(self):
        return self._aim

    @aim.setter
    def aim(self, vector):
        self._aim = vector

    def get_angle(self):
        angle = atan2(1, 0) - atan2(self.aim[1], self.aim[0])
        return angle*180/np.pi

    def get_angleRad(self):
        angle = atan2(1, 0) - atan2(self.aim[1], self.aim[0])
        return angle


    def set_aim(self,CursorPos):
       self._aim = vct.vector_from_dots((self.xpos,self.ypos), CursorPos)


    def set_pos(self,L):
        self.xpos=L[0]
        self.ypos=L[1]

    #-------------Surcharge de str pour affichage---------

    def __str__(self):
        return self.Tag

    #--------------Gestion des armes-----------------

    # @property
    # def primary(self):
    #     return self._primary
    # 
    # @property
    # def secondary(self):
    #     return self._secondary
    # 
    # @property
    # def primarybis(self):
    #     return self._primarybis
    # @property
    # def secondarybis(self):
    #     return self._secondarybis
    #------------------------Gestion de la distance de mouvement-------------------------
    @property
    def MoveRange(self):
        return self._MoveRange
    @MoveRange.setter
    def MoveRange(self,d):
        self._MoveRange=d
    #---------------------------Autres------------------------


    @property
    def loadouts(self):
        return self.loadouts

    @property
    def Hangars(self):
        return self.__Hangars

    def add_engagement(self, opp):
        self.engagements.append(opp)
        self.locked = True

    def del_engagement(self,opp):
        if opp in self.engagements:
            n= self.engagements.index(opp)
            self.engagements.pop(n)
        if len(self.engagements)==0:
            self.locked=False
            self.attacked=False

    @property
    def type(self):
        return self.type

    # ---------------------------Gestion des sons------------------------

    @property
    def ClickSound(self):
        n = random.randint(1, 9)
        if self._Faction == "UNSC":
            return self.ClickUNSC[n]
        else:
            return self.ClickCovenant[n]



#-------------------------------Core Elements: UNSC----------------------------#

class UNSC_Supported_Epoch(TheoryElement):

    def __init__(self,pos,aim, docked = []):
        super().__init__(DT=[10,8,5],docked=docked,Hangars=6,BR=5,Movement=6,Tag="UNSC Supported Epoch Heavy Carrier",Capital=True,Size="Large",
                 BC=190,faction="UNSC",ld=[loads.Carrier_Action(3),loads.Hard_Burn(7),loads.Missile_Barrage(),loads.Point_Defence(6),
                                           loads.Titanium_Armor(5)],SizeFactor=0.83)

        self.image='Assets/Drawable/Ships/UNSC/Elements/UNSC_Supported_Epoch_Heavy_Cruiser.png'
        self.__primary=weapons.Weapons("MAC",10,20,12,["Forth"],"Light MAC",[loads.Light_MAC])
        self.__secondary=weapons.Weapons("Missile",12,24,15,["Starboard","Port"],"Missile Batteries",[loads.Missile_Weapon])

class UNSC_Epoch_Heavy_Carrier(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[9,8,5],docked=docked,Hangars=6,BR=4,Movement=6,Tag="UNSC Epoch Heavy Carrier",Capital=True,Size="Large",
                 BC=175,faction="UNSC",ld=[loads.Carrier_Action(3),loads.Hard_Burn(7),loads.Missile_Barrage(),loads.Point_Defence(5),
                                           loads.Titanium_Armor(4)],SizeFactor=0.83)

        self.image='Assets/Drawable/Ships/UNSC/Elements/UNSC_Epoch_Heavy_Cruiser.png'
        self.__primary=weapons.Weapons("MAC",10,20,10,["Forth"],"Light MAC",[loads.Light_MAC])
        self.__secondary=weapons.Weapons("Missile",12,24,12,["Starboard","Port"],"Missile Batteries",[loads.Missile_Weapon])

class UNSC_Supported_Marathon_Heavy_Cruiser(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[7,6,3],Hangars=2,docked=docked,BR=3,Movement=8,Tag="UNSC Supported Marathon Heavy Cruiser",Capital=True,Size="Medium",
                 BC=110,faction="UNSC",ld=[loads.Hard_Burn(10),loads.Missile_Barrage(),loads.Point_Defence(4),
                                           loads.Titanium_Armor(4)],SizeFactor=0.4)

        self.image='Assets/Drawable/Ships/UNSC/Elements/UNSC_Supported_Marathon_Heavy_Cruiser.png'
        self.__primary=weapons.Weapons("MAC",16,32,10,["Forth"],"Heavy MAC",[loads.Heavy_MAC])
        self.__secondary=weapons.Weapons("Missile",12,24,8,["Starboard","Port"],"Missile Batteries",[loads.Missile_Weapon])

class UNSC_Marathon_Heavy_Cruiser(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[6,6,3],Hangars=2,docked=docked,BR=2,Movement=8,Tag="UNSC Marathon Heavy Cruiser",Capital=True,Size="Medium",
                 BC=95,faction="UNSC",ld=[loads.Hard_Burn(10),loads.Missile_Barrage(),loads.Point_Defence(4),
                                           loads.Titanium_Armor(3)],SizeFactor=0.4)

        self.image='Assets/Drawable/Ships/UNSC/Elements/UNSC_Marathon_Heavy_Cruiser.png'
        self.__primary=weapons.Weapons("MAC",16,32,8,["Forth"],"Heavy MAC",[loads.Heavy_MAC])
        self.__secondary=weapons.Weapons("Missile",12,24,7,["Starboard","Port"],"Missile Batteries",[loads.Missile_Weapon])

class UNSC_Paris_Frigate_Arrow(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(pos=pos,DT=[3,3,3],docked=docked,CDT=[3,3,3],Hangars=0,BR=1,Movement=10,Tag="UNSC Paris Frigate (Arrowhead Formation)",Capital=False,Size="Small",
                 BC=25,faction="UNSC",ld=[loads.Hard_Burn(13),loads.Missile_Barrage(),loads.Point_Defence(2),
                                           loads.Titanium_Armor(2),loads.Elusive], SizeFactor=0.159)

        self.weaponsPos = [(1.25, -0.4), (-1.25, -0.4), (0, 1.5)]
        self.weaponsRange = [(-110,110),(-110,110),(-110,110)]
        self.explosionLocation = [(1.25,-0.8),(-1.25,-0.8),(0,1.1)]
        self.image = "Assets/Drawable/Ships/UNSC/Elements/UNSC_Paris_Frigate_Arrowhead_Formation.png"
        self.set_aim(aim)

        self.primary=weapons.Weapons("MAC",10,20,4,["Forth"],"Light MAC",[loads.Light_MAC])
        self.secondary=weapons.Weapons("Missile",12,24,2,["Starboard","Port"],"Missile Batteries",[loads.Missile_Weapon])

class UNSC_Paris_Frigate_Trident(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[4,3,3],Hangars=0,docked=docked,BR=1,Movement=10,Tag="UNSC Paris Frigate (Trident Formation)",Capital=False,Size="Small",
                 BC=25,faction="UNSC",ld=[loads.Hard_Burn(13),loads.Missile_Barrage(),loads.Point_Defence(2),
                                           loads.Titanium_Armor(2),loads.Elusive],SizeFactor=0.159)

        self.image='Assets/Drawable/ShipsUNSC/Elements/UNSC_Paris_Frigate_Trident_Formation.png'
        self.__primary=weapons.Weapons("MAC",10,20,3,["Forth"],"Light MAC",[loads.Light_MAC])
        self.__secondary=weapons.Weapons("Missile",12,24,3,["Starboard","Port"],"Missile Batteries",[loads.Missile_Weapon])


#--------------------Core Elements: Covenants------------------------

class Covenant_Supported_ORS_Heavy_Cruiser(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[11,10,6],Hangars=6,docked=docked,BR=5,Movement=5,Tag="Covenant Supported ORS Heavy Cruiser",Capital=True,Size="Large",
                 BC=220,faction="Covenant",ld=[loads.Cloaking_System,loads.Defence_Array(5),loads.Glide(3),loads.Point_Defence(6),loads.Elusive], SizeFactor=1)

        self.image='Assets/Drawable/Ships/Covenant/Elements/Covenant_Supported_ORS_Heavy_Cruiser.png'
        self.__primary=weapons.Weapons("Plasma",18,32,14,["Forth","Port","Starboard"],"Plasma Lance",[loads.Plasma_Lance()])
        self.__primarybis=weapons.Weapons("Plasma",12,None,9,["Forth","Port","Starboard"],"Plasma Beam",[loads.Beam(),loads.Plasma_Weapon()])
        self.__secondary=weapons.Weapons("Plasma",10,20,12,["Forth","Port","Starboard"],"Plasma Cannon Arrays",[loads.Plasma_Weapon()])
        self.__secondarybis=weapons.Weapons("Plasma/Missile",12,24,5,["Forth"],"Plasma Torpedoes",[loads.Plasma_Weapon(),loads.Missile()])

class Covenant_ORS_Heavy_Cruiser(TheoryElement):
    def __init__(self,pos,aim,docked = []):
        super().__init__(DT=[11,10,5],docked=docked,Hangars=5,BR=4,Movement=5,Tag="Covenant Heavy Cruiser",Capital=True,Size="Large",
                 BC=25,faction="UNSC",ld=[loads.Cloaking_System(),loads.Defence_Array(4),loads.Glide(3),loads.Point_Defence(5)],SizeFactor=1)

        self.image='Assets/Drawable/Ships/Covenant/Elements/Covenant_ORS_Heavy_Cruiser.png'
        self.__primary=weapons.Weapons("Plasma",18,32,14,["Forth","Port","Starboard"],"Plasma Cannon Arrays",[loads.Plasma_Weapon()])
        self.__primarybis=weapons.Weapons("Plasma",12,None,9,["Forth","Port","Starboard"],"Plasma Beam",[loads.Beam(),loads.Plasma_Weapon()])
        self.__secondary=weapons.Weapons("Plasma",10,20,10,["Forth","Starboard","Port"],"Plasma Cannon Arrays",[loads.Plasma_Weapons()])

class Covenant_Supported_CCS_Battlecruiser(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[8,7,4],Hangars=3,docked=docked,BR=4,Movement=7,Tag="Covenant Supported CCS BattleCruiser",Capital=True,Size="Medium",
                 BC=170,faction="Covenant",ld=[loads.Cloaking_System(),loads.Defence_Array(5),loads.Glide(4),loads.Point_Defence(4),
                                               loads.Carrier_Action(1)], SizeFactor=0.594)

        self.image='Assets/Drawable/Ships/Covenant/Elements\Covenant_Supported_CSS_BattleCruiser.png'
        self.__primary=weapons.Weapons("Plasma",18,32,12,["Forth","Port","Starboard"],"Plasma Lance",[loads.Plasma_Lance()])
        self.__secondary=weapons.Weapons("Plasma",10,20,10,["Forth","Port","Starboard"],"Plasma Cannon Arrays",[loads.Plasma_Weapon()])
        self.__secondarybis=weapons.Weapons("Plasma",12,24,5,["Forth"],"Plasma Torpedoes",[loads.Plasma_Weapons(),loads.Missile_Weapon()])

class Covenant_CCS_Battlecruiser(TheoryElement):
    def __init__(self,pos,aim,docked = []):
        super().__init__(pos,DT=[8,7,3],CDT=[8,7,3],Hangars=2,BR=3,Movement=8,Tag="Covenant CCS BattleCruiser",Capital=True,Size="Medium",
                 BC=150,faction="Covenant",docked=docked,ld=[loads.Defence_Array(4),loads.Glide(4),loads.Point_Defence(3),
                                               loads.Carrier_Action(1)], SizeFactor=0.594)

        self.image = "Assets/Drawable/Ships/Covenant/Elements/Covenant_CSS_BattleCruiser.png"
        self.weaponsPos = [(0.025, 1.5)]
        self.weaponsRange = [(-90,90)]
        self.set_aim(aim)

        self.primary=weapons.Weapons("Plasma",18,32,12,["Forth","Port","Starboard"],"Plasma Lance",[loads.Plasma_Lance()])
        self.secondary=weapons.Weapons("Plasma",10,20,9,["Forth","Port","Starboard"],"Plasma Cannon Arrays",[loads.Plasma_Weapon()])

class Covenant_SDV_Heavy_Corvette_Line(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[4,4,3],Hangars=1,docked=docked,BR=1,Movement=9,Tag="Covenant SDV Heavy Corvette (Line Formation)",Capital=False,Size="Small",
                 BC=40,faction="Covenant",ld=[loads.Cloaking_System(),loads.Defence_Array(2),loads.Glide(5),loads.Point_Defence(3),
                                               loads.Cloaking_System()],SizeFactor=0.216)
        self.image='Assets/Drawable/Ships/Covenant/Elements/Covenant_SDV_Heavy_Corvette_Line.png'
        self.__primary=weapons.Weapons("Plasma",10,20,3,["Forth","Port","Starboard"],"Plasma Cannon Arrays",[loads.Plasma_Weapon()])
        self.__secondary=weapons.Weapons("Plasma",12,24,4,["Forth"],"Plasma Torpedoes",[loads.Plasma_Weapon(),loads.Missile_Weapon()])

class Covenant_SDV_Heavy_Corvette_Oblique(TheoryElement):
    def __init__(self,pos,aim, docked= []):
        super().__init__(DT=[4,3,3],Hangars=1,docked=docked,BR=1,Movement=9,Tag="Covenant SDV Heavy Corvette (Oblique Formation)",
                         Capital=False,Size="Small",BC=40,faction="Covenant",
                         ld=[loads.Cloaking_System(),loads.Defence_Array(2),loads.Glide(5),loads.Point_Defence(3),
                             loads.Cloaking_System()],SizeFactor=0.216)

        self.image='Assets/Drawable/Ships/Covenant/Elements/Covenant_SDV_Heavy_Corvette_Oblique.png'
        self.__primary=weapons.Weapons("Plasma",10,20,4,["Forth","Port","Starboard"],"Plasma Cannon Arrays",
                                         [loads.Plasma_Weapon()])
        self.secondary=weapons.Weapons("Plasma",12,24,3,["Forth"],"Plasma Torpedoes",
                                           [loads.Plasma_Weapon(),loads.Missile_Weapon()])


#----------------------------Bombers and Fighters,UNSC----------------------------

class Spacecraft(metaclass=ABCMeta):

    """
    This theoric class is the mother class for all wing tokens in the game. When creating tokens, most arguments will
    be set by default according to the game's RuleBook. The only arguments that need to be given by the user are the
    token's position on the board, and the number of spacecrafts in the squadron.

    - vs_wing_dice is the number of damage dice dealt by the unit to an ennemy wing

    - DamageTrack is the number of damage that can be undergone by the wing before being destroyed

    - pos is the wing's position on board given as a tuple of two real numbers (xpos,ypos)

    - wingtype is a string that can either be "Bomber" of "Interceptor", as both type don't have the same properties

    - MoveRange is a real number refering to the maximum distance can be travelled by the wing in one turn

    - DockUnit is a boolean holding "True" if the wing is docked to an element, "False" if not

    - Type is the type of unit used to distinguish wings from elements. Its value is "Wing" here.

    - str has been overloaded to display the name of the spacecraft squadron to the user.

    - add_engagement and del_engagment are to methods used to add or remove an enemy the engagement list. They both
      take as argument an enemy element or wing

    - engage is a method used to attack and enter combat with another enemy. It handles modifications of the
     engagement lists of the target and the attacker

    - move_unit is a method to change the token's location on the battlefield.

    """

    def __init__(self,DT,Movement,Tag,faction,FS,vswing,vselement):
        self.__DamageTrack=DT
        self._CDT = DT
        self._MoveRange=Movement
        self.Tag=Tag
        self._Faction=faction
        self.xpos=0
        self.ypos=0
        self.__Flight_Slot=FS
        self.__vs_wing_dice=vswing
        self.__vs_elem_dice=vselement
        self.UnitNumber = 0
        self.image = ""
        self.icon = ""
        self.locked = False
        self.dock_unit = []
        self.activated = False
        self.locked = False
        self.engagements = []
        self.explosionLocation = []
        self.WingType = None
        self.attacked = False
        self._aim = vct.vector_from_dots((0,0), (1, 1))
        self.sizeFactor = 1
        self.type = "Wing"

    def __del__(self):
        for target in self.engagements:
            target.del_engagement(self)

    def destroySelf(self):
        for target in self.engagements:
            target.del_engagement(self)

    @property
    def DisplayCDamageTrack(self):
        return str(self._CDT)

    @property
    def vs_wing_dice(self):
        return self

    @property
    def DamageTrack(self):
        return self.__DamageTrack

    @property
    def aim(self):
        return self._aim

    @aim.setter
    def aim(self, vector):
        self._aim = vector

    def get_angle(self):
        angle = atan2(1, 0) - atan2(self.aim[1], self.aim[0])
        return angle * 180 / np.pi

    def get_angleRad(self):
        angle = atan2(1, 0) - atan2(self.aim[1], self.aim[0])
        return angle

    def set_aim(self, CursorPos):
        self._aim = vct.vector_from_dots((self.xpos, self.ypos), CursorPos)

    @property
    def pos(self):
        return self.xpos,self.ypos

    @property
    def wingtype(self):
        return self.WingType

    def set_pos(self,L):
        self.set_aim(L)
        self.xpos=L[0]
        self.ypos=L[1]


    @property
    def MoveRange(self):
        return self._MoveRange

    @property
    def Dock_Unit(self):
        return self.dock_unit

    @property
    def Type(self):
        return self.type

    def add_engagement(self, opp):
        self.engagements.append(opp)
        self.locked = True

    def del_engagement(self,opp):
        if opp in self.engagements:
            n= self.engagements.index(opp)
            self.engagements.pop(n)
        if len(self.engagements)==0:
            self.locked=False
            self.attacked=False

    def move_unit(self,x,y):
        if np.sqrt((self.xpos-x)**2+(self.ypos-y)**2)<=self._MoveRange:
            L=[x,y]
            self.set_pos(L)
            return True
        else:
            return False


    def engage(self,ennemies):
        P=[]
        for e in ennemies:
            if np.sqrt((self.xpos-e.xpos)**2+(self.ypos-e.ypos)**2)<=GLOBAL_ENGAGE_RANGE:
                P.append(e)
        if len(P) > 0:
            target=P[0]
            d=np.sqrt((self.xpos-P[0].xpos)**2+(self.ypos-P[0].ypos)**2)
            for i in range(1,len(P)):
                b=np.sqrt((self.xpos-P[i].xpos)**2+(self.ypos-P[i].ypos)**2)
                if b<d:
                    target=P[i]
            target.attacked=True
            self.add_engagement(target)
            target.add_engagement(self)
            for e in target.engagements:
                if hasattr(e, "WingType") and e.WingType=="Bomber":
                    e.del_engagement(target)
                    target.del_engagement(e)
                elif e.attacked==True:
                    e.del_engagement(target)
                    target.del_engagement(e)

    def __str__(self):
        return self.Tag

    @property
    def faction(self):
        return self._Faction



class UNSC_Broadsword_Interceptor_Flight(Spacecraft):
    def __init__(self,pos,n):
        super().__init__(DT=2,Movement=16,Tag="UNSC Broadsword Interceptor Flight",faction="UNSC",FS=1,vselement=0,vswing=2)
        self.xpos=pos[0]
        self.ypos=pos[1]
        self.UnitNumber = n
        self.WingType = "Interceptor"

        self.sizeFactor = 0.1
        self.image = "Assets/Drawable/Ships/UNSC/Wings/UNSC_ShortSword_Interceptor_Flight.png"
        self.icon = "Assets/Drawable/Ships/UNSC/Wings/Icons/UNSC_ShortSword_Interceptor_Flight_Icon.png"
        self.explosionLocation = [(0,0)]
        self.weaponsPos = [(-0.23, 0.2),(0.17, 0.2)]

    @property
    def FlightSize(self):
        return self.UnitNumber
    @property
    def vs_wing_dice(self):
        return self.vs_wing_dice


class UNSC_Longsword_Bomber_Flight(Spacecraft):
    def __init__(self,pos,n):
        super().__init__(DT=2,Movement=16,Tag="UNSC Longsword Bomber Flight",faction="UNSC",FS=1,vselement=2,vswing=1)
        self.xpos=pos[0]
        self.ypos=pos[1]
        self.UnitNumber=n
        self.WingType = "Bomber"

        self.sizeFactor = 0.1
        self.image = "Assets/Drawable/Ships/UNSC/Wings/UNSC_Longwsord_Bomber_Flight.png"
        self.icon = "Assets/Drawable/Ships/UNSC/Wings/Icons/UNSC_Longwsord_Bomber_Flight_Icon.png"
        self.explosionLocation = [(0, 0)]
        self.weaponsPos = []

    @property
    def FlightSize(self):
        return self.UnitNumber
    @property
    def vs_wing_dice(self):
        return self.vs_wing_dice


class Covenant_Banshee_Interceptor_Flight(Spacecraft):
    def __init__(self,pos,n):
        super().__init__(DT=2,Movement=16,Tag="Covenant Banshee Interceptor Flight",faction="Covenant",FS=1,vselement=0,vswing=2)
        self.xpos=pos[0]
        self.ypos=pos[1]
        self.UnitNumber=n

        self.weaponsPos=[(0.1, 0.7), (-0.1,0.7)]
        self.explosionLocation = [(0,0)]
        self.sizeFactor = 0.1
        self.image = "Assets/Drawable/Ships/Covenant/Wings/Covenant_Banshee_Interceptor_Flight.png"
        self.icon = "Assets/Drawable/Ships/Covenant/Wings/Icons/Covenant_Banshee_Interceptor_Flight_Icon.png"
        self.WingType = "Interceptor"

    @property
    def FlightSize(self):
        return self.UnitNumber
    @property
    def vs_wing_dice(self):
        return self.vs_wing_dice


class Covenant_Seraph_Bomber_Flight(Spacecraft):
    def __init__(self, pos, n):
        super().__init__(DT=2, Movement=16, Tag="Covenant Seraph Bomber Flight", faction="Covenant", FS=1, vselement=0, vswing=2)
        self.xpos=pos[0]
        self.ypos=pos[1]
        self.UnitNumber=n
        self.WingType = "Interceptor"

        self.sizeFactor = 0.1
        self.image = "Assets/Drawable/Ships/Covenant/Wings/Covenant_Seraph_Bomber_Flight.png"
        self.icon = "Assets/Drawable/Ships/Covenant/Wings/Icons/Covenant_Seraph_Bomber_Flight_Icon.png"
        self.explosionLocation = [(0, 0.2)]
        self.weaponsPos = []

    @property
    def FlightSize(self):
        return self.UnitNumber

    @property
    def vs_wing_dice(self):
        return self.vs_wing_dice

class TestUnits(unittest.TestCase):
    unitA = None
    unitB = None
    wingA = None
    wingB = None
    def setUp(self):
        unitA=UNSC_Epoch_Heavy_Carrier((18,19),vct.vector_from_dots((11.8, 11.6), (18, 16)))
        unitB=Covenant_CCS_Battlecruiser((0,8),vct.vector_from_dots((-11.8, 11.6), (-18, 16)))
        wingA=UNSC_Longsword_Bomber_Flight((57,12),6)
        wingB=Covenant_Seraph_Bomber_Flight((34,2),6)
    def testInit(self):
        self.assertIsInstance(self.unitA,TheoryElement)
        self.assertIsInstance(self.unitA,UNSC_Epoch_Heavy_Carrier)
        self.assertFalse(len(self.unitB.loadouts)==0)
        self.assertNotEqual(self.unitA.faction,self.unitB.faction)
        self.assertIsInstance(self.unitA, UNSC_Epoch_Heavy_Carrier)
