"""
Module registry for managing and loading ELLMa modules.
"""

import importlib
import inspect
from pathlib import Path
from typing import Dict, Type, Any, Optional, TypeVar, Generic, List

from ellma.utils.logger import get_logger

T = TypeVar('T')

class ModuleRegistry(Generic[T]):
    """
    A registry for managing and loading ELLMa modules.
    
    This class handles the registration, discovery, and instantiation of
    modules that extend the functionality of the ELLMa system.
    """
    
    def __init__(self, base_class: Type[T]):
        """
        Initialize the module registry.
        
        Args:
            base_class: The base class that all registered modules must inherit from
        """
        self.base_class = base_class
        self._modules: Dict[str, Type[T]] = {}
        self._instances: Dict[str, T] = {}
        self.logger = get_logger(__name__)
    
    def register(self, name: str) -> callable:
        """
        Decorator to register a module class.
        
        Args:
            name: The name to register the module under
            
        Returns:
            A decorator function that registers the class
        """
        def decorator(cls: Type[T]) -> Type[T]:
            if not inspect.isclass(cls) or not issubclass(cls, self.base_class):
                raise ValueError(f"Registered module must be a subclass of {self.base_class.__name__}")
            
            if name in self._modules:
                self.logger.warning(f"Overwriting module '{name}': {self._modules[name]} with {cls}")
            
            self._modules[name] = cls
            self.logger.debug(f"Registered module '{name}': {cls.__name__}")
            return cls
        
        return decorator
    
    def get(self, name: str, *args: Any, **kwargs: Any) -> Optional[T]:
        """
        Get an instance of a registered module.
        
        Args:
            name: The name of the module to get
            *args: Positional arguments to pass to the module's constructor
            **kwargs: Keyword arguments to pass to the module's constructor
            
        Returns:
            An instance of the requested module, or None if not found
        """
        if name in self._instances:
            return self._instances[name]
        
        if name not in self._modules:
            self.logger.error(f"Module '{name}' not found in registry")
            return None
        
        try:
            module_class = self._modules[name]
            instance = module_class(*args, **kwargs)
            self._instances[name] = instance
            return instance
        except Exception as e:
            self.logger.error(f"Failed to instantiate module '{name}': {e}", exc_info=True)
            return None
    
    def get_all(self) -> Dict[str, Type[T]]:
        """
        Get all registered module classes.
        
        Returns:
            A dictionary mapping module names to their classes
        """
        return self._modules.copy()
    
    def get_instance(self, name: str) -> Optional[T]:
        """
        Get an existing instance of a module if it exists.
        
        Args:
            name: The name of the module
            
        Returns:
            The module instance or None if not found
        """
        return self._instances.get(name)
    
    def discover_modules(self, module_path: str, base_package: str) -> None:
        """
        Discover and register modules in a directory.
        
        Args:
            module_path: Path to the directory containing modules
            base_package: The base package name (e.g., 'ellma.modules')
        """
        module_dir = Path(module_path)
        
        if not module_dir.exists() or not module_dir.is_dir():
            self.logger.warning(f"Module directory not found: {module_path}")
            return
        
        for py_file in module_dir.glob("*.py"):
            if py_file.name.startswith('_') or py_file.name == 'registry.py':
                continue
                
            module_name = py_file.stem
            full_module_name = f"{base_package}.{module_name}"
            
            try:
                module = importlib.import_module(full_module_name)
                
                # Find all classes in the module that are subclasses of base_class
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        issubclass(obj, self.base_class) and
                        obj != self.base_class and
                        obj.__module__ == module.__name__
                    ):
                        # Register with the class name as the default name
                        self._modules[module_name] = obj
                        self.logger.debug(f"Discovered module '{module_name}': {obj.__name__}")
                        
            except ImportError as e:
                self.logger.error(f"Failed to import module '{full_module_name}': {e}")
            except Exception as e:
                self.logger.error(f"Error processing module '{full_module_name}': {e}", exc_info=True)
    
    def clear(self) -> None:
        """Clear all registered modules and instances."""
        self._modules.clear()
        self._instances.clear()
    
    def __contains__(self, name: str) -> bool:
        """Check if a module is registered."""
        return name in self._modules
    
    def __getitem__(self, name: str) -> Type[T]:
        """Get a module class by name."""
        return self._modules[name]
    
    def __iter__(self):
        """Iterate over registered module names and classes."""
        return iter(self._modules.items())
