#!/usr/bin/env Python
"""Goal of this program is to take in a link from the wonderful tappedout.net and
ouput the deck in a format that TabletopSimulator can understand for easy magic deck importing."""
import wx
from html.parser import HTMLParser
from bs4 import BeautifulSoup #parsing web papge
from PIL import Image #image processing library
import urllib.request #Getting webpage
import os #file commands
import glob #for gettind dir list
import shutil
from threading import *

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
class Deck:
    """Decided to reorder this, making it easier to group all the functions"""
    def __init__(self, url = None):
        """build a deck from a url Gets the data from a tappedout.net webpage and stores it into a card class"""
        self.data = []
        if url != None:
            self.addFromURL(url)
    def addFromURL(self, url):
        """build a deck from a url Gets the data from a tappedout.net webpage and stores it into a card class"""
        local_filename, headers = urllib.request.urlretrieve(url)
        html = open(local_filename)
        soup = BeautifulSoup(html, "html.parser");
        tags = soup.find_all('li', 'member') #refine the list a bit.
        for tag in tags:
            #Okay so now that we have all the tags with cards we want to stick it into a new soup, and refine down to the actual values through the hyperlinks used
            refine_soup = BeautifulSoup(str(tag), 'html.parser')
            links = refine_soup.find_all('a')
            temp = Card()
            for link in links: #Check each link, if it has a value we want, pull it out.
                if link.has_attr("data-image"):
                    temp.img = link.get('data-image')
                if link.has_attr("data-quantity"):
                    temp.num = link.get("data-quantity")
                if link.has_attr("data-name"):
                    temp.name = link.get("data-name")
            self.data.append(temp) #add the card to the list.
    def printDeck(self):
        for card in self.data:
            card.printCard()
    def download(self, directory):
        """Downloads all the card images into a folder to be used later."""
        #Check if directory exists
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)
        for card in self.data:
            #go through and save each card in images
            urllib.request.urlretrieve(card.img, directory+"/"+card.name+'.'+card.img.rsplit('.', 1)[1])
            #print(card.name, " has been saved to "+ directory)
    def delete(self):
        """Super simple, deletes the directory when we're done with it., mostly just puts it under a friendly name"""
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)
            #print(self.directory+" has been deleted")
        else:
            #print("cannot find directory, not deleted")
            pass
    def findCard(self, name):
        """This function returns a card from it's name, returns None if not found"""
        result = None
        for card in self.data:
            if card.name == name:
                result = card
                break
        return result
    def count(self):
        """returns how many cards in the deck"""
        count = 0
        for card in self.data:
            count += int(card.num)
        return count
    def stitch(self, imgnumx, imgnumy, resolutionx, resolutiony, borderpx, hidden = None):
        """MUST RUN DOWNLOAD FOR THIS TO WORK.
        imgnumx: how many images side per side in a row usually 10
        imgnumy: how many images on top of each other. usually 7
        resolutionx: all the resolutions have to be the same, so set it here
        resolutiony: y version of x
        borderpx: All magic cards have a border, usually black, which is all I support here, this is how this the border will be
        this stitches all the image into a grid so TabletopSimulator and other things can read it. """
        #first off create an image array with all the images, and resize the images so theyre all the same size
        imagedata = []
        for f in glob.glob(self.directory+'/*'):
            #print("Adding " + f + " to imagedata" )
            im = Image.open(f)
            im = im.resize((resolutionx,resolutiony)) #resize it so we can stitch it evenly
            #Instead of being nice to tabletop I wanna have the cards repeat, instead of looping it ourselves so we'll append them multiple times
            i = 0
            repeats = self.findCard(f.split('\\', 1)[1].split('.',1)[0])
            repeats= int(repeats.num)

            for i in range(repeats): #Not gonna lie, gross. 1 less than the found cards number based on filename
                imagedata.append(im) #add it to the list multiple times if needed, prob a memory hog :/
        #create the base black image.
        #Can only incorporate 69 images I believe for TTS, so make sure you can have them all
        finalarray = []
        new_im = Image.new("RGB",(imgnumx*(resolutionx+2*borderpx), imgnumy*(resolutiony+2*borderpx)), (0,0,0))
        if hidden != None:
            new_im.paste(Image.open(hidden).resize((resolutionx, resolutiony)), ((borderpx + (resolutionx + 2*borderpx) * (imgnumx-1), borderpx + (resolutiony + 2*borderpx) *(imgnumy-1))))
        countx = 0 #Counters to keep track of where to paste the image
        county = 0
        count = 0
        #add each image to the picture
        #print(imagedata)
        while imagedata != []:
            #print("entered while loops")
            im = imagedata.pop(0)
            new_im.paste(im, (borderpx + (resolutionx + 2*borderpx) * countx, borderpx + (resolutiony + 2*borderpx) *county))
            countx += 1 #prepare for the next loop
            count += 1
            #Check if you need to reset position
            if countx == imgnumx:
                #reset
                countx = 0
                county +=1
            if count == 69:
                #print("New image!")
                #image is full, append current and start a new
                finalarray.append(new_im) #save done image
                new_im = Image.new("RGB",(imgnumx*(resolutionx+2*borderpx), imgnumy*(resolutiony+2*borderpx)), (0,0,0))
                if hidden != None:
                    new_im.paste(Image.open(hidden).resize((resolutionx, resolutiony)), ((borderpx + (resolutionx + 2*borderpx) * (imgnumx-1), borderpx + (resolutiony + 2*borderpx) *(imgnumy-1))))
                countx = 0
                county = 0
                count = 0
        finalarray.append(new_im) #add final image toarray
        #print("Done!")
        return finalarray




class Card:
    """data holder for convenience."""
    def __init__(self, img, num, name):
        self.img = img
        self.num = num
        self.name = name
    def __init__(self):
        self.img = None
        self.num = None
        self.name = None
    def printCard(self):
        print (self.num, "x ", self.name, " (", self.img, ") ")


if __name__ == '__main__':
    app = wx.App()
    frame = SimpleGUI()
    frame.Show()
    app.MainLoop()
