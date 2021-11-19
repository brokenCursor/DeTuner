# -*- coding: utf-8 -*-
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
import traceback
import sys


class DeWorker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    callback (function): The function callback to run on this worker thread. Supplied args and
                        kwargs will be passed through to the runner.

    args (list): Arguments to pass to the callback function

    kwargs (dict):  Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(DeWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = DeWorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        ''' Initialise the runner function with passed args, kwargs. '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            # Return the result of the processing
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()  # Done


class DeWorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Signals:

    finished (): No data

    error (tuple): 
            data about error: (exctype, value, traceback.format_exc())

    result (Any): object data returned from processing

    progress (int): progress in %
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(tuple)
