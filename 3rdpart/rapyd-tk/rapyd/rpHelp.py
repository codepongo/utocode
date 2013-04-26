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
A help facility to use with Tkinter.

This help facility was developed for use with Rapyd-Tk but is quite
    general. It could be included in virtually any Tkinter based
    project that needs a stand-alone help facility:


How to add help this help facility to a python program.

    o In your program, create an instance of the help providing class, like this:
    
        MyInstance = rpHelp.TheHelpThingy( arguments )
          
        Where "arguments" is one or more of the following keyword arguments.

        o "Path" is the path to the file in which all the help information is stored.
           If the compiler is being offered and the file doesn't exist you are asked
           if you want to create the file. If the compiler isn't being offered and the
           file doesn't exist you simply get a message saying it doesn't exist. No
           default; this argument is required.
        
        o "Index" If true, we present an 'Index' button which links to a list of all
           abstracts of all topics from which the user can choose. Defaults to True.
    
        o "Intro" If not "None" and it is the name of a TopicID, then we present 
           the user with an "Introduction" button which links to the specified 
           topic which is usually some 'new user start here' stuff. Defaults to
           "None".
        
        o "Locate" Tells us to position the help window with respect to a particular widget.     
           If specified, it should be a 3-element list or tuple giving (X,Y,Widget).
           The help window will be positioned X to the right of and Y below the upper
           left corner of Widget. If Locate is not specified, the help window pops
           up wherever the window manager decides to place it. Note that the data in
           Locate is used AT THE TIME THE HELP WINDOW IS CREATED which may be different
           than it was when TheHelpThingy instance was created.
    
        o "OfferCompiler" If true and we are passed a help topic which doesn't exist, we
           create the help topic and offer to fire up the HelpCompiler for the user.
           When OfferCompiler is true (which suggests we are in development mode)
           then the HelpTopicID is shown on the user help page. Defaults to False.
        
        o "Title", if given, is the title used on the user help window. Defaults to "Help".    
    
    o To invoke help from within your program:
    
        MyInstance( help-topic )
        
        Where help-topic is a text string containing the help topic. 
        
    o To author help screens either run this module by itself (supply the name of the
        help file when asked) or set "OfferCompiler" when running your program in 
        which case you will be bounced into the help compiler on encountering a
        not-yet-defined help topic.


The help information is kept in a dictionary:
    o "Key"         The topic ID string
    o "['Abstract']"  A list of lines to appear in the help topic list
    o "['Hotlinks']"  A list of hotlink phrases
    o "['Comments']"  Where help authors can talk to themselves
    o "['Plurals']"   A list of integer indicies, possibly empty. See below.
    o "['Text']"      The actual text to be formatted
    o "['Wip']"       A boolean. True if this topic is a work-in-progress, false if complete.
    o "['Links']" An optional list of any link references in this topic. Each item in the
        list is a string like this:
        
        "&<HotlinkText>" for a hotlink
        "=<LinkTarget>"' for a link.
                
        This entry isn't guaranteed to exist, but the routine "LinksExtract" will
            compute and set this entry if necessary. This entry exists simply for
            speed; to prevent dangling links and duplicate hotlinks we scan every
            help topic when a help topic has changed. Accessing these lists of links
            is way faster than finding the links in the text each time.
            
    "Plurals" There are times when one or more arguments passed to a help topic are numbers
        and it is often convenient to be able to adjust the text depending on whether the
        number is singular or plural. Each item in the "Plurals" list is an index which
        selects one of the arguments from the argument list. If "Plurals" is empty, no
        pluralization processing is done. See the routine "HelpPluralizer" for details.

    Note: A 'tuli' is a tuple or a list. 

----- 2005 -----    
02/18 Initial development.
02/19 Topic create button works.
      Topic redirect at user-help-time works.
      Clicking on a link in the help text now takes you to the topic.
      'Back' button now works.
      Index function works and is optional. 
      Intro facility added.
      Added 'Locate' option to TheHelpThingy
      Topic delete works
02/20 Now each compiler tab has it's own view area.      
      We now support bulleted and numerated lists.
02/21 Added format types F and G for fixed and fixed-bold text
      Added listbox above hotlink listbox showing topics in tabs
      Added a scroll bar to the user help window.
      User help window and view window now use hand2 cursor      
      Now support comments at top of unedited text
      At top of unedited text you can now enter topics, hotlinks and comments in any order.
      At TopicUpdate time we now check for orphaned hotlinks
      Added button to display the links to a given topic
      When HelpThingy adds a new topic, it has the compiler select that topic in a tab.
      Global substitution using __substitutions__ in place.
      Added a BACK button to the compiler.
      The title for the user help window is now passed as an argument.
      We now save and restore grab on behalf of invoking modal dialogs.
      If OfferCompiler is set, we display the help topic ID on the help page.
      In the edit window after an Enter we put the cursor under first non-blank of previous line.
      Index page was showing up double spaced. Fixed.
      Added 'tabbed' (in addition to bulleted and enumerated) in formatter.
      Now trim trailing whitespace from end of text at topic save time.
02/22 A topic with more than one line of hotlinks is now handled properly      
      Now check for LINKS button with no topic selected.
      Render was dropping the last character of text. Fixed.
      When compiler is invoked from help window, we now select the current topice in an edit tab.
      Hotlink listbox now properly fills available height.
      When we evict a topic from an edit tab, we now clear its view area.
      We now keep roughly the same text visible when the user presses the VIEW button.
      Added 'WorkInProgress' feature.
      When about to edit a topic the compiler releases any grab that was in effect.
      We now size the compiler to fill most of the screen.
      Changing indented list type in mid stream now handled gracefully by Render.
      Revised Render so it makes the bullets bold
02/24 We weren't creating Comments or Wip at from-help topic creation. Fixed      
02/25 Added @n arguments for use with redirected help topics.
      Split Redirector out into it's own routine.
      At Compiler View time we now do redirections with argument replacement.
02/26 Added help topic 'rename' facility to compiler.      
      We now keep link references in Topics[ID]['Links']
      On topic delete, we try to keep the IDBox selection at the same spot.
      Now focus on Edit area when selecting a tab for editing.
      Userhelp backlist now saves the topic ID and the argument list; needed for BACK.
02/28 Changed format of __substitutions__ to allow multi-line replacement text      
      Added 'Tidy' function to clean up the unformatted text of a topic.
03/02 Now compute width of Edit area in chars and rewidth unformatted text automatically at load time.
      Rewidth in response to 'Tidy' button now computes Edit area width dynamically.      
      Revised Render so we properly handle multi-word hotlink references which contain a newline.
      Render wasn't properly reporting unclosed brace items; fixed.
03/04 Render phase-2 wasn't properly handling an empty line which contained a tag (it happens). Fixed.
      We don't automatically rewidth the substitution page on load.
04/07 Wip setting now selectes the wip'd item in the IDBox      
      When renaming a topic we now prompt with the existing topic name.
      On renaming a topic we now update the name-in-tab listbox.
      The "links" report now also shows statistics about number of help topics and link references.
04/27 After creating a new topic it is now selected in the listbox.      
      Clicking on a link was selecting text in the new topic. Binding to ButtonRelease fixed that.
      Now put a 3 pixel border of blank space around text widgets.
      Added facility to move hotlinks from one topic to another.
----- 2006 -----
01/25 Moved substitution to it's own method.
      Now do substitution on index entries.      
      We no longer squish spaces out of index search queries.
