from Qt import QtCore

class Worker(QtCore.QThread):
    finished = QtCore.Signal()
    progress = QtCore.Signal(str)
    error = QtCore.Signal(str)
    
    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self._should_stop = False
    
    def stop(self):
        self._should_stop = True
        if not self.wait(2000):
            self.terminate()
        
    def run(self):
        try:
            self.task(self._should_stop, *self.args, **self.kwargs)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
