from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from direct.task import Task
from direct.fsm import FSM
import sys, os
from panda3d.core import loadPrcFileData
from direct.filter.CommonFilters import CommonFilters
from DirectGuiExtension.DirectBoxSizer import DirectBoxSizer
from panda3d.core import Filename, OrthographicLens, MouseWatcherGroup, MouseWatcher, MouseWatcherRegion, TransparencyAttrib, PNMImageHeader, Vec3, CollisionNode, GeomNode, CollisionRay, CollisionTraverser, CollisionHandlerQueue, LineSegs, Texture
from gameLogic import *
import ctypes

mydir = os.path.abspath(sys.path[0])

# Convert that to panda's unix-style notation.
mydir = Filename.fromOsSpecific(mydir).getFullpath()

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.keyMap = {
            "Escape": False,
        }
        winProps = WindowProperties()
        winProps.setSize(1920, 1080)
        winProps.setFullscreen(True)
        self.win.requestProperties(winProps)
        self.accept("escape", self.updateKeyMap, ["Escape", True])
        self.accept("mouse1", self.handle_element_click)
        self.accept("mouse3", self.handle_unselect)
        self.taskMgr.add(self.handleQuit, "detect-escape")
        self.MouseNavDisabled = False

        self.menu = MainMenu(self)
        self.menu.show()
        self.Frames = [[],[]]
        self.movable = []

        self.clickonObjectTrav = CollisionTraverser()
        self.clickonObject = CollisionHandlerQueue()
        pickerNode = CollisionNode('mouseRay')
        pickerNP = self.cam.attachNewNode(pickerNode)
        pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay = CollisionRay()
        pickerNode.addSolid(self.pickerRay)
        self.clickonObjectTrav.addCollider(pickerNP, self.clickonObject)

    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState

    def handleQuit(self, task):
        if self.keyMap["Escape"]:
            self.quit()
        return task.cont

    def quit(self):
        sys.exit(0)

    def handle_unselect(self):
        if hasattr(self, "detailed"):
            del self.detailed

    def StartGame(self):
        self.HUD = HUD(self)
        self.setBackgroundColor(0.1,0.1,0.1,1)
        self.bg = OnscreenImage('Assets/Terrain/Background.jpg', pos=(0,0,0), scale=(1000*self.getAspectRatio(), 1,1000))
        self.bg.setTag('clickable', "fond")
        self.bg.reparentTo(render)

        self.lens = OrthographicLens()
        self.lens.setFilmSize(1920, 1080)
        self.lens.setNearFar(-50, 50)
        self.cam.node().setLens(self.lens)

        self.accept('wheel_up', self.handle_zoom_out)
        self.accept('wheel_down', self.handle_zoom_in)

        self.MouseNav = MouseWatcher()

        self.MouseNav.addRegion(MouseWatcherRegion("bot", -2, 2, -1, -0.98))
        self.MouseNav.addRegion(MouseWatcherRegion("top", -2, 2, 0.98, 1))
        self.MouseNav.addRegion(MouseWatcherRegion("left", -1, -0.99, -1, 1))
        self.MouseNav.addRegion(MouseWatcherRegion("right", 0.99, 1, -1, 1))

        #self.MouseNav.showRegions(render2d, 'gui-popup', 0)

        self.taskMgr.add(self.handle_mouse_nav, "mouse-nav")
        self.taskMgr.add(self.show_moving_object, "move-range")
        self.taskMgr.add(self.UpdateGameState, "update-state")


        self.HUD.show()


        self.Game = MainGame(self)

        UNSC = Player("UNSC")
        Covenant = Player("Covenant")

        UNSC.addToken(UNSC_Paris_Frigate_Arrow((0, 0), (2.8, 11.6)))
        Covenant.addToken(Covenant_CCS_Battlecruiser((300, 300), (12.7, 1.3), docked=[Covenant_Banshee_Interceptor_Flight((300,300), 3)]))

        self.music = loader.loadSfx("Assets/Music/Ambiant.mp3")
        self.music.setLoop(True)
        self.music.play()

        self.Game.startGameFromSituation(UNSC, Covenant)

    def setPlayer(self, player):
        self.GlobalState[2] = player


    def UpdateGameState(self, task):
        for object in self.UNSC.tokens:
            if (object in self.Frames[0]):
                i = self.Frames[0].index(object)
            else:
                i = len(self.Frames[0])
                self.Frames[0].append(object)
                img = self.loadImageRealScaleWithFactor(object.image, render, SHIP_IMAGE_SCALE_FACTOR)
                img.setPos(0,0,0)
                img.setTransparency(TransparencyAttrib.MAlpha)
                self.Frames[1].append(img)
                self.Frames[1][i].reparentTo(render)
                self.Frames[1][i].setTag('clickable', str(id(self.Frames[0][i])))
            self.Frames[1][i].setPos(object.xpos, -1, object.ypos)
            self.Frames[1][i].setHpr(0, 0, object.get_angle())
        for object in self.Covenant.tokens:
            if (object in self.Frames[0]):
                i = self.Frames[0].index(object)
            else:
                i = len(self.Frames[0])
                self.Frames[0].append(object)
                img = self.loadImageRealScaleWithFactor(object.image, render, SHIP_IMAGE_SCALE_FACTOR)
                img.setPos(0, 0, 0)
                img.setTransparency(TransparencyAttrib.MAlpha)
                self.Frames[1].append(img)
                self.Frames[1][i].reparentTo(render)
                self.Frames[1][i].setTag('clickable', str(id(self.Frames[0][i])))
            self.Frames[1][i].setPos(object.xpos, -2, object.ypos)
            self.Frames[1][i].setHpr(0, 0, object.get_angle())
        for i in range(len(self.Frames[0])):
            if (self.Frames[0][i] not in self.UNSC.tokens and self.Frames[0][i] not in self.Covenant.tokens):
                self.Frames[1][i].destroy()
                self.Frames[0].pop(i)
                self.Frames[1].pop(i)
        self.HUD.setGameInfo(self.GlobalState)
        return task.cont

    def handle_element_click(self):
        mpos = self.mouseWatcherNode.getMouse()
        self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())
        self.clickonObjectTrav.traverse(render)
        # Assume for simplicity's sake that myHandler is a CollisionHandlerQueue.
        if self.clickonObject.getNumEntries() > 0:
            # This is so we get the closest object.
            self.clickonObject.sortEntries()
            i = 0
            pickedObjG = self.clickonObject.getEntry(i).getIntoNodePath()
            pickedObj = pickedObjG.getTag('clickable')
            while(not pickedObj and i < self.clickonObject.getNumEntries()):
                i += 1
                pickedObjG = self.clickonObject.getEntry(i).getIntoNodePath()
                pickedObj = pickedObjG.getTag('clickable')
            if pickedObj and pickedObj != "":
                if pickedObj == "fond":
                    if(hasattr(self, "detailed")):
                        del self.detailed
                elif pickedObj == "range":
                    if(not self.detailed.rangeOnly):
                        NewPos = self.clickonObject.getEntry(0).getSurfacePoint(NodePath(self.cam)) + (self.cam.getX(), 0, self.cam.getZ())
                        if (distAB(self.detailed.object.xpos, self.detailed.object.ypos, NewPos[0], NewPos[2]) < MOVE_RANGE_SCALE_FACTOR * self.detailed.object.MoveRange): #Request Move To Game logic
                            success = self.Game.requestMove(self.detailed.object, (NewPos[0], NewPos[2]))
                            if success == 0:
                                loader.loadSfx("Assets/Sounds/ShipMove.mp3").play()
                            elif success == 1:
                                self.HUD.popupError("Already Moved this phase !")
                        del self.detailed
                elif pickedObj == "moveObject":
                    loader.loadSfx("Assets/Sounds/ButtonClick.mp3").play()
                    self.detailed.drawMove()
                elif pickedObj == "deployWing":
                    loader.loadSfx("Assets/Sounds/ButtonClick.mp3").play()
                    self.detailed.showWingMenu()
                elif pickedObj == "deploySelectedWing":
                    loader.loadSfx("Assets/Sounds/ButtonClick.mp3").play()
                    self.detailed.deploy(ctypes.cast(int(pickedObjG.getTag("wingId")), ctypes.py_object).value)
                elif pickedObj == "WDeployrange":
                    NewPos = self.clickonObject.getEntry(0).getSurfacePoint(NodePath(self.cam)) + (self.cam.getX(), 0, self.cam.getZ())
                    if (distAB(self.detailed.object.xpos, self.detailed.object.ypos, NewPos[0], NewPos[2]) < MOVE_RANGE_SCALE_FACTOR * self.detailed.wing.MoveRange): #deplacement du wing
                        self.Game.deployWing(self.detailed.wing, self.detailed.object)  # Deploiment du wing
                        succes = self.Game.requestMove(self.detailed.wing, (NewPos[0], NewPos[2]))
                        if succes == 0:
                            loader.loadSfx("Assets/Sounds/ShipMove.mp3").play()
                    del self.detailed
                else:
                    element = ctypes.cast(int(pickedObj), ctypes.py_object).value
                    isSelectableForAction, isMovable, canDeploy = self.Game.requestObjectSelect(element)
                    if(hasattr(self, "detailed")):
                        del self.detailed
                    loader.loadSfx("Assets/Sounds/ButtonClick.mp3").play()
                    self.detailed = objectDetails(element, self.HUD, isMovable, canDeploy, aspectRatio=self.getAspectRatio(), rangeOnly=(not isSelectableForAction))

    def show_moving_object(self, task):
        if(hasattr(self, "detailed")):
            mpos = self.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())
            self.clickonObjectTrav.traverse(render)

            if self.clickonObject.getNumEntries() > 0:

                self.clickonObject.sortEntries()
                pickedObj = self.clickonObject.getEntry(self.clickonObject.getNumEntries()-1).getSurfacePoint(NodePath(self.camNode))
                pickedObj[0] += self.cam.getX()
                pickedObj[2] += self.cam.getZ()
                self.detailed.drawRangeLine(pickedObj)

        return task.cont

    def setMovable(self, objects):
        self.movable = objects

    def handle_zoom_in(self):
        if(min(self.lens.film_size - (5000 * globalClock.getDt() * self.getAspectRatio(), 5000 * globalClock.getDt())) > 0):
             self.lens.setFilmSize(self.lens.film_size - (5000 * globalClock.getDt() * self.getAspectRatio(), 5000 * globalClock.getDt()))

    def handle_zoom_out(self):
        if(self.lens.film_size < (1920,1080)):
            self.lens.setFilmSize(self.lens.film_size + (5000 * globalClock.getDt() * self.getAspectRatio(), 5000 * globalClock.getDt()))

    def handle_mouse_nav(self, task):
        if(not self.MouseNavDisabled):
            try:
                reg = self.MouseNav.getOverRegion(self.mouseWatcherNode.getMouseX(), self.mouseWatcherNode.getMouseY())
                if(reg):
                    if(reg.getName() == "top" and (self.cam.getZ() + self.lens.film_size[0]/2) < (self.bg.getTexture().getYSize()/1.6)):
                        self.cam.setZ(self.cam.getZ()+ 400 * globalClock.getDt())
                    elif(reg.getName() == "bot" and (self.cam.getZ() - self.lens.film_size[0]/2) > (-self.bg.getTexture().getYSize()/1.6)):
                        self.cam.setZ(self.cam.getZ() - 400 * globalClock.getDt())
                    elif(reg.getName() == "left" and (self.cam.getX() - self.lens.film_size[1]/2) > (-self.bg.getTexture().getXSize()/1.6)):
                        self.cam.setX(self.cam.getX() - 400 * globalClock.getDt())
                    elif(reg.getName() == "right" and (self.cam.getX() + self.lens.film_size[1]/2) < (self.bg.getTexture().getXSize()/1.6)):
                        self.cam.setX(self.cam.getX() + 400 * globalClock.getDt())
            except Exception:
                pass
        return task.cont

    def setGameState(self, UNSC, Covenant, State):
        self.UNSC = UNSC
        self.Covenant = Covenant
        self.GlobalState = State #(PHASE, TURN, ACTUAL_PLAYER)

    def NextPlayer(self):
        loader.loadSfx("Assets/Sounds/ButtonClick.mp3")
        if (hasattr(self, "detailed")):
            del self.detailed
        self.Game.nextPlayer()

    def EndTurn(self):
        loader.loadSfx("Assets/Sounds/ButtonClick.mp3")
        self.Game.endTurn()

    def save(self):
        pass

    def loadImageRealScaleWithFactor(self, name, parent, factor):
        iH = PNMImageHeader()
        iH.readHeader(Filename(name))
        yS = float(iH.getYSize())
        np = OnscreenImage(name)
        np.setScale(Vec3(iH.getXSize(), 1, yS) / self.win.getYSize()*factor)
        np.setTransparency(TransparencyAttrib.MAlpha)
        np.reparentTo(parent)
        return np



