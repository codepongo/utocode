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
Widgets (and friends) created for use with Rapyd.

Note: A "tuli" is a tuple or a list. I got tired of typing "tuple or list" all over the place.      

"""

#=d Dialogs and Widgets
#=t Text functions
#=u Utility functions

import keyword
import os
import os.path
import random
import rpHelp as Rph
import sha
import sys
import time
import traceback
from   tkCommonDialog import Dialog
from   Tkinter import *
# Somewhere around Python 2.5 Tkinter started return Tcl objects in places
#     where it previously returned strings. Thus we set "wantobjects" to
#     false to prevent things from breaking. 
import Tkinter
Tkinter.wantobjects = False

#Use these for setting truth values, not for testing, eh?
True = 1
False = 0

#A dictionary of all those ordinary characters for which Tk uses long-winded keysyms
Xdict = {
        'bracketright':']',
        'bracketleft':'[',
        'asciicircum':'^',
        'underscore':'_',
        'parenright':')',
        'numbersign':'#',
        'braceright':'}',
        'asciitilde':'~',
        'apostrophe':"'",
        'semicolon':';',
        'parenleft':'(',
        'braceleft':'{',
        'backslash':'\\',
        'ampersand':'&',
        'quotedbl':'"',
        'question':'?',
        'asterisk':'*',
        'percent':'%',
        'greater':'>',
        'period':'.',
        'exclam':'!',
        'dollar':'$',
        'slash':'/',
        'minus':'-',
        'grave':'`',
        'equal':'=',
        'comma':',',
        'colon':':',
        'plus':'+',
        'less':'<',
        'bar':'|',
        'at':'@'
        }

def D(*Stuff):
    """=u
    This simply prints the arguments. 
    
    The point of using this, rather than 'print', is that once were done debugging 
    we can easily search for and remove the 'D' statements.
    """
    for T in Stuff:
        print T,
        print

Alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
AlphaMeric = Alpha + '0123456789'


def Wow(self, FuncName, Arg):
    assert type(FuncName) == type(''), 'You need to pass the NAME of a function, not an actual function'
    return eval('lambda s=self, a=Arg: s.%s(a)'%FuncName)

def Fontificate(S):
    """
    Deal with a string which may specify a font.
    
    If the string looks to be a tuple of the form (<Family>,<Size>[,<Modifiers>)
        then we return a tuple. 
    Otherwise we return the string as is.
    """
    try:
        T = list(eval(S))
    except:
        return S    
    if len(T) in (2,3):
        if len(T) == 2:
            T.append('')
        #Make sure size is an integer
        try:
            T[1] = int(T[1])
        except:
            return S    
        return tuple(T)
    else:
        return S        

def FontToString(Font):
    """
    Convert a font sequence to a string.
    
    If Font is empty we return None.
    If Font is a 3-tuple we format it as a string.
    If Font is a string we return it untouched.
    """
    if not Font:
        return None
    if type(Font) == type(()):    
        return '%s %s %s'%tuple(Font)
    return Font    

def Columnate(Arg,Lmarg=0,Spacing=1):
    """
    Convert a list of string tuples into a string with appropriate column widths.
    
    Arg is a list of tuples. Each tuple consists of one or more character strings. Each
        tuple has the same number of characters strings.
        
    The point of this routine is to format the argument into a series of columns so that
        the n-th string from each tuple line up one below the other. We compute the space
        for each column and format accordingly.
        
    Lmarg is the number of spaces to leave at the start of each line.
    
    Spacing is the minimum number of spaces to leave between each column.
    """
    if len(Arg) == 0:
        return ''
    MaxLengths = len(Arg[0])*[0]
    for Entry in Arg:
        for J in range(len(MaxLengths)):
            MaxLengths[J] = max(MaxLengths[J],len(Entry[J]))
    for J in range(len(MaxLengths)):
        MaxLengths[J] += Spacing        
    FormatString = ((' '*Lmarg) + ('$-%ds'*len(MaxLengths)%tuple(MaxLengths))).replace('$','%')
    Result = []
    for Entry in Arg:
        Result.append(FormatString%Entry)
    return '\n'.join(Result)    


def TextMeasure(Text,Widget):
    """=u
    Measure size of "Text", in pixels, if displayed in "Widget".
    
    I lifted this straight out of Idle. Thanks Guido.
    """
    return int(Widget.tk.call("font", "measure", Widget["font"]
        ,"-displayof", Widget.master, Text ))
        
        
def DashesToMatch(Text,Widget):
    """
    Generate a string of dashes of about the same width as "Text"
    
    Widget is the widget they are to be displayed in.
    """        
    DashWidth = TextMeasure('-',Widget)
    TextWidth = TextMeasure(Text,Widget)
    return int(round(float(TextWidth) / float(DashWidth))) * '-'


def PythonModuleFind(Name):
    """
    Walk the Python search path looking for a module.
    
    Given a simple file name, eg "Tkinter.py", we look for the first occurrance in the Python module 
        search path and return as the result the full path to the file including the file itself,
        eg "/usr/lib/python2.3/lib-tk/Tkinter.py". 
        
    If we don't find a matching file we return None.
    """
    for Path in sys.path:
        if Path:
            for FileName in os.listdir(Path):
                if FileName == Name:
                    Result = Path+'/'+Name
                    if os.path.isfile(Result):
                        return Result
    return None 


def ExtractName(Path):
    """
    Extract just the bare filename from a path.
    
    eg given "/spam/parrot/stringettes.py" we return "stringettes"
    """
    return os.path.splitext(os.path.split(Path)[1])[0]

def CurrentDate():
    """=U
    Return the current day as a "'YYYY/MM/DD'"
    """
    Temp = time.localtime(time.time())
    return '%4.4d/%2.2d/%2.2d' % Temp[0:3]

def CurrentTime():
    """
    Return the current time as "'HH:MM:SS'"
    """
    Temp = time.localtime(time.time())
    return '%2.2d:%2.2d:%2.2d'%Temp[3:6]

def CurrentDateTime():
    """
    Return current date and time as "'YYYY/MM/SS HH:MM:SS'"
    """
    return '%s %s'%(CurrentDate(),CurrentTime())

class _Dialog(Dialog):
    def _fixoptions(self):
        try:
            # make sure "filetypes" is a tuple
            self.options["filetypes"] = tuple(self.options["filetypes"])
        except KeyError:
            pass

    def _fixresult(self, widget, result):
        if result:
            # keep directory and filename until next time
            # Note: In python 2.1 "result" arrived on our doorstep as a string.
            #       Now, python 2.3, it arrives as an object of type 
            #       _tkinter.Tcl_Ojb and we blow up on and error if we don't
            #       convert it to a string. So we convert.
            result = str(result)
            path, file = os.path.split(result)
            self.options["initialdir"] = path
            #self.options["initialfile"] = file
        self.filename = result # compatibility
        return result

class Directory(_Dialog):
    command = "tk_chooseDirectory"

def AskDirectory(**options):
    """
    Invoke the common Tk dialog to get a directory.
    """
    return apply(Directory, (), options).show()

class Counter(Frame):
    """
    A simple numeric up/down counter widget.
    
    Arguments:
    
        entrywidth: Width of the entry. If omitted, defaults to 6.
            
        modifiedcommand: A command to call when the entry has been modified.
        
        
    """
    def __init__(self,Master=None,**kw):
        #
        #Fetch and validate arguments.
        #
        ArgList = (('entrywidth',       'EntryWidth',       6),
                   ('modifiedcommand',  'ModifiedCommand',  None),
                  ) 
        for ArgName,LocalName,DefaultValue in ArgList:
            if kw.has_key(ArgName):
                DefaultValue = kw[ArgName]
                del kw[ArgName]
            exec('self._Counter__%s = DefaultValue'%LocalName)
        
        #We use the height of the entry to size our buttons.        
        Size = Rph.MeasureWidget('Entry()')[1]-8

        apply(Frame.__init__,(self,Master),kw)
        ButtonRelief = FLAT
        self.__DnButton = Button(self,image=Cfg.Info['CloseIcon'],height=Size,width=Size,command=self.__on_CountDn
            ,relief=ButtonRelief)
        self.__DnButton.pack(side=LEFT)
        self.__Entry1 = Entry(self,width=self.__EntryWidth)
        self.__Entry1.pack(fill='x',side='left',expand='y')
        self.__Entry1.bind('<KeyRelease>',self.__on_KeyRelease)
        self.__UpButton = Button(self,image=Cfg.Info['OpenIcon'],height=Size,width=Size,command=self.__on_CountUp
            ,relief=ButtonRelief)
        self.__UpButton.pack(side=LEFT)
        
        self.__CurrentCount = 0
        
    #
    # Public methods
    #

    def Able(self,Flag):
        """
        Enable/Disable ourself based on boolean Flag
        """
        if Flag:
            NewState = NORMAL
        else:
            NewState = DISABLED
        self.__DnButton.config(state=NewState)
        self.__UpButton.config(state=NewState)
        self.__Entry1.config(state=NewState)
    
    def Get(self):
        """
        Return the current value of the counter.
        """
        return self.__CurrentCount

    def Set(self,Value):
        """
        Set the counter to the specified value.
        """
        self.__CurrentCount = int(Value)
        self.__Sync()

    #
    # Private methods
    #
    def __on_CountUp(self,Event=None):
        """
        User clicked on the "+" button.
        """
        self.__CurrentCount += 1
        self.__Sync()
        apply(self.__ModifiedCommand)
        
    def __on_CountDn(self,Event=None):
        """
        User clicked on the "-" button.
        """
        self.__CurrentCount -= 1
        self.__Sync()
        apply(self.__ModifiedCommand)

    def __on_KeyRelease(self,Event=None):
        """
        User released key after altering entry.
        """
        if self.__Entry1.get() == '':
            #We allow blank and treat it as zero.
            self.__CurrentCount = 0
            apply(self.__ModifiedCommand)
            return
        try:
            #If the revised value is an integer, make it our new CurrentCount
            self.__CurrentCount = int(self.__Entry1.get())
            apply(self.__ModifiedCommand)
        except ValueError:
            #But if revised value is twonky, reset the entry to the current count
            self.__Sync()    

    def __Sync(self):
        """
        Update the entry to match CurrentCount
        """
        self.__Entry1.delete(0,END)
        self.__Entry1.insert(0,str(self.__CurrentCount))
        

class ComboBox(Frame):
    """
    A simple ComboBox with drop-down choice list.
    
    Since the drop-down list does not scroll, this ComboBox is best suited for cases where
        there are a moderate number of choices.
        
    Arguments:
    
        label: If supplied, we create a label with this text to the left of the combo box.
        
        selectioncommand: If supplied, when the user selects a choice we call this function
            with no arguments.
            
        arrowicon: If supplied, should be a 2-tuli of icons (enabled,disabled) for use with
            the dropdown button. The button is disabled if there is nothing to drop down.
            
        
    """
    def __init__(self,Master=None,**kw):
        #
        #Fetch and validate arguments.
        #
        ArgList = (('label',            'Label',            None),
                   ('selectioncommand', 'SelectionCommand', None),
                   ('arrowicon',        'ArrowIcon',        None),
                  ) 
        for ArgName,LocalName,DefaultValue in ArgList:
            if kw.has_key(ArgName):
                DefaultValue = kw[ArgName]
                del kw[ArgName]
            exec('self._ComboBox__%s = DefaultValue'%LocalName)
        
        #We use the height of the entry to size out button.        
        Size = Rph.MeasureWidget('Entry()')[1]-8

        apply(Frame.__init__,(self,Master),kw)
        if self.__Label:
            #If we were passed label text then create a label at the top
            self.__Label = Label(self,text=self.__Label)
            self.__Label.pack(side=LEFT)
        self.__Entry1 = Entry(self)
        self.__Entry1.pack(fill='x',side='left',expand='y')
        self.__Entry1.bind('<KeyPress-Return>',self.__on_Return)
        if self.__ArrowIcon:
            #If we were passed an arrow icon then we use it on the drop-down button.
            self.__Button1 = Button(self,image=self.__ArrowIcon[1],command=self.__on_Button1_command)
        else:    
            #Otherwise we used an arbitrary bitmap just so our button is still sized in pixels
            self.__Button1 = Button(self,bitmap='gray25',command=self.__on_Button1_command)
        self.__Button1.pack(side='left')
        self.__Button1.config(height=Size,width=Size)
            
        self.__ChoiceList = []

    def __on_Button1_command(self,Event=None):
        """
        User clicked on the arrow to drop the selection list.
        """
        if self.__ChoiceList:
            #Do the dropdown only if ChoiceList isn't empty
            DropDown = Menu(self,tearoff=0)
            DropDown.delete(0,END)
            for Choice in self.__ChoiceList:
                DropDown.add_command(label=Choice,command=Wow(self,"_ComboBox__on_Choice",Choice))
            W,H,X,Y = Rph.WidgetInScreen(self.__Entry1)
            DropDown.tk_popup(X,Y+H)
    #
    # Public methods
    #
    def ChoiceListSet(self,ChoiceList):
        """
        Set list of choices user gets to pick from.
        """
        self.__ChoiceList = ChoiceList
        self.__SetButtonIcon()
    
    def clear(self):
        """
        Clear the selector.
        """
        self.__ChoiceList = []
        self.__SetEntry('')
        self.__SetButtonIcon()

    def component(self,Name):
        """
        User asked for a component.
        """
        if Name == 'label':
            return self.__Label
        if Name == 'entry':
            return self.__Entry1
        if Name == 'arrowbutton':
            return self.__Button1
        raise Exception, 'Unknown component "%s"'%Name

    def getcurselection(self):
        """
        Return the name of the currently selected item.
        """
        return self.__Entry1.get()

    def selectitem(self,Name):
        """
        Select the item of the specified name.
        
        This simply puts Name in the Entry.
        """
        self.__SetEntry(Name)

    def selectnone(self):
        """
        Arrange for no item to be selected.
        """            
        self.__SetEntry('')
        
    #
    # Private methods
    #

    def __on_Choice(self,ChoiceText):
        """
        User clicked on a choice
        """
        self.__SetEntry(ChoiceText)
        if self.__SelectionCommand:
            apply(self.__SelectionCommand)
        
    def __on_Return(self,Event=None):
        """
        User pressed Return in entry
        """
        if self.__SelectionCommand:
            apply(self.__SelectionCommand)

    def __SetEntry(self,Text):
        """
        Set our entry to the specified text.
        """
        self.__Entry1.delete(0,END)
        self.__Entry1.insert(0,Text)
        
    def __SetButtonIcon(self):
        """
        Set the button icon to enabled or disabled.
        
        Depending on if ChoiceList is empty or not.
        """    
        if self.__ArrowIcon:
            I = len(self.__ChoiceList) == 0
            self.__Button1.config(image=self.__ArrowIcon[I])

class RadioSelect(Frame):
    """
    A simple vertical radio/checkbutton selector widget.
    
    If buttontype is "radiobutton" then only one button at a time can be selected.
    if buttontype is "checkbutton" then any number of buttons can be selected.
    """
    def __init__(self, Master, **kw):
        """
        """
        ArgList = (('buttontype',None),
                   ('orient','vertical'),
                   ('command',None),
                   ('padx',5),
                   ('pady',5),
                   ('labelpos',None),
                   ('label_text','')
                  )
        #Extract or default arguments we care about 
        for ArgName,DefaultValue in ArgList:
            if kw.has_key(ArgName):
                DefaultValue = kw[ArgName]
                del kw[ArgName]
            exec('self._RadioSelect__%s = DefaultValue'%ArgName)
        apply(Frame.__init__,(self,Master))
        if self.__buttontype not in ('radiobutton','checkbutton'):
            raise Exception, 'Must specify button type of "radiobutton" or "checkbutton" (got %s)'%self.__buttontype
        if self.__orient <> 'vertical':
            raise Exception, 'Only orient "vertical" current supported (got %s)'%self.__orient

        #Look after optional label
        if self.__labelpos <> None:
            X = {'n':TOP, 'e':RIGHT, 's':BOTTOM, 'w':LEFT}
            self.__Label = Label(self,text=self.__label_text)
            PackSide = X[self.__labelpos[0]]
            Anchor = CENTER
            if len(self.__labelpos) > 1:
                Anchor = self.__labelpos[1]
            self.__Label.pack(side=PackSide,anchor=Anchor)
        else:
            self.__Label = None
        
        self.__ControlVar = StringVar()            
        self.__ButtonDict = {}            
        self.__ButtonCount = 0
            
    def add(self,Name,text=None):
        """
        Add a button to our RadioSelect.
        """    
        if text == None:
            text = Name
        if self.__ButtonDict.has_key(Name):
            raise Exception, 'This RadioSelect already has a button named "%s"'%Name
        if self.__buttontype == 'radiobutton':
            New = Radiobutton(self,command=self.__command,text=text,value=Name,variable=self.__ControlVar)
        else:   
            New = CheckbuttonRP(self,command=self.__command,text=text)
            New.Name = Name
        New.pack(anchor=W,padx=self.__padx, pady=self.__pady)
        self.__ButtonDict[self.__ButtonCount] = New
        self.__ButtonDict[Name] = New
        self.__ButtonCount += 1
        return New
        
    def button(self,NameOrIndex):
        """
        Return the specified button.
        """
        return self.__ButtonDict[NameOrIndex]
                    
    def getcurselection(self):
        """
        Return the current selection.
        
        If buttontype is radiobutton then the result is a string giving the name of the
            currently selected button (or None if no button is selected).
        if buttontype is checkbutton then the result is a list of names of currently
            checked buttons    
        """            
        if self.__buttontype == 'radiobutton':
            Result = self.__ControlVar.get()
            if not Result:
                Result = None
        else:
            Result = []
            for J in range(self.__ButtonCount):
                Button = self.__ButtonDict[J]
                if Button.get():
                    Result.append(Button.Name)
        return Result
        
    def invoke(self,NameOrIndex):
        """
        Invoke the command of the specified button.
        """        
        self.__ButtonDict[NameOrIndex].invoke()
        
    def label(self):
        """
        Return the label, or None if there is no label.
        """        
        return self.__Label

    def numbuttons(self):
        """
        Return number of buttons.
        """                
        return self.__ButtonCount
        
class NestedOption:
    """
    Class to help deal with nested option dictionaries
    
    This class behaves somewhat like a dictionary, with extras.
    
    Each item in this class has a key which is the name of the option and a value
        which is a four element list holding:
        o [0] The Type of the option
        o [1] The Default value of the option
        o [2] The Current value of the option
        o [3] The Extra information of the option
        
    For most options Default/Current/Extra are simple values like string, integer or
        None. For certain special types Default is the kind of special component,
        Current is a NestedOption object and Extra is 1 if this nested option
        object is open, 0 if it is closed and -1 if it is hidden.
        
    To access nested options use a key like "MainOption.SubOption".        
    
    To create an option entry use:
    
        w[EntryName] = [Type,Default,Current,Extra]
        
        note that you *can not* change an existing entry using this syntax.
    
        If "Type" is one of the nesting types, then "Current" has to be a NestedOption
        object and "Extra" should be boolean saying if it is to be visible.
    
    To change the "Default", "Current" or "Extra" values use 
    
        W.SetDefault(EntryName,NewDefault)
        W.SetCurrent(EntryName,NewValue)
        W.SetExtra(EntryName,NewExtra)
        
        These work only on options which are not nest nodes.         
        
    You can access an option using:
    
        W[EntryName]
        
        *but* be aware that the result is a *copy*; any changes made to that copy do
        *not* affect the actual option values.    
        
    The w.keys() function is similar to the dictionary keys function but it returns
        a list of keys of all options, including nested ones, 
        using dotted names as necessary to indicate nesting.    
        
    w.Seek(Type) returns a list like dict.items() but only for those items whose
        type matches the specified type. The items returned are *copies*.    

    w.Visible() is like dict.items() but it will return nested items with appropriate
        dotted names but only visible nested items are returned. As with simple
        w[EntryName] access, the data returned is a *copy*.
        
    w.SetVis(EntryName,Value) There are three levels of visibility for nested options:
        o Open The options are both accessable and they are visible.
        o Closed The options are accessable (they still exist) but they are closed
            (meaning that they should not be shown to the user).
        o Consealed The options are not accessable and they should not be shown to the
            user. Consealed options are *not* reported by w.keys().    
    
        A Value of -1 set the visibility to consealed, any other true value sets them
            to open and any value sets them to closed.
    
    w.Copy() Returns a copy of the entire object. 
    
    """
    def __init__(self):
        self.Info = {}
        
    def __getitem__(self,Key):
        Key = Key.split('.')
        Item = self.Info
        for Sub in Key[:-1]:
            Item = Item[Sub][2].Info
        Result = Item[Key[-1]]            
        if Result[0] in NestedOption.SpecialTypes:
            Result = [Result[0], Result[1], Result[1], Result[3]]
        else:
            Result = Result[:]    
        return Result    

    def __setitem__(self,Key,Value):
        if Value[0] in NestedOption.SpecialTypes:
            if not isinstance(Value[2],NestedOption):
                raise Exception, "OptionType %s but Current not an instance of NestedOption"%Value[0]
        else:
            if isinstance(Value[2],NestedOption):
                raise Exception, "OptonType %s can't have NestedOption as Current"        
        Key = Key.split('.')
        Item = self.Info
        for Sub in Key[:-1]:
            Item = Item[Sub][2].Info
        if Item.has_key(Key[-1]):
            raise Exception, "OverwriteError"
        Item[Key[-1]] = Value        

    def __str__(self):
        """
        Return a string representation of this object.
        """
        return '\n'.join(self.__StringWalker(self))
        
    def __StringWalker(self,Object):
        Result = []
        Keys = Object.Info.keys()
        Keys.sort()
        for Key in Keys:
            Type,Default,Current,Extra = Object.Info[Key]
            if Type in NestedOption.SpecialTypes:
                if Extra:
                    V = '<open>'
                else:
                    V = '<closed>'    
                Result.append('%s: %s %s - %s'%(Key,Type,Default,V))
                Temp = self.__StringWalker(Current)
                for T in Temp:
                    Result.append('  .'+T)
            else:
                Result.append('%s: %s %s %s %s'%(Key,Type,Default,Current,Extra))
        return Result        

    def Copy(self):
        """
        Return a copy of the current object.
        """
        Result = NestedOption()
        for Key in self.Info.keys():
            Type,Default,Current,Extra = self.Info[Key]
            if Type in NestedOption.SpecialTypes:
                Result[Key] = [Type,Default,Current.Copy(),Extra]
            else:
                Result[Key] = [Type,Default,Current,Extra]
        return Result            
    
    def SetCurrent(self,Key,Value):
        """
        Set the "Current" field of the specified entry
        """
        Key = Key.split('.')
        Item = self.Info
        for Sub in Key[:-1]:
            Item = Item[Sub][2].Info
        if Item[Key[-1]][0] in NestedOption.SpecialTypes:
            raise Exception, "AccessError"
        Item[Key[-1]][2] = Value
        
    def SetExtra(self,Key,Extra):
        """
        Set the "Extra" field of the specified entry.
        """
        Key = Key.split('.')
        Item = self.Info
        for Sub in Key[:-1]:
            Item = Item[Sub][2].Info
        if Item[Key[-1]][0] in NestedOption.SpecialTypes:
            raise Exception, "AccessError"
        Item[Key[-1]][3] = Extra

    def SetDefault(self,Key,Extra):
        """
        Set the "Default" field of the specified entry.
        """
        Key = Key.split('.')
        Item = self.Info
        for Sub in Key[:-1]:
            Item = Item[Sub][2].Info
        if Item[Key[-1]][0] in NestedOption.SpecialTypes:
            raise Exception, "AccessError"
        Item[Key[-1]][1] = Extra

    def SetVis(self,Key,Vis):
        """
        Set the visibility of the specified option on or off.
        
        The option specified must be a nested option.
        """
        Key = Key.split('.')
        Item = self.Info
        for Sub in Key[:-1]:
            Item = Item[Sub][2].Info
        if not Item[Key[-1]][0] in NestedOption.SpecialTypes:
            raise Exception, "AccessError"
        if Vis == -1:
            Item[Key[-1]][3] = -1    
        elif Vis:    
            Item[Key[-1]][3] = 1
        else:
            Item[Key[-1]][3] = 0    

    def keys(self,SeeAll=False):
        """
        Return all keys as a list.
        
        Normally we only return keys of nested options if they are accessable.
        If "SeeAll" is true we return keys of ALL options.
        """
        return self.__KeyWalker(self.Info,SeeAll)

    def Seek(self,Type):
        """
        Like Dict.items() but only for items whose type matches Type
        """
        return self.__SeekWalker(self.Info,Type)
        
    def Visible(self):
        """
        This is like Dict.items() but only for visible items.
        """
        return self.__VisWalker(self.Info)
        
    def __KeyWalker(self,Dict,SeeAll):
        Result = []
        for Key in Dict.keys():
            Type,Default,Current,Extra = Dict[Key]
            if Type in NestedOption.SpecialTypes and (Extra <> -1 or SeeAll):
                Result.append(Key)
                Temp = self.__KeyWalker(Current.Info,SeeAll)
                for T in Temp:
                    Result.append('%s.%s'%(Key,T))
            else:        
                Result.append(Key)
        return Result        

    def __SeekWalker(self,Dict,SeekType):
        Result = []
        for Key in Dict.keys():
            Type,Default,Current,Extra = Dict[Key]
            if Type in NestedOption.SpecialTypes and Extra <> -1:
                if Type==SeekType:
                    Result.append((Key,[Type,Default,None,Extra]))
                Temp = self.__VisWalker(Current.Info)
                for T in Temp:
                    if T[1][0] == SeekType:
                        FullKey = '%s.%s'%(Key,T[0])
                        Result.append((FullKey,T[1][:]))
            else:            
                if Type==SeekType:
                    Result.append((Key,[Type,Default,None,Extra]))
        return Result        

    def __VisWalker(self,Dict):
        Result = []
        for Key in Dict.keys():
            Type,Default,Current,Extra = Dict[Key]
            if Type in NestedOption.SpecialTypes:
                if Extra <> -1:
                    #Process nested type only if it is accessable
                    Result.append((Key,[Type,Default,None,Extra]))
                    if Extra:
                        Temp = self.__VisWalker(Current.Info)
                        for T in Temp:
                            FullKey = '%s.%s'%(Key,T[0])
                            Result.append((FullKey,T[1][:]))
            else:
                Result.append((Key,Dict[Key][:]))        
        return Result        

class ColorizedText(Text):
    """=d
    A Text widget that knows how to colorize Python code.
    
    """
    def __init__(self, Master=None, **kw):
    
        apply(Text.__init__,(self,Master),kw)
        self.Scheme = Cfg.Info['Schemes'][Cfg.Info['SchemeCurName']]
        self.TextWidget = self
        self.TextWidget.bind('<KeyRelease>',self.on_KeyRelease)
        self.TextWidget.bind('<KeyPress>',self.on_KeyPress)
        self.CibSt = Rph.Enumerated('NeverStarted Running Stopped MustRegroup Done')
        self.CibState = self.CibSt.NeverStarted
        self.CibCommand = []
        self.ColorizeAfterId = None
    
        #Our colorizer instance
        self.Colorizer = Colorize()
        #Here we set the colors that are associated with the tags used for colorizing.
        #   The tags are named "color_X" where X is the color specification that was
        #   supplied in the config file, eg "#FF0000".
        ColorList = [] #Just so we don't create duplicate tags
        for Element,Color in self.Scheme['Colors'].items():
            if not Color in ColorList:
                ColorList.append(Color)
                TagName = self.ColorToTagName(Color)
                if Element == 'background':
                    pass
                elif Element == 'bgldt':
                    self.TextWidget.tag_config(Element,background=Color)
                else:    
                    self.TextWidget.tag_config(TagName,foreground=Color)
        del ColorList        
        
        #The user is allowed to look but not modify systext. When a key goes down we check
        #    to see if it is one which could hurt systext and if so we disallow it. In order
        #    to accomplish this we need to know which keys to disallow. "BackSpace", 
        #    "Delete" and "Return" are not user changeable and are always disallowed. To 
        #    find the user defined keys which have been bound to disallowed actions, for
        #    example "Cut", we have to root through the scheme.
        self.DisallowedList = ['BackSpace','Delete','Return']
        BadActions = 'Cut CutAppend Indent IndentBlock Outdent OutdentBlock Paste PasteFile'.split()
        for ActionName, EventString in self.Scheme['Actions']:
            if ActionName in BadActions:
                self.DisallowedList.append(EventString[1:-1])

    #---------------------------------------------------------------------------
    # Published methods
    #---------------------------------------------------------------------------

    def Gather(self):
        """
        Create an object that represents the text of the widget.
        
        The result is a dictionary:
        
            o "['Cursor']" The current location of the insert cursor.
            o "['Sha']" A 40 byte string containing the "sha" hex digest of the text.
            o "['Text']" A list of text chunks, alternating systext, usertext. If the
                first chunk is empty this indicates that the first character in the
                text is usertext.
            o "['Version']" An integer identifying the format of the gathered
                information. If we ever change the format in the future, the version
                number will aid implementing backwards compatability.
        """
        Temp = self.tag_ranges('bgldt')
        LineList = []
        if Temp[0] <> '1.0':
            #We don't start with systext, so the first clump is empty
            LineList.append('')
            LineList.append(self.get('1.0',Temp[0]))
        J = 0
        #Accumulate text chunks up to the last one of systext
        while J+1 < len(Temp):
            LineList.append(self.get(Temp[J],Temp[J+1]))
            J += 1
        #Look after usertext past the last systext. The Tk Text widget has a habit of
        #    giving us an extranious newline at the end. If you don't strip them then
        #    every load/save cycle creates an extra one. That explains the rstrip.
        if Temp[-1] <> self.index(END):
            LastText = self.get(Temp[-1],self.index(END)).rstrip()
            LineList.append(LastText)    
        Hash = sha.new()
        for L in LineList:
            Hash.update(L)
        Result = {'Text':LineList,'Version':0,'Sha':Hash.hexdigest()
            ,'Cursor':self.index(INSERT)}
        return Result
                
    def ColorizeVisible(self):
        """
        Colorize any text visible on the screen
        """
        First,Last = self.Visible()        
        Range = self.tag_ranges('C')
        J = 0
        while J < len(Range):
            ColFrom = int(float(Range[J]))
            ColTo = int(float(Range[J+1]))
            if First >= ColFrom and Last <= ColTo:
                #Visible lines are totally within a colored area; no coloring needed.
                return
            if First < ColFrom:
                #Visible lines are prior to the current colored area by were not
                #    noted previously as all colored; that means some or all
                #    need to be colored.
                break
            J += 2    
        self.CommandIssue('goto','ColorizedText.ColorizeVisible',First)

    def CommandIssue(self,Command,Requestor,Argument=None):
        """
        Send Command and Argument to background colorizer
        """
        ##D('CommandIssue(%s) Command=%s Requestor=%s Arg=%s'%(self,Command,Requestor,Argument))
        self.CibCommand[0:0] = [(Command,Argument,Requestor)]

    def Visible(self):
        """
        Return a tuple showing line numbers of first and last lines visible.
        """
        #First = self.IndexToList('@0,0')[0]
        First = int(float(self.TextWidget.index('@0,0')))
        H = self.TextWidget.winfo_height()
        #Last = self.IndexToList('@0,%s'%H)[0]
        Last = int(float(self.TextWidget.index('@0,%s'%H)))
        return (First,Last)

    def SystextReplace(self,ID,NewText):
        """
        Replace a chunk of look-don't-touch system text with specified text.
        
        "ID" is a string of text which should occur somewhere in the chunk of systext
            to be replaced. This string should be unique to the chunk being replaced.
            This string is simply used to identify the chunk to be replace. Note
            that the entire chunk of systext is replaced, not just that portion that
            matches ID.
            
        "NewText" is the text which replaces the entire chunk of existing systext.    
        
        We raise an error if no match for ID is found.
        """
        #Get a list of all systext ranges
        Ranges = self.TextWidget.tag_ranges('bgldt')
        #Search for desired chunk
        I = 0
        while 1:
            if I+2 > len(Ranges):
                raise Exception, 'No SysText chunk containing "%s" was found.'%ID
            R = self.search(ID,Ranges[I],stopindex=Ranges[I+1])
            if R <> '':
                #We have a match
                break
            I += 2
        #Delete the found chunk
        self.delete(Ranges[I],Ranges[I+1],PowerPill=1)
        #Insert the new text
        self.insert(Ranges[I],NewText,'bgldt')

    def SystextFind(self,ID,Type='Exact'):
        """
        Attempt to find a chunk of systext which contains specific text.

        "ID" is a string of text which should occur somewhere in the chunk of systext
            you are looking for and should be unique to that chunk.
            
        "Type" should be "Start", "Exact" or "End". If omitted it defaults to "Exact".    
        
        If no match is found the result is an empty string.
        
        If a match is found, then the result varies depending on "Type"
        
        o "Start": The result is the index of the start of the block of systext which
            contains the matching text.
        o "Exact": The result is the index of the start of the systext which matches ID.
        o "End": The result is the index of the location after the block of systext
            which contains the matching text.
        
            
        If found, the result is the index to the start of the systext which matches ID.
        If not found, the result is an empty string.    
        """
        assert Type in ('Start','Exact','End')
        #Get a list of all systext ranges
        Ranges = self.TextWidget.tag_ranges('bgldt')
        #Search for desired chunk
        I = 0
        while 1:
            if I+2 > len(Ranges):
                return ''
            R = self.search(ID,Ranges[I],stopindex=Ranges[I+1])
            if R <> '':
                #We have a match
                if Type == 'Start':
                    R = Ranges[I]
                elif Type == 'End':
                    R = Ranges[I+1]
                return R
            I += 2

    def HandlerSeekAt(self,TextIndex):
        """
        Seek name of hander at specified TextIndex.
        
        If TextIndex (which is an INDEX as defined by the Tkinter Text widget, not an ordinary
            numeric index) is inside the systext of an event handler then we return the name
            of the handler, otherwise we return None.
        """
        Info = self.HandlerNameList(Verbose=True)
        for HandlerName,SystextStart,SystextEnd in Info:
            if self.compare(TextIndex,'>=',SystextStart) and self.compare(TextIndex,'<=',SystextEnd):
                #Passed INDEX is within this handlers systext
                return HandlerName
        return None        

    def HandlerNameList(self,Verbose=False):
        """
        Return a list of all the event-handlers in our text.
        
        If verbose is false the result is a list of strings.
        
        If verbose is true then the result is a list of tuples:
            [0] Name of handler
            [1] Index of start of handler systext
            [2] Index of end of handler systext
        """
        Ranges = self.TextWidget.tag_ranges('bgldt')
        #4 chunks of systext are the minimum we expect
        assert len(Ranges) >= 8
        #The first 3 chunks and the last chunk are not event handlers
        Ranges = Ranges[6:-2]
        I = 0
        Result = []
        while I < len(Ranges):
            Text = self.get(Ranges[I],Ranges[I+1]).lstrip()
            assert Text[:4] == 'def '
            T = Text.find('(')
            assert T <> -1
            HandlerName = Text[4:T]
            if Verbose:
                Result.append((HandlerName,Ranges[I],Ranges[I+1]))
            else:
                Result.append(HandlerName)
            I += 2
        return Result    

    def SystextFindLast(self):
        """
        Return the index following the last chuck of systext.
        """
        return self.TextWidget.tag_ranges('bgldt')[-1]

    def SystextFetchByIndex(self,I):
        """
        Return the Nth systext chunk.
        
        The result is a 3-tuple giving:
        o "[0]" The from index of the chunk
        o "[1]" The to index of the chunk
        o "[2]" The text of the chunk
        
        It is an error to ask for a non existent chunk.
        """
        I = I*2
        From, To = self.TextWidget.tag_ranges('bgldt')[I:I+2]
        Text = self.TextWidget.get(From,To)
        return (From,To,Text)

    def ChunkCut(self,Index):
        """
        Cut and return a chunk of sys/user text.
        
        "I" Is the index, which must be the start of an area of systext.
        
        The result is a two element list. The first element is the sys text, the
            second element is the user text (which runs as far as the next systext
            or end-of-text whichever comes first).
        """
        Ranges = list(self.tag_ranges('bgldt'))
        J = Ranges.index(Index)
        Sys = self.get(Ranges[J],Ranges[J+1])
        if J+2 >= len(Ranges):
            To = 'end'
        else:
            To = Ranges[J+2]
        User = self.get(Ranges[J+1],To)
        self.delete(Ranges[J],To,PowerPill=1)
        return [Sys,User]        

    def Scatter(self,Text):
        """
        Replace existing text with supplied text.
        
        "Text" is a dictionary as returned by "Gather".
        """
        self.delete('1.0',END,PowerPill=1)
        Tag = 'bgldt'
        for T in Text['Text']:
            if len(T) > 0:
                self.insert(END,T,Tag)
            if Tag == 'bgldt':
                Tag = ''
            else:
                Tag = 'bgldt'
        self.mark_set(INSERT,self.IndexToLeft(Text['Cursor']))
        self.see(INSERT)
        
    def SystextInSel(self):
        """
        Does the currently selected area include any systext?
        
        Result is 1 if so, else 0.
        """
        try:
            SelFrom = self.index(SEL_FIRST)
            SelTo = self.index(SEL_LAST)
        except TclError:
            #There is no selected area
            return False
        return self.SystextInRegion(SelFrom,SelTo)
            
    def SystextInRegion(self,From,To):
        """
        Does the specified from/to region include any systext?
        
        Result is 1 if so, else 0.
        """
        Ranges = list(self.tag_ranges('bgldt'))
        ##D('SystextInRegion From=%s To=%s Ranges=%s'%(From,To,Ranges))
        #Step over the from-to pairs looking for conflicts
        J = 0
        while J < len(Ranges):
            RangeFrom = Ranges[J]
            RangeTo = Ranges[J+1]
            if self.compare(From,'>=',RangeFrom) and self.compare(From,'<',RangeTo):
                #Start of region is inside systext
                ##D('RangeFrom=%s RangeTo=%s Start of region inside systext'%(RangeFrom,RangeTo))
                return True
            if self.compare(To,'>',RangeFrom) and self.compare(To,'<=',RangeTo):
                #End of region is inside systext
                ##D('RangeFrom=%s RangeTo=%s End of region is inside systext'%(RangeFrom,RangeTo))
                return True
            if self.compare(RangeFrom,'>',From) and self.compare(RangeTo,'<',To):
                #Systext range is totally within our region.
                ##D('RangeFrom=%s RangeTo=%s Systext chunk totally within region'%(RangeFrom,RangeTo))
                return True    
            J += 2    
        return False        

    def CursorInSystext(self):
        """
        Is the cursor currently in a systext area?
        
        Result is 1 if so, else 0.
        """
        return 'bgldt' in self.TextWidget.tag_names(INSERT)

    def CurrentInSystext(self):
        """
        Is the character at the mouse currently in a systext area?
        
        Result is 1 if so, else 0.
        """
        return 'bgldt' in self.TextWidget.tag_names(CURRENT)
        
    def SystextBookendsRegion(self,From,To):
        """
        Return True if there is systext immediately before and after a region.
        """
        return 'bgldt' in self.TextWidget.tag_names(From+'-1c') \
        and 'bgldt' in self.TextWidget.tag_names(To)
        
    #---------------------------------------------------------------------------
    # Overridden methods
    #---------------------------------------------------------------------------

    def delete(self,index1,index2=None,PowerPill=0):
        """
        Don't allow deletion of look-don't-touch systext unless "PowerPill" is true
        """
        #If index2 is "None" then Text.delete only deletes one character, however
        #    Text.tag_nextrange checks all the way to the end if index2 is "None".
        #    Therefore we generate To, for use with tag_nextrange, which matches
        #    the way delete works.
        From = self.TextWidget.index(index1)
        if index2 == None:
            To = From
        else:    
            To = self.TextWidget.index(index2)
        if not PowerPill:
            Next = self.TextWidget.tag_nextrange('bgldt',From,To)
            if len(Next) <> 0:
                return
        Text.delete(self,index1,index2)    

    def insert(self,index,text,tags=None,ProgressFunction=None):
        """
        Insert text into the widget.
        
        Just like Text.insert *but* if "ProgressFunctions" is specified then
            we call it periodically (with a percentage number from 0..100 as the
            argument). At insert time we have to tag each line with a Q3
            parity marker and on multi-thousand line inserts this can take
            a few seconds. The "ProgressFunction" facility allows you to
            put up and maintain a progress indicator so the user doesn't
            think we've dropped dead.
        """
        InsertPoint = int(float(self.index(index)))
        Text.insert(self,index,text,tags)
        Count = text.count('\n')
        #We have to do some fudging because of the way the Tk END index works; it often
        #    results in a value one greater than you would otherwise expect. On an empty
        #    text widget END is "2.0". But if you add a single line to the END of an empty 
        #    Text it goes in as line "1". In general END produces a result one higher than
        #    might be expected.
        Fudge = index == END
        self.TextQuoteParityTag(InsertPoint-Fudge,InsertPoint+Count+Fudge,ProgressFunction)
        if Count == 0:
            #Text was inserted within a single line, so just recolorize that line.
            #We need to pass the opening Q3 parity to the colorizer
            Q3Parity = self.LineQuoteParityCheck(InsertPoint)
            self.LineColorize(InsertPoint,Q3Parity)
            return
        if self.CibState == self.CibSt.NeverStarted:
            #If the colorizer had never run then start from scratch.
            self.CibInit()
        elif self.CibState == self.CibSt.Done:
            self.CibState = self.CibSt.MustRegroup
            self.CibRegroupTarget = InsertPoint-1
        elif self.CibState in (self.CibSt.Running, self.CibSt.Stopped, self.CibSt.MustRegroup):
            #no action required
            pass
        else:
            raise Exception, "Unknown CibState: "+self.CibState    
        ##D('End of Insert. History follows\n%s'%'\n'.join(History))
        ##D('CibState=%s'%self.CibSt.Decode(self.CibState))

    #---------------------------------------------------------------------------
    # Event handlers
    #---------------------------------------------------------------------------

    def on_ScrollbarButton1Up():
        """
        User let go of scroll bar
        """
        self.ColorizeVisible()    

    def on_KeyPress(self,Event):
        #D('keysym=%s state=%s'%(Event.keysym,Event.state))
        if Event.keysym in ('Delete','BackSpace'):
            #Must note area being deleted for use once key is released
            try:
                From = self.TextWidget.index(SEL_FIRST)
                To = self.TextWidget.index(SEL_LAST)
                #Don't allow deletion of look-don't-touch text
                if 'bgldt' in self.TextWidget.tag_names(From):
                    #Selection starts in an LDT area
                    self.DeletionFromTo = None
                    return 'break'
                Next = self.TextWidget.tag_nextrange('bgldt',From,To)
                if len(Next) <> 0 :
                    #Selection moves into an LDT area
                    self.DeletionFromTo = None
                    return 'break'
            except TclError:
                #There is no selection    
                if Event.keysym == 'Delete':
                    if 'bgldt' in self.TextWidget.tag_names(INSERT):
                        #Were in look-don't-touch text
                        self.DeletionFromTo = None
                        return 'break'
                    From = self.TextWidget.index(INSERT)
                    To = self.TextWidget.index(From+'+1c')
                else:
                    #Backspace; check for look-don't-touch area
                    if 'bgldt' in self.TextWidget.tag_names(INSERT+'-1c'):
                        #AGG
                        self.DeletionFromTo = None
                        return 'break'
                    To = self.TextWidget.index(INSERT)
                    From = self.TextWidget.index(INSERT+'-1c')
            #Disallow if the From-To region would delete everything between two
            #    clumps of look-don't-touch text    
            if self.SystextBookendsRegion(From,To):
                #if 'bgldt' in self.TextWidget.tag_names(From+'-1c') \
                #and 'bgldt' in self.TextWidget.tag_names(To)    :
                self.DeletionFromTo = None
                return 'break'
            self.DeletionFromTo = (From,To)
        else:
            #The key is not delete or backspace.
            #At this point we need to disallow a key which would hurt systext. We 
            #    therefore check to see if the cursor is in systext or if the
            #    selected region (if any) includes systext.
            ##D('keysym=%s'%Event.keysym)
            if 'bgldt' in self.TextWidget.tag_names(INSERT) or self.SystextInSel():
                #Were over or have selected systext
                if (len(Event.keysym)==1           #a simple graphic like 'a'
                or Xdict.has_key(Event.keysym)     #a graphic with a verbose name like "minus"
                or Event.keysym=='space'           #space isn't in Xdict but needs to be disallowed
                or Event.keysym in self.DisallowedList): #a key bound to an action that 
                                                        #would hurt systext
                    #You aren't allowed this key or action inside systext
                    ##D("Returning break")
                    return 'break'
            if len(Event.char) == 1 and Event.char >= ' ' and Event.char <= '~':
                #Standard ascii graphic. By inserting it ourselves the character gets
                #    colorized with no visible delay.
                self.insert(INSERT,Event.char)        
                return 'break'

    def on_KeyRelease(self,Event):
        """
        Colorization happens here.
        """
        if Event.keysym in ('Alt_L','Alt_R','Caps_Lock','Control_L','Control_R','Shift_L','Shift_R'):
            #ignore keys that for sure don't change things
            return
        ##D('on_KeyRelease keysym=%s'%Event.keysym)
        if Event.keysym in ('Down','Left','Next','Prior','Right','Up'):
            C = int(float(self.TextWidget.index(INSERT)))
            #We call ColorizeFromTo on the current line, because that checks for and
            #    recolorizes the line if it's Q3 parity differs from the parity at
            #    colorization time.
            #self.ColorizeFromTo(C,C)
            #We call ColorizeVisible to make sure all lines visible have been
            #    colorized. This does NOT recolorize the lines if their Q3 parity
            #    is wrong, since it does not even look at Q3 parity.
            #self.ColorizeVisible()
            #If you don't call update_idletasks here, then the cursor tends to vanish if the
            #    user moves up/down by many lines.
            self.TextWidget.update_idletasks()
            #At this point we have a bit of a dilema. On one hand, having moved to a new line
            #    we would like to make sure the Q3 colorization of that line is up to date and
            #    we sould like to make sure that all visible lines on the screen are colorized.
            #    We can do that, but it chews up a fair bit of processor time. If the user is
            #    simply plodding up or down one at a time, it works fine. If they ard holding
            #    down on an arrow key so as to zip up/down by many lines then we can't do the
            #    processing as fast as the keystrokes come in. We attempt to solve this by
            #    setting an "after" with a modest delay. If another motion key arrives before
            #    the "after" happens, then we move the cursor and set a new after. Thus if the
            #    keystrokes are arriving rapidly we don't mess around with colorizing. If they
            #    user is entering keystrokes slowly, or at the end of a bunch of rapid keystrokes,
            #    then the "after" times out and we attend to colorization at that time.
            if self.ColorizeAfterId <> None:
                self.TextWidget.after_cancel(self.ColorizeAfterId)
            self.ColorizeAfterId = self.TextWidget.after(100,self.ColorizeAfter)
            return
        if Event.keysym in ('Delete','Backspace'):
            #The from/to extent was noted when the key was pressed. Now tell the background
            #    colorizer about it.
            if self.DeletionFromTo == None:
                #naughty naughty - they tried to delete systext
                return
            From,To = self.DeletionFromTo
            self.DeletionFromTo = None    
        if Event.keysym == 'Return':
            #A return may have broken a line into two pieces.
            #Recolor the previous line
            PrevLine = int(float(self.TextWidget.index(INSERT)))-1
            Flag = self.LineColorize(PrevLine,Flag=self.LineQuoteParityCheck(PrevLine))
            #We save this as an aid for outside users
            self.RecentFlagInfo = {'Line':PrevLine, 'Flag':Flag}
            #Update the parity tag on the previous line
            self.TextQuoteParityTag(PrevLine)
        #Recolor the current line since it may have changed    
        CurrentLine = int(float(self.TextWidget.index(INSERT)))
        self.LineColorize(CurrentLine,Flag=self.LineQuoteParityCheck(CurrentLine))
        #Update the parity tag on the current line
        self.TextQuoteParityTag(CurrentLine)
        self.TextWidget.update_idletasks()

    #---------------------------------------------------------------------------
    # Everything else
    #---------------------------------------------------------------------------

    def IndexToLeft(self,Index):
        """
        Revise an index so it referrs to the left side of a line.
        
        For example given an index "29.17" we return "29.0"
        """
        return '%s.0'%self.index(Index).split('.')[0]

    def ColorizeAfter(self):
        self.ColorizeAfterId = None
        C = int(float(self.TextWidget.index(INSERT)))
        #We call ColorizeFromTo on the current line, because that checks for and
        #    recolorizes the line if it's Q3 parity differs from the parity at
        #    colorization time.
        self.ColorizeFromTo(C,C)
        #We call ColorizeVisible to make sure all lines visible have been
        #    colorized. This does NOT recolorize the lines if their Q3 parity
        #    is wrong, since it does not even look at Q3 parity.
        self.ColorizeVisible()

    def ColorizeFromTo(self,From,To,Flag=None,ShowOnGo=0,Force=0):    
        """
        Colorize lines in the specified range.
        
        "Flag" gives the Q3 state (0..3) at the start of the first line. If "Flag" is
            "None" we fetch the state ourselves.
        "ShowOnGo" if true we call update_idletasks every few lines so the screen
            follows our colorizing.    

        The result is the Q3 color state at the end of colorizing the last requested
            line.
        
        Note: This routine will NOT re-colorize a line unless it's Q3 status has changed
            since the last time it was colorized or "Force" is True.
        """
        FlagIn = Flag
        if Flag == None:
            State = self.LineQuoteParityCheck(From)
        else:
            State = Flag    
        # State is:
        #    0 No Q3 issues
        #    1 Q3d in force at start of line
        #    2 Q3s cooked in force at start of line
        #    3 Q3s raw in force at start of line
        for Line in range(From,To+1):
            #Fetch the special tags for this line
            Color = 1
            if not Force:
                #Don't colorize unless we need to
                TagList = self.TextWidget.tag_names('%s.end'%Line)
                Q3Tag = None
                for Tag in TagList:
                    if Tag[:9] == 'ColorFlag':
                        #This line is already colorized
                        Flag = int(Tag[9:])
                        if Flag == State:
                            #And the Q3 parity at colorization matches current Q3 parity
                            Color = 0
                            break
                    elif Tag[:3] == 'Q3-':
                        #This line has a Q3 parity transformation tag
                        Q3Tag = Tag        
                    else:
                        #This line needs to be colorized
                        pass
            if Color == 0:
                #The colorization of this line is up to date Q3 parity-wise so we will not
                #    re-color it. We do, however, need to compute what the Q3 state will be
                #    at the end of the line. 
                if Q3Tag <> None:
                    #Then this line can possibly affect Q3 state
                    State = int(Q3Tag[State+3])
            else:
                #Either this line has never been colorized or it was colorized but the Q3
                #    parity has changed since it was colorized. In either case it needs to
                #    be recolorized.                        
                State = self.LineColorize(Line,State)[0]
                if ShowOnGo and not Line % 3:
                    self.TextWidget.update_idletasks()
        return State    

    def CibInit(self,TargetLine=1):
        """
        Start the background colorizer from scratch at a specific line.
        
        In addition to being useful at startup, this is also useful if the user 
            has changed Q3 status and a bunch of lines need to be recolorized. 
            
        Target must be a line number from 1 up.    
        """
        assert type(TargetLine) == type(0)
        assert TargetLine >= 1
        if self.TextWidget.index(END) == '2.0':
            #There is no text; nothing to do
            return
        #Kill any pending background colorizer 'after'    
        try:
            self.TextWidget.after_cancel(self.CibAfterID)
        except:
            pass
        #Make sure the first line is already colorized    
        self.ColorizeFromTo(1,1)
        #this is our cue to start up.
        self.CibCommand = []
        self.CibState = self.CibSt.MustRegroup
        self.CibRegroupTarget = TargetLine
        self.CibAfterID = self.TextWidget.after(1,self.ColorizeInBackground,1)    

    def ColorizeInBackground(self,LineNumber):
        """
        The background colorizer. "Cib" to it's friends.

        Use the routine CibInit to start or restart the colorizer.        
        
        While it is running, you send it commands by putting them in "self.CibCommand".
        The commands are:
          o "stop" The colorizer suspends operation but continues waiting for commands.
          o "resume" The colorizer resumes operation if stopped.
          o "goto: The colorizer stops colorizing where it is and begins colorizing
              at the line specified by "self.CibData". If the specified line is in an 
              already colored area then colorizing resumes at the first non-colorized 
              line following the specified line. If there are no non-colorized lines 
              following the specified line then the colorizer resumes colorizing with 
              the very first not yet colorized line.
        """
        #These are default values for Delay and NextLine for use by the "after" just before we
        #    exit. Set different values if you need something other than the default.    
        Delay = 1
        ##D('Cib State=%s LineNumber=%s Command=%s'%(self.CibSt.Decode(self.CibState)
        ##    ,LineNumber,self.CibCommand))
        NextLine = LineNumber + 1    
    
        if self.CibState == self.CibSt.Running:
            #
            # We are running
            #            
            if self.CibCommand == []:    
                #No command - were just chugging along.
                #Look to see if we are at end-of-text
                LastLine = int(float(self.TextWidget.index(END)))
                ##D('Cib: LineNumber=%s LastLine=%s'%(LineNumber,LastLine))
                if LineNumber > LastLine:
                    ##D('----- end of text -----')
                    #We are at end-of-text
                    #Regroup so we go looking for other areas to color
                    self.CibState = self.CibSt.MustRegroup
                    #We have no pet target; let the regrouper pick
                    self.CibRegroupTarget = None
                else:
                    #We are not at end-of-text; Colorize one line.
                    self.CibPreviousQ3State = self.ColorizeFromTo(LineNumber,LineNumber
                        ,Flag=self.CibPreviousQ3State,Force=True)
                    if 0 == NextLine%100:
                        #Every 100 lines we re-sync with the official Q3 state
                        self.CibQ3PreviousState = self.LineQuoteParityCheck(NextLine)
                        ##D(NextLine)
                    #NextLine is needed by CibNoteDeletion    
                    #self.CibNextLine = NextLine
                    if "C" in self.tag_names('%s.end'%NextLine):
                        ##D('Need regroup NextLine=%s tags=%s'%(NextLine,self.tag_names('%s.end'%NextLine)))
                        #The next line is already colored; must regroup
                        self.CibState = self.CibSt.MustRegroup
                        self.CibRegroupTarget = NextLine
            else:
                #we have a command
                Command, Data, Who = self.CibCommand.pop()
                ##D('Processing command=%s Data=%s Who=%s Stack=%s'%(Command,Data,Who,self.CibCommand))
                if Command == 'stop':
                    self.CibState = self.CibSt.Stopped
                    self.CibRegroupTarget = None
                    Delay = 250
                elif Command == 'goto':
                    self.CibState = self.CibSt.MustRegroup
                    self.CibRegroupTarget = Data    
                    NextLine = 0
                    ##D('Requesting regroup, target=%s'%self.CibRegroupTarget)
                elif Command == 'resume':
                    #Were already running; no action necessary; retain same line
                    NextLine = LineNumber
                else:
                    raise Exception, "Unknown Cib command: "+Command
        elif self.CibState in (self.CibSt.Stopped,self.CibSt.Done) :
            #
            # Stopped or Done
            #       
            NextLine -= 1
            if self.CibCommand == []:
                #no command, keep idling
                Delay = 1000
            else:   
                #There is a command 
                Command, Data, Who = self.CibCommand.pop()     
                ##D('Processing command=%s Data=%s Who=%s Stack=%s'%(Command,Data,Who,self.CibCommand))
                if Command == 'resume':
                    self.CibState = self.CibSt.MustRegroup
                elif Command == 'stop':
                    #Note state and carry on
                    self.CibState = self.CibSt.Stopped    
                elif Command == 'goto':
                    #goto is ignored while we are stopped
                    pass
                else:
                    raise Exception, "Unknown Cib command: "+Command        
        elif self.CibState == self.CibSt.MustRegroup:
            #
            # Regroup
            #
            Target = self.CibRegroupTarget
            Range = self.tag_ranges('C')
            ##D('Regrouping Target=%s End=%s Range=%s'%(Target, self.index(END), Range))
            if len(Range) == 2  \
            and Range[0] == self.index('1.0') \
            and Range[1] == self.index(END):
                #we are done
                ##D('Were done')
                self.CibState = self.CibSt.Done
                Delay = 250
            else:
                ##D('Not done')
                #We are not done; continue with the regroup.
                if Target == None:
                    #Start with the first uncolored line
                    if len(Range) == 0:
                        NextLine = 0
                    else:    
                        NextLine = int(float(Range[1]))
                else:
                    #Start with the first uncolored line following target
                    J = 0
                    while J < len(Range):
                        #print 'Range[J]=',str(Range[J])
                        if Target < int(float(Range[J])):
                            ##D('J=%s Target is in an uncolored area; start with it'%J)
                            NextLine = Target
                            break
                        if Target <= int(float(Range[J+1])):
                            ##D('J=%s Target is in an already colored area'%J)
                            if Range[J+1] == self.index(END):    
                                #Everything from target to the end is already colored;
                                #    Start with first uncolored area
                                ##D('Target to end colored; starting with first uncolored')
                                NextLine = int(float(Range[1]))
                            else:
                                #There is uncolored text after the target; start with the
                                #    first uncolored area
                                ##D('Starting with uncolored text following target')
                                NextLine = int(float(Range[J+1]))
                            break
                        J += 2
                    else:
                        #Either nothing is colored or Target is in an uncolored region after last 
                        #    colored region. In either case start with target.
                        NextLine= Target
                self.CibState = self.CibSt.Running
            self.CibRegroupTarget = None
            #Regrouping toasts the Q3 state
            self.CibPreviousQ3State = None
            ##D('EndRegroup. NextLine=%s Range=%s'%(NextLine,str(Range)))
        #
        # Wrap up and go home
        #
        
        #Sanity check 
        if NextLine < 0:
            raise Exception, 'NextLine unexpectedly less than zero: %s'%NextLine
        self.CibAfterID = self.TextWidget.after(Delay,self.ColorizeInBackground,NextLine)    
       
    def LineColorize(self,Line,Flag=0):
        """
        Colorize the specified line.
        
        "Flag" is an integer as returned by Colorize.
        
        The result is the result returned by Colorize on this line.
        
        Having colorized the line, we put a tag on the end of the it of the form "ColorFlag<n>"
            where "<n>" is the value of the "Flag" paramater. This flag says "here's what the
            Q3 parity was at the start of this line the last time it was colorized". This
            is useful when, at some later time, we revisit this line and want to know if it
            needs to be recolorized because the Q3 parity has changed. By comparing the
            "ColorFlag" on a line with the current Q3 parity (which depends on all lines
            previous) you can find out if a line needs to be recolorized.
            
        We also put a "C" tag on the line to indicate that it has been colorized.    
        """        
        Text = self.TextWidget.get('%s.0'%Line,'%s.end'%Line)
        if Flag == 1:
            #This line opens with Q3d in force. If the line does not change this, then we can
            #    simply render the entire line in the comment color without wasting time
            #    calling the colorizer.
            NewFlag = Flag
            EndTags = self.TextWidget.tag_names('%s.end'%Line)
            for Tag in EndTags:
                if Tag[:3] == 'Q3-':
                    #This is a Q3 translation tag
                    NewFlag = Tag[Flag+3]
                    break
            if NewFlag == 1:
                #Q3d is still in force at end-of-line
                ColorInfo = (Flag,[{'Class':'comment', 'Start':0, 'Length':len(Text)
                    ,'Color':self.Scheme['Colors']['comment']}],0)
            else:
                #Q3d not in force at end of line; must colorize    
                ColorInfo = self.Colorizer(Text,Flag)
        else:    
            #This line does not open with Q3d in force
            ColorInfo = self.Colorizer(Text,Flag)
        
        #Toast all existing color tags on the line
        StartIndex = '%s.0'%Line
        EndIndex = '%s.end'%Line
        for Color in self.Scheme['Colors'].values():
            self.TextWidget.tag_remove('Color_'+Color, StartIndex,EndIndex)        

        for Dict in ColorInfo[1]:
            Start = Dict['Start']
            End = Start + Dict['Length']
            self.TextWidget.tag_add('Color_'+Dict['Color'],'%s.%s'%(Line,Start),'%s.%s'%(Line,End))

        #Update ColorFlag tag at end of line
        ColorTagIndex = '%s.end'%Line
        TagList = self.TextWidget.tag_names(ColorTagIndex)
        for Tag in TagList:
            #Check for existing ColorFlag tag
            if Tag[:9] == 'ColorFlag':
                TagColorState = int(Tag[9:])
                if TagColorState <> Flag:
                    #ColorFlag has changed; must update; toast the old tag
                    self.TextWidget.tag_remove(Tag,ColorTagIndex)
                    #Place the new tag
                    NewColorStateTag = 'ColorFlag%s'%Flag
                    self.TextWidget.tag_add(NewColorStateTag,ColorTagIndex)
                    break
        else:
            #No previous ColorFlag tag; create new one
            NewColorStateTag = 'ColorFlag%s'%Flag
            self.TextWidget.tag_add(NewColorStateTag,ColorTagIndex)
        #Mark the line colored
        self.TextWidget.tag_add("C",'%s.0'%Line,ColorTagIndex+'+1c')    
        return ColorInfo

    def LineDump(self,LineNumber):
        """
        Dump a line and all its tags.
        """
        J = 0
        Chr = None
        while Chr <> 'eol':
            #Index = self.ListToIndex([LineNumber,J])
            Index = '%s.%s'%(LineNumber,J)
            Chr = self.TextWidget.get(Index)
            if Chr == '\n':
                Chr = 'eol'
            Tags = self.TextWidget.tag_names(Index)
            print '%3s %s'%(Chr,Tags)
            J += 1

    def TextQuoteParityTag(self,LineNumber=None,LastLine=None,ProgressFunction=None):
        """
        Tag all line(s) which have one or more instances of triple quotes.
        
        If "LineNumber" is None, we tag *all* lines, otherwise we tag just the
            lines mentioned. If "LastLine" is omitted then only the one line
            is tagged. 
            
        If "ProgressFunction" isn't "None" then it should be a callable object. We call
            it every couple of hundred lines with the number of showing percentage of
            lines tagged. This allows for updating a progress bar while we tag a large
            number of lines,.

        If were doing just a single line then we remove any existing Q3 tags from that
            line first. If we are doing 2 or more lines then it is assumed that these
            are new lines which have no Q3 tags.
        
        If a line contains any instance of triple quotes then we process it. After processing
            the line will have two Q3 parity related tag:
            o A "Q3" tag which simply allows us to quickly identify this as a line which can
              affect Q3 parity.
            o A translation tag of the form "Q3-xxxx" where each "x" will be one of "0123".
              The digit in each position indicates what effect this line will have on Q3
              parity based on differing starting premises. Left to right the premises are:
                o No Q3 in effect at start of line
                o Q3d in effect at start of line
                o Q3s cooked in effect at start of line
                o Q3s raw in effect at end of line
              The four possible digits in turn indicate what the Q3 status will be at the end
                of the line for the given premis:
                o 0 = No Q3 in effect at end of line
                o 1 = Q3d in effect at end of line
                o 2 = Q3s cooked in effect at end of line
                o 3 = Q3s raw in effect at end of line    
        """
        if LineNumber == None:
            #Were doing everything
            LastLine = int(float(self.TextWidget.index(END)))    
            Line = 1
        else:
            #Were not doing everything
            if LastLine == None:
                #apparently just one line
                LastLine = Line = LineNumber 
                #Delete any existing quote parity tags on that one line
                self.TextWidget.tag_remove('Q3','%s.end'%Line)
                Tags = self.TextWidget.tag_names('%s.end'%Line)
                for Tag in Tags:
                    if Tag[:3] == 'Q3-':
                        self.TextWidget.tag_remove(Tag,'%s.end'%Line)
            else:
                #a specifed number of lines
                assert LastLine >= LineNumber
                Line = LineNumber
        st = Rph.Enumerated('Idle Q3d Q3s Q3sr SingleStart DoubleStart QuoteRun Comment')
        Result = ['I'] * 4
        FirstLine = Line
        TotalLines = LastLine - FirstLine
        while Line <= LastLine:
            if ProgressFunction <> None and (Line & 0xFF) == 0:
                LinesDone = Line - FirstLine
                PercentDone = (LinesDone*100)/TotalLines
                ProgressFunction(PercentDone)
            Text = self.TextWidget.get('%s.0'%Line,'%s.end'%Line)
            if (Text.count('"""') + Text.count("'''")) > 0:
                #This line contains Q3 instances; must scan
                QuoteType = [None] * 4
                QuoteCount = [0,0,0,0]
                ScanState = [st.Idle, st.Q3d, st.Q3s, st.Q3sr]
                ClosingQuoteNeeded = [None] * 4
                StringPrefix = [' '] * 4
                OldC = ' '
                for C in Text:
                    Temp = ''
                    for J in range(4):
                        Temp += '%-15s'%st.Decode(ScanState[J])
                    ##D('C=%s ScanState=%s'%(C,Temp))
                    for J in range(4):    
                        CurScanState = ScanState[J]
                        if C in '"' + "'":
                            #We have a quote of either type
                            if C <> QuoteType[J]:
                                QuoteType[J] = C
                                QuoteCount[J] = 1
                            else:
                                QuoteCount[J] += 1        
                        else:
                            #OldC tracks whatever came before quotes
                            OldC = C
                        if CurScanState == st.Idle:
                            if C == '#':
                                #open comment ends the logical line
                                ScanState[J] = st.Comment
                            if C == "'":
                                #Start of some sort of single quote thing
                                ScanState[J] = st.SingleStart
                                StringPrefix[J] = OldC
                            elif C == '"':
                                #Start of some sort of double quote thing
                                ScanState[J] = st.DoubleStart
                                StringPrefix[J] = OldC
                        elif CurScanState == st.Comment:
                            pass        
                        elif CurScanState == st.SingleStart:
                            #Start of single quoted something
                            if C == "'":
                                #we have a second or third quote
                                if QuoteCount[J] == 3:
                                    #This is the start of a Q3s
                                    if StringPrefix[J].lower() == 'r':
                                        #Q3s raw
                                        ScanState[J] = st.Q3sr
                                    else:
                                        #Q3s cooked
                                        ScanState[J] = st.Q3s    
                                    QuoteType[J] = None
                            else:
                                #We have something other than a quote
                                if QuoteCount[J] == 1:
                                    #Start of Q1s string
                                    ScanState[J] = st.QuoteRun
                                    ClosingQuoteNeeded[J] = "'"
                                else:
                                    #it was simply an empty single quote string
                                    ScanState[J] = st.Idle                    
                        elif CurScanState == st.DoubleStart:
                            #Start of double quoted something
                            if C == '"':
                                #we have a second or third quote
                                if QuoteCount[J] == 3:
                                    #This is the start of a Q3d
                                    ScanState[J] = st.Q3d
                                    QuoteType[J] = None
                            else:
                                #We have something other than a quote
                                if QuoteCount[J] == 1:
                                    #Start of Q1d string
                                    ScanState[J] = st.QuoteRun
                                    ClosingQuoteNeeded[J] = '"'
                                else:
                                    #it was simply an empty double quote string
                                    ScanState[J] = st.Idle
                        elif CurScanState == st.QuoteRun:
                            if C == ClosingQuoteNeeded[J]:
                                #Single quoted string ends
                                ScanState[J] = st.Idle
                                QuoteType[J] = None
                        elif CurScanState == st.Q3d:
                            #we are inside Q3d quotes
                            if QuoteType[J] == '"' and QuoteCount[J] == 3:
                                #We have closing Q3d
                                ScanState[J] = st.Idle
                                QuoteType[J] = None
                        elif CurScanState in (st.Q3s, st.Q3sr):
                            #we are inside Q3s quotes, cooked or raw
                            if QuoteType[J] == "'" and QuoteCount[J] == 3:
                                #We have closing Q3s
                                ScanState[J] = st.Idle
                                QuoteType[J] = None
                #We made it to end-of-line.
                Result = ['0'] * 4
                for J in range(4):
                    if ScanState[J] == st.Q3d:
                        #Q3d in effect at end
                        Result[J] = '1'
                    elif ScanState[J] == st.Q3sr:
                        #Q3s raw in effect at end
                        Result[J] = '3'
                    elif ScanState[J] == st.Q3s:
                        #Q3s cooked in effect at end
                        Result[J] = '2'    
                #Create the universal Q3 locator tag
                OurIndex = '%s.end'%Line
                self.TextWidget.tag_add('Q3',OurIndex)
                #Create specific line action tag
                SpecificTag = 'Q3-'+(''.join(Result))
                self.TextWidget.tag_add(SpecificTag,OurIndex)        
            Line += 1
        return Result #purely for debugging

    def LineQuoteParityCheck(self,LineNumber):
        """
        Find the opening Q3 parity status of a specified line.
        
        The result is:
            o 0 if the line is not inside triple quotes
            o 1 the line starts with Q3d in force
            o 2 the line starts with Q3s cooked in force
            o 3 the line starts with Q3s raw in force
        """
        ##D('Begin Q3 parity check on line %s'%LineNumber)
        Q3List = self.TextWidget.tag_ranges('Q3')
        State = 0
        ListIndex = 0
        if len(Q3List) == 0:
            Q3Next = 999999
        else:
            Q3Next = int(float(Q3List[ListIndex]))    
        while 1:
            ##D('    LineNumber=%s Q3Next=%s'%(LineNumber,Q3Next))
            if LineNumber <= Q3Next:
                #Were done
                ##D('    End Q3 parity check. Result=%s'%State)
                return State
            else:
                AllTags = self.TextWidget.tag_names('%s.end'%Q3Next)
                for Tag in AllTags:
                    if Tag[:3] == 'Q3-':
                        #we found the state translation tag
                        OldState = State
                        State = int(Tag[State+3])
                        ##D('    Line= %s Tag=%s State went from %s to %s'%(Q3Next,Tag,OldState,State))
                        break
                else:
                    raise Exception, 'Expected Q3-xxx tag not found'
                #Advance to next line in list
                ListIndex += 2
                ##D('    ListIndex=%s'%ListIndex)
                if ListIndex < len(Q3List):
                    Q3Next = int(float(Q3List[ListIndex]))
                else:
                    Q3Next = 999999
            
    def ColorToTagName(self,Color):
        """
        Given a color designator, return our corresponding tag name.
        
        The color specification is a color name as returned by the config parser.
        """
        return 'Color_%s'%Color

    def TagNameToColor(self,TagName):
        """
        If a tag name is one of our color-tags, return just the color. Otherwise return "None".
        """
        if TagName[:6] == 'Color_':
            #This is one of our color tags
            return TagName[6:]
        else:
            #Not one of our color tags
            return None    
        
#------------------------------------------------------------------------------
#
# end of colorizer
#
#-------------------------------------------------------------------------------

class ToplevelRP(Toplevel):
    """=d
    A Toplevel with some positioning smarts added.
    
    In addition to the usual "Toplevel" arguments this class accepts:
    
      o "sizeguess" A tuli giving your best guess as to the final size of this Toplevel
          after all its content has been packed. This doesn't have to be exact; it is
          used when positioning to help get centering correct and to prevent the Toplevel
          from being drawn with part of it falling off the edge of the screen. If this
          argument is omitted or passed as "None" then we assume (200,200).
      o "where" This says where to place the toplevel, and can be in one of:
          o "'Mouse'" The Toplevel is placed near the mouse.      
          o "'Center'" The Toplevel is centered on the screen
          o Any other text string is taken to be a geometry string.
          o If a widget, then the dialog is centered on that widget.
          o If "where" is omitted or "None" then the toplevel is placed near the mouse.
    """
    def __init__(self, Master=None, **kw):
        """
        Create the widget.
        """
        try:
            Where = kw['where']
            del kw['where']
        except KeyError:
            Where = 'Mouse'
        try:
            Width,Height = kw['sizeguess']
            del kw['sizeguess']
        except KeyError:
            Width, Height = (200,200)
        
        apply(Toplevel.__init__,(self,Master),kw)
        #Default title
        self.title('Rapyd-Tk')
        #define some window metrics
        ScreenWidth = self.winfo_screenwidth()
        ScreenHeight = self.winfo_screenheight()
        if Where == 'Mouse':
            #place dialog near the mouse
            Mx,My = self.winfo_pointerxy()
            Mx -= Width/2
            Geo = [Width,Height,Mx,My]            
        elif Where == 'Center':
            #place dialog in center of screen
            X = (ScreenWidth-Width)/2
            Y = (ScreenHeight-Height)/2
            Geo = [Width,Height,X,Y]
        elif type(Where) == type(''):
            #any other text string is taken to be a geometry string
            Geo = list(Rph.GeometryDecode(Where))
        else:
            #any non-text argument is taken to be a widget
            #figure out where passed widget is on the screen
            WidW,WidH,WidX,WidY = Rph.WidgetInScreen(Where)
            #now center it there
            X = WidX + ((WidW-Width)/2)
            Y = WidY + ((WidH-Height)/2)
            Geo = [Width,Height,X,Y]
        #Try to keep us on the screen, ok?
        if (Geo[0] + Geo[2]) > ScreenWidth:     #no falling off the right
            Geo[2] = ScreenWidth-Geo[0]
        if (Geo[1] + Geo[3]) > ScreenHeight:    #no falling of the bottome
            Geo[3] = ScreenHeight-Geo[1]            
        Geo[2] = max(0, Geo[2])                 #no falling off the left
        Geo[3] = max(0, Geo[3])                 #no falling off the top
        self.geometry('+%s+%s'%(Geo[2],Geo[3]))

class ProgressDialog(ToplevelRP):
    """=d
    A simple progress meter dialog
    
    Additional argument "title" is the title for the Toplevel widget. If no title
        is specified it defaults to "Progress".
        
    The result, returned in "self.Result" is a two-tuple:
        o "[0]" The directory; ends in a slash.
        o "[1]" The file name; no extension        
    """

    def __init__(self,Master=None,**kw):
        """=U
        Create the widget.
        """
        kw['sizeguess'] = (265,200)
        
        try:
            Title = kw['title']
            del kw['title']
        except KeyError:
            Title = 'Progress'
        
        apply(ToplevelRP.__init__,(self,Master),kw)
        self.Indicator = Scale(self,orient=HORIZONTAL,length=200)
        self.title(Title)
        self.Indicator.pack(padx=30,pady=30)
        
    def Set(self,Value):
        self.Indicator.set(Value)
        self.update_idletasks()
        
    def Close(self):
        self.destroy()        

class NewProjectDialog(ToplevelRP):
    """
    Dialog to kick off a new project.
    
    In addition to the usual "ToplevelRP" we expect argument "InitialDir" which is the
        directory string we start with.
        
    Argument "ProjectFile" is optional an is the initial name which will be suggested
        to the user. If omitted it defaults to empty.    
        
    The result is None if the user cancelled or a 2-tuple:
        o "[0]" The directory the user picked for the project; guaranteed to end
            with a slash.
        o "[1]" The name the user entered for the new project; no extension.    
    """
    def __init__(self,Master=None,**kw):
        """
        Create the dialog.
        """
        try:
            self.ProjectDir = kw['InitialDir']
            del kw['InitialDir']
        except KeyError:
            raise Exception, 'Option "InitialDir" not found'
            
        try:
            self.ProjectFile = kw['ProjectFile']
            del kw['ProjectFile']
        except KeyError:        
            self.ProjectFile = ''    

        apply(ToplevelRP.__init__,(self,Master),kw)
        self.title('New Project')

        self.Result = None
        Label(self).pack(pady=0)
        Label(self,text='Name for new project:').pack(padx=20,anchor=W)
        #
        # Entry
        #
        self.Entry = Entry(self,width=20)
        self.Entry.insert(0,self.ProjectFile)
        self.Entry.pack(side=TOP,padx=20,anchor=W)
        
        Label(self).pack(pady=0)
        
        Label(self,text='Directory for new project:').pack(padx=20,anchor=W)
        
        self.DirButton = Button(self,text=self.ProjectDir,command=self.on_DirButton,pady=0)
        self.DirButton.pack(side=TOP,anchor=W,padx=20)
        
        Label(self).pack()
        
        #
        # Button bar
        #        
        self.Buttons = Rph.ButtonBox(self)
        B = self.Buttons.add('OK',command=self.on_OK)
        B['default'] = 'active'
        self.Buttons.add('Help',command=self.on_Help)
        self.Buttons.add('Cancel',command=self.on_Cancel)
        self.Buttons.pack(side=TOP)

        self.bind('<Return>',self.on_OK)
        self.bind('<Escape>',self.on_Cancel)
        self.bind('<F1>',self.on_Help)
        #
        #be modal
        #
        self.Entry.focus_set()
        Rph.Grabber(self)
        self.wait_window()

    def on_DirButton(self):
        """
        User wants to set directory
        """
        Temp = AskDirectory(parent=self
            ,initialdir=self.ProjectDir,title='Directory for new project')
        if Temp:
            self.ProjectDir = Temp
            self.DirButton['text'] = Temp
        
    def on_OK(self,Event=None):
        Temp = os.path.splitext(self.Entry.get().strip())
        if Temp[0] == '':
            ErrorDialog(Message='No name for project given. Please enter a name or click Cancel.')
            return
        FileList = []
        Path = self.ProjectDir + '/' + Temp[0]    
        Filename = Path+'.py'
        if os.path.exists(Filename):
            FileList = [Temp[0]+'.py']
        Filename = Path+'.rpj'
        if os.path.exists(Filename):
            FileList.append(Temp[0]+'.rpj')
        if len(FileList) <> 0:
            if len(FileList) == 1:
                Msg = 'A file named "%s" already exists in directory "%s". ' \
                    'Keep going anyway?'%(FileList[0],self.ProjectDir)
            else:
                Msg = 'Files named "%s" and "%s" already exist in directory "%s". ' \
                    'Keep going anyway?'%tuple(FileList+[self.ProjectDir])
            H = 'project.new.dialog.fileexists'
            R = MessageDialog(Title='Warning',Message=Msg
                ,Buttons=(('Keep going',1),('~Cancel',None)),Help=H).Result
            if R <> 1:
                return
        self.Result = (self.ProjectDir+'/',Temp[0])
        self.destroy()

    def on_Cancel(self,Event=None):
        self.destroy()        
        
    def on_Help(self,Event=None):
        Help('project.new.dialog')


class ModuleNameDialog(ToplevelRP):
    """
    Dialog about adding a new module to the project or changing the
        name of a module.
    
    In addition to the usual "TopleverRP" option, we expect:
    
        o "Modules" a list of our modules.
        o "Forms" a list of forms.
        o "ProjectDirectory" the name of the project directory, '' if the current directory.
        
    And optional is:
    
        o "Current" The name of a module.
        
    If "Current" is not supplied then we get the name of a new
        module.
        
    If "Current" is supplied, we get the name the user wants to
        change the current module to.            
        
    The "Forms" argument is for the case where we are renaming the main module. Renaming the main
        module implies renaming the main form of the main module and thus we want to avoid letting
        the user rename to something that would conflict with an existing form of the main module.
        For most cases Forms is an empty list. In the case of the main module, it is a list of 
        form names and hence of names not suitable for the new module/project name.        
    """
    def __init__(self,Master=None,**kw):
        """
        Create the widget.
        """
        try:
            self.Modules = kw['Modules']
            del kw['Modules']
        except KeyError:
            raise Exception, 'Keyword arguemnt "Modules" not found'

        try:
            self.ProjectDirectory = kw['ProjectDirectory']
            del kw['ProjectDirectory']
        except KeyError:
            raise Exception, 'Keyword arguemnt "ProjectDirectory" not found'

        try:
            self.Current = kw['Current']
            del kw['Current']
        except KeyError:
            self.Current = ''

        try:
            self.Forms = kw['Forms']
            del kw['Forms']
        except KeyError:
            self.Forms = []

        apply(ToplevelRP.__init__,(self,Master),kw)
        self.title(' ')

        self.Result = None
        self.MainModuleRename = False
        if self.Current == '':
            Msg = "Enter name for the new module:"
            self.HelpTopic = 'module.new.dialog'
        else:
            if self.Current == Cfg.Info['ProjectName']:
                Msg = '"%s" is the main-module of the project. Renaming it ' \
                    'will rename the project, the main-module of the project and the main-form of the ' \
                    'main-module all at once. ' \
                    'Enter the new name the project:'%self.Current
                self.HelpTopic = 'project.rename.dialog'
                self.MainModuleRename = True
            else:
                Msg = 'Enter new name for module "%s".'%self.Current
                self.HelpTopic = 'module.rename.dialog'
                
        Label(self,text=Rph.TextBreak(Msg,45)).pack(padx=20,pady=20)
        #
        # Entry
        #
        self.Entry = Entry(self,width=20)
        self.Entry.insert(0,self.Current)
        self.Entry.pack(side=TOP,padx=10,pady=10)
        #
        # Button bar
        #        
        self.Buttons = Rph.ButtonBox(self)
        B = self.Buttons.add('OK',command=self.on_OK)
        B['default'] = 'active'
        self.Buttons.add('Help',command=self.on_Help)
        self.Buttons.add('Cancel',command=self.on_Cancel)
        self.Buttons.pack(side=TOP)

        self.bind('<Return>',self.on_OK)
        self.bind('<Escape>',self.on_Cancel)
        self.bind('<F1>',self.on_Help)
        #
        #be modal
        #
        self.Entry.focus_set()
        Rph.Grabber(self)
        self.wait_window()
        
    def on_OK(self,Event=None):
        Temp = os.path.splitext(self.Entry.get().strip())
        if Temp[0] == '':
            ErrorDialog(Message='No name for module given. Please enter a name or click Cancel.')
            return
        if Temp[0] == self.Current:
            #They renamed it to the same thing; this is the same as pressing cancel
            self.on_Cancel()    
            return
        if not NameVet(Temp[0]):
            ErrorDialog(Message='"%s" is not a valid Python name.'%Temp[0])
            return
        if Temp[0] in self.Modules:
            ErrorDialog(Message='The project already has a module named "%s". Please choose ' \
                'a different name or click Cancel.'%Temp[0])
            return
        if Temp[0] in self.Forms:
            R = ErrorDialog(Message='The name "%s" conflicts with the name of a form in the main'
                ' module.'%Temp[0],Help=1).Result
            if R == 1:
                Help('module.new.dialog.formconflict',[Temp[0]])
            return    
        Filename = '%s%s.py'%(self.ProjectDirectory,Temp[0])
        if os.path.exists(Filename):
            Msg = 'A file named "%s" already exists. Keep going anyway?'%(Filename)
            if self.Current == '':
                H = ('module.new.dialog.fileexists',(Temp[0],Filename))
            else:
                H = ('module.rename.dialog.fileexists',(Temp[0],Filename,self.ProjectDirectory+self.Current))    
            R = MessageDialog(Title='Warning',Message=Msg
                ,Buttons=(('Keep going',1),('~Cancel',None)),Help=H).Result
            if R <> 1:
                return
        if self.MainModuleRename:
            Filename = Temp[0]+'.rpj'
            if os.path.exists(Filename):
                Msg = 'A project named "%s" already exists. Keep going anyway?'%Filename
                H = ('project.rename.dialog.fileexists',(Temp[0],Filename,self.Current))    
                R = MessageDialog(Title='Warning',Message=Msg
                    ,Buttons=(('Keep going',1),('~Cancel',None)),Help=H).Result
                if R <> 1:
                    return
        
        self.Result = Temp[0]            
        self.destroy()
        
    def on_Cancel(self,Event=None):
        self.destroy()        
        
    def on_Help(self,Event=None):
        Help(self.HelpTopic)

class ModuleDialog(ToplevelRP):
    """
    Dialog where the user selects the current module.
    
    In addition to the usual "TopleverRP" option, we expect:
    
        o "Modules" a list of our modules.
        o "Current" name of the currently selected module.
    """
    def __init__(self,Master=None,**kw):
        """
        Create the widget.
        """
        try:
            self.Modules = kw['Modules']
            del kw['Modules']
        except KeyError:
            raise Exception, 'Keyword arguemnt "Modules" not found'

        try:
            self.Current = kw['Current']
            del kw['Current']
        except KeyError:
            raise Exception, 'Keyword arguemnt "Current" not found'

        apply(ToplevelRP.__init__,(self,Master),kw)
        self.title(' ')

        self.Result = None
        Label(self,text="Select the module to make current").pack(padx=20,pady=20)
        #
        # Checkbuttons
        #
        self.Modules.sort()
        self.RadioCvar = StringVar()
        for Module in self.Modules:
            Temp = Radiobutton(self,text=Module,value=Module,variable=self.RadioCvar)
            Temp.pack(anchor=W,padx=20)
            if Module == self.Current:
                Temp.select()
        Label(self).pack(pady=10)    
        #
        # Button bar
        #        
        self.Buttons = Rph.ButtonBox(self)
        B = self.Buttons.add('OK',command=self.on_OK)
        B['default'] = 'active'
        self.Buttons.add('Help',command=self.on_Help)
        self.Buttons.add('Cancel',command=self.on_Cancel)
        self.Buttons.pack(side=TOP)

        self.bind('<Return>',self.on_OK)
        self.bind('<Escape>',self.on_Cancel)
        self.bind('<F1>',self.on_Help)
        #
        #be modal
        #
        self.focus_set()
        Rph.Grabber(self)
        self.wait_window()
        
    def on_OK(self,Event=None):
        self.Result = self.RadioCvar.get()
        self.destroy()
        
    def on_Cancel(self,Event=None):
        self.destroy()        
        
    def on_Help(self,Event=None):
        Help('module.select.dialog')


class FormSeeDialog(ToplevelRP):
    """
    Dialog where the user selects which forms appear in tabs
    
    In addition to the usual "TopleverRP" option, we expect:
    
        o "Herds" a list of current herds.
        o "Tabs" a list of forms currenlty appearing on tabs.
           We need the tab names so we can show those forms as being
           currently selected for display.
           
    The result is a list of form names.
    
    NOTE: If the user selects *no* forms then we give them -Main-; it's not
        a good idea to attempt to display no forms.     
        
    """
    def __init__(self,Master=None,**kw):
        """
        Create the widget.
        """
        try:
            self.Herds = kw['Herds']
            del kw['Herds']
        except KeyError:
            raise Exception, 'Keyword arguemnt "Herds" not found'

        try:
            self.Tabs = kw['Tabs']
            del kw['Tabs']
        except KeyError:
            raise Exception, 'Keyword arguemnt "Tabs" not found'

        apply(ToplevelRP.__init__,(self,Master),kw)
        self.title(' ')

        self.Result = None
        Label(self,text="Select forms to appear on tabs").pack(padx=20,pady=20)
        #
        # Checkbuttons
        #
        self.Herds.sort()
        self.Checkbuttons = []
        for Herd in self.Herds:
            if ' ' in Herd:
                #This is a special herd (eg the parking lot)
                continue
            Temp = CheckbuttonRP(self,text=Herd)
            Temp.pack(anchor=W,padx=20)
            if Herd in self.Tabs:
                Temp.set(1)
            Temp.Herd = Herd    
            self.Checkbuttons.append(Temp)        
        Label(self).pack(pady=10)    
        #
        # Button bar
        #        
        self.Buttons = Rph.ButtonBox(self)
        B = self.Buttons.add('OK',command=self.on_OK)
        B['default'] = 'active'
        self.Buttons.add('Help',command=self.on_Help)
        self.Buttons.add('Cancel',command=self.on_Cancel)
        self.Buttons.pack(side=TOP)

        self.bind('<Return>',self.on_OK)
        self.bind('<Escape>',self.on_Cancel)
        self.bind('<F1>',self.on_Help)

        #
        #be modal
        #
        self.focus_set()
        Rph.Grabber(self)
        self.wait_window()
        
    def on_OK(self,Event=None):
        self.Result = []
        for CB in self.Checkbuttons:
            if CB.get():
                self.Result.append(CB.Herd)
        if len(self.Result) == 0:
            self.Result = ['-Main-']
        self.destroy()
        
    def on_Cancel(self,Event=None):
        self.destroy()        
        
    def on_Help(self,Event=None):
        Help('FormSeeDialog')

class FormDialog(ToplevelRP):
    """=d
    Dialog to allow user to edit form properties.
    
    In addition to the usual "TopleverRP" option, we accept:
    
        "Settings": A dictionary the same as our result dictionary.
        "Title":    Title for this dialog.
        "Prompt":   The prompt for the form name entry
        "AllowNameEdit": Defaults to false. If true, we allow the user to edit the
                    name passed in "Settings['Name']".
        "FrameOnly": Defaults to false. If true we don't allow them to set it to derive
                    from Toplevel. This is in aid of the main form of the main module
                    which must derive only from a frame.            
    
    The result is returned in w.Result. The result is "None" if the user cancelled,
        or a dictionary thus: 
    
      o "['Name']" The users name for the form.
      o "['Type']" "'Tkinter.Toplevel'", "'Tkinter.Frame'" or "'Pmw.ScrolledFrame'".
      o "['BaseClass'] The name of the class from which this form is to be derived.
          If we are deriving directly from Toplevel or Frame then this will be either
          Toplevel or Frame. If we are deriving from some other class (which must itself
          be derived from Toplevel or Frame) then the name of that class.
    """

    def __init__(self,Master=None,**kw):
        """=U
        Create the widget.
        """
        try:
            self.Settings = kw['Settings']
            del kw['Settings']
        except KeyError:
            raise Exception, 'Keyword arguemnt "Settings" not found'

        try:
            Title = kw['Title']
            del kw['Title']
        except KeyError:
            raise Exception, 'Keyword arguemnt "Title" not found'

        try:
            Prompt = kw['Prompt']
            del kw['Prompt']
        except KeyError:
            raise Exception, 'Keyword arguemnt "Prompt" not found'

        try:
            self.AllowNameEdit = kw['AllowNameEdit']
            del kw['AllowNameEdit']
        except KeyError:
            self.AllowNameEdit = 0    

        try:
            self.FrameOnly = kw['FrameOnly']
            del kw['FrameOnly']
        except KeyError:
            self.FrameOnly = False

        kw['sizeguess'] = (310,340)

        apply(ToplevelRP.__init__,(self,Master),kw)

        self.title(Title)
        Py = 10
        Px = 10
        #
        # Label and entry for form name
        #
        Label(self).pack(side=TOP)
        if self.AllowNameEdit:
            Label(self,text=Prompt).pack(side=TOP,padx=Px,pady=0,anchor=W)
        
            self.Entry = Entry(self,width=40)
            self.Entry.pack(side=TOP,padx=Px,pady=Py)
            self.Entry.insert(0,self.Settings['Name'])
        else:
            Label(self,text='%s %s'%(Prompt,self.Settings['Name'])).pack(side=TOP
                ,padx=Px,pady=0,anchor=W)
        #
        # Label and radio buttons for type
        #
        Label(self).pack(side=TOP)
        TypeLabel = Label(self,text='This form to derive from:').pack(side=TOP
            ,padx=Px,pady=0,anchor=W)
        self.TypeCVar = StringVar()
        T = Radiobutton(self,text='Tkinter.Toplevel',variable=self.TypeCVar
            ,value='Tkinter.Toplevel')
        if self.FrameOnly:
            T.config(state=DISABLED)
        T.pack(side=TOP,padx=Px+20,pady=0,anchor=W)
        F = Radiobutton(self,text='Tkinter.Frame',variable=self.TypeCVar
            ,value='Tkinter.Frame')
        F.pack(side=TOP,padx=Px+20,pady=0,anchor=W)
        S = Radiobutton(self,text='Pmw.ScrolledFrame',variable=self.TypeCVar
            ,value='Pmw.ScrolledFrame')
        S.pack(side=TOP,padx=Px+20,pady=0,anchor=W)
        TD = Radiobutton(self,text='A widget derived from Tkinter.Toplevel',variable=self.TypeCVar
            ,value='ToplevelDerived')
        if self.FrameOnly:
            TD.config(state=DISABLED)
        TD.pack(side=TOP,padx=Px+20,pady=0,anchor=W)
        FD = Radiobutton(self,text='A widget derived from Tkinter.Frame',variable=self.TypeCVar
            ,value='FrameDerived')
        FD.pack(side=TOP,padx=Px+20,pady=0,anchor=W)
        SD = Radiobutton(self,text='A widget derived from Pmw.ScrolledFrame',variable=self.TypeCVar
            ,value='ScrolledFrameDerived')
        SD.pack(side=TOP,padx=Px+20,pady=0,anchor=W)
        ##D('BaseClass=%s Type=%s'%(self.Settings['BaseClass'],self.Settings['Type']))
        if self.Settings['BaseClass'] == self.Settings['Type']:
            #We are deriving directly from Toplevel or Frame
            if self.Settings['Type'] == 'Tkinter.Toplevel':
                T.select()
            elif self.Settings['Type'] == 'Tkinter.Frame':
                F.select()
            elif self.Settings['Type'] == 'Pmw.ScrolledFrame':
                S.select()    
            else:
                raise Exception, 'Invalid Type: %s'%self.Settings['Type']    
        else:        
            #We are deriving indirectly from Toplevel or Frame
            if self.Settings['Type'] == 'Tkinter.Toplevel':
                TD.select()
            elif self.Settings['Type'] == 'Tkinter.Frame':
                FD.select()
            elif self.Settings['Type'] == 'Pmw.ScrolledFrame':
                SD.select()    
            else:
                raise Exception, 'Invalid Type'
        self.TypeEntry = Entry(self,width=30,relief=FLAT)
        self.TypeEntry.pack(side=TOP,padx=Px+45,anchor=W)
        if self.TypeCVar.get() in ('ToplevelDerived','FrameDerived','ScrolledFrameDerived'):
            self.TypeEntry.insert(0,self.Settings['BaseClass'])
            self.TypeEntry['relief'] = SUNKEN
        else:
            self.TypeEntry['state'] = DISABLED    
        T['command'] = self.on_TypeChange    
        F['command'] = self.on_TypeChange    
        S['command'] = self.on_TypeChange    
        TD['command'] = self.on_TypeChange    
        FD['command'] = self.on_TypeChange
        SD['command'] = self.on_TypeChange
        #
        # Buttons at bottom
        #
        self.ButtonFrame = Frame(self)
        self.ButtonFrame.pack(side=TOP,padx=Px,pady=Py)
        
        self.OK = Button(self.ButtonFrame,text='OK',command=self.on_OK)
        self.OK.pack(side=LEFT,padx=Px,pady=Py)

        self.Help = Button(self.ButtonFrame,text='Help',command=self.on_Help)
        self.Help.pack(side=LEFT,padx=Px,pady=Py)

        self.Cancel = Button(self.ButtonFrame,text='Cancel',command=self.on_Cancel)
        self.Cancel.pack(side=LEFT,padx=Px,pady=Py)

        self.Result = None

        self.bind('<Return>',self.on_OK)
        self.bind('<Escape>',self.on_Cancel)
        
        #Be modal
        if self.AllowNameEdit:
            self.Entry.focus_set()
        Rph.Grabber(self)
        self.wait_window()

    def on_TypeChange(self):
        if self.TypeCVar.get() in ('ToplevelDerived','FrameDerived','ScrolledFrameDerived'):
            self.TypeEntry['state'] = NORMAL
            self.TypeEntry['relief'] = SUNKEN
        else:
            self.TypeEntry.delete(0,END)
            self.TypeEntry['relief'] = FLAT
            self.TypeEntry['state'] = DISABLED    
        
    def on_OK(self,Event=None):
        if self.AllowNameEdit:
            Name = self.Entry.get()
        else:
            Name = self.Settings['Name']
        Type = self.TypeCVar.get()
        if Type == 'ToplevelDerived':
            Type = 'Tkinter.Toplevel'
            BaseClass = self.TypeEntry.get()
        elif Type == 'FrameDerived':
            Type = 'Tkinter.Frame'
            BaseClass = self.TypeEntry.get()
        elif Type == 'ScrolledFrameDerived':
            Type = 'Pmw.ScrolledFrame'
            BaseClass = self.TypeEntry.get()    
        else:
            BaseClass = Type        
        if self.AllowNameEdit and (not NameVet(Name)):
            #We don't like their name
            R = MessageDialog(Title='Oops',Message='"%s" is not an acceptable form name. '
                'Please pick another name or cancel.'%Name
                ,Buttons=(('Dismiss',None),('Help',0))).Result
            if R == 0:
                #They asked for help
                Help('Form.InvalidName')
            return
        if BaseClass == '':
            R = MessageDialog(Title='Oops',Message='You need to specify the name of the class ' \
                'from which this form is to be derived.'
                ,Buttons=(('Dismiss',None),('Help',0))).Result
            if R == 0:
                #They asked for help
                Help(('Form.BaseClassOmitted'),(Type,))
            return    
                    
        if not NameVet(BaseClass,AllowDot=True):
            #We don't like their name
            R = MessageDialog(Title='Oops',Message='"%s" is not an acceptable class-name to derive from. '
                'Please pick another name or cancel.'%BaseClass
                ,Buttons=(('Dismiss',None),('Help',0))).Result
            if R == 0:
                #They asked for help
                Help('Form.InvalidBaseClassName')
            return    
        self.Result = {
            'Name':Name, 
            'Type':Type,
            'BaseClass':BaseClass
            }
        self.destroy()
    
    def on_Help(self):
        if self.AllowNameEdit:
            #If the user is allowed to edit the name then the form in question is a new
            #    on in which case it can derive from any of the three classes.
            Help('form-properties-dialog')
        else:
            if self.FrameOnly:
                #We are working on the main frame of the main module.
                Help('form-properties-dialog-main')
            else:    
                #We are working on a frame other than the main frame
                Help('form-properties-dialog-noname')
    def on_Cancel(self,Event=None):
        self.destroy()        

class FrameDialog(ToplevelRP):
    """=d
    Dialog to allow user to edit frame properties.
    
    In addition to the usual "TopleverRP" option, we accept:
    
        "Settings":  A dictionary containing:
           o ['Name'] The name of the frame.
           o ['Type'] The present type, either "Tkinter.Frame" or "Pmw.ScrolledFrame".
    
    The result is returned in w.Result. The result is "None" if the user cancelled,
        or a string giving the selected type.
    """
    def __init__(self,Master=None,**kw):
        """=U
        Create the widget.
        """
        try:
            self.Settings = kw['Settings']
            del kw['Settings']
        except KeyError:
            raise Exception, 'Keyword arguemnt "Settings" not found'

        kw['sizeguess'] = (310,340)

        apply(ToplevelRP.__init__,(self,Master),kw)

        self.title('Frame properties')
        Py = 10
        Px = 10
        #
        # Label and entry for form name
        #
        Label(self).pack(side=TOP)
        Label(self,text='Frame: %s'%self.Settings['Name']).pack(side=TOP,padx=Px,pady=0,anchor=W)
        #
        # Label and radio buttons for type
        #
        Label(self).pack(side=TOP)
        TypeLabel = Label(self,text='This frame to be an instance of:').pack(side=TOP
            ,padx=Px,pady=0,anchor=W)
        self.TypeCVar = StringVar()
        Tk = Radiobutton(self,text='Tkinter.Frame',variable=self.TypeCVar,value='Frame')
        Tk.pack(side=TOP,padx=Px+20,pady=0,anchor=W)
        Pmw = Radiobutton(self,text='Pmw.ScrolledFrame',variable=self.TypeCVar,value='ScrolledFrame')
        Pmw.pack(side=TOP,padx=Px+20,pady=0,anchor=W)
        if self.Settings['Type'] == 'Frame':
            Tk.select()
        elif self.Settings['Type'] == 'ScrolledFrame':
            Pmw.select()
        else:
            raise Exception, 'Invalid Type'    
                
        Label(self).pack(side=TOP)
        #
        # Buttons at bottom
        #
        self.ButtonFrame = Frame(self)
        self.ButtonFrame.pack(side=TOP,padx=Px,pady=Py)
        
        self.OK = Button(self.ButtonFrame,text='OK',command=self.on_OK)
        self.OK.pack(side=LEFT,padx=Px,pady=Py)

        self.Help = Button(self.ButtonFrame,text='Help',command=self.on_Help)
        self.Help.pack(side=LEFT,padx=Px,pady=Py)

        self.Cancel = Button(self.ButtonFrame,text='Cancel',command=self.on_Cancel)
        self.Cancel.pack(side=LEFT,padx=Px,pady=Py)

        self.Result = None

        self.bind('<Return>',self.on_OK)
        self.bind('<Escape>',self.on_Cancel)
        
        #Be modal
        Rph.Grabber(self)
        self.wait_window()

    def on_OK(self,Event=None):
        self.Result = self.TypeCVar.get()
        self.destroy()
    
    def on_Help(self):
        Help('frame-properties-dialog')

    def on_Cancel(self,Event=None):
        self.destroy()        

class SearchDialog(ToplevelRP):
    """=d
    Search dialog for text editor.
    
    In addition to the usual "TopleverRP" option, we accept:
    
        o "settings" which should be "None" or a dictionary as returned by
          this class. If supplied, the values in the dictionary are used to
          set the initial values of all the options.
        o "AndReplace" If omitted or false, then the dialog shows only search
          related choices. If true, the dialog shows both search and replace
          related choices.  
    
    The result is returned in w.Result. The result is "None" if the user cancelled,
        or a dictionary thus: 
    
      o "['Text']" The string the user entered.
      o "['Case']" A boolean from the "Case sensitive" checkbox.
      o "['Back']" A boolean from the "Backwards" checkbox.
      o "['Regex']" A booleean from the "Regex" checkbutton.
      o "['Top']" A boolean from the "From first/last line" checkbutton.
      o "['Prompt']" A boolean from the "Prompt on replace" checkbutton.
      o "['All']" A boolean from the "Replace all" checkbutton.
      o "['RepText']" The replacement string the user entered.
      
      Note that the last three items are always supplied but they are meaningful
        only if "AndReplace" is in effect.
    """

    def __init__(self,Master=None,**kw):
        """=U
        Create the widget.
        """
        try:
            Settings = kw['settings']
            del kw['settings']
        except KeyError:
            Settings = None

        try:
            self.AndReplace = kw['AndReplace']
            del kw['AndReplace']
        except KeyError:
            self.AndReplace = 0

        apply(ToplevelRP.__init__,(self,Master),kw)

        if self.AndReplace:
            self.title(' Search and Replace ')
            Py = 5
        else:
            self.title(' Search ')        
            Py = 10
        Px = 10
        #
        # Label and entry for search text
        #
        Label(self).pack(side=TOP)
        Label(self,text='Enter search string:').pack(side=TOP,padx=Px,pady=0)
        
        self.Entry = Entry(self,width=40)
        self.Entry.pack(side=TOP,padx=Px,pady=Py)
        #
        # Label and entry for replacement text
        #
        self.ReplacementPadLabel = Label(self)
        self.ReplaceLabel = Label(self,text='Enter replacement string:')
        self.ReplacementEntry = Entry(self,width=40)

        if self.AndReplace:
            self.ReplacementPadLabel.pack(side=TOP)
            self.ReplaceLabel.pack(side=TOP,padx=Px,pady=0)
            self.ReplacementEntry.pack(side=TOP,padx=Px,pady=Py)
        #
        # Checkbuttons
        #
        self.Zero = CheckbuttonRP(self,text='From first line')
        self.Zero.pack(side=TOP,anchor=W,padx=Px,pady=Py)

        self.Case = CheckbuttonRP(self,text='Case sensitive')
        self.Case.pack(side=TOP,anchor=W,padx=Px,pady=Py)
        
        self.Back = CheckbuttonRP(self,text='Backwards',command=self.on_Backwards)
        self.Back.pack(side=TOP,anchor=W,padx=Px,pady=Py)

        self.Regex = CheckbuttonRP(self,text='Regular expression')
        self.Regex.pack(side=TOP,anchor=W,padx=Px,pady=Py)

        #We always create the 'AndReplace' buttons but pack them only if needed.        
        self.Prompt = CheckbuttonRP(self,text='Prompt on replace')
        self.All = CheckbuttonRP(self,text='Replace all')

        if self.AndReplace:
            self.Prompt.pack(side=TOP,anchor=W,padx=Px,pady=Py)
            self.All.pack(side=TOP,anchor=W,padx=Px,pady=Py)
        #
        # Buttons at bottom
        #
        self.ButtonFrame = Frame(self)
        self.ButtonFrame.pack(side=TOP,padx=Px,pady=Py)
        
        self.OK = Button(self.ButtonFrame,text='OK',command=self.on_OK)
        self.OK.pack(side=LEFT,padx=Px,pady=Py)

        self.Help = Button(self.ButtonFrame,text='Help',command=self.on_Help)
        self.Help.pack(side=LEFT,padx=Px,pady=Py)

        self.Cancel = Button(self.ButtonFrame,text='Cancel',command=self.on_Cancel)
        self.Cancel.pack(side=LEFT,padx=Px,pady=Py)

        self.Result = None

        self.bind('<Return>',self.on_OK)
        self.bind('<Escape>',self.on_Cancel)
        
        if Settings <> None:
            #Previous settings were supplied
            self.Entry.insert(0,Settings['Text'])
            self.ReplacementEntry.insert(0,Settings['RepText'])
            if Settings['Case']:
                self.Case.set(1)
            if Settings['Back']:
                self.Back.set(1)
            if Settings['Regex']:
                self.Regex.set(1)
            if Settings['Top']:
                self.Zero.set(1)
            if Settings['Prompt']:
                self.Prompt.set(1)
            if Settings['All']:
                self.All.set(1)        
        else:
            #No previous settings were supplied
            self.Prompt.set(1)    
            
        #Select all text in the entry, so user can easily delete old text
        self.Entry.select_range(0,END)
        
        #Be modal
        self.Entry.focus_set()
        Rph.Grabber(self)
        self.wait_window()
    
    def on_Backwards(self):
        if self.Back.get():
            #user asked for backwards
            self.Zero['text'] = 'From last line'
        else:
            #user asked for forwards
            self.Zero['text'] = 'From first line'    

    def on_OK(self,Event=None):
        self.Result = {'Text':self.Entry.get(), 'Case':self.Case.get()
            ,'Back':self.Back.get(), 'Regex':self.Regex.get(), 'Top':self.Zero.get()
            ,'Prompt':self.Prompt.get(), 'All':self.All.get()
            ,'RepText':self.ReplacementEntry.get()}
        self.destroy()
    
    def on_Help(self):
        if self.AndReplace:
            Help('search.replace-dialog')
        else:
            Help('search.dialog')
        
    def on_Cancel(self,Event=None):
        self.destroy()        

class CheckbuttonRP(Checkbutton):
    """=d
    An enhanced check button.
    
    This checkbutton has the control variable built in. The get/set methods
        return/expect an integer representing true or false.
    """
    def __init__(self,cnf={},**kw):
        self._CurrentState = IntVar()
        kw['variable'] = self._CurrentState
        Checkbutton.__init__(self,cnf,kw)
        
    def get(self):
        return self._CurrentState.get()
        
    def set(self,Value):
        self._CurrentState.set(Value)

class Colorize:
    """=d
    A class to beat colorization information out of a line of Pytyon code.
    
    Note: Colorizing involves a lot of discussion of triple-quoted strings and there is a distinction
        to be made between triple-quotes consisting of single quotes and triple-quotes consisting
        of double quotes. Tiring of typing seemingly oxymoronic phrases like "single triple quotes"
        and "double triple quotes" I eventually settled on Q3s as a short form for the former, Q3d
        as a short form for the latter, and Q3 for "triple quotes of either kind".
    """
    def __init__(self):
        """
        Create the class.
        """
        self.KeywordDict = {}
        for kw in keyword.kwlist:
            self.KeywordDict[kw] = None
        self.ColorDict = Cfg.Info['Schemes'][Cfg.Info['SchemeCurName']]['Colors']
            
    def __call__(self,Line,InitialState=0):
        """
        Given a line of Python text, return colorization information.
        
        "Line" is the text to be scanned.
        
        "InitialState" is -1, 0, 1 or 2:
            o "-1 or 0": This is a normal line
            o "1": This line continues a Q3d comment line
            o "2": This line continues a Q3s cooked string line
            o "3": This line continues a Q3s raw string line
            
        The result is a three element tuple:

        "[0]" A value giving some information about state at end-of-line:
            o "-1" A non-triple quoted string was open.
            o "0" We were idle.   
            o "1" A Q3d comment was open.
            o "2" A Q3s cooked string was open.
            o "3" A Q3s raw string was open.
            
        "[1]" A list of dictionarys. Each dictionary gives information about a contiguous portion
            of the line which needs colorization:
            o "Class": The class of colorization element. This value corresponds to the syntactic
              colorization elements as defined by the config file, and will consist of either a
              single character (for single-character elements, eg % + - { } etc) or a element
              name "comment", "keyword", "phrase", "self", "string", "escape".    
            o "Start": The index of the starting character of this element.
            o "Length": The number of characters in this element.  
            o "Color": The required color for this element as a string, eg "'#FF0000'".
            
        "[2]" An integer indicating if a hash comment was in force at end of line.
            o 0 No hash comment in force at end of line
            o 1 Hash comment in force at end of line
        """
        assert InitialState in (-1, 0 ,1 ,2, 3)
        st = Rph.Enumerated('Idle Name Singleton SquoteStart QuoteRun PhraseStart PhraseKey1 PhraseKeyN '
            'PhraseFlags PhraseWidth PhrasePrecision PhraseType DquoteStart DQcomment Escape')
        State = st.Idle
        Result = []
        J = -1
        Line = Line + '$'
        Watchdog = int(len(Line) * 3)
        C = ''
        RawFlag = ''
        Advance = 1
        QuoteCount = 0
        HashFlag = 0
        #At start triple quote parity is even
        Q3d = 0
        Q3s = 0
        if InitialState == 1:
            #This line is a continuation of a triple double-quote comment
            Start = 0
            ClosingQuotesNeeded = 3
            State = st.DQcomment
        elif InitialState == 2:
            #This line is a continuation of a triple single-quoted cooked string
            Start = 0    
            State = st.QuoteRun
            ClosingQuotesNeeded = 3
            ClosingQuoteType = "'"
            RawFlag = ' '
        elif InitialState == 3:
            #This line is a continuation of a triple single-quoted raw string
            Start = 0    
            State = st.QuoteRun
            ClosingQuotesNeeded = 3
            ClosingQuoteType = "'"
            RawFlag = 'r'
        while J < len(Line)-1:
            Watchdog -= 1
            if Watchdog < 0:
                raise Exception, 'Watchdog'
            if Advance:
                J += 1
                PreviousC = C
            C = Line[J]
            #print J, C, RawFlag, st.Decode(State)
            Advance = 1
            if State == st.Idle:
            #
            # --- Idle ---
            #
                Start = J
                if C in Alpha:
                    #Start of a name
                    State = st.Name
                elif self.ColorDict.has_key(C):
                    #Start of colored singletons
                    State = st.Singleton
                    Color = self.ColorDict[C]
                elif C == '#':
                    #Start of hash comment
                    Result.append({'Start':Start, 'Length':len(Line)-Start-1, 'Class':'comment'})
                    HashFlag = 1
                    break
                elif C == "'":
                    #Start of single quoted something
                    State = st.SquoteStart
                    QuoteCount = 1
                    RawFlag = PreviousC.lower()
                    if RawFlag == 'r':
                        #Include the r in the string
                        Start -= 1
                elif C == '"':
                    #Start of double quoted something
                    State = st.DquoteStart    
                    QuoteCount = 1
                    RawFlag = PreviousC.lower()
                    if RawFlag == 'r':
                        #Include the r in the string
                        Start -= 1
            elif State == st.DquoteStart:
            #
            # --- Start of double quoted something ---
            #
                if C == '"':
                    #We have a second or third quote
                    QuoteCount += 1
                    if QuoteCount == 3:
                        #This is the start of a triple double-quoted comment
                        State = st.DQcomment
                        ClosingQuotesNeeded = 3
                        QuoteCount = 0
                        Q3d = not Q3d
                else:
                    #We have something other than a quote
                    if QuoteCount == 1:
                        #Start of double quoted string
                        State = st.QuoteRun
                        ClosingQuotesNeeded = 1
                        ClosingQuoteType = '"'
                        QuoteCount = 0
                    else:
                        #It was simply a double quoted empty string
                        Result.append({'Start':Start, 'Length':J-Start, 'Class':'string'})
                        State = st.Idle
                    #In neither case do we advance    
                    Advance = 0 
            #
            # --- In triple double-quoted comment ---
            #
            elif State == st.DQcomment:
                if C == '"':
                    QuoteCount += 1
                    if QuoteCount == 3:
                        #triple double-quoted comment ends
                        Result.append({'Start':Start, 'Length':J-Start+1, 'Class':'comment'})
                        State = st.Idle
                        Q3d = not Q3d
                else:
                    #Non-quote resets quote-count
                    QuoteCount = 0        
            #
            # --- Start of single quoted something ---
            #
            elif State == st.SquoteStart:
                if C == "'":
                    #We have a second or third quote
                    QuoteCount += 1
                    if QuoteCount == 3:
                        #This is the start of a triple single-quoted string
                        State = st.QuoteRun
                        ClosingQuotesNeeded = 3
                        ClosingQuoteType = "'"
                        QuoteCount = 0
                        Q3s = not Q3s
                else:
                    #We have something other than a quote
                    if QuoteCount == 1:
                        #Start of single quoted string
                        State = st.QuoteRun
                        ClosingQuotesNeeded = 1
                        ClosingQuoteType = "'"
                        QuoteCount = 0
                    else:
                        #It was simple a single quoted empty string
                        Result.append({'Start':Start, 'Length':J-Start, 'Class':'string'})
                        State = st.Idle
                    Advance = 0
            elif State == st.QuoteRun:
            #
            # --- Inside a quoted string ---
            #        
                #Note that this state looks after strings of all types except triple double-quoted strings,
                #    which for colorizing pursposes are considered to be comments.
                if C == ClosingQuoteType:
                    QuoteCount += 1
                    if QuoteCount == ClosingQuotesNeeded:
                        #single-quote string ends
                        Result.append({'Start':Start, 'Length':J-Start+1, 'Class':'string'})
                        State = st.Idle
                        if ClosingQuotesNeeded == 3:
                            #String just closed was a Q3s
                            Q3s = not Q3s
                elif C == '\\' and RawFlag <> 'r':
                    #Possible an escaped character in non-raw string
                    State = st.Escape
                    PhraseStartJ = J        
                else:
                    #Non-quote resets quote-count
                    QuoteCount = 0        
                    if C == '%':
                        #Start of format phrase
                        State = st.PhraseStart
                        #Since this may or may not be the start of a format phrase, we need to keep track
                        #    of where it started for use later.
                        PhraseStartJ = J
            elif State == st.Escape:
            #
            # --- possibly an escaped character ---
            #
                if C in 'abfnrtv\\':
                    PhraseLen = J-PhraseStartJ+1
                    #First we have to issue the part of the string that came before the escape sequence
                    Result.append({'Start':Start, 'Length':PhraseStartJ-Start, 'Class':'string'})
                    #Now issue the actual escape section
                    Result.append({'Start':PhraseStartJ, 'Length':PhraseLen, 'Class':'escape'})
                    #And having finished with the secape we are back in string mode
                    Start = J+1
                State = st.QuoteRun
            elif State == st.PhraseStart:
            #
            # --- At start of format phrase ---
            #
                if C == "'":
                    #A quote may be the start of the end of the string and hence bounces us out of phrase
                    State = st.QuoteRun
                    Advance = 0
                elif C == "(":
                    #Start of a key specifier
                    State = st.PhraseKey1
                elif C in "0- +#":
                    #A flag
                    State = st.PhraseFlags
                elif C in "123456789":
                    #Start of width
                    State = st.PhraseWidth
                elif C == '.':
                    #Dot signals precision is next
                    State = st.PhrasePrecision
                else:
                    #Anything else had better be a type
                    State = st.PhraseType
                    Advance = 0
            elif State == st.PhraseKey1:
            #
            # --- format phrase: expecting first character of key name ---
            #                                 
                if C in Alpha:        
                    #Key name first character is valid
                    State = st.PhraseKeyN
                else:
                    #First character of key name not valid
                    State = st.QuoteRun
                    Advance = 0
            elif State == st.PhraseKeyN:
            #
            # --- format phrase: expecting additional characters of key name or end-of-key-name
            #
                if C == ")":
                    #Key name ends;
                    State = st.PhraseFlags        
                elif not C in AlphaMeric:
                    #Character not a valid name character
                    State = st.QuoteRun
                    Advance = 0
            #
            # --- expecting format phrase flags or later ---
            #        
            elif State == st.PhraseFlags:           
                if C in "0- +#":
                    #A flag
                    pass
                elif C in "123456789":
                    #Start of width
                    State = st.PhraseWidth
                elif C == '.':
                    #Dot signals precision is next
                    State = st.PhrasePrecision
                else:
                    #Anything else had better be a type
                    State = st.PhraseType
                    Advance = 0
            #
            # --- expecting format phrase width or later ---
            #        
            elif State == st.PhraseWidth:
                if C in "123456789":
                    #width continues
                    pass
                elif C == '.':
                    #Dot signals precision is next
                    State = st.PhrasePrecision
                else:
                    #Anything else had better be a type
                    State = st.PhraseType
                    Advance = 0
            #
            # --- expecting format phrase precision or later ---
            #                    
            elif State == st.PhrasePrecision:
                if C in "0123456789":
                    #precision digits
                    pass
                else:
                    #Anything else had better be a type
                    State = st.PhraseType
                    Advance = 0
            #
            # --- expecting format phrase type ---
            #
            elif State == st.PhraseType:
                PhraseLen = J-PhraseStartJ+1
                if (not C in "diufFeEgGoxXcrs%") or (C == '%' and PhraseLen <> 2):
                    #not a format phrase
                    State = st.QuoteRun
                    Advance = 0
                else:
                    #Cowabunga: we have a complete, valid format phrase!
                    #First we have to issue the part of the string that came before the format
                    #    phrase as a string.
                    Result.append({'Start':Start, 'Length':PhraseStartJ-Start, 'Class':'string'})
                    #Now issue the actual format phrase
                    Result.append({'Start':PhraseStartJ, 'Length':PhraseLen, 'Class':'format'})
                    #And having finished with the phrase we are back in string mode
                    Start = J+1
                    State = st.QuoteRun
            #
            # --- Singleton ---
            #        
            elif State == st.Singleton:
                try:
                    NewColor = self.ColorDict[C]
                    if NewColor <> Color:
                        #New char is single but not of same color
                        raise KeyError
                except KeyError:
                    #this character is not same color as current one
                    Result.append({'Start':Start, 'Length':J-Start, 'Class':'single', 'Color':Color})
                    State = st.Idle
                    Advance = 0
                        
            elif State == st.Name:
            #
            # --- Name ---
            #        
                if C in AlphaMeric:
                    #Name continues
                    pass
                else:
                    #Name ends
                    Name = Line[Start:J]
                    if Name == 'self' or (len(Name) > 4 and Name[:2] == '__' and Name[-2:] == '__'):
                        Class = 'special'
                    elif self.KeywordDict.has_key(Name):
                        Class = 'keyword'
                    elif __builtins__.has_key(Name): 
                        Class = 'builtin'    
                    else:        
                        Class = 'other'
                    if Class <> 'other':    
                        Result.append({'Start':Start, 'Length':J-Start, 'Class':Class})
                    State = st.Idle
                    Advance = 0
        InfoState = 0
        if State == st.DQcomment:
            #We were in a triple double-quoted comment at the end
            Result.append({'Start':Start, 'Length':J-Start+1, 'Class':'comment'})
            InfoState = 1
        elif State == st.QuoteRun:
            #We were in a quoted string at the end
            Result.append({'Start':Start, 'Length':J-Start+1, 'Class':'string'})
            if ClosingQuotesNeeded == 3:
                InfoState = 2
                if RawFlag == 'r':
                    InfoState = 3
            else:
                #We were in an unclosed non-triple quoted string
                InfoState = -1    
        elif State in (st.PhraseStart, st.PhraseKey1, st.PhraseKeyN, st.PhraseFlags
            ,st.PhraseWidth, st.PhrasePrecision, st.PhraseType):
            #We were in a format phrase in a quoted string at the end          
            PhraseLen = J-PhraseStartJ+1
            Result.append({'Start':Start, 'Length':PhraseStartJ-Start, 'Class':'string'})
            #Now issue the actual format phrase
            Result.append({'Start':PhraseStartJ, 'Length':PhraseLen, 'Class':'format'})
            InfoState = 2
            if RawFlag == 'r':
                InfoState = 3
        #
        # Supply color information for any entry that doesn't already have it.
        #
        for Entry in Result:
            if not Entry.has_key('Color'):
                Entry['Color'] = self.ColorDict[Entry['Class']]        
        #
        # Were done!
        #        
        return (InfoState,Result,HashFlag)
            
def NameVet(Name,AllowDot=False):
    """=u
    Check to see if we like a name.
    
    We like a name if it follow the Python rules, ie:
    o Starts with a letter or underscore.
    o Continues with letters, underscore or digits.
    """
    if len(Name) == 0:
        return False
    if AllowDot:
        AM = AlphaMeric + '.'    
    else:
        AM = AlphaMeric  
    if not Name[0] in Alpha:
        return False
    for C in Name[1:]:
        if not C in AM:
            return False
    return True                

def Tupalize(S):
    """=u
    Attempt to clean up a tuple.
    
    The argument S is supposed to be a string representing a single-level integer
        tuple. We apply some heruistics which may help to clean up poorly formed
        tuples. Technically the user is damn well supposed to key in properly 
        formed tuples. Somewhat less technically are willing to accept less than 
        pristine tuples.
        
    The result is an actual tuple or '???' if the tuple was pathalogical.
    """
    S = list(str(S))
    #toast everything but digits
    for I in range(len(S)):
        if not S[I] in '0123456789':
            S[I] = ' '
    S = ''.join(S)
    #Break into space delimited chunks
    S = S.split()
    #Supply delimiting commas
    S = ', '.join(S)
    #And enclosing parens
    if len(S) == 0:
        return ()
    try:
        result = eval('(%s,)'%S)        
    except:
        result = '???'
    return result        

def GeneralizedSaveFinalizeNumeric(Path):
    """=u
    A perversly safe way to finish a save.
    
    o Path is the full path name to the file which is being replaced, complete with
        appropriate extension; this file doesn't necessarily have to exist.
        For example, if saving a text file Path might be "/home/cam/text/whatever.txt"

    o Prior to calling this routine you must have written the new version of the file
        with the same name but an extension of "$$$". Continuing our example above, the
        new version file would be "/home/cam/text/whatever.$$$"

    o This routine:
        o Renames the current file to be of the form "file.ext.nnnn" where "nnnn" is a
          4-digit integer. The numeric value chosen is one greater than the hightest
          existing file of the given name and extension, or 0000 if no such files
          exist.
        o Renames the "$$$" file to be of the standard extension (eg "txt").
    """
    # Given a path like "/home/cam/text/whatever.txt" break it up into:
    # PathName: /home/cam/text/
    # FileFull: whatever.py
    # FileBase: whatever
    # FileExt:  .py
    PathName, FileFull = os.path.split(Path)
    FileBase, FileExt = os.path.splitext(FileFull)
    if PathName <> '':
        PathName += '/'
    #Find highest numeric extension on matching filenames
    Value = 0    
    for N in os.listdir(PathName+'.'):
        B, E = os.path.splitext(N)
        if B == FileFull and len(E) == 5 and E[0] == '.':
            #Filename matches and extension of correct length
            try:
                Temp = int(E[1:])
                Value = max(Value,Temp+1)
            except:
                #but its not an integer
                pass
    #Rename existing file
    try:
        os.rename(Path,Path+'.%4.4d'%Value)
    except OSError:
        #No original file
        pass                    
    #rename the new file to be the current file
    os.rename(PathName+FileBase+'.$$$',Path)

def MouseInWidget(w):
    """=u
    Given a widget, return mouse position with respect to the widget.
    
    The result is a tuple (x,y) giving the mouse position with respect to
    the upper left corner of the widget.
    
    Note that it is entirely possible that the mouse will be outside the widget.
    """
    #M is position of mouse on the screen
    M = w.winfo_pointerxy()
    #print 'M=%s'%`M`
    #G is geometry of the widget
    G = Rph.WidgetInScreen(w)
    return M[0]-G[2], M[1]-G[3]

class SlidingButtonBar(Frame):
    """=d
    A button bar widget with sliding buttons.
    """
    def __init__(self, _Master, _Schema, _Button=Button, **_kw):
        """
        Create the button bar.
        
        The sliding feature allows for more buttons than can be displayed in the
            frame at one time. Arrows on either end of the frame allow the user
            to slide the buttons left or right to expose currently hidden buttons.
            
        _Schema is a tuli of tuli's.
        
            o The first element is a 4-tuli of PhotoImage icons
                  for the left and right arrows:
                  o [0] Left pointing arrow, enabled
                  o [1] Left pointing arrow, disabled
                  o [2] Right pointing arrow, enabled
                  o [3] Right pointing arrow, disabled
            o Second and subsequent elemets each define one button to be added to the
                  button bar. Buttons are added left-to-right. Each element is a 4-tuli:
                  o [0] The name of the button. Optional. If you choose to name the button,
                            don't start the name with an underscore. If you choose not to
                            name the button, this should be an empty string or None.
                  o [1] The filename of the icon for this button.
                  o [2] The command to be invoked when the user clicks on this button.
                  o [3] The flyover hint for this button, empty if no hint needed.

            The arrow and button icons must be of identical height.
        
            The arrow icons must be of identical width.
        
            The button icons must be of identical width.
        
        _Button defaults to the standard Tkinter "Button" widget but you can 
            pass an alternate button to be used.
        
        The keyword arguments allowed are the same as the arguments allowed for the
            Tkinter "Frame" widget except for "height" and "width":
            
            o The height is implicitly set by the height of the arrow and button
              icons themselves. Therefore don't specify a height.
            
            o Width is the width IN BUTTONS, not pixels. The default value is 5.
              Width is a somewhat uncertain ally: the widget may end up being 
              smaller (if there is insufficient room) or larger (if pack
              fill in the X direction is enabled and the space allocated for
              the widget is large enough). About all width says is: Make the
              widget this size if there is enough room and if the pack options
              haven't set the stage for the widget to grow.

        Having created a widget, "w", of type SlidingButtonBar you can then access the
            individual buttons in two possible ways:
            
            o If you named the button, then "w.name" gets you the specified button 
              and is handy for hard-coded access to that button.
              
            o "w._Buttonlist" is a property of "w" and is handy for programatic
              access to the buttons. Each entry in "_Buttonlist" is a 2-list giving:
               
               o "[0]" The name of the button exactly as specified by "_Schema" (that is, an
                     empty string or "None" for unnamed buttons).
               o "[1]" The actual button widget.     
        
        """
        assert len(_Schema) >= 2, "Schema must have at least two entries"
        assert len(_Schema[0]) == 4, "Schema[0] must be of length four"
        #Fetch the arrow icons and do some checks.
        self._ArrowIcons = {}
        self._ArrowIcons['LeftNorm'] = _Schema[0][0]
        self._ArrowIcons['LeftGray'] = _Schema[0][1]
        self._ArrowIcons['RiteNorm'] = _Schema[0][2]
        self._ArrowIcons['RiteGray'] = _Schema[0][3]
        self._Height = None
        self._ArrowWidth = None
        for _Key,_Value in self._ArrowIcons.items():
            if self._Height == None:
                self._Height = _Value.height()
                self._ArrowWidth = _Value.width()
            else:
                assert _Value.height() == self._Height, "Arrow icons of different heights"
                assert _Value.width() == self._ArrowWidth, "Arrow icons of different widths"
        #Pad is the number of extra pixels we get horizontally and vertically per button.
        # Four of the eight are from the border provided by Button and you can make them
        # go away by creating the buttons with "bd=0". The remaining four are blank space
        # around each and button and you get it whether you want it or not. Personally I
        # would have gone without it but I could find no way to make it go away. Sort of 
        # like George Bush.
        self._Pad = 4
        #Use the verified height to set the height of our frame            
        _kw['height'] = self._Height+10
        #Scan over Schema doing sanity checks and while were at it, create a list of
        # the actual icons to go with the buttons. Since the first element of Schema
        # isn't a button we create a first dummy element in ButtonIcons so the indicies
        # correspond.
        if not _kw.has_key('borderwidth'):
            _kw['borderwidth'] = 2
        if not _kw.has_key('relief'):
            _kw['relief'] = GROOVE
        self._ButtonIcons = [None]
        self._ButtonWidth = None
        for _Entry in _Schema[1:]:
            assert len(_Entry) == 4, "Schema button entry not 4 long"
            assert type(_Entry[0]) in (type(''),type(None)), "Button name not string or None"
            if type(_Entry[0]) == type('') and len(_Entry[0]) > 0:
                assert _Entry[0][0] <> '_', "Button name starts with underscore"
            _Temp = _Entry[1]
            assert _Temp.height() == self._Height, "Button icon of incorrect height"
            self._ButtonIcons.append(_Temp)
            if self._ButtonWidth == None:
                self._ButtonWidth = _Temp.width()
            else:
                assert _Temp.width() == self._ButtonWidth, "Button icons of different widths"    
        self._TotalButtons = len(_Schema) - 1        
        #Get the width of the Frame straightened out. 
        try:
            self._WidthInButtons = _kw['width']
        except KeyError:
            self._WidthInButtons = 5
        assert self._WidthInButtons >= 1, "Width of zero buttons"
        self._FrameWidth = ((self._ArrowWidth+self._Pad)*2) + ((self._ButtonWidth+self._Pad)*self._WidthInButtons)        
        #Put the computed height in the stuff we pass then create the actual Frame
        _kw['width'] = self._FrameWidth
        Frame.__init__(self, _Master, _kw)
        self.pack_propagate(0)
        self.bind('<Configure>',self._on_Configure)
        #
        #Create but do not yet pack our buttons
        #    
        self._Buttonlist = []
        for _I in range(1,len(_Schema)):
            _Name,_Dummy,_Command,_Hint = _Schema[_I]
            _Icon = self._ButtonIcons[_I]
            _B = _Button(self,image=_Icon,command=_Command,bd=0)
            if _Hint:
                Rph.HintHandler(_B,_Hint)
            self._Buttonlist.append([_Name,_B])
            if _Name:
                self.__dict__[_Name] = _B    
        #Create and pack the left and right arrow buttons
        self._ArrowLeft = Button(self,image=self._ArrowIcons['LeftGray'],command=self._on_ArrowLeft,bd=0)
        self._ArrowLeft.pack(side=LEFT)
        self._ArrowRite = Button(self,image=self._ArrowIcons['RiteGray'],command=self._on_ArrowRite,bd=0)
        self._ArrowRite.pack(side=RIGHT)
        self._FirstShowing = 0
        self._NumberShowing = 0
        # Note that at this point no buttons have been packed in our widget, however, once
        # pack has the geometry figured out it calls the <Configure> method which will
        # display an appropriate number of buttons.
        #
        # The following handy-dandy information is available throughout:
        #
        # self._ArrowIcons      Dictionary of icons for the arrows
        # self._ArrowWidth      The width of each arrow in pixels
        # self._ButtonIcons     List of icons for each button
        # self._Buttonlist      For each button: [ButtonName,Button]
        # self._ButtonWidth     The width of each button in pixels
        # self._FirstShowing    The index of the first actually showing button
        # self._Height          Height of our frame in pixels
        # self._NumberShowing   The number of buttons presently showing
        # self._TotalButtons    The total number of buttons available for display
        # self._WidthInButtons  Maximum number of buttons we can display in the frame

    def _on_Configure(self,Event):
        #
        """
        This gets called at startup and when we get resized.
        """
        self._ButtonShifter(0)
        
    def _ButtonShifter(self,_Offset):
        #
        """
        Adjust first showing button by offset, then display as many buttons as will fit.
        
        A positive offset shifts buttons showing to the right, negative to the left.
        
        Regardless of what Offset calls for we will not display fewer
            buttons than possible.
        """        
        #Calculate the number of buttons we have room for.
        _T = self.winfo_width() - ((self._ArrowWidth+self._Pad) * 2)
        self._WidthInButtons = _T / (self._ButtonWidth+self._Pad)
        #Apply offset and some sanity checks to get the first button we want to show
        _T = self._FirstShowing + _Offset
        if _T < 0:
            #we can't show a button prior to the first one
            _T = 0
        if _T > self._TotalButtons - self._WidthInButtons:
            #nor will we leave button positions empty if we have buttons for them
            _T = max(self._TotalButtons - self._WidthInButtons,0)
        _FirstShowingNew = _T
        _NumberToShow = min(self._TotalButtons,self._WidthInButtons)
        #We know the first button we want to show and how many buttons we can show.
        # If these values are the same as what we are already showing then there
        # is nothing to do and we can go home early.
        if _FirstShowingNew == self._FirstShowing and _NumberToShow == self._NumberShowing:
            #that was easy
            return
        #First unpack any currently packed buttons and the right arrow
        for _I in range(self._FirstShowing,self._FirstShowing+self._NumberShowing):
            self._Buttonlist[_I][1].pack_forget()
        self._ArrowRite.pack_forget()
        self._NumberShowing = 0
        self._FirstShowing = _FirstShowingNew
        #Enable/disable the arrows as appropriate
        if  self._FirstShowing > 0:
            self._ArrowLeft.config(image=self._ArrowIcons['LeftNorm'])
        else:    
            self._ArrowLeft.config(image=self._ArrowIcons['LeftGray'])
        if  self._FirstShowing+_NumberToShow < self._TotalButtons:
            self._ArrowRite.config(image=self._ArrowIcons['RiteNorm'])
        else:    
            self._ArrowRite.config(image=self._ArrowIcons['RiteGray'])
        #Pack the little suckers
        for _I in range(self._FirstShowing,self._FirstShowing+self._WidthInButtons):
            if _I >= len(self._Buttonlist):
                #we ran out of buttons before running out of button locations
                break
            self._Buttonlist[_I][1].pack(side=LEFT,expand=YES)
            self._NumberShowing += 1
        #Clack on the right arrow
        self._ArrowRite.pack(side=LEFT)    
            
    def _on_ArrowLeft(self):
        #
        """
        User clicked on shift-left arrow
        """
        self._ButtonShifter(0-self._WidthInButtons)
        
    def _on_ArrowRite(self):
        #
        """
        User clicked on shirt-right arrow
        """
        self._ButtonShifter(self._WidthInButtons)        


class PromptDialog:
    """=d
    A simple dialog to prompt for a string value.
    
    "Title" is the title for the window.
    
    "Message" is the instruction to the user.
    
    "Prompt" is the initial value. If omitted, the Entry is initially blank.

    If "Help" is supplied then we add a help button and we invoke the specified help if
        the help button is pressed. User can also call up the supplied help by pressing
        the system help key (F1 at time of writing).

    If specified XY should be a tuple locating the upper-left corner of the dialog.
        If omitted we position near the mouse.    
        
    The result is returned as "self.Result".
    
    If the user cancels or exits by clicking on the window manager "close" button, then
        we return "None".
        
    Pressing the "Enter" key has the same effect as clicking "OK".
    Pressing the "Esc" key has the same effect as clicking "Cancel".    
    """
    def  __init__(self,Title='Query',Message='Message',Help=None,Prompt='',XY=None):
        """
        create the dialog.
        """
        self._Win = Toplevel()
        self._Win.title(Title)
        self.Result = None
        self.Help = Help
        Width = 300
        Height = 150
        if XY <> None:
            #User is placing us explicitly
            Geo = (Width,Height,X[0],Y[1])
        else:
            #position near the mouse    
            MouseX, MouseY = self._Win.winfo_pointerxy()
        
            Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
            if Geo[3]+Height+70 > self._Win.winfo_screenheight():
                #but don't run us off the bottom of the screen
                Geo[3] = max(self._Win.winfo_screenheight()-Height-70,0)
            if Geo[3] < 0:
                Geo[3] = MouseY    
        self._Win.geometry('+%s+%s'%(Geo[2],Geo[3]))        
        #
        # Message label
        #
        self.LabelStringVar = StringVar()
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar)
        self.OurLabel.pack(side=TOP,anchor='w',pady=10,padx=20,expand=YES,fill=BOTH)
        self.LabelStringVar.set(Rph.TextBreak(str(Message),34))    
        #
        # Entry area
        #
        self.OurEntry = Entry(self._Win)
        self.OurEntry.insert(0,Prompt)
        self.OurEntry.pack(side=TOP,padx=20)
        self.OurEntry.bind('<Return>',self.on_OK)
        self.OurEntry.bind('<Escape>',self.on_Cancel)
        #
        # Buttons
        #
        self.Buttons = Rph.ButtonBox(self._Win)
        self.Buttons.add('OK',command=self.on_OK)
        if Help <> None:
            self.Buttons.add('Help',command=self.on_Help)
        self.Buttons.add('Cancel',command=self.on_Cancel)
        self.Buttons.pack(side=TOP)
        #
        #be modal
        #
        self._Win.focus_set()
        Rph.Grabber(self._Win)
        self.OurEntry.focus_set()
        self._Win.wait_window()
        
    def on_OK(self,Event=None):
        self.Result = self.OurEntry.get()
        self._Win.destroy()

    def on_Help(self,Event=None):
        Help(self.Help)
        
    def on_Cancel(self,Event=None):
        self._Win.destroy()        
        

