# -*- coding: utf-8 -*-

import logging
from inspect import cleandoc
from threading import Thread

class StreamToLogRedirector(object):
    """
    """
    def __init__(self, logger, stream_type = 'stdout'):
        self.logger =  logger
        if stream_type == 'stderr':
            self.level = logging.CRITICAL
        else:
            self.level = logging.INFO

    def write(self, message):
        """
        """
        message = message.strip()
        if message != '':
            if self.level != logging.CRITICAL:
                if '<DEBUG>' in message:
                    message = message.replace('<DEBUG>','').strip()
                    self.logger.warning(message)
                elif '<WARNING>' in message:
                    message = message.replace('<WARNING>','').strip()
                    self.logger.warning(message)
                elif '<ERROR>' in message:
                    message = message.replace('<ERROR>','').strip()
                    self.logger.error(message)
                elif '<CRITICAL>' in message:
                    message = message.replace('<ERROR>','').strip()
                    self.logger.critical(message)
                else:
                    self.logger.log(self.level, message)
            else:
               self.logger.log(self.level, message)

    def flush(self):
        return None

class QueueHandler(logging.Handler):
    """
    This handler sends events to a queue. Typically, it would be used together
    with a multiprocessing Queue to centralise logging to file in one process
    (in a multi-process application), so as to avoid file write contention
    between processes.

    This code is new in Python 3.2, but this class can be copy pasted into
    user code for use with earlier Python versions.
    """

    def __init__(self, queue):
        """
        Initialise an instance, using the passed queue.
        """
        logging.Handler.__init__(self)
        self.queue = queue

    def enqueue(self, record):
        """
        Enqueue a record.

        The base implementation uses put_nowait. You may want to override
        this method if you want to use blocking, timeouts or custom queue
        implementations.
        """
        self.queue.put_nowait(record)

    def prepare(self, record):
        """
        Prepares a record for queueing. The object returned by this
        method is enqueued.
        The base implementation formats the record to merge the message
        and arguments, and removes unpickleable items from the record
        in-place.
        You might want to override this method if you want to convert
        the record to a dict or JSON string, or send a modified copy
        of the record while leaving the original intact.
        """
        # The format operation gets traceback text into record.exc_text
        # (if there's exception data), and also puts the message into
        # record.message. We can then use this to replace the original
        # msg + args, as these might be unpickleable. We also zap the
        # exc_info attribute, as it's no longer needed and, if not None,
        # will typically not be pickleable.
        self.format(record)
        record.msg = record.message
        record.args = None
        record.exc_info = None
        return record

    def emit(self, record):
        """
        Emit a record.

        Writes the LogRecord to the queue, preparing it first.
        """
        try:
            self.enqueue(self.prepare(record))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

class GuiConsoleHandler(logging.Handler):
    """
    """
    def __init__(self, process_panel_dict):
        """
        """
        logging.Handler.__init__(self)
        self.process_panel_dict = process_panel_dict

    def emit(self, record):
        """
        Emit a record.

        Writes the LogRecord to the queue, preparing it first.
        """
        panel = self.process_panel_dict[record.processName]
        try:
            if record.levelname == 'INFO':
                panel.string += record.message + '\n'
            elif record.levelname == 'CRITICAL':
                panel.string += cleandoc('''An error occured please check the
                                log file for more details.''') + '\n'
            else:
                panel.string += record.levelname + ':' + \
                                                record.message + '\n'
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class QueueLoggerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, queue):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self.queue = queue
        self.go_on = True

    def run(self):
        """
        Pull any output from the queue while the process runs
        """
        while self.go_on:
            #Collect all display output from process
            record = self.queue.get()
            logger = logging.getLogger(record.name)
            logger.handle(record)