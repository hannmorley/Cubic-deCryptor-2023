#  Speech to text program

#  July 2, 2023  Added code to compute the default source and destination language index values
#                Also added comments to clarify some functions
#
# July 17, 2023  Added code to continuously update the text widget as translation is taking place
#                Added buttons to save the contents of the text widget in a file and to close out
#                the translator
#                Modified the code to force the text box to scroll down when it is full so that the 
#                last line is always visible


# the source and destination language variables are global variables

global s_lang, d_lang
s_lang = "th"
d_lang = "en"

# import necessary libraries

import os
import speech_recognition as sr
import tkinter as tk
import signal
import time
import multiprocessing
from multiprocessing import Process, Manager
from gtts import lang
from googletrans import Translator
from tkinter import ttk
from tkinter import *

def set_lang():
    global s_lang, d_lang
    s_lang = lang_format[example1.current()]
    d_lang = lang_format[example2.current()]
    var.set(1)
    user.destroy()

def speech_to_text(src_lang, ka, q_in):
    
    # This function uses the google recognizer to capture audio from the microphone
    # and converts it to text in the source language

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        ######
        os.system('printf "\033[H\033[2J"')
        print ("Listening...")
        ######
        while ka.value != 0:
            audio = r.listen(source, phrase_time_limit=4)  # Edit the phrase time limit to change the listening time
            try:
                text = r.recognize_google(audio, language=src_lang)
            except:
                text = "."
            q_in.put(text)
       
def translate_text(src_lang, dst_lang, ka, q_in, q_out):

# Translate the text from the source to the destination language

    translator = Translator()
    while ka.value > 0:
        text = q_in.get()
        tr_text = translator.translate(text, src=src_lang, dest=dst_lang)
        translation_text = tr_text.text + " "
        q_out.put(translation_text)
        
    
def display_text(ka, q_out):
    
# Creates a window with a text widget that has a scroll bar

    root = Tk()
    root.title('ALWAIS Live Translator')
    w = 800 # width for the Tk root window
    h = 650 # height for the Tk root window

    # get screen width and height

    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window

    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    # set the dimensions of the text box and where it is placed

    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    Label(root, text="Cubic DeCryptor", font=("Helvetica 20 bold"), fg="black", bg='#FFFF40').pack(pady=10)

        
    def stop_trans():
    
    # Command for stop_button
    # When the button is pressed, it kills the root window and sets the keep-alive value to zero.
    # That will kill all three child processes
    
        ka.value=0
        root.destroy()
    
    def save_trans():
        
    # Command for save_button
    # When the button is pressed, it checks for the existance of a file
    # If the file doesn't exist, it creates and then opens it
    # Then, it appends the contents of the text widget buffer to it
    # Finally, it deletes the contents of the buffer and closes the file
        
        tf = open('/home/pi/transfile.txt','a')
        text_string = mytext.get(1.0,END)
        tf.write(text_string)
        tf.close()
        mytext.delete("1.0", "end")
        
    # Added code to provide "tactile response" to button push
    
    def change_button1(event):
        while event.widget['text'] == 'Stop Translation':
            event.widget.configure(state="disabled")
            event.widget.configure(state="active")
            event.widget.configure(text="Stopped! DC to End")
            break
        
        while event.widget['text'] == 'Save Text':
            event.widget.configure(state="disabled")
            event.widget.configure(state="active")
            break
        
    # added code to provide intermediate step so that tactile response could be seen
    
    def change_button2(event):
        while event.widget['text'] == 'Stopped! DC to End':
            event.widget.configure(command=stop_trans)
            break
  
         
# Build the scrollbar and buttons for the root display

    scrollbar = Scrollbar(root)
    scrollbar.pack(side=RIGHT, fill=Y)

    stop_button = Button(root, text="Stop Translation", state="active", borderwidth=2, bg="lightblue", fg="black", font="blue", highlightbackground="white", highlightcolor="blue", highlightthickness=4, )
    stop_button.bind('<ButtonRelease-1>',change_button1)
    stop_button.bind("<Double-1>",change_button2)
    stop_button.pack(side=BOTTOM, fill=Y, pady=10)
    save_button = Button(root, text="Save Text", state="active", command=save_trans, borderwidth=2,bg="lightblue", fg="black", font="blue", highlightbackground="white", highlightcolor="blue", highlightthickness=4, ) 
    save_button.bind('<ButtonRelease-1>',change_button1)
    save_button.pack(side=BOTTOM, fill=Y, pady=10)
    mytext = Text(root, yscrollcommand=scrollbar.set)

# Display the results of the translation   
  
    def update_txt():
        dest_txt = q_out.get()
        mytext.insert(END, dest_txt)
        mytext.after(10, update_txt)
        mytext.yview_moveto(1)  # Causes text to scroll up when text box is full
        
    mytext = Text(root, yscrollcommand=scrollbar.set)
    mytext.config(state='normal')
    update_txt()
    mytext.pack(fill=BOTH)
    scrollbar.config(command=mytext.yview)

    # Run the loop for the root code
    root.mainloop()

if __name__ == "__main__":

    # Import the list of languages that googletrans supports for translation

    lang_dict = lang.tts_langs()
    lang_name = list(lang_dict.values())
    size = len(lang_dict)
    lang_format = list(lang_dict.keys())

    #  Create the language selection screen (user)

    user = Tk()

    #  These two variables support the drop down lists containing the supported source and destination languages

    variable1 = StringVar(user)
    variable2 = StringVar(user)

    #  Source language combo box

    comb1 = tk.Label(user, text = "Source language")
    comb1.grid(column = 2, row = 1)
    example1 = ttk.Combobox(user, values = (lang_name), textvariable=variable1)

    # compute default index value for the source language from lang_name 

    default_src = 'Hebrew'   #edit this string to change the default source language

    for i in range(len(lang_name)):         # search for a match in the list of supported languages
        if lang_name[i] == default_src:     # if a match is found, save the index to it
            src = i                         

    example1.current(src)
    example1.grid(column = 2, row = 2, padx = 10)

    # Variable used to pause the program until the result button is pushed

    var = tk.IntVar()

    #  Submit button
    #  Note that this button calls the set_lang command when it is pushed

    result = Button(user, text = "submit", command = set_lang)
    result.grid(column = 6, row = 2, padx = 10, pady = 3)

    # Destination language combo box

    comb2 = tk.Label(user, text = "Destination language")
    comb2.grid(column = 5, row = 1)
    example2 = ttk.Combobox(user, values = (lang_name), textvariable=variable2)

    # compute default index value for the destination language from lang_name 

    default_dst = 'English'   # Edit this string to change the default destination language

    for i in range(len(lang_name)):       # search for a match in the list of supported languages
        if lang_name[i] == default_dst:   # if a match is found, save the index to it
            dst = i

    example2.current(dst)
    example2.grid(column = 5, row = 2, padx = 10)

    # Here, we pause until the submit button is pushed

    result.wait_variable(var)
    manager = Manager()
    queue_in = manager.Queue()
    queue_out = manager.Queue()
    keep_alive = manager.Value('i', 1)
    
    # Subprocesses are defined here

    p1 = Process(target=speech_to_text, args=(s_lang, keep_alive, queue_in))
    p2 = Process(target=translate_text, args=(s_lang, d_lang, keep_alive, queue_in, queue_out))
    p3 = Process(target=display_text, args=(keep_alive, queue_out))

    # Subprocesses are started here

    p1.start()
    p2.start()
    p3.start()
        
    # Subprocesses are joined here
        
    p1.join()
    p2.join()
    p3.join()
