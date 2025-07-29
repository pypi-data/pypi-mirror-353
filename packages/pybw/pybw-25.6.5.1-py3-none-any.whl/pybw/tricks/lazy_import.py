# -*- coding: utf-8 -*-
# function: lazy import


## ------ System ------
import os
import sys
import gc
import inspect
import copy
import shutil
import time
# from datetime import datetime
from glob import glob
from pathlib import Path

try:
    from dotted_dict import DottedDict
except:
    pass


## ------ System Pro ------
import _pickle as pickle

try:
    from tqdm import tqdm
except:
    pass

try:
    from joblib import Parallel, delayed
except:
    pass

# try:
    # from func_timeout import func_set_timeout, func_timeout
# except:
    # pass


## ------ Data Analysis ------
import re
import random
from configparser import ConfigParser

try:
    import json
except:
    pass

try:
    import yaml
except:
    pass

try:
    from prettytable import PrettyTable
except:
    pass

try:
    import numpy as np
except:
    pass

try:
    import pandas as pd
except:
    pass

# try:
    # import polars as pl
# except:
    # pass

try:
    import matplotlib.pyplot as plt
    # import scienceplots
    
    plt.ion()

    """
    # plt.style.use('ggplot')
    plt.style.use('default')
    
    # colors_ggplot = plt.style.library['ggplot']['axes.prop_cycle']
    plt.rcParams['axes.prop_cycle'] = plt.style.library['ggplot']['axes.prop_cycle']

    # plt.rcParams['mathtext.fontset'] = 'dejavusans'
    # plt.rcParams['font.family'] = ['Arial']
    # plt.rcParams['font.family'] = ['sans-serif']
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_minus'] = False
    
    plt.rcParams.update({
        'text.color'       : 'black',
        'axes.labelcolor'  : 'black',
        'axes.titlecolor'  : 'black',
        'xtick.color'      : 'black',
        'ytick.color'      : 'black',
        
        'font.size'        : 20,
        'font.family'      : ['Microsoft YaHei'],
        
        'lines.linewidth'  : 2,
        'lines.markersize' : 6,
        
        'legend.frameon'   : False,     # 图例边框
    })
    """
        
    
except:
    pass

try:
    import seaborn as sns
except:
    pass


## ------ Scientific Calculation ------
import math
from decimal import Decimal


## ------ Audio Video ------
# from moviepy.editor import VideoFileClip, AudioFileClip


## ------ pybw ------
from pybw.core import *


