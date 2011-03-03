#!/usr/bin/env python

from glob import glob
from configobj import ConfigObj
import sys, os
import argparse

class colors:
    pink = '\033[95m'
    red = '\033[91m'
    green = '\033[92m'
    gold = '\033[93m'
    blue = '\033[94m'
    end = '\033[0m'

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

# Prep for run
passed = []
failed = []
checks = configs()

# Run our Checks
for check in sorted(checks):
    os.system('clear')
    message = checks[check]['message']
    print 'CHECK: ' + str(check)
    print '='*80
    print '         ' + message + '\n'
    
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
