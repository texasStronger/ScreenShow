import tkinter as tk
import datetime

class PopupSettings():
    # Display a popup tkinter window to allow user to change some of the settings.
    # Pause, Hide and Save will update config settings in use, not the file
    # Done just returns. and Exit will shut off screenshow
    # This dialog just stores results in self.settings which is shared with SlideShow
    def __init__(self,settings,x,y):
        self.top = tk.Toplevel(settings['root'])
        self.app= settings['app']
        #self.top.grab_set()
        self.settings = settings
        self.top.title('Slideshow Settings')
        f = ('Times', 20)
        self.reload_var = tk.BooleanVar(value=self.settings['reload_filenames']) 
        self.scaleup_var = tk.BooleanVar(value=self.settings['scaleup'])
        self.scaledown_var = tk.BooleanVar(value=self.settings['scaledown'])
        self.show_filenames_var = tk.BooleanVar(value=self.settings['show_filenames'])
        self.blend_var = tk.BooleanVar(value=self.settings['blend'])
        self.blend_speed_var = tk.DoubleVar(value=self.settings['blend_speed'])
        self.time_begin_var = tk.StringVar()
        self.time_end_var = tk.StringVar()
        self.delay_time_var =  tk.IntVar(value=self.settings['delay_time'])
        self.pause_the_photo_var = tk.BooleanVar(value=self.settings['pause_the_photo'])
        self.hide_the_screen_var = tk.BooleanVar(value=self.settings['hide_the_screen'])
        
        # show on / off check boxes
        tk.Checkbutton(self.top, text="Reload filenames", padx=20,pady=5,font=f,variable=self.reload_var).grid(row=0,column=0,sticky=tk.W,padx=10)
        tk.Checkbutton(self.top, text="Scale up",         padx=20,pady=5,font=f,variable=self.scaleup_var).grid(row=1,column=0,sticky=tk.W,padx=10)
        tk.Checkbutton(self.top, text="Scale down",       padx=20,pady=5,font=f,variable=self.scaledown_var).grid(row=2,column=0,sticky=tk.W,padx=10)
        tk.Checkbutton(self.top, text="Show filenames",  padx=20,pady=5,font=f,variable=self.show_filenames_var).grid(row=3,column=0,sticky=tk.W,padx=10)
        tk.Checkbutton(self.top, text="Blend images",    padx=20,pady=5,font=f,variable=self.blend_var).grid(row=4,column=0,sticky=tk.W,padx=10)

        # show time spinners
        # generate list of 15 minute increments
        spacing=15 # 15 min. apart
        # save this valid_times = [str(i*datetime.timedelta(minutes=spacing)).zfill(8) for i in range(24*60//spacing)]
        # make valid times of form HH:MM
        valid_times = [str(i).zfill(2)+':'+j for i in range(0,24,1) for j in ('00','15','30','45')]

        # start time
        fr = tk.Frame(self.top,padx=20,pady=5)
        fr.grid(row=5,column=0,sticky=tk.W,columnspan=3)
        # make sure begin and end times are of for HH:MM by adding 0 prefix
        tk.Label( fr, text="Begin time:", font=f).pack(side=tk.LEFT)
        tk.Spinbox( fr, font=f,values=valid_times,textvariable=self.time_begin_var, width=7,justify=tk.RIGHT).pack(side=tk.LEFT)
        self.time_begin_var.set(value=self.settings['time_begin'].zfill(5))

        # end time
        fr = tk.Frame(self.top,padx=20,pady=5)
        fr.grid(row=6,column=0,sticky=tk.W,columnspan=3)
        tk.Label( fr, text="End time:",   font=f,pady=5).pack(side=tk.LEFT)
        tk.Spinbox( fr, font=f, values=valid_times,textvariable=self.time_end_var, width=7 ,justify=tk.RIGHT).pack(side=tk.LEFT)
        self.time_end_var.set(value=self.settings['time_end'].zfill(5))

        # show delay time
        fr = tk.Frame(self.top,padx=20,pady=5)
        fr.grid(row=7,column=0,sticky=tk.W,columnspan=3)
        tk.Label( fr, text="Delay seconds:", font=f).pack(side=tk.LEFT)
        tk.Spinbox( fr, from_=1, to=180,  font=f,textvariable=self.delay_time_var, width=3,justify=tk.RIGHT ).pack(side=tk.LEFT)
        
        # show blend speed (for alpha blending)
        fr = tk.Frame(self.top,padx=20,pady=5)
        fr.grid(row=8,column=0,sticky=tk.W,columnspan=3)
        tk.Label( fr, text="Blend speed:", font=f).pack(side=tk.LEFT)
        tk.Spinbox( fr, from_=0.10, to=1.00, increment=0.10,  font=f,textvariable=self.blend_speed_var, width=5,justify=tk.RIGHT ).pack(side=tk.LEFT)

        # show sort options
        fr = tk.Frame(self.top,padx=20,pady=5)
        fr.grid(row=9,column=0,sticky=tk.W,columnspan=3)
        values = {"none":0, "ascending" : 1, "descending" : 2, "random" : 3}
        tk.Label( fr, text="Sort:", pady=5,padx=10,font=f).pack(side=tk.LEFT)
        self.listbox = tk.Listbox(fr,font=f,height=4,width=10,selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT)
        for (text, value) in values.items():
            self.listbox.insert(int(value),text)
        self.listbox.select_set(0)
        
        #show  pause, hide
        fr = tk.Frame(self.top,padx=20,pady=5)
        fr.grid(row=10,column=0,sticky=tk.W,columnspan=3)
        tk.Checkbutton(fr, text='Hide',  padx=20,pady=5,font=f,variable=self.hide_the_screen_var).pack(side='left')
        tk.Checkbutton(fr, text='Pause', padx=20,pady=5,font=f,variable=self.pause_the_photo_var).pack()
        
        #show  return, save, exit
        fr = tk.Frame(self.top,pady=5)
        fr.grid(row=11,column=0,columnspan=3,sticky=tk.W)
        but = tk.Button(fr, text ="Return",command =self.returnButtonCallback,bd=3,font=f,width=8)
        but.pack(side=tk.LEFT)
        but = tk.Button(fr, text ="Save",command =self.saveButtonCallback,bd=3,font=f,width=8)
        but.pack(side=tk.LEFT)
        but = tk.Button(fr, text ="Exit",command =self.exitButtonCallback,bd=3,font=f,width=8)
        but.pack(side=tk.LEFT)
        #self.top.geometry('+%d+%d'% ((self.settings['screen_width']/2)-500,(self.settings['screen_height']/2)-500))
        self.top.geometry('+%d+%d'% (x,y))

    def exitButtonCallback(self):
        self.saveSettings()
        self.settings['clicked']='exit'
        self.settings['exit'] = True
        self.top.destroy()
    def destroy(self):
        self.top.destroy()
        
    def returnButtonCallback(self):
        self.top.destroy()
        self.settings['clicked']='return'
        pass

    def saveButtonCallback(self):
        self.saveSettings()
        self.settings['save'] = True
        self.settings['clicked']='save'
        self.top.destroy()

    def saveSettings(self):
        self.settings['reload_filenames'] = self.reload_var.get() 
        self.settings['scaleup'] = self.scaleup_var.get()
        self.settings['scaledown'] = self.scaledown_var.get()
        self.settings['time_begin'] = self.time_begin_var.get()
        self.settings['time_end'] = self.time_end_var.get()
        self.settings['show_filenames'] = self.show_filenames_var.get()
        self.settings['blend'] = self.blend_var.get()
        self.settings['blend_speed'] = self.blend_speed_var.get()
        self.settings['delay_time'] = self.delay_time_var.get() 
        self.settings['pause_the_photo'] = self.pause_the_photo_var.get() 
        self.settings['hide_the_screen'] = self.hide_the_screen_var.get() 
        self.settings['sort'] = self.listbox.get(self.listbox.curselection())
        self.settings['save'] = True
        self.settings['clicked']='save'
        
