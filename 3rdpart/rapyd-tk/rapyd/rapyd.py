#!/usr/bin/python
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

VersionNumber = '0.1.2'

"""
Note: A tuli is a TUple or a LIst. I got tired of typing "tuple or list" all over the place.

Major classes, in the order in which they appear:

class LineMind         LineMind's purpose is to think about lines.
class MenuAids         A class to help with menu creation.
class WidreqRepository Where widget requestors live
class rpDndCanvas      A drag and drop enabled canvas to which we have added some features.
class rpDndCanvasWid   An rpDndCanvas which is specifically tailored to accept widreqs
class BindMixin        A mixin class specifically for classes the need to mess with bindings.
class rpDndCanvasTrash An rpDndCanvas which is specifically tailored to be a trash bin.
class TextEdit         Text editor for user access to source code.
class BindEdit         The bind editor widget that goes inside the Widgetator bind edit page
class ResizeBar        Provide two knobs in a bar for resizing a two column area.
class OptionEdit       This editor works on either widget options or pack options depending on argument Edit.
class Widgetator       The dreaded Widgetator
class WidReq           A widget requestor.
class Layout           The Layout area. This is the big one.
class ParkingLotEditor Our parking lot class
class GuiEditor        This is where users edit frames and widreqs on a form
class ConfigReader     Reads the config file and stores it in dictionary self.Info.

"""

#=m Macho classes
#=t Trivial classes
#=u Utility stuff

from Tkinter import *

# Somewhere around Python 2.5 Tkinter started return Tcl objects in places
#     where it previously returned strings. Thus we set "wantobjects" to
#     false to prevent things from breaking. 
import Tkinter
Tkinter.wantobjects = False
ENABLED = NORMAL
import copy
import ConfigParser
import cPickle
import dnd_realworld as DND
import os
import os.path
import random
import rpErrorHandler
import rpHelp
import rpOption as Rpo
import rpWidgets as Rpw
import sys
import time
import Tkdnd
import tkFont
import tkFileDialog
import traceback

DND.Verbosity = 0

True = 1
False = 0

#Line direction constants
DirnH = 0
DirnV = 1

class LineMind:
    """
    LineMind's purpose is to think about lines.
    
    It doesn't draw line but it does create a representation of lines and helps
        to answer questions about lines.
        
    LineMind works on a 10,000 square virtual grid. The upper-left corner of our 
        grid is (0,0) while the lower-right corner is (10000,10000).
    """
    def __init__(self):
        self.Clear()
        
    def __repr__(self):
        """
        Return representation of our current line information
        """
        Result = ['Dir   Pos  From    To Level']
        for T in self.__InfonList:
            Result.append(' %s  %5d %5d %5d %s'%('HV'[T['Dirn']],T['Pos'],T['From'],T['To'],T['Level']))
        return '\n'.join(Result)
        
    def Clear(self):
        """
        Clear all information about lines.
        """
        self.__InfonList = []
        
    def Gather(self):
        """
        Gather and return information about the lines in this instance.
        
        The result is a list where each list element is a tuple:
            [0] The level of this line.
            [1] A 3-tuple of information about the line:
                [0] X location of middle of line
                [1] Y location of middle of line
                [2] Direction (0/1) of line
        """
        Result = []
        for T in self.__InfonList:
            if T['Dirn'] == DirnH:
                X = (T['From'] + T['To']) / 2
                Y = T['Pos']
            else:
                X = T['Pos']
                Y = (T['From'] + T['To']) / 2
            Result.append((T['Level'],(X,Y,T['Dirn'])))        
        return Result
    
    def LevelFind(self,LineEnds):
        """
        Given endpoints of a line fragment, return the level of the line on which the fragment lies.
        
        LineEnds is a tuple (X1,Y1,X2,Y2)
        
        If the line fragment falls along a line we return it's Level.
        If the line fragment does not fall along a line we return None
        """
        X1,Y1,X2,Y2 = LineEnds
        assert X1==X2 or Y1==Y2,'Line can not be diagonal'
        if X1 == X2:
            #Line is vertical
            if X1 in (0,10000):
                #The line lies along left or right edge
                return 0
            Dirn = DirnV
            Pos = X1
            From = Y1
            To = Y2
        else:
            #Line is horizontal
            if Y1 in (0,10000):
                #The line lines on top or bottom edge
                return 0
            Dirn = DirnH
            Pos = Y1
            From = X1
            To = X2
        for Infon in self.__InfonList:
            if Infon['Dirn']==Dirn and Infon['Pos']==Pos and Infon['From']<=From and Infon['To']>=To:
                #We have a match
                return Infon['Level']
        return None
        
    def LineAdd(self,LineRequestor):
        """
        Add a new line.
        
        Info is a "line requestor" tuple of (X,Y,Dirn) where (X,y) locates the center of the line.
        
        The result is 1 if the add was successful, 0 if the requested line fell over top of an
            existing line, which is not allowed.
            
        Note that the new line is added to the lines already part of this instance and is thus
            subject to ending as soon is it runs into any existing line.            
        """        
        X,Y,Dirn = LineRequestor
        #Prior to intersecting with any previous lines, our new line extends from frame to frame
        From = 0
        To = 10000
        MaxIntersectorLevel = 1
        #Scan existing lines, adjusting From and To per other lines which we intersect.
        for Infon in self.__InfonList:
            T = self.__IntersectionFind(LineRequestor,Infon)
            if T == None:
                #Oops - LineRequestor is right on the Infon line
                return 0
            if T <> (None,None):
                #The lines would intersect. At this point:
                #    (X,Y) is the origin point of the new line
                #    (Tx,Ty) is the point at which the lines would meet
                Tx, Ty = T
                if Dirn == DirnH:
                    #The line is horizontal
                    if Tx < X:
                        #The intersection point is left of our origin
                        if Tx > From:
                            #This is a new closest-intersector
                            From = Tx
                            MaxIntersectorLevel = max(MaxIntersectorLevel, Infon['Level'])
                    else:
                        #The intersection point is right of our origin
                        if Tx < To:
                            #This is a new closest-intersector
                            To = Tx
                            MaxIntersectorLevel = max(MaxIntersectorLevel, Infon['Level'])
                else:
                    #The line is vertical
                    if Ty < Y:
                        #The intersection point is above our origin
                        if Ty > From:
                            #This is a new closest-intersector
                            From = Ty
                            MaxIntersectorLevel = max(MaxIntersectorLevel, Infon['Level'])
                    else:
                        #The intersection point is above our origin
                        if Ty < To:
                            #This is the new closest-intersector
                            To = Ty
                            MaxIntersectorLevel = max(MaxIntersectorLevel, Infon['Level'])
        #Position depends on direction
        if Dirn == DirnH:
            Pos = Y
        else:
            Pos = X
        #We have all the information, add new entry
        self.__InfonList.append({'Dirn':Dirn, 'Pos':Pos, 'From':From, 'To':To, 'Level':MaxIntersectorLevel+1})
        return 1
        
    def LineInsert(self,LineRequestor,Level):
        """
        Insert a line at the specified level.
        
        Result is 1 if all went well, 0 if new line fell exactly on an old line.
            In the later case our line information is not altered.
        
        Note that since the level is specified, the new line will be added as if
            it had been added prior to any lines of higher level.
            
        Note also that the specified level simply affects how the new line is added.
            There is no guarantee that the line will retain the level specified
            although the line will not be of a higher level than specified.
        """
        #Save copy of line info in case things go badly
        InfonCopy = self.__InfonList
        #Fetch info about existing lines
        Lines = self.Gather()
        #Toast the existing lines
        self.Clear()
        #Add our new line
        Lines.append((Level,LineRequestor))
        #Sort so we add them in the correct order
        Lines.sort()
        #Now rebuild all the lines
        for Level,Requestor in Lines:
            T = self.LineAdd(Requestor)
            if T == 0:
                #oops, something went badly
                self.__InfonList = InfonCopy
                return 0
        return 1
        
    """  - - - - - Internal details - - - - -    
        
    __InfonList holds information about our lines. Each entry is a "line infon" 
        dictionary with the following fields:
        ['Dirn'] The direction of this line.
        ['Pos']  The common position of the line (ie the Y position for a horizontal
                    line or the X position for a vertical line)
        ['From'] The lower end coordinate (eg left X for horizontal line)
        ['To']   The higher end coordinate (eg right X for horizontal line)
        ['Level'] The level of this line. See discussion below.
        
    Level. This is a characteristic of lines in a form. Functionally, lines at a
        given level can be drawn in any order without affecting the outcome but
        lower level lines must be drawn before higher level lines for things to
        work properly.
        
        The the four sides of the form are at level zero. To compute the level of
        any additional lines: the subject line is S. Line S terminates against two
        lines ST1 and ST2. The level of line S is 1+max(level(ST1),level(ST2)) which
        is to say one greater than the highest level it terminates against.
        
        Note that while the four sides of the form are at level zero, the lowest
            level of the internal lines is 2. We start at two so that should we
            wish to insert another outside line at a previous level, it can be
            inserted at level 1.
    """
        
    def __IntersectionFind(self,Line,Infon):
        """
        Given a line-requestor and a line-infon, return intersection information.
        
        The result is either an (x,y) tuple if the lines intersect or (None,None)
            if they do not intersect. If the line-requestor is EXACTLY ON the infon-
            line then we return a single None.
            
        Note that the line-requestor defines a line which starts at the specified 
            point and expands to hit both frame edges.
        """        
        X,Y,Dirn = Line
        #Check for line-requestor ON infon line
        if Infon['Dirn'] == DirnH:
            #Infon line is horizontal
            if Infon['From'] <= X and Infon['To'] >= X and Infon['Pos'] == Y:
                return None
        else:
            #Infon line is vertical
            if Infon['From'] <= Y and Infon['To'] >= Y and Infon['Pos'] == X:
                return None
        #If the lines are parallel they clearly don't intersect
        if Dirn == Infon['Dirn']:
            return (None, None)
        #Check for possible intersection
        Result = [None,None]
        if Dirn == DirnV:
            #line-requestor is vertical, infon-line is horizontal            
            if Infon['From'] <= X and Infon['To'] >= X:
                #We do intersect
                return (X,Infon['Pos'])
            else:
                #We do not intersect
                return (None,None)
        else:
            #line-requestor is horizontal, infon-line is vertical
            if Infon['From'] <= Y and Infon['To'] >= Y:
                #We do intersect
                return (Infon['Pos'],Y)
            else:
                #We do not intersect
                return (None,None)
                

class MenuAids:

    #Names of actions which can be bound to a key in an edit scheme.
    BindableActions = (
        ' Bottom' 
        ' Cut' 
        ' CutAppend' 
        ' Copy' 
        ' CopyAppend' 
        ' CopyToFile'
        ' Delete' 
        ' DeleteLine'
        ' Exit'
        ' FindMatch' 
        ' FormAlternate'
        ' FormSwapCodeLayout'
        ' Goto' 
        ' Indent'
        ' IndentBlock'
        ' ModuleAlternate'
        ' ModuleNext'
        ' Outdent'
        ' OutdentBlock'
        ' Paste'
        ' PasteFile'
        ' PopToLineNumber'
        ' ProgramExit'
        ' ProjectBuild'
        ' ProjectBuildRun'
        ' ProjectLoad'
        ' ProjectSave'
        ' ProjectSaveBuild'
        ' ProjectSaveBuildRun'
        ' PushLineNumber' 
        ' Recolorize' 
        ' Search'
        ' SearchAgain'
        ' SearchReplace'
        ' SelectAll'
        ' SwapWithTop'
        ' Top').split()

    def ActionMenuSetup(self):
        """
        Setup to begin a session of action menu generation
        
        ActionMenuList is a list of tuli's, where each tuli is:
            [0] The left part of the menu's text, eg "New Project"
            [1] The right part of the menu's text, eg "F6"
            [2] The method which is to be object of the menu's "command" option
            
        Adding menus is a two step process. First we accululate all the entries, then we
            add them to the menu. This allows us to compute the optimum width of the
            entries before adding them.    
        """
        self.ActionMenuList = []

    def ActionMenuAdd(self,Text,Action=None):
        """
        Prepare to add a choice representing an action to a menu.
        
        "Text" is the text to appear in this menu.
        "Action" if supplied, is the name of the action in question. If omitted
            or "None" then the action is derived from "Text" by putting a capital
            on each word and then squeezing out the spaces; thus text "Copy to file"
            becomes action "CopyToFile".
            
        The result is the index of the current item within the menu.            
        """
        #Derive Action name if necessary
        if Action == None:
            Action = Text.title().replace(' ','')
        #Get the event string, if any, for this action.    
        Event = self.ActionEventGet(Action)
        #Some events have silly names which we translate to something reasonable.
        Event = EventTranslate(Event)
        Command = eval('self.on_Action%s'%Action)
        self.ActionMenuList.append([Text,Event,Command])
        return len(self.ActionMenuList)-1

    def ActionMenuSep(self):
        """
        Note to add a seperator to the menu
        """
        self.ActionMenuList.append([None]*3)

    def ActionMenuGenerate(self,Menu):
        """
        Actually generate the menu items already specified by ActionMenuAdd/ActionMenuSep.
        """
        if self.ActionMenuList:
            #Figure out how much space we need
            MaxWid = 0
            for Left,Right,Command in self.ActionMenuList:
                if Command:
                    MaxWid = max(MaxWid, TextMeasure('%s      %s'%(Left,Right),Menu))
            #Create the menu entries based on that space
            for Left,Right,Command in self.ActionMenuList:
                if Command:
                    Label = PadToWidth(Left,Right,MaxWid,Menu)
                    Menu.add_command(label=Label,command=Command)
                else:
                    Menu.add_separator()    
        self.ActionMenuList = []                    

    def ActionEventGet(self,TargetAction):
        """
        Get a version of the event string, if any, for a specified action.
        
        "TargetAction" is the name of a Rapyd text edit action as defined in the config
            file, eg "Search". 
            
        If the specified action was defined in the config file then we return
            the event string with the opening and closing angle brackets removed.
            If the specified action was not defined, we return an empty string.    
        """
        Scheme = Cfg.Info['Schemes'][Cfg.Info['SchemeCurName']]
        for Action,Result in Scheme['Actions']:
            if Action == TargetAction:
                if Result[:1] == '<':
                    Result = Result[1:]
                if Result [-1:] == '>':
                    Result = Result[:-1]
                break
        else:            
            Result = ''
        Result = Result.replace('><','  ')    
        Result = Result.replace('Control','Ctrl')
        return Result            

    def GenerateBindings(self,BindTargetName):
        """
        Setup the key bindings as specified in the config file. Note that for this to work each
            Action Implementation Method must have a name of the form "on_Action<x>" where <x>
            is the name of the action as known by the config file.
            
        BindTargetName must be the name of the widget to which the action is to be bound.            
        """
        assert type(BindTargetName) == type('')
        Scheme = Cfg.Info['Schemes'][Cfg.Info['SchemeCurName']]
        for Action,EventString in Scheme['Actions']:
            Temp = 'self.%s.bind(EventString, self.on_Action%s)'%(BindTargetName,Action)
            ##D('TextEdit: binding: %s to self.on_Action%s'%(EventString,Action))
            try:
                exec(Temp)
            except AttributeError:
                #not every action is implemented by us
                pass

def DictPretty(SomeDir):
    """
    Convert a dictionary to a string with no more than one item per line
    """
    Keys = SomeDir.keys()
    Keys.sort()
    Result = ['{']
    for Key in Keys:
        Result.append('%s: %s'%(str(Key),str(SomeDir[Key])))
    Result.append('}')
    return '\n'.join(Result)

def DonorModulesUseScan(ModuleDescriptor):
    """
    Given a module descriptor return a dictionary of donor modules (eg Tkinter) used.
    
    A donor module is considered to be 'used' if any form in the Rapyd module contains
        a widget from the donor module.
        
    In the result the key is the donor module name while the value is the number of
        widgets in ModuleDescriptor which come from the donor module.
    """
    Result = {}
    for FormInfo in ModuleDescriptor['Forms']:
        for Widreq in FormInfo['Widreqs']:
            DonorModule = Widreq['ModuleName']
            try:
                Result[DonorModule] += 1
            except KeyError:
                Result[DonorModule] = 1
    return Result                

def DonorModuleUseReport(ProjectDescriptor,DonorModuleList):
    """
    Generate a report showing widgets used from specified donor modules.
    
    The result is a string with embedded newlines showing, for each use:
    
    D-module P-module Form Widget Name
    
    Where:
    
    D-module is the name of the donor module.
    
    P-module is the name of the rapyd project module.
    
    Form is the form within the module 
    
    Widget is kind of widget from the donor module eg Button
    
    Name is the name of the widget in the form eg MyButton
    
    """
    Result = [('Dmodule','Pmodule','Form','Widget','Name'),('-------','-------','----','------','----')]
    MaxLengths = [7,7,4,6,4]
    for ModuleDescriptor in ProjectDescriptor[1:]:
        Pmodule = ModuleDescriptor['Name']
        for FormInfo in ModuleDescriptor['Forms']:
            FormName = FormInfo['Name']
            for Widreq in FormInfo['Widreqs']:
                WidreqInstanceName = Widreq['Name']
                WidreqTypeName = Widreq['WidgetName']
                Dmodule = Widreq['ModuleName']
                if Dmodule in DonorModuleList:
                    #This widreq is from one of our donors 
                    Line = (Dmodule,Pmodule,FormName,WidreqTypeName,WidreqInstanceName)
                    for J in range(5):
                        MaxLengths[J] = max(MaxLengths[J],len(Line[J]))
                    Result.append(Line)    
    #Now convert the tuples to a string with each field widthed as necessary
    FormatString = ((' $-%ds'*5)%tuple(MaxLengths)).replace('$','%')
    for J in range(len(Result)):
        Result[J] = FormatString%Result[J]
    Result = '{f' + ('\n'.join(Result)) + '}'
    return Result

def HelpListPretty(TheList):    
    """
    Format a list of strings for use in a help message.
    
    As returned the list will form a series of tabbed lines in bold monospaced font.
    """
    return '\n'.join(['t {g%s}'%X for X in TheList])

def GenerateCommentBox(Text,Width):
    """
    Generate a comment box as specified.
    """
    A = '#%s#\n'%((Width-2)*'-')
    B = '#%s#\n'%((Width-2)*' ')
    TotalPad = Width-len(Text)-2
    LeftPad = TotalPad / 2
    RightPad = TotalPad - LeftPad
    C = '#%s%s%s#\n'%(LeftPad*' ',Text,RightPad*' ')
    return '%s%s%s%s%s'%(A,B,C,B,A)

def GenerateImportLines(ImportModuleList):
    """
    Given a list of import modules, return the proper lines to import them.
    
    The modules specified must be ones mentioned in the config file.
    
    Note: At text generation time we rely on this text starting with a line that says
        "import rpErrorHandler".
    """
    ImportModuleList.sort()
    #D('Import list=%s'%str(ImportModuleList))
    Result = ['import rpErrorHandler']
    for IM in ImportModuleList:
        Type = Cfg.Info['Modules'][IM]['ImportType']
        if Type == 'from':
            Result.append('from %s import *'%IM)
        elif Type == 'import':
            Result.append('import %s'%IM)
        else:
            raise Exception, 'Unknown import type "%s" for module "%s"'%(str(Type),IM)    
    Result.append('')
    Result = '\n'.join(Result)
    return Result

def GenerateInitLines(ImportModuleList,Indent):
    """
    Given a list of import modules, return the proper lines to do basic initialization.
    
    "Indent" is an integer saying how many spaces to put in front of the lines.
    
    Note: At text generation time we rely on this text starting with a line that says
        "Root =".
    
    """
    Result = []
    Indent = Indent*' '
    TkType = Cfg.Info['Modules']['Tkinter']['ImportType']
    if TkType == 'from':
        Result.append('%sRoot = Tk()'%Indent)
    else:
        Result.append('%sRoot = Tkinter.Tk()'%Indent)    
    if 'Pmw' in ImportModuleList:
        PmwType = Cfg.Info['Modules']['Pmw']['ImportType']
        if PmwType == 'from':
            Result.append('%sinitialise(Root)'%Indent)   
        else:
            Result.append('%sPmw.initialise(Root)'%Indent)

    if TkType == 'from':
        Result.append('%simport Tkinter'%Indent)
        Result.append('%sTkinter.CallWrapper = rpErrorHandler.CallWrapper'%Indent)
        Result.append('%sdel Tkinter'%Indent)
    elif TkType == 'import':
        Result.append('%sTkinter.CallWrapper = rpErrorHandler.CallWrapper'%Indent)
    else:
        raise Exception, 'Unknown import type "%s" for module "Tkinter"'%TkType    
    Result.append('%sApp = %s(Root)'%(Indent,Cfg.Info['ProjectName']))
    Result.append("%sApp.pack(expand='yes',fill='both')"%Indent)

    Result.append('')        
    Result = '\n'.join(Result)
    return Result            
    
def DiffFind(A,B,History=''):
    """
    Compare A and B, reporting any differences.
    
    A and B can be any Python type but mostly this is useful for comparing big honking
        nested lists, tuples or dictionaries which you know to be different *somewhere*
        in their depths but you would like to know exactly where.
    """
    if type(A) <> type(B):
        print('at %s A is type %s, B is type %s'%(History,type(A),type(B)))
        return
    if type(A) in (type([]),type(())):
        #list or tuple
        if type(A) == type([]):
            Type = 'list'
            Fmt = '[%s]'
        else:
            Type = 'tuple'
            Fmt = '(%s)'
        if len(A) <> len(B):    
            print('at %s %s A is length %s, %s B is length %s'%(History,Type,len(A),Type,len(B)))
            return
        for J in range(len(A)):
            DiffFind(A[J], B[J], History+(Fmt%J) )
    elif type(A) == type({}):
        #dictionary
        Akeys = A.keys()
        Bkeys = B.keys()
        Akeys.sort()
        Bkeys.sort()
        if Akeys <> Bkeys:
            print 'at %s dictionarys have different keys:'
            print 'A_keys: %s'%str(Akeys)
            print 'B_keys: %s'%str(Bkeys)
            return
        for Key in A.keys():
            if not B.has_key(Key):
                print ('At %s{ A has_key "%s" but B does not'%(History,Key))
                return
            DiffFind(A[Key],B[Key],History+('{%s}'%repr(Key)))
    else:
        #Not list, tuple, or dictionary
        if A <> B:
            print 'at %s items of type %s are not equal'%(History,type(A))        
            print '---------- A ----------'
            print str(A)
            print '---------- B ----------'
            print str(B)
                
def CanvasToGeneric(XY,CanvasSize):
    """=v
    Convert an "(X,Y)" pair from Canvas to Generic coordinates.
    
    Generic coordinates work on a virtual 10,000 x 10,000 grid.
    """
    X = int(round((float(XY[0]) / float(CanvasSize[0])) * 10000.0))
    Y = int(round((float(XY[1]) / float(CanvasSize[1])) * 10000.0))
    return [X,Y]

def GenericToCanvas(XY,CanvasSize):
    """=v
    Convert an "(X,Y)" pair from Generic to Canvas coordinates
    """
    X = int(round((float(XY[0]) / 10000.0) * float(CanvasSize[0])))
    Y = int(round((float(XY[1]) / 10000.0) * float(CanvasSize[1])))
    return [X,Y]

def Intify(X):
    """=u
    Return X as an integer if possible or as received if not possible.
    """
    try:
        X = int(X)
    except:
        pass
    return X        

def PadToWidth(LeftPart,RightPart,Width,Widget):
    """
    Given left and right parts, return string of specified width in pixels.
    
    o "LeftPart" is the string to be left justified in the result.
    o "RightPart" is the string to be right justified in the result.
    o "Width" is the desired width, in pixels, of the result.
    o "Widget" the calculation is done with reference to the font set for this widget.
    
    Note that since we pad with space characters, the result will be as close as
        possible to the target size but will not necessarily be exactly the number
        of pixels requested.
    """
    UsedPixels = TextMeasure(LeftPart+RightPart,Widget)
    PadPixels = Width - UsedPixels
    PadCount = int(round(float(PadPixels) / float(TextMeasure(' ',Widget))))
    ##D('Width=%s UsedPixels=%s PadPixels=%s PadCount=%s'%(self.MenuWidthCurrent
    ##    ,UsedPixels,PadPixels,PadCount))
    return '%s%s%s'%(LeftPart,' '*PadCount,RightPart)

def TextMeasure(Text,Widget):
    """=u
    Measure size of "Text", in pixels, if displayed in "Widget".
    
    I lifted this straight out of Idle. Thanks Guido, it's not something I would have
        figured out on my own.
    """
    return int(Widget.tk.call("font", "measure", Widget["font"]
        ,"-displayof", Widget.master, Text ))
        
def TextMeasureHeight(Widget):
    """
    Measure the height needed for a font of a widget
    """        
    return int(Widget.tk.call("font", "metrics", Widget["font"]
        ,"-displayof", Widget.master, '-linespace' ))
        
def DashesToMatch(Text,Widget):
    """
    Generate a string of dashes of about the same width as "Text"
    
    Widget is the widget in which they are to be displayed.
    """        
    DashWidth = TextMeasure('-',Widget)
    TextWidth = TextMeasure(Text,Widget)
    return int(round(float(TextWidth) / float(DashWidth))) * '-'

def DecomposeHandlerName(HandlerName,WidgetName):
    """=u
    Attempt to decompose a standard EventHandler name.
    
    Standard event handler names are of the form:
    
        "on_widget_event"
        
    Where "widget" is the name of the widget and "event" is the abbreviated version
        of the event string.
        
    This routine checks the passed handler name and returns the event string
        abbreviation as the result if:
        
    o The HandlerName is of the form A_B_C, and
    o The A part is "'on'", and
    o The B part matches the passed WidgetName.
    
    Otherwise we return None.
    """
    Temp = HandlerName.split('_',2)
    if len(Temp) <> 3:
        return None
    if Temp[0] == 'on' and Temp[1] == WidgetName:
        return Temp[2]
    return None    

def ActionSubstitutionsGenerate():
    """
    Set text editor action substitutions for the help system    
    
    Generate a help global substitutions for each text-editor action. These
        allow us to mention the action keys even though we don't know what they
        are at help writing time. Example: assuming action "SelectAll" is currently
        bound to <Alt-a> then we generate these this substitution entry:
        
        $tActionSelectAll  Alt-a
        
        For those actions which the schema ignores we generate a translation to "None" (thats the text
        string "None" not the Python object None) which is a link to topic "edit-schema.no-bind" which
        explains that the schema didn't supply a key binding for this action.
    """
    #AllActions starts as a list of all named editor actions. As we process bindings
    #    from the schema we remove the corresponding name from the list.
    AllActions = MenuAids.BindableActions[:]
    for Action,Event in Cfg.Info['Schemes'][Cfg.Info['SchemeCurName']]['Actions']:
        AllActions.remove(Action)
        Event = EventTranslate(Event)
        OldTextT = '$tAction%s'%Action
        NewTextT = Event
        Help.AddSubstitution([OldTextT,NewTextT])
    #If AllActions isn't empty then those actions have no binding and we generate 
    #    translations to "None".
    NewTextT = '{LNone=edit-schema.no-bind}. (The editor schema "%s" did not bind this function to any key)'% \
        Cfg.Info['SchemeCurName']
    for Action in AllActions:
        OldTextT = '$tAction%s'%Action
        Help.AddSubstitution([OldTextT,NewTextT])

def EventTranslate(S):
    """
    Translate text key-names to graphics in an event string.
    
    Tk uses long-winded text names for many of the standard ASCII characters,
        eg "bracketleft" for "[". If there are any such long-winded names
        in the string, they are replaced with their ASCII graphic character.
    
    """
    Xlist = (
            ('bracketright',']'),
            ('bracketleft','['),
            ('asciicircum','^'),
            ('underscore','_'),
            ('parenright',')'),
            ('numbersign','#'),
            ('braceright','}'),
            ('asciitilde','~'),
            ('apostrophe',"'"),
            ('semicolon',';'),
            ('parenleft','('),
            ('braceleft','{'),
            ('backslash','\\'),
            ('ampersand','&'),
            ('quotedbl','"'),
            ('question','?'),
            ('asterisk','*'),
            ('percent','%'),
            ('greater','>'),
            ('period','.'),
            ('exclam','!'),
            ('dollar','$'),
            ('slash','/'),
            ('minus','-'),
            ('grave','`'),
            ('equal','='),
            ('comma',','),
            ('colon',':'),
            ('plus','+'),
            ('less','<'),
            ('bar','|'),
            ('at','@'),
            )
    for Long,Short in Xlist:
        if S.find(Long) <> -1:
            S = S.replace(Long,Short)
    return S        

def Wow(self, FuncName, Arg):
    """
    Wow indeed.
    
    I think this function deserves some sort of merit badge, possibly for obscurity.
    
    This function returns a nameless function which takes zero through two arguments.
        The nameless function's job is to execute the function whose NAME was passed
        in paramater FuncName with the argument passed in Arg.
        
    This isn't just an exercise to see how much obscurity could be stuffed into one
        line. Let me explain. Many Tkinter widgets have a 'command' option where
        you get to supply a method to be executed when something happens. If you have
        no need to pass the method any arguments then you can simply code this:
        
        "Button(yadayada, command=self.MyMethod)"
            
    and "self.MyMethod" will be called at the appropriate time. There are
        some occasions when it would be useful to be able to pass an argument to
        the called method but Tkinter makes no provision for doing so. You can
        get around this by using lambda to create a nameless function which in
        turn calls self.MyMethod with an argument. If we want to pass the argument
        string "'banana'" to self.MyMethod we could code:
        
        "Button(yadayada, command=lambda s=self, a='banana': s.MyMethod(a))"
            
    but that lambda expression is long winded, hard to remember and easy to
        mis-type. That's where the function "Wow" comes in; it does the messing
        around with lambda for you. Using Wow we code:
        
        "Button(yadayada, command=Wow(self,'MyMethod','banana'))"
            
    which is vastly less error prone since we simply give Wow self, the name
        of the function and the argument to be passed to the function.    
        
    *Note:* Do remember that you have to pass the *name* of your function, as a string,
        not the function itself. 
    """
    assert type(FuncName) == type(''), 'You need to pass the NAME of a function, not an actual function'
    return eval('lambda s=self, a=Arg: s.%s(a)'%FuncName)

def D(*Stuff):
    """
    This simply prints the arguments. 
    
    The point of using this, rather than 'print', is that once were done debugging 
    we can easily search for and remove the 'D' statements.
    """
    for T in Stuff:
        print T,
    print

def E(*Stuff):
    """
    This is like D but it prints to a file
    """
    try:
        F = open('D.txt','a')
        for T in Stuff:
            F.write(str(T))
        F.write('\n')
    finally:
        F.close()    

def NameWidReq(Default,WhichForm=None):
    """
    Generate an arbitrary, non-conflicting name for a widreq.
    
    Default is the default base name (eg "Button") for this type of 
        WidReq. We scan all the  WidReqs in the currently selected
        herd and return the first available name, eg "Button1".
        
    Normally we look in the current herd but it "WhichForm" is given
        then we look in the specified herd. If "WhichForm" is a tuli
        then we return a name that exists in none of the specified
        herds.
    """
    if type(WhichForm) in (type(''),type(None)):
        ListOfHerds = [WhichForm]
    else:
        assert type(WhichForm) in (type(()),type([]))    
        ListOfHerds = WhichForm
    Xlist = []
    Default = Cfg.Info['ManglePrefix'] + Default
    LD = len(Default)
    for WhichHerd in ListOfHerds:
        assert type(WhichHerd) in (type(''),type(None))
        for Name in Repo.ListWidreqs(WhichHerd):
            if Name[:LD] == Default:
                #the base portion of the names matches
                try:
                    Number = int(Name[LD:])
                    if Number > len(Xlist):
                        Xlist.extend([0] * (Number-len(Xlist)))
                    Xlist[Number-1] = 1    
                except:
                    pass
    Xlist.append(0)
    for J in range(len(Xlist)):
        if Xlist[J] == 0:
            return '%s%s'%(Default,J+1)                    

def BlankToNone(Arg):
    """
    If Arg is an empty string return None, else return Arg.
    """
    if type(Arg) == type('') and Arg.strip() == '':
        return None
    return Arg    

def BBToSize(BB):
    """
    Given a bounding box (x1,y1,x2,y2) return the (x,y) size of the box
    """
    return (BB[2]-BB[0], BB[3]-BB[1])

def BBToCenter(BB):
    """
    Given a bounding box (x1,y1,x2,y2) return the (x,y) center.
    """
    return ((BB[2]+BB[0])/2, (BB[3]+BB[1])/2)

def ReverseDictLookup(Dict,Value):
    """
    Do a reverse lookup on a dictionary
     
    Given a dictionary and a value, return the first key which matches
        Value. If there is more than one matching value then you simply
        get whatever is the first we find. Don't depend on it always being
        the same one. If there is no matching value we raise an error.
    """
    for K,V in Dict.items():
        if V == Value:
            return K
    raise Exception, "ValueError: Value=%s, Dict=%s"%(Value,Dict)

class EntryPixel(Entry):
    """=t
    An Entry widget that takes it's width specification in pixels.
    
    You MUST specify a width and (since Entry widgets actually get sized in 
        character multiples) you will get the largest possible Entry that does 
        not exceed the number of pixels specified.
    """
    def __init__(self, Master, **kw):
        """
        Create the entry widget.
        """
        assert kw.has_key('width'), 'You MUST specify a width'
        I = Cfg.Info['Metrics']['Entry']
        kw['width'] = (kw['width'] - I[0]) / I[1]
        apply(Entry.__init__,(self,Master),kw)

class LabelPixel(Label):
    """
    A text Label widget that takes it's width specification in pixels.
    
    You MUST specify a width and (since text Label widgets actually get sized 
        in character multiples) you will get the largest possible Label that 
        does not exceed the number of pixels specified.
    """
    def __init__(self, Master, **kw):
        """
        Create the Label widget.
        """
        assert kw.has_key('width'), 'You MUST specify a width'
        I = Cfg.Info['Metrics']['Label']
        kw['width'] = (kw['width'] - I[0]) / I[1]
        apply(Label.__init__,(self,Master),kw)

class WidreqRepository:
    """=m
    Where widreqs live.
    
    All widreqs live in this repository, aggregated into herds. Each herd has a unique
        name. Each widreq within a herd has a unique name.
        
    Anyone is allowed to send requests to this repository, but they have to register
        themselves with the repository before they can issue requests.
        
    Requests issued to the repository are just that, requests. The action they request
        may or may not happen depending on circumstances. All requests return 1 if they
        succeed or "(reason-string, decliner, flag)" if they do not, further details below.
        
    At any given time only one herd is the currently selected herd. In order to request
        an action against a particular widreq it has to be in the selected herd.
                
    Requests may be issued against a herd or against a particular widreq of the currently
        selected herd. The possible requests are:
        o Herd, create 
        o Herd, delete
        o Herd, select
        o Herd, rename
        o Widreq, create
        o Widreq, delete
        o Widreq, select
        o Widreq, rename
        o Widreq, relocate
        
    When the currently selected Widreq is deleted, if the herd from which it was 
        deleted is not empty then some other widreq is selected, pretty much at random.        
        
    In addition to placing requests, registerd repository users can bind to various
        repository events. By way of explanation, lets talk about how requests are
        processed. The repository handles each request in three phases:
        
        o The Query Phase. In this phase, anybody who is interested is asked if they
          are OK with the action proposed by the request. If any of the interested
          parties are not OK with it then they supply a reason string, the request
          is denied, the originator of the request gets the reason string as part of the
          result and that's the end of the process. If ALL interested parties are OK
          with the proposed action then we continue on the the action phase.

        o The Action Phase. The action proposed by the request is carried out and we
          continue on to the notify phase.

        o The Notify Phase. All interested parties are notified that the action has
          been carried out.  
    
    Registered users can bind a callback function to the Query and/or Notify phases
        of any of the possible requests except WidreqRelocate. Binding to the Query 
        phase gives interested parties a chance to say yes or no to any proposed 
        action, while binding to the Notify phase allows any interested parties to 
        keep themselves up to date about changes.
        
    WidreqRelocate moves a widreq from a specified herd to the currently selected 
        herd and it is a bit of an odd duck. You can't bind to it specificially 
        because it actually is composed of a delete from the specified herd and 
        a create in the current herd (both of which can be bound to). In order 
        to do the relocation cleanly we first do queries on the proposed deletion 
        and creation; if everyone is OK with that, and if the name doesn't conflict 
        in the current herd, then the relocation takes place.    
        
    Any given repository user can have at most *one* function bound to any
        particular event. For example, HerdCreateQuery is a specific event and a
        given user can bind at most one function to that event. If a particular 
        repository user calls "Bind" twice with the same event the then second binding 
        *replaces* the first binding; it does not cause two functions to be bound to 
        the same event. 

    When a widreq related request (WidreqCreate/Delete/Select/Rename) is processed,
        callbacks are done only to those functions which pertain to the herd against
        which the widreq request is happening. It works like this. When a widreq 
        related binding (eg WidreqCreateQuery) is created, the name of the current
        herd is noted with the binding. When a widreq related request is processed,
        we call bound callback functions only if the current herd matches the herd
        noted in the binding. Thus code which cares about herd 'A' gets callbacks
        only pretaining to herd 'A' and not about herds 'B', 'C' etc.

    Query and Notify callback functions are passed three arguments:
    
            o The event name eg 'WidreqCreate'
            o The A and B arguments from the request
    
        A query function should return:
        
            o 1 if it is ok with the request, or
            o "(<reason string>,<boolean>)" if it is not ok with the request
                Reason string should explain it's objection
                Boolean should be 1 if the user has been notified, otherwise 0

    *Tentative requests:* There are times when users want to find out if a particular
        request would succeed, without actually carrying out the request. For example,
        a repository user may want to find out if creating a new widreq now is 
        acceptable to all interested parties. They could post a 'WidreqCreate' request
        and see if it succeeds, but if it does then at the end of that process there
        is an actual new widreq whereas all the user wanted to find out was if
        creating one would be *acceptable;* it didn't actually want to create one yet.
        There is no specific repository method to do a tentative query, but there is
        an easy solution: if the user who initiates a request is also bound to the
        corresponding 'query' event then the widreq repository GUARANTEES THAT THE
        INITIATOR OF THE REQUEST WILL BE QUERIED *LAST.* Since the querying process
        terminates on the first objection, if the initiating process is in fact
        queried it knows that no other user objected to the request. At this point
        the initiating user can (in their function that was queried) decline the
        request. Since the request is declined it doesn't actually happen but the
        initiating user now knows if all other interested parties are or are not
        OK with the proposed request. Just be sure not to mistake your own declination
        for an objection by some other user. The fact that you were queried AT ALL
        indicates that other users are OK with the request. Since you yourself 
        propose to decline, you know in advance that the result of the query is
        certain to be a declination.

    *Unbind and requests in progress.* It is possible that a repository invoked callback
        function, invoked as a Request is processed, may make a call to the repositorys
        Unbind method. We have to be careful how this is handled. Normally we simply
        delete an entry from the callback list for the repository event in question.
        However, if a Request is in progress then we can be in the process of looping
        over the list from which the item is being deleted. If a Request is in progress
        (ie "NestDepth > 0") then Unbind, instead of actually deleting the no longer
        needed bind entry, sets it's three fields "(ID,Function,Herd)" to "None" and marks
        the corresponding Binder entry (eg "WidgetCreateNotify") in the "BinderDirty"
        dictionary. People who look at Binder are smart enough to note and ignore such
        'deleted' entries. At the end of a Request, if "NestDepth" is zero and "BinderDirty"
        isn't empty, we call "BinderClean" which scans the dirty Binder items and physically
        expunges the pending 'deleted' entries. 
        
    When creating additional binder entries, we first look for a "(None,None,None)" and if
        found we reuse that entry for our new binding. If there were no null entries then
        we append our new one to the end of the list. It is important that we re-use the
        null entries this way. If, as part of a callback, a repository user re-binds to
        the chain we are currently traversing then this is treated as an unbind followed
        by a bind. The unbind makes the existing entry null. If we *don't* reuse the null
        entry and we put the new binding at the end, then we will come upon it again and
        we will re-invoke the callback which will do the same thing again ad nauseum. Ask
        me how I know.
        
    "PreviousForm" is the name of the form (not herd) which was visible prior to the current
        one. This is used to implement the facility whereby the user can snap back and
        forth between two forms.    

    *Internal Details*

    "Barn" is a dictionary of herds. The key is the herd name, the value is a a dictionary of
        three items:
        o "['Widreqs']" A dictionary of widreqs, where the key is the name of the widreq and 
           the value is the widreq itself.
        o "['Selected']" The name of the presently selected widreq, or None if there is
           no selected widreq. This allows us to keep track of the selected widreq in
           herds which are not currently selected.
        o "['Form']" A dictionary of form related information. This is maintained by the
           layout form; check there for details. Herds which are not forms (eg the Parking
           lot) do not use this item. This item is created as an empty dictionary at the
           time the herd is created.      

    "Binder" is a dictionary with one key for each possible event (eg 'HerdCreateQuery') and the
        value is a list to 3-tuples:
        o The ID of the owner of the callback function.
        o A callback function bound to this event.
        o The name of the herd selected when the bind was created
    
    "NextId" is the next available user ID number.
    
    "SelectedHerd" is the name of the currently selected herd, or None if no herd is selected.

    "Users" is a dictionary where the key is the users ID number and the value is the users
        description string.                            
    #=p Published Methods
    #=u Unpublished Methods    
    """
                    
    def __init__(self):
        """=u
        Create the widget repository.
        """
        self.NextId = 5000 #Starting at zero would be so boring.
        self.Users = {}
        self.Barn = {}
        self.SelectedHerd = None
        self.SelectedWidreq = None
        self.DebugSelector = ''
        self.Binder = {}
        self.RequestDescription = None
        self.HerdRenamePair = None
        self.PreviousForm = None
        WidreqRepository.NestDepth = 0
        for A in ['Herd','Widreq']:
            for B in ['Create', 'Delete', 'Select', 'Rename']:
                for C in ['Query','Notify']:
                    self.Binder[A+B+C] = []
        self.BinderDirty = {}            
        #String identifying us for use in error results
        self.Who = 'The Widreq Repository'
        #Zero stats
        self.Stats = {}
        for T in ('register','unregister','rename','bind','unbind','request','list','fetch'
            ,'recursion','findframe','fetchform'):
            self.Stats[T] = 0

    def DebugSelectorSet(self,S):
        """=p
        Specify which repository events to print to standard output.
        
        "S" should be a string consisting of these letters:
          o "r" Print register/unregister/rename events.
          o "q" Print request events.
          o "b" Print bind events.
          o "u" Print unbind events.
        """
        assert type(S) == type('')
        for T in S:
            assert T in 'rbqu', 'Invalid reqpository debug code'
        self.DebugSelector = S 
        
    def DebugSelectorGet(self):
        """
        Return the current debug selector value
        """    
        return self.DebugSelector

    def Register(self,Who):
        """=p
        Register as a user of the repository.
        
        Call this method to register yourself with the repository. The
             argument "Who" should be a short string clearly identifying who
             you are, eg "The Widgetator" .
                        
        The result is your ID number; you will need this to further access
             the repository. 
                        
        If you try to register twice, or if you attempt to register with an
             already used "Who" string then you will receive None as the result. ;
        """                         
        self.Stats['register'] += 1
        assert type(Who) == type(''), 'Used Who must be a string'
        if Who in self.Users.values():
            #The Who string is already in use, or you are trying to register twice
            print 'WidreqRepository.Register: username "%s" already in use'%Who
            Result = None
        else:
            #Sign them up
            Result = self.NextId
            self.Users[Result] = Who
            self.Debug('r','User "%s" registered at %s'%(Who,self.NextId))
            self.NextId += 1    
        return Result

    def Unregister(self, ID):
        """=p
        Unregister from the repository.
        
        Unregister an existing registered user. 
        
        o Frees up the username that was associated with the registered user. 
        o Unbinds any bindings that user ID had in effect. 
        """  
        self.Stats['unregister'] += 1
        if not ID in self.Users.keys():
            self.Error(None,'ID %s not a registered repository user'%ID)
        self.Unbind(ID,'All')
        self.Debug('r','User %s (%s) unregistered'%(ID,self.Users[ID]))
        del self.Users[ID]    
        return 1

    def Rename(self, ID, NewName):
        """=p
        Change the name of an existing register repository user.
        
        Call this method to change your identification string. The result will
             be 1 if the rename was accepted, 0 if the name is already taken. ;
        """
        self.Stats['rename'] += 1
        assert type(NewName) == type(''), 'Used NewName must be a string'
        if not ID in self.Users.keys():
            self.Error(None,'ID %s not a registered repository user'%ID)
        if NewName == self.Users[ID]:
            self.Debug('r', 'User %s (%s) asked for a rename to their existing name. No action necessary.' 
                %(ID, self.Users[ID]))
            return 1    
        if NewName in self.Users.values():
            print 'WidreqRepository.Rename: username "%s" already in use'%NewName
            Result = 0
        else:
            self.Debug('r', 'User %s renamed from "%s" to "%s".'%(ID,self.Users[ID],NewName))
            self.Users[ID] = NewName
            Result = 1
        return Result    
        
    def Bind(self, ID, Events, Function):
        """=p
        Bind a callback function to a list of one or more repository events.
        
        Call this method to bind your callback function to one
            or more repository events. 
                    
            o "ID" is the ID supplied by "Register".
            o "EventList" is a string consisting of a space delimited list of
                  events indicators. An event indicator consists of "Herd" or "Widreq"
                  followed by one of "Create", "Delete","Select" or "Rename", followed
                  by one of "Query" or "Notify" (eg "WidreqSelectNotify").
            o "Function" is your callback function. It will be called as:
                  "f(EventIndicator,A,B)" where 
                  o "EventIndicator" is the event which prompted the callback (eg "HerdCreateNotify").
                  o "A" is the name of the herd or widreq in question.
                  o "B" is the new name (in the case of a rename) or "None" (all other cases).
                          
        If the callback function is OK with the proposed action it should
            return 1. If it is not OK with the proposed action it should return
            a tuple giving 
            o "[0]" A reason string briefly explaning it's objection, and
            o "[1]" a boolean set to 1 is the user has already been notified of
              the objection, 0 if not. 
        """
        if not ID in self.Users.keys():
            #we don't talk to no stinking unregisterd objects
            self.Error(None,'ID %s not a registered repository user'%ID)
            return None
        for T in Events.split():
            self.Stats['bind'] += 1
            #validate the event specifier
            if not T in self.Binder.keys():
                self.Error(ID, 'Bind: "%s" is not a valid event specifier'%T)
            if T[:6] == 'Widreq' and self.SelectedHerd == None and len(self.Barn) > 1:
                #If there is only one herd in existence it will be the parking lot in which
                #case there is no actual form to select so wo don't issue this message in that case.
                print self.Who + ' says: User %s (%s) bound a callback to event %s, but ' \
                    'no herd is currently selected. While not technically illegal, this is ' \
                    'pointless since widreq related bindings pertain only to the currently ' \
                    'selected herd. Bind accepted with doubts as to intent.'%(ID,self.Users[ID],T)    
            #if there was a previous binding to this ID get rid of it
            self.Unbind(ID, T)
            #create the new binding
            if T[:6] == 'Widreq':
                Herd = self.SelectedHerd
            else:
                Herd = None    
            #If there is a null binding in the list, overwrite that first. This is important.
            for J in range(len(self.Binder[T])):
                if self.Binder[T][J][0] == None:
                    #we found a null entry; use it
                    self.Binder[T][J] = [ID, Function, Herd]
                    break
            else:            
                #No null entry was found; create a new one
                self.Binder[T].append([ID, Function, Herd])
            self.Debug('b', 'User "%s" bound callback to %s of %s'%(self.Users[ID], T, self.SelectedHerd))
            
    def Unbind(self, ID, Events):            
        """=p
        Unbind the specified user from one or more repository event.

         Call this method to remove previously created bindings for the specified user. Asking to
            unbind something which is not currently bound is allowed.
                        
            o "ID" is the ID supplied by "Register"
            o "EventList" is a string containing one or more space delimited event indicators
                as described in "Bind". 
            In addition, an event indicator of
                "'All'" removes all bindings for this user.
        """
        if not ID in self.Users.keys():
            #we don't talk to no stinking unregisterd objects
            self.Error(None,'ID %s not a registered repository user'%ID)
            return None
        for T in Events.split():
            if T == 'All':
                #unbind everything for this ID
                for E in self.Binder.keys():
                    self.UnbindOne(ID,E)
            else:        
                #validate event specifier
                if not T in self.Binder.keys():    
                    self.Error(ID, 'Unbind: "%s" is not a valid event specifier'%T)
                #look for any binding to this ID
                self.UnbindOne(ID,T)

    def RequestDescriptionFetch(self):
        """
        Return the description of the request in progress.
        """
        return self.RequestDescription

    def Request(self, ID, Event, A=None, B=None, Description=None):
        """=p
        Process a request to the repository.
        
         o "ID" is the ID supplied by "Register"
         o "Event" is a string as described below, requesting a single
           action, eg "WidreqCreate".
         o "A" and "B" vary depending on the request:
           o "HerdCreate" - "A" is the name of the new herd, "B" is unused.
           o "HerdDelete" - "A" is the name of the herd to be deleted, "B" is unused. Deleting
             the selected herd leaves no herd selected.
           o "HerdSelect" - "A" is the name of the herd to be selected, "B" is unused.
           o "HerdRename" - "A" is the name of the herd to be renamed, "B" is the new name
           o "WidreqCreate" - "A" is the name of the new widreq, "B" is the new widreq instance
           o "WidreqDelete" - "A" is the name of the widreq to be deleted, "B" is unused
           o "WidreqSelect" - "A" is the name of the widreq to be selected, "B" is unused
           o "WidreqRename" - "A" is the name of the widreq to be renamed, "B" is the new name. 
           o "WidreqRelocate" - "A" is the name of the widreq to be relocated, "B" is the name of the 
             source herd.
            
        o "Description" is an optional string describing what you are doing. This is simply
            stored for the duration of the request; the method "FetchRequestDescription" will
            return it to anybody who is interested.
                          
        The result will be 1 if the request was completed successuflly or a 3-tuple:
          
          o "[0]" The reason string issued by the object which declined the request.
          o "[1]" A string identifying the repository user who declined the request. Note that
             the repository itself can decline requests (eg a request to delete a widreq that
             does not exist) in which case this string will be "'The Widreq Repository'".
          o "[2]" A boolean, supplied by the decliner. 1 if the user has already been notified
            of the reason, 0 if not. 
                        
        Note that we insist that *widreqs* have Python legal names, but we make no such
            restriction on *herd* names. In particular note that that all internal users
            (eg "The Widgetator") and all internal herds (eg "the Parking Lot") have
            spaces in their names so they are guaranteed not to conflict with any user 
            supplied Python legal names.
        """
        self.Stats['request'] += 1
        self.RequestDescription = Description
        if not ID in self.Users.keys():
            self.Error(None,'ID %s not a registered repository user'%ID)
        self.Debug('q', 'User "%s" posted request (%s,%s,%s) sH=%s sW=%s'
            %(self.Users[ID],Event,A,B,self.SelectedHerd,self.SelectedWidreq))
        if WidreqRepository.NestDepth > 0:
            self.Stats['recursion'] += 1    
        WidreqRepository.NestDepth += 1
        try:    
            if (Event == 'HerdSelect' and A == self.SelectedHerd):
                self.Debug('q', 'Requested herd is already selected; taking no action')
                #Selecting the currently selected herd is a non-event; tell user it's done
                return 1
            EventPhase = Event + 'Query'
            if Event == 'WidreqRelocate':
                #Relocate requires special handling
                if B == self.SelectedHerd:
                    #they asked to relocate a widreq from it's current herd.
                    return 1
                #Make sure the source herd exists
                if not self.Barn.has_key(B):
                    #it does not exist
                    return (self.Xlate('There is no herd named "%s" to relocate "%s" from.'%(B,A)),self.Who,0)
                #Temporarily select the source herd
                RealSelectedHerd = self.SelectedHerd
                self.RequestActionPhase(ID, 'HerdSelect', B)
                #We need the actual widreq at several places below                    
                TheWidreqInstance = self.Fetch(A)
                #See if anybody objects to deleting the widreq from the source herd.
                R = self.RequestQueryPhase(ID, 'WidreqDelete', A, None)    
                if R <> 1:
                    self.RequestActionPhase(ID, 'HerdSelect', RealSelectedHerd)
                    return R #somebody did object
                #See if anybody objects to creating the widreq in the current herd.
                self.RequestActionPhase(ID, 'HerdSelect', RealSelectedHerd)
                R = self.RequestQueryPhase(ID, 'WidreqCreate', A, TheWidreqInstance)    
                if R <> 1:
                    return R #somebody did object
                #Make sure the widreq exists in the source herd
                if not self.Barn[B]['Widreqs'].has_key(A):    
                    #It does not
                    return (self.Xlate('Herd "%s" has no widreq named "%s" to relocate.'%(RealSelectedHerd,A)),self.Who,0)
                #Make sure the widreq name is unused in the selected herd
                if self.Barn[RealSelectedHerd]['Widreqs'].has_key(A):
                    return (self.Xlate('Selected herd "%s" already has a widreq named "%s".'%(B,A)),self.Who,0)
                #Everything looks good so far; do the actual relocation
                self.RequestActionPhase(ID, 'HerdSelect', B)
                assert TheWidreqInstance <> None, 'Widreq instance unexpectedly not there'
                R = self.RequestActionPhase(ID, 'WidreqDelete', A, None)    
                assert R == 1, 'Widreq delete (as part of relocate) failed unexpectedly'
                self.RequestActionPhase(ID, 'HerdSelect', RealSelectedHerd)
                R = self.RequestActionPhase(ID, 'WidreqCreate', A, TheWidreqInstance)
                assert R == 1, 'Widreq create (as part of relocate) failed unexpectedly'
                #The widreq has been relocated; notify everybody
                self.RequestActionPhase(ID, 'HerdSelect', B)
                self.RequestNotifyPhase(ID, 'WidreqDelete', A, None)
                self.RequestActionPhase(ID, 'HerdSelect', RealSelectedHerd)
                self.RequestNotifyPhase(ID, 'WidreqCreate', A, TheWidreqInstance)
                #Return signaling success
                return 1
            #All requests other than 'WidreqRelocate' are handled here            
            if not (EventPhase) in self.Binder.keys():
                self.Error(ID, 'Request: "%s" is not a valid event specifier'%Event)
            if Event == 'HerdRename':
                #See "ListWidreqs" to find out what this is about
                self.HerdRenamePair = (A,B)    
            #    
            #Query all interested parties about the proposed request
            #
            R = self.RequestQueryPhase(ID, Event, A, B)
            if R <> 1:
                #somebody quashed the request
                return R
            #                
            #Everybody was OK with the request; attempt to make it so
            #
            R = self.RequestActionPhase(ID, Event, A, B)
            if R <> 1:
                #There was a problem implementing the action
                return R
            #            
            #Notify all interested parties about the completed request
            #
            self.RequestNotifyPhase(ID, Event, A, B)
            return 1     
        finally:
            WidreqRepository.NestDepth -= 1    
            if self.BinderDirty <> {} and WidreqRepository.NestDepth == 0:
                #There are deleted-but-not-purged entries in the binder
                self.BinderClean()
            #D('Event=%s SelWid=%s'%(Event,self.SelectedWidreq))
            if Event == 'WidreqDelete' and self.SelectedWidreq == None \
            and len(self.Barn[self.SelectedHerd]['Widreqs']) <> 0:
                #We just deleted a widreq, the deletion left not widreq selected and we have at least one widreq in the herd
                Temp = self.ListWidreqs()
                #Select a widreq from those remaining
                self.Request(ID,'WidreqSelect',Temp[0],None)        
            self.HerdRenamePair = None
            self.RequestDescription = None    
    
    def RequestQueryPhase(self, ID, Event, A, B):
        """=u
        Query all interested parties about the proposed request.
        
        The result is 1 if everyone concurs or "(ReasonString, Complainent, UserNotifiedFlag)" if not.
        """
        EventPhase = Event + 'Query'
        if Event == 'WidreqCreate':
            if not Rpw.NameVet (A):
                #The name is invalid
                return ('"%s" is not a valid name.'%A,self.Who,0)
        if Event == 'WidreqRename':
            if not Rpw.NameVet(B):        
                return ('"%s" is not a valid name.'%B,self.Who,0)
        DeferredFuncFID = None        
        for FID, Func, Herd in self.Binder[EventPhase]:    
            if FID == None:
                #This is a deleted-but-not-yet-purged binder entry
                continue
            if Event[:6] == 'Widreq' and Herd <> self.SelectedHerd:
                #Widreq-centric events apply only to a particular herd
                continue
            if FID == ID:
                #We defer querying the initiator of the query until last
                DeferredFuncFID = (Func, FID)
            else:    
                R = Func(EventPhase,A,B)
                self.Debug('q', 'User "%s" queried re %s. Reply=%s'%(self.Users[FID], EventPhase,R))
                if R == 1:
                    continue
                if (type(R) <> type(()) and type(R) <> type([])) \
                or len(R) <> 2 \
                or type(R[0]) <> type('') \
                or (R[1] <> 0) and (R[1] <> 1):
                    self.Error(ID, 'Response "%s" from callback "%s.%s" is not (String,Boolean)' \
                        %(R,self.Users[FID],EventPhase))
                #An interested party quashed the request. Return (Reason, UserWho, UserNoticeBoolean)            
                return (R[0],self.Users[ID],R[1])
        if DeferredFuncFID <> None:
            #The initiator wants to be queried; do so now after all other queries
            Func, FID = DeferredFuncFID
            R = Func(EventPhase,A,B)
            self.Debug('q', 'User "%s" queried re %s. Reply=%s'%(self.Users[FID], EventPhase,R))
            if R <> 1:
                if (type(R) <> type(()) and type(R) <> type([])) \
                or len(R) <> 2 \
                or type(R[0]) <> type('') \
                or (R[1] <> 0) and (R[1] <> 1):
                    self.Error(ID, 'Response "%s" from callback "%s.%s" is not (String,Boolean)' \
                        %(R,self.Users[FID],EventPhase))
                #An interested party quashed the request. Return (Reason, UserWho, UserNoticeBoolean)            
                return (R[0],self.Users[ID],R[1])
        #Nobody objected
        return 1        

    def RequestActionPhase(self, ID, Event, A, B=None):
        """=u
        Attempt to implement the the request.
        
        The result is 1 if thing went well, or (ReasonString, Complainent, UserNotifiedFlag) if not.
        """
        if self.SelectedHerd:    
            assert self.SelectedWidreq == self.Barn[self.SelectedHerd]['Selected'], \
                "SelectedWidreq(%s)<>Barn[SelectedHerd]['Selected'](%s) before ID=%s Event=%s, A=%s, B=%s" \
                %(self.SelectedWidreq,self.Barn[self.SelectedHerd]['Selected'],ID,Event,A,B)    
        Result = 1
        if Event[:6] == 'Widreq' and self.SelectedHerd == None:
            Result = (('Can\'t process event "%s" because there is no selected herd.'%Event,self.Who,0))
        else:
            if Event == 'HerdCreate':
                if self.Barn.has_key(A):
                    Result = (('There is already a herd named "%s".'%A,self.Who,0))
                else:
                    self.Barn[A] = {'Widreqs':{}, 'Selected':None, 'Form':{}}
            elif Event == 'HerdDelete':        
                if not self.Barn.has_key(A):
                    Result = (('There is no herd named "%s" to delete.'%A,self.Who,0))
                else:
                    del self.Barn[A]
                    if A == self.SelectedHerd:
                        self.SelectedHerd = None
            
            elif Event == 'HerdSelect':        
                if not self.Barn.has_key(A):
                    Result = (('There is no herd named "%s" to select.'%A,self.Who,0))
                else:
                    #Remember the widreq selected in the current herd, for later use
                    if self.SelectedHerd:
                        self.Barn[self.SelectedHerd]['Selected'] = self.SelectedWidreq
                    self.SelectedHerd = A
                    #Restore as selected the widreq which was last selected in this herd
                    self.SelectedWidreq = self.Barn[self.SelectedHerd]['Selected']

            elif Event == 'HerdRename':        
                if not self.Barn.has_key(A):
                    Result = (('There is no herd named "%s" to rename.'%A,self.Who,0))
                else:    
                    if A <> B:
                        #We rename only if the names are different
                        if self.Barn.has_key(B):
                            Result = (('There is already a herd named "%s".'%(B),self.Who,0))
                        else:
                            #All systems GO; do the rename
                            self.Barn[B] = self.Barn[A]
                            del self.Barn[A]
                            if self.SelectedHerd == A:
                                self.SelectedHerd = B
                            #Check for and update any instances of the old herd name in Binder
                            for Key in self.Binder.keys():
                                for BindEntry in self.Binder[Key]:
                                    if BindEntry[2] == A:
                                        BindEntry[2] = B    
            
            elif Event == 'WidreqCreate':
                if self.Barn[self.SelectedHerd]['Widreqs'].has_key(A):
                    Result = (('Herd "%s" already has a widreq named "%s".'%(self.SelectedHerd,A),self.Who,0))
                else:
                    self.Barn[self.SelectedHerd]['Widreqs'][A] = B    
                    
            elif Event == 'WidreqDelete':
                if not self.Barn[self.SelectedHerd]['Widreqs'].has_key(A):
                    Result = (('Herd "%s" has no widreq named "%s" to delete.'%(self.SelectedHerd,A),self.Who,0))
                else:
                    del self.Barn[self.SelectedHerd]['Widreqs'][A] 
                    if self.SelectedWidreq == A:
                        self.SelectedWidreq = None
                        self.Barn[self.SelectedHerd]['Selected'] = None

            elif Event == 'WidreqSelect':
                if not self.Barn[self.SelectedHerd]['Widreqs'].has_key(A):
                    Result = (('Herd "%s" has no widreq named "%s" to select.'%(self.SelectedHerd,A),self.Who,0))
                else:
                    self.SelectedWidreq = A
                    self.Barn[self.SelectedHerd]['Selected'] = A

            elif Event == 'WidreqRename':        
                if not self.Barn[self.SelectedHerd]['Widreqs'].has_key(A):
                    Result = (('Herd "%s" has no widreq named "%s" to rename.'%(self.SelectedHerd,A),self.Who,0))
                else:    
                    if A <> B:
                        #We rename only if the names are different
                        if self.Barn[self.SelectedHerd]['Widreqs'].has_key(B):
                            Result = (('Herd "%s" already has a widreq named "%s".'%(self.SelectedHerd,B),self.Who,0))
                        else:
                            self.Barn[self.SelectedHerd]['Widreqs'][B] = self.Barn[self.SelectedHerd]['Widreqs'][A]
                            del self.Barn[self.SelectedHerd]['Widreqs'][A]
                            if self.SelectedWidreq == A:
                                self.SelectedWidreq = B
                                self.Barn[self.SelectedHerd]['Selected'] = B
                            #Tell the widreq to rename itself    
                            self.Barn[self.SelectedHerd]['Widreqs'][B].Rename(B)    
            else:
                raise Exception, "WidgetRepository missed an event; call for programming support"
        if Result <> 1:        
            self.Debug('q', 'Request %s declined, reason = %s'%(Event,`Result`))
            #Convert herd-speak to user-speak
            Result = (self.Xlate(Result[0]),Result[1],Result[2])
        if self.SelectedHerd:    
            assert self.SelectedWidreq == self.Barn[self.SelectedHerd]['Selected'], \
                "SelectedWidreq(%s)<>Barn[SelectedHerd]['Selected'](%s) after ID=%s Event=%s, A=%s, B=%s" \
                %(self.SelectedWidreq,self.Barn[self.SelectedHerd]['Selected'],ID,Event,A,B)    
        return Result

    def RequestNotifyPhase(self, OriginatorID, Event, A, B):
        """=u
        Notify all interested parties of the completed action.
        """
        EventPhase = Event+'Notify'
        #Since callbacks may alter Binder, we work from a copy
        for ID, Func, Herd in self.Binder[EventPhase]:    
            if ID == None:
                #This is a deleted-but-not-yet-purged binder entry
                continue
            if Event[:6] == 'Widreq' and Herd <> self.SelectedHerd:
                #Widreq-centric events apply only to a particular herd
                #self.Debug('q', 'User "%s" NOT notified of %s (target herd=%s)'%(self.Users[ID],EventPhase,Herd))
                continue
            UserName = self.Users[ID]    
            self.Debug('q', 'About to notify user "%s" of %s'%(UserName,EventPhase))
            Func(EventPhase,A,B)
        try:
            Name = self.Users[OriginatorID]
        except KeyError:
            #This can happen if a user Unregisters while we are in the midst of doing notifications.
            Name = str(OriginatorID)
        self.Debug('q', 'Done. User "%s" (%s,%s,%s)'%(Name,Event,A,B))

    def Xlate(self,String):
        """=u
        Convert Herd-speak to User-speak
        """
        return String

    def HerdRemediate(self,Herd):
        """=p
        Remediate a herd name if necessary.

        A problem can happen during herd rename like this: During the notify 
            phase, routine A - which thinks it knows the name of it's herd - is called 
            (perhaps by routine B which is being notified of the change) after the
            herd name has been changed but before routine A has been notified. 
            Routine A calls ListWidreqs or Fetch with the old name of its herd and we
            blow up on a KeyError because of the wrong herd name. To get around
            this, when a HerdRename is taking place we set "self.HerdRenamePair" which
            is a tuple of the old and new herd names. This routine checks a herd name
            and if it isn't the name of a current herd and and HerdRenamePair isn't
            None and the name we were passed is the old name of the herd being renamed 
            then we translate the name on behalf of the caller. It's sort of like 
            "The knights who until recently went ni".    
        """
        if self.Barn.has_key(Herd):
            return Herd
        if self.HerdRenamePair <> None and self.HerdRenamePair[0] == Herd:
            return self.HerdRenamePair[1]
        return Herd        

    def FetchSelected(self,Herd=None):
        """
        Return the name of the currently selected widreq.
        
        o If no herd is specified then the currently selected herd is used.
        o If no herd is specified and there is no currently selected herd then
            the result is None.
        """
        if Herd == None:
            Herd = self.SelectedHerd
        else:
            Herd = self.HerdRemediate(Herd)    
        try:
            Result = self.Barn[Herd]['Selected']
        except KeyError:
            Result = None
        return Result        

    def ListWidreqs(self,Herd=None):
        """=p
        Return a list of all widreqs in the specified herd.
        
        o If no herd is specified the currently selected herd is listed.
        o If no herd is specified and there is no currently selected herd, the result
            is an empty list.
        """
        self.Stats['list'] += 1
        if Herd == None:
            Herd = self.SelectedHerd
        else:
            Herd = self.HerdRemediate(Herd)    
        if Herd == None:
            Result = []
        else:    
            try:
                Result = self.Barn[Herd]['Widreqs'].keys()         
            except:
                raise Exception, 'error'
            Result.sort()
        return Result        

    def FindFrame(self,FrameID,Herd=None):
        """p
        Given a "FrameID" find the corresponding container-Widreq.
        
        o If no herd is specified we look in the currently selected herd.
        o If no herd is specified and there is no currently selected herd, the result is None.
        o If there is no container widreq of the specified ID the result is None.
        o If there is a container widreq of the specified ID we return it as the result.
        """
        self.Stats['findframe'] += 1
        if Herd == None:
            Herd = self.SelectedHerd
        if Herd == None:
            return None
        else:    
            for W in self.Barn[Herd]['Widreqs'].values():
                if W.FrameID == FrameID:
                    return W      
        return None

    def ListHerds(self):
        """=p
        Return a sorted list of the names of all the herds in the repository.
        """
        Result = self.Barn.keys()
        Result.sort()
        return Result

    def Fetch(self, Name, Herd=None):
        """=p
        Fetch the specified widreq from the specified herd.
        
        If no herd is specified, we look in the currently selected herd.
        If there is no such herd or widreq the result is None
        """
        self.Stats['fetch'] += 1
        if Herd == None:
            Herd = self.SelectedHerd
        else:
            Herd = self.HerdRemediate(Herd)    
        try:
            Result = self.Barn[Herd]['Widreqs'][Name]
        except KeyError:
            Result = None
        return Result        

    def FetchForm(self, Herd=None):
        """=p
        Fetch the form information dictionary for the specified herd.

        If no herd is specified, we look in the currently selected herd. If there
            is no currently selected herd the result is None
        If a herd is specified we return the data for that herd or None if there
            is no such herd.
        """
        self.Stats['fetchform'] += 1
        if Herd == None:
            Herd = self.SelectedHerd
        else:
            Herd = self.HerdRemediate(Herd)    
        try:
            Result = self.Barn[Herd]['Form']
        except KeyError:
            Result = None
        return Result        

    def Tell(self,Info):
        """=p
        Nicely handle repository Request declination tuple.
        
        If a repository request is declined, the caller gets back a tuple:
        [0] A string saying why the request was declined.
        [1] A string identifying the user who issued the declination.
        [2] A boolean: 1 if user has already been notified, 0 if not.
        
        This routine accepts a declination tuple and, if the user hasn't already
            been notified, it puts up a reasonably formatted dialog.
            
        As a bonus, you can pass ANY repository Request result to us and we
            will handle it properly. If the Request was processed successfully
            the result is a 1 which consider as requiring no action.    
        """
        if Info == 1:
            return
        assert len(Info) == 3
        Reason, User, Boolean = Info
        assert type(Reason) == type('')
        assert type(User) == type('')
        assert type(Boolean) == type(0)
        if Boolean:
            return
        Msg = 'A widget repository request was declined by %s. The reason ' \
            'given was: %s'%(User,Reason)
        Rpw.MessageDialog(Message=Msg)
                 
    #---------------------------------------------------------------------------
    # Private methods 
    #---------------------------------------------------------------------------    

    def Dumphry(self,What,Comment=''):
        """=u
        Dump specified parts of the repository.

        "What" is a string containing one or more of:
            o "B" = binder
            o "H" = herds
            o "U" = users
            
        If "Comment" is supplied, it it printed at the top of the dump.    
        """
        X = Comment + ' ---------- WidRep %s ----------'
        if 'U' in What:
            print X%'users'
            #dump users
            Users = self.Users.keys()
            Users.sort()
            for K in Users:
                print '%s: %s'%(K,self.Users[K])
        if 'H' in What:
            #dump herds
            print X%'herds'
            print 'SelectedHerd=%s, SelectedWidreq=%s'%(self.SelectedHerd, self.SelectedWidreq)
            Herds = self.Barn.keys()
            Herds.sort()
            for H in Herds:
                Widreqs = self.Barn[H]['Widreqs'].keys()
                print 'Herd: %s, %s widreqs. Selected=%s.'%(H,len(Widreqs),self.Barn[H]['Selected'])
                Temp = self.Barn[H]['Form'].keys()
                Temp.sort()
                Prefix = '          '
                print    '     Form:%s'%H
                for Key in Temp:
                    print '%s%s : %s'%(Prefix,Key,self.Barn[H]['Form'][Key])
                Widreqs.sort()
                for W in Widreqs:
                    Wid = self.Barn[H]['Widreqs'][W]
                    print '   Widreq: %s, Name=%s, PresentHome=%s, FrameID=%s' \
                        %(W,Wid.Name,Wid.PresentHome,Wid.FrameID)
        if 'B' in What:
            #Dump bindings
            print X%'bindings'
            Bindings = self.Binder.keys()
            Bindings.sort()
            for B in Bindings:
                if self.Binder[B] == []:
                    continue
                print B
                Temp = self.Binder[B]
                Temp.sort()
                for User, Func, Herd in Temp:
                    #trim memory location from Func information
                    Func = ' '.join(str(Func).split()[0:4])
                    try:
                        User = '%s (%s)'%(User,self.Users[User])
                    except:
                        pass    
                    print '   %s %s %s'%(User,Herd,Func)

    def Debug(self, Code, Msg):
        """=u
        Call this to (if enabled) print debug information on standard output.
        
        "Code" should be a letter from "r q b u" indicating the type of event
            to which this message relates:
          o "r" register/unregister/rename events.
          o "q" request events.
          o "b" bind events.
          o "u" unbind events.
          
        "Msg" is the text to be printed if events of this type are being tracked.  
        """
        if Code in self.DebugSelector:
            Indent = (WidreqRepository.NestDepth * 2) * ' '
            print '%s[%s] WidRep: %s'%(Indent, WidreqRepository.NestDepth, Msg)

    def UnbindOne(self,ID,OneEvent):
        """=u
        Our local unbinder. 
        
        The caller should have verified that the "ID" and the
            one event specified are legal. We don't check.
            
        *Note:* If we are not in the midst of processing a request (ie "NestDepth == 0") then we
            bodily delete the specified binding. If we are in th midst of processing a request
            then it is important that we not shrink the bind list, so we set the specified
            binding to "(None,None,None)" and flag it in "BinderDirty". This will get cleaned
            up at the end of the request.    
        """
        self.Stats['unbind'] += 1
        #print 'ID=%s, Event=%s'%(`ID`,`OneEvent`)
        self.Debug('u', 'User "%s" unbound from %s'%(self.Users[ID], OneEvent))
        T = range(len(self.Binder[OneEvent]))
        T.reverse()
        for Index in T :
            if self.Binder[OneEvent][Index][0] == ID:
                if WidreqRepository.NestDepth == 0:
                    #we can muck with the list of bindings directly
                    self.Binder[OneEvent].pop(Index)
                else:
                    #a request is in progress; null the binding and mark this binder entry dirty
                    self.Binder[OneEvent][Index] = [None,None,None]
                    self.BinderDirty[OneEvent] = 1    

    def BinderClean(self):
        """=u
        Cleanup any deleted-but-not-purged binder entries
        """
        assert WidreqRepository.NestDepth == 0
        for OneEvent in self.BinderDirty.keys():
            T = range(len(self.Binder[OneEvent]))
            T.reverse()
            for Index in T:
                if self.Binder[OneEvent][Index][0] == None:
                    #This is a 'deleted' binding
                    self.Binder[OneEvent].pop(Index)
        self.BinderDirty = {}            
        
    def Error(self, ID, Message):
        """=u
        Issue an error message then raise an exception
        """
        if ID <> None and ID in self.Users.keys():
            Who = self.Users[ID]
        else:
            Who = '<%s>'%ID    
        Message = '(User=%s) %s'%(Who,Message)
        raise Exception, 'RepositoryError: '+Message

class rpDndCanvas(DND.CanvasDnd):
    """=m
    A drag and drop enabled canvas to which we have added some features.
    """

    def BabysitScrollregion(self):
        """
        Adjust the scroll region of our canvas.
        
        A Canvas is apparently too stupid to figure out it's own scroll region;
         that or I don't yet fully comprehend the wisdom of how Canvas does
         work. In any case this routine checks to see what area is already
         used in the canvas and sets that as the region we can scroll through.
        """
        T=self.bbox('all')
        if T <> None:
            x1, y1, x2, y2=T
            self.configure(scrollregion=(x1, y1, x2+5, y2+5))
        
    def clear(self):
        """
        Clear the canvas by removing all it's objects.
        """
        for Item in self.find_all():
            self.delete(Item)
        self.BabysitScrollregion()
            
    def size(self,TagOrId=None):
        """
        Return (x,y) size tuple of specified canvas object.
        
        If no object is specified we return the size of the rectangle which encloses
            all objects on the canvas.
        """
        return BBToSize(self.bbox(TagOrId))
    

class rpDndCanvasWid(rpDndCanvas):
    """=m
    An rpDndCanvas which is specifically tailored to accept widreqs

    In addition to the regular 'Canvas' arguments, you must supply two names:
    
        o "herdname" is the name of the herd associated with this canvas, eg "Form1".
        o "ourname" identifies this particular canvas, eg "GuiEditor"
        
        We create a composite "RepoName" as "<ourname> for <herdname> (eg "GuiEditor for Form1")
            which is the name we use to register with the widreq repository.
    """

    def __init__(self, Master, **kw):
        """
        Create the canvas.
        """
        assert kw.has_key('herdname'), 'You HAVE to supply argument "herdname"'
        assert kw.has_key('ourname'), 'You HAVE to supply argument "ourname"'
        self.HerdName = kw['herdname']
        assert self.HerdName <> None
        self.OurName = kw['ourname']
        assert self.OurName <> None
        self.RepoName = '%s for %s'%(kw['ourname'],self.HerdName)
        del kw['herdname'] 
        del kw['ourname']
        apply(DND.CanvasDnd.__init__,(self,Master),kw)
        #By default you get an ObjectDict for free with a dndCanvas, however, we use the
        #    repository to keep track of widreqs instead. We toast ObjectDict because
        #    otherwise the dnd canvas will get confused by all our name changes. The
        #    dnd canvas is perfectly happy to operate without an ObjectDict.
        del self.ObjectDict
        #--- keeping track of the selected widreq ---
        #Register ourself with the repository
        self.RepoSignup()
        
    def RepoSignup(self):
        """
        Do initialization related to the repository.
        """    
        self.WRID = Repo.Register(self.RepoName)
        assert None <> self.WRID, 'Repository registration failed'
        self.SelectedWidreq = None
        Repo.Bind(self.WRID,'WidreqSelectNotify WidreqDeleteQuery WidreqDeleteNotify ' \
            'HerdSelectNotify HerdRenameNotify HerdDeleteNotify',self.on_WidreqEvents)
        #self.Modified = False    

    def on_WidreqEvents(self,Event,Name,B):
        """
        Look after various widreq events.
        
        It's purpose is to make sure that the selected widreq is represented on the layout
            canvas as selected and that all other widreqs are shown as non-selected.
        """
        ##D('Event=%s HerdName=%s OurName=%s'%(Event,self.HerdName,self.OurName))
        if Event == 'HerdDeleteNotify':
            if Name == self.HerdName:
                #WE are being deleted; unregister
                Repo.Unregister(self.WRID)
                self.WRID = None
            return    
        if Event == 'HerdRenameNotify':
            if Name == self.HerdName:
                #This canvases herd is being renamed
                self.HerdName = B
                #Must change registration name
                self.RepoName = '%s for %s'%(self.OurName,self.HerdName)
                Repo.Rename(self.WRID,self.RepoName)
            return
        if Event == 'WidreqSelectNotify':
            if self.SelectedWidreq <> None:
                #we have a presently selected widreq; tell it to look non-selected.
                SW = self.SelectedWidreq
                SW.WidgetShow(SW.Label,IsSelected=False)
            #Fetch a pointer to the newly selected widreq from the repository
            self.SelectedWidreq = Repo.Fetch(Name)
            if self.SelectedWidreq == None:
                Rpw.MessageDialog(Msg='Layout.on_WidreqSelectNotify: expecting Widreq; got None.')
            else:
                #Have the newly selected widreq display itself as such
                SW = self.SelectedWidreq
                SW.WidgetShow(SW.Label,IsSelected=True)

        elif Event == 'WidreqDeleteQuery':
            #If a widreq is being deleted, make a note of it
            self.WidreqForDeletion = Repo.Fetch(Name)
            return 1 #it works for us
            
        elif Event == 'WidreqDeleteNotify':
            #It actually got deleted    
            if self.WidreqForDeletion == self.SelectedWidreq:
                #And it was our selected widreq; that means we have no selected widreq
                self.SelectedWidreq = None
                #Tell the widreq to look not-selected; this is important for frame widreqs
                if self.WidreqForDeletion.FrameID <> None:
                    #This is a frame widreq
                    self.WidreqForDeletion.WidgetShow(self.WidreqForDeletion,IsSelected=0)
            #Toast the reference to the dead widreq    
            self.WidreqForDeletion = None                        

        elif Event == 'HerdSelectNotify':
            #The selected herd has changed
            SW = self.SelectedWidreq
            if Name == self.HerdName:
                #The herd being selected is ours
                if SW <> None:
                    #Tell our selected widreq to look selected
                    SW.WidgetShow(SW.Label,IsSelected=True)
            else:
                #Some other herd is being selected.
                #If we have a selected widreq, tell it to look unselected
                if SW <> None:
                    SW.WidgetShow(SW.Label,IsSelected=False)
                #Remove any frame mark indicators    
                self.FrameMark(None)                
        else:
            raise Exception, 'Unhandled Repo event: %s'%Event    

    def dnd_commit(self,Source,Event):
        """
        A dragged object - presumably a widreq - is being dropped on us.
        
        "Source" is the widget being dropped.
        """
        #Make sure we are the selected herd. If we have to relocate the widreq, it gets
        #    relocated into the current herd. If we need to generate a name for the widreq,
        #    'NameWidReq' checks the current herd to avoid duplicate names.
        #self.Modified = True
        R = Repo.Request(self.WRID, 'HerdSelect', self.HerdName)
        if R <> 1:
            print R
            raise Exception, 'Request to make "%s" the current herd failed unexpectedly'%self.HerdName
        if Source.PresentHome == None:
            #It's a newborn widreq that has been dropped on our doorstep. Tell it about it's new home
            Source.PresentHome = self.HerdName
            #Get a name for it.
            Source.Rename(NameWidReq(Source.WidgetName))
            #Since it's a newborn we must register it with the repository
            R = Repo.Request(self.WRID,'WidreqCreate',Source.Name,Source)
            if R <> 1:
                print R
                raise Exception, 'Registration of newbord widreq with repository failed unexpectedly'
        elif Source.PresentHome == self.HerdName:
            #It's a widreq that already lives here; no action required
            pass
        else:
            #It's a widreq that lived somewhere else.
            #See if we already have a widreq of the same name
            Temp = Repo.Fetch(Source.Name)
            if Temp <> None:
                #oh-oh; we already have a widreq of the same name; rename and inform user
                #We pass NameWidReq the names of both the originating herd and our herd so
                #    we get a name that will conflict with neither herd. Since we rename in
                #    the originating herd then move to our herd this is important.
                NewName = NameWidReq(Source.WidgetName,(Source.PresentHome,self.HerdName))
                Msg = 'Hi, I\'m %s and you just dropped a widget named "%s" on me, however I ' \
                    'already have a widget of that name, therefore, I have changed the name of the ' \
                    'dropped widget to "%s". Feel free to rename it after you have dismissed this message.' \
                    %(self.HerdName, Source.Name, NewName)
                Rpw.MessageDialog(Message=Msg)
                #We want to rename the dropping widreq, therefore we must select the herd in
                #    which it resides, do the rename, then select our herd and relocate it.
                R = Repo.Request(self.WRID, 'HerdSelect', Source.PresentHome)
                if R <> 1:
                    print R
                    raise Exception, 'Request to make "%s" the current herd failed unexpectedly'%Source.PresentHome
                #do the rename
                #The widreq needs to know the name of the herd it't bound for in order to properly
                #    look after handler renaming issues. TargetHerd says where it's going.
                Source.TargetHerd = self.HerdName
                R = Repo.Request(self.WRID,'WidreqRename', Source.Name, NewName)    
                if R <> 1:
                    print R
                    raise Exception, 'Attempt by %s to rename widreq %s to %s failed unexpectedly.' \
                        %(self.RepoName, Source.Name, NewName),R
                #Source.Rename(NewName)
                R = Repo.Request(self.WRID, 'HerdSelect', self.HerdName)
                #Now re-select our herd.
                TheName = NewName    
            else:
                #we do not have a widreq of the same name
                TheName = Source.Name        
            #The name has been dealt with; relocate widreq to current herd
            R = Repo.Request(self.WRID, 'WidreqRelocate', Source.Name, Source.PresentHome)
            if R <> 1:
                print R
                raise Exception, 'Request to relocate widget "%s" from herd "%s" failed unexpectedly'% \
                    (Source.name, Source.PresentHome)
            Source.PresentHome = self.HerdName 
            Source.TargetHerd = None
            #Here we 'rename' the Source widreq. If we actually changed it's name then it is told about
            #   the new name here. If we didn't change it's actual name it is STILL important that we
            #   call Rename here because that causes the widreq to re-register it's editor with the
            #   repository, with the new herd mentioned. This is important.
            Source.Rename(TheName)    
        #Update creation code to include the new or moved widreq
        GblLayout.CreationSystextRegen('rpDndCanvasWid %s on %s'%(self.OurName,self.HerdName))    
        #Regardless of how the widreq got here, attempt to make it the current widreq.
        Repo.Request(self.WRID,'WidreqSelect',Source.Name)

    def FrameMark(self,Whatever):
        """
        A dummy frame mark method; override as necessary.
        """
        pass

class BindMixin:
    """
    A mixin class specifically for classes the need to mess with bindings.
    """

    def __init__(self):
        pass

    def OrphanHandlersProcess(self,WidgetName,HandlerList):
        """
        Give user chance to delete orphan handlers resulting from widreq deletion.
        
        "WidreqName" is the name of the widreq whose demise resulted in orphan handlers.
        "HandlerList" is a list a list of the handlers which were referenced by the widreq.
        """
        #Figure out which ones are orphans
        OrphanList = [X for X in HandlerList if self.HandlerReferencesCount(X)==0]
        if OrphanList:
            Msg = ("There {is/are} %s event handler{/s} which {was/were} referenced only by the recently "
                "departed widget $s. Since {that/those} handler{/s} {is/are} now referenced by no Rapyd-tk "
                "maintained bindings would you like to delete {it/them} now?")
            Msg = rpHelp.Plural(Msg,len(OrphanList),ToPercent='$')
            Msg = Msg%WidgetName
            DH = rpHelp.Plural('Delete handler{/s}',len(OrphanList))
            KH = rpHelp.Plural('Keep handler{/s}',len(OrphanList))
            R = Rpw.MessageDialog(Title='Query',Message=Msg,Buttons=((DH,1),(KH,None)),
                Help=('delete.handlerstoo',(WidgetName,HelpListPretty(OrphanList),len(OrphanList)))).Result
            if R == 1:
                for Handler in OrphanList:
                    self.HandlerDelete(Handler)

    def HandlerReferencesCount(self,HandlerName,Verbose=False):
        """
        Count the number of bindings that reference a given event handler.
        
        This checks all bindings in all widreqs of the current form.
        
        Event handlers may be referenced by bind entries or by command options which
            are really bindings in disguise. We check both.
            
        If Verbose is false the result is a simple integer indicating the number of
            bindings to this handler.
            
        If Verbose is true the result is a sorted list of tuples where each tuple represents
            one reference to the event handler:
            [0] Name of widget
            [1] The event string (for bindings) or the option name (for commands)
        """
        Result = 0
        if Verbose:
            Result = []
        Visible = GblLayout.CurrentlyVisibleForm()
        for WidreqName in Repo.ListWidreqs(Visible):
            Widreq = Repo.Fetch(WidreqName,Herd=Visible)
            #Have the widreq supply a list of (HandlerName,EventStringOrCommandOption) tuples for handlers
            #    referenced by this widreq.
            HList = Widreq.HandlersList(Verbose=True)
            for H in HList:
                if H[0] == HandlerName:
                    if Verbose:
                        Result.append((WidreqName,H[1]))
                    else:
                        Result += 1    
        if Verbose:
            Result.sort()
        return Result            

    def HandlerFind(self,HandlerName):
        """
        Attempt to find the start of a handler in the text.
        
        The result is the line index (as an integer) if found, or '' if not found.
        """
        TextEditor = GblLayout.TextEditFetch().TextWidget
        return TextEditor.SystextFind('def %s('%HandlerName,Type='Start')

    def HandlerRename(self,Old,New):
        """
        Rename an event handler and update references to it.
        
        IMPORTANT! It is the *callers* responsibility to make sure that that a handler of the 
            "New" name does not already exist.
        """
        #Find the existing handler
        I = self.HandlerFind(Old)
        assert I <> '', "Handler text unexpectedly not found"
        #Cut it's text bodily
        TextEditor = GblLayout.TextEditFetch().TextWidget
        Temp = TextEditor.ChunkCut(I)
        ##D('HandlerRename: OldName=%s NewName=%s Temp[0]=%s'%(Old,New,Temp[0]))
        #Revise the 'def' line to mention the new name
        Temp[0] = Temp[0].replace(Old,New)
        #Place the revised handler in alphabetical order
        self.HandlerEnsure(New,HandlerText=Temp)
        #Have widreqs revise any references to the old name
        Visible = GblLayout.CurrentlyVisibleForm()
        for WidreqName in Repo.ListWidreqs(Visible):
            Widreq = Repo.Fetch(WidreqName,Herd=Visible)
            Widreq.HandlerRenameNotify(Old,New)
        #Have the current option/bind/pack editor refresh itself if needed.                
        GblLayout.TheWidgetator.EditorRefresh()                

    def HandlerEnsure(self,HandlerName,HandlerText=None):
        """
        If a handler of the specified name doesn't already exist, create one.
        
        If "HandlerText" is None, we create default text for the handler.
        Otherwise "HandlerText" must be a 2-list of strings:
            o "[0]" The Systext part of the handler.
            o "[1]" The Usertext part of the handler. 
        
        """
        ##D('HandlerEnsure: HandlerName=%s HandlerText=%s'%(HandlerName,HandlerText))
        TextEditor = GblLayout.TextEditFetch().TextWidget
        #The left paren after the handler name when we search is *required*. Since
        #there may be an existing handler named "yadayada" and we don't want
        #to find a match if we are considering creating a handler named "yada".
        #                                     v
        Index = TextEditor.SystextFind('def %s('%HandlerName)
        if Index == '':
            #The handler does not exist. Since we keep the handlers in alphabetical
            #    order, scan the handlers to find where we should put the new one.
            J = 3
            while 1:
                From, To, Text = TextEditor.SystextFetchByIndex(J)
                if Text.find('Start of non-Rapyd') <> -1:
                    #we ran out of handlers.
                    break
                Text = Text.lstrip()
                assert Text[:4] == 'def '
                if Text[4:] > HandlerName:
                    #We want to insert in front of this one
                    break
                J += 1        
            if HandlerText == None:    
                #We must create default text for the handler
                Scheme = Cfg.Info['Schemes'][Cfg.Info['SchemeCurName']]
                Indent = Scheme['Indent']
                I = Indent*' '
                HandlerText = ['\n%sdef %s(self'%(I,HandlerName)
                    ,',Event=None):\n%s%spass\n'%((I,)*2)]
            Systext, Usertext = HandlerText
            TextEditor.insert(From,Usertext,'')
            TextEditor.insert(From,Systext,'bgldt')

    def HandlerDelete(self,HandlerName):
        """
        Delete the handler of the specifed name and all references to it.
        """
        #First we toast the text of the handler
        TextEditor = GblLayout.TextEditFetch().TextWidget
        SystextIndex = TextEditor.SystextFind('def '+HandlerName,Type='Start')
        assert SystextIndex <> '','We were sort of expecting to find the handler'
        Temp = TextEditor.ChunkCut(SystextIndex)
        #Have widreqs delete any references to this handler
        Visible = GblLayout.CurrentlyVisibleForm()
        for WidreqName in Repo.ListWidreqs(Visible):
            Widreq = Repo.Fetch(WidreqName,Herd=Visible)
            Widreq.HandlerDeleteNotify(HandlerName)
        #Have the current option/bind/pack editor refresh itself if needed.                
        GblLayout.TheWidgetator.EditorRefresh()                

    def HandlerChangeProcess(self,OriginalName,NewName,Who):
        """
        Handle arcane details of proposed event handler name change.
        
        Who should be either "'bind'" or "'command'". We use this when invoking
            help topics.
        
        If NewName is "*DELETE*' then this is a request to delete the *binding*.
        
        Many cases require the user to make a choice and we look after this.
        
        Possible results are:
        
             None   - Operation cancelled, do nothing
             0      - The binding was deleted
             1      - The binding was accepted
        """     
        assert Who in ('bind','command')
        TextEditor = GblLayout.TextEditFetch().TextWidget
        ##D('HandlerChangeProcess: Original=%s, New=%s, Who=%s'%(OriginalName,NewName,Who))
        if NewName == '*DELETE*':
            #User asked to delete this binding
            #Count the number of bindings to this event handler
            Count = self.HandlerReferencesCount(OriginalName)            
            if Count == 1:
                #This is the only binding that refers to the handler
                if Who == 'bind':
                    Action = 'deleting this binding'
                elif Who == 'command':
                    Action = 'clearing this command-option'
                else:
                    raise Exception, 'UnexpectedWho: '+Who        
                M = ('No other binding nor command-option refers to the event handler '
                    '"%s". Do you want to delete the event handler in addition to '
                    '%s?'%(OriginalName,Action))
                Choice = Rpw.MessageDialog(Title='Query'
                    ,Message=M
                    ,Buttons=(('Delete handler',1),('Keep handler',None),('~Cancel',2))
                    ,Help=('%s.delete.handlertoo'%Who,(OriginalName,))).Result
                if Choice == 2:
                    #Used decided to delete neither
                    return None
                if Choice == 1:
                    #User said to toast the handler too
                    SystextIndex = TextEditor.SystextFind('def '+OriginalName,Type='Start')
                    assert SystextIndex <> '','We were sort of expecting to find the handler'
                    Temp = TextEditor.ChunkCut(SystextIndex)
            return 0
        else:        
            #User supplied a binding of some sort.
            if OriginalName == '':
                #This is a newly minted handler name
                assert NewName <> '','User not supposed to be able to create blank handler name'
                self.HandlerEnsure(NewName)
                return 1
            else:
                #There was an existing handler name
                if NewName == OriginalName:
                    #The user did not change the name of the handler
                    return 1
                else:
                    #The user changed the name of the handler.
                    #We need a count of references in either case.
                    Count = self.HandlerReferencesCount(OriginalName)
                    assert Count >= 1
                    #Look for a handler of the new name
                    HandlerIndex = self.HandlerFind(NewName) 
                    if HandlerIndex <> '':
                        #A handler of the new name already exists.
                        if Count == 1:
                            #After the change, no bindings will refer to the old handler.
                            M = ('After the change you just made, no bindings nor command-'
                                'options will refer to the event handler "%s". Do you want me '
                                'to delete this event handler now?'%OriginalName)
                            HelpTuple = ('%s.orphan.handler'%Who,(OriginalName,NewName))     
                            Choice = Rpw.MessageDialog(Title='Query',Message=M,Help=HelpTuple
                                ,Buttons=(('Delete handler',1),('Keep handler',None),('~Cancel',2))).Result
                            if Choice == 2:
                                #User decided to cancel change
                                return None
                            if Choice == 1:
                                #User asked to delete the handler
                                TextEditor = GblLayout.TextEditFetch().TextWidget
                                OldHandlerIndex = self.HandlerFind(OriginalName)
                                assert OldHandlerIndex <> ''
                                Temp = TextEditor.ChunkCut(OldHandlerIndex)
                            return 1
                        else:
                            #After the change, at least one other binding will refer to the
                            #   old handler; no action required
                            return 1
                    else:
                        #A handler of the new name does not exist    
                        if Count == 1:
                            #We are the only binding that referrs to the handler.
                            #    Rename it without comment.
                            self.HandlerRename(OriginalName,NewName)
                            return 1
                        else:
                            #One or more other bindings refer to the hander. Ask the
                            #    user for guidance.
                            M = ('%s other binding{/s} or command-option{/s} also refer{s/} '
                                'to the event handler ' 
                                '"$s". You have a choice between simply changing the name ' 
                                'of the hander to "$s" or creating a new handler of that ' 
                                "name specifically for this command-option. If this isn't "
                                "perfectly clear then click Help for additional explanation.")
                            M = rpHelp.Plural(M,Count-1,ToPercent='$')
                            M = M%(OriginalName,NewName)
                            #PrettyNumber = rpHelp.Plural('%s',Count-1).lower()
                            HelpTuple = ('%s.change.choice'%Who,(OriginalName,NewName
                                ,Count-1))
                            Choice = Rpw.MessageDialog(Title='Query',Message=M
                                ,Buttons=(('Change Name',0),('New Handler',1),('~Cancel',None))
                                ,Help=HelpTuple).Result
                            if Choice == None:
                                #User cancelled
                                return None
                            if Choice == 0:
                                #User wants to change the name
                                self.HandlerRename(OriginalName,NewName)
                            elif Choice == 1:
                                #User wants to create new handler of this name
                                self.HandlerEnsure(NewName)
                            else:
                                raise Exception, "Unexpected Choice: "+Choice
                            return 1    

        
class rpDndCanvasTrash(rpDndCanvas,BindMixin):
    """=m
    An rpDndCanvas which is specifically tailored to be a trash bin.

    In addition to the regular 'Canvas' arguments, you must supply a name for this
        Canvas (as parameter "rapydname=") which we use when we register with the
        repository. This should be a descriptive name of this canvas.
    """

    def __init__(self, Master, **kw):
        """
        Create the trash bin.
        """
        assert kw.has_key('rapydname'), 'You HAVE to supply a name'
        self.OurName = kw['rapydname']
        del kw['rapydname'] 
        #Register ourself with the repository
        apply(DND.CanvasDnd.__init__,(self,Master),kw)
        self.RepoSignup()

    def RepoSignup(self):
        """
        Signup with the repository.
        """
        self.WRID = Repo.Register(self.OurName)
        assert None <> self.WRID, 'Repository registration failed'

    def dnd_commit(self,Source,Event):
        """
        A dragged object - presumably a widreq - is being dropped on us.
        
        "Source" is the widreq being dropped.
        """
        WidgetName = Source.Name
        if Source.PresentHome <> None:
            #The widreq lives somewhere. Make it's herd current.
            R = Repo.Request(self.WRID, 'HerdSelect', Source.PresentHome)
            if R <> 1:
                print R
                raise Exception, 'Request to make "%s" the current herd failed unexpectedly'%Source.PresentHome
            #Ask the repository to delete it
            R = Repo.Request(self.WRID, 'WidreqDelete', Source.Name)    
            if R <> 1:
                print R
                raise Exception, 'Request to delete widreq "%s" failed unexpectedly'%Source.Name
            #Tell the widreq it is homeless. This will prompt it to unregister from the
            #    repository when it is notified of being dropped.    
            Source.PresentHome = None        
        #It gone from the repository; now get rid of its canvas representation.
        Source.Vanish(All=1)
        #Update creation code to account for the deleted widreq
        GblLayout.CreationSystextRegen('TrashBin')    
        #Fetch a list of the handlers it references
        HandlerList = Source.HandlersList()
        #If any handlers are now orphans, give the user the option to delete them.
        self.OrphanHandlersProcess(WidgetName,HandlerList)

class TextEdit(Frame, BindMixin, MenuAids):
    """
    Text editor for user access to source code.
    """

    def __init__(self,Master,**kw):
        #Create the widget
        apply(Frame.__init__,(self,Master),kw)
        self.Scheme = Cfg.Info['Schemes'][Cfg.Info['SchemeCurName']]

        #
        #--- the menu bar ---
        #
        self.MenuBarFrame = Frame(self,borderwidth=2,relief=RAISED)
        self.MenuBarFrame.pack(side=TOP, fill=X)
        
        #
        #--- the text editing area
        #
        self.TextArea = rpHelp.ScrolledWhatever(self,widget=Rpw.ColorizedText)
        self.TextWidget = self.TextArea.FetchWidget()
        self.TextWidget.config(bg=self.Scheme['Colors']['background'],fg=self.Scheme['Colors']['other']
            ,font=self.Scheme['Font'],insertontime=500,insertofftime=50,insertwidth=3,wrap='none'
            ,insertbackground=self.Scheme['Colors']['cursor'])
        self.TextWidget.bind('<F1>',self.on_TextWidgetHelp)
        self.TextWidget.bind('<ButtonRelease-3>',self.on_TextRightClick)
        #We vet buttonrelease-2 in order to prevent middle-click insert into systext
        self.TextWidget.bind('<ButtonRelease-2>',self.on_TextMiddleClickRelease)
        self.TextWidget.bind('<Button-2>',self.on_TextMiddleClick)
        #PgUp/PgDn don't work right on their own, so we handle them manually
        self.TextWidget.bind('<KeyPress-Next>',self.on_KeyNext)
        self.TextWidget.bind('<KeyPress-Prior>',self.on_KeyPrior)
        #This is the height, in pixels, of each line of text. Used by PgUp/PgDn handlers.
        self.TextHeight = TextMeasureHeight(self.TextWidget)

        #Edit menu
        
        self.EditButton = Menubutton(self.MenuBarFrame,text=' Edit ',pady=0)
        self.EditButton.pack(side=LEFT,fill=X) 
        self.EditButton.bind(HelpButton,self.on_ActionEditHelp)
        
        self.EditMenu = Menu(self.EditButton,tearoff=0)

        self.ActionMenuSetup()
        self.ActionMenuAdd('Cut')
        self.ActionMenuAdd('Cut append')        
        self.ActionMenuAdd('Copy')        
        self.ActionMenuAdd('Copy append')
        self.ActionMenuAdd('Paste')
        self.ActionMenuAdd('Select all')
        
        self.ActionMenuSep()
        self.ActionMenuAdd('Delete line')
        
        self.ActionMenuSep()
        self.ActionMenuAdd('Copy to file')
        self.ActionMenuAdd('Paste file')

        self.ActionMenuSep()
        self.ActionMenuAdd('Indent line','Indent')
        self.ActionMenuAdd('Indent block')
        self.ActionMenuAdd('Outdent line','Outdent')
        self.ActionMenuAdd('Outdent block')

        self.ActionMenuSep()
        self.ActionMenuAdd('First line','Top')
        self.ActionMenuAdd('Last line','Bottom')
        self.ActionMenuAdd('Goto to line number','Goto')
        self.ActionMenuAdd('Push line number')
        self.ActionMenuAdd('Pop to line number')
        self.ActionMenuAdd('Swap with top')
        self.ActionMenuAdd('Forget')

        self.ActionMenuSep()
        self.ActionMenuAdd('Restart colorizer','Recolorize')
        
        self.ActionMenuSep()
        self.ActionMenuAdd('Help','EditHelp')
        self.ActionMenuGenerate(self.EditMenu)

        self.EditButton.config(menu=self.EditMenu)

        #Search menu
        self.SearchButton = Menubutton(self.MenuBarFrame,text=' Search ',pady=0)
        self.SearchButton.pack(side=LEFT,fill=X) 
        self.SearchButton.bind(HelpButton,self.on_ActionSearchHelp)
        
        self.SearchMenu = Menu(self.SearchButton,tearoff=0)

        self.ActionMenuAdd('Search')
        self.ActionMenuAdd('Search again')
        self.ActionMenuAdd('Search and replace','SearchReplace')
        
        self.ActionMenuSep()
        self.ActionMenuAdd('Find matching','FindMatch')
        
        self.ActionMenuSep()
        self.ActionMenuAdd('Help','SearchHelp')
        self.ActionMenuGenerate(self.SearchMenu)
        
        self.SearchButton.config(menu=self.SearchMenu)

        if Cfg.Info['Debug']:
            #Debug menu
            self.DebugButton = Menubutton(self.MenuBarFrame,text=' Debug ',pady=0)
            self.DebugButton.pack(side=LEFT,fill=X) 
        
            self.DebugMenu = Menu(self.DebugButton,tearoff=0)
            self.DebugMenu.add_command(label='Dump current line with tags',command=Wow(self,'on_Debug','DumpLine'))
            self.DebugButton.config(menu=self.DebugMenu)

        #Info area
        self.InfoLabel = Label(self.MenuBarFrame,padx=10,pady=0)
        self.InfoLabel.pack(side=RIGHT)
        self.InfoLabel.bind(HelpButton,self.on_InfoLabelHelp)

        #This causes us to colorize after the user has moved using the scrollbar
        self.TextArea.FetchYBar().bind('<ButtonRelease-1>'
            ,self.TextWidget.ColorizeVisible())
        #Get rid of all those annoying default Control bindings
        for C in 'abdefhiknoptv':
            self.TextWidget.unbind_class('Text','<Control-%s>'%C)    
        #Setup the key bindings as specified in the config file. Note that for this to work each
        #    Action Implementation Method must have a name of the form "on_Action<x>" where <x>
        #    is the name of the action as known by the config file.
        self.GenerateBindings('TextWidget')
        #NewLine you get for free
        self.TextWidget.bind('<KeyRelease>', self.on_KeyRelease, '+')
        self.TextWidget.bind('<KeyPress>', self.on_KeyPress, '+')
        self.TextArea.FetchYBar().bind('<ButtonRelease-1>'
            ,self.on_ScrollBarRelease)
        self.TextWidget.bind('<ButtonRelease-1>',self.on_TextWidgetRelease)    
        self.TextArea.pack(side=BOTTOM,expand=YES,fill=BOTH)
        
        #Tag used for highlighting found matching brackets
        self.TextWidget.tag_config('MatchSet',background='#FF0000')
        self.MatchSet = None
        
        self.SearchSettings = None
        self.TextWidget.focus_set()
        self.TextWidget.mark_set(INSERT,'1.0')
        #LineStack is used to keep track of remembered lines. Each entry is a list of [Line-number, column-number].
        self.LineStack = []
        self.StatusUpdate()
        self.HaveKey = False

    #---------------------------------------------------------------------------
    # Public Methods
    #----------------------------------------------------------------------------

    def HandlerGoto(self,HandlerName):
        """
        Given a hander name, goto the first line of the handler
        """
        Target = self.TextWidget.search('def %s('%HandlerName,'1.0')
        if Target <> '':
            self.TextWidget.mark_set(INSERT,Target+'+1l')
            self.TextWidget.see(INSERT)
            self.TextWidget.ColorizeVisible()
            self.TextWidget.focus_set()

    def StatusUpdate(self):
        """
        Update the status display
        """
        #Look after lit up matching bracket. We count down to zero because we
        #    get called on release of the key the lit it up in the first place.
        #    The count has us turn it off on the *next* keystroke.
        if self.MatchSet <> None:
            self.MatchSet['Count'] -= 1
            if self.MatchSet['Count'] <= 0:
                self.TextWidget.tag_remove('MatchSet',self.MatchSet['Index'])
                self.MatchSet = None
        #Update the status line        
        Y,X = self.TextWidget.index(INSERT).split('.')
        #Compute total number of lines of code
        Size = int(float(self.TextWidget.index(END)))-1
        #Show the number of entries in the line stack.
        if self.LineStack:
            LS = len(self.LineStack)
        else:
            LS = '-'    
        self.InfoLabel['text'] = 'Line:%s/%s  %s'%(int(Y),Size,LS)

    #---------------------------------------------------------------------------
    # Action implementation routines
    #----------------------------------------------------------------------------

    def on_ActionBottom(self,Event=None):
        """
        Go to the last line of code.
        """
        self.TextWidget.mark_set(INSERT,END)
        self.TextWidget.see(INSERT)
        self.TextWidget.ColorizeVisible()
        return 'break'    

    def on_ActionCut(self,Event=None):
        """
        Cut text.
        """
        if self.TextWidget.SystextInSel():
            Rpw.ErrorDialog("You can't cut generated text")
        else:    
            try:
                self.TextWidget.clipboard_clear()
                Temp = self.TextWidget.get(SEL_FIRST,SEL_LAST)
                self.TextWidget.clipboard_append(Temp)
                self.ActionCutCommon()
            except TclError:
                Rpw.ErrorDialog('No text is selected. Nothing to cut.')    
        return 'break'    

    def on_ActionCutAppend(self,Event=None):
        """
        Append Cut text to buffer
        """
        if self.TextWidget.SystextInSel():
            Rpw.ErrorDialog("You can't cut generated text")
        else:    
            try:
                Temp = self.TextWidget.get(SEL_FIRST,SEL_LAST)
                self.TextWidget.clipboard_append(Temp)
                self.ActionCutCommon()
            except TclError:
                Rpw.ErrorDialog('No text is selected. Nothing to cut.')    
        return 'break'    

    def ActionCutCommon(self):
        """
        Common code for Cut and CutAppend
        """
        #If we were attempting to cut systext we wouldn't have gone this far. However, if
        #    we are cutting *everything* between two pieces of systext then that would
        #    cause the two systext regions to merge which is a Bad Thing.  Therefore we
        #    check and if the character before the cut area AND the character after the
        #    cut area are systext then after the cut we inject a Return to keep the 
        #    systext areas distinct.
        ReturnNeeded = ('bgldt' in self.TextWidget.tag_names(SEL_FIRST+'-1c')) \
        and ('bgldt' in self.TextWidget.tag_names(SEL_LAST+'+1c'))
        
        #bye bye text
        self.TextWidget.delete(SEL_FIRST,SEL_LAST)
        if ReturnNeeded:
            self.TextWidget.insert(INSERT,'\n','')

    def on_ActionCopy(self,Event=None):
        """
        Copy text.
        """
        try:
            self.TextWidget.clipboard_clear()
            Temp = self.TextWidget.get(SEL_FIRST,SEL_LAST)
            self.TextWidget.clipboard_append(Temp)
        except TclError:
            Rpw.ErrorDialog('No text is selected. Nothing to Copy.')    
        return 'break'    
        
    def on_ActionCopyAppend(self,Event=None):
        """
        Append copied text to buffer
        """
        try:
            Temp = self.TextWidget.get(SEL_FIRST,SEL_LAST)
            self.TextWidget.clipboard_append(Temp)
        except TclError:
            Rpw.ErrorDialog('No text is selected. Nothing to Copy.')        
        return 'break'    

    def on_ActionCopyToFile(self,Event=None):
        """
        Copy current selection to a file
        """
        try:
            self.SelNote()
            TempBuffer = self.TextWidget.get(SEL_FIRST,SEL_LAST)
        except TclError:
            Rpw.ErrorDialog('No text is selected. Nothing to Copy.')    
            return 'break'    
        File = tkFileDialog.asksaveasfile(parent=self.TextWidget
            ,initialfile='copied.txt',title='Copy to file')
        self.SelRestore()
        if not File:
            #User bailed
            return 'break'
        File.write(TempBuffer)
        File.close()    
        return 'break'    

    def on_ActionDeleteLine(self,Event=None):
        """
        Delete the current line.
        """
        Where = self.IndexToList(INSERT)
        From = self.TextWidget.index('%s.0'%Where[0])
        To = self.TextWidget.index('%s.0'%(Where[0]+1))
        ##D('Where=%s From=%s To=%s'%(Where,From,To))
        if self.TextWidget.SystextInRegion(From,To):
            #You can't indent generated text
            Rpw.ErrorDialog("Can't delete line which contains generated text")
            return 'break'
        if self.TextWidget.SystextBookendsRegion(From,To):    
            #You can't merge generated text clumps
            Rpw.ErrorDialog("Can't merge areas of generated text")
            return 'break'
        self.TextWidget.delete(From,To)

    def on_ActionFindMatch(self,Event=None):
        """
        Find matching bracket or brace and light it up in red.
        """
        Cur = self.TextWidget.get(INSERT)
        if not Cur in '[]{}()':
            return 'break'
        if Cur in '[{(':
            Backwards = 0
            Offset = '+1c'
            Stop = END
        else:
            Backwards = 1
            Offset = '-1c'
            Stop = '1.0'
        if Cur == '[':
            Pattern = '\\[|\\]'
            Target = ']'
        elif Cur == '{':
            Pattern = '{|}'
            Target = '}'
        elif Cur == '(':
            Pattern = '\\(|\\)'
            Target = ')'
        elif Cur == ']':            
            Target = '['
            Pattern = '\\[|\\]'
        elif Cur == '}':
            Pattern = '{|}'
            Target = '{'
        elif Cur == ')':
            Pattern = '\\(|\\)'
            Target = '('
        else:
            raise Exception, "Unhandled case"    
        Count = 1   
        Index = INSERT 
        while Count <> 0: 
            if not Backwards:
                #If going forward we have to skip over the starting or found character
                Index = Index + Offset
            R = self.TextWidget.search(Pattern,Index,backwards=Backwards,regexp=1
                ,stopindex=Stop)
            if R == '':
                return 'break'
            Index = R    
            Found = self.TextWidget.get(R)
            if Found == Target:
                Count -= 1
            else:
                Count += 1
        self.TextWidget.tag_add('MatchSet',Index)
        self.MatchSet = {'Count':2,'Index':Index}

    def on_ActionForget(self,Event=None):
        """
        Clear the stack of remembered lines.
        """
        self.LineStack = []
        self.StatusUpdate()
        return 'break'

    def on_ActionGoto(self,Event=None):
        """
        Put up a dialog box and go to the specified line.
        """   
        P = ''
        while 1:
            R = Rpw.PromptDialog(Title='Goto Line',Message='Enter line number:'
                ,Prompt=P).Result
            try:
                if R == None:
                    return 'break'
                R = int(R)
                #Move the insert mark as requested
                self.GotoLineNumber(R)
                break
            except ValueError:
                #User entered a non-number; have them try again
                P = R
        return 'break'    
            
    def on_ActionIndent(self,Event=None):
        """
        Indent the current line.
        """
        if self.TextWidget.CursorInSystext():
            #You can't indent generated text
            return 'break'
        Where = self.IndexToList(INSERT)
        #Generate an appropriate number of pad spaces
        Indent = self.Scheme['Indent']
        Pad = ' ' * (Indent - (Where[1] % Indent))
        #And stuff them into the line
        self.TextWidget.insert(self.ListToIndex(Where), Pad,'')
        return 'break'    

    def on_ActionIndentBlock(self,Event=None):
        """
        Indent the current block
        """
        if self.TextWidget.SystextInSel():
            Rpw.ErrorDialog("You can't indent generated text")
            return 'break'
        Extent = self.SelExtentFetch()
        Pad = ' ' * self.Scheme['Indent']
        Current, Last = Extent
        while Current < Last:
            self.TextWidget.insert('%s.0'%Current,Pad,'')
            Current += 1
        return 'break'    

    def on_ActionOutdent(self,Event=None):
        """
        Outdent the current line by IndentSize,
        
        This attempts to be the inverse of Indent (aka Tab). Whereas Indent inserts spaces until
            the cursor is on an Indent multiple, Outdent backspaces through spaces until the
            cursor is on an Indent multiple. We stop if the character to the left of the cursor 
            is not a space.
        """
        if self.TextWidget.CursorInSystext():
            #You can't outdent generated text
            return 'break'
        #Find out where we are now
        Line, Col  = self.IndexToList(INSERT)
        Count = self.Scheme['Indent']
        #Count is how many spaces we would like to delete    
        for J in range(Count):
            if Col <> 0:
                #We have not run out of spaces
                Col -= 1
            I = self.ListToIndex([Line,Col])
            T = self.TextWidget.get(I)
            #T is the character we would delete
            if ' ' <> T:
                #We ran out of spaces to delete
                break
            #Delete the space.
            self.TextWidget.delete(I)
        return 'break'    

    def on_ActionOutdentBlock(self,Event=None):
        """
        Outdent the current block.
        
        If the entire block can not be outdented then we take no action.
        """
        if self.TextWidget.SystextInSel():
            Rpw.ErrorDialog("You can't outdent generated text")
            return 'break'
        Extent = self.SelExtentFetch()
        Len = self.Scheme['Indent']
        Pad = ' ' * Len
        #First make sure all lines have room to outdent
        Current, Last = Extent
        while Current < Last:
            #From each line we take an indents worth of characters and strip them. If this
            #    goes to empty we know the line is indentable.
            Stuff = self.TextWidget.get('%s.0'%Current,'%s.end'%Current)[:Len].strip()
            if Stuff:
                #A line does not have room
                return 'break'
            Current += 1
        #All lines have room; do the deletion
        Current, Last = Extent
        while Current < Last:
            self.TextWidget.delete('%s.0'%Current,'%s.%s'%(Current,Len))
            Current += 1      
        return 'break'    
        
    def on_ActionPaste(self,Event=None):
        """
        Paste text
        """
        if self.TextWidget.CursorInSystext():
            Rpw.ErrorDialog("You can't paste into generated text")
            return 'break'
        #Note position of cursor before insert    
        Index = self.TextWidget.index(INSERT)    
        #Do the insert
        try:
            Temp = self.selection_get(selection='CLIPBOARD')
            self.TextWidget.insert(INSERT,Temp,'')
            #Put the cursor at top of insert and make sure we can see it
            self.TextWidget.mark_set(INSERT,Index)
            self.TextWidget.see(INSERT)
        except TclError:
            Rpw.MessageDialog(Message='The clipboard is empty; nothing to paste')    
        return 'break'

    def on_ActionPasteFile(self,Event=None):
        """
        Insert file at cursor
        """
        if self.TextWidget.CursorInSystext():
            Rpw.ErrorDialog("You can't paste into generated text")
            return 'break'
        File = tkFileDialog.askopenfile(parent=self.TextWidget
            ,initialfile='copied.txt',title='Paste file')
        if not File:
            #User bailed
            return 'break'
        #Note position of cursor before insert    
        Index = self.TextWidget.index(INSERT)    
        #Do the insert
        Text = File.read()
        if len(Text) > 50000:
            Dialog = Rpw.ProgressDialog(title=' Loading... ')
            ProgressFunc = Dialog.Set
        else:
            ProgressFunc = None    
        self.TextWidget.insert(INSERT,Text,tags='',ProgressFunction=ProgressFunc)
        File.close()
        if ProgressFunc <> None:
            Dialog.Close()        
        #Put the cursor at top of insert and make sure we can see it
        self.TextWidget.mark_set(INSERT,Index)
        self.TextWidget.see(Index)
        return 'break'    

    def on_ActionPopToLineNumber(self,Event=None):
        """
        Pop top entry from rememberances stack and goto that line
        """
        if self.LineStack:
            R = self.LineStack.pop()
            self.TextWidget.mark_set(INSERT,self.ListToIndex(R))
            self.TextWidget.see(INSERT)
            self.TextWidget.ColorizeVisible()
            self.StatusUpdate()
        else:
            Rpw.ErrorDialog(Message='There is no remembered line to go to.')    
        return 'break'    

    def on_ActionPushLineNumber(self,Event=None):
        """
        Push current line and column numbers on the rememberance stack
        """
        self.LineStack.append(self.IndexToList(self.TextWidget.index(INSERT)))
        self.StatusUpdate()
        return 'break'    

    def on_ActionRecolorize(self,Event=None):
        """
        Restart the colorizer from the first visible line.
        """
        self.TextWidget.CibInit(self.TextWidget.Visible()[0])
        return 'break'    
        
    def on_ActionSearchAgain(self,Event=None):
        """
        Repeat an existing search
        """
        self.SearchCommon(Ask=0)
        return 'break'    
                    
    def on_ActionSearch(self,Event=None):
        """
        Initiate a search.
        """
        self.SearchCommon(Ask=1)
        return 'break'    
        
    def on_ActionSearchReplace(self,Event=None):        
        """
        Initialte search and replace
        """
        #Get the search settings
        self.SelNote()
        Info = Rpw.SearchDialog(where=self.TextWidget,sizeguess=(310,370)
            ,AndReplace=True,settings=self.SearchSettings).Result
        self.SelRestore()    
        self.SearchSettings = Info
        if Info == None or Info['Text'].strip() == '':
            #user bailed or entered no text
            return 'break'
        #We have the settings - do the search            
        if Info['Top']:
            #We are to search from first/last line
            if Info['Back']:
                #Were searching backwards from the last line
                self.TextWidget.mark_set(INSERT,END)  
                StopIndex = '1.0'
            else:
                #Were searching forwards from the first line
                self.TextWidget.mark_set(INSERT,"1.0")
                StopIndex = END
        #Set the stopping point based on direction of search        
        if Info['Back']:
            #Were searching backwards from the last line
            StopIndex = '1.0'
        else:
            #Were searching forwards from the first line
            StopIndex = END
        SearchCount = IntVar() 
        ReplaceCount = 0
        while 1:
            Where = self.TextWidget.search(Info['Text'],INSERT,backwards=Info['Back'],regexp=Info['Regex']
                ,nocase=not Info['Case'],count=SearchCount,stopindex=StopIndex)
            #We reset the "from first/last" setting automatically    
            Info['Top'] = 0    
            if Where:
                #We have found text that matches, but before we rush off to do a replace we must
                #    check to make sure that none of the found text is systext. If any of the match
                #    is systext then we don't prompt the user and we don't replace.
                Past = Where + '+%sc'%SearchCount.get()
                NoSystext = not self.TextWidget.SystextInRegion(Where,Past)
                #D('Where=%s, Past=%s, T=%s'%(Where,Past,T))
            if Where:
                #We found a match
                if Info['Prompt'] and NoSystext:
                    #User wants to be prompted and match contains no systext
                    self.TextWidget.tag_remove(SEL,'1.0',END)
                    self.TextWidget.tag_add(SEL,Where,Past)
                    self.TextWidget.see(Where)
                    #Attempt to place the confirmation dialog so it doesn't block the users
                    #   view of the selected area. This algorithm works fine as long as there
                    #   is more text than will fit in the text widget. If there are so few
                    #   lines of text that they do not fill the widget then we may place the
                    #   prompt dialog over the selected text. Whats really needed here is some
                    #   way of finding where a particular index is within the widget; if there
                    #   is a reasonable way to do that it is unknown to me. Given a point in
                    #   the widget you can find the nearest text character but there is no
                    #   inverse function and given that the current algorithm works for all
                    #   but tiny amounts of text, I wasn't going to spend a lot of time on
                    #   it. 
                    First,Last = self.TextWidget.Visible()
                    Target = int(float(Where))
                    ##D('First=%s Last=%s Target=%s'%(First,Last,Target))
                    if Target < ((First+Last)/2):
                        #selected stuff is in the upper half of the widget
                        FactorY = 0.6
                    else:
                        #selected stuff is in the lower half of the widget
                        FactorY = 0.1
                    WidgetGeo = rpHelp.WidgetInScreen(self.TextWidget)
                    #Desired displacement from top of Text widget
                    DeltaY = int(WidgetGeo[1] * FactorY)
                    Y = WidgetGeo[3] + DeltaY
                    #Desired absolute Y position on screen
                    XY = (WidgetGeo[2]+25,Y)
                    Doit = Rpw.MessageDialog(Title='Confirm'
                        ,Message='Replace with "%s"?'%Info['RepText']
                        ,XY=XY,Buttons=(('Replace',1),('No',None),('~Cancel',0))).Result
                    if Doit == 0:
                        #User said to cancel
                        return 'break'
                    #Doit will now be 1 for replace and None for don't-replace
                else:
                    #Used does not want to be prompted or match contains systext.
                    Doit = NoSystext
                #In order to be able to continue searching (without re-finding the text just found)
                #    we place the INSERT cursor just after the text if searching forward or just
                #    before the text if searching backward.
                if Info['Back']:
                    self.TextWidget.mark_set(INSERT,Where)
                else:
                    self.TextWidget.mark_set(INSERT,Past)
                if Doit:
                    ReplaceCount += 1
                    self.TextWidget.delete(Where,Past)
                    self.TextWidget.insert(Where,Info['RepText'],'')
                    if not Info['All']:
                        self.TextWidget.see(INSERT)
                        return 'break'
            else:
                #We did not find the text
                self.TextWidget.see(INSERT)
                if ReplaceCount == 0:
                    Message = 'Search string not found.'
                else:
                    Message = rpHelp.Plural('%s replacement{/s} done.',ReplaceCount)    
                Rpw.MessageDialog(Message=Message)    
                break
        return 'break'    
        
    def on_ActionSelectAll(self,Event=None):
        """
        Select all text
        """        
        self.TextWidget.tag_remove(SEL,'1.0',END)
        self.TextWidget.tag_add(SEL,'1.0',END)
        return 'break'    
            
    def on_ActionSwapWithTop(self,Event=None):
        """
        Swap top of rememberance stack with current line
        """
        if self.LineStack:
            R = self.LineStack[-1]
            self.LineStack[-1] = self.IndexToList(self.TextWidget.index(INSERT))
            self.TextWidget.mark_set(INSERT,self.ListToIndex(R))
            self.TextWidget.see(INSERT)
            self.TextWidget.ColorizeVisible()
            self.StatusUpdate()
        else:
            Rpw.ErrorDialog(Message='There is no remembered line to swap with.')    
        return 'break'    

    def on_ActionTop(self,Event=None):
        """
        Go to the first line of code.
        """
        self.TextWidget.mark_set(INSERT,"1.0")
        self.TextWidget.see(INSERT)
        self.TextWidget.ColorizeVisible()
        return 'break'    


    def SearchCommon(self,Ask): 
        """
        This routine does the work for "Search" and "SearchAgain".
        
        If "Ask" is false and we already have search settings in "self.SearchSettings"
            then we just go ahead and start the search. Otherwise we put up the dialog
            and her the user enter the search settings.
        """
        if Ask or self.SearchSettings == None:   
            #Either we were told to ask or there were no prior settings
            self.SelNote()
            Info = Rpw.SearchDialog(where=self.TextWidget,sizeguess=(310,320)
                ,settings=self.SearchSettings).Result
            self.SelRestore()    
            if Info == None or Info['Text'].strip() == '':
                #user bailed or entered no text
                return
            self.SearchSettings = Info    
        else:
            Info = self.SearchSettings    
        #We have the settings - do the search            
        if Info['Top']:
            #We are to search from first/last line
            if Info['Back']:
                #Were searching backwards from the last line
                self.TextWidget.mark_set(INSERT,END)  
                StopIndex = '1.0'
            else:
                #Were searching forwards from the first line
                self.TextWidget.mark_set(INSERT,"1.0")
                StopIndex = END
        #Set the stopping point based on direction of search        
        if Info['Back']:
            #Were searching backwards from the last line
            StopIndex = '1.0'
        else:
            #Were searching forwards from the first line
            StopIndex = END
            
        SearchCount = IntVar() 
        Where = self.TextWidget.search(Info['Text'],INSERT,backwards=Info['Back'],regexp=Info['Regex']
            ,nocase=not Info['Case'],count=SearchCount,stopindex=StopIndex)
        #We reset the "from first/last" setting automatically    
        self.SearchSettings['Top'] = 0    
        if Where:
            #We found the text
            self.TextWidget.tag_remove(SEL,'1.0',END)
            Past = Where + '+%sc'%SearchCount.get()
            #In order to be able to continue searching (without re-finding the text just found)
            #    we place the INSERT cursor just after the text if searching forward or just
            #    before the text if searching backward.
            if Info['Back']:
                self.TextWidget.mark_set(INSERT,Where)
            else:
                self.TextWidget.mark_set(INSERT,Past)
            self.TextWidget.see(Where)
            self.TextWidget.ColorizeVisible()
        else:
            Rpw.MessageDialog(Message='Search string not found')    
        
    #---------------------------------------------------------------------------
    # End Action implementation routines
    #----------------------------------------------------------------------------


    def on_KeyNext(self,Event=None):
        """
        Handle PgDn key.
        
        TextWidgets have built-in PgUp/PgDn handling, but some of the time annoyingly they
            are not symetrical. That is, even if you are well away from start/end, that
            PgUp followed by PgDn doesn't land you back on the original line. A small point
            but it gets annoying after a while.
        """
        Delta = int(self.TextWidget.winfo_height() / self.TextHeight)
        self.TextWidget.mark_set(INSERT,'insert+%sl'%Delta)
        self.TextWidget.see(INSERT)
        self.TextWidget.ColorizeVisible()
        return 'break'        

    def on_KeyPrior(self,Event=None):
        """
        Handle PgUp key.
        """
        Delta = int(self.TextWidget.winfo_height() / self.TextHeight)
        self.TextWidget.mark_set(INSERT,'insert-%sl'%Delta)
        self.TextWidget.see(INSERT)
        self.TextWidget.ColorizeVisible()
        return 'break'        

    def on_TextMiddleClick(self,Event=None):
        """
        Serve help in response to middle click.
        """
        Help('code-editor')
        
        
    def on_TextMiddleClickRelease(self,Event=None):
        """
        Inserting text via middle clicking is problematic for us.
        """
        return 'break'
        

    def on_TextRightClick(self,Event=None):
        """
        Handle right click over text
        
        If the cursor is over the systext of an event handler then we pop up a menu
            of event handler actions.
        """
        self.HandlerName = self.TextWidget.HandlerSeekAt(CURRENT)
        if self.HandlerName:
            Bgc = '#000000'
            HandlerPopup = Menu(self,tearoff=0)
            HandlerPopup.add_command(label='Event handler: %s'%self.HandlerName,state=DISABLED
                ,activeforeground='#FFFFFF',foreground='#FFFFFF',background=Bgc,activebackground=Bgc)
            HandlerPopup.add_separator()
            HandlerPopup.add_command(label='See references',command=self.on_PopupSeeReferences)
            HandlerPopup.add_command(label='Rename',command=self.on_PopupRename)
            HandlerPopup.add_separator()
            HandlerPopup.add_command(label='Delete',command=self.on_PopupDelete)
            HandlerPopup.add_separator()
            HandlerPopup.add_command(label='Help',command=self.on_PopupHelp)
            HandlerPopup.tk_popup(Event.x_root,Event.y_root)

    def on_PopupSeeReferences(self,Event=None):
        """
        Show references to event handler
        """
        Refs = self.HandlerReferencesCount(self.HandlerName,Verbose=True)
        Rpw.HandlerReferencesDialog(HandlerName=self.HandlerName,Refs=Refs)
        
    def on_PopupRename(self,Event=None):
        """
        Help user rename event handler
        """
        H = self.TextWidget.HandlerNameList()
        R = self.HandlerReferencesCount(self.HandlerName)
        Result = Rpw.HandlerRenameDialog(HandlerName=self.HandlerName,HandlerList=H,RefCount=R).Result
        if Result:
            self.HandlerRename(self.HandlerName,Result)
            if R > 0:
                #Update creation systext to note the changed bindings
                GblLayout.CreationSystextRegen('Event-handler popup rename')    
        
    def on_PopupDelete(self,Event=None):
        """
        Help user delete event handler
        """ 
        RefCount = self.HandlerReferencesCount(self.HandlerName)
        if RefCount == 0:
            Msg = ('No Rapyd-Tk maintained bindings nor command-options refer to '
                'event handler %s. Delete this handler now?')
        else:
            Msg = ('%s Rapyd-Tk maintained binding{/s} or command-option{/s} refer{s/} to '
                'event handler $s. Referring bindings will be deleted while referring '
                'command-options will be cleared. Delete this handler and its referring '
                'binding{/s}/command-option{/s} now?')
            Msg = rpHelp.Plural(Msg,RefCount,ToPercent='$')
        Msg=Msg%self.HandlerName
        R = Rpw.MessageDialog(Title='Last Chance'
            ,Message=Msg
            ,Buttons=(('Delete Now',1),('~Cancel',None))
            ,Help=('HandlerDelete',[self.HandlerName,RefCount])).Result
        if R == 1:
            self.HandlerDelete(self.HandlerName)    
            if RefCount > 0:
                #Update creation systext to note the deleted bindings
                GblLayout.CreationSystextRegen('Event handler popup delete')    

        
    def on_PopupHelp(self,Event=None):
        """
        Help on event handler popup
        """           
        Help('Eventhandler-popup-menu')

    def on_ActionEditHelp(self,Event=None):
        Help('code-edit.edit-menu')
        
    def on_ActionSearchHelp(self,Event=None):
        Help('code-edit.search-menu')
        
    def on_InfoLabelHelp(self,Event=None):
        Help('code-edit.info-label')        

    def on_TextWidgetHelp(self,Event=None):
        Help('code-editor')
        
    def on_ScrollBarRelease(self,Event):
        """
        User let go of vertical scroll bar.
        """
        #Make sure our new text is colorized.
        self.TextWidget.ColorizeVisible()
        self.CursorVisible()
        self.StatusUpdate()

    def on_TextWidgetRelease(self,Event):
        """
        User just finished clicking over text.
        """
        self.StatusUpdate()

    def CursorVisible(self):
        """
        If the cursor is not visible, place it mid widget.
        """
        First,Last = self.TextWidget.Visible()
        Cursor = int(float(self.TextWidget.index(INSERT)))
        if Cursor < First or Cursor > Last:
            Middle = (First+Last)/2
            self.TextWidget.mark_set(INSERT,'%s.0'%Middle)

    def on_Debug(self,Option):
        """
        Handle request from debug menu
        """
        if Option == 'DumpLine':
            self.TextWidget.LineDump(self.CurrentLineNumberFetch())
        else:
            print 'Unknown Debug option: %s'%Option    

    def GotoLineNumber(self,LineNumber,ColumnNumber=0):
        """
        Move the cursor to the specified line and, optionally, column.
        
        Note that LineNumber is origin-1 while columnNumber is origin-0.
        """
        self.TextWidget.mark_set(INSERT,self.ListToIndex([LineNumber,ColumnNumber]))
        self.TextWidget.see(INSERT)
        self.TextWidget.ColorizeVisible()
        self.TextWidget.focus_set()

    def SelExtentFetch(self):
        """
        Return a (From,To) pair indicating the extent of the selected block.
        
        "From" is the first line of the selected block. "To" is the first line
            *after* the selected block. If no block is selected we return a
            "To/From" pair indicating the current line.
        """
        try:
            From = int(float(self.TextWidget.index(SEL_FIRST)))
            To = int(float(self.TextWidget.index(SEL_LAST)))+1
        except:    
            #No selected block
            From = int(float(self.TextWidget.index(INSERT)))
            To = From + 1
        return (From,To)    

    def SelNote(self):
        """
        Note the currently selected area in "self.SelectionNoted" tuple.
        """
        try:
            self.SelectionNoted = (self.TextWidget.index(SEL_FIRST)
                ,self.TextWidget.index(SEL_LAST))
        except TclError:
            self.SelectionNoted = None        
            
    def SelRestore(self):
        """
        Restore the selected area from "self.SelectionNoted".
        
        There are a number of instances where our selected area gratituitiously
            goes away, for example when we call up a load/save dialog box. Therefore
            prior to such an event we save the extent of the selected area using
            "self.SelNote" and this routine to put the selection back. The obvious
            thing for this routine to do is simply the two lines of code which you
            can see below in routine "SelRestoreReally". *However* if you simply
            code that here it does *not* restore the selection. You apparently 
            have to wait for something else to happen and *then* you can restore
            the selection without difficulty. Therefore, we set a really short
            "after" and the routine "SelRestoreReally" sets the selection and it
            actually works. It took me a certain amount of time to figure this
            out and come up with a solution that works. !@$%$#%*^! 
        """
        if self.SelectionNoted:
            self.TextWidget.after(1,self.SelRestoreReally)
        
    def SelRestoreReally(self):
        #See "SelRestore"
        self.TextWidget.tag_remove(SEL,'1.0',END)
        self.TextWidget.tag_add(SEL,self.SelectionNoted[0],self.SelectionNoted[1])
        
    def on_KeyPress(self,Event):
        #HaveKey helps us solve a little problem. If the user calls up a dialog
        #    for example, the GOTO dialog, and then they close the dialog by
        #    pressing the ENTER key and if that dialog is bound to <KeyPress>
        #    then WE end up getting the key release which we don't really want,
        #    since a keyrelease on ENTER prompts us to indent the current line.
        #    Therefore on a keypress genuinely for us we set HaveKey and then
        #    in the KeyRelease handler, just below, we check HaveKey. If it is
        #    not set we know this is a spurious release which we ignore.
        self.HaveKey = True
                        
    def on_KeyRelease(self,Event):
        """
        Handle key-release formatting and status issues
        """
        if not self.HaveKey:
            return
        self.HaveKey = False    
        if Event.keysym in ('Alt_L','Alt_R','Caps_Lock','Control_L','Control_R','Shift_L','Shift_R'):
            #ignore keys that for sure don't change things
            return
        if Event.keysym in ('Down','Left','Next','Prior','Right','Up'):
            self.StatusUpdate()
            return
        self.StatusUpdate()    
        if Event.keysym == 'Return' and not self.TextWidget.CursorInSystext():
            #The key is Return and the cursor is not in systext. We shouldn't have to check for
            #    systext here because ColorizedText has already detected a Return in systext and has
            #    returned 'break' to stop the event chain. This works for plain old Return but it
            #    does not work for Alt/Return nor Ctrl/Return hence we have to do the check. This
            #    whole issue smells a bit fishy; when you depress Ctrl or Alt then the first Return
            #    pressed gets through to us here but subsequent ones (as long as you hold down the
            #    Alt/Ctrl key) don't.
            #In any case, having arrived here, this is where we attempt to indent the newly minted
            #    line including increasing the indent if the previous line is not a comment and ends
            #    with a colon.
            #Get the text of the previous line
            PrevLine = self.CurrentLineNumberFetch()-1
            PrevText = self.LineFetch(PrevLine)
            #We want to indent the new line under the previous line
            Count = 0
            for C in PrevText:
                if C <> ' ':
                    break
                Count += 1
            #The colorizer is kind enough to save the flag information available at the 
            #    end of colorizing the previous line. Fetch that info and verity that
            #    we are talking about the same line
            Flag = self.TextWidget.RecentFlagInfo['Flag']
            L = self.TextWidget.RecentFlagInfo['Line']
            assert L == PrevLine, 'Unexpexted difference in line numbers'    
            if PrevText[-1:] == ':' and Flag[0] == 0 and Flag[2] == 0:
                #Line ends with a colon and not inside quotes and no hash comment in effect
                Count += self.Scheme['Indent']    
            if Count:
                #insert spaces if required
                self.TextWidget.insert(INSERT,''+(' '*Count),'')
        self.TextWidget.update_idletasks()


    def CurrentLineFetch(self):
        """
        Fetch the current line
        """        
        Temp = self.TextWidget.index(INSERT)
        Temp = self.LineColToList(Temp)
        return self.LineFetch(Temp[0])

    def CurrentLineNumberFetch(self):
        """
        Return the current line number as in integer
        """
        Temp = self.TextWidget.index(INSERT)
        return self.LineColToList(Temp)[0]

    def LastLineNumberFetch(self):
        """
        Fetch the numer of the last line of text.
        
        For reasons unknown to me, the END index returns one greater than the actual number of
            the last line. For example, if your text consists of 'yada\nyada' then the END index
            returns 3.0 when in fact there are only two lines. That explains the "- 1" in 
            the code below.
        """
        Temp = self.TextWidget.index(END)
        return self.LineColToList(Temp)[0] - 1

    def LineFetch(self,LineNumber):
        """
        Fetch the specified line.
        """        
        return self.TextWidget.get('%s.0'%LineNumber,'%s.end'%LineNumber)

    def LineColToList(self,LineCol):
        """
        Convert a Text widget "line.column" designator to a Python numeric list [line,column]
        """
        T = LineCol.split('.')
        return [int(T[0]), int(T[1])]

    def ListToIndex(self,List):
        """
        Given a [line,column] list, convert it to a string index "line.column"
        """
        return '%s.%s'%(List[0],List[1])

    def IndexToList(self,Index):
        """
        Given a Text widget index specifier, return a [line,column] list.
        
        "Index" is a string giving an index, eg "INSERT" etc.
        """
        return self.LineColToList(self.TextWidget.index(Index))


class BindEdit(Frame, BindMixin):
    """=m
    The bind editor widget that goes inside the Widgetator bind edit page
    """
    def __init__(self, Master, Widreq, Height, Widths):
        """
        Create the bind editor.
        """
        self.Frame = self
        self.HeightTotal = Height
        self.CurrentWidreq = Widreq
        self.WidthEvent = Widths[0]
        self.WidthHandler = Widths[1]
        self.NeedRefresh = False
        Frame.__init__(self,Master)
        #Register with WidreqRepository
        self.WRID = None
        self.Register(Widreq.Name)
        #We devote this much space to each edit item
        self.HeightEach = Cfg.Info['Metrics']['Entry'][2] + 2
        self.WidthResizeKnob = Cfg.Info['ResizeIcon'].width()
        self.HeightResizeKnob = Cfg.Info['ResizeIcon'].height()
        #We use this much space above the edit items for the resize knobs
        self.HeightOverhead = self.HeightResizeKnob
        #Total width available to us
        self.WidthTotal = self.WidthEvent + self.WidthHandler
        #Total height for the main edit canvas
        self.HeightForCanvas = self.HeightTotal - self.HeightOverhead
    
        self.HeightAssistIcon = Cfg.Info['AssistIcon'].height()
        self.WidthAssistIcon = Cfg.Info['AssistIcon'].width()
        #This is the smallest we let the edit area get. We allow room for a 20 pixel entry widget,
        #    AssistIcon,  Scroll bar.
        self.WidthMinEdit = 30+self.WidthAssistIcon+Cfg.Info['Metrics']['ScrollBarWidth']
        self.HeightSelectionOffset = 1
            
        #The proto selectionbox
        self.SelectionBox = {'X':None, 'Y': None, 'Index':None}
    
        #Generate initial display
        self.Generate()

    def Register(self,OurName):
        """=r
        Register (or re-register) with the repository.
        
        This gets called if our name or the herd in which we reside changes.
        """
        RegistryName = 'BindEdit for %s on %s'%(OurName, Repo.SelectedHerd)
        if self.WRID == None:
            #We haven't registered yet; do so
            self.WRID = Repo.Register(RegistryName)
            assert self.WRID <> None, 'Initial registration of widget %s failed unexpectedly'%OurName
        else:
            #we are already registered; change our name    
            R = Repo.Rename(self.WRID,RegistryName) 
            assert R == 1, 'Regigester of widget %s failed unexpectedly'%OurName
        #It is important to re-bind if we have changed herds. Always binding achieves this.
        Repo.Bind(self.WRID, 'WidreqCreateQuery WidreqSelectQuery HerdSelectQuery '
            'WidreqSelectNotify WidreqRenameNotify', self.WidrepCallback)

    def Terminate(self):
        if self.WRID <> None:
            Repo.Unregister(self.WRID)
            self.WRID = None

    def WidrepCallback(self,Event,A,B):
        """=r
        This is bound to certain WidreqRepository events.
        """
        if Event in ['WidreqCreateQuery', 'WidreqSelectQuery', 'HerdSelectQuery']:
            #Do we care about these?
            return 1
        if Event == "WidreqSelectNotify":
            if A == self.CurrentWidreq.Name:
                #we are the widreq which was just selected, in which case we start caring about
                #requests to create or select a different widrea
                Repo.Bind(self.WRID, 'WidreqCreateQuery WidreqSelectQuery', self.WidrepCallback)
            else:
                #Since we are no longer selected there is no point in watching these requests
                Repo.Unbind(self.WRID, 'WidreqCreateQuery WidreqSelectQuery')
            return
        if Event == 'WidreqRenameNotify':
            #If we have been renamed we must update our registration with the repository
            if B == self.CurrentWidreq.Name:
                #That's us that just got renamed
                self.Register(B)
            return
        print 'BindEdit got unexpected Widrep event "%s"'%Event        
        
    def ReportWidths(self):
        """
        Return a 2-list giving widths of Event and Handler areas as presently drawn.
        """
        return [self.WidthEvent,self.WidthHandler]

    def NotifyExternalChange(self):
        """
        Called if an external agent changes some of our data.
        
        We should refresh our display the next time we are the active editor.
        
        This is needed in cases where editor information is changed by someone
            out the editor (eg change of event handler name in option command)
        """
        self.NeedRefresh = True
        
    def EditorRefresh(self):
        """
        Refresh our display if needed.
        """
        if self.NeedRefresh:
            self.Generate()

    def on_GeneralClick(self,Event):
        """
        This handles clicking on entry and help requests.
        """
        Help(Event.widget.HelpTopic)

    def ComputeHeights(self):
        """=z
        Compute the height required to accomodate all items we need to edit.
        """
        Stuff = self.CurrentWidreq.Bindings
        self.HeightRequired = self.HeightEach * len(Stuff)
    
    def DoScrollBar(self):
        """=m
        Install/Deinstall Y scroll bar as needed.
        """
        self.ComputeHeights()
        if self.HeightRequired > self.HeightForCanvas:
            if not hasattr(self,'ScrollY'):
                self.ScrollY = Scrollbar(self.Frame,orient=VERTICAL
                    ,command=self.Canvas.yview)
                self.ScrollY.pack(side=RIGHT,fill=Y)    
                self.Canvas['yscrollcommand'] = self.ScrollY.set
        else:
            if hasattr(self,'ScrollY'):
                #get rid of the existing scroll bar
                self.Canvas['yscrollcommand'] = None
                self.ScrollY.pack_forget()
                del self.ScrollY

    def on_Assist(self,Event):
        """
        User clicked on a bind assist button.
        """
        if self.CurrentWidreq.PresentHome == 'the Parking Lot':
            M = "You can't alter a widget's bindings while it is on the parking lot"
            Rpw.MessageDialog(Message=M,Help='bind.on.parkinglot')
            return
        BindIndex = Event.widget.OurIndex
        #CurrentEvents is a list of tuples, one for each binding of this widreq except
        #   the current binding. Each tuple consists of [0] the event string for this
        #   binding, [1] the Component for this binding. We pass this list to the assist 
        #   in an effort to prevent the user from accidentally creating duplicate bindings.
        CurrentEvents = [(J[1],J[3]) for J in self.CurrentWidreq.Bindings]
        try:
            Quad = self.CurrentWidreq.Bindings[BindIndex]
            del CurrentEvents[BindIndex]
        except IndexError:
            #This happens when user accesses the 'new binding' slot at the end.
            Quad = [None,'','','']    
        OriginalInfo = copy.deepcopy(Quad)
        #Give user the opportunity to edit the binding    
        TextEditor = GblLayout.TextEditFetch().TextWidget
        CompList = self.CurrentWidreq.ListComponents()
        R = Rpo.BindAssist(Quad, self.CurrentWidreq.Name, CurrentEvents
            ,TextEditor.HandlerNameList(),CompList).Result
        if R == None:
            #User bailed
            return
        elif R == '*DELETE*':
            NewName = R
        else:
            NewName = R[2]    
        Temp = self.HandlerChangeProcess(OriginalInfo[2],NewName,'bind')
        if Temp == None:
            #User cancelled
            return
        elif Temp == 0:
            #The binding was deleted as requested; toast the actual binding        
            self.CurrentWidreq.Bindings.pop(BindIndex)
        elif Temp == 1:
            #The new binding value was accepted        
            if OriginalInfo == [None,'','','']:
                #This is a newly minted binding
                self.CurrentWidreq.Bindings.append(R)
            else:    
                #Update the existing binding
                self.CurrentWidreq.Bindings[BindIndex] = R                            
        else:
            raise Exception, "Unexpected value = %s"%str(Temp)    

        #Regenerate the display to reflect the new binding.    
        self.Generate()            
        #Update text to reflect the change
        GblLayout.CreationSystextRegen('BindEditor')

    def on_GotoHandler(self,Event):
        """
        User double clicked to goto a handler
        """
        if self.CurrentWidreq.PresentHome == 'the Parking Lot':
            return
        OurIndex = Event.widget.OurIndex
        Decomposed, Event, Handler, Component = self.CurrentWidreq.Bindings[OurIndex]
        GblLayout.HandlerGoto(Handler)        
                
    def Generate(self):
        """=m
        Create and populate the canvas on which we actually edit
        """        
        self.NeedRefresh = False
        #If we already have a canvas then get rid of it.
        if hasattr(self,'Canvas'):
            self.Canvas.clear()
            self.Canvas.pack_forget()
            del self.Canvas
            if hasattr(self,'ScrollY'):
                self.ScrollY.pack_forget()
                del self.ScrollY
        #Stuff is the option information from our widreq
        self.CurrentWidreq.Bindings.sort()
        Stuff = self.CurrentWidreq.Bindings[:]
        Stuff.append((None,'','','')) #A spot for the user to create a new binding
        
        #Our edit area consists of:
        #    A label showing the event string
        #    A label showing the handler name
        #    The assist icon for changing things
        #   
        #    Scroll bar if necessary.
        self.ComputeHeights()
        WidthCanvas = self.WidthTotal
        #The fudge factor of +4 leaves room for our selection right of the assist icon
        HandlerPixels = self.WidthHandler - (self.WidthAssistIcon)
        if self.HeightRequired > self.HeightForCanvas:
            #scroll bar is required; adjust things
            HandlerPixels -= Cfg.Info['Metrics']['ScrollBarWidth']
            WidthCanvas -= Cfg.Info['Metrics']['ScrollBarWidth']

        #Create a  canvas to hold the options to be edited
        self.Canvas = rpDndCanvas(self.Frame,width=WidthCanvas,height=self.HeightForCanvas
            ,scrollregion=(0,0,100,1000),bd=0,highlightthickness=0)
        self.Canvas.bind(HelpButton,self.on_GeneralClick) #this handles help requests
        self.Canvas.HelpTopic = 'Bind-Editor'
        
        #EditList contains one entry per option being displayed. Each entry is a dictionary
        #   of information about that entry:
        #   
        #   'Assist': The assist button widget, or None.
        #   'Y': The Y location on the canvas of the top of this options area.
        #
        #Note that the Assist contains in it 'OurIndex' which is an index
        #   into EditList.
        self.EditList = []
        #We start Ypos at 1 to leave room for the selection rectangle above the top item.
        Ypos = self.HeightSelectionOffset + 2
        OurIndex = 0 
        #If no entry is selected, then select the first one
        if self.SelectionBox['Index'] == None:
            self.SelectionBox['Index'] = 0
        for Decomposition, Event, Handler, Component in Stuff:    
            #    
            #The text of the event string
            #
            if Decomposition and Decomposition[3] == 1:
                #This is a wizard compliant event string; show an abbreviation
                Abbrv = Rpo.EventAbbreviate(Decomposition)
            else:
                #User supplied non-wizard compliant string; show the whole thing
                Abbrv = Event    
            E = LabelPixel(self.Canvas,width=self.WidthEvent,text=Abbrv,anchor=W
                ,pady=0)
            E.HelpTopic = 'Bind-Editor'
            E.bind(HelpButton,self.on_GeneralClick) #for help
            E.bind('<Double-Button-1>',self.on_GotoHandler)
            E.OurIndex = OurIndex
            Id1 = self.Canvas.create_window(5,Ypos,window=E,anchor=NW)
            rpHelp.HintHandler(E, Event)
            #    
            #The text of the handler name
            #
            E = LabelPixel(self.Canvas,width=HandlerPixels,text=' '+Handler,anchor=W
                ,pady=0)
            E.bind(HelpButton,self.on_GeneralClick) #for help
            E.bind('<Double-Button-1>',self.on_GotoHandler)
            E.OurIndex = OurIndex
            E.HelpTopic = 'Bind-Editor'
            Id2 = self.Canvas.create_window(self.WidthEvent,Ypos,window=E,anchor=NW)
            rpHelp.HintHandler(E, Handler)
            #
            #The assist button
            #    
            AssistX = self.WidthEvent+HandlerPixels + 4
            if Event == '' and Handler == '':
                #Create 'New binding button'
                A = Button(self.Canvas,text='Create New Binding',pady=0)
                Hint = 'Click to create a new binding'
                A.OurIndex = OurIndex
                A.bind('<ButtonRelease-1>',self.on_Assist)
                IdA = self.Canvas.create_window(WidthCanvas/2,Ypos+1,window=A,anchor=N)
                A.HelpTopic = 'BindEdit.NewButton'
            else:
                #Create "assist" button
                A = Label(self.Canvas,borderwidth=0,image=Cfg.Info['AssistIcon'],relief=FLAT,takefocus=1)
                A.OurIndex = OurIndex
                A.bind('<Button-1>',self.on_Assist)
                IdA = self.Canvas.create_window(AssistX,Ypos+1,window=A,anchor=NW)
                Hint = 'Click to edit or delete this binding'
                A.HelpTopic = 'BindAssist.Button'
            rpHelp.HintHandler(A,Hint)        
            A.bind(HelpButton,self.on_GeneralClick)
            #
            # The (optional) component designation
            #
            if Component <> '':
                Ypos += int(round(self.HeightEach * 0.7))
                C = LabelPixel(self.Canvas,width=self.WidthEvent+HandlerPixels,text='  -->'+Component,anchor=W
                    ,pady=0)
                C.bind(HelpButton,self.on_GeneralClick) #for help
                C.bind('<Double-Button-1>',self.on_GotoHandler)
                C.OurIndex = OurIndex
                C.HelpTopic = 'Bind-Editor'
                IdC = self.Canvas.create_window(5,Ypos,window=C,anchor=NW)
                rpHelp.HintHandler(C, 'The widget component to which this binding pertains')
            #Build the entry in EditList
            self.EditList.append({'Y':Ypos, 'Assist':A})
            Ypos += self.HeightEach
            OurIndex += 1
        self.Canvas.pack(side=LEFT,expand=NO,fill=BOTH)
        self.DoScrollBar()
        self.Canvas.BabysitScrollregion()
            
#-------------------------------------------------------------------------------                
#
# Option Editor related
#
#-------------------------------------------------------------------------------                

class ResizeBar(Canvas):
    """
    Provide two knobs in a bar for resizing a two column area.
    
    When the user has dragged and dropped a resize knob, we invoke the callback as:
    
    "f(NewLeftWidth, NewRightWidth)"

     o "Widths" is a 2-tuli giving the widths of the left and right areas.
     o "NotifyCallback" is a function which we call when the user has moved and dropped one of the
       resize knobs. The argument provided is a 2-tuli giving the new sizes.
     o "AreaNames" is is 2-tuli giving the name of the left and right area (eg "['label','edit']").
       These are used to create hints for the knobs of the form "Drag to resize %s area".
     o "HelpTopic" is the help topic to invoke if the user help-clicks on us.  
    =p Published methods
    =u Unpublished methods
    """
    
    def __init__(self, Master, Widths,  NotifyCallback):
        """=u
        Create the resize bar
        """
        self.NotifyCallback = NotifyCallback
        self.WidthLabel = Widths[0]
        self.WidthEdit = Widths[1]
        #Total width available to us
        self.WidthTotal = self.WidthLabel + self.WidthEdit
        #Metric on the resize knobs
        self.WidthResizeKnob = Cfg.Info['ResizeIcon'].width()
        self.HeightResizeKnob = Cfg.Info['ResizeIcon'].height()
        Canvas.__init__(self,Master,width=self.WidthTotal,height=self.HeightResizeKnob,bg='#c0c0c0')

        #We draw the label resize knob this much left of our actual boundry
        self.LabelKnobFudge = (self.WidthResizeKnob/2) + 2
        
        self.WidthAssistIcon = Cfg.Info['AssistIcon'].width()
        #This is the smallest we let the edit area get. We allow room for a 20 pixel entry widget,
        #    AssistIcon,  Scroll bar.
        self.WidthMinEdit = 30+self.WidthAssistIcon+Cfg.Info['Metrics']['ScrollBarWidth']
        self.HeightSelectionOffset = 1
         
        #Draw the resize knobs
        T = Label(self,anchor=NW,borderwidth=0,image=Cfg.Info['ResizeIcon'],relief=FLAT)
        self.LeftKnob = T
        self.LeftHint = rpHelp.HintHandler(T,'Drag to resize')
        T.Who = 'LabelKnob'
        self.LabelKnob = self.create_window(self.WidthLabel-self.LabelKnobFudge
            ,0,window=T,anchor=NW)
        T.bind('<Button-1>',self.ResizeDown)
        T.bind('<Motion>',self.ResizeMotion)
        T.bind('<ButtonRelease-1>',self.ResizeRelease)
        T.bind(HelpButton,self.on_ClickHelp)
        #Second knob
        T = Label(self,anchor=NW,borderwidth=0,image=Cfg.Info['ResizeIcon'],relief=FLAT)
        self.RightKnob = T
        self.RightHint = rpHelp.HintHandler(T,'Drag to resize')
        T.Who = 'EditKnob'
        self.EditKnob = self.create_window(self.WidthTotal-self.WidthResizeKnob
            ,0,window=T,anchor=NW)
        T.bind('<Button-1>',self.ResizeDown)
        T.bind('<Motion>',self.ResizeMotion)
        T.bind('<ButtonRelease-1>',self.ResizeRelease)
        T.bind(HelpButton,self.on_ClickHelp)
        #Bind help to resize canvas
        self.bind(HelpButton,self.on_ClickHelp)
        self.ResizeState = 'Idle'
        self.HelpTopic = None
        
    #---------------------------------------------------------------------------
    # Published methods 
    #---------------------------------------------------------------------------
    def NoteWidths(self, NewWidths):
        """=p
        Handle change of width.
        
        Call this routine to note new widths.
        """
        self.WidthLabel = NewWidths[0]
        self.WidthEdit = NewWidths[1]
        self.WidthTotal = self.WidthLabel + self.WidthEdit
        #Place the knobs in their correct positions    
        self.coords(self.LabelKnob,self.WidthLabel-self.LabelKnobFudge,0)
        self.coords(self.EditKnob,self.WidthTotal-self.WidthResizeKnob,0)

    def NoteInfo(self, AreaNames=['',''], HelpTopic=''):
        """
        Set area names and help topic.
        """
        self.HelpTopic = HelpTopic
        self.LeftHint.Text('Drag to resize %s area'%AreaNames[0])
        self.RightHint.Text('Drag to resize %s area'%AreaNames[1])

    #---------------------------------------------------------------------------
    # Unpublished methods from here to end-of-class
    #---------------------------------------------------------------------------
    def ResizeDown(self,Event):
        """=u
        This gets called when the user clicks on a resize knob
        """
        self.ResizeState = Event.widget.Who

    def ResizeMotion(self,Event):
        """=u
        This gets called when the user is dragging a resize knob
        """
        if self.ResizeState == 'Idle':
            return
        NewX = DND.MouseInWidget(self,self,Event)[0]
        if self.ResizeState == 'LabelKnob':
            #print 'NewX=%s WidthTotal=%s'%(NewX,self.WidthTotal-(self.WidthResizeKnob*2))
            NewX = max(NewX,40)
            NewX = min(NewX,self.WidthTotal-(self.WidthResizeKnob*2))
            self.coords(self.LabelKnob,NewX,0)
        if self.ResizeState == 'EditKnob':
            #print 'NewX=%s WidthTotal=%s'%(NewX,self.WidthTotal-(self.WidthResizeKnob*2))
            #don't let user specify a foolishly small edit area
            NewX = max(NewX,self.WidthLabel+self.WidthMinEdit)
            #not do we let the move the knob outside the notepad, although the mouse may
            NewX = min(NewX,self.WidthTotal-self.WidthResizeKnob)
            self.coords(self.EditKnob,NewX,0)

    def ResizeRelease(self,Event):
        """=u
        This gets called when the user drops a resize knob
        """
        if self.ResizeState == 'LabelKnob':
            NewX = DND.MouseInWidget(self,self,Event)[0]
            NewX = max(NewX,40)
            NewX = min(NewX,self.WidthTotal-(self.WidthResizeKnob*2))
            self.WidthLabel = NewX + self.LabelKnobFudge
        if self.ResizeState == 'EditKnob':
            NewX = DND.MouseInWidget(self,self,Event)[0]
            NewX = max(NewX,self.WidthLabel+self.WidthMinEdit)
            self.WidthEdit = NewX + self.LabelKnobFudge - self.WidthLabel
        self.ResizeState = 'Idle'    
        self.WidthTotal = self.WidthLabel + self.WidthEdit
        NewWidths = [self.WidthLabel, self.WidthEdit]
        #Inform our owner of the new widths.
        self.NotifyCallback(NewWidths)

    def on_ClickHelp(self,Event):
        """=u
        User clicked for help:
        """
        if self.HelpTopic:
            Help(self.HelpTopic)
    
class OptionEdit(Frame, BindMixin):
    """=m
    This editor works on either widget options or pack options depending on argument Edit.
    
    {
    "Widreq" : The widreq whose options we are to edit. ;
    "Height" : The maximum amount of screen height we can use. ;
    "Widths" : Widths of left (label) and right (Entry) edit areas ;
    "Edit"   " "'Options'" to edit widget options, or "'Pack'" to edit pack options.
               if omitted, it defaults to "'Options'". ;
    }    
    
    General Variables
    {
    "CurrentWidreq" : The widget request we are editing. ;
    "on_WidthChange" : The width change callback function. ;
    }
    
    Size Variables
    {
    "HeightEach" : The pixels of Y space devoted to each option edit area. ;
    "HeightForCanvas" : The amount of Y space available for our edit canvas.
    "HeightSelectionOffset" : We draw the selection bar starting this many pixels above the nominal Y location
                          of each entry. ;
    "WidthAssistIcon" : The width of our assist icon. ;
    "WidthEdit" : The width, in pixels, of the area for the entry, the assist icon and of the scroll bar,
                  if needed. ;
    "WidthLabel" : The width, in pixels, of the area for showing the option name label. ;
    "WidthMinEdit" : We don't let the user set the edit area smaller than this to prevent a uselessly small edit area. ;
    "WidthTotal" : The total width available for all our editing purposes: label, entry, assist, scrollbar. ;
    "WidthResizeKnob" : The width of our resize knobs. ;
    }

    The selection indication rectangle.
        o To indicate that an option is selected we draw our own selection rectange around it.
        o The initial rectangle is drawn by Generate. After that, the routine ShiftFocusTo moves
           the focus rectangle as requested.
        o We keep information about the selection box in dictionary "self.SelectionBox":
            o "Y": The current Y coordinate of the selection box.
            o "ID": The canvas ID of the selection rectangle.
            o "Index": The index (into self.EditList) of the currently selected option.

    "self.EditList" contains one entry per option being displayed. It is built by "Generate" and
        used by many routines thereafter. Each entry is a dictionary of information about 
        that entry:
       {
       "Entry"  : Whatever edit widget this option needs, often an Entry, sometimes a Label ;
       "Assist" : The assist button widget, or None. ;
       "Y"      : The Y location on the canvas of the top of this options area. ;
       "Name"   : The name of this option. ;
       "EntryCode" : A single letter code indicating the type of edit device:
                    "-" for Label, "e" for Entry. }
    
    *Note:* Each Entry and each Assist in "EditList" contains in it "OurIndex" 
        which is an index into EditList.

    *Note:* We make the assumption that at create time and at Reregister time that
        we are part of the current herd. If this is wrong, code will need fixing.

    The actual OptionEdit canvas is built and populated by routine "Generate". Virtually
        all the rest of the code is concerned with reacting to user clicks and entries.
        
    Note:
    
        Some special handling happens for the "labelpos" and "boolean_c" enumerated option. Both
        of these control if one or more other components are generated. Their extra information is
        a tuple listing the names of the dependent options. If labelpos is None or boolean_c if
        false then the corresponding dependent options will not be created and we set their
        visibility to -1 so they are not presented to the user. If labelpos is not None or boolean_c
        is True then the dependent options will be created and we set their visibility to 0 so
        the user can see them.
        
    #=e Event Handlers
    #=m Miscelaneous
    #=r Repository 
    #=s Selection 
    #=v Validation 
    #=z Size handling
    """


    def __init__(self, Master, Widreq, Height, Widths, Edit='Options'):
        """
        Create the option editor.
        """
        self.Frame = self
        self.CurrentWidreq = Widreq
        self.WidthLabel = Widths[0]
        self.WidthEdit = Widths[1]
        self.Edit = Edit
        self.NeedRefresh = False
        Frame.__init__(self,Master)
        #Register with WidreqRepository
        self.WRID = None
        self.Register(Widreq.Name)
        #We devote this much space to each edit item
        self.HeightEach = Cfg.Info['Metrics']['Entry'][2] + 2
        #Total width available to us
        self.WidthTotal = self.WidthLabel + self.WidthEdit
        #Total height for the main edit canvas
        self.HeightForCanvas = Height
    
        self.WidthAssistIcon = Cfg.Info['AssistIcon'].width()
        #This is the smallest we let the edit area get. We allow room for a 20 pixel entry widget,
        #    AssistIcon,  Scroll bar.
        self.WidthMinEdit = 30+self.WidthAssistIcon+Cfg.Info['Metrics']['ScrollBarWidth']
        self.HeightSelectionOffset = 1
        self.EnumerateRadio = None
    
        #The proto selectionbox
        self.SelectionBox = {'X':None, 'Y': None, 'Index':None}
    
        if Edit == 'Options':
            self.Options = self.CurrentWidreq.Options
        elif Edit == 'Pack':
            self.Options = self.CurrentWidreq.PackOptions
        else:
            raise Exception, "Unknown edit type: "+Edit    

        #Generate initial display
        self.Generate()
        
        #Used to prevent focus looping. See routine "ShiftFocusTo".
        self.FocusDepth = 0
        self.IgnoreFocusInEvent = False

    def Register(self,OurName):
        """=r
        Register (or re-register) with the repository.
        
        This should be called if our name or the herd in which we reside changes.
        """
        RegistryName = '%sEdit for %s on %s'%(self.Edit,OurName, Repo.SelectedHerd)
        if self.WRID == None:
            #We haven't registered yet; do so
            self.WRID = Repo.Register(RegistryName)
            assert self.WRID <> None, 'Initial registration of widget %s failed unexpectedly'%OurName
        else:
            #we are already registered; change our name    
            R = Repo.Rename(self.WRID,RegistryName) 
            assert R == 1, 'Regigester of widget %s failed unexpectedly'%OurName
        #It is important to re-bind if we have chaged herds. Always binding achieves this.
        Repo.Bind(self.WRID, 'WidreqCreateQuery WidreqSelectQuery HerdSelectQuery '
            'WidreqSelectNotify WidreqRenameNotify HerdCreateQuery', self.WidrepCallback)
    
    def Terminate(self):
        if self.WRID <> None:
            Repo.Unregister(self.WRID)
            self.WRID = None
    
    def WidrepCallback(self,Event,A,B):
        """=r
        This is bound to certain WidreqRepository events.
        """
        if Event in ['WidreqCreateQuery', 'WidreqSelectQuery', 'HerdSelectQuery', 'HerdCreateQuery']:
            #If a widreq is being created or selected then our current edit entry had better
            #   be valid or we block the request.
            #Close any possible enumerated assist.
            self.on_EnumerateRadioFinish()
            if Event == 'WidreqCreateQuery':
                Arg = 'create a new widget instance'
            elif Event == 'WidreqSelectQuery':
                Arg = 'select a different widget'
            elif Event == 'HerdSelectQuery':
                Arg = 'select a different form'
            elif Event == 'HerdCreateQuery':
                Arg = 'add a new form to the project'    
            else:
                raise Exception, 'Unhandled repository event: '+Event   
            Temp = Repo.RequestDescriptionFetch()
            if Temp:
                #A specified request description trumps a generic event-based description'
                Arg = Temp    
            if self.StatusCheck(HelpTopic=('OptionEdit.InvalidValue',[Arg])):
                #our current edit is fine; give our OK
                Result = 1
            else:
                #current edit is invalid; nix nix
                Result = ("Current widreq contains an invalid edit area", 1)
            return Result
        if Event == "WidreqSelectNotify":
            if A == self.CurrentWidreq.Name:
                #we are the widreq which was just selected, in which case we start caring about
                #requests to create or select a different widrea
                Repo.Bind(self.WRID, 'WidreqCreateQuery WidreqSelectQuery', self.WidrepCallback)
            else:
                #Since we are no longer selected there is no point in watching these requests
                Repo.Unbind(self.WRID, 'WidreqCreateQuery WidreqSelectQuery')
            return
        if Event == 'WidreqRenameNotify':
            #D('WidrewCallback A=%s B=%s Event=%s CurrentWidreq.Name=%s Edit=%s'%(A,B,Event,self.CurrentWidreq.Name,self.Edit))
            if B == self.CurrentWidreq.Name:
                #We are we widreq being renamed. At this point we have already been renamed, 
                #    but we must update the content of the name Entry.
                for I in range(len(self.EditList)):
                    #Scan EditList looking for the 'name' option.
                    if self.EditList[I]['Name'] == 'name':
                        #update the text of the name Entry
                        try:
                            E = self.EditList[I]['Entry']            
                            E.delete(0,END)
                            E.insert(0,B)
                        except AttributeError:
                            #The main form of the main module doesn't have an edit
                            pass    
                if self.Edit == 'Options':
                    #Were the option editor; give user a chance to rename handlers.
                    self.RenameVisHandlers(A,B)        
            return    
        print '%sEdit got unexpected Widrep event "%s"'%(self.Edit,Event)

    def RenameVisHandlers(self,A,B):
        """
        We just got renamed. Look after renaming of event handlers.
        """
        #D('RVH: A=%s B=%s home=%s target=%s'%(A,B,self.CurrentWidreq.PresentHome,self.CurrentWidreq.TargetHerd))
        if self.CurrentWidreq.PresentHome == GblParkingLotName or \
            self.CurrentWidreq.TargetHerd == GblParkingLotName:
            #Either were on the parking lot or were in the process of being moved to the
            #    parking lot. In either case we simply rename any handler references that 
            #    are of the standard form and mention our name. We get away with this because
            #    while we are on the parking lot the handler names are not actually bindings,
            #    simply names of handlers for future bindings.
            #Look after renaming handler names in bind entries.
            HandlerList = self.CurrentWidreq.HandlersList()
            for HandlerName in HandlerList:
                Temp = DecomposeHandlerName(HandlerName,A)
                if Temp:
                    #Name is standard form and refers to our previous name
                    New = 'on_%s_%s'%(B,Temp)
                    self.CurrentWidreq.HandlerRenameNotify(HandlerName,New)
            #Have the widgetator update the editor if needed                    
            GblLayout.TheWidgetator.EditorRefresh()                
            return        
            
        TextEditor = GblLayout.TextEditFetch().TextWidget
        #--- Get a list of all handers of the form "on_thiswidget_"
        HL = TextEditor.HandlerNameList()
        #Each entry in HandlerList is a list of:
            # The new handler name
            # The old handler name
        HandlerList = []
        for OldHandlerName in HL:
            Event = DecomposeHandlerName(OldHandlerName,A)
            if Event:
                #Handler name is of the form 'on_ourwidget_whatever'
                HandlerList.append(['on_%s_%s'%(B,Event),OldHandlerName])
        if len(HandlerList) == 0:
            #No handlers to rename
            return
        #---Check if potentially renamed handlers would conflict with existing handlers---
        ConflictList = []
        #Each entry in ConflictList is [NewName,OldName] where there is *already* a handler
        #    of NewName.
        for NewName,OldName in HandlerList:
            if NewName in HL:
                ConflictList.append([NewName,OldName])
        Count = len(HandlerList)
        ConflictCount = len(ConflictList)
        OldList = '\n'.join(['t {g%s}'%X[1] for X in HandlerList])
        NewList = '\n'.join(['t {g%s}'%X[0] for X in HandlerList])
        if ConflictCount == 0:        
            #---No conflicts - Ask user if they want to rename the handlers---    
            Count = len(HandlerList)
            M = 'You just renamed the current widget from "$s" to "$s". The current form ' \
                'has %s event handler{/s} with {a name/names} like "on_$s_whatever". Do ' \
                'you want me to revise {the/those} handler name{/s} to be "on_$s_whatever"?'
            M = rpHelp.Plural(M,Count,ToPercent='$')
            M = M%(A,B,A,B)
            HelpTuple = ('widget.rename.handlers',(A,B,OldList,len(HandlerList),NewList))
            R = Rpw.MessageDialog(Title='Query',Message=M
                ,Buttons=(('Yes',1),('~No',None)),Help=HelpTuple).Result
            if R == None:
                #User bailed
                return
            assert R == 1
        else:
            #---There are conflicts ---
            if Count <> ConflictCount:
                ConList = '\n'.join(['t {g%s}'%X[0] for X in ConflictList])
                #At least one of the names would not conflict.
                M = ('You just renamed the current widget from "$s" to "$s". The current form ' 
                    'has %s event handler{/s} with {a name/names} like "on_$s_whatever". ' 
                    '\n\nAt this point I would usually ask if you want to rename {that/those} handler{/s} to '
                    'be named like "on_$s_whatever" BUT')
                M = rpHelp.Plural(M,Count,ToPercent='$')
                M = M%(A,B,A,B)
                M += (' I also notice that if I did the rename then the name of %s of the renamed handler{s} '
                    'would conflict with the name{/s} of {an/} already existing handler{/s}. Click Help to '
                    'see details of the name conflict. Click "Yes" to rename all but the conflicting handler{/s}. '
                    'Click "No" to rename none of the handlers.')
                HelpTuple = ('widget.rename.handlers.conflict',(A,B,OldList,Count,NewList
                    ,ConflictCount,ConList))
                M = rpHelp.Plural(M,ConflictCount,ToPercent='$')    
                R = Rpw.MessageDialog(Title='Query',Message=M
                    ,Buttons=(('Yes',1),('~No',None)),Help=HelpTuple).Result
                if R == None:
                    return
                assert R == 1
            else:
                #All of the names conflict
                M = ('You just renamed the current widget from "$s" to "$s". The current form ' 
                    'has %s event handler{/s} with {a name/names} like "on_$s_whatever". ' 
                    '\n\nAt this point I would usually ask if you want to rename {that/those} handler{/s} to '
                    'be named like "on_$s_whatever" BUT I also notice that if I did the rename then '
                    '{/all} the changed name{/s} would conflict with the name of {an/} already existing '
                    'handler{/s}, thus there is no point in even thinking about renaming.')
                M = rpHelp.Plural(M,Count,ToPercent='$')
                M = M%(A,B,A,B)
                HelpTuple = ('widget.rename.handlers.allconflict',(A,B,OldList,Count,NewList))
                Rpw.MessageDialog(Title='Information',Message=M,Help=HelpTuple)
                return
        #---User said yes---
        for Temp in HandlerList:
            if not (Temp in ConflictList):
                NewName,OldName = Temp
                self.HandlerRename(OldName,NewName)
        return
        
    def NoteNewHeight(self,NewHeight):
        """=z
        Call this to notify the OptionEdit frame that the available Y space has changed.    
        """
        self.HeightForCanvas = NewHeight
        if self.HeightRequired > self.HeightForCanvas:
            #we need a scroll bar
            if not hasattr(self,'ScrollY'):
                #but we don't have one; regenerate
                self.Generate()
        else:
            #we don't need a scroll bar
            if hasattr(self,'ScrollY'):
                #but we have one; regenerate
                self.Generate()        

    def ReportWidths(self):
        """
        Return a 2-list giving widths of Label and Edit areas as presently drawn.
        """
        return [self.WidthLabel,self.WidthEdit]    

    def NotifyExternalChange(self):
        """
        Called if an external agent changes some data.
        
        We should refresh our display the next time we are the active editor.
        
        This is needed in cases where editor information is changed by someone
            outthe editor (eg change of event handler name in option command)
        """
        self.NeedRefresh = True
        
    def EditorRefresh(self):
        """
        Refresh our display if needed.
        """
        if self.NeedRefresh:
            if self.Edit == 'Options':
                self.Options = self.CurrentWidreq.Options
            elif Edit == 'Pack':
                self.Options = self.CurrentWidreq.PackOptions
            else:
                raise Exception, "Unknown edit type: "+Edit    
            self.Generate()
            
    def WhoIsSelected(self):
        """=s
        Return the name of the currently selected option.
        """
        if self.Edit == 'Pack' and self.CurrentWidreq.FrameID == (0,):
            #No actual pack editor in case of root frame
            return ''
        return self.EditList[self.SelectionBox['Index']]['Name']

    def SelectByName(self,Name):
        """=s
        Attempt to select the option of the given name.
        
        If there is no option of the given name we take no action.
        """
        if Name:
            #Do only real names
            for I in range(len(self.EditList)):
                #Scan EditList looking for an option of that name
                if self.EditList[I]['Name'] == Name:
                    #shift focus to the matching option
                    self.ShiftFocusTo(I,Who='SelectByName')
                    return

    def StatusCheck(self,HelpTopic=None):
        """=s
        Check the validity of the current option.
        
        If it is valid we return true. If it is invalid we put up a modal error 
            dialog. Once the dialog closes we return false.
            
        "HelpTopic" If specified and the current option is not valid, then the modal dialog will
            include a "Help" button and pressing it will invoke the help topic. 
            
        Note that "HelpTopic" can be either:
            o A simple string giving the help topic name, or
            o A tuli giving the help topic name followed by a *list* of string arguments to be
              passed to the help facility if needed.    
        """
        class Oops(Exception): pass
        if self.Edit == 'Pack' and self.CurrentWidreq.FrameID == (0,):
            #No actual pack editor in case of root frame
            return 1
        Index = self.SelectionBox['Index']
        ThisOption = self.EditList[Index]
        OptionName = ThisOption['Name']
        WidgetName = self.CurrentWidreq.WidgetName
        WidreqInstanceName = self.CurrentWidreq.Name
        Record = self.Options[OptionName]
        OptionType, DefaultValue, PresentValue, ExtraInfo = Record
        if HelpTopic and type(HelpTopic) <> type(''):
            #They are including an argument list
            HelpTopic[1].extend([OptionName, WidreqInstanceName])
        #If this option has an entry field, get it's content
        if ThisOption['EntryCode'] ==  'e':
            #Get value from Entry widget
            NewValue = ThisOption['Entry'].get()
            if NewValue == '' and OptionType<>'Name':
                #Empty in an edit is a request for the default value except for the Name option
                #    which has no default.
                NewValue = DefaultValue
                #Display the default value in the entry now. This is necessary in the case where the
                #    option was already at the default value and then the user makes the entry empty.
                #    Since no actual change has taken place to the value (it was and is default) we
                #    check below and do nothing furter. But if we *don't* display the value now then
                #    the entry is left blank which is misleading.
                ThisOption['Entry'].delete(0,END)
                if NewValue <> None:
                    ThisOption['Entry'].insert(0,NewValue)
        elif ThisOption['EntryCode'] == '-':
            #Labels provide no new value        
            NewValue = PresentValue
        else:
            raise Oops, 'Unknown EntryCode "%s"'%ThisOption['EntryCode']    
        Error = 'Error'
        ##D('NewValue=%s PresentValue=%s'%(`NewValue`,`PresentValue`))
        if (NewValue == '' and PresentValue == None)  \
        or Intify(NewValue) == Intify(PresentValue)   \
        or OptionType == 'pmwcomp':
            #No change was made; by definition things are OK and no action is required
            return 1
        ##D('NewValue=%s PresentValue=%s'%(`NewValue`,`PresentValue`))
        try:    
            if OptionType in Cfg.Info['EnumeratedOptions'].keys():
                #
                #--- Enumerated ---
                #
                #print 'OptionType=%s DefaultValue=%s PresentValue=%s'%(OptionType, DefaultValue,PresentValue)
                #print 'List=%s'%Cfg.Info['EnumeratedOptions'][OptionType]
                return 1
                if NewValue and not NewValue in Cfg.Info['EnumeratedOptions'][OptionType].keys():
                    Exception, Error, '"%s" is not a valid choice for %s. Valid choices are: %s.' \
                        %(NewValue,OptionName,Cfg.Info['EnumeratedOptions'][OptionType])
            #            
            #NOTE: If we need to special case any option which IS in BuiltinOptions, then 
            #      do so before getting to here.
            #
            elif Cfg.Info['BuiltinOptions'].has_key(OptionType):            
                #
                # --- standard options ----
                #
                #R = Rpo.bbox_Validate(NewValue,OptionName)
                R = Cfg.Info['BuiltinOptions'][OptionType]['Validate'](NewValue,OptionName)
                if R[0] <> 1:
                    print 'bbox R=%s'%str(R)
                    raise Oops,R[0]
                else:
                    if NewValue <> None:
                        NewValue = BlankToNone(str(R[1]))
            elif OptionType == 'name':
                #
                #--- name ---
                #
                #run the proposed name change past the widreq repository
                if self.CurrentWidreq.IsForm():
                    #This widreq is the container of a form. The user is thus changing
                    #    the name of a form in the project as well as the name of a widreq.
                    if NewValue in Repo.ListHerds():
                        raise Oops,'There is already a form named "%s".'%NewValue
                    if NewValue in Repo.ListWidreqs():
                        raise Oops,'There is already a widget named "%s" on this form.'%NewValue
                    #Change the name of the widreq    
                    R = Repo.Request(self.WRID,'WidreqRename',PresentValue,NewValue)
                    assert R == 1, 'WidreqRename failed unexpectedly'
                    self.Register(NewValue)
                    #Change the name of the herd
                    R = Repo.Request(self.WRID,'HerdRename',PresentValue,NewValue)
                    if R <> 1:
                        raise Oops,'HerdRename failed unexpectedly: '+R
                    self.Register(NewValue)
                else:
                    #This widreq is not the container of a form. The user is changing
                    #    the name of a widreq within a form.
                    R = Repo.Request(self.WRID,'WidreqRename',PresentValue,NewValue)
                    if R <> 1:
                        #the name change didn't fly
                        raise Oops, R[0]
                    else:
                        #The name change did fly; we must revise our own name
                        self.Register(NewValue)
            else:
                raise Exception,'Unknown option type "%".'%OptionType
            #Make the new value the current value
            Record = self.Options[OptionName]
            self.Options.SetCurrent(OptionName,NewValue)
            #And put it in our edit widget
            EntryCode = self.EditList[Index]['EntryCode']
            EntryWidget = self.EditList[Index]['Entry']
            if EntryCode == 'e':
                #our edit widget is an entry
                EntryWidget.delete(0,END)
                if NewValue <> None:
                    EntryWidget.insert(0,NewValue)
            elif EntryCode == '-':
                #our 'edit' widget is a label    
                if NewValue <> None:
                    EntryWidget['text'] = NewValue
                else:
                    EntryWidget['text'] = ''    
            else:
                raise Exception, 'Unknown EntryCode "%s".'%EntryCode    
            #Update creation text
            GblLayout.CreationSystextRegen('OptionEditor - StatusCheck')    
            #signal all OK
            return 1
                          
        except Oops, Message:
            #whine to the user
            if 1 == Rpw.ErrorDialog(Message,Help=HelpTopic<>None).Result:
                #User clicked on help
                Help(HelpTopic)
            #and signal not OK
            return 0                        

    #---------------------------------------------------------------------------
    # Private methods from here to end of class
    #---------------------------------------------------------------------------
        
    def ComputeHeights(self):
        """=z
        Compute the height required to accomodate all items we need to edit.
        """
        Stuff = self.Options.Visible()
        self.HeightRequired = self.HeightEach * len(Stuff)
    
    def DoScrollBar(self):
        """=m
        Install/Deinstall Y scroll bar as needed.
        """
        self.ComputeHeights()
        if self.HeightRequired > self.HeightForCanvas:
            #We need a scroll bar
            if not hasattr(self,'ScrollY'):
                self.ScrollY = Scrollbar(self.Frame,orient=VERTICAL
                    ,command=self.Canvas.yview)
                self.ScrollY.pack(side=RIGHT,fill=Y)    
                self.Canvas['yscrollcommand'] = self.ScrollY.set
        else:
            #We don't need a scroll bar
            if hasattr(self,'ScrollY'):
                #get rid of the existing scroll bar
                self.Canvas['yscrollcommand'] = None
                self.ScrollY.pack_forget()
                del self.ScrollY

    def on_FocusIn(self,Event):
        """=e
        This is called when an entry or assist gets the focus.
        Our response is to shift the focus rectangle.
        """
        if self.IgnoreFocusInEvent:
            return
        I = Event.widget.OurIndex
        self.ShiftFocusTo(I,Who='on_FocusIn',Focus=False)
        time.sleep(0.1)

    def on_UpKey(self,Event):
        """=e
        User pressed cursor up key.
        """
        self.ShiftFocusTo(self.SelectionBox['Index'] - 1,Who='on_UpKey')

    def on_DownKey(self,Event):
        """=e
        User pressed cursor down key.
        """
        self.ShiftFocusTo(self.SelectionBox['Index'] + 1,Who='on_DownKey')
        
    def ShiftFocusTo(self,Index,Focus=True,Who=''):
        """=s
        Call this routine to shift the focus rectangle to the option of the
            specified index.
        """      
        ##D('---------------------ShiftFocusTo:Index=%s Who=%s Depth=%s'%(Index,Who,self.FocusDepth))
        if self.FocusDepth > 0:
            #This check explicitly nullifies a call to this routine if this routine is
            #    already active. There are (rare) cases where this can happen and if you
            #    let it happen the resuts aren't good.
            return
        self.FocusDepth += 1
        if self.EnumerateRadio <> None and Index <> self.EnumerateRadio.OurIndex:
            #There is an enumeration box hanging around; get rid of it
            self.EnumerateRadio.place_forget()
            self.EnumerateRadio = None
        if Index < 0 or Index >= len(self.Options.Visible()):
            #Do nothing if index is out of range
            self.FocusDepth -= 1
            return
        if Index <> self.SelectionBox['Index'] \
        and not self.StatusCheck(HelpTopic=('OptionEdit.InvalidValue',['select a different option'])):
            #If we are attempting to select an option other than the currently selected one
            #    AND the selected option is not valid it must remain selected.
            #Tricky. At this point Tkinter has already set the focus on another entry but we want
            #    it to stay on the invalid entry. By setting Focus we will shortly set the focus
            #    where we want it. But if we didn't set IgnoreFocusInEvent (which the on_FocusIn
            #    event handler pays attention to) then that would provoke another event which would
            #    attempt to focus on the other entry which would provoke another StatusCheck which
            #    in turn creates a loop.
            Index = self.SelectionBox['Index']
            Focus = True
            self.IgnoreFocusInEvent = True
        if Index <> self.SelectionBox['Index']:
            #The requested option is not already selected; move the selection bar
            Info = self.EditList[Index]    
            Ymove = (Info['Y']-self.HeightSelectionOffset) - self.SelectionBox['Y']
            self.Canvas.move(self.SelectionBox['Id'],0,Ymove)
            self.SelectionBox['Y'] += Ymove
            self.SelectionBox['Index'] = Index
            #Insure selected item is visible on the canvas
            FirstVisible = self.Canvas.canvasy(0)
            LastVisible = self.Canvas.canvasy(self.HeightForCanvas)
            #Get top and bottom Y location of selected entry
            Top = Info['Y'] 
            Bottom = Top + self.HeightEach+2
            if Top < FirstVisible or Bottom > LastVisible:
                ##D('Top=%s FirstVisible=%s Bottom=%s LastVisible=%s'%(Top,FirstVisible,Bottom,LastVisible))
                ##D('self.Canvas.winfo_geometry()=%s'%str(self.Canvas.winfo_geometry()))
                #Agg! Part of selected entry is not visible.
                Middle = (Top + Bottom) / 2
                #Attempt to position the selected entry in the middle of the viewport
                Target = (float(Middle) - float(self.HeightForCanvas/2)) / float(self.HeightRequired)
                #print 'Must scroll. Middle=%s HtReq=%s Target=%s'%(Target,Middle,self.HeightRequired)
                self.Canvas.yview_moveto(Target)
        #Now set the focus
        if Focus:
            ##D('ShiftFocusTo: About to set focus. Index=%s'%Index)
            if self.EditList[Index]['Entry'] <> None:
                #Our first choice is the edit entry
                self.EditList[Index]['Entry'].focus_set()
            else:    
                #but we will focus on the assist if need be
                if self.EditList[Index]['Assist'] <> None:
                    self.EditList[Index]['Assist'].focus_set()
        self.FocusDepth -= 1
        self.IgnoreFocusInEvent = False

    def on_DoubleClick(self,Event):
        """
        Handle double click = request to goto command option code
        
        Since there is apparently no obvious way to tell from an Event object if it
            was in response to a double click, we have our own routine and we 
            pass doubleclick as an argument.
        """
        self.on_GeneralClick(Event,DoubleClick=True)

    def on_GeneralClick(self,Event=None,DoubleClick=None):
        """=e
        Shift focus or serve help in response to user clicking mouse.
        
        There are three slightly different cases that we process, although all are 
            instances of the user clicking the mouse and us wanting to position the
            selection bar appropriately or serve help. The cases are:
        
         o The user clicked over a portion of our canvas which is unused or is 
            devoted to an option-name label. In this case we get an event, and
            "Event.widget" is our canvas. Note that a label in the edit area 
            (used for those cases where the only user-edit capability is 
            provided by the assist button) is different since (in order for 
            cursor up/down to work) it has to take the focus. 
            
         o The user clicked on a label in the edit area. In this case we also get
            an event but "Event.widget" is the label itself.
            
         o The user clicked on an OptionEdit. In this case we don't get an event.    
        
        In the first case "Event.y" gives us the position of the cursor in in the
            canvas directly. In the latter two cases we have to figure out the
            cursor position from basic principles.
        
        *Note:* Help clicking over an option both selects that option AND serves up
            help. Initially I was just going to serve help and leave the selection
            alone. However, clicking ANY mouse button over an entry seemed to cause
            that option to be selected, and I didn't really mind the effect. To 
            make it consistent, we select and help when you HelpClick over ANY
            portion of an option.    
        """
        self.EnumerateRadioToast()
        if hasattr(Event,'widget')  and Event.widget == self.Canvas:
            #This is the easy case; we get the Y cursor position for free
            CanvasY = self.Canvas.canvasy(Event.y)
        else:        
            #The harder case; we have to go rooting around for the cursor position
            CanvasY = self.Canvas.canvasy(Rpw.MouseInWidget(self.Canvas)[1])
        #Run through all our options looking for the one we are over    
        for I in range(len(self.EditList)):
            OptionY = self.EditList[I]['Y']
            if CanvasY >= OptionY and CanvasY <= (OptionY + self.HeightEach):
                #mouse was over this option
                if DoubleClick:
                    if Event.num == 1:
                        #They double-1 clicked
                        OptionName = self.EditList[I]['Name']
                        OptionType, DefaultValue, PresentValue, ExtraInfo = self.Options[OptionName]
                        if OptionType == 'command' and PresentValue:
                            GblLayout.HandlerGoto(PresentValue)        
                    else:
                        #We ignore all other double-clicks
                        pass
                    return        
                if Event.num in (1,2):
                    #user left or middle clicked; select the specified option
                    self.ShiftFocusTo(I,Who='on_GeneralClick')
                    self.Canvas.update_idletasks() #make the selection visible NOW
                if Event.num == 2:
                    #user middle clicked; serve help
                    if self.Edit == 'Options':
                        #Were an option editor.
                        #For compound Pmw names, use only the right portion
                        WidgetName = '%s.%s'%(self.CurrentWidreq.ModuleName,self.CurrentWidreq.WidgetName)
                        OptionName = self.EditList[I]['Name']
                        ##D('WidgetName=%s, OptionName=%s'%(WidgetName,OptionName))
                        if '.' in OptionName:
                            #It's a compound Pmw option name eg "hull.Frame".
                            Temp = OptionName.split('.')
                            #Note: it is possible to get option names like a.b.c; in this case we want to get
                            #    a.b as the parent option and c as the option name. Since I know of no way to
                            #    tell Python to split from the right we jump around a bit.
                            ParentOption = '.'.join(Temp[:-1]) #eg hull
                            OptionName = Temp[-1] #eg Frame
                            #Get the module.widget of what we are from the parent
                            WidgetName = self.CurrentWidreq.Options[ParentOption][2]
                            Topic = 'wid.%s.opt.%s'%(WidgetName,OptionName)
                        elif OptionName == 'name' and self.CurrentWidreq.IsMainForm():
                            #The 'name' option of the main form of the main module is special and it gets
                            #    it's own special help
                            Topic = 'wid.mainform.name'
                        elif OptionName == 'name' and self.CurrentWidreq.FrameID == (0,):
                            #This is the 'name' option of a highest-level widget    
                            Topic = 'wid.%s.opt.nametop'%WidgetName
                        else:        
                            Topic = 'wid.%s.opt.%s'%(WidgetName,OptionName)
                    else:
                        #Were a pack editor
                        Topic = 'pack.option.%s'%self.EditList[I]['Name']        
                    Help(Topic)
                return

    def on_EnumerateRadioFinish(self,Dummy=None):
        """=v
        Accept users selection of an enumerated type.
        
        Note: There looks to be no way to select an item in a RadioSelect without
            also firing off the command. The act of setting the initial value (in
            Assist_Enumerated) causes us to be invoked, which isn't really what we
            want. However, at that point RadioEnumerated is still None, so we 
            first test for that and if so we exit immediatly.
        """
        if self.EnumerateRadio == None:
            return
        #This lets the user see the selection (briefly) before the RadioSelect closes.    
        self.Canvas.update_idletasks()    
        time.sleep(0.25)    
        #Fetch the users selection    
        DisplayValue = self.EnumerateRadio.getcurselection()
        #Convert display value (eg 'False') to it's storage form (eg 0)
        StorageValue = Cfg.Info['EnumeratedOptions'][self.EnumerateRadio.OptionType][DisplayValue]
        Index = self.EnumerateRadio.OurIndex
        OptionName = self.EditList[Index]['Name']
        OptionType, DefaultValue, PresentValue, ExtraInfo = self.Options[OptionName]
        #And stuff it into the 'PresentValue' slot in this option of the widreq
        self.Options.SetCurrent(OptionName,StorageValue)
        #Also update the label that displays the present value
        self.EditList[Index]['Entry']['text'] = DisplayValue
        #Make the RadioSelect go away    
        self.EnumerateRadioToast()
        #Assume we won't have to regnerate the option editor display
        RegenRequired = False
        ##D('ExtraInfo=%s'%ExtraInfo)
        if OptionType in ('labelpos','boolean_c') and ExtraInfo <> None:
            #This option controls the accessability of one or more related nested options
            CurrentSelection = self.WhoIsSelected()
            for Extra in ExtraInfo:
                TargetOptionType, TargetDefaultValue, TargetPresentValue, TargetExtraInfo = self.Options[Extra]
                if StorageValue in (None,0):
                    #Our target nested option should be inaccessable
                    if TargetExtraInfo <> -1:
                        #But it's not
                        self.Options.SetVis(Extra,-1)
                        RegenRequired = True
                else:
                    #Our target nested option should be accessable
                    if TargetExtraInfo == -1:
                        #But it's not
                        self.Options.SetVis(Extra,0)
                        RegenRequired = True        
        #Update creation text
        GblLayout.CreationSystextRegen('OptionEditor - EnumeratedRadioFinish')
        if RegenRequired:
            #If we are regenerating this means we have opened or closed an option in
            self.Generate(CurrentSelection)
                
    def Assist_Enumerated(self,Index):
        """=v
        Handle assist for an enumerated option
        """
        OptionName = self.EditList[Index]['Name']
        OptionType, DefaultValue, PresentValue, ExtraInfo = self.Options[OptionName]
        ChoiceList = Cfg.Info['EnumeratedOptions'][OptionType].keys()
        Title = '  %s  '%rpHelp.Cap(OptionName)
        R = Rpw.RadioSelect(self.Canvas.winfo_toplevel(),buttontype='radiobutton'
            ,labelpos=N,label_text=Title,command=self.on_EnumerateRadioFinish)
        R.config(borderwidth=2,relief=RAISED)
        R.label().config(background="#c0c0c0")
        ChoiceList.sort()    
        #Convert present value (eg 0) into a display value (eg 'False')
        PresentDisplayValue = ReverseDictLookup(Cfg.Info['EnumeratedOptions'][OptionType],PresentValue)
        DefaultDisplayValue = ReverseDictLookup(Cfg.Info['EnumeratedOptions'][OptionType],DefaultValue)
        for Choice in ChoiceList:    
            T = Choice
            if T == DefaultDisplayValue:
                T += ' *'
            R.add(Choice,text=T)
            if Choice == PresentDisplayValue:
                R.invoke(Choice)
        Xpos, Ypos, TopW, TopH, TopX, TopY = rpHelp.MouseInTop(self.Canvas)
        self.Canvas.update_idletasks() #needed to set height of R
        MenuHeight = R.winfo_reqheight()
        #Adjust so we display a bit left and up of the mouse
        Xpos -= 25
        Ypos -= 50
        if (MenuHeight + Ypos) > TopH:
            #The menu is going to fall off the bottom of the top level window
            #Shift the menu up, but not off the top of the top level window
            Ypos = max(TopH - MenuHeight, 0)
        R.place(x=Xpos, y=Ypos)
        R.OurIndex = Index
        R.OptionType = OptionType
        self.EnumerateRadio = R

    def on_Assist(self,Event):
        """=e
        This routine is called when the user clicks on an assist.
        
        If the current option is a built-in type then we invoke it's assist dialog and
            if the user didn't cancel we install the new value.    

        If the current option is an enumerated type then we invoke "Assist_Enumerated"
            which pops up a RadioSelect. We can't hang around here waiting for
            the user (RadioSelects aren't modal). The end of this process is looked
            after by "on_EnumerateRadioFinish". Note that if the user opens a RadioSelect
            and they wander off doing something else, we still have the RadioSelect
            hanging around. The routine "EnumerateRadioToast" gets rid of any pending
            RadioSelect and is called when we click within the OptionEdit or when we
            redraw the OptionEdit.
        """
        I = Event.widget.OurIndex
        if self.SelectionBox['Index'] <> I:
            #The assist clicked is not the assist of the currently selected option
            if not self.StatusCheck(HelpTopic=('OptionEdit.InvalidValue',['invoke an assist'])):
                #if the currently selected option value is invalid, belay this assist request
                return
        self.ShiftFocusTo(I,Who='on_Assist')
        OptionType = Event.widget.OptionType
        ##D('on_Assist: OptionType=%s, I=%s, EditList[I]=%s'%(OptionType,I,self.EditList[I]))
        OptionName = self.EditList[I]['Name']
        EntryCode = self.EditList[I]['EntryCode']
        EntryWidget = self.EditList[I]['Entry']
        #Extract useful info from the Widreq about this option
        OptionType, DefaultValue, PresentValue, ExtraInfo = self.Options[OptionName]
        #Exclude command options if on parking lot        
        if OptionType == 'command' and self.CurrentWidreq.PresentHome == 'the Parking Lot':
            M = "You can't alter a widget's command options while it is on the parking lot"
            Rpw.MessageDialog(Message=M,Help='command.option.on.parkinglot')
            return
        #The assists operate on strings, so we convert None to '' on their behalf
        if PresentValue == None:
            PresentValue = ''
        if EntryCode == 'e':
            #Edit widget is Entry; get present value from  it
            PresentValue = EntryWidget.get()
        if OptionType in Cfg.Info['EnumeratedOptions'].keys():
            #It's an enumerated type
            self.Assist_Enumerated(I)
            return
        if OptionType == 'cvar':
            #
            # cvar
            #
            # Cvars are special because we have to keep auto/manual creation and
            #     possible the type to create.
            WidreqName = self.CurrentWidreq.Name
            Result = Rpo.cvar_Assist(PresentValue,OptionName,ExtraInfo,WidreqName).Result
            if Result == None:
                #The user didn't do anything.
                return
            DisplayValue = NewValue = BlankToNone(Result[0])
            ExtraInfo = Result[1]
            if NewValue <> None:
                #punch up the display value to included auto/man and type info.
                DisplayValue = Rpo.cvar_Format(NewValue,ExtraInfo)
        elif OptionType == 'command':
            #
            # command
            #
            # the "command" option is special because it is really a binding in
            #     options clothing; it needs all the bind functionality.        
            TextEditor = GblLayout.TextEditFetch().TextWidget
            WidreqName = self.CurrentWidreq.Name
            ListOfHandlers = TextEditor.HandlerNameList()
            R = Rpo.command_Assist(PresentValue,ExtraInfo,OptionName,ListOfHandlers,WidreqName).Result
            if R == None:
                #The user didn't do anything.
                return
            #Look after possible handler name change or delete with user input as needed
            HandlerName, CreateHandlerFlag = R
            if CreateHandlerFlag:
                #This is a rapyd maintained handler
                Temp = self.HandlerChangeProcess(PresentValue,HandlerName,'command')
            else:
                #This handler is user-maintained. Set temp like HandlerChangeProcessor would.
                if HandlerName == '*DELETE*':
                    Temp = 0
                else:
                    Temp = 1        
            ExtraInfo = CreateHandlerFlag    
            if Temp == None:
                #User cancelled
                return
            elif Temp == 0:
                #The command-option was cleared as requested
                DisplayValue = NewValue = None
            elif Temp == 1:
                #The new command-option value was accepted        
                DisplayValue = NewValue = HandlerName
            else:
                raise Exception, "Unexpected value = %s"%str(Temp)    
        elif OptionType == 'pmwdatatype':
            #
            # pmwdatatype
            #
            # pmwdatatype is special because we maintain extra information.
            WidreqName = self.CurrentWidreq.Name
            Result = Rpo.pmwdatatype_Assist(PresentValue,OptionName,ExtraInfo).Result
            if Result == None:
                #The user didn't do anything.
                return
            DisplayValue = NewValue = Result[0]
            ExtraInfo = Result[1]
        #
        #
        # Any option types which require special processing should be handled above
        #    
        #        
        elif Cfg.Info['BuiltinOptions'].has_key(OptionType):
            #
            # most option types are handled here by common code
            #
            #D('PresentValue=%s'%repr(PresentValue))
            NewValue = Cfg.Info['BuiltinOptions'][OptionType]['Assist'] \
                (ValueToEdit=PresentValue,OptionName=OptionName).Result
            if NewValue == None:
                #The user didn't do anything.
                return
            if OptionType == 'font':
                DisplayValue = NewValue = Rpw.FontToString(NewValue)
            else:    
                DisplayValue = NewValue = BlankToNone(NewValue)
        else:
            raise Exception,'Unknown option type: '+OptionType
        #Place the new value in the widreq
        self.Options.SetCurrent(OptionName,NewValue)
        self.Options.SetExtra(OptionName,ExtraInfo)
        
        #And put it in our edit widget
        if EntryCode == 'e':
            #our edit widget is an entry
            EntryWidget.delete(0,END)
            if DisplayValue <> None:
                EntryWidget.insert(0,DisplayValue)
        elif EntryCode == '-':
            #our 'edit' widget is a label    
            if DisplayValue <> None:
                EntryWidget['text'] = DisplayValue
            else:
                EntryWidget['text'] = ''    
        else:
            raise Exception, 'Unknown EntryCode "%s".'%EntryCode    
        #Update creation text
        GblLayout.CreationSystextRegen('OptionEditor - EnumeratedRadioFinish')    

    def EnumerateRadioToast(self):
        """=s
        If there is an enumerated type RadioSelect about, get rid of it.
        """
        if self.EnumerateRadio <> None:
            #There is one; toast it
            self.EnumerateRadio.place_forget()
            self.EnumerateRadio = None

    def on_OpenClose(self,Event):
        """
        User clicked on a nested option open-close icon
        """
        I = Event.widget.OurIndex
        OptionType = Event.widget.OptionType
        OptionName = self.EditList[I]['Name']
        EntryCode = self.EditList[I]['EntryCode']
        EntryWidget = self.EditList[I]['Entry']
        #Extract useful info from the Widreq about this option
        OptionType, DefaultValue, PresentValue, ExtraInfo = self.Options[OptionName]
        if self.SelectionBox['Index'] <> I:
            #The icon clicked is not of the currently selected option
            Reason = ('open','close')[ExtraInfo]
                
            if not self.StatusCheck(HelpTopic=('OptionEdit.InvalidValue',['%s a nested option'%Reason])):
                #if the currently selected option value is invalid, belay this assist request
                return
        self.ShiftFocusTo(I,Who='on_OpenClose')
        self.Options.SetVis(OptionName,not ExtraInfo)
        self.Generate()
            
    def on_F1(self,Event):
        """=e
        User pressed F1 for help; figure out which option is active and invoke help.
        """
        Index = self.SelectionBox['Index']
        OptionName = self.EditList[Index]['Name']
        if self.Edit == 'Option':
            Widget = self.CurrentWidreq.WidgetName
            Help('widget.%s.option.%s'%(Widget,OptionName))
            
        elif self.Edit == 'Pack':
            Help('pack.option.%s'%OptionName)

    def ContractOptionName(self,Name):
        """
        Look after contracting names of nested options.
        
        Nested option names can be things like "Yada.Spam.Whatever" and they take up too much
            space. We shorten them to simply "Whatever", which is to say the final segment
            of the name.
            
        Also, remove any dashes from the name. In some instances we put dashes in the option
            name to make otherwise ambiguous cases distinct (eg Pmw.ScrolledCanvas borderframe
            and border-frame) but we delete them here before the user sees them.            
        """
        SpaceFactor = 4
        Temp = Name.split('.')
        return Temp[-1].replace('-','')

    def Generate(self,TargetSelectionName=None):
        """=m
        Create and populate the canvas on which we actually edit.
        
        If TargetSelectionName is not None they we draw a selection box around the option
            of the same name. If there is no option of the same name then no selection
            box is drawn.
        """        
        self.NeedRefresh = False
        self.EnumerateRadioToast()

        #Made sure our options are up to date
        if self.Edit == 'Options':
            self.Options = self.CurrentWidreq.Options
        elif self.Edit == 'Pack':
            self.Options = self.CurrentWidreq.PackOptions
        else:
            raise Exception, "Unknown edit type: "+Edit    

        #If we already have a canvas then get rid of it.
        if hasattr(self,'Canvas'):
            self.Canvas.clear()
            self.Canvas.pack_forget()
            del self.Canvas
            if hasattr(self,'ScrollY'):
                self.ScrollY.pack_forget()
                del self.ScrollY
        #Stuff is the option information from our widreq but only those options which are
        #    currently expanded for visibility
        self.EnumerateRadio = None
        Stuff = self.Options.Visible()
        Stuff.sort()

        #Our edit area consists of:
        #    The actual entry or whatever widget
        #    The assist icon
        #    Scroll bar if necessary.
        self.ComputeHeights()
        WidthCanvas = self.WidthTotal
        #The fudge factor of +4 leaves room for our selection right of the assist icon
        EntryPixels = self.WidthEdit - (self.WidthAssistIcon+4)
        if self.HeightRequired > self.HeightForCanvas:
            #scroll bar is required; adjust things
            EntryPixels -= Cfg.Info['Metrics']['ScrollBarWidth']
            WidthCanvas -= Cfg.Info['Metrics']['ScrollBarWidth']
        
        if self.Edit == 'Pack' and self.CurrentWidreq.FrameID == (0,):
            #Hmm, we are the root frame which doesn't have a pack editor.
            Msg = 'The form itself has no pack options.\n\nThe form is a class and ' \
                'any instance of the class is packed by the code that creates ' \
                'the instance.'
            Space = WidthCanvas - 50    
            self.Canvas = Label(self.Frame,text=Msg,wraplength=Space,justify=LEFT)
            self.Canvas.pack(padx=20,pady=20)
            self.EditList = []
            return

        #Create a  canvas to hold the options to be edited
        self.Canvas = rpDndCanvas(self,width=WidthCanvas,height=self.HeightForCanvas
            ,scrollregion=(0,0,100,1000),bd=0,highlightthickness=0)
        self.Canvas.pack(side=LEFT,expand=N,fill=BOTH)
        self.Canvas.bind('<Button-1>',self.on_GeneralClick) #this handles option selection
        self.Canvas.bind('<Double-Button-1>',self.on_DoubleClick) #this handles handler go-to
        self.Canvas.bind(HelpButton,self.on_GeneralClick) #this handles help requests
        
        #EditList contains one entry per option being displayed. Each entry is a dictionary
        #   of information about that entry:
        #   'Entry': Whatever edit widget this option needs, often an Entry, sometimes a Label
        #   'Assist': The assist button widget, or None.
        #   'Y': The Y location on the canvas of the top of this options area.
        #   'Name': The name of this option
        #   'EntryCode': A single letter code indicating the type of edit device:
        #                - for Label, e for Entry.
        #
        #Note that each Entry and each Assist contains in it 'OurIndex' which is an index
        #   into EditList.
        self.EditList = []
        #We start Ypos at 1 to leave room for the selection rectangle above the top item.
        Ypos = self.HeightSelectionOffset + 2
        OurIndex = -1
        #This is used for indenting nested options
        IndentPixels = 12
        #Get the name of the selected entry
        if TargetSelectionName == None:
            #We wern't directed to a specific entry
            if self.SelectionBox['Index'] == None:
                #No entry previusly selected, default to first entry
                self.SelectionBox['Index'] = 0
            else:
                #Make sure the previously selected entry is reasonable
                if self.SelectionBox['Index'] >= len(Stuff):
                    #It's off the end - select the last entry
                    self.SelectionBox['Index'] = len(Stuff) - 1
            TargetSelectionName = Stuff[self.SelectionBox['Index']][0]            
        SelectedYTop = None
        for Opt,Info in Stuff:
            OurIndex += 1
            #Opt is the name of the option eg "anchor"
            OptionType, DefaultValue, PresentValue, ExtraInfo = Info
            #Fetch the two letter code that says what to do vis-a-vis edit and assist
            if OptionType in Cfg.Info['EnumeratedOptions'].keys():
                #Enumerated options automatically get a label and an assist
                Letters = '-a'
                Choices = Cfg.Info['EnumeratedOptions'][OptionType]
                IsEnumerated = 1
            elif OptionType in Cfg.Info['BuiltinOptions'].keys():
                #Builtin options get what the config says to give them
                Letters = Cfg.Info['BuiltinOptions'][OptionType]['EditCodes']
                IsEnumerated = 0
            elif OptionType == 'name':
                #name is special    
                IsEnumerated = 0
                Letters = 'e-'
                if self.CurrentWidreq.IsMainForm():
                    #Our widreq is the main form of the main module; you can't change it's name.
                    Letters = '--'
            else:
                raise Exception, 'OptionEdit.Generate: Unknown option type "%s"'%OptionType
            #    
            #The label, and possible open/close button
            #
            # I'm not sure why we have to set the font here. I thought in Config we set
            #    a global font specification, and everybody else seems to use that 
            #    font. Here, howerver, if you don't specify the font you get some
            #    default font which isn't what we want. 
            Fudge = IndentPixels * Opt.count('.')
            if OptionType in Cfg.Info['NestedOptions']:
                #It's a nested option; we need the open/close button
                Icon = Cfg.Info['OpenIcon']
                if ExtraInfo:
                    Icon = Cfg.Info['CloseIcon']
                OCI = Label(self.Canvas,borderwidth=0,image=Icon,relief=FLAT,takefocus=1)
                OCI.OurIndex = OurIndex
                OCI.bind('<Button-1>',self.on_OpenClose)
                OCI.bind(HelpButton,self.on_GeneralClick)
                OCI.OptionType = OptionType
                IdOCI = self.Canvas.create_window(2+Fudge,Ypos+4,window=OCI,anchor=NW)
                Fudge = Fudge + 12
            #Now the actual label
            Idl = self.Canvas.create_text(5+Fudge,Ypos+4 ,font=Cfg.Info['Font']
                ,anchor=NW,text=self.ContractOptionName(Opt))
            #    
            #The edit
            #
            XFudge = 0
            if Letters[0] == 'e':    
                #Supply an entry field
                E = EntryPixel(self.Canvas,width=EntryPixels,highlightthickness=0)
                if Info[2] <> None:
                    E.insert(0,Info[2])
                E.bind('<FocusIn>',self.on_FocusIn)
            elif Letters[0] == '-':
                #Supply a label
                if IsEnumerated:
                    #Convert present value (eg 0) into a display value (eg 'False')
                    PresentValue = ReverseDictLookup(Choices,PresentValue)
                if OptionType == 'cvar':
                    #cvars need special formatting    
                    PresentValue = Rpo.cvar_Format(PresentValue,ExtraInfo)
                elif OptionType == 'pmwcomp':
                    #For this type the value to display is in Default
                    PresentValue = DefaultValue
                elif OptionType == 'font':
                    #Format the tuli
                    PresentValue = Rpw.FontToString(PresentValue)
                E = LabelPixel(self.Canvas,width=EntryPixels,text=PresentValue,takefocus=1,anchor=W
                    ,pady=0)
                E.bind('<Button-1>',self.on_GeneralClick) #for selection
                E.bind('<Double-Button-1>',self.on_DoubleClick) #for handler goto
                E.bind(HelpButton,self.on_GeneralClick) #for help
                if OptionType == 'command':
                    #Command options get bubble help
                    rpHelp.HintHandler(E,PresentValue)
            else:
                raise Exception, 'Unknown edit area code "%s"'%Letters[0]
            E.OurIndex = OurIndex
            E.Option = Opt
            E.bind(HelpButton,self.on_GeneralClick) #for help
            #I tried binding Up/Down to the canvas but that didn't fly, so we bind them
            #    to the edit
            E.bind('<KeyPress-Up>',self.on_UpKey)        
            E.bind('<KeyPress-Down>',self.on_DownKey)
            E.bind('<KeyPress-Return>',self.on_DownKey)
            E.bind('<F1>',self.on_F1)        
            IdE = self.Canvas.create_window(self.WidthLabel+XFudge,Ypos,window=E,anchor=NW)
            #
            #The assist button
            #
            if Letters[1] == 'a':
                A = Label(self.Canvas,borderwidth=0,image=Cfg.Info['AssistIcon'],relief=FLAT,takefocus=1)
                A.OurIndex = OurIndex
                A.bind('<Button-1>',self.on_Assist)
                A.bind(HelpButton,self.on_GeneralClick)
                A.OptionType = OptionType
                IdA = self.Canvas.create_window(self.WidthLabel+EntryPixels,Ypos+1,window=A,anchor=NW)
            elif Letters[1] == '-':
                #We need a placeholder even if there is no actual assist
                A = None
            else:    
                raise Exception, 'Unknown assist code "%s"'%Letters[0]
            #Build the entry in EditList
            self.EditList.append({'Entry':E, 'EntryCode':Letters[0], 'Y':Ypos, 'Name':Opt, 'Assist':A})
            #If this is the selected option, draw the selection box around it.
            #if OurIndex == self.SelectionBox['Index']:
            if TargetSelectionName == Opt:
                X1 = 1
                Y1 = Ypos-self.HeightSelectionOffset
                X2 = WidthCanvas-1
                Y2 = Ypos+self.HeightEach-3
                #~self.SelectionBox = {'X':X1, 'Y': Y1, 'Index':OurIndex}
                self.SelectionBox['X'] = X1
                self.SelectionBox['Y'] = Y1
                self.SelectionBox['Id'] = self.Canvas.create_line(X1,Y1,X2,Y1,X2,Y2,X1,Y2,X1,Y1,width=2)
                self.SelectionBox['Index'] = OurIndex
                SelectedYTop = Ypos
            Ypos += self.HeightEach
        self.DoScrollBar()
        self.Canvas.BabysitScrollregion()

        #Insure selected item is visible on the canvas
        if SelectedYTop == None:
            #We didn't encounter an option to select
            return
        FirstVisible = self.Canvas.canvasy(0)
        LastVisible = self.Canvas.canvasy(self.HeightForCanvas)
        #Get top and bottom Y location of selected entry
        Top = SelectedYTop 
        Bottom = Top + self.HeightEach+2
        if Top < FirstVisible or Bottom > LastVisible:
            ##D('Top=%s FirstVisible=%s Bottom=%s LastVisible=%s'%(Top,FirstVisible,Bottom,LastVisible))
            ##D('self.Canvas.winfo_geometry()=%s'%str(self.Canvas.winfo_geometry()))
            #Agg! Part of selected entry is not visible.
            Middle = (Top + Bottom) / 2
            #Attempt to position the selected entry in the middle of the viewport
            Target = (float(Middle) - float(self.HeightForCanvas/2)) / float(self.HeightRequired)
            ##D('Must scroll. Middle=%s HtReq=%s Target=%s'%(Target,Middle,self.HeightRequired))
            self.Canvas.yview_moveto(Target)

class Widgetator(Frame):
    """=m
    The dreaded Widgetator
    
    """
    def __init__(self,Master,**kw):
        """
        Create the widgetator
        """
        Frame.__init__(self,Master)
        self.AllWidreqs = []
        #Initially we have no packed editors
        self.CurrentOptionEditor = None
        self.CurrentBindEditor = None
        self.CurrentPackEditor = None
        #
        # widreq selector pulldown at the top
        #
        self.Selector = Rpw.ComboBox(self,label='  Widget:',selectioncommand=self.on_Selection
            ,arrowicon=Cfg.Info['ComboIcon'])    
        self.Selector.pack(side=TOP,pady='5',fill=X)
        for Name in ['label','arrowbutton','entry']:
            #bind everything in sight to help
            Comp = self.Selector.component(Name)
            Comp.HelpTopic='widgetator.selector'
            Comp.bind(HelpButton,self.on_HelpClick)
        # The widreq presently showing in the widgetator
        self.CurrentWidreq = None
        #
        # tabbed notebook for editors
        #
        self.NoteBook = rpHelp.TabbedFrame(self
            ,RaiseCommand=self.on_NoteBookRaise
            ,LowerCommand=self.on_NoteBookLower
            ,borderwidth=1
            ,relief=GROOVE)
        self.NoteBook.pack(side=TOP,expand=YES,fill=BOTH)
        self.NoteBook.Add('Options')
        self.NoteBook.Add('Bindings')
        self.NoteBook.Add('Pack')
        self.NoteBook.Select('Options')
        self.NoteBook.PageFrame().bind('<Configure>',self.PageSizeChange)
        # The nominal width of the option editor width and edit areas
        self.OptionWidths = [130,130]
        self.BindWidths = [130,130]
        self.PackWidths = [130,130]
        # Register ourself with the widreq repository
        self. WRID = Repo.Register('The Widgetator')
        Repo.Bind(self.WRID,'HerdSelectNotify', self.on_HerdSelect)
        #If a herd is already selected, then call our function to bind to it.
        if Repo.SelectedHerd <> None:
            self.on_HerdSelect('HerdSelect',Repo.SelectedHerd,None)
        #Bind help to the widgetator tabs
        for T in self.NoteBook.TabNames():
            Tab = self.NoteBook.Tab(T)
            Tab.HelpTopic = 'widgetator.tab.%s'%T
            Tab.bind(HelpButton,self.on_HelpClick)
        #We have no current option for option editor
        self.CurrentOptionName = None
        #Create - but do not pack - the resize bar
        NoteBookPage = self.NoteBook.PageFrame()
        self.ResizeBar = ResizeBar(NoteBookPage,self.OptionWidths,self.on_ResizeKnobs)

    def StatusCheck(self,Help=None):
        """
        Return True if Option and Pack editors have all valid values, else False
        """
        if self.CurrentOptionEditor <> None:
            #We have an option editor
            if not self.CurrentOptionEditor.StatusCheck(Help):
                #If has an invalid value
                return False
        if self.CurrentPackEditor <> None:
            #We have a pack editor
            if not self.CurrentPackEditor.StatusCheck(Help):
                #It has an invalid value
                return False
        return True            

    def WidthsGet(self):
        """
        Return current widths of option/bind/pack editors, in that order.
        
        The result is a tuple of three elements where each element is a 2-tuple giving
            (left-part-width, right-part-width).
        """
        return (self.OptionWidths,self.BindWidths,self.PackWidths)

    def WidthsSet(self,Widths):
        """
        Set widths of option/bind/pack editors. Argument as returned by WidthsGet.
        """
        self.OptionWidths, self.BindWidths, self.PackWidths = Widths
        
    def EditorRefresh(self):
        """
        Request the current editor (option,bind,pack) refresh it's display.
        
        This is useful if an external actor has changed some of the data which
            the editor displays and we want to sync the display with the data.
            
        Note that this affects only the currently visible editor.    
        """
        
        WidgetatorTab = self.NoteBook.GetCurSelection()
        Widreq = self.CurrentWidreq
        if WidgetatorTab == 'Options':
            if hasattr(Widreq,'OptionEditor'):
                Widreq.OptionEditor.EditorRefresh()
        elif WidgetatorTab == 'Bindings':
            if hasattr(Widreq,'BindEditor'):
                Widreq.BindEditor.EditorRefresh()
        elif WidgetatorTab == 'Pack':
            if hasattr(Widreq,'PackEditor'):
                Widreq.PackEditor.EditorRefresh()

    def ModuleNew(self):
        """
        A new module has been added to the project. Take action as necessary.
        """
        self. WRID = Repo.Register('The Widgetator')
        Repo.Bind(self.WRID,'HerdSelectNotify', self.on_HerdSelect)
        self.CurrentWidreq = None
        #If a herd is already selected, then call our function to bind to it.
        if Repo.SelectedHerd <> None:
            self.on_HerdSelect('HerdSelect',Repo.SelectedHerd,None)
            self.CuttentOptionName = None
        self.EditorsUnpack()
        self.SelectorUpdate()    

    def ModuleChange(self):
        """
        The currently selected module has changed; adjust display.
        """
        self.EditorsUnpack()
        ##D('ModuleChange; Repo.FetchSelected()=%s'%Repo.FetchSelected())
        self.SelectorUpdate()    
        self.NowActivate(Repo.Fetch(Repo.FetchSelected()))
        
    def on_NoteBookRaise(self,Page):
        """
        This gets called when the user switches NoteBook tabs.
        """
        self.NowActivate(self.CurrentWidreq)

    def on_NoteBookLower(self,Page):
        """
        This gets called when the user switches Widgetator NoteBook tabs.
        
        If an editor is showing on the current page we unpack it. If we *don't* unpack
            it and some other editor on a different tab tries to shrink the page, it won't 
            be allowed to because *this* editor will be larger.
        """    
        #D('on_NoteBookLower. Page=%s'%Page)
        if Page == 'Options':
            #The OptionEditor page is currently active
            if self.CurrentWidreq and hasattr(self.CurrentWidreq,'OptionEditor'):
                #Check for presently invalid option value
                H = ('OptionEdit.InvalidValue',['select a different editor'])
                if not self.CurrentWidreq.OptionEditor.StatusCheck(HelpTopic=H):
                    #status is not ok; we refuse to be lowred
                    return False
                self.NoteSelectedOptions()
            else:
                self.CurrentOptionName = None
            self.EditorsUnpack('option')
        elif Page == 'Bindings':
            #The bind editor page is currently active
            self.EditorsUnpack('bind')    
        elif Page == 'Pack':
            #The PackEditor page is currently active
            if self.CurrentWidreq and hasattr(self.CurrentWidreq,'PackEditor'):
                #Check for presently invalid option value
                H = ('PackEdit.InvalidValue',['select a different editor'])
                if not self.CurrentWidreq.PackEditor.StatusCheck(HelpTopic=H):
                    #status is not ok; we refuse to be lowred
                    return False
                self.NoteSelectedOptions()
            else:
                self.CurrentPackOptionName = None
            self.EditorsUnpack('pack')    
        else:
            raise Exception, "Unknown NoteBook page: "+Page                    
        #The resize bars always go
        try:
            self.ResizeBar.pack_forget()    
        except AttributeError:
            pass #doesn't exist yet    
        #All systems are apparently go
        return True

    def on_HelpClick(self,Event):
        """
        User clicked for help in a widgetator area
        """
        Help(Event.widget.HelpTopic)
        
    def on_HerdSelect(self, Event, A, B):
        """
        This gets called when the current herd changes.
        
        Since we want to take action in response to widreq activity, we
            bind to various events on the newly selected herd.
        """
        ##D('on_HerdSelect Event=%s A=%s B=%s'%(Event,A,B))
        Repo.Bind(self.WRID,'WidreqCreateNotify WidreqDeleteQuery WidreqDeleteNotify'
            ' WidreqRenameNotify WidreqSelectNotify',self.WidrepCallback)
        #Any editor packed will have pertained to the previous form
        self.EditorsUnpack()
        #Since the form has changed, so has the selected widreq    
        self.CurrentWidreq = Repo.FetchSelected()
        #Since the herd has changed we must update the selector
        self.SelectorUpdate()    

    def WidrepCallback(self, Event, A, B):
        """
        This is bound to various widreq repository events.
        """
        if Event == 'WidreqDeleteQuery':
            #A widreq is being proposed for deletion. That is OK with us, but some
            #    cleanup will have to be done once it is deleted. We make a link
            #    to the targed widreq so we can still mess with it after it is
            #    'deleted'. Sort of a (brief) afterlife for dead widreqs.
            self.WidreqForDeletion = Repo.Fetch(A)
            return 1
            
        if Event == 'WidreqDeleteNotify':
            #The widreq actually got deleted; make it's icon on the canvas go away
            self.WidreqForDeletion.Vanish(All=True)
            #If the widreq has an Editor, it will be registered with the repository; 
            #    unregister it. This is important. The Widreq is registered with the 
            #    repository under some name (eg Button1). If we DON'T unregister it 
            #    and we go to create another widreq named Button1 then the repository 
            #    will say it's a duplicate registration. Besides, we should not keep 
            #    unnecessary crap in the repository.
            self.EditorsUnpack()
            if hasattr(self.WidreqForDeletion,'OptionEditor'):
                self.WidreqForDeletion.OptionEditor.Terminate()
            if hasattr(self.WidreqForDeletion,'BindEditor'):
                self.WidreqForDeletion.BindEditor.Terminate()
            if hasattr(self.WidreqForDeletion,'PackEditor'):
                self.WidreqForDeletion.PackEditor.Terminate()
            if self.WidreqForDeletion == self.CurrentWidreq:
                Temp = Repo.ListWidreqs()
                if Temp == []:
                    #There are no widreqs in the current herd
                    self.CurrentWidreq = None
                    self.ResizeBar.pack_forget()
            #Delete the reference so it can go away
            self.WidreqForDeletion = None    
            
        if Event in ['WidreqCreateNotify', 'WidreqDeleteNotify', 'WidreqRenameNotify']:
            #the widreq set has changed; update the selector
            self.SelectorUpdate()
            
        if Event in ['WidreqSelectNotify']:
            if GblLoadInProgress:
                return
            NewSelectee = Repo.Fetch(A)
            if self.CurrentWidreq:
                #We have a currently selected widreq
                self.NoteSelectedOptions()
                if self.CurrentWidreq <> NewSelectee:
                    #Our current widreq is being unselected
                    self.EditorsUnpack()
            #Make sure the selector reflects the new selection. NOTE: it is important that we
            #    call SelectorUpdate *after* we have unpacked the previous editor.        
            self.SelectorUpdate()
            #Activate the new widreq
            self.NowActivate(NewSelectee)
            
        if Event in ['WidreqRenameNotify']:
            self.Selector.selectitem(Repo.FetchSelected())

    def EditorsUnpack(self,Which='all'):
        """
        Unpack editor(s) as specified
        
        Which can be "option", "bind", "pack" or "all"
        """
        if Which in ('all','option') and self.CurrentOptionEditor <> None:
            self.CurrentOptionEditor.pack_forget()
            self.CurrentOptionEditor = None
        if Which in ('all','bind') and self.CurrentBindEditor <> None:
            self.CurrentBindEditor.pack_forget()
            self.CurrentBindEditor = None
        if Which in ('all','pack') and self.CurrentPackEditor <> None:
            self.CurrentPackEditor.pack_forget()
            self.CurrentPackEditor = None
        #If were toasting them all then the resize bars go too
        if  self.CurrentOptionEditor == None \
        and self.CurrentBindEditor == None   \
        and self.CurrentPackEditor == None:            
            try:
                self.ResizeBar.pack_forget()    
            except AttributeError:
                #May not exist yet
                pass    

    def NoteSelectedOptions(self):
        """
        Note selected options of current widreq.
        """
        if self.CurrentWidreq:
            if hasattr(self.CurrentWidreq, 'OptionEditor'):
                self.CurrentOptionName = self.CurrentWidreq.OptionEditor.WhoIsSelected()
            if hasattr(self.CurrentWidreq, 'PackEditor'):
                self.CurrentPackOptionName = self.CurrentWidreq.PackEditor.WhoIsSelected()

    def SelectorUpdate(self):
        """
        Update the selector
        """
        if GblLoadInProgress:
            return
        List = Repo.ListWidreqs()
        if len(List) == 0:
            self.Selector.clear()
        else:    
            #Update the list of widreq the user can choose from
            self.Selector.ChoiceListSet(List)
            #Make sure the currently selected widreq is showen in the Entry
            SelWid = Repo.FetchSelected()
            if SelWid <> None:
                self.Selector.selectitem(SelWid)
                self.NowActivate(Repo.Fetch(SelWid))
        if self.CurrentWidreq == None:
            #We have no current widreq; blank out the Entry in the ComboBox
            self.Selector.selectnone()

    def PageSizeChange(self,Event):
        """
        This gets called when we get resized
        """
        HeightAvailable = rpHelp.GeometryDecode(self.NoteBook.PageFrame().winfo_geometry())[1] - 8
        if hasattr(self.CurrentWidreq,'OptionEditor'):
            #the option editor exists, tell it about the new height
            self.CurrentWidreq.OptionEditor.NoteNewHeight(HeightAvailable)
        if hasattr(self.CurrentWidreq,'PackEditor'):
            #the pack editor exists, tell it about the new height
            self.CurrentWidreq.PackEditor.NoteNewHeight(HeightAvailable)

    def WidthCoerce(self,Master,Slave):
        """
        Given two width pairs, coerce Slave to size of Master
        
        Each of the arguments is a two-element list giving:
            o Width of left part
            o Width of right part
            
        On return the total width of Slave will have been set to match the total
            width of Master. The relative size of Slave's left/right parts is
            preserved.
        """
        MTotal = Master[0] + Master[1]
        STotal = Slave[0] + Slave[1]
        if MTotal == STotal:
            #No coercion is necessary
            return
        #Compute fraction presently allocated to slave left    
        SLeft = float(Slave[0]) / float(STotal) 
        #Allocate slave left a corresponding amount of the new total
        Slave[0] = int(round(SLeft * MTotal))
        #And slave right gets whatever remains
        Slave[1] = MTotal - Slave[0]
        #Sanity check
        assert Master[0] + Master[1] == Slave[0] + Slave[1]
            
    def on_Selection(self):
        """
        This gets called when the user choses the name of a widreq  in the Selector.
        """
        Temp = self.Selector.getcurselection()
        if len(Temp) == 0:
            #nothing was selected; happens if user clicks on an empty Selector
            return
        WidreqName = Temp
        # Request that the currently selected widreq be changed
        R = Repo.Request(self.WRID, 'WidreqSelect', WidreqName)
        if  R <> 1:
            #The change didn't fly
            if R[2] == 0:
                #the user hasn't been notified yet. 
                #Rpw.ErrorDialog('%s (from %s)'%(R[0], R[1]))
                Rpw.ErrorDialog('There is no widget named "%s" to select.'%WidreqName)
            #since the user may have keyed in bonzo stuff we refresh the list
            List = Repo.ListWidreqs()
            self.Selector.ChoiceListSet(List)

    def PrintWidths(self):
        #D('OptionWidths now  %s'%str(self.OptionWidths+[self.OptionWidths[0]+self.OptionWidths[1]]))
        #D('  BindWidths now  %s'%str(self.BindWidths+[self.BindWidths[0]+self.BindWidths[1]]))
        return

    def on_ResizeKnobs(self,NewWidths):
        """
        This is invoked by the resize bar when the user has changed the requested size.
        """
        WidgetatorTab = self.NoteBook.GetCurSelection()
        if WidgetatorTab == 'Options':
            if NewWidths == self.OptionWidths:
                #They didn't change; no action needed
                return
            self.OptionWidths = NewWidths
            #Coerce other editors to the same total width
            self.WidthCoerce(self.OptionWidths, self.BindWidths)
            self.WidthCoerce(self.OptionWidths, self.PackWidths)
        elif WidgetatorTab == 'Bindings':
            if NewWidths == self.BindWidths:
                #They didn't change; no action needed
                return
            self.BindWidths = NewWidths
            #Coerce other editors to the same total width
            self.WidthCoerce(self.BindWidths, self.OptionWidths)
            self.WidthCoerce(self.BindWidths, self.PackWidths)
        elif WidgetatorTab == 'Pack':
            if NewWidths == self.PackWidths:
                #They didn't change; no action needed
                return
            self.PackWidths = NewWidths
            #Coerce other editors to the same total width
            self.WidthCoerce(self.PackWidths, self.BindWidths)
            self.WidthCoerce(self.PackWidths, self.OptionWidths)
        else:
            raise Exception, "Unknown tab type: "+WidgetatorTab
        #Invoke NowActivate to redraw the editor at the correct size.                
        self.PrintWidths()
        self.NowActivate(self.CurrentWidreq)
    
    def ResizeBarSetup(self):
        """
        Set the resize bars to the size and info for the current editor
        """        
        if not hasattr(self,'ResizeBar'):
            #The resize bar doesn't exist yet
            return
        WidgetatorTab = self.NoteBook.GetCurSelection()
        if not GblLoadInProgress:
            self.ResizeBar.pack(side=TOP,fill=X)
        if WidgetatorTab == 'Options':
            #Have resize bar show option widths
            self.ResizeBar.NoteWidths(self.OptionWidths)
            #And information re option editor
            self.ResizeBar.NoteInfo(['edit','entry'],'optioneditor.resizeKnobs')
        elif WidgetatorTab == 'Bindings':
            #Have resize bar show binding widths
            self.ResizeBar.NoteWidths(self.BindWidths)
            #And information re bind editor
            self.ResizeBar.NoteInfo(['event abbreviation','handler name'],'bind-editor.resizeKnobs')
        elif WidgetatorTab == 'Pack':
            #Have resize bar show pack widths
            self.ResizeBar.NoteWidths(self.PackWidths)
            #And information re bind editor
            self.ResizeBar.NoteInfo(['edit','entry'],'pack-editor.resizeKnobs')
            pass    
        else:
            raise Exception, "Unknown Widgetator tab"+WidgetatorTab        

    def NowActivate(self,Widreq):
        """
        This gets called when the current widget changes or the NoteBook tab changes.
        """   
        if GblLoadInProgress:
            return
        R = self.NowActivateSub(Widreq)
        if not R:
            self.NowActivateSub(Widreq)
                    
    def NowActivateSub(self, Widreq):
        """
        This method does the actual work.
        """
        if Widreq == None:
            #The widreq is None; little to do. This can happen if the user switches
            #    NoteBook tabs with no or no selected widreq.
            return
        #Make sure the specified widreq is shown in the selector    
        self.Selector.selectitem(Widreq.Name)
        #Find out what tab is presently showing
        WidgetatorTab = self.NoteBook.GetCurSelection()
        self.CurrentWidreq = Widreq
        #setup resize bar position, help and hint
        self.ResizeBarSetup()
        #Check to see if being-activated widreq already has an appropriate editor
        if WidgetatorTab == 'Options':
            if hasattr(Widreq,'OptionEditor'):
                #Tab is Options and Widreq already has an editor.
                if Widreq.OptionEditor.ReportWidths() == self.OptionWidths \
                and not Widreq.OptionEditor.NeedRefresh:
                    #This editor was drawn at the current option editor width settings so we can us it as-is.
                    Widreq.OptionEditor.pack(expand=YES,fill=BOTH)
                    self.CurrentOptionEditor = Widreq.OptionEditor
                    #Have the editor attempt to select the most recently used option
                    Widreq.OptionEditor.SelectByName(self.CurrentOptionName)
                    return
                else:
                    #This editor was drawn with old widths; delete it and we will recreate it at the
                    #    correct size
                    Widreq.OptionEditor.pack_forget()    
                    Widreq.OptionEditor.Terminate()
                    del Widreq.OptionEditor
        elif WidgetatorTab == 'Bindings':
            if hasattr(Widreq,'BindEditor'):
                #Tab is Bindings and Widreq already has a bind editor.
                if Widreq.BindEditor.ReportWidths() == self.BindWidths \
                and not Widreq.BindEditor.NeedRefresh:
                    #This editor was drawn at the current option editor width settings so we can us it as-is.
                    Widreq.BindEditor.pack(expand=YES,fill=BOTH)
                    self.CurrentBindEditor = Widreq.BindEditor
                    return
                else:
                    #This editor was drawn with old widths; delete it and we will recreate it at the
                    #    correct size
                    Widreq.BindEditor.pack_forget()
                    Widreq.BindEditor.Terminate()
                    del Widreq.BindEditor
        elif WidgetatorTab == 'Pack':
            if hasattr(Widreq,'PackEditor'):
                #Tab is Pack and Widreq already has a pack editor.
                if Widreq.PackEditor.ReportWidths() == self.PackWidths:
                    #This editor was drawn at the current pack editor width settings so we can us it as-is.
                    Widreq.PackEditor.pack(expand=YES,fill=BOTH)
                    #self.CurrentOptionEditor = Widreq.PackEditor
                    self.CurrentPackEditor = Widreq.PackEditor
                    #Have the editor attempt to select the most recently used option
                    Widreq.PackEditor.SelectByName(self.CurrentPackOptionName)
                    return
                else:
                    #This editor was drawn with old widths; delete it and we will recreate it at the
                    #    correct size
                    Widreq.PackEditor.pack_forget()    
                    Widreq.PackEditor.Terminate()
                    del Widreq.PackEditor
        else:
            raise Exception, 'Unknown tab type: '+WidgetatorTab    
        #-------------------------------------------------------------------->            
        #Having arrived here we know that we need to create a new editor instance
        #    for this widgetator page.
        #This is the actual amount of space available for the option edit widget
        HeightAvailable = rpHelp.GeometryDecode(self.NoteBook.PageFrame().winfo_geometry())[1] - 8
        NoteBookPage = self.NoteBook.PageFrame()
        if WidgetatorTab == 'Options':
            #We are doing option editor
            assert not hasattr(self.CurrentWidreq,'OptionEditor'), "Should be no editor at this point"
            #Create option editor for this widreq
            Widreq.OptionEditor = OptionEdit(NoteBookPage,Widreq,HeightAvailable
                ,self.OptionWidths)
            #If there was a previously active editor then pass the name of the option it had
            #   selected to the new editor in case it has an option of the same name.
            Widreq.OptionEditor.SelectByName(self.CurrentOptionName)
            Widreq.OptionEditor.pack(expand=YES,fill=BOTH)
            self.CurrentOptionEditor = Widreq.OptionEditor
        elif WidgetatorTab == 'Bindings':
            #We are doing a bind editor
            assert not hasattr(self.CurrentWidreq,'BindEditor'), "Should be no editor at this point"
            #Create bind editor for this widreq
            Widreq.BindEditor = BindEdit(NoteBookPage,Widreq,HeightAvailable
                ,self.BindWidths)
            Widreq.BindEditor.pack(expand=YES,fill=BOTH)
            self.CurrentBindEditor = Widreq.BindEditor
        elif WidgetatorTab == 'Pack':
            #We are doing pack editor
            assert not hasattr(self.CurrentWidreq,'PackEditor'), "Should be no pack editor at this point"
            #Create pack editor for this widreq
            Widreq.PackEditor = OptionEdit(NoteBookPage,Widreq,HeightAvailable
                ,self.PackWidths,Edit='Pack')
            #If there was a previously active editor then pass the name of the option it had
            #   selected to the new editor in case it has an option of the same name.
            #Widreq.OptionEditor.SelectByName(self.CurrentOptionName)
            Widreq.PackEditor.pack(expand=YES,fill=BOTH)
            self.CurrentPackEditor = Widreq.PackEditor
        else:
            raise Exception, 'Unknown tab type: '+WidgetatorTab    
        self.update_idletasks()
        #If we got different size than we called for, adjust widths to use size
        ActualTotal = self.NoteBook.PageFrame().winfo_width()
        if ActualTotal == 1:
            if WidgetatorTab == 'Options':
                self.OptionEditorsUnpack('option')
                Widreq.OptionEditor.Terminate()
                del Widreq.OptionEditor
            elif WidgetatorTab == 'Bindings':    
                self.OptionEditorsUnpack('bind')
                Widreq.BindEditor.Terminate()
                del Widreq.BindEditor
            elif WidgetatorTab == 'Pack':
                self.OptionEditorsUnpack('pack')
                Widreq.PackEditor.Terminate()
                del Widreq.PackEditor
            return 1    
        if ActualTotal <> self.OptionWidths[0] + self.OptionWidths[1]:
            FakeMaster = [ActualTotal,0]
            self.WidthCoerce(FakeMaster,self.OptionWidths)
            self.WidthCoerce(FakeMaster,self.BindWidths)
            self.PrintWidths()
            return 1
        #Now that we have the size settled, get the resize knobs right
        if WidgetatorTab == 'Options':
            self.ResizeBar.NoteWidths(self.OptionWidths)
        elif WidgetatorTab == 'Bindings':
            self.ResizeBar.NoteWidths(self.BindWidths)
        elif WidgetatorTab == 'Pack':
            self.ResizeBar.NoteWidths(self.PackWidths)    
        else:
            raise Exception, 'Unknown notebook page: '+WidgetatorTab
        return

class WidReq(DND.Dragged,BindMixin):
    """=m
    A widget requestor.
    
    This is a DraggedObject to which we've added all the functionality we 
        need to implement widget requests.

    *Creating*

    Arguments:

    {
    "WidgetName" : The standard name of the kind of widget we are creating,
        eg "Button" for a standard Tkinter button. This is the name, which 
        if used to index "Cfg.Info['Modules'][ModuleName]['Widgets']" will get 
        you all the config info for the corresponding widget. ;
    "InstanceName" : The name of this widget requestor instance. Typically
        the WidgetName plus a number ('Button5') but don't rely on this. ;
    "FrameID" : If this widget is a "TopLevel" or a "Frame" then this is
        the ID of the corresponding frame. FrameID's are numeric tuples with
        the root frame being "(0,)". ;
    "PresentHome" : is where this widreq is living. This is generally known at
        widreq creation time for frame widreqs and unknown for other widreqs. ;
    "OptionList" : an optional list of dictionaries giving initial option settings. 
        This is specifically in aid of widreqs being created at project-load time.
        Each dictionary is as the "Options" dictionary generated by the "Gather"
        method of this class.
    "BindingList" : an option list of dictionaries giving the initial bindings.
        Each dictionary is as the "Binding" dictionary from "Gather".    
    "ModuleName" : The name of the module from which this type of widget is imported.
    }    

    *Variables*
    {
    "self.Bindings" : A list of binding quads: "[DecomposedEventList, EventString, EventHandlerMethod, Component]"
    
                    "DecomposedEventListList" is the list returned by function "EventStringDecompose"
                    "Component" is empty if the binding is against the main widget, or something like
                    "'frame'" or "'entryfield.entry'" if against a component of the widget.  ;
    "self.Canvas" :  The Canvas instance on which we are drawn. ;
    "self.FrameID" : If this widget is a "Toplevel", "Frame" or "Pmw.ScrolledFrame" then this is the
                     ID of the corresponding frame. Otherwise None. ;
    "self.HintHandler" : Our hint handler, None until we have been shown ;                 
    "self.FrameParent" : I *think* this is the ID of the frame on which a non-frame widget is being shown or "None"
                        for frame widgets and for non-frame widgets which aren't currently being shown. But don't
                        bet the farm on this being correct: FrameParent wasn't documented when it was introduced
                        and I just did a cursory check. If you care, do a thourough check.
    "self.Icon" :    The icon we use to represent ourself. An object of type
                     PhotoImage. ;
    "self.Label" :   The Label which is representing us on a canvas ;
    "self.Name" :    The instance name of this particular widreq, eg MyButton ;
    "self.ModuleName" : The name of the module from which this widget is imported ;
    "self.Options" : A dictionary of this widreqs options:
                     o [key] The name of this option
                     o [0] The option type
                     o [1] The default value
                     o [2] The current actual value 
                     o [3] The 'extra information field' ;
    "self.PackOptions" : Similar to "Options", but pertaining to pack options.                 
    "self.WidgetName" : The canonical name of the kind of widget we are, eg Button ;
    "self.X"        : The X location of our left side on the canvas. ;
    "self.Y"        : The Y location of our top on the canvas. ;
    }
    """
    def __init__(self
        ,WidgetName
        ,InstanceName
        ,FrameID=None
        ,PresentHome=None
        ,OptionList=None
        ,BindingList=None
        ,PackOptionList=None
        ,ModuleName=None):
        """
        Create a widget requestor.
        """
        DND.Dragged.__init__(self,Type='WidReq')
        #The canonical name of this widget
        self.WidgetName = WidgetName
        assert ModuleName <> None
        self.ModuleName = ModuleName
        #A link to this widgets info in the config info
        self.OurWidgetInfo = Cfg.Info['Modules'][self.ModuleName]['Widgets'][WidgetName]
        #The icon we show on the users form
        self.Icon =  self.OurWidgetInfo['Icon_w']
        #Our FrameID or None
        self.FrameID = FrameID
        #Create option dictionary for this widreq (Key:Type,Default,Value)
        #Create NestedOption object for this specific widget
        self.Options = self.OurWidgetInfo['Options'].Copy()
        
        #Set unique name as an option
        self.Options['name'] = ['name', InstanceName, InstanceName, None]
        #Create our pack options
        self.PackOptions = Cfg.Info['PackOptions'].Copy()
        #the dnd stuff uses this name, as does the routine 'NameWidReq'. Check around a bit
        #    before removing it, OK?
        self.Name = InstanceName
        #Note initial present home, if any
        self.PresentHome = PresentHome
        #Nor do they have any bindings
        self.Bindings = [] 
        self.Label = None
        ##D('Creating %s'%self.WRID_NameFetch())
        #Register with the repository
        self.WRID = Repo.Register(self.WRID_NameFetch())
        assert self.WRID <> None, 'Signup with repository unexpectedly failed'
        Repo.Bind(self.WRID, 'WidreqDeleteNotify HerdRenameNotify', self.on_WidRepNotify)
        #If option values were specified, set them now
        self.SetOptions(OptionList)
        self.SetBindings(BindingList)
        if PackOptionList <> None:
            for Opt in PackOptionList:
                self.PackOptions.SetCurrent(Opt['Name'],Opt['Value'])
        #We haven't been placed yet        
        self.X = self.Y = None 
        #We don't get a hint handler until we have been shown       
        self.OurHintHandler = None
        #If we are renamed as part of being moved to a different herd then this tells us
        #    the name to the receiving herd. At all other times this is None.
        self.TargetHerd = None
        #We don't have a FrameParent yet
        self.FrameParent = None

    def __str__(self):
        return 'Widreq instance %s on %s'%(self.Name, self.PresentHome)

    def MasterStringFetch(self,Base=None):
        """
        Return the string to be used to designate this widreq as master.
        
        Normally this is simply the name of the widreq instance, however some container
            widreqs, eg Pmw.ScrolledFrame, need extra qualification because they are not
            themselves something which derived from frame. The necessary information is
            supplied by the "Master" field of the config file.
            
        If "Base" is None then we use our name as the base.    
        """
        if Base == None:
            Base = self.Name
        
        return Base + Cfg.Info['Modules'][self.ModuleName]['Widgets'][self.WidgetName]['Master']

    def Convert(self,NewWidgetName,NewModuleName):
        """
        Convert the present widreq from one widget type to another.
        
        eg from Frame to ScrolledFrame
        
        The basic effect is to delete all of our existing options and replace them with
            default options of the new type. This makes most sense for container widreqs
            which are changing type.
        
        """
        self.WidgetName = NewWidgetName
        self.ModuleName = NewModuleName
        self.OurWidgetInfo = Cfg.Info['Modules'][self.ModuleName]['Widgets'][self.WidgetName]
        self.Options = self.OurWidgetInfo['Options'].Copy()
        self.Options['name'] = ['name', self.Name, self.Name, None]
        try:
            self.OptionEditor.NotifyExternalChange()
            self.OptionEditor.EditorRefresh()
        except AttributeError:
            #OptionEditor may not exist yet
            pass

    def IsMainForm(self):
        """
        Return True if we are the main form of the main module of the project.
        
        Each project has a main module, and each main module had a main form, which
            is special in that it shares the name of the project and it must be a frame
            and thus can derive only from Tkinter.Frame or Pmw.ScrolledFrame.
        """
        return Repo.ModuleName == Cfg.Info['ProjectName'] and self.Name == Cfg.Info['ProjectName']

    def SetOptions(self,OptionList):
        """
        Set some or all of the options to specified values.
        
        OptionList is a list of dictionaries where each dictionary has:
            o "['Name']" The name of the option to set.
            o "['Value']" The present value for this option.
            o "['Extra']" The extra information for this option
        """
        if OptionList:
            for Opt in OptionList:
                if self.Options[Opt['Name']][0] == 'pmwcomp':
                    #For nestged options set visibility
                    self.Options.SetVis(Opt['Name'],Opt['Extra'])
                else:
                    #Ordinary garden variety option
                    self.Options.SetCurrent(Opt['Name'],Opt['Value'])
                    self.Options.SetExtra(Opt['Name'],Opt['Extra'])

    def ListComponents(self):
        """
        Return a list of names of options of this widget which are Pmw components
        """
        Result = []
        for OptionName in self.Options.keys():
            Type,Default,Current,Extra = self.Options[OptionName]
            if Type == 'pmwcomp':
                Result.append(OptionName)
        return Result        
    
    def HandlerRenameNotify(self,Old,New):
        """
        Notify this widreq that the handler named "Old" has been renamed to "New".
        
        Any references this widreq has to the old handler name are updated.
        """
        #Look after bindings
        ##D('HandlerRenameNotify: widget=%s, Old=%s, New=%s'%(self.Name,Old,New))
        for Index in range(len(self.Bindings)):
            Decomposed,Event,Handler,Component = self.Bindings[Index]
            if Handler == Old:
                self.Bindings[Index][2] = New
                try:
                    self.BindEditor.NotifyExternalChange()
                except AttributeError:
                    #BindEditor may not exist yet
                    pass    
        #Look after command options     
        for OptionName in self.Options.keys():
            Type,Default,Current,Extra = self.Options[OptionName]
            if Type == 'command' and Current == Old and Extra:
                #Note that Extra is 1 if this is a Rapyd maintained binding
                self.Options.SetCurrent(OptionName,New)
                try:
                    self.OptionEditor.NotifyExternalChange()
                except AttributeError:
                    #OptionEditor may not exist yet
                    pass

    def HandlerDeleteNotify(self,HandlerName):
        """
        Note that a handler of the specified name has been deleted.
        
        Any bindings that referenced the handler are deleted while any command options that
            referenced the handler are cleared.
        """
        #Look after bindings; must do last-to-first because of possible deletions
        IndexRange = range(len(self.Bindings))
        IndexRange.reverse()
        for Index in IndexRange:
            Decomposed,Event,Handler,Component = self.Bindings[Index]
            if Handler == HandlerName:
                del self.Bindings[Index]
                try:
                    self.BindEditor.NotifyExternalChange()
                except AttributeError:
                    #BindEditor may not exist yet
                    pass    
        #Look after command options     
        for OptionName in self.Options.keys():
            Type,Default,Current,Extra = self.Options[OptionName]
            if Type == 'command' and Current == HandlerName and Extra == 1:
                #Note that Extra is 1 if this is a Rapyd maintained command option
                self.Options.SetCurrent(OptionName,None)
                try:
                    self.OptionEditor.NotifyExternalChange()
                except AttributeError:
                    #OptionEditor may not exist yet
                    pass
        
    def SetBindings(self,BindingList):
        """
        Set bindings.
        """
        if BindingList:
            for Bind in BindingList:
                Decomp = Rpo.EventStringDecompose(Bind['Event'])
                #2006/03/22 Note: Some projects were created before we had the component field
                #   for bindings. Once all projects have been converted to the new format then
                #   change this code to simply expect the Bind['Compenent'] entry.
                if Bind.has_key('Component'):
                    Component = Bind['Component']
                else:
                    Component = ''    
                self.Bindings.append([Decomp, Bind['Event'], Bind['Handler'], Component])        

    def HandlersList(self,Verbose=False):
        """
        Return a list of the Rapyd maintained event handlers referenced by this widget.
        
        Note that we check both bindings and command options.
        
        If "Verbose" is "False" then the result is a simple list of
            handler names.
        If "Verbose" is "True" then the result is a list where each element is
            a list:
            o [0] Name of handler
            o [1] Event string or command option name     
        """
        Temp = {}
        Result = []
        #Scan bindings
        for Decomp,String,Handler,Component in self.Bindings:
            if Verbose:
                Result.append([Handler,String])
            else:
                Temp[Handler] = 0
        #Scan options        
        for Key in self.Options.keys():
            Type,Default,Current,Extra = self.Options[Key]
            #Note that Extra is false for non-Rapyd maintained command options
            if Type=='command' and Current and Extra:
                if Verbose:
                    Result.append([Current,Key])
                else:
                    Temp[Current] = 1
        if not Verbose:
            Result = Temp.keys()            
        return Result

    def Gather(self,CanvasSize=None):
        """
        Gather information about this widreq and return it in a dictionary

        If "CanvasSize" is specified, we use it when translating from window
            coordinates to generic coordinates. If "CanvasSize" is not
            specified then we use the current size of our canvas.

        The result is a dictionary thus:
        
        o "['Name']" The name of this widreq, eg "MyButton"
        o "['ModuleName']" The name of the module from which we import this widget
            eg "'Tkinter'".
        o "['WidgetName"] The type of widget, eg "Button"
        o "['XY']" A 2-tuple giving the XY generic coordinates. For Frame and Toplevel 
            widgets this entry is always (0,0).
        o "['ID']" The frame-ID of this widreq, "None" if it isn't a frame.
        o "['Options']" A list of dictionaries:
            o "['Name']": The name of the option
            o "['Value']": The present value of the option
            o "['Extra']": The 'extra information' for this option.
        Note that *only* options whose value differs from the default value
            are included. Options whose value equals the default value are
            *NOT* shown here. Most options don't need extra information and
            the value of Extra for those options is None.
        o "['Bindings']" A list of dictionaries
            o "['Event']" The event string, eg "Button-Release-1"
            o "['Handler']" The name of the event handler, eg "on_MyButton_ButRel1"
            o "['Component']" '' if the binding applies to the base widget, or the name of the 
                component to which the binding applies, eg 'frame' or 'entryfield.entry'
        o "['PackOptions']" A list of dictionaries:
            o "['Name']" The name of the pack option.
            o "['Value']" The value of the pack option.
        Only those pack option whose value differs from the default option
            are listed.
        """
        if CanvasSize == None:
            CanvasSize = (self.Canvas.winfo_width(),self.Canvas.winfo_height())
        if self.FrameID == None:
            XY = CanvasToGeneric(self.WhereCenter(),(CanvasSize))
        else:
            XY = (0,0)    
        #D('Generic XY=%s, WhereCenter=%s'%(str((X,Y)),str(W.WhereCenter())))
        #Gather basic widget info:    
        Result = {'Name':self.Name,
                      'WidgetName':self.WidgetName,
                      'ModuleName':self.ModuleName,
                      'XY':XY,
                      'ID':self.FrameID}
        #Gather info about non-default options
        WidreqOptions = []
        for Option in self.Options.keys(SeeAll=True):
            if Option == 'name':
                continue
            OptionType, Default, Current, Extra = self.Options[Option] 
            if Default <> Current or OptionType == 'pmwcomp':
                #we only save non-default settings 
                WidreqOptions.append({'Name':Option, 'Value':Current, 'Extra':Extra})
        Result['Options'] = WidreqOptions        
        #Gather info about bindings
        Temp = [X[1:] for X in self.Bindings]
        for J in range(len(Temp)):
            Temp[J] = {'Event':Temp[J][0], 'Handler':Temp[J][1], 'Component':Temp[J][2]}
        Result['Bindings'] = Temp
        #Gather info about pack options
        PackOptions = []
        for Option in self.PackOptions.keys():
            OptionType, Default, Current, Extra = self.PackOptions[Option] 
            if Default <> Current:
                #we only save non-default settings
                PackOptions.append({'Name':Option, 'Value':Current})
        Result['PackOptions'] = PackOptions
        return Result

    def Unregister(self):
        """
        Tell this widreq to unregister from the repository.
        
        This is useful mostly in the case where you create a new widreq but when you
            ask to add it to the repository the request is declined. If at that point
            you throw the widreq away, it is still registered with the repository and
            chewing up a repository name. Call this routine to have it unregister 
            before thowing it away.
        """
        if self.WRID <> None:
            Repo.Unregister(self.WRID)
            self.WRID = None

    def Rename(self,NewName):
        """
        Call this method to give the widreq a new name, or if it switches herds.
        
        You need to call this if the widreq moves to a new herd because each widreq has an
            editor which is registered with the repository as 'option edit for <widgetname>
            on <herdname>'. If the herd changes the edit needs to reregister with the
            repository or you can get repository user name conflicts, which leads to 
            nothing good.
        """
        #Change our name
        self.Name = NewName
        if self.FrameID == None:
            #Update the hint only for non-container widgets
            if self.OurHintHandler:
                #And only if it isn't None
                self.OurHintHandler.Text(NewName)
        #Update the name 'option'
        self.Options.SetCurrent('name',NewName)
        #Any editors we have will have to re-register
        if hasattr(self,'OptionEditor'):
            self.OptionEditor.Register(NewName)
        if hasattr(self,'BindEditor'):
            self.BindEditor.Register(NewName)
        if hasattr(self,'PackEditor'):
            self.PackEditor.Register(NewName)
        if self.WRID == None:
            #We need to register with the repository. Although we register on creation, when we get
            #    relocated from one herd to another we get 'deleted' from the original herd which
            #    prompts us to unregister from the repository. Then we get reborn, all attributes
            #    intact, in the new herd. It's sort of celestial experience but we still need to 
            #    register again with the repository.    
            self.WRID = Repo.Register(self.WRID_NameFetch())
            assert self.WRID <> None, 'Signup with repository unexpectedly failed'
            Repo.Bind(self.WRID, 'WidreqDeleteNotify', self.on_WidRepNotify)
        else:    
            #Were already signed up, just make sure our registration name is correct
            R = Repo.Rename(self.WRID, self.WRID_NameFetch())
            if R <> 1:
                print R
                raise Exception, 'Rename with repository unexpectedly failed (%s)'%self.WRID_NameFetch()
        #We need to rebind in either case, since we may now be in a different herd        
        Repo.Bind(self.WRID, 'WidreqDeleteNotify', self.on_WidRepNotify)
        
    def on_WidRepNotify(self, Event, A, B):
        """
        We are being notified of a repository event.
        
        Note that newly created widreqs aren't added to the repository for the first time
            until they are dropped somewhere. If they are dropped in the middle of nowhere
            then they are NEVER added to the repository and they evaporate on drop.
        """
        if Event == 'WidreqDeleteNotify':
            if A == self.Name:
                #AGG that's us! Unregister from the repository.
                Repo.Unregister(self.WRID)
                self.WRID = None
        elif Event == 'HerdRenameNotify':
            if A == self.PresentHome:
                #Our home is being renamed
                self.PresentHome = B
                #Rename will update our repo stuff
                self.Rename(self.Name)
        else:
            print 'WidReq %s: unhandled repository event %s'%(self.Name,Event)        

    def dnd_end(self, Target, Event):
        ##D('dnd_end: PresentHome=%s'%self.PresentHome)
        if self.PresentHome == None:
            #We are headed for oblivion
            if self.WRID <> None:
                #If were still registered with the repository then un-register. This happens
                #    when a newly created widreq (which is registered with the repository as
                #    a user but is not yet added to the repository as a widreq) is dropped in
                #    the middle of nowhere.
                Repo.Unregister(self.WRID)
                self.WRID = None
        elif self.PresentHome == 'the Parking Lot':
            #Dropped on the parking lot, no action necessary.
            pass
        else:
            #We were dropped on a form. 
            #Make a list of handlers which we refer to that don't exist.
            FI = Repo.FetchForm(self.PresentHome)
            if FI['Type'] <> 'Tkinter.Toplevel' and self.WidgetName == 'MainMenuBar' and self.ModuleName == 'Pmw':
                #We were dropped on a non-Toplevel form and we are a Pmw.MainMenuBar
                if Repo.ModuleName <> Cfg.Info['ProjectName'] or self.PresentHome <> Cfg.Info['ProjectName']:
                    #And were not the main form of the main module
                    Msg = ("Warning warning Will Robinson. I'm a Pmw.MainMenuBar and you just dropped me on a "
                        "form which is neither a Toplevel nor the main-form of the main-module. Chances "
                        "of anything good coming of this are low. No actual harm has happened but I really make "
                        "sense only on a toplevel form, not on a frame-based form other than the main-form.")
                    Rpw.MessageDialog(Message=Msg,Help='Wid.MainMenuBar.BadDrop')
                    
            MissingHandlerDict = {}
            BindingCount = 0
            CommandCount = 0
            HandlerList = self.HandlersList(Verbose=True)
            for HandlerName,Reference in HandlerList:
                if self.HandlerFind(HandlerName) == '':
                    #Handler not found
                    MissingHandlerDict[HandlerName] = None
                    if Reference[0] == '<':
                        BindingCount += 1
                    else:
                        CommandCount += 1    
                        
            MissingHandlerList = MissingHandlerDict.keys()                
            if MissingHandlerList:
                TotalCount = CommandCount + BindingCount
                BothFlag = CommandCount > 0 and BindingCount > 0
                HandlerCount = len(MissingHandlerList)
                Msg = ("Hi, widget %s here. You just moved me from the parking lot and dropped me on"        
                    " form %s. I have "%(self.Name,self.PresentHome))
                H1 = ''    
                if BindingCount > 0:
                    H1 += rpHelp.Plural('%s &binding{/s} ',BindingCount,DoCap=False)
                if BothFlag:
                    H1 += 'and '
                if CommandCount > 0:
                    H1 += rpHelp.Plural('%s &command option{/s} ',CommandCount,DoCap=False)
                Msg += H1.replace('&','')    
                Msg += rpHelp.Plural('which refer{s} to ',TotalCount,DoCap=False)
                Msg += rpHelp.Plural("%s event handler{/s} that {doesn't/don't} exist in ",HandlerCount,DoCap=False)
                Msg +='%s. '%self.PresentHome
                Msg += rpHelp.Plural("You can delete the reference{0/s} to the handler{1/s} or you can elect to "
                    "create {1an} empty handler{1/s}. Press Help for full details.",(TotalCount,HandlerCount))
                Buttons = ((rpHelp.Plural('Create handler{/s}',HandlerCount),None)
                          ,(rpHelp.Plural('Delete reference{/s}',TotalCount),1))
                MissingHandlerList.sort()          
                PrettyHandlers = HelpListPretty(MissingHandlerList)
                HelpTuple = ('widget.drop.missing.handlers',(H1,PrettyHandlers,HandlerCount,TotalCount
                    ,self.Name,self.PresentHome))
                R = Rpw.MessageDialog(Message=Msg,Buttons=Buttons,Help=HelpTuple).Result
                if R == 1:
                    #User wants to delete references
                    for HandlerName in MissingHandlerList:
                        self.HandlerDeleteNotify(HandlerName)

                    #Have the current option/bind/pack editor refresh itself if needed.                
                    GblLayout.TheWidgetator.EditorRefresh()                
                else:
                    #User wants to create handlers.
                    for H in MissingHandlerList:
                        self.HandlerEnsure(H)                        
                    
        DND.Dragged.dnd_end(self, Target, Event)
    
    def WRID_NameFetch(self):
        """
        Return the name under which we wish to be known to the repository
        """
        Result = 'Widget %s on %s'%(self.Name, self.PresentHome)
        ##D('Result=%s'%Result)
        return Result

    def CreationList(self,Source):
        """
        Return a list of options that need to be set at our creation.
        
        The result is a list of 2-tuples giving the name and value for the option.
            The result is sorted by name.
            
        "Source" is the dictionary we work from: either "self.Options" or
            "self.PackOptions".            
        """
        Result = []
        NameList = Source.keys()
        for Name in NameList:
            Data = Source[Name]
            if Name in ('name','pyclass'):
                #The name and pyclass fields are for internal use only.
                continue
            Type,Default,Current,Extra = Data
            if Intify(Default) <> Intify(Current) or Type=='datatype':
                #This option differs from the default; must specify
                #Dots are replaced with underscores to make Pmw happy
                FudgedName = Name.replace('.','_')
                #We allow dashes in option names to disambiguate names which would otherwise
                #    be the same (eg Pmw.ScrolledCanvas has both a borderframe option and a
                #    borderframe component) but we delete them here to get the proper name.
                FudgedName = FudgedName.replace('-','')
                #Command option is special
                if Type in ('command','cvar'):
                    #Value of command/cvar is self + the actual name of the command, no quotes
                    Result.append((FudgedName,'self.%s'%Current))
                elif Type == 'pmwdatatype':
                    #Datetype needs special processing
                    if Current == 'integer':
                        #Integer requires nothing special
                        continue
                    elif Current == 'real':
                        if Extra[0] == '.':
                            #Standard separator case
                            Value = '"%s"'%Current
                        else:
                            #Special separator case
                            Value = '{"counter":"%s","separator":"%s"}'%(Current,Extra[0])
                    elif Current == 'time':
                        if Extra[0] == ':':
                            #Standard separator case
                            Value = '"%s"'%Current
                        else:
                            #Special separator case
                            Value = '{"counter":"%s","separator":"%s"}'%(Current,Extra[0])
                    elif Current == 'date':
                        if Extra == '/ymd':
                            #Standard case
                            Value = '"date"'
                        else:
                            #Special case
                            Value = '{"counter":"date"'
                            if Extra[0] <> '/':
                                Value += ',"Separator":"%s"'%Extra[0]
                            if Extra[1:] <> 'ymd':
                                Value += ',"format":"%s"'%Extra[1:]
                            Value += '}'
                    elif Current == 'dictionary':
                        Value = Extra
                    else:
                        raise Exception, 'Unexpected pmwdatetype Current=%s'%Current    
                    Result.append((FudgedName,Value))                                
                elif Type in ('verbatim','pyclass'):
                    #Verbatim is just what it says, the users text as-is
                    #Pyclass needs to be not in quotes
                    Result.append((FudgedName,Current))    
                else:
                    """
                    #For all others we present them unqouted if they are int or floats, otherwise
                    #    inside quotes.
                    """
                    try:
                        #Attempt integer
                        int(Current)
                        Result.append((FudgedName,'%s'%Current))        
                    except ValueError:
                        #It's not an int, try float
                        try:
                            float(Current)
                            Result.append((FudgedName,'%s'%Current))
                        except ValueError:
                            #It's not float either, give up and use quoted string
                            Result.append((FudgedName,"'%s'"%Current))
                    except TypeError:
                        #It's not even a string (fonts are tuples)        
                        Result.append((FudgedName,"%s"%str(Current)))
                        
        Result.sort()        
        return Result

    def BindCode(self,Indent,Wrap):
        """
        Return the text needed to create bindings for the widget.
        
        "Indent" is the minimum number of spaces at the start of each line.
        
        "Wrap" We wrap lines which would be longer than this.
        
        The result is a string with embedded newlines.
        """
        Result = []
        for Decomposed,Event,Handler,Component in self.Bindings:
            if self.IsForm():
                #If we *are* the from then bind is against just "self"
                Temp = ['self']
            else:
                #Otherwise we are a widget of the form and we bind against self.us
                Temp = ['self.%s'%self.Name]
            Comp = Component
            if Component <> '':
                Comp = ''
                for C in Component.split('.'):
                    Temp.append(".component('%s')"%C)
            Temp.append(".bind('%s'"%Event)    
            Temp.append(",self.%s)"%Handler)
            OneLine = (Indent*2)*' '
            for T in Temp:
                if len(OneLine) + len(T) > Wrap:
                    Result.append(OneLine+' \\')
                    OneLine = (Indent*3)*' '
                OneLine += T
            Result.append(OneLine)        
        return '\n'.join(Result)    

    def PackCode(self,Indent,Wrap,Side):
        """
        Return the text needed to pack the requested widget.
        
        "Indent" is the minimum number of spaces at the start of each line.
        
        "Wrap" We wrap lines which would be longer than this.
        
        "Side" The pack side. One of "top", "bottom", "left", "right". This is specified
            as an agrument because it is computed by Rapyd, not set by the user.

        """
        #MainMenuBars don't get packed.
        if self.WidgetName == 'MainMenuBar':
            return ''
        Result = ['%sself.%s.pack('%((Indent*2)*' ',self.Name)]
        CL = self.CreationList(self.PackOptions)
        CL.append(('side',"'%s'"%Side))
        CL.sort()
        TheComma = ''
        for Name,Current in CL:
            Text = "%s%s=%s"%(TheComma,Name,Current)
            TheComma = ','
            if len(Result[-1]) + len(Text) > Wrap:
                #line would be too long, start another line
                Result.append(((Indent*3)*' ')+Text)
            else:
                #line length ok, append the current text
                Result[-1] += Text    
        Result[-1] += ')'        
        return '\n'.join(Result)

    def CreationCode(self,Master,Indent,Wrap,IsMainForm=False):
        """
        Return the text needed to generate the requested widget.
        
        "Master" is the name of the master of our widget.
        
        "Indent" is the indent factor.
        
        "Wrap" We wrap lines which would be longer than this.
        
        "IsMainForm" is true if we are located in the main form of the main module. We need to
            know this to properly generate code for Pmw.MainMenuBar.
        """
        Result = []
        #if Master <> 'self':
        #    Master = 'self.'+Master
        #If any cvars need to be generated do so now
        for Key in self.Options.keys():
            Info = self.Options[Key]
            Type,Default,Current,Extra = Info
            if Type == 'cvar' and Default <> Current:
                #Extra: '<allowed types>.<auto/man flag><requested type>'
                Allowed,Stuff = Extra.split('.')
                assert len(Stuff) == 2
                AutoMan,CvarType = Stuff
                assert AutoMan in 'am'
                assert CvarType in 'sif'
                if AutoMan == 'a':
                    #We are to generate this cvar automatically
                    LoadType = Cfg.Info['Modules']['Tkinter']['ImportType']
                    assert LoadType in ('import','from'),LoadType
                    Prefix = {'from':'','import':'Tkinter.'}[LoadType]
                    T = {'s':'String','i':'Int','f':'Double'}[CvarType]
                    Result.append('%sself.%s = %s%sVar()'%((Indent*2)*' ',Current,Prefix,T))
        #            
        #Generate basic creation code        
        #
        # Master is almost always 'self', however for a MainMenuBar on the main form of the main module
        #     the base is 'Root'.
        if IsMainForm and self.ModuleName == 'Pmw' and self.WidgetName == 'MainMenuBar':
            Master = 'Root'
        WidgetInfo = Cfg.Info['Modules'][self.ModuleName]['Widgets'][self.WidgetName]
        LoadType = Cfg.Info['Modules'][self.ModuleName]['ImportType']
        assert LoadType in ('import','from')
        Temp = '%sself.%s = '%((Indent*2)*' ',self.Name)

        #The current value of the pyclass option is what we need to emit to create an instance
        Type, Default, Current, Extra = self.Options['pyclass']

        if LoadType == 'import' and Default==Current:
            #If using "import" form then prepend the name of the donor module UNLESS the user has
            #    specified a non-standard pyclass in which case it's up to them to mention a 
            #    donor module should that be necessary.
            Temp += '%s.'%WidgetInfo['Module']

        Temp += '%s(%s'%(Current,Master)
        Result.append(Temp)
        #Generate any non-default options
        CL = self.CreationList(self.Options)
        for Name,Current in CL:
            Text = ",%s=%s"%(Name,Current)
            if len(Result[-1]) + len(Text) > Wrap:
                #line would be too long, start another line
                Result.append(((Indent*3)*' ')+Text)
            else:
                #line length ok, append the current text
                Result[-1] += Text    
        Result[-1] += ')'        
        return '\n'.join(Result)
        
    def WhereCenter(self):
        """
        Return (X,Y) tuple giving location of center of this widreq icon on canvas.
        """    
        X = self.X + (self.Icon.width()/2)
        Y = self.Y + (self.Icon.height()/2)
        return (X,Y)

    def PlaceOnCanvasCenter(self,Canvas,XY,IsSelected=1):
        """
        Have this widreq appear on Canvas centered on XY.
        """
        XY[0] -= self.Icon.width()/2
        XY[1] -= self.Icon.height()/2
        self.Vanish()
        #draw ourself on the new canvas. Since we are being placed arbitrarily,
        #    we zero the offset.
        self.OffsetX = 0
        self.OffsetY = 0
        self.Appear(Canvas,XY,IsSelected=IsSelected)
        #bind to ButtonPress so user can drag us around
        self.Label.bind('<ButtonPress>',self.Press)
        #self.PlaceOnCanvas(Canvas,XY)

    def Appear(self, Canvas, XY,IsSelected=1):
        """
        Put an label representing this Dragged instance on Canvas.
        
        XY says where the mouse pointer is. We don't, however, necessarily want
            to draw our upper left corner at XY. Why not? Because if the user
            pressed over an existing label AND the mouse wasn't exactly over the
            upper left of the label (which is pretty likely) then we would like
            to keep the mouse pointer at the same relative position inside the
            label. We therefore adjust X and Y by self.OffsetX and self.OffseY
            thus moving our upper left corner up and/or left by the specified
            amounts. These offsets are set to a nominal value when an instance
            of Dragged is created (where it matters rather less), and to a useful
            value by our "Press" routine when the user clicks on an existing
            instance of us.
            
        We override this method of dragged so we can pass along IsSelected.    
        """
        if self.Canvas:
            #we are already on a canva
            self.Vanish()
        self.X, self.Y = XY    
        self.X -= self.OffsetX
        self.Y -= self.OffsetY

        #Note the canvas on which we will draw the label.
        self.Canvas = Canvas
        
        #Create a label which identifies us, including our unique number
        self.Label = self.WidgetShow(None,Canvas,IsSelected=IsSelected)
        #Adjust position, if needed, so our label doesn't fall partly off the canvas
        self.LabelContain()
        #Display the label on a window on the canvas. We need the ID returned by
        #    the canvas so we can move the label around as the mouse moves.
        self.ID = Canvas.create_window(self.X, self.Y, window=self.Label, anchor="nw")
    
        #If canvas has an ObjectDict, then make sure we are listed in it
        if hasattr(self.Canvas,'ObjectDict') and type(self.Canvas.ObjectDict) == type({}):
            self.Canvas.ObjectDict[self.Name] = self

    def on_Help(self,Event):
        """
        User clicked for help over this widreq.
        """
        if self.PresentHome == GblParkingLotName:
            Home = '&parking lot, although I am a little nervous since the ' \
                "parking lot is right next to the &trash bin which scares the hell out of me; " \
                "widgets have vanished in that thing"
        else:
            Home = 'the &layout area in form %s'%self.PresentHome        
        if Repo.FetchSelected() == self.Name and Repo.SelectedHerd == self.PresentHome:
            Msg = "Right now {bI'm} the selected widget, so that's all about me you are " \
                "seeing off to the left in the &widgetator. You can tell I'm the selected " \
                "widget because I've got this cool border around me and that's my name " \
                "in the &selector in the upper left corner where it says 'Widget: %s'. " \
                "I just {ilove} seeing my name in lights."%self.Name
        else:
            Msg = "Sadly, I'm not currently the selected widget but if you were to left " \
                "click on me then I {iwould} be the selected widget. You could also " \
                "select me by chosing my name from the &selector in the upper left " \
                "corner. The information you are currently seeing way over to the left " \
                "in the &widgetator " \
                "is about stupid old %s on %s but if you were to select {bme} the you " \
                "could see all my infomation. Just a thought." \
                %(Repo.FetchSelected(),Repo.SelectedHerd)
        
        Help('widget.instance',[self.Name, self.WidgetName, Home, Msg, self.ModuleName])

    def IsForm(self):
        """
        Return True if this widreq is the top level container of a form, else False.
        """
        return self.FrameID == (0,)

    def InBox(self,Box):
        """
        Return True if we are a containee and inside the specified bounding box.
        
        "Box" is a 4-tuli bounding box.
        """
        ##D('InBox: Name=%s FrameID=%s'%(self.Name,self.FrameID))
        if self.FrameID <> None:
            #we are a container widget
            return False
        if self.X == None:
            #We haven't been placed yet.
            return False    
        if self.X >= Box[0] and self.Y >= Box[1] and \
            self.X <= Box[2] and self.Y <= Box[3]:
            return True
        return False    
                
    def WidgetShow(self, Widget, Parent=None, IsSelected=1):
        """
        Arrange for a Widget to represent this instance of WidReq.
        
        If Widget is "None", then create one, on "Parent", and return it as
            the result. 
        
        If Widget is not "None" it will be a widget, previously created by
            this method, which should be set so it displays our proper
            representation. In this case, "Parent" need not be given.
            
        If "IsSelected" is true then we make the widget conspicuously visible;
            otherwise we draw it normally.    
        """
        #D('WidgetShow: Name=%s FrameID=%s Parent=%s IsSelected=%s'
        #    %(self.Name,self.FrameID,Parent,IsSelected))
        if Parent <> None:
            self.FrameParent = Parent
        if self.FrameID <> None:
            #We are a container widget (Frame or Toplevel)
            #This is a container widget
            if IsSelected:
                self.FrameParent.FrameMark(self.FrameID)            
            else:
                pass
            Result = None    
        else:
            #This is a containee widget            
            if Widget == None:
                #we need to create one from scratch
                Result = Label(Parent)
                #Our hint is our name
                self.OurHintHandler = rpHelp.HintHandler(Result,self.Options['name'][2])
                #Bind help to our representation
                Result.bind(HelpButton,self.on_Help)
            else:
                Result = Widget    
            #set it's attributes appropriately    
            Result['image'] = self.Icon
            if IsSelected:
                #We are the selected widreq
                Result['relief'] = RIDGE
                Result['borderwidth'] = 4
                #Since we are a selected non-frame widreq, erase any frame-widreq
                #    selection mark. We check for attribute FrameMark, since the
                #    parking lot doesn't have this capability.
                if hasattr(self.FrameParent,'FrameMark'):
                    self.FrameParent.FrameMark(None)
                    self.FrameParent.update_idletasks()    
            else:
                #We are not the selected widreq
                Result['relief'] = FLAT
                Result['borderwidth'] = 4
        return Result
        
    def WidgetHide(self, Widget):    
        """
        Arrange for Widget to be invisible.
        
        Widget will have been previously created by method WidgetShow. On
            exit from this method Widget should still exist on the canvas
            but it should be invisible, ie, no text, no image, no border.
        """
        Widget['image'] = ''
        Widget['relief'] = FLAT
        Widget['borderwidth'] = 0

    def Press(self, Event):
        """
        User clicked on this widreq.
        
        We override this method so, before starting a dnd operation, we query the
            repository to see if everybody is ok with us selecting ourself.
            If the result we receive is false, we don't start the
            dnd operation.
        """
        #Being pressed implies that we are being selected. Ask the repository
        #    to select us.
        if Repo.SelectedHerd <> self.PresentHome:
            #Our herd is not currently selected; ask for it
            R = Repo.Request(self.WRID, 'HerdSelect', self.PresentHome)
            if R <> 1:
                #The selection was denied; no dnd for us
                return        
        R = Repo.Request(self.WRID, 'WidreqSelect', self.Name)
        if R == 1:
            #Selection went well, start the drag-and-drop process
            DND.Dragged.Press(self,Event)

class Layout(MenuAids):
    """=m
    The Layout area.

    A fair bit of what goes on in the Layout involves Widget Requests (WidReqs), so
        lets talk a little about them.
    
    *Creation* Widreqs spring into existence when the user clicks on a button in the
        WidgetBuffet. That activates "<Layout.on_BuffetPress>" which runs a request
        past the repository (to make sure nobody objects to creating a new widreq
        now) but doesn't actually add a new widreq to the repository. If anybody
        objects (eg There is an open widreq with invalid option data) then the creation
        of a new one is abandoned. If no one objects, we create a WidReq instance named 
        "__NewWidreq__" which is handed off to drag-n-drop. At this point the widreq is 
        of no fixed address and it's "PresentHome" attribute is "None".
        
        There are four possible locations where the user might drop such a newly
            minted widreq:
        o The current form's GuiEditor canvas. The GuiEditor will assign the widget
           some innocuous name ('button5') and register it with the repository.
        o The Parking Lot. The lot will assign the widges some similarly innocuous
           and will register it with the repository.
        o The Trash Bin. The Bin does nothing which causes the WidReq to evaporate.
        o Anywhere else. The widreq is not accepted and evaporates.

    *Moving* Moving a widreq within it's current form is reasonably straightforward.
        In general dragged objects bind themselves to button-1-press. Widreqs override
        the "on_Press" method so when a user clicks on a widreq, the widreq itself
        posts a repo request to select itself. If the selection fails, nothing further
        happens. If it succeeds then the widreq initiates the drag and drop process.
        
    Moving a widreq onto another another form (ie from to parking lot or vice versa)
        is more complex. If the widreq's name duplicates a name on the target canvas
        then the canvas selects the widreqs current herd, renames it, switches back to
        the current herd and notifies the user. Once the name is looked after, the
        target canvas has the repository relocate the widreq to the target forms herd
        (and this itself is quite a song and dance, documented in the repository).
        
    *Deletion* There are three ways in which widreqs can expire:
        o The user can drop them on the trash bin. The trasn bin's "dnd_commit" method
           deletes the widreq from the repository, sets the widreqs "PresentHome"
           to "None", and calls the widreq's "Vanish" method to have it undraw itself.
           When the widreqs "dnd_end" method is called it notices that it is homeless
           (a sure fire indication that it is headed for the bone yard) and unregisters
           from the repository. The widreq then evaporates. 
           
          Note that a widreq is both an object held in the repository AND it is a registered
            user of the repository. These two functions are separate and distinct, hence the
            widreq has to be deleted from the repository AND it has to unregister itself as
            a respository user. Although the widreq may have been deleted from the repository,
            it will still hang around a bit until the last reference to it is gone.
            
        o The frame in which the widreq is located can be deleted. This is handled by the
           "on_Button3Down" method of "GuiEditor". Having confirmed with the user it simply
           does a "WidreqDelete" request to the repository against the widreq(s) to be
           deleted. Anybody who cares is bound to the "WidreqDeleteNotify" repository event.
           People who care include:
           o The Widgetator. It tells the widreq to undraw itself. And it tells the widreqs
              option editor to unregister itself. This particular task falls to the
              Widgetator mostly because it was the one who created the editor in the first
              place. 
           o The widreq itself sees the delete notify and unregisters itself from the repository.      
           
        o The form in which the widreq is located can be deleted. This action is handled by
           the "FormDelete" method of "LayoutArea" but in principle works just like deletion
           from the frame.   
        
    "BuffetTabInfo" is a dictionary of information relating to the widget buffet. The key is
        the name of the widget buffet tab. Each value is a dictionary thus:
        o "['ButtonBar']" The sliding button bar widget for this tab.

    Each form has in the repository a form entry which is a dictionary of form related
        information thus:        
        o "['BaseClass']" The class from which this frame is derived, This will be
          Toplevel, Frame, or some other class which itself is derived from Toplevel
          or Frame.    
        o "['Gui']" The layout gui for this form. The main text area isn't actually a
            form and hence this entry is None in that case.
        o "['NoteBookSize']" A tuple giving the size of the PageFrame the last time this
            form was resized. If we select this form and this value differes from the
            current size of the notebook, we know we need to resize the form.
        o "['OnTab']" A boolean indicating if this form is currently represented by a tab
            in the layout area.    
        o "['Requested']" Either "'Gui'" or "'Text'", indicating which editor is the one
            currently requested by the user.    
        o "['Text']" The text editor for this form. "None" if no text editor has been created
            for it yet.
        o "['Type']" "Toplevel" or "Frame", indicating the type of class from which this frame
            is being ultimately derived.    
            
    Each TabbedFrame tab is given an arbitrary name of the form "Tnnn", where nnn is a three
        digit number and the first tab created is "T000". I initially tried
        using the name of the form as the name of the tab. Unfortunatly Pmw doesn't
        allow the use of underscore in tab names. Since I didn't want to have to
        disallow underscores in form names we now use arbitrary names for the tabs.
        The dictionary "self.TabToForm" allows easy conversion from tab number to form
        name: the key is the name of the tab (eg "T000") while the value is a string
        giving the name of the corresponding form (eg "Form1"). Going the other
        way, there is a "TabName" entry for each form in "TabInfo".
        
    On detecting when a project has changed. 
    
        There are times when we would like to know if the user has made changes to a project
        so we can offer to save it form them before losing changes, eg prior to exiting or
        to loading another project. The question is how best to note a changed project. a
        project can consist of many modules each of which consists of many forms and there
        are a variety of ways of changing a form. At project save time we bag up the entire
        project into a list which we pickle to disk. Then we prune out the text from the
        forms, while keeping an SHA checksum of each forms text; this is stored in
        GblLastSavedProject. We detect a changed project by comparing a gathered and pruned 
        copy of the current project with GblLastSavedProject.
        


    At save time a project is gathered into a list and that list 
        is pickled to disk.  Here we describe the details of that list.
    
    The first element of the project list is a 
        <preamble-descriptor> while all subsequent elements are 
        <module-descriptors>.
    
    <preamble-descriptor> dictionary
        ID: "Rapyd Project"
        Geometry: The top-level project window geometry at the 
            time the project was saved.
        ProjectName: The name (no extension) under which the 
            project is stored. Also the name of the main module 
            of the project.
        ModuleCurrent: The name of the module which was selected 
            when the project was saved.
        ModulePrevious: The name of the previously selected 
            module at the time the project was saved.
        Version: Currently "0".
        ParkingLot: a <parking lot descriptor>
        ImportTypes: A list of tuples, where each tuple is:
            [0] Name of widget supplying module (eg Tkinter, Pmw)
            [1] Import type, eg "from" or "import"
            We need this information at project load time to see 
            if the import types given in the config-file are 
            different from those in effect the last time the 
            project was built. If so we have to regenerate the 
            creation code of each form.
        EditorWidths: A tuple of length three. Each element is
            a 2-list giving the width settings of the option, bind
            and pack editors respectivly.

    
    <module-descriptor> dictionary
        Name: The name of this module.
        -Main-: A <text-descriptor> of the main form code.
        SelectedForm: The name of the selected form or "None" if 
            no form was selected.
        VisibleForm: The name of the currently visible form tab, 
            or None if no forms are on tabs. Note that the 
            SelectedForm and the VisibleForm are often but not 
            always the same. For example it is possible for Form1
            to be visible but "The Parking Lot" to be the selected 
            form.
        PreviousForm: The name of the previous visible form or
            None if there is no previous form.
        OnTab: Boolean indicating if the -Main- text area was on
            a tab at save time.    
        Forms: list of <form descriptors>
    
    
    <parking lot descriptor> dictionary
        SelectedWidreq: The name of the selected widreq or "None".
        Widreqs: A list of <widreq-descriptors>
        
    
    <form-descriptor> dictionary
        BaseClass: The name of the class from which this form 
            derives. Generally either Frame or TopLevel but users 
            are allowed to derive from other classes which should 
            themselves either derive from Frame or Toplevel or 
            from a class with equivalent functionality.
        Lines: list of <line-descriptors>
        Name: The name of this form.
        OnTab: A boolean indicating if this form was showing on a 
            tab at save time.
        Requested: Either "Gui" or "Text" indicating which editor 
            was most recently requested by the user.
        SelectedWidreq: The name of the currently selected widreq 
            or "None" if no selected widreq.
        Text: A <text-descriptor> for the code of this form.    
        Type: Either "Frame" or "Toplevel", indicating the nature 
            of the class from which we are deriving. If the 
            BaseClass is Frame or Toplevel then this will be the 
            same. If the base class is something else, then this 
            indicates the type of functionality we expect the base 
            class to provide.
        Widreqs: list of <widreq-descriptors>
    
                
    <line-descriptor> tuple
        [0] X location in generic coordinates, a 10,000 x 10,000 
            grid.
        [1] Y location.
        [2] Dirn 0 => horizontal, 1 => vertical
        
        
    <text-descriptor> dictionary
        Version: Currently "1.0"
        Cursor: The location of the insert cursor at save time.
        Sha: a 40 byte string containing the sha hex digest of 
            the text.
        Text: a list of text chunks alternating systext, usertext. 
            If the first chunk is emtpy then the first character 
            of text is usertext.
    
    
    <widreq-descriptor> dictionary
        Name: The name for this widget instance, eg "MyButton"
        ModuleName: The name of the module from which this widget 
            is imported. eg Tkinter.
        WidgetName: The type of widget, eg "Button"
        XY: a 2-tuple giving the XY location of the widreq in 
            generic coordinates. For frame and toplevel widgets 
            this is (0,0). Generic coordinates work on a 10,000 
            x 10,000 grid.
        Options: a list of <option-descriptors>
        Bindings: a list of <binding-descriptors>
        PackOptions: a list of <pack-descriptors>
        
        
    <option-descriptor> dictionary
        #Note that only those options whose value differs from 
        #   the default value  are listed. Options whose value 
        #   equals the default do NOT appear here.
        Name: The name of the option
        Value: The present value of the option
        Extra: Any extra information needed for this option. Most 
            options don't need extra information in which case 
            this is "None"
    
               
    <binding-descriptor> dictionary
        Event: The event string, eg "Button-Release-1"
        Handler: The name of the event handler, 
            eg "on_MyButton_ButRel1"
    
        
    <pack-descriptor> dictionary
        #Note that only those pack options whose value differs 
        #   from the default value are listed. Options whose 
        #   value equals the default do NOT appear here.
        Name: The name of the pack option
        Value: The value of the pack option              


    #=e Event Handlers
    #=f Form Related    
    #=h Help
    #=m Main Menu   
    #=p Published methods
    #=t Tab related 
    """
    
    def __init__(self, _Win, InitialProject):
        """
        Create the layout area.
        """
	self.SeparatorCounter = 0
        self._Win = _Win
        self.ApplicationTitleSet()
	self._Win.title("     Rapyd-TK  Version %s     "%VersionNumber)
	self._Win.geometry('+20+100')
        self._WinSize = (1,1)
        #This gives us control if the user closes us via the window manager
        self._Win.protocol("WM_DELETE_WINDOW",self.on_ActionExit)
        
        #Register with the widreq repository
        self.WRID = Repo.Register('Layout area')
        
        #--- the widgetator on the left ---
        self.TheWidgetator = Widgetator(self._Win)
        self.TheWidgetator.pack(side=LEFT,fill=Y,anchor=W)

        #
        #--- the main menu ---
        #
        self.MenuBarFrame = Frame(self._Win,borderwidth=2,relief=RAISED)
        self.MenuBarFrame.pack(side=TOP, fill=X)
        #-----------------------------------------------------------------------
        # File    
        #-----------------------------------------------------------------------
        self.FileButton = Menubutton(self.MenuBarFrame,text=' Project ',pady=0)
        self.FileButton.pack(side=LEFT) 
        self.FileButton.bind(HelpButton,self.on_ActionProjectHelp)
        self.FileButton.bind('<1>',self.on_ProjectClick)
        

        self.FileMenu = Menu(self.FileButton,tearoff=0)
        self.ActionMenuSetup()
        
        self.ActionMenuAdd('Load Project','ProjectLoad')
        self.ActionMenuAdd('Save Project','ProjectSave')

        self.ActionMenuSep()
        self.ActionMenuAdd('Rename Project','ProjectRename')
        
        self.ActionMenuSep()
        self.ActionMenuAdd('New Project','ProjectNew')
        
        self.ActionMenuSep()
        self.ActionMenuAdd('Build Project','ProjectBuild')
        self.ActionMenuAdd('Build + Run','ProjectBuildRun')
        self.ActionMenuAdd('Save + Build','ProjectSaveBuild')
        self.ActionMenuAdd('Save + Build + Run','ProjectSaveBuildRun')
        self.ProjectInfoIndex = self.ActionMenuAdd('Project Info')
        
        self.ActionMenuSep()
        self.ActionMenuAdd('Exit')
        
        self.ActionMenuSep()
        self.ActionMenuAdd('Help on projects','ProjectHelp')
        
        self.ActionMenuGenerate(self.FileMenu)
        self.FileButton.config(menu=self.FileMenu)
        #-----------------------------------------------------------------------
        # Module
        #-----------------------------------------------------------------------
        self.ModuleButton = Menubutton(self.MenuBarFrame,text=' Modules ',pady=0)
        self.ModuleButton.pack(side=LEFT) 
        self.ModuleButton.bind(HelpButton,self.on_ActionModuleHelp)
        self.ModuleButton.bind('<1>',self.on_ModuleClick)

        self.ModuleMenu = Menu(self.ModuleButton,tearoff=0)
        self.ActionMenuAdd('Select Module','ModuleSelect')
        self.ActionMenuAdd('Module alternate')
        self.ActionMenuAdd('Module next')

        self.ActionMenuSep()
        self.ActionMenuAdd('Add new module to project','ModuleNew')
        self.ActionMenuAdd('Rename the current module','ModuleRename')

        self.ActionMenuSep()
        self.ModuleDeleteIndex = self.ActionMenuAdd('Delete the current module','ModuleDelete')

        self.ActionMenuSep()
        self.ActionMenuAdd('Help on modules','ModuleHelp')
        
        self.ActionMenuGenerate(self.ModuleMenu)
        self.ModuleButton.config(menu=self.ModuleMenu)
        #-----------------------------------------------------------------------
        # Form
        #-----------------------------------------------------------------------
        self.FormButton = Menubutton(self.MenuBarFrame,text=' Forms ',pady=0)
        self.FormButton.pack(side=LEFT) 
        self.FormButton.bind(HelpButton,self.on_ActionFormHelp)
        self.FormButton.bind('<1>',self.on_FormClick)

        self.FormMenu = Menu(self.FormButton,tearoff=0)
        self.ActionMenuAdd('Swap code/layout','FormSwapCodeLayout')
        self.ActionMenuAdd('Form Alternate')
        self.ActionMenuAdd('Select forms to see','FormsSelect')
        
        self.ActionMenuSep()
        self.ActionMenuAdd('Add new form to module','FormNew')
        self.ActionMenuAdd('Import a form','FormImport')
        self.FormExportIndex = self.ActionMenuAdd('Export the current form','FormExport')
        
        self.ActionMenuSep()
        self.FormDeriveIndex = self.ActionMenuAdd('Set "derive from" class','FormChangeDerive')
        self.ActionMenuAdd('How to rename a form','FormRename')

        self.ActionMenuSep()
        self.FormDeleteIndex = self.ActionMenuAdd('Delete the current form','FormDelete')

        self.ActionMenuSep()
        self.ActionMenuAdd('Help on forms','FormHelp')

        self.ActionMenuGenerate(self.FormMenu)
        self.FormButton.config(menu=self.FormMenu)
        #-----------------------------------------------------------------------
        # Help
        #-----------------------------------------------------------------------
        self.HelpButton = Menubutton(self.MenuBarFrame,text=' Help ',pady=0)
        self.HelpButton.pack(side=LEFT) 
        self.HelpButton.bind(HelpButton,self.on_ActionHelpHelp)
    
        self.HelpMenu = Menu(self.HelpButton,tearoff=0)
        self.ActionMenuAdd('About')
        self.ActionMenuAdd('Main help page','HelpHelp')
        self.ActionMenuAdd('Search help index','HelpIndex')
        self.ActionMenuAdd('License','HelpLicense')
        
        self.ActionMenuGenerate(self.HelpMenu)
        self.HelpButton.config(menu=self.HelpMenu)

        #Create control vars that track the repository events we want to monitor
        self.RepoEventDebugCvar = {}
        for T in 'rqbu':
            self.RepoEventDebugCvar[T] = StringVar()
        #-----------------------------------------------------------------------
        # Debug
        #-----------------------------------------------------------------------
        if Cfg.Info['Debug']:
            self.DbugButton = Menubutton(self.MenuBarFrame,text=' Debug ',pady=0)
            self.DbugButton.pack(side=LEFT) 
    
            self.DbugMenu = Menu(self.DbugButton,tearoff=0)
            #self.DbugMenu.add_command(label='RepositoryDumpAll',command=self.Handler)
            self.DbugMenu.add_command(label='RepositoryDumpAll',command=Wow(self,'on_DebugRepo','UHB'))
            self.DbugMenu.add_command(label='RepositoryDumpUsers',command=Wow(self,'on_DebugRepo','U'))
            self.DbugMenu.add_command(label='RepositoryDumpHerds',command=Wow(self,'on_DebugRepo','H'))
            self.DbugMenu.add_command(label='RepositoryDumpBindings',command=Wow(self,'on_DebugRepo','B'))
        
            self.DbugMenu.add_separator()
        
            self.DbugMenu.add_checkbutton(label='Trace repository Register events',command=self.on_DebugRepoEvent
                ,variable=self.RepoEventDebugCvar['r'], offvalue='', onvalue='r')
            self.DbugMenu.add_checkbutton(label='Trace repository Request events',command=self.on_DebugRepoEvent
                ,variable=self.RepoEventDebugCvar['q'], offvalue='', onvalue='q')
            self.DbugMenu.add_checkbutton(label='Trace repository Bind events',command=self.on_DebugRepoEvent
                ,variable=self.RepoEventDebugCvar['b'], offvalue='', onvalue='b')
            self.DbugMenu.add_checkbutton(label='Trace repository Unbind events',command=self.on_DebugRepoEvent
                ,variable=self.RepoEventDebugCvar['u'], offvalue='', onvalue='u')
            self.DbugButton.config(menu=self.DbugMenu)
    
            self.DbugMenu.add_separator()
        
            self.DbugMenu.add_command(label='Print separator line',command=Wow(self,'on_DebugGen','separator'))
            self.DbugMenu.add_command(label='Print repository stats',command=Wow(self,'on_DebugGen','repo_stats'))
            self.DbugMenu.add_command(label='Print FormInfo',command=Wow(self,'on_DebugGen','print_forminfo'))
            self.DbugMenu.add_command(label='Print spanify info',command=Wow(self,'on_DebugGen','print_spanify'))
            self.DbugMenu.add_command(label='Print visible form',command=Wow(self,'on_DebugGen','print_visible'))
        # Module indicator
        self.ModuleIndicator = Label(self.MenuBarFrame)
        self.ModuleIndicator.pack(side=RIGHT,padx=10)    
        self.ModuleIndicator.bind(HelpButton,self.on_ModuleIndicatorHelp)
        self.ModuleNameUpdate()
        #
        #--- the widget buffet ---
        #
        self.Buffet = rpHelp.TabbedFrame(self._Win
            ,LowerCommand=self.on_BuffetLower
            ,RaiseCommand=self.on_BuffetRaise
            ,borderwidth=1
            ,relief=GROOVE
            ,TabsOn=BOTTOM )
        self.BuffetTabInfo = {}
        #
        #create each widget buffet tab per config information
        #
        #Build Temp, a list with one entry per tab, where each entry is a 3-tuple thus:
        #    [0] An integer showing the position of this tab in the Widget Buffet
        #    [1] The ID of this tab (ie the name of the module)
        #    [2] The caption text of this tab
        TempT = []
        Tabs = Cfg.Info['Tabs']
        for Key in Tabs.keys():
            #Create the tab
            TempT.append( [ Tabs[Key][0], Key, Tabs[Key][1] ] )
            
        TempT.sort() #so we get them in the desired tab order
        for TabIndex, TabID, TabText in TempT:
            Schema = [Cfg.Info['SbbIcons']]
            #find all widgets that wish to be on this tab
            #Built Temp, a list with one entry per widget that wants to be on this tab,
            #    where each entry is a tuple  thus:
            #    [0] An integer showing the position of this widget in this widget buffet tab
            #    [1] The name of the widget
            #    [2] The 'Icon_b' for this widget
            #    [3] The hint for this eidget
            Temp = []
            for WidgetName,WidgetInfo in Cfg.Info['Modules'][TabID]['Widgets'].items():
                if WidgetInfo['Tab'] == None:
                    #This widget (presumably Toplevel or Frame) is not on a tab
                    continue
                if WidgetInfo['Tab'][1] == TabID:
                    Temp.append( [ WidgetInfo['Tab'][0], WidgetName, WidgetInfo['Icon_b'], WidgetInfo['Hint'] ] )
            Temp.sort() #so we get the widgets in the requested order
            #print 'Temp=%s'%Temp
            for WidgetIndex, WidgetName, Icon_b, Hint in Temp:        
                #print WidgetInfo['Tab'], TabID
                SchemaLine = (WidgetName, Icon_b, None, Hint)
                Schema.append(SchemaLine)
            #Schema is built; add the tab            
            self.Buffet.Add(TabText)
            #Bind the tab to help
            TabComponent = self.Buffet.Tab(TabText)
            TabComponent.HelpTopic = 'Tab'
            TabComponent.bind(HelpButton,self.on_BuffetHelp)
            if len(Schema) > 1:
                #add a sliding button bar only if there are two or more buttons
                Page = self.Buffet.PageFrame()
                T = Rpw.SlidingButtonBar(Page,Schema,width=len(Schema)-1)
                self.BuffetTabInfo[TabText] = {'ButtonBar':T}
                #process the newly created buttons
                for I in range(len(T._Buttonlist)):
                    B = T._Buttonlist[I]
                    #Put the cannonical name of the widget in the button. By so doing, we can
                    #    find the name of the widget from inside an event handler.
                    B[1].DefaultName = Schema[I+1][0]
                    #Likewise for the name of the module from which this widget is drawn
                    B[1].DefaultModule = TabID
                    #All buffet buttons bind to the same handler for dragging and dropping.
                    B[1].bind("<ButtonPress>",self.on_BuffetPress)
                    B[1].bind(HelpButton,self.on_BuffetHelpWidget)
                #Bind help to the arrows
                T._ArrowLeft.HelpTopic='SlideArrow'    
                T._ArrowRite.HelpTopic='SlideArrow'    
                T._ArrowLeft.bind(HelpButton,self.on_BuffetHelp)
                T._ArrowRite.bind(HelpButton,self.on_BuffetHelp)
        #Select the first tab
        TabIndex, TabID, TabText = TempT[0]
        self.Buffet.Select(TabText)        
        #
        # The main layout-area notebook
        #
        self.LayoutNotebook = rpHelp.TabbedFrame(self._Win
            ,RaiseCommand=self.on_LayoutAreaRaise
            ,LowerCommand=self.on_LayoutAreaLower
            ,ReclickCommand=self.on_ActionFormSwapCodeLayout
            ,Sort=True)
        self.LayoutNotebook.SetHelpBinding(HelpButton,self.on_LayoutNotebookHelp)
        self.LayoutNotebook.pack(side=TOP,expand=YES,fill=BOTH)

        #
        # A frame at the bottom for the parking lot and the trash bin
        #
        self.LowerFrame = Frame(self._Win)
        self.Buffet.pack(side=BOTTOM,fill=X)
        self.LowerFrame.pack(side=BOTTOM,fill=X)

        #
        # the duplicator
        #
        self.DuplicatorSize = (50,50)
        self.Duplicator = Button(self.LowerFrame,bd=2,width=self.DuplicatorSize[0]
            ,height=self.DuplicatorSize[1],image=Cfg.Info['DuplicatorIcon'])
        self.Duplicator.pack(side=LEFT,anchor='e',expand=NO)
        self.Duplicator.HelpTopic = 'duplicator'
        self.Duplicator.bind('<Button-1>',self.on_DuplicatorPress)
        self.Duplicator.bind(HelpButton,self.on_KnownHelp)
        
        #
        # The parking lot
        #
        self.ParkingLotSize = (50,50)
        self.ParkingLot = ParkingLotEditor(self.LowerFrame,scrollregion=(0,0,self.ParkingLotSize[0]
            ,self.ParkingLotSize[1]),bd=2,relief=RAISED,DropTypes=['WidReq']
            ,width=self.ParkingLotSize[0],height=self.ParkingLotSize[1]
            ,herdname=GblParkingLotName,ourname='Visual Canvas')
        self.ParkingLot.pack(side=LEFT,anchor='e',expand=YES,fill=X)
        self.ParkingLot.HelpTopic = 'parking-lot.main'
        self.ParkingLot.bind(HelpButton, self.on_KnownHelp)

        #
        # The trash bin
        #
        self.TrashBinSize = (50,50)
        self.TrashBin = rpDndCanvasTrash(self.LowerFrame,scrollregion=(0,0,self.TrashBinSize[0]
            ,self.TrashBinSize[1]),bd=2,relief=RAISED,DropTypes=['WidReq']
            ,width=self.TrashBinSize[0],height=self.TrashBinSize[1]
            ,rapydname='The Trash Bin')
        self.TrashBin.pack(side=RIGHT,anchor='e',expand=NO,fill=X)
        self.TrashBin.HelpTopic = 'TrashBin'
        self.TrashBin.bind(HelpButton, self.on_KnownHelp)
        self.TrashBin.create_image(25,25,image=Cfg.Info['TrashIcon'])
        self.LayoutEditorPacked = None
        
        #--- if we get resized, the main notebook will need resizing ---
        self._Win.bind('<Configure>',self.on_Configure)
        #--- Make the initial project happen ---
        if InitialProject == None:
            #No initial project was specified; have user load, new or quit
            self.LoadOrNew('No project was specified on the command line. ',HelpTopic='startup.query')
        else:
            if not os.path.exists(InitialProject):
                Message='No file named "%s" was found.\n\n'%InitialProject
                H = "load.filenotfound"
                R = 2
                PossibleName = InitialProject
            else:    
                R = self.ProjectLoad(InitialProject)
                if R == 1:
                    Message = 'Loading of project "%s" was cancelled.\n\n'%InitialProject
                    H = 'load.cancelled'
                else:    
                    Message = 'An error was encountered while attempting to load "%s".\n\n'%InitialProject
                    H = 'load.failed'
                PossibleName = ''
            if R <> 0:
                #Load ran into trouble
                self.LoadOrNew(Message,HelpTopic=(H,(InitialProject,)),PossibleName=PossibleName)
            else:
                #Project loaded OK.
                Rpw.MessageDialog(Message='Project "%s" successfully loaded.'%InitialProject
                    ,Widget=self._Win,Title='Splash Screen',License=True,Buttons=(('Continue',0),))
        #Generate key bindings to those config-specified actions that we implement
        self.GenerateBindings('_Win')        
        
        #We care if we get renamed
        Repo.Bind(self.WRID,'HerdRenameNotify',self.FormRename)

    def on_LayoutNotebookHelp(self,Event=None):
        """
        User middle clicked over layout notebook
        """
        Help('LayoutArea.FormTab')    
        

    #---------------------------------------------------------------------------
    # Published methods
    #---------------------------------------------------------------------------

    def TextEditFetch(self):
        """=p
        Return the text editor of the currently visible form.
        """    
        Visible = self.CurrentlyVisibleForm()
        return Repo.FetchForm(Herd=Visible)['Text']
        
    def HandlerGoto(self,HandlerName):
        """
        Bring text exitor to the front and goto the specified handler
        """   
        TE = self.TextEditFetch()
        if TE == None:
            return
        Entry = Repo.FetchForm()
        if Entry == None:
            return
        #We have at least one form in tab
        if Entry['Requested'] == 'Gui':
            #The Gui editor is showing; switch to text
            self.on_ActionFormSwapCodeLayout()
        TE.HandlerGoto(HandlerName)    

    #---------------------------------------------------------------------------
    # Main menu command
    #---------------------------------------------------------------------------

    def on_ActionExit(self,Event=None):
        """
        User wants to shutdown.
        """
        if self.SaveOption('Exit'):
            #User cancelled the exit
            return
        sys.exit()

    def on_ActionProjectInfo(self,Event=None):
        """
        User asked to see project info.
        """
        Msg = [('Module','Lines'),('------','-----')]
        Total = 0
        GblProjectInfo.sort()
        for Mod,Lines in GblProjectInfo:
            Msg.append((Mod,str(Lines)))
            Total += Lines
        Msg.append(('','-----'))
        Msg.append(('Total:',str(Total)))    
        Msg = Rpw.Columnate(Msg)
        Msg = ('Project: %s\n\n'%Cfg.Info['ProjectName']) + Msg
        Rpw.MessageDialog(Message=Msg,Widget=self._Win,Justify=LEFT,Font='courier -12')
        
    def on_ActionFormRename(self,Event=None):
        """
        Tell user how to rename a form
        """        
        Help('howto.rename.form')

    def on_ActionFormAlternate(self,Event=None):
        """
        User wants to swap current form for previous form
        """        
        if Repo.PreviousForm:
            self.LayoutNotebook.Select(Repo.PreviousForm)

    def on_ActionProjectRename(self):
        """
        Rename the project.
        
        You can't explicitly rename the project; all you can do is rename the main
            module of the project. We provide this as a convenience for the user.
            It selects the main-module then invokes the module rename stuff.
        """    
        self.ModuleSelect(Cfg.Info['ProjectName'])
        self.on_ActionModuleRename()

    def on_ActionProjectNew(self,SaveOption=True,PossibleName=''):
        """
        Start a new project.
        
        If "SaveOption" is true we give the user a chance to save if the project
            has changed since the last save. This option exists so the "start from
            scratch" code can create a new project without having to trip over 
            the fact that there is no existing project.
            
        "PossibleName" is the name presented to the user as the possible name for the
            project. If omitted, it defaults to empty'    
            
        We return False if the user cancelled, otherwise True
        """
        global GblProjectDirectory
        if SaveOption:
            if self.SaveOption('New'):
                #User cancelled the New operation
                return False
        Dir = Cfg.Info['DefaultDir']
        if Dir == '*' or not os.path.isdir(Dir):
            #Either the config said to use the current working directory or the directory
            #    the config specified does not exist.
            Dir = os.getcwd()
        R = Rpw.NewProjectDialog(self._Win,InitialDir=Dir,where=self._Win,ProjectFile=PossibleName).Result
        if R == None:
            return False
        GblProjectDirectory, ProjectName = R
        self.ProjectNewBuild(ProjectName,GblProjectDirectory)    
        #Create the initial form of the project
        self.FormCreateNew({'Name':ProjectName,'Type':'Tkinter.Frame','BaseClass':'Tkinter.Frame'})
        return True
            
    def ProjectNewBuild(self,ProjectName,ProjectDir):
        """
        Build a new, empty project.
        
        "ProjectName" is the name for the new project and for the main module of the
            project.
            
        "ProjectDir' is a path to the directory when the project is to be saved.    
        """        
        global GblModules, GblPreviousModule, Repo, GblWrid, GblLastSavedProject
        global GblProjectInfo
        #Clear any tabs from the layout area
        self.LayoutNotebook.Clear()
        Cfg.Info['ProjectName'] = ProjectName
        Cfg.Info['ProjectDir'] = ProjectDir        
        GblModules = {ProjectName:WidreqRepository()}
        GblPreviousModule = ProjectName
        GblProjectInfo = None
        Repo = GblModules[ProjectName]
        Repo.ModuleName = ProjectName
        Rpo.Repo = Repo


        GblWRID = Repo.Register('Global main loop')
        R = Repo.Request(GblWRID, 'HerdCreate', GblParkingLotName)
        if R <> 1:
            print R
            raise Exception, "Creation of parking lot failed unexpectedly"
        R = Repo.Request(GblWRID, 'HerdSelect', GblParkingLotName)
        if R <> 1:
            print R
            raise Exception, "Selection of parking lot failed unexpectedly"
        self.WRID = Repo.Register('Layout area')
        self.ModuleNameUpdate()
        self.ApplicationTitleSet(ProjectName)
        GblLastSavedProject = None
        self.FormCreateNew({'Name':GblMainName,'Type':None,'BaseClass':None},OfMainModule=True)
        #Let the widgetator know we have a 'new' module on the go
        self.TheWidgetator.ModuleNew()
        #Have the parking lot and trash bin sign up with the new repo.
        assert 1==Repo.Request(self.WRID,'HerdSelect','the Parking Lot')
        self.ParkingLot.RepoSignup()
        self.TrashBin.RepoSignup()

    def on_ActionProjectLoad(self):
        """=m
        Load a new project.
        
        We return True if the project is successfully loaded, or False if the user
            bails or we encounter an error during load.
        """
        #Give user opportunity to save or cancel.
        if self.SaveOption("Load"):
            #User cancelled the load
            return False
        R = self.ProjectLoad()
        if R == 2:
            #We blew up during load
            self.LoadOrNew('','load.failed')
            
    def on_ActionProjectSave(self,Event=None):
        """=m
        User asked to save the current project.
        """
        self.ProjectSave()
        Rpw.MessageDialog(Message='Project Saved')
        
    def on_ActionProjectBuild(self,Event=None):
        """
        Build the project.
        """
        self.ProjectBuild()
        
    def on_ActionProjectSaveBuild(self,Event=None):
        """
        Save then build the project.
        """
        self.ProjectSave()
        self.ProjectBuild()
        
    def on_ActionProjectBuildRun(self,Event=None):
        """
        Build then run the project.
        """
        self.ProjectBuild(Run=True)
            
    def on_ActionProjectSaveBuildRun(self,Event=None):
        """
        Save, build then run the project.
        """
        self.ProjectSave()
        self.ProjectBuild(Run=True)
            
    def on_ActionProjectHelp(self,Event=None):
        """=m
        User asked for help on main menu / project choices.
        """
        Help('layout.menu.project')

    def on_ActionModuleAlternate(self,Event=None):
        """
        Select the previously selected module.
        """
        if not self.TheWidgetator.StatusCheck():
            #There are invalid edit values
            return
        if GblPreviousModule <> Repo.ModuleName:
            #The remembered module name differs from the current module name
            if GblModules.has_key(GblPreviousModule):
                #The remembered module still exists; select it
                Target = GblPreviousModule
                self.ModuleSelect(Target)
            else:
                #The remembered module is no longer with us; advance to next module    
                self.ModuleSelect(self.ModuleNext(Repo.ModuleName))
        
    def on_ActionModuleNext(self,Event=None):
        """
        Advance to the next module in alphabetical order.
        """    
        if not self.TheWidgetator.StatusCheck():
            #There are invalid edit values
            return
        self.ModuleSelect(self.ModuleNext(Repo.ModuleName))

    def on_ActionModuleRename(self):
        """
        User wants to rename the current module.
        """
        global GblModules, Repo
        #Make sure we don't have a bad option before we get halfway through things
        SelectedName = Repo.FetchSelected()    
        SelectedWidreq = Repo.Fetch(SelectedName)
        try:
            if not SelectedWidreq.OptionEditor.StatusCheck():
                #Invalid option value
                return
        except AttributeError:
            pass    
        try:    
            if not SelectedWidreq.PackEditor.StatusCheck():
                #Invalid pack value
                return
        except AttributeError:
            pass
            
        OldName = Repo.ModuleName
        if OldName == Cfg.Info['ProjectName']:
            #Were renaming the main module; must pass a list of form names so we don't get
            #    a conflict when it comes time to rename the main form.
            Forms = Repo.ListHerds()
            #We need the gui of the main form so make sure the main for is on a tab
            #    and visible
            if 1 <> self.FormSee(Cfg.Info['ProjectName']):
                MessageDialog(Msg='Unable to select the main form of the main module')
                return
        else:
            Forms = []    
        NewName = Rpw.ModuleNameDialog(Modules=GblModules.keys(),Current=OldName
            ,Forms=Forms,ProjectDirectory=GblProjectDirectory).Result
        if NewName == None:
            return
        #Update the repository directory so we are known by the new name    
        GblModules[NewName] = Repo
        del GblModules[Repo.ModuleName]
        Repo = GblModules[NewName]
        #Update the actual module name in our repository entry
        Repo.ModuleName = NewName
        #Show the new name to the user
        self.ModuleNameUpdate()
        #Delete any old generated module file
        try:
            os.remove(Cfg.Info['ProjectDir'] + OldName + '.py')
        except OSError:
            pass    
        if OldName == Cfg.Info['ProjectName']:
            #Were renaming the entire project.
            Cfg.Info['ProjectName'] = NewName
            self.ApplicationTitleSet(NewName)
            #Note the currently selected herd so we can restore when done
            WasSelected = Repo.SelectedHerd
            #Select the main form so we can rename it
            R = Repo.Request(self.WRID,'HerdSelect', OldName)    
            if R <> 1:
                print R
                raise Exception, 'Attempt to select form %s failed unexpectedly.' \
                    %(OldName),R
            #Rename the main form of the main module
            R = Repo.Request(self.WRID,'WidreqRename', OldName, NewName)    
            if R <> 1:
                print R
                raise Exception, 'Attempt to rename widreq %s to %s failed unexpectedly.' \
                    %(OldName, NewName),R
            #And rename the herd itself        
            R = Repo.Request(self.WRID,'HerdRename',OldName,NewName)
            if R <> 1:
                raise Exception, 'HerdRename failed unexpectedly: '+R
            MainFormWidreq = Repo.Fetch(NewName)    
            try:
                #Update the name in the main form's option editor
                MainFormWidreq.OptionEditor.NotifyExternalChange()
                MainFormWidreq.OptionEditor.EditorRefresh()
            except AttributeError:
                #The option editor my not yet exist in which case no action is required
                pass    
            #If there was a selected herd, restore it
            if WasSelected and WasSelected <> OldName:
                #Select the previous selected form unless the main form was already selected
                R = Repo.Request(self.WRID,'HerdSelect', WasSelected)    
                if R <> 1:
                    raise Exception, 'Attempt to select form %s failed unexpectedly.' \
                        %(OldName),R
                

    def on_ActionModuleDelete(self):
        """
        User wants to delete the current module.
        """
        global GblModules, Repo, GblPreviousModule
        assert len(GblModules) > 1
        ToDelete = Repo.ModuleName
        R = Rpw.MessageDialog(Title='Confirmation',Message='Delete module "%s" and all it\'s content now? '
            %ToDelete,Buttons=(('Delete Module',1),('~Cancel',None))
            ,Help=('Module.Delete.Confirmation',(ToDelete,))).Result
        if R <> 1:
            return
        del GblModules[ToDelete]
        self.ModuleSelect(GblPreviousModule,NotePrevious=False)

    def on_ActionModuleNew(self):
        """
        User wants to add a new module to the project
        """
        if not self.TheWidgetator.StatusCheck():
            #There are invalid edit values
            return
        Temp = Rpw.ModuleNameDialog(Modules=GblModules.keys(),ProjectDirectory=GblProjectDirectory).Result        
        if Temp == None:
            return
        self.ModuleNewBuild(Temp)    
            
    def ModuleNewBuild(self,ModuleName):
        """
        Build a new module of the specified name.
        
        Note: We cheat a bit here. For the sake of discussion there are two kinds of
            repository users: permanent users and transient users. The permanent users
            are: Global Main Loop, Layout area, Widgetator, Parking lot and Trash bin.
            The permanent users use whatever repository (ie module) is current and thus
            have interactions with *all* repositories. The transient users (eg widgets,
            gui editors etc) are associated solely with a single module and repository.
            To simplify things we make sure that the permanent users get identical ID
            numbers in all the repositories, thus we can change repositories without
            the permanent users having to worry about it. On creating a new repository
            we then sign up the permanent users in the same order and they then get the
            same ID numbers.
        """        
        global GblModules, Repo, GblPreviousModule
        #Note name of current module so we can alternate to it
        GblPreviousModule = Repo.ModuleName
        #Turn off all colorizers of the current module
        self.ColorizerOffAll()    
        #Remember the currently visible form so we can bring its tab forward on reselect
        Repo.VisibleForm = self.LayoutNotebook.GetCurSelection()
        #Collect widreqs from the parking lot so we can transplant them to the new module
        ParkedWidreqs = self.ParkingLot.Gather()
        #
        #
        #
        self.LayoutNotebook.Clear()
        #Create new repository for new module
        GblModules[ModuleName] = WidreqRepository()
        Repo = GblModules[ModuleName]
        Repo.ModuleName = ModuleName
        Repo.DebugSelectorSet('')

        GblWRID = Repo.Register('Global main loop')
        R = Repo.Request(GblWRID, 'HerdCreate', GblParkingLotName)
        if R <> 1:
            print R
            raise Exception, "Creation of parking lot failed unexpectedly"
        R = Repo.Request(GblWRID, 'HerdSelect', GblParkingLotName)
        if R <> 1:
            print R
            raise Exception, "Selection of parking lot failed unexpectedly"
        self.WRID = Repo.Register('Layout area')
        self.FormCreateNew({'Name':GblMainName,'Type':None,'BaseClass':None})
        self.TheWidgetator.ModuleNew()
        #Have the parking lot and trash bin sign up with the new repo.
        assert 1==Repo.Request(self.WRID,'HerdSelect','the Parking Lot')
        self.ParkingLot.RepoSignup()
        self.TrashBin.RepoSignup()
        #Restore parking lot widreqs
        self.ParkingLot.Scatter(ParkedWidreqs)
        self.ParkingLot.CanvasConfigure()
        self.ModuleNameUpdate()

    def on_ActionModuleSelect(self):
        """
        User wants to select the current module
        """
        if not self.TheWidgetator.StatusCheck():
            #There are invalid edit values
            return
        Temp = Rpw.ModuleDialog(Modules=GblModules.keys(),Current=Repo.ModuleName).Result
        if Temp == None:
            #User bailed
            return
        if Temp == Repo.ModuleName:
            #They selected the current module; nothing to do
            return
        self.ModuleSelect(Temp)                
        
    def on_ActionModuleHelp(self,Event=None):
        """
        User asked for help on main menu / modules choices.
        """    
        Help('layout.menu.modules')
        
    def on_ModuleIndicatorHelp(self,Event=None):
        """
        User asked for help about the module indicator
        """
        Help('layout.module-indicator')

    def on_ProjectClick(self,Event):
        """
        User called up the project menu.
        """
        if GblProjectInfo <> None:
            S = NORMAL
        else:
            S = DISABLED
        self.FileMenu.entryconfigure(self.ProjectInfoIndex,state=S)        

    def on_ModuleClick(self,Event):
        """
        User called up the module menu; some choices are enabled dynamically
        """
        if Repo.ModuleName == Cfg.Info['ProjectName']:
            #We are the main module
            S = DISABLED
        else:
            S = NORMAL
        self.ModuleMenu.entryconfigure(self.ModuleDeleteIndex,state=S)
        

    def on_FormClick(self,Event):
        """
        User called up the form menu; some choices are enabled dynamically
        """
        #If the main form is the currently visible form then we disable the selections
        #    about deleting the form (main form always exists) and changing the "derived
        #    from" value (since the main form isn't a class and isn't derived).
        FormName = self.LayoutNotebook.GetCurSelection()
        if FormName == GblMainName:
            #The main code area is selected
            S = DISABLED
        else:
            S = NORMAL
        self.FormMenu.entryconfigure(self.FormDeriveIndex,state=S)
        self.FormMenu.entryconfigure(self.FormDeleteIndex,state=S)        
        self.FormMenu.entryconfigure(self.FormExportIndex,state=S)

    def on_ActionFormsSelect(self):
        """=m
        User asked to choose which forms to see.
        """
        Herds = Repo.ListHerds()
        Tabs=self.LayoutNotebook.TabNames()
        Requested = Rpw.FormSeeDialog(self._Win,Herds=Herds
            ,Tabs=Tabs).Result
        if Requested == None:
            #User bailed
            return
        #Delete any unwanted tabs
        for T in Tabs:
            if not T in Requested:
                self.LayoutNotebook.Delete(T)
        #Add any newly requested tabs
        for R in Requested:
            if not R in Tabs:
                self.LayoutNotebook.Add(R)
        #Mark status in repository
        for H in Herds:
            Form = Repo.FetchForm(H)        
            if Form <> None:
                Form['OnTab'] = H in Requested
        
    def on_ActionFormNew(self):
        """=m
        User asked to add a new form to the project.
        """
        #Generate a default non-conflicting name
        if not self.RepoActionCheck('HerdCreate'):
            #Somebody isn't happy about creating a form now
            return
        Name = self.NameForm()
        Info = {'Name':Name, 'Type':'Tkinter.Toplevel','BaseClass':'Tkinter.Toplevel'}
        while 1:
            #Ask user for their choice of name
            Info = Rpw.FormDialog(self._Win,Settings=Info,Title=' New Form '
                ,Prompt='Name for new form:',AllowNameEdit=1).Result
            if Info == None:
                #user cancelled
                return
            if not Info['Name'] in Repo.ListHerds():
                #Name is unique
                break
            #They picked a duplicate; whine
            R = Rpw.MessageDialog(Title='Oops',Message='There is already a form named "%s" in this project '
                'Please pick another name or cancel.'%Info['Name'],Buttons=(('Pick again',1),('~Cancel',None))).Result
            if R == None:
                #they cancelled
                return
        self.FormCreateNew(Info)

    def on_ActionFormChangeDerive(self):
        """=m
        User asked to change our "derive from" class
        """
        Name = ''
        PresentName = Repo.SelectedHerd
        if PresentName == None:
            Rpw.MessageDialog(Message='There is no currently selected form.')
            return
        SelectedWidreq = Repo.FetchSelected()
        ##D('Initially selected widreq=%s'%SelectedWidreq)
        #Make sure we can select the widreq of the form. This will fail if some other widreq
        #    is selected and it has an invalid option value. We don't actually need our widreq
        #    to be selected but better to fail now, before the user has gone to the trouble of
        #    selecting their new choice, rather than after when we go to delete and recreate
        #    the widreq of the form
        R = Repo.Request(self.WRID,'WidreqSelect',PresentName)
        if R <> 1:
            return
        FI = Repo.FetchForm()
        Info = {'Name':PresentName, 'Type':FI['Type'], 'BaseClass':FI['BaseClass']}
        MainForm = Repo.ModuleName == Cfg.Info['ProjectName'] and PresentName == Cfg.Info['ProjectName']
        #Ask user for their choice of name
        Info = Rpw.FormDialog(self._Win,Settings=Info,Title=' Form Properties '
            ,Prompt='Form:',FrameOnly=MainForm).Result
        if Info == None:
            #user cancelled; restore selection
            Repo.Request(self.WRID,'WidreqSelect',SelectedWidreq)
            return
        #Update possible changed non-name choices
        if FI['Type'] <> Info['Type']:
            #They changed our type.
            ExistingWidreq = Repo.Fetch(PresentName)
            WidgetName = ExistingWidreq.WidgetName
            ModuleName = ExistingWidreq.ModuleName
            FrameID = ExistingWidreq.FrameID
            FrameParent = ExistingWidreq.FrameParent
            PresentHome = ExistingWidreq.PresentHome
            #Delete old
            R = Repo.Request(self.WRID,'WidreqDelete',PresentName)
            if R <> 1:
                raise Exception, "request to delete form widreq unexpectedly failed"
                return
            #Create new
            NewWidreq = WidReq(WidgetName=WidgetName,InstanceName=PresentName
                ,FrameID=FrameID,PresentHome=PresentHome,ModuleName=ModuleName)
            R = Repo.Request(self.WRID,'WidreqCreate',PresentName,NewWidreq)
            if R <> 1:
                raise Exception, "request to delete form widreq unexpectedly failed"
                return
            NewWidreq.FrameParent = FrameParent    
        if FI['Type'] <> Info['Type'] or FI['BaseClass'] <> Info['BaseClass']:
            #Update the systext in our text editor
            ST = self.FormSystextHeaderGenerate(PresentName,Info['BaseClass'],Info['Type'])
            FI['Text'].TextWidget.SystextReplace('class',ST[0])
            FI['Text'].TextWidget.SystextReplace('apply(',ST[1])
            #Update form information
            FI['Type'] = Info['Type']
            FI['BaseClass'] = Info['BaseClass']
        #Restore the originally selected widreq    
        Repo.Request(self.WRID,'WidreqSelect',SelectedWidreq)
            
    def on_ActionFormDelete(self):
        """=m
        User asked to delete the current form.
        """
        #if len(Repo.ListHerds()) == 2:
        #    RpwMessageDialog(Message='There is only one form in the project. 
        Form = Repo.SelectedHerd
        if Form == None:
            Rpw.MessageDialog(Message='There is no currently selected form to delete.')
            return
        elif Form == Cfg.Info['ProjectName'] and Repo.ModuleName == Cfg.Info['ProjectName']:
            M = '"%s" is the main form of the main module and as such is not deletable.'%Form
            R = Rpw.MessageDialog(Title='Information',Message=M,Help='Form.Delete.MainForm')
            return    
        R = Rpw.MessageDialog(Title='Confirmation',Message='Delete form "%s" and all it\'s content now? '
            %Form,Buttons=(('Delete',1),('~Cancel',None))
            ,Help=('Form.Delete.Confirmation',(Form,Repo.ModuleName))).Result
        if R <> 1:
            return
        self.FormDelete(Form)
        
    def on_ActionFormExport(self,Event=None):
        """=m
        User asked to export the current form.
        
        A form is exported as a pickled tuple:
            [0] The string 'Form'
            [1] The version number
            [2] The data gathered from the gui editor and the text editor, just as when saving a project.
            [3] List of import type information per the config file.
        """
        Form = Repo.SelectedHerd
        if Form == Cfg.Info['ProjectName'] and Repo.ModuleName == Cfg.Info['ProjectName']:
            M = '"%s" is the main form of the main module. Alas, the main form of the main module is special ' \
                'and the code to allow it to be exported has not yet been written. Sorry.'%Form
            R = Rpw.MessageDialog(Title='Information',Message=M) 
            return    
        FI = Repo.FetchForm()
        assert FI['Gui'] <> None, 'Attempt to export the main code area'
        FormInfo = FI['Gui'].Gather()
        FormInfo['Text'] = FI['Text'].TextWidget.Gather()
        ImportTypes = self.ProjectFetchImportTypes()
        Data = ('Form',0,FormInfo,ImportTypes)

        File = tkFileDialog.asksaveasfile(parent=self._Win
            ,initialfile='%s%s.rpf'%(GblProjectDirectory,Form),title='Copy to file')
        if not File:
            #User bailed
            return 
        cPickle.dump(Data,File)
        File.close()
        Rpw.MessageDialog(Message='Form exported')
        
    def on_ActionFormImport(self,Event=None):
        """
        User asked to import a form.
        """        
        File = tkFileDialog.askopenfile(parent=self._Win,initialfile=GblProjectDirectory,title='Import Form'
            ,filetypes=([('Rapyd forms','*.rpf')]))

        #
        # Setup the exception we want to catch
        #
        if Cfg.Info['Debug']:
            #If in debug mode we want to leave exceptions uncaught so we can
            #    seen them where and as they happen. Therefore we create a dummy
            #    exception (which will never get raised) and setup to catch that.
            class Dummy(Exception): pass
            ExceptionToCatch = Dummy
        else:
            #If in non-debug mode then we want to catch all exceptions so if things
            #    go wrong we give the user a polite message and carry on.
            ExceptionToCatch = Exception    
        #
        # Fetch the pickled form
        #
        try:
            Info = cPickle.load(File)
            File.close()
            assert len(Info) == 4
            assert Info[0] == 'Form'
            assert Info[1] == 0
            FormInfo = Info[2]
            FormImportTypes = Info[3]
            Name = FormInfo['Name']
            while 1:
                Name = Rpw.PromptDialog(Message='Name for form in this project'
                    ,Prompt=FormInfo['Name'],Help='FormImportNameSelect').Result
                if not Name:
                    #User cancelled
                    return
                if not Name in Repo.ListHerds():
                    #Name is unique
                    break
                R = Rpw.MessageDialog(Title='Oops',Message='There is already a form named "%s" in this project '
                    'Please pick another name or cancel.'%Name,Buttons=(('Pick again',1),('~Cancel',None))).Result
                if R == None:
                    #they cancelled
                    return

            #Rename the form and the main frame
            FormInfo['Name'] = Name
            for WidreqInfo in FormInfo['Widreqs']:
                if WidreqInfo['ID'] == (0,):
                    #This is the outermost frame - its name must match too
                    WidreqInfo['Name'] = Name
                    break

            #And now for a while pile of checking.

            # When the project was saved we noted the ImportType for each of the
            #     widget donor modules (eg Tkinter, Pmw). If the import status as specified
            #     by the config file is now different than it was when we saved the project then
            #     we must regenerate the creation code for each form and the user may have some
            #     work to do too. Here we check both for donor modules of changed import type
            #     and for donor modules that went away totally.
            MustRegenerate = False
            ChangeList = []
            MissingList = []
            for ModuleName,SavedImportType in FormImportTypes:
                if Cfg.Info['Modules'].has_key(ModuleName):
                    #The moduled mentioned at save time is still in use
                    CurrentImportType = Cfg.Info['Modules'][ModuleName]['ImportType']
                    if SavedImportType <> CurrentImportType:
                        #But it's import type has changed
                        ChangeList.append((ModuleName,SavedImportType,CurrentImportType))
                else:
                    #The module mentioned at save time is no longer in use
                    MissingList.append(ModuleName)        
            #Look after missing donor modules
            AlteredFormDict = {}
            if MissingList:
                #We have at least one missing module. Although it's missing, it may be one that
                #    this form didn't use. Scan the form to get a dictionary of all
                #    the donor modules used by the form.
                
                #Note: DonorModulesUseScan expects a module, not a form, so we dress up our form
                #    enough to make it happy.
                DonorModuleDict = DonorModulesUseScan({'Forms':[FormInfo]})
                #In DonorModuleDict the key is the name of a donor moduled used by this project while
                #    the value is a number of no particular significance here.
                #Delete any values from MissingList which are not used in this module
                for J in range(len(MissingList)):
                    if not MissingList[J] in DonorModuleDict.keys():
                        MissingList.pop(J)
                if MissingList:
                    MissingAsString = ', '.join(MissingList)        
                    #Any values still in MissingList represent donor modules missing and used by this project.
                    Msg = ('The form you just imported contains one or more widgets from the module{/s} "%s" and'
                        ' {that/those} module{/s} {was/were} available when the form was exported.'
                        ' However, {that/those} module{/s} {is/are} not available now because the config'
                        ' file did not make {it/them} available. It seems likely that either you changed the'
                        ' config file since you exported the form, or you got the form from'
                        ' a different Rapyd installation. In any case the form is not loadable'
                        ' in its present state'
                        ' because it references widgets currently unknown to me.\n\nIf you choose "delete'
                        ' widget references" I will delete all references to the widgets from the missing'
                        ' module{/s} which will allow me to carry on with the import. Deleting these widgets'
                        '  may break a lot of the form\'s code but'
                        ' it\'s your choice. Alternately you can cancel importing the form. Click on'
                        ' "Help" to get a full list of the missing widgets and where they are used.'
                        %MissingAsString)
                    Msg = rpHelp.Plural(Msg,len(MissingList))    

                    Arg = [('Widget','Name'),('------','----')]

                    FormName = FormInfo['Name']
                    for Widreq in FormInfo['Widreqs']:
                        WidreqInstanceName = Widreq['Name']
                        WidreqTypeName = Widreq['WidgetName']
                        Dmodule = Widreq['ModuleName']
                        if Dmodule in MissingList:
                            #This widreq is from one of our donors 
                            Arg.append(('%s.%s'%(Dmodule,WidreqTypeName),WidreqInstanceName))
                    #Now convert the tuples to a string with each field widthed as necessary
                    Arg = Rpw.Columnate(Arg,Lmarg=1,Spacing=2)
                    Arg = '{f' + Arg + '}'
                    
                    MissingModuleCount = len(MissingList)
                    WidgetInstanceCount = Arg.count('\n')-1
                    HelpTuple = ('load.missing.widgets.form'
                        ,[Arg,MissingModuleCount,WidgetInstanceCount,MissingAsString])
                    R = Rpw.MessageDialog(Message=Msg,Help=HelpTuple,Widget=self._Win
                        ,Buttons=(('Delete Widgets',1),('~Cancel',None))).Result
                    if R == None:
                        #User cancelled
                        return 
                    elif R == 1:
                        #Delete the widgets that were from the missing modules.
                        Temp = range(len(FormInfo['Widreqs']))
                        Temp.reverse()
                        for J in Temp:
                            Widreq = FormInfo['Widreqs'][J]
                            Dmodule = Widreq['ModuleName']
                            if Widreq['ModuleName'] in MissingList:
                                FormInfo['Widreqs'].pop(J)
                    
            #Look after donor modules that changed import-type
            if ChangeList:
                #We have at least one changed module. Although it's changed, it may be one that
                #    this project didn't use. Scan all of our modules to get a dictionary of all
                #    the donor modules used by this project.

                #Note: DonorModulesUseScan expects a module, not a form, so we dress up our form
                #    a bit to make it look like a module.
                DonorModuleDict = DonorModulesUseScan({'Forms':[FormInfo]})
                #In DonorModuleDict the key is the name of a donor moduled used by this project while
                #    the value is a number of no particular significance here.
                #Delete any values from ChangeList which are not used in this module
                for J in range(len(ChangeList)):
                    if not ChangeList[J][0] in DonorModuleDict.keys():
                        ChangeList.pop(J)
                if ChangeList:
                    ChangeAsString = ', '.join([X[0] for X in ChangeList])        
                    #We have changed modules which were in fact used.
                    Msg = ('This form uses widgets from {the /}module{/s} "%s" but in'
                        ' the config file the import type of'
                        ' {that/those} modules{/s} is different than it was when the form was exported.'
                        ' It seems likely that either you changed the config file since exporting'
                        ' the form or you got this form from a different Rapyd installation.'
                        '\n\nThis is not a problem since I will update all the Rapyd-maintained code to'
                        ' reflect the current import-type setting.'
                        ' Just press "Continue" and the import will complete.'
                        ' Either that or press "Cancel" to cancel importing of this'
                        ' form.\n\nBear in mind that although all the Rapyd maintained code will be updated'
                        ' automatically, any user supplied code that references anything from {this/these}'
                        ' module{/s} will have to be adjusted accordingly by hand.'%ChangeAsString)
                    Msg = rpHelp.Plural(Msg,len(ChangeList))    
                    Arg = [' Module     At-save    Now',' ------     -------    ----']
                    for Temp in ChangeList:
                        Arg.append(' %-10s %-10s %s'%Temp)
                    Arg = '{f' + ('\n'.join(Arg)) + '}'    
                    HelpTuple = ('load.changed.importtype',[Arg,len(ChangeList),'form'])
                    R = Rpw.MessageDialog(Message=Msg,Widget=self._Win,Help=HelpTuple
                        ,Buttons=(('Continue',1),('~Cancel',None))).Result
                    if R == None:
                        return 
                    # $$marker$$
            #Verify that widgets used in this form are widgets we have available
            MissingWidgetList = [('Widget type','Widget name'),
                                 ('-----------','-----------')]
            MissingWidgetCount = 0
            FormName = FormInfo['Name']
            Temp = self.VetWidgetsExist(FormInfo['Widreqs'])
            #Temp is a list of widgets that are not available in the current
            #    config as (widget-type, widget-name)
            if Temp:
                for T in Temp:
                    MissingWidgetList.append(T)
                    MissingWidgetCount += 1
            if MissingWidgetCount:
                Msg = ('The form you are attempting to import contains {a /}reference{/s} to{ a/}'
                    ' widget{/s} which {is/are} unknown to me. This suggests that you made changes'
                    ' to the config file, or the form being imported came from a different Rapyd'
                    ' installation. In any case the form is unloadable as it currently stands.'
                    '\n\nIf you choose "delete widgets" I will delete all reference{/s}'
                    ' to the unknown widget{/s}, which will allow me to carry on with the import.'
                    ' Deleting {this/these} widget{/s} may beak a lot of the form\'s code but it\'s your'
                    ' choice. Alternately you can cancel importing of this form. Click on "Help" to'
                    ' get a full information about the missing widget{/s}.')
                Msg = rpHelp.Plural(Msg,MissingWidgetCount)
                Arg = '{f' + Rpw.Columnate(MissingWidgetList,Lmarg=1,Spacing=2) + '}'
                R = Rpw.MessageDialog(Message=Msg,Help=('load.widgets.missing',[MissingWidgetCount,Arg,'form'])
                    ,Widget=self._Win,Buttons=(('Delete widgets',None),('~Cancel',1))).Result
                if R == 1:
                    return 1

            #Here we verify the option types and values for all option settings of all widgets.
            #    What we are looking for is saved options which no longer exist in the config
            #    file and for option values which are not valid per the config file. Options
            #    which no longer exist are simply deleted while options with invalid values are
            #    set to the default value. In either case we make sure the module/form is mentioned
            #    in AlteredFormDict since that prompts regeneration of the code of that form.
            DeletedOptionCount = 0
            ResetOptionCount = 0
            DeletedOptionList = [('Module','Form','Widget type','Widget name','Option'),
                                 ('------','----','-----------','-----------','------')]
            ResetOptionList = [('Module','Form','Widget','Option','Original','Revised'),
                               ('------','----','------','------','--------','-------')]                     
            ModuleName = '-'
            FormName = FormInfo['Name']
            Temp = self.VetOptionsExist(FormInfo['Widreqs'],ModuleName,FormName)
            DeletedOptionList.extend(Temp)
            DeletedOptionCount += len(Temp)
            if Temp:
                AlteredFormDict[(ModuleName,FormName)] = None
            Temp = self.VetOptionValues(FormInfo['Widreqs'],ModuleName,FormName)
            ResetOptionList.extend(Temp)
            ResetOptionCount += len(Temp)
            if Temp:
                AlteredFormDict[(ModuleName,FormName)] = None
            if DeletedOptionCount:
                Msg = ('In the course of importing the form I found %s instance{/s}'
                    ' of {a }widget option{/s} which existed when the form was exported but'
                    ' which (according to the current config file) {does/do} not exist now. The option{/s} in'
                    ' question {has/have} been deleted. This is merely an advisory; no action on your'
                    ' part is required. Click on "Help" for details.')
                Msg = rpHelp.Plural(Msg,DeletedOptionCount)    
                Arg = '{f' + Rpw.Columnate(DeletedOptionList,Lmarg=1,Spacing=2) + '}'
                R = Rpw.MessageDialog(Message=Msg,Help=('load.options.missing',[Arg,'form'])
                    ,Widget=self._Win,Buttons=(('OK',None),('~Cancel',1))).Result
                if R == 1:
                    return 1
            if ResetOptionCount:
                Msg = ('In the course of loading the form I found %s instance{/s}'
                    ' of {a }widget option{/s} with an invalid value'
                    ' (according to the current config file). The option{/s} in'
                    ' question {has/have} been set to {its/their} default value. This is merely'
                    ' an advisory; no action on your'
                    ' part is required. Click on "Help" for details.')
                Msg = rpHelp.Plural(Msg,ResetOptionCount)    
                Arg = '{f' + Rpw.Columnate(ResetOptionList,Lmarg=1,Spacing=2) + '}'
                R = Rpw.MessageDialog(Message=Msg,Help=('load.options.reset',[Arg,'form'])
                    ,Widget=self._Win,Buttons=(('OK',None),('~Cancel',1))).Result
                if R == 1:
                    return 1

            #Load the form into the project
            self.FormLoad(FormInfo)
            self.FormRaise(FormInfo['Name'])
            self.EditorPack(ForceEditor='Gui')                    
            self.CreationSystextRegen('Project load')    
            
        except ExceptionToCatch, Message:
            #See note at top of the "try" as to what "ExceptionToCatch" is about.
            Rpw.MessageDialog(Message='An error was encountered while attempting to import the Form.'
                ,Widget=self._Win)

    def on_ActionFormHelp(self,Event=None):
        """=m
        User asked for help on main menu / forms.
        """
        Help('layout.menu.forms')

    def on_ActionAbout(self,Event=None):
        """
        User clicked the About menu item
        """
        Help('layout.menu.about')
        
    def on_ActionHelpHelp(self,Event=None):
        """
        User clicked the main help menu item
        """       
        Help('__intro') 

    def on_ActionHelpIndex(self,Event=None):
        """
        User clicked the main help index item
        """       
        Help('#') 

    def on_ActionHelpLicense(self,Event=None):
        """
        User clicked the main help license item
        """       
        Help('gpl') 

    def on_DebugRepoEvent(self):
        """=m
        User changed a repository event tracking flag.
        """
        Setting = ''
        for T in 'rqbu':
            Setting += self.RepoEventDebugCvar[T].get()
            Repo.DebugSelectorSet(Setting)

    def on_DebugRepo(self,Which):
        """=m
        Dump specified widreq repository info.
        """
        Repo.Dumphry(Which)

    def on_DebugGen(self,Action):
        """=m
        Perform a requested debug action.
        """
        if Action == 'separator':
            T = 40*'-'
            print '%s %s %s'%(T,self.SeparatorCounter,T)
            self.SeparatorCounter += 1
        elif Action == 'repo_stats':
            print Repo.Stats    
        elif Action == 'print_spanify':
            SelForm = Repo.FetchForm()
            if SelForm == None:
                print 'No form is selected; nothing to print'
            else:    
                print SelForm['Gui'].FrameInfoFormat()
        elif Action == 'print_visible':
            print self.CurrentlyVisibleForm()        
        else:
            print 'Unknown DebugAction %s'%Action    
            
    #---------------------------------------------------------------------------
    # End main menu commands
    #---------------------------------------------------------------------------

    def FormSee(self,FormName):
        """
        Make sure the specified form is on a tab and visible.
        
        Result is normally 1, or 0 if current tab declined to lower.
        """
        T = self.LayoutNotebook.Select(FormName)
        if T == 0:
            #The current tab declined to be lowered
            return 0
        if T == -1:
            #That form is not on a tab; put it on a tab
            self.LayoutNotebook.Add(FormName)        
            T = self.LayoutNotebook.Select(FormName)
            if T <> 1:
                raise Exception, 'Unexpected problem while selecting form. T=%s'%T
        return 1        

    def LoadOrNew(self,Message,HelpTopic,PossibleName=''):
        """
        Give the user the choice of loading a project, creating a project or quitting.
        
        If PossibleName is provided, then if they elect to create a new project, this
            value is used as the inital prompt for the suggested name.
        
        If they quit, we shutdown and don't return.
        
        If we do return it means there is a valid project in place.
        """
        while 1:
            M = Message + "Do you want to create a new project " \
                "or open an existing project?"
            R = Rpw.MessageDialog(Title='Hello',Message=M,Widget=self._Win
                ,Buttons=(('Create new',None),('Open existing',1),('~Quit',2))
                ,Help=HelpTopic,License=True).Result
            if R == 2:
                sys.exit()    
            if R == 1:
                #They asked to open an existing project
                Result = self.ProjectLoad()
                if Result in (1,2):
                    #They bailed or the load failed
                    continue
                #successful load    
                break    
            if R == None:    
                #They asked to create a new project
                if not self.on_ActionProjectNew(SaveOption=False,PossibleName=PossibleName):
                    #They bailed
                    continue
                break
            else:
                raise Exception, "Unexpected result: "+R

    def ProjectFetchImportTypes(self):
        """
        Fetch a list of import type information.

        Result is a list of tuples, where each tuple is:
            [0] Name of widget supplying module (eg Tkinter, Pmw)
            [1] Import type, eg "from" or "import"
            
        """
        ImportTypes = []
        for ModuleName in Cfg.Info['Modules'].keys():
            ImportTypes.append((ModuleName, Cfg.Info['Modules'][ModuleName]['ImportType']))
        return ImportTypes

    def ProjectGather(self):
        """
        Gather the entire current project and return it as a list.
        """
        ImportTypes = self.ProjectFetchImportTypes()
        Project = [{'ID':'Rapyd Project'
           ,'Version':0
           ,'ProjectName':Cfg.Info['ProjectName']
           ,'ModuleCurrent':Repo.ModuleName
           ,'ModulePrevious':GblPreviousModule
           ,'ParkingLot':self.ParkingLot.Gather()
           ,'Geometry':Root.winfo_geometry()
           ,'ImportTypes':ImportTypes
           ,'EditorWidths':self.TheWidgetator.WidthsGet()
           }]
        for OneRepo in GblModules.values():
            Project.append(self.ModuleGather(OneRepo.ModuleName))
        return Project

    def ProjectBuild(self,Run=False):
        """
        Build code files for the entire project and, optionally, run the project.
        
        We return 1 if the build was successful else 0.
        A build will fail if there is an open option with an invalid value.
        """
        #Attempt to select the already selected widreq; the point is to fail now if there
        #    is an open option with an invalid edit.
        global GblProjectInfo
        W = Repo.FetchSelected()
        if W <> None:
            R = Repo.Request(self.WRID,'WidreqSelect',W)
            if R <> 1:
                #oop - that didn't fly
                #But it is possible that we get an error if there was an open edit on the name
                #    of the current widreq because the widreq gets renamed and the name we
                #    passed is no longer recognized.
                if R[0].find('has no widreq named') <> -1:
                    #That may be the case; try one more time
                    W = Repo.FetchSelected()
                    R = Repo.Request(self.WRID,'WidreqSelect',W)
                    if R <> 1:
                        #Still a problem, give up
                        return 0
                else:
                    #Some other sort of problem, give up        
                    return 0
        GblProjectInfo = []            
        Dlg = Rpw.MessageDialog(Message='\n\nBuilding project...\n\n',Modal=False,Widget=self._Win)            
        #While we are building the project we also build the decoder file.        
        DecFilename = '%s%s.dec'%(GblProjectDirectory,Cfg.Info['ProjectName'])
        DecFile = open(DecFilename,'w')       
        #LocatorDict: key is the path to the module, data is locator data from ModuleBuild.
        LocatorDict = {} 
        for OneRepo in GblModules.values():
            DecFile.write('%s.py\n'%OneRepo.ModuleName)
            FN = '%s.py'%OneRepo.ModuleName
            L = self.ModuleBuild(OneRepo.ModuleName)
            LocatorDict[FN] = L[1]
            for Form,Offset,Lines in L[1]:
                DecFile.write(' %s %s %s\n'%(Form,Offset,Lines))
            GblProjectInfo.append((OneRepo.ModuleName,L[0]))    
        DecFile.close()        
        if Run:
            #Get the name of the result file and make sure we don't have one before
            #    we do any invoking of the project.
            ResultFN = '%s%s.result'%(GblProjectDirectory,Cfg.Info['ProjectName'])
            try:
                os.remove(ResultFN)
            except:
                pass    
            E = os.environ
            E['FROMRAPYD'] = DecFilename
            FN = '%s%s.py'%(GblProjectDirectory,Cfg.Info['ProjectName'])
            if GblProjectDirectory <> '':
                os.chdir(GblProjectDirectory)
            try:
                #This doesn't actually run the project (since the project contains a test and doesn't
                #    run if it's not __main__) but it does catch any syntax and indentation errors that 
                #    would prevent the project from even getting off the ground. That said, this does
                #    run *some* code in the project and if that code is inside the main "try" loop then
                #    it gets handled by rpErrorHandler within the project. We set environment variable
                #    FROMRAPYD to the path to the decoder file so rpErrorHandler can find it if needed.
                #FIX:file is not in the rapyd's directory and import module
                sys.path.append(GblProjectDirectory)
                execfile(FN,{})
                R = self.ProjectBuildProcessResult(ResultFN)
                if R <> None:
                    #Problem of some sort
                    Dlg.Close()
                    if R == 1:
                        #Couldn't access result
                        return 1
                    else:
                        #Ordinary user code problem.
                        return    
            except:
                #Oh-oh. Looks like the project bombed on a syntax or indentationerror. Invoke the error handler to
                #    give the user a look at the problem.
                Dlg.Close()
                R = rpErrorHandler.RunError(Info=LocatorDict,ProjectDirectory=GblProjectDirectory).Result
                if R == None:
                    #No action required
                    pass
                elif R == 1:
                    #Pass error to Tkinter
                    raise    
                else:
                    #Goto error line
                    TargetModule,TargetForm,TargetLine = R
                    self.ModuleSelect(TargetModule)
                    #Select the target form
                    #assert 1==Repo.Request(self.WRID,'HerdSelect',TargetForm)
                    self.LayoutNotebook.Select(TargetForm)
                    self.EditorPack('Text')
                    #select the target line number
                    FI = Repo.FetchForm()
                    FI['Text'].GotoLineNumber(TargetLine)
                    FI['Text'].focus_force()
                return 1    
            #So far so good. Now spawn the project as a distinct task. We set the environment
            #    variable FROMRAPID so if the error handler of the project gets control that it
            #    will know that it was invoked by us. If the error handler does get control and
            #    it wants to send information back to us it puts it in file '<project>.result'.
            #    Therefore before we spawn the program we erase that file so if one exists after
            #    we know it was from our project.
            Dlg.Close()
            self._Win.update_idletasks()
            E['FROMRAPYD'] = '*'
            #We can't spawn the project directly. We spawn the python interpreter with the path to
            #   the project as the argument.
            #Warning Warning: While Linux is perfectly happy if the first argument to the spawned
            #   program is empty, windows (or at least some version of windows) aren't; hence the
            #   'whatever' in the following line.
            os.spawnve(os.P_WAIT,sys.executable,['whatever',FN],E)
            #Now look for a result from the project.
            if self.ProjectBuildProcessResult(ResultFN) == 1:
                #Problem accessing the result
                return 1
        else:
            Dlg.Close()
        return 1    

    def ProjectBuildProcessResult(self,ResultFN):
        """
        Process a result file generated by rpErrorHandler in a run project.
        
        Result is:
            None - No error was encountered.
            0    - Error, users request dealt with
            1    - Unable to read result file
        """
        if os.path.isfile(ResultFN):
            try:
                F = open(ResultFN)
                Result = F.read()
                F.close()
            except:
                print 'Error reading result file "%s"'%ResultFN
                return 1
            if Result == '!HELP!':
                #User asked for help
                Help('run-error-dialog')
            elif Result == '!HANDLED!':
                #User error already handled
                return 0
            else:
                #Anything else is supposed to be a request to goto a specific line
                Temp = self.DecodeResult(Result)
                if type(Temp) == type(''):
                    #error decoding the result
                    Rpw.ErrorDialog('Error "%s" while processing result "%s" from run project.'
                        %(Temp,Result))
                    return 1    
                #The data looks valid; goto the specified line
                TargetModule,TargetForm,TargetLine = Temp
                self.ModuleSelect(TargetModule)
                #Select the target form
                #assert 1==Repo.Request(self.WRID,'HerdSelect',TargetForm)
                self.LayoutNotebook.Select(TargetForm)
                self.EditorPack('Text')
                #select the target line number
                FI = Repo.FetchForm()
                FI['Text'].GotoLineNumber(TargetLine)
                FI['Text'].focus_get()
            return 0
        else:
            #No error
            return None
            
    def DecodeResult(self,Line):
        """
        Attempt to decode a result line.
        
        If the line is of the form "modulename formname linenumber" and all three are valid within the
            context of the current project then we return then as a 3-tuple.
            
        For all other cases we return a string error message.    
        """
        Line = Line.strip().split()
        if len(Line) <> 3:
            return 'not three items'
        ModuleName, FormName, LineNumber = Line    
        if not ModuleName in GblModules.keys():
            return "no module named '%s' in this project"%ModuleName
        if not FormName in GblModules[ModuleName].ListHerds():
            return "no form names '%s' in module %s"%(FormName,ModuleName)
        try:
            LineNumber = int(LineNumber)
        except:
            return "'%s' is not a valid number"%LineNumber
        return (ModuleName,FormName,LineNumber)                        
        
    def ProjectPrune(self,Prj):
        """
        Return a copy of the passed project with certain information pruned out.
        
        Information in a project file can be divided into two categories:
        
            1) Stuff that affects the generated version of the project.
            2) Stuff that only affects how the project is shown to the user.
            
        In order to create a version of the project suitable for detecting "if the project
            has been changed" we prune out the text (since we already have a checksum of 
            the text) plus any "category-2" information which affects only how the project
            is shown to the user, eg cursor positions, which widget is currently selected,
            which forms are on tabs and so on.     
            
        Note that we also prune out widreq location information. Technically widreq location
            can affect the generated project *but* location of wireqs on the parking lot
            never affects the generated project and if a change in position of a form widreq
            is substantive it will affect the generated code which will cause the project
            to be noted as different.     
        """
        Project = copy.deepcopy(Prj)
        Preamble = Project[0]
        del Preamble['ModuleCurrent']
        del Preamble['ModulePrevious']
        del Preamble['ParkingLot']['SelectedWidreq']
        del Preamble['Geometry']
        for W in Preamble['ParkingLot']['Widreqs']:
            del W['XY']
        for ModuleInfo in Project[1:]:
            del ModuleInfo['SelectedForm']
            del ModuleInfo['VisibleForm']
            del ModuleInfo[GblMainName]['Text']
            del ModuleInfo[GblMainName]['Cursor']
            for Form in ModuleInfo['Forms']:
                del Form['Requested']
                del Form['SelectedWidreq']
                del Form['Text']['Text']
                del Form['Text']['Cursor']
                for W in Form['Widreqs']:
                    del W['XY']
        return Project        
            
    def VetOptionValues(self,WidreqList,ModuleName,FormName):
        """
        Verify that options mentioned have valid values.
        
        "WidreqList is a list of <widreq-descriptors>
        
        We check each widreq in the list to verify that any options used have valid values. If not
            we reset that option to the default value. The result is a list of tuples, one per
            option reset. Each tuple contains six text strings giving:
            [0] The module name as passed to us
            [1] The form name as passed to us
            [2] The name of the widget in the form eg MyButton
            [3] The name of the offending option
            [4] The original as-received value of the option
            [5] The now as-revised value of the option            
        """
        class NoDice(Exception): pass
        Result = []
        for Widreq in WidreqList:
            WidreqName = Widreq['Name']
            WidreqKind = Widreq['WidgetName']
            DonorModule = Widreq['ModuleName']
            Temp = range(len(Widreq['Options']))
            Temp.reverse()
            for J in Temp:
                Option = Widreq['Options'][J]
                Type,Default,Current,Extra = Cfg.Info['Modules'][DonorModule]['Widgets'][WidreqKind]['Options'][Option['Name']]
                try:
                    Value = Option['Value']
                    if Cfg.Info['BuiltinOptions'].has_key(Type):
                        if Value == None:
                            #Validators work on strings
                            Value = ''
                        R = Cfg.Info['BuiltinOptions'][Type]['Validate'](Value,Type)
                        if R[0] <> 1:
                            #The validation didn't fly
                            raise NoDice
                    elif Cfg.Info['EnumeratedOptions'].has_key(Type):
                        #Enumerated type. Make sure the default value is one of the specified end-values.
                        Enu = Cfg.Info['EnumeratedOptions'][Type]
                        if not Value in Enu.values():
                            raise NoDice
                    else:
                        raise Exception, "Type unexpectedly not found: "+Type        
                except NoDice:
                    #The current value didn't validate
                    Widreq['Options'][J]['Value'] = Default
                    Result.append((ModuleName,FormName,WidreqName,Option['Name'],str(Value),str(Default)))
        return Result            

    def VetOptionsExist(self,WidreqList,ModuleName,FormName):
        """
        Verify that options mentioned in widreqs exist in the config file.
        
        "WidreqList" is a list of <widreq-descriptors>
        
        We check each widreq in the list to verify that any options used are options we know about from
            the config file. If not, we delete the unknown option. The result is a list of tuples, one
            tuple per each deleted option. Each tuple contains five text strings giving:
            [0] The module name as passed to us
            [1] The form name as passed to us
            [2] The widget type (eg Button)
            [3] The name of the widget in the form (eg MyButton)
            [4] The option which was deleted.
        """
        Result = []
        for Widreq in WidreqList:
            WidreqName = Widreq['Name']
            WidreqKind = Widreq['WidgetName']
            DonorModule = Widreq['ModuleName']
            Temp = range(len(Widreq['Options']))
            Temp.reverse()
            for J in Temp:
                Option = Widreq['Options'][J]
                AvailableOptions = Cfg.Info['Modules'][DonorModule]['Widgets'][WidreqKind]['Options'].keys(SeeAll=True)
                if not Option['Name'] in AvailableOptions:
                    Result.append((ModuleName,FormName,Widreq['WidgetName'],WidreqName,Option['Name']))
                    Widreq['Options'].pop(J)
        return Result            

    def VetWidgetsExist(self,WidreqList):
        """
        Verify that specified widgets exist in the config file.
        
        "WidreqList" is a list of <widreq-descriptors>
        
        We check that each widreq in the list corresponds to a widget described by the config file.
            If the widreq is *not* described by the config file then we add an entry to the result and
            remove that <widget-descriptor> from WidreqList. The result is a list of tuples, where
            each tuple gives:
            [0] The widget type (eg Tkinter.Button)
            [1] The widget name (eg MyButton)
        """
        Result = []
        Temp = range(len(WidreqList))
        Temp.reverse()
        for J in Temp:
            Widreq = WidreqList[J]
            WidreqName = Widreq['Name']
            WidreqKind = Widreq['WidgetName']
            DonorModule = Widreq['ModuleName']
            if not Cfg.Info['Modules'][DonorModule]['Widgets'].has_key(WidreqKind):
                Result.append(('%s.%s'%(DonorModule,WidreqKind),WidreqName))
                WidreqList.pop(J)
        return Result            

    def ProjectLoad(self,ProjectPath=None):
        """=m
        Load a new project.
        
        If no "ProjectPath" is given we prompt for one. If supplied, "ProjectPath" should
            be the full path, complete with extension.
        
        The result is an integer in the range 0..2:
            o 0 - A project was successfully loaded.
            o 1 - The user declined to load a project.
            o 2 - Error while loading project; existing project state unknown.
            
        A note about the loading of gui editors. Each form has a gui editor. The simple minded
            way of loading these (and the way that in fact happens if you don't set
            "GblLoadInProgress" to True below) is to have each editor create and populate
            itself with lines and widreqs as we load. While this works just fine in a
            theoretical sense, it also involves a whole lot of flashing and honking on the
            screen as every gui editor in the entire project gets built before your eyes.
            With small projects this isn't much of an issue; for large projects consisting
            of dozens of forms it gets annoying. If "GblLoadInProgress" is set to true then
            we do things a bit differently. At form create time the gui editor is set to
            None and we take the pickled form information (which was originally produced 
            by a gui editor's "Gather" method) and save it in the form information of the
            repository as ['LoadInfo']. When the user goes to call up this gui editor, the
            editor packer notes that the gui editor is "None", creates and populates a
            gui editor and then sets ['LoadInfo'] to None. At this point we are back to
            normal. 
            
            This has implications at save time. At save time for a normal gui editor we
            call it's Gather method to get a dictionary of information suitable for saving.
            If the user has loaded a project and never called up a particular gui editor, 
            then there is no gui editor but there is the "LoadInfo" which was produced by
            a Gather at some point in the past. Since it is exactly the information we
            want, we simply use it as the data we save. It's sort of a 'gui editor on
            demand' thing.
            
            At load time we arbitrarily say that the selected editor is the gui editor.    
            There are a number of circumstances where the gui editor *must* exist and if 
            you allow the text editor to be selected when a form is first shown then some
            things will break. As long as the form isn't the selected form then having the 
            gui latent is ok, but once it is the selected form then it really should exist.
            For a while I tried putting in code that would ensure the gui sprang into
            existence prior to those places where it was needed but that caused an 
            apparently unnecessary flash on the screen and got pretty clunky and I kept
            finding new cases. Saying that we always start with the gui solves the problem
            nicely and doesn't seem to be an undue burden on the user.
        """
        global GblPreviousModule, GblLoadInProgress, GblLastSavedProject, GblProjectDirectory
        global GblProjectInfo
        if ProjectPath == None:
            Dir = Cfg.Info['DefaultDir']
            if Dir == '*' or not os.path.isdir(Dir):
                #Either the config said to use the current working directory or the directory
                #    the config specified does not exist.
                Dir = os.getcwd()
            ProjectPath = tkFileDialog.askopenfilename(parent=self._Win
                ,initialdir=Dir
                ,filetypes=(('Rapyd Project','.rpj'),('All files','*'))
                ,title='Load project')
            if not ProjectPath:
                #User bailed
                return 1
        TheDir, TheFile = os.path.split(ProjectPath)
        GblProjectInfo = None
        #
        # Setup the exception we want to catch
        #
        if Cfg.Info['Debug']:
            #If in debug mode we want to leave exceptions uncaught so we can
            #    seen them where and as they happen. Therefore we create a dummy
            #    exception (which will never get raised) and setup to catch that.
            class Dummy(Exception): pass
            ExceptionToCatch = Dummy
        else:
            #If in non-debug mode then we want to catch all exceptions so if things
            #    go wrong we give the user a polite message and carry on.
            ExceptionToCatch = Exception    
        #
        # Fetch the pickled project
        #
        try:
            F = open(ProjectPath)
            Project = cPickle.load(F)
            F.close()
            ProjectInfo = Project[0]
            if ProjectInfo['ID'] <> 'Rapyd Project':
                raise Exception, 'Not a rapyd project'        
            if ProjectInfo['Version'] <> 0:
                raise Exception, 'Version conflict'
            if ProjectInfo.has_key('EditorWidths'):    
                self.TheWidgetator.WidthsSet(ProjectInfo['EditorWidths'])
            Root.geometry(ProjectInfo['Geometry'])    
            Cfg.Info['ProjectDir'] = TheDir
            GblLoadInProgress = True
            self.LayoutNotebook.Clear()
            ProjectName = os.path.splitext(TheFile)[0]
            self.ProjectNewBuild(ProjectName,TheDir)
            #Populate the parking lot
            self.ParkingLot.Scatter(ProjectInfo['ParkingLot'])
            #We don't yet know the target widreq
            TargetWidreq = None

            # When the project was saved we noted the ImportType for each of the
            #     widget donor modules (eg Tkinter, Pmw). If the import status as specified
            #     by the config file is now different than it was when we saved the project then
            #     we must regenerate the creation code for each form and the user may have some
            #     work to do too. Here we check both for donor modules of changed import type
            #     and for donor modules that went away totally.
            MustRegenerate = False
            ChangeList = []
            MissingList = []
            if ProjectInfo.has_key('ImportTypes'):
                for ModuleName,SavedImportType in ProjectInfo['ImportTypes']:
                    if Cfg.Info['Modules'].has_key(ModuleName):
                        #The moduled mentioned at save time is still in use
                        CurrentImportType = Cfg.Info['Modules'][ModuleName]['ImportType']
                        if SavedImportType <> CurrentImportType:
                            #But it's import type has changed
                            ChangeList.append((ModuleName,SavedImportType,CurrentImportType))
                    else:
                        #The module mentioned at save time is no longer in use
                        MissingList.append(ModuleName)        
            #Look after missing donor modules
            AlteredFormDict = {}
            if MissingList:
                #We have at least one missing module. Although it's missing, it may be one that
                #    this project didn't use. Scan all of our modules to get a dictionary of all
                #    the donor modules used by this project.
                DonorModuleDict = {}
                for OneModule in Project[1:]:
                    DonorModuleDict.update(DonorModulesUseScan(OneModule))
                #In DonorModuleDict the key is the name of a donor moduled used by this project while
                #    the value is a number of no particular significance here.
                #Delete any values from MissingList which are not used in this module
                for J in range(len(MissingList)):
                    if not MissingList[J] in DonorModuleDict.keys():
                        MissingList.pop(J)
                if MissingList:
                    MissingAsString = ', '.join(MissingList)        
                    #Any values still in MissingList represent donor modules missing and used by this project.
                    Msg = ('This project contains one or more widgets from the module{/s} "%s" and'
                        ' {that/those} module{/s} {was/were} available the last time the project was saved.'
                        ' However, {that/those} module{/s} {is/are} not available now because the config'
                        ' file did not make {it/them} available. It seems likely that either you changed the'
                        ' config file since the last time you saved this project or you got this project'
                        ' from a different Rapyd installation. In any case the project is not loadable'
                        ' in its present state'
                        ' because it references widgets currently unknown to me.\n\nIf you choose "delete'
                        ' widget references" I will delete all references to the widgets from the missing'
                        ' module{/s} which will allow me to carry on with the load. Deleting these widgets'
                        '  may break a lot of the project but'
                        ' it\'s your call. Alternately you can cancel loading of this project. Click on'
                        ' "Help" to get a full list of the missing widgets and where they are used.'
                        %MissingAsString)
                    Msg = rpHelp.Plural(Msg,len(MissingList))    
                    Arg = DonorModuleUseReport(Project,MissingList)
                    MissingModuleCount = len(MissingList)
                    WidgetInstanceCount = Arg.count('\n')-1
                    HelpTuple = ('load.missing.widgets'
                        ,[Arg,MissingModuleCount,WidgetInstanceCount,MissingAsString,'project'])
                    R = Rpw.MessageDialog(Message=Msg,Help=HelpTuple,Widget=self._Win
                        ,Buttons=(('Delete Widgets',1),('~Cancel',None))).Result
                    if R == None:
                        #User cancelled
                        return 1    
                    elif R == 1:
                        #Delete the widgets that were from the missing modules. For later use by the code
                        #    regenerator we create a dictionary where the key is a tuple of (ModuleName,FormName)
                        #    for each form from which we delete one or more modules.
                        for ModuleDescriptor in Project[1:]:
                            Pmodule = ModuleDescriptor['Name']
                            for FormInfo in ModuleDescriptor['Forms']:
                                Temp = range(len(FormInfo['Widreqs']))
                                Temp.reverse()
                                for J in Temp:
                                    Widreq = FormInfo['Widreqs'][J]
                                    Dmodule = Widreq['ModuleName']
                                    if Widreq['ModuleName'] in MissingList:
                                        AlteredFormDict[(Pmodule,FormInfo['Name'])] = None
                                        FormInfo['Widreqs'].pop(J)
                    
            #Look after donor modules that changed import-type
            if ChangeList:
                #We have at least one changed module. Although it's changed, it may be one that
                #    this project didn't use. Scan all of our modules to get a dictionary of all
                #    the donor modules used by this project.
                DonorModuleDict = {}
                for OneModule in Project[1:]:
                    DonorModuleDict.update(DonorModulesUseScan(OneModule))
                #In DonorModuleDict the key is the name of a donor moduled used by this project while
                #    the value is a number of no particular significance here.
                #Delete any values from ChangeList which are not used in this module
                for J in range(len(ChangeList)):
                    if not ChangeList[J][0] in DonorModuleDict.keys():
                        ChangeList.pop(J)
                if ChangeList:
                    ChangeAsString = ', '.join([X[0] for X in ChangeList])        
                    #We have changed modules which were in fact used.
                    Msg = ('This project uses widgets from {the/these} module{/s} "%s" but in'
                        ' the config file the import type of'
                        ' {that/those} modules{/s} is different than it was the last time the project was'
                        ' saved. It seems likely that either you changed the config file since the last time'
                        ' you saved this project or you got this project from a different Rapyd installation.'
                        '\n\nThis is not a problem since I will update all the Rapyd-maintained code to'
                        ' reflect the current import-type setting.'
                        ' Just press "Continue" and sit back until load is complete.'
                        ' Either that or press "Cancel" to cancel loading of this'
                        ' project.\n\nBear in mind that while all the Rapyd maintained code will be updated'
                        ' automatically, any user supplied code that references anything from {this/these}'
                        ' module{/s} will have to be adjusted accordingly by hand.'%ChangeAsString)
                    Msg = rpHelp.Plural(Msg,len(ChangeList))    
                    Arg = [' Module     At-save    Now',' ------     -------    ----']
                    for Temp in ChangeList:
                        Arg.append(' %-10s %-10s %s'%Temp)
                    Arg = '{f' + ('\n'.join(Arg)) + '}'    
                    HelpTuple = ('load.changed.importtype',[Arg,len(ChangeList),'project'])
                    R = Rpw.MessageDialog(Message=Msg,Widget=self._Win,Help=HelpTuple
                        ,Buttons=(('Continue',1),('~Cancel',None))).Result
                    if R == None:
                        return 1
            
            #Verify that widgets used in the project are widgets we have available
            MissingWidgetList = [('Module','Form','Widget type','Widget name'),
                                 ('------','----','-----------','-----------')]
            MissingWidgetCount = 0
            for ModuleDescriptor in Project[1:]:
                ModuleName = ModuleDescriptor['Name']
                for FormDescriptor in ModuleDescriptor['Forms']:
                    FormName = FormDescriptor['Name']
                    Temp = self.VetWidgetsExist(FormDescriptor['Widreqs'])
                    #Temp is a list of widgets that are not available in the current
                    #    config as (widget-type, widget-name)
                    if Temp:
                        for T in Temp:
                            MissingWidgetList.append((ModuleName,FormName,T[0],T[1]))
                            MissingWidgetCount += 1
            if MissingWidgetCount:
                Msg = ('The project you are attempting to load contains {a /}reference{/s} to{ a/}'
                    ' widget{/s} which {is/are} unknown to me. This suggests that you made changes'
                    ' to the config file, or the project being loaded came from a different Rapyd'
                    ' installation. In any case the project is unloadable as it currently stands.'
                    '\n\nIf you choose "delete widgets" I will delete all reference{/s}'
                    ' to the unknown widget{/s}, which will allow me to carry on with the load.'
                    ' Deleting {this/these} widget{/s} may beak a lot of the project but it\'s your'
                    ' call. Alternately you can cancel loading of this project. Click on "Help" to'
                    ' get a full information about the missing widget{/s}.')
                Msg = rpHelp.Plural(Msg,MissingWidgetCount)
                Arg = '{f' + Rpw.Columnate(MissingWidgetList,Lmarg=1,Spacing=2) + '}'
                R = Rpw.MessageDialog(Message=Msg,Help=('load.widgets.missing',[MissingWidgetCount,Arg,'project'])
                    ,Widget=self._Win,Buttons=(('Delete widgets',None),('~Cancel',1))).Result
                if R == 1:
                    return 1

            #Here we verify the option types and values for all option settings of all widgets.
            #    What we are looking for is saved options which no longer exist in the config
            #    file and for option values which are not valid per the config file. Options
            #    which no longer exist are simply deleted while options with invalid values are
            #    set to the default value. In either case we make sure the module/form is mentioned
            #    in AlteredFormDict since that prompts regeneration of the code of that form.
            DeletedOptionCount = 0
            ResetOptionCount = 0
            DeletedOptionList = [('Module','Form','Widget type','Widget name','Option'),
                                 ('------','----','-----------','-----------','------')]
            ResetOptionList = [('Module','Form','Widget','Option','Original','Revised'),
                               ('------','----','------','------','--------','-------')]                     
            for ModuleDescriptor in Project[1:]:
                ModuleName = ModuleDescriptor['Name']
                for FormDescriptor in ModuleDescriptor['Forms']:
                    FormName = FormDescriptor['Name']
                    Temp = self.VetOptionsExist(FormDescriptor['Widreqs'],ModuleName,FormName)
                    DeletedOptionList.extend(Temp)
                    DeletedOptionCount += len(Temp)
                    if Temp:
                        AlteredFormDict[(ModuleName,FormName)] = None
                    Temp = self.VetOptionValues(FormDescriptor['Widreqs'],ModuleName,FormName)
                    ResetOptionList.extend(Temp)
                    ResetOptionCount += len(Temp)
                    if Temp:
                        AlteredFormDict[(ModuleName,FormName)] = None
            if DeletedOptionCount:
                Msg = ('In the course of loading the project I found %s instance{/s}'
                    ' of {a }widget option{/s} which existed when the project was last saved but'
                    ' which (according to the current config file) {does/do} not exist now. The option{/s} in'
                    ' question {has/have} been deleted. This is merely an advisory; no action on your'
                    ' part is required. Click on "Help" for details.')
                Msg = rpHelp.Plural(Msg,DeletedOptionCount)    
                Arg = '{f' + Rpw.Columnate(DeletedOptionList,Lmarg=1,Spacing=2) + '}'
                R = Rpw.MessageDialog(Message=Msg,Help=('load.options.missing',[Arg,'project'])
                    ,Widget=self._Win,Buttons=(('OK',None),('~Cancel',1))).Result
                if R == 1:
                    return 1
            if ResetOptionCount:
                Msg = ('In the course of loading the project I found %s instance{/s}'
                    ' of {a }widget option{/s} with an invalid value'
                    ' (according to the current config file). The option{/s} in'
                    ' question {has/have} been set to {its/their} default value. This is merely'
                    ' an advisory; no action on your'
                    ' part is required. Click on "Help" for details.')
                Msg = rpHelp.Plural(Msg,ResetOptionCount)    
                Arg = '{f' + Rpw.Columnate(ResetOptionList,Lmarg=1,Spacing=2) + '}'
                R = Rpw.MessageDialog(Message=Msg,Help=('load.options.reset',[Arg,'project'])
                    ,Widget=self._Win,Buttons=(('OK',None),('~Cancel',1))).Result
                if R == 1:
                    return 1
            #
            # Now that all that pain-in-the-ass checking is done lets load the actual project.
            #    
            MD = Rpw.MessageDialog(Message='Loading...',Modal=False,Widget=self._Win)
            self._Win.update_idletasks()
            for OneModule in Project[1:]:
                #Process one module
                ModuleName = OneModule['Name']
                if ModuleName == ProjectInfo['ProjectName']:
                    #This is the main module which already exists; select it
                    self.ModuleSelect(ProjectName)
                else:
                    #This is not the main module. Build and select new module.
                    self.ModuleNewBuild(OneModule['Name'])
                try:    
                    Repo.PreviousForm = OneModule['PreviousForm']    
                except KeyError:
                    Repo.PreviousForm = None    
                #
                # Main text area
                #
                assert 1==Repo.Request(self.WRID,'HerdSelect',GblMainName)
                FI = Repo.FetchForm()
                FI['Text'].TextWidget.Scatter(OneModule[GblMainName])
                #Restore the main code areas tab status
                FI['OnTab'] = OneModule['OnTab']
                if not OneModule['OnTab']:
                    #This form is not to be on a tab
                    self.LayoutNotebook.Delete(GblMainName)
                #
                # Forms
                #     
                for Info in OneModule['Forms']:
                    if ProjectInfo['ModuleCurrent'] == ModuleName:
                        #We are the module that is to be made current.
                        if Info['Name'] == OneModule['SelectedForm']:
                            #We are the herd that is to be selected
                            TargetWidreq = Info['SelectedWidreq']
                    self.FormLoad(Info)
                #Restore the widreq selection
                #print Repo.Request(self.WRID,'WidreqSelect',SelectedWidreq)    
                #
                # Select specified 'selected' form
                #
                self.LayoutNotebook.Select(OneModule['VisibleForm'])
                assert 1==Repo.Request(self.WRID,'HerdSelect',OneModule['SelectedForm'])    
                if ProjectInfo['ModuleCurrent'] == ModuleName:
                    #We are the module that is to be made current.
                    #Note the herd and form that we should select
                    TargetHerd = OneModule['SelectedForm']
                    TargetForm = OneModule['VisibleForm']

            GblLoadInProgress = False

            #Ok, that was fun. Gather up a copy of the project, less
            #    non-essential stuff so we can later see if the project has changed.
            GblLastSavedProject = self.ProjectPrune(self.ProjectGather())
            GblProjectDirectory = TheDir
            if GblProjectDirectory:
                GblProjectDirectory += '/'

            #If one or more forms must have their code regenerated do so now.
            #At this point AlteredFormDict is a dictionary whose keys are tuples of (ModuleName,FormName) for
            #    each project module/form in which we made changes while ChangeList is a list of tuples
            #    each of which is (ModuleName,SavedImportMode,CurrentImportMode).
            #    Having arrived here if either of these  isn't empty then we need to regenerate the code
            #    of any form if it contains widgets from a module whose import type has changed, or if it had
            #    widgets deleted from it.
            if ChangeList or AlteredFormDict:
                #Force project to look changed
                GblLastSavedProject = None
                ChangedModules = [X[0] for X in ChangeList]
                for ModuleDescriptor in Project[1:]:
                    ModuleName = ModuleDescriptor['Name']
                    for FormDescriptor in ModuleDescriptor['Forms']:
                        Count = 0
                        FormName = FormDescriptor['Name']
                        for Widget in FormDescriptor['Widreqs']:
                            if Widget['ModuleName'] in ChangedModules:
                                Count += 1
                        if Count > 0 or (ModuleName,FormName) in AlteredFormDict.keys():
                            #This form used widgets from a module which changed import type or we deleted widgets from it    
                            #Select the necessary module
                            self.ModuleSelect(ModuleName)
                            #Select the necessary form
                            self.FormRaise(FormName)
                            self.EditorPack(ForceEditor='Gui')                    
                            self.CreationSystextRegen('Project load')    

            #
            # Select current module
            #        
            self.ModuleSelect(ProjectInfo['ModuleCurrent'])
            GblPreviousModule = ProjectInfo['ModulePrevious']
            if GblPreviousModule == ProjectInfo['ProjectName']:
                #This looks after the case where the main module of the project is the noted
                #    'PreviousModule' AND the user used the OS to rename the project prior
                #    to loading it.
                GblPreviousModule = ProjectName
            #
            # Select the currently visible form of the current module
            #    
            if TargetForm <> None:
                assert 1==Repo.Request(self.WRID,'HerdSelect',TargetForm)
                #Have the correct editor appear for the user
                self.EditorPack()
            #
            # Select the target herd
            #    
            if TargetHerd <> None:
                Repo.Request(self.WRID,'HerdSelect',TargetHerd)
            #
            # Select the target widreq
            #    
            #It is possible we have no selected widreq. This happens if the parking lot is
            #    selected but has no widreqs of if -Main- is selected since it has no gui.
            if TargetHerd == 'the Parking Lot':
                TargetWidreq = ProjectInfo['ParkingLot']['SelectedWidreq']
            if TargetWidreq <> None:    
                Repo.Request(self.WRID,'WidreqSelect',TargetWidreq)                
                #We don't check for failure to select here because if the previously selected widreq
                #    was one which we deleted because it's donor module went away then it is not
                #    available to select but no harm is done.
            #Provoke the widgetator into updating the current editor    
            self.TheWidgetator.ModuleChange()
            
            #
            MD.Close()
            return 0
        except ExceptionToCatch, Message:
            #See note at top of the "try" as to what "ExceptionToCatch" is about.
            GblLoadInProgress = False
            try:
                MD.Close()
            except:
                #MD may not exist yet.
                pass    
            Rpw.MessageDialog(Message='An error was encountered while attempting to load the project.'
                ,Widget=self._Win)
            return 2

    def FormLoad(self,Info):
        """
        Add a pre-existing form to the project.
        
        This is used for both project-load and from-import.
        
        "Info" is the dictionary of information about the form that was saved about the form.
        """
        #Create the form
        self.FormCreateNew({'Name':Info['Name'],'Type':Info['Type']
            ,'BaseClass':Info['BaseClass']})
        assert 1==Repo.Request(self.WRID,'HerdSelect',Info['Name'])    
        FI = Repo.FetchForm()
        #Restore the form's tab status
        FI['OnTab'] = Info['OnTab']
        
        if not Info['OnTab']:
            #This form is not to be on a tab
            self.LayoutNotebook.Delete(Info['Name'])
        
        #Build the widreq instances
        for WidreqInfo in Info['Widreqs']:
            if WidreqInfo['ID'] == (0,):
                #The outermost frame was already created by "FormCreateNew" so
                #    we don't need to create it again. We do need to set its
                #    option and bind settings.
                assert WidreqInfo['Name'] == Info['Name']
                Widreq = Repo.Fetch(WidreqInfo['Name'])
                Widreq.SetOptions(WidreqInfo['Options'])
                Widreq.SetBindings(WidreqInfo['Bindings'])
                continue
            WidreqName = WidreqInfo['Name']
            #Build the actual widreq instance
            W = WidReq(WidgetName=WidreqInfo['WidgetName']
                      ,InstanceName=WidreqName
                      ,FrameID=WidreqInfo['ID']
                      ,PresentHome=Info['Name']
                      ,OptionList=WidreqInfo['Options']
                      ,BindingList=WidreqInfo['Bindings']
                      ,PackOptionList=WidreqInfo['PackOptions']
                      ,ModuleName=WidreqInfo['ModuleName'])
            #Add it to the repository          
            assert 1==Repo.Request(self.WRID,'WidreqCreate',WidreqInfo['Name'],W)
        #Restore the widreq selection if we have one
        if Info['SelectedWidreq']:
            #D(repr(Info['SelectedWidreq']))
            R = Repo.Request(self.WRID,'WidreqSelect',Info['SelectedWidreq'])    
            #We don't check for failure to select here because if the previously selected widreq
            #    was one which we deleted because it's donor module went away then it is not
            #    available to select but no harm is done.
        if GblLoadInProgress:
            #Were operating in quiet mode. When we created the form, no gui editor was built 
            #    because we are in mid-load. Here we save the gathered form information 
            #    pulled from the pickled project. It will be used to populate the form the 
            #    first time the gui editor is called for.
            FI['LoadInfo'] = Info
        else:
            #Were in noisy mode; create the gui right now
            FI['Gui'].CanvasConfigure(Info)    
        #Have the text editor set it's text
        FI['Text'].TextWidget.Scatter(Info['Text'])
        #Set the requested editor
        FI['Requested'] = Info['Requested']
        #Note! Regardless of what the user may have been looking at when they saved
        #    the project we here select the gui editor. There are a number of
        #    circumstances where the gui editor *must* exist and if you allow the
        #    text editor to be selected when a form is first shown then some
        #    things will break. As long as the form isn't the selected form then
        #    having the gui latent is ok, but once it is the selected form then
        #    it really should exist.
        FI['Requested'] = 'Gui'

    def FormTextDecode(self,Text,Indent=0,ShowText=False):
        """
        Given a dictionary of gathered text, decode it.
        
        The result is a LIST of text strings.
        
        Each line is indented as specified by indent.
        If "ShowText" is false then we simply list the number of
            lines of text, not the actual text.
        """
        R = []
        I = Indent * ' '
        R.append(I + 'Version: %s'%Text['Version'])
        R.append(I + 'Cursor: %s'%Text['Cursor'])
        if ShowText:
            R.append(I + 'ActualText...')
            I += '    '
            Mark = 's '
            for Clump in Text['Text']:
                for Line in Clump.split('\n'):
                    R.append(I+Mark+Line) 
                if 's' in Mark:
                    Mark = '| '
                else:
                    Mark = 's '    
        else:
            Count = 0
            for Clump in Text['Text']:
                Count += Clump.count('\n')
            R.append(I + '%s lines of text omitted'%Count)        
        return R        

    def FormDecode(self,Form,Indent=0):
        """
        Given a dictionary of form information return a string representing it.
        
        Each line is indented as specified by Indent.
        """
        R = []
        I = Indent * ' '
        R.append(I + 'BaseClass: %s'%Form['BaseClass'])
        R.append(I + 'Lines...')
        for Line in Form['Lines']:
            R.append(I + '    X: %5d Y:%5d Dirn:%s'%tuple(Line))
        R.append(I + 'OnTab: %s'%Form['OnTab'])
        R.append(I + 'Requested: %s'%Form['Requested'])
        R.append(I + 'SelectedWidreq: %s'%Form['SelectedWidreq'])
        R.append(I + 'Type: %s'%Form['Type'])
        R.append(I + 'Code...')
        R += self.FormTextDecode(Form['Text'],Indent=Indent+4)
        for Widreq in Form['Widreqs']:
            R.append(I + 'Widreq %s...'%Widreq['Name'])
            R += self.WidreqDecode(Widreq,Indent=Indent+4)
        return R    

    def WidreqDecode(self,W,Indent=0):
        """
        Given a dictionary of widreq information return a string representing it.
        
        Each line is indented as specified by Indent.
        """
        R = []
        I = Indent * ' '
        R.append(I + 'WidgetName: %s'%W['WidgetName'])
        R.append(I + '[Import]ModuleName: %s'%W['ModuleName'])
        R.append(I + 'XY: %s %s'%tuple(W['XY']))
        R.append(I + 'Options...')
        for Option in W['Options']:
            R.append(I + '    %s %s %s'%(Option['Name'], Option['Value'], Option['Extra']))
        R.append(I + 'Bindings...')    
        for Bind in W['Bindings']:
            R.append(I + '    %s %s %s'%(Bind['Event'],Bind['Handler'],Bind['Component']))
        R.append(I + 'Pack options...')
        for Pack in W['PackOptions']:    
            R.append(I + '    %s %s'%(Pack['Name'],Pack['Value']))
        return R    

    def ProjectDecode(self,Project):
        """
        Given a project object, return a string that represents it.
        
        A 'project object' is the thing we pickle and then save as an rpj file.
        
        A project is a list. The first item in the list is a bunch of fixed information
            while each subsequent item is a gathered module.
        
        """
        R = []
        Preamble = Project[0]
        R.append('--- Preamble ---')
        R.append('    ID: %s'%Preamble['ID'])
        R.append('    ProjectName: %s'%Preamble['ProjectName'])
        R.append('    Geometry: %s'%Preamble['Geometry'])
        R.append('    ModuleCurrent: %s'%Preamble['ModuleCurrent'])
        R.append('    ModulePrevious: %s'%Preamble['ModulePrevious'])
        R.append('    Version: %s'%Preamble['Version'])
        R.append('    ImportTypes: %s'%Preamble['ImportTypes'])
        R.append('    EditorWidths: %s'%str(Preamble['EditorWidths']))

        R.append('    the Parking lot...')
        R.append('        SelectedWidreq: %s'%Preamble['ParkingLot']['SelectedWidreq'])
        for Widreq in Preamble['ParkingLot']['Widreqs']:
            R.append('        Widreq %s...'%Widreq['Name'])
            R += self.WidreqDecode(Widreq,Indent=12)

        for Module in Project[1:]:
            R.append('--- Module: %s ---'%Module['Name'])
            R.append('    SelectedForm: %s'%Module['SelectedForm'])
            R.append('    VisibleForm: %s'%Module['VisibleForm'])
            R.append('    PreviousForm: %s'%Module['PreviousForm'])
            R.append('    OnTab: %s'%Module['OnTab'])
            R.append('    Main text area...')
            R += self.FormTextDecode(Module['-Main-'],Indent=8)
            for Form in Module['Forms']:
                R.append('    Form %s...'%Form['Name'])
                R += self.FormDecode(Form,Indent=8)
        R.append('--- End Of Project ---')
        return '\n'.join(R)        
    
    def SaveOption(self,Operation):
        """
        If the project has changed, give the user the chance to save it.
        
        The result is normally 0. We return 1 if the project has changed AND
            the user asked to cancel whatever operation prompted the call
            to this method.
        
        "Operation" is a string indicating the operation in progress which
            the user may elect to cancel, eg "Load", "New, "Quit".
        """
        
        Now = self.ProjectPrune(self.ProjectGather())
        if Now <> GblLastSavedProject:
            ##D('Comparing A (current project) with B (original project):')
            ##D(DiffFind(Now,GblLastSavedProject))
            R = Rpw.MessageDialog(Title='Last Chance'
                ,Message='The project has been changed since the last save.'
                ,Buttons=(('Save now',1),('Lose changes',0),('~Cancel %s'%Operation,None))).Result
            assert R in (0,1,None)    
            if R == None:
                #User asked to cancel 
                return 1
            if R == 1:
                self.ProjectSave()
        return 0        

    def ProjectSave(self):
        """
        Save the project.
        """
        global GblLastSavedProject
        
        #Gather the project into a list
        Project = self.ProjectGather()
        
        #Pickle it to disk
        FN = '%s%s'%(GblProjectDirectory,Cfg.Info['ProjectName'])
        F = open(FN+'.$$$','w')
        cPickle.dump(Project,F)
        F.close()
        
        BackupMode = Cfg.Info['Backup']
        if BackupMode == 0:
            os.rename(FN+'.$$$', FN+'.rpj')
        elif BackupMode == 2:    
            Rpw.GeneralizedSaveFinalizeNumeric(FN+'.rpj')
        else:
            rpHelp.GeneralizedSaveFinalize(FN+'.rpj')

        #If were in debug mode, generate a decoded version of the project in a tex file.
        if Cfg.Info['Debug']:
            F = open(FN+'.txt','w')
            F.write(self.ProjectDecode(Project))
            F.close()
        
        #Prune out non-essential stuff so we can later tell if
        #    the project has been modified.
        GblLastSavedProject = self.ProjectPrune(Project)


    def ModuleBuild(self,ModuleName):
        """
        Build the code file for the specified module.
        
        The -Main- code area of a module consists of five chunks (if it's the main
            module of the project):
        
            o [0] usertext prior to the import lines, including the shebang line.
            o [1] the systext import lines
            o [2] usertext between the import in the init lines
            o [3] the systext init line(s)
            o [4] usertext after the import lines.
                  
            or three chunks (if it's an additional module of the project):
            
            o [0] Usertext prior to the import lines
            o [1] The systext import lines
            o [2] The usertext after the import lines. 
              
         The file we generate consists of:
         
            o Chunk zero
            o The import lines
            o Code from all the forms in alphabetic order
            o Chunks 2, 3 and 4

        Note: We need to set "Repo" to be be module in question, but we don't
            want to actually select the module since that implies a lot of
            (unnecessary for the purpose at hand) screen activity. So we
            remember the original Repo setting and restore it on exit.    
            
        The result is a tuple of:
            [0] Count of lines of code in the module
            [1] Locator list.

        In Locator list each element is a 3-tuple:
        
            o The name of the form or '-Main-'
            o The offset in lines to where the first line from this form appears
                  in the generated file.
            o The number of lines from this form which appear in the generated form
                  at this spot.
                  
            The point of the locator list is to allow us, given a line number in the
            generated file, to locate the corresponding form and line number in this
            module.                
        """
        global Repo
        OriginalRepo = Repo        

        Repo = GblModules[ModuleName]
        Locator = []
        LineCount = 0
        #
        # The import lines
        #

        # Our first task is to generate the necessary import lines. To do that we
        #     must scan every widreq of every form and make a note of the import
        #     modules needed for the widreqs of this module. We use a dictionary
        #     because it's a handy way of handling duplicates
        ImportModuleDict = {'Tkinter':None}
        HerdList = Repo.ListHerds()
        for Herd in HerdList:
            if Herd in ('the Parking Lot',GblMainName):
                #Neither require action
                pass
            else:
                #This is an actual form.
                FI = Repo.FetchForm(Herd)
                if FI['Gui'] == None:
                    #No gui editor yet. This happens when a project is loaded but the
                    #    user never calls up the gui editor for a form.
                    assert FI['LoadInfo'] <> None
                    FormInfo = FI['LoadInfo']
                else:
                    #The gui editor exists; get the info from it.
                    FormInfo = FI['Gui'].Gather()
                #We have the gathered information about this form. Now root through it
                #    checking on the widreqs import modules.
                for WidreqData in FormInfo['Widreqs']:
                    ImportModuleDict[WidreqData['ModuleName']] = None

        ImportLines = GenerateImportLines(ImportModuleDict.keys())
        #Now use the generated  lines to update the main module
        IsMainModule = Cfg.Info['ProjectName'] == ModuleName
        FI = Repo.FetchForm(GblMainName)
        FI['Text'].TextWidget.SystextReplace('import rpErrorHandler',ImportLines)
        if IsMainModule:
            #If main module, look after the initialization lines.
            IndentAmount = Cfg.Info['Template'][3]
            InitLines = GenerateInitLines(ImportModuleDict.keys(),IndentAmount)
            FI['Text'].TextWidget.SystextReplace('Root =',InitLines)
        
        #
        # Fetch the three or five  sections of the -Main- text
        #
        
        #Gather produces a list of text chunks alternating systext,usertext. Since the -Main-
        #    code area opens with user text the first chunk is an empty string and what we
        #    are after is in the next three or five chunks.
        GatheredMainText = FI['Text'].TextWidget.Gather()['Text']
        Preamble = GatheredMainText[1]
        if IsMainModule:
            Postamble = '%s\n%s\n%s'%(GatheredMainText[3],GatheredMainText[4],GatheredMainText[5])
        else:
            Postamble = GatheredMainText[3]
        
        #
        # Open file and honk out the first two segments
        #
        LineCount += Preamble.count('\n')
        LineCount += ImportLines.count('\n')
        Filename = '%s%s.py'%(GblProjectDirectory,ModuleName)
        try:
            os.remove(Filename)
        except:
            pass    
        F = open(Filename,'w')
        F.write(Preamble)
        F.write(ImportLines)
        Offset = 0
        Len = Preamble.count('\n') + ImportLines.count('\n') 
        Locator.append(('-Main-',0,Len))        
        #
        # Then the text of the forms, in alphabetic order
        #
        Offset += Len
        HerdList.sort()        
        for Herd in HerdList:
            if Herd in ('the Parking Lot',GblMainName):
                #Neither require action
                pass
            else:
                #This is an actual form.
                FI = Repo.FetchForm(Herd)
                Text = FI['Text'].TextWidget.get('1.0',END)
                LineCount += Text.count('\n')
                F.write(Text)
                Len = Text.count('\n')
                Locator.append((Herd,Offset,Len))        
                Offset += Len
                
        #
        # And finally the postamble
        #
        LineCount += Postamble.count('\n')
        F.write(Postamble)
        Len = Postamble.count('\n')+1
        Locator.append(('-Main-',Offset,Len))

        F.close()
        Repo = OriginalRepo
        return (LineCount,Locator)

    def ModuleGather(self,ModuleName):
        """
        Return a <module-descriptor> of the specified module.
                
        Note: We need to set "Repo" to be be module in question, but we don't
            want to actually select the module since that implies a lot of
            (unnecessary for the purpose at hand) screen activity. So we
            remember the original Repo setting and restore it on exit.    
        """
        global Repo
        OriginalRepo = Repo        
        
        Result = {'Name':ModuleName}
        Repo = GblModules[ModuleName]
        HerdList = Repo.ListHerds()
        FormList = []
        for Herd in HerdList:
            if Herd == 'the Parking Lot':
                pass
            elif Herd == GblMainName:
                #for the main text area we just have text
                FI = Repo.FetchForm(Herd)
                Result[GblMainName] = FI['Text'].TextWidget.Gather()
                Result['OnTab'] = FI['OnTab']
            else:
                #We have a user defined form     
                FI = Repo.FetchForm(Herd)
                if FI['Gui'] == None:
                    #No gui editor yet. This happens when a project is loaded but the
                    #    user never calls up the gui editor for a form.
                    assert FI['LoadInfo'] <> None
                    FormInfo = FI['LoadInfo']
                else:
                    #The gui editor exists; get the info from it.
                    FormInfo = FI['Gui'].Gather()
                FormInfo['Text'] = FI['Text'].TextWidget.Gather()
                FormList.append(FormInfo)    
        Result['Forms'] = FormList
        Result['SelectedForm'] = Repo.SelectedHerd
        Result['PreviousForm'] = Repo.PreviousForm
        if Repo is OriginalRepo:
            #Were gathering the repo associated with visible stuff
            Result['VisibleForm'] = self.LayoutNotebook.GetCurSelection()
        else:
            #Were gathering a non-current repo    
            Result['VisibleForm'] = Repo.VisibleForm
        Repo = OriginalRepo
        return Result        

    def ApplicationTitleSet(self,ProjectName=None):
        """
        Set the title of the entire application.
        
        It "ProjectName" is given it is included in the title.
        """
        PN = ''
        if ProjectName:
            PN = 'Project: %s   '%ProjectName
	self._Win.title("     Rapyd-TK   Version %s   %s   "%(VersionNumber,PN))
        
    def ModuleNext(self,ModuleName):
        """
        Given a module name, return the next name in alphabetical order.
        
        If there is no next name, we return the very first name.
        """
        Names = GblModules.keys()
        Names.sort()
        I = Names.index(ModuleName) + 1
        if I >= len(Names):
            I = 0
        return Names[I]    

    def ModuleSelect(self,ModuleName,NotePrevious=True):
        """
        Select the specified module.
        
        It is the callers responsibility to be sure the requested module exists.
        
        If "NotePrevious" is True we save the name of the currently selected module
            in "GblPreviousModule" before we select the specified module.
        """
        global Repo, GblPreviousModule
        if ModuleName == Repo.ModuleName:
            #The requested module is already selected
            return
        if NotePrevious:    
            GblPreviousModule = Repo.ModuleName
        #Turn off all colorizers of the current module
        self.ColorizerOffAll()    
        #Note the visible tab in the outgoing module
        Repo.VisibleForm = self.LayoutNotebook.GetCurSelection()
        #Collect widreqs from the parking lot so we can transplant them to the new form
        ParkedWidreqs = self.ParkingLot.Gather()
        self.LayoutNotebook.Clear()
        #Retain the debug display option
        Debug = Repo.DebugSelectorGet()
        ##D('ModuleName=%s GblModules.keys()=%s'%(ModuleName,GblModules.keys()))
        #
        #
        #
        Repo = GblModules[ModuleName]
        #Insert parked widreqs in the newly selected repo
        self.ParkingLot.Scatter(ParkedWidreqs)
        self.ParkingLot.CanvasConfigure()
        self.ModuleNameUpdate()
        self.TheWidgetator.ModuleChange()        
        #Restore the requested layout area tabs
        for H in Repo.ListHerds():
            Form = Repo.FetchForm(H)
            if Form and Form['OnTab']:
                self.LayoutNotebook.Add(H,BulkAdd=True)
            else:
                pass
        #Restore the debug selection
        Repo.DebugSelectorSet(Debug)        
        self.LayoutNotebook.Select(Repo.VisibleForm)
        self.EditorPack()
        
    def ModuleNameUpdate(self):
        """
        Update the display of the current module name
        """
        self.ModuleIndicator['text'] = 'Module: %s'%(Repo.ModuleName)

    def CreationSystextRegen(self,WhoCalled):
        """
        Regenerate the creation systext of the currently selected form.
        
        The creation systext is the chunk that contains the "apply" statement followed
            by the code that creates, packs and binds the frames and widgets.
        """
        ##D('Creation text (re)generated per %s'%WhoCalled)
        PresentName = Repo.SelectedHerd
        if PresentName == None:
            #There is no currently selected form. This can happen if there are no forms
            #    and the user drops/moves a widreq on the parking lot
            return
        if PresentName == 'the Parking Lot':
            #Well the parking lot is the selected herd but it has no code, so instead we
            #    use the name of the form which is currently selected in the layout area.
            #    This situation comes up if the user drags a widreq from a form and drops
            #    it on the parking lot. At that point the parking lot is the selected herd
            #    but we need to regenerate the code of the form to reflect the now gone
            #    widreq.
            PresentName = self.LayoutNotebook.GetCurSelection()    
        FI = Repo.FetchForm(PresentName)

        ST = self.FormSystextHeaderGenerate(PresentName,FI['BaseClass'],FI['Type'])
        FI['Text'].TextWidget.SystextReplace('class',ST[0])
        FI['Text'].TextWidget.SystextReplace('apply(',ST[1])

    def on_ActionFormSwapCodeLayout(self,Dummy=None):
        """
        Swap Gui/Text editor of the current form.
        """
        #Get the tab entry of the selected tab.
        FormName = self.LayoutNotebook.GetCurSelection()
        Entry = Repo.FetchForm(FormName)
        if FormName == GblMainName:
            #This is the main code area; it has no gui.
            return
        if Entry:
            #We have at least one form in tab
            if Entry['Requested'] == 'Gui':
                #The Gui editor is showing; switch to text
                Entry['Requested'] = 'Text'
            else:
                #Text editor is showing; now switch to gui
                Entry['Requested'] = 'Gui'
            #Pack it for user to see     
            self.EditorPack()

    def ColorizerOffAll(self):
        """
        Turn off all colorizers of the current module.
        """
        for Form in Repo.ListHerds():
            self.ColorizerOff(Form)
            
    def ColorizerOff(self,Herd=None):
        """
        Turn off the text colorizer of a colorized text.
        
        If no herd is specified we use the current herd.
        """
        if Herd == None:
            Entry = Repo.FetchForm()
        else:
            Entry = Repo.FetchForm(Herd)    
        if Entry and Entry['OnTab']:
            Temp = Entry['Text']
            if Temp:
                Temp.TextWidget.CommandIssue('stop','Layout.ColorizerOff')

    def EditorPack(self,ForceEditor=None):
        """
        Pack the currently requested editor of the current form onto the PageFrame.
        
        If an editor is already packed, we unpack it first.
        
        If ForceEditor is 'Gui' or 'Text' we request that editor, then pack.
        
        """
        FormName = self.LayoutNotebook.GetCurSelection()
        Entry = Repo.FetchForm(FormName)
            
        ##D('EditorPack: FormName=%s '%FormName)
        if Entry:
            if ForceEditor:
                assert ForceEditor in ('Gui','Text')
                Entry['Requested'] = ForceEditor
            if self.LayoutEditorPacked <> None:
                #An editor is already packed; unpack it
                self.LayoutEditorPacked.pack_forget()
                self.LayoutEditorPacked = None
            if Entry['Requested'] == 'Text':
                #Text editor is requested
                self.Buffet.pack_forget()
                self.LowerFrame.pack_forget()
                if Entry['Text'] == None:
                    #No text editor yet; create it
                    Page = self.LayoutNotebook.PageFrame()
                    Entry['Text'] = TextEdit(Page)
                if not GblLoadInProgress:    
                    Entry['Text'].pack(expand=YES,fill=BOTH)
                    #Create a reference to the packed editor for use when unpacking it.
                    self.LayoutEditorPacked = Entry['Text']
                #Focus on the just-packed editor so the flashing cursor appears.    
                Entry['Text'].TextWidget.focus_set()    
                #Get the line counter display up to date
                Entry['Text'].StatusUpdate()
            else:
                #Gui editor is requested
                self.Buffet.pack(side=BOTTOM,fill=X)
                self.LowerFrame.pack(side=BOTTOM,fill=X)
                self._Win.update_idletasks()
                Size = self.NoteBookSize()
                if not GblLoadInProgress:
                    if Entry['Gui'] == None:
                        #The gui hasn't been created yet; this happens first time a gui
                        #    is required after load; reconstitute it.
                        #When a form is saved all it's information is gathered into a <form-descriptor> and
                        #    saved as part of the project. When the project is later loaded, we don't
                        #    generate all the gui's of all the forms. Rather, we store the <form-descriptor>
                        #    in the form as "LoadInfo" and we later reconstitute the gui only when it is
                        #    needed. It is needed when the user asks for the gui or when the user makes a
                        #    change to a widget which prompts us to regerate the systext (the gui is needed
                        #    because it's "Create" method supplies the creation code for the widgets et al.
                        Page = self.LayoutNotebook.PageFrame()
                        #Build the gui editor
                        Entry['Gui'] = GuiEditor(Page,FormName=FormName)
                        #And pack into the layout area
                        Entry['Gui'].pack(side=TOP,anchor='e',expand=YES,fill=BOTH)
                        self._Win.update_idletasks()
                        #Populate it with gathered data received from load
                        Entry['Gui'].CanvasConfigure(Entry['LoadInfo'])
                        #The load info is no longer needed
                        Entry['LoadInfo'] = None
                        #Remember the size of the NoteBook when the Gui was last resized
                        Entry['NoteBookSize'] = self.NoteBookSize()
                    elif Entry['NoteBookSize'] <> Size:
                        #The size changed; have gui redraw itself
                        Entry['Gui'].pack(side=TOP,anchor='e',expand=YES,fill=BOTH)
                        self._Win.update_idletasks()
                        Entry['Gui'].CanvasConfigure()
                        #Remember the size of the NoteBook when the Gui was last resized
                        Entry['NoteBookSize'] = Size
                    else:
                        #The size did not change. Just pack the gui
                        Entry['Gui'].pack(side=TOP,anchor='e',expand=YES,fill=BOTH)
                    #Create a reference to the packed editor for use when unpacking it.
                    self.LayoutEditorPacked = Entry['Gui']
            #Regardless of which editor is visible, if there is a text editor then
            #    fire up it's colorizer (unless we are in mid-load)
            if Entry['Text'] <> None and not GblLoadInProgress:    
                Entry['Text'].TextWidget.CommandIssue('resume','Layout.EditorPack')

    def on_BuffetLower(self,TabName):
        """
        A buffet tab is being lowered.
        """
        #Unpack the correspoinding sliding button bar
        if self.BuffetTabInfo.has_key(TabName):
            self.BuffetTabInfo[TabName]['ButtonBar'].pack_forget()
        return 1    
            
    def on_BuffetRaise(self,TabName):
        """
        A buffet tab is being raised.
        """  
        #Pack the correspoinding sliding button bar
        if self.BuffetTabInfo.has_key(TabName):
            self.BuffetTabInfo[TabName]['ButtonBar'].pack()

    def on_LayoutAreaLower(self,FormName):
        """
        The current LayoutTab is being lowered.
        """
        #Make sure everybody is OK with changing forms
        if not self.RepoActionCheck('HerdSelect'):
            #Somebody whined; refuse to lower
            return 0
        #Only the colorizer of the current form should run
        #assert FormName == Repo.SelectedHerd
        self.ColorizerOff()
        Repo.PreviousForm = FormName
        return 1

    def on_LayoutAreaRaise(self,FormName):
        """=e
        The user has clicked on a LayoutTab to select a particular form.
        
        We issue a repo request to select the form and then, if the size of
            the layout area notebook has changed, we tell the gui to resize itself.
        """
        if not FormName in Repo.ListHerds():
            #We are in the midst of initially creating this form; nothing more to do
            return    
        #We expect the lowering frame to the the currently selected one.
        R = Repo.Request(self.WRID,'HerdSelect', FormName, None)
        if R <> 1:
            print 'Problem selecting form: %s'%str(R)
        #Show the currently requested editor for this form    
        self.EditorPack()
        
    def RepoActionCheckHelper(self,Event,A,B):
        #A helper function for "RepoActionCheck".
        #If we got this far, nobody objects.
        self.RepoActionCheckFlag = 1
        return ('We were just checking',0)

    def CurrentlyVisibleForm(self):
        """
        Return the name of the currently visible form or None if no form is visible.
        """
        return self.LayoutNotebook.GetCurSelection()

    def RepoActionCheck(self,TheAction):
        """
        Check to see if people are OK with a particular Repo action.
        
        "TheAction" must be a Repo event, eg "HerdCreate".
        
        If everyone is OK with the proposed action we return 1.
        if anybody objects, we return 0
        """
        BindEventName = TheAction+'Query'
        Repo.Bind(self.WRID,BindEventName,self.RepoActionCheckHelper)
        self.RepoActionCheckFlag = 0
        Repo.Request(self.WRID,TheAction,self.NameForm)
        Repo.Unbind(self.WRID,BindEventName)
        return self.RepoActionCheckFlag

    def FormSystextHeaderGenerate(self,FormName,BaseClass,ModType):
        """
        Generate systext header pair for a form.
        
        "FormName" is the name of the form, eg "Form1".
        "BaseClass" is the class from which the form is derived.
        "ModType" is "Tkinter.Toplevel", "Tkinter.Frame" or "Pmw.ScrolledFrame".
        
        The result is a tuple of two strings:
        
        o "[0]" Class statement that kicks off the form along with statements to
            set the options of the top-most frame.
        o "[1]" The apply statement and all the code to generate and setup the widgets.
        """
        ##D('FormName=%s, BaseClass=%s, ModType=%s'%(FormName,BaseClass,ModType))
        DirectDerivation = BaseClass in ('Tkinter.Toplevel','Tkinter.Frame','Pmw.ScrolledFrame')
        Module = ModType.split('.')[0]
        ImportType = Cfg.Info['Modules'][Module]['ImportType']
        ##D('ImportType=%s'%ImportType)
        if ImportType == 'import':
            pass
        elif ImportType == 'from':
            if DirectDerivation:
                #If we are deriving directly then BaseClass will be of the form "Module.Widget" but we
                #just want the widget part. If we are deriving indirectly then it's the users
                #responsibility to have provided us with the proper name.
                BaseClass = BaseClass.split('.')[1]    
        else:
            raise Exception, 'Invalid import type: '+ImportType    
        #
        # Above we do some horsing around to get things as we need them. At this point:
        # "BaseClass" is the text that will get plugged into the "apply(<BaseClass>.__init..." line.
        #    
        Scheme = Cfg.Info['Schemes'][Cfg.Info['SchemeCurName']]
        ##D('BaseClass=%s'%BaseClass)
        Indent = ' ' * Scheme['Indent']
        TemplateA = GenerateCommentBox(FormName,Scheme['Wrap']) + 'class %s(%s):\n'
        TemplateB = '\n%sapply(%s.__init__,(self,Master),kw)\n'
        TemplateD = '%sassert isinstance(%s,%s)\n'
        TemplateE = '%sdef __init__(self,Master=None,**kw):\n'%Indent
        #--- Insert code to set options for our class ---    
        #Here we rely on the fact that each form has a widreq of the same name which
        #    holds the options for the form.
        
        #We are passed the FormName; why were we asking for it here:
        #FormName = self.LayoutNotebook.GetCurSelection()
        ##D('FormName=%s'%FormName)
        FormWidreq = Repo.Fetch(FormName,FormName)
        #Have the widreq generate a list of options that need to be set
        CL = FormWidreq.CreationList(FormWidreq.Options)
        for Name,Value in CL:
            TemplateE += "%skw['%s'] = %s\n"%(Indent*2,Name,Value) 
        A = TemplateA%(FormName,BaseClass)
        if not DirectDerivation:
            #If not deriving directly from Toplevel or Frame then this is where to put
            #    code which could check what we are deriving from. Currently we don't
            #    check.
            pass
        A += TemplateE
        B = TemplateB%(Indent*2, BaseClass)
        #Look after bindings for our topmost 
        Temp = FormWidreq.BindCode(Scheme['Indent'],Scheme['Wrap'])
        if Temp:
            B += Temp + '\n'

        #Get the code to generate/pack/bind our widgets
        Form = Repo.FetchForm(FormName)
        Gen = Form['Gui'].Create(Scheme['Indent'],Scheme['Wrap'],Whine=True)
        B = B + Gen + '\n'
        return (A,B)

    def TemplateZap(self,Template,Flag):
        """
        Adjust template lines based on Flag.
        
        "Template" is a string of lines with embedded newlines.
        
        If "Flag" is true then any lines whose first character is '/' have their
            first character deleted.
            
        If "Flag" is false then any lines whose first character is '/' are
            deleted in their entirety.
            
        The result is the revised string.        
        """
        L = Template.split()
        Result = []
        for Line in Template.split('\n'):
            if Line[0:1] == '/':
                if Flag:
                    Result.append(Line[1:])
            else:
                Result.append(Line)
        return '\n'.join(Result)     

    def FormCreateNew(self,Info,OfMainModule=False):
        """=f
        Add a new form to the current project.
        
        "Info" is a dictionary:
            o "['Name']" The name of the new form.
            o "['Type']" "'Tkinter.Toplevel'", "'Tkinter.Frame'", "'Pmw.ScrolledFrame'".
            o "['BaseClass']" The name of the class from which we are to derive.
            
        if "OfMainModule" is true and Info['Name'] == GblMainName then we know we are
            creating the main code area of the main module. This is important because the
            code varies depending on whether we are the main or an additional module.
            
        Normally we create a tab for the new form. If "OnTab" is false then we don't.            
        
        IT IS THE CALLERS RESPONSIBILITY TO HAVE VERIFIED THAT THE "Info" ENTRIES
            ARE ACCEPTABLE FOR A NEW FORM.
        """
        Scheme = Cfg.Info['Schemes'][Cfg.Info['SchemeCurName']]
        Indent = Scheme['Indent']
        I = Indent * ' '
        II = (Indent*2)*' '
        #Were going to switch forms so turn off the current forms colorizer
        self.ColorizerOff()
        #Register and select a herd for this form
        NewName = Info['Name']
        R = Repo.Request(self.WRID, 'HerdCreate', NewName)
        if R <> 1:
            print R
            raise Exception, 'Request to create empty initial herd for form %sunexpectedly failed'%NewName
        R = Repo.Request(self.WRID, 'HerdSelect', NewName)
        if R <> 1:
            print R
            raise Exception, 'Request to select empty initial herd for form %s unexpectedly failed'%NewName
        #Put the new form in a tab.
        FormName = Info['Name']
        #Add tab for our frame to the layout area
        self.LayoutNotebook.Add(FormName,BulkAdd=GblLoadInProgress)
        ThePage = self.LayoutNotebook.PageFrame()
        FI = Repo.FetchForm()
        if FormName <> GblMainName:
            #This is not the main code area; create a gui editor for it
            if not GblLoadInProgress:
                Temp = GuiEditor(ThePage,FormName=FormName)
                Temp.pack(side=TOP,anchor='e',expand=YES,fill=BOTH)
            else:
                Temp = None    
            FI['Gui'] = Temp
            Req = 'Gui'
        else:
            #This is the main code area; it has no gui
            FI['Gui'] = None
            Req = 'Text'
        FI['Text'] = TextEdit(ThePage)
        FI['Requested'] = Req
        FI['Type'] = Info['Type']
        FI['BaseClass'] = Info['BaseClass']
        FI['OnTab'] = True
        self._Win.update_idletasks()
        FI['NoteBookSize'] = (0,0) #Fake size will prompt Gui redisplay
        self.EditorPack()

        if NewName == GblMainName:
            #We are creating the main code area; it's special
            IsMainModule = Cfg.Info['ProjectName'] == Repo.ModuleName
            TextEditor = Repo.FetchForm()['Text'].TextWidget
            PartOne = self.TemplateZap(Cfg.Info['Template'][0],IsMainModule)
            TextEditor.insert(END,PartOne,'')
            TextEditor.insert(END,GenerateImportLines(['Tkinter']),'bgldt')
            
            PartTwo   = Cfg.Info['Template'][1].replace('$NAME',Cfg.Info['ProjectName'])
            PartThree = Cfg.Info['Template'][2].replace('$NAME',Cfg.Info['ProjectName'])
            PartTwo   = self.TemplateZap(PartTwo,IsMainModule)
            PartThree = self.TemplateZap(PartThree,IsMainModule)
            TextEditor.insert(END,PartTwo,'')
            if IsMainModule:
                #We are creating the main module
                IndentAmount = Cfg.Info['Template'][3]
                InitCode = GenerateInitLines(['Tkinter'],IndentAmount)
                TextEditor.insert(END,InitCode,'bgldt')
            TextEditor.insert(END,PartThree,'')
        else:
            #We are creating a normal form    
            #Create and register the outermost frame instance
            WidModule,WidType = Info['Type'].split('.')
            Temp = WidReq(WidType,Info['Name'],FrameID=(0,),PresentHome=Info['Name']
                ,ModuleName=WidModule)
            R = Repo.Request(self.WRID,'WidreqCreate',Info['Name'],Temp)
            if R <> 1:
                Repo.Tell(R)
                raise Exception, "unexpected Repo result"
            #Create the initial representation 
            if not GblLoadInProgress:
                GuiCanvas = Repo.FetchForm()['Gui']
                Temp.WidgetShow(None,GuiCanvas,IsSelected=1)            
                #Create the default text
                ST = self.FormSystextHeaderGenerate(Info['Name'],Info['BaseClass'],Info['Type'])
                TemplateA = '%s#\n%s#Your code here\n%s#\n'%(II,II,II)
                TemplateB = '%s#\n%s#Start of event handler methods\n%s#\n'%(I,I,I)
                TemplateC = '%s#\n%s#Start of non-Rapyd user code\n%s#\n'%(I,I,I)
                TextEditor = Repo.FetchForm()['Text'].TextWidget
            
                TextEditor.insert('1.0',ST[0],'bgldt')
                TextEditor.insert(END,TemplateA,'')
                TextEditor.insert(END,ST[1],'bgldt')
                TextEditor.insert(END,TemplateA,'')
                TextEditor.insert(END,TemplateB,'bgldt')
                TextEditor.insert(END,'\n','')
                TextEditor.insert(END,TemplateC,'bgldt')
                #Request selection so everybody knows it is the selected item
                R = Repo.Request(self.WRID,'WidreqSelect',Info['Name'])
                if R <> 1:
                    Repo.Tell(R)
                    raise Exception, "Unexpected Repo result"

    def FormRename(self,Event,PresentName,NewName):
        """=f
        Rename a form.
        
        IT IS THE CALLERS RESPONSIBILITY TO HAVE VERIFIED THAT THE NAMES SUPPLIED ARE
            ACCEPTABLE. 
            
        We just crash and burn if they are not acceptable.
        """
        FI = Repo.FetchForm()
        #Show the new name in the tab
        self.LayoutNotebook.ReName(PresentName,NewName=NewName)
        #Update the systext in our text editor
        ST = self.FormSystextHeaderGenerate(NewName,FI['BaseClass'],FI['Type'])
        FI['Text'].TextWidget.SystextReplace('class',ST[0])
        FI['Text'].TextWidget.SystextReplace('apply(',ST[1])

    def FormDelete(self,FormName):
        """=f
        Delete the form of the specified name.
        
        It is the callers responsibility to make sure that the specified form exists.
        
        Required:
            o Query the repository
            o Widreqs unregister when they receive delete notification
            o OptionEditor is unregistered by the Widgetator, which created it in the first place.
            o The GuiEditor unregisters in response to HerdDelete
            o The form canvas unregisters in response to HerdDelete
        """
        #Make sure the visible form is the Repo selected form (there's always the parking lot)
        R = Repo.Request(self.WRID,'HerdSelect',FormName)                
        if R <> 1:
            #Select was declined; this is possible
            print Repo.Tell(R)
            return
        #Delete all the widreqs on this form
        for W in Repo.ListWidreqs(FormName):
            R = Repo.Request(self.WRID,'WidreqDelete',W)
            if R <> 1:
                print R
                raise Exception, 'Unexpected objection to WidReq (%s) delete'%W,R
        #Turn off the colorizer just in case
        self.ColorizerOff()
        #Now delete the herd
        R = Repo.Request(self.WRID,'HerdDelete',FormName)                
        if R <> 1:
            print R
            raise Exception, 'Unexpected objection to herd delete: '+R
        self.LayoutNotebook.Delete(FormName)

    def NameForm(self):
        """=f
        Generate an arbitrary, non-conflicting name for a form.
        
        The result will be a name like "Form<n>"' where <n> is the smallest
            integer, greater than zero, which results in a unique name.
        """
        Highest = 0
        Default = 'Form'
        LD = len(Default)
        for Name in Repo.ListHerds():
            if Name[:LD] == Default:
                #the base portion of the names matches
                try:
                    Number = int(Name[LD:])
                    Highest = max(Highest, Number)
                except:
                    pass
        return '%s%s'%(Default,Highest+1)                    

    def FormRaise(self,NameOfForm):
        """=t
        Raise the specified form to the top in the LayoutArea NoteBook
        """
        self.LayoutNotebook.Select(NameOfForm)

    def on_Configure(self,Event):
        """=e
        Our main TopLevel got resized
        
        Instead of blindly redrawing everything in response to each shift of the mouse, we
            wait until things have held steady for a bit before redrawing, then that task
            is handled by method "on_ConfigureAfter".
        """
        if Event.widget <> self._Win:
            #For ***really*** unknown reasons, this routine gets called for ALL configure
            #    events for all widgets of _Win, rather as if I had used "w.bind_all"
            #    which I most certainly did not. Therefore, we check the Event widget 
            #    and exit immediately for any event OTHER than one against _Win which 
            #    is what we wanted in the first place. Grump. It took me a while to 
            #    figure this one out.
            return
        if hasattr(self,'ConfigureAfterID'):
            #hmm; apparently we have been here recently; cancel the current after
            self._Win.after_cancel(self.ConfigureAfterID)
        #Setup an after so we redraw only after the user has quit dinking around
        self.ConfigureAfterID = self._Win.after(250,self.on_ConfigureAfter)

    def on_ConfigureAfter(self):
        """=e
        Now actually resize the TopLevel
        """
        #if Event.widget <> self._Win:
        #    return
        #Look after the parking lot
        self.ParkingLot.CanvasConfigure()
        #Then the layout area
        CurTab = self.LayoutNotebook.GetCurSelection()
        if CurTab == None:
            #There are no tabs; nothing needs done
            return
        FormInfo = Repo.FetchForm(CurTab)    
        if FormInfo.has_key('Gui') and FormInfo['Gui'] <> None:
            #We have to update_idletasks here in order to get the new size
            self._Win.update_idletasks()
            Size = self.NoteBookSize()
            #D('on_Configure NoteBookSize=%s'%str(Size))
            if Size <> (1,1):
                #We have some real size for the NoteBook; resize the Gui canvas
                FormInfo['Gui'].CanvasConfigure()
                #Remember the size of the NoteBook when the Gui was last resized
                FormInfo['NoteBookSize'] = Size
                #Note the size of the Gui.Canvas.
                TC = FormInfo['Gui']
                self.GuiCanvasSize = [TC.winfo_width(), TC.winfo_height()]

    def NoteBookSize(self):
        """=t
        Return an (x,y) tuple showing the size of the LayoutArea NoteBook widget.
        """
        PF = self.LayoutNotebook.PageFrame()
        return (PF.winfo_width(),PF.winfo_height())

    def on_BuffetHelpWidget(self,Event):
        """=h
        User clicked for help over a widget buffet button
        """
        HelpTopic = 'Buffet.Widget.%s'%Event.widget.DefaultName
        Help(HelpTopic)
        

    def on_BuffetHelp(self,Event):    
        """=h
        User clicked for help over non-widget part of buffet
        """
        HelpTopic = 'Buffet.%s'%Event.widget.HelpTopic
        Help(HelpTopic)


    def on_KnownHelp(self,Event):
        """=h
        Help click over widgets with built-in help topic come here.
        """
        Help(Event.widget.HelpTopic)


    def on_WidreqCreateQuery(self,Event,Name,Dummy):
        """=e
        A helper function for on_BuffetPress
        """
        #The fact that we were queried at all indicates everybody elese was ok with it
        self.NewWidreqOK = True    
        #Now we return a reason string to quash the request.
        return ("We were just checking", 0)

    def on_DuplicatorPress(self,Event):
        """
        Called when the user clicks on the duplicator.
        """
        Sel = Repo.FetchSelected()
        if Sel == None:
            #No widrew is selected, nothing to do
            return
        SelWid = Repo.Fetch(Sel)
        if SelWid.FrameID <> None:
            #The selected widreq is a frame; you can't duplicate those.
            return
        Info = SelWid.Gather()
        NewWidreq = WidReq(WidgetName=SelWid.WidgetName
            ,InstanceName='__NewWidget__'
            ,OptionList=Info['Options']
            ,BindingList=Info['Bindings']
            ,PackOptionList=Info['PackOptions']
            ,ModuleName=Info['ModuleName'])
        #Start the drag and drop process
        Tkdnd.dnd_start(NewWidreq,Event)
            

    def on_BuffetPress(self,Event):
        """=e
        Called when user clicks on a buffet widget to create a new WidReq
        """
        if Repo.FetchForm() <> None:
            #A tab is selected; must check before creating widreq
            #At this point we would like to find out if it's OK to create a new widreq without
            #    actually creating one because, among other things, we don't know the it's
            #    eventual destination. Instead, we go through the motions of creating
            #    a widreq (if anybody else is against they will decline) and then WE decline.
            #    This allows us to find out if creating one is OK without actually creating one.
            #Bind our helper function to the appropriate query
            Repo.Bind(self.WRID,'WidreqCreateQuery',self.on_WidreqCreateQuery)
            #Assume we can't create a new widreq.
            self.NewWidreqOK = False
            #Fire off a request to find out;
            R = Repo.Request(self.WRID, 'WidreqCreate', '__NewWidget__', 'DummyWidreqBody')
            #Now unbind out function so it isn't objecting to other widget create requests
            Repo.Unbind(self.WRID,'WidreqCreateQuery')
            if not self.NewWidreqOK:
                #Somebody other than us objected
                #print 'R=%s'%`R`
                if R[2] == 0:
                    #tell the user if they don't already know
                    Rpw.ErrorDialog('%s (from %s)'%(R[0],R[1]))
                return
        #
        # Everybody is OK with the concept of creating a new widreq
        #
        #The name/module of the widget was stored in the button for use now
        BaseName = Event.widget.DefaultName
        BaseModule = Event.widget.DefaultModule
        #Assign an arbitrary name to indicate a new widget
        InstanceName = '__NewWidget__'
        #Create the new WidReq instance
        NewWidreq = WidReq(BaseName,InstanceName,ModuleName=BaseModule)
        #Start the drag and drop process
        Tkdnd.dnd_start(NewWidreq,Event)

#-------------------------------------------------------------------------------
#
# Parking Lot
#
#-------------------------------------------------------------------------------

class ParkingLotEditor(rpDndCanvasWid):
    """
    Our parking lot class
    """
    def __init__(self,Master,**kw):
        """
        Create the parking lot
        """
        #Extract the one argument we require
        apply(rpDndCanvasWid.__init__, (self,Master), kw)        

    def Gather(self):
        """
        Return and gather information about the content of the parking lot.
        
        The result is a dictionary:
            o "['SelectedWidreq']" The name of the selected widreq, or None.
            o "['Widreqs']" A list of widreqs on the parking lot.
        """
        ParkingList = []
        Herd = 'the Parking Lot'
        Widreqs = Repo.ListWidreqs(Herd)
        for Widreq in Widreqs:
            W = Repo.Fetch(Widreq,Herd)
            ParkingList.append(W.Gather(CanvasSize=self.CanvasSize))
        return {'SelectedWidreq':Repo.FetchSelected('the Parking Lot'), 'Widreqs':ParkingList}

    def Scatter(self,Info):
        """
        Populate the parking lot per the passed information.
        
        "Info" is a dictionary as returned by "Gather".
        
        We delete any widreqs currently on the parking lot, then create ones per
            "Info".
        """
        self.CanvasSize = (self.winfo_width(),self.winfo_height())
        FormName = 'the Parking Lot'
        assert 1==Repo.Request(self.WRID,'HerdSelect',FormName)
        #Delete any current parking lot widreqs
        for W in Repo.ListWidreqs():
            assert 1==Repo.Request(self.WRID,'WidreqDelete',W)
        #Construct the specified widreqs    
        SelectedWidreq = Info['SelectedWidreq']
        for WidreqInfo in Info['Widreqs']:
            WidreqName = WidreqInfo['Name']
            #Build the actual widreq instance
            W = WidReq(WidgetName=WidreqInfo['WidgetName']
                      ,InstanceName=WidreqName
                      ,FrameID=WidreqInfo['ID']
                      ,PresentHome='the Parking Lot'
                      ,OptionList=WidreqInfo['Options']
                      ,BindingList=WidreqInfo['Bindings']
                      ,PackOptionList=WidreqInfo['PackOptions']
                      ,ModuleName=WidreqInfo['ModuleName'])
            #Add it to the repository          
            assert 1==Repo.Request(self.WRID,'WidreqCreate',WidreqInfo['Name'],W)
            #Have it represent itself of the parking lot
            IsSel = WidreqName == SelectedWidreq
            W.PlaceOnCanvasCenter(self
                ,GenericToCanvas(WidreqInfo['XY'],self.CanvasSize)
                ,IsSelected=IsSel)

    def CanvasConfigure(self,Info=None):
        """=e
        It's time to redraw the parking lot
        
        If "Info" is "None" then we are simply redrawing the canvas because it was resized.
        
        If "Info" is supplied, this means we are drawing the canvas as part of "Load".
        """
        HerdName = 'the Parking Lot'
        if Info == None:
            #Get description of current canvas content.
            Info = self.Gather()
            #Tell all widreqs on this form to vanish
            for Name in Repo.ListWidreqs(HerdName):
                W =  Repo.Fetch(Name,HerdName)
                assert W <> None
                W.Vanish()
        #Toast everything left on the canvas.
        self.clear()
        self.create_image(25,25,image=Cfg.Info['ParkingIcon'])
        #Get the revised size of the canvas.
        self.CanvasSize = [self.winfo_width(), self.winfo_height()]
        #Relocate the widreqs
        for WidreqInfo in Info['Widreqs']:
            #Get the widreq instance from the repository        
            W = Repo.Fetch(WidreqInfo['Name'],HerdName)            
            assert W <> None 
            IsSel = HerdName == Repo.SelectedHerd and WidreqInfo['Name'] == Repo.FetchSelected()
            W.PlaceOnCanvasCenter(self, GenericToCanvas(WidreqInfo['XY'],self.CanvasSize),IsSel)
        Sel = Repo.FetchSelected()
        """
        if Sel <> None and self.SelectedWidreq == None:
            #A widreq is selected but we haven't established a reference to it; this can happen
            #    the first time we are configured following a load. Create the reference.
            self.SelectedWidreq = Repo.Fetch(Sel)            
        """    
    

#-------------------------------------------------------------------------------
#
# GuiEditor
#
#-------------------------------------------------------------------------------

class GuiEditor(rpDndCanvasWid,BindMixin):
    """=m
    This is where users edit frames and widreqs on a form

    *Note:* A great many routines depend on the fact that bounding boxes are represented
        (UpperLeft-LowerRight), that is, X1 <= X2 and Y1 <= Y2. A lot of stuff
        will break if you violate this.
    -----    
    #=c Code Generation    
    #=e Event Handlers    
    #=f Frame related
    #=l Line related
    #=m Major methods
    #=u Utility methods
    #=v Canvas methods
    """
    StateIdle = 0       #We are idle.
    StateLineStart = 1  #User has requested a line but we don't yet know what direction.
    StateLinePlace = 2  #We are placing a new line
    StateLineMove = 3   #We are moving an existing line

    LineTag = "BoundingLine" # lines we create get this tag
    LineStippleStandard = ""
    LineStippleNew = "gray50"
    
    Bumper = 20 #we keep adjacent parallel lines this far apart

    def __init__(self,Master,**kw):
        """
        Create the GuiEditor.
        """
        #Extract the one argument we require
        try:
            FormName = kw['FormName']
            del kw['FormName']
        except KeyError:
            raise Exception, 'No "FormName" argument was specified'
        assert FormName <> None    
        #Set the defaults we care about    
        BorderWidth = 1
        self.BorderFudge = (BorderWidth+1) * 2 #Number of actual pixels we lose to the border.
        self.SetDefaults(kw,[('width',50),('height',100),('bd',BorderWidth)
            ,('relief','sunken'),('DropTypes',['WidReq'])])
        self.SetDefaults(kw,[('scrollregion',(0,0,kw['width'],kw['height']))])
        kw['herdname'] = FormName
        kw['ourname'] = 'GuiEditor'
        
        apply(rpDndCanvasWid.__init__, (self,Master), kw)        
        
        self.HelpTopic = 'Layout.Canvas'
        self.bind(HelpButton, self.on_LayoutCanvasHelp)

        #--- bindings that facilitate drawing lines on the canvas ---
        self.bind('<Button-1>',self.on_Button1Down)
        self.bind('<ButtonRelease-1>',self.on_Button1Up)
        self.bind('<Motion>',self.on_MouseMotion)
        self.bind('<ButtonRelease-3>',self.on_Button3Down)
        
        self.State = GuiEditor.StateIdle
        Master.update_idletasks()
        self.CanvasSize = [1,1]
        #For reasons not clear to me, the very first GuiEditor comes up thinking the canvas
        #    is wider than the space actually allocated to it causing it to draw the form
        #    selection rectangle incorrectly. Calling "CanvasConfigure" after a brief delay
        #    draws the selection rectangle correctly.
        self.after(100,self.CanvasConfigure)
        self.OurModule = Repo.ModuleName

    def SetDefaults(self,Dict,List):
        """
        Set a series of defaults in a dictionary.
        
        "List" is a series of (Option,Value) pairs. If "Dict" does not already have an option
            named "Option" then one is created with value "Value"
        """
        for Option, Value in List:
            if not Dict.has_key(Option):
                Dict[Option] = Value

    def CanvasSizeFetch(self):
        """
        Return canvas size adjusted to include the border.
        
        Where did the "minus one" come from you say. Well, way back in the mists of time,
            we wrote all the code so that if the canvas is X by Y, that we consider the
            outermost bounding box to be X by Y; it sounded so reasonable at the time.
            Of course given a canvas X by Y, you can draw on horizontal pixel 0 (the left
            edge of our imputed bounding box) but you can't draw on pixel X; since our
            last pixel is X-1.
            
        The correct way to fix this would be to go back and revise a whole bunch of
            routines that make this mis-assumption. The quick way to fix this, as done
            below, is to lie and say the canvas is one smaller than it actually is. 
            Thus if we have a canvas 100 wide, we lie and say it is 99 wide, then when
            the routines try to write on pixel 99 it works. This is a slight hack but
            I don't offhand see how it is going to hurt anything. If it bothers you, feel
            free to go over the code and do it the correct way, OK?
        """
        return [self.winfo_width()-self.BorderFudge-1, self.winfo_height()-self.BorderFudge-1]

    def CanvasConfigure(self,Info=None):
        """=e
        It's time to redraw the main canvas.
        
        If "Info" is "None" then we are simply redrawing the canvas because it was resized.
        
        If "Info" is supplied, this means we are drawing the cansas as part of "Load".
        """
        if self.OurModule <> Repo.ModuleName:
            #The wrong repo module is selected; do nothing
            return
        assert not GblLoadInProgress, "Should not get here if load-in-progress"    
        if Info == None:
            #Get description of current canvas content.
            Info = self.Gather()
            #Tell all widreqs on this form to vanish
            for Name in Repo.ListWidreqs(self.HerdName):
                W =  Repo.Fetch(Name,self.HerdName)
                assert W <> None
                W.Vanish()
        #Toast everything left on the canvas.
        self.clear()
        #Get the revised size of the canvas.
        self.CanvasSize = self.CanvasSizeFetch()
        #Redraw the lines
        for X, Y, Dirn in Info['Lines']:
            XY = GenericToCanvas((X,Y),self.CanvasSize)
            self.Draw(XY,Dirn,GuiEditor.LineStippleStandard)
        #Relocate the widreqs
        for WidreqInfo in Info['Widreqs']:
            #Get the widreq instance from the repository        
            W = Repo.Fetch(WidreqInfo['Name'],self.HerdName)            
            assert W <> None 
            if WidreqInfo['ID'] == None:
                #This is a containee widget; have it appear at the new location.
                IsSel = self.HerdName == Repo.SelectedHerd and WidreqInfo['Name'] == Repo.FetchSelected()
                W.PlaceOnCanvasCenter(self, GenericToCanvas(WidreqInfo['XY'],self.CanvasSize),IsSel)
                #It will appear as the selected widreq. If it isn't the selected
                #    widreq then draw it as such.
                #if self.HerdName <> Repo.SelectedHerd or WidreqInfo['Name'] <> Repo.FetchSelected():
                #    W.WidgetShow(W.Label,IsSelected=False)
            else:
                #This is a container widget
                ##D("WidreqInfo['ID']=%s W.FrameID=%s"%(`WidreqInfo['ID']`,`W.FrameID`))
                assert WidreqInfo['ID'] == W.FrameID
                #Find out if this is or is not the selected widreq
                Sel = self.HerdName == Repo.SelectedHerd and WidreqInfo['Name'] == Info['SelectedWidreq']
                ##D("Sel=%s WidreqInfo['Name']=%s"%(Sel,WidreqInfo['Name']))
                #Now show it with appropriate selection
                W.WidgetShow(None,self,Sel)    
        Sel = Repo.FetchSelected()
        if Sel <> None and self.SelectedWidreq == None:
            #A widreq is selected but we haven't established a reference to it; this can happen
            #    the first time we are configured following a load. Create the reference.
            self.SelectedWidreq = Repo.Fetch(Sel)            

    def on_LayoutCanvasHelp(self,Event):
        """=e
        User clicked help over the layout canvas
        """
        Help('Layout.canvas')
    
    def EventInfo(self,Event,Comment):
        """=u
        A development routine to print event information
        """
        print '%s x=%s y=%s'%(Comment,Event.x,Event.y)

    def Emit(self,LineOfCode):
        """=c
        Emit one line of code.
        """
        return
        print 'Code: %s'%LineOfCode

    def Create(self,Indent,Wrap,Whine):
        """
        Return a string with the code necessary to create all the frames and widgets except the top most.
        
        "Indent" is the indent factor.
        
        "Wrap" We wrap lines so they don't exceed this number of characters.
        
        If "Whine" is true then prior to exit if any forms were not clearly horizontal
            or vertical then we display a message saying so. We generate code for these
            frames but since the users intent wasn't clear the pack 'side' settings
            may not be what they had in mind either.
        """
        ErrorList = []
        Info = self.FrameInfoGen()[0]
        FrameList = self.FrameNameInner(Info)
        #FrameList gives frame names from outer-most to inner-most
        FrameList.reverse()
        #Since we will need to go from FrameID to widreq, make a dictionary where
        #    the key is the FrameID and the value is the actual widreq.
        XDict = {}
        for WidReqName in Repo.ListWidreqs(self.HerdName):
            WidReq = Repo.Fetch(WidReqName,self.HerdName)
            if WidReq.FrameID <> None:
                #This is a container widreq
                XDict[WidReq.FrameID] = WidReq
        Result = []
        #Routine CreationCode needs to know if we are the main form of the main module. We note that in
        #    a boolean for later use.
        IsMainForm = self.HerdName == Cfg.Info['ProjectName'] and Repo.ModuleName == Cfg.Info['ProjectName']
        #
        # Generate container widgets
        #
        for FrameID in FrameList:
            if FrameID <> (0,):
                #This is a frame other than the form itself.
                MasterWidreq = XDict[FrameID[:-1]]
                Base = MasterWidreq.Name
                if MasterWidreq.Name == self.HerdName:
                    Base = 'self'
                else:
                    Base = 'self.' + MasterWidreq.Name    
                MasterString = MasterWidreq.MasterStringFetch(Base)
                if Info[FrameID]['Dirn'] == 0:
                    #This frame and it's siblings are horizontal
                    Side = 'top'
                else:
                    #Vertical frames
                    Side = 'left'    
                #Get code to generate current frame
                try:
                    Widreq = XDict[FrameID]
                except:
                    #It is possible to get a KeyError here because we were called while
                    #    a new frame or frame-pair were being created and Info finds a
                    #    new frame which hasn't yet been added to the repository. We
                    #    simply ignore the missing widreq; this causes no problem because
                    #    after the frame(s) have been created we get called again. The
                    #    cases I have seen would typically occur if the user made a 
                    #    change to a widreq option and then immediately created a new
                    #    frame.
                    continue
                Result.append(Widreq.CreationCode(MasterString,Indent,Wrap))
                Result.append(Widreq.PackCode(Indent,Wrap,Side))
                Temp = Widreq.BindCode(Indent,Wrap)
                if Temp:
                    #We have one or more binding
                    Result.append(Temp)
            #    
            #Generate any containee widgets in the current frame
            #

            MasterWidreq = XDict[FrameID]
            Base = MasterWidreq.Name
            if MasterWidreq.Name == self.HerdName:
                Base = 'self'
            else:
                Base = 'self.' + MasterWidreq.Name    
            MasterString = MasterWidreq.MasterStringFetch(Base)


            Bbox = Info[FrameID]['Bbox']
            if len(Info[FrameID]['WidReqs']) == 1:
                #This frame contains but a single widreq; pack based on the side it is
                #    closest to
                W = Repo.Fetch(Info[FrameID]['WidReqs'][0],self.HerdName)
                DistanceList = [[W.X - Bbox[0],'left']
                               ,[Bbox[2] - W.X,'right']
                               ,[W.Y - Bbox[1],'top']
                               ,[Bbox[3] - W.Y,'bottom']]
                DistanceList.sort()
                PackSide = DistanceList[0][1]
                #Generate the code
                Result.append(W.CreationCode(MasterString,Indent,Wrap,IsMainForm))
                Result.append(W.PackCode(Indent,Wrap,PackSide))
                Result.append(W.BindCode(Indent,Wrap))
            else:
                #This frame contains two or more widreqs.                
                #Scan to get the X-Y range of the widgets in the frame
                Xmin = Ymin = 99999
                Xmax = Ymax = 0
                for WidreqName in Info[FrameID]['WidReqs']:
                    W = Repo.Fetch(WidreqName,self.HerdName)
                    Xmin = min(Xmin,W.X)
                    Xmax = max(Xmax,W.X)
                    Ymin = min(Ymin,W.Y)
                    Ymax = max(Ymax,W.Y)
                Xrange = Xmax - Xmin
                Yrange = Ymax - Ymin
                if Xrange <= Yrange:
                    #We are nominally vertical
                    Dirn = 1
                    VirtualStart = Bbox[1]
                    VirtualEnd = Bbox[3]
                    TopLeft = 'top'
                    BottomRight = 'bottom'
                else:
                    #We are nominally horizontal
                    Dirn = 0
                    VirtualStart = Bbox[0]
                    VirtualEnd = Bbox[2]
                    TopLeft = 'left'
                    BottomRight = 'right'
                if len(Info[FrameID]['WidReqs']) <= 1 or (Xrange*2 < Yrange or Yrange*2 < Xrange):
                    #Either we have less than two widreqs or we 2+ widreqs we do have are
                    #    clearly horizontal or vertical.
                    pass
                else:    
                    #Orientation is not clear                
                    ErrorList.append(MasterWidreq.Name)
                #Note: VirtualStart is initially the top/left coordinate of the frame and VirtualEnd 
                #    is initially the bottom/right coordinate of the frame. We process widreqs moving
                #    from near the frame edges toward the center. When we process a widreq which was
                #    near the VirtualStart, then it's location becomes the new virtual start. When we
                #    process a widreq which was near the VirtualEnd, it's location becomes the new
                #    virtual end. The point of this is to assign a pack side that makes sense based 
                #    on how the user had the widreqs placed in the frame. Some examples, where the
                #    frame is horizontal, letters represent widreqs and vertical bars represent the
                #    frame edges.
                #
                #    |A         B|
                #    A is clearly 'left' and B clearly 'right'.
                #
                #    |ABCDEFGHI  |
                #    All are 'left' even though, for example, widreq I is far to the right in the frame.
                #        We treat it as 'left' because it is part of a string of widreqs which 
                #        originated on the left. Our moving-virtual-Start/End makes this happen.
                #
                #    |ABC     DEF| 
                #    A, B and C are 'left'; D, E, and F are 'right'.
                #
                #    |ABCDEFGHIJK|  
                #    In this case it's not clear what the user had in mind. The algorithm allocates
                #        widreqs from the outside in thus A will be assigned 'left', K 'right', B
                #        left, J 'right' until all are assigned. This doesn't seem unreasonable given
                #        that that the users intention wasn't clear in the first place.
                
                #
                #Make a sorted list of [KeyCoordinate,Widget]
                #
                Wlist = []
                for WidreqName in Info[FrameID]['WidReqs']:
                    W = Repo.Fetch(WidreqName,self.HerdName)
                    if Dirn == 0:
                        Wlist.append([W.X,W])
                    else:
                        Wlist.append([W.Y,W])
                Wlist.sort()
                #
                #Make passes over the list picking the outside widreq to assign next.
                #
                BottomList = []
                while len(Wlist) >= 1:
                    #Here we look at the first and last items in the list to find out which
                    #    one is closest to it's virtual end. We deal with whichever one is
                    #    closes, pop it from the list and carry on. Note that if there is 
                    #    only one item in the list then it is both the first and last item
                    #    in the list and depending which virtual end it is closer to it will
                    #    be processed appropriatly.
                    StartCoord = Wlist[0][0]
                    FirstToStart = StartCoord - VirtualStart
                    EndCoord = Wlist[-1][0]
                    LastToEnd = VirtualEnd - EndCoord
                    assert FirstToStart >= 0
                    assert LastToEnd >= 0
                    if FirstToStart < LastToEnd:
                        #The first widget is the closer of the two. Process it with
                        #    top/left packing
                        Coord, W = Wlist.pop(0)
                        Result.append(W.CreationCode(MasterString,Indent,Wrap,IsMainForm))
                        Result.append(W.PackCode(Indent,Wrap,TopLeft))

                        Temp = W.BindCode(Indent,Wrap)
                        if Temp:
                            Result.append(Temp)

                        VirtualStart = StartCoord
                    else:
                        #The last widget is th closer of the top. Append it to the list of
                        #   widreqs to be processed later for BottomLeft packing.
                        #    be processed by the 'last-item-in-list' code.
                        BottomList.append(Wlist.pop())
                        VirtualEnd = EndCoord
                #At this point we have processed all the top/left packing widgets and we
                #    have a list of the 'bottom/right' packing widgets in the correct
                #    order.
                for Coord, W in BottomList:
                    Result.append(W.CreationCode(MasterString,Indent,Wrap,IsMainForm))
                    Result.append(W.PackCode(Indent,Wrap,BottomRight))

                    Temp = W.BindCode(Indent,Wrap)
                    if Temp:
                        Result.append(Temp)

        if Whine and ErrorList <> []:
            ErrorList.sort()
            M = 'Frame{/s} $s contain{s/} widgets which are not clearly vertical ' \
                'or horizontal. Pack "side" settings have been ' \
                'assigned to the widgets in {that/those} frame{/s} with ' \
                'doubts as to your intent. Click help for details.'
            M = rpHelp.Plural(M,len(ErrorList),ToPercent='$')
            M = M%(', '.join(ErrorList))
            Rpw.MessageDialog(Title='Notice',Message=M,Buttons=(('Continue',None),)
                ,Help='pack.orientation-violation').Result
        #The list comprehension squished out empty lines. It is possible to get empty lines for example
        #    because the MainMenuBar widget doesn't need to get packed.        
        return '\n'.join([X for X in Result if X])        

    def Gather(self):
        """
        Return a dictionary that represents our form.

        o "['BaseClass']" The name of the class from which this module derives.

        o "['Lines']" A list of 3-tuples, each of which contains:
            o "[0]" The X generic coordinate.
            o "[1]" The Y generic coordinate.
            o "[2]" Dirn: 0 for horizontal, 1 for vertical
          Note that the lines are presented in order from most significant to least
              significant. Put another way, if you draw the lines in the order
              presented, you will get back the proper layout.

        o "['Name']" The name of the form.    

        o "['OnTab']" A boolean indicating if this 
        
        o "['Requested']" Either "Gui" or "Text" indicating which editor was most
            recently requested by the user.
    
        o "['SelectedWidreq']" The name of the currently selected widreq, or None if no
            selected widreq.
              
        o "['Type']" Either "Frame" or "Toplevel" indicating the type of the class
            from which this module derives.

        o "['Widreqs']" A list of dictionaries, each of which contains:
            o "['Name']" The name of this widreq, eg "MyButton"
            o "['WidgetName"] The type of widget, eg "Button"
            o "['XY']" A 2-tuple giving the XY generic coordinates
            o "['ID']" The frame-ID of this widreq, "None" if it isn't a frame.
            o "['Options']" A list of dictionaries:
                o "['Name']": The name of the option
                o "['Value']": The present value of the option
                o "['Extra']": The 'extra information' for this option.
            Note that *only* options whose value differs from the default value
                are included. Options whose value equals the default value are
                *NOT* shown here. Most options don't need extra information and
                the value for Extra for those options is None.
            o "['Bindings']" A list of dictionaries
                o "['Event']" The event string, eg "Button-Release-1"
                o "['Handler']" The name of the event handler, eg "on_MyButton_ButRel1"
            o "['PackOptions']" A list of dictionaries:
                o "['Name']" The name of the pack option.
                o "['Value']" The value of the pack option.
            Only those pack option whose value differs from the default option
                are listed.
        """
        F = Repo.FetchForm(self.HerdName)
        #
        # Lines, Name
        #
        Frames, Lines = self.FrameInfoGen()
        Temp = Lines[:]
        for J in range(len(Temp)):
            Temp[J][0], Temp[J][1] = CanvasToGeneric(tuple(Temp[J][0:2]),self.CanvasSize)
        Result = {'Lines':Temp,'Name':self.HerdName}
        #
        # Form stuff
        #
        Result['BaseClass'] = F['BaseClass']
        Result['OnTab'] = F['OnTab']
        Result['Requested'] = F['Requested']
        Result['Type'] = F['Type']
        Result['SelectedWidreq'] = Repo.FetchSelected(self.HerdName)
        #
        # Widreqs
        #
        WidreqList = []
        Widreqs = Repo.ListWidreqs(self.HerdName)
        for Name in Widreqs:
            W = Repo.Fetch(Name, self.HerdName)
            WidreqList.append(W.Gather(self.CanvasSize))
        Result['Widreqs'] = WidreqList    
        #D('Gather=%s'%Result)            
        return Result

    def Spanify(self, Box, Name, FrameDict, LineList=None):
        """=f
        Scan the rectangles; produce frame tree dictionary
        
        "Box" is a BoundingBox to be inspected, as "(X1,Y1,X2,Y2)".
        
        "Name" is a tuple of integers giving the 'name' of the box.
        
        "FrameDict" is a dictionary of information about the frame.
        
        Each entry in "FrameDict" represents one frame, although that frame may in
            turn contain sub-frames.
        
        The key for each item is the 'name' of the frame. The original parent is 
            named "(0,)"; it's sub-frames are named "(0,0)", "(0,1)", "(0,2)" and so on. 
            In my opinion, it does make at least some sense to use numeric-tuples
            to name frames.
        
        The value for each item is a dictionary:
            o ["'Bbox'"] A 4-list giving the bounding box of this frame.
            o ["'WidReqs'"] A list of the names of all the WidReq's which are inside
                  this frame. WidReq's are considered to be 'in' the most deeply 
                  nested frame.
            o ["'Dirn'"] If this box is one of some nested boxes, this indicates the
                orientation of boxes: 0 horizontal, 1 vertical.
            o ["'RelSize'"]: If the current box is one of several boxes nested inside 
                an enclosing box, this indicates the relative size of the current
                box with respect to its siblings: 0 for small, 1 for large. 
                If all siblings are of similar size, they are all marked as
                being 'large'.
                
        If "LineList" is not "None" then as we process lines we add one entry to the
            list for each line processed. The entry describing one line is a
            3-list thus:
                o "[0]" The X coordinate of the middle of the line.
                o "[1]" The Y coordinate of the middle of the line.
                o "[2]" Dirn: 0 for horizontal, 1 for vertical.
            *Note* that the lines will be in order from Major to Minor. That is, 
                starting from a blank canvas if you draw each line in turn as a 
                spanning line, then you should recreate the lines that were 
                scanned.    
                
        "Spanify" calls itself recursivly and that accounts for the strangeness of the
            arguments you need to pass it. If what you want to do is have "Spanify"
            scan an entire form then see method "FrameInfoGen". It does the necessary
            setup, calls "Spanify" and returns the result.        
        """
        SpanLines = self.LineSpanFind(Box)
        if LineList <> None:
            #We are accumulating information about lines
            for Line in SpanLines:
                XY = self.LineCenter(Line)
                Dirn = self.LineDirn(Line)
                LineList.append([XY[0], XY[1], Dirn])
        #D( 'Box=%s SpanLines=%s'%(`Box`,`SpanLines`))
        FrameDict[Name] = {'Bbox':Box,'WidReqs':[],'Depth':0}
        if len(SpanLines) <> 0:
            #this box is subdivided; process the sub-boxes
            SubBoxes = self.SpanToBoxes(Box,SpanLines)
            #get info about sub-box orientation and relative size
            BoxInfo = self.SubBoxAnalyze(SubBoxes)
            #FrameDict[Name]['Dirn'] = BoxInfo[0]
            #D( 'BoxInfo=%s'%BoxInfo)
            #print 'SubBoxes=%s'%`SubBoxes`
            for I in range(len(SubBoxes)):
                Sub = SubBoxes[I]
                #print Name,type(Name),I,type(I)
                SubName = Name + (I,)
                #recur to handle any subordinate boxes
                self.Spanify(Sub, SubName, FrameDict, LineList)
                #now that the sub-box entry is there, note relative size
                FrameDict[SubName]['RelSize'] = BoxInfo[1][I]
                FrameDict[SubName]['Dirn'] = BoxInfo[0]
        else:
            #this box is not subdivided; find any WidReqs in it.
            for WidReqName in Repo.ListWidreqs(self.HerdName):
                WidReq = Repo.Fetch(WidReqName, self.HerdName)
                if WidReq.InBox(Box):
                   #WidReq is in our bounding box
                   FrameDict[Name]['WidReqs'].append(WidReqName)

    def SubBoxAnalyze(self, B):
        """=v
        Beat information out of a list of sub boxes.
        
        "B" is a list of bounding boxes "(x1,y1,x2,y2)" which, when stacked together, 
            will all fit perfectly inside a rectangle. The boxes are stacked 
            either horizontally or vertically but NOT BOTH. The sub-boxes will
            be in order, ie, top-to-bottom or left-to-right.
            
        Our task is two fold:
            o Find out if the boxes are horizontal or vertical.
            o Decide if each box is 'large' or 'small'
            
        The result is a list:
            o "[0]" is 0 for horizontal boxes, 1 for Vertical boxes.
            o "[1]" is a list of the same length as "B". Each list element
                is for one box and is 0 for a small box, 1 for a large box.
                
        The large box/small box distinction is a judgement call. At the time of
            writing, we declare a box small if it is less than 60% percent of
            the size of the largest box of the group. This means that if all
            the boxes are roughly the same size, they will all be declared large.
        """
        assert len(B)>1, "A single box makes no sense here"
        if B[0][3] == B[1][1]:
            #The lower-right corner of the first box is at the same Y location
            #    as the uppler-left corner of the second box. That means the
            #boxes are horizontal.
            Dirn = 0
        elif B[0][2] == B[1][0]:
            #They match in the X direction. Vertical boxes.
            Dirn = 1
        else:
            assert 0, "First and second box don't match as expected"
        #Build list of sizes
        SizeList = len(B) * [0]
        Undirn = not Dirn
        for I in range(len(B)):
            SizeList[I] = B[I][Undirn+2] - B[I][Undirn]
        #Compute maximum size 'small' box
        MaxSmall = int(max(SizeList) * 0.6)
        #Convert SizeList to our small/large list
        for I in range(len(B)):
            SizeList[I] = SizeList[I] > MaxSmall
        return [Dirn,SizeList]    
        
    def FrameSanityCheck(self,Description):
        """
        Do a sanity check on frames.
        
        Description should be a string indicating when or by whom we were called.
        
        This makes sure that there is a one-to-one correspondence between visual frames as reported by spanify
            and frame WidReqs in the repository. If not we print useful information and pop up a dialog.
        """    
        FrameDict = self.FrameInfoGen()[0]
        ErrorCount = 0
        FramesProcessed = []
        #Check for WidReqs referencing non-existent frames
        for WidReqName in Repo.ListWidreqs():
            WidReq = Repo.Fetch(WidReqName)
            if WidReq.FrameID <> None:
                #This is a container widreq
                if FrameDict.has_key(WidReq.FrameID):
                    del FrameDict[WidReq.FrameID]
                    FramesProcessed.append((WidReq.FrameID,WidReqName))
                else:
                    #The frame referenced by WidReq is not in info. That could be because there was no such
                    #    frame or because the frame was referenced by two WidReqs - the current one and a
                    #    previously processed one. 
                    for ID,NameOfWidreq in FramesProcessed:
                        if ID == WidReq.FrameID:
                            #Two widreqs referenced the same frame
                            if ErrorCount == 0:
                                print('-----FrameSanityCheck %s-----'%Description)
                            print('   Error: Widreqs %s and %s both refer to frame %s'%(NameOfWidreq,WidReqName,str(ID)))
                            ErrorCount += 1
                            break
                    else:
                        #The widreq references a frame which doesn't exist
                        if ErrorCount == 0:
                            print('-----FrameSanityCheck %s-----'%Description)
                        print('   Error: WidReq "%s" referenced Frame %s which does not exist.'%(WidReqName,str(WidReq.FrameID)))
                        ErrorCount += 1
        #Check for frames to which no WidReq refers
        if len(FrameDict) <> 0:
            if ErrorCount == 0:
                print('-----FrameSanityCheck %s-----'%Description)
            for ID in FrameDict.keys():
                print('   Error: There is no frame WidReq which references Frame %s'%str(ID))
                ErrorCount += 1
        if ErrorCount == 0:
            pass
            ##D('---- No errors found by frame sanity check %s'% Description)
        #Dump info
        return
        #the following is a presently disabled debugging aid
        print('   List of visual frames as returned by spanify:')
        FrameDict, LineInfo = self.FrameInfoGen()
        Temp = FrameDict.keys()
        Temp.sort()
        for K in FrameDict.keys():
            print('      %s'%str(K))
        print('   List of lines as returned by spanify:')
        for L in LineInfo:
            print('      %s'%str(L))
        print('   List of frame WidReqs in repo:')
        for WidReqName in Repo.ListWidreqs():
            WidReq = Repo.Fetch(WidReqName)
            if WidReq.FrameID <> None:
                print('      Widreq %s, FrameID %s'%(WidReqName,str(WidReq.FrameID)))
        
    def BboxDictCreate(self,Info):
        """
        Return a dictionary where the key is the FrameID and the value is the bounding box of that frame.
        
        Info is as returnd by FrameInfoGen.
        
        Note that the result is based on the FrameID's as currently set in the frame widreqs of
            the current repository herd.
        """
        BboxDict = {}
        for WidReqName in Repo.ListWidreqs():
            WidReq = Repo.Fetch(WidReqName)
            if WidReq.FrameID <> None:
                #D('WidReqName=%s, WidReq.FrameID=%s'%(str(WidReqName),str(WidReq.FrameID)))
                #This is a container widreq
                ##D('Widreq=%s attributes=%s'%(WidReqName,dir(WidReq)))
                try:
                    BboxDict[WidReqName] = Info[0][WidReq.FrameID]['Bbox']
                except KeyError:
                    print 'Widreq.FrameID=%s'%str(WidReq.FrameID)
                    print 'Info[0]=%s'%str(Info[0])
                    raise Exception, "Key error building bounding box dictionary; details printed"
        return BboxDict
        
    def SpanToBoxes(self,Box,SpanList):
        """=v
        Compute sub-bounding boxes from a bounding box and span lines.
        
        Lines which span a bounding box divide that bounding box up into two or
            more sub boxes. Given a bounding box and zero or more span lines,
            this routine computes a list of sub-bounding boxes.
            
        The result is a list of one or more 4-lists, each giving X1,Y1,X2,Y2
            for each of the sub-bounding boxes. The sub-bounding boxes will be
            in order: top-to-bottom or left-to-right.
            
        Note that if SpanList is empty what you get back is, reasonably enough,
            the original bounding box.        
        """
        #get a list of span line ID's
        SpanList = self.LineSpanFind(Box)
        #convert each ID to it's end-point-list
        for I in range(len(SpanList)):
            SpanList[I] = self.LineEndPoints(SpanList[I])
        SpanList.sort()
        First = Box[:2]
        Result = []
        for Span in SpanList:
            Result.append(First+Span[2:])
            First = Span[:2]
        Result.append(First+Box[2:])
        return Result

    def LineSpanFind(self,Box):
        """=v
        Find lines that span a bounding box.
        
        Given a bounding box (X1,Y1,X2,Y2) we return a list of any of our lines
            which run from one edge of the box to the other.
            
        Each item in the result is an ID number of a line in our canvas.    
        """
        #print 'Box=%s'%Box
        Result = []
        LineList = list(self.find_all())
        self.JustLines(LineList)
        BoxXXYY = ((Box[0],  Box[2]), (Box[1], Box[3]))
        for L in LineList:
            LineEnds = self.LineEndPoints(L)
            #print 'LineEnds=%s'%LineEnds
            #Eliminate lines which are coincident with the bounding box 
            Dirn = self.LineDirn(LineEnds)
            Undirn = not Dirn
            if LineEnds[Undirn] in (BoxXXYY[Undirn]):
                #this line is coincident
                continue
            if LineEnds[Dirn] == Box[Dirn] and LineEnds[Dirn+2] == Box[Dirn+2] \
            and Box[Undirn] < LineEnds[Undirn] < Box[Undirn+2]:    
                #this line spans the entire bounding box in its main direction 
                #and is inside the bounding box in the other direction
                Result.append(L)
                #print 'Line %s spans %s'%(`LineEnds`,`Box`)
        return Result    

    def CanvasObjectInfo(self,ID):
        """=v
        Return a string of information about the specified canvas object.
        """
        Type = self.type(ID)
        Tags = self.gettags(ID)
        Result = 'CanvasID=%s Type=%s Tags=%s'%(ID,Type,Tags)
        return Result
        
    def CanvasDump(self):
        """=v
        Display info about every object on our canvas
        """
        for ID in self.find_all():
            print self.CanvasObjectInfo(ID)    
        print 'Canvas.winfo_width=%s Canvas.winfo_height=%s'%(self.winfo_width(),self.winfo_height())    

    def JustLines(self,IdList):
        """=l
        Given a list of canvas object ID's remove any that are *not* our lines.
        
        *This method modifies the list passed*
        
        We recognize our lines by the fact that they have a tag of "LineTag".
        """
        #We go in reverse order so deletions don't affect entries we 
        # haven't yet processed.
        L = range(len(IdList))
        L.reverse()
        for I in L:
            if not GuiEditor.LineTag in self.gettags(IdList[I]):
                #current item is not one of our lines
                del IdList[I]

    def LineFindNear(self,X,Y,Delta=2):
        """=l
        Look for one of our lines near (X,Y).
        
        If found the result is the lines ID.
        If more than one line is found we pick one arbitrarily.
        If not found the result is None.
        
        We look within radius "Delta" of the point specified.
        """
        #get list of *anything* near our target
        L = list(self.find_overlapping(X-Delta,Y-Delta,X+Delta,Y+Delta))
        #weed out things that aren't our lines
        self.JustLines(L)
        if len(L) == 0:
            Result = None
        else:
            Result = L[0]    
        return Result    

    def LineFindExact(self,LineEndPoints):
        """=l
        Given a line as (x1,y1,x2,y2) return it's canvas ID if found, or None
        """
        Tag = self.LineEndpointsFormat(LineEndPoints)
        Temp = self.find_withtag(Tag)
        if len(Temp) == 0:
            return None
        else:
            return Temp[0]

    def LineDirn(self,LineInfo):
        """=l
        Given a line, return 0 for horizontal, 1 for vertical.
        
        LineInfo can be either a line ID or 4-tuli X1,Y1,X2,Y2.
        """
        if type(LineInfo) == type(1):
            LineInfo = self.LineEndPoints(LineInfo)
        if LineInfo[0] == LineInfo[2]:
            return 1
        if LineInfo[1] == LineInfo[3]:
            return 0
        raise Exception, 'Line %s is diagonal'%`LineInfo`        

    def LineCrossCheck(self,ID1,ID2):
        """=l
        Given 2 line ID's return intersection point if they cross, or None.
        
        The lines must be either horizontal or vertical, not diagonal.
        """
        Info = [self.LineEndPoints(ID1),self.LineEndPoints(ID2)]
        assert Info[0][0]<>Info[0][2] or Info[0][1]<>Info[0][3], 'Line-1 is diagonal %s'%`Info`
        assert Info[1][0]<>Info[1][2] or Info[1][1]<>Info[1][3], 'Line-2 is diagonal %s'%`Info`
        if Info[0][0]==Info[0][2] and Info[1][0]==Info[1][2]:
            #both lines are vertical
            return None
        if Info[0][1]==Info[0][3] and Info[1][1]==Info[1][3]:
            #both lines are horizontal
            return None
        # The lines are perpindicular; we want ((HorizBB),(VertBB)).
        # Note: For most of this calculation we don't care which is the vertical
        #       and which is the horizontal line, but when it comes time to
        #       produce the result we need to select the vertical-X and the
        #       and the horizontal-Y so at some point we have to care.
        if Info[0][1] <> Info[0][3]:
            #but we it's reversed, so flip them
            Info.reverse()
        HStart = Info[0][0] #H-lines X start point
        HEnd =   Info[0][2] #H-lines X end point
        HY =     Info[0][1] #H-lines Y position
        YStart = Info[1][1] #V-lines Y start point
        YEnd   = Info[1][3] #V-lines Y end point
        VX     = Info[1][0] #V=lines X position
        if HStart<=VX and HEnd>=VX and YStart<=HY and YEnd >=HY:
            #great zot, they cross or at least touch
            return [VX,HY]
        else:
            #they don't even touch
            return None    

    def LineEndPoints(self,ID):
        """=l
        Given a line ID, return line end points [x1,y1,x2,y2].
        
        The ID passed must be that of a line which we drew and
        which contains a tag showing the end points.
        """
        Tags = self.gettags(ID)
        for T in Tags:
            if T[0] == '(':
                #this is the tag (generated by self.Draw) which lists our
                #end points
                return list(eval(T))
        raise Exception, 'Location tag not found in line %s'%ID        

    def LineCenter(self,ID):
        """=l
        Given a line ID, return the center point of the line [X,Y]
        """
        T = self.LineEndPoints(ID)
        return [(T[0]+T[2])/2, (T[1]+T[3])/2]

    def ConstraintBoxFind(self,ID):
        """=l
        Given the ID of an existing line return it's constraint box.
        
        The result is a list [x1,y1,x2,y2].
        
        When we go to move an existing line, there are constraints on all four
         sides. The user is allowed to move the mouse freely within the constraint
         box but when it moves outside that box we 'clip' the mouse position at
         the edge of the constraint box which effectivly keeps the mouse position
         inside the constraint box. This routine computes the constraint box for
         any given line.
        
        For the sake of discussion consider a vertical line. The top (y1) and 
         bottom (y2) constraints are one inside the top and bottom of the line.
         The left (x1) constraint is the closest vertical line to the left of the
         subject line which falls within the Y range of the subject line plus a
         fudge factor 'Bumper'. If there is no such left line, the left 
         constraint is the left side of the canvas plus bumper. Less technically, 
         the left constraint is Bumper away from the first line into which we
         would bump if moved left. 
        """
        #Get list of all canvas objects
        LineList = list(self.find_all())
        #Weed out non-lines
        self.JustLines(LineList)
        #Weed out the subject line
        I = LineList.index(ID)
        del LineList[I]
        #get subject line end points for future use
        SubX1, SubY1, SubX2, SubY2 = self.LineEndPoints(ID)
        if self.LineDirn(ID) == 0:
            #horizontal line
            X1 = SubX1+1
            X2 = SubX2-1
            #assume the canvas edges are the top and bottom constraints
            Y1 = 0 + GuiEditor.Bumper
            Y2 = self.CanvasSize[1] - GuiEditor.Bumper
            #now look for possibly more constraining lines
            for L in LineList:
                if self.LineDirn(L) == 0:
                    #L is a horizontal line; get it's end points
                    LX1, LY1, LX2, LY2 = self.LineEndPoints(L)
                    if LX1 < X2 and LX2 > X1:
                        #This is a potentially constraining line
                        if LY1 < SubY1:
                            #L is above our line
                            Y1 = max(Y1,LY1+GuiEditor.Bumper)
                        else:
                            #L is below our line
                            Y2 = min(Y2,LY1-GuiEditor.Bumper)    
        else:
            #vertical line
            Y1 = SubY1+1
            Y2 = SubY2-1
            #assume the canvas edges are the left and right constraints
            X1 = 0 + GuiEditor.Bumper
            X2 = self.CanvasSize[0] - GuiEditor.Bumper
            #now look for possibly more constraining lines
            for L in LineList:
                if self.LineDirn(L) == 1:
                    #L is a vertical line; get it's end points
                    LX1, LY1, LX2, LY2 = self.LineEndPoints(L)
                    if LY1 < Y2 and LY2 > Y1:
                        #L's top is above our bottom and L's bottom is above our top
                        #This is a potentially constraining line
                        if LX1 < SubX1:
                            #L is left of our line
                            X1 = max(X1,LX1+GuiEditor.Bumper)
                        else:
                            #L is right of our line
                            X2 = min(X2,LX1-GuiEditor.Bumper)    
        return [X1,Y1,X2,Y2]            

    def NewLineCheck(self,X,Y,Dirn):
        """        =l
        See if a new line at the specified location is allowed.
        
        Result is 1 if yes, 0 if no.
        
        A line is allowed unless it would be within 'Bumper' distance of an
            adjacent parallel line or the edge of the canvas.
        """
        Undirn = not Dirn
        LineList = list(self.find_all())
        Point = (X,Y)
        if Point[Undirn] < GuiEditor.Bumper:
            #too close to top or left edge
            return 0
        if (self.CanvasSize[Undirn] - Point[Undirn]) < GuiEditor.Bumper:
            #too close to bottom or right edge
            return 0
        self.JustLines(LineList)
        #check all lines we have created
        for L in LineList:
            LineInfo = self.LineEndPoints(L)
            if self.LineDirn(LineInfo) == Dirn:
                #this line is paralel
                if Point[Dirn] < LineInfo[Dirn] or Point[Dirn] > LineInfo[Dirn+2]:
                    #point is beyond range of line; no conflict
                    continue
                if abs(LineInfo[Undirn]-Point[Undirn]) < GuiEditor.Bumper:
                    #this line is too close
                    return 0
        #no conflict found            
        return 1            
        
    def TermLinesFind(self,ID):
        """=l
        Find any lines that terminate on a given line.
        
        "ID" is the given line.
        The result is a list of line ID's of any lines which terminate on the given line.
        """
        #Find anything that overlaps the subject line
        BB = self.bbox(ID)
        L = list(apply(self.find_overlapping,BB))
        #Weed out non-lines
        self.JustLines(L)
        #Weed out the subject line
        I = L.index(ID)
        del L[I]
        #We now have a list of lines which anywhere touch the subject line.
        # However, we only want to know about lines which touch the subject
        # line along it's span, not at it's ends. Thus we go weeding those out.
        IndexList = range(len(L))
        IndexList.reverse()
        for I in IndexList:
            T = L[I]
            #Look for the intersection point of the two lines
            Int = self.LineCrossCheck(ID,T)
            if Int:
                #they do intersect
                Tgt = self.LineEndPoints(T)
                if Tgt[:2] <> Int and Tgt[2:]<>Int:
                    #neither of the target lines end point coincide with the
                    # intersection point, therefore the target line does not
                    # terminate on the subject line.
                    del L[I]
            else:
                #These lines don't even cross. This can happen when two parallel
                #lines happen to meet end-to-end at a common perpindicular line.
                #Thanks to Andrea for finding this case. Since the target line
                #doesn't even cross the subject line it certainly isn't a termline
                #so we delete it from the list.
                del L[I]
        return L

    def LinesPerpInfoGather(self,ID1,ID2):
        """=l
        Get certain information about perpindicular lines.
        
        Given two *perpindicular* lines, return a three element list thus:
            o "[0]" "+1" if line2 is to the right of or below line1
                "-1" if line2 is to the left of or above line 1
            o "[1]" The position of line2 on line1, that is, if line1 is vertical
                then this is the Y location at which line2 intersects line1;
                if line1 is horizontal then this is the X location at which line2
                intersects line1.
            o "[2]" The Dirn of line2: 0=horizontal, 1=vertical    
        """
        Dirn = self.LineDirn(ID2)
        Cent = self.LineCenter(ID2)
        Ends = self.LineEndPoints(ID1)
        if Cent[Dirn] > Ends[Dirn]:
            Offset = +1
        else:
            Offset = -1
        Pos = Cent[not Dirn]    
        return [Offset, Pos, Dirn]        

    def LinesInsideCount(self,Bbox,Dirn,Info):
        """
        Given a bounding box and a direction return a count of lines whose center is within the box and whose direction matches.
        
        Info is a returned by Spanify.
        """
        X1,Y1,X2,Y2 = Bbox
        Result = 0
        for X,Y,Dn in Info[1]:
            if Dn==Dirn and X >= X1 and X <= X2 and Y >= Y1 and Y <=Y2:
                Result += 1
        return Result

    def PointInBB(self,XY,BB):
        """=f
        Check to see if a point is INSIDE a bounding box.
        
        If the point is INSIDE the bounding box we return 1
        If the point is ON the bounding box we return NONE.
        If the point is OUTSIDE the bounding box we return 0
        """
        X, Y = XY
        BBX1, BBY1, BBX2, BBY2 = BB
        if X in (BBX1, BBX2) or Y in (BBY1, BBY2):
            #the point is on the bounding box
            return None
        if X < BBX1 or X > BBX2 or Y < BBY1 or Y > BBY2:
            #the point is outside the bounding box
            return 0
        #The point must be inside the bounding box
        return 1    
        
    def FrameInfoFormat(self,FrameInfo=None):
        """
        Format the information returned by FrameInfoGen.
        
        If FrameInfo is passed, we format that. If not passed we call FrameInfoGen to
            get the information to format.
        """ 
        Result = []   
        if FrameInfo == None:
            FrameInfo = self.FrameInfoGen()
        for ID,Info in FrameInfo[0].items():
            Result.append('%s: %s'%(str(ID),str(Info)))
        for Item in FrameInfo[1]:
            Result.append(str(Item))
        return '\n'.join(Result)        

    def FrameInfoGen(self):
        """=f
        Invoke "Spanify" to compute a tuple of frame information.
        
        This is just a convenience routine that looks after the detail work 
            involved in calling "Spanify".
        
        Result:
            o "[0]" is the FrameDictionary returned by "Spanify".
            o "[1]" is the LineList returned by "Spanify"
        """
        D = {}
        L = []
        CanvasBbox = [0,0] + self.CanvasSize
        self.Spanify(CanvasBbox,(0,),D,L)
        return (D,L)
    
    def FrameNameInner(self,FrameDict):
        """=f
        Given a FrameDictionary generate a list of keys, sorted inner-most first.
        """
        #Create a list of (len,ID)
        FrameList = FrameDict.keys()
        #Get a list of (Depth,Key)
        Temp = [(len(X),X) for X in FrameList]
        #Temp = zip(,FrameList)
        #reverse sort the list
        Temp.sort()
        Temp.reverse()
        #return just the ID's in sorted order
        return [X[1] for X in Temp] #wow - I actually used a list comprehension

    def EnclosingFrameFind(self,CanvasXY,FrameDict):
        """=f
        Find out which frame a given canvas point is in.
        
        "CanvasXY" is a Canvas (not window) point.
        "FrameDict" holds frame information, as produced by Spanify.
        
        If the point is on a bounding line then it is ambiguous and we return None.
        
        Otherwise we find the innermost frame which contains the point and we return
            it's frame ID.
        """
        Sorted = self.FrameNameInner(FrameDict)
        for Frame in Sorted:
            Temp = self.PointInBB(CanvasXY,FrameDict[Frame]['Bbox']) 
            if Temp == 1:
                return Frame
            elif Temp == None:
                return None
        #Point was not in any frame; not supposed to happen
        raise Exception, "Point %s not found in any frame"%str(FrameDict)            

    def FramesAreSiblings(self,F1,F2):
        """=f
        Given two Frame ID's return True if the frames are siblings.
        
        A frame is not it's own sibling; if F1 == F2 we return False.
        """
        return len(F1) == len(F2) and F1 <> F2 and F1[:-1] == F2[:-1]
        
    def FindChildren(self,FrameID,InfoDict):
        """
        Given a FrameID return list of it's children.
        
        InfoDict is as returned by Spanify.
        """
        Result = []
        for ID in InfoDict.keys():
            if len(ID) > len(FrameID) and ID[:len(FrameID)] == FrameID:
                Result.append(ID)
        return Result

    def FindSiblings(self,FrameID,InfoDict):
        """
        Given a FrameId return list of it's siblings
        
        InfoDict is as returned by Spanify
        """
        Result = []
        for ID in InfoDict.keys():
            if self.FramesAreSiblings(FrameID,ID):
                Result.append(ID)
        return Result        

    def HasChildren(self,FrameID,InfoDict):
        """
        Given a FrameID return 1 if the frame has children, else 0.
        
        InfoDict is as returned by Spanify.
        """
        for ID in InfoDict.keys():
            if len(ID) > len(FrameID):
                if ID[:len(FrameID)] == FrameID:
                    return 1
        return 0            
        
    def FramesCommonLineFind(self,A,B,Info):    
        """=f
        If two frames share a common line, return it as (X1,Y1,X2,Y2), else return None.
        
        "Info" is "[FrameDictionary, LineList]" as returned by "Spanify".
        """
        FrameDict, LineList = Info
        Ax1, Ay1, Ax2, Ay2 = FrameDict[A]['Bbox']
        Bx1, By1, Bx2, By2 = FrameDict[B]['Bbox']
        if Ax1==Bx1 and Ax2==Bx2:
            #The X coordinates match; we may have vertically adjacent frames
            if Ay1==By2:
                #B lies just above A
                return (Ax1,Ay1,Bx2,By2)
            elif Ay2==By1:
                #B lies just below A
                return (Bx1,By1,Ax2,Ay2)
            else:
                #not adjacent vertically
                return None        
        elif Ay1==By1 and Ay2==By2:
            #The Y coordinates match; we may have horizontally adjacent frames
            if Ax1==Bx2:
                #B lies just left of A
                return (Ax1,Ay1,Bx2,By2)
            elif Ax2==Bx1:
                #B lies just right of A
                return (Bx1,By1,Ax2,Ay2)
            else:
                #not adjacend horizontally
                return None    
        else:
            #Neither coordinate matches.
            return None        
        
    def SiblingsCommonLinesFind(self,ID,Info):
        """=f
        Find any lines which are shared by a specified frame and its siblings.
        
        "ID" is the canvas line ID of the subject line.
        "Info" is "[frame, line]" information returned by Spanify.
        
        The result is a list of 3-tuples "(X,Y,Dirn)" of lines. 
        
        """
        Result = []
        FrameDict, LineList = Info
        for FrameID in FrameDict.keys():
            #Step through every frame
            if self.FramesAreSiblings(ID,FrameID):
                Temp = self.FramesCommonLineFind(ID,FrameID,Info)
                if Temp <> None:
                    #The frames share a common line; add it to result list
                    Result.append(Temp)
        return Result            

    def FrameMark(self,FrameID,Info=None,Width=5,Color='#b0b0b0'):
        """=f
        Mark the specified frame to draw attention to it.
        
        The default mark is a gray rectangle of width 5, but you can specify a
            different "Width" and/or "Color".

        "FrameID" is the ID of the frame to be marked. If None, then we remove
            any existing frame mark.
        
        "Info: is frame and line information returned by Spanify. If not supplied we
            call Spanify to generated it. 
        
        """
        #Delete any current frame mark.
        FrameMarkTag = 'FrameMark'
        self.delete(FrameMarkTag)
        if FrameID <> None:
            #Mark the specified frame
            if Info == None:
                #In this case we call spanify to get the info
                Info = self.FrameInfoGen()
            X1,Y1,X2,Y2 = Info[0][FrameID]['Bbox']
            ##D('Bbox=%s CanvasSize=%s W,H=%s'%([X1,Y1,X2,Y2],self.CanvasSize
            ##    ,[self.winfo_width(),self.winfo_height()]))
            #And now for a minor annoying wrinkle. If we are drawing against the outside edge of
            #    the form then we want the frame mark tight up against the edge. For example if
            #    we are drawing down the left side of the form at X=0 then we actually want to
            #    draw along the X=0 pixels. On the other hand if we are drawing up against a
            #    frame boundry line, we want to draw one away from the line, otherwise we wipe
            #    out the line itself. For example if drawing along a vertical line a X=37 then we
            #    want (assuming we are on the right side of the line) to draw at X=38. Hence
            #    the following little dance of adjustment.
            if X1 > 0:
                X1 += 1
            if Y1 > 0:
                Y1 += 1
            if X2 < self.CanvasSize[0]:
                X2 -= 1        
            if Y2 < self.CanvasSize[1]:
                Y2 -= 1
            #F - the fudge factor. If we draw a frame mark of width greater than 1, then it spills
            #    onto either side of the area we specify. However, the numbers we have at this
            #    point specify the OUTSIDE of where we want to frame to appear, hence we have to
            #    adjust by our fudge factor.
            F = max(Width/2,1)
            X1 += F
            Y1 += F
            X2 -= F
            Y2 -= F
            #Were finished messing around with adjustmens; draw the thing already.    
            self.create_rectangle(X1,Y1,X2,Y2,outline=Color,width=Width,tags=FrameMarkTag)
            self.update_idletasks()

    def LineInLine(self,A,B):
        """
        Return 1 if line A lies entirely within line B.
        
        This routine only works if A and B are horizontal or vertical, not diagonal.
        """
        Ax0,Ay0,Ax1,Ay1 = A
        Bx0,By0,Bx1,By1 = B
        if Ax0 == Ax1:
            #A is vertical
            if Bx0 == Bx1:
                #B is vertical
                if Ax0 == Bx0:
                    #A and B share X location
                    if Ay0 >= By0 and Ay1 <= By1:
                    #they match
                        return 1
        if Ay0 == Ay1:
            #A is horizontal
            if By0 == By1:
                #B is horizontal
                if Ay0 == By0:
                    #A and B share Y location
                    if Ax0 >= Bx0 and Ax1 <= Bx1:
                        #they match
                        return 1
        return 0                                
        
    def BboxDifference(self,A,B):
        """
        Compute difference information about two bounding boxes.
        
        If A and B are identical we return 0.
        If 3 of A's lines are identical-to or lie-along B's lines we return 1
        Else we return 2
        """
        if A == B:
            return 0
        Ax0,Ay0,Ax1,Ay1 = A
        Bx0,By0,Bx1,By1 = B
        Count =  self.LineInLine((Ax0,Ay0,Ax1,Ay0),(Bx0,By0,Bx1,By0)) #top
        Count += self.LineInLine((Ax0,Ay0,Ax0,Ay1),(Bx0,By0,Bx0,By1)) #left
        Count += self.LineInLine((Ax0,Ay1,Ax1,Ay1),(Bx0,By1,Bx1,By1)) #bottom
        Count += self.LineInLine((Ax1,Ay0,Ax1,Ay1),(Bx1,By0,Bx1,By1)) #right
        if Count == 3:
            return 1
        return 2    

    def EventXYCanvas(self,Event,Canvas):
        """=v
        Given an event against our Canvas, return the "(X,Y)" Canvas (not screen) coordinates.
        """
        return (int(round(self.canvasx(Event.x))), int(round(self.canvasy(Event.y))))

    def FramesRemediate(self,BboxDict,Mode):
        """
        Remediate frameID's of FrameWidRew's following frame insertion or deletion.
        
        BboxDict is a FrameName->BoundingBox dictionary.
        
        Both the above must represent the situation *before* the addition/deletion.
        
        Mode is 'd' if we are remediating following deletion, 'i' if after insertion.
        
        Frames have two designations. There is the user-assigned-name (eg Frame7) and thre is
            also the internal FrameID assigned by spanify (eg (0,1,0)). When a new frame-line
            is inserted or a frame is deleted then the FrameID's can change. The point of this
            routine is to look at the newly assigned FrameID's and to associate them with the
            existing FrameWidReq's. If FrameWidReq's need to be deleted or created then we look
            after that here. Note that in the case of deletion, it is the callers responsibility
            to have delete the containee widreqs from within the FramwWidReq.
            
        The general plot is that before doing the creation or deletion you call BboxDictCreate to
            create a dictionary which lists *existing* frame user names and their corresponding frame
            bounding box.
            
            After the insertion/deletion you call this routine which, using the bounding box
            information, figures out which existing FrameWidReq corresponds to which FrameID and
            updates the FrameWidReq's with their new FrameID.
            
        Note that the deletion of a single frame can result in more than one frame going away. The
            case where two go away is obvious and common. It is not difficult to construct a case
            where three go away. It may be possible to make four or more go a way but I haven't
            yet discovered examples.
        """
        #D('FramesRemediate')
        assert Mode in 'di'
        #Info represents the new state of affairs as reported by spanify
        Info = self.FrameInfoGen()
        ##D('--- Begin FrameRemediate.\nBboxDict=%s\nInfo[0]=%s\nInfo[1]=%s'%(DictPretty(BboxDict),DictPretty(Info[0]),str(Info[1])))
        #---Phase 1: make a list of (Name,FrameID) tuples for those cases where the
        #   old and new bounding boxes match exactly.
        Match = []
        for Name,Bbox in BboxDict.items():
            for ID in Info[0].keys():
                if Bbox == Info[0][ID]['Bbox']:
                    Match.append((Name,ID))
        #---Phase 2: Set the new FrameID in the widreqs and delete the corresponding
        #   entries from both dictionaries, since they have been processed.
        #D('Exact match list=%s'%Match)
        for Name,ID in Match:
            W = Repo.Fetch(Name)
            assert W <> None, 'We were expecting a widreq'
            W.FrameID = ID
            del Info[0][ID]
            del BboxDict[Name]
            ##dDD(B of frame %s exactly matches new frame %s'%(Name,str(ID)))
        #---Phase 3: Make a list of (Name,FrameID) tuples for those cases where 3
        #   of the old bounding box lines are within the corresponding line of the
        #   new bounding box.
        Match = []
        NamesMatched = []
        for Name,Bbox in BboxDict.items():
            for ID in Info[0].keys():
                #Note that we reverse the order of arguments to BboxDifference depending on whether
                #    frames are being deleted or added. This is important. 
                if Mode == 'd':
                    if 1 == self.BboxDifference(Bbox,Info[0][ID]['Bbox']):
                        Match.append((Name,ID))
                else:
                    if 1 == self.BboxDifference(Info[0][ID]['Bbox'],Bbox):
                        Match.append((Name,ID))
                        #This break is required. When new frames are created there
                        #can be two which match to old enclosing frame but we want
                        #to assign only one of them the identity of the old frame
                        #Without the break we would attempt to assign the old
                        #frame identity to two new frames. Ixnay.
                        break
        #---Phase 4: Set the new FrameID in the widreqs and delete the corresponding
        #   entries from both dictionaries, since they have been processed.
        #D('3-side match list=%s'%Match)
        for Name,ID in Match:
            #D('--BbboxDict=%s'%str(BboxDict))
            #D('--Info[0]=%s'%str(Info[0]))
            W = Repo.Fetch(Name)
            assert W <> None, 'We were expecting a widreq'
            W.FrameID = ID
            del Info[0][ID]
            del BboxDict[Name]
            ##D('BB of frame %s is a 3-side match for new frame %s'%(Name,str(ID)))
        if Mode == 'd':
            #---Phase 5: Sanity checking - deletion mode. If things have gone as expected, 
            #   the dictionary of new frames should be empty (because we have proccessed 
            #   them all) 
            assert len(Info[0]) == 0
            #---Phase 6 - deletion mode: If BboxDict isn't empty then we need to delete any 
            #   frames it mentions because they have gone away.
            for Name in BboxDict.keys():
                R = Repo.Request(self.WRID,'WidreqDelete',Name)                
                if R <> 1:
                    print 
                    Rpw.MessageDialog(Message='Widget deletion failed unexpectedly with reason: %s from %s'%(R[0],R[1]))
        else:
            #---Phase 5: Sanity checking - insertion mode. If things have gone as expected,
            #   the dictionary of old frames should be empty (because we have processed
            #   them all) and the number of items in the dictionary of new frames should
            #   be 1 or 2.
            if len(BboxDict) <> 0:
                print 'BboxDict=%s'%str(BboxDict)
                raise Exception, "Expecting BboxDict to be empty but it was not. Info printed."
            if len(Info[0]) not in (0,1,2):
                #Normally we will have 1 or 2 new frames. That said, if the user starts to
                #    create a new frame but they drops in the middle of nowhere (thus aborting
                #    the frame creation) we can end up with zero.
                print 'Info[0]=%s'%str(Info[0])
                raise Exception, "Was expecting Info[0] to have 1 or 2 items. Info printed."
            #---Phase 6 - insertion mode. We need to create FrameWidreqs for the frame(s)
            #   mentioned in the list of new frames.
            NeedToSelect = True
            for NewFrameID in Info[0].keys():
                #This frame needs a WidReq; create and register a Frame instance
                NewFrameName = NameWidReq('Frame')
                Temp = WidReq('Frame',NewFrameName,NewFrameID,self.HerdName,ModuleName='Tkinter')
                R = Repo.Request(self.WRID,'WidreqCreate',NewFrameName,Temp)
                if R <> 1:
                    Repo.Tell(R)
                    raise Exception, "Unexpected Repo result"
                #Create the initial representation    
                Temp.WidgetShow(None,self,IsSelected=NeedToSelect)            
                if NeedToSelect:
                    #Request selection so everybody knows it is the selected item
                    R = Repo.Request(self.WRID,'WidreqSelect',NewFrameName)
                    if R <> 1:
                        Repo.Tell(R)
                        raise Exception, "Unexpected Repo result"
                NeedToSelect = False
                ##D('Frame %s <-> %s'%(str(ID),NewFrameName))


        #Regenerate code to reflect changed frame layout
        GblLayout.CreationSystextRegen('GuiEditor - frame deletion')
        

    def on_Button3Down(self,Event):
        """=e
        User requested frame popup menu
        """
        #Select our form and bail if selection is declined
        WeAreNewlySelected = Repo.SelectedHerd <> self.HerdName
        R = Repo.Request(self.WRID,'HerdSelect',self.HerdName)
        if R <> 1:
            #Somebody objected; cancel popup
            return
        CanvasXY = self.EventXYCanvas(Event, self)
        #Info holds (FrameDict, LineList)
        FrameInfo = self.FrameInfoGen()
        PopupData = {'Info' : FrameInfo}
        PopupData['CanvasXY'] = CanvasXY
        
        #If we were the selected herd AND a container widreq is selected AND where the user clicked is
        #    inside that selected widreq THEN we want to work against that selected wireq ELSE select
        #    the innermost frame around where the user clicked and work against that frame. 
        #---Find the currently selected widreq---
        CSW = Repo.Fetch(Repo.FetchSelected())
        if not WeAreNewlySelected and CSW.FrameID <> None and self.PointInBB(CanvasXY,FrameInfo[0][CSW.FrameID]['Bbox']):
            #We were the selected herd AND a container widreq is selected AND we clicked inside it
            PopupData['FrameID'] = CSW.FrameID
            PopupData['FrameWidget'] = Repo.FindFrame(PopupData['FrameID'])
            PopupData['FrameName'] = PopupData['FrameWidget'].Name
        else:    
            #Find the frame in which the user clicked    
            PopupData['FrameID'] = self.EnclosingFrameFind(CanvasXY,PopupData['Info'][0])
            if PopupData['FrameID'] == None:
                #The user clicked over a bounding line; nothing to do
                return
            PopupData['FrameWidget'] = Repo.FindFrame(PopupData['FrameID'])
            PopupData['FrameName'] = PopupData['FrameWidget'].Name
            #Attempt to select the frame we are in
            R = Repo.Request(self.WRID,'WidreqSelect',PopupData['FrameName'])
            if R <> 1:
                #That didn't fly
                return

        CSW = Repo.Fetch(Repo.FetchSelected())
        
        #Enable the 'Delete' choice unless this is the main frame or this frame contains children.
        PopupData['IsMainframe'] = PopupData['FrameID'] == (0,)
        DelState = (NORMAL,DISABLED)[PopupData['IsMainframe'] or self.HasChildren(PopupData['FrameID'],FrameInfo[0])]

        #Enable the 'Tidy' choice unless there are no widreqs in the frame to tidy
        WidreqCount =  len(PopupData['Info'][0][PopupData['FrameID']]['WidReqs'])
        TidyState = (DISABLED,NORMAL)[WidreqCount>1]
        
        #Now it's time to decide about the "insert-frame" choices. For insert to be allowed on any given side, 
        #    there must be no lines which are parellel to that side and which are wholely withing Bumper*2 of that side.
        Left = False
        Right = False
        Above = False
        Below = False
        #Get bounding box for our frame, save in PopupData then explode to four variables
        X1,Y1,X2,Y2 = PopupData['Bbox'] = FrameInfo[0][PopupData['FrameID']]['Bbox']
        #Contract the bounding box by one pixel. If we don't do this, then when we check for parallel lines which
        #    are within Bumper*2 we find the line which makes up the frame itself. Since any existing lines will
        #    be at least Bumper away, contracting by one pixel here does no harm
        X1 += 1
        Y1 += 1
        X2 -= 1
        Y2 -= 1
        #A handy nickname 
        B2 = GuiEditor.Bumper * 2
        #Initially set flags based on there being no parallel lines within Bumper*2 of the sides of our frame
        Left  = self.LinesInsideCount((X1,   Y1,X1+B2,Y2   ),1,FrameInfo) == 0
        Right = self.LinesInsideCount((X2-B2,Y1,X2,   Y2   ),1,FrameInfo) == 0
        Above = self.LinesInsideCount((X1,   Y1,X2,   Y1+B2),0,FrameInfo) == 0
        Below = self.LinesInsideCount((X1,Y2-B2,X2,   Y2   ),0,FrameInfo) == 0
        #Now disallow if the frame itself is less than Bumper*2 high/wide
        if (X2-X1) < B2:
            Left = Right = False
        if (Y2-Y1) < B2:
            Above = Below = False
        #Build the popup menu        
                    
        Bgc = '#000000'
        HandlerPopup = Menu(self,tearoff=0)
        HandlerPopup.add_command(label='Frame: %s'%PopupData['FrameName'],state=DISABLED
            ,activeforeground='#FFFFFF',foreground='#FFFFFF',background=Bgc,activebackground=Bgc)
        HandlerPopup.add_separator()

        HandlerPopup.add_command(label='Properties',command=Wow(self,'on_PopupFrameProperties',PopupData))
        HandlerPopup.add_command(label='Tidy widgets',command=Wow(self,'on_PopupFrameTidy',PopupData)
            ,state=TidyState)
            
        HandlerPopup.add_separator()
        DN = (DISABLED,NORMAL)
        HandlerPopup.add_command(label='Insert frame left', state=DN[Left], command=Wow(self,'on_PopupInsertLeft',PopupData))
        HandlerPopup.add_command(label='Insert frame right',state=DN[Right],command=Wow(self,'on_PopupInsertRight',PopupData))
        HandlerPopup.add_command(label='Insert frame above',state=DN[Above],command=Wow(self,'on_PopupInsertAbove',PopupData))
        HandlerPopup.add_command(label='Insert frame below',state=DN[Below],command=Wow(self,'on_PopupInsertBelow',PopupData))

        HandlerPopup.add_separator()
        HandlerPopup.add_command(label='Delete frame',command=Wow(self,'on_PopupFrameDelete',PopupData)
            ,state=DelState)
        HandlerPopup.add_separator()
        HandlerPopup.add_command(label='Help',command=self.on_PopupFrameHelp)
        HandlerPopup.tk_popup(Event.x_root,Event.y_root)

    def on_PopupInsertLeft(self,PopupData):
        """
        Insert new frame at left of current frame.
        
        We don't get this far if it isn't valid and reasonable to do so.
        """
        self.PopupInsertCommon(PopupData,'l')
        

    def on_PopupInsertRight(self,PopupData):
        """
        Insert new frame at right of current frame.
        
        We don't get this far if it isn't valid and reasonable to do so.
        """
        self.PopupInsertCommon(PopupData,'r')

    def on_PopupInsertAbove(self,PopupData):
        """
        Insert new frame above the current frame.
        
        We don't get this far if it isn't valid and reasonable to do so.
        """
        self.PopupInsertCommon(PopupData,'a')

    def on_PopupInsertBelow(self,PopupData):
        """
        Insert new frame below the current frame.
        
        We don't get this far if it isn't valid and reasonable to do so.
        """
        self.PopupInsertCommon(PopupData,'b')

    def PopupInsertCommon(self,PopupData,Side):
        """
        """
        self.FrameSanityCheck('Prior to frame insert')
        #We need BboxDict in order to remediate the frames later
        BboxDict = self.BboxDictCreate(self.FrameInfoGen())
        #Call gather to get information about current lines
        Temp = self.Gather()
        #Create an instance of LineMind to do the work for us
        LM = LineMind()
        #And tell it about all the lines
        for Line in Temp['Lines']:
            LM.LineAdd(Line)
        #Now to figure out the level of the line we are going to insert.
        #To do this we consider the bounding box of our frame, we find the level of the
        #    sides of that bounding box. The level of our new line has to be no
        #    lower then the level of the highest-level parallel side AND no lower
        #    than one plus the level of the highest-level perpindicular side.
        #    There is no vast theory behind this; the rule was derived from looking
        #    at various model cases.
        #We can't just go sticking the line into the form "as is" because there may 
        #    be other lines in the way. The business of mucking around with the "level"
        #    of lines (see LineMind for a discussion of level) lets us insert the new
        #    line at the correct position so it spans our frame but takes priority
        #    over any conflicting lines internal to our form.
        #The first order of business is to get the bounding box of our frame in
        #    generic coordinates.
        Bx1,By1 = CanvasToGeneric(PopupData['Bbox'][:2],self.CanvasSize)
        Bx2,By2 = CanvasToGeneric(PopupData['Bbox'][2:],self.CanvasSize)
        if Side in 'lr':
            #Were doing a left/right insert/
            LineA = (Bx1,By1,Bx1,By2)
            LineB = (Bx2,By1,Bx2,By2)
            LineC = (Bx1,By1,Bx2,By1)
            LineD = (Bx1,By2,Bx2,By2)
            
        else:
            #Were doing an above/below insert.
            #    top and bottom bounding box lines
            LineA = (Bx1,By1,Bx2,By1)
            LineB = (Bx1,By2,Bx2,By2)
            LineC = (Bx1,By1,Bx1,By2)
            LineD = (Bx2,By1,Bx2,By2)
        #At this point LineA/LineB are the bounding box lines parallel to our new line, while
        #    LineC/LineD are the bounding box lines perpindicular to our new line.
        LevelLineA = LM.LevelFind(LineA)
        LevelLineB = LM.LevelFind(LineB)
        LevelLineC = LM.LevelFind(LineC)
        LevelLineD = LM.LevelFind(LineD)
        if LevelLineA==None or LevelLineB==None or LevelLineC==None or LevelLineD==None:
            print 'LevelA=%s LevelB=%s LevelC=%s LevelD=%s'%(LevelLineA,LevelLineB,LevelLineC,LevelLineD)
            raise Exception, 'Level of frame bounding line not found. Info printed.'
        #                 Parallel    Paralled    Perpindicular Perpindicular
        TargetLevel = max(LevelLineA, LevelLineB, LevelLineC+1, LevelLineD+1)
        #Since were working in generic coordinates we need Bumper in generic, we also add a 
        #    fudge factor so we're not skirting the edge.
        BumperG = int(CanvasToGeneric((GuiEditor.Bumper,GuiEditor.Bumper),self.CanvasSize)[0] * 1.2)
        #Now compute the origin and direction of our line
        if Side == 'l':
            Dirn = DirnV
            X = Bx1 + BumperG
            Y = (By1 + By2) / 2
        elif Side == 'r':
            Dirn = DirnV
            X = Bx2 - BumperG
            Y = (By1 + By2) / 2
        elif Side == 'a':
            Dirn = DirnH
            X = (Bx1 + Bx2) / 2
            Y = By1 + BumperG 
        elif Side == 'b':
            Dirn = DirnH
            X = (Bx1 + Bx2) / 2
            Y = By2 - BumperG
        else:
            raise exception,"Invalid side '%s'"%Side
        #We know everything we need for our new line; add it
        if 1 <>LM.LineInsert((X,Y,Dirn),TargetLevel):
            raise Exception,"Insertion of new line failed unexpectedly"
        #Fetch revised list of lines
        Lines = LM.Gather()
        #Sort so we are in order by class
        Lines.sort()
        #Then extract just the line info to replace
        Temp['Lines'] = [X[1] for X in Lines]
        #Redraw the canvas with the new frame layout
        self.CanvasConfigure(Info=Temp)
        #And look after the new frame(s) that have appeared
        self.FramesRemediate(BboxDict,'i')
        self.FrameSanityCheck('Following frame insert')

    def on_PopupFrameProperties(self,PopupData):
        """
        Let user have at frame properties
        """
        CurrentType = PopupData['FrameWidget'].WidgetName
        if PopupData['FrameWidget'].FrameID == (0,):
            #This is the toplevel 
            FI = Repo.FetchForm()
            Info = {'Name':PopupData['FrameName'], 'Type':FI['Type'], 'BaseClass':FI['BaseClass']}
            #Ask user for their choice of name
            MainForm = Repo.ModuleName == Cfg.Info['ProjectName'] and PopupData['FrameName'] == Cfg.Info['ProjectName']
            Info = Rpw.FormDialog(self,Settings=Info,Title=' Form Properties '
                ,Prompt='Form:',FrameOnly = MainForm).Result
            if Info == None:
                #User bailed
                return    
            Modified = False    
            if Info['Type'] <> FI['Type']:
                #User changed the derive-from class
                #Tell the widreq to convert itself to the new type
                NewModule,NewType = Info['Type'].split('.')
                PopupData['FrameWidget'].Convert(NewType,NewModule) 
                FI['Type'] = Info['Type']
                Modified = True
            if FI['BaseClass'] <> Info['BaseClass']:    
                FI['BaseClass'] = Info['BaseClass']
                Modified = True
            if Modified:
                #Adjust the creation systext               
                GblLayout.CreationSystextRegen('PopupFrameProperties')    
        else:
            #It's a non-toplevel
            NewType = Rpw.FrameDialog(self
                ,Settings={'Name':PopupData['FrameName'],'Type':CurrentType}).Result
            if NewType == None:
                #User bailed
                return
            if NewType <> CurrentType:
                if NewType == 'Frame':
                    NewModule = 'Tkinter'
                elif NewType == 'ScrolledFrame':
                    NewModule = 'Pmw'
                else:
                    raise Exception, "Unknown NewType: "+NewType
                #Tell the widreq to convert itself to the new type
                PopupData['FrameWidget'].Convert(NewType,NewModule) 
                #Adjust the creation systext               
                GblLayout.CreationSystextRegen('PopupFrameProperties')    
        
    def on_PopupFrameTidy(self,PopupData):
        """
        Tidy widreqs in frame to be exactly vertical or horizontal
        """
        FrameID = PopupData['FrameID']
        Info = PopupData['Info']
        CanvasXY = PopupData['CanvasXY']
        MinX = 999999
        MinY = 999999
        MaxX = 0
        MaxY = 0
        SumX = 0
        SumY = 0
        for WidReqName in Info[0][FrameID]['WidReqs']:
            WidReq = Repo.Fetch(WidReqName)
            X,Y =WidReq.WhereCenter()
            MinX = min(X,MinX)
            MinY = min(Y,MinY)
            MaxX = max(X,MaxX)
            MaxY = max(Y,MaxY)
            SumX += X
            SumY += Y
        DeltaX = MaxX - MinX
        DeltaY = MaxY - MinY    
        Count = len(Info[0][FrameID]['WidReqs'])
        AvgX = SumX / Count
        AvgY = SumY / Count
        for WidReqName in Info[0][FrameID]['WidReqs']:
            WidReq = Repo.Fetch(WidReqName)
            X,Y =WidReq.WhereCenter()
            IsSel = self.HerdName == Repo.SelectedHerd and WidReqName == Repo.FetchSelected()
            if DeltaY > DeltaX:
                #widgets are vertical
                WidReq.PlaceOnCanvasCenter(self,[AvgX,Y],IsSel)
            else:
                #widgets are horizontal
                WidReq.PlaceOnCanvasCenter(self,[X,AvgY],IsSel)

    def on_PopupFrameDelete(self,PopupData):
        #Ask the user if it is OK to delete the frame.
        FrameID = PopupData['FrameID']
        Info = PopupData['Info']
        CanvasXY = PopupData['CanvasXY']
        assert len(Info[1]) <> 0, "Why are we trying to delete the main frame, eg the form itself?"
        self.FrameMark(FrameID,Info,Color='#c00000',Width=4)
        Msg = 'Delete frame now?'
        WidreqCount =  len(Info[0][FrameID]['WidReqs'])
        if WidreqCount:
            Msg = rpHelp.Plural('Delete frame and the %s widget{/s} it contains now?',WidreqCount)
        Response =  Rpw.MessageDialog(Message=Msg,Title='Query',Help='Frame.delete'
            ,Buttons=(('Delete',1),('~Cancel',None))).Result
        self.FrameMark(None,Info)
        if Response <> 1:
            #User declined
            return
        #User said Yes - Delete the contained widreqs
        self.FrameSanityCheck('Just before deleting frame %s'%PopupData['FrameName'])
        for WidReqName in Info[0][FrameID]['WidReqs']:
            WidReq = Repo.Fetch(WidReqName)
            HandlerList = WidReq.HandlersList()
            R = Repo.Request(self.WRID,'WidreqDelete',WidReqName)                
            if R <> 1:
                print 
                Rpw.MessageDialog(Message='Widget deletion failed unexpectedly with reason: %s from %s'%(R[0],R[1]))
            #If any handlers are now orphans, give the user the option to delete them.
            self.OrphanHandlersProcess(WidReqName,HandlerList)

        #Delete the frame widreq
        WidReq = Repo.FindFrame(FrameID)
        assert WidReq <> None, "Expected Frame WidReq not found" 
        WidReq = WidReq.Name
        R = Repo.Request(self.WRID,'WidreqDelete',WidReq)                
        if R <> 1:
            print 
            Rpw.MessageDialog(Message='Frame deletion failed unexpectedly with reason: %s from %s'%(R[0],R[1]))
        
        #Create a dictionary where the key is the name of each frame widreq and the value
        #    is the bounding box for that frame. Note that we do this *before* we actually
        #    delete the frame, so this dictionary represents the 'before the deletion' state
        #    of affairs.
        BboxDict = self.BboxDictCreate(Info)
        #Find the common line(s) this frame shares with it's sibling(s)
        List = self.SiblingsCommonLinesFind(FrameID,Info) 
        List.sort()
        #If there is more than one line, we somewhat arbitrarily delete the
        #   right or lower line.
        self.CurLine = self.LineFindExact(List[-1])
        #remember any lines that terminate against our line
        TermLines = self.TermLinesFind(self.CurLine)
        #first delete any TermLines, replacing each TermLine entry with 
        #a 3-list giving +-1 offset, dirn and position.
        for I in range(len(TermLines)):
            ID = TermLines[I]
            TermLines[I] = self.LinesPerpInfoGather(self.CurLine,ID)
            self.delete(ID)
        #delete our old actual line    
        self.delete(self.CurLine)
        #redraw the termlines. The start-point for redrawing each termline is
        #from one pixel away from curline, which side given by offset.
        for I in range(len(TermLines)):
            Offset, Pos, Dirn = TermLines[I]
            X = (CanvasXY[0]+Offset, Pos)[Dirn]
            Y = (Pos, CanvasXY[1]+Offset)[Dirn]
            self.Draw((X,Y),Dirn,GuiEditor.LineStippleStandard)
        #We have deleted the *visual* frame, but now we need to update frame widreqs since
        #    their FrameID may have changed.
        self.FramesRemediate(BboxDict,'d')
        self.FrameSanityCheck('Just after deleting a frame')
        return

    def on_PopupFrameHelp(self):
        """
        Serve help re frame popup
        """
        Help('Frame.popup')
                
    def on_Button1Down(self,Event):
        """=e
        Button-1 went down over our layout canvas
        """
        if self.CanvasSize == [1,1]:
            self.CanvasSize = self.CanvasSizeFetch()
        self.TermLines = None
        Tx = self.canvasx(Event.x)
        Ty = self.canvasy(Event.y)
        ##D('Clickon x=%s %s y=%s %s'%(Event.x,Tx,Event.y,Ty))
        Tx = Event.x
        Ty = Event.y
        CanvasX, CanvasY = self.EventXYCanvas(Event,self)
        for I in (0,20,200):
            TestX = self.canvasx(I)
            TestY = self.canvasy(I)
        #We want to know now, not when the user lets go of the mouse button, if anybody
        #    is going to object to the creation of a new widreq. The most likely cause
        #    of such an objection is an invalid option/pack entry value but regardless we
        #    want to know now. We therefore create and, if necessary, subsequently delete
        #    a 'just for checking' frame widreq. We have to pass the name of our herd
        #    since it is possible for the parking lot to be selected at this point.
        NewFrameName = NameWidReq('Frame',self.HerdName)
        Temp = WidReq('Frame',NewFrameName,None,self.HerdName,ModuleName='Tkinter')
        R = Repo.Request(self.WRID,'WidreqCreate',NewFrameName,Temp,'create or move a line')
        if R <> 1:
            #There was an objection
            #Must have temp widreq unregister with repo to free up the name
            Temp.Unregister()
            return
        #Nobody objected; delete our widreq    
        R = Repo.Request(self.WRID,'WidreqDelete',NewFrameName)
        if R <> 1:
            Repo.Tell(R)
            raise Exception, "Surprised that we were unable to delete this widreq"

        if self.State == GuiEditor.StateIdle:
            #If were over an existing line, then grab it.
            self.CurLine = self.LineFindNear(CanvasX,CanvasY)
            if self.CurLine:
                #remember any lines that terminate against our line
                self.TermLines = self.TermLinesFind(self.CurLine)
                #set appropriate state
                self.State = GuiEditor.StateLineMove
                #compute and save the constraint box for this line
                self.ConstraintBox = self.ConstraintBoxFind(self.CurLine)
                #print 'ConstraintBox=%s'%`self.ConstraintBox`
                #note the line orientation
                self.Dirn = self.LineDirn(self.CurLine)
                #render the line in our "line in motion" color
                self.itemconfigure(self.CurLine,stipple=GuiEditor.LineStippleNew)
            else:    
                #Possible start of a new line. To create a new line, which implies creating a
                #    new container-widreq, we need to be able to select our form. Since
                #    it is possible for people to decline the selection, we attempt to select 
                #    now (not after the user has drawn a line).
                #But first, note if we are being newly selected, that is, if somebody else
                #    (like the parking lot) was selected before we selected ourselves. This
                #    information is used as part of figuring out which frame to select if the
                #    user in fact just clicks rather than drawing a new line.
                self.WeAreNewlySelected = Repo.SelectedHerd <> self.HerdName
                R = Repo.Request(self.WRID,'HerdSelect',self.HerdName)
                if R <> 1:
                    #Somebody objected; cancel starting a new line
                    return
                self.StartX = CanvasX
                self.StartY = CanvasY
                #At line-drop time we need to remediate the Frame-name to FrameID correspondence
                #   and we need "before the new line" frame information to do it. Hence we call
                #   FrameInfoGen and save the result.
                self.FrameSanityCheck('On button-1 down prior to possible draw of new line')
                self.BboxDictStart = self.BboxDictCreate(self.FrameInfoGen())
                self.State = GuiEditor.StateLineStart

    def on_Button1Up(self,Event):
        """=e
        Mouse button 1 went up
        """
        if self.State == GuiEditor.StateLinePlace or self.State == GuiEditor.StateLineMove:
            #we were placing a line
            if self.CurLine <> None:
                #and we actually had a tentative line, render in the "real line" color
                self.itemconfigure(self.CurLine,stipple=GuiEditor.LineStippleStandard)
            if self.State == GuiEditor.StateLineMove:
                #We just placed a moved line. If a container widreq is selected then
                #    we redraw it's selection mark, in case the selection mark was
                #    along the line that moved. 
                #---Find the currently selected widreq---
                CSW = Repo.Fetch(Repo.FetchSelected())
                if CSW.FrameID <> None:
                    #A container widget is currently selected.
                    self.FrameMark(CSW.FrameID)
            if self.State == GuiEditor.StateLinePlace:
                #We just placed a *new* line. That means that there will be one or
                #    possibly two frames that need to have Frame widreqs generated
                #    for them. Step through all the frames and create widreqs as
                #    necessary. Note that our form was selected when the user pressed
                #    the mouse button in the first place so we don't have to worry about
                #    that now.
                self.FramesRemediate(self.BboxDictStart,'i')
                self.FrameSanityCheck('Just after creating a new line')
            #self.Modified = True    
            self.State = GuiEditor.StateIdle
            #In any case regenerate code to reflect current state
            GblLayout.CreationSystextRegen('GuiEditor - line place/move')
            
        elif self.State == GuiEditor.StateLineStart:
            #User clicked on an empty area inside a frame (ie not on a widget or line).
            #We want to select a frame. If a containee widget is currently selected or
            #    a container-widget is selected but the cursor hotspot is outside that
            #    widget then we want to select the most deeply nested frame of the clicked-on 
            #    spot. If a container-widget is currently selected and the cursor hotspot
            #    is inside that container-widget, then we want to select the next
            #    larger frame, unless the largest frame (eg the form itself) is already
            #    selected, in which case we wrap and select the most deeply nested frame.
            #    So the plot is:
            #    1) Compute the target nest depth. 
            #    2) Get FrameInfo and scan for the most deeply nested frame which:
            #       a) includes our click point, and
            #       b) does not exceed our target NestDepth
            #    3) Find the widget associated with our found frame
            #    4) Select that frame.
            #We need our herd selected
            self.State = GuiEditor.StateIdle
            #Note: It is important that our herd be selected, but that was done when the
            #    user first pressed the mouse button so we don't need to worrry about it now.
            #---Find the currently selected widreq---
            CSW = Repo.Fetch(Repo.FetchSelected())
            #---Get frame info; we will need it soon---
            FrameInfo = self.FrameInfoGen()[0]
            #---Decide on the target nest depth---
            if CSW == None or CSW.FrameID == None or self.WeAreNewlySelected:
                #No widreq is selected or the selected widreq is a containee or some other form
                #    (like the parking lot) was selected when the user clicked.
                #We want the most deeply nested frame
                TargetNestDepth = 9999
            else:
                #A container-widreq is selected. Find out if we are in it.
                Info = FrameInfo[CSW.FrameID]
                if self.PointInBB((Event.x,Event.y),Info['Bbox']) == 1:
                    #We are inside currently selected frame; we want one level up
                    TargetNestDepth = len(CSW.FrameID) - 1
                    #Unless we were already at the top
                    if TargetNestDepth == 0:
                        #We were at the top; go for the deepest frame
                        TargetNestDepth = 9999
                else:
                    #We are not inside currently selected frame; go for max depth
                    TargetNestDepth = 9999        
            #---Scan for our target frame---
            TargetFrameID = ()
            for ID,Info in FrameInfo.items():
                if len(ID) > TargetNestDepth:
                    #This frame is too deeply nested; ignore it
                    continue
                if len(ID) < len(TargetFrameID):
                    #This frame is less deeply nested than our present best candidate;
                    #    ignore it
                    continue    
                if self.PointInBB((Event.x,Event.y),Info['Bbox']) == 1:
                    #The mouse hot-spot is inside this frame; that makes it the best
                    #    candidate yet.
                    TargetFrameID = ID
            if len(TargetFrameID) == 0:
                #This can happen if the user clicks inside our toplevel but
                #    releases outside of it.
                return
            #---We have our frame; now get the corresponding widreq---    
            W = Repo.FindFrame(TargetFrameID)
            assert W <> None, 'Continer WidReq not found; ID=%s'%str(TargetFrameID)
            #---Select that widreq---
            R = Repo.Request(self.WRID,'WidreqSelect',W.Name)

    def on_MouseMotion(self,Event):
        """=e
        Mouse moved
        """
        #D('Mouse motion')
        CanvasX, CanvasY = self.EventXYCanvas(Event,self)
        if self.State == GuiEditor.StateLineStart:
            X = abs(self.StartX - CanvasX)
            Y = abs(self.StartY - CanvasY)
            if X + Y > 25:
                #mouse has moved enough to try decoding the line
                if X > Y * 3:
                    #it is a horizontal line
                    self.Dirn = 0
                elif Y > X * 3:
                    #its a vertical line
                    self.Dirn = 1
                else:
                    #it's not a line yet
                    return
                #draw the new line        
                if self.NewLineCheck(CanvasX, CanvasY, self.Dirn):    
                    self.CurLine = self.Draw((CanvasX,CanvasY),self.Dirn,GuiEditor.LineStippleNew)
                else:
                    self.CurLine = None    
                self.State = GuiEditor.StateLinePlace
        elif self.State == GuiEditor.StateLinePlace:
            #delete the old line, if it exists
            if self.CurLine:
                self.delete(self.CurLine)
            self.CurLine = None    
            #draw the new line if allowed at mouse position
            if self.NewLineCheck(CanvasX, CanvasY, self.Dirn):    
                self.CurLine = self.Draw((CanvasX,CanvasY),self.Dirn,GuiEditor.LineStippleNew)
        elif self.State == GuiEditor.StateLineMove:
            #If user has moved mouse outside the constraint box then adjust the
            #nominal mouse position to be inside the constraint box
            CanvasX = max(CanvasX, self.ConstraintBox[0])
            CanvasY = max(CanvasY, self.ConstraintBox[1])
            CanvasX = min(CanvasX, self.ConstraintBox[2])
            CanvasY = min(CanvasY, self.ConstraintBox[3])
            #first delete any TermLines, replacing each TermLine entry with 
            #a 3-list giving +-1 offset, dirn and position.
            for I in range(len(self.TermLines)):
                ID = self.TermLines[I]
                self.TermLines[I] = self.LinesPerpInfoGather(self.CurLine,ID)
                self.delete(ID)
            #delete our old actual line    
            self.delete(self.CurLine)
            #draw the new line
            self.CurLine = self.Draw((CanvasX,CanvasY),self.Dirn,GuiEditor.LineStippleNew)
            #redraw the termlines. The start-point for redrawing each termline is
            #from one pixel away from curline, which side given by offset.
            for I in range(len(self.TermLines)):
                Offset, Pos, Dirn = self.TermLines[I]
                X = (CanvasX+Offset, Pos)[Dirn]
                Y = (Pos, CanvasY+Offset)[Dirn]
                self.TermLines[I] = self.Draw((X,Y),Dirn,GuiEditor.LineStippleStandard)

    def LineEndpointsFormat(self,LineEndPoints):
        """=l
        Given line endpoints (x1,y1,x2,y2) return them as a string '(x1,y1,x2,y2)'
        """
        return '(%s,%s,%s,%s)'%LineEndPoints

    def Draw(self,Origin,Dirn,Stipple):
        """=v
        Draw a bounding line on the canvas
        
        o "Origin" is a tuple giving the (X,Y) origin of the line.
        o "Dirn" is 0 for horizontal, 1 for vertical.
        o "Stipple" is the bitmap used to draw the line.
        
        If Origin is on the canvas, then the result is the canvas ID of the drawn line.
        If Origin is off the canvas we don't draw a line and the result is None.
        
        We add two tags to the drawn line:
            o "BoundingLine"
            o "(x1,y1,x2,y2)"
        The first tag identifies this as a bounding line generated by us.
        The second tag gives us the end points of the line which is otherwise 
            hard to get; I looked but was unable to find any other way to get
            this information. Further, if you know the end points of a line 
            and want to find it's line-object on the canvas you can search
            for a tag of the form "(x1,y1,x2,y2)".
        """
        assert type(Origin[0]) == type(0) and type(Origin[1]) == type(0)
        if (Origin[0] < 0) \
        or (Origin[0] > self.CanvasSize[0]) \
        or (Origin[1] < 0) \
        or (Origin[1] > self.CanvasSize[1]):
            #were off the canvas
            return None
        #Find the limits of our line. We do this by first assuming that the new 
        # new line will extend horizontally or vertically from the initial
        # origin point all the way to the edges of the canvas. Then we look
        # for any opposite direction lines which would halt our progress before
        # reaching the edges of the canvas.
        #First assume our line will span the entire canvas
        StartPoint = 0
        EndPoint = self.CanvasSize[Dirn]
        AntiDirn = not Dirn
        #This bounding box is where the line would go if it ran edge to edge
        BB = ((0, Origin[1], self.CanvasSize[0], Origin[1]),
              (Origin[0], 0, Origin[0], self.CanvasSize[1]))[Dirn]
        #Find any canvas object that might be in our way
        HitList = apply(self.find_overlapping,BB)
        #Check each overlapping object in turn
        for ID in HitList:
            #ID indicates *anything* with which we intersect
            if GuiEditor.LineTag in self.gettags(ID):
                #ID indicates a line with which we intersect
                #P is where the intersecting line would cross our line
                P = self.LineCenter(ID)[Dirn]
                #Q is the end points of our intersecting line
                Q = self.LineEndPoints(ID)
                if Q[AntiDirn] == Origin[AntiDirn] or Q[AntiDirn+2] == Origin[AntiDirn]:
                    #An endpoint of the intersection line falls exactly on our new line,
                    #therefore the intersection line doesn't actually intersect it merely
                    #Ts into our line so it is not a constraint.
                    continue
                if P < Origin[Dirn] and P > StartPoint:
                    #Intersecting line is left/above start point and it
                    #is the most constraining line so far.
                    #print 'Start=%s End=%d P=%d - setting new Start'%(StartPoint,EndPoint,P)
                    StartPoint = P
                elif P > Origin[Dirn] and P < EndPoint:
                    #Intersecting line if right/below start point and it
                    #is the most constraining line so far.
                    #print 'Start=%s End=%d P=%d - setting new End'%(StartPoint,EndPoint,P)
                    EndPoint = P
        #We've checked constraints, draw the line               
        if Dirn == 0:
            X1 = StartPoint
            Y1 = Origin[1]
            X2 = EndPoint
            Y2 = Origin[1]
        else:        
            X1 = Origin[0]
            Y1 = StartPoint
            X2 = Origin[0]
            Y2 = EndPoint
        #TheTag = '%s (%s,%s,%s,%s)'%(GuiEditor.LineTag,X1,Y1,X2,Y2)
        TheTag = '%s %s'%(GuiEditor.LineTag, self.LineEndpointsFormat((X1,Y1,X2,Y2)))
        #D('Drawing (%s,%s) -> (%s,%s)'%(X1,Y1,X2,Y2))
        Result = self.create_line(X1,Y1,X2,Y2,tag=TheTag,stipple=Stipple)
        return Result

#-------------------------------------------------------------------------------
#
# Config Stuff
#
#-------------------------------------------------------------------------------

class ConfigParserCam(ConfigParser.ConfigParser):
    """=t
    By default ConfigParser lowers config names, which is not what we want.
    """
    def optionxform(self,Arg):
        return Arg

class ConfigReader:
    """=m
    Reads the config file and stores it in dictionary self.Info.
    
    "self.Info" consists of the following sections:
    
    o ["'Backup'"] An integer saying what to do about backups when we save a project.
        0: No backup
        1: Rename the existing file to be "whatever.bak".
        2: Rename the existing to be "whatever.rpj.nnnn" where nnnn is an integer which 
           is one higher than any similarly named file.
    
    o ["'CibDefault'"] A boolean saying if ColorizationInBackground should default
        to on or off.

    o ["'Debug'"] A boolean saying if debug mode is enabled. If true, some
        debug menus are shown and various debugging features are enabled.

    o ["'DefaultDir'"] The default directory to be used by the "new process"
        dialog. If a single asterisk ('*') is specified, the new process
        dialog uses the current working directory as the default.

    o ["'EnumeratedOptions'"] is a dictionary where the key is the name of
        the option type while the value is a list of allowed values.
    
    o ["'Font'"] A tuple or string describing the font to use for everything
        except code.
        
    o ["'HelpPath'"] The path to the help file.
    
    o ["'HelpTextSize'"] A tuple of two integers giving the size of regular help
        text and heading help text.
    
    o ["'IconDir'"] The path to the icon directory.

    o ["'LinkColor'"] The color we use when rendering links in help text. If not
        specified it defaults to #006000, a muted green color.
    
    o ["'ResizeIcon'"] The icon for the sub-frame resize knob.
    o ["'ParkingIcon'"] The icon for the parking lot.
    o ["'TrashIcon'"] The icon for the trash bin.
    o ["'DuplicatorIcon'"] The icon for the duplicator button.
    o ["'OpenIcon'"] The + icon for use with nested options.
    o ["'CloseIcon'"] The - icon for user with nested options.
    o ["'ComboIcon'"] A 2-tuple of icons (enabled/disabled) to use with with combobox
        dropdown button.

    o ["'ManglePrefix'"] This is set by the "AutoMangle" option and will be "__"
        if AutoMangle was true or "" if AutoMangle is false. It is prepended to
        names of widgets, eventhandlers etc.
    
    o ["'Metrics'"] A dictionary of metric information for various widgets
        about whose size we care. This doesn't come from the config file,
        rather we actually measure the widgets and store the information
        here for convenience.
    
    o ["'Modules'"] This is a dictionary where the key is the name of the
        module and the value is a dictionary of two elements:
        o ["'ImportType'"] Either 'Import' or 'From'.
        o ["'Widgets'"] A dictionary of widgets of this module. The key is the name 
          of the widget while the value is a dictionary of widget information thus:
    
            o ["'Hint'"] The text of the hint to use with this widgets button on
                the widget buffet.
            o ["'Icon_b'"] The icon (as a PhotoImage object) to use on this
                widgets button in the widget buffet.
            o ["'Icon_w'"] The icon (as a PhotoImage object) to use to represent a
                request for this widget on the users form.
            o ["'Master'"] Used only for container widgets (ie frames) and even then it
                is optional. If omitted then the frame widget itself is considered to be
                the master into which containee widgets are packed. For example, having
                created a Frame named MyFrame, then a button would be placed into that
                frame using "MyButton = Button(MyFrame...)". However, some frame widgets
                (eg Pmw.ScrolledFrame) are not actually derived from Frame and that's
                where the "Master" field comes in; if supplied it is appended to the 
                name of the frame to get the master when adding widgets. For example
                in the case of Pmw.ScrolledFrame "Master" is set to ".interior()" and
                having created a ScrolledFrame named MyFrame, then a button would be
                placed into that frame using "MyButton = Button(MyFrame.interior()...)".
            o ["'Tab'"] A 2-tuple giving:
                o [0] The ordinal position of this widget on it's buffet page (zero = first).
                o [1] The TabID of the widget buttet page on which this widget is 
                    to appear, as defined in section "Tabs".
            o ["'Options'"] A NestedOption object which is a dictionary-like object
                which holds option values with nesting as needed. The key is the
                name of the option while, for most cases, the value is
                4-list of:
                o Option type, which must be either a built-in or enumerated
                      option type.
                o The default value for this option. If there is no default then
                    this is None. For type 'font' this is a tuple of three strings;
                    for all other types this is a string.
                o Current value for this option, initially the same as the default value.    
                o Extra information. Most option types don't need extra information
                    and for them this value is "None". For type 'cvar' you specify
                    up to three characters (from "sif") indicating what types of
                    control variable (string/integer/float) the user gets to choose
                    from for this cvar.  
                While similar to a dictionary it is not identical. see the NestedOption
                    class in rpWidgets.py for full details.    
    o ["'NestedOptions'"] A list of string, each giving the name of an option type
        which is nested.

    o ["'PackOptions'"] A NestedOption object containing all the standard pack options.
        Since the option and pack editors are really the same class the format of options
        and pack options has to be the same, even though we never have nested pack options.
        But you could if you wanted to.

    o ["'Tabs'"] is a dictionary of tabs to appear on the widget buffet. The
        key is the tab ID (ie the name of the module t which his tab corresponds)
        while the value is a 2-tuple giving:
        o [0] An integer giving the ordinal position of this tab in the
            tabs of the widget buffer.
        o [1] A string giving the text to appear on the widget buffet tab.        
    
    o ["'Template'"] A list of three text strings and an integer giving the text to use when
        creating a new module. Note that these two strings come from the
        file "rapyd.template", not from the config file.
        o [0] Text to come before the 'import' lines.
        o [1] Text to come between the 'import' and 'init' lines.    
        o [2] Text to come after the 'init' line.
        o [3] The number of spaces to indent the generated init lines

    o ["'SchemeCurName'"] The name of the current editor scheme.
        
    o ["'Schemes'"] is a dictionary of text editor schemes. The key is the name of the
        scheme. The value is a dictionary of information for that scheme, thus:
        
        o ["Actions"] A list of 2-element tuli's:
            o ["0"] A string naming a known editor action, eg "'Outdent'".
            o ["1"] The event string to which the action is to be bound, eg "'<F9>'".
        o ["Colors"] A dictionary where each key is a color element name (from "ColorizerElements")
            and each value is a color specifier, as either a color name or a hex value.
        o ["Font"] A string giving the font to be used, eg "Courier 12 bold".
        o ["Indent"] An integer in the range 1..16 giving the indent/outdent amount.
        o ["Wrap"] An integer. Rapyd-generated code is wrapped so no line exceeds
            this number of characters.
    
    """
    #These are the option types that we handle by built-in code.
    #   The key is the name of the type,
    #   The value is a length-2 string where the first character indicates the
    #       entry area and the second character indicates the assist.
    #       Entry area codes
    #           - Display the current value in a label
    #           e Provide an Entry widget
    #       Assist area codes
    #           - Do not provide an assist button
    #           a Provide an assist button
    #
    #Note that after a bit of processing (not long below) each entry in
    #    Cfg.Info['BuiltinOptions'] consists of:
    #
    #    ['EditCodes'] The editcodes, as described just above
    #    ['Validate'] The validation routine (code in rpOptions.py)
    #    ['Assist'] The assist class (code also in rpOptions.py)
    BuiltinOptionTypes = {
        'bitmap'     : {'EditCodes':'ea'},
        'bbox'       : {'EditCodes':'ea'},
        'color'      : {'EditCodes':'ea'},
        'command'    : {'EditCodes':'-a'},
        'cursor'     : {'EditCodes':'-a'},
        'cvar'       : {'EditCodes':'-a'},
        'dim'        : {'EditCodes':'e-'},
        'float'      : {'EditCodes':'e-'},
        'font'       : {'EditCodes':'-a'},
        'image'      : {'EditCodes':'ea'},
        'int'        : {'EditCodes':'e-'}, 
        'pmwcomp'    : {'EditCodes':'--'},
        'pmwdatatype': {'EditCodes':'-a'}, 
        'pyclass'    : {'EditCodes':'e-'},
        'tabs'       : {'EditCodes':'ea'},
        'text'       : {'EditCodes':'e-'},
        'verbatim'   : {'EditCodes':'e-'},
        'xy'         : {'EditCodes':'ea'}
        }
    
    #Here we list those options which are not an option in themselves but represent a
    #    group of nested sub-options.
    NestedOptionList = ['pmwcomp']

    ColorizerElements = 'builtin other comment cursor keyword special string' \
        ' format escape background bgldt' \
        '~ % ^ & * ( ) { } [ ] - + = | ; : < > , . / !'.split()


    def __init__(self):
        """
        Create the config reader/
        """
        ConfigFilename = None
        #Look on the command line for our config file specification.
        for Arg in sys.argv:
            if Arg[:9] == '--config=':
                ConfigFilename = Arg[9:]
                break
        if not ConfigFilename:
            #If the command line didn't give us any joy check the environment
            if os.environ.has_key('RAPYDCONFIG'):
                ConfigFilename = os.environ['RAPYDCONFIG']
        if not ConfigFilename:
            #If neither of the above gave us anything default to CWD
            ConfigFilename = 'rapyd.config'        
        ##D('ConfigFilename=%s'%ConfigFilename)
        self.Info = {}
        #Create information repository on built-in options
        self.Info['BuiltinOptions'] = ConfigReader.BuiltinOptionTypes
        self.Info['NestedOptions'] = ConfigReader.NestedOptionList
        for Temp in ConfigReader.BuiltinOptionTypes.keys():
            self.Info['BuiltinOptions'][Temp]['Validate'] = eval('Rpo.%s_Validate'%Temp)
            self.Info['BuiltinOptions'][Temp]['Assist']   = eval('Rpo.%s_Assist'%Temp)


        self.ErrorCount = 0
        self.C = ConfigParserCam()
        try:
            F = open(ConfigFilename)
        except IOError:
            print 'Unable to open config file "%s"'%ConfigFilename
            self.ErrorCount += 1
            return
        self.C.readfp(F)
        F.close()
    
        SectionList = self.C.sections()
        self.MissingSections = []
        #
        # Section: General
        #
        Name = 'General'
        if not self.C.has_section(Name):
            self.Error('Section "%s" not found'%Name)
        else:
            #The color for help links
            self.Info['LinkColor'] = '#006000'
            LinkColor = self.Fetch('General','LinkColor')
            if LinkColor:
                R = Rpo.color_Validate(LinkColor,'')
                if R[0] <> 1:
                    #We don't like their color specification
                    self.Error('Option "LinkColor": %s'%R[0])
                else:    
                    self.Info['LinkColor'] = LinkColor
            #The backup setting
            Backup = self.Fetch('General','Backup')
            if Backup == None:
                #Default to simple backup if nothing specified
                Backup = 1
            try:
                Backup = int(Backup)
            except ValueError:
                self.Error('"Backup" specification not 0, 1 or 2')
            self.Info['Backup'] = Backup    
            #The icon directory    
            IconDir = self.Fetch('General','IconDir')
            if IconDir == '*':
                #User wants to look for Icon directory in same directory as config file
                Path = os.path.split(ConfigFilename)[0]
                if Path == '':
                    IconDir = 'Icons'
                else:    
                    IconDir = Path + '/Icons'
            #Path to the help file.
            HelpPath = self.Fetch('General','HelpPath')
            if HelpPath == '*':        
                #User wants to look for help in same directory as config file
                Path = os.path.split(ConfigFilename)[0]
                if Path == '':
                    HelpPath = 'rapyd.help'
                else:    
                    HelpPath = Path + '/rapyd.help'
            if not os.path.isfile(HelpPath):
                self.Error('Help file "%s" not found'%HelpPath)        
            #Help text size
            Temp = self.Fetch('General','HelpTextSize')
            self.Info['HelpTextSize'] = (-12, -14)
            try:
                T = eval(Temp)
                if type(T) <> type(()) or len(T) <> 2 or type(T[0]) <> type(0) or type(T[1]) <> type(0):
                    raise Exception
                self.Info['HelpTextSize'] = T
            except:
                self.Error('Section "General", "HelpTextSize" specification "%s" is not valid'%Temp)
            #The default "new project" directory
            self.Info['DefaultDir'] = self.Fetch('General','DefaultDir')
            self.Info['IconDir'] = IconDir
            self.Info['HelpPath'] = HelpPath
            #make sure directory name ends in a slash
            if self.Info['IconDir'][-1] <> '/':
                self.Info['IconDir'] += '/'
            # The AutoMangle option
            Temp = self.Fetch('General','AutoMangle')
            self.Info['ManglePrefix'] = ''
            try:
                if eval(Temp):
                    self.Info['ManglePrefix'] = '__'
            except:
                pass        
            # The widgetator assistant icon
            self.Info['AssistIcon'] = self.FetchIcon('pr-msc-assist.ppm')    
            # The resize icon    
            self.Info['ResizeIcon'] = self.FetchIcon('pr-msc-resize.ppm')
            # The parking lot icon
            self.Info['ParkingIcon'] = self.FetchIcon('pr-parking.ppm')
            # The trash bin icon
            self.Info['TrashIcon'] = self.FetchIcon('pr-trash.ppm')
            # The duplicator bin icon
            self.Info['DuplicatorIcon'] = self.FetchIcon('pr-duplicator.ppm')
            # The open and close icons
            self.Info['OpenIcon'] = self.FetchIcon('pr-msc-open.ppm')
            self.Info['CloseIcon'] = self.FetchIcon('pr-msc-close.ppm')
            #The four arrow icons for the sliding button bar
            T = []
            T.append(self.FetchIcon('pr-sbb-left-norm.ppm'))
            T.append(self.FetchIcon('pr-sbb-left-gray.ppm'))
            T.append(self.FetchIcon('pr-sbb-rite-norm.ppm'))
            T.append(self.FetchIcon('pr-sbb-rite-gray.ppm'))
            self.Info['SbbIcons'] = T
            SectionList.remove(Name)
            # The down and up triangles for combo box use
            self.Info['ComboIcon'] = (self.FetchIcon('pr-msc-tri-down.ppm'),self.FetchIcon('pr-msc-tri-down-dis.ppm'))
            # The font to use
            FontString = self.Fetch('General','Font')
            Font = Rpw.Fontificate(FontString)
            R = Rpo.font_Validate(Font,'')
            if R[0] <> 1:
                self.Error('Section "General" font specification "%s" is not valid.'%FontString)
            """
            F = eval(Font)
            if len(F) <> 3:
                self.Error('Font specification "%s" not a 3-tuple'%Font)
            Temp = tkFont.Font(family=F[0], size=F[1], weight=F[2])
            #Root.option_add('*font', Temp)
            """
            Root.option_add('*font', Font)
            self.Info['Font'] = Font
            # The default code editor scheme. We check for validity after the
            #     various editor schemes have been processed
            self.Info['SchemeCurName'] = self.Fetch('General','DefaultEditorScheme')
        #
        # Section: Modules
        #
        Name = "Modules"
        ModuleDir = {}
        if not self.C.has_section(Name):
            self.Error('Section "%s" not found'%Name)
        else:    
            Modules = self.C.options(Name)
            if len(Modules) == 0:
                self.Error('Section "%s" contained no definitions'%Name)
            for Module in Modules:
                Type = self.Fetch(Name,Module).lower()
                if not Type in ('from','import'):
                    self.Error('Section Modules: module name "%s" not followed by From or Import'%Module)
                else:
                    ModuleDir[Module] = {'ImportType':Type, 'Widgets':{}}
            SectionList.remove(Name)
        self.Info['Modules'] = ModuleDir            
        if not self.Info['Modules'].has_key('Tkinter'):
            M = ("Rapyd is a program all about Tkinter but no module"
                " named 'Tkinter' was defined. We really must insist")
            self.Error(M)    
        #
        # Section: Tabs
        #
        Name = 'Tabs'
        TabDir = {}
        #We accumulate the order specifiers here but we process them after all the 
        #    widgets have been handled. OrderSpecifiers is a dictionary where the
        #    key is the TabID (ie the name of the module which corresponds to this
        #    tab) and the value is a string of widget names, in the
        #    order they are to appear in this tab in the widget buffet.
        OrderSpecifiers = {}
        if not self.C.has_section(Name):
            self.Error('Section "%s" not found'%Name)
        else:    
            Tabs = self.C.options(Name)
            if len(Tabs) == 0:
                self.Error('Section "%s" contained no definitions'%Name)
            for Tab in Tabs:
                if Tab == 'Order':
                    #This tells us the order in which to place the tabs in
                    #    the widget buffet. Save it
                    TabOrder = self.Fetch(Name,Tab).split()
                elif Tab[:6] == 'Order_':
                    #This is an order-specifier for a particular tab.    
                    OrderSpecifiers[Tab[6:]] = self.Fetch(Name,Tab)
                else:    
                    #An actual tab specification.
                    Text = self.Fetch(Name,Tab)
                    if len(Text) == 0:
                        self.Error('Tab "%s"; text for buffet tab is empty'%Page)
                    else:
                        TabDir[Tab] = Text
            #Look after ordering the tabs
            if len(TabOrder) <> len(TabDir):
                Msg = '%s tabs are defined but "Order" lists %s items. Each tab should be listed ' \
                    'exactly once in Order'%(len(TabDir), len(TabOrder))
                self.Error(Msg)
            else:
                #Put the appropriate indicies on each tab entry
                J = 0
                for K in TabOrder:
                    try:
                        TabDir[K] = (J,TabDir[K])
                        J += 1
                    except KeyError:
                        Msg = 'Section Tab: Order makes reference to a tab named "%s" but no ' \
                            'such tab was defined'%K
                        self.Error(Msg)    
            SectionList.remove(Name)
        self.Info['Tabs'] = TabDir            
        #
        # Section: EnumeratedOptionTypes
        #
        Name = 'EnumeratedOptionTypes'
        EOptionDict = {}    
        if not self.C.has_section(Name):
            #the entire section is missing
            self.Error('Section "%s" not found'%Name)
        else:    
            #the section exists
            EOptions = self.C.options(Name)    
            if len(EOptions) == 0:
                #but nothing is defined in it
                self.Error('Section "%s" contained no definitions'%Name)
            for EOption in EOptions:
                #List is all the options split by whitespace
                List = self.Fetch(Name,EOption).split(',')
                if len(List) < 2:
                    #you have to have at least two choices
                    self.Error('EnumeratedOption "%s" contains less than two choices'%EOption)
                else:
                    if EOption in ConfigReader.BuiltinOptionTypes.keys():
                        self.Error('EnumeratedOption "%s" duplicates a built-in option type'%EOption)
                    else:   
                        #Choices are specified as A:B where A is the part the user sees and gets to
                        #    choose from while B is what is actually coded for the choice. Note that
                        #    the B part can be either numeric or string; that means if it is string 
                        #    you have to quote it. In the (reasonably common) case where B is a string
                        #    which is identical to A then you can simply code A.
                        #
                        #Some examples:
                        #    True:1 False:0
                        #        Here the user gets to choose from the text True or False but what gets
                        #            coded are the NUMBERS one and zero.
                        #
                        #    normal disabled
                        #        This is a short form for:  normal:"normal" disabled:"disabled"
                        #   
                        #We store the choices in a dictionary where A is the key and B is the value.
                        Temp = {}
                        for Choice in List:
                            #Changing tildes to spaces lets us put spaces inside enumerated options
                            Choice = Choice.strip()
                            Choice = Choice.split(':')
                            if not len(Choice) in [1,2]:
                                self.Error('EnumeratedOption "%s", choice "%s" is invalid'%(EOption,Choice))
                            if len(Choice) == 1:
                                Choice.append('"%s"'%Choice[0])
                            try:
                                #convert string number to number or quoted string to string
                                Choice[1] = eval(Choice[1])    
                            except:
                                #the conversion barfed    
                                self.Error('EnumeratedOption "%s", choice "%s" is invalid'%(EOption,Choice))
                            Temp[Choice[0]] = Choice[1]    
                        EOptionDict[EOption] = Temp
            SectionList.remove(Name)
        self.Info['EnumeratedOptions'] = EOptionDict            
        #
        #TextEditor scheme
        #
        self.Info['Schemes'] = {}
        for J in range(len(SectionList)-1,-1,-1):
            #Scan SectionList last-to-first
            Section = SectionList[J]
            T = Section.split()
            if len(T) == 2 and T[0] == 'EditorScheme':
                #We have an editor scheme
                SchemeName = T[-1]
                Scheme = {'Colors':{}}
                #Default color chart has white everything on a black background
                for Element in ConfigReader.ColorizerElements:
                    Scheme['Colors'][Element] = '#FFFFFF'
                Scheme['Colors']['background'] = '#000000'    
                #Action binding list defaults to empty
                Scheme['Actions'] = []    
                #Default indent
                Scheme['Indent'] = 4
                #Default wrap
                Scheme['Wrap'] = 80
                #Default font
                Scheme['Font'] = 'Courier 12'
                SectionList.pop(J)
                Options = self.C.options(Section)
                #D('Options=%s'%Options)
                for Option in Options:
                    if Option[:6] == 'Color_':
                        #
                        # Color specification
                        #
                        Color = Option[6:]
                        #Use the option editor color validater
                        Temp = Rpo.color_Validate(Color,None)
                        if Temp[0] <> 1:
                            #Color didn't fly
                            Msg = 'Section "%s", option "%s", %s'%(Section,Option,Temp[0])
                            self.Error(Msg)
                            continue
                        #We have a valid color    
                        Color = Temp[1]
                        Elements = self.Fetch(Section,Option).split()
                        #D('Elements=%s'%str(Elements))
                        #Process each specified element
                        for Element in Elements:
                            try:
                                Scheme['Colors'][Element] = Color
                            except KeyError:
                                #they specified a non-element
                                Msg = 'Section "%s", opition "%s", "%s" is not a valid element name'%(Section
                                    ,Option,Element)    
                                self.Error(Msg)
                                continue
                    elif Option[:7] == 'Action_':
                        #
                        # Action specification
                        #
                        Action = Option[7:]
                        if not Action in MenuAids.BindableActions:
                            Msg = 'Section "%s", option "%s", "%s" is not a valid bindable action'%(Section,Option,Action)
                            self.Error(Msg)
                            continue        
                        EventString = self.Fetch(Section,Option)
                        try:
                            B = Button()
                            B.bind(EventString,self.DummyHandler)
                        except TclError:
                            Msg = 'Section "%s", option "%s": "%s" is not an acceptable event description string' \
                                %(Section,Option,EventString)
                            self.Error(Msg)
                            continue    
                        Scheme['Actions'].append((Action,EventString),)                        
                    elif Option == 'Font':
                        Font = self.Fetch(Section,Option)                
                        Temp = Rpo.font_Validate(Font,None)
                        if Temp[0] <> 1:
                            #Font didn't fly
                            Msg = 'Section "%s", option "%s", %s'%(Section,Option,Temp[0])
                            self.Error(Msg)
                            continue
                        #We have a valid Font
                        Scheme['Font'] = Rpw.Fontificate(Font)    
                    elif Option == 'Indent':
                        Indent = self.Fetch(Section,Option)
                        try:
                            IndentInt = int(Indent)
                            if IndentInt < 1 or IndentInt > 16:
                                raise ValueError
                        except ValueError:
                            Msg = 'Section "%s", option "%s": "%s" is not an acceptable value'%(Section,Option,Indent)
                            self.Error(Msg)
                            continue
                        Scheme['Indent'] = IndentInt    
                    elif Option == 'Wrap':
                        Indent = self.Fetch(Section,Option)
                        try:
                            IndentInt = int(Indent)
                            if IndentInt < 40:
                                raise ValueError
                        except ValueError:
                            Msg = 'Section "%s", option "%s": "%s" is not an acceptable value'%(Section,Option,Indent)
                            self.Error(Msg)
                            continue
                        Scheme['Wrap'] = IndentInt    
                    else:
                        Msg = 'Section %s, unrecognized option: "%s"'%(Section,Option)
                        self.Error(Msg)
                        continue    
                #We have a valid scheme
                self.Info['Schemes'][SchemeName] = Scheme #the multi-scheme version
        if not self.Info['SchemeCurName'] in self.Info['Schemes'].keys():
            Msg = 'Section "general", option "DefaultEditorScheme": no editor scheme ' \
                'named "%s" was defined'%self.Info['SchemeCurName']
            self.Error(Msg)    
        #
        # Widgets
        #
        
        #We do widgets last. Having processed (and removed from SectionList) all other valid
        #    sections all we should have left is widgets.
        
        WidgetDict = {}
        #This is used to accumulate a list of non-standard defaults for nested widgets. Once the
        #    NestedOption objects are built we update the defaults per the list. Each entry is a list:
        #    [0] The name of the module eg Pmw
        #    [1] The name of the widget eg Group
        #    [2] The name of the option eg ring.relief
        #    [3] The new default value eg groove
        NonStandardDefaults = []
        while len(SectionList) > 0:
            #Scan a single widget specification
            S = SectionList[0]
            SectionList.pop(0)
            T = S.split()
            if len(T) <> 3 or T[0] <> 'widget':
                self.Error('Invalid section name: "%s"'%S)
                continue
            Name = T[2]
            OurModule = T[1]
            Widget = {}

            #Widget['Emit'] = self.Fetch(S,')Emit')
            Widget['Module'] = OurModule
            #Make sure the specified module exists
            if not self.Info['Modules'].has_key(OurModule):
                M = ('Widget %s claims to live in module %s but no module of that name'
                    ' was defined')%(Name,OurModule)
                self.Error(M)
                continue
            #Make sure no widget of this name exists in that module
            ##D(Name,OurModule,self.Info['Modules'][OurModule]['Widgets'].keys())
            if self.Info['Modules'][OurModule]['Widgets'].has_key(Name):
                M = 'Duplicate definition of widget %s in module %s'%(Name,OurModule)
                self.Error(M)
                continue
            Widget['Master'] = ''    
            if self.C.has_option(S,')Master'):
                Widget['Master'] = self.Fetch(S,')Master')    
            Widget['Hint'] = self.Fetch(S,')Hint')
            Widget['Icon_b'] = self.FetchIcon(S,')Icon_b') 
            Widget['Icon_w'] = self.FetchIcon(S,')Icon_w')
            Widget['ProtoOptions'] = {}
            Widget['Tab'] = None #this gets set later
            Options = self.C.options(S)
            
            for Option in Options:
                if Option[0] == ')':        
                    #ignore special options already processed
                    continue
                T = self.C.get(S,Option)
                if Option[0] == '.':
                    #Option that starts with a dot is a non-standard default for a nested option.
                    #    Save info for later processing.
                    if T == 'None':
                        T = None
                    #try to convert numbers to numbers
                    T = Intify(T)
                    NonStandardDefaults.append([OurModule,Name,Option[1:],T])
                    #D('%s %s'%(Option,T))
                    continue
                TT = T.split()
                #At this point 
                #    TT[0] is the option type and
                #    TT[1:] is everything else
                if len(TT) < 2:
                    Msg = 'Widget "%s", option "%s". Expected "<type> <default>":, found "%s" '  \
                        %(Name,Option,' '.join(TT))
                    self.Error(Msg)    
                    continue
                if TT[0] == 'font':    
                    try:
                        FontInfo = eval(' '.join(TT[1:]))
                        if FontInfo <> None:
                            if len(FontInfo) < 2:
                                raise 'FontError'
                            for F in FontInfo:
                                if type(F) <> type(''):
                                    raise 'FontError'
                            int(FontInfo[1])
                            FontInfo = list(FontInfo)
                            if len(FontInfo) == 2:
                                FontInfo.append('')
                        #print 'FontInfo*<%s>'%str(FontInfo)
                    except:
                        Msg = 'Widget "%s", option "%s", value "%s" ' \
                        "Bad font specifier. Expected a 2-or-3-tuple of ('Family', 'Size'[, 'Modifiers'])" \
                        %(Name,Option,' '.join(TT))
                        self.Error(Msg)    
                        continue
                    TT = [TT[0], FontInfo, None] 
                elif TT[0] in ('cvar','pmwcomp'):    
                    #we need extra info for certain types
                    if len(TT) <> 3:
                        Msg = 'Widget "%s", option "%s", value "%s" does not consist of exactly three items' \
                        %(Name,Option,' '.join(TT))
                        self.Error(Msg)
                        continue
                elif TT[0] in ('labelpos','boolean_c'):
                    #We accept any number of args for labelpos        
                    if len(TT) >= 3:
                        TT[2] = ','.join(TT[2:])
                        del TT[3:]
                else:
                    if len(TT) <> 2:
                        Msg = 'Widget "%s", option "%s", value "%s" does not consist of exactly two items' \
                        %(Name,Option,' '.join(TT))
                        self.Error(Msg)
                        continue
                    TT.append(None) #these types have no 'additional info'    
                if Widget['ProtoOptions'].has_key(Option):
                    Msg = 'Widget "%s", option "%s" is defined twice'%(Name,Option)
                    continue
                #String None becomes real None    
                if TT[1] == 'None':
                    TT[1] = None
                #try to convert numbers to numbers
                TT[1] = Intify(TT[1])
                if self.Info['BuiltinOptions'].has_key(TT[0]):
                    #Built-in option type. Run the default value through the corresponding 
                    #    validater to make sure it is acceptable. Since the validaters 
                    #    expect a string argument, we convert None to '' before validating.
                    ValidationArg = TT[1]
                    if ValidationArg == None:
                        ValidationArg = ''
                    #print 'ValidationArg=<%s>'%str(ValidationArg),type(ValidationArg)    
                    R = self.Info['BuiltinOptions'][TT[0]]['Validate'](ValidationArg,Option)
                    R = (1,1)
                    if R[0] <> 1:
                        #we didn't like the default value
                        Msg = 'Widget "%s", option "%s", type "%s", default value "%s" problem: %s' \
                            %(Name,Option,TT[0],TT[1],R[0])
                        self.Error(Msg)
                        continue
                elif self.Info['EnumeratedOptions'].has_key(TT[0]):
                    #Enumerated type. Make sure the default value is one of the specified end-values.
                    Enu = self.Info['EnumeratedOptions'][TT[0]]
                    if not TT[1] in Enu.values():
                        Msg = 'Widget "%s", option "%s", type "%s", default value "%s" is not a ' \
                            'legal end-value for this enumerated type'%(Name,Option,TT[0],TT[1])
                        self.Error(Msg)
                        continue    
                else:
                    Msg = 'Widget "%s", option "%s": "%s" is not a built-in nor an enumerated option type' \
                        %(Name,Option,TT[0])
                    self.Error(Msg)
                    continue    
                Widget['ProtoOptions'][Option] = TT  
            #Check this widget to make sure any labelpos/boolean_c option's extra information references
            #    an actual option in this widget. At this point Extra is a simple string. Since
            #    the user can specify a comma separated list of controlled widget we convert to
            #    a tuple of strings.
            for OptionName,OptionInfo in Widget['ProtoOptions'].items():
                Type,Default,ExtraTuple = OptionInfo
                if Type in ('labelpos','boolean_c'):
                    OptionInfo[2] = tuple(OptionInfo[2].split(','))
                    for Extra in OptionInfo[2]:
                        if not Extra in Widget['ProtoOptions'].keys():
                            Msg = 'Widget "%s", option "%s", type "%s", 4th field "%s" is not the ' \
                                'name of an option in this widget'%(Name,OptionName,Type,Extra)
                            self.Error(Msg)
                            continue
                            if Widget['ProtoOptions'][Extra][0] <> 'pmwcomp':
                                Msg = 'Widget "%s", option "%s", type "%s", 4th field "%s" refers to an option ' \
                                    'whose type is not "pmwcomp"'%(Name,OptionName,Type,Extra)
                                self.Error(Msg)
                        
            self.Info['Modules'][OurModule]['Widgets'][Name] = Widget
        del self.C
        if self.ErrorCount <> 0:
            #Further processing is dependent on things going well up to now. Bail out
            #    if we aready have errors.
            return
        #
        # Nested options
        #
        """
        At this point each widget has a "ProtoOptions" attribute which is a simple dictionary where the key is
            the name of the option and the value is a list of [Type,Default,Extra]. We want to turn these
            dictionaries in full blown NestedOption objects complete with nested options as specifed by
            the simple dictionaries which will become the widgets "Options" attribute. 
            
            Our first step is to scan all widgets to make sure the targets specified by nesting types
            actually exist; if any don't exist there is little point continuing.
            
            Step two is to call OptionRealize against all the simple dictionaries. This recursive function
            builds the proper NestedOption object and returns it as the result and that is what gets
            installed in the widget as the the "Options" attribute.
            
            Step three is to delete the "ProtoOptions" attributes which are no longer needed.
        """
        
        Rpw.NestedOption.SpecialTypes = ConfigReader.NestedOptionList
        for ModuleName,ModuleData in self.Info['Modules'].items():
            #Scan all import modules
            for WidgetName,WidgetData in ModuleData['Widgets'].items():
                #Scan all widgets
                for OptionName,OptionData in WidgetData['ProtoOptions'].items():
                    #Scan all options
                    Type,Default,Extra = OptionData
                    if Type in ConfigReader.NestedOptionList:
                        #This is a nested option type; verify that we like it
                        Temp = Default.split('.')
                        if len(Temp) <> 2:
                            Msg = ('Module "%s", widget "%s", option "%s": expecting default of the form "module.widget";'
                                ' got "%s"'%(ModuleName,WidgetName,OptionName,Default))
                            self.Error(Msg)    
                            continue
                        if not self.Info['Modules'].has_key(Temp[0]):
                            Msg = ('Module "%s", widget "%s", option "%s": this nest-option references a module "%s"'
                                ' which does not exist'%(ModuleName,WidgetName,OptionName,Temp[0]))
                            self.Error(Msg)    
                            continue
                        if not self.Info['Modules'][Temp[0]]['Widgets'].has_key(Temp[1]):
                            Msg = ('Module "%s", widget "%s", option "%s": this nest-option references "%s"'
                                ' which does not exist'%(ModuleName,WidgetName,OptionName,Default))
                            self.Error(Msg)    
                            continue
                        try:
                            Extra = int(Extra)
                        except:
                            pass
                        if type(Extra) <> type(0) or not Extra in(0,1,-1):            
                            Msg = ('Module "%s", widget "%s", option "%s": expecting 0, 1 or -1 value for Extra;'
                                ' got "%s"'%(ModuleName,WidgetName,OptionName,Extra))
                            self.Error(Msg)    
                            continue
        if self.ErrorCount <> 0:
            return
        #Having arrived this far we know that we liked all the nest options. Time for step two.

        #The option cross reference works agains the ProtoOption dictionaries so
        #   we look after it now while they still exist.                
        if '--poc' in sys.argv:
            print 'Option -poc (PrintOptionCrossreference) specified'
            print
            self.PrintOptionXref()
        
        #Step two
        for ModuleName,ModuleData in self.Info['Modules'].items():
            #Scan all import modules
            for WidgetName,WidgetData in ModuleData['Widgets'].items():
                #Scan all widgets
                Temp = self.OptionsRealize(WidgetData['ProtoOptions'])
                #D('\n%s.%s----------------------------'%(ModuleName,WidgetName))
                #D(str(Temp))        
                WidgetData['Options'] = Temp

        #Now to expunge all the ProtoOption dictionaries.        
        for ModuleName,ModuleData in self.Info['Modules'].items():
            #Scan all import modules
            for WidgetName,WidgetData in ModuleData['Widgets'].items():
                del WidgetData['ProtoOptions']
        #Time to look after non-standard defaults.
        for Module,Widget,Option,NewDefault in NonStandardDefaults:
            Options = self.Info['Modules'][Module]['Widgets'][Widget]['Options']
            Options.SetDefault(Option,NewDefault)
            Options.SetCurrent(Option,NewDefault)
                    
        #
        # Pack options.
        #
        """
        Here we build a NestedOption object with the standard pack options. When a widreq
            is created it makes a copy of this to hold it's pack options.
        """        
        T = Rpw.NestedOption()
        T['anchor'] = ['anchor','center','center','']
        T['expand'] = ['yesno','no','no','']
        T['fill'] = ['fill',None,None,'']
        T['ipadx'] = ['dim',0,0,'']
        T['ipady'] = ['dim',0,0,'']
        T['padx'] = ['dim',0,0,'']
        T['pady'] = ['dim',0,0,'']
        self.Info['PackOptions'] = T            

        #Some options can specify a clump of options which the user can open and close
        #    as a group. Here we scan for and resolve such macro options. We do this after
        #    all widgets are defined because they may refer to widgets which were not defined
        #    at the time.
        
        #
        # Order specifiers
        #
        #Now process the OrderSpecifiers dictionary which we developed back in the "Tabs".
        #    section. We had to wait till all the widgets had been processed before we
        #    could process OrderSpecifiers.
        for Tab in OrderSpecifiers.keys():
            #Tab steps through every tab for which an order was specified
            if not self.Info['Tabs'].has_key(Tab):
                #The tab specified doesn't exist
                Msg = 'Section Tabs, item "Order_%s": there is no tab named "%s"'%(Tab,Tab)
                self.Error(Msg)
            else:
                #the tab exists
                J = 0
                for Widget in OrderSpecifiers[Tab].split():
                    #Widget steps through every widget mentioned as being in Tab
                    if not self.Info['Modules'][Tab]['Widgets'].has_key(Widget):
                        #There is no such widget
                        Msg = 'Section "Tabs", item "Order_%s" references a widget named "%s" '\
                            'but no such widget was defined'%(Tab,Widget)
                        self.Error(Msg)
                    
                    else:
                        #the widget exists; create it's tab entry
                        self.Info['Modules'][Tab]['Widgets'][Widget]['Tab'] = (J,Tab)
                        J += 1
            #Make sure all widgets got put on a tab
            for WidgetName in self.Info['Modules'][Tab]['Widgets'].keys():
                Widget = self.Info['Modules'][Tab]['Widgets'][WidgetName]
                if Widget['Icon_b'] == None and Widget['Icon_w'] == None:
                    #This widget has no icons so it should not be on a tab
                    if Widget['Tab'] <> None:
                        M = ('Widget %s of module %s was defined without icons which suggests it is '
                            'a container widget like "Frame". However it was placed on a widgetator '
                            'tab which is incorrect')%(WidgetName,Tab)
                        self.Error(M)    
                else:
                    #This widget has icons so it should be on a tab    
                    if Widget['Tab'] == None:
                        M = 'Widget %s of module %s is defined but was not placed on the tab'%(WidgetName,Tab)
                        self.Error(M)

        #
        # Section: metrics
        #
        # Compute some widget metrics which are otherwise hard to come by.
        self.Info['Metrics'] = {}
        self.Info['Metrics']['ScrollBarWidth'] = self.MeasureWidget("Scrollbar()")[0]        
        self.Info['Metrics']['Label'] = self.MeasureCharacterWidget('Label')        
        self.Info['Metrics']['Entry'] = self.MeasureCharacterWidget('Entry')        
        #
        # Template
        #
        # Read the file "rapyd.template" and break it up into three sections, one which comes before the import lines, 
        #    one which comes between the import and init lines and one which comes after the init lines. The file is
        #     obliged to contain a line containing "=import" and another containing "=init" indicating the divisions.
        #User wants to look for Icon directory in same directory as config file
        Path = os.path.split(ConfigFilename)[0]
        if Path == '':
            TemplateFile = 'rapyd.template'
        else:    
            TemplateFile = Path + '/rapyd.template'
        
        try:
            F = open(TemplateFile)
            Temp = F.readlines()
            F.close()
        except:
            self.Error('Unable to read new-module template file "rapyd.template"')
        Template = [[],[],[],0]
        State = 'pre'
        for Line in Temp:
            if Line.strip()[:1] == '$':
                #Ignore lines that open with dollar sign
                continue
            if State == 'pre':
                if Line.find('=import') <> -1:
                    State = 'mid'
                else:
                    Template[0].append(Line)
            elif State == 'mid':
                T = Line.find('=init') 
                if T <> -1:
                    State = 'end'
                    Template[3] = T
                    if Line[0] == '/':
                        #Account for the slash that will vanish before the line is used.
                        Template[3] -= 1
                else:
                    Template[1].append(Line)
            else:
                Template[2].append(Line)
        if State == 'pre':
            self.Error('No line containing "=import" was found in the new-module ' \
                'template file "rapyd.template"')
        elif State == 'mid':
            self.Error('No line containing "=init" was found in the new-module ' \
                'template file "rapyd.template"')
        for J in range(3):
            Template[J] = ''.join(Template[J])        
        self.Info['Template'] = Template        
        #
        # Options
        #
        self.Info['Debug'] = False 
        if '--debug' in sys.argv:
            self.Info['Debug'] = not self.Info['Debug']
        
        if '--pot' in sys.argv:
            print 'Option -pot (PrintOptionTypes) specified'
            print
            self.PrintOptionTypes()
        if '--pca' in sys.argv:    
            print 'Option -pca (PrintConfiguration All) specified'
            print
            self.Print(self.Info)
        if '--pcb' in sys.argv:
            print 'Option -pcb (PrintConfiguration Brief) specified'
            print
            self.Print(self.Info,OmitWidgets=1)
            
    def OptionsRealize(self,SimpleOptionDict):
        """
        Given a "ProtoOptions" dictionary return a full NestedOption object.
        
        Note that the current value is set to the default value here.
        """
        Result = Rpw.NestedOption()
        for Key,Data in SimpleOptionDict.items():
            Type,Default,Extra = Data
            if Type in ConfigReader.NestedOptionList:
                #This is a nested type; we call ourself recursivly to generated the nested stuff
                Module,Widget = Default.split('.')
                ProtoDict = self.Info['Modules'][Module]['Widgets'][Widget]['ProtoOptions']
                Nested = self.OptionsRealize(ProtoDict)
                Result[Key] = [Type,Default,Nested,int(Extra)]
            else:
                #Non-nested type; 
                Result[Key] = [Type,Default,Default,Extra]
        return Result        

    def DummyHandler(self,Event):
        """
        Used when verifying event strings.
        """
        return

    def MeasureCharacterWidget(self,Widget,WidthCommand='width',FontCommand='font',ExtraCommands=''):
        """
        Develop some metrics about a character widthed widget.
        
        Some widgets are measured in characters. That's nice until you want to
            create one that is so many pixels long; then you are rather in the
            dark. Given a Widget which has a width option which works in
            characters (eg "Label") this routine takes some measures and returns 
            a three element tuple:
            o [0] The width of a widget containing zero characters.
            o [1] The additional number of pixels you get per additional 
                character of width.
            o [2] The height of the widget in pixels.    
        
        *Note* The standard Tkinter widgets use the standard 'width=' initialization
            option, however we make it an optional argument because some widgets,
            eg Pmw OptionMenu, need a different incantation to set the width.    
            Likewise for font.
            
        "ExtraCommands", if given, must start with a comma since they are injected into
            a running list of initiation commands.            
        """
        #TheFont = '%s=("Helvetica","-12","bold")'%FontCommand
        TheFont = '%s=%s'%(FontCommand,`self.Info['Font']`)
        #print 'TheFont=%s'%TheFont
        A = self.MeasureWidget('%s(%s=1,%s%s)'%(Widget,WidthCommand,TheFont,ExtraCommands))
        B = self.MeasureWidget('%s(%s=2,%s%s)'%(Widget,WidthCommand,TheFont,ExtraCommands))
        #print 'A=%s B=%s'%(`A`,`B`)
        return (A[0]-(B[0]-A[0]), B[0]-A[0], A[1])

    def MeasureWidget(self,Widget):
        """
        Measure the size of a widget.
        
        This measures the size of a widget by putting it on a little temporary
            canvas and then checking to see what size it is.
        """
        C = Canvas(Root,width=200,height=200)
        T = eval(Widget)
        #print 'T=%s'%`T`
        ID = C.create_window(10,10,window=T)
        T.update_idletasks()
        Bbox = C.bbox(ID)
        C.delete(ID)
        del C
        Size = BBToSize(Bbox)
        return Size

    def Print(self,Info,OmitWidgets=0):
        """
        Print config information with at least some formatting
        """
        print 'General'
        Temp = Info.keys()
        Temp.sort()
        for K in Temp:
            #Handle all the items that are stand-alone without a lot of structure
            if not K in ('Modules','Tabs','Metrics','EnumeratedOptions','Widgets','Scheme'):
                if K == 'SbbIcons':
                    print '     %s: %s %s %s %s'%tuple([K]+Info[K])
                elif K == 'BuiltinOptions':
                    print '     %s'%K
                    Temp = Info[K].items()
                    Temp.sort()
                    for Key,Value in Temp:
                        print '          %-7s %s'%(Key,Value)        
                else:    
                    print '     %s: %s'%(K,Info[K])
        #Now handle the more complicated things, other than widgets            
        for N in ( 'Modules', 'Tabs', 'EnumeratedOptions','Metrics','Scheme'):
            print N
            Temp = Info[N].items()
            Temp.sort()
            for Item in Temp:
                print '    %s: %s'%tuple(Item)
        #Now deal with the widgets        
        if OmitWidgets:
            print 'Widgets omitted by request.'
        else:

            for Tab in Info['Modules']:
                print 'Widgets of module %s:'%Tab
                Temp = Info['Modules'][Tab]['Widgets'].items()
                Temp.sort()
                for Widget,Items in Temp:
                    print '    %s:'%Widget        
                    Items = Items.items()
                    Items.sort()
                    #print non-options first
                    for I in Items:
                        if I[0] <> 'Options':
                            print '        %s: %s'%tuple(I)
                    #then the options            
                    for I in Items:
                        if I[0] == 'Options':
                            print '        Options:'
                            Options = I[1].items()
                            Options.sort()
                            for Option,Value in Options:
                                print '            %s: %s'%(Option,Value)    

        print '----- end -----'                
            
    def FetchIcon(self,Section,Option=None):
        """
        Fetch an icon as a photo image.
        
        If "Section" and "Option" are both specified then we fetch the *name* of the
            icon based on "Section" and "Option"
            
        If "Option" is "None" the "Section" *is* the name of the icon.    
        
        1) We fetch the icon name from the config file.
        2) We prepend the path to the icon directory.
        3) We convert the icon to a photo image.
        
        The result will be the photo image if things went well or None if things went badly.
        """
        if Option:
            #Fetch the name of the icon from the config file
            Temp = self.Fetch(Section,Option)
        else:
            #Caller passed us the icon name directly
            Temp = Section    
        if Temp <> None and Temp <> 'None' and self.Info['IconDir'] <> None:
            try:
                Path = self.Info['IconDir'] + Temp
                Temp = PhotoImage(file=Path)
            except:
                if Option:
                    #We fetched the option name from the config file
                    M = ('Section "%s", Option "%s" an error happened while trying to '
                        'read the icon "%s". Does this icon file exist?')%(Section,Option,Path)
                else:
                    #We were given the option name
                    M = ('An error happend while trying to read the icon "%s". Does this '
                        'icon file exist?')%Path        
                self.Error(M)
                Temp = None    
        else:
            #the icon name or the icon directory name were missing
            Temp = None    
        return Temp    
    
    def Fetch(self,Section,Option):
        """
        Fetch a config option from specified section.
        
        If a section is missing we issue a message and note the missing
            section so we don't spew out redundant messages.
            
        The result is the option, or None if the option or section were
            missing.            
        """
        if Section in self.MissingSections:
            #that section is already known to be missing
            Result = None
        else:    
            #the section is there
            if not self.C.has_section(Section):
                #section is missing
                self.MissingSections.append(Section)    
                print 'Error: required section "%s" not found in config file.'%Section
                self.ErrorCount += 1
                Result = None
            else:    
                #section exists
                if self.C.has_option(Section,Option):
                    #option exists
                    Result = self.C.get(Section,Option)
                else:
                    print 'Error: required option "%s" not found in section "%s" of the config file.'%(Option,Section)    
                    self.ErrorCount += 1
                    Result = None
        return Result    

    def PrintOptionTypes(self):
        """
        Print a sorted list of all known option types.
        """
        List = list(ConfigReader.BuiltinOptionTypes.keys())
        Margin = 3 * ' '
        print Margin + "rapyd configuration widget option types"
        print ""
        List += self.Info['EnumeratedOptions'].keys()
        List.sort()
        for Type in List:
            if Type in ConfigReader.BuiltinOptionTypes.keys():
                Detail = 'Builtin'
            else:
                Detail = self.Info['EnumeratedOptions'][Type]
            print '%s%-10s: %s'%(Margin,Type,Detail)        

    def PrintOptionXref(self):
        """
        Print a crossreference of options and the widgets that use them
        """
        Stuff = {}
        for Tab in self.Info['Modules'].keys():
            for W in self.Info['Modules'][Tab]['Widgets'].keys():
                #W runs though the name of all widgets
                Widget = self.Info['Modules'][Tab]['Widgets'][W]
                for O in Widget['ProtoOptions'].keys():
                    #O runs through the names of all options in this widget
                    try:
                        Stuff[O].append(W)
                    except KeyError:
                        Stuff[O] = [W]
        Keys = Stuff.keys()
        Keys.sort()
        for K in Keys:
            Stuff[K].sort()
            Temp = rpHelp.TextWrap(' '.join(Stuff[K]),48)
            K = K + ':'
            for T in Temp:
                print '    %25s %s'%(K,T)
                K = 25*' '
                
        print '--- end ---'        


    def Error(self,Message):
        """
        Issue an error message and update the error count.
        """
        if self.ErrorCount == 0:
            print '\nError(s) in configuration file:'
        if not Message[-1] in '.?':
            Message += '.'    
        print rpHelp.TextBreak('--> %s'%Message,79,Glue='\n    ')    
        self.ErrorCount += 1

def PrintHelp():
    """
    Print command line help message
    """
    print """
This is Rapyd-Tk, a GUI program for creating and maintaining
applications written using Python and Tkinter.

Rapyd Copyright 2010 Cam Farnell

Rapyd is free software; you can redistribute if and/or modify it under
the terms of the GNU General Public License, version 2, as published by
the Free Software Foundation. The full text of the  License is available
via the Rapyd help system: click "Help", then "License" then "Full text
of GNU General Public License".

Rapyd requires Python version 2.1 or greater.

This note covers installation only. Once Rapyd is running, use the help
systen to learn about all other aspects of Rapyd. There is a presumption
here that you already have some knowledge of Python and Tkinter. If you
are totally new to both of these then Rapyd probably isn't the place to
learn.

As unpacked Rapyd consists of these files and directories:

The main file to run:

    rapyd.py
    
Additional modules required for operation:

    rpWidgets.py
    rpOptions.py
    rpHelp.py
    rpErrorHandler.py
    dnd_realworld.py
    
The file containing the help messages:

    rapyd.help
    
The configuration file:

    rapyd.config
    
The file containing a template for newly created projects:

    rapyd.template
    
Version and revision history:

    versions.txt
    
A demonstration Rapyd application:

    RapydDemo.rpj        

A directory containing icons, and images used in help messages:

    Icons
    
Where you put these files is pretty much up to you. Perhaps at some
point we'll write a fancy installer but we haven't done so yet.

There are various option in the config file that you can set. These are
documented in the config file itself, which is simply a text file. Unless
you move files around (see below) there is nothing in the config file that
*needs* to be touched in order for Rapyd to work. As delivered the Rapyd code
editor uses the same key bindings and colorization settings as Idle. An
additional bindings/colorization scheme which matches the Midnight Commander
is also included; if you want to use it you will have to revise the
"DefaultEditorScheme" setting in the config file. You can easily define your
own bindings/colorization scheme - see documentation in the config file for
details.


As unpacked all the Rapyd files are in one directory and the icons are
in a directory from that directory. If you go to the directory in
question and run Rapyd it should work. If you to move the files to
other locations then here's what you need to know:

When you run "rapyd.py" it needs to be able to find the config file. 

o If you invoke rapyd with an option of "--config=<path>" on the command
  line then Rapyd looks to <path> for the config file. Note that <path>
  must be the full path to the file including the filename and extension.

o If the path to the config file was not specified on the command line then
  Rapyd checks for an environment variable RAPYDCONFIG and if found uses
  it's value as the path to the config file.

o If neither of the above are specified then Rapyd looks in the current
  directory for the config file.

Rapyd expects the template file to be in the same directory as the
config file.

In the config file there are options to say where the help file and the
icon directory are located. If you use the config file exactly as it was
received then Rapyd will expect the help file and the icon directory to
be in the same directory as the config file. If you want them to be
somewhere else then put them where you want them and revise the config
file to say where they are.

Text size
---------

Depending on the size of your screen, the text in Rapyd may be too large
or too small. If this is an issue, from within Rapyd call up the help
index and search for "font size"; the corresponding help page explains
how to change the size of the fonts used.


Run time error handling
-----------------------

Note that projects produced by Rapyd rely on module "rpErrorHandler.py" to
gracefully handle error reports in a Rapyd-aware manner. Once a project 
which was developed using Rapyd is done and working, it can be run directly 
without need of Rapyd itself, but the module "rpErrorHandler" *is* required 
and should be available.
    """
            
"""
GblProjectDirectory. Is set at "Load Project" and "New Project" time. Is guaranteed to end
    in a slash unless it refers to the current directory in which case it is an empty string.
"""

if '--help' in sys.argv or '-?' in sys.argv or '-h' in sys.argv:
    PrintHelp()
    sys.exit()

Root = Tk()
Root.geometry('800x600+20+100')

#The name under which the main code area is known
GblMainName = '-Main-'

# Fetch the config information and exit if it was invalid
Cfg = ConfigReader()
if Cfg.ErrorCount <> 0:
    print "\nTerminating due to configuration errors.\n"
    sys.exit(100)

HelpButton = "<ButtonPress-2>"
Help = rpHelp.TheHelpThingy(
    Intro='__intro'
    ,Locate=(20,20,Root)
    ,OfferCompiler=Cfg.Info['Debug']
    ,Path=Cfg.Info['HelpPath']
    ,Title='  Rapyd-Tk Help  '
    ,LinkColor = Cfg.Info['LinkColor']
    ,BasicFontSize = Cfg.Info['HelpTextSize'][0]
    ,HeadingFontSize = Cfg.Info['HelpTextSize'][1]
    )
Rpw.Help = Help
Rpw.HelpButton = HelpButton
Rpw.Cfg = Cfg

Rpo.Help = Help
Rpo.HelpButton = HelpButton
Rpo.Cfg = Cfg

rpErrorHandler.Help = Help

#Create help substitution entries for the editor actions in help
ActionSubstitutionsGenerate()

#Generate a substitution for the schema name
Help.AddSubstitution(['$editschema',Cfg.Info['SchemeCurName']])

#And path to icon/image directory
Help.AddSubstitution(['$img',Cfg.Info['IconDir']])

#And the version number
Help.AddSubstitution(['$version',VersionNumber])
Rpw.VersionNumber = VersionNumber

# Create the widreq repository and a default herd
GblParkingLotName = 'the Parking Lot'

GblModules = {'NewProject':WidreqRepository()}
GblPreviousModule = 'NewProject'
Repo = GblModules['NewProject']
Repo.ModuleName = 'NewProject'
Rpo.Repo = Repo

#Repo.DebugSelectorSet('')

GblWRID = Repo.Register('Global main loop')
R = Repo.Request(GblWRID, 'HerdCreate', GblParkingLotName)
if R <> 1:
    print R
    raise Exception, "Creation of parking lot failed unexpectedly"
R = Repo.Request(GblWRID, 'HerdSelect', GblParkingLotName)
if R <> 1:
    print R
    raise Exception, "Selection of parking lot failed unexpectedly"

InitialProject = None
for Temp in sys.argv[1:]:
    if Temp[0] <> '-':
        Temp = list(os.path.splitext(Temp))
        if Temp[1] in ('','.'):
            # We get '' if they specified no extension ("baffy")
            # We get '.' it they specified a trailing dot ("baffy.")
            Temp[1] = '.rpj'
        InitialProject = ''.join(Temp)
        break        
GblLoadInProgress = False        
GblLayout = Layout(Root,InitialProject)
Root.mainloop()
