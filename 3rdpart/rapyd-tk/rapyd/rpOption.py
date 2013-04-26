"""
Option editor related stuff for Rapyd-Tk, mostly option editor validation routines for all
    the various types and 'assist' routines for those types that need them. 
"""

#----------------------------------------------------------------------------------.
#                                                                                  |
#  Copyright (C) 2010  Cam Farnell                                                 |
#                                                                                  |
#  This program is free software; you can redistribute it and/or                   |
#  modify it under the terms of the GNU General Public License,                    |
#  version 2, as published by the Free Software Foundation.                        |
#                                                                                  |
#  This program is distributed in the hope that it will be useful,                 |
#  but WITHOUT ANY WARRANTY; without even the implied warranty of                  |
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   |
#  GNU General Public License for more details.                                    |
#                                                                                  |
#  You should have received a copy of the GNU General Public License               |
#  along with this program; if not, write to the Free Software                     |
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA. |
#                                                                                  |
#----------------------------------------------------------------------------------'

"""


Note: A "tuli" is a TUple or a LIst. I got tired of typing "tuple or list" all over the place.      


How to a add a new built-in option to Rapyd:

    o Write a Validate and an Assist function for the new type. These both HAVE to exist
      even if they are pro-forma and do nothing. See the existing routines below
      for examples, particularly Text which has pro-forma routines.
      
    o Add the name of the new type to dictionary BuiltinOptionTypes which is defined
      near the top of Class ConfigReader in rapyd.py. You will have to specify the
      edit codes for this new type; they are described in the code.
      
    The above assumes that the new type requires no special processing. If
        it does then you may have to fiddle with code where the option editor
        processes changed entry values (routine StatusCheck) and where it deals
        with assists (routine on_Assist).

"""

import os.path
import time
import rpHelp as Rph
import rpWidgets as Rpw
import time
import tkFont
from   Tkinter import *

# Somewhere around Python 2.5 Tkinter started return Tcl objects in places
#     where it previously returned strings. Thus we set "wantobjects" to
#     false to prevent things from breaking. 
import Tkinter
Tkinter.wantobjects = False

True = 1
False = 0

def D(*Stuff):
    """
    This simply prints the arguments. 
    
    The point of using this, rather than 'print', is that once were done debugging 
    we can easily search for and remove the 'D' statements.
    """
    for T in Stuff:
        print T,
        print

def CenterOnScreen(Widget,Width,Height):
    """
    Generate a geometry string to center a widget on the screen.
    """
    X = (Widget.winfo_screenwidth() - Width) / 2
    Y = (Widget.winfo_screenheight() - Height) / 2
    return '+%s+%s'%(X,Y)        

#-------------------------------------------------------------------------------
#
#    xy
#
#-------------------------------------------------------------------------------
    
def xy_Validate(Arg,OptionName):
    """
    Verify that we like an xy offset.
    
    The result is a tuple consisting of:
        o "[0]" 1 if we like the argument, or an error string if we don't.
        o "[1]" The argument after we finish messing with it.

    Although I'm not clear on what offset is FOR, it can apparently be:
        o x,y
        o #x,y
        o an anchor specification        
    """
    Arg = Arg.strip()
    if Arg == '':
        #Empty is allowed
        return (1,Arg)
    try:
        Canvas(offset=Arg)
    except:
        return ('"%s" is not a valid offset.'%Arg,Arg)        
    return (1,Arg)            

class xy_Assist:
    """
    A placeholder xy edit assist.
    
    ValueToEdit is the initial value to show the user. It is taken, unchecked, from
        the Entry widget. 
        
    If the user choose CANCEL we return None.
    
    If the result is not None then the user has entered a valid value and pressed OK and
        the result is that valid value. For xy valid values are either an empty string
        or a 2-tuple of integers.
    """
    def  __init__(self,ValueToEdit,OptionName):
        #This is our default result in case we close unexpectedly
        self.Result = None
        self.ValueToEdit = ValueToEdit = str(ValueToEdit)
        self.OptionName = OptionName
        #create the window
        Width = 300
        Height = 200
        self._Win = Toplevel()
        self._Win.title(Rph.Cap(OptionName))
        #We want to position ourself near the mouse        
        MouseX, MouseY = self._Win.winfo_pointerxy()
        
        Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
        if Geo[3]+Height+70 > self._Win.winfo_screenheight():
            #don't run us off the bottom of the screen
            Geo[3] = max(self._Win.winfo_screenheight()-Height-70,0)
        self._Win.geometry(Rph.GeometryEncode(Geo))
        #message label
        Msg = 'This is a bare-bones placeholder for the "offset" edit assist dialog. ' \
            'The plan is to provide more reasonably functionality in due course.'
        self.LabelStringVar = StringVar()
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar)
        self.OurLabel.pack(anchor='w',pady=10,expand=YES,fill=BOTH)
        self.LabelStringVar.set(Rph.TextBreak(Msg,40))
        #Entry area
        self.Entry = Entry(self._Win)
        self.Entry.insert(0,ValueToEdit)
        self.Entry.pack(expand=YES)
        self.Entry.bind('<Return>',self.on_OK)
        #button bar across the bottom
        self.BB = Rph.ButtonBox(self._Win)
        self.BB.pack(side='bottom')
        self.BB.add('OK',command=self.on_OK)
        self.BB.add('Cancel',command=self.on_Cancel)
        #be modal
        self.Entry.focus_set()
        Rph.Grabber(self._Win)
        self._Win.wait_window()
            
    def on_OK(self,Event=None):
        NewValue = self.Entry.get()
        Temp = xy_Validate(NewValue,self.OptionName)
        if Temp[0] <> 1:
            Rpw.ErrorDialog(Temp[0])
            return
        self.Result = str(Temp[1])
        self._Win.destroy()    

    def on_Cancel(self):
        self._Win.destroy()    

#-------------------------------------------------------------------------------
#
#   verbatim
#
#-------------------------------------------------------------------------------

def verbatim_Validate(Arg,OptionName):
    """
    Verify that we like a verbatim field.
    
    Since there isn't much to not-like about verbatim fields the result is always
        a tuple consisting of:
        o "[0]" 1 signaling that we like the argument.
        o "[1]" The argument,
    """
    return (1,Arg)

class verbatim_Assist:
    """
    There is no assist for this type of option. 
    """

    def  __init__(self,ValueToEdit,OptionName):
        raise Exception, "Unexpected use of dummy assist"

#-------------------------------------------------------------------------------
#
#   text
#
#-------------------------------------------------------------------------------

def text_Validate(Arg,OptionName):
    """
    Verify that we like a text field.
    
    Since there isn't much to not-like about text fields the result is always
        a tuple consisting of:
        o "[0]" 1 signaling that we like the argument.
        o "[1]" The argument,

    Note: This routine exists mostly so we don't have to special-case options
        of type text elsewhere.
    """
    return (1,Arg)

class text_Assist:
    """
    There is no assist for this type of option. 
    
    This dummy assist exists only so we can create a list of validation and 
        assist routines in the main program without having to special case this type.
    """

    def  __init__(self,ValueToEdit,OptionName):
        raise Exception, "Unexpected use of dummy assist"

#-------------------------------------------------------------------------------
#
#    tabs
#
#-------------------------------------------------------------------------------
    
def tabs_Validate(Arg,OptionName):
    """
    Verify that we like a tab specification.
    
    The result is a tuple consisting of:
        o "[0]" 1 if we like the argument, or an error string if we don't.
        o "[1]"  The argument after we finish messing with it.

    Tabs is a string of screen dimensions or "left/right/center/numeric".
    """
    Arg = Arg.strip()
    if Arg == '':
        #Empty is allowed
        return (1,Arg)
    for Temp in Arg.split():
        #scan each sub-argument so we can report on exactly which one we don't like
        R = dim_Validate(Temp,OptionName)
        if R[0] == 1:
            #it's a valid screen dimension
            continue
        #it's not a screen dimension
        if Temp in ('left','right','center','numeric'): 
            #its a valid keyword
            continue
        return ('"%s" is neither a valid screen dimension nor a valid alignment keyword.'%Temp,Arg)
    #so far we like it; Text is the ultimate authority
    try:
        Text(tabs=Arg)
    except:
        return ('"%s" is not valid.'%Temp,Arg)
    #Huzza - everybody is happy
    return (1,Arg)    
        

class tabs_Assist:
    """
    A placeholder tabs edit assist.
    
    ValueToEdit is the initial value to show the user. It is taken, unchecked, from
        the Entry widget. 
        
    If the user choosed CANCEL we return None.
    
    If the result is not None then the user has entered a valid value and pressed OK and
        the result is that valid value.
    """
    def  __init__(self,ValueToEdit,OptionName):
        #This is our default result in case we close unexpectedly
        self.Result = None
        self.ValueToEdit = ValueToEdit = str(ValueToEdit)
        self.OptionName = OptionName
        #create the window
        Width = 300
        Height = 200
        self._Win = Toplevel()
        self._Win.title(Rph.Cap(OptionName))
        #We want to position ourself near the mouse        
        MouseX, MouseY = self._Win.winfo_pointerxy()
        
        Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
        if Geo[3]+Height+70 > self._Win.winfo_screenheight():
            #nuy don't run us off the bottom of the screen
            Geo[3] = max(self._Win.winfo_screenheight()-Height-70,0)
        self._Win.geometry(Rph.GeometryEncode(Geo))
        #message label
        Msg = 'This is a bare-bones placeholder for the "tabs" edit assist dialog. ' \
            'The plan is to provide more reasonably functionality in due course.'
        self.LabelStringVar = StringVar()
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar)
        self.OurLabel.pack(anchor='w',pady=10,expand=YES,fill=BOTH)
        self.LabelStringVar.set(Rph.TextBreak(Msg,40))
        #Entry area
        self.Entry = Entry(self._Win)
        self.Entry.insert(0,ValueToEdit)
        self.Entry.pack(expand=YES)
        self.Entry.bind('<Return>',self.on_OK)
        #button bar across the bottom
        self.BB = Rph.ButtonBox(self._Win)
        self.BB.pack(side='bottom')
        self.BB.add('OK',command=self.on_OK)
        self.BB.add('Cancel',command=self.on_Cancel)
        #be modal
        self.Entry.focus_set()
        Rph.Grabber(self._Win)
        self._Win.wait_window()
            
    def on_OK(self,Event=None):
        NewValue = self.Entry.get()
        Temp = tabs_Validate(NewValue,self.OptionName)
        if Temp[0] <> 1:
            Rpw.ErrorDialog(Temp[0])
            return
        self.Result = str(Temp[1])
        self._Win.destroy()    

    def on_Cancel(self):
        self._Win.destroy()    

#-------------------------------------------------------------------------------
#
#   pyclass
#
#-------------------------------------------------------------------------------

def pyclass_Validate(Arg,OptionName):
    """
    Verify that we like a pyclass field.
    
    Since there isn't much to not-like about text fields the result is always
        a tuple consisting of:
        o "[0]" 1 signaling that we like the argument.
        o "[1]" The argument,

    Note: This routine exists mostly so we don't have to special-case options
        of type text elsewhere.
    """
    return (1,Arg)

class pyclass_Assist:
    """
    There is no assist for this type of option. 
    
    This dummy assist exists
        only so we can create a list of validation and assist routines
        in the main program without having to special case this type.
    """

    def  __init__(self,ValueToEdit,OptionName):
        raise Exception, "Unexpected use of dummy assist"

#-------------------------------------------------------------------------------
#
#   pmwdatatyp;e
#
#-------------------------------------------------------------------------------


def pmwdatatype_Validate(Arg,OptionName):
    """
    Verify that we like a pmwdatatype.
    
    The result is a tuple consisting of:
        o "[0]" 1 "f we like the argument, or an error string if we don't.
        o "[1]" The argument,
        
    This routine exists, pro forma so to speak, in case in the future we decide
        we do want to put some checks on pmwdatatype.    
    """
    return (1,Arg)                   

