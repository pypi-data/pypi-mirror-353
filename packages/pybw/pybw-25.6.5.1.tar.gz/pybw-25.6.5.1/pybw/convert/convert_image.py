# -*- coding: utf-8 -*-
"""
"""
from pathlib import Path
from PIL import Image



def convert_image(file_in, file_out=None, dpi=600):
    """
    """
    if not file_out:
        path_file_in = Path(file_in)
        file_stem = path_file_in.stem
        suffix = path_file_in.suffix
        file_out = '{}-dpi_{}{}'.format(file_stem, dpi, suffix)
    
    with Image.open(file_in) as img:
        img.save(file_out, dpi=(dpi, dpi))
    print('\n    - done: convert {} to {}\n'.format(file_in, file_out))



def main():
    while True:
        print('\n{}'.format('-' * 50))
        file = input('>> input image file: ')
        dpi = input('>> dpi [600]: ')
        file_out = input('>> output file [None]: ')
        
        dpi = dpi.strip()
        if not dpi:
            dpi = 600
        else:
            dpi = int(dpi)
        
        file_out = file_out.strip()
        if not file_out:
            file_out = None
        else:
            file_out = file_out
        
        
        convert_image(file_in=file, file_out=file_out, dpi=dpi)



if __name__ == '__main__':
    
    while True:
        print('\n{}'.format('-' * 50))
        file = input('>> input image file: ')
        dpi = input('>> dpi [600]: ')
        
        dpi = dpi.strip()
        if not dpi:
            dpi = 600
        else:
            dpi = int(dpi)
        
        convert_image(file_in=file, file_out=None, dpi=dpi)
    

