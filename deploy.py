import os
import re
import git
import shutil
import argparse
import datetime

def check_dir( directory_path ):
    if( not os.path.isdir( directory_path ) ):
        msg = "%r is not a directory" % directory_path
        raise argparse.ArgumentTypeError(msg)
    return directory_path

def get_local_repo_dir( args ):
    return [ os.path.join( args.d, rdname ) for rdname in next(os.walk( args.d ))[1] if not rdname[0] == '.']

def process_repos( args ):
    repos = get_local_repo_dir( args )
    for module in module_list+lib_list:
        #print( '>' + module )
        for repo in repos:
            repo_bname = os.path.basename( repo )
            if re.search( r'\b' + module + r'\b', repo_bname ):
                #print ( '>>' + repo )
                update( repo );
                rename( repo, repo_bname );
                repos.remove( repo )
                break

def update( dirname ):
    git.cmd.Git( dirname ).pull( 'origin', 'master' )

def copy( args ):
    repos = get_local_repo_dir( args )
    copy_comps( repos, args.l, args.ld )
    copy_comps( repos, args.m, args.md )

def copy_comps( repos, comps, dst_dir ):
    if comps == None or dst_dir == None:
        return

    for comp in comps:
        #print( '>' + comp )
        for repo in repos:
            #print ( '>>' + repo )
            repo_name = os.path.basename( repo )
            if re.search( r'\b' + comp + r'\b', repo_name ):
                new_name = '-'.join( repo_name.split('-')[:-1] ) + datetime.datetime.now().strftime ("-%Y%m%d")
                #print( '>>>' + repo )
                full_dst_dir = os.path.join( dst_dir, new_name )
                #print ( '>>>' + full_dst_dir )

                gCompDstDirDic[ comp ] = full_dst_dir

                shutil.copytree( repo, full_dst_dir )
                repos.remove( repo )
                break

def rename( repo, repo_bname ):
    new_name = '-'.join( repo_bname.split('-')[:-1] ) + datetime.datetime.now().strftime ("-%Y%m%d")
    #print( '>>>' + repo )
    #print ( '>>>' + os.path.join(os.path.dirname(repo), new_name ) )
    os.rename( repo, os.path.join(os.path.dirname(repo), new_name ) );

lib_list = ['libubac', 'libkimeng']
module_list = ['init', 'weblogin', 'login', 'market-data', 'market-movers', 'market-insight', 'portfolio', 'reports', 'trade', 'watchlist']

parser = argparse.ArgumentParser(description='Auto deploy in Single Server Environment ( like UAT )', epilog='Happy deploying ;)')

parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0')

parser.add_argument('-l', choices=lib_list, nargs='*', help='list of libraries to be deployed')
parser.add_argument('-ld', type=check_dir, help='directory to which libraries to be copied', metavar='/path/to/lib_dir')

parser.add_argument('m', nargs='*', choices=module_list, help='list of modules to be deployed')
parser.add_argument('-md', type=check_dir, help='directory to which modules to be copied', required=True, metavar='/path/to/module_dir')
parser.add_argument('-d', type=check_dir, help='directory where repos are checkout', required=True, metavar='/path/to/repo_dir')

gCompDstDirDic={}
args = parser.parse_args()
print(args)

process_repos( args )
print( get_local_repo_dir( args ) )

copy( args )
print( gCompDstDirDic )

"""
update_repos()

copy_lib();

copy_modules();


UAT deployment steps

- update repo folders
- rename repo folders to today

- if lib is there copy to library_folder
- compile & install lib
- relink to new lib folder

- copy the components to Broker folder
- compile all components
- stop components
- relink components
- start components

deploy -l libubac libkimeng -ld /path/to/libdir -md /path/to/moduledir -d /path/to/checkoutdir login trade reports 


master: latest changes
dev: current developing changes
uat:

"""
