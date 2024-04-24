"""
Copyright Elemental Reasoning, LLC, 2019
All rights reserved unless otherwise specified in licensing agreement.
---------------
"""

import os
import logging
import logging.handlers
import coloredlogs
import configparser
import sys
import datetime
import inspect

####################################################
# Original code, was copied to each file.  Errors abounded:
# import logging
# import logging.handlers
# import coloredlogs
# import coloredlogsconfig
#
# depth = 0
# loggername = ""
# while True:
#     try:
#         srcFile = sys._getframe(depth).f_globals.get('__file__')
#         if srcFile == None:
#             break
#         importScope = os.path.splitext(os.path.basename(srcFile))[0]
#         if depth == 0:
#             loggername = importScope
#         else:
#             loggername = importScope + "." + loggername
#         depth = depth + 6
#     except ValueError:
#         break
# logger = None
# ch = None
# logger = logging.getLogger(loggername)
#
# if depth == 6:
#     fmt='%(asctime)s - %(module)s %(funcName)s [%(lineno)4d] - %(levelname)s - %(message)s'
#     styles={'asctime': {'color': 'green'}, 'module': {'color': 'magenta'}, 'levelname': {'color': 'white', 'bold': True}, 'funcName': {'color': 'cyan'}, 'programname': {'color': 'blue'}}

#     logger.setLevel(logging.WARNING)
#
#     formatter = logging.Formatter(fmt)
#     fh = logging.handlers.RotatingFileHandler(loggername + ".log", maxBytes=10485760, backupCount=5)
#     fh.setLevel(logging.WARNING)
#     fh.setFormatter(formatter)
#     logger.addHandler(fh)
#
#     coloredlogs.install(level='DEBUG', fmt=fmt, field_styles=styles, logger=logger)
####################################################

####################################################
# Useful snippets:
#
#     for h in logger.__getattribute__('handlers'):
#         printHandlerInfo(h)
#
#     for h in logger.__getattribute__('handlers'):
#         h.setLevel(logging.DEBUG)
#
#     printLoggerInfo(logger)
#     for h in logger.__getattribute__('handlers'):
#         printHandlerInfo(h)
#
#     for key in logging.Logger.manager.loggerDict:
#         print(key)
#
#
# Email handler setup can be made easier with a config file that you *don't* check in to git
# erlogging.preSetupEmailFromConfig("erEmailSetup.config")
#
####################################################

# Expose the logging levels just for convenience of calling modules
CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG

emailSetupInfo = {}

def debugPrefix():
    callingframe = inspect.currentframe().f_back
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - erlogging " + callingframe.f_code.co_name + " [ " + str(callingframe.f_lineno) + "] - "

def preSetupEmail(mailhost, fromaddr, toaddrs, subject, credentials, secure):
    global emailSetupInfo
    emailSetupInfo["mailhost"] = mailhost
    emailSetupInfo["fromaddr"] = fromaddr
    emailSetupInfo["toaddrs"] = toaddrs
    emailSetupInfo["subject"] = subject
    emailSetupInfo["credentials"] = credentials
    emailSetupInfo["secure"] = secure


def preSetupEmailFromConfig(configfile):
    config = configparser.ConfigParser()
    if os.path.exists(configfile):
        config.read(configfile)
        preSetupEmail(tuple(config.get("DEFAULT", "mailhost").split()),
                      config.get("DEFAULT", "fromaddr"),
                      config.get("DEFAULT", "toaddr").split(),
                      config.get("DEFAULT", "subject"),
                      tuple(config.get("DEFAULT", "credentials").split()),
                      tuple(config.get("DEFAULT", "secure").split())
                      )
    else:
        print(debugPrefix() + "ERROR:  (erlogging) No such email config file: '{}'".format(configfile))

# Set up this info as per logging.SMTPHandler
#   Example:
#       emailHostPort = ("smtp.gmail.com", 587)
#       emailCredentials = ("foo@gmail.com", "myvoiceismy")
#       emailFromAddr =
#

