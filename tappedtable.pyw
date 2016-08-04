#!/usr/bin/env Python
"""Goal of this program is to take in a link from the wonderful tappedout.net and
ouput the deck in a format that TabletopSimulator can understand for easy magic deck importing."""
import wx
from tools import *

class SimpleGUI(wx.Frame):
    """This is a point and click version. Saves a set of images under a folder in the same directory and cleans it's mess. I hate GUI shit .-.
    """
    def __init__(self):
        wx.Frame.__init__(self, None, -1, title = "Tapped Table")
        panel = wx.Panel(self)
        self.updateText = ""
        #elements
        self.button = wx.Button(panel, -1, label = "Create Image(s)")
        self.url = wx.TextCtrl(panel, -1,size = (150, 20), style = wx.TE_PROCESS_ENTER)
        label = wx.StaticText(panel, -1, label = "Enter a tappedout.net deck URL:")
        self.status = wx.TextCtrl(panel, -1, size= (250, 60), value = "", style = wx.TE_MULTILINE)
        self.status.SetEditable(False)
        #sizers
        urlSizer = wx.BoxSizer(wx.HORIZONTAL)
        urlSizer.Add(self.url)
        urlSizer.Add(self.button)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(label)
        mainSizer.Add(urlSizer)
        mainSizer.Add(self.status)
        panel.SetSizer(mainSizer)
        frameSizer = wx.BoxSizer(wx.HORIZONTAL)
        frameSizer.Add(panel)
        #binds
        self.url.Bind(wx.EVT_TEXT_ENTER, self.onGenerate)
        self.button.Bind(wx.EVT_BUTTON, self.onGenerate)
        self.threadstatus = dict() #hub for threads to say how theyre doin.
        #Getting it to work
        self.SetSizer(frameSizer)
        self.Fit()
        self.Center()
        #Timer stuff
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.updateStatus, self.timer)
    def onGenerate(self, evt):
        #check if thread is already running, then make a new thread if it isnt.
        #No additional thread, safe to make a new one
        print("Creating Thread")
        thread = WorkerThread(self.url.GetValue(), self.threadstatus)
        thread.start()
        if not self.timer.IsRunning():
            self.timer.Start(300)

    def updateStatus(self, evt):
        string = ""
        for name, status in self.threadstatus.items():
            string += name + ": " + status +'\n'
        self.status.SetValue(string)
        if active_count() > 1:
            wx.CallLater(300, self.updateStatus)


if __name__ == '__main__':
    app = wx.App(True, 'log.txt')
    frame = SimpleGUI()
    frame.Show()
    app.MainLoop()
