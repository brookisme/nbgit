from __future__ import print_function
import os
import re
import argparse
import gitnb.paths as paths
import gitnb.utils as utils
from gitnb.topy import NB2Py
from gitnb.tonb import Py2NB
import gitnb.config as con
from gitnb.project import GitNBProject as NBGP



#
# CONFIG
#
ALL_NOTEBOOKS='all'
TRACKED_NOTEBOOKS='tracked'
UNTRACKED_NOTEBOOKS='untracked'
NBPYS='nbpy'
LIST_TYPES=[
    ALL_NOTEBOOKS,
    TRACKED_NOTEBOOKS,
    UNTRACKED_NOTEBOOKS,
    NBPYS]




#
# METHODS
#
def initialize():
    """ Installs GITNB
        - installs git pre-commit hook
        - creates .gitnb dir
    """
    NBGP.initialize()


def configure():
    """ Install config file
        allows user to change config
    """
    NBGP.configure()


def gitingore():
    """ ?: UPDATE GIT IGNORE
        ignore:
            - ipynb_checkpoints/
            - *.ipynb
            ? .ng_git
    """ 
    pass


def diff():
    """ DIFF NOTEBOOKS
        1. create tmp copy
        2. diff tmp with current
    """
    pass


def list_files(list_type=ALL_NOTEBOOKS):
    """ Notebook paths as list
    """
    prj=NBGP()
    if list_type==ALL_NOTEBOOKS:
        return prj.list_notebooks(), prj.list_untracked()
    elif list_type==TRACKED_NOTEBOOKS:
        return prj.list_notebooks()
    elif list_type==UNTRACKED_NOTEBOOKS:
        return prj.list_untracked()
    elif list_type==NBPYS:
        return prj.list_nbpys()




def update():
    """ 
        - Update all nbpy files
    """
    NBGP().update()



def add(path,destination_path=None):
    """ 
        - Convert Notebook to NBPY FILE
        - Add to Notebooks list: .gitnb/notebooks
        - Add NBPY file to git repo (if GIT_ADD_ON_GitNB_ADD=True)
    """
    nbpy_path=_safe_path_exec(
        NBGP().add,
        'add',
        path,
        destination_path)



def remove(path):
    """ remove ipynb-nbpy line from notebooks list
        - does not delete file
        - does not change git tracking
    """
    return _safe_path_exec(
        NBGP().remove,
        'remove',
        path,
        False)
  


def topy(path,destination_path=None):
    """ Convert Notebook to Py
    """
    return _safe_path_exec(
        _convert_to_py,
        'topy',
        path,
        destination_path)


def tonb(path,destination_path=None):
    """ Convert NBPy to Noteook
    """
    return _safe_path_exec(
        _convert_to_nb,
        'tonb',
        path,
        destination_path)



#
# HELPERS
#
def _safe_path_exec(func,action,path,destination_path=None):
    if os.path.isfile(path):
        _exec(func,path,destination_path)
    elif os.path.isdir(path):
        file_paths=utils.rglob(
            match='*.ipynb',root=path,exclude_dirs=con.fig('EXCLUDE_DIRS'))
        file_paths=[_clean_path(file_path) for file_path in file_paths]
        if destination_path:
            print('\ngitnb[WARNING]: destination_path ignored')
            print('\t- `gitnb {}` for directories always uses default path'.format(
                action))
            print('\t- the default path is configurable (see gitnb configure)\n')
            destination_path=None
        for file_path in file_paths:
            _exec(func,file_path,destination_path)
    else:
        print('gitnb[ERROR]: {} does not exist'.format(path))


def _exec(func,path,destination_path=None):
    if destination_path is False:
        func(path)
    else:
        func(path,destination_path)


def _convert_to_py(path,destination_path=None):
    print('\ngitnb[topy]:'.format(path))
    print('\tPlease note that you are creating a nbpy file but')
    print('\tnot tracking it. To track the file use "gitnb add"\n')
    NB2Py(path,destination_path).convert()


def _convert_to_nb(path,destination_path=None):
    Py2NB(path,destination_path).convert()