def setup(nameGetter, explicitLogDir=None, logConfigFile=None, emailConfigFile=None, debug=False):
    """Set up a logger for a module that calls this function.  This is a bit different.  
    We need the call to sys._getframe to happen in the file that we want info for, but 
    we can do that by having the file send us a lambda of the call.  We do all the heavy 
    lifting here, walking through the call stack to extract an import chain that we use 
    as the loggername, using depth of (useful) stack to set up handlers only when needed, etc."""
    
    global emailSetupInfo
    
    # Controls for stepping through sys._getframe
    # Step is dependent on Python version (boo)
    # Pre 3.3, it is 0, then with 3.3 it gets weird.  Look up by version
    version = sys.version_info
    versionStr = "{}.{}.{}".format(version.major, version.minor, version.micro)
    if debug:
        print(debugPrefix() + "Python version {}".format(versionStr))
    if version.major < 3:
        __depthStep = 0
    else:
        # Each of python 3.0 through 3.12
        # 3.0 -> 3.2
        if version.minor < 3:
            __depthStep = 0
        # 3.3
        if version.minor == 3:
            __depthStep = 9
        # 3.4
        if version.minor == 4:
            __depthStep = 7
        # 3.5, 3.6
        if version.minor > 4 and version.minor < 7:
            __depthStep = 6
        # 3.7.0 -> 3.7.8
        if version.minor == 7 and version.micro < 9:
            __depthStep = 6
        # 3.7.9 -> ??
        # These use the new, much more direct approach.
        if version.minor == 7 and version.micro > 8:
            __depthStep = 0
        if version.minor == 8:
            __depthStep = 0
        if version.minor == 9:
            __depthStep = 0
        if version.minor == 10:
            __depthStep = 0
        else:
            __depthStep = 0
        
        if debug:
            print(debugPrefix() + "Python version {}, __depthStep: {}".format(versionStr, __depthStep))

    # Offset is to roll back from this call site to the function/lambda defined in the module of interest
    __depthOffset = 2

    def getFrameStackPseudoModules():
        depth = 0
        modules = []
        while True:
            try:
                modules.insert(0, os.path.splitext(os.path.basename(nameGetter(depth).f_globals.get('__file__')))[0])
                # print(debugPrefix() + name)
                depth += 1
            except ValueError:
                break
        modules = [n for n in modules if '_bootstrap' not in n]

        return modules

    def printFrameStackPseudoModules():
        depth = 0
        name = ""
        while True:
            try:
                name = os.path.splitext(os.path.basename(nameGetter(depth).f_globals.get('__file__')))[0] + "." + name
                print(debugPrefix() + name)
                depth += 1
            except ValueError:
                break

    def printFrameStackFiles():
        depth = 0
        name = ""
        while True:
            try:
                name = nameGetter(depth).f_globals.get('__file__') + "." + name
                print(debugPrefix() + name)
                depth += 1
            except ValueError:
                break

    loggername = ""
    depth = 0
    if debug:
        printFrameStackPseudoModules()
        # printFrameStackFiles()

    def name_eq_main():
        # When executing directly (as in `$ python -m module` in the shell) to invoke the std "if __name__ == 'main':"
        if debug:
            print(debugPrefix() + "Checking if running as __main__")
        result = (depth == __depthStep + __depthOffset)
        if result and debug:
            print(debugPrefix() + "Running as __main__")
        return result

    def being_run_inside_setuptools_wrapper():
        # Check to see if we're being exceuted inside a setuptools wrapper
        if debug:
            print(debugPrefix() + "Checking if running setuptools wrapper")
        result = False
        if version.major < 3 or (version.major == 3 and version.minor < 7) or (version.major == 3 and version.minor == 7 and version.micro < 9):
            # Up until python 3.7.8, '__init__' is the wrapper name.
            if debug:
                print(debugPrefix() + "\t... up to python 3.7.8")
            # The depth cleanly maps to the following calculation.
            result = (depth == __depthStep * 2 + __depthOffset) and loggername[:8] == '__init__'
            if result and debug:
                print(debugPrefix() + "Running in setuptools wrapper (pre-3.7.9)")
        else:
            # Starting in python 3.7.9, '_bootstrap' is the new wrapper name.
            if debug:
                print(debugPrefix() + "\t... in python 3.7.9 and later")
            # The depth has no clear calculation at this point, so just go by name
            result = loggername[:10] == '_bootstrap'
            if result and debug:
                print(debugPrefix() + "Running in setuptools wrapper (3.7.9 and after)")
        return result

    def getLoggername(__depthOffset, __depthStep):
        depth = __depthOffset
        loggername = ""
        while True:
            try:
                # print (nameGetter(depth))
                # Starting in Python 3.12, sys._getframemodulename(depth) can be used to get this info more directly.
                srcFile = nameGetter(depth).f_globals.get('__file__')
                if srcFile == None:
                    print(debugPrefix() + "ERROR: NO SOURCE FILE??")
                    break
                importScope = os.path.splitext(os.path.basename(srcFile))[0]
                if depth == __depthOffset:
                    loggername = importScope
                else:
                    loggername = importScope + "." + loggername
                depth += __depthStep
                if debug:
                    print(debugPrefix() + "{}: '{}' at depth {} using offset {} and step {}".format(srcFile,
                        loggername, depth, __depthOffset, __depthStep))
            except ValueError:
                break

        if debug: 
            print(debugPrefix() + "loggername: '{}'".format(loggername))
            print(debugPrefix() + "   at depth: {}".format(depth))

        return loggername, depth
    
    def trySteps():
    # When new versions of setuptools are released, use this to determine which step value works
    # This is for development only.
        for __depthStep in range(1, 9):
            # Start at this offset into the frame stack
            print ("---------------- step = {}".format(__depthStep))
            loggername, depth = getLoggername(__depthOffset, __depthStep)
            if not name_eq_main():
                being_run_inside_setuptools_wrapper()
        print("----------------")
            

    def setTopLevelLogger(logger, loggername):
        # If this is a top level module, set the formatters and handlers for it.
        # Children of this logger will inherit these behaviors

        if debug: print (debugPrefix() + "----------- Setting up top level logger!")
        # Formatting and output styles
        fmt='%(asctime)s - %(module)s %(funcName)s [%(lineno)4d] - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt)

        # File handler - DEBUG
        logdir = os.getcwd()
        if "ER_LOG_DIR" in os.environ:
            envlogdir = os.environ["ER_LOG_DIR"]
            if debug:
                print(debugPrefix() + "Found ER_LOG_DIR: {}".format(envlogdir))
            logdir = os.path.abspath(os.path.expanduser(envlogdir))
        if explicitLogDir:
            logdir = explicitLogDir
        logfile = os.path.join(logdir, loggername + ".log")
        if debug:
            print(debugPrefix() + "logfile: {}".format(logfile))
        fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=10485760, backupCount=5)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        # Email handler - ERROR and CRITICAL only (includes .exception() calls)
        if "ER_EMAIL_CONFIG" in os.environ:
            preSetupEmailFromConfig(os.environ["ER_EMAIL_CONFIG"])
        if emailConfigFile:
            preSetupEmailFromConfig(emailConfigFile)
        if len(emailSetupInfo) > 0:
            try:
                emailHandler = logging.handlers.SMTPHandler(**(emailSetupInfo))
                emailHandler.setLevel(logging.ERROR)
                emailHandler.setFormatter(formatter)
                logger.addHandler(emailHandler)
            except Exception as e:
                print(e)
    
        # Colored syntax stderr handler - DEBUG
        styles={
            'asctime': {'color': 'green'}, 'module': {'color': 'magenta'}, 
            'levelname': {'color': 'white', 'bold': True}, 
            'funcName': {'color': 'cyan'}, 'programname': {'color': 'blue'}
        }
        coloredlogs.install(level='DEBUG', fmt=fmt, field_styles=styles, logger=logger)
    
        # Default level for logger
        logger.setLevel(logging.WARNING)

        # Default exception behavior - don't raise
        logging.raiseExceptions = True
        
        # if debug: trySteps()

    if __depthStep:
        # Old approach
        loggername, depth = getLoggername(__depthOffset, __depthStep)
        logger = logging.getLogger(loggername)

        if name_eq_main() or being_run_inside_setuptools_wrapper():
            setTopLevelLogger(logger, loggername)
        else:
            if debug: print ("Not top level logger, will inherit setup from parent logger(s)")

    else:
        # New approach
        modules = getFrameStackPseudoModules()
        modules = [n for n in modules if 'erlogging' not in n]
        modules = modules[:-1]
        if len(modules) == 0:
            modules.append('erlogging')
        if debug: print (modules)
        loggername = '.'.join(modules)
        logger = logging.getLogger(loggername)
        if len(modules) == 1:
            setTopLevelLogger(logger, loggername)
        else:
            if debug: print ("Not top level logger, will inherit setup from parent logger(s)")

    return logger


