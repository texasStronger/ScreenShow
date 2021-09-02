# ScreenShow
Python Screen Show to display images with options

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
  timeoff - a number, indicates a time when a black screen will appear instead of images
  scaleup - True or False, indicates that small pictures will be increased to screen size (True)
  scaledown - True or False, indicates that large pictures will be decreased to screen size (True)
  showfilenames - True or False, bottom of the screen will show full file name
  reload - True of False, If the config file changed, indicates if filenames should be reloaded
  includedfolders = pathnames to where files are found including subfolders
  excludedfolders = pathnames to folders and their contents to ignore (no subfolders)

SlideShow will monitor config.txt. If the file changes, the new setting will be applied including possibly
re-reading all of the image file names. e.g. I have an older flat screen windows laptop that I am using now for a photo frame. I can sftp new files or drag them as a mounted drive. Then I place a config.txt file in the top folder.
To exit SlideShow, hit the Escape or q keys.
Perform the left button click to hide the screen and pause.
Perform right button click to advance to the next image immediately.
Hit spacebar to pause, and again to resume.

