#!/usr/bin/env python

from glob import glob
from configobj import ConfigObj
import sys, os

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

# Take input for location of SPEC file
#spec = sys.argv[1]

# This will be the list that hold our results
results = []
checks = configs()

# Check 1
for check in sorted(checks):
    os.system('clear')
    message = checks[check]['message']
    print 'Check #' + str(check)
    print '='*80
    print '         ' + message + '\n'
    results.append(runcheck(checks[check]['type'], checks[check]['message']))

os.system('clear')
print 'Results for Bugzilla'
print '='*80
for result in results:
    print result