class MainMenu(DirectObject):
    def __init__(self, app):
        self.app = app
        self.mainFrame = DirectFrame(frameColor=(0, 0, 0, 1),
                                     frameSize=(-1,1,1,1),
                                     pos=(-1, 0, -0.1))

        self.bg = OnscreenImage('pic/Main-background.jpg')
        self.bg.reparentTo(render2d)


        Quit = DirectButton(text="Quit",
                           command=self.quit,
                           pos=(-0.2, 0, -0.2),
                           parent=self.mainFrame,
                           clickSound=loader.loadSfx("Assets/Sounds/ButtonClick.mp3"),
                           rolloverSound=loader.loadSfx("Assets/Sounds/ButtonHover.mp3"),
                           scale=0.07,
                           frameSize=(-4, 4, -1, 1),
                           text_scale=0.75,
                           relief=DGG.FLAT,
                           text_pos=(0, -0.2))
        Quit.setTransparency(True)

        Load = DirectButton(text="Load Game",
                           command=self.LoadGame,
                           clickSound=loader.loadSfx("Assets/Sounds/ButtonClick.mp3"),
                           rolloverSound=loader.loadSfx("Assets/Sounds/ButtonHover.mp3"),
                           pos=(-0.2, 0, 0),
                           parent=self.mainFrame,
                           scale=0.07,
                           frameSize=(-4, 4, -1, 1),
                           text_scale=0.75,
                           relief=DGG.FLAT,
                           text_pos=(0, -0.2))
        Load.setTransparency(True)

        New = DirectButton(text="New Game",
                           command='',
                           rolloverSound=loader.loadSfx("Assets/Sounds/ButtonHover.mp3"),
                           clickSound=loader.loadSfx("Assets/Sounds/ButtonClick.mp3"),
                           pos=(-0.2, 0, 0.2),
                           parent=self.mainFrame,
                           scale=0.07,
                           frameSize=(-4, 4, -1, 1),
                           text_scale=0.75,
                           relief=DGG.FLAT,
                           text_pos=(0, -0.2))
        New.setTransparency(True)
        self.music = loader.loadSfx("Assets/Music/MainMenuMusic.mp3")
        self.music.setLoop(True)
        self.music.play()

    def show(self):
        self.mainFrame.show()

    def hide(self):
        self.mainFrame.hide()
        self.bg.hide()
        self.music.stop()

    def quit(self):
        self.app.quit()

    def LoadGame(self):
        self.hide()
        self.app.StartGame()