class pmwdatatype_Assist:
    """
    A Pmw datatype assist.
    
    "ValueToEdit" should be on of 'integer', 'real', 'time', 'date' or 'dictionary'.
        It it is anything else we arbitrarily set it to 'integer'.
        
    For those cases where it matters the first character of ExtraInfo is the separator
        character while the remaining 3 are the date format characters.    
        
    If the user chooses *CANCEL* we return "None".

    If the user chooses OK then we return a two element list:
        o "[0]" The setting chosen
        o "[1]" A four-character string giving the separator and date format characters.
                In cases where these are not used they are set to space.
    """
    def  __init__(self, ValueToEdit, OptionName, ExtraInfo):
        """
        Create the assist.
        """
        #This is our default result in case we close unexpectedly
        self.Result = None
        self.ValueToEdit = ValueToEdit
        self.ExtraInfo = ExtraInfo
        self.OptionName = OptionName
        #create the window
        Width = 500
        Height = 400
        self._Win = Toplevel()
        self._Win.title(Rph.Cap(OptionName))

        #The format of cvar ExtraInfo is described with cvar_Format
        #We want to position ourself near the mouse        
        MouseX, MouseY = self._Win.winfo_pointerxy()
        
        Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
        if Geo[3]+Height+70 > self._Win.winfo_screenheight():
            #but don't run us off the bottom of the screen
            Geo[3] = max(self._Win.winfo_screenheight()-Height-70,0)
        self._Win.geometry('+100+100')

        #just for space
        Label(self._Win).pack(side=TOP)
                
        #message label
        Msg = 'Datatype:'
        self.LabelStringVar = StringVar()
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar,anchor=SW)
        self.OurLabel.pack(anchor='w',expand=YES,fill=BOTH,padx=20)
        self.LabelStringVar.set(Rph.TextBreak(Msg,40))

        #Setup variables to remember possible extra data
        self.RealSep = '.'
        self.TimeSep = ':'
        self.DateSep = '/'
        self.DateFmt = 'ymd'
        self.DictName = ''
        if self.ValueToEdit == 'integer':
            pass
        if self.ValueToEdit == 'real':
            self.RealSep = self.ExtraInfo[0]
        elif self.ValueToEdit == 'time':
            self.TimeSep = self.ExtraInfo[0]
        elif self.ValueToEdit == 'date':
            self.DateSep = self.ExtraInfo[0]
            self.DateFmt = self.ExtraInfo[1:4]
        elif self.ValueToEdit == 'dictionary':
            self.DictName = self.ExtraInfo
        else:
            #Invalid initial value
            self.ValueToEdit = 'integer'
            self.ExtraInfo = '    '    
        self.PreviousType = None
        
        #Auto/Manual radio select
        self.TypeRadio = Rpw.RadioSelect(self._Win,buttontype='radiobutton',command=self.on_TypeRadio
            ,orient=VERTICAL)
        self.TypeRadio.add('Integer',text='Integer (default)')
        self.TypeRadio.add('Real')
        self.TypeRadio.add('Date')
        self.TypeRadio.add('Time')
        self.TypeRadio.add('Dictionary')
        self.TypeRadio.pack(expand=YES,side=TOP,pady=10,anchor=W,padx=10)
        
        #Y space
        Label(self._Win).pack(side=TOP)
        
        #Label over the separator / dictionary entry
        self.EntryLabel = Label(self._Win)
        self.EntryLabel.pack(side=TOP,anchor=W,padx=20)
        
        #Entry area for separator / dictionary
        self.Entry = Entry(self._Win)
        self.Entry.pack(expand=YES,fill=X,padx=20)

        #Y space
        Label(self._Win).pack(side=TOP)
        
        #Label over the date format entry
        self.EntryLabel2 = Label(self._Win)
        self.EntryLabel2.pack(side=TOP,anchor=W,padx=20)
        
        #Entry area for date format
        self.Entry2 = Entry(self._Win)
        self.Entry2.pack(expand=YES,fill=X,padx=20)

        self.SetState()
        
        #button bar across the bottom
        self.BB = Rph.ButtonBox(self._Win)
        self.BB.pack(side='bottom')
        self.BB.add('OK',command=self.on_OK)
        self.BB.add('Help',command=self.on_Help)
        self.BB.add('Cancel',command=self.on_Cancel)

        self.TypeRadio.invoke(ValueToEdit.title())

        #be modal
        Rph.Grabber(self._Win)
        self._Win.wait_window()

    def on_Help(self):
        Help('Assist.pmwdatatype')

    def SetState(self,Event=None):
        #
        """
        Set the state of the AutoMan and Selection items as appropriate.
        """
        NewType = self.TypeRadio.getcurselection()
        if NewType == None:
            #Can happen at startup
            return
        NewType = NewType.lower()    
        if NewType <> self.PreviousType:
            if self.PreviousType == 'real':
                self.RealSep = self.Entry.get()
            elif self.PreviousType == 'time':
                self.TimeSep = self.Entry.get()
            elif self.PreviousType == 'date':
                self.DateSep = self.Entry.get()
                self.DateFmt = self.Entry2.get()
            elif self.PreviousType == 'dictionary':
                self.DictName = self.Entry.get()            
        #Assume label/entry not needed
        Caption = ''
        Caption2 = ''
        State = DISABLED
        State2 = DISABLED
        if NewType == 'real':
            Caption = 'Decimal separator'
            State = NORMAL
        elif NewType == 'date':
            Caption = 'Date separator'
            Caption2 = 'Date format'
            State = NORMAL
            State2 = NORMAL
        elif NewType == 'time':
            Caption = 'Time separator'
            State = NORMAL
        elif NewType == 'dictionary':
            Caption = 'Dictionary'
            State = NORMAL
        self.Entry.config(state=NORMAL)
        self.Entry2.config(state=NORMAL)
        self.Entry.delete(0,END)
        self.Entry2.delete(0,END)
        if State == DISABLED:
            self.Entry.config(relief=FLAT)
        else:
            self.Entry.config(relief=SUNKEN)    
    
        if State2 == DISABLED:    
            self.Entry2.config(relief=FLAT)
        else:
            self.Entry2.config(relief=SUNKEN)    
            
        self.EntryLabel.config(text=Caption,state=State)
        self.EntryLabel2.config(text=Caption2,state=State2)
        self.Entry.config(state=State)
        if NewType == 'real':
            self.Entry.insert(0,self.RealSep)
        elif NewType == 'time':
            self.Entry.insert(0,self.TimeSep)
        elif NewType == 'date':
            self.Entry.insert(0,self.DateSep)
            self.Entry2.insert(0,self.DateFmt)
        elif NewType == 'dictionary':
            self.Entry.insert(0,self.DictName)
        self.PreviousType = NewType
        self.TypeRadio.focus_set()

    def on_TypeRadio(self,Event=None):
        #
        """
        Called when the user makes a selection in the Type radio select
        """
        self.SetState()

    def on_OK(self,Entry=None):
        Type = self.TypeRadio.getcurselection().lower()
        Sep = self.Entry.get().strip()
        Fmt = self.Entry2.get().lower()
        if Type in ('real','time','date') and len(Sep) <> 1:
            Msg = ('For type "%s" the seperator must be exactly one character but it is currently'
                ' set to "%s".'%(Type,Sep))
            Rpw.ErrorDialog(Message=Msg)
            return
        if Type == 'integer':
            Extra = '    '
        elif Type in ('real','time'):
            Extra = Sep+'   '
        elif Type == 'date':
            if len(Fmt) <> 3:
                Msg = ('For type "date" the format string must be exactly three characters but it'
                    ' is currently set to "%s".'%Fmt)    
                Rpw.ErrorDialog(Message=Msg)
                return
            for T in 'ymd':
                if not T in Fmt:
                    Msg = ('For type "date" the format string must contains the letters "y", "m" and "d"'
                        ' in any order but it presently is set to "%s".'%Fmt)        
                    Rpw.ErrorDialog(Message=Msg)
                    return
            Extra = Sep+Fmt
        elif Type == 'dictionary':
            if len(Sep) == 0:
                Msg = ('For type "dictionary" you need to supply either the name of a dictionary or an'            
                    ' actual dictionary but presently it is blank.')
                Rpw.ErrorDialog(Message=Msg)
                return
            if not Rpw.NameVet(Sep) and (Sep[0] <> '{' or Sep[-1] <> '}'):
                #Not a python name and not in brackets
                if Rpw.ErrorDialog(Message='Invalid dictionary specification',Help=1).Result:
                    Help('DatatypeAssist.BadDict')
                return    
            Extra = Sep
        else:
            raise Exception, 'UnknownType'        
        self.Result = [Type,Extra]
        self._Win.destroy()    

    def on_Cancel(self):
        self._Win.destroy()    

#-------------------------------------------------------------------------------
#
#   pmwcomp
#
#-------------------------------------------------------------------------------

def pmwcomp_Validate(Arg,OptionName):
    """
    Verify that we like a pmwcomp field.
    
    Since there isn't much to not-like about text fields the result is always
        a tuple consisting of:
        o "[0]" 1 signaling that we like the argument.
        o "[1]" The argument,

    Note: This routine exists mostly so we don't have to special-case options
        of type text elsewhere.
    """
    return (1,Arg)

class pmwcomp_Assist:
    """
    There is no assist for this type of option. 
    
    This dummy assist exists only so we can create a list of validation and assist 
        routines in the main program without having to special case this type.
    """

    def  __init__(self,ValueToEdit,OptionName):
        raise Exception, "Unexpected use of dummy assist"


#-------------------------------------------------------------------------------
#
#   int
#
#-------------------------------------------------------------------------------

def int_Validate(Arg,OptionName):
    """
    Verify that we like an int.
    
    The result is a tuple consisting of:
        o "[0]" 1 if we like the argument, or an error string if we don't.
        o "[1]" The argument,

    Note: Since ints are just simple numbers we provide a validation routine
        but no assist.        
    """
    Arg = str(Arg).strip()
    if len(Arg) == 0:
        return ('Option "%s" can not be blank.'%OptionName,Arg)
    try:
        int(Arg)
        return (1,Arg)
    except:    
        return('"%s" is not a valid integer.'%Arg,Arg)

class int_Assist:
    """
    There is no assist for this type of option. 
    
    This dummy assist exists only so we can create a list of validation and assist 
        routines in the main program without having to special case this type.
    """

    def  __init__(self,ValueToEdit,OptionName):
        raise Exception, "Unexpected use of dummy assist"


#-------------------------------------------------------------------------------
#
#   image
#
#-------------------------------------------------------------------------------

def image_Validate(Arg,OptionName):
    """
    Verify that we like an image name
    
    The result is a tuple consisting of:
        o "[0]" 1 if we like the argument, or an error string if we don't.
        o "[1]" The argument,
        
    I'm not sure there is anything we can check for here. The user is specifying
        the name of an image, which could be pretty much anything.
        
    This routine exists, pro forma so to speak, in case in the future we decide
        we do want to put some checks on image names.    
    """
    return(1,Arg)

class image_Assist:
    """
    A placeholder procedure image name edit assist.
    
    ValueToEdit is the initial value to show the user. It is taken, unchecked, from
        the Entry widget. 
        
    If the user chooses CANCEL we return None.
    
    If the result is not None then the user has entered a valid value and pressed OK and
        the result is that valid value. Right now, pretty much anything is valid.
    """
    def  __init__(self,ValueToEdit,OptionName):
        #This is our default result in case we close unexpectedly
        self.Result = None
        self.ValueToEdit = ValueToEdit = str(ValueToEdit)
        self.OptionName = OptionName
        #create the window
        Width = 300
        Height = 200
        self._Win = Toplevel()
        self._Win.title(Rph.Cap(OptionName))
        #We want to position ourself near the mouse        
        MouseX, MouseY = self._Win.winfo_pointerxy()
        
        Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
        if Geo[3]+Height+70 > self._Win.winfo_screenheight():
            #but don't run us off the bottom of the screen
            Geo[3] = max(self._Win.winfo_screenheight()-Height-70,0)
        self._Win.geometry(Rph.GeometryEncode(Geo))
        #message label
        Msg = 'This is a bare-bones placeholder for the "image" edit assist dialog. ' \
            'The plan is to provide more reasonably functionality in due course.'
        self.LabelStringVar = StringVar()
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar)
        self.OurLabel.pack(anchor='w',pady=10,expand=YES,fill=BOTH)
        self.LabelStringVar.set(Rph.TextBreak(Msg,40))
        #Entry area
        self.Entry = Entry(self._Win)
        self.Entry.insert(0,ValueToEdit)
        self.Entry.pack(expand=YES,fill=X,padx=20)
        self.Entry.bind('<Return>',self.on_OK)
        #button bar across the bottom
        self.BB = Rph.ButtonBox(self._Win)
        self.BB.pack(side='bottom')
        self.BB.add('OK',command=self.on_OK)
        self.BB.add('Cancel',command=self.on_Cancel)
        self.BB.add('Help',command=self.on_Help)
        #be modal
        self.Entry.focus_set()
        Rph.Grabber(self._Win)
        self._Win.wait_window()

    def on_OK(self,Event=None):
        NewValue = self.Entry.get()
        Temp = image_Validate(NewValue,self.OptionName)
        if Temp[0] <> 1:
            Rpw.ErrorDialog(Temp[0])
            return
        self.Result = str(Temp[1])
        self._Win.destroy()    

    def on_Cancel(self):
        self._Win.destroy()    

    def on_Help(self):
        Help('Assist.image')


#-------------------------------------------------------------------------------
#
#    font
#
#-------------------------------------------------------------------------------

def font_Validate(Arg,OptionName):
    """
    Verify that we like a font specification.
    
    The specification will be either a tuli of (Family, Size, Modifiers) or an
        X style font string.
    
    The result is a tuple consisting of:
        o "[0]" 1 if we like the argument, or an error string if we don't.
        o "[1]" The argument.
        
    If we like the argument then "result[1]" will be the font selection
        string or empty.
        
    Note that when supplying a font for a widget a font of None is acceptable
        (presumably indicating a default font) but "''" is not acceptable.    
    """
    
    if Arg <> None:
        if type(Arg) <> type(''):
            Arg = tuple(Arg)
        try:
            Button(font=Arg)
        except:
            return ('"%s" is not an acceptable font descriptor.'%str(Arg),Arg)
    return (1,Arg)                   

