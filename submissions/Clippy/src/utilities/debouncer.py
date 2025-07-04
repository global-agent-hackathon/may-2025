import threading


class Debouncer:
    def __init__(self, wait, callback):
        self.wait = wait
        self.callback = callback
        self.timer = None

    def call(self, *args, **kwargs):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(
            self.wait, lambda: self.callback(*args, **kwargs))
        self.timer.start()