class HUD(DirectObject):
    def __init__(self, app):
        self.Frame = []
        self.app = app
        self.globalFrame = DirectFrame(frameColor=(0, 0, 0, 0), frameSize=(-2, 2, -1, 1))
        self.Bar = DirectFrame(frameColor=(0, 0, 0, 0), frameSize=(-1.2, 1.2, 0, 0.2))
        Name = self.loadImageRealScale('Assets/HUD/NameHolder.png', self.Bar)
        Name.setPos(-1.37,0,0)

        self.Bar.setPos(0, 0, -0.95)
        self.SideMenu = DirectFrame(frameColor=(0, 0, 0, 0),
                              frameSize=(-0.3, 0, -0.6, 0.6))
        self.SideMenu.setPos(1.7, 0, 0)
        self.loadImageRealScale('Assets/HUD/SideMenu.png', self.SideMenu)

        self.TopBar = DirectFrame(frameColor=(0, 0, 0, 0),
                                    frameSize=(-1.8, 1.8, -0.1, 0))
        self.TopBar.setPos(0, 0, 0.95)
        self.loadImageRealScale('Assets/HUD/TopBar.png', self.TopBar)
        self.SelectedName = OnscreenText('', pos=(-1.40, -0.98), scale=(0.027,0.03), font=loader.loadFont("Assets/HUD/Halo.ttf"))

        self.Phase = OnscreenText('', pos=(0, 0.96), scale=0.03, font=loader.loadFont("Assets/HUD/Halo.ttf"))
        self.Turn = OnscreenText('', pos=(-0.4, 0.96), scale=0.03, font=loader.loadFont("Assets/HUD/Halo.ttf"))
        self.Player = OnscreenText('', pos=(0.4, 0.96), scale=0.03, font=loader.loadFont("Assets/HUD/Halo.ttf"))

        self.EndTurn = DirectButton(text="",
                            command=self.app.EndTurn,
                            pos=(1.655,0,-0.96),
                            rolloverSound=loader.loadSfx("Assets/Sounds/ButtonHover.mp3"),
                            clickSound=loader.loadSfx("Assets/Sounds/ButtonClick.mp3"),
                            parent=self.globalFrame,
                            scale=(app.getAspectRatio()*0.07, 1, 0.05),
                            image='Assets/HUD/NextPhase.png',
                            frameSize=(-1, 1, -1, 1),
                            relief=None)

        self.NextPlayer = DirectButton(text="",
                            command=self.app.NextPlayer,
                            pos=(1.655,0,-0.85),
                            rolloverSound=loader.loadSfx("Assets/Sounds/ButtonHover.mp3"),
                            clickSound=loader.loadSfx("Assets/Sounds/ButtonClick.mp3"),
                            parent=self.globalFrame,
                            scale=(app.getAspectRatio()*0.07, 1, 0.05),
                            image='Assets/HUD/NextPlayer.png',
                            frameSize=(-1, 1, -1, 1),
                            relief=None)

        self.EndTurn.setTransparency(True)
        self.NextPlayer.setTransparency(True)

        Quit = DirectButton(text="",
                            command=app.quit,
                            pos=(-1.73, 0, -0.005),
                            rolloverSound=loader.loadSfx("Assets/Sounds/ButtonHover.mp3"),
                            clickSound=loader.loadSfx("Assets/Sounds/ButtonClick.mp3"),
                            parent=self.TopBar,
                            scale=0.018,
                            image='Assets/HUD/quit-squared.png',
                            frameSize=(-1, 1, -1, 1),
                            relief=None)

        Quit.setTransparency(True)

        self.PauseScreen = DirectDialog(frameSize=(-1, 1, -0.7, 0.7),
                                        fadeScreen=0.4,
                                        pos = (0,-2,0),
                                        relief=DGG.FLAT,
                                        parent=aspect2d,
                                        frameTexture = "Assets/PauseMenu/Background.png",
                                        dialogName="PauseDialog",
                                        )
        self.PauseScreen.setTransparency(True)
        self.PauseScreen.hide()

        PScreenResume = DirectButton(text="",
                                     command=self.hidePauseScreen,
                                     rolloverSound=loader.loadSfx("Assets/Sounds/ButtonHover.mp3"),
                                     clickSound=loader.loadSfx("Assets/Sounds/ButtonClick.mp3"),
                                     pos=(-0.3, 0, 0),
                                     scale=(0.13*app.getAspectRatio(), 1, 0.08),
                                     image='Assets/PauseMenu/Resume.png',
                                     relief=None)
        PScreenResume.setTransparency(True)
        PScreenResume.reparentTo(self.PauseScreen)

        PScreenQuit = DirectButton(text="",
                                     command=self.app.quit,
                                     rolloverSound=loader.loadSfx("Assets/Sounds/ButtonHover.mp3"),
                                     clickSound=loader.loadSfx("Assets/Sounds/ButtonClick.mp3"),
                                     pos=(0.3, 0, 0),
                                     scale=(0.13 * app.getAspectRatio(), 1, 0.08),
                                     image='Assets/PauseMenu/Quit.png',
                                     parent=self.PauseScreen,
                                     relief=None)
        PScreenQuit.setTransparency(True)

        PScreenSave = DirectButton(text="",
                                   command=self.app.save,
                                   rolloverSound=loader.loadSfx("Assets/Sounds/ButtonHover.mp3"),
                                   clickSound=loader.loadSfx("Assets/Sounds/ButtonClick.mp3"),
                                   pos=(0, 0, -0.3),
                                   scale=(0.13 * app.getAspectRatio(), 1, 0.08),
                                   image='Assets/PauseMenu/Save.png',
                                   parent=self.PauseScreen,
                                   relief=None)
        PScreenSave.setTransparency(True)


        Pause = DirectButton(text="",
                            command=self.showPauseScreen,
                            pos=(-1.67, 0, -0.005),
                            parent=self.TopBar,
                            rolloverSound=loader.loadSfx("Assets/Sounds/ButtonHover.mp3"),
                            clickSound=loader.loadSfx("Assets/Sounds/ButtonClick.mp3"),
                            scale=0.02,
                            image='Assets/HUD/pause-squared.png',
                            frameSize=(-1, 1, -1, 1),
                            relief=None)

        Pause.setTransparency(True)



        self.ExpandedSideMenu = DirectFrame(frameColor=(1, 1, 0, 0),
                              frameSize=(-0.3, 0, -0.6, 0.6))

        self.ExpandedSideMenu.setPos(1.5, 0, 0)
        self.loadImageRealScale('Assets/HUD/SideMenuExpanded.png', self.ExpandedSideMenu)

        self.Frame.append(self.Bar)
        self.Frame.append(self.SideMenu)
        self.Frame.append(self.TopBar)

        self.errorPopup = DirectDialog(frameSize=(-1, 1, -0.7, 0.7),
                                        fadeScreen=0.4,
                                        pos = (0,-2,0),
                                        relief=None,
                                        parent=render2d,
                                        dialogName="ErrorDialog",
                                        )
        self.loadImageRealScale("Assets/HUD/ErrorBG.png", self.errorPopup)
        self.errorText = OnscreenText('', pos=(-0.5, 0), scale=0.07, font=loader.loadFont("Assets/HUD/Halo.ttf"), parent=self.errorPopup)
        self.errorPopup.hide()


    def showPauseScreen(self):
        self.PauseScreen.show()
        self.app.MouseNavDisabled = True
        self.app.music.stop()

    def hidePauseScreen(self):
        self.PauseScreen.hide()
        self.app.MouseNavDisabled = False
        self.app.music.play()

    def disableUserControl(self):
        self.EndTurn.hide()
        self.NextPlayer.hide()

    def enableUserControl(self):
        self.EndTurn.show()
        self.NextPlayer.show()

    def setGameInfo(self, State):
        Dict = ["Wing Movement", "Wing Attack", "Battle Movement", 'Battle Atack']
        self.Phase.setText(Dict[State[0]])
        self.Turn.setText("Turn " + str(State[1]))
        self.Player.setText("Playing " + State[2].type)
        self.setPlayer(State[2].type)
        if(self.app.Game.NotCurrentPlayer.turnEnded):
            self.NextPlayer.hide()
        else:
            self.NextPlayer.show()

    def popupError(self,error):
        #self.errorPopup.show()
        #self.errorText.setText(error)
        #self.app.taskMgr.doMethodLater(TIME_ERROR_POPUP, self.hideError, 'hide-error-popup')
        pass


    def loadImageRealScale(self, name, parent):
        iH = PNMImageHeader()
        iH.readHeader(Filename(name))
        yS = float(iH.getYSize())
        np = OnscreenImage(name)
        np.setScale(Vec3(iH.getXSize(), 1, yS) / self.app.win.getYSize())
        np.setTransparency(TransparencyAttrib.MAlpha)
        np.reparentTo(parent)
        return np


    def show(self):
        for frame in self.Frame:
            frame.show()
        self.ExpandedSideMenu.hide()

    def setPlayer(self,name):
        if(name == "UNSC"):
            if(hasattr(self, "BarImage")):
                self.BarImage.destroy()
            if (hasattr(self.app, "detailed") and self.app.detailed.object.locked):
                self.BarImage = self.loadImageRealScale('Assets/HUD/Bar.png', self.Bar)
            else:
                self.BarImage = self.loadImageRealScale('Assets/HUD/Bar.png', self.Bar)
        else:
            if (hasattr(self, "BarImage")):
                self.BarImage.destroy()
            if(hasattr(self.app, "detailed") and self.app.detailed.object.locked):
                self.BarImage = self.loadImageRealScale('Assets/HUD/CovBarEngaged.png', self.Bar)
            else:
                self.BarImage = self.loadImageRealScale('Assets/HUD/CovBar.png', self.Bar)