#----------------------------------------------------------------------------------------#
#                                                                                        #
#                                      font_Assist                                       #
#                                                                                        #
#----------------------------------------------------------------------------------------#
class font_Assist(Toplevel):
    def __init__(self,Master=None,**kw):
        kw['width'] = 300
        #
        #Your code here
        #
        # "ValueToEdit" is a 3-tuple giving (Family,Size,Options) or ''.
        if kw.has_key('ValueToEdit'):
            self.Font = kw['ValueToEdit']
            del kw['ValueToEdit']
        else:
            self.Font = None
        if kw.has_key('OptionName'):
            self.OptionName = kw['OptionName']
            del kw['OptionName']
        else:
            self.OptionName = ''
        self.Initializing = 1    
        if self.Font == '':
            self.Font = None

        apply(Toplevel.__init__,(self,Master),kw)
        self.geometry(CenterOnScreen(self,350,300))
        self.Frame2 = Frame(self,relief='ridge')
        self.Frame2.pack(expand='yes',fill='both',side='top')
        self.DefaultSetting = IntVar()
        self.DefaultButton = Checkbutton(self.Frame2,command=self.on_DefaultButton_command
            ,text='Use default font',variable=self.DefaultSetting)
        self.DefaultButton.pack(anchor='w',padx=5,pady=5,side='top')
        self.Frame1 = Frame(self)
        self.Frame1.pack(expand='yes',fill='both',side='top')
        self.Frame6 = Frame(self)
        self.Frame6.pack(expand='yes',fill='both',side='top')
        self.Text1 = Text(self.Frame6,height=5,width=50)
        self.Text1.pack(expand='yes',fill='both',side='bottom')
        self.Frame3 = Frame(self)
        self.Frame3.pack(expand='yes',fill='both',side='top')
        self.ButtonOk = Button(self.Frame3,text='Ok')
        self.ButtonOk.pack(expand='yes',side='left')
        self.ButtonOk.bind('<ButtonRelease-1>',self.on_ButtonOk_ButRel_1)
        self.ButtonHelp = Button(self.Frame3,command=self.on_ButtonHelp_command
            ,text='Help')
        self.ButtonHelp.pack(side='left')
        self.ButtonCancel = Button(self.Frame3,text='Cancel')
        self.ButtonCancel.pack(expand='yes',side='right')
        self.ButtonCancel.bind('<ButtonRelease-1>',self.on_ButtonCancel_ButRel_1)
        self.Frame7 = Frame(self.Frame1,borderwidth=2,relief='ridge')
        self.Frame7.pack(expand='yes',fill='both',side='left')
        self.FamiliesListBox = Rph.ScrolledListbox(self.Frame7,label='Font Family',width=35)
        self.FamiliesListBox.pack(expand='yes',fill='both',side='bottom')
        self.FamiliesListBox.FetchWidget().bind('<ButtonRelease-1>',self.on_UpdateNow)
        self.Frame4 = Frame(self.Frame1,borderwidth=2,relief='ridge')
        self.Frame4.pack(expand='yes',fill='both',side='left')
        self.Label2 = Label(self.Frame4,text='Font size')
        self.Label2.pack(side=TOP)
        self.Counter1 = Rpw.Counter(self.Frame4,entrywidth=5,modifiedcommand=self.on_UpdateNow)
        self.Counter1.pack(anchor='w',side='top')
        self.RadioSizeStyle = Rpw.RadioSelect(self.Frame4,buttontype='radiobutton'
            ,command=self.on_UpdateNow,orient='vertical',pady=0)
        self.RadioSizeStyle.pack(anchor='w',ipadx=5,side='top')
        self.Label1 = Label(self.Frame4)
        self.Label1.pack(side='top')
        self.RadioFontAttributes = Rpw.RadioSelect(self.Frame4,buttontype='checkbutton'
            ,command=self.on_UpdateNow,orient='vertical',pady=0)
        self.RadioFontAttributes.pack(anchor='w',ipadx=5,side='top')
        #
        #Your code here
        #

        self.title('%s'%self.OptionName)
        
        self.RadioFontAttributes.add('Bold')
        self.RadioFontAttributes.add('Italic')
        self.RadioFontAttributes.add('Underline')                
        self.RadioFontAttributes.add('Overstrike')

        self.RadioSizeStyle.add('Points')
        self.RadioSizeStyle.add('Pixels')
        
        #Set default checkbutton if font is None
        self.DefaultSetting.set(self.Font == None)

        self.Initialize()       

        #Be modal
        Rph.Grabber(self)
        self.wait_window()
    #
    #Start of event handler methods
    #


    def on_ButtonCancel_ButRel_1(self,Event=None):
        """
        User clicked CANCEL button
        """
        self.Result = None
        self.destroy()        

    def on_ButtonHelp_command(self,Event=None):
        """
        User clicked on HELP button
        """
        Help('assist-font')

    def on_ButtonOk_ButRel_1(self,Event=None):
        """
        User clicked OK button
        """
        self.Result = self.Font
        if self.Result == None:
            self.Result = ''
        self.destroy()

    def on_DefaultButton_command(self,Event=None):
        """
        The state of the "Use default font" button just changed
        """
        self.Initialize()

    def on_UpdateNow(self,Event=None,Extra=None):
        """
        Read font into and update the sample text.
        """
        if self.Initializing:
            #This prevents unnecessary activity as the various components are
            #initialized.
            return
        if self.DefaultSetting.get() == 1:
            #We are to use the default font
            self.Font = None
            return
        #Were not using the default font
        Temp = self.FamiliesListBox.getcurselection()
        if len(Temp) == 0:
            #No font is selected; nothing to do. This can happen if the user
            #works on another window then comes back to this dialog.
            return
        FontName = Temp[0].strip()
        FontSize = self.Counter1.Get()
        if self.RadioSizeStyle.getcurselection() == 'Pixels':
            FontSize = 0 - FontSize
        self.update_idletasks()
        Temp = self.RadioFontAttributes.getcurselection()
        FontModifiers = ' '.join(Temp).lower()
        self.Font = (FontName,FontSize,FontModifiers)
        self.Text1.tag_config('demotext',font=self.Font)
        
    #
    #Start of non-Rapyd user code
    #
    def Initialize(self):
        """
        Initialize things depending on default font checkbutton.
        """
        self.Initializing = 1
        if self.DefaultSetting.get() == 0:
            #We are not using the default font.
            self.EnableWidgets(True)
            #If the font specification is omitted or invalid then pick an arbitrary font.
            Families = list(tkFont.families(self))
            Families.sort()
            if self.Font == None \
            or not type(self.Font) in (type(()), type([])) \
            or len(self.Font) <> 3: 
                self.Font = (Families[0], 12, '')
            #Populate the listbox with names of available fonts
            self.FamiliesListBox.setlist([' '+X for X in Families])            
            self.Font = list(self.Font)
            #Insurance against possible case issue in font specification
            self.Font[0] = self.Font[0].lower()
            self.Font[2] = self.Font[2].lower()
            #Get font size as an integer; if it's invalid pick 12 as an arbitrary value.
            try:
                self.Font[1] = int(self.Font[1])
            except:
                self.Font[1] = 12 
            #Selected the requested font in the listbox. If the requested font is not in our
            #    list of fonts, arbitrarily select the first font in the list.
            try:
                FontIndex = Families.index(self.Font[0])
            except ValueError:
                FontIndex = 0
            self.FamiliesListBox.FetchWidget().selection_set(FontIndex)
            self.FamiliesListBox.FetchWidget().see(FontIndex)
            #Font size counter
            self.Counter1.Set(abs(self.Font[1]))

            #Font size-type radio buttons
            if self.Font[1] > 0:
                self.RadioSizeStyle.invoke('Points')
            else:
                self.RadioSizeStyle.invoke('Pixels') 
            #Font modifier checkbuttons
            for Modifier in ('Bold','Italic','Underline','Overstrike'):
                if Modifier.lower() in self.Font[2].split():
                    #This modifier is enabled
                    if not Modifier in self.RadioFontAttributes.getcurselection():
                        #But the checkbox is not set
                        self.RadioFontAttributes.invoke(Modifier)
            self.Initializing = 0
            self.Text1.delete('1.0',END)
            self.Text1.insert(END,'The quick brown fox jumps over the lazy brown dog. 0123456789'
                ,'demotext')
            TState = NORMAL
        else:      
            #We are using the default font.
            #Show no font families.
            self.FamiliesListBox.setlist([])
            self.Text1.delete('1.0',END)             
            self.EnableWidgets(False)
        #Set state of various widgets per setting
        self.Initializing = 0
        self.on_UpdateNow()
        
    def EnableWidgets(self,Flag):
        """
        If Flag is true we enable a bunch of components, else we disable them.
        """
        TState = (DISABLED,NORMAL)[Flag]
        self.Counter1.Able(Flag) 
        self.Label2.config(state=TState)
        self.FamiliesListBox.FetchLabel().config(state=TState)  
        for J in range(self.RadioSizeStyle.numbuttons()):
            self.RadioSizeStyle.button(J).config(state=TState)
        for J in range(self.RadioFontAttributes.numbuttons()):
            self.RadioFontAttributes.button(J).config(state=TState)        


#-------------------------------------------------------------------------------
#
#   float
#
#-------------------------------------------------------------------------------

def float_Validate(Arg,OptionName):
    """
    Verify that we like a float.
    
    The result is a tuple consisting of:
        o "[0]" 1 if we like the argument, or an error string if we don't.
        o "[1]" The argument,

    Note: Since floats are just simple numbers we provide a validation routine
        but no assist.        
    """
    Arg = str(Arg).strip()
    if len(Arg) == 0:
        return ('Option "%s" can not be blank.'%OptionName,Arg)
    try:
        float(Arg)
        return (1,Arg)
    except:    
        return('"%s" is not a valid floating point number.'%Arg,Arg)

class float_Assist:
    """
    There is no assist for this type of option. 
    
    This dummy assist exists
        only so we can create a list of validation and assist routines
        in the main program without having to special case this type.
    """

    def  __init__(self,ValueToEdit,OptionName):
        raise Exception, "Unexpected use of dummy assist"


#-------------------------------------------------------------------------------
#
#   proc
#
#-------------------------------------------------------------------------------

def command_Validate(Arg,OptionName):
    """
    Verify that we like a command
    
    The result is a tuple consisting of:
        o "[0]" 1 if we like the argument, or an error string if we don't.
        o "[1]" The argument,
        
    I'm not sure there is anything we can check for here. The user is specifying
        the name of a procedure and for all I know they could have a dictionary
        of procedures and hence specify something like "mydict['mykey']"
        which would be quite legal. I think users are sort of on their own
        recognisance here.
        
    This routine exists, pro forma so to speak, in case in the future we decide
        we do want to put some checks on procedure names.    
    """
    return (1,Arg)

