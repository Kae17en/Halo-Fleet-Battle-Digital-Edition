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
from panda3d.core import Filename, OrthographicLens, MouseWatcherGroup, MouseWatcher, MouseWatcherRegion, TransparencyAttrib, PNMImageHeader, Vec3, CollisionNode, GeomNode, CollisionRay, CollisionTraverser, CollisionHandlerQueue
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
        base.win.requestProperties(winProps)
        self.accept("escape", self.updateKeyMap, ["Escape", True])
        self.accept("mouse1", self.handle_element_click)
        self.taskMgr.add(self.handleQuit, "detect-escape")
        self.menu = MainMenu(self)
        self.menu.show()
        self.Frames = [[],[]]

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
        self.taskMgr.add(self.UpdateGameState, "update-state")

        self.HUD.show()

        self.Game = MainGame(self)
        UNSC = Player("UNSC")
        Covenant = Player("Covenant")
        UNSC.addToken(UNSC_Paris_Frigate_Arrow((0, 0), vct.vector_from_dots((11.8, 11.6), (0, 0))))
        Covenant.addToken(Covenant_CCS_Battlecruiser((300, 300), vct.vector_from_dots((12.7, 1.3), (300, 300))))
        self.setGameState(UNSC,Covenant)
        # Game.startGameFromSituation(UNSC, Covenant)

    def UpdateGameState(self, task):
        for object in self.UNSC.tokens:
            if (object in self.Frames[0]):
                i = self.Frames[0].index(object)
            else:
                i = len(self.Frames[0])
                self.Frames[0].append(object)
                self.Frames[1].append(OnscreenImage('Assets/Tokens/UNSC.png', pos=(0,0,0), scale=(10*self.getAspectRatio(), 1,10)))
                self.Frames[1][i].reparentTo(render)
                self.Frames[1][i].setTag('clickable', str(id(self.Frames[0][i])))
            self.Frames[1][i].setPos(object.xpos, -1, object.ypos)
        for object in self.Covenant.tokens:
            if (object in self.Frames[0]):
                i = self.Frames[0].index(object)
            else:
                i = len(self.Frames[0])
                self.Frames[0].append(object)
                self.Frames[1].append(OnscreenImage('Assets/Tokens/Cov.png', pos=(0,0,0), scale=(10*self.getAspectRatio(), 1,10)))
                self.Frames[1][i].reparentTo(render)
                self.Frames[1][i].setTag('clickable', str(id(self.Frames[0][i])))
            self.Frames[1][i].setPos(object.xpos, -2, object.ypos)
        for i in range(len(self.Frames[0])):
            if (self.Frames[0][i] not in self.UNSC.tokens and self.Frames[0][i] not in self.Covenant.tokens):
                self.Frames[1][i].destroy()
                self.Frames[0].pop(i)
                self.Frames[1].pop(i)
        task.cont

    def handle_element_click(self):
        mpos = self.mouseWatcherNode.getMouse()
        self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())
        self.clickonObjectTrav.traverse(render)
        # Assume for simplicity's sake that myHandler is a CollisionHandlerQueue.
        if self.clickonObject.getNumEntries() > 0:
            # This is so we get the closest object.
            self.clickonObject.sortEntries()
            pickedObj = self.clickonObject.getEntry(0).getIntoNodePath()
            pickedObj = pickedObj.getTag('clickable')
            if pickedObj and pickedObj != "":
                if pickedObj == "fond":
                    if(self.detailed):
                        del self.detailed
                else:
                    element = ctypes.cast(int(pickedObj), ctypes.py_object).value
                    self.detailed = objectDetails(element)






    def handle_zoom_in(self):
        if(min(self.lens.film_size - (5000 * globalClock.getDt() * self.getAspectRatio(), 5000 * globalClock.getDt())) > 0):
             self.lens.setFilmSize(self.lens.film_size - (5000 * globalClock.getDt() * self.getAspectRatio(), 5000 * globalClock.getDt()))

    def handle_zoom_out(self):
        if(self.lens.film_size < (1920,1080)):
            self.lens.setFilmSize(self.lens.film_size + (5000 * globalClock.getDt() * self.getAspectRatio(), 5000 * globalClock.getDt()))

    def handle_mouse_nav(self, task):
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

    def setGameState(self, UNSC, Covenant):
        self.UNSC = UNSC
        self.Covenant = Covenant






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
                           scale=0.07,
                           frameSize=(-4, 4, -1, 1),
                           text_scale=0.75,
                           relief=DGG.FLAT,
                           text_pos=(0, -0.2))
        Quit.setTransparency(True)

        Load = DirectButton(text="Load Game",
                           command=self.LoadGame,
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
                           pos=(-0.2, 0, 0.2),
                           parent=self.mainFrame,
                           scale=0.07,
                           frameSize=(-4, 4, -1, 1),
                           text_scale=0.75,
                           relief=DGG.FLAT,
                           text_pos=(0, -0.2))
        New.setTransparency(True)

    def show(self):
        self.mainFrame.show()

    def hide(self):
        self.mainFrame.hide()
        self.bg.hide()

    def quit(self):
        self.app.quit()

    def LoadGame(self):
        self.hide()
        self.app.StartGame()

