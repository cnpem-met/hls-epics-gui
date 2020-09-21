# HLS-EpicsGUI

Client-type GUI program for visualization and controlling of the HLS Epics IOC running in the same network. 
The program is based on the PyDM package, which uses the PyQT5 package for creating the visual content.

## Dependencies

As mentioned, PyDM is required for the program to run. For a complete setup usind Anaconda, run the following commands:

`cd HLS-EpicsGUI`
`conda env create --prefix ./hlsGUI-env -f requirements.yml`

## Running

Once all the dependencies were installed in the 'hlsGUI-env' dir, you can activate it and run the program:

`conda activate ./hlsGUI-env`
`python GUI-HLS.py` 
