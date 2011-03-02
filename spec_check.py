#!/usr/bin/env python

import sys, os

def read_spec(spec):
    if os.path.exists(spec):
        f = file(spec, 'r')
        content = f.readlines()
        return content

def run_check(output):
    userinput = raw_input('Does this look good (Y/n/skip): ')
    if userinput.lower() == 'y':
        results = '[ pass ] ' + output
    elif userinput.lower() == 'skip':
        results = '[ ---- ] ' + output
    else:
        results = '[ fail ] ' + output
    return results

# Take input for location of SPEC file
spec = sys.argv[1]

# This will be the list that hold our results
results = []

# Lets read in the spec now
spec_lines = read_spec(spec)

# Check 1
os.system('clear')
print 'rpmlint must be run on every package\n'
results.append(run_check('MUST: rpmlint must be run on every package'))

# Complete
for result in results:
    print result
