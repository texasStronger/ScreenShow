
import os
import tkinter
import datetime
import random
import configparser
from itertools import cycle
import tkinter as tk
from PIL import Image, ImageTk
from PopupSettings import PopupSettings
import time

class Slideshow():
    '''
    Usage: python config.txt
    
    Info:
    SlideShow displays a slide show of photos (jpg, gif, png, jpeg).
    Start the program with a config.txt. All specified sub-folders will be searched. 
    The /path/ should have a config.txt file to change program operations. Otherwise hard coded
    defaults are used. Format of config.txt:
    
    [slideshow]
    #delay seconds from 1 to ...
    delay=30
    # reload this config file when it is changed: true or false
    reload=true
    # scale smaller photos up to screen: true or false
    scaleup=True
    # scale larger photos down to screen size: true or false
    scaledown=True: true or false
    # begin slide show at: format HH:MM
    time_begin=06:30
    # end slide show at: format HH:MM
    time_end=21:59
    # show filenames on the screen: true or false
    showfilenames=true
    # sort photos by full path name : none, ascending, descending or random
    sort=random
    # transition photos with a blend: true or false
    blend=true
    # blend speed: 0.0 to 1.0
    blend_speed=0.10
    # included photos from these folders and their subfolders
    includedfolders=  ./mmedia/pics
    # excluded photos from these folders and their subfolders
    excludedfolders= ./mmedia/pics/1996  ./mmedia/pics/1998
    
    Keys / mouse:
    Left click or 's' key: show the settings popup for changes to currently running SlideShow
    Right click or 'space bar' key: advance to next photo
    'p' key: pause the current photo
    'h' key: hide the screen
    'esc', 'q' keys: ends the program
    
    If config.txt or SlideShow.py are changed in the file system, the program will reload 
    and restart, respectively.
    
    Files needed: SlideShow.py PopupSettings.py config.txt
    Tested on windows 10 and raspberry pi buster, Python 3.9 with tkinter and Pillow
    
log:
    '''
    print(__doc__)
   
    def __init__(self, path):
    #------------------------------------------------------
    # initializes variables, UI, etc.
        #setup screen stuff
        self.root = tk.Tk()
        w = self.root.winfo_screenwidth() #get max screen resolution on device
        h =  self.root.winfo_screenheight()
        self.root.geometry("%dx%d+%d+%d" % (w,h,0,0)) #set tkinter widget to full screen
        self.root.configure(bg='black')
        self.root.attributes('-fullscreen', True)
        self.root.resizable(False, False)
        print("Screen width %d height %d "%(w,h))

        self.path = path # a folder of pictures and subfolders
        self.settings = { # settings, used to send to Popup dialog also
            # these are from config file
            'blend':False,
            'blend_speed': 0.10,
            'delay_time': 2,
            'hide_the_screen': False,
            'pause_the_photo': False,
            'reload_filenames':True,
            'scaleup': True,
            'scaledown': True,
            'screen_height': 600,
            'screen_width': 800,
            'show_filenames': True,
            'sort':'none',
            'time_begin': '0700',
            'time_end': '2300',
            # these are not from config file
            'app':self,
            'root':self.root,
            'exit': False,
            'save': False,
            'clicked':'none'
            }
        self.settings['screen_width']= w
        self.settings['screen_height']= h
        self.configfile_timestamp = 0 # default config.txt time stamp
        self.slideshowfile_timestamp = os.stat(__file__).st_mtime #time stamp of SlideShow.py
        self.photo_filenames = False # holds all of the filenames of images as a cycle
        self.number_of_photos_found = 0
        self.includedfolders = ['.'] #default
        self.excludedfolders = [] # remove these folders and files
        self.current_photo_name = 'none' # current name of current photo
        self.photo = None
        self.previous_photo = None
        self.after_slideshow_id = None # for tkinter callback loop
        self.after_blend_id = None # for tkinter callback loop
        self.blend_in_progress = 'no'
        self.alpha = 0.0
        self.alpha_increment = 0.1
        self.counter = 1
        
        # the photos will be added to a Label widget
        self.photo_widget= tkinter.Label(self.root,bg='black',borderwidth=0,padx=0, pady=0)
        self.photo_widget.bind_all('<Any-KeyPress>',self.keypressed)
        self.photo_widget.pack(side='top')
        self.filename_widget = tkinter.Label(self.root, font=('Arial', 18),fg='black',bg='white',padx=4,pady=4,relief=tk.RAISED)
        self.filename_widget.pack(side='bottom',fill=tk.X)
        self.photo_widget.pack()
        self.root.bind("<Button-1>", self.popup_settings)
        self.root.bind("<Button-3>", self.popup_settings)

        self.popup_results = {}# holds results from settings popup
        self.popup = None

    def popup_settings(self,event):
        if event.num == 3: # right button
            self.onNext()
            return
        #otherwise left button, show settings popup
        if self.popup == None:
            self.popup = PopupSettings(self.settings,event.x,event.y)
            self.root.wait_window(self.popup.top)
            self.popup = None
            '''
            if self.settings['hide_the_screen']:
                self.onHide()
            '''
            if self.settings['pause_the_photo']:
                self.onPause()
            elif self.settings['clicked'] == 'exit':
                self.onExit()
            elif self.settings['clicked'] == 'save':
                self.onSave()
            elif self.settings['clicked'] == 'return':
                self.onReturn()


    def keypressed(self,event):
        
        if event.keycode == 27 or event.char == 'q' or event.char == '\x1b': # ESC or q to exit/quit
            self.onExit()
        elif event.keysym =='p': # toggle pause screen
            self.settings['pause_the_photo'] = not self.settings['pause_the_photo']
            self.onPause()
        elif event.keysym.lower() =='s': # show settings
            self.popup_settings(event)
        elif event.keysym =='h': # hide screen
            self.settings['hide_the_screen'] = not self.settings['hide_the_screen']
            self.onHide()
        elif event.keysym =='space': 
            self.onNext()

    def onSave(self):
        # stop slideshow and restart in case new files have to be loaded
        self.root.after_cancel(self.after_slideshow_id) # stop slide show
        self.slideshow_loop()
        pass
    def onHide(self):
        # settings is True or False and mail slideshow loop will pick it up
        # program still runs, just won't display
        self.root.after_cancel(self.after_slideshow_id) # stop slide show
        self.slideshow_loop()
        pass
        
    def onReturn(self):
        # Popup just returned, nothing to do
        pass

    def onPause(self):
        # will keep current picture on the screen until a resume based on settings variable T/F
        if self.settings['pause_the_photo']: # on, so freeze pic
            self.root.after_cancel(self.after_slideshow_id) # stop slide show
            pass
        else: 
            self.slideshow_loop() # resume slide show

    def onExit(self):
        self.root.destroy() # destroy windows, done
        
    def onNext(self):
        self.root.after_cancel(self.after_slideshow_id) # stop slide show
        self.slideshow_loop() # restart immediately
        
         

    def get_next_image(self):
    #------------------------------------------------------
        # get the next image 
        try:
            self.current_photo_name =  next(self.photo_filenames)
            screenw = self.settings['screen_width']
            screenh = self.settings['screen_height']

            current_image = Image.open(self.current_photo_name) # load name as PIL Image
            current_image_width, current_image_height = current_image.size

            # use this if you want to scale up an down
            ratio_image = current_image_width / current_image_height
            ratio_screen = screenw / screenh  
            #determine how best to scale image to screen.  
            if ratio_screen > ratio_image:
                    scaled_width = int( current_image_width * screenh /current_image_height)
                    scaled_height = screenh
            else:
                    scaled_width = screenw
                    scaled_height = int(current_image_height * screenw / current_image_width)
            if self.settings['scaleup'] or self.settings['scaledown']: # only scale if config.txt indicates to do so
                self.scaled_image = current_image.resize((scaled_width,scaled_height))
            else:
                self.scaled_image = current_image
            (neww,newh) = self.scaled_image.size
            # create a black full screen image so that if we have an image smaller, we will paste it
            # into the black image. This will allow us to ensure all images are the same size when
            # showing and allow us to blend images if specificed in config.ASN1_CTXt
            self.black_image  = Image.new( mode = "RGBA", size = (self.settings['screen_width'],self.settings['screen_height']), color = (0,0,0) )
            if self.settings['blend']:
                offsetw = int(screenw/2 - neww/2)
                offseth = int(screenh/2 - newh/2)
                self.black_image.paste(self.scaled_image,(offsetw,offseth))
                self.scaled_image = self.black_image
            # convert PIL image to tkinter image
            self.previous_photo = self.photo
            self.photo = self.scaled_image
        except:
            print("*** Error with %s, skipping."%self.current_photo_name)
            pass

    def read_photo_filenames(self):
    #------------------------------------------------------
    # We have a list of included folders (and their subfolders) to include plus
    # a list of folders/subfolders to remove
        try:
            # either perform the 1st load or a new load (config.txt) of filenames
            if self.photo_filenames == False:
                included_filenames = self.read_folders(self.includedfolders)
                excluded_filenames = self.read_folders(self.excludedfolders)
                filenames = [f for f in included_filenames if f not in excluded_filenames]
                if self.sortfilenames == 'ascending': # determine order of filenames
                    filenames.sort()
                elif self.sortfilenames == 'descending':
                    filenames.sort(reverse=True)
                elif self.sortfilenames == 'random':
                    random.shuffle(filenames)
                self.number_of_photos_found = len(filenames)
                self.photo_filenames = cycle(filenames)
        except:
                raise ("*** Error reading photo folders.")

        if self.number_of_photos_found == 0:
            raise("*** No photos specified.")

    def read_folders(self,folders):
    #------------------------------------------------------
    # Return a list of all filenames in 'folders' and the subfolders that are an image type
        try:
            exts = ("jpg", "bmp", "png", "gif", "jpeg")
            filenames = []
            for current_folder in folders: # finds pics in a included folders and their sub-folders 
                for root, _, files in os.walk(current_folder):
                    for f in files:
                        if f.endswith(exts) and f not in filenames:
                            filenames.append(os.path.normpath(os.path.join(root, f))) # only add if not already added
            return filenames
        except:
                print("*** Error reading folders")

        
    def check_schedule(self):
    #------ This runs only between begin and end ousrs
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        hidden = self.settings['hide_the_screen']
        if current_time >= self.settings['time_begin'] and current_time <= self.settings['time_end'] and not hidden: 
            return True
        else:
            return False

    def check_for_program_timestamp_changes(self):
    #------------------------------------------------------
        try:
            config_file = self.path
            # see if config.txt is there and if so, has it been updated?
            if os.path.exists(config_file) and os.path.isfile(config_file):
                current_config_file_time =os.stat(config_file).st_mtime
                if self.configfile_timestamp < current_config_file_time:
                    self.configfile_timestamp = current_config_file_time
                    # found config.txt that has been changed, get new values
                    config = configparser.RawConfigParser()
                    config.read(config_file)
                    d = dict(config.items('slideshow'))
                    try:
                        self.settings['delay_time'] = int(d.get('delay','3')) # delay must be ms. so when used multiply by 1000
                        self.settings['reload_filenames'] = d['reload'].lower() == 'true'
                        self.settings['time_begin'] = d.get('time_begin','0700')
                        self.settings['time_end'] = d.get('time_end','2200')
                        self.settings['scaleup'] = d['scaleup'].lower() == 'true'
                        self.settings['scaledown'] = d['scaledown'].lower() == 'true'
                        self.settings['blend'] = d['blend'].lower() == 'true'
                        self.settings['blend_speed'] = float(d.get('blend_speed',0.10))
                        self.includedfolders = d.get('includedfolders','').replace('\n','').split()
                        self.excludedfolders = d.get('excludedfolders','').replace('\n','').split()
                        self.showfilenames = d['showfilenames'].lower() == 'true'
                        self.sortfilenames = d.get('sort','none').lower()
                    except:
                        pass
                    if self.settings['reload_filenames'] == True:
                        # config said to reload files names, otherwise keep going with current files
                        self.photo_filenames = False # going to reload filenames

                    print("config.txt read:\n",self.settings)  
        except:
                print("*** Error in config.txt")
                pass
        try:
            # see if SlideShow.py is there and if so, has it been updated
            program_file = os.path.join(self.path,__file__)
            if os.path.exists(program_file):
                current_program_file_time=os.path.getmtime(program_file)

                if self.slideshowfile_timestamp < current_program_file_time: 
                    # found SlideShow.py  has been changed, restart it
                    print("\nRestarting ...\n------------")
                    self.slideshowfile_timestamp = current_program_file_time
                    os.execv(sys.executable,[__file__]+ sys.argv)
        except:
                print("*** Error restarting SlideShow.py")
                pass


    def slideshow_loop(self):
    #---Run the slideshow. Basics steps: make sure the schedule is on and the screen is no hidden.
    #-- Then get the next image, display it along with its name.  Then recall this function
    #-- using 'after.'  This creates a multithreaded program in tkinter.
    #-- But wait, if we are blending two images, we will call blendLoop, which itself runs with an
    #--- after statement.  So this loop will still run, but will not do anything until blend is
    #--- finished. Blend can be running 'yes', not running 'no', or just finished.
    # When just finished, we need to make sure we delay again.
        self.check_for_program_timestamp_changes()     # see if config.txt has changed
        try:
            self.read_photo_filenames()    # determine if we have to read/re-read image filenames
        except:
            self.onExit() # no photos
            return
        
        if self.photo_filenames == []:
            print("No photos included.")
            return

        if self.blend_in_progress == 'yes': # don't do anything until finished
            time.sleep(1)
            self.after_slideshow_id = self.root.after(int(self.settings['delay_time']*1000), self.slideshow_loop) #recall main after a pause
            return
        elif self.blend_in_progress == 'finished':
            self.blend_in_progress = 'no'
            self.after_slideshow_id = self.root.after(int(self.settings['delay_time']*1000), self.slideshow_loop) #recall main after a pause
            return

        if not self.check_schedule() or self.settings['hide_the_screen']: # check schedule to see if we show image or black screen only
            # show blank image on slide widget
            self.photo_widget.config(image='')
            self.photo_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
            self.filename_widget.config(text='')
            time.sleep(1) # might as well sleep and not burn CPU
        else:
            self.get_next_image() # load up next image for display
            print('file: ',self.current_photo_name)
            try: 
                if self.previous_photo != None and self.settings['blend']: # show current image and/or file name 
                    self.blend_in_progress = 'yes' # do a blended transition
                    self.root.after_cancel(self.after_slideshow_id)
                    if self.settings['show_filenames']: 
                        self.filename_widget.pack(side='bottom',fill=tk.X)
                        self.filename_widget.configure(text=self.current_photo_name)
                    else: 
                        self.filename_widget.pack_forget() 
                    self.blendLoop()
                    return
                else:
                    # just display a single image
                    self.tmpimg=ImageTk.PhotoImage(self.photo)
                    self.photo_widget.config(image=self.tmpimg)
                    self.photo_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
                    if self.settings['show_filenames']: 
                        self.filename_widget.pack(side='bottom') 
                        self.filename_widget.configure(text=self.current_photo_name)
                    else: 
                        self.filename_widget.pack_forget() # BUG here. won't turn back on
            except:
                print("*** Error adding ",self.current_photo_name)
                pass
        self.after_slideshow_id = self.root.after(int(self.settings['delay_time']*1000), self.slideshow_loop) #recall main after a pause

    def blendLoop(self):
    #---------- Do alpha blend on two images, when finished, restart slideshowLoop ----------
        if self.previous_photo == None: 
            self.blend_in_progress = 'finished'
            self.slideshow_loop()
            return
        if 1.0 <= self.alpha:
            # for some reason, python is giving 1.0000000002 so we need
            # to end with an alpha 1.0 which displays self.photo
            self.blended= Image.blend(self.previous_photo,self.photo,1.0)
            self.alpha = 0.0
            self.display_photo = ImageTk.PhotoImage(self.blended)
            self.photo_widget.config(image=self.display_photo)
            self.photo_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
            self.blend_in_progress = 'finished'
            self.slideshow_loop()
            return
        self.blended= Image.blend(self.previous_photo,self.photo,self.alpha)
        self.display_photo = ImageTk.PhotoImage(self.blended)
        self.alpha = self.alpha + self.settings['blend_speed']
        self.photo_widget.config(image=self.display_photo)
        self.photo_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        self.after_blend_id = self.root.after(3, self.blendLoop)
    

    def start(self):
    #------------------------------------------------------
        self.slideshow_loop() # my code
        self.root.mainloop() # tkinter framework


#------------------------------------------------------
if __name__ == "__main__":
    import sys
    path = 'config.txt'
    if len(sys.argv) == 2:
        path = sys.argv[1]
    slideshow = Slideshow(path)
    slideshow.start()