class command_Assist:
    """
    The assist to handle the "command" option, which is really a binding in option's
        clothing.
    
    "ValueToEdit" is the initial value to show the user, ie the name of the event
        handler to which this command option referrs unless this is the first time the
        user as invoked the proc assist on this widget in which case it will be an
        empty string. It is taken, unchecked, from the Entry widget. 

    "CreateHandlerFlag" is a boolean. If "ValueToEdit" is not emtpy then we return
        this value untouched. If "ValueToEdit" is empty (ie this command option was
        blank) then we put up a "Create handler" checkbox and return it's setting.
        This allows the user to create a command option but omit the automatically
        generated handler, eg to link to scrollbars.
    
    "OptionName" the name of the current option.

    "NameOfWidreq" is just like it says.
    
    "HandlerList" is a list of all the event handlers currently defined in our form.
        
    If the user chooses CANCEL we return None.
    
    If the result is not None then the user has entered a valid value and pressed OK and
        the result is a tuple:
        [0] The name of the handler as entered by the user.
        [1] The "CreateHandlerFlag" boolean.
    """
    def  __init__(self,ValueToEdit,CreateHandlerFlag,OptionName,HandlerList,NameOfWidreq):
        #This is our default result in case we close unexpectedly
        self.Result = None
        self.ValueToEdit = ValueToEdit = str(ValueToEdit)
        self.OptionName = OptionName
        self.NameOfWidreq = NameOfWidreq
        self.HandlerList = HandlerList
        self.CreateHandlerFlag = CreateHandlerFlag
        #create the window
        Width = 300
        Height = 250
        self._Win = Toplevel()
        self._Win.title(Rph.Cap(OptionName))
        #We want to position ourself near the mouse        
        MouseX, MouseY = self._Win.winfo_pointerxy()
        
        Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
        if Geo[3]+Height+70 > self._Win.winfo_screenheight():
            #but don't run us off the bottom of the screen
            Geo[3] = max(self._Win.winfo_screenheight()-Height-70,0)
        self._Win.geometry(Rph.GeometryEncode(Geo))
        
        
        if self.ValueToEdit == '':
            #No handler is currently associated with this command option so make up
            #    a standard-format suggested handler name.

            #Remove leading underscores from widget name so we don't get triple underscores
            NW = self.NameOfWidreq
            if NW[:2] == '__':
                NW = NW[2:]

            self.ValueToEdit = '%son_%s_%s'%(Cfg.Info['ManglePrefix'], NW, self.OptionName[:7])
            self.FirstTime = True
            Msg = ('No event handler is currently associated with this command option. '
                'A suggested handler name has been generated as shown below. '
                'To accept this name and generate the corresponding handler, click '
                '"OK"; otherwise type or select the handler name as desired.')
        else:
            self.FirstTime= False    
            Msg = ('The event handler shown below is currently associated with this '
                'command-option.')

        #
        #message label
        #
        self.LabelStringVar = StringVar()
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar)
        self.OurLabel.pack(anchor='w',pady=10,expand=YES,fill=BOTH)
        self.LabelStringVar.set(Rph.TextBreak(Msg,40))

        #
        # Check button or label
        #
        if self.FirstTime:
            self.CreateHandler = Rpw.CheckbuttonRP(self._Win,text='Rapyd-Tk maintained handler.')
            self.CreateHandler.pack(pady=10,padx=20,anchor=W)
            self.CreateHandler.set(1)
        else:
            if self.CreateHandlerFlag:
                Temp = 'Type: Rapyd-Tk maintained.'
            else:
                Temp = 'Type: User maintained.'
            Label(self._Win,text=Rph.TextBreak(Temp,40)).pack(anchor=W,pady=10,expand=YES,fill=BOTH)        
                
        #
        # Combo box for handler entry/selection
        #
        HandlerList.sort()        
        self.HandlerCombo = Rpw.ComboBox(self._Win,arrowicon=Cfg.Info['ComboIcon'])
        self.HandlerCombo.pack(side=TOP,anchor=W,fill=X,padx=20)
        self.HandlerCombo.ChoiceListSet(HandlerList)
        self.HandlerCombo.selectitem(self.ValueToEdit)
        #
        #button bar across the bottom
        #
        self.BB = Rph.ButtonBox(self._Win)
        self.BB.pack(side='bottom')
        self.BB.add('OK',command=self.on_OK)
        if not self.FirstTime:
            self.BB.add('Clear',command=self.on_Delete)
        self.BB.add('Help',command=self.on_Help)
        self.BB.add('Cancel',command=self.on_Cancel)
        #be modal
        Rph.Grabber(self._Win)
        self._Win.wait_window()

    def on_OK(self,Event=None):

        NewValue = self.HandlerCombo.getcurselection().strip()
        #Verify event handler given    
        if NewValue == '':
            if Rpw.ErrorDialog(Message='Handler name is empty.',Help=1).Result:
                Help('CommandAssist.HandlerEmpty')
            return
        if self.FirstTime:
            self.CreateHandlerFlag = self.CreateHandler.get()
        #This is a bit obscure. We allow dots in the name if the name is not that of a rapyd
        #    maintaied handler.     
        if not Rpw.NameVet(NewValue,AllowDot=not self.CreateHandlerFlag):    
            if Rpw.ErrorDialog(Message='Handler name (%s) is not valid.'%NewValue,Help=1).Result:
                Help('CommandAssist.HandlerInvalidName')
            return
        Temp = command_Validate(NewValue,self.OptionName)
        if Temp[0] <> 1:
            Rpw.ErrorDialog(Temp[0])
            return
        self.Result = (str(Temp[1]),self.CreateHandlerFlag)
        self._Win.destroy()    

    def on_Cancel(self):
        self._Win.destroy()    

    def on_Delete(self):
        self.Result = ('*DELETE*',self.CreateHandlerFlag)
        self._Win.destroy()

    def on_Help(self):
        if self.FirstTime:
            Help('Assist.proc.new')
        else:
            Help('Assist.proc.exist')    


#-------------------------------------------------------------------------------
#
#   dim
#
#-------------------------------------------------------------------------------

def dim_Validate(Arg,OptionName):
    """
    Verify that we like a dimensioned value
    
    The result is a tuple consisting of:
        o "[0]" 1 if we like the argument, or an error string if we don't.
        o "[1]" The argument, with leading/trailing spaces removed.
    """
    Arg = str(Arg).strip()
    if len(Arg) == 0:
        return ('Blank is not a valid dimension value',Arg)
    try:
        int(Arg)
        return (1,Arg)
    except:
        pass
    if Arg[-1] in 'cimp':
        try:
            float(Arg[:-1])
            return (1,Arg)
        except:
            pass
    return ('"%s" is neither an integer nor a number followed by "c", "i", "m" or "p".'%Arg,Arg)

class dim_Assist:
    """
    A placeholder dimensioned-value edit assist.
    
    ValueToEdit is the initial value to show the user. It is taken, unchecked, from
        the Entry widget. 
        
    If the user chooses CANCEL we return None.
    
    If the result is not None then the user has entered a valid value and pressed OK and
        the result is that valid value. For dim, valid values are:
        o An integer, or
        o An integer or float followed by one of "cimp" 
    """
    def  __init__(self,ValueToEdit,OptionName):
        raise Exception,'Unepected use of dummy assist'

#-------------------------------------------------------------------------------
#
#    cvar 
#
#-------------------------------------------------------------------------------

def cvar_Format(Text,ExtraInfo):
    """
    Format a 'cvar' specification suitable for display.
    
    "Text" is simply the name of the control variable.

    "ExtraInfo" can consist of up to four items:
        
        o A text string of up to three letters, drawn from "sif" showing the
           *allowed* types.
        o A dot
        o Either an "a" or "m" signalling Auto/Manual
        o Either "s", "i" or "f" indicating the requested type (Str/Int/Float)
        
        Note that in a newly minted widreq the cvar specification is missing
            the dot and everything following it; this information is generated
            by the cvar_Assist routine.
    """

    if not '.' in ExtraInfo:
        #nothing much to format if no dot
        Result = Text
    else:        
        TypeInfo = ''
        if ExtraInfo[-2] == 'a':
            TypeInfo = {'i':',Int','s':',Str','f':',Float'}[ExtraInfo[-1]]
        Result = '%s [%s%s]'%(Text,{'a':'Auto','m':'Man'}[ExtraInfo[-2]],TypeInfo)
    return Result    

def cvar_Validate(Arg,OptionName):
    """
    Verify that we like a cvar
    
    The result is a tuple consisting of:
        o "[0]" 1 "f we like the argument, or an error string if we don't.
        o "[1]" The argument,
        
    I'm not sure there is anything we can check for here. The user is specifying
        the name of a variable and for all I know they could have a dictionary
        of control variables and hence specify something like "mydict['mykey']"
        which would be quite legal. I think users are sort of on their own
        recognisance here.
        
    This routine exists, pro forma so to speak, in case in the future we decide
        we do want to put some checks on control variable names.    
    """
    return (1,Arg)                   

class cvar_Assist:
    """
    The cvar edit assist.
    
    "ValueToEdit" is the initial value to show the user. It is taken, unchecked, from
        the Entry widget. 
        
    If the user chooses *CANCEL* we return "None".

    If the user chooses OK then we return a two element list:
        o "[0]" The name of the control variable.
        o "[1]" The present "ExtraInfo" settings    
    """
    def  __init__(self, ValueToEdit, OptionName, ExtraInfo, WidreqName):
        """
        Create the assist.
        """
        #This is our default result in case we close unexpectedly
        self.Result = None
        self.ValueToEdit = ValueToEdit = str(ValueToEdit)
        self.OptionName = OptionName
        #create the window
        Width = 500
        Height = 400
        self._Win = Toplevel()
        self._Win.title(Rph.Cap(OptionName))
        #The format of cvar ExtraInfo is described with cvar_Format
        Temp = ExtraInfo.split('.')
        assert len(Temp) in (1,2)
        self.AllowedTypes = Temp[0]
        if len(Temp) == 1:
            self.AutoFlag = 'a'
            self.TypeFlag = self.AllowedTypes[0]
        else:
            assert len(Temp[1]) == 2
            self.AutoFlag, self.TypeFlag = Temp[1]
            assert self.AutoFlag in 'am'
            assert self.TypeFlag in self.AllowedTypes
        TypeNames = {'s' : 'string', 'i' : 'integer', 'f' : 'float'}    
        #We want to position ourself near the mouse        
        MouseX, MouseY = self._Win.winfo_pointerxy()
        
        Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
        if Geo[3]+Height+70 > self._Win.winfo_screenheight():
            #but don't run us off the bottom of the screen
            Geo[3] = max(self._Win.winfo_screenheight()-Height-70,0)
        self._Win.geometry('+100+100')

        #just for space
        Label(self._Win).pack(side=TOP)
                
        #message label
        Msg = 'Control variable name:'
        self.LabelStringVar = StringVar()
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar,anchor=SW)
        self.OurLabel.pack(anchor='w',expand=YES,fill=BOTH,padx=20)
        self.LabelStringVar.set(Rph.TextBreak(Msg,40))
        
        #Entry area
        self.Entry = Entry(self._Win)
        self.Entry.insert(0,ValueToEdit)
        self.Entry.pack(expand=YES,fill=X,padx=20)
        self.Entry.bind('<KeyRelease>',self.SetState)
        self.Entry.bind('<Return>',self.on_OK)
        
        #Auto/Manual radio select
        self.AutoMan = Rpw.RadioSelect(self._Win,buttontype='radiobutton',command=self.on_AutoMan
            ,orient=VERTICAL)
        self.AutoMan.add('Auto',text='Automatically create this control variable when the widget "%s" is created.'
            %WidreqName)
        self.AutoMan.add('Manual',text='I will create this control variable manually.')
        self.AutoMan.pack(expand=YES,side=TOP,pady=10,anchor=W,padx=10)
        
        #Area for type selection/notification
        if len(self.AllowedTypes) == 1:
            self.Selection = Label(self._Win,anchor=W
                ,text='This control variable must be of type %s.'%TypeNames[self.AllowedTypes[0]])
        else:
            self.Selection = Rpw.RadioSelect(self._Win,buttontype='radiobutton',orient=VERTICAL
                ,labelpos=NW,label_text='Create control variable as type:',command=self.on_TypeChange)
            for T in self.AllowedTypes:
                self.Selection.add(T,text=TypeNames[T])
        self.Selection.pack(expand=YES,pady=10,side=TOP,anchor=W,padx=10)
        #Enable/Disable buttons as appropriate
        self.SetState()
        
        #button bar across the bottom
        self.BB = Rph.ButtonBox(self._Win)
        self.BB.pack(side='bottom')
        self.BB.add('OK',command=self.on_OK)
        self.BB.add('Help',command=self.on_Help)
        self.BB.add('Cancel',command=self.on_Cancel)
        #be modal
        self.Entry.focus_set()
        Rph.Grabber(self._Win)
        self._Win.wait_window()

    def on_Help(self):
        Help('Assist.cvar')

    def SetState(self,Event=None):
        #
        """
        Set the state of the AutoMan and Selection items as appropriate.
        """
        #Initially assume everybody will be disabled
        Auto = DISABLED
        Selection = DISABLED 
        #Decide who is and isn't to be enabled
        if self.Entry.get().strip() <> '':
            #we need a cvar name for anything to be enabled
            Auto = NORMAL
            if self.AutoFlag == 'a':
                #If automatic, then the selector enables
                Selection = NORMAL        
        #Do the actual enabling
        Colors = ('#a0a0a0', '#550000')
        for T in ('Auto','Manual'    ):
            Button = self.AutoMan.button(T)
            Button.config(state=NORMAL)
            Button.config(selectcolor=Colors[Auto==NORMAL])
            Button.config(state= Auto)
            if Auto==DISABLED:
                Button.deselect()
            else:
            
                if T[0].lower() == self.AutoFlag:
                    Button.select()
                else:
                    Button.deselect()    

        if len(self.AllowedTypes) > 1 and hasattr(self,'Selection'):
            #we have more than 1 allowed type AND Selection has been created
            self.Selection.label()['state'] = Selection
            for T in self.AllowedTypes:
                Button = self.Selection.button(T)
                Button.config(state=Selection)
                Button.config(selectcolor=Colors[Selection==NORMAL])
                if Selection==DISABLED:
                    Button.deselect()
                else:
                    if T[0].lower() == self.TypeFlag:
                        Button.select()
                    else:
                        Button.deselect()    
                        
    def on_AutoMan(self,Event=None):
        #
        """
        Called when the user makes a selection in the Auto/Manual radio select
        """
        self.AutoFlag = self.AutoMan.getcurselection()[0].lower()
        self.SetState()

    def on_TypeChange(self,Event=None):
        self.TypeFlag = self.Selection.getcurselection()[0]

    def on_OK(self,Entry=None):
        NewValue = self.Entry.get()
        Temp = cvar_Validate(NewValue,self.OptionName)
        if Temp[0] <> 1:
            Rpw.ErrorDialog(Temp[0])
            return
        ReconstructedExtraInfo = '%s.%s%s'%(self.AllowedTypes,self.AutoFlag,self.TypeFlag)    
        Name = Temp[1]
        self.Result = (Name, ReconstructedExtraInfo)
        self._Win.destroy()    

    def on_Cancel(self):
        self._Win.destroy()    

#-------------------------------------------------------------------------------
#
#    cursor
#
#-------------------------------------------------------------------------------

def cursor_Validate(Arg,OptionName):
    """
    Verify that we like a cursor
    
    The result is a tuple consisting of:
        o "[0]" 1 if we like the argument, or an error string if we don't.
        o "[1]" The argument, with possible modification by us.
        
    If we like the argument then "result[1]" will be the name of the 
        cursor or an empty string.
    """
    Arg = str(Arg).strip()
    try:
        Button(cursor=Arg)
    except:
        return ('"%s" is not the name of a valid cursor.'%Arg,Arg)
    return (1,Arg)                   

