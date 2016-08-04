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
        #Getting it to work
        self.SetSizer(frameSizer)
        self.Fit()
        self.Center()
        #binds
        self.url.Bind(wx.EVT_TEXT_ENTER, self.onGenerate)
        self.button.Bind(wx.EVT_BUTTON, self.onGenerate)
    def onGenerate(self, evt):
        #check if thread is already running, then make a new thread if it isnt.
        if active_count() == 1: #No additional thread, safe to make a new one
            thread = WorkerThread(self.url.GetValue(), self.status)
            thread.run()



#Im gonna be lame and just have it all in one filename
class WorkerThread(Thread):
    def __init__(self, url, status = None):
        self.url = url
        self.status = status
        if status != None:
            self.update = True #set this flag if we wanna update on progress
        else:
            self.update = False
    def run(self):
        if self.update:
            self.status.SetValue("Reading Webpage...")
        if self.url == '' or "tappedout.net/mtg-decks" not in self.url :
            self.status.SetValue("Please enter a tappedout.net deck URL")
            return
        deck = Deck(self.url)
        if self.update:
            self.status.SetValue(self.status.GetValue() + "\nGathering Images...")
        deck.download("images") #save images locally to beused
        savespot = self.url.split("/")[-2] #Use the deck name for a save spot
        if self.update:
            self.status.SetValue(self.status.GetValue() + "\nStitching together...")
        finalImages = deck.stitch(10, 7, 464, 664, 15) #stitch them bitches
        if self.update:
            self.status.SetValue(self.status.GetValue() + "\nCleaning resources...")
        deck.delete() #clear out images
        if self.update:
            self.status.SetValue(self.status.GetValue() + "\nSaving result in " + savespot + "...")
        if not os.path.exists(savespot):
            os.makedirs(savespot)
        i = 1
        for image in finalImages:
            image.save(savespot + '/' + str(i) + ".jpg", "JPEG")
            i +=1
        if self.update:
            self.status.SetValue(self.status.GetValue() + "\nResults saved at " + savespot  + ", card count is " + str(deck.count()))

if __name__ == '__main__':
    app = wx.App(True, 'log.txt')
    frame = SimpleGUI()
    frame.Show()
    app.MainLoop()
