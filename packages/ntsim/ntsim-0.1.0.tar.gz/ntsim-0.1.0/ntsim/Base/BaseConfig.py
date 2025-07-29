from abc import ABC, abstractmethod

class _logger_descriptor:
    """A class that will provide correct loggers for this given class"""
    def __get__(self, instance, owner):
        return logging.getLogger('NTSim.'+owner.__name__)
        
class BaseConfig(ABC):
    arg_dict = {}    
    logger = _logger_descriptor()
    
    @classmethod
    def add_args(cls, parser):
        for arg, meta in cls.arg_dict.items():
            unique_name = f"{cls.__name__}.{arg}"
            arg_options = {}
            if 'type' in meta:
                arg_options['type'] = meta['type']
            if 'default' in meta:
                arg_options['default'] = meta['default']
            if 'help' in meta:
                arg_options['help'] = meta['help']
            if 'action' in meta:
                arg_options['action'] = meta['action']
            if 'nargs' in meta:
                arg_options['nargs'] = meta['nargs']
#            print(unique_name,arg_options)
            parser.add_argument(f"--{unique_name}", **arg_options)

    def configure(self, opts):
        for arg in self.arg_dict.keys():
            unique_name = f"{self.__class__.__name__}.{arg}"
            if hasattr(opts, unique_name):
                value = getattr(opts, unique_name)
                setattr(self, arg, value)
                self.arg_dict[arg]['value'] = value
