import os
import re
import argparse
import datetime

def check_dir( directory_path ):
    if( not os.path.isdir( directory_path ) ):
        msg = "%r is not a directory" % directory_path
        raise argparse.ArgumentTypeError(msg)
    return directory_path

def rename_repos( args ):
    for module in args.m:
        #print( '>' + module )
        for repo in repos:
            #print ( '>>' + repo )
            repo_name = os.path.basename( repo )
            if re.search( r'\b' + module + r'\b', repo_name ):
                new_name = '-'.join( repo_name.split('-')[:-1] ) + datetime.datetime.now().strftime ("-%Y%m%d")
                #print( '>>>' + repo )
                #print ( '>>>' + os.path.join(os.path.dirname(repo), new_name ) )
                os.rename( repo, os.path.join(os.path.dirname(repo), new_name ) );
                repos.remove( repo )
                break

parser = argparse.ArgumentParser(description='Auto deploy in Single Server Environment ( like UAT )', epilog='Happy deploying ;)')

parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0')

parser.add_argument('-l', choices=['libubac', 'libkimeng'], nargs='*', help='list of libraries to be deployed')
parser.add_argument('-ld', type=check_dir, help='directory to which libraries to be copied', metavar='/path/to/lib_dir')

parser.add_argument('m', nargs='*', choices=['init', 'weblogin', 'login', 'market-data', 'market-movers', 'market-insight', 'portfolio', 'reports', 'trade', 'watchlist'], help='list of modules to be deployed')
parser.add_argument('-md', type=check_dir, help='directory to which modules to be copied', required=True, metavar='/path/to/module_dir')
parser.add_argument('-d', type=check_dir, help='directory where repos are checkout', required=True, metavar='/path/to/repo_dir')

args = parser.parse_args()
print(args)

repos = next(os.walk( args.d ))[1]
rename_repos( args )
                


"""
update_repos()

copy_lib();

copy_modules();


UAT deployment steps

- rename repo folders to today
- update repo folders

- if lib is there copy to library_folder
- compile & install lib
- relink to new lib folder

- copy the components to Broker folder
- compile all components
- stop components
- relink components
- start components

deploy -l libubac libkimeng -m login trade reports -ld ~/Libraries -md ~/Broker


master: latest changes
dev: current developing changes
uat:

"""
