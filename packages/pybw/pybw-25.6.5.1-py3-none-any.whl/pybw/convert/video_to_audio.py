# -*- coding: utf-8 -*-
"""
version: 2024.12.17

Convert video files to audio files.
"""
import os, sys, time
from glob import glob
from pathlib import Path
from tqdm import tqdm
# from colorama import Fore, Back, Style, init
from moviepy.editor import VideoFileClip



def convert_one_file(file=None, engine='ffmpeg'):
    if not file:
        print('\n\n' + '-' * 50)
        file = input('\nVideo file: ')
        file = file.strip()
        
        if not file:
            return
    
    '''
    \033[31m 红色
    \033[32m 绿色
    \033[33m 黄色
    \033[34m 蓝色
    \033[35m 紫色
    \033[36m 青色
    \033[37m 白色
    \033[39m 默认颜色
    '''
    
    assert isinstance(file, str), 'input file should be string.'
    file = file.strip()
    
    if file.lower() == 'exit':
        print()
        for i in range(3, 0, -1):
            print('\rProgram exiting in \033[32m{}\033[39m s ...'.format(i), end='')
            time.sleep(1)
        print()
        os.sys.exit()
    
    file = glob('*{}*'.format(file))
    file = [i for i in file if os.path.isfile(i)]
    file = [i for i in file if not i.endswith('.mp3')]
    
    if not file:
        print('Pass: can not find any matched file.')
        return
    
    file = file[0]
    print('\nFind file: {}\n'.format(file))
    
    if not os.path.exists(file):
        print('Can not find video file \"{}\"'.format(file))
        os.system('pause')
        os.sys.exit()
    
    if engine == 'moviepy':
        clip = VideoFileClip(file)
        
        audio = clip.audio
        save = Path(file).stem + '.mp3'
        audio.write_audiofile(save)
    
    elif engine == 'ffmpeg':
        save = Path(file).stem + '.m4a'
        os.system('ffmpeg -y -i \"{}\" -c:a copy -vn -sn -loglevel quiet \"{}\"'.format(file, save))
        print('    - done: convert \"{}\" to \"{}\".'.format(file, save))
    


def main():
    
    engine = 'ffmpeg'
    
    files = []
    
    print()
    judge = True
    while judge:
        file = input('Video file: ')
        if file.strip():
            files.append(file.strip())
        else:
            judge = False
    
    length = len([i for i in files if not i.strip().lower() == 'exit'])
    
    for i, file in enumerate(files):
        print('\n\n{0}  Convert {1} in {2}  {0}'.format('-' * 25, i + 1, length))
        convert_one_file(file, engine=engine)
    
    
    while True:
        convert_one_file(engine=engine)


def execute_script():
    if len(sys.argv) > 1:
        for file in sys.argv[1:]:
            convert_one_file(file)
    else:
        main()



if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        for file in sys.argv[1:]:
            convert_one_file(file)
    else:
        main()
        
    
    