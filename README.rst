errutils
========

Elemental Reasoning reporting utilities

Just some simple utilities that aid in logging and reporting errors

erlogging
---------

Copy the following code to the beginning of each file::

	from errutils import erlogging
	logger = erlogging.setup(lambda depth: sys._getframe(depth))

That's it.  Use the logger as normal from logging module.  


It has two default handlers, and one optional one.

1) Colored stderr output - if you are on a terminal that is not color capable, it falls back to monochrome

Set to WARNING by default.

2) A rotating file handler

Uses the same format as stderr output, but set to `DEBUG` by default.  

`logger.setLevel` will let you control both at one shot.

Use `erlogging.<LOG_LEVEL>` instead of `logging.<LOG_LEVEL>` if you like, they're provided for convenience.

Default location for writing the log files is "./", but this is where the *script* resides, not where it is being run from.
This is probably less than useful if you have installed this package with pip.  You have two options
for indicating where the logs should be written:

- Set shell environment variable ER_LOG_DIR
- Pass the path as an argument to erlogging.setup as named parameter explicitLogDir:
	from errutils import erlogging
	logger = erlogging.setup(lambda depth: sys._getframe(depth), explicitLogDir="path/to/log/directory/")

If both are provided, explicitLogDir wins.  This allows your code to modify it on a per-run basis, for
instance taking the path from a config file or command line option.

3) Email of CRITICAL errors

If you wish to have critical logging sent to you via email, erlogging uses the emailer module below and can
be enabled in a manner similar to setting the log output directory:

In that case, set up the logger with:

	from errutils import erlogging
	logger = erlogging.setup(lambda depth: sys._getframe(depth), emailConfigFile="path/to/myEmail.config")

Additionally, setting ER_EMAIL_CONFIG as below will enable erlogging to send emails for 
critical messages using the provided configuration.

If both are provided, emailConfigFile wins, for the same reasons as for ER_LOG_DIR above.


emailer
-------

A simple email wrapper useful with erlogging::

	from errutils import emailer
	mailer = emailer.Emailer("path/to/myEmail.config")
	mailer.sendEmail("toaddr@company.com", "fromaddr@company.com", "Subject line", "Message body\ncontinued.")
	mailer.sendEmail("Message body using defaults\n")

Note that all mail will be sent using the account data in myEmail.config.

Example myEmail.config::

	[DEFAULT]
	mailhost=smtp.gmail.com 587
	fromaddr=tool@company.com
	toaddr=admin@company.com
	subject=I regret to inform you...
	credentials=tool@company.com plaintextpasswordyesthisisstupid
	secure=

Set shell environment variable ER_EMAIL_CONFIG to provide a default for all scripts to use.