class cursor_Assist:
    """
    A placeholder cursor edit assist.
    
    ValueToEdit is the initial value to show the user. It is taken, unchecked, from
        the Entry widget. 
        
    If the user chooses CANCEL we return None.
    
    If the result is not None then the user has entered a valid value and pressed OK and
        the result is that valid value. For cursor, valid values are the name of a 
        cursor or an empty string.
    """
    def  __init__(self,ValueToEdit,OptionName):
        #This is our default result in case we close unexpectedly
        self.Result = None
        self.ValueToEdit = ValueToEdit = str(ValueToEdit)
        self.OptionName = OptionName
        #create the window
        Width = 300
        Height = 200
        self._Win = Toplevel()
        self._Win.title(Rph.Cap(OptionName))
        #We want to position ourself near the mouse        
        MouseX, MouseY = self._Win.winfo_pointerxy()
        
        Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
        if Geo[3]+Height+70 > self._Win.winfo_screenheight():
            #but don't run us off the bottom of the screen
            Geo[3] = max(self._Win.winfo_screenheight()-Height-70,0)
        self._Win.geometry(Rph.GeometryEncode(Geo))
        #message label
        Msg = 'This is a bare-bones placeholder for the "cursor" edit assist dialog. ' \
            'The plan is to provide more reasonably functionality in due course.'
        self.LabelStringVar = StringVar()
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar)
        self.OurLabel.pack(anchor='w',pady=10,expand=YES,fill=BOTH)
        self.LabelStringVar.set(Rph.TextBreak(Msg,40))
        #Entry area
        self.Entry = Entry(self._Win)
        self.Entry.insert(0,ValueToEdit)
        self.Entry.pack(expand=YES,fill=X,padx=20)
        self.Entry.bind('<Return>',self.on_OK)
        #button bar across the bottom
        self.BB = Rph.ButtonBox(self._Win)
        self.BB.pack(side='bottom')
        self.BB.add('OK',command=self.on_OK)
        self.BB.add('Cancel',command=self.on_Cancel)
        #be modal
        self.Entry.focus_set()
        Rph.Grabber(self._Win)
        self._Win.wait_window()

    def on_OK(self,Event=None):
        NewValue = self.Entry.get()
        Temp = cursor_Validate(NewValue,self.OptionName)
        if Temp[0] <> 1:
            Rpw.ErrorDialog(Temp[0])
            return
        self.Result = str(Temp[1])
        self._Win.destroy()    

    def on_Cancel(self):
        self._Win.destroy()    

#-------------------------------------------------------------------------------
#
#    color
#
#-------------------------------------------------------------------------------

def color_Validate(Arg,OptionName):
    """
    Verify that we like a color
    
    The result is a tuple consisting of:
        o "[0]" 1 if we like the argument, or an error string if we don't.
        o "[1]" The argument, with possible modification by us.
        
    If we like the argument then "result[1]" will be a string representing
        the color, either as a color name or in "#rgb" format.
        
    Note that an empty specification is not valid.
    """
    Arg = str(Arg).strip()
    if len(Arg) == 0:
        return ('Color specification can not be blank.',Arg)
    try:
        Button(bg=Arg)
    except:
        if Arg[:1] == '#':
            return ('"%s" is not an acceptable color specification.'%Arg,Arg)
        #perhaps they forgot the number-sign
        try:
            Button(bg='#'+Arg)
            Arg = '#' + Arg
        except:
            return ('"%s" is not a valid standard color.'%Arg,Arg)
    return (1,Arg)                   

class color_Assist:
    """
    A placeholder color edit assist.
    
    ValueToEdit is the initial value to show the user. It is taken, unchecked, from
        the Entry widget. 
        
    If the user chooses CANCEL we return None.
    
    If the result is not None then the user has entered a valid value and pressed OK and
        the result is that valid value. For color, valid values are the name of a 
        color or a number-sign followed by a vaild rgb color specification.
    """
    def  __init__(self,ValueToEdit,OptionName):
        #This is our default result in case we close unexpectedly
        self.Result = None
        self.ValueToEdit = ValueToEdit = str(ValueToEdit)
        self.OptionName = OptionName
        #create the window
        Width = 300
        Height = 200
        self._Win = Toplevel()
        self._Win.title(Rph.Cap(OptionName))
        #We want to position ourself near the mouse        
        MouseX, MouseY = self._Win.winfo_pointerxy()
        
        Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
        if Geo[3]+Height+70 > self._Win.winfo_screenheight():
            #but don't run us off the bottom of the screen
            Geo[3] = max(self._Win.winfo_screenheight()-Height-70,0)
        self._Win.geometry(Rph.GeometryEncode(Geo))
        #message label
        Msg = 'This is a bare-bones placeholder for the "color" edit assist dialog. ' \
            'The plan is to provide more reasonably functionality in due course.'
        self.LabelStringVar = StringVar()
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar)
        self.OurLabel.pack(anchor='w',pady=10,expand=YES,fill=BOTH)
        self.LabelStringVar.set(Rph.TextBreak(Msg,40))
        #Entry area
        self.Entry = Entry(self._Win)
        self.Entry.insert(0,ValueToEdit)
        self.Entry.pack(expand=YES,fill=X,padx=20)
        self.Entry.bind('<Return>',self.on_OK)
        #button bar across the bottom
        self.BB = Rph.ButtonBox(self._Win)
        self.BB.pack(side='bottom')
        self.BB.add('OK',command=self.on_OK)
        self.BB.add('Cancel',command=self.on_Cancel)
        #be modal
        self.Entry.focus_set()
        Rph.Grabber(self._Win)
        self._Win.wait_window()
            
    def on_OK(self,Event=None):
        NewValue = self.Entry.get()
        Temp = color_Validate(NewValue,self.OptionName)
        if Temp[0] <> 1:
            Rpw.ErrorDialog(Temp[0])
            return
        self.Result = str(Temp[1])
        self._Win.destroy()    

    def on_Cancel(self):
        self._Win.destroy()    

#-------------------------------------------------------------------------------
#
#    bitmap
#
#-------------------------------------------------------------------------------

def bitmap_Validate(Arg,OptionName):
    """
    Verify that we like a bitmap
    
    The result is a tuple consisting of:
        o "[0]" 1 if we like the argument, or an error string if we don't.
        o "[1]" The argument, with possible modification by us.
        
    If we like the argument then "result[1]" will be a string representing
        either a standard bitmap or "@" followed by the path to a valid
        ".xbm" bitmap file.
        
    Note that an empty string is valid, and denotes 'no bitmap'.        
    """
    try:
        Button(bitmap=Arg)
    except:
        if Arg[:1] == '@':
            if not os.path.exists(Arg[1:]):
                return ('No file named "%s" was found.'%Arg[1:],Arg) 
            return ('File "%s" is not an acceptable .xbm bitmap.'%Arg,Arg)
        #perhaps they forgot the at-sign
        try:
            Button(bitmap='@'+Arg)
            Arg = '@' + Arg
        except:
            return ('"%s" is not a valid standard bitmap.'%Arg,Arg)
    return (1,Arg)                   

class bitmap_Assist:
    """
    A placeholder bitmap edit assist.
    
    ValueToEdit is the initial value to show the user. It is taken, unchecked, from
        the Entry widget. 
        
    If the user choosed CANCEL we return None.
    
    If the result is not None then the user has entered a valid value and pressed OK and
        the result is that valid value. For bitmap, valid values are an empty string,
        the name of a standard bitmap or an at-sign followed by the path to a valid
        .xbm bitmap file.
    """
    def  __init__(self,ValueToEdit,OptionName):
        #This is our default result in case we close unexpectedly
        self.Result = None
        self.ValueToEdit = ValueToEdit = str(ValueToEdit)
        self.OptionName = OptionName
        #create the window
        Width = 300
        Height = 200
        self._Win = Toplevel()
        self._Win.title(Rph.Cap(OptionName))
        #We want to position ourself near the mouse        
        MouseX, MouseY = self._Win.winfo_pointerxy()
        
        Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
        if Geo[3]+Height+70 > self._Win.winfo_screenheight():
            #but don't run us off the bottom of the screen
            Geo[3] = max(self._Win.winfo_screenheight()-Height-70,0)
        self._Win.geometry(Rph.GeometryEncode(Geo))
        #message label
        Msg = 'This is a bare-bones placeholder for the "bitmap" edit assist dialog. ' \
            'The plan is to provide more reasonably functionality in due course.'
        self.LabelStringVar = StringVar()
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar)
        self.OurLabel.pack(anchor='w',pady=10,expand=YES,fill=BOTH)
        self.LabelStringVar.set(Rph.TextBreak(Msg,40))
        #Entry area
        self.Entry = Entry(self._Win)
        self.Entry.insert(0,ValueToEdit)
        self.Entry.pack(expand=YES,fill=X,padx=20)
        self.Entry.bind('<Return>',self.on_OK)
        #button bar across the bottom
        self.BB = Rph.ButtonBox(self._Win)
        self.BB.pack(side='bottom')
        self.BB.add('OK',command=self.on_OK)
        self.BB.add('Cancel',command=self.on_Cancel)
        #be modal
        self.Entry.focus_set()
        Rph.Grabber(self._Win)
        self._Win.wait_window()
            
    def on_OK(self,Event=None):
        NewValue = self.Entry.get()
        Temp = bitmap_Validate(NewValue,self.OptionName)
        if Temp[0] <> 1:
            Rpw.ErrorDialog(Temp[0])
            return
        self.Result = str(Temp[1])
        self._Win.destroy()    

    def on_Cancel(self):
        self._Win.destroy()    

#-------------------------------------------------------------------------------
#
#    bbox
#
#-------------------------------------------------------------------------------
    
def bbox_Validate(Arg,OptionName):
    """
    Verify that we like a bbox.
    
    The result is a tuple consisting of:
        o "[0]" 1 if we like the argument, or an error string if we don't.
        o "[1]" The argument after we finish messing with it.
        
    If we like the argument then "result[1]" will be either a 4-element tuple
        or an empty string.    
    """
    Arg = Arg.strip()
    if Arg == '':
        #Empty is allowed
        return (1,Arg)
    Arg = Rpw.Tupalize(Arg)
    if len(Arg) <> 4:
        return (Rph.Cap('%s must be four integers, or all blank.'%OptionName),Arg)
    if Arg[0] > Arg[2]:
        return (Rph.Cap('%s first value (X1) must be less than or equal to the third value (X2)'%OptionName),Arg)
    if Arg[1] > Arg[3]:
        return (Rpw.Cam('%s second value (Y1) must be less than or equal to the fourth value (Y2)'%OptionName),Arg)
    return (1,Arg)            

class bbox_Assist:
    """
    A placeholder bbox edit assist.
    
    ValueToEdit is the initial value to show the user. It is taken, unchecked, from
        the Entry widget. 
        
    If the user choosed CANCEL we return None.
    
    If the result is not None then the user has entered a valid value and pressed OK and
        the result is that valid value. For bbox valid values are either an empty string
        or a 4-tuple of integers.
    """
    def  __init__(self,ValueToEdit,OptionName):
        #This is our default result in case we close unexpectedly
        self.Result = None
        self.ValueToEdit = ValueToEdit = str(ValueToEdit)
        self.OptionName = OptionName
        #create the window
        Width = 300
        Height = 200
        self._Win = Toplevel()
        self._Win.title(Rph.Cap(OptionName))
        #We want to position ourself near the mouse        
        MouseX, MouseY = self._Win.winfo_pointerxy()
        
        Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
        if Geo[3]+Height+70 > self._Win.winfo_screenheight():
            #nuy don't run us off the bottom of the screen
            Geo[3] = max(self._Win.winfo_screenheight()-Height-70,0)
        self._Win.geometry(Rph.GeometryEncode(Geo))
        #message label
        Msg = 'This is a bare-bones placeholder for the "bbox" edit assist dialog. ' \
            'The plan is to provide more reasonably functionality in due course.'
        self.LabelStringVar = StringVar()
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar)
        self.OurLabel.pack(anchor='w',pady=10,expand=YES,fill=BOTH)
        self.LabelStringVar.set(Rph.TextBreak(Msg,40))
        #Entry area
        self.Entry = Entry(self._Win)
        self.Entry.insert(0,ValueToEdit)
        self.Entry.pack(expand=YES)
        self.Entry.bind('<Return>',self.on_OK)
        #button bar across the bottom
        self.BB = Rph.ButtonBox(self._Win)
        self.BB.pack(side='bottom')
        self.BB.add('OK',command=self.on_OK)
        self.BB.add('Cancel',command=self.on_Cancel)
        #be modal
        self.Entry.focus_set()
        Rph.Grabber(self._Win)
        self._Win.wait_window()
            
    def on_OK(self,Event=None):
        NewValue = self.Entry.get()
        Temp = bbox_Validate(NewValue,self.OptionName)
        if Temp[0] <> 1:
            Rpw.ErrorDialog(Temp[0])
            return
        self.Result = str(Temp[1])
        self._Win.destroy()    

    def on_Cancel(self):
        self._Win.destroy()    