def _print_list(list_type,items):
    if items:
        print('gitnb[{}]'.format(list_type))
        for item in items:
            print('\t{}'.format(item))



#######################################################
#
# CLI 
#
#######################################################


#
# args methods:
#
def _init(args):
    return initialize()


def _configure(args):
    return configure()


def _update(args):
    return update()


def _list(args):
    list_type=args.type
    if list_type not in LIST_TYPES:
        print('gitnb[list]: ERROR - {} is not a vaild list type'.format(list_type))
    else:
        if list_type==ALL_NOTEBOOKS:
            tracked,untracked=list_files(list_type)
            _print_list('tracked',tracked)
            _print_list('untracked',untracked)
        else:
            _print_list(list_type,list_files(list_type))


def _add(args):
    destination_path=args.destination_path
    if not utils.truthy(destination_path): destination_path=None
    return add(args.path,destination_path)


def _remove(args):
    return remove(args.path)


def _topy(args):
    destination_path=args.destination_path
    if not utils.truthy(destination_path): destination_path=None
    return topy(args.path,destination_path)


def _tonb(args):
    destination_path=args.destination_path
    if not utils.truthy(destination_path): destination_path=None
    return tonb(args.path,destination_path)


def _clean_path(string):
    return re.sub('^\.\/','',string)


#
# MAIN
#
def main():
    parser=argparse.ArgumentParser(description='GITNB: TRACKING FOR PYTHON NOTEBOOKS')
    subparsers=parser.add_subparsers()
    
    """ install """
    parser_init=subparsers.add_parser(
        'init',
        help='initialize gitnb for local project')
    parser_init.set_defaults(func=_init)    
    
    """ configure """
    parser_configure=subparsers.add_parser(
        'configure',
        help='creates local configuration file ({})'.format(paths.USER_CONFIG))
    parser_configure.set_defaults(func=_configure)    
    
    """ list """
    parser_list=subparsers.add_parser(
        'list',
        help='list notebooks or nbpy files')
    parser_list.add_argument('type',
        nargs='?',
        default='all',
        help='notebooks: ( {} | {} | {} ), or nbpy'.format(
            ALL_NOTEBOOKS,TRACKED_NOTEBOOKS,UNTRACKED_NOTEBOOKS))
    parser_list.set_defaults(func=_list)  
    
    """ update """
    parser_update=subparsers.add_parser(
        'update',
        help='updates nbpy files from tracked notebooks')
    parser_update.set_defaults(func=_update) 

    
    """ add """
    parser_add=subparsers.add_parser(
        'add',
        help='converts notebook to nbpy and adds nbpy to repo')
    parser_add.add_argument('path',
        help='path to ipynb file')   
    parser_add.add_argument('destination_path',
        nargs='?',
        default=None,
        help='if falsey uses default destination path')
    parser_add.set_defaults(func=_add)
    
    """ remove """
    parser_remove=subparsers.add_parser(
        'remove',
        help='stops gitnb from tracking notebook')
    parser_remove.add_argument('path',
        help='path to ipynb file')   
    parser_remove.set_defaults(func=_remove)

    
    """ topy """
    parser_topy=subparsers.add_parser(
        'topy',
        help='topy .ipynb files to .nbpy.py files')
    parser_topy.add_argument('path',
        help='path to ipynb file')   
    parser_topy.add_argument('destination_path',
        nargs='?',
        default=None,
        help='if falsey uses default destination path')
    parser_topy.set_defaults(func=_topy)
    
    
    """ tonb """
    parser_tonb=subparsers.add_parser(
        'tonb',
        help='tonb .ipynb files to .nbpy.py files')
    parser_tonb.add_argument('path',
        help='path to ipynb file')   
    parser_tonb.add_argument('destination_path',
        nargs='?',
        default=None,
        help='if falsey uses default destination path')
    parser_tonb.set_defaults(func=_tonb)   
    
    """ run """
    args=parser.parse_args()
    args.func(args)



if __name__ == "__main__": 
    main()


