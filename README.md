GNXEdit
=======

Editor and Librarian for Digitech GNX1
--------------------------------------

Application Help File
---------------------

**TABLE OF CONTENTS**

*   [Information](#information)
*   [Introduction](#introduction)
*   [System Exclusive](#system_exclusive)
*   [Installation](#installation)
    *   [Windows](#installation_windows)
    *   [Linux (Ubuntu)](#installation_linux)
*   [Getting Started](#getting_started)
*   [Status Indication](#status_indication)
    *   [Current Patch](#status_indication_current_patch)
    *   [Connected Indicator](#status_indication_connected_indicator)
    *   [MIDI Channel](#status_indication_midi_channel)
    *   [Watchdog](#status_indication_watchdog)
    *   [Resync](#status_indication_resync)
    *   [Uploading](#status_indication_uploading)
*   [Library Functions](#library_functions)
    *   [GNX Patch Selection](#library_functions_gnx_patch_selection)
    *   [Creating Library Categories](#library_functions_creating_library_categories)
    *   [Saving Patches To Library Categories](saving_patches_to_library_categories)
    *   [Saving Patches To GNX1](#library_functions_saving_patches_to_gnx1)
*   [Resync](#resync)  
    

### Information

[Back to Top](#toc)

> Version: 1.0, 11 January, 2025
> 
> Copyright © 2025 Gary Barnes (gary-1959). All rights reserved.
> 
> This software and its source code is made freely available under the GNU General Public License version 3.
> 
> More details at: [https://opensource.org/license/gpl-3-0'](https://opensource.org/license/gpl-3-0)
> 
> Source Code: [https://github.com/gary-1959/GNXEdit](https://github.com/gary-1959/GNXEdit)

### Introduction

[Back to Top](#toc)

> GNXEdit is an editor and librarian program for use with the DigiTech GNX1 guitar effects processor.
> 
> The functionality of the program is similar to the DigiTech GENEdit program for Windows, but includes enhanced library functionality and is cross-platform (Windows and Linux).
> 
> The program is written in Python and leverages the QT GUI framework. It iscompletely open source and freely available at [https://github.com/gary-1959/GNXEdit](https://github.com/gary-1959/GNXEdit).
> 
> A detailed description of the operation of the Digitech GNX1 is beyond the scope of this HELP page, but a good understanding of how it works is essential for gaining maximum benefit from GNXEdit. A copy of the user manual is available by [clicking here](file://C:\Users\garyb\Projects\GNXEdit\documents/digitech-gnx1-user-manual.pdf).

### System Exclusive

[Back to Top](#toc)

> There was no information available from DigiTech detailing the System Exclusive commands, so to write the program the System Exclusive protocol had to be reverse engineered by snooping on communications between the GENEdit program and a GNX1 device. This work has been documented separately and is available in another GitHub repository: [https://github.com/gary-1959/Digitech-GNX1-System-Exclusive](https://github.com/gary-1959/Digitech-GNX1-System-Exclusive).
> 
> There are gaps in this knowledge and any contribution to filling these gaps (or errors) will be most gratefully received and incorporated imto the document.

### Installation

[Back to Top](#toc)

> #### Windows
> 
> 1.  Download and install Python (minimum version 13.2) if not already installed from [https://www.python.org/downloads/windows](https://www.python.org/downloads/windows)
> 2.  If you are familiar with GitHub CLI or GitHub Desktop, use this to clone the repository [at https://github.com/gary-1959/GNXEdit](https://github.com/gary-1959/GNXEdit).  
>     If not, download the repository from [https://github.com/gary-1959/GNXEdit/archive/refs/heads/main.zip](https://github.com/gary-1959/GNXEdit/archive/refs/heads/main.zip) and unzip (extract) it into a location of your choice. This folder can be located anywhere in your system.
> 3.  Open a command terminal and cd into this folder. You should see a folder named "src".
> 4.  Python works best when applications are run in their own dedicated environment. A Python environment is simply a folder which contains the main Python program and all the dependant libraries. Create an environment with the following command: `python -m venv .venv` Select the version 13.2 (or later) Python interpreter if prompted.
> 5.  Activate the Python environment with the following command (note the dot before venv):`.venv\Scripts\activate`You should now see (.venv) at the start of the command prompt, indicating that the environment has been activated.
> 6.  Install the dependant libraries with the command `pip install -r src\requirements.txt`
> 7.  Check the program runs with the command: `src\main.py`
> 8.  To run the program in its correct environment a batch file is available in the src folder of the GNXEdit folder, which can be run from a desktop icon. To create a desktop icon:
>     1.  Open File Explorer and navigate to the GNXEdit src folder. Right-click on the file named _**GNXEdit.bat**_ and select_**  
>         Send to > Desktop (create shortcut)**_.
>     2.  Close File Explorer then right-click on the newly created desktop icon.and select **_Properties._**  
>         Click _**Change Icon...**_ followed by _**OK**_ .
>     3.  Click the _**Browse..**_ option in the dialog that opens then navigate to the GNXEdit src folder where you will find a GNXEdit.ico file. Select this file, click _**OK**_ (then _**OK**_ again), to exit the Properties dialog. The desktop icon will now be set.
> 9.  This completes the Windows installation. The most convenient way to update the program to new versions is through the GitHub Desktop program, or download the zip file from the repository then extract and overwrite the program files. Your library data and configuration is stored in your home folder and will be preserved.
> 10.  To uninstall the program simply delete the GNXEdit folder containing the program files. To remove your library and configuration data as well, navigate to your home folder. Locate the AppData\\Local\\GNXEdit folder and delete it.
> 
> #### Linux (Ubuntu)
> 
> 1.  Install Python (minimum version 13.2) if not already installed using the package manager of your choice, e.g: `sudo apt install python`
> 2.  If you are familiar with GitHub CLI or GitHub Desktop, use this to clone the repository [at https://github.com/gary-1959/GNXEdit](https://github.com/gary-1959/GNXEdit).  
>     If not, download the repository from [https://github.com/gary-1959/GNXEdit/archive/refs/heads/main.zip](https://github.com/gary-1959/GNXEdit/archive/refs/heads/main.zip) and unzip (extract) it into a location of your choice. This folder can be located anywhere in your system.
> 3.  Open a command terminal and cd into this folder. You should see a folder named "src".
> 4.  Python works best when applications are run in their own dedicated environment. A Python environment is simply a folder which contains the main Python program and all the dependant libraries. Create an environment with the following command: `python3 -m venv .venv` Select the version 13.2 (or later) Python interpreter if prompted.
> 5.  Activate the Python environment with the following command (note the dot before venv):`source .venv/bin/activate`You should now see (.venv) at the start of the command prompt, indicating that the environment has been activated.
> 6.  Install the dependant libraries with the command `pip install -r src/requirements.txt`
> 7.  Check the program runs with the command: `python src/main.py`
> 8.  Deactivate the environment with the command `deactivate`
> 9.  To run the program from the command line in its correct environment:`cd <path to your GNXEdit folder>; .venv/bin/python src/main.py`
> 10.  It is far easier to launch the program from a desktop icon. A prototype desktop icon (for Ubuntu/Gnome Desktop systems) is available in the GNXEdit src folder called GNXEdit.desktop. Copy this file to your desktop and edit with the text editor of your choice and insert the correct paths in the lines hightlighted in the file, and save it.
> 11.  On the desktop, right-click on the file icon and click _**Allow Launching**_.
> 12.  Right-click the icon again, select _**Properties**_ then click _**Executable as Program**_ on.
> 13.  The icon should change to the GNXEdit icon. If not, check the path names are correct.
> 14.  Double-click the icon to check the program runs.
> 15.  For Linux systems other than Ubuntu/Gnome Desktop please check the procedure for creating desktop icons.

### Getting Started

[Back to Top](#toc)

> Familiarity with the features of the GNX1 is essential to gain maximum benefit from using GNXEdit. This is beyond the scope of this HELP page but is well covered in the User Manual. A copy of the user manual is available by [clicking here](file://C:\Users\garyb\Projects\GNXEdit\documents/digitech-gnx1-user-manual.pdf).
> 
> Getting started with GNXEdit involves connecting the GNX1 device to your computer via MIDI, then setting GNXEdit to use the same MIDI ports.
> 
> 1.  Make sure the GNX1 device is turned off and connect up your MIDI interface and cables.
> 2.  Start up GNXEdit and from the menu select _**MIDI Interface**_.
> 3.  Select the MIDI input and output ports which the GNX1 is connected to.
> 4.  GNXEdit will find the MIDI channel which your GNX1 is using automatically, but if you want to specify a specific channel for any reason select it under _**Lock to Channel**_.
> 5.  Click _**OK**_ to close the dialog.
> 6.  Turn on your GNX1 device and after a few seconds, all being well, GNXEdit will synchronise to the currently selected patch. You may see a spurious System Exclusive error. Clear this by clicking _**OK** in the error message box._
> 7.  Begin editing the patch by adjusting parameters on the screen.

### Status Indication

[Back to Top](#toc)

> The status bar at the foot of the screen gives information about the current status of GNXEdit:
> 
> ##### Current Patch
> 
> Contains details of the current patch name, bank (USER or FACTORY) and patch number. This will be synchronised to your GNX1 device
> 
> ##### Connected Indicator
> 
> A green disc indicates that GNXEdit is connected to a GNX1 device. A red disc indicates no nonnection
> 
> ##### MIDI Channel
> 
> The current MIDI channel is indicated (1 - 16)
> 
> ##### Watchdog
> 
> GNXEdit has an internal watchdog which repeatedly checks the connection status. This will be grayed out during normal operation. If the GNX1 device becomes disconnected, the watchdog will "bite", turning th WATCHDOG legend red, and GNXEdit will initiate a rerconnection protocol.
> 
> ##### Resync
> 
> The status bar RESYNC indicator is normally grayed out, but will turn green when a GNXEdit is trying to synchronise withyour GNX1.
> 
> ##### Uploading
> 
> The process of uploading a patch from the GNXEdit library to the connected device is indicated with the UPLOADING indicator. Normally grayed out, when an upload is in progress this indicator will turn green and also indicate the stage number of the upload process.

### Library Functions

[Back to Top](#toc)

> The GNXEdit left-hand panel is an expandable tree which displays all the patches available in the GNX1 device user and factory banks and custom patches which arer held in a database.
> 
> Patches can be organised into separate folders and sub-folders (categories). Patches can be transferred on an individual basis between the library and your GNX1 device.
> 
> ##### GNX Patch Section
> 
> To expand the GNX section click on the adjacent arrow in the library pane. To view the factory or usr patches click their adjacent arrow. Patches are selected by simply clicking the patch name, which will automatically change the patch on your GNX1 device.
> 
> **CAUTION**: this will erase any edits you may have made to the previously selected patch in your GNX1, so be sure to save any edits.
> 
> ##### Creating Library Categories
> 
> To create your first library category right-click the LIBRARY header in the left hand pane. Select _**Add Category**_ from the menu and enter a name for the category in the dialog box. Click _**OK**_. This will add your category to the library root level. Further categories can be created at the same level, or sub-categories can be added to those you have created to create a tree structure. Category names can be any length.
> 
> ##### Saving Patches To Library Categories
> 
> Once you have ceated a new patch which you would like to add to your library select _**Device>Save Patch to Library**_ from the GNXEdit main menu. In the dialog select the location from the library tree where you want to save your patch. You can enter a new name and add a description or tags. Click on _**OK**_ to save the patch. Note that names are limited to 6 characters.
> 
> **CAUTION**: this will save the patch with the new name in the GNX1 location you were editing.
> 
> ##### Saving Patches To GNX1
> 
> When you are happy with your new patch you can save it into any one of the GNX1 user memory locations (1 - 48) by selecting _**Device>Save Patch**_ to User Bank from the GNXEdit main menu. Select the patch location in the dialog, and change the name if you want to. Names are limited to 6 characters. Click on _**OK**_ to confirm.
> 
> **CAUTION**: this will overwrite the patch in the location you selected.

### Resync

[Back to Top](#toc)

> If you find GNXEdit is out of sync with your GNX1 click _**Device>Resync**_ in the GNXEdit main menu. GNXEdit will now correctly match the contents of the GNX1 edit buffer.
