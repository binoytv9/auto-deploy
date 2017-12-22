"""
Deployment steps

- update repo folders
- rename repo folders to today

- if lib is there copy to library_folder
- compile & install lib
- relink to new lib folder

- copy the modules to module_folder
- compile all modules
- stop modules
- relink modules
- start modules

python3.6 deploy.py -l lib1 lib2 -ld /path/to/libdir -md /path/to/moduledir -d /path/to/checkoutdir mod1 mod2

"""

import os
import re
import sys
import time
import shutil
import argparse
import datetime
import subprocess

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
                print ( '>>' + repo )
                update( repo );
                rename( repo, repo_bname );
                repos.remove( repo )
                break

def update( dirname ):
    cmd = ['git', '-C', 'pull', 'origin', 'master']
    cmd.insert( 2, dirname )
    if subprocess.run( cmd ).returncode != 0:
        sys.exit(1)

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

def compile_all( args ):
    compile_lib( args.l )
    compile_mod( args.m )

# sequencial compilation
def compile_lib( libs ):
    if libs == None:
        return

    for lib in libs:
        dirname = gCompDstDirDic[lib]
        subprocess.run( ['make', '-C', dirname, 'clean'] )
        subprocess.run( ['make', '-j2', '-C', dirname] )
        subprocess.run( ['sudo', 'make', '-C', dirname, 'install'] )

# parallel compilation
def compile_mod( modules ):
    processes=[]
    for module in modules:
        dirname = gCompDstDirDic[module]
        subprocess.run( ['make', '-C', dirname, 'clean'] )
        processes.append( subprocess.Popen( ['make', '-j2', '-C', dirname] ) )

    for process in processes:
        process.wait()

def relink_all( args ):
    relink_lib( args.l )
    relink_mod( args.m )

def relink_lib( libs ):
    if libs == None:
        return

    for lib in libs:
        dirname = gCompDstDirDic[lib]
        subprocess.run( ['unlink', lib], cwd=os.path.dirname(dirname) )
        subprocess.run( ['ln', '-s', os.path.basename(dirname), lib], cwd=os.path.dirname(dirname) )

def relink_mod( modules ):
    for module in modules:
        dirname = gCompDstDirDic[ module ]
        subprocess.run( ['monit', '-c', '/home/mkeadmin/etc/monit/monitrc', 'stop', module] )
        time.sleep(1)
        subprocess.run( ['unlink', module], cwd=os.path.dirname(dirname) )
        subprocess.run( ['ln', '-s', os.path.basename(dirname), module], cwd=os.path.dirname(dirname) )
        subprocess.run( ['monit', '-c', '/home/mkeadmin/etc/monit/monitrc', , 'start', module] )

gCompDstDirDic={}
lib_list = ['libkimeng']
module_list = ['init', 'weblogin', 'login', 'market-data', 'market-movers', 'market-insight', 'portfolio', 'reports', 'trade', 'watchlist']

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Auto deploy in Single Server Environment ( like UAT )', epilog='Happy deploying ;)')

    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0')

    parser.add_argument('-l', choices=lib_list, nargs='*', help='list of libraries to be deployed')
    parser.add_argument('-ld', type=check_dir, help='directory to which libraries to be copied', metavar='/path/to/lib_dir')

    parser.add_argument('m', nargs='*', choices=module_list, help='list of modules to be deployed')
    parser.add_argument('-md', type=check_dir, help='directory to which modules to be copied', required=True, metavar='/path/to/module_dir')
    parser.add_argument('-d', type=check_dir, help='directory where repos are checkout', required=True, metavar='/path/to/repo_dir')

    args = parser.parse_args()
    print(args)

    process_repos( args )
    print( get_local_repo_dir( args ) )

    copy( args )
    print( gCompDstDirDic )

    compile_all( args )

    relink_all( args )
