#!/usr/bin/env python3

# Description
###############################################################################
'''
Sets of classes and functions that are used to prepare Dock6 files and run it.

They are imported as:

import OCDocker.Docking.Dock6 as ocdock6
'''
# TODO: Finish this
# Imports
###############################################################################
import errno
import json
import os

import numpy as np

from glob import glob
from typing import Dict, List, Tuple, Union

from OCDocker.Initialise import *

import OCDocker.Ligand as ocl
import OCDocker.Receptor as ocr
import OCDocker.Toolbox.Conversion as occonversion
import OCDocker.Toolbox.FilesFolders as ocff
import OCDocker.Toolbox.IO as ocio
import OCDocker.Toolbox.MoleculeProcessing as ocmolproc
import OCDocker.Toolbox.Printing as ocprint
import OCDocker.Toolbox.Running as ocrun
import OCDocker.Toolbox.Validation as ocvalidation

# License
###############################################################################
'''
OCDocker
Authors: Rossi, A.D.; Torres, P.H.M.
Federal University of Rio de Janeiro
Carlos Chagas Filho Institute of Biophysics
Laboratory for Molecular Modeling and Dynamics

Licensed under the Apache License, Version 2.0 (January 2004)
See: http://www.apache.org/licenses/LICENSE-2.0

Commercial use requires a separate license.  
Contact: Artur Duque Rossi - arturossi10@gmail.com
'''

# Classes
###############################################################################
class Ledock:
    """ Ledock object with methods for easy run. """

    def __init__(self, configPath: str, boxFile: str, receptor: ocr.Receptor, preparedReceptorPath: str, ligand: ocl.Ligand, preparedLigandPath: str, ledockLog: str, outputLedock: str, name: str = "", overwriteConfig: bool = False, spacing: float = 2.9) -> None:
        '''Constructor of the class Ledock.
        
        Parameters
        ----------
        configPath : str
            The path for the config file.
        boxFile : str
            The path for the box file.
        receptor : ocr.Receptor
            The receptor object.
        preparedReceptorPath : str
            The path for the prepared receptor.
        ligand : ocl.Ligand
            The ligand object.
        preparedLigandPath : str
            The path for the prepared ligand.
        ledockLog : str
            The path for the Ledock log file.
        outputLedock : str
            The path for the Ledock output files.
        name : str, optional
            The name of the Ledock object, by default "".
        spacing : float, optional
            The spacing between to expand the box, by default 2.9.

        Returns
        -------
        None
        '''

        pass