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
*needs* to be touched in order for Rapyd to work. As delivered, the Rapyd code
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

Note that projects produced by Rapyd rely on module "rpErrorHandler.py"
to gracefully handle error reports in a Rapyd-aware manner. Once a
project  which was developed using Rapyd is done and working, it can be
run directly  without need of Rapyd itself, but the module
"rpErrorHandler" *is* required  and should be available. Also required
is the file "<project-name>.dec" which is generated when your project is
built. This text file contains the information needed so rpErrorHandler
can relate error line numbers back to Rapyd project related
module/form/line format. Projects will run without this file but error
report will be less meaningful. 