class objectDetails():
    def __init__(self, object, HUD, isMovable, canDeploy, aspectRatio, rangeOnly = False):
        self.HUD = HUD
        self.object = object
        self.HUD.SelectedName.setText(str(object))
        self.moving = False
        self.ratio = aspectRatio
        self.isMovable = isMovable
        self.rangeOnly = rangeOnly
        if issubclass(type(object), Spacecraft) or rangeOnly:
            self.drawMove()
        else:
            self.ObjectMenu = OnscreenImage('Assets/ObjectMenu/Background.png', scale=(100, 1, 75),
                                            pos=(object.xpos - 130, -4, object.ypos - 100), parent=render)
            self.ObjectMenu.setTransparency(TransparencyAttrib.MAlpha)
            lines = LineSegs()
            lines.moveTo(self.object.xpos, -2, self.object.ypos)
            lines.drawTo(self.object.xpos - 30, -2, self.object.ypos - 25)
            lines.setThickness(2)
            lines.setColor(1, 1, 1, 1)
            node = lines.create()
            self.menuline = NodePath(node)
            self.menuline.reparentTo(render)
            if(isMovable):
                self.moveShipButton = OnscreenImage('Assets/ObjectMenu/MoveShipButton.png', scale=(0.4, 1, 0.7), pos=(-0.5, -2, -0.2), parent=self.ObjectMenu)
                self.moveShipButton.setTag('clickable', "moveObject")
            else:
                self.moveShipButton = OnscreenImage('Assets/ObjectMenu/MoveShipButtonDisabled.png', scale=(0.4, 1, 0.7), pos=(-0.5, -2, -0.2), parent=self.ObjectMenu)
            if(canDeploy):
                self.deployButton = OnscreenImage('Assets/ObjectMenu/DeployButton.png', scale=(0.4, 1, 0.7), pos=(0.5, -2, -0.2), parent=self.ObjectMenu)
                self.deployButton.setTag('clickable', "deployWing")
            else:
                self.deployButton = OnscreenImage('Assets/ObjectMenu/DeployButtonDisabled.png', scale=(0.4, 1, 0.7), pos=(0.5, -2, -0.2), parent=self.ObjectMenu)

            self.moveShipButton.setTransparency(TransparencyAttrib.MAlpha)
            self.deployButton.setTransparency(TransparencyAttrib.MAlpha)


    def __del__(self):
        if (hasattr(self, "range")):
            self.range.destroy()
        if(hasattr(self, "np")):
            self.np.removeNode()
            self.engageRange.destroy()
        self.HUD.SelectedName.setText('')
        if (hasattr(self, "ObjectMenu")):
            self.ObjectMenu.destroy()
            self.menuline.removeNode()
            self.moveShipButton.destroy()
            self.deployButton.destroy()
        if(hasattr(self, "Wrange")):
            self.Wrange.destroy()
        if(hasattr(self, "WMenuBackgrounf")):
            for image in self.DeployOptionsFrames:
                image.destroy()
            self.WMenuBackgrounf.destroy()


    def drawRangeLine(self, mpos):
        if(self.moving and not self.rangeOnly):
            tx, ty = 0, 0
            if (hasattr(self, "np")):
                self.np.removeNode()
            lines = LineSegs()
            lines.moveTo(self.object.xpos,-8, self.object.ypos)
            lines.drawTo(1*mpos[0], -8, 1*mpos[2])
            lines.setThickness(4)
            lines.setColor(1,1,0,1)
            node = lines.create()
            self.np = NodePath(node)
            self.np.reparentTo(render)
            if(hasattr(self, "engageRange")):
                self.engageRange.setPos(mpos[0], -8, mpos[2])
            else:
                self.engageRange = OnscreenImage('Assets/Drawable/AttackRange.png', pos=(mpos[0], -8, mpos[2]),scale=(GLOBAL_ENGAGE_RANGE, 1, GLOBAL_ENGAGE_RANGE), parent=render)
                self.engageRange.setTransparency(TransparencyAttrib.MAlpha)

    def drawMove(self):
        self.moving = True
        if (hasattr(self, "ObjectMenu")):
            self.ObjectMenu.destroy()
            self.menuline.removeNode()
            self.moveShipButton.destroy()
            self.deployButton.destroy()
        self.range = OnscreenImage('Assets/Drawable/Range.png', pos=(self.object.xpos, -4, self.object.ypos),
                                   scale=(MOVE_RANGE_SCALE_FACTOR * self.object.MoveRange, 1, MOVE_RANGE_SCALE_FACTOR * self.object.MoveRange), parent=render)
        self.range.setTransparency(TransparencyAttrib.MAlpha)
        self.range.setTag('clickable', "range")


    def showWingMenu(self):
        self.ObjectMenu.destroy()
        self.menuline.removeNode()
        self.moveShipButton.destroy()
        self.deployButton.destroy()

        self.WMenuBackgrounf = OnscreenImage('Assets/ObjectMenu/WingMenuBackground.png', pos=(self.object.xpos - 130, -4, self.object.ypos - 100),
                                    scale=(110, 1, 250), parent=render)
        self.WMenuBackgrounf.setTransparency(TransparencyAttrib.MAlpha)
        self.DeployOptionsFrames = []
        for i in range(len(self.object.docked)):
            option = OnscreenImage(self.object.docked[i].icon, pos=(-0.5 + 0.3*i%3, -6, 0.55 - 0.2*int(i/3)), scale=(ICON_2D_SCALE_FACTOR*self.ratio,1,ICON_2D_SCALE_FACTOR), parent=self.WMenuBackgrounf)
            option.setTag("wingId", str(id(self.object.docked[i])))
            option.setTag("clickable", "deploySelectedWing")
            option.setTransparency(TransparencyAttrib.MAlpha)
            self.DeployOptionsFrames.append(option)

    def deploy(self, wing):
        self.moving = True
        if (hasattr(self, "WMenuBackgrounf")):
            for image in self.DeployOptionsFrames:
                image.destroy()
            self.WMenuBackgrounf.destroy()
        self.Wrange = OnscreenImage('Assets/Drawable/Range.png', pos=(self.object.xpos, -4, self.object.ypos),
                                   scale=(MOVE_RANGE_SCALE_FACTOR * wing.MoveRange, 1, MOVE_RANGE_SCALE_FACTOR * wing.MoveRange), parent=render)
        self.Wrange.setTag('clickable', "WDeployrange")
        self.Wrange.setTransparency(TransparencyAttrib.MAlpha)
        self.wing = wing

def distAB(ax,ay,bx,by):
    return np.sqrt((ax-bx)**2+(ay-by)**2)

app = MyApp()
app.run()