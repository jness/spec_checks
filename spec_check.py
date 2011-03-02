#!/usr/bin/env python

from glob import glob
from configobj import ConfigObj
import sys, os
import argparse

def configs():
    'Check config files in ./configs and parse the data'
    config_dir = './configs'
    checks = {}
    for _file in glob("%s/*.conf" % config_dir):
        c = ConfigObj(_file)
        if not c['enabled'] in [True, 'True', 'true', 1, '1']:
            continue
        checks[int(c['order'])] = c
    return checks

def runcheck(type, message):
    userinput = raw_input('Does this look good (Y/n/skip): ')
    output = type + ' ' + message
    if userinput.lower() == 'y':
        results = '[ pass ] ' + output
    elif userinput.lower() == 'skip':
        results = '[ ---- ] ' + output
    else:
        results = '[ fail ] ' + output
    return results

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

# Use argparse to take input for SPEC File
parser = argparse.ArgumentParser()
parser.add_argument('--spec', help='SPEC File', required=True)
args = parser.parse_args()

# Prep for run
results = []
checks = configs()
spec_lines = readspec(args.spec)

# Run our Checks
for check in sorted(checks):
    os.system('clear')
    message = checks[check]['message']
    print 'CHECK: ' + str(check)
    print specfile(args.spec)
    print '='*80
    print '         ' + message + '\n'
    
    # Try to run the command if it is there
    try:
        command = checks[check]['command']
    except KeyError:
        pass
    else:
        print specfile(args.spec) + ':'
        print '-'*35
        print '   ' + eval(command) + '\n'

    results.append(runcheck(checks[check]['type'], checks[check]['message']))

os.system('clear')
print 'Results for Bugzilla'
print '='*80
for result in results:
    print result
