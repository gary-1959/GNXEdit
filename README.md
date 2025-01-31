



GNXEdit Help File


GNXEdit
=======

Editor and Librarian for Digitech GNX1
--------------------------------------

Application Help File
---------------------

**TABLE OF CONTENTS**

* [Information](#a0 "#a0")
* [Introduction](#a1 "#a1")
* [System Exclusive](#a2 "#a2")
* [Installation](#a3 "#a3")
* [Windows](#a4 "#a4")
* [Linux (Ubuntu)](#a5 "#a5")
* [Getting Started](#a6 "#a6")
* [Status Indication](#a7 "#a7")
* [Current Patch](#a8 "#a8")
* [Connected Indicator](#a9 "#a9")
* [MIDI Channel](#a10 "#a10")
* [Watchdog](#a11 "#a11")
* [Resync](#a12 "#a12")
* [Uploading](#a13 "#a13")
* [Library Functions](#a14 "#a14")
* [GNX Patch Section](#a15 "#a15")
* [Creating Library Categories](#a16 "#a16")
* [Saving Patches To Library Categories](#a17 "#a17")
* [Saving Amp/Cab Configurations To Library Categories](#a18 "#a18")
* [Saving Patches To GNX1](#a19 "#a19")
* [Saving Amp/Cab Patches To GNX1](#a20 "#a20")
* [Transferring Patches To GNX1 From The Library](#a21 "#a21")
* [Changing Patch and Category Names](#a22 "#a22")
* [Library Cut, Copy, Paste and Delete](#a23 "#a23")
* [Search Library](#a24 "#a24")
* [Editing Amps and Cabs](#a25 "#a25")
* [Warping Amp And Cabinet Models](#a26 "#a26")
* [Editing Effects](#a27 "#a27")
* [Resync](#a28 "#a28")
* [GNXEdit Rack Image](#a29 "#a29")

### Information
[Back to Top](#toc "#toc")
> Version: 1.0, 11 January, 2025
> 
> Copyright © 2025 Gary Barnes (gary-1959). All rights reserved.
> 
> This software and its source code is made freely available under the GNU General Public License version 3.
> 
> More details at: [https://opensource.org/license/gpl-3-0'](https://opensource.org/license/gpl-3-0 "https://opensource.org/license/gpl-3-0")
> 
> Source Code: [https://github.com/gary-1959/GNXEdit](https://github.com/gary-1959/GNXEdit "https://github.com/gary-1959/GNXEdit")

### Introduction
[Back to Top](#toc "#toc")
> GNXEdit is an editor and librarian program for use with the DigiTech GNX1 guitar effects processor.
> 
> The functionality of the program is similar to the DigiTech GENEdit program for Windows,
> but includes enhanced library functionality and is cross-platform (Windows and Linux).
> 
> The program is written in Python and leverages the QT GUI framework. It is completely open source and freely
> available at [https://github.com/gary-1959/GNXEdit](https://github.com/gary-1959/GNXEdit "https://github.com/gary-1959/GNXEdit").
> 
> A detailed description of the operation of the DigiTech GNX1 is beyond the scope of this HELP page,
> but a good understanding of how it works is essential for gaining maximum benefit from GNXEdit.
> A copy of the user manual is available by
> [clicking here](file:///home/gary/Projects/GNXEdit/documents/digitech-gnx1-user-manual.pdf "file:///home/gary/Projects/GNXEdit/documents/digitech-gnx1-user-manual.pdf").

### System Exclusive
[Back to Top](#toc "#toc")
> There was no information available from DigiTech detailing the System Exclusive commands, so to write
> the program the System Exclusive protocol had to be reverse engineered by snooping on communications
> between the GENEdit program and a GNX1 device. This work has been documented separately
> and is available in another GitHub repository: [https://github.com/gary-1959/Digitech-GNX1-System-Exclusive](https://github.com/gary-1959/Digitech-GNX1-System-Exclusive "https://github.com/gary-1959/Digitech-GNX1-System-Exclusive").
> 
> There are gaps in this knowledge and any contribution to filling these gaps (or errors) will be
> most gratefully received and incorporated into the document.

### Installation
[Back to Top](#toc "#toc")
> #### Windows
> 
> 1. Download and install Python (minimum version 13.2) if not already installed from
>    [https://www.python.org/downloads/windows](https://www.python.org/downloads/windows "https://www.python.org/downloads/windows")
> 2. If you are familiar with GitHub CLI or GitHub Desktop, use this to clone the repository at [https://github.com/gary-1959/GNXEdit](https://github.com/gary-1959/GNXEdit "https://github.com/gary-1959/GNXEdit").  
>    
>    If not,
>    download the repository from [https://github.com/gary-1959/GNXEdit/archive/refs/heads/main.zip](https://github.com/gary-1959/GNXEdit/archive/refs/heads/main.zip "https://github.com/gary-1959/GNXEdit/archive/refs/heads/main.zip") and unzip (extract) it into a location of your choice.
>    This folder can be located anywhere in your system.
> 3. Open a command terminal and cd into this folder. You should see a folder named "src".
> 4. Python works best when applications are run in their own dedicated environment. A Python environment
>    is simply a folder which contains the main Python program and all the dependant libraries. Create an environment with the following command:
>    ```
>    python -m venv .venv
>    ```
>    Select the version 13.2 (or later) Python interpreter if prompted.
> 5. Activate the Python environment with the following command (note the dot before venv):
>    ```
>    .venv\Scripts\activate
>    ```
>    You should now see (.venv) at the start of the command prompt, indicating that the environment has been activated.
> 6. Install the dependant libraries with the command
>    ```
>    pip install -r src\requirements.txt
>    ```
> 7. Check the program runs with the command:
>    ```
>    src\main.py
>    ```
> 8. To run the program in its correct environment a batch file is available in the src folder of the GNXEdit folder, which can be run from a desktop icon.
>    To create a desktop icon:
>    1. Open File Explorer and navigate to the GNXEdit src folder. Right-click on the file named ***GNXEdit.bat*** and select  ***Send to > Desktop (create shortcut)***.
>    2. Close File Explorer then right-click on the newly created desktop icon and select ***Properties.***   
>       
>       Click ***Change Icon...*** followed by ***OK*** .
>    3. Click the ***Browse..*** option in the dialog that opens then navigate to the GNXEdit src folder where you will find a GNXEdit.ico file. Select this file, click ***OK*** (then ***OK*** again), to exit the Properties dialog. The desktop icon will now be set.
> 9. This completes the Windows installation. The most convenient way to update the program to new versions is through the GitHub Desktop program, or download the zip file from the repository then extract and overwrite the program files. Your library data and configuration is stored in your home folder and will be preserved.
> 10. To uninstall the program simply delete the GNXEdit folder containing the program files. To remove your library and configuration data as well, navigate to your home folder. Locate the AppData\Local\GNXEdit folder and delete it.
> 
> #### Linux (Ubuntu)
> 
> 1. Install Python (minimum version 13.2) if not already installed using the package manager of your choice, e.g.:
>    ```
>    sudo apt install python
>    ```
> 2. If you are familiar with GitHub CLI or GitHub Desktop, use this to clone the repository at [https://github.com/gary-1959/GNXEdit](https://github.com/gary-1959/GNXEdit "https://github.com/gary-1959/GNXEdit").  
>    
>    If not,
>    download the repository from [https://github.com/gary-1959/GNXEdit/archive/refs/heads/main.zip](https://github.com/gary-1959/GNXEdit/archive/refs/heads/main.zip "https://github.com/gary-1959/GNXEdit/archive/refs/heads/main.zip") and unzip (extract) it into a location of your choice.
>    This folder can be located anywhere in your system.
> 3. Open a command terminal and cd into this folder. You should see a folder named "src".
> 4. Python works best when applications are run in their own dedicated environment. A Python environment
>    is simply a folder which contains the main Python program and all the dependant libraries. Create an environment with the following command:
>    ```
>    python3 -m venv .venv
>    ```
>    Select the version 13.2 (or later) Python interpreter if prompted.
> 5. Activate the Python environment with the following command (note the dot before venv):
>    ```
>    source .venv/bin/activate
>    ```
>    You should now see (.venv) at the start of the command prompt, indicating that the environment has been activated.
> 6. Install the dependant libraries with the command
>    ```
>    pip install -r src/requirements.txt
>    ```
> 7. Check the program runs with the command:
>    ```
>    python src/main.py
>    ```
> 8. Deactivate the environment with the command
>    ```
>    deactivate
>    ```
> 9. To run the program from the command line in its correct environment:
>    ```
>    cd <path to your GNXEdit folder>; .venv/bin/python src/main.py
>    ```
> 10. It is far easier to launch the program from a desktop icon. A prototype desktop icon (for Ubuntu/Gnome Desktop systems) is available in the GNXEdit src folder called GNXEdit.desktop.
>     Copy this file to your desktop and edit with the text editor of your choice and insert the correct paths in the lines highlighted in the file, and save it.
> 11. On the desktop, right-click on the file icon and click ***Allow Launching***.
> 12. Right-click the icon again, select ***Properties*** then click ***Executable as Program*** on.
> 13. The icon should change to the GNXEdit icon. If not, check the path names are correct.
> 14. Double-click the icon to check the program runs.
> 15. For Linux systems other than Ubuntu/Gnome Desktop please check the procedure for creating desktop icons.

### Getting Started
[Back to Top](#toc "#toc")
> Familiarity with the features of the GNX1 is essential to gain maximum benefit from using GNXEdit. This is beyond the scope of this
> HELP page but is well covered in the User Manual. A copy of the user manual is available by
> [clicking here](file:///home/gary/Projects/GNXEdit/documents/digitech-gnx1-user-manual.pdf "file:///home/gary/Projects/GNXEdit/documents/digitech-gnx1-user-manual.pdf").
> 
> Getting started with GNXEdit involves connecting the GNX1 device to your computer via MIDI, then setting GNXEdit to use the same MIDI ports.
> 
> 1. Make sure the GNX1 device is turned off and connect up your MIDI interface and cables.
> 2. Start up GNXEdit and from the menu select ***MIDI Interface***.
> 3. Select the MIDI input and output ports which the GNX1 is connected to.
> 4. GNXEdit will find the MIDI channel which your GNX1 is using automatically, but if you want to specify a specific
>    channel for any reason select it under ***Lock to Channel***.
> 5. Click ***OK*** to close the dialog.
> 6. Turn on your GNX1 device and after a few seconds, all being well, GNXEdit will synchronise to the currently selected patch.
>    You may see a spurious System Exclusive error. Clear this by clicking ***OK** in the error message box.*
> 7. Begin editing the patch by adjusting parameters on the screen.

### Status Indication
[Back to Top](#toc "#toc")
> The status bar at the foot of the screen gives information about the current status of GNXEdit:
> 
> ##### Current Patch
> 
> Contains details of the current patch name, bank (USER or FACTORY) and patch number. This will be synchronised
> to your GNX1 device
> 
> ##### Connected Indicator
> 
> A green disc indicates that GNXEdit is connected to a GNX1 device. A red disc indicates no connection
> 
> ##### MIDI Channel
> 
> The current MIDI channel is indicated (1 - 16)
> 
> ##### Watchdog
> 
> GNXEdit has an internal watchdog which repeatedly checks the connection status. This will be grayed out during
> normal operation. If the GNX1 device becomes disconnected, the watchdog will "bite", turning the WATCHDOG legend red,
> and GNXEdit will initiate a reconnection protocol.
> 
> ##### Resync
> 
> The status bar RESYNC indicator is normally grayed out, but will turn green when a GNXEdit is trying to synchronise with your GNX1.
> 
> ##### Uploading
> 
> The process of uploading a patch from the GNXEdit library to the connected device is indicated with the UPLOADING indicator.
> Normally grayed out, when an upload is in progress this indicator will turn green and also indicate the stage number of
> the upload process.

### Library Functions
[Back to Top](#toc "#toc")
> The GNXEdit left-hand panel is an expandable tree which displays all the patches available in the GNX1 device User and Factory banks, and custom patches which are held in a database.
> 
> Patches can be organised into separate folders and sub-folders (categories). Patches can be transferred on an individual basis between the library and your GNX1 device.
> 
> ##### GNX Patch Section
> 
> To expand the GNX section click on the adjacent arrow in the library pane. To view the Factory or User patches click their adjacent arrow. Patches are selected by simply right-clicking the patch name, then clicking ***Select on GNX***. This action will erase any edits you may have made to the previously selected patch in your GNX1, so be sure to save any edits first. Select ***OK*** in warning dialog if it's OK to continue
> 
> ##### Creating Library Categories
> 
> To create your first library category right-click the LIBRARY header in the left hand pane. Select ***Add Category*** from the menu and enter a name for the category in the dialog box. Click ***OK***. This will add your category to the library root level. Further categories can be created at the same level, or sub-categories can be added to those you have created to create a tree structure. Category names can be any length (from 2 to 32 characters).
> 
> ##### Saving Patches To Library Categories
> 
> Once you have created a new patch which you would like to add to your library select ***Device>Save Patch to Library*** from the GNXEdit main menu. In the dialog select the location from the library tree where you want to save your patch. You can enter a new name and add a description or tags. Click on ***OK*** to save the patch. Note that library names are not limited to 6 characters, which allows more descriptive name.
> 
> This does not automatically save the patch to the GNX1 (see below)
> 
> ##### Saving Amp/Cab Configurations To Library Categories
> 
> If you have an amplifier and cabinet combination in a patch that you particularly like you can store it in the Library and
> add it into other patches. Both red and green amplifier and cabinet configurations are saved, together with the amp selection and warp settings.
> Select ***Device>Save Amp to Library*** from the GNXEdit main menu. In the dialog select the location from the library tree
> where you want to save your patch. You can enter a new name and add a description or tags.
> Click on ***OK*** to save the patch. Note that library names are not limited to 6 characters, which allows more descriptive name.
> 
> This does not automatically save the amp configuration in the current GNX1 patch. To save the entire patch (amp and effects) to the GNX1 see below.
> 
> ##### Saving Patches To GNX1
> 
> When you are happy with your new patch you can save it into any one of the GNX1 user memory locations (1 - 48) by selecting ***Device>Save Patch to User Bank*** from the GNXEdit main menu. Select the patch location in the dialog, and change the name if you want to. Names are limited to 6 characters. Click on ***OK*** to confirm.
> 
> **CAUTION**: this will overwrite the patch in the location you selected.
> 
> ##### Saving Amp/Cab Patches To GNX1
> 
> When you are happy with your new amp/cabinet setup you can save it into any one of 9 User amp locations in the GNX1 ***Device>Save Amp to User Amps*** from the GNXEdit main menu. Select the patch location in the dialog, and change the name if you want to. Names are limited to 6 characters. Click on ***OK*** to confirm.
> 
> After saving this way your User amp will also appear in the list of amplifier models available by right-clicking the green or red amplifier graphic in GNXEdit.
> 
> **CAUTION**: this will overwrite the patch in the location you selected.
> 
> ##### Transferring Patches To GNX1 From The Library
> 
> To transfer a patch from the Library right-click it in the Library and select ***Send Patch to GNX*** or ***Send Amp/Cab to GNX*** as applicable. A warning about overwriting the existing buffer will pop up because this action will replace the contents of the GNX1 edit buffer. To save permanently in a User Bank location in the GNX1 select ***Device>Save Patch to GNX*** from the menu, change the patch name if required and select the target location.
> 
> This means that patches and amp/cab configurations can be reviewed prior to saving without losing any of the GNX1 User patches
> 
> ##### Changing Patch and Category Names
> 
> To change a patch name in the tree double-click it. Factory patch names can not be changed. User patch names can only be edited if the patch is selected on the GNX1 device.
> 
> When Library patches or amps are selected in the tree a pop-up window allows the description and tags to be edited. Click ***Update*** to save the changes.
> 
> Alternatively, right-click on the patch or category and select ***Edit***. This also allows patch or amp descriptions and tags to be altered where applicable.
> 
> ##### Library Cut, Copy, Paste and Delete
> 
> Categories and patches in the Library area can be cut, copied, pasted and deleted by right-clicking and selecting the required option. If a category is selected to cut, copy or delete the action will be applied to the entire contents of the category.
> 
> These functions can not be applied to the User and Factory patch listings.
> 
> Drag and drop is not currently supported.
> 
> ##### Search Library
> 
> The Library can be searched can by entering search text in the Search Bar above the Library tree, This searches for the text you enter in patch names, description and tags.
> 
> For example, if you are looking for a patch which has 'blues' in the name, description or tags enter blues in the Search Bar and click the Search Button (spyglass). Any matching items will be displayed in a pop-up window. To navigate to the item, click the link in the results window.

### Editing Amps and Cabs
[Back to Top](#toc "#toc")
> The GNX1 has powerful amplifier and cabinet modelling algorithms. Each patch can have two amp/cab setups, which are labelled green and red. A third option is yellow, which is a blend of the green and red, a process known as 'warping'. The green, red or yellow amp models are selected by clicking the colourde buttons in the Warp module.
> 
> To select an amplifier model in GNXEdit, right-click the amplifier graphic to get a list of standard models and any User versions you may have created and stored in the GNX1. Click on your preferred model. This will also change the cabinet to a pre-determined match. You can alter the cabinet by similarly right-clicking on the graphic and selecting an alternative.
> 
> Amp parameters and cabinet tuning potentiometers can be altered either by clicking and dragging, by hovering the mouse pointer over the pot and using the mouse scroll wheel to scroll the value up or down, or simply left clicking at a point around the dial. Once a pot has been selected you can also use the up/down arrows on the computer keyboard to raise and lower values. Home, End, PgUp and PgDown keys are also effective.
> 
> All amp and cab parameters cause the GNX1 to display the parameter and value on its display as they are altered.

### Warping Amp And Cabinet Models
[Back to Top](#toc "#toc")
> With the yellow amp selected it is possible to blend the green and red models using the Warp module. You can warp between green and red amp models by dragging (or clicking) the cross-hair target in the Warp module up (green) or down (red). Similarly, you can warp between the green and red cabinet models by dragging (or clicking) the cross-hair target left (green) and right (red).

### Editing Effects
[Back to Top](#toc "#toc")
> The GNX1 effects are displayed as a virtual rack with modules for each function.
> 
> Buttons are 'pressed' by left-clicking. Potentiometers can be altered by clicking and dragging, by hovering the mouse pointer over the pot and using the mouse scroll wheel to scroll the value up or down, or simply left clicking at a point around the dial. Once a pot has been selected you can also use the up/down arrows on the computer keyboard to raise and lower values. Home, End, PgUp and PgDown keys are also effective.
> 
> Most parameters cause the GNX1 to display the parameter and value on its display as they are altered. Exceptions are the Expression and LFO modules.

### Resync
[Back to Top](#toc "#toc")
> If you find GNXEdit is out of sync with your GNX1 click ***Device>Resync*** in the GNXEdit main menu. GNXEdit will now correctly match the contents of the GNX1 edit buffer.

### GNXEdit Rack Image
[Back to Top](#toc "#toc")
> ![GNXEdit Rack](https://github.com/gary-1959/GNXEdit/blob/main/documents/GNXEdit_Rack.png?raw=true "GNXEdit Rack")



