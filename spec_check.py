#!/usr/bin/env python

from glob import glob
from configobj import ConfigObj
import sys, os
import pickle
import argparse

class colors:
    red = '\033[91m'
    green = '\033[92m'
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

def runcheck(type, message, doc, default):
    if not default:
        default = 'pass'

    # Catch CTRL + C on close
    try:
        userinput = raw_input('Does this look good (Y/n/skip) [' + default + ']: ')
    except KeyboardInterrupt:
        print '\n'
        sys.exit()

    output = type + ' ' + message

    # Check Input
    if userinput.lower() == 'y' or userinput.lower() == 'pass':
        color = colors.green
        msg = 'pass'
        status = 'pass'
        default = False
    elif userinput.lower() == 's' or userinput.lower() == 'skip':
        color = colors.green
        msg = '----'
        status = 'skip'
        default = False
    elif userinput.lower() == 'n' or userinput.lower() == 'fail':
        color = colors.red
        msg = 'fail'
        status = 'fail'
        default = False
    else:
        color = colors.green
        msg = 'pass'
        status = 'pass'
        default = True

    # Message for Bugzilla
    results = '''[ ''' + color + msg + colors.end + ''' ] ''' + output + ''' 

 ''' + doc

    return results, status, default

def results_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return

def past_answers(path):
    if os.path.exists(path + '/review'):
        f = open(path + '/review', 'rb')
        saved = pickle.load(f)
        f.close()
        return saved


# Build my Parser with help for user input
parser = argparse.ArgumentParser()
parser.add_argument('name', help='Package Name')
parser.add_argument('--results', action='store_true',
        dest='results', default=None, help='Print out the report using saved answers')
args = parser.parse_args()

# Prep for run
passed = []
failed = []
checks = configs()

# Create our Save Path
path = os.path.expanduser('~/.spec_check/' + args.name)
results_directory(path)
saved = past_answers(path)
if not saved:
    saved = {}

# Print results and quit
if args.results:
    if not saved:
        print 'You do not have saved results for', args.name
        sys.exit()

    print "FAILED MUST HAVE's:\n"
    for check in sorted(checks):

        # Get documentation URL
        try:
            doc = checks[check]['doc']
        except KeyError:
            pass

        # Get stored info
        try:
            default = saved[checks[check]['order']]
        except KeyError:
            default = False
        except TypeError:
            default = False

        if default == 'fail':
            print '[', colors.red + default + colors.end, ']', checks[check]['type'], checks[check]['message']
            print '\n' + '  ' + checks[check]['doc'], '\n'

    print "PASSED MUST HAVE's:\n"
    for check in sorted(checks):

        # Get documentation URL
        try:
            doc = checks[check]['doc']
        except KeyError:
            pass

        # Get stored info
        try:
            default = saved[checks[check]['order']]
        except KeyError:
            default = False
        except TypeError:
            default = False

        if default != 'fail' and default != False:
            if default == 'skip':
                default = '----'
            print '[', colors.green + default + colors.end, ']', checks[check]['type'], checks[check]['message']
            print '\n' + '  ' + checks[check]['doc'], '\n'

    # Only print so lets quit now
    sys.exit()
         

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
    
    try:
        default = saved[checks[check]['order']]
    except KeyError:
        default = False
    except TypeError:
        default = False

    # Run the given check
    mycheck = runcheck(checks[check]['type'], checks[check]['message'], checks[check]['doc'], default)

    # If we have a default from the saved file
    if default and mycheck[2]:
        if default == 'pass' or default == 'skip':
            passed.append(mycheck[0])
        else:
            failed.append(mycheck[0])    

        saved[checks[check]['order']] = default

    else:
        if mycheck[1] == 'pass' or mycheck[1] == 'skip':
            passed.append(mycheck[0])
        else:
            failed.append(mycheck[0])    

        saved[checks[check]['order']] = mycheck[1]

    # Store Check file
    f = open(path + '/review', 'wb')
    pickle.dump(saved, f)
    f.close()


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
