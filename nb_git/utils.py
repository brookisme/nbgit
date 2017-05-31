import os
import subprocess
import fnmatch
import re
import nb_git.config as con


def rglob(match='*',root='.',exclude_dirs=[]):
    """ Recursive Glob
        Args:
            match: <str> string to match
            root: <str> dir to start recursive search
            exclude: <list[str]> list of directories to skip
    """
    matches = []
    for froot, _, filenames in os.walk(root):
        if not any(xdir in froot for xdir in exclude_dirs):
            for filename in fnmatch.filter(filenames, match):
                matches.append(os.path.join(froot, filename))
    return matches


def copy_append(input_path,output_path,open_type=None):
    """ COPY OR APPEND input_path to output_path
    """
    if not open_type:
        if os.path.isfile(output_path): open_type='a'
        else: open_type='w'
    with open(output_path,open_type) as output_file:
        with open(input_path,'r') as input_file:
            output_file.write(input_file.read())


def git_add(path,noisy=True):
    """ GIT ADD FILE
    """
    safe_path="'{}'".format(path)
    cmd=' '.join(['git add',safe_path])
    if noisy: print('nb_git: {}'.format(cmd))
    subprocess.check_output(cmd, shell=True)


def truthy(value):
    """ Stringy Truthyness
    """
    value=str(value).lower().strip(' ')
    if value in ['none','false','0','nope','','[]']:
        return False
    else:
        return True


def read_lines(path):
    """ Read file
        return lines list
    """ 
    with open(path,'r') as file:
        lines=file.readlines()
    return lines

import subprocess


def nb_matching_lines(grep,path):
    """ count lines without match in file
        returns int
    """
    safe_path="'{}'".format(path)
    cmd="cat {} | grep {} | wc -l".format(safe_path,grep)
    out=subprocess.check_output(cmd, shell=True)
    return int(out.strip(' ').strip('\n'))



def remove_lines(ngrep,path,bak_ext='bak'):
    """ Removes Line with matching ngrep
        - creates a backup path.bak_ext
    """
    # backup file
    safe_path="'{}'".format(path)
    safe_path_bak="'{}.{}'".format(path,bak_ext)
    cmd1=' '.join(['cp',safe_path,safe_path_bak])
    subprocess.check_output(cmd1, shell=True)
    # backup file
    cmd2="cat {} | grep -v {} > {}".format(safe_path_bak,ngrep,safe_path)
    subprocess.check_output(cmd2, shell=True)




def mkdirs(path):
    """ Make parent dirs if they dont exist
    """
    if not os.path.exists(os.path.dirname(path)):
        nb_dir=os.path.dirname(path)
        if truthy(nb_dir):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise


def default_nbpy_path(ipynb_path):
    """ Get Path for nbpy.py file
        - if NBPY_IDENT: use .{ident}.py ext
        - if NBPY_DIR: put in nbpy_dir
        - else put in same direcotry as file
    """
    nbpy_ident=con.fig('NBPY_IDENT')
    nbpy_dir=con.fig('NBPY_DIR')
    if nbpy_ident: ext='.{}.py'.format(nbpy_ident)
    else: ext='.py'
    py_path=re.sub('.ipynb$',ext,ipynb_path)
    if truthy(nbpy_dir):
        py_name=os.path.basename(py_path)
        py_path=os.path.join(nbpy_dir,py_name)
    return py_path