#------------------------------------------------------------------------------#
#                                                                              #
#                                MessageDialog                                 #
#                                                                              #
#------------------------------------------------------------------------------#
    
class MessageDialog:
    """=d
    A simple utility Message Dialog.

    "Title" is the window title.

    "Message" is the message to appear in the body of the dialog.
    
    If "Modal" is true then the dialog is modal and it doesn't go away until the 
        user closes it. If "Modal" is false then the dialog is not modal and it
        stays up until it's "Close" method is called.
        
    If "Modal" is false, then you can use the dialogs "Message(str)" method to
        update the message being displayed. Note that no buttons are displayed for
        non-modal dialogs, ever.
        
    If specified "XY" should be a tuple locating the upper-left corner of the dialog.
    
    If "Widget" is specified, we center the dialog on that widget. This option is
        ignored if XY is specified.
    
    If neither "XY" nor "widget" are specified,  we position near the mouse.    
        
    If "Buttons" is omitted you get a single 'Dismiss' button. Otherwise "Buttons" should 
        be a tuli of 2-element tulis, each of which gives:
            o [0] A string giving the text for the button, and
            o [1] The object to be returned when this button is pressed.
        
        The buttons are created left to right in the order you give them. When the user
            presses a button, it's object is returned as instance.Result

        The first button created is bound to the "Return" key, so choose your button
            order carefully. We draw a little border around this button to let the
            user know it's the default button.
            
        Usually there is a 'contrary' button which is the opposite of the 'affirmative'
            first button. We bind the contrary button to the "Escape" key. Indicate which
            is the contrary button by prefixing it's name with a tilde ('~'). The tilde
            is removed before the button. 
        
        If the user closes by clicking on the 'close' button in the upper right corner
            then instance.Result is None.
            
    "Justify" says how multiple lines are justified. The default is CENTER.            
    
    "Font" is the font for the label if a non-standard font is desired.

    If "Help" is supplied then we add a help button and we invoke the specified help if
        the help button is pressed. User can also call up the supplied help by pressing
        the system help key (F1 at time of writing).
    """

    def  __init__(self,Title='Information'
                      ,Message='You forgot the message, dumox'
                      ,Modal=1
                      ,XY=None
                      ,Widget=None
                      ,Buttons=None
                      ,Help=None
                      ,Justify=CENTER
                      ,Font=None
                      ,License=False):
        """
        Create the dialog.
        """
        self._Win = Toplevel()
        self._Win.title(Title)
        self.Result = None
        self.Help = Help
        Width = 300
        Height = 150

        if XY <> None:
            #User is placing us explicitly
            Geo = [Width,Height,XY[0],XY[1]]
        else:
            if Widget <> None:
                #A widget was passed; try to center us on it
                WidW,WidH,WidX,WidY = Rph.WidgetInScreen(Widget)
                #now center it there
                X = WidX + ((WidW-Width)/2)
                Y = WidY + ((WidH-Height)/2)
                Geo = [Width,Height,X,Y]
            else:    
                #position near the mouse    
                MouseX, MouseY = self._Win.winfo_pointerxy()
            
                Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
                #if Geo[3]+Height+70 > self._Win.winfo_screenheight():
                #    #don't run us off the bottom of the screen
                #    Geo[3] = max(self._Win.winfo_screenheight()-Height-70,0)
                #if Geo[3] < 0:
                #    Geo[3] = MouseY    
        #Try to keep us on the screen, ok?
        ScreenWidth = self._Win.winfo_screenwidth()
        ScreenHeight = self._Win.winfo_screenheight()
        if (Geo[0] + Geo[2]) > ScreenWidth:     #no falling off the right
            Geo[2] = ScreenWidth-Geo[0]
        if (Geo[1] + Geo[3]) > ScreenHeight:    #no falling of the bottome
            Geo[3] = ScreenHeight-Geo[1]            
        Geo[2] = max(0, Geo[2])                 #no falling off the left
        Geo[3] = max(0, Geo[3])                 #no falling off the top
        
        self._Win.geometry('+%s+%s'%(Geo[2],Geo[3]))        
        if Buttons == None:
            Buttons = [['Dismiss',None]]
        
        #message label
        self.LabelStringVar = StringVar()
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar,justify=Justify,font=Font)
        self.OurLabel.pack(anchor='w',pady=10,padx=20,expand=YES,fill=BOTH)
        self.LabelStringVar.set(Rph.TextBreak(str(Message),44))    
        HelpPlaced = False
        if Modal:
            #button bar across the bottom
            self.BB = Rph.ButtonBox(self._Win)
    	    self.BB.pack(side='top')
            FirstButton = True
            for T in Buttons:
                assert len(T) == 2, str(T)
                if T[0][0] == '~' and Help and not HelpPlaced:
                    #place help button just before the contrary button if possible
                    B = self.BB.add('Help')
                    B.bind('<ButtonRelease-1>',self.on_Help)
                    self._Win.bind(HelpButton,self.on_Help)
                    self._Win.bind('<F1>',self.on_Help)
                    HelpPlaced = True
                B = self.BB.add(T[0].replace('~',''))
                B.Result = T[1]
                B.bind('<ButtonRelease-1>',self.Close)
                if FirstButton:
                    #Draw a little border around the button to show it's the default
                    B['default'] = 'active'
                    self._Win.bind('<KeyPress-Return>',self.Enter)
                    self.EnterResult = T[1]
                    FirstButton = False
                if T[0][0] == '~':
                    #This is the contrary button, bind it to escape
                    self._Win.bind('<KeyPress-Escape>',self.Esc)
                    self.EscResult = T[1]
            if Help and not HelpPlaced:
                #Help button required but not yet placed
                B = self.BB.add('Help')
                B.bind('<ButtonRelease-1>',self.on_Help)
                self._Win.bind(HelpButton,self.on_Help)
                self._Win.bind('<F1>',self.on_Help)

            if License: 
                Message = ('Rapyd-Tk version %s\nCopyright 2010 Cam Farnell\n\n'
                    'Rapyd-Tk comes with ABSOLUTELY NO WARRANTY; for details click "Warranty". '
                    'This is free software, and you are welcome to redistribute it '
                    'under certain conditions; click "Conditions" for details.'%VersionNumber)

                self.Label2StringVar = StringVar()
                self.OurLabel2 = Label(self._Win,textvariable=self.Label2StringVar)
                self.OurLabel2.pack(anchor='w',pady=10,padx=20,expand=YES,fill=BOTH)
                self.Label2StringVar.set(Rph.TextBreak(str(Message),44))    
                
                self.BB2 = Rph.ButtonBox(self._Win)
        	self.BB2.pack(side='top')
                self.BB2.add('Warranty',command=self.on_Warantee)
                self.BB2.add('Conditions',command=self.on_Conditions)
                
            #be modal
            self._Win.focus_set()
            Rph.Grabber(self._Win)
            self._Win.wait_window()
        else:   
            self._Win.focus_set()
            self._Win.update_idletasks()

    def Enter(self,Event):
        self.Result = self.EnterResult
        self._Win.destroy()
            
    def Esc(self,Event):
        self.Result = self.EscResult
        self._Win.destroy()

    def on_Warantee(self):
        Help('gpl.warantee')
        
    def on_Conditions(self):
        Help('gpl.license')
            
    def Message(self,M):
        """
        Set the message to be displayed in the dialog.
        """
        self.LabelStringVar.set(M)
        self._Win.update_idletasks()    

    def on_Help(self,Event):
        Help(self.Help)

    def Close(self,Event=None):
        """
        Close the dialog. Not needed if dialog is modal.
        """
        try:
            self.Result = Event.widget.Result
        except:
            pass    
        self._Win.destroy()    


