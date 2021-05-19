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
from panda3d.core import Filename

mydir = os.path.abspath(sys.path[0])

# Convert that to panda's unix-style notation.
mydir = Filename.fromOsSpecific(mydir).getFullpath()

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        winProps = WindowProperties()
        winProps.setSize(1920, 1080)
        winProps.setFullscreen(True)
        base.win.requestProperties(winProps)
        self.menu = MainMenu()
        self.menu.show()

        # self.scene = self.loader.loadModel("models/environment")
        # # Reparent the model to render.
        # self.scene.reparentTo(self.render)
        # # Apply scale and position transforms on the model.
        # self.scene.setScale(0.25, 0.25, 0.25)
        # self.scene.setPos(-8, 42, 0)

class MainMenu(DirectObject):
    def __init__(self):
        self.mainFrame = DirectFrame(frameColor=(0, 0, 0, 1),
                                     frameSize=(-1,1,1,1),
                                     pos=(-1, 0, -0.1))

        self.bg = OnscreenImage('pic/Main-background.jpg')
        self.bg.reparentTo(render2d)

        maps = loader.loadModel(mydir + '/UI/Button/button_maps.egg')

        btn = DirectButton(text="Quit",
                           command='',
                           pos=(-0.3, 0, -0.2),
                           parent=self.mainFrame,
                           scale=0.07,
                           geom=(maps.find('**/Normal'),
                                 maps.find('**/Pressed'),
                                 maps.find('**/Highlight'),
                                 maps.find('**/Disabled')),
                           frameSize=(-4, 4, -1, 1),
                           text_scale=0.75,
                           relief=DGG.FLAT,
                           text_pos=(0, -0.2))
        btn.setTransparency(True)


    def show(self):
        self.mainFrame.show()

    def hide(self):
        self.mainFrame.hide()

app = MyApp()
app.run()