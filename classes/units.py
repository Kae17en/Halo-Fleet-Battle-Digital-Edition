import numpy as np
from abc import *
import classes.weapons
import classes.loadouts as loads
import vectors2d as vct
from config import *


#----------------------------------------------#Vaisseaux#-----------------------------------------------

#Superclasse vaisseau
from classes import weapons


class TheoryElement(metaclass=ABCMeta):

    """
    Cette classe est la superclasse utilisée pour la création de tout pion du plateau.Elle n'intègre que les
    statistiques de l'élément, sans prendre en compte les variables du token liées à la situation en jeu
    Les types de variables attendus dans le constructeur sont:
    (Liste taille 3,Liste taille 3,entier,entier,entier,string,Booléen,entier,string,entier,sprite,pg.rect,
    string,liste de ref au dico equipement,liste de ref dico armes)
    """
    def __init__(self,pos,DT,CDT,Hangars,BR,Movement,Tag,Capital,Size,BC,faction,ld, docked):
        self.__DamageTrack=DT        #liste contenant 3 entiers positifs,damage track initiale
        self._CDamageTrack=CDT       #Damage track actuelle, relative à l'attribut
        self.__Hangars=Hangars       #entier représentant le nombre de hangars de l'élément
        self._BuildRating=BR         #entier entre 0 et 6, coût d'ajout de l'élément au groupe
        self._MoveRange=Movement     #distance de mouvement maximale
        self.Tag=Tag                 #Nom de l'élément(str)
        self._Capital=Capital        #Booléen valant True si l'élément est capital
        self._Size=Size              #Taille de l'élément,Small,Medium,Large,Gigantic
        self._BuildCost=BC           #Cout d'ajout à la flotte
        self._Faction=faction        #Faction à laquelle appartient l'élément. Aussi joueur controleur
        self.__Loadouts=ld           #Liste d'équipements
        self.xpos = pos[0]                #Position en x
        self.ypos = pos[1]            #Position en y
        self.set_aim((0,0))                       #Direction pointée par l'unité
        self.__primary=0             #Arme primaire
        self.__secondary=0           #Arme Secondaire
        self.__primarybis=0          #En cas d'arme primaire double
        self.__secondarybis=0        #En cas d'arme secondaire double
        self.docked = docked                            #En cas d'arme secondaire double
        self.activated=False
        self.locked=False
        self.engagements=[]
        self.image = ""
        self.sizeFactor = 1

    #Gestion de la Damage Track---------------------------

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
    def pos(self):
        return self.xpos,self.ypos

    @property
    def aim(self):
        return self._aim

    def get_angle(self):
        return ((np.arctan(self.aim[0]/self.aim[1]))*180/np.pi)


    def set_aim(self,CursorPos):
       self._aim = vct.vector_from_dots(CursorPos,(self.xpos,self.ypos))


    def set_pos(self,L):
        self.xpos=L[0]
        self.ypos=L[1]

    #-------------Surcharge de str pour affichage---------

    def __str__(self):
        return self.Tag

    #--------------Gestion des armes-----------------

    @property
    def primary(self):
        return self.__primary

    @property
    def secondary(self):
        return self.__secondary
    @property
    def primarybis(self):
        return self.__primarybis
    @property
    def secondarybis(self):
        return self.__secondarybis
    #------------------------Gestion de la distance de mouvement-------------------------
    @property
    def MoveRange(self):
        return self._MoveRange
    @MoveRange.setter
    def MoveRange(self,d):
        self._MoveRange=d
    #---------------------------Autres------------------------

    @property
    def faction(self):
        return self.__Faction

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





#-------------------------------Core Elements: UNSC----------------------------#

class UNSC_Supported_Epoch(TheoryElement):

    def __init__(self,pos,aim, docked = []):
        super().__init__(DT=[10,8,5],docked=docked,Hangars=6,BR=5,Movement=6,Tag="UNSC Supported Epoch Heavy Carrier",Capital=True,Size="Large",
                 BC=190,faction="UNSC",ld=[loads.Carrier_Action(3),loads.Hard_Burn(7),loads.Missile_Barrage(),loads.Point_Defence(6),
                                           loads.Titanium_Armor(5)])

        self.__primary=weapons.Weapons("MAC",10,20,12,["Forth"],"Light MAC",[loads.Light_MAC])
        self.__secondary=weapons.Weapons("Missile",12,24,15,["Starboard","Port"],"Missile Batteries",[loads.Missile_Weapon])

