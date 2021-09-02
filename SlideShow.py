#!/usr/bin/env python3
import os
import tkinter
import datetime
import random
import configparser
from itertools import cycle
from PIL import Image, ImageTk



# defaults
PATH = './'
DELAY_TIME = 10000 # 10 seconds
SHUFFLE = False

class Slideshow(tkinter.Tk):
    '''
SlideShow displays a slide show of images (photos, pictures, jpg, gif, etc).
Start the program with a folder to images. All sub-folders will be searched. e.g. : python SlideShow.py  /path/2/config/
The /path/ should have a config.txt file to change program operations. Otherwise hard coded
defaults are used. Format of config.txt:

[screensaver]
delay=15
shuffle=True
timeon=0645
timeoff=2300
scaleup=True
scaledown=True
showfilenames=True
reload=false
timeon=0630
timeoff=2400
includedfolders=  /mmedia/pics
excludedfolders=/mmedia/pics/1996



The meaning of parameters in config.txt:
  delay  - a number, indicates how many seconds to wait between images. 
  shuffle -  True or False, indicates if pictures will be read in order (False) or shuffled (True)
  timeon - a number, indicates a time when screen saver shows images
  timeoff - a number, indicates a time when a black screen wil appear instead of images
  scaleup - True or False, indicates that small pictures will be increased to screen size (True)
  scaledown - True or False, indicates that large pictures will be decreased to screen size (True)
  showfilenames - True or False, bottom of screen will show full file name
  reload - True of False, If the config file changed, indicates if filenames should be reloaded
  includedfolders = pathnames to where files are found including subfolders
  excludedfolders = pathnames to folders and their contents to ignore (not subfolders)

SlideShow will monitor config.txt. If the file changes, new setting will be applied including possibly
re-reading all of the image file names. e.g. I have an older flat screen windows laptop that I am using now for a photo frame. I can sftp new 
files or drag them as a mounted drive. Then I place a config.txt file in the top folder.
To exit SlideShow, hit the Escape or q keys.
Perform left button click to hide the screen and pause.
Perform right button click to advance to next image immediately.
Hit spacebar to pause, and again to resume.

log:
    '''

    print(__doc__)
   
    def __init__(self, path, delay_time, shuffle):
    #------------------------------------------------------
        tkinter.Tk.__init__(self)
        self.delay_time = delay_time # in ms.
        self.path = path # a folder of pictures and subfolders
        self.shuffle = shuffle # mix or no mix images
        self.reload_filenames=False
        self.config_time = 0 # unchanged config file
        self.timeon = 700 # 7am
        self.timeoff = 2200 # 10pm
        self.image_filenames = False # hold the filenames of images
        self.scaleup = True # make small images larger
        self.scaledown = True # make large pictures fit to screen
        self.hide_screen = False
        self.space_bar_pause = False
        self.program_time = os.stat(__file__).st_mtime #time stamp of SlideShow.py
        self.includedfolders = ['.']
        self.excludedfolders = []
        self.showfilenames = True
        self.image_name = 'noimage'
        self.after_id = None
                        
        #get max screen resolution on device
        self.screen_width= self.winfo_screenwidth()
        self.screen_height= self.winfo_screenheight()               
        print("Screen width %d height %d "%(self.screen_width,self.screen_height))
        #set tkinter widget to full screen
        self.geometry("%dx%d+%d+%d" % (self.screen_width,self.screen_height,0,0)) 
        self.configure(bg='black')
        self.attributes('-fullscreen', True)
        self.resizable(False, False)
        # the images will be added to a Label widget
        self.photo_widget= tkinter.Label(self,bg='black',borderwidth=0,padx=0, pady=0)
        self.photo_widget.bind_all('<Any-KeyPress>',self.keypressed)
        self.filename_widget = tkinter.Label(self, font=('Arial', 18),fg='white',bg='black',padx=4,pady=4)
        self.filename_widget.pack(side=tkinter.BOTTOM)
        self.photo_widget.pack()
        self.bind("<Button-1>", self.toggle_screen_visibility)
        self.bind("<Button-3>", self.advance_image_now)
        #self.bind("<Button-1>", lambda x: print("LEFT CLICK"))

    def keypressed(self,event):
        print('key pressed: ',event)
        if event.keycode == 27 or event.char == 'q': # ESC or q to quit
            self.after_cancel(self.after_id)
            self.destroy()
        elif event.keysym =='space': # toggle pause screen
            if self.hide_screen: # turn screen back on
                self.doit()
            else: self.after_cancel(self.after_id) #pause
            self.hide_screen = not self.hide_screen
         
    def advance_image_now (self,event): # screen was clicked by right button
        print("Button right: ",event)
        self.after_cancel(self.after_id)
        print("Button right: ",event)
        self.doit()

    def toggle_screen_visibility(self,event): # screen was clicked by left button
        self.after_cancel(self.after_id)
        self.hide_screen = not self.hide_screen
        print("Button left: ",event, ", screen blank: "+str(self.hide_screen))
        self.doit()



    def get_next_image(self):
    #------------------------------------------------------
        # get the next image 
        try:
            self.image_name =  next(self.image_filenames)
            current_image = Image.open(self.image_name) # load name as PIL Image
            current_image_width, current_image_height = current_image.size
            print("Next image %s, width(%d) height(%d)"%(self.image_name,current_image_width,current_image_height))
            # use this if you want to scale up an down
            ratio_image = current_image_width / current_image_height
            ratio_screen = self.screen_width / self.screen_height
            #determine how best to scale image to screen.  
            if ratio_screen > ratio_image:
                    scaled_width = int( current_image_width * self.screen_height/current_image_height)
                    scaled_height = self.screen_height
            else:
                    scaled_width = self.screen_width
                    scaled_height = int(current_image_height * self.screen_width/ current_image_width)
            if self.scaleup or self.scaledown: # only scale if config.txt indicates to do so
                scaled_image = current_image.resize((scaled_width,scaled_height))
            else:
                scaled_image = current_image
            print("Scale by: width(%d) height(%d)" % (scaled_width,scaled_height))
            # convert PIL image to tkinter image
            self.image = ImageTk.PhotoImage(scaled_image)
            print("Final image: width(%s) height(%d)" % (self.image.width(), self.image.height()))
        except:
            print("*** Error with %s, skipping."%self.image_name)
            pass

    def read_image_filenames(self):
    #------------------------------------------------------
    # We have a list of included folders (and their subfolders) to include plus
    # a list of folders/subfolders to remove
        try:
            # either perform the 1st load or a new load (config.txt) of filenames
            if self.image_filenames == False:
                included_filenames = self.read_folders(self.includedfolders)
                print("Included folders images found: ",len(included_filenames))

                excluded_filenames = self.read_folders(self.excludedfolders)
                print("Excluded folders images found: ",len(excluded_filenames))
                filenames = [f for f in included_filenames if f not in excluded_filenames]
                print("Total images remaining: ",len(filenames))
                if self.shuffle: # determine if we want to shuffle and create iterator of image filenames #print(images)
                    random.shuffle(filenames)
                self.image_filenames = cycle(filenames)
        except:
                print("*** Error reading image filenanmes")

    def read_folders(self,folders):
    #------------------------------------------------------
    # Return a list of all filenames in 'folders' and the subfolders that are an image type
        try:
            exts = ("jpg", "bmp", "png", "gif", "jpeg")
            filenames = []
            # finds pics in all config.txt included folders and their sub-folders 
            for current_folder in folders:
                for root, _, files in os.walk(current_folder):
                    for f in files:
                        if f.endswith(exts) and f not in filenames:
                            # only add if not already added
                            filenames.append(os.path.normpath(os.path.join(root, f)))
            return filenames
        except:
                print("*** Error reading folders")

        
    def check_schedule(self):
    #------ This runs only between begin and end ousrs
        current = int(datetime.datetime.now().strftime('%H%M'))
        if current >= self.timeon and current <= self.timeoff and not self.hide_screen:
            print("Schedule %d - %d now %r " % (self.timeon,self.timeoff, True))
            return True
        else:
            print("Schedule %d - %d now %r " % (self.timeon,self.timeoff, False))
            return False

    def check_for_program_changes(self):
    #------------------------------------------------------
        try:
            # see if config.txt is there and if so, has it been updated
            #config_file = os.path.join(self.path,'config.txt')
            config_file = self.path
            if os.path.exists(config_file) and os.path.isfile(config_file):
                print("Found: ",os.path.abspath(config_file))
                current_config_file_time =os.stat(config_file).st_mtime
                if self.config_time < current_config_file_time:
                    self.config_time = current_config_file_time
                    # found config.txt that has been changed
                    print("(%s) timestamp: %f" %(config_file,self.config_time))
                    # get values from config file
                    config = configparser.RawConfigParser()
                    config.read(config_file)
                    d = dict(config.items('slideshow'))
                    try:
                        self.delay_time = int(d.get('delay','15'))*1000 # to get real seconds
                        self.shuffle = d['shuffle'].lower() == 'true'
                        self.reload_filenames = d['reload'].lower() == 'true'
                        self.timeon = int(d.get('timeon','0700'))
                        self.timeoff = int(d.get('timeoff','2100'))
                        self.scaleup = d['scaleup'].lower() == 'true'
                        self.scaledown = d['scaledown'].lower() == 'True'
                        self.includedfolders = d.get('includedfolders','').replace('\n','').split()
                        self.excludedfolders = d.get('excludedfolders','').replace('\n','').split()
                        self.showfilenames = d['showfilenames'].lower() == 'true'
                    except:
                        pass
                    if self.reload_filenames == True:
                        # config said to reload files names, otherwise keep going with current files
                        self.image_filenames = False # going to reload filenames
                        self.reload_filenames = False

                    print("Config read: delay(%d), shuffle(%r), timeon(%d), timeoff(%d), scaleup(%r), scaledown(%r), showfilenames(%r), reload filenames(%r)"  
                      %(self.delay_time,self.shuffle,self.timeon,self.timeoff,self.scaleup, self.scaledown,self.showfilenames,self.reload_filenames)) 
        except:
                print("*** Error in config.txt")
                pass
        try:
            # see if SlideShow.py is there and if so, has it been updated
            program_file = os.path.join(self.path,__file__)
            if os.path.exists(program_file):
                print("Found: ",__file__)
                current_program_file_time=os.path.getmtime(program_file)

                if self.program_time < current_program_file_time: 
                    # found SlideShow.py  has been changed, restart it
                    print("\nRestarting ...\n------------")
                    self.program_time = current_program_file_time
                    os.execv(sys.executable,[__file__]+ sys.argv)
        except:
                print("*** Error restarting SlideShow.py")
                pass


    def doit(self):
    #------------------------------------------------------
        print("Start doit callback")
        self.check_for_program_changes()     # see if config.txt has changed
        self.read_image_filenames()    # determine if we have to read/re-read image filenames
        # check schedule to see if we show image or black screen only
        if not self.check_schedule():
            # show blank image on slide widget
            self.photo_widget.config(image='')
            self.photo_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
            self.filename_widget.config(text='')
            self.title('')
        else:
            self.get_next_image() # load up next image for display
            try: # okay, lets make sure self.image is valid, otherwise skip
                # show current image and/or file name 
                self.photo_widget.config(image=self.image)
                self.photo_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
                if self.showfilenames: 
                    self.filename_widget.pack() 
                    self.filename_widget.configure(text=self.image_name)
                else: 
                    self.filename_widget.pack_forget() # BUG here. won't turn back on
            except:
                print("*** Error adding loaded photo.")
                pass
        self.after_id = self.after(self.delay_time, self.doit) #recall main after a pause
    

    def start(self):
    #------------------------------------------------------
        # call this only once
        self.doit() # my code
        self.mainloop() # tkinter framework


#------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print ('Usage: python ScreenSaver.py  /somepath/config.txt')
    path = sys.argv[1]
    slideshow = Slideshow(path, DELAY_TIME, SHUFFLE)
    slideshow.start()
