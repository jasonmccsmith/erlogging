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
        preSetupEmail(tuple(config.get("DEFAULT", "mailhost").split()), \
                      config.get("DEFAULT", "fromaddr"), \
                      config.get("DEFAULT", "toaddr").split(), \
                      config.get("DEFAULT", "subject"), \
                      tuple(config.get("DEFAULT", "credentials").split()), \
                      tuple(config.get("DEFAULT", "secure").split()) \
                     )
    else:
        print ("ERROR:  (erlogging) No such email config file: '{}'".format(configfile))
    
# Set up this info as per logging.SMTPHandler
#   Example:
#       emailHostPort = ("smtp.gmail.com", 587)
#       emailCredentials = ("foo@gmail.com", "myvoiceismy")
#       emailFromAddr = 
#

def setup(nameGetter, explicitLogDir=None, logConfigFile=None, emailConfigFile=None):
    """Set up a logger for a module that calls this function.  This is a bit different.  
    We need the call to sys._getframe to happen in the file that we want info for, but 
    we can do that by having the file send us a lambda of the call.  We do all the heavy 
    lifting here, walking through the call stack to extract an import chain that we use 
    as the loggername, using depth of (useful) stack to set up handlers only when needed, etc."""
    
    global emailSetupInfo
    
    # Controls for stepping through sys._getframe
    # Step is dependent on Python version (boo)
    # Pre 3.3, it is 0, then with 3.3 it gets weird.  Look up by version
    import sys
    version = sys.version_info
    if version.major < 3:
        __depthStep = 0
    else:
        steps3 = [0, 0, 0, 9, 7, 6, 6, 6, 6, 6, 6]
        __depthStep = steps3[version.minor]
        # print (version.minor, steps3, steps3[version.minor])

    # Offset is to roll back from this call site to the function/lambda defined in the module of interest
    __depthOffset = 2

    # print("First level logger is at __depthStep + __depthOffset = {}".format(__depthStep + __depthOffset))
    
    depth = __depthOffset
    loggername = ""
    while True:
        try:
            srcFile = nameGetter(depth).f_globals.get('__file__')
            if srcFile == None:
                # print("ERROR: NO SOURCE FILE??")
                break
            importScope = os.path.splitext(os.path.basename(srcFile))[0]
            if depth == __depthOffset:
                loggername = importScope
            else:
                loggername = importScope + "." + loggername
            depth += __depthStep
            # print ("{}: '{}' at depth {} using offset {} and step {}".format(srcFile, loggername, depth, __depthOffset, __depthStep))
        except ValueError:
            break
    # print ("{}: '{}' at depth {}".format(srcFile, loggername, depth))
    
    # Get the bloody logger
    logger = logging.getLogger(loggername)
    # print("'{}'".format(loggername[:10]))
    
    # If this is a top level module, set the formatters and handlers for it.
    # Children of this logger will inherit these behaviors
    if   depth == __depthStep + __depthOffset or \
        (depth == __depthStep * 2 + __depthOffset and loggername[:8] == '__init__'):
        # Second clause is for when the top level is wrapped in a setuptools entry point
        # print ("----------- Setting up logger!")
        # Formatting and output styles
        fmt='%(asctime)s - %(module)s %(funcName)s [%(lineno)4d] - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt)

        # File handler - DEBUG
        logdir = os.getcwd()
        if "ER_LOG_DIR" in os.environ:
            envlogdir = os.environ["ER_LOG_DIR"]
            # print ("Found ER_LOG_DIR: {}".format(envlogdir))
            logdir = os.path.abspath(os.path.expanduser(envlogdir))
        if explicitLogDir:
            logdir = explicitLogDir
        logfile = os.path.join(logdir, loggername + ".log")
        # print ("logfile: {}".format(logfile))
        fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=10485760, backupCount=5, encoding='utf-8')
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
        
    return logger

###########################################
##
##  Utility functions for debugging loggers
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
##  Abandonded code for other approaches for getting name of modules
##
##
def stack_depth():
    depth = 0
    while True:
        try:
            print ("stack_depth:", sys._getframe(depth).f_globals['__file__'])
            depth +=1
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
##  Simple tester __main__
##
##
if __name__ == '__main__':
    import argparse, sys
    parser = argparse.ArgumentParser(description = 'OMG Google Sheets Demo')
    # Debugging and testing
    parser.add_argument('--verbose', default=False, action='store_true')
    parser.add_argument('--debug', default=False, action='store_true')
    args = parser.parse_args()

    logger = setup(lambda depth: sys._getframe(depth))
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
    # printLoggerInfo()