class HUD(DirectObject):
    def __init__(self, app):
        self.Frame = []
        self.app = app

        self.Bar = DirectFrame(frameColor=(0, 0, 0, 0), frameSize=(-1.2, 1.2, 0, 0.2))
        self.loadImageRealScale('Assets/HUD/Bar.png', self.Bar)

        self.Bar.setPos(0, 0, -0.95)
        self.SideMenu = DirectFrame(frameColor=(0, 0, 0, 0),
                              frameSize=(-0.3, 0, -0.6, 0.6))
        self.SideMenu.setPos(1.7, 0, 0)
        self.loadImageRealScale('Assets/HUD/SideMenu.png', self.SideMenu)

        self.TopBar = DirectFrame(frameColor=(0, 0, 0, 0),
                                    frameSize=(-1.8, 1.8, -0.1, 0))
        self.TopBar.setPos(0, 0, 0.95)
        self.loadImageRealScale('Assets/HUD/TopBar.png', self.TopBar)


        Quit = DirectButton(text="",
                            command=app.quit,
                            pos=(-1.73, 0, -0.005),
                            parent=self.TopBar,
                            scale=0.018,
                            image='Assets/HUD/quit-squared.png',
                            frameSize=(-1, 1, -1, 1),
                            relief=None)

        Quit.setTransparency(True)

        Pause = DirectButton(text="",
                            command='',
                            pos=(-1.67, 0, -0.005),
                            parent=self.TopBar,
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

        buttonImages = ((
            loader.loadTexture('Assets/HUD/Confirm.png'),
            loader.loadTexture('Assets/HUD/ConfirmHover.png'),
            loader.loadTexture('Assets/HUD/ConfirmHover.png'),
            loader.loadTexture('Assets/HUD/ConfirmHover.png'))
        )

        self.Confirm = DirectButton(text="",
                            pos=(0.9, 0, -0.95),
                            parent=render2d,
                            scale=(0.1,1,0.05),
                            frameTexture=buttonImages,
                            frameSize=(-1, 1, -1, 1),
                            relief=DGG.FLAT)

        self.Confirm.setTransparency(True)

    def loadImageRealScale(self, name, parent):
        iH = PNMImageHeader()
        iH.readHeader(Filename(name))
        yS = float(iH.getYSize())
        np = OnscreenImage(name)
        np.setScale(Vec3(iH.getXSize(), 1, yS) / self.app.win.getYSize())
        np.setTransparency(TransparencyAttrib.MAlpha)
        np.reparentTo(parent)


    def show(self):
        for frame in self.Frame:
            frame.show()
        self.ExpandedSideMenu.hide()

class objectDetails():
    def __init__(self, object):
        print("loadinfg")
        self.range = OnscreenImage('Assets/Drawable/Range.png', pos=(object.xpos,-4,object.ypos), scale=(10*object.MoveRange, 1, 10*object.MoveRange), parent=render)
        self.range.setTransparency(TransparencyAttrib.MAlpha)

    def __del__(self):
        self.range.destroy()


app = MyApp()
app.run()