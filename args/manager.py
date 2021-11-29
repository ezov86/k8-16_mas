from pattern_singleton import Singleton


class ArgsManager(metaclass=Singleton):
    def __init__(self):
        self.source_file_path = ''
        self.stop_after_parsing = False
        self.ignore_warnings = False
        self.use_csv = False
        self.use_intel_hex = False

    def init(self, args):
        self.__dict__.update(args.__dict__)
