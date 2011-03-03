#!/usr/bin/env python

from glob import glob
from configobj import ConfigObj
import subprocess
import sys, os
import argparse
import urllib
import shutil, shlex

class colors:
    pink = '\033[95m'
    red = '\033[91m'
    green = '\033[92m'
    gold = '\033[93m'
    blue = '\033[94m'
    end = '\033[0m'

def configs():
    'Check config files in ./configs and parse the data'
    config_dir = './configs_I_RUN_FEDORA'
    checks = {}
    for _file in glob("%s/*.conf" % config_dir):
        c = ConfigObj(_file)
        if not c['enabled'] in [True, 'True', 'true', 1, '1']:
            continue
        checks[int(c['order'])] = c
    return checks

def runcheck(type, message, doc):
    userinput = raw_input('Does this look good (Y/n/skip): ')
    output = type + ' ' + message
    if userinput.lower() == 'y':
        results = '[ ' + colors.green + 'pass' + colors.end + ' ] ' + output
        status = 'pass'
    elif userinput.lower() == 'skip':
        results = '[ ' + colors.green + '----' + colors.end + ' ] ' + output
        status = 'pass'
    else:
        results = '''[ ''' + colors.red + '''fail''' + colors.end + ''' ] ''' + output + ''' 

 ''' + doc
        status = 'fail'
    return results, status

def readspec(spec):
    if os.path.exists(spec):
        f = file(spec, 'r')
        content = f.readlines()
        return content

def specfile(spec):
    specfile = spec.split('/')[-1]
    return specfile

def specname(spec_lines):
    for line in spec_lines:
        if 'Name: ' in line:
            name = line.split()[1]
            return name

def specversion(spec_lines):
    for line in spec_lines:
        if 'Version: ' in line:
            version = line.split()[1]
            return version

def speclicense(spec_lines):
    for line in spec_lines:
        if 'License: ' in line:
            license = line
            return license

def specbuildrequires(spec_lines):
    for line in spec_lines:
        if 'BuildRequires: ' in line:
            print line
        

def runcommand(command):
    args = shlex.split(command)
    process = subprocess.Popen(args, shell=False)
    results = process.communicate()
    results = results[0]
    return results

# Use argparse to take input for SPEC File
parser = argparse.ArgumentParser()
#parser.add_argument('--spec', help='SPEC File', required=True)
parser.add_argument('--srpm', help='URL For SRPM', required=True)
args = parser.parse_args()

# Prep for run
passed = []
failed = []
checks = configs() # Read in all our checks
path = './tmp' # Where SRPM is kept
srpm = args.srpm.split('/')[-1]

# Download the SRPM
if not os.path.exists(path):
    os.mkdir(path)
    print 'Downloading', srpm
    urllib.urlretrieve(args.srpm, path + '/' + srpm)

# Check for .srpm
if os.path.exists('./tmp/' + srpm):
    print 'Installing', srpm
    os.chdir(path)
    install = runcommand('rpm -i --quiet ' + srpm)

# Get our SPEC Name
specs = glob('SPECS/*.spec')
if len(specs) == 1:
    spec = specs[0]
else:
    print 'Maybe the URL was invalid, maybe there is more than one SPEC...'
    sys.exit(0)

# Look for tarballs in SOURCE
# FIX ME, i need some sort of looping
tgz = glob('SOURCES/*.tar.gz')
if tgz:
    source = tgz
tar = glob('SOURCES/*.tar.gz')
if tar:
    source = tar

# Run through the spec
spec_lines = readspec(spec)

# Run our Checks
for check in sorted(checks):
    os.system('clear')
    message = checks[check]['message']
    print 'CHECK: ' + str(check)
    print specfile(spec)
    print '='*80
    print '         ' + message + '\n'
    
    # Try to run the command if it is there
    try:
        command = checks[check]['command']
    except KeyError:
        pass
    else:
        print specfile(spec) + ':'
        print '-'*35
        commandoutput = eval(command)
        if commandoutput:
            print '   ' + commandoutput + '\n'
        else:
            print '\n'

    # See if we have Fedora Documentation
    try:
        doc = checks[check]['doc']
    except KeyError:
        pass
    else:
        print '  What does Fedora have to say?'
        print '  ' + doc + '\n'
    
    # Run the given check
    mycheck = runcheck(checks[check]['type'], checks[check]['message'], checks[check]['doc'])
    if mycheck[1] == 'pass':
        passed.append(mycheck[0])
    else:
        failed.append(mycheck[0])    


os.system('clear')

# Print our failed checks
if failed:
    print "FAILED MUST HAVE's:\n"
    for f in failed:
        print f + '\n'

# Print our Passed checks
if passed:
    print "PASSED MUST HAVE'S:\n"
    for p in passed:
        print p + '\n'
