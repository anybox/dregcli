class Client(object):
    def __init__(self, url, verbose=False):
        super().__init__()
        self.url = url
        self.verbose = verbose
        self.request_kwargs = dict()

    def display(self, *args):
        if self.verbose:
            print(*args)
