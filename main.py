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
from panda3d.core import Filename, OrthographicLens, MouseWatcherGroup, MouseWatcher, MouseWatcherRegion, TransparencyAttrib

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
        self.taskMgr.add(self.handleQuit, "detect-escape")
        self.menu = MainMenu(self)
        self.menu.show()

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

        self.HUD.show()

    def handle_zoom_in(self):
        if(min(self.lens.film_size - (5000 * globalClock.getDt() * self.getAspectRatio(), 5000 * globalClock.getDt())) > 0):
             self.lens.setFilmSize(self.lens.film_size - (5000 * globalClock.getDt() * self.getAspectRatio(), 5000 * globalClock.getDt()))

    def handle_zoom_out(self):
        if(self.lens.film_size < (1920,1080)):
            self.lens.setFilmSize(self.lens.film_size + (5000 * globalClock.getDt() * self.getAspectRatio(), 5000 * globalClock.getDt()))

    def handle_mouse_nav(self, task):
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
        return task.cont



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
        bg = OnscreenImage('Assets/HUD/Bar.png', scale=(1, 1, 0.1), pos=(0, 0, 0.095))
        bg.setTransparency(TransparencyAttrib.MAlpha)
        bg.reparentTo(self.Bar)

        self.Bar.setPos(0, 0, -1)
        self.SideMenu = DirectFrame(frameColor=(1, 1, 0, 0.3),
                              frameSize=(-0.3, 0, -0.6, 0.6))

        self.SideMenu.setPos(1.8, 0, 0)
        self.TopBar = DirectFrame(frameColor=(0, 0, 0, 0),
                                    frameSize=(-1.8, 1.8, -0.1, 0))
        bg = OnscreenImage('Assets/HUD/TopBar.png', scale=(1.8, 1, 0.05), pos=(0, 0, -0.05))
        bg.setTransparency(TransparencyAttrib.MAlpha)
        bg.reparentTo(self.TopBar)

        Quit = DirectButton(text="",
                            command=app.quit,
                            pos=(-1.7, 0, -0.05),
                            parent=self.TopBar,
                            scale=0.018,
                            image='Assets/HUD/quit-squared.png',
                            frameSize=(-1, 1, -1, 1),
                            relief=None)

        Quit.setTransparency(True)

        Pause = DirectButton(text="",
                            command='',
                            pos=(-1.63, 0, -0.05),
                            parent=self.TopBar,
                            scale=0.02,
                            image='Assets/HUD/pause-squared.png',
                            frameSize=(-1, 1, -1, 1),
                            relief=None)

        Pause.setTransparency(True)


        self.TopBar.setPos(0, 0, 1)

        self.ExpandedSideMenu = DirectFrame(frameColor=(1, 1, 0, 0.3),
                              frameSize=(-0.3, 0, -0.6, 0.6))

        self.ExpandedSideMenu.setPos(1.5, 0, 0)

        self.Frame.append(self.Bar)
        self.Frame.append(self.SideMenu)
        self.Frame.append(self.TopBar)
        self.Frame.append(self.ExpandedSideMenu)




    def show(self):
        for frame in self.Frame:
            frame.show()

app = MyApp()
app.run()