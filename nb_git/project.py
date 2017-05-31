import os
import nb_git.utils as utils
from nb_git.topy import NB2Py
from nb_git.paths import *


#
# CONFIG
#
NOTEBOOKS_SEP='|'
NOTEBOOKS_FMT='{} {} {}'



#
# NBGitProject:
#
class NBGitProject(object):
    
    
    def __init__(self):
        self._notebooks= None
        self._all_notebooks= None
        self._tracked_notebooks= None
        self._untracked_notebooks= None


    def initialize(self):
        """ Installs NBGIT
            - installs git pre-commit hook
            - creates .nb_git dir
        """
        if os.path.exists(GIT_DIR):
            cmd1='cp -R {} {}'.format(DOT_NBGIT_CONFIG_DIR,NBGIT_CONFIG_DIR)
            os.system(cmd1)
            utils.copy_append(PRECOMMIT_SCRIPT,GIT_PC)
            cmd2='chmod +x {}'.format(GIT_PC)
            os.system(cmd2)
            print("nb_git: INSTALLED ")
            print("\t - nbpy.py files will be created/updated/tracked")
            print("\t - install user config with: $ nb_git configure")
        else:
            print("nb_git: MUST INITIALIZE GIT")


    def all_notebooks(self):
        nbks_list=utils.rglob(
            '*.ipynb',exclude_dirs=con.fig('EXCLUDE_DIRS'))
        nbks_list=[self._clean_path(nbk) for nbk in nbks_list]
        return nbks_list
    
    
    def notebooks(self):
        nbks_dict={}
        nbks_lines=utils.read_lines(NOTEBOOK_LIST)
        for line in nbks_lines:
            parts=line.split(NOTEBOOKS_SEP)
            if len(parts)==2:
                key, value=(self._clean(part) for part in parts)
                nbks_dict[key]=value
        return nbks_dict

    
    def list_notebooks(self):
        return self.notebooks().keys()  
    

    def list_nbpys(self):
        return self.notebooks().values()

    
    def list_untracked(self):
        all_set=set(self.all_notebooks())
        tracked_set=set(self.list_notebooks())
        return list(all_set-tracked_set)

    
    def add(self,path,nbpy_path=None):
        nbks=self.notebooks()
        if nbks.get(path):
            level='WARNING'
            msg='{} already tracked by {}'.format(path,nbks.get(path))
        elif nbpy_path in self.list_nbpys():
            level='WARNING'
            msg='nbpy.py file ({}) already added'.format(nbpy_path)
        else:
            if os.path.isfile(path):
                nbpy_path=NB2Py(path,nbpy_path).convert()
                self._append_notebooks(path,nbpy_path)
                utils.git_add(nbpy_path)
                msg=None
            else:
                level='WARNING'
                msg='notebook ({}) does not exist'.format(path)
        if msg: self._out(msg,level)


    def remove(self,path):
        if not path in self.list_notebooks():
            level='WARNING'
            msg='{} is not being tracked'.format(path)
        else:
            nb_match=utils.nb_matching_lines(
                path,NOTEBOOK_LIST)
            if nb_match==0:
                level='ERROR'
                msg="failed to remove {} from {}".format(
                    path,NOTEBOOK_LIST)
            if nb_match>1:
                level='WARNING'
                msg="more than one line matching {} in {}".format(
                    path,NOTEBOOK_LIST)
            else:
                level=None
                utils.remove_lines(path,NOTEBOOK_LIST)
                msg="{} no longer being tracked".format(path)
        self._out(msg,level)


    def _append_notebooks(self,path,nbpy_path):
        nbk_line=NOTEBOOKS_FMT.format(path,NOTEBOOKS_SEP,nbpy_path)
        self._out('add ({})'.format(nbk_line))
        with open(NOTEBOOK_LIST, "a") as nbks_file:
            nbks_file.write('\n{}'.format(nbk_line))
        

    def _out(self,msg,level=None):
        if level: info="nbgit[{}]".format(level)
        else: info="nbgit"
        print("{}: {}".format(info,msg))


    def _clean_path(self,string):
        return re.sub('^\.\/','',string)


    def _clean(self,string):
        return string.strip(' ').strip('\n').strip(' ')