class ErrorDialog(MessageDialog):
    """=d
    A simple modal error dialog.

    If "Help" is true then a Help button is provided in addition to the
        usual "Dismiss" button.        
        
    Result is returned in w.Result. It is usually None unless a help button was
        requested AND the user clicked help in which case the result is 1.
    """
    def __init__(self,Message='This is a message',Modal=1,Help=0):
        """
        Create the dialog.
        """
        if Help:
            Buttons = [('Dismiss',None),('Help',1)]
        else:
            Buttons = [('Dismiss',None)]
        MessageDialog.__init__(self,Title='Error',Message=Message,Buttons=Buttons)

class HandlerReferencesDialog(ToplevelRP):
    """
    Dialog to show references to an event handler.
    
    HandlerName: A string giving the name of the handler.
    Refs: A tuple of references to the handler:
            [0] Widget name
            [1] Event string or command
    """
    def __init__(self, Master=None, **kw):
        self.HandlerName = kw['HandlerName']
        del kw['HandlerName']
        self.Refs = kw['Refs']
        del kw['Refs']
        kw['where'] = 'Center'

        apply(ToplevelRP.__init__,(self,Master),kw)
        #
        # Frame with label and references
        #
        #SFrame = Pmw.ScrolledFrame(self,labelpos='n'
        #    ,label_text='References to event handler %s'%self.HandlerName)
        if len(self.Refs) == 0:
            Msg = 'No Rapyd-Tk maintained bindings nor option commands reference event handler "%s".'%self.HandlerName
            Msg = Rph.TextBreak(Msg,50)
            L = Label(self,text=Msg)
            L.pack(side=TOP,pady=20,padx=20)
        else:
            #The more references the taller the frame, up to a limit.
            Fudge = min(400,100+(len(self.Refs)*18))
            L = Label(self,text='References to event handler: %s'%self.HandlerName)
            L.pack(side=TOP,pady=20,padx=20)
            #TheFrame = Pmw.ScrolledFrame(self,usehullsize=1,hull_height=Fudge,hull_width=350)
            #SFrame = TheFrame.interior()
            SFrame = Frame(self)
            SFrame.pack(side=TOP,expand=YES,fill=BOTH,padx=10)
            WHead = 'Refering widget'
            EHead = '<Event-string> or option-name'    
            Xp = 0
            LeftPad = 5 * ' '
            Label(SFrame,text=LeftPad+WHead).grid(row=0,column=0,sticky=E,padx=Xp)
            Label(SFrame,text=EHead).grid(row=0,column=1,sticky=W,padx=Xp)

            Label(SFrame,text=DashesToMatch(WHead,L)).grid(row=1,column=0,sticky=E,padx=Xp)
            Label(SFrame,text=DashesToMatch(EHead,L)).grid(row=1,column=1,sticky=W,padx=Xp)
            Row = 2
            for Widget,Event in self.Refs:
                Label(SFrame,text=Widget).grid(row=Row,column=0,sticky=E)
                Label(SFrame,text=Event).grid(row=Row,column=1,sticky=W)
                Row += 1
        Label(self).pack(side=TOP)
        #
        # Button bar
        #        
        self.Buttons = Rph.ButtonBox(self)
        B = self.Buttons.add('Dismiss',command=self.on_Dismiss)
        self.Buttons.add('Help',command=self.on_Help)
        self.Buttons.pack(side=TOP)

        self.bind('<Return>',self.on_Dismiss)
        self.bind('<Escape>',self.on_Dismiss)
        self.bind('<F1>',self.on_Help)

        #be modal
        self.focus_set()
        Rph.Grabber(self)
        self.wait_window()
            
    def on_Help(self,Event=None):
        Help('Dialog-HandlerReference',[self.HandlerName])

    def on_Dismiss(self,Event=None):
        """
        Close the dialog.
        """
        self.destroy()    