class BindAssist:
    """
    The assist that edits bind events and handler names.
    
    "BindQuad" is a 4-tuli:
        o "[0]" The event as a decomposition list as returned by "EventStringDecompose"
        o "[1]" The event as a string.
        o "[2]" A string giving the name of the handler for this event.
        o "[3]" '' if this binding applies to the base widget or the name of the component
                to which it applies, eg 'frame' or 'entryfield.entry'.
        
    "NameOfWidreq" is just like it says.
    
    "ExistingEvents" is a list of tuples, one for each binding of this widreq except
        the current binding. Each tuple consists of [0] the event string for this
        binding, [1] the Component for this binding. The point of this is to help prevent
        duplicate bindings. As long as the user uses the wizard it will prevent
        duplicates, but it is quite possible to create by-hand event strings that
        are different strings but refer to the same event; these we make no attempt
        to detect. 
        
    "HandlerList" is a list of all the event handlers currently defined in our form.
    
    "ComponentList" is a list off all the components in the current widreq.
        
    If we are being handed a new bind event then it will be "(None,'','')"
    
    Our result is returned in self.Result.
        o If the user cancels we return None.
        o If a non-empty event was supplied and the user chose to delete it then
              we return "'*DELETE*'".
        o Otherwise we return a BindTriple as described above. 
    """
    def  __init__(self,BindQuad, NameOfWidreq, ExistingEvents, HandlerList, ComponentList):
        self.NameOfWidreq = NameOfWidreq
        self.ComponentList = ComponentList
        #This is our default result in case we close unexpectedly
        self.Result = None
        self.Decomposition, self.Event, self.Handler, self.Component = BindQuad
        if ComponentList == []:
            #If widget has no components then there can't be a component on start.
            self.Component = ''
        self.ExistingEvents = ExistingEvents
        #create the window
        Width = 450
        Height = 350
        self.Win = Toplevel()
        self.Win.title('Bind Assist')
        BlabWidth = 55
        #We want to position ourself near the mouse        
        MouseX, MouseY = self.Win.winfo_pointerxy()
        Geo = [Width, Height, MouseX-70, MouseY - 50]
        if Geo[3]+Height+70 > self.Win.winfo_screenheight():
            #but don't run us off the bottom of the screen
            Geo[3] = max(self.Win.winfo_screenheight()-Height-70,0)
        self.Win.geometry('+%s+%s'%(Geo[2], Geo[3]))
        
        if ComponentList:
            self.ComponentChoiceList = [NameOfWidreq]
            for C in ComponentList:
                self.ComponentChoiceList.append('%s.%s'%(NameOfWidreq,C))
            self.ComponentChoiceList.sort()
            if self.Component == '':
                CurrentComponent = NameOfWidreq
            else:    
                CurrentComponent = self.Component
        
            Label(self.Win,text=Rph.TextBreak('\nSelect this widget or the widget component to which '
                'this binding is to apply.',BlabWidth),justify=LEFT).pack(side=TOP,anchor=W,padx=20)
            self.ComponentCombo = Rpw.ComboBox(self.Win,arrowicon=Cfg.Info['ComboIcon'])
            self.ComponentCombo.pack(side=TOP,anchor=W,fill=X,padx=20)
            self.ComponentCombo.ChoiceListSet(self.ComponentChoiceList)
            self.ComponentCombo.selectitem(CurrentComponent)

            Label(self.Win).pack()
            
        #
        # Label at top
        #
        if self.Event == '':
            Word = 'specify the new'
        else:
            Word = 'revise the current'    
        Text = Rph.TextBreak('\nTo %s event either click on the "Event Wizard" button (the easy way) '
            'or type in the event string below the Wizard button (the hard way).'%Word,BlabWidth)
        L = Label(self.Win,text=Text,justify=LEFT)
        L.pack(side=TOP,anchor=W,padx=20)
        L.HelpTopic = 'Event'
        L.bind(HelpButton,self.on_Help)
        #
        # Button for the bind event wizard
        #
        Wizard = Button(self.Win,text='Event Wizard',command=self.on_Wizard)
        Wizard.pack(side=TOP,pady=10,anchor=W,padx=20)
        Wizard.HelpTopic = 'Event'
        Wizard.bind(HelpButton,self.on_Help)
        #
        # Entry for the actual event name my hand
        #
        self.EventName = Entry(self.Win,width=30)
        self.EventName.insert(0,self.Event)
        self.EventName.pack(side=TOP,anchor=W,fill=X,padx=20)
        #
        # Label for handler instructions
        #
        Text = Rph.TextBreak('\n\n\nKey in or select the name of the handler for this event:',BlabWidth)
        L = Label(self.Win,text=Text,justify=LEFT)
        L.pack(side=TOP,anchor=W,padx=20)
        L.HelpTopic = 'Handler'
        L.bind(HelpButton,self.on_Help)
        #
        # Combo box for handler entry/selection
        #
        HandlerList.sort()        
        self.HandlerCombo = Rpw.ComboBox(self.Win,arrowicon=Cfg.Info['ComboIcon'])
        self.HandlerCombo.pack(side=TOP,anchor=W,fill=X,padx=20)
        self.HandlerCombo.ChoiceListSet(HandlerList)
        self.HandlerCombo.selectitem(self.Handler)
        #
        # Some space
        #
        Label(self.Win,text='\n').pack()
        #
        # Buttons across the bottom
        #
        self.ButtonBox = Rph.ButtonBox(self.Win)
        self.ButtonBox.add('OK',command=self.on_OK)
        if self.Event <> '':
            T = self.ButtonBox.add('Delete',command=self.on_Delete)
            T.HelpTopic = 'Delete this binding'
            T.bind(HelpButton,self.on_Help)
        self.ButtonBox.add('Help',command=self.on_Help)
        self.ButtonBox.add('Cancel',command=self.on_Cancel)
        self.ButtonBox.pack(side=BOTTOM,fill=X)
        for B in 'OK Help Cancel'.split():
            T = self.ButtonBox.button(B)
            T.HelpTopic = 'General'
            T.bind(HelpButton,self.on_Help)
        #be modal
        Rph.Grabber(self.Win)
        self.Win.wait_window()
        
    def on_OK(self):
        """
        User pressed the OK button
        """
        #Build result:
        #   [0] Decomposed event string
        #   [1] Plain event string
        #   [2] Handler name
        #   [3] Component name
        EventString = self.EventName.get().strip()
        Decomp = EventStringDecompose(EventString)
        Component = ''
        if self.ComponentList:
            #Non-empty component list implies widget with components.
            #Verify that we like the Component specification
            Component = self.ComponentCombo.getcurselection()
            if not Component in self.ComponentChoiceList:
                if Rpw.ErrorDialog(Message='Invalid component value.',Help=1).Result:
                    Help('BindAssist.BadComponent',[Component])
                return    
            if Component == self.NameOfWidreq:
                #Empty indicates the actual widget itself
                Component = ''
            else:
                #Shoot off everything up to and including the first dot.
                Component = Component[Component.find('.')+1:]    
        self.Result = [Decomp, EventString, self.HandlerCombo.getcurselection().strip(), Component]
        #Verify event string specified
        if self.Result[1] == '':
            if Rpw.ErrorDialog(Message='Event string is empty.',Help=1).Result:
                Help('BindAssist.EventEmpty')
            return
        if self.Result[1][0] <> '<' or self.Result[1][-1] <> '>':
            if Rpw.ErrorDialog(Message='Event string not in angle brackets.',Help=1).Result:
                Help('BindAssist.EventNoAngle')
            return
            
        #Verify event handler given    
        if self.Result[2] == '':
            if Rpw.ErrorDialog(Message='Handler name is empty.',Help=1).Result:
                Help('BindAssist.HandlerEmpty')
            return
        if not Rpw.NameVet(self.Result[2]):    
            if Rpw.ErrorDialog(Message='Handler name (%s) is not valid.'
                %self.Result[2],Help=1).Result:
                Help('BindAssist.HandlerInvalidName')
            return
        if (self.Result[1],Component) in self.ExistingEvents:
            if Component:
                Message = 'There is already a binding between event "%s" and component "%s"' \
                ' of this widget. Either choose a different event string, a different' \
                ' component or press Cancel'%(self.Result[1],Component)
                HelpTopic = 'BindAssist.DuplicateComponent'
            else:
                Message = 'This widget already has an existing binding ' \
                'to event "%s". Either choose a different event string or ' \
                'press Cancel.'%self.Result[1]
                HelpTopic = 'BindAssist.DuplicateEvent'
            if Rpw.ErrorDialog(Message=Message,Help=1).Result:
                Help(HelpTopic,[self.Result[1],Component])
            return
        self.Win.destroy()    
        
    def on_Help(self,Event=None):
        """
        User pressed the Help button
        """
        Topic = 'BindAssist.'
        if Event == None:
            Topic += 'General'
        else:
            Topic += Event.widget.HelpTopic    
        Help(Topic)
        
    def on_Cancel(self,Event=None):
        """
        User pressed the Cancel button
        """
        self.Result = None
        self.Win.destroy()    

    def on_Delete(self):
        """
        User clicked the Delete button
        """
        Msg = 'Delete this bind entry now?'
        R = Rph.MessageDialog(Title=' Query ',Message=Msg,Buttons=(('Delete it',1),('~Cancel',None))).Result
        if R <> 1:
            return
        self.Result = '*DELETE*'
        self.Win.destroy()    
        
    def on_Wizard(self):
        """
        User asked for the event wizard
        """        
        self.Event = self.EventName.get()
        Component = ''
        if self.ComponentList:
            #Non-empty component list implies widget with components
            Component = self.ComponentCombo.getcurselection()
            if not Component in self.ComponentChoiceList:
                if Rpw.ErrorDialog(Message='Invalid component value. Please correct the'
                    ' component selection before running the wizard.',Help=1).Result:
                    Help('BindAssist.BadComponent')
                return    
            if Component == self.NameOfWidreq:
                #Empty indicates the actual widget itself
                Component = ''
            else:
                #Shoot off everything up to but not including the first dot.
                Component = Component[Component.find('.'):]
            #And convert any dots to underscores
            Component = Component.replace('.','_')
        self.Decomposition = EventStringDecompose(self.Event)
        if self.Decomposition[3] <> 1:
            #The event string is beyond the domain of the wizard
            Msg = 'The event description string "%s" is beyond the domain of event descriptions '       \
                'that the Wizard can handle. (The Wizard\'s comment about the string was "%s".)\n\n'      \
                'At this point you can either contine with the Wizard, which will help you to create '  \
                'a complete new event description string, or you can cancel, after which you can '      \
                '(if you wish) modify the event description string by hand.'%(self.Event,self.Decomposition[3])
            R = Rph.MessageDialog(Title=' Query ',Message=Msg,Buttons=(('Wizard',1),('~Cancel',None))).Result
            if R == None:
                #User said to cancel
                return
        #Note that if the decomposed string is non-wizard compliant, the wizard ignores it.        
        R = BindEventWizard(DecomposedEvent=self.Decomposition).Result
        if R <> None:
            self.EventName.delete(0,END)
            self.EventName.insert(0,R)
            self.Event = R
            self.Decomposition = EventStringDecompose(R)
            ##D('Decomposition=%s'%str(self.Decomposition))
            ##D('Abbreviation=%s'%EventAbbreviate(self.Decomposition))
            assert self.Decomposition[3] == 1
            #Create Event_Detail_Modifiers string
            Temp = EventAbbreviate(self.Decomposition)
            ##D('Name=<%s>'%Temp)
            #Shoot off leading underscores from widreq name; no point in having three embedded
            #    underscores in the handler name.
            NW = self.NameOfWidreq
            if NW[:2] == '__':
                NW = NW[2:]
            self.Handler = '%son_%s%s_%s'%(Cfg.Info['ManglePrefix'], NW, Component,Temp)
            self.HandlerCombo.selectitem(self.Handler)
        
#-------------------------------------------------------------------------------                
#
# Bind Editor related
#
#-------------------------------------------------------------------------------                

def EventAbbreviate(DecomposedEvent):
    """
    Given a decomposed event string, return an abbreviation of the string.
    
    This only works on wizard compliant decomposed event strings. If passed a non-wizard
        compliant string we return "None".
    """
    BasicEvents = {'Activate':'Actvte','ButtonPress':'Button', 'ButtonRelease':'ButRel', 'Configure':'Config',  
        'Deactivate':'Deact',
        'Destroy':'Dstry', 'Enter':'Enter', 'Expose':'Expose', 'FocusIn':'FocIn', 'FocusOut':'FocOut', 'KeyPress':'Key',
        'KeyRelease':'KeyRel', 'Leave':'Leave', 'Map':'Map', 'Motion':'Motion', 'Unmap':'Unmap', 'Visibility':'Vis'}
    Modifiers = {'Alt':'A', 'Any':'N', 'Control':'C', 'Double':'D', 'Lock':'L', 'Shift':'S', 'Triple':'T'}
    
    if DecomposedEvent[3] <> 1:
        return None    
    #Start with the abbreviation for the basic event    
    Result = BasicEvents[DecomposedEvent[0]]
    #Glue detail on verbatim
    if DecomposedEvent[1] <> '' or DecomposedEvent[2] <> '':
        #Supply detail if we have detail or modifiers
        Result += '_' + DecomposedEvent[1]
    #If we have modifiers make then into a single string
    if DecomposedEvent[2] <> '':
        ModString = ''
        for Mod in DecomposedEvent[2].split():
            ModString += Modifiers[Mod]
        Result += '_%s'%ModString
    return Result            

