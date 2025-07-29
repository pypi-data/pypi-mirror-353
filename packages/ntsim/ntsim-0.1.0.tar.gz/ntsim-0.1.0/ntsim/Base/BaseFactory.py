import pkgutil
import importlib
import inspect
import logging
import sys
from argparse import Namespace

class BaseFactory:
    def __init__(self, base_package, base_class):
        self.log = logging.getLogger(f'NTSim.{self.__class__.__name__}')
        self.name = None
        self.blueprint = None
        self.known_instances = {}
        self.log.debug(base_class)
        self._find_instances(base_package, base_class)
        self.print_knowns()

    def print_knowns(self):
        self.log.info(f'known instances: {", ".join(self.known_instances.keys())}')

    def _find_instances(self, package_name, base_class):
        self.log.debug(f"Checking package: {package_name}")
        package = importlib.import_module(package_name)
        for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
            full_module_name = f"{package.__name__}.{name}"
            self.log.debug(f"Importing module: {full_module_name}")
            try:
                module = importlib.import_module(full_module_name)
            except ModuleNotFoundError as e:
                self.log.info(f"Skipping '{full_module_name}': missing module '{e.name}'")
                continue

            for attr_name in dir(module):
                attr_value = getattr(module, attr_name)

                if isinstance(attr_value, type):  # Ensure it's a class
                    self.log.debug(f"Checking class: {attr_value}")
                    is_subclass = issubclass(attr_value, base_class)
                    is_abstract = inspect.isabstract(attr_value)
                    self.log.debug(f"is_subclass: {is_subclass}")
                    self.log.debug(f"is_abstract: {is_abstract}")
                    if is_subclass and not is_abstract:
                        self.log.debug(f"Adding to known_instances: {attr_value}")
                        self.known_instances[attr_name] = attr_value

            if is_pkg:
                self._find_instances(full_module_name, base_class)


    def configure(self, opts, name_attr) -> None:
        instance_name = getattr(opts, name_attr)
        if instance_name in self.known_instances:
            self.blueprint = self.known_instances[instance_name]
            self.name      = instance_name
        elif instance_name is None:
            pass
        else:
            # Handle unknown instance name
            self.log.error(f'Unknown instance name={instance_name}')
            self.log.info(f'Known instances are: {list(self.known_instances.keys())}. EXIT')
            sys.exit()

#    def get_instance(self):
#        self.instance = self.known_instances[instance_name](instance_name)
#        return self.instance

    def get_blueprint(self):
        return self.blueprint