class HandlerRenameDialog(ToplevelRP):
    """
    Dialog to help user rename an event handler
    
    HandlerName: A string giving the present name of the handler.
    ExistingHandlers: A list of names of current handlers.
    """
    def __init__(self, Master=None, **kw):
        self.HandlerName = kw['HandlerName']
        del kw['HandlerName']
        self.HandlerList = kw['HandlerList']
        del kw['HandlerList']
        self.RefCount = kw['RefCount']
        del kw['RefCount']
        kw['where'] = 'Center'

        apply(ToplevelRP.__init__,(self,Master),kw)
        
        Label(self,text='Rename event handler').pack(side=TOP,pady=10)
        Label(self).pack(side=TOP)
        
        if self.RefCount == 0:
            Msg = ('No Rapyd-Tk maintained bindings nor command-options refer to this event handler.\n'
                'Changing the event handler name will not affect any Rapyd-Tk maintained bindings nor command-options.')
        else:
            Msg = ('%s Rapyd-Tk maintained binding{/s} or command-option{/s} refer{s/} to this event '
                'handler.\n{It/All of them} will be updated to refer to the new name chosen.')
        Msg = Rph.Plural(Msg,self.RefCount)
        Msg = Rph.TextBreak(Msg,50)
        Label(self,text=Msg).pack(side=TOP,padx=20)
        Label(self).pack(side=TOP)
        
        F = Frame(self)
        F.pack(expand=YES,fill=BOTH,padx=10,pady=10)

        L = Label(F,text='Current name: ')
        L.grid(row=0,column=0,sticky=E,pady=10)
        L = Label(F,text=self.HandlerName)
        L.grid(row=0,column=1,sticky=W)
        L = Label(F,text='New name: ',pady=10)
        L.grid(row=1,column=0,sticky=E)
        self.E = Entry(F)
        self.E.grid(row=1,column=1,sticky=W)
        self.E.insert(0,self.HandlerName)
        self.Result = None        
        
        #
        # Button bar
        #        
        self.Buttons = Rph.ButtonBox(self)
        self.Buttons.add('OK',command=self.on_OK)
        self.Buttons.add('Help',command=self.on_Help)
        self.Buttons.add('Cancel',command=self.on_Cancel)
        self.Buttons.pack(side=TOP)

        self.bind('<Return>',self.on_OK)
        self.bind('<Escape>',self.on_Cancel)
        self.bind('<F1>',self.on_Help)

        #be modal
        self.E.focus_set()
        Rph.Grabber(self)
        self.wait_window()
            
    def on_Help(self,Event=None):
        Help('Dialog-HandlerRename',[self.HandlerName])

    def on_OK(self,Event=None):
        """
        Return users choice.
        """
        NewName = self.E.get()
        if NewName in self.HandlerList and NewName <> self.HandlerName:
            ErrorDialog('There is already a handler named "%s".'%NewName,Help='Dialog-HandlerRename-Duplicate')
            return
        if not NameVet(NewName):
            ErrorDialog('"%s" is not a valid Python name.'%NewName,Help='Dialog-HandlerRename-BadName')
            return
        if NewName == self.HandlerName:
            #Leaving the name the same equivalent to clicking Cancel.
            NewName = None    
        self.Result = NewName                
        self.destroy()    

    def on_Cancel(self,Event=None):
        """
        Close the dialog.
        """
        self.Result = None
        self.destroy()    

if __name__ == '__main__':        
    pass