class UNSC_Epoch_Heavy_Carrier(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[9,8,5],docked=docked,Hangars=6,BR=4,Movement=6,Tag="UNSC Epoch Heavy Carrier",Capital=True,Size="Large",
                 BC=175,faction="UNSC",ld=[loads.Carrier_Action(3),loads.Hard_Burn(7),loads.Missile_Barrage(),loads.Point_Defence(5),
                                           loads.Titanium_Armor(4)])

        self.__primary=weapons.Weapons("MAC",10,20,10,["Forth"],"Light MAC",[loads.Light_MAC])
        self.__secondary=weapons.Weapons("Missile",12,24,12,["Starboard","Port"],"Missile Batteries",[loads.Missile_Weapon])

class UNSC_Supported_Marathon_Heavy_Cruiser(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[7,6,3],Hangars=2,docked=docked,BR=3,Movement=8,Tag="UNSC Supported Marathon Heavy Cruiser",Capital=True,Size="Medium",
                 BC=110,faction="UNSC",ld=[loads.Hard_Burn(10),loads.Missile_Barrage(),loads.Point_Defence(4),
                                           loads.Titanium_Armor(4)])

        self.__primary=weapons.Weapons("MAC",16,32,10,["Forth"],"Heavy MAC",[loads.Heavy_MAC])
        self.__secondary=weapons.Weapons("Missile",12,24,8,["Starboard","Port"],"Missile Batteries",[loads.Missile_Weapon])

class UNSC_Marathon_Heavy_Cruiser(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[6,6,3],Hangars=2,docked=docked,BR=2,Movement=8,Tag="UNSC Marathon Heavy Cruiser",Capital=True,Size="Medium",
                 BC=95,faction="UNSC",ld=[loads.Hard_Burn(10),loads.Missile_Barrage(),loads.Point_Defence(4),
                                           loads.Titanium_Armor(3)])

        self.__primary=weapons.Weapons("MAC",16,32,8,["Forth"],"Heavy MAC",[loads.Heavy_MAC])
        self.__secondary=weapons.Weapons("Missile",12,24,7,["Starboard","Port"],"Missile Batteries",[loads.Missile_Weapon])