###########################################
##
# Utility functions for debugging loggers
##
##



def printLoggerInfo(logger):
    print(logger)
    # print(dir(logger))
    for l in dir(logger):
        print(l, logger.__getattribute__(l))


def printHandlerInfo(handler):
    print('-------------------------------------------------------\n', handler)
    # print(dir(handler))
    for l in dir(handler):
        print(l, handler.__getattribute__(l))


###########################################
##
# Abandonded code for other approaches for getting name of modules
##
##
def stack_depth():
    depth = 0
    while True:
        try:
            print("stack_depth:", sys._getframe(depth).f_globals['__file__'])
            depth += 1
        except ValueError as e:
            break
    return depth


__importedBy = None


def imported_from(depth=0):
    # skip the frames of this function, and the caller
    f = sys._getframe(depth + 2)
    while f and f.f_code.co_filename.startswith("<frozen importlib._bootstrap"):
        f = f.f_back
    print(stack_depth())
    return sys._getframe(6).f_globals['__file__']


def getModuleName():
    depth = 0
    loggername = ""
    while True:
        try:
            srcFile = sys._getframe(depth).f_globals.get('__file__')
            if srcFile == None:
                break
            print(os.path.splitext(os.path.basename(srcFile)))
            importScope = os.path.splitext(os.path.basename(srcFile))[0]
            if depth == 0:
                loggername = importScope
            else:
                if not importScope.startswith('_bootstrap') and loggername != importScope:
                    loggername = importScope + "." + loggername
            depth += 1
        except ValueError:
            break
    print("def:", loggername, depth)
    return int(depth/6), loggername


###########################################
##
# Simple tester __main__
##
##
if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='ER Logging Demo')
    # Debugging and testing
    parser.add_argument('--verbose', default=False, action='store_true')
    parser.add_argument('--debug', default=False, action='store_true')
    args = parser.parse_args()

    logger = setup(lambda depth: sys._getframe(depth), debug=True)
    if args.verbose:
        logger.setLevel(INFO)
    if args.debug:
        logger.setLevel(DEBUG)

    logger.debug("Messages")
    logger.info("From")
    logger.warning("Bad")
    logger.error("To")
    logger.critical("Worst")

    # printHandlerInfo(logger)
    # printLoggerInfo(logger)
