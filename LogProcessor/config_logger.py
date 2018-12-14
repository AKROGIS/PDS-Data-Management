# This is a logger configuration dictionary.
# It is defined in https://docs.python.org/2/library/logging.config.html

config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'brief': {
            'format':  '%(name)-12s: %(levelname)-8s %(message)s',
        },
        'detailed': {
            'format':  '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            'datefmt': '%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        # command line arguments (--verbose and --debug will change the level of first handler to INFO and DEBUG)
        'console': {
            'class':     'logging.StreamHandler',
            'level':     'WARNING',
            'formatter': 'brief',
            'stream':    'ext://sys.stdout'
        },
        'file': {
            'class':     'logging.FileHandler',
            'level':     'INFO',
            'formatter': 'detailed',
            'filename':  'E:/Xdrive/Logs/LogProcessor.log'
        },
        'email': {
            'class':    'BufferingSMTPHandler.BufferingSMTPHandler',  # Bundle 100 messages into a single email
            # 'class':    'logging.handlers.SMTPHandler',  # Separate email for each message
            'level':     'ERROR',
            'formatter': 'detailed',
            'mailhost': 'mailer.itc.nps.gov',
            'fromaddr': 'regan_sarwas@nps.gov',
            'toaddrs':  ['regan_sarwas@nps.gov'],
            'subject':  'Error running Robocopy Log Processor'
        }
    },
    'root': {
        'level': 'NOTSET',
        # 'handlers': ['console', 'file']  # Do not send emails when testing
        'handlers': ['console', 'file', 'email']  # Send emails in production
    }
}
