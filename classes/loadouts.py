from abc import *
from classes.misc import *

class Loadouts(metaclass=ABCMeta):

    """
    Loadouts are various equipments mounted on an element, a wing or a weapon. They can affect multiple stages of the
    game at different moments. Therefore, all loadouts have one modifier of each kind. Therefore, a entire list of
    loadouts can be called to apply modifications to a situation in the game logic. If a loadout don't modify
    the situation, the modifier associated to the situation is either set to "pass", "None", or 0.
    A loadout modify a situation if the game's rulebook says so.
    In each loadout, str has been overloaded to display the loadout name on the HUD.


    """

    def __init__(self,fpm,dicem):
        self.__fpm=fpm
        self.__dicem=dicem

    @property
    def fpm(self):
        return self.__fpm
    @property
    def dicem(self):
        return self.__dicem





class Light_MAC(Loadouts):
    def __init__(self):
        super().__init__(self,0,0)
        self.__macvalue=1

    @property
    def MacValue(self):
        return self.__macvalue


    def __str__(self):
        return "Light MAC(1)"


class Heavy_MAC(Loadouts):
    def __init__(self):
        super().__init__(self, 0, 0)
        self.__macvalue=2

    @property
    def MacValue(self):
        return self.__macvalue


    def __str__(self):
        return "Heavy MAC(2)"



class Missile_Weapon(Loadouts):
    def __init__(self):
        super().__init__(self, 1, 0)

    def modifyfp(self,LongRange):
        if LongRange==True:
            return self.fpm

    def __str__(self):
        return "Missile Weapon"



class Glide(Loadouts):
    def __init__(self,d):
        super().__init__(0,0)
        self.__gliderange=d
    @property
    def GlideRange(self):
        return self.__gliderange

    def __str__(self):
        return "Glide"

class Hard_Burn(Loadouts):
    def __init__(self,d):
        super().__init__(0,0)
        self.__BurnRange=d
    @property
    def BurnRange(self):
        return self.__BurnRange


    def __str__(self):
        return "Hard Burn"

class Lumbering(Loadouts):
    def __init__(self):
        super().__init__(0,0)


    def __str__(self):
        return "Lumbering"

class Nimble(Loadouts):
    def __init__(self):
        super().__init__(0,0)



    def __str__(self):
        return "Nimble"

class Cloaking_System(Loadouts):
    def __init__(self):
        super().__init__(-1, 0)

    def modifyfp(self,LongRange):
        if LongRange == True:
            return self.fpm


    def __str__(self):
        return "Cloaking System"

class Defence_Array(Loadouts):
    def __init__(self,n):
        super().__init__(0,0)
        self.__ArrayValue=n

    @property
    def ArrayValue(self):
        return self.__ArrayValue

    @property
    def modifydice(self):
        dicem=Damage_Dice_Roll(self.__ArrayValue,4)
        return dicem


    def __str__(self):
        return "Defence Array({})".format(self.__ArrayValue)

class Elusive(Loadouts):
    def __init__(self):
        super().__init__(-1,0)

    def __str__(self):
        return "Elusive"

    @property
    def modifyfp(self):
        return self.fpm

class Hard_Target():
    def __init__(self):
        super().__init__(-1, 0)

    def __str__(self):
        return "Hard Target"

    def modifysuccess(self,n):
        return -n

class Massive():
    def __init__(self):
        pass
    def modifyfp(self,LongRange):
        if LongRange==False:
            return -1


    def __str__(self):
        return "Massive"

class Missile_Barrage():
    def __init__(self):
        pass

    def __str__(self):
        return "Missile Barrage"


class Plasma_Weapon():
    def __init__(self):
        self.__ShortRange = 0

    def modifyfp(self,d):
        if d>self.__ShortRange:
            return -1
        else:
            return +1

    def __str__(self):
        return "Plasma Weapon"

class Beam(Plasma_Weapon):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Plasma Beam"

    @property
    def showspecificoptions(self):
        return "Plasma Beam Attack"

class Plasma_Cannon_Array(Plasma_Weapon):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Plasma Cannon Array"

class Plasma_Torpedoes(Plasma_Weapon):
    def __init__(self):
        super().__init__()


    def modifyfp(self,d):
        if d>=self.__ShortRange:
            return 0
        else:
            return -1

    def __str__(self):
        return "Plasma Torpedoes"

class Plasma_Lance(Plasma_Weapon):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Plasma Lance"

class Point_Defence():
    def __init__(self,n):
        self.__Point_Value=n
    @property
    def Point_Value(self):
        return self.__Point_Value

    @property
    def dicem(self):
        return Damage_Dice_Roll(self.__Point_Value,4)

    def __str__(self):
        return "Point Defence({})".format(self.__Point_Value)

class Titanium_Armor():
    def __init__(self,n):
        self.__Armor_Value=n
    @property
    def ArmorValue(self):
        return self.__Armor_Value
    @property
    def dicem(self):
        return Damage_Dice_Roll(self.__Armor_Value,4)

    def __str__(self):
        return "Titanium Armor({})".format(self.__Armor_Value)

class Carrier_Action():
    def __init__(self,n):
        self.__Carrier_Value=n
    @property
    def Carrier_Value(self):
        return self.__Carrier_Value

    def __str__(self):
        return "Carrier Action({})".format(self.__Carrier_Value)


class Emplacement():
    def __str__(self):
        return "Emplacement"