class App():

    def __init__(self):
        self.root = tk.Tk()
        self.settings = { # settings, used to send to Popup dialog also
            'app':self,
            'background': "black",
            'blend': True,
            'blend_speed': 0.10,
            'clicked':'none',
            'delay_time': 3,
            'exit': False,
            'hide_the_screen': False,
            'pause_the_photo': False,
            'reload_filenames':True,
            'root':self.root,
            'save': False,
            'scaleup': True,
            'scaledown': True,
            'screen_width': 1920,
            'screen_height': 1080,
            'show_filenames': True,
            'sort':'none',
            'time_begin': '7:00',
            'time_end': '13:45'
            }
        self.popup_results=None
        f=('Times',20)
        mainButton = tk.Button(self.root, text='Click me', font=f,command=self.onClick)
        mainButton.pack()
        myExitButton= tk.Button(self.root, text='Exit', font=f,command=self.byebye)
        myExitButton.pack()
        self.root.geometry('300x300+300+200')
        self.root.mainloop()

    def byebye(self):
        print("Exit")
        self.root.destroy()


    def onClick(self):
        self.popup = PopupSettings(self.settings,500,500)
        self.root.wait_window(self.popup.top)
        print("Settings:\n",self.settings)

if __name__ == '__main__':

    a = App()