02/07 Added the pluaralization facility.      
02/11 Can now have PhotoImages in help.
02/15 Added numer origin facility.
04/14 Added help to index dialog.
05/07 Created ButtonBox widget.
"""

import cPickle
import os.path
import re
import time
from Tkinter import *

# Somewhere around Python 2.5 Tkinter started return Tcl objects in places
#     where it previously returned strings. Thus we set "wantobjects" to
#     false to prevent things from breaking. 
import Tkinter
Tkinter.wantobjects = False

import tkFont

True = 1
False = 0

SubPage = '__substitutions__'

HelpCursor = 'hand2' #The cursor we use over rendered help text.

def D(*Stuff):
    for T in Stuff:
        print T,
        print

def MeasureWidget(Widget):
    """
    Measure the size of a widget.
    
    This measures the size of a widget by putting it on a little temporary
        canvas and then checking to see what size it is.
    """
    C = Canvas(width=200,height=200)
    T = eval(Widget)
    #print 'T=%s'%`T`
    ID = C.create_window(10,10,window=T)
    T.update_idletasks()
    Bbox = C.bbox(ID)
    C.delete(ID)
    del C
    return (Bbox[2]-Bbox[0], Bbox[3]-Bbox[1])

class TabbedFrame(Frame):
    """=d
    A widget with selectable tabs attached to a frame.
    
    This started as an alternate to "Pmw.NoteBook", although in the course of development it has
        wandered pretty far from where we started. Initially I used the "Pmw.NoteBook" widget in
        Rapyd but eventually gave up on it because of size problems. I kept running into cases where
        I would pack something onto a notebook page, call "setnaturalsize()", call "update_idletasks()",
        then check the size of the page only to get the size that the page had been BEFORE my latest
        item had been packed into it, although the item was sitting on the screen staring back at it's
        actual expected size. I spent a *long* time finding and then chasing this without success. So 
        I gave up and wrote this widget instead. 
        
    This is in no way a 'drop-in' replacement for "Pmw.NoteBook". This widget has multiple tabs but
        only a single page; you have to pack stuff onto and off of the single page as tabs change. This
        isn't a problem for me but if it is for you then by all means rewrite the code. There are a whole
        bunch of "Pmw.NoteBook" features that I didn't need and hence this widget doesn't support, plus
        a number of new features unique to this widget.

    o "LowerCommand" This is called (with the name of the page being lowered as the argument) when the 
      current page is being deselected. It should return a boolean true if it is OK with the page being 
      lowered, or return a boolean false (other than "None") to refuse to be lowered.
          
    o "RaiseCommand" This is called (with the name of the page being raised as an argument) when a
      new page is being raised.  
      
    o "ReclickCommand" This is called (with the name of the currently selected page as an argument) when
      the user clicks on the tab for the currently selected page.  
          
    o "Sort" defaults to false. If set to true, then tabs are displayed in alphabetical order.
    
    o "TabsOn" defaults to TOP and specifies where the tabs should appear. If set to BOTTOM the tabs
      show up at the bottom of the widget instead of the top.
      
    *Internal details*
    
    "TabList" is a list of dictionaries, one per tab, thus:
        o "'Name'" The name of this tab.
        o "'Text'" The text that appears on the tab.
        o "'Instance'" The label which represents the tab.
        
    #=P Published methods
    #=U Unpublished methods    
    """
    def __init__(self,Master,**kw):
        """=U
        Create the widget.
        """
        try:
            self._LowerCommand = kw['LowerCommand']
            del kw['LowerCommand']
        except KeyError:
            self._LowerCommand = None

        try:
            self._RaiseCommand = kw['RaiseCommand']
            del kw['RaiseCommand']
        except KeyError:
            self._RaiseCommand = None

        try:
            self._ReclickCommand = kw['ReclickCommand']
            del kw['ReclickCommand']
        except KeyError:
            self._ReclickCommand = None
        try:
            self._Sort = kw['Sort']
            del kw['Sort']
        except KeyError:
            self._Sort = 0        

        try:
            self._TabsOn = kw['TabsOn']
            del kw['TabsOn']
        except KeyError:
            self._TabsOn = TOP
            
        apply(Frame.__init__,(self,Master),kw)

        self._SelBackColor = '#d9d9d9'
        self._NonBackColor = '#c0c0c0'
        self._SelForeColor = '#000000'
        self._NonForeColor = '#404040'
        self._SelRelief = RAISED
        self._NonRelief = GROOVE
        self._TabFrame = Frame(self,bg=self._NonBackColor)
        self._TabFrame.pack(side=self._TabsOn,fill=X)
        self._Page = Frame(self)
        self._Page.pack(side=BOTTOM,expand=YES,fill=BOTH)
        self._TabList = []
        self._Dummy = None
        self.Clear()
        self._HelpBinding = None

    def Clear(self):
        """
        Delete all tabs from the frame
        """
        if self._Dummy <> None:
            #We had a dummy placeholder; toast it
            self._Dummy.pack_forget()
            self._Dummy = None
        for Entry in self._TabList:
            if Entry['Instance']:
                Entry['Instance'].pack_forget()
        self._TabList = []
        self._CurPage = None
        self._DrawTabs()
        self._Selected = None
        
    def Add(self,_TabName,TabText=None,BulkAdd=False):
        """=P
        Add a new tab to the widget per the name passed.
        
        If TabText is supplied, then it is the text which appears on the tab and can
            be different from the name of the tab.
            
        if TabText is omitted or None, then the name of the tab is also the text
            which appears on the tab.
            
        If "BulkAdd" is True (it defaults to False) then we add the new entry but
            we don't select the new entry and we don't update the display of the
            tabs. This is useful if you have a bunch of tabs to add. 
        """
        if TabText == None:
            TabText = _TabName
        #Add a new entry to _TabList
        self._TabList.append({'Name':_TabName,'Instance':None,'Text':TabText})
        #Sort if needed
        if self._Sort:
            self._TabList.sort(self._CompareTabs)
        if BulkAdd == False:    
            #Selecting the new tab will create a tab instance for it    
            self.Select(_TabName)

    def Delete(self,_TabName):
        """=P
        Attempt to delete the specified tab.
        
        Note that if the tab to be deleted is the currently selected tab AND that
            tab refused to be lowered, then we can not delete it.
            
        The result is 1 if the tab was deleted, 0 if not.    
        """
        _TabIndex = self._FindTab(_TabName)
        if _TabIndex == None:
            raise Exception, 'There is no tab named "%s".'%_TabName
        if self._Selected == _TabName:
            #The tab for deletion is the current tab        
            if len(self._TabList) == 1:
                #After deletion there will be zero tabs left
                if self._LowerCommand:
                    #If we have a lower command invoke it
                    R = self._LowerCommand(self._Selected)
                    if not R:
                        #The current tab refused to be lowered
                        return 0
                self._Selected = None
            else:
                #After deletion there will be one or more tabs left
                if _TabIndex == len(self._TabList)-1:
                    #The very first tab is being delted
                    _NewSel = _TabIndex - 1
                else:
                    #Tab other than the last is being deleted                
                    _NewSel = _TabIndex + 1
                _NewSelName = self._TabList[_NewSel]['Name']    
                #Attempt to select the new tab
                R = self.Select(_NewSelName)
                if not R:
                    #The current tab refused to be lowered
                    return 0
        #We have to unpack the deletee since their _TabList entry will be gone by
        #   the time we get to DrawTabs
        I = self._TabList[_TabIndex]['Instance']
        if I:
            I.pack_forget()
        #Toast the deletee            
        self._TabList.pop(_TabIndex)
        #Show the revised tabs
        self._DrawTabs()

    def GetCurSelection(self):
        """
        Return the name of the currently selected tab or None if there are no tabs.
        """
        return self._Selected

    def PageFrame(self):
        """=P
        Return the frame object which lies below the tabs. 
        """
        return self._Page

    def ReName(self, OldName, NewName=None, NewText=None):
        """
        Change the name and/or text of a tab entry.
        
        If the existing name and text are the same an all you supply is a new name
            then both the name and the text are set to the new name.
            
        If you supply new text, or if the existing name and text are different then
            the name and the text are updated independently.    
        """
        #Make sure the tab exists
        TabIndex = self._FindTab(OldName)
        if TabIndex == None:
            raise Exception, 'There is no tab named "%s".'%OldName
        Entry = self._TabList[TabIndex]
        if Entry['Name'] == Entry['Text'] and NewText == None:
            NewText = NewName
        if NewName <> None:
            #Rename the tab
            Entry['Name'] = NewName
            Entry['Instance'].Name = NewName
            if self._Selected == OldName:
                #Handler rename of selected tab properly
                self._Selected = NewName
        if NewText <> None:    
            #Retext the tab    
            Entry['Text'] = NewText
            Entry['Instance']['text'] = NewText
            #Sort if needed
            if self._Sort:
                self._TabList.sort(self._CompareTabs)
        #Display the revised tabs
        self._DrawTabs()        
        
    def Select(self,_TabName):
        """=P
        Attempt to select the specified tab.
        
        The result is 
            o  1 if the tab is now selected, 
            o  0 if the currently selected tab refused to be lowered,
            o -1 if there is no tab of the specified name.
        """
        if _TabName == self._Selected:
            #Requested tab is already selected; no action required
            return 1
        #Make sure the tab exists
        if self._FindTab(_TabName) == None:        
            return -1
        if self._Selected and self._LowerCommand:
            #An actual page is selected AND we hve a LowerCommand
            R = self._LowerCommand(self._Selected)
            if R == None:
                raise Exception, "LowerCommand must return a boolean other than None"
            if not R:
                #The page resuled to be lowered
                return 0
        #Note the new selection        
        self._Selected = _TabName
        #And give the raise command a kick at the can
        if self._RaiseCommand:
            self._RaiseCommand(self._Selected)
        #Revise the tab visuals to show the new selection    
        self._DrawTabs()            
        return 1

    def SetHelpBinding(self,EventString,Procedure):
        """
        Specify a binding to be applied to newly created tabs.
        
        This is handy if all tabs are to share the same help specification.
        
        EventString is typically the mouse button used for help.
        """
        self._HelpBinding = (EventString,Procedure)

    def Tab(self,_TabName):
        """
        Return the label object of the specified tab.
        """
        #Make sure the tab exists
        _TabIndex = self._FindTab(_TabName)
        if _TabIndex == None:
            raise Exception,  'There is no tab named "%s".'%_TabName
        #Return the tab    
        Result = self._TabList[_TabIndex]['Instance']
        assert Result <> None
        return Result

    def TabNames(self):
        """
        Return a list of the names of all tabs.
        """
        Result = []
        for Temp in self._TabList:
            Result.append(Temp['Name'])
        return Result    

    def _on_Click(self,_Event):
        """=U
        User clicked on a tab; try to select it.
        """
        _NewTab = _Event.widget.Name
        if _NewTab <> self._Selected:
            #User clicked on a non-selected tab; attempt to select it
            self.Select(_NewTab)
        else:
            #User clicked on the currently selected page.    
            if self._ReclickCommand:
                #Invoke reclick command if possible
                self._ReclickCommand(self._Selected)

    def _CompareTabs(self,A,B):
        """=U
        Compare two tab names from self._TabList.
        """
        return cmp(A['Text'], B['Text'])

    def _DrawTabs(self):
        """=U
        Update the tab display.
        """
        #Unpack any currently packed tabs
        for Entry in self._TabList:
            if Entry['Instance']:
                Entry['Instance'].pack_forget()
        if self._TabList == []:
            #If we have no tabs at all we draw a dummy placeholder so the tab frame shows at
            #    the correct height.
            self._Dummy = Label(self._TabFrame,text='',relief=FLAT,bg=self._NonBackColor
                ,activebackground=self._NonBackColor)
            self._Dummy.pack(side=LEFT)
        else:
            #We have one or more actual tabs
            if self._Dummy <> None:
                #We had a dummy placeholder; toast it
                self._Dummy.pack_forget()
                self._Dummy = None
            #Draw each tab in turn                
            for Entry in self._TabList:
                if Entry['Instance'] == None:
                    #The tab instance Label doesn't exist yet; create it
                    L = Label(self._TabFrame,text=Entry['Text'],pady=2,padx=4)
                    Entry['Instance'] = L
                    Entry['Instance'].Name = Entry['Name']
                    Entry['Instance'].bind('<Button-1>',self._on_Click)
                    if self._HelpBinding:
                        Entry['Instance'].bind(self._HelpBinding[0],self._HelpBinding[1])
                B = Entry['Instance']    
                #Pack this instance so it shows    
                B.pack(side=LEFT,pady=0,padx=0)
                #Mark the selected tab with special color and border    
                if Entry['Name'] == self._Selected:
                    R = self._SelRelief
                    BG = self._SelBackColor
                    FG = self._SelForeColor
                else:
                    R = self._NonRelief
                    BG = self._NonBackColor
                    FG = self._NonForeColor
                B['relief'] = R        
                B['activebackground'] = BG
                B['bg'] = BG
                B['activeforeground'] = FG
                B['fg'] = FG
                
    def _FindTab(self,_TabName):
        """=U
        Find index for the tab of the specified name.
        
        The result is an index into "self._TabList", or None if there is no tab of that name.
        """
        for J in range(len(self._TabList)):
            if self._TabList[J]['Name'] == _TabName:
                return J
        return None                

class NoteBook(TabbedFrame):
    """
    A simple notebook with one frame per page.
    
    For people who care, this saves the trouble of packing stuff onto and off of the single
        frame provided by "TabbedFrame".
    """
    def __init__(self,Master=None,**kw):

        try:
            self.__UserRaiseCommand = kw['RaiseCommand']
        except KeyError:
            self.__UserRaiseCommand = None
        kw['RaiseCommand'] = self.__OurRaiseCommand

        try:
            self.__UserLowerCommand = kw['LowerCommand']
        except KeyError:
            self.__UserLowerCommand = None
        kw['LowerCommand'] = self.__OurLowerCommand

        apply(TabbedFrame.__init__,(self,Master),kw)
        #The frame for each page
        self.__FrameList = []
        #Key is the name of the frame, value is the page index
        self.__NameList = []
        self.__PackedFrame = None

    def selectpage(self,PageIndex):
        """
        Select the specified page
        """
        self.__Unpack()
        self.Select(self.__NameList[PageIndex])
        Temp = self.__FrameList[PageIndex]
        Temp.pack(expand=YES,fill=BOTH)
        self.__PackedFrame = Temp
        
    def add(self,PageName):
        """
        Add a new page of the specified name to the notebook.
        
        Resuilt is the frame of the new page.
        """
        self.__Unpack()
        Temp = Frame(self.PageFrame())
        Temp.pack(expand=YES,fill=BOTH)
        self.__PackedFrame = Temp
        self.__NameList.append(PageName)
        self.__FrameList.append(Temp)
        self.Add(PageName,TabText='    %s    '%PageName)
        return Temp
        
    def page(self,PageIndex):
        """
        Return the frame that represents the specified page
        """
        return self.__FrameList[int(PageIndex)]
        
    def __OurRaiseCommand(self,Page):
        """
        A page is being raised per user click.
        """
        I = self.__NameList.index(Page)
        self.selectpage(I)
        if self.__UserRaiseCommand:
            self.__UserRaiseCommand(Page)
        
    def __OurLowerCommand(self,Page):
        """
        A page is being lowered per user click
        """    
        if self.__UserLowerCommand:
            self.__UserLowerCommand(Page)
        self.__Unpack()
        return 1

    def __Unpack(self):
        """
        Make sure no frame is packed in the TabbedFrame
        """        
        if self.__PackedFrame:
            self.__PackedFrame.pack_forget()
        self.__PackedFrame = None
        
class ScrolledWhatever(Frame):
    """
    Generic scrolling logic suitable for deriving specific scrolled widgets.
    
    Arguments "hscrollmode" and "vscrollmode" can be either:
        o "static"  Scroll bar always present.
        o 'none"    Scroll bar never present.
        o "dynamic" Scroll bar comes and goes as necessary.
    If omitted, they default to "dynamic".
    """
    def __init__(self,Master=None,**kw):
        #
        #Fetch and validate arguments.
        #
        ArgList = (('hscrollmode', 'Xmode', 'dynamic'),
                   ('vscrollmode', 'Ymode', 'dynamic'),
                   ('widget',      'Widget', None),
                   ('label',       'label',  None),
                   ('width',       'width',  1),
                   ('height',      'height', 1),
                  ) 
        #Extract or default arguments we care about 
        for ArgName,LocalName,DefaultValue in ArgList:
            if kw.has_key(ArgName):
                DefaultValue = kw[ArgName]
                del kw[ArgName]
            exec('self._ScrolledWhatever__%s = DefaultValue'%LocalName)

        LegalModes = ('dynamic','static','none')
        assert self.__Xmode in LegalModes
        assert self.__Ymode in LegalModes
        assert self.__Widget <> None

        apply(Frame.__init__,(self,Master),kw)
        self.bind('<Configure>',self.__on_Config)
        if self.__label <> None:
            self.__label = Label(self,text=self.__label)
            self.__label.pack(side=TOP)
        self.__Frame4 = Frame(self)
        self.__Frame4.pack(expand='yes',fill='both',side='top')
        self.__BottomFrame = Frame(self)
        self.__MainFrame = Frame(self.__Frame4)
        self.__MainFrame.pack(expand='yes',fill='both',side='left')
        self.__Widget1 = self.__Widget(self.__MainFrame,height=self.__height,width=self.__width)
        self.__Widget1.pack(expand='yes',fill='both',side='top')
        self.__RightFrame = Frame(self.__Frame4)

        #Create and link the scrollbars. They get packed/unpacked later as needed
        self.__XBar = Scrollbar(self.__BottomFrame,orient=HORIZONTAL, command=self.__Widget1.xview)
        self.__YBar = Scrollbar(self.__RightFrame,orient=VERTICAL, command=self.__Widget1.yview)
        self.__Widget1['xscrollcommand'] = self.__XBar.set
        self.__Widget1['yscrollcommand'] = self.__YBar.set
        
        #These track the packedness of the scroll bars.
        self.__XBarPacked = 0
        self.__YBarPacked = 0
        
        if self.__Xmode == 'dynamic' or self.__Ymode == 'dynamic':
            #Start the babysitter only if at least one scrollbar is dynamic.
            self.after(1000,self.__Babysitter)
        
        #Measure the size of a scrollbar in aid of generating a canvas of the correct size
        #    to place in the bottom right corner when both scrollbars and in use.        
        self.__YBarSize = MeasureWidget('Scrollbar(orient="vertical")')
        
        #This is the canvas for use in the bottom right corner.
        self.__Corner = Canvas(self.__BottomFrame,width=self.__YBarSize[0]
            ,height=self.__YBarSize[0],borderwidth=0,relief=RAISED)


        #Kluge for testing. Pack all scrollbars to see if this stops the wobble problem
        self.__Corner.pack(side='right')  
        self.__BottomFrame.pack(fill='x',side='bottom')
        self.__XBar.pack(side=BOTTOM,fill=X)
        self.__RightFrame.pack(fill='y',side='right')
        self.__YBar.pack(side=RIGHT,fill=Y)


        self.__Count = 0       

    def __on_Config(self,Event=None):
        """
        Our main frame has been resized; configure scroll bars.
        """
        
        return #Testing
        
        print 'ScrolledWhatever: rebarring due to config event %s'%self.__Count
        self.__Count += 1
        self.__Barify()        
    #
    #Start of non-Rapyd user code
    #
    #
    # Public methods
    #
    def FetchLabel(self):
        """
        Return the label widget.
        """
        return self.__label
    
    def FetchWidget(self):
        """
        Return the text widget.
        """
        return self.__Widget1
        
    def FetchYBar(self):
        """
        Return the vertical scrollbar widget.
        """
        return self.__YBar

    def FetchXBar(self):
        """
        Return the horizontal scrollbar widget.
        """
        return self.__XBar
        
    def Rebar(self):
        """
        Regenerate the scrollbars based on current conditions
        """
        self.__Barify()

    #
    # Private methods
    #

    def __Barify(self,Caution=0):
        """
        Install or de-install scrollbars as necessary.
        
        If Caution is true and Xmode is 'dynamic' then we will add a horizontal scrollbar if
            necessary but we will not remove one. Without this there are cases where we would
            loop adding and removing the horizontal scrollbar.
        """
        
        return #Testing
        
        #Figure out what we need
        Xview = self.__Widget1.xview()
        Yview = self.__Widget1.yview()
        if Yview == (0,0):
            #This can happen at startup;
            Yview = (0,1)
        self.BarifyInProgress = 1
        if self.__Xmode == 'none':
            XBarNeeded = 0
        elif self.__Xmode == 'static':
            XBarNeeded = 1
        else:
            XBarNeeded = (Xview <> (0.0, 1.0)) or (self.__XBarPacked and Caution)
        if self.__Ymode == 'none':
            YBarNeeded = 0
        elif self.__Ymode == 'static':
            YBarNeeded = 1
        else:
            YBarNeeded = Yview <> (0.0, 1.0)
        BothNeeded = XBarNeeded and YBarNeeded
        BothPacked = self.__XBarPacked and self.__YBarPacked

        ##D('Xv=%s Yv=%s Xn=%s Xp=%s Yn=%s Yp=%s BothNeeded=%s, BothPacked=%s'%(Xview,Yview,XBarNeeded,self.__XBarPacked
        ##    ,YBarNeeded,self.__YBarPacked,BothNeeded,BothPacked))

        #The cornerblock
        if BothNeeded <> BothPacked:
            if BothPacked:
                self.__Corner.pack_forget()
            else:
                #For reasons not clear, it is necessary to pack the corner first and then
                #   pack the XBar. If we already have an XBar we unpack it here, then pack
                #   the corner. Since both bars are needed, the code below will repack the
                #    XBar.
                if self.__XBarPacked:
                    self.__XBar.pack_forget()
                    self.__BottomFrame.pack_forget()
                    self.__XBarPacked = 0
                self.__Corner.pack(side='right')  

        #Horizontal bar                             
        if XBarNeeded <> self.__XBarPacked:
            self.__XBarPacked = XBarNeeded
            if XBarNeeded:
                self.__BottomFrame.pack(fill='x',side='bottom')
                self.__XBar.pack(side=BOTTOM,fill=X)
            else:
                self.__XBar.pack_forget()
                self.__BottomFrame.pack_forget()

        #Vertical bar
        if YBarNeeded <> self.__YBarPacked:
            self.__YBarPacked = YBarNeeded
            if YBarNeeded:
                self.__RightFrame.pack(fill='y',side='right')
                self.__YBar.pack(side=RIGHT,fill=Y)
            else:
                self.__YBar.pack_forget()
                self.__RightFrame.pack_forget()
        self.__BarifyInProgress = 0

    def __Babysitter(self,Args=None):
        """
        Check every so often; add or remove scrollbars as necessary.
        
        Note that this routine will add a horizontal scrollbar if necessary
            but will never remove one.
        """
        self.__Barify(Caution=1)
        self.after(500,self.__Babysitter)

class ScrolledText(ScrolledWhatever):
    """
    A simple scrolled Text widget.
        
    If hscrollmode is 'none' then wrap defaults to 'word', otherwise wrap defaults to 'none'.    
    """
    def __init__(self,Master=None,**kw):
        kw['widget'] = Text
        try:
            Xmode = kw['hscrollmode']
        except KeyError:
            Xmode = 'dynamic'    
        apply(ScrolledWhatever.__init__,(self,Master),kw)
        if Xmode == 'none':
            Wrap = 'word'
        else:
            Wrap = 'none'    
        self.FetchWidget().config(wrap=Wrap)

class ScrolledListbox(ScrolledWhatever):
    """
    A simple scrolled Listbox widget.
    """
    def __init__(self,Master=None,**kw):
        kw['widget'] = Listbox
        apply(ScrolledWhatever.__init__,(self,Master),kw)
        
    def setlist(self,ItemList):
        """
        Replace all listbox items with those in ItemList.
        """
        L = self.FetchWidget()
        L.delete(0,END)
        for Item in ItemList:
            L.insert(END,Item)
            
    def getcurselection(self):
        """
        Return the text of the selected items as a list.
        """
        L = self.FetchWidget()
        Result = []
        for LineNumber in L.curselection():
            Result.append(L.get(LineNumber))
        return Result    

class ButtonBox(Frame):
    """
    A simple horizontal ButtonBox widget.
    """
    def __init__(self, Master, padx=3, pady=6):
        self.__padx = padx
        self.__pady = pady
        self.__Buttons = {}
        apply(Frame.__init__,(self,Master))
        
    def add(self, Name, **kw):
        """
        Add a button to the ButtonBox.
        """
        if not kw.has_key('text'):
            kw['text'] = Name
        Result = apply(Button,(self,),kw)    
        Result.pack(side=LEFT,expand=YES,padx=self.__padx,pady=self.__pady)
        self.__Buttons[Name] = Result
        return Result    
        
    def button(self, Name):
        """
        Return the button of the specified name
        """
        if self.__Buttons.has_key(Name):
            return self.__Buttons[Name]
        else:
            return None    

class HintHandler:
    """=u
    Hint implementation object.
    
    "HintHandler(Widget, HintText)"
    
    At creation time pass a widget and hint text. Thereafter the hint will appear
        when the mouse pointer is over the widget and has not moved for 1000 ms. The hint
        will stay visible for 3000 ms or the mouse pointer leaves the widget.
    
    There are three public methods:
      o "Text(HintText)"  changes the text of the hint to be displayed. 
      o "Delay(Value)" sets the delay prior to a hint appearing to Value ms. 
      o "Duration(Value)" sets the amount of time a hint stays visible to Value ms.
    
    Note that the delay and duration pertain to ALL instances of HintHandler.
    
    This class can easily be applied to an ordinary Tkinter widget instance or used 
     to add built-in hint capability to a derived widget.
    """
    def __init__(self, Widget, hint=None):
        self.Widget = Widget
        self.Widget.bind('<Enter>',self.on_Enter)
        self.Widget.bind('<Leave>',self.on_Leave)
        self.Hint = hint
        self.HintShowing = 0
        self.AfterPending = None
    
    def Text(self,HintText):
        """
        Set the text of our hint as specified.
        """
        self.Hint = HintText
        
    def Delay(self,Value):
        """
        Set the delay prior to hint appearing, in mS.
        """
        HintHandler.CheckCount = int(Value) / HintHandler.CheckDelay         
        
    def Duration(self,Value):
        """
        Set the amount of time the hint stays visible, in mS.
        """
        HintHandler.ShowTime = int(Value)
        
    #--- Items from here to the end of the class are private. Use at your own risk ---#

    #Number of times we check to make sure the cursor hasn't moved before showing hint
    CheckCount = 4
    #Number of ms of delay between checking
    CheckDelay = 5 
    #Default number of ms that hint displays for
    ShowTime  = 3000
    # The default offset from the cursor
    HintXOffset = 6
    HintYOffset = 16
                    
    def on_Enter(self,event):
        #
        """
        The mouse just entered our widget. 
        
        Start the process of checking to see if the mouse has stopped moving.
        """
        if self.Hint <> None:
            self.AfterPending = self.Widget.after(HintHandler.CheckDelay,func=self.CheckForStopped)
            self.MouseAt = self.Widget.winfo_pointerxy()
            self.CountDown = HintHandler.CheckCount
        
    def CheckForStopped(self):
        #
        """
        Check to see if the mouse has held still long enough
        """
        if self.Widget.winfo_pointerxy() <> self.MouseAt:
            #the mouse moved since last time we checked
            #remember things and setup to check again soon
            self.AfterPending = self.Widget.after(HintHandler.CheckDelay,func=self.CheckForStopped)
            self.MouseAt = self.Widget.winfo_pointerxy()
            self.CountDown = HintHandler.CheckCount
            return
        #the mouse has not moved recently
        self.CountDown -= 1
        if self.CountDown > 0:
            #mouse hasn't held still long enough; we'll come back soon and check again
            self.AfterPending = self.Widget.after(HintHandler.CheckDelay,func=self.CheckForStopped)
            return
        #The mouse has held still for long enough; it's time to actually show the hint. 
        self.Help = Label(self.Widget.winfo_toplevel(),text=self.Hint,bg='#FFFFA0',relief=GROOVE,bd=3)
        #Get location of mouse with respect to top-level window, and geometry of top level window
        X, Y, TopW, TopH, TopX, TopY = MouseInTop(self.Widget)
        #And now for a few sanity checks. Usually we place the hint just below and to the right of the
        #cursor, but we adjust that if the hint would fall off the right or the bottom of the top level
        #window. 
        Xpos = X + HintHandler.HintXOffset
        HintWidth = self.Help.winfo_reqwidth()
        if (HintWidth + Xpos) > TopW:
            #The hint is going to fall off the right side of the top level window
            #Shift the hint left, but not off the left side of the top level window
            Xpos = max(TopW - HintWidth, 0)
        Ypos = Y + HintHandler.HintYOffset
        HintHeight = self.Help.winfo_reqheight()
        if (HintHeight + Ypos) > TopH:
            #The hint is going to fall off the bottom of the top level window
            #Shift the hint up, but not off the top of the top level window
            Ypos = max(TopH - HintHeight, 0)
        #Place the hint per our calculation    
        self.Help.place(x=Xpos, y=Ypos)
        self.HintShowing = 1
        #Start timer so we clear hint eventually
        self.AfterPending = self.Widget.after(HintHandler.ShowTime,func=self.HideHint)
        
    def on_Leave(self,event):
        #
        """
        Pointer left the widget; clean up any pending timers
        """
        self.HideHint()
        if self.AfterPending <> None:
            self.Widget.after_cancel(self.AfterPending)
            self.AfterPending = None
    
    def HideHint(self):
        #
        """
        If the hint is showing make it go away
        """
        if self.HintShowing:
            self.HintShowing = 0
            self.Help.destroy()

def MouseInTop(w):
    """=u
    Given a widget, return a six element geometry tuple. 
    
    The first two elements give the position of the mouse 
        with respect to the top-level window in which the widget resides. The last four elements are the
        geometry information for that top level window.
    """
    #Get mouse position with respect to the display
    M = w.winfo_pointerxy()
    #Get geometry of top level window with respect to the screen
    T = GeoTop(w)
    return (M[0]-T[2], M[1]-T[3])+T

def GeoTop(w):
    """=u
    Return some geometry related informat about a widget.
    
    Given a widget "w" return a geometry tuple "(w,h,x,y)" showing the size and position of the
        widgets top level window (which is *not* necessarily the root window) with respect to
        the uppler left corner of the display.
    """
    while 1:
        ParentName = w.winfo_parent()
        #print w.winfo_class()
        if w.winfo_class() in ('Toplevel', 'Tk'):
            #were at a top level window; done
            break
        w = w.nametowidget(ParentName)
    return GeometryDecode(w.winfo_geometry())

def GeometryDecode(GeometryString):
    """=u
    Given a geometry string of the form wxh+-x+-y we return the four numbers as a tuple
    """
    GeometryString = GeometryString.replace('x',',')
    GeometryString = GeometryString.replace('+',',')
    return eval(GeometryString)

def GeometryEncode(GeometrySequence):
    """=u
    Given a tuli of four numbers, return a geometry string of the form wxh+x+y
    """
    return '%dx%d%+d%+d'%tuple(GeometrySequence)

class MessageDialog:
    """=d
    A simple utility Message Dialog.

    "Title" is the window title.

    "Message" is the message to appear in the body of the dialog.
    
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
    """

    def  __init__(self,Title='Information'
                      ,Message='You forgot the message, dumox'
                      ,Buttons=None):
        """
        Create the dialog.
        """
        self._Win = Toplevel()
        self._Win.title(Title)
        self.Result = None
        Width = 300
        Height = 150

        #position near the mouse    
        MouseX, MouseY = self._Win.winfo_pointerxy()
    
        Geo = [Width, Height, MouseX-70, MouseY - (Height/2)]
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
        self.OurLabel = Label(self._Win,textvariable=self.LabelStringVar)
        self.OurLabel.pack(anchor='w',pady=10,padx=20,expand=YES,fill=BOTH)
        self.LabelStringVar.set(TextBreak(str(Message),44))    
        #button bar across the bottom
        self.BB = ButtonBox(self._Win)
	self.BB.pack(side='top')

        FirstButton = True
        for T in Buttons:
            assert len(T) == 2, str(T)
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
        #be modal
        self._Win.focus_set()
        Grabber(self._Win)
        self._Win.wait_window()

    def Enter(self,Event):
        self.Result = self.EnterResult
        self._Win.destroy()
            
    def Esc(self,Event):
        self.Result = self.EscResult
        self._Win.destroy()

    def Message(self,M):
        """
        Set the message to be displayed in the dialog.
        """
        self.LabelStringVar.set(M)
        self._Win.update_idletasks()    

    def Close(self,Event):
        """
        Close the dialog. Not needed if dialog is modal.
        """
        self.Result = Event.widget.Result
        self._Win.destroy()    

def DigitEncode(Value):
    """
    Convert a single digit number to a string.
    
    If "Value" is an integer and it is in the range 0..9 we convert it to a word,
        otherwise it is returned as is.
    """
    if type(Value) == type(0) and Value in range(10):
        Value = ('zero','one','two','three','four','five','six','seven','eight','nine')[Value]
    return Value

def Plural(String,Pluralist,ToPercent='',Meta='{/}',DoCap=True):
    """
    Do canonical pluralization.
    
    If Pluralist is an integer or tuli of length one then that one element is the 
        indicator and terms in String of the form {ssss/pppp} are replaced by just 
        ssss if the indicator is singular or by just pppp if the indicator is non-singular. 
        
        If Pluralist is of length > 1 then terms are of the form {nssss/pppp} and the
        indicator is Pluralist[n].
        
        To put a left-brace in your text use {{.
        
        To put a slash in ssss or pppp text use //.
        
        To put a right-brace in ssss or pppp text use }}.
        
        The only thing you can't do is to have an ssss part whose first character
            is a left-brace. Sorry.
            
        If the plural part is empty then {ssss} is acceptable.
        
        To create an empty singular part use {/pppp}    
            
    If Pluralist is an integer and the text contains a single percent-sign then we format
        the value of Pluralist into the string.            
 
    If "ToPercent" is not an empty string, then after the pluralization is complete, any
        instance of the ToPercent string is replaced with a percent sign. This is useful
        in cases where additional text formatting is to be done after the pluralization
        is complete.

    Normally we make the first character of the message upper case. Set DoCap false to
        defeat this option.
        
    By default the Meta characters are left-brace, slash and right-brace. Supply a three
        character string to use custom meta characters.    
    """
    State = 0
    Result = []
    assert len(Meta) == 3
    assert type(Meta) == type('')
    if type(Pluralist) == type(0) and String.count('%') == 1:
        String %= DigitEncode(Pluralist)
    if DoCap:    
        String = Cap(String)    
    MetaBegin,MetaSwitch,MetaEnd = Meta
    if type(Pluralist) == type(0):
        Pluralist = [Pluralist]
    if len(Pluralist) == 1:
        Indicator = int(Pluralist[0])
    for C in String:
        if State == 0:
            #we have been copying ordinary text
            if C == MetaBegin:
                #time to copy singular text
                State = 1
            else:
                Result.append(C)
            continue    
        if State == 1:
            #we are at first character after MetaBegin
            if C == MetaBegin:
                #They want an actual MetaBegin in text
                Result.append(MetaBegin)
                State = 0
                continue
            if len(Pluralist) > 1:
                #This is our indicator character
                assert C in ('0123456789')
                Indicator = int(Pluralist[int(C)])
                State = 2
                continue
            #Anything else to be processed by state 2    
            State = 2
        if State == 2:
            #we have been scanning singular text
            if C == MetaEnd:
                #We may be done
                State = 5
            elif C == MetaSwitch:
                #time to copy plural text
                State = 3
            else:
                #just copy
                if Indicator == 1:
                    Result.append(C)                    
            continue        
        if State == 3:
            #we are at first character after MetaSwitch
            if C == MetaSwitch:
                #They want a MetaSwitch in the text
                Result.append(MetaSwitch)
                State = 2
                continue
            #anything else takes us to state 4
            State = 4    
        if State == 4:
            #we have been scanning plural text
            if C == MetaEnd:
                #we may be done
                State = 6
            else:
                #just copy
                if Indicator <> 1:
                    Result.append(C)
            continue
        if State == 5:
            #we are at first character after MetaEnd in singular mode
            if C == MetaEnd:
                #They want an actual MetaEnd in the text
                Result.append(MetaEnd)
                State = 2
            else:
                #we really are done
                if C == MetaBegin:
                    #but they just opened a new entry
                    State = 1
                else:
                    Result.append(C)
            continue
        if State == 6:
            #we are at first character after MetaEnd in plural mode
            if C == MetaEnd:
                #They want an actual MetaEnd in the text
                Result.append(MetaEnd)
                State = 4
            else:
                #we really are done
                if C == MetaBegin:
                    #but they just opened a new entry
                    State = 1
                else:
                    Result.append(C)
            continue
        raise Exception, 'Unhandled State: '+State
    Result = ''.join(Result)                                
    if ToPercent:
        Result = Result.replace(ToPercent,'%')
    return Result

def Cap(S):
    """=t
    Make sure the first letter of string S is upper case
    """
    if len(S) == 0 or S[0] == S[0].upper():
        result = S
    else:
        S = list(S)
        S[0] = S[0].upper()
        result = ''.join(S)
    return result    

def Cleave(S,Max):
    """=t
    Cleave a string into two parts, where the first part is no longer than Max.
    
    We attempt to break on space but will break arbitrarily if there is no space.
    
    The result is a tuple of the two pieces.
    
    If S is no longer then Length, then the result is "(S,'')"    
    """
    if len(S) <= Max:
        return (S,'')
    if S[Max] == ' ':
        #lucky break; a space just where we need it.
        return (S[:Max], S[Max+1:])
    #Not so lucky; search for a space
    BreakPoint = S[:Max].rfind(' ')
    if BreakPoint <> -1:
        #we found a space to break on
        return(S[:BreakPoint], S[BreakPoint+1:])
    #There is no space; do a mid-word break
    return (S[:Max], S[Max:])        

def WidgetInScreen(w):
    """=u
    Given a widget find out where it is on the screen.
    
    The result is a 4-element W,H,X,Y geometry list showing the widget's size and
        position WITH RESPECT TO THE SCREEN. 
    
    Note that plain old w.winfo_geometry() returns information
     with respect to the widgets parent.
    """
    X = 0
    Y = 0
    W, H = GeometryDecode(w.winfo_geometry())[0:2]
    while 1:
        Info = GeometryDecode(w.winfo_geometry())
        #print 'clas ',w.winfo_class()
        #print '---> ',Info
        X += Info[2]
        Y += Info[3]
        ParentName = w.winfo_parent()
        #print "PN= ",ParentName
        if w.winfo_class() in ('Toplevel', 'Tk'):
            #were at a top level window; done
            break
        # back up to parent of current widget
        w = w.nametowidget(ParentName)
    return (W,H,X,Y)    

def Grabber(Widget,Whine=0):
    """=u
    A persistent grabber
    
    For unknown reasons it sometimes takes awhile before the grab is successful;
        perhaps you have to wait until the window has finished appearing. In
        any case this persistent grabber loops for up to 0.3 seconds waiting for
        the grab to take before giving up.
    """
    for J in range(3):
        time.sleep(0.1)
        try:
            Widget.grab_set()
            return
        except TclError:
            pass
    if Whine:
        print 'Grab failed'        

class Searcher:
    """
    A class to facilitate simple searching.
    
    The concept is that you have a search string and you want to see if it matches a bunch
        of other strings. It works in two parts:
        
        o First you use "Parse" to parse the search string.
        o Then you use "Search" to see if the already parsed text matches a string.
        
    Search string rules. In the examples here the search string is shown inside angle
        brackets <like this>.
        
        o All comparisons are case insensitive.
        o To search for lines which contain all of a series to tokens, list the tokens 
              separated with spaces. <spam eggs> will match any line which contains both
              the word spam and and the word eggs.
        o To match an exact phrase including spaces put inside quotes. <"spam and eggs"> will
              only match a string which contains the exact phrase "spam and eggs". Quotes
              can be single or double, Python style.
        o You can combine the above two rules. <"spam and eggs" parrot> will only match a
              string which contains the exact phrase "spam and eggs" and which also contains
              the word "parrot".
        o To search for a series of alternatives use commas. <Spam, eggs, parrot> will match
             any string which contains the word "spam" or any string which contains the word
             "eggs" or any string which contains the word "parrot".                
    """
    
    def __init__(self):
        self.Pattern = []
        
    def Parse(self,Target):
        """
        Parse a string for later use with Search.
        
        We parse the string into self.Pattern which is a list. Each element of self.Pattern is
            a list of string.         
        """
        self.Pattern = []
        TokenList = []    
        ps = Enumerated('Idle InQuotes InText')
        State = ps.Idle
        Token = ''
        for C in Target.lower():
            if State == ps.Idle:
                if C in '"\'':
                    QuoteType = C
                    State = ps.InQuotes
                    Token = ''
                elif C == ',':
                    #Comma ends non-empty TokenList
                    if TokenList:
                        self.Pattern.append(TokenList)
                        TokenList = []
                elif C <> ' ':
                    #Anything but space initiates a token
                    Token = C
                    State = ps.InText
                else:
                    #Ignore spaces here
                    pass    
            elif State == ps.InQuotes:
                if C == QuoteType:
                    #End of quotes, end of token
                    if Token:
                        TokenList.append(Token)
                    State=ps.Idle    
                else:
                    #Continue accumulating quoted token
                    Token += C
            elif State == ps.InText:
                if C == ' ':
                    #Space ends token        
                    if Token:
                        TokenList.append(Token)
                    State=ps.Idle    
                elif C == ',':
                    #Comma ends Token and ends TokenList
                    if Token:
                        TokenList.append(Token)
                    self.Pattern.append(TokenList)
                    TokenList = []
                    State = ps.Idle
                else:
                    Token += C
            else:
                raise Exception, 'InvalidState'
        if Token:
            TokenList.append(Token)
            self.Pattern.append(TokenList)

    def Search(self,Line):
        """
        See if Line matches the already parsed string.
        
        The result is 1 if we have a match or 0 if not. If no string has already been
            paresed then there is no match.
        """
        Line = Line.lower()
        for TokenList in self.Pattern:
            for Token in TokenList:
                if Line.find(Token) == -1:
                    break
            else:        
                #All Tokens in this TokenList matched
                return 1
        return 0            

class Enumerated:
    """=u
    Create an object of enumerated names.
    
    Example:
        "Baffy = Enumerated('Yada Zot Wow')"
        
        Returns an an object "Baffy" with three attributes ("Baffy.Yada", "Baffy.Zot"
            and "Baffy.Wow") all of which have unique arbitrary values.
            
        Further, ALL attributes in all instances of this class will have unique
            values.    
            
        Use the "Decode" method to convert an enumerated attbibute value back to
            its original name. Following the example above:
            
            "print Baffy.Decode(Baffy.Zot)"
            
        Will print "Zot". This example is trivial. The "Decode" method is rather more useful
            in situations where you have a variable which has been assigned an enumerated
            attribute and you would like to find the *name* of the corresponding attribute.        
    """    
    V = 0
    DecodeList = []
    def __init__(self,Namelist):
        for T in Namelist.split():
            self.__dict__[T] = Enumerated.V
            Enumerated.DecodeList.append(T)
            Enumerated.V += 1
            
    def Decode(self,Attribute):
        try:
            return Enumerated.DecodeList[Attribute]
        except "banana":
            return 'Argument "%s" is not a valid Enumerated attribute'%Attribute    

def ExtArb(Filename,Extension):
    """=u
    Transplant an arbitrary extension onto a filename.
    
    Given any path/filename, shoot off any existing extension and append
        the specified extension.
        
    If "Extension" doesn't start with a dot then one is supplied.    
    """    
    Root, Ext = os.path.splitext(Filename)
    if Extension[:1] <> '.':
        Extension = '.' + Extension
    return Root + Extension    

def GeneralizedSaveFinalize(Path):
    """=u
    A safe way to finish a save.
    
    o Path is the full path name to the file which is being replaced, complete with
        appropriate extension; this file doesn't necessarily have to exist.
        For example, if saving a text file Path might be "/home/cam/text/whatever.txt"

    o Prior to calling this routine you must have written the new version of the file
        with the same name but an extension of "$$$". Continuing our example above, the
        new version file would be "/home/cam/text/whatever.$$$"

    o This routine:
        o Deletes any old backup file (eg "/home/cam/text/whatever.bak").
        o Renames the current file to be of extension ".bak".
        o Renames the "$$$" file to be of the standard extension (eg "txt").
    """
    BasePath,StandardExtension = os.path.splitext(Path)
    #toast the old backup file
    try:
        os.remove(BasePath + '.bak')
    except OSError:
        #in case there is no backup file
        pass
    #rename the old file to be the backup file
    try:
        os.rename(Path,BasePath+'.bak')
    except OSError:
        #no original file
        pass
    #rename the new file to be the current file
    os.rename(BasePath+'.$$$',Path)

def TextWrap(Text,MaxWidth):
    """=t
    Wrap a text string to a specified width.
    
    Text is a string of arbitrary length which may already contain newlines.
    
    The result is a list of strings, each of which is no longer than MaxWid.
    
    This routine trys to break on SPACE but will break in mid-word if no space
     is available
    """
    Result = []
    T = Text.split('\n')
    for Text in T:    
        I = 0 #index of first character in Text not yet processed
        while (I+MaxWidth) < len(Text):
            Chunk = Text[I:I+MaxWidth]
            if Text[I+MaxWidth] == ' ':
                #there is a break just following our chunk
                BreakPoint = MaxWidth
                DropCount = 1
            else:
                #we need to look for a breakpoint in our chunk
                BreakPoint = Chunk.rfind(' ')
                DropCount = 1
                if BreakPoint == -1:
                    #no natural breakpoint find; break in mid-word
                    BreakPoint = MaxWidth
                    DropCount = 0
            Result.append(Text[I:I+BreakPoint])
            I = I + BreakPoint + DropCount
        Result.append(Text[I:])
    return Result        

def TextBreak(Text,MaxWidth,Glue='\n'):
    """=t
    Similar to TextWrap but returns a single string with embedded newlines.
    """
    return Glue.join(TextWrap(Text,MaxWidth))

class PromptDialog:
    """=d
    A simple dialog to prompt for a string value.
    
    "Title" is the title for the window.
    
    "Message" is the instruction to the user.
    
    "Prompt" is the initial value. If omitted, the Entry is initially blank.

    The result is returned as "self.Result".
    
    If the user cancels or exits by clicking on the window manager "close" button, then
        we return "None".
        
    If "Help" isn't "None" then it must be a tuli giving:
        [0] The object to be called to serve help.
        [1] The help topic index to be passed to the above object.            
        
    Pressing the "Enter" key has the same effect as clicking "OK".
    Pressing the "Esc" key has the same effect as clicking "Cancel".    
    """
    def  __init__(self,Title='Query',Message='Message',Help=None,Prompt=''):
        """
        create the dialog.
        """
        self._Win = Toplevel()
        self._Win.title(Title)
        self.Result = None
        self.Help = Help
        Width = 300
        Height = 150
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
        self.LabelStringVar.set(TextBreak(str(Message),34))    
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
        self.Buttons = ButtonBox(self._Win)
        self.Buttons.add('OK',command=self.on_OK)
        if Help <> None:
            self.Buttons.add('Help',command=self.on_Help)
        self.Buttons.add('Cancel',command=self.on_Cancel)
        self.Buttons.pack(side=TOP)
        #
        #be modal
        #
        self._Win.focus_set()
        Grabber(self._Win)
        self.OurEntry.focus_set()
        self._Win.wait_window()
        
    def on_OK(self,Event=None):
        self.Result = self.OurEntry.get()
        self._Win.destroy()

    def on_Cancel(self,Event=None):
        self._Win.destroy()        
        
    def on_Help(self,Event=None):
        self.Help[0](self.Help[1])        
        

class HelpCompiler:
    """
    This class is for authoring the help messages.
    
    This Help compiler is for authoring help messages. We should 
        be able to omit it and still have the end-user help function properly.
        Actual end-user help is provided by "TheHelpThingy", below.
        
    Help information keyed in by a help author is of the following format:
    
     o If the first line is of the form "><topic ID>" (ie a greater-than sign
       followed by a topic-ID) then this topic is redirected to the specified
       ID and the lines of text following the first line are ignored. See also
       the note below about argument replacement in redirection. If the first 
       line isn't a redirection then the topic text must be in the following 
       format: 
    
     o Zero or more lines of the form "!<abstract text>". Abstract text is used
       to build the topic list the user can choose from. It should be a short
       phrase describing the content of the this topic.
       
     o Zero or more lines of the form "&<hotlink> [&<hotlink...]". The hotlink
       text runs to the next "&" or end-of-line, whichever comes first. Hotlink
       references on other pages will link to this topic. 

     o Zero or more lines of the form "#<comment text>". These are simply comments 
       where help authors can make notes to themselves.
       
     o Zero or one line of the form "[<list of integers>]. This is the pluralization
       list and each items selects one item from the argument list passed to the
       topic at render time.       
      
     o Zero or more lines of text to be presented to the user.
    
    Technically Abstracts, Hotlinks and Comments are supposed to appear in that
        order. Somewhat less technically you can mix and match those three types
        of lines without any problem. They will be sorted into official order
        when saved and reloded. However, the redirect line, if given, really
        does have to be the first line and the text to be formatted really does
        have to come AFTER any of the other line types.
        
    Within text there are these format controls:
    
        o "{B<text>}"    bold text ;
        o "{I<text>}"    italic text 
        o "{H<text>}"    heading text
        o "{F<text>}"    fixed pitch text
        o "{G<text>}"    fixed pitch bold text
        
    To create a hyperlink to another topic:
        "{L<text to show user>=<TopicID>}"

    The code letter after the left-brace in text format and link specifiers is
        case insensitive.
        
    Hotlinks to other pages are coded as "&<Hotlink text>". The Hotlink text *is*
        what the user sees and it must correspond to a hotlink defined in some
        help topic. 
        
    Note that hotlinks are self closing, that is, no trailing delimiter is 
        needed; the hotlink ends when it matches an existing defined hotlink 
        value. This is a good news/bad news proposition.
        
        o The good news is that no trailing delimiter is required, making it
          easy and convenient to inject hotlinks into the text. The whole point
          of hotlinks is easy and convenient.
          
        o The bad news is that it places limits on hotlink names. You can't, for
          example, have hot links named 'banana' and 'ban' because as soon as
          you enter "&ban" it matches "ban" and the hot link ends. Solution?
          Don't do that.
          
        o The other bad news is that if you mis-spell a hot link it could 
          potentially go on for the rest of your text. To prevent this, we place
          an upper limit of 40 characters on the length of a hotlink.
          
    Both Hotlinks and the TopicID of links are *CASE INSENSITIVE.*          
    
    This is SIMPLE formatting not HTML; you can't embed any of the above items inside
        each other.

    *Indented lists*
    
    You can create bulleted, numerated and indentet lists using:
    
        o "o Yadayadayada" for bulleted lists
        o "n Yadayadayada" for numerated lists
        o "t Yadayadayada" for indented lists
        
    Note that text following the 'indicator character' should be indented below the text
        following the indicator character as long as it is part of the list. Bulleted lists
        are presumably obvious, numerated lists are like bulleted lists but you automaticallly
        get ascending numbers for each point within a single list and indented lists are just
        like bulleted lists but without the bullet character.
        
    *Redirection and agrument replacement.*
    
     The full form of the redirection line 
        (which must be the first line in the unformatted text) is:
        
        "><targettopic> [<arguments>]"
        
        Arguments are optional, but if present they must be quoted and, if there
            is more than one argument, comma separated. The following are some example
            valid redirection lines:
            
            >baffy
            >baffy 'Zap'
            >baffy 'Hello, I am argument zero', 'This is argument one'
            
    all of which redirect to topic 'baffy' and with varying numbers of arguments.
        The arguments MUST be quoted, but the quotes can be single or double (Python
        style). 
            
    In the topic which is the target of a redirection, you can access the arguments
        as "@0, @1" and so on up to "@9". You can access, at most, 10 arguments.
        When rendered in the help area the argument designator (eg "@0") is replaced
        by the text of the corresponding argument. In there is no corresponding
        argument then they are considered to be empty. An at-sign followed by anything
        other than a digit is treated at face value. If you need to put an actual
        instance of an at-sign followed by a digit in the text, then use two
        at-signs: enter "@@5" to see "@5" in the final text.
        
    """
    def __init__(self,Help,Top=None):
        """
        Start the help compiler
        
        "self.TabInfo" is a list of dictionary used to keep track of the 8 edit
            tabs. Each entry pertains to one tab, and is a dictionary:
            o "['ID']" The topic ID of the topic currently in this edit tab. Empty if the
                   tab doesn't yet exist.
            o "['LastUsed']" The time, as a string, when this topic was last selected.
                   empty if this tab doesn't exist yet.
            o "['Label']" The Label widget at the top of the page used to display the
                topic ID.
            o "['Edit']" The upper Tkinter Text widget in which the help author edits the
                raw help message text.
            o "['View']" The lower Tkinter Text widget in which the help author views the
                formatted help message.    
            o "['NeedsRefresh']" If true, then the next time this tab is selected as the current
                tab, we refresh the content of it's Edit from Topics. Normally the content
                of Edit is current with Topics. This flag is needed for the case where some
                the Topics content changes (eg some other topic was renamed and references
                to that topic in the current page were updated) and that needs to be reflected
                in Edit before the user goes editing.
        """
        if Help.Topics == None:
            #oh-oh - the help thingy didn't start well
            print "Help had problems starting - can't open compiler."
            return
        self.Help = Help
        self.CurrentTabPage = None

        
        self.EditTabCount = 8 #we create this many edit tabs
        # Create out work area
        if Top == None:
            #we must create our own top-level window
            self.Win = Toplevel()
        else:
            #the caller gave us a top-level window
            self.Win = Top
        #We open at full screen width and 90% of screen height    
        Width = self.Win.winfo_screenwidth()
        Height = int(self.Win.winfo_screenheight() * 0.9)
        self.Win.geometry('%sx%s+0+20'%(Width,Height))
        self.Win.title(' Help Compiler ')

        #Set the font used for unformatted text and measure the actual size of the
        #    font we got
        self.EditFont = ('courier','-14')
        TempFont = tkFont.Font(self.Win,self.EditFont)
        self.EditFontWidth = TempFont.measure('a')
        self.VScrollbarSize = None
        #The font we use in the view area.
        self.ViewFont = self.Help.FontNormal

        #Create the list that holds information about the edit tabs
        self.TabInfo = []
        for J in range(self.EditTabCount):
            self.TabInfo.append({'ID':'','LastUsed':'','NeedsRefresh':0})
        #
        # Listbox for Help topic ID's
        #
        
        self.IDBox = ScrolledListbox(self.Win,label='Help ID',width=30)    
        self.IDBox.FetchWidget().bind('<Double-ButtonPress-1>',self.on_IDBox)
        
        self.IDBox.pack(side=LEFT,fill=Y,anchor=W)    
        self.IDBoxUpdate()
        #
        # Frame for page name and hotlinks
        #
        self.OurFrame = Frame(self.Win)
        self.OurFrame.pack(side=LEFT,fill=Y)
        #
        # Listbox for page names
        #
        Label(self.OurFrame,text='Topics in tabs').pack(side=TOP)
        self.TabBox = Listbox(self.OurFrame,height=self.EditTabCount,width=25)
        self.TabBox.pack(side=TOP,fill=Y,anchor=W)
        self.TabBoxUpdate()
        self.TabBox.bind('<Double-Button-1>',self.on_TabBox)
        #
        # Listbox for hotlink values
        #
        Temp = self.Help.Hotlinks.keys()
        Temp.sort()
            
        self.HotBox = ScrolledListbox(self.OurFrame,label='Hotlinks',width=25)
        self.HotBox.setlist(Temp)
        self.HotBox.bind('<Double-Button-1>',self.on_HotBox)
        self.HotBox.pack(side=TOP,fill=Y,anchor=W,expand=YES)    
        #
        # Buttons above the edit area
        #
        self.Buttons = ButtonBox(self.Win,padx=0)
        B = self.Buttons.add('Vu',command=self.on_View)
        HintHandler(B,'View the formatted version of the current topic')

        B = self.Buttons.add('Tdy',command=self.on_Tidy)
        HintHandler(B,'Tidy the unformatted text')

        B = self.Buttons.add('Bk',command=self.on_Back)
        HintHandler(B,'View the previous help topic')
        B['state'] = DISABLED
        self.BackButton = B

        B = self.Buttons.add('Nu', command=self.on_Create)
        HintHandler(B,'Create a new help topic')

        B = self.Buttons.add('Ren',command=self.on_Rename)
        HintHandler(B,'Rename the current help topic')

        B = self.Buttons.add('Del',command=self.on_Delete)
        HintHandler(B,'Delete the current help topic')
        
        B = self.Buttons.add('Mv',command=self.on_HotlinkMove)
        HintHandler(B,'Move a hotlink to a different topic')

        B = self.Buttons.add('Lnk',command=self.on_Links)
        HintHandler(B,'Show who links to the current help topic')

        B = self.Buttons.add('Wip',command=self.on_Wip)
        HintHandler(B,'Toggle WorkInProgress status')
        
        #B = self.Buttons.add('Debug',command=self.on_Debug)
        self.Buttons.add('Xit',command=self.on_Quit)
        self.Buttons.pack(side=TOP,fill=X)
        #
        # Notebook to hold edit pages
        #
        self.Notebook = NoteBook(self.Win,RaiseCommand=self.on_PageRaised
            ,LowerCommand=self.on_PageLowered)
        self.Notebook.pack(side=TOP,expand=YES,fill=BOTH)

        #This is used for the Back function
        self.Backlist = []

    def on_Debug(self):
        print 40*'-'
        print 'CurrentTabPage=%s'%self.CurrentTabPage
        print 40*'-'

    def on_Wip(self):
        """
        Toggle the WorkInProgress status of the current topic.
        """
        if self.CurrentTabPage == None:
            MessageDialog(Message='No topic is currently selected')
            return
        CurTopic = self.Help.Topics[self.TabInfo[self.CurrentTabPage]['ID']]
        CurTopic['Wip'] ^= 1
        self.SetTabLabel()
        TopicName = self.TabInfo[self.CurrentTabPage]['ID']
        Index = self.LocateInListbox(TopicName,self.IDBox.FetchWidget())
        self.IDBoxUpdate(Index)

    def on_Back(self):
        """
        Used asked to view the previous topic        
        """
        if self.Backlist:
            self.Backlist.pop()
            if self.Backlist:
                self.NowEdit(self.Backlist[-1])
        if len(self.Backlist) < 2:
            self.BackButton['state'] = DISABLED    

    def on_Links(self):
        """
        User wants to see who links to us.
        """
        if self.CurrentTabPage == None:
            MessageDialog(Message='No help topic is selected')
            return
        Info = self.TabInfo[self.CurrentTabPage]
        TopicID = Info['ID']
        Info['View'].delete("1.0",END)
        #In Refs, each key is either: a) the topic ID of the current page, or
        #    b) a hotlink which is defined on the current page. Each value
        #    is a list of TopicID's in which there is a reference to the
        #    key link/hotlink.
        Refs = {}
        #Scan for links
        for T in self.Help.Topics.keys():
            #T is the TopicID of the page were currently checking
            if T <> TopicID: #don't check ourself
                #Check for links that point to this page
                Links = self.LinksExtract(T)
                for L in Links:
                    #L is a hotlink or link target mentioned in page T
                    if L[0] == '&':
                        #L is a hotlink
                        Hotlink = L[1:]
                        if self.Help.Hotlinks[Hotlink] == TopicID:
                            #this hotlink refers to us
                            if not Refs.has_key(L):
                                Refs[L] = []
                            Refs[L].append(T)
                    elif L[0] == '=':
                        #L is a link
                        Link = L[1:]
                        if Link == TopicID:
                            #this link points to us
                            if not Refs.has_key(L):
                                Refs[L] = []
                            Refs[L].append(T)
        #Report to the user in the view area
        Names = Refs.keys()
        Names.sort()
        Count = 0
        for Name in Names:
            if Refs[Name]:
                Info['View'].insert(INSERT,'%s\n'%Name)
                Temp = Refs[Name]
                Temp.sort()
                for ID in Temp:
                    Info['View'].insert(INSERT,'    %s\n'%ID)
                    Count += 1
        Info['View'].insert(INSERT,'----- %s references total -----\n\n'% Count)
        #Report statistics
        T = self.StatsGen()
        T['Total'] = T['Wip'] + T['Comp'] + T['ReWip'] + T['ReComp']
        T['TotalWip'] = T['Wip'] + T['ReWip']
        T['TotalComp'] = T['Comp'] + T['ReComp']
        T['TotalRe'] = T['ReWip'] + T['ReComp']
        T['TotalNonRe'] = T['Wip'] + T['Comp']
        
        L = (('Total','Total topics')
            ,('','')
            ,('TotalWip','Total work-in-progress topics')
            ,('TotalComp','Total complete topics')
            ,('TotalRe','Total redirected topics')
            ,('TotalNonRe','Total non-redirected topics')
            ,('','')
            ,('Wip','Non-redirected work-in-progress topics')  
            ,('Comp','Non-redirected complete topics')
            ,('ReWip','Redirected work-in-progress topics')
            ,('ReComp','Redirected complete topics')
            ,('','')
            ,('Hotlinks','Hotlinks defined')
            ,('Refs','Ordinary references')
            ,('Hotrefs','Hotlink references'))
        for Key,Title in L:
            if Key == '':
                Info['View'].insert(INSERT,'\n')
            else:
                Info['View'].insert(INSERT,'%4d %s\n'%(T[Key], Title))
        
    def on_TabBox(self,Event):
        """
        User double clicked on an entry in the Tab listbox
        """
        T = self.TabBox.curselection()
        if T:
            T = int(T[0])
            ID = self.TabInfo[T]['ID']
            if ID <> '' and ID <> '<none>':
                self.NowEdit(ID)

    def Lift(self):
        """
        Call this to raise the compiler toplevel so it's visible.
        """
        self.Win.lift()

    def on_HotlinkMove(self):
        """
        User wants to move a hotlink to a different topic.
        """
        if self.CurrentTabPage == None:
            MessageDialog(Message='No topic is currently selected')
            return
        CurrentTopicID = self.TabInfo[self.CurrentTabPage]['ID']
        CurrentTopic = self.Help.Topics[CurrentTopicID]
        if len(CurrentTopic['Hotlinks']) == 0:
            MessageDialog(Message='The current topic has no hotlinks to move')
            return
        Hot = CurrentTopic['Hotlinks'][0]    
        while 1:    
            Hot = PromptDialog(Message='Name of hotlink to be moved'
                ,Title='Move Hotlink'
                ,Prompt=Hot).Result
            if Hot == None:
                return
            if Hot in CurrentTopic['Hotlinks']:
                break
            MessageDialog(Message='There is no hotlink named "%s" in the current ' \
                'topic. Please enter the name of a hotlink in the current topic or ' \
                'cancel.'%Hot)
        Target = ''
        while 1:        
            Target = PromptDialog(Message='Name of topic to receive hotline "%s"'%Hot
                ,Title='Move Hotlink'
                ,Prompt=Target).Result
            if Target == None:
                return
            if Target == CurrentTopicID:
                MessageDialog(Message='"%s" is the current topic. Please choose a ' \
                    'different topic or cancel.'%Target)
                Target = ''
                continue
            if Target in self.Help.Topics.keys():
                break
            MessageDialog(Message='There is no topic named "%s". '\
                'Please enter the name a valid topic or ' \
                'cancel.'%Target)
        #Delete the link from the current topic
        I = CurrentTopic['Hotlinks'].index(Hot)
        del CurrentTopic['Hotlinks'][I]
        #Update the display of the current topic
        self.TopicToEdit(CurrentTopicID,self.TabInfo[self.CurrentTabPage]['Edit'])
        #And add it to the target topic
        self.Help.Topics[Target]['Hotlinks'].append(Hot)        
        #If the target is in a tab, then we should refresh if on next visit.
        self.MarkNeedsRefresh(Target)
        #Update the entry in the hotlinks table
        self.Help.Hotlinks[Hot] = Target

    def on_Rename(self):
        """
        User asked to rename the current topic.
        """
        if self.CurrentTabPage == None:
            MessageDialog(Message='No topic is currently selected')
            return
        CurrentTopicID = self.TabInfo[self.CurrentTabPage]['ID']
        CurrentTopic = self.Help.Topics[CurrentTopicID]
        # Get the proposed name
        NewID = PromptDialog(Message='The present id is "%s". Enter the new ID:'%CurrentTopicID
            ,Prompt=CurrentTopicID).Result
        if NewID <> None:
            NewID = NewID.lower()
            if self.Help.Topics.has_key(NewID):
                #That topic already exists
                MessageDialog(Message='A help topic with the ID "%s" already exists'%NewID)
            else:
                #Adjust links in other pages to use the new name
                OldText = '=%s}'%CurrentTopicID
                NewText = '=%s}'%NewID
                Count = 0
                for ID in self.Help.Topics.keys():
                    #ID is the HelpTopic we are currently checking for links to the renamed page
                    for Link in self.LinksExtract(ID):
                        if Link[0] == '=' and Link[1:] == CurrentTopicID:
                            #There is at least one link to us in this page; revise it
                            self.Help.Topics[ID]['Text'] = self.Help.Topics[ID]['Text'].replace(OldText,NewText)
                            Count += 1
                            #If this page is in a tab it will need refreshing
                            self.MarkNeedsRefresh(ID)
                #Create an entry with the new name
                self.Help.Topics[NewID] = self.Help.Topics[CurrentTopicID]
                #And toast the original entry
                del self.Help.Topics[CurrentTopicID]            
                #Reflect the changed name in TabInfo,
                self.TabInfo[self.CurrentTabPage]['ID'] = NewID
                #And in the edit tab label,
                self.SetTabLabel()
                #And in the topic listbox and tab listbox
                self.IDBoxUpdate()    
                self.TabBoxUpdate()
                #Reassure user
                Msg=Plural('The name has been changed and %s referring page{/s} {has/have} ' 
                    'been updated.',Count)            
                MessageDialog(Message=Msg)    

    def on_Delete(self):
        """
        User asked to delete current topic.
        """
        if self.CurrentTabPage == None:
            MessageDialog(Message='No topic is currently selected')
            return
        CurrentTopicID = self.TabInfo[self.CurrentTabPage]['ID']
        if CurrentTopicID == '<none>':
            MessageDialog(Message='No topic is currently selected.')
            return
        CurrentTopic = self.Help.Topics[CurrentTopicID]
        #
        # Check for links to this page
        #
        #print 'CurrentTab=',self.CurrentTabPage
        #print 'Current=',CurrentTopicID
        for ID in self.Help.Topics.keys():
            if ID <> CurrentTopicID:
                for Link in self.LinksExtract(ID):
                    if Link[0] == '=' and Link[1:] == CurrentTopicID:
                        Msg = 'Can\'t delete current topic ("%s") because it is the target of a link '\
                            'in topic "%s"'%(CurrentTopicID,ID)
                        MessageDialog(Message=Msg)
                        return
                    elif Link[0] == '&' and Link[1:] in CurrentTopic['Hotlinks']:
                        Msg = 'Can\'t delete current topic ("%s") because it is the target of hotlink '\
                            '"%s" in topic "%s"'%(CurrentTopicID, Link, ID)
                        MessageDialog(Message=Msg)
                        return
        #
        # Get confirmation from user
        #                
        Msg = 'Permanently delete topic "%s" now?'%CurrentTopicID
        R = MessageDialog(Message=Msg,Buttons=(('No',0),('Yes',1))).Result
        if R == 1:
            #Note which line of the TopicID list box is selected so we can keep
            #    if from jumping around too much
            SelectedLine = self.IDBox.FetchWidget().curselection()
            if len(SelectedLine) == 0:
                SelectedLine = 0
            else:
                SelectedLine = int(SelectedLine[0])
            #Delete the topic from out master list        
            del self.Help.Topics[CurrentTopicID]
            #Reflect the change on the screen
            self.IDBoxUpdate(SelectedLine)
            self.Help.HotlinksUpdate()
            self.HotboxUpdate()
            #Free up the edit page    
            Tab = self.TabInfo[self.CurrentTabPage]
            #ThePage = self.Notebook.page(self.CurrentTabPage)        
            Tab['Edit'].delete("1.0",END)
            Tab['View'].delete("1.0",END)
            Tab['LastUsed'] = 1.0
            Tab['ID'] = '<none>'
            Tab['Label']['text'] = '<none>'
            self.TabBoxUpdate()


    def on_PageRaised(self,PageName):
        """
        An edit page is being made current
        """
        if self.CurrentTabPage <> None and not self.TabInfo[self.CurrentTabPage]['ID'] == PageName:
            #We don't already know about it
            self.CurrentTabPage = int(PageName)
        Tab = self.TabInfo[self.CurrentTabPage]    
        self.NoteIDVisited(Tab['ID'])
        if Tab['NeedsRefresh']:
            #Unformatted text was changed; refresh it; last arg says to tidy unles its the substitutions pate
            self.TopicToEdit(Tab['ID'],Tab['Edit'],PageName<>SubPage)
            Tab['NeedsRefresh'] = 0
        
    def on_PageLowered(self,PageIndex):
        """
        An edit page is being made not-current
        """
        #ThePage = self.Notebook.page(PageIndex)
        Tab = self.TabInfo[int(PageIndex)]
        TheText = Tab['Edit'].get('1.0',END)
        TopicID = Tab['ID']
        if TopicID == '' or TopicID == '<none>':
            #Page contains no topic
            return 1
        R = self.TopicUpdate(TopicID, TheText)
        if R <> 1:
            Msg = 'Error: %s'%R
            MessageDialog(Message=Msg)
            #Ok. At this point we would really like to cancel the changing of edit
            #    pages because the current one contains an error. However, we really
            #    are not in control of the process and it rather carries on whether
            #    we like it or not. Therefore we invoke "after" to select the page
            #    we want at some short time in the future AFTER the process of
            #    selecting the wrong page has completed. Is that clear?
            self.Notebook.after(500,self.NowEdit,TopicID)        
        return 1

    def on_Create(self):
        """
        User asked to create a new topic.
        """
        ID = PromptDialog(Message='Enter the ID for the new topic to be created:').Result
        if ID <> None:
            ID = ID.lower()
            if self.Help.Topics.has_key(ID):
                #That topic already exists
                MessageDialog(Message='A help topic with the ID "%s" already exists'%ID)
            else:
                #Create the empty topic
                self.Help.Topics[ID] = {'Abstracts':[], 'Hotlinks':[], 'Comments':[], 'Plurals':[], 'Text':'', 'Wip':1}
                #Show it in the topic list
                self.IDBoxUpdate()
                Index = self.LocateInListbox(ID,self.IDBox.FetchWidget())
                self.IDBoxUpdate(Index)
            #in either case, put the topic in an edit tab
            self.NowEdit(ID)        

    def on_Quit(self):
        """
        Save and exit
        """
        #Update main dictionary from edit tabs
        for J in range(self.EditTabCount):
            if self.TabInfo[J]['ID']:
                Tab = self.TabInfo[J]
                TheText = Tab['Edit'].get('1.0',END)
                TheID = Tab['ID']
                R = self.TopicUpdate(TheID, TheText)
                if R <> 1:
                    self.Notebook.selectpage(J)
                    Msg = 'Error: %s'%R
                    MessageDialog(Message=Msg)
                    return
        #Save main dictionary to disk            
        self.Help.Save()                    
        self.Win.destroy()

    def on_Tidy(self):
        """
        Rewidth the text in the Edit area.
        """
        if self.CurrentTabPage <> None:
            self.Notebook.selectpage(self.CurrentTabPage)
            Tab = self.TabInfo[self.CurrentTabPage]
            if Tab['ID'] == '<none>':
                #This tab was vacated
                return
            #Extract text from the Text widget and attempt to update Topics with it
            TheText = Tab['Edit'].get('1.0',END)
            TheID = Tab['ID']
            R = self.TopicUpdate(TheID, TheText)
            if R <> 1:
                #The update didn't go well; whine to user
                Msg = 'Error: %s'%R
                MessageDialog(Message=Msg)
                return
            WidthInChars = self.TextWidthInChars(Tab['Edit'],self.EditFontWidth)
            New = self.Rewidth(self.Help.Topics[TheID]['Text'],WidthInChars).Result
            self.Help.Topics[TheID]['Text'] = New
            self.TopicToEdit(TheID,Tab['Edit'])
            #Regenerate the scrollbards so an unnecessary horizontal scrollbar will go away.
            Tab['Edit'].Rebar()

    def on_View(self):
        """
        User has asked to see the formatted verions of our text.
        """
        if self.CurrentTabPage <> None:
            self.Notebook.selectpage(self.CurrentTabPage)
            Tab = self.TabInfo[self.CurrentTabPage]
            if Tab['ID'] == '<none>':
                #This tab was vacated
                return
            TheView = Tab['View']
            #Here we find the index of the line of text which is presently in the
            #    middle of the View area. After we have rendered the text onto
            #    the view area we ask for this line to be in the visible area.
            #    The net effect is that the text widget will center the specified
            #    line on the screen unless it was already visiblle. The point of
            #    this is to keep approximately the same test visible when you
            #    press the VIEW button. If we don't do this, then every time you
            #    press VIEW, you snap to the top of the formatted text.
            MiddleIndex = TheView.index('@0,%s'%(TheView.winfo_height()/2))
            #Extract text from the Text widget and attempt to update Topics with it
            TheText = Tab['Edit'].get('1.0',END)
            TheID = Tab['ID']
            R = self.TopicUpdate(TheID, TheText)
            if R <> 1:
                #The update didn't go well; whine to user
                Msg = 'Error: %s'%R
                MessageDialog(Message=Msg)
            else:   
                #The update went ok 
                self.Help.Save()
                #Process any possible redirection
                R = self.Help.Redirector(TheID)
                if R == None:
                    #Redirection failed, user already notified, nothing further to do
                    pass
                else:    
                    NewID, TheText, ArgumentList = R
                    #print 'R=%s'%str(R)
                    if NewID == TheID:
                        #no redirection happened. Rendering without ArgumentList causes
                        #    any instances of @n to be rendered as such. If we passed an
                        #    empty argument list then they would be rendered as empty
                        #    strings, which makes them rather harder to spot in the
                        #    rendered text.
                        L = self.Help.Render(TheView,TheText,self.Help.Topics)
                        #Update our links record per links found by render
                        self.Help.Topics[TheID]['Links'] = L
                    else:    
                        #we were redirected
                        L = self.Help.Render(TheView,TheText,self.Help.Topics,ArgumentList)
                        self.Help.Topics[NewID]['Links'] = L
                    #Put us back in the approximate spot in the text from which we started
                    Tab['View'].see(MiddleIndex)

    def on_HotBox(self,Event=None):
        """
        User double clicked on a line in the Hotlink listbox
        """
        Hotlink = self.HotBox.getcurselection()[0]
        ID = self.Help.Hotlinks[Hotlink]
        self.NowEdit(ID)

    def on_IDBox(self,Event=None):
        """
        User double clicked on a line in the Topic ID listbox
        """
        Temp = self.IDBox.FetchWidget().curselection()
        Temp = int(Temp[0])
        Topic = self.IDBoxContent[Temp]
        self.NowEdit(Topic)

    def on_EditReturn(self,Event):
        """
        User pressed Enter in an edit Text.
        
        We position the cursor under the first non-blank character of the
            previous line. It is important that this be bound to KeyRelease
            so we get control AFTER the Text widget has inserted the newline
            and moved the cursor.
        """
        Text = Event.widget
        Temp = Text.index(INSERT)
        if Temp <> '':
            Temp = self.IndexToList(Temp)
            #fetch the previous line
            PrevLine = Text.get('%s.0'%(Temp[0]-1),'%s.end'%(Temp[0]-1))
            Count = 0
            for C in PrevLine:
                if C <> ' ':
                    break
                Count += 1
            if Count:
                #insert spaces if required
                Text.insert(INSERT,''+(' '*Count))

    def MarkNeedsRefresh(self,HelpTopicID):
        """
        If the specified ID is in a tab, mark it as needing refresh.
        """
        for J in range(self.EditTabCount):
            if self.TabInfo[J]['ID'] == HelpTopicID:
                self.TabInfo[J]['NeedsRefresh'] = 1

    def IndexToList(self,Index):
        """
        Convert a "line.column" Text widget index to a Python numeric list [line,column]
        """
        T = Index.split('.')
        return [int(T[0]), int(T[1])]
        
    def NoteIDVisited(self,ID):
        """
        Note that a particular Topic has been visited.
        
        But don't create duplicate consecutive entries.
        """
        assert type(ID) == type('')
        if self.Backlist==[] or self.Backlist[-1] <> ID:
            self.Backlist.append(ID)
            if len(self.Backlist) > 1:
                self.BackButton['state'] = NORMAL
        #print self.Backlist        

    def TopicToTabNumber(self,TopicID):
        """
        Given a topic ID return the corresponding notebook tab number.
        
        If the ID doesn't correspond to any tab, we return None
        """
        for J in range(self.EditTabCount):
            if self.TabInfo[J]['ID'] == TopicID:
                return J
        return None

    def StatsGen(self):
        """
        Return a dictionary of statistics about the help topics.
        
        The result contains the following, all integers:
            o "['Wip']" The number of non-redirecxted work-in-progress topics.
            o "['Comp']" The number of complete topics.
            o "['ReWip']" The number of redirected work-in-progress topics.
            o "['ReComp']" The number of redirected complete topics.
            o "['Hotlinks']" The number of hotlinks defined.
            o "['Refs']" Then number of references (links) to topics.
            o "['Hotrefs']" The number of references to hotlinks.
        """
        Result = {'Wip':0, 'ReWip':0, 'Comp':0, 'ReComp':0, 'Hotlinks':0
            ,'Refs':0, 'Hotrefs':0}
        for ID in self.Help.Topics.keys():
            Entry = self.Help.Topics[ID]
            if Entry['Wip']:
                if Entry['Text'][:1] == '>':
                    Result['ReWip'] += 1
                else:    
                    Result['Wip'] += 1
            else:
                if Entry['Text'][:1] == '>':
                    Result['ReComp'] += 1
                else:    
                    Result['Comp'] += 1
            Result['Hotlinks'] += len(Entry['Hotlinks'])                    
            for Link in Entry['Links']:
                if Link[0] == '&':
                    Result['Hotrefs'] += 1
                elif Link[0] == '=':
                    Result['Refs'] += 1
                else:
                    raise Exception, 'Unknown link type: '+Link
        return Result

    def TabBoxUpdate(self):
        """
        Refresh the list of topics in the Tab listbox
        """
        self.TabBox.delete(0,self.EditTabCount-1)
        for J in range(self.EditTabCount):
            self.TabBox.insert(END,'%s: %s'%(J,self.TabInfo[J]['ID']))

    def IDBoxUpdate(self,Select=None):
        """
        Refresh the list of help topic ID in the ID listbox.
        
        Select controls what we do with selection:
            None: We do nothing.
            int:  If an integer, we select and make visible the entry specified
                by the integer.
        """
        Temp = self.Help.Topics.keys()
        Temp.sort()
        #Save the actual help topic ID's before we muck them up
        #   with indicator characters
        self.IDBoxContent = Temp[:]
        #Prefix Work-in-progress topics with a flag character
        for J in range(len(Temp)):
            Name = Temp[J]
            Prefix = ('  ','*')[self.Help.Topics[Name]['Wip']]
            Temp[J] = Prefix + Name    
        self.IDBox.setlist(Temp)
        if type(Select) == type(0):
            LB = self.IDBox.FetchWidget()
            LB.selection_set(Select)
            LB.see(Select)
        
    def HotboxUpdate(self):
        """
        Refresh the list of Hotlink topics in the Hotlink listbox.
        """
        Temp = self.Help.Hotlinks.keys()
        Temp.sort()
        self.HotBox.setlist(Temp)

    def SetTabLabel(self):
        """
        Set the label in an edit tab.
        
        The label shows the ID of the current topic follow by the Wip status.
        """
        Tab = self.TabInfo[self.CurrentTabPage]
        Wip = self.Help.Topics[Tab['ID']]['Wip']
        Tab['Label']['text'] = Tab['ID'] + '     (%s)'%('Complete','Work-in-progress')[Wip]

    def LocateInListbox(self,Target,Listbox):
        """
        Return the index of "Target" in "Listbox", or -1.
        
        Note that we ignore a leading asterisk in the listbox entries.
        """
        Items = Listbox.get(0,Listbox.size())
        J = 0
        for Item in Items:
            Item = Item.lstrip()
            if Item[:1] == '*':
                Item = Item[1:]
            if Item == Target:    
                return J
            J += 1
        return -1        

    def NowEdit(self,ID):
        """
        Setup to start editing the specified topic.
        """
        #Here we release any grab that was in effect. The help compiler never
        #    does a grab of it's own accord, however, if help is invoked from inside
        #    a modal dialog and then help invokes the compiler then none of our
        #    buttons work because of the grab. Toasting the grab rather violates
        #    the spirit of the modal dialog but this sort of thing is done during
        #    *development* by people who supposedly know what they are doing so I'm
        #    not too worried about it. 
        Grab = self.Win.grab_current()
        if Grab:
            self.Win.grab_set()
            self.Win.grab_release()            
        if ID == "#index":
            #Apparently we were invoked from help while it was displaying the index.
            #   Since the index is virtual you can't edit it per se.
            return   
        #Service the Backlist
        self.NoteIDVisited(ID)
        #Look to see if the target topic is already in an edit tab
        for J in range(self.EditTabCount):
            if self.TabInfo[J]['ID'] == ID:
                #great zot - there it is; select it's page
                self.CurrentTabPage = J
                self.Notebook.selectpage(J)
                #and mark it as 'recently used'
                self.TabInfo[J]['LastUsed'] = time.time()
                self.TabInfo[J]['Edit'].focus_set()
                return
        #Look for a currently unused edit page.
        for J in range(self.EditTabCount):
            if self.TabInfo[J]['ID'] == '':
                #found one; create our editing stuff
                self.CurrentTabPage = J
                self.TabInfo[J]['LastUsed'] = time.time()
                self.TabInfo[J]['ID'] = ID
                #the page doesn't exist; create it
                ThePage = self.Notebook.add(str(J))
                TheLabel = Label(ThePage,text=ID)
                TheLabel.pack(side=TOP,padx=5,anchor=W)
                Edit = ScrolledText(ThePage)
                Edit.FetchWidget()['font'] = self.EditFont
                Edit.pack(side=TOP,expand=YES,fill=BOTH,padx=0,pady=0)
                View = ScrolledText(ThePage,hscrollmode='none')
                View.FetchWidget().config(font=self.ViewFont,cursor=HelpCursor)    
                View.pack(side=TOP,expand=YES,fill=BOTH,padx=0,pady=0)
                self.TabInfo[J]['Label'] = TheLabel
                self.TabInfo[J]['Edit'] = Edit.FetchWidget()
                #This allows convenient access to the Rebar routine at tidy time
                self.TabInfo[J]['Edit'].Rebar = Edit.Rebar
                self.TabInfo[J]['View'] = View.FetchWidget()
                #we bind to Return so we can position the cursor nicely
                self.TabInfo[J]['Edit'].bind('<KeyRelease-Return>',self.on_EditReturn)
                break
        else:
            #No edit tabs are currently unused; find the oldest one.
            OldestLastUsed = time.time()
            OldestIndex = None
            for J in range(self.EditTabCount):
                if self.TabInfo[J]['LastUsed'] < OldestLastUsed:
                    OldestLastUsed = self.TabInfo[J]['LastUsed']
                    OldestIndex = J
            ThePage = self.Notebook.page(OldestIndex)        
            OldID = self.TabInfo[OldestIndex]['ID']
            #Evict the looser from the edit tab
            self.CurrentTabPage = OldestIndex
            TheEdit = self.TabInfo[OldestIndex]['Edit']
            TheView = self.TabInfo[OldestIndex]['View']
            TheText = TheEdit.get("1.0",END)
            R = self.TopicUpdate(OldID,TheText)
            if R <> 1:
                self.Notebook.selectpage(OldestIndex)
                Msg = 'Hello there. I was about to free up an edit tab in order to display ' \
                    'a new help topic, but there is a problem with the ' \
                    'text in the current topic. Best bet is to clean up that topic, THEN choose ' \
                    'your new topic. The problem in the page is: %s'%R
                MessageDialog(Message=Msg)
                return
            #The text has been saved
            TheEdit.delete("1.0",END) #delete the unformatted text
            TheView.delete("1.0",END) #delete anything in the view area
            J = OldestIndex
        #    
        #We have an edit tab for our use
        #
        self.Notebook.selectpage(J)
        Tab = self.TabInfo[self.CurrentTabPage]
        Tab['LastUsed'] = time.time()
        Tab['ID'] = ID
        Topic = self.Help.Topics[ID]
        self.SetTabLabel() #show the ID and Wip status
        #Display the unformatted information in our Edit area
        #    Last argument says to tidy unles it's the substitutions page
        self.TopicToEdit(ID,Tab['Edit'],Tab['ID']<>SubPage)
        #Reflect the new topic in the tab topic listbox
        self.TabBoxUpdate()
        Tab['Edit'].focus_set()

    def TopicToEdit(self,TopicID,Edit,Tidy=True):
        """
        Render unformatted version of a topic to a Text widget for Editing.
        
        We automatically tidy the text to the width of the Edit area unless
            specifically told not to.
        """ 
        Edit.delete("1.0",END) #delete the current content
        Topic = self.Help.Topics[TopicID]
        for Line in Topic['Abstracts']:
            Edit.insert(INSERT,'!%s\n'%Line)
        if Topic['Hotlinks']:
            #display hotlinks as lines of reasonable length
            Line = ''
            for Hot in Topic['Hotlinks']:
                if len(Hot) + len(Line) > 60:
                    Edit.insert(INSERT,Line+'\n')
                    Line = ''
                Line = '%s&%s  '%(Line,Hot)
            if Line:
                Edit.insert(INSERT,Line+'\n')
        if len(Topic['Plurals']) > 0:
            Edit.insert(INSERT,'%s\n'%Topic['Plurals'])
        try:    
            for Line in Topic['Comments']:
                Edit.insert(INSERT,'#%s\n'%Line)
        except KeyError:
            pass  #some early topics didn't have a comment attribute 
        TheText = Topic['Text']
        if Tidy:            
            WidthInChars = self.TextWidthInChars(Edit,self.EditFontWidth)
            TheText = self.Rewidth(TheText,WidthInChars).Result
        Edit.insert(INSERT,TheText)

    def TextWidthInChars(self,Text,WidthPerChar):
        """
        Compute the width of a Text widget in characters.
        
        "Text" is the text area whose width we want to compute.
        "WidthPerchar" is the width, in pixels, of the font used. If a fixed pitch font is
            in use the result will be precise. If a proportional font is used then 
            WidthPerChar should be the average width of a character are the result will
            be approximate.
            
        For unknown reasons, the fudge factor of 2 is required to produce a valid result.    
        """
        #We need to know the width of a scrollbar
        if self.VScrollbarSize == None:
            self.VScrollbarSize = self.MeasureWidget('Scrollbar(orient=VERTICAL)')
        TextWidth = Text.winfo_width()
        if TextWidth == 1:
            #apparently the geometry hasn't been negotiated yet; prompt that to happen
            Text.update_idletasks()
            TextWidth = Text.winfo_width()
        Result = (TextWidth-self.VScrollbarSize[0]) / WidthPerChar - 2
        return Result

    def BBToSize(self,BB):
        """
        Given a bounding box (x1,y1,x2,y2) return the (x,y) size of the box
        """
        return (BB[2]-BB[0], BB[3]-BB[1])

    def MeasureWidget(self,Widget):
        """
        This measures the size of a widget by putting it on a little temporary
            canvas and then checking to see what size it is.
        """
        #Originally I was creating this canvas on master self.Win but Tk whines
        #    about that (don't know why) in the case where we have created self.Win
        #    as a Toplevel.
        C = Canvas(width=100,height=100)
        T = eval(Widget)
        #print 'T=%s'%`T`
        ID = C.create_window(10,10,window=T)
        self.Win.update_idletasks()
        Bbox = C.bbox(ID)
        C.delete(ID)
        del C
        Size = self.BBToSize(Bbox)
        return Size
        
    def LinksExtract(self,TopicID):
        """
        Given a Topic, return a list of all link and hotlink references in that topic's text.
        
        Each item in the result is a string and will be of the form 
            '&<HotlinkName>' for hotlinks,
            '=<TopicID>' for links.
        """
        Topic = self.Help.Topics[TopicID]
        if Topic.has_key('Links'):
            #this is the easy case
            R = Topic['Links']
        else:
            #we have to search for the links
            R = self.Help.Render(None,Topic['Text'],self.Help.Topics)
            Topic['Links'] = R
        #print '%s Links=%s'%(TopicID,R)
        return R

    def IsSubstring(self,A,B):
        """
        Return true if A or B is a leading substring of the other
        """
        return A[0:len(B)] == B or B[0:len(A)] == A
            
    def TopicUpdate(self,TopicID,Text):      
        """
        Update a topic with text from the user.
        
        We return 1 if all went well, otherwise an error message string.
        """
        #Break the text up into it's component parts
        if (TopicID == ''         #topic never been used
        or  TopicID == '<none>'): #topic freed up by delete
            return 1
        if not TopicID in self.Help.Topics.keys():
            raise Exception,  'TopicUpdate: invalid TopicId=%s'%str(TopicID)
        R = self.VetTopicText(TopicID,Text)
        if type(R) == type(''):
            #we got a reason string indicating an error; return it signalling failure
            return R
        #The text is OK; move it into place    
        T = self.Help.Topics[TopicID]
        for K in ('Abstracts','Comments','Hotlinks','Text','Plurals'):
            T[K] = R[K]
        #Bring the listbox up to date on new Hotlinks
        self.Help.HotlinksUpdate()
        self.HotboxUpdate()
        return 1                

    def VetTopicText(self,TopicID,Text):
        """
        Scan a blast of text to see if we like it as the unformatted text of a topic.
        
        If we don't like the text, the result is a reason string.
        
        This routine checks for:
            o The text being of type string (duh).
            o Hotlinks within this text which conflict with each other.
            o Hotlinks within this text which confilct with hotlinks in Help.Topics
            o Hotlinks in other pages which point to a hotlink in this page which
                  is no longer there.
            o The Plurals line being properly formed.      
        
        If we like the text, the result is a topic dictionary suitable inclusion
            in Help.Topics. Note that the 'Wip' entry in the result is arbitrarily
            set to 1. If this isn't what you want, change it or don't use it.
            
        We need the TopicID here so we don't look for hotlink conflicts between 
            this text and the version already in Help.Topics.
            
        Note that the topic passed to this routine may or may not already exist in
            Help.Topics. Which is to say you can call this routine either to vet
            an existing topic which is being updated or to vet a proposed new
            topic.        
        """
        if type(Text) <> type(''):
            return 'Text not of type string. (%s)'%str(Text)    
        Abstracts = []
        Hotlinks = {}
        Comments = []
        TopicText = []
        Plurals = []
        Text = Text.rstrip() #toast any trailing whitespace
        Mode = '>'
        for L in Text.split('\n'):                    
            First = L[0:1]
            if Mode == '>':
                if First == '>':
                    Redirect = L[1:].split()[0].lower()
                    if not self.Help.Topics.has_key(Redirect):
                        return 'The ID "%s" to which this topic is being redirected does not exist.'%Redirect
                    TopicText = [Text]
                    break
                Mode = '!&#'        
            if Mode == '!&#':
                if First == '!':
                    Abstracts.append(L[1:].strip())
                    continue
                if First == '&':
                    Temp = L[1:].split('&')
                    for H in Temp:
                        Hotlinks[H.strip().lower()] = None
                    continue    
                if First == '#':
                    Comments.append(L[1:].strip())
                    continue    
                if First == '[':
                    if Plurals <> []:
                        return 'More than one pluralization line'
                    try:
                        Plurals = eval(L)
                        if type(Plurals) <> type([]):
                            return 'Plural line not a list'
                        for P in Plurals:
                            if type(P) <> type(0):
                                return 'Plural line contains "%s" which is not an integer'%str(P)
                    except:
                        return 'Invalid pluralization line'            
                    continue    
                Mode = 't'        
            if Mode == 't':
                TopicText.append(L)
        #vet the hotlinks against themselves
        for A in Hotlinks.keys():
            for B in Hotlinks.keys():
                if A <> B and self.IsSubstring(A,B):
                    return 'hotlinks "&%s" and "&%s" within this topic conflict.'%(A,B)
        #Vet hotlinks against other hotlinks and dangling hotlinks.
        #In Danglers the key is the hotlink name and the values are lists of TopicIDs which
        #    refer to that hotlink.
        Danglers = {}
        for T in self.Help.Topics.keys():
            if T <> TopicID: #don't check ourself
                #Check for hotlink conflicts
                for A in self.Help.Topics[T]['Hotlinks']:
                    for B in Hotlinks.keys():
                        if  self.IsSubstring(A,B):
                            return 'hotlink "&%s" conflicts with hotlink "&%s" in topic "%s'%(B,A,T)
                #Check for dangling hotlinks that point to this page
                Links = self.LinksExtract(T)
                for L in Links:
                    if L[0] == '&':
                        Hotlink = L[1:]
                        if self.Help.Hotlinks[Hotlink] == TopicID:
                            if not Hotlink in Hotlinks.keys():
                                #hotlink points to us, but we show no such link
                                if not Danglers.has_key(Hotlink):
                                    Danglers[Hotlink] = []
                                Danglers[Hotlink].append(T)
        if Danglers:
            Msg = 'One or more pages have hotlinks which refer to a hotlink which is no longer' \
                ' defined on this page. '
            for D in Danglers.keys():
                Msg += '  &%s('%D
                for R in Danglers[D]:
                    Msg += '%s, '%R
            Msg = Msg[:-2] + ')'
            return Msg
        #we like the text; build our result dictionary
        Temp = Hotlinks.keys()
        Temp.sort()
        Text = '\n'.join(TopicText)
        return {'Abstracts':Abstracts, 'Hotlinks':Temp, 'Comments':Comments, 'Plurals':Plurals, 'Wip':1, 'Text':Text}

    class Rewidth:
    
        def __init__(self,Text,Width):
            """
            Given a blast of unformatted help style text, rearrange the lines so
                they are optimized for the specified width. The result is returned
                as Rewidth.Result
            """
            assert Width>=20, 'Formatting to a window narrower than 20 is silly'
            self.Width = Width
            self.InsertPoint = 0
            self.HeldText = ''
            Stack = []
            self.Result = []
            for L in Text.split('\n'):
                #print 'L=<%s>'%L
                L = L.rstrip()
                Fnbi = len(L) - len(L.strip())
                if L == '':
                    #blank line
                    self.Emit()
                    self.Result.append('')
                    continue
                if Fnbi < self.InsertPoint:
                    #We are backing out of one or more indented lists
                    self.Emit()
                    while Fnbi < self.InsertPoint:
                        #print '#backing out'
                        Stack.pop()
                        if Stack:
                            self.InsertPoint = Stack[-1] + 2
                        else:
                            self.InsertPoint = 0                
                if L[Fnbi] in ('ont') and L[Fnbi+1:Fnbi+2] in (' ',''):
                    #This is an indented list item
                    self.Emit()
                    if Stack == [] or Stack[-1] < Fnbi:
                        #print "#Starting new indent"
                        #Either no stack is in effect, or this item is more deeply nested
                        #    than the current stack. In either case we start a new indented list.
                        Stack.append(Fnbi)
                        self.InsertPoint = Fnbi + 2
                    self.HeldText = L
                else:
                    #We do not have the start of an indented list
                    if Fnbi == self.InsertPoint:
                        #print '#carry-n line'
                        if self.HeldText:
                            #Line is logical continuation of previous line
                            self.HeldText += ' '
                            self.HeldText += L.strip()                
                        else:
                            #This is a new carry-on line
                            self.HeldText = L    
                        continue
                    if Fnbi > self.InsertPoint:
                        #this line is indented; start a new logical line
                        #print 'New logical line'
                        self.Emit()
                        self.HeldText = (self.InsertPoint * ' ') + ' ' + L.strip()
                        continue
                    raise Exception, "Should not get here"
            self.Emit()
            self.Result = '\n'.join(self.Result)

        def Emit(self):
            while self.HeldText:
                ToPrint, self.HeldText = Cleave(self.HeldText,self.Width)
                if self.HeldText:
                    self.HeldText = (self.InsertPoint*' ') + self.HeldText
                self.Result.append(ToPrint)


class TheHelpThingy:
    """
    This class provides user help.
    
     o "Index" If true, we present an 'Index' button which links to a list of all
        abstracts of all topics from which the user can choose.
    
     o "Intro" If not "None" and it is the name of a TopicID, then we
        present the user with an "Introduction" button which links to the
        specified topic which is usually some 'new user start here' stuff.
        
     o "LinkColor" The color the use when rendering hyperlink text. Defaults to
        a muted green.    
        
     o "Locate" Tells us to position the help window with respect to a particular widget.     
        If specified, it should be a 3-element list or tuple giving (X,Y,Widget).
        The help window will be positioned X to the right of and Y below the upper
        left corner of Widget. If Locate is not specified, the help window pops
        up wherever the window manager decides to place it. Note that the data in
        Locate is used AT THE TIME THE HELP WINDOW IS CREATED which may be different
        than it was when TheHelpThingy instance was created.
    
     o "OfferCompiler" If true and we are passed a help topic which doesn't exist, we
        create the help topic and offer to fire up the HelpCompiler for the user.
        When OfferCompiler is true (which suggests we are in development mode)
        then the HelpTopicID is shown on the user help page.
        
     o "Path" is the path to the file in which all the help information is stored.
        If the compiler is being offered and the file doesn't exist you are asked
        if you want to create the file. If the compiler isn't being offered and the
        file doesn't exist you simply get a message saying it doesn't exist.    
        
     o "Title", if given, is the title used on the user help window. Defaults to "Help".    
    
    Help topics are stored in dictionary self.Topics, where each item is itself a dictionary:
        {
        "[Key]"        : A string or number which identifies this help topic. ;
        "['Abstracts']" : A list of strings, each of which describes this topic. All
                          topic strings are aggregated to create the the topic
                          index which the user can see. ;
        "['Hotlinks']" : A list of strings, each of which is a word or phrase which
                          other help topics can to create a link to this topic. ;
        "['Comments']" : Comment area for use by help authors. ;
        "['Wip']"      : 1 if this topic is a work-in-progress, 0 if it is complete. ;                  
        "['Text']"     : The unformatted text of this topic. ;
        }

    "self.Hotlinks" is a dictionary where the key is the hotlink text and the value
        is the help topic ID (ie a Key in "self.Topics").        
        
    "self.Backlist" is the list of topics we have visited, with the last topic being
        the currently displayed one. This is used to implement the 'Back' function.    
        Each entry in backlist is a list consisting of:
        o "[0]" The help topic itself.
        o "[1]" The argument list; necessary for redirected topics with replacement.
    #=p Public Methods
    #=u Unpublished Methods    
    """
    def __init__(self
            ,Index=1
            ,Intro=None
            ,LinkColor='#006000'
            ,Locate=None
            ,OfferCompiler=0
            ,Path=None
            ,Title='Help'
            ,BasicFontSize=-12
            ,HeadingFontSize=-14):
        global Compiler, SubstitutionDict
        """=p
        Create the help object.
        
        Note that on exit from this function "self.Topics" will normally be the dictionary
            containing the help topics. If the help file did not exist and the user did not
            elect to create one (they get that choice if "OfferCompiler" is true) then
            "self.Topics" will be None.
        """
        self.Topics = None
        if  Path==None:
            MessageDialog(Message='You forgot to specify the path to the help file.')
            return
            
        #setup our fonts    
        self.FontNormal    = ('helvetica', BasicFontSize)
        self.FontBold      = ('helvetica', BasicFontSize, 'bold')
        self.FontItalic    = ('helvetica', BasicFontSize, 'italic')
        self.FontHeading   = ('helvetica', HeadingFontSize, 'bold')
        self.FontFixed     = ('courier',   BasicFontSize)
        self.FontFixedBold = ('courier',   BasicFontSize, 'bold')
        self.FontBullet    = self.FontFixedBold
        self.LinkColor = LinkColor
        #We would compute this now but we need a window which we don't yet have. Flagging
        #   this as None prompts Render to compute it when needed.
        self.BulletIndent = None 
            
        # Fetch the help information
        self.FileName = Path
        self.IntroTopic = Intro
        self.Locate = Locate
        self.OfferCompiler = OfferCompiler
        self.Title = Title
        if Locate:
            assert len(Locate) == 3
            assert type(Locate[0]) == type(0)
            assert type(Locate[1]) == type(0)
        self.IndexButtonRequested = Index
        if not os.path.isfile(self.FileName):
            #We didn't find the help file
            if OfferCompiler:
                R =MessageDialog('Information','Help file "%s" not found. Create it now?'%self.FileName
                    ,Buttons=(('Yes',1),('~No',0))).Result
                if R:    
                    self.Topics = {}
                    self.Save()
                else:
                    MessageDialog('Information','Help file not created. No help will be available')
                    return
            else:
                MessageDialog('Warning','Help file "%s" was not found. No help will be available.'%self.FileName)
                return 
        self.Topics = cPickle.load(open(self.FileName)) 
        #Initially there are no saved arguments
        self.SavedArgumentList = []
        
        #Temporary code 
        """
        for Key in self.Topics.keys():
            Info = self.Topics[Key]
            if Info['Wip']:
                if Info['Text'][0] == '>':
                    print Info['Text']
                    Info['Wip'] = 0
        """
        #Build the hotlink directory
        self.HotlinksUpdate()
        
        #We have no help window initially
        self.Win = None
        #And no compiler
        Compiler = None
        #And no substitutions
        SubstitutionDict = {}
        
    def __call__(self, HelpTopicID, ArgumentList=None):
        """=p
        Call this routine to display help on the specified HelpTopicID.
        
        "HelpTopicID" can be either a string giving the topic ID, or it can be a tuli
            containing:
            o [0] The topic ID string
            o [1] An argument list.
            
        If "HelpTopicID" is a tuli as described above, then "ArgumentList" must be
            omitted.    
        
        ArgumentList, if provided, must be a list of items to be used to replace
            @n paramaters in the help text.
            
        Note: The argument list is used unless the topic is redirected, in which case
            we get the arguments from the redirection line.
        """
        global Compiler
        if type(HelpTopicID) in (type(()), type([])):
            #Caller supplied an ID and an argument list in one shot
            assert len(HelpTopicID) == 2
            assert type(HelpTopicID[0]) == type('')
            assert type(HelpTopicID[1]) in (type(()), type([]))
            assert ArgumentList == None
            ArgumentList = HelpTopicID[1]
            HelpTopicID = HelpTopicID[0]
        else:
            #ID is just a plain ID string
            assert type(HelpTopicID) == type('')
        if ArgumentList:
            #Ensure all arguments are strings
            #ArgumentList = [str(X) for X in ArgumentList]
            pass
        if self.Topics == None:
            MessageDialog(Message='No help is available.')
            return
        HelpTopicID = HelpTopicID.lower()
        if HelpTopicID[0:1] == '#':
            #Its a request for the index
            self.on_Index()
        elif self.Topics.has_key(HelpTopicID):
            #It is a known help topic or a request for the index.
            self.DisplayKnown(HelpTopicID,ArgumentList)
        else:
            #this is an unknown help ID
            if self.OfferCompiler:
                self.Topics[HelpTopicID] = {'Abstracts':[], 'Hotlinks':[], 'Text':''
                    , 'Comments':[], 'Plurals':[], 'Wip':1}
                ##D('__call__: Compiler=%s'%Compiler)
                if not Compiler:
                    #We don't have the compiler running; ask user if they want it
                    Msg = 'Help ID "%s" is new. Should I fire up the help editor now?'%HelpTopicID
                    R = MessageDialog(Title='Query',Message=Msg,Buttons=(('Yes',1),('~No',0))).Result
                    if R:
                        Compiler = HelpCompiler(self)
                        ##D( "__call__: HelpCompiler built")
                        Compiler.NowEdit(HelpTopicID)
                else:
                    #we had a compiler
                    try:
                        #Assume it's still there
                        Compiler.Lift()
                    except TclError:
                        #OK, it's not still there, create a new instance
                        Compiler = HelpCompiler(self)    
                    Compiler.IDBoxUpdate()
                    Msg = 'Help ID "%s" is new and has been added to the help topic list.'%(HelpTopicID)
                    MessageDialog(Message=Msg)
                    Compiler.NowEdit(HelpTopicID) #select the new message
                self.Save()    
            else:    
                Msg = 'There is no help page for the topic "%s".'%HelpTopicID
                MessageDialog(Message=Msg)

    def AddSubstitution(self,SubTuli):
        """
        Add a substitution pair.
        
        The argument must be a 2-element tuli of strings, where the first string
            is the target text which will be replaced while the second string 
            is the text it will be replaced with.
            
        Prior to rendering a help topic we run the substitution list against
            the topic text and then the substitutions specified in the (optional)
            topic __substitutions__    
        """
        global SubstitutionDict
        assert len(SubTuli) == 2
        assert type(SubTuli[0]) == type('')
        assert type(SubTuli[1]) == type('')
        SubstitutionDict[SubTuli[0]] = SubTuli[1]

    def DefineTopic(self,HelpTopicID,InitialText):
        """=p
        Request that a new topic be defined.
        
        This is valid *ONLY* if this instance of help was creted with option
            "OfferCompiler" set to true *and* the compiler is up and running.
            
        If things go well the result is 1.
        
        If things go poorly, the result is a reason string.    
        """
        if not Compiler:
            return 'The compiler needs to be running to use DefineTopic'
        #Make sure this really is a NEW topic.
        if self.Topics.has_key(HelpTopicID):
            #it isn't
            return 'DefineTopic only defines NEW topics. Topic "%s" already exists'%HelpTopicID
        #See if this topic meets with the compilers approval
        R = Compiler.VetTopicText(HelpTopicID,InitialText)
        if type(R) == type(''):
            #it does not; pass reason string back to our caller
            return R
        #All systems go; add the new topic
        assert type(R) == type({})
        self.Topics[HelpTopicID] = R
        return 1    
                

    def Redirector(self,HelpTopicID):
        """=p
        Attempt to resolve a redirected help topic.
        
        HelpTopicID is the initial ID which may or may not be redirected.
        
        Our goal is to find the ultimate target TopicID and to build the argument list.
        
        If things go well, we return a two element tuple consisting of:
        
            o [0] The final TopicID
            o [1] The text of the final topic
            o [2] The argument list, which is a list of strings
        
        If the topic isn't redirected the final TopicID is simply the one we
            received and the argument list is empty, but that is fine.
            
        If there are too many redirections, probably due to  circular references,
            then after showing the user a message we return None
        """
        ArgumentList = []
        RedirectMax = 10
        while 1:
            TheText = self.Topics[HelpTopicID]['Text']
            if TheText == '' or TheText[0] <> '>':
                #topic is not redirected
                break
            RedirectMax -= 1
            if RedirectMax <= 0:
                MessageDialog(Message='More than 10 redirects were encountered ' \
                    'while fetching the help topic. This is probably an error on the ' \
                    'part of the help author. Sorry.')
                return
            #HelpTopicID = TheText.split('\n')[0][1:].lower()
            FirstLine = TheText.split('\n')[0]
            #Help topic is up to the first space; arguments are everything after first space
            HelpTopicID = FirstLine[1:].split(None,1) 
            if len(HelpTopicID) > 1:
                #There were arguments, split them out
                HelpTopicID, Arguments = HelpTopicID
            else:
                HelpTopicID = HelpTopicID[0]
                Arguments = ''    
            HelpTopicID = HelpTopicID.lower()
            try:
                Temp = eval('[%s]'%Arguments)
            except:
                #argument list is invalid
                Temp = ['INVALID ARG LIST (HelpTopicID=%s)'%HelpTopicID]   
            ArgumentList.extend(Temp)    
            if not self.Topics.has_key(HelpTopicID):
                MessageDialog(Message='The help topic you requested was redirected ' \
                    'to help topic ID "%s" which does not exist. This is probably an ' \
                    'error on the part of the help author. Sorry'%HelpTopicID)
                return None
        return (HelpTopicID,TheText,ArgumentList)
    
    #---------------------------------------------------------------------------
    # Private methods from here down
    #---------------------------------------------------------------------------

    def DisplayKnown(self, HelpTopicID, PassedArgumentList=None):
        """=u
        Display specified help topic. If needed, we build out toplevel help window.
        
        If "HelpTopicID" starts with a number sign then we take this to mean that
            the caller wants to see part or all of the index. If nothing follows
            the number sign then we display the entire index. If a string follows
            the number sign then we expunge any non-alphameric characters then
            display all index entries which contain that string.

        If provided, "PassedArgumentList" must be a list of strings.

        Note that we use the "PassedArgumentList" unless the topic is redirected,
            in which case we ignore the passed arguments and get the arguments from
            the redirection line.

        *Help, grab and modal dialogs.* 
        
        Most of the time the help window is not modal: if you open if from inside a 
            program both the program and the help window are available for use. 
            However if help is invoked from inside a dialog which is itself modal 
            then we have issues. 
            
        If we simply carry on our merry way then none of the help window buttons 
            will work, because the modal dialog has a grab in effect. What do is 
            to note if a widget had a grab in effect when we are invoked. If so 
            WE do a grab (so our buttons work) which also has the effect of 
            making US modal. When the user closes the help window (since were 
            modal they don't have much choice) then we restore the grab to the 
            widget from which we stole it (we remember this in self.InitialGrab) 
            which puts things back pretty much the way they were when we were 
            invoked. When we are modal we put a message in the title saying
            close help to continue.
            
        If would be alright with me if help could come up non-modal while the
            dialog that invoked us stayed modal, but if there is a way to do that,
            I haven't found it yet.
        
        If we were created in development mode ("OfferCompiler=1") then we simply
            release any grabs that were in effect because if help is modal then the
            help compiler doesn't work which is annoying when you are trying to 
            author help messages.
        """
        if self.Topics == None:
            MessageDialog(Message='No help is available.')
            return
        if self.Win == None:
            #Need to create our help window
            self.Win = Toplevel()
            self.Win.title(self.Title)
            self.Win.bind('<Destroy>',self.on_Destroy)
            if self.Locate:
                #Locate our window with respect to user supplied widget
                Temp = WidgetInScreen(self.Locate[2])
                Xpos = Temp[2] + self.Locate[0]
                Ypos = Temp[3] + self.Locate[1]
                self.Win.geometry('640x480+%s+%s'%(Xpos,Ypos))
            else:
                self.Win.geometry('640x480+50+50')
            #
            # Button bar across the top
            #
            self.Buttons = ButtonBox(self.Win)
            self.Buttons.add('Back',command=self.on_Back)
            if self.IndexButtonRequested:
                self.Buttons.add('Index',command=self.on_Index)
            if self.Topics.has_key(self.IntroTopic):    
                self.Buttons.add('Introduction',command=self.on_Intro)
            if self.OfferCompiler:
                self.Buttons.add('Compiler',command=self.on_Compiler)    
            Close = self.Buttons.add('Close',command=self.on_Close)    
            self.Buttons.pack(side=TOP,fill=X)
            Close.bind('<ButtonRelease-3>',self.on_ShowTopicId)
            #
            # If compiler is offered, a label to show current topic ID
            #
            if self.OfferCompiler:
                self.IDLabel = Label(self.Win)
                self.IDLabel.pack(side=TOP,fill=Y,anchor=W)
            #
            # Area to hold rendered text
            #
            """
            self.Text = Pmw.ScrolledText(self.Win
                ,text_borderwidth=3
                ,text_relief=FLAT
                ,text_wrap=WORD
                ,text_cursor=HelpCursor)
            """
            self.Text = ScrolledText(self.Win,hscrollmode='none',vscrollmode='dynamic')
            TextComponent = self.Text.FetchWidget()
            TextComponent.config(cursor=HelpCursor)
            self.Text.pack(side=TOP,expand=YES,fill=BOTH)        
            TextComponent.focus_set()
            
            self.Backlist = []

        #Be modal if invoked from a modal dialog
        self.InitialGrab = self.Win.grab_current() 
        #print 'InitialGrab=%s, type=%s'%(self.InitialGrab,type(self.InitialGrab))
        #print 'WeAre=%s'%self.Win
        if self.InitialGrab:
            if self.InitialGrab <> self.Win:
                Grabber(self.Win)
                self.Win.title(self.Title+'  (Close help to continue)  ')

        #But not if we are in development mode
        if self.OfferCompiler:
            self.Win.grab_release()
            self.Win.title(self.Title)

        # 'Back' button is enabled only if we have history
        if self.Backlist:
            Temp = NORMAL
        else:
            Temp = DISABLED
        self.Buttons.button('Back')['state'] = Temp        
        ArgumentList = []                
        if HelpTopicID[0] == '#':
            #Request for some or all of index; build it dynamically
            Index = []
            Target = HelpTopicID[1:].strip()
            #D('Target="%s"'%Target)
            S = Searcher()
            S.Parse(Target)
            for T in self.Topics.keys():
                Link = '{L%s=%s}'%(Target,T)
                for Abs in self.Topics[T]['Abstracts']:
                    #Look after possible substitutions
                    Abs = self.Substitute(Abs,self.Topics)
                    if S.Search(Abs) or Target == '':
                        #Either it matches or they asked for everything
                        Index.append([Abs,' {L>>> =%s} %s'%(T, Abs)])
            #D('Index=%s'%Index)
            Index.sort()
            Index = [Entry[1] for Entry in Index]
            Header = 'Help topics matching: %s'%Target
            if Target == '':
                Header = 'All help topics'
            if Index == []:
                Header = 'No help topics matched: %s'%Target    
            TheText = '{H%s}\n\n%s'%(Header,'\n'.join(Index))
                            
            ArgumentList = [] #must have empty arglist to push on Backlist
        else:
            #Topic is not the index page


            TheText = self.Topics[HelpTopicID]['Text']
            if TheText == '' or TheText[0] <> '>':
                #topic is not redirected
                ArgumentList = PassedArgumentList
            else:
                #topic is redirected    
                R = self.Redirector(HelpTopicID)
                if R == None:
                    #too many redirections; user has already seen message
                    return
                HelpTopicID, TheText, ArgumentList = R    
            """
            #Legacy code, remove if above code works
            if PassedArgumentList == None:
                #process any redirection
                R = self.Redirector(HelpTopicID)
                if R == None:
                    #too many redirections; user has already seen message
                    return
                HelpTopicID, TheText, ArgumentList = R    
            else:
                #We were given an argument list - do not attempt redirect
                ArgumentList = PassedArgumentList
                TheText = self.Topics[HelpTopicID]['Text']    
            """    
        #If the compiler is offered, show the help topic ID
        if self.OfferCompiler:
            self.IDLabel['text'] = 'HelpTopic ID = %s'%HelpTopicID 
        self.Backlist.append([HelpTopicID,ArgumentList])
        # Display topic for user. We save a copy of the argument list at this point.
        #    If the user clicks on a line, then we pass the saved argument; this allows
        #    us to have links to topics which can use the arguments that were in force
        #    when help was first invoked.            
        self.SavedArgumentList = ArgumentList
        if HelpTopicID[0] == '#':
            #Help topic has no pluralist
            PluralList = None
        else:    
            #But regular topics do
            PluralList = self.Topics[HelpTopicID]['Plurals']
        self.Render(self.Text.FetchWidget(),TheText,self.Topics,ArgumentList,PluralList)

    def on_ShowTopicId(self,Event=None):
        """
        Display the current topic ID in a dialog, for debugging.
        """
        MessageDialog(Message='CurrentTopic = "%s"'%self.Backlist[-1][0])

    def on_Close(self):
        """
        User asked to close the help window.
        """
        self.Win.destroy()

    def on_Compiler(self):
        """
        User has requested the compiler.
        """
        global Compiler
        if not Compiler:
            #We have not had a compiler; create one
            Compiler = HelpCompiler(self)
        else:
            #We may have a compiler
            try:
                #Try to make it front and center
                Compiler.Lift()
            except TclError:
                #Apparently the user closed it    
                Compiler = HelpCompiler(self)
        #Select the current topic other than the index page        
        CurTopic = self.Backlist[-1][0]
        if CurTopic[0] <> '#':
            Compiler.NowEdit(self.Backlist[-1][0]) 

    def on_Destroy(self,Event):
        """
        The user is toasting the help window.
        """
        #We must create our widoow next time help is invoked.
        if self.InitialGrab <> None:
            #we stole the grab from some widget; give it back
            Grabber(self.InitialGrab)
        self.Win = None
        
    def on_Back(self):
        """
        User clicked on the Back button.
        
        We backup to the first previous topic which is different from the 
            current topic.
        """
        Current = self.Backlist.pop()
        #Current is the entry for the page they were already on
        while 1:
            #Keep backing up till we find a page different than the curren page
            #    or we run out of stacked pages.
            if self.Backlist == []:
                #We ran out
                return
            Target = self.Backlist.pop()
            if Target[0] <> Current[0]:
                #AhHa - we found a page.
                break    
        HelpTopicID, ArgumentList = Target        
        self.DisplayKnown(HelpTopicID, ArgumentList)
        
    def on_Index(self):
        """
        User clicked on the Index button
        """
        M = 'Enter a word or phrase describing the topic of interest. To see the ' \
            'entire index, click OK without entering any text.'
        Target = PromptDialog(Title='Search help index',Message=M,Help=(self,'help.index')).Result
        if Target <> None:
            self.DisplayKnown('#'+Target)
                    
    def on_Intro(self):
        """
        User clicked on the Introduction button.
        """
        self.DisplayKnown(self.IntroTopic)
            
    def HotlinksUpdate(self):
        """
        Build the directory of hotlinks from info in the main dictionary.
        """
        self.Hotlinks = {}
        for T in self.Topics.keys():
            for H in self.Topics[T]['Hotlinks']:
                self.Hotlinks[H] = T

    def Save(self):
        """
        Save Info to disk.
        """
        F = open(ExtArb(self.FileName,'$$$'),'w')
        cPickle.dump(self.Topics,F)
        F.close()
        GeneralizedSaveFinalize(self.FileName)

    def Substitute(self,Text,Topics):
        """
        Given a text string do substitutions and return result as a string.
        
        Dynamic substitutions exists to handle substitutions whose target values are set
            at run-time and thus are not known at help-authoring time. These are set at
            run-time by calling the "AddSubstitution" method. As an example, in Rapyd
            we use this facility to allow us to mention the keys associated with various
            text editing functions even though those keys depend on the editor schema
            selected by the config file and thus are not known till run-time.
            
        Static substitutions take their values from the help topic __substitutions__ and
            exist as a way of having standardized item which show up in many places but
            can be easily revised by making only once change.    
        
        """
        #Handle dynamic global substitutions
        Items = SubstitutionDict.items()
        Temp = zip(map(lambda X:len(X[0]),Items),range(len(Items)))
        Temp.sort()
        Temp.reverse()
        #Temp is now a list of (<len>,<index>) tuples. We go to this fiddle because we
        #    want to process the substitutions in decreasing order of length. For
        #    example, if we are substituting both "$Copy" and "$CopyAppend" then if
        #    we hope to ever substitute the latter then we had better do the longer
        #    ones first. 
        for Len, Index in Temp:
            OldText, NewText = Items[Index]
            if Text.find(OldText) <> -1:
                #Substitution is necessary
                Text = Text.replace(OldText,NewText)
        #Handle static global substitution        
        try:
            #Break the substitution specification up into lines
            SubList = Topics[SubPage]['Text'].split('\n')
            #Append .end so we don't have a dangling substitution; two .ends in a row
            #   won't hurt anything.
            SubList.append('.end')
            NewTextList = []
            OldText = ''
            for Line in SubList:
                if Line.lower()[:4] == '.end':
                    #We have the end of a replacement sequence
                    if OldText <> '' and NewTextList <> []:
                        #We have old and new text
                        if Text.find(OldText) <> -1:
                            #Substitution is necessary
                            Text = Text.replace(OldText,'\n'.join(NewTextList))
                    #setup for to start next replacement sequence    
                    NewTextList = []
                    OldText = ''
                else:
                    #we have something other than end-of-replacement-sequence
                    if OldText == '':
                        #First line of replacement sequence specifies text to be replaced
                        OldText = Line
                    else:
                        #Second and subsequent lines are replacement text
                        NewTextList.append(Line)    
                    
        except KeyError:
            #no topic named __substitutions__
            pass        
        return Text

    def Render(self,TextWidget,Text,Topics,Arglist=None,Plurallist=None):
        """
        Format marked up help text into a Text widget.
        
        "TextWidget" is the Text into which we render the formatted text.
        
        "Text" is the unformatted text of the help topic.
        
        "Topics" is the dictionary of all help topics.
        
        "Arglist" is a list of strings, one per @x substitution indicator.
        
        "Plurallist" is a list of indicies into Arglist. If not empty, we do canonical pluralization
            processing prior to formatting the text. Each element in Plurallist is an index into
            Arglist and the string from Arglist is converted to an integer and then used to drive
            the pluralizer. If Pluralist is a single value then it works like this. The text is
            scanned for entries of the form <ssss/pppp>. If the integer is singular only the ssss
            part is copied to the text; if the integer is non-singular then only the pppp part is
            copied. 
            
            If Plurallist contains more than one value then the selection entries must be of the
            form <nssss/pppp> where "n" is a single digit indicating which entry from Pluralist
            is to be used for this entry.
        
        As we format the text we accumulate a list of links and hotlinks found
            in the text and we return it as our result. Each item in the result 
            is a string and will be of the form 
            o "&<HotlinkName>" for hotlinks,
            o "=<TopicID>" for links.
                
        If TextWidget is "None", then we simply scan for links without rendering
            any text.                
        
        If "Topics['__substitutions__']" exists then prior to any other formatting, we
            use the lines in this topic to do text substitution like this. The first
            line indicates the text to be replaced. Second and subsequent lines
            provide the replacement text. The end of replacement text is indicated
            by a line whose sole content is ".end". As many clumps of substitution
            text as desired can be placed in __substitutions__. The following example
            would replace all occurances of "black" with "white" and "fruit" with
            a bulleted list of several fruit:
            
            "black"
            "white"
            ".end"
            "fruit"
            "o apple"
            "o banana"
            "o grapefruit"
            "o kiwi"
            "o pear"
            ".end"
                    
        This text formatting process ended up rather more complex than I would have
            liked, but if there was some vastly better way, it didn't jump off the
            page at me. Formatting is done in two phases:
            
            1) A character-at-a-time phase which looks after argument replacement,
               character appearance issues (eg bold, heading etc) and link 
               resolution. 
               
            2) A line-at-a-time phase which looks after indented lists, eg bulleted,
               numerated and tabbed paragraphs.       
               
            If all we are doing is scanning the text (TextWidget=None) then only 
               phase 1 happens; phase 2 is omitted.   
        """
        #
        # Phase One
        #
        if self.BulletIndent == None:        
            #Get metric information if we don't already have it
            TempFont = tkFont.Font(TextWidget,self.FontBullet)
            self.BulletIndent = TempFont.measure('o ')
            TempFont = tkFont.Font(TextWidget,self.FontNormal)
            self.NumberIndent = TempFont.measure('1) ')
    
        #Handle any required substitution
        Text = self.Substitute(Text,Topics)
        
        #Convert single digit numeric arguments to words
        if Arglist:
            Arglist = list(Arglist) #People have been known to hand us a tuple
            for J in range(len(Arglist)):
                if type(Arglist[J]) == type(0):
                    Arglist[J] = DigitEncode(Arglist[J])
                Arglist[J] = str(Arglist[J])    
        
        #Handle pluralization
        if Plurallist:
            PL = []
            for P in Plurallist:
                try:
                    IndicatorArg = Arglist[P]
                except IndexError:
                    M = ('Hi. Help module here.\n\nI was about to do pluralization using argument '
                        '@%s as the indicator but was unable to because I received only %s argument{/s}. '
                        'For the sake of not grinding to a halt I have arbitrarily supplied the value '
                        '"one" for the missing argument. This error is the result of an oversight on the '
                        'part of the author of the help message in question.'%(P,len(Arglist)))
                    M = Plural(M,len(Arglist))    
                    MessageDialog(Message=M)
                    IndicatorArg = 1
                #Allow words as numbers for single digit values
                try:
                    IndicatorArg = 'zero one two three four five six seven eight nine'.split().index(IndicatorArg)
                except ValueError:
                    pass    
                try:
                    PL.append(int(IndicatorArg))
                except ValueError:
                    M = ('Hi, Help module here.\n\nI was about to do pluralization using argument '
                        "@%s as the indicator but for that to work the argument must be an integer but it's value "
                        'is "%s" - certainly not an integer. For the sake of not grinding to a '
                        'halt on an exception I have arbitrarily used the value "one" instead. This '
                        'error is the result of an oversight on the part of the authorof the help message '
                        'in question.'
                        %(P,Arglist[P]))
                    MessageDialog(Message=M)
                    PL.append(1)
            Text = Plural(Text,PL,Meta='</>',DoCap=False)
    
        st = Enumerated('Normal TypeNext Formatted LinkText LinkTarget HotLink HotLinkFinish PhotoName Numer')
        AS = Enumerated('ArgNormal ArgDigitNext')
        nt = Enumerated('NumerDecimal NumerLower NumerUpper NumerError')
        Open  = '{' #character that opens  formatted text
        Close = '}' #character that closes formatted text
        Hot   = '&' #character that opens a hotlink
        Link  = '=' #character that separates link text from link target
        Arg   = '@' #character that signals argument 
        self.PhotoList = []
        
        if TextWidget:
            #We are actually going to render text
            TextWidget['font'] = self.FontNormal
            TextWidget.tag_configure('Bold', font=self.FontBold)
            TextWidget.tag_configure('Italic', font=self.FontItalic)
            TextWidget.tag_configure('Heading', font=self.FontHeading)
            TextWidget.tag_configure('Fixed', font=self.FontFixed)
            TextWidget.tag_configure('FixedBold', font=self.FontFixedBold)            
            TextWidget.tag_configure('Link', font=self.FontNormal, foreground=self.LinkColor)
            TextWidget.tag_configure('Error', font=self.FontBold, background='#FF0000')
            TextWidget.tag_bind('Link','<ButtonRelease-1>',self.on_Hyperlink)
    
            TextWidget.delete('1.0',END)
            TextWidget.tag_delete(TextWidget.tag_names())
            
            #The intent here is to lift the help window on the screen. However, if we
            #    do that right now there are instances where the window from which we
            #    were invoked then grabs back the focus which isn't what we want.
            #    Hence we call after to setup a brief delay before we lift.
            TextWidget.after(300,self.FocusOnHelp,TextWidget.winfo_toplevel())
            
            Text = Text.rstrip() #toast any trailing whitespace
            Text += ' ' #but for one space, needed to terminate a trailing hotlink
            TextList = []
        #Result holds accumulated link information
        Result = []    
        
        State = st.Normal
        ArgState = AS.ArgNormal
        ArgBuffer = []
        Buffer = []
        FormatCode = None
        HotLinkText = ''
        LinkTarget = ''
        J = -1
        #print 'Render: Arglist=%s'%Arglist
        while J < len(Text)-1:
            #
            # Fetch the next character    
            #
            if ArgBuffer:
                #If ArgBuffer not empty we fetch the next character from it
                C = ArgBuffer.pop(0)
            else:
                #ArgBuffer is empty; fetch next character from text    
                J += 1
                C = Text[J]
            #
            # Look after argument replacement
            #    
            if Arglist <> None and C == Arg and ArgState == AS.ArgNormal:
                #we have the start of an argument specifications
                ArgState = AS.ArgDigitNext
                continue
            elif ArgState == AS.ArgDigitNext:
                ArgState = AS.ArgNormal
                if C in '0123456789':
                    #we got our digit; do the replacement
                    try:
                        ArgBuffer[0:0] = list(Arglist[int(C)])
                    except IndexError:
                        #no such argument; nothing to do
                        pass
                    #we have done the replacement; go fetch the next character    
                    continue
                if C == Arg:
                    #two arg specifiers in a row get you one    
                    C = Arg
                #we didn't get an argument specifier digit in which case we want to
                #    leave the @C in the text. In order to do that we make '@' the
                #    current character and put our non-digit in ArgBuffer to fetch
                #    as the next character.
                else:    
                    ArgBuffer[0:0] = [C]
                    C = Arg
            #
            # Process the fetched character
            #                            
            Emit = False
            if State == st.Normal:
                #Processing normal text
                if C == Open:
                    State = st.TypeNext
                    Emit = True
                    Tags = ''
                elif C == Hot:
                    State = st.HotLink
                    HotLinkText = ''
                    Emit = True
                    Tags = ''
                    Pre = Hot
                else:
                    Buffer.append(C)
            elif State == st.TypeNext:
                #We are expecting a format character
                if C.upper() in 'IBHFG':
                    #we got our formatting character
                    FormatCode = C.upper()
                    State = st.Formatted
                    Pre = Open + C            
                elif C.upper() == 'L':
                    #start of a link
                    FormatCode = C
                    LinkTarget = ''
                    State = st.LinkText
                    Pre = Open + C
                elif C.upper() == 'P':
                    #start of photo name
                    FormatCode = C
                    PhotoName = ''
                    State = st.PhotoName
                    Pre = Open + C    
                elif C.upper() == 'N':
                    #start of numeration specification
                    FormatCode = C
                    NumerText = ''
                    NumerType = None
                    State = st.Numer
                    Pre = Open + C    
                elif C==Open:
                    #Two opens gets you one
                    Buffer.append(C)
                    State = st.Normal    
                else:
                    #we didn't get a valid character
                    Buffer += [Open, C]
                    Tags = 'Error'
                    Emit = True   
                    State = st.Normal 
            elif State == st.Formatted:
                #we are processing formatted text
                if C == Close:
                    #end of formatted text
                    Tags = {'B':'Bold','I':'Italic','H':'Heading','F':'Fixed','G':'FixedBold'}[FormatCode]
                    Emit = True
                    State = st.Normal
                else:
                    Buffer.append(C)
            elif State == st.LinkText:
                #were accumulating the text of a link            
                if C == Link:
                    State = st.LinkTarget
                    LinkTarget = ''
                else:
                    Buffer.append(C)
            elif State == st.LinkTarget:
                #were accumulating the target of a link
                if C == Close:
                    Result.append('='+LinkTarget.lower())
                    if self.Topics.has_key(LinkTarget.lower()):
                        #The target is a known help topic
                        Tags = '%s =%s'%('Link', LinkTarget)
                    else:
                        Tags = 'Error'
                        Buffer.insert(0,Open)
                        Buffer.insert(1,'L')
                        Buffer += list('%s%s%s'%(Link, LinkTarget, Close))
                    Emit = True
                    State = st.Normal
                else:
                    LinkTarget += C
            elif State == st.PhotoName:
                #Were accumulating a PhotoName
                if C == Close:
                    try:
                        T = PhotoImage(file=PhotoName)
                        self.PhotoList.append(T)
                        #Insert index of this photo into the buffer
                        Buffer.insert(0,len(self.PhotoList)-1)
                    except TclError:
                        Tags = 'Error'
                        Buffer.insert(0,Open)
                        Buffer.insert(1,'P')
                        Buffer += list('%s%s'%(PhotoName,Close))    
                    Emit = True
                    State = st.Normal    
                else:
                    PhotoName += C
            elif State == st.Numer:
                #Were accumulating a numeration specification
                if C == Close:
                    if not NumerType in (nt.NumerError,None) and len(NumerText) < 10:
                        #We like the argument
                        if NumerType == nt.NumerDecimal:
                            NumerText = str(int(NumerText))
                        Buffer.insert(0,'#'+NumerText)
                    else:
                        #We don't like the argument
                        Tags = 'Error'
                        Buffer.insert(0,Open)
                        Buffer.insert(1,'N')
                        Buffer += list('%s%s'%(NumerText,Close))    
                    Emit = True
                    State = st.Normal        
                else:
                    NumerText += C
                    if NumerType == None:
                        #First character sets type
                        if C >= '0' and C <= '9':
                            NumerType = nt.NumerDecimal
                            NumerLimits = '09'
                        elif C >= 'a' and C <='z':
                            NumerType = nt.NumerLower
                            NumerLimits = 'az'
                        elif C >= 'A' and C <= 'Z':
                            NumerType = nt.NumerUpper
                            NumerLimits = 'AZ'
                        else:
                            NumerType = nt.NumerError
                            NumerLimits = ' ~'
                    else:
                        #Verify that subsequent characters match type
                        if C < NumerLimits[0] or C > NumerLimits[1]:
                            NumerType = nt.NumerError
                                                
            elif State == st.HotLink:
                #HotLinkText is the actual text which we will pass on to the next phase
                #    of formatting. HotLinkTextNominal is that same text but with all
                #    letters changed to lower case (so hotlinks are case insensitive
                #    and with newlines changed to spaces (so we still recognize multi-
                #    word hotlinks even though they span a line break.
                HotLinkText += C
                #Lower and remove redundant spaces. You have to remove reduncant spaces
                #    because if a multi-word hot link reference spans two lines AND it's 
                #    inside indented text then you get redundant spaces where you 
                #    really want only one.
                HotLinkTextNominal = ' '.join(HotLinkText.split()).lower()
                ##D('HotLinkTextNominal=<%s>'%HotLinkTextNominal)
                if self.Hotlinks.has_key(HotLinkTextNominal):
                    #we have our match
                    State = st.HotLinkFinish    
                    #Make lower case and remove redundant spaces
                    """
                    Result.append('&'+HotLinkText.lower())
                    #we have our match
                    Tags = '%s =%s'%('Link', self.Hotlinks[HotLinkTextNominal])
                    Emit = True
                    State = st.Normal
                    Buffer = list(HotLinkText)
                    """
                elif len(HotLinkText) > 40:
                    #we declare this a bonzo hotlink
                    Buffer += list(Hot + HotLinkText)
                    Tags = 'Error'
                    Emit = True
                    State = st.Normal    
            elif State == st.HotLinkFinish:
                """
                The point of this state is to have the visual hotlink (the part that lights
                    up in the 'link' color) run to the next space or newline. Example:
                    the matched hotlink is 'measure' but they word in the text we are scanning
                    which has matched is 'measuring'. Rather than have 'measur' lit up as link
                    and 'ing' as regular text, we keep scanning text till we get to whitespace
                    and then declare the hotlink done.
                """
                HotLinkText += C
                ##D('HotLinkText=%s'%HotLinkText)
                if C in (' ','\n'):
                    #we have whitespace, hotlink ends
                    Result.append('&'+HotLinkTextNominal)
                    #we have our match
                    Tags = '%s =%s'%('Link', self.Hotlinks[HotLinkTextNominal])
                    Emit = True
                    State = st.Normal
                    Buffer = list(HotLinkText)
            if Emit and TextWidget:
                #TextWidget.insert(INSERT,''.join(Buffer),Tags)
                TextList.append(Tags)
                TextList.extend(Buffer)
                Buffer = []
                Tags = ''
                HotLinkText = ''
                LinkTarget = ''
        if TextWidget == None:
            #we were just scanning for links; return the result now
            return Result    
        if Buffer or LinkTarget or HotLinkText:
            #emit any trailing text or pending accumulated stuff
            if State <> st.Normal:
                #Were not in a normal state; show formatting stuff to user
                Buffer = list(Pre) + Buffer
                if LinkTarget <> '':
                    Buffer += list(Link+LinkTarget) 
                if HotLinkText <> '':
                    Buffer += list(HotLinkText)
                Tags = 'Error'
            else:
                Tags = ''
            #TextWidget.insert(INSERT,''.join(Buffer),Tags)
            TextList.append(Tags)
            TextList.extend(Buffer)
        if State <> st.Normal:
            #TextWidget.insert(INSERT,' (UNCLOSED ITEM) ','Error')        
            TextList.append('Error')
            TextList.extend(list(' (UNCLOSED ITEM) '))
        #
        # Phase Two
        #
        """
        At this point TextList consists of text characters and tags. Characters
            are of length one. Things of any other length are tags. Note that an
            empty string is a tag (it's length isn't one) which says 'no tag needed'.
            The tags are PREFIXES; each tag applies to the text that follows, up
            until the next tag.
        """
        ##D('TextList=%s'%TextList)
        #Used to keep track of bulleted and enumerated lists
        ListList = []
        #Holds stuff we are accumulating 
        Buffer = BufObj(TextWidget,self.BulletIndent,self.NumberIndent,self.PhotoList)
        #Notes origin of next numerated paragraph
        NumerOrigin = '1'
        #Indicates where on the line we are currently expecting to find the
        #   first character of text. 
        InsertPoint = 0
        # 
        I = -1 #This steps through TextList
        First = 0 #The start of the current line
        while I < len(TextList)-0:
            I += 1
            if I <> len(TextList) and TextList[I] <> '\n':    
                #we don't have end-of-line or end-of-text
                continue
            #we have found a line; get it with no tags and no images.
            #The line runs from First to I
            #print 'TextList[First:I] %s %s %s'%(First,I,TextList[First:I])
            Line = []
            for J in range(First,I):
                if type(TextList[J])==type('') and TextList[J][0:1] == '#':
                    #This is a NumerOrigin
                    NumerOrigin = TextList[J][1:]
                elif TextList[J] and (type(TextList[J])<>type(0) and len(TextList[J]) == 1):
                    #Character
                    Line.append(TextList[J])
                elif type(TextList[J]) == type(0):
                    #Image; put a placeholder character in the text
                    Line.append(chr(0x7F))    
            L = ''.join(Line).rstrip()
            
            #First is the index of the first character in the line in TextList
            if L == '':
                #Line is blank; although the line contains no printable characters, it
                #    is possible for it to contain a tag, hence we do the buffer Extend
                #    with whatever is in the line.
                Buffer.Extend(TextList[First:I])
                Buffer.EmitNonEmpty()
                Buffer.Emit()
            else:
                #Line is not blank
                M = L.strip()
                Fnbi = len(L) - len(M) #Compute index of first non-blank
                HaveBullet = L[Fnbi] == 'o' and L[Fnbi+1:Fnbi+2] in (' ','')
                HaveNumber = L[Fnbi] == 'n' and L[Fnbi+1:Fnbi+2] in (' ','')
                HaveTab    = L[Fnbi] == 't' and L[Fnbi+1:Fnbi+2] in (' ','')
                #Since at most only one of the above can be true, HaveList will
                #    be in (0,1,2,3)
                HaveList = HaveBullet + (HaveNumber*2) + (HaveTab*3)
                #Process possible list closures
                if Fnbi < InsertPoint:
                    #we are closing one or more indented lists
                    Buffer.EmitNonEmpty()
                    while Fnbi < InsertPoint:
                        if HaveList and Fnbi == InsertPoint - 2:
                            #This is a continuation of an existing list;
                            break
                        Temp = Buffer.ListPop()
                        #print 'POP-------------'
                        if Temp <> None:
                            #we have backed up to a previous list
                            InsertPoint = Temp + 2
                        else:
                            #we are no longer in a list
                            InsertPoint = 0
                #Process possible list opening
                if HaveList:
                    #A list implicity creates a line break; flush the buffer
                    Buffer.EmitNonEmpty()
                    Temp = Buffer.ListLast()
                    if Temp == None or Temp < Fnbi:
                        #Either no list is in effect, or this bullet is more deeply
                        #   indented than previous bullets. In either case we push
                        #   a value on the stack to start a new list.
                        #print 'Fnbi=%s'%Fnbi
                        Buffer.ListPush(Fnbi,HaveList,NumerOrigin)
                        if HaveNumber:
                            #A new numer resets the numer origin
                            NumerOrigin = '1'
                        InsertPoint = Fnbi + 2
                    #Process bulleted line.
                    Buffer.MarkBullet(HaveList)              
                    Buffer.Extend(TextList[First:I])
                else:
                    #we do not have the start of a bulleted point
                    ##D('Not bullet. Fnbi=%s InsertPoint=%s'%(Fnbi,InsertPoint))
                    if Fnbi == InsertPoint:
                        #text as expected
                        if Buffer.NonEmpty():
                            #This line continues a previous one; supply a free space.
                            Buffer.InjectSpace()
                        #Hand the line to the buffer
                        Buffer.Extend(TextList[First:I])
                    elif Fnbi > InsertPoint:
                        #this line is indented; start a new logical line
                        Buffer.EmitNonEmpty()
                        Buffer.Extend(TextList[First:I])
                    else:
                        raise Exception, "Shouldn't get here"
            #print TextList[First:I+1]
            #print Line
            First = I + 1            
        #handle any text left at the end.                
        Buffer.EmitNonEmpty()                
        return Result
                
    def on_Hyperlink(self,Event):
        """
        Called when user clicks on a link in the help text.
        """
        #Get tags associated with the cursor position
        Tags = Event.widget.tag_names(CURRENT)
        for T in Tags:
            #look for a tag of the form '=<TopicID>'
            if T[0:1] == '=':
                TopicID = T[1:]
                #Note that the argument list was saved for us; this allows passed
                #    arguments to persist as the user clicks on links.
                self(TopicID,self.SavedArgumentList)

    def FocusOnHelp(self,OurTopLevel):
        """
        This is invoked (via w.after from Render) to focus on the help window.
        """
        OurTopLevel.lift()

class BufObj:
    """
    A buffer object solely to help Render deal with indented lists.
    """    
    def __init__(self,TextWidget,BulletIndent,NumberIndent,PhotoList):
        #The number of pixels by which a bullet indents our text in our font
        self.BulletIndent = BulletIndent
        self.NumberIndent = NumberIndent
        self.PhotoList = PhotoList
        #The widget to which we render the text
        self.TextWidget = TextWidget
        #Holds characters and tags temporarily
        self.Buffer = []
        #0 = normal line; 1 = line opens with numerator; 2 = line opens with bullet
        self.BulletLine = 0
        #This keeps track of bulleted and enumerated lists
        self.ListList = []
        #This keep track of the tags that get passed to us in the text stream.
        self.RunningTag = ''

    def MarkBullet(self,BulletFlag):
        """
        Note that the current line is bulleted or numerated.
        
        If BulletFlag is:
             1 if the line is bulleted,
             2 if the line is numerated,
             3 if the line is tabbed.
        """
        assert BulletFlag in (1,2,3)
        self.BulletLine = BulletFlag 
        if BulletFlag <> self.ListList[-1][0]:
            #User is changing indented list type in mid stream. This probably
            #    isn't a brilliant tactic but neither is it worth coughing up
            #    an error message about. We treat it as the start of a new
            #    indented list (at the same indent) and carry on.
            self.ListList[-1][0:2] = [BulletFlag,1]

    def InjectSpace(self):
        """
        Add a space character to Buffer
        """
        self.Buffer.append(' ')

    def Extend(self,List):
        """
        Add the passed list to the buffer
        """
        #trim any trailing whitespace from List without hurting tags.
        ##D( '+++',List)
        assert type(List) == type([])
        Seq = range(len(List))
        Seq.reverse()
        for J in Seq:
            C = List[J]
            if C == ' ' or C == '\n':
                #trim trailing whitespace
                List.pop(J)
            elif type(C) == type(0) or len(C) == 1:
                #any image or non-whitespace non-tag ends the process
                break
        #trim leading whitespace from List without hurting tags.
        White = []
        for J in range(len(List)):
            C = List[J]
            #D('C=<%s>'%str(C))
            if type(C) == type(0) or (len(C) == 1 and not C in (' ','\n')):
                #we've run out of whitespace
                break
            if len(List[J]) == 1:
                White.append(J)
        White.reverse()
        for J in White:
            List.pop(J)            
        #print 'Buffer now %s'%self.Buffer
        self.Buffer.extend(List)

    def ListPush(self,Value,TypeOfList,NumerOrigin):
        """
        Push a value onto the list.
        
        Each list entry is a list thus:
        [0] The list type. 1 for bulleted, 2 for numerated, 3 for tabbed
        [1] The next enumeration value to use
        [2] The saved value of InsertPoint
        """
        assert TypeOfList in (1,2,3)
        self.ListList.append([TypeOfList,NumerOrigin,Value])
        #print 'PUSH %s'%self.ListList

    def ListPop(self):
        """
        Pop the enumeration list and return the new last entry. If the list is now
            empty, we return None.
        """
        self.ListList.pop()
        #print 'POP  %s'%self.ListList
        return self.ListLast()

    def ListLast(self):
        """
        Return the last item in the list, or None if the list is empty.
        """
        if self.ListList:
            return self.ListList[-1][2]
        else:
            return None    

    def NonEmpty(self):
        """
        Return 1 if the buffer is non-empty.
        
        Non-empty means it contains at least one CHARACTER or a Photo. For our present purpose
            tags are not counted. I'm not sure we will ever get a buffer containing
            nothing but tags, but I'm being careful.
        """
        for C in self.Buffer:
            if type(C) == type(0) or len(C) == 1:
                return 1
        return 0
                        
    def EmitNonEmpty(self):
        """
        If buffer is non-empty issue it plus a newline.
        
        Non-empty means it contains at least one CHARACTER. For our present purpose
            tags are not counted. I'm not sure we will ever get a buffer containing
            nothing but tags, but I'm being careful.
        """
        if self.NonEmpty():
            #we found an actual character; honk out the buffer
            self.Emit()

    def NumerNext(self,N):
        """
        Given a numer value return the next value.
        
        The sequences go something like this:
        
            0       A       a
            ~       ~       ~
            9       Z       z
            10      AA      aa
            ~       ~       ~
            19      AZ      az
            20      BA      ba
            ~       ~       ~        
            29      BZ      bz
        """
        try:
            N = int(N)
            #it's numeric
            return str(N + 1)
        except ValueError:
            #it's alpha
            if N[0] < '^':
                #It's upper case alpha
                Max = 'Z'
                Min = 'A'
            else:
                #Lower case
                Max = 'z'
                Min = 'a'  
            N = list(N)
            Indices = range(len(N))
            Indices.reverse()
            for I in Indices:
                if N[I] < Max:
                    N[I] = chr(ord(N[I])+1)
                    break
                else:
                    N[I] = Min
            else:
                N.append(Min)
            return ''.join(N)
    
    def Emit(self):
        """
        Emit whatever text is in buffer plus a newline.
        """
        #Build whatever tag we need for the text in buffer based on our
        #    current list state.
        ##D('About to emit buffer. ListList=%s'%self.ListList)
        #Note: the indicator character ('o' for bulleted, 'n' for numerated and 't' for tabbed)
        #    is *usually* but not always the first item in the buffer. However, there are
        #    some instances where buffer opens with a tag. Therefore we go looking for the
        #    indicator character rather than assuming it is first.
        if self.BulletLine == 1:
            #Bulleted; inject font stuff so the bullet stands out
            I = self.Buffer.index('o')
            self.Buffer[I:I+2] = ['&push','FixedBold','o',' ','&pop']
        if self.BulletLine == 2:
            #print 'Numerated %s'%self.Buffer
            #Numerated. Stuff the number into the line
            I = self.Buffer.index('n')
            self.Buffer[I:I+1] = list(str(self.ListList[-1][1])+')')
            #advance the numerator
            self.ListList[-1][1] = self.NumerNext(self.ListList[-1][1])
                
        elif self.BulletLine == 3:
            #Tabbed. Get rid of the t and the blank from front of line
            I = self.Buffer.index('t')
            self.Buffer[I:I+2] = []    
        ##D('Emit: Buffer=%s'%self.Buffer)    
        self.Buffer.append('\n')
        if self.ListList:
            #we are inside a list
            Value = self.ListList[-1][2]
            Type = self.ListList[-1][0]
            assert Type in (1,2,3)
            if Type in (1,3):
                #bulleted or tabbed line
                Indent = self.BulletIndent
            elif Type == 2:
                #Numerated line
                Indent = self.NumberIndent
            elif Type == 3:
                #tabbed line
                Indent = self.BulletIndent    
            #print 'Type=%s  Indent=%s'%(Type,Indent)
                
            if self.BulletLine in (1,2):
                #this line has a bullet or number
                Value 
                Tag = 'T%sa'%Value #this gives us a unique tag for each indentation depth
                LM1 = Value * Indent
                LM2 = LM1 + Indent
            else:
                #this is a second or greater line in a list, or a tabbed line
                Tag = 'T%sb'%Value
                LM1 = LM2 = (Value + 1) * Indent
            self.TextWidget.tag_config(Tag, lmargin1=LM1, lmargin2=LM2) 
            #print 'LM1=%s LM2=%s'%(LM1, LM2)
        else:
            #we are not inside a bulleted list
            Tag = ''
        #Now actually issue the text. Everything in Buffer is subject to the Tag we just
        #   finished building. However, there will also be tags in buffer and when we come
        #   across them we have to do an insert with the combined tags. Note that the tags
        #   in Buffer are prefixes. Thus we would receive the word 'zot' in bold followed 
        #   by normal text as ['Bold','z','o','t','']. Thus we keep track of the running
        #   tag and issue a blast of text when the tag changes.
        Text = []
        #There are times when we want to temporarily change the font (eg to make the bullet
        #    character unique) but we also don't want to mess up the authors chosen font
        #    either. For this we used the special tags '&push' and '&pop' which cause us
        #    to push/pop RunningTag information. This usage is purely local to this 
        #    particular method. At the end of this method the stack should be empty.
        ##D('Tag=%s'%Tag)
        TagStack = []
        for C in self.Buffer:
            if type(C) == type(0):
                #We have an image; issue any accumulated text first
                if Tag <> '' and self.RunningTag <> '':
                    CombinedTag = '%s %s'%(Tag, self.RunningTag)
                else:
                    CombinedTag = Tag + self.RunningTag
                self.TextWidget.insert(INSERT,''.join(Text),CombinedTag)
                Text = []
                self.TextWidget.image_create(INSERT,image=self.PhotoList[C],align=BASELINE)
            elif len(C) <> 1:
                ##D('C=%s RunningTag=%s'%(C,self.RunningTag))
                if C == '&push':
                    TagStack.append(self.RunningTag)
                    continue
                #we have a tag; must issue
                if Tag <> '' and self.RunningTag <> '':
                    CombinedTag = '%s %s'%(Tag, self.RunningTag)
                else:
                    CombinedTag = Tag + self.RunningTag    
                ##D('Inserting Text=<%s> Tags=<%s>'%(''.join(Text),CombinedTag))
                self.TextWidget.insert(INSERT,''.join(Text),CombinedTag)
                if C[0:1] <> '&':       
                    self.RunningTag = C
                    ##D('C=%s RunningTag=%s'%(str(C),str(self.RunningTag)))
                if C == '&pop':
                    self.RunningTag = TagStack.pop()    
                    ##D('Pop; RunningTag=%s'%str(self.RunningTag))
                Text = []
            else:
                Text.append(C)    
        if Text:        
            ##D('Tag=%s, RunningTag=%s'%(str(Tag),str(self.RunningTag)))
            if Tag <> '' and self.RunningTag <> '':
                CombinedTag = '%s %s'%(Tag, self.RunningTag)
            else:
                CombinedTag = Tag + self.RunningTag    
            ##D('Inserting Text=<%s> Tags=<%s>'%(''.join(Text),CombinedTag))
            self.TextWidget.insert(INSERT,''.join(Text),CombinedTag)
        self.Buffer = []
        self.BulletLine = 0    
        assert len(TagStack) == 0
        
if __name__ == '__main__':

    Root = Tk()
    
    #Set Filename to None to prompt for a filename.
    Filename = None    
    
    if not Filename:
        #If we don't yet have a filename prompt the user for one
        Filename = PromptDialog(Message='Specify HelpFile to work on',Prompt='help.help').Result
        
    if Filename:
        #Startup only if we got a filename
        Help = TheHelpThingy(Path=Filename,OfferCompiler=True)
        if Help.Topics <> None:
            #The help file exists or was created
            HelpComp = HelpCompiler(Help,Root)
    
            Root.mainloop()        