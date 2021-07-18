#!/usr/bin/env python3
"""
Copyright Elemental Reasoning, LLC, 2019
All rights reserved unless otherwise specified in licensing agreement.
---------------
"""

import sys
import os

from . import erlogging
erlogging.preSetupEmailFromConfig("omgEmailSetup.config")
logger = erlogging.setup(lambda depth: sys._getframe(depth))

import configparser
import smtplib
import ssl
class Emailer(object):
    def __init__(self, configFile, persistent_connection = False):
        if os.path.exists(configFile):
            config = configparser.ConfigParser()
            config.read(configFile)
            self.host, self.port = config.get('DEFAULT', 'mailhost').split()
            self.sender_email = config.get('DEFAULT', 'fromaddr')
            self.username, self.password = config.get('DEFAULT', 'credentials').split()
            self.server = None
            if persistent_connection:
                self.server = smtplib.SMTP_SSL(self.host, self.port, context=ssl.create_default_context())
                self.login(self.username, self.password)
        else:
            logger.error("No config file at: {}".format(configFile))
            logger.error("Will not email errors or alerts")
            self.host = None
    
    def sendEmail(self, to, subject, message):
        try:
            if self.host == None:
                logger.error("Attempted to send mail, mailer not configured")
                logger.error("To: %s" % (to))
                logger.error("Subject: %s" % (subject))
                logger.error("Message: %s" % (message))
                return
            if self.server:
                server.sendmail(sender_email, receiver_email, "Subject: " + subject + "\n\n" + message)
            else:
                with smtplib.SMTP_SSL(self.host, self.port) as server:
                # with smtplib.SMTP_SSL(self.host, self.port, context=ssl.create_default_context()) as server:
                # with smtplib.SMTP(self.host, self.port) as server:
                    # server.ehlo()
                    # server.start_ttls()
                    # logger.debug("Logging in as %s / %s" % (self.username, self.password))
                    server.login(self.username, self.password)
                    server.sendmail(self.sender_email, to, "Subject: " + subject + "\n\n" + message)
                    logger.debug("Mail sent")
        except (Exception) as e:
            logger.error("Mail error: Attempting to send from %s through %s:%s" % (self.sender_email, self.host, self.port))
            logger.error("\tTo: %s" % (to))
            logger.error("\tSubject: %s" % (subject))
            logger.error("\tMessage: %s" % (message))
            logger.exception(e)
