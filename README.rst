# errutils

## erlogging

Copy the following code to the beginning of each file:

	import erlogging
	logger = erlogging.setup(lambda depth: sys._getframe(depth))

That's it.  Use the logger as normal from logging module.  It has two handlers:
1) Colored stderr output - if you are on a terminal that is not color capable, it falls back to monochrome
2) A rotating file handler
Both use the same format, and are set to `DEBUG` by default.  `logger.setLevel` will let you control both at one shot.

Use `erlogging.<LOG_LEVEL>` instead of `logging.<LOG_LEVEL>` if you like, they're provided for convenience.

## emailer
A simple email wrapper useful with erlogging.

	from emailer import Emailer
	emailer = Emailer("myEmail.config")
	emailer.sendEmail("toaddr@company.com", "fromaddr@company.com", "Subject line", "Message body\ncontinued.")
	emailer.sendEmail("Message body using defaults\n")

Note that all mail will be sent using the account data in myEmail.config.

Example myEmail.config:

	[DEFAULT]
	mailhost=smtp.gmail.com 587
	fromaddr=tool@company.com
	toaddr=admin@company.com
	subject=I regret to inform you...
	credentials=tool@company.com plaintextpasswordyesthisisstupid
	secure=