def EventStringDecompose(ES):
    """
    Attempt to decompose a Tk bind event string into it's component parts.
    
    The result is a list:
        o [0] The basic event (eg "ButtonPress")
        o [1] The detail, possibly empty (eg "a")
        o [2] A space delimited list of modifiers, possibly empty (eg "Alt Shift") in 
              in alphabetical order.
        o [3] 1 if the event string is within the comprehension of the wizard, or a reason
              string saying why not.
              
    This routine has two purposes:
    
        o It lets us know if the event string is suitable for use by the wizard and gives
            a reason if not.
        o A list of results from this function is suitable for sorting, since the event
            type, the important part, comes first, followed by the detail and lastly by
            the lowly modifiers.              
    """
    #Here are the ones the wizard knows about
    BasicEvents = 'Activate ButtonPress ButtonRelease Configure Deactivate Destroy Enter Expose ' \
        'FocusIn FocusOut KeyPress KeyRelease Leave Map Motion Unmap Visibility'.split()
        #And here are a bunch of far-out ones
    ExtendedEvents = 'MouseWheel Property Colormap MapRequest CirculateRequest ResizeRequest ' \
        'ConfigureRequest Create Gravity Reparent Circulate'.split()
    
    #The common modifiers    
    Modifiers = 'Alt Any Control Double Lock Shift Triple'.split()
    ExtendedModifiers = 'Button1 Button2 Button3 Button4 Button5 Mod1 Mod2 Mod3 Mod4 Mod5 ' \
        'M1 M2 M3 M4 M5 Meta M Quadruple'.split()
    #Assume the wizard can comprehend this string
    Wizard = 1
    #All fields start out empty
    ResultEvent = ''
    ResultDetail = ''
    #Modifier dictionary starts out all off
    ModDict = {}
    for Temp in Modifiers:
        ModDict[Temp] = 0
    WeHaveModifiers = 0    
    #Death to whitespace
    ES = ES.strip()    
    class Done(Exception): pass
    class NoDice(Exception): pass
    try:
        if ES == '':
            raise Done
        if ES[0] == '<' and ES[-1] == '>':
            #We have matching angle brackets; toast them
            ES = ES[1:-1]
        elif (ES[0]=='<' and ES[-1]<>'>') or (ES[0]<>'<' and ES[-1]=='>'):
            #We have mismatched angle brackets
            raise NoDice, 'Angle brackets are mismatched'
        else:
            #We have no angle brackets    
            if len(ES) > 1:
                #Multi-char non-bracket it out of our league
                ResultDetail = ES
                raise NoDice, 'No-angle-brackets and length greater then 1'
            else:
                #Single character not bracket is key press    
                ResultEvent = 'KeyPress'
        #If we have multiple claused we look no further
        if ES.count('<') > 0 or ES.count('>') > 0:
            raise NoDice, 'More than one clause'    
        #Since dashes and spaces are equivalent we convert dashes to spaces
        ES = ES.replace('-', ' ')
        #Get it as a list of strings
        ES = ES.split()    
        #Process as many leading modifiers as we can find
        while len(ES) > 0 and ES[0] in (Modifiers + ExtendedModifiers):
            WeHaveModifiers += 1
            Temp = ES.pop(0)
            ModDict[Temp] = 1
            if Temp in ExtendedModifiers:
                Wizard = "Modifier '%s' is legal for Tk but sufficiently uncommon that I don't support it"%Temp
        if WeHaveModifiers and ES == []:
            raise NoDice, Rph.Plural('It has %s modifier{/s} but no event nor detail',WeHaveModifiers)
        #At this point we may have type and/or detail parts left
        if ES[0] in (BasicEvents + ExtendedEvents):
            #We found our type
            ResultEvent = ES[0]
            if ES[0] in ExtendedEvents:
                Wizard = "Event type '%s' is legal for Tk but is sufficiently uncommon that I don't support it"%ES[0]
            ES.pop(0)        
        #At this point we hould have only a detail part or nothing left
        if len(ES) == 1:
            ResultDetail = ES[0]
            if ResultEvent == '':
                if ResultDetail in ('1','2','3'):
                    ResultEvent = 'Button'
                else:    
                    ResultEvent = 'KeyPress'
        if len(ES) > 1:
            #Too much stuff
            raise NoDice, 'Detail contains more than one item'
    except NoDice, Reason:
        Wizard = Reason
    except Done:
        pass    
    if ResultEvent == 'Button':
        ResultEvent = 'ButtonPress'    
    #Build modifier list
    ML = []
    Keys = ModDict.keys()
    Keys.sort()
    for Temp in Keys:
        if ModDict[Temp] == 1:
            ML.append(Temp)    
    return [ResultEvent, ResultDetail, ' '.join(ML), Wizard]    