class UNSC_Paris_Frigate_Arrow(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(pos=pos,DT=[3,3,3],docked=docked,CDT=[3,3,3],Hangars=0,BR=1,Movement=10,Tag="UNSC Paris Frigate (Arrowhead Formation)",Capital=False,Size="Small",
                 BC=25,faction="UNSC",ld=[loads.Hard_Burn(13),loads.Missile_Barrage(),loads.Point_Defence(2),
                                           loads.Titanium_Armor(2),loads.Elusive])

        self.image = "Assets/Drawable/Ships/UNSC/Elements/UNSC_Paris_Frigate_Arrowhead_Formation.png"
        self.sizeFactor = 0.1
        self.set_aim(aim)
        self.__primary=weapons.Weapons("MAC",10,20,4,["Forth"],"Light MAC",[loads.Light_MAC])
        self.__secondary=weapons.Weapons("Missile",12,24,2,["Starboard","Port"],"Missile Batteries",[loads.Missile_Weapon])

class UNSC_Paris_Frigate_Trident(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[4,3,3],Hangars=0,docked=docked,BR=1,Movement=10,Tag="UNSC Paris Frigate (Trident Formation)",Capital=False,Size="Small",
                 BC=25,faction="UNSC",ld=[loads.Hard_Burn(13),loads.Missile_Barrage(),loads.Point_Defence(2),
                                           loads.Titanium_Armor(2),loads.Elusive])

        self.__primary=weapons.Weapons("MAC",10,20,3,["Forth"],"Light MAC",[loads.Light_MAC])
        self.__secondary=weapons.Weapons("Missile",12,24,3,["Starboard","Port"],"Missile Batteries",[loads.Missile_Weapon])


#--------------------Core Elements: Covenants------------------------

class Covenant_Supported_ORS_Heavy_Cruiser(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[11,10,6],Hangars=6,docked=docked,BR=5,Movement=5,Tag="Covenant Supported ORS Heavy Cruiser",Capital=True,Size="Large",
                 BC=220,faction="Covenant",ld=[loads.Cloaking_System,loads.Defence_Array(5),loads.Glide(3),loads.Point_Defence(6),loads.Elusive])

        self.__primary=weapons.Weapons("Plasma",18,32,14,["Forth","Port","Starboard"],"Plasma Lance",[loads.Plasma_Lance()])
        self.__primarybis=weapons.Weapons("Plasma",12,None,9,["Forth","Port","Starboard"],"Plasma Beam",[loads.Beam(),loads.Plasma_Weapon()])
        self.__secondary=weapons.Weapons("Plasma",10,20,12,["Forth","Port","Starboard"],"Plasma Cannon Arrays",[loads.Plasma_Weapon()])
        self.__secondarybis=weapons.Weapons("Plasma/Missile",12,24,5,["Forth"],"Plasma Torpedoes",[loads.Plasma_Weapon(),loads.Missile()])

class Covenant_ORS_Heavy_Cruiser(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[11,10,5],docked=docked,Hangars=5,BR=4,Movement=5,Tag="Covenant Heavy Cruiser",Capital=True,Size="Large",
                 BC=25,faction="UNSC",ld=[loads.Cloaking_System(),loads.Defence_Array(4),loads.Glide(3),loads.Point_Defence(5)])


        self.__primary=weapons.Weapons("Plasma",18,32,14,["Forth","Port","Starboard"],"Plasma Cannon Arrays",[loads.Plasma_Weapon()])
        self.__primarybis=weapons.Weapons("Plasma",12,None,9,["Forth","Port","Starboard"],"Plasma Beam",[loads.Beam(),loads.Plasma_Weapon()])
        self.__secondary=weapons.Weapons("Plasma",10,20,10,["Forth","Starboard","Port"],"Plasma Cannon Arrays",[loads.Plasma_Weapons()])

class Covenant_Supported_CCS_Battlecruiser(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[8,7,4],Hangars=3,docked=docked,BR=4,Movement=7,Tag="Covenant Supported CCS BattleCruiser",Capital=True,Size="Medium",
                 BC=170,faction="Covenant",ld=[loads.Cloaking_System(),loads.Defence_Array(5),loads.Glide(4),loads.Point_Defence(4),
                                               loads.Carrier_Action(1)])


        self.__primary=weapons.Weapons("Plasma",18,32,12,["Forth","Port","Starboard"],"Plasma Lance",[loads.Plasma_Lance()])
        self.__secondary=weapons.Weapons("Plasma",10,20,10,["Forth","Port","Starboard"],"Plasma Cannon Arrays",[loads.Plasma_Weapon()])
        self.__secondarybis=weapons.Weapons("Plasma",12,24,5,["Forth"],"Plasma Torpedoes",[loads.Plasma_Weapons(),loads.Missile_Weapon()])

class Covenant_CCS_Battlecruiser(TheoryElement):
    def __init__(self,pos,aim,docked = []):
        super().__init__(pos,DT=[8,7,3],CDT=[8,7,3],Hangars=2,BR=3,Movement=8,Tag="Covenant CCS BattleCruiser",Capital=True,Size="Medium",
                 BC=150,faction="Covenant",docked=docked,ld=[loads.Defence_Array(4),loads.Glide(4),loads.Point_Defence(3),
                                               loads.Carrier_Action(1)])
        self.image = "Assets/Drawable/Ships/Covenant/Elements/Covenant_CSS_BattleCruiser.png"
        self.set_aim(aim)
        self.__primary=weapons.Weapons("Plasma",18,32,12,["Forth","Port","Starboard"],"Plasma Lance",[loads.Plasma_Lance()])
        self.__secondary=weapons.Weapons("Plasma",10,20,9,["Forth","Port","Starboard"],"Plasma Cannon Arrays",[loads.Plasma_Weapon()])

class Covenant_SDV_Heavy_Corvette_Line(TheoryElement):
    def __init__(self,pos,aim,docked= []):
        super().__init__(DT=[4,4,3],Hangars=1,docked=docked,BR=1,Movement=9,Tag="Covenant SDV Heavy Corvette (Line Formation)",Capital=False,Size="Small",
                 BC=40,faction="Covenant",ld=[loads.Cloaking_System(),loads.Defence_Array(2),loads.Glide(5),loads.Point_Defence(3),
                                               loads.Cloaking_System()])

        self.__primary=weapons.Weapons("Plasma",10,20,3,["Forth","Port","Starboard"],"Plasma Cannon Arrays",[loads.Plasma_Weapon()])
        self.__secondary=weapons.Weapons("Plasma",12,24,4,["Forth"],"Plasma Torpedoes",[loads.Plasma_Weapon(),loads.Missile_Weapon()])

class Covenant_SDV_Heavy_Corvette_Oblique(TheoryElement):
    def __init__(self,pos,aim, docked= []):
        super().__init__(DT=[4,3,3],Hangars=1,docked=docked,BR=1,Movement=9,Tag="Covenant SDV Heavy Corvette (Oblique Formation)",
                         Capital=False,Size="Small",BC=40,faction="Covenant",
                         ld=[loads.Cloaking_System(),loads.Defence_Array(2),loads.Glide(5),loads.Point_Defence(3),
                             loads.Cloaking_System()])

        self.__primary=weapons.Weapons("Plasma",10,20,4,["Forth","Port","Starboard"],"Plasma Cannon Arrays",
                                         [loads.Plasma_Weapon()])
        self.__secondary=weapons.Weapons("Plasma",12,24,3,["Forth"],"Plasma Torpedoes",
                                           [loads.Plasma_Weapon(),loads.Missile_Weapon()])


#----------------------------Bombers and Fighters,UNSC----------------------------

class Spacecraft():
    def __init__(self,DT,Movement,Tag,faction,FS,vswing,vselement):
        self.__DamageTrack=DT
        self._MoveRange=Movement
        self.Tag=Tag
        self._Faction=faction
        self.xpos=0
        self.ypos=0
        self.__Flight_Slot=FS
        self.__vs_wing_dice=vswing
        self.__vs_elem_dice=vselement
        self.image = ""
        self.icon = ""
        self.locked = False
        self.dock_unit = []
        self.activated = False
        self.locked = False
        self.engagements = []
        self.WingType = None
        self.attacked = False
        self._aim = vct.vector_from_dots((0,0), (1, 1))
        self.sizeFactor = 1


    @property
    def vs_wing_dice(self):
        return self

    @property
    def DamageTrack(self):
        return self.__DamageTrack

    @property
    def aim(self):
        return self._aim

    def get_angle(self):
        return ((np.arctan(self.aim[1] / self.aim[0])) * 180 / np.pi)

    def set_aim(self, CursorPos):
        self._aim = vct.vector_from_dots(CursorPos, (self.xpos, self.ypos))

    @property
    def pos(self):
        return self.xpos,self.ypos

    def set_pos(self,L):
        self.set_aim(L)
        self.xpos=L[0]
        self.ypos=L[1]


    @property
    def MoveRange(self):
        return self._MoveRange

    @property
    def __str__(self):
        return self.Tag

    @property
    def Dock_Unit(self):
        return self.dock_unit

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
                if e.WingType=="Bomber":
                    e.del_engagement(target)
                    target.del_engagement(e)
                elif e.attacked==True:
                    e.del_engagement(target)
                    target.del_engagement(e)

    def __str__(self):
        return self.Tag





class UNSC_Broadsword_Interceptor_Flight(Spacecraft):
    def __init__(self,pos,n):
        super().__init__(DT=2,Movement=16,Tag="UNSC Broadsword Interceptor Flight",faction="UNSC",FS=1,vselement=0,vswing=2)
        self.xpos=pos[0]
        self.ypos=pos[1]
        self.UnitNumber = n
        self.WingType = "Interceptor"

    @property
    def FlightSize(self):
        return self.UnitNumber
    @property
    def vs_wing_dice(self):
        return self.vs_wing_dice

    @property
    def UnitNumber(self):
        return self.UnitNumber

    @UnitNumber.setter
    def setFlightSize(self,n):
        self.UnitNumber=n

class UNSC_Longsword_Bomber_Flight(Spacecraft):
    def __init__(self,pos,n):
        super().__init__(DT=2,Movement=16,Tag="UNSC Longsword Bomber Flight",faction="UNSC",FS=1,vselement=2,vswing=1)
        self.xpos=pos[0]
        self.ypos=pos[1]
        self.UnitNumber=n
        self.WingType = "Bomber"

    @property
    def FlightSize(self):
        return self.UnitNumber
    @property
    def vs_wing_dice(self):
        return self.vs_wing_dice

    @property
    def UnitNumber(self):
        return self.UnitNumber

    @UnitNumber.setter
    def setFlightSize(self,n):
        self.UnitNumber=n

class Covenant_Banshee_Interceptor_Flight(Spacecraft):
    def __init__(self,pos,n):
        super().__init__(DT=2,Movement=16,Tag="Covenant Banshee Interceptor Flight",faction="Covenant",FS=1,vselement=0,vswing=2)
        self.xpos=pos[0]
        self.ypos=pos[1]
        self.UnitNumber=n
        self.image = "Assets/Drawable/Ships/Covenant/Wings/Covenant_Banshee_Interceptor_Flight.png"
        self.icon = "Assets/Drawable/Ships/Covenant/Wings/Icons/Covenant_Banshee_Interceptor_Flight_Icon.png"
        self.WingType = "Interceptor"

    @property
    def FlightSize(self):
        return self.UnitNumber
    @property
    def vs_wing_dice(self):
        return self.vs_wing_dice



class Covenant_Tarrasque_Interceptor_Flight(Spacecraft):
    def __init__(self,pos,n):
        super().__init__(DT=2,Movement=16,Tag="Covenant Tarrasque Interceptor Flight",faction="Covenant",FS=1,vselement=2,vswing=1)
        self.xpos=pos[0]
        self.ypos=pos[1]
        self.UnitNumber=n
        self.WingType = "Interceptor"

    @property
    def FlightSize(self):
        return self.UnitNumber
    @property
    def vs_wing_dice(self):
        return self.vs_wing_dice

    def UnitNumber(self):
        return self.UnitNumber

    def setFlightSize(self, n):
        self.UnitNumber = n