class BindEventWizard:
    """
    The wizard which helps the user to create a bind event string.

    If specified "XY" should be a tuple locating the upper-left corner of the dialog.
        If omitted we position near the mouse.    

    "DecomposedEvent", if supplied, is a 4 element list as returned by the function
        "EventStringDecompose". If the decomposed event is wizard-compliant then we
        use it's values as the default values, otherwise we ignore it.
        
    The result is returned in "instance.Result".
        o If the user cancels the operation we return "None".
        o If the user finishes the event specification we return the event as a
           string, eg "<Shift-ButtonPress-A>".
           
    This class has no published methods and no published variables.       
    """
    def __init__(self,XY=None,DecomposedEvent=None):
        """
        Create the wizard.
        """
        self.BasicEvents = 'Activate ButtonPress ButtonRelease Configure Deactivate Destroy Enter Expose ' \
            'FocusIn FocusOut KeyPress KeyRelease Leave Map Motion Unmap Visibility'
        self.ButtonEvents = 'ButtonPress ButtonRelease'.split()
        self.KeyEvents = 'KeyPress KeyRelease'.split()
        self.MetaModifiers = 'Alt Control Shift Lock'.split()
        self.MetaKeys = 'Alt Control Shift Caps_Lock'.split()
        self.OurHelpPrefix = 'bind.eventwizard.'
        #Long winded text is wrapped to this number of characters
        self.BlabWidth = 45
        self.Result = None    
        self.Win = Toplevel()
        self.Win.title(' Bind Event Wizard ')
        Width = 300
        Height = 450
        if XY <> None:
            #User is placing us explicitly
            assert len(XY) == 2
            Geo = (Width,Height,XY[0],XY[1])
        else:
            #position near the mouse    
            MouseX, MouseY = self.Win.winfo_pointerxy()
        
            Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
            if Geo[3]+Height+70 > self.Win.winfo_screenheight():
                #don't run us off the bottom of the screen
                Geo[3] = max(self.Win.winfo_screenheight()-Height-70,0)
            if Geo[3] < 0:
                Geo[3] = MouseY    
        self.Win.geometry('+%s+%s'%( Geo[2], Geo[3]))
        #
        # Button bar along the bottom
        #         
        ButtonFrame = Frame(self.Win)
        ButtonFrame.pack(side=BOTTOM,fill=X)
        self.ButtonContinue = Button(ButtonFrame,text='Continue',command=self.on_Continue,state=DISABLED)
        self.ButtonBackup =   Button(ButtonFrame,text='BackUp',command=self.on_Backup,state=DISABLED)
        self.ButtonHelp =     Button(ButtonFrame,text='Help',command=self.on_Help)
        self.ButtonCancel =   Button(ButtonFrame,text='Cancel',command=self.on_Cancel)
        self.ButtonContinue.pack(side=LEFT,expand=YES)
        self.ButtonBackup.pack(side=LEFT,expand=YES)
        self.ButtonHelp.pack(side=LEFT,expand=YES)
        self.ButtonCancel.pack(side=LEFT,expand=YES)

        self.ButtonContinue.bind(HelpButton,self.on_Help)
        self.ButtonBackup.bind(HelpButton,self.on_Help)
        self.ButtonHelp.bind(HelpButton,self.on_Help)
        self.ButtonCancel.bind(HelpButton,self.on_Help)

        #A bit of space at the top
        Label(self.Win).pack(side=TOP)
        self.Progress = Label(self.Win,anchor=W)
        self.Progress.pack(side=TOP)
        self.Progress.bind(HelpButton,self.on_ProgressHelp)
        Label(self.Win).pack(side=TOP)
        
        #And some at the bottom
        Label(self.Win).pack(side=BOTTOM)
        
        #Our nominal PadY for those who need it
        self.PadY = 10
        
        #Initially we have no KeyType
        self.KeyType = None
        
        #This holds transient widgets
        self.WidgetList = []
        #
        #Create the empty variables that hold our event
        self.Modifiers = {}
        for Mods in 'Alt Any Control Double Lock Shift Triple'.split():
            self.Modifiers[Mods] = ''
        self.Detail = '' 
        self.BasicEvent = ''   
        if DecomposedEvent and DecomposedEvent[3] == 1:
            #We have a wizard compliant decomposed string
            self.BasicEvent = DecomposedEvent[0]
            self.Detail = DecomposedEvent[1]
            for Temp in DecomposedEvent[2].split():
                self.Modifiers[Temp] = Temp
        
        #
        # Start by giving the user a choice of basic events
        #
        self.State = 0
        self.DoState()
        #
        # Freeze the geometry so our toplevel doesn't bounce around in size
        #     as we display various choices
        #
        self.Win.update_idletasks()
        Temp = Rph.GeometryDecode(self.Win.winfo_geometry())
        self.Win.geometry('%sx%s+%s+%s'%(int(Temp[0]*1.5), Temp[1], Temp[2], Temp[3]))
        #
        # Be modal
        #
        self.Win.focus_set()
        Rph.Grabber(self.Win)
        self.Win.wait_window()

    def HelpSet(self,TopicId):
        """
        Bind the passed function to HelpButton on everything in sight.
        """
        self.HelpTopic = self.OurHelpPrefix + TopicId
        for W in self.WidgetList:
            W.bind(HelpButton,self.on_Help)

    def on_Help(self,Event=None):
        """
        User asked for help on HelpTopic.
        """
        Help(self.HelpTopic)

    def on_ProgressHelp(self,Event):
        """
        User help clicked on the progress label
        """
        Help(self.OurHelpPrefix + 'progress')

    def on_Cancel(self):
        """
        Cancel the wizard.
        """
        self.Win.destroy()

    def on_Continue(self,Event=None):
        """
        Advance to the next state.
        """
        #Toast any transient widgets
        self.Cleanup()        
        #Advance state
        self.State = self.NextState
        #Take the states action
        self.DoState()

    def on_Backup(self):
        """
        Backup to the previous state.
        """
        #Toast any transient widgets
        self.Cleanup()        
        #Backup state
        self.State = self.PrevState
        #Take the states action
        self.DoState()

    def ProgressUpdate(self):
        Temp = self.EventBuild()
        if Temp == '<>':
            Temp = ''
        else:
            Temp = 'Event: ' + Temp    
        self.Progress['text'] = Temp
        
    def DoState(self):    
        #We automatically disable the Continue button; the action routine we call
        #    can enable it if and when appropriate
        self.ContinueSet(DISABLED)
        #We know the state; do it
        if self.State == 0:
            #We need the basic event
            self.BasicEventGet()
            self.NextState = 1
            self.PrevState = None
        elif self.State == 1:
            #We have the basic event
            self.PrevState = 0
            if self.BasicEvent in ('ButtonPress', 'ButtonRelease'):
                #Event is mouse; get which buttons
                self.MouseButtonsGet()
                self.NextState = 2
            elif self.BasicEvent in ('KeyPress', 'KeyRelease'):
                #Event is key; get key type
                self.NextState = 4
                self.KeyGet()
            else:
                #all other types
                self.Detail = '' #simple events don't have detail
                self.ProgressUpdate() #just in case we had detail from before
                self.NextState = 999
                self.MetaModifiersGet()
        elif self.State == 2:
            #Event is mouse, have buttons, get click-count        
            self.NextState = 3
            self.PrevState = 1
            self.MouseClicksGet()
        elif self.State == 3:
            #Event is mouse, have buttons and click count, get modifiers
            self.NextState = 999
            self.PrevState = 2
            self.MetaModifiersGet()        
        elif self.State == 4:
            #Event is key, we have the key type, get the actual key
            self.PrevState = 1
            if self.KeyType == 'logical':
                self.NextState = 999
                self.KeyCodeGet()            
            elif self.KeyType == 'physical':
                self.NextState = 5
                self.KeyCodeGet()
            elif self.KeyType == 'any'    :
                self.NextState = 999
                self.MetaModifiersGet()
            else:
                raise Exception, 'Unknown KeyType: %s'%self.KeyType    
        elif self.State == 5:
            #Event is physical-key or any-key, we have the key; get modifiers
            self.NextState = 999
            self.PrevState = 4
            self.MetaModifiersGet()
        elif self.State == 999:
            #were done
            self.Result = self.EventBuild()
            self.Win.destroy()
            return    
        #The backup button we enable if there is a state to backup to.
        P = NORMAL
        if self.PrevState == None:
            P = DISABLED
        self.ButtonBackup['state'] = P        
        #If next state is 999 that means next state is finish
        self.ButtonContinue['text'] = ('Next','Finish')[self.NextState==999]

    def KeyCodeGetPress(self,Event):
        """
        Handle keypress while waiting for user to pick key
        """
        if Event.keysym == '??':
            Rph.MessageDialog(Title='Sorry',Message = "Sorry, that's not a key I know how to handle. "
                "If you really need to bind to that key you will have to create an event string "
                " manually.")
            return    
        if self.KeyType == 'physical':
            #In Physical mode the first key is THE key
            self.Detail = Event.keysym
        else:
            #In Logical mode we note meta keys but act only on non-meta keys
            for Key in self.MetaKeys:
                if Event.keysym.find(Key) <> -1:
                    #it was a meta-key; adjust state
                    self.MetaKeyState[Key] = 1
                    return
            #It wasn't a meta key        
            self.Detail = Event.keysym
            for J in range(4):
                Temp = self.MetaModifiers[J]
                if self.MetaKeyState[self.MetaKeys[J]]:
                    self.Modifiers[Temp] = Temp
                else:
                    self.Modifiers[Temp] = ''    
        #Show user current state
        self.ProgressUpdate()                    
        self.ContinueSet(NORMAL)
                
    def KeyCodeGetRelease(self, Event):
        """
        Handle key release while waiting for user to pick key
        """
        if self.KeyType == 'logical':
            #Check for meta keys
            for Key in self.MetaKeys:
                if Event.keysym.find(Key) <> -1:
                    #it was a meta-key; adjust state
                    self.MetaKeyState[Key] = 0
            
    def KeyCodeGet(self):
        """
        Have user press the actual key for binding
        """
        #If we already have detail part then they can continue immediatly
        if self.Detail <> '':
            self.ContinueSet(NORMAL)
        #Init the meta state dict 
        self.MetaKeyState = {}
        for Key in self.MetaKeys:
            self.MetaKeyState[Key] = 0
        if self.KeyType == 'physical':
            Temp = 'Press and release the one physical key for this event. Note that when dealing ' \
                ' with physical keys, Shift, Ctrl, Alt and CapsLock count as being "the one key".' 
            self.HelpSet('keyphysical')
        elif self.KeyType == 'logical':
            Temp = 'Press and hold down any of the "meta" keys (Shift, Ctrl, Alt, CapsLock) you want, then press ' \
                ' the one "real" key which is to be combined with the meta keys for this event.'
            self.HelpSet('keylogical')
        else:
            raise Exception, 'Unrecognized KeyType: %s'%self.KeyType            
        Temp = Rph.TextBreak(Temp + ' Feel free to click on HELP for more information.',self.BlabWidth)
        L = Label(self.Win,padx=10,text=Temp,justify=LEFT)
        L.pack()
        self.WidgetList.append(L)
        L = Label(self.Win)
        L.pack()
        self.WidgetList.append(L)
        L.focus_set()
        L.bind('<KeyPress>',self.KeyCodeGetPress)
        L.bind('<KeyRelease>',self.KeyCodeGetRelease)
        #Bind appropriate help to everything
        if self.KeyType == 'physical':
            self.HelpSet('keyphysical')
        elif self.KeyType == 'logical':
            self.HelpSet('keylogical')

    def KeyGetCommand(self):
        """
        User clicked a radio button.
        """
        if self.KeyTypeVar.get().find('physical') <> -1:
            self.KeyType = 'physical'
        elif self.KeyTypeVar.get().find('logical') <> -1:
            self.KeyType = 'logical'
        elif self.KeyTypeVar.get() == 'Any key':
            self.KeyType = 'any'
            self.Detail = ''
        else:
            raise 
            Exception, 'Unrecognized KeyTypeVar: %s'%self.KeyTypeVar.get()            
        self.ProgressUpdate()

    def KeyGet(self):
        """
        Help the user identify the key they want to bind to.
        """
        #Instruction at the top
        Temp = Rph.TextBreak('Do you want to respond to any key or one particular key? Click on HELP ' \
            'to learn more about the difference between physical and logical keys.',self.BlabWidth)
        L = Label(self.Win,padx=10,text=Temp,justify=LEFT)
        L.pack()
        self.WidgetList.append(L)
        L = Label(self.Win)
        L.pack()
        self.WidgetList.append(L)

        #We start with the modifiers clear
        for T in self.MetaModifiers:
            self.Modifiers[T] = ''

        #If no key type, we default to 'Any'
        if self.KeyType == None:
            self.KeyType = 'any'
        
        #Build the radio selector
        self.KeyTypeVar = StringVar()
        self.KeyTypeVar.set('')
        for T in 'Any key.A particular physical key.A particular logical key'.split('.'):
            R = Radiobutton(self.Win,padx=20,pady=self.PadY,text=T,command=self.KeyGetCommand
                ,value=T,variable=self.KeyTypeVar,anchor=W)
            R.pack(side=TOP,fill=X)
            R.bind(HelpButton,R) 
            if T.lower().find(self.KeyType) <> -1:
                self.ContinueSet(NORMAL)
                R.select()   
            self.WidgetList.append(R)
        #Setup help
        self.HelpSet('keytype')

    def MouseClicksGetCommand(self):
        """
        User made a selection; enable the continue button.
        """        
        Temp = self.MouseClicksVar.get()
        if Temp == 'Triple-click':
            self.Modifiers['Triple'] = 'Triple'
            self.Modifiers['Double'] = ''
        elif Temp == 'Double-click':
            self.Modifiers['Double'] = 'Double'
            self.Modifiers['Triple'] = ''
        elif Temp == 'Single-click':
            self.Modifiers['Double'] = ''
            self.Modifiers['Triple'] = ''
        else:    
            raise Exception, 'Invalid MouseClicks value: %s'%Temp
        self.ProgressUpdate()
        
    def MouseClicksGet(self):
        """
        Help user select the mouse clicks.
        """
        #Sanity check mouse click count and find current setting
        if self.Modifiers['Triple'] <> '':
            self.Modifiers['Triple'] = 'Triple'
            self.Modifiers['Double'] = ''
            Current = 'Triple-click'
        elif self.Modifiers['Double'] <> '':
            self.Modifiers['Double'] = 'Double'
            self.Modifiers['Triple'] = ''
            Current = 'Double-click'
        else:
            Current = 'Single-click'    
    
        #Instruction at the top
        L = Label(self.Win,text='Select mouse click-count for this event:',padx=10)
        L.pack()
        self.WidgetList.append(L)
        L = Label(self.Win)
        L.pack()
        self.WidgetList.append(L)
        
        #Build the radio selector
        self.MouseClicksVar = StringVar()
        self.MouseButtonVar.set('')
        for T in 'Single-click Double-click Triple-click'.split():
            R = Radiobutton(self.Win,command=self.MouseClicksGetCommand,padx=20,pady=self.PadY,text=T
                ,value=T,variable=self.MouseClicksVar,anchor=W)
            R.pack(side=TOP,fill=X)
            R.bind(HelpButton,R)    
            if T == Current:
                R.select()
            self.WidgetList.append(R)

        #Setup help
        self.HelpSet('mouseclicks')
        
        #Since we always have a selection the continue button is always enabled
        self.ContinueSet(NORMAL)


    def MouseButtonsGetCommand(self):
        """
        User made a selection; enable the continue button.
        """        
        Temp = self.MouseButtonVar.get()
        self.ContinueSet(NORMAL)
        if Temp == 'Any':
            self.Modifiers['Any'] = Temp
            self.Detail = ''
        else:
            self.Modifiers['Any'] = ''
            self.Detail = Temp
        self.ProgressUpdate()
        
    def MouseButtonsGet(self):
        """
        Help user select the mouse buttons.
        """
        #Sanity check mouse button settings
        if self.Modifiers['Any'] <> '':
            self.Modifiers['Any'] = 'Any'
            self.Detail = ''
        elif not self.Detail in ('1', '2', '3'):
            self.Detail = ''
        if self.Modifiers['Any'] == '' and self.Detail == '':
            #If nothing was previously selected then assume button 1
            self.Detail = '1'    
        #Instruction at the top
        L = Label(self.Win,text='Mouse button(s) to respond to:',padx=10)
        L.pack()
        self.WidgetList.append(L)
        L = Label(self.Win)
        L.pack()
        self.WidgetList.append(L)
        
        #Build the radio selector
        self.MouseButtonVar = StringVar()
        self.MouseButtonVar.set('')
        for T in '1 2 3 Any'.split():
            R = Radiobutton(self.Win,command=self.MouseButtonsGetCommand,padx=20,pady=self.PadY,text=T
                ,value=T,variable=self.MouseButtonVar,anchor=W)
            R.pack(side=TOP,fill=X)    
            if T == self.Detail or T == self.Modifiers['Any']:
                R.select()
            self.WidgetList.append(R)
        
        #The continue button is disabled unless we have a selected radiobutton        
        T = DISABLED
        if self.MouseButtonVar.get() <> '':
            T = NORMAL
        self.ContinueSet(T)
        #Setup help
        self.HelpSet('mousebuttons')

    def MetaModifiersGetCommand(self):
        """
        The user checked/unchecked on of the meta modifier Checkbuttons.
        
        This reads the value from all the meta checkbuttons and stores them in
            our "self.Modifiers" dictionary.
        """
        for T in self.MetaVars.keys():
            self.Modifiers[T] = self.MetaVars[T].get()
        self.ProgressUpdate()
        
    def MetaModifiersGet(self):
        #Instruction at the top
        L = Label(self.Win,text=Rph.TextBreak('Select any number of "meta" keys from the list below. If one or more '
            'of the meta keys are selected here, then those key(s) will have to be down for the "%s" event '
            'to happen.'%self.BasicEvent,self.BlabWidth),justify=LEFT,padx=10)
        L.pack(fill=X)
        self.WidgetList.append(L)
        L = Label(self.Win)
        L.pack()
        self.WidgetList.append(L)
        #A dictionary of ControlVars tracks the checkbuttons
        self.MetaVars = {}
        #Build the checkbutton list        
        for T in self.MetaModifiers:
            #Create a string cvar for this modifier
            self.MetaVars[T] = StringVar()
            #Hello checkbutton
            C = Checkbutton(self.Win, command=self.MetaModifiersGetCommand,offvalue='',onvalue=T,padx=20
                ,pady=self.PadY,text=T,variable=self.MetaVars[T],anchor=W)
            C.pack(side=TOP,fill=X)
            #If it's already set mark it as such    
            if self.Modifiers[T] <> '':
                C.select()
            #Remember if for cleanup    
            self.WidgetList.append(C)    
        #Setup help
        self.HelpSet('metamodifiers')
        #Since any combination is allowed the continue button is always enabled
        self.ContinueSet(NORMAL)

    def EventClassify(self,Event):
        """
        Return a character classifying the specified event type.
        
        "B" for button related events.
        "K" for keyboard related events.
        "X" for all other events.
        """
        if Event in self.ButtonEvents:
            return 'B'
        if Event in self.KeyEvents:
            return 'K'
        return 'X'
        
    def BasicEventGetCommand(self):
        """
        User made a selection; enable the continue button.
        """        
        ExistingClass = self.EventClassify(self.BasicEvent)
        self.BasicEvent = self.EventVar.get()
        NewClass = self.EventClassify(self.BasicEvent)
        if NewClass == 'X' or NewClass <> ExistingClass:
            #Clear detail if not appropriate for this class of event or if user changed event class.
            self.Detail = ''
        self.ContinueSet(NORMAL)
        self.ProgressUpdate()
        
    def BasicEventGet(self):
        """
        Help user select the basic event.
        """
        self.ProgressUpdate()
        #Instruction at the top
        L = Label(self.Win,text='Select the basic event type:',padx=10)
        L.pack()
        self.WidgetList.append(L)
        L = Label(self.Win)
        L.pack()
        self.WidgetList.append(L)
        
        #Build the radio selector
        self.EventVar = StringVar()
        self.EventVar.set('')
        for T in self.BasicEvents.split():
            R = Radiobutton(self.Win,command=self.BasicEventGetCommand,padx=20,pady=0,text=T
                ,value=T,variable=self.EventVar,anchor=W)
            R.pack(side=TOP,fill=X)    
            #If this is the currently selected event show it as such
            if T == self.BasicEvent:
                R.select()
            self.WidgetList.append(R)
        
        #This is step one, so the backup button has no meaning.
        self.ButtonBackup['state'] = DISABLED
        #The continue button is disabled unless we have a selected radiobutton        
        T = DISABLED
        if self.EventVar.get() <> '':
            T = NORMAL
        self.ContinueSet(T)
        #Setup help
        self.HelpSet('basicevent')
    
    def ContinueSet(self,State):
        """
        Enable / Disable the continue button.
        """
        self.ButtonContinue['state'] = State
        if State == NORMAL:
            self.Win.bind('<Return>',self.on_Continue)
        else:
            self.Win.unbind('<Return>')    

    def Cleanup(self):
        """
        Cleanup any transient widgets
        """    
        #Cleaning transient widgets
        for R in self.WidgetList:
            #print 'Unpacking ',R
            R.pack_forget()
        self.WidgetList = []   

    def EventBuild(self):
        """
        Build and return the event string from information on hand.
        """
        R = []
        for T in self.Modifiers.values():
            if T <> '':
                R.append(T+'-')
        R.sort()
        R.append(self.BasicEvent)
        if self.Detail <> '':
            R.append('-' + self.Detail)
        return '<%s>'%''.join(R)    
        