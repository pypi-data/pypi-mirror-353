import importlib
import inspect
import logging
import os
import sys
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Set, Type, get_type_hints

from framefox.core.di.exceptions import (
    CircularDependencyError,
    ServiceInstantiationError,
    ServiceNotFoundError,
)
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Union
from framefox.core.di.service_config import ServiceConfig
from framefox.core.di.service_definition import ServiceDefinition
from framefox.core.di.service_factory_manager import ServiceFactoryManager
from framefox.core.di.service_registry import ServiceRegistry

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class ServiceContainer:
    """
    Advanced dependency injection container for the Framefox framework.

    Features:
    - Automatic service discovery and registration
    - Dependency injection with type hints
    - Service factories and method calls
    - Tag-based service grouping
    - Circular dependency detection
    - Performance optimizations with caching
    - Thread safety considerations
    """

    _instance: Optional["ServiceContainer"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceContainer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._logger = logging.getLogger("SERVICE_CONTAINER")
        self._ensure_python_path()

        # Core components
        self._registry = ServiceRegistry()
        self._factory_manager = ServiceFactoryManager()
        self._config = ServiceConfig()

        # Instance storage and tracking
        self._instances: Dict[Type[Any], Any] = {}
        self._resolution_cache: Dict[Type[Any], Any] = {}
        self._circular_detection: Set[Type[Any]] = set()

        # ✅ LAZY LOADING : Cache et état
        self._scanned_modules: Set[str] = set()
        self._module_scan_cache: Dict[str, List[Type]] = {}
        
        # ✅ LAZY LOADING : État du scan src
        self._src_scanned: bool = False
        self._src_scan_in_progress: bool = False
        self._src_scan_future: Optional[Any] = None
        self._src_paths: List[Path] = []
        self._excluded_directories: List[str] = []
        self._excluded_modules: List[str] = []

        # ✅ ASYNCHRONE : Thread pool pour le scan
        self._executor: Optional[ThreadPoolExecutor] = None
        self._background_scan_enabled: bool = True

        # Initialization state
        self._instance_counter = 1
        self._initialized = True

        # ✅ LAZY : Initialiser SEULEMENT le core
        self._initialize_container()
    def _process_module(self, module_name: str) -> None:
        """Process a module with caching."""
        

        if module_name in self._scanned_modules:
            return
            
        if module_name in self._module_scan_cache:
            # Utiliser le cache
            for service_class in self._module_scan_cache[module_name]:
                if not self._registry.has_definition(service_class):
                    self._create_and_register_definition(service_class)
            return

        try:
            module = importlib.import_module(module_name)
            discovered_services = []
            
            for attr_name in dir(module):
                try:
                    attr = getattr(module, attr_name)
                    if (inspect.isclass(attr) and 
                        attr.__module__ == module_name and 
                        self._can_be_service(attr)):
                        
                        discovered_services.append(attr)
                        self._create_and_register_definition(attr)
                        
                except Exception:
                    pass
            
       
            self._module_scan_cache[module_name] = discovered_services
            self._scanned_modules.add(module_name)
            
        except (ModuleNotFoundError, ImportError):
            self._scanned_modules.add(module_name)
    def _ensure_python_path(self) -> None:
        """Ensure project directory is in PYTHONPATH."""
        # Add the root directory of the framefox project
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        project_root_str = str(project_root)
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)
        
        # Add the current working directory
        current_dir = str(Path.cwd())
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            self._logger.debug(f"Added current directory to PYTHONPATH: {current_dir}")
        
        # Add parent of src folder explicitly
        src_paths = self._find_source_paths()
        for src_path in src_paths:
            if src_path.exists():
                # Add parent of src folder to PYTHONPATH
                src_parent = str(src_path.parent)
                if src_parent not in sys.path:
                    sys.path.insert(0, src_parent)
                    self._logger.debug(f"Added src parent directory to PYTHONPATH: {src_parent}")

    def _initialize_container(self) -> None:
        """Initialize the container with all services."""
        try:
            self._create_module_aliases()
            self._register_essential_services()
            self._discover_and_register_services()
            # self._registry.freeze()

        except Exception as e:
            self._logger.error(f"Failed to initialize service container: {e}")
            raise
    def freeze_registry(self) -> None:
        """Freeze the registry when initialization is complete."""
        if not self._registry._frozen:
            self._registry.freeze()
            self._logger.debug("Service registry frozen after complete initialization")
    def _create_module_aliases(self) -> None:
        """Create module aliases for easier imports (framefox.X -> framefox.core.X)."""
        core_modules = [
            "controller",
            "routing",
            "logging",
            "di",
            "events",
            "config",
            "debug",
            "request",
            "orm",
            "templates",
            "security",
            "middleware",
            "kernel",
        ]

        for module_name in core_modules:
            core_module = f"framefox.core.{module_name}"
            alias_name = f"framefox.{module_name}"

            if alias_name not in sys.modules:
                try:
                    module = importlib.import_module(core_module)
                    sys.modules[alias_name] = module
                except ModuleNotFoundError:
                    pass

    def _register_essential_services(self) -> None:
        """Register essential services that must be available early."""
        essential_services = [
            "framefox.core.request.session.session.Session",
            "framefox.core.config.settings.Settings",
            "framefox.core.logging.logger.Logger",
            "framefox.core.security.user.entity_user_provider.EntityUserProvider",
            "framefox.core.orm.entity_manager_registry.EntityManagerRegistry",
            "framefox.core.bundle.bundle_manager.BundleManager",

            "framefox.core.security.token_storage.TokenStorage",
            "framefox.core.security.user.user_provider.UserProvider",
            "framefox.core.security.handlers.security_context_handler.SecurityContextHandler",
            "framefox.core.orm.entity_manager_interface.EntityManagerInterface",
            "framefox.core.security.handlers.firewall_handler.FirewallHandler",
        ]

        for service_path in essential_services:
            try:
                service_cls = self._import_service_class(service_path)
                definition = ServiceDefinition(service_cls, public=True, synthetic=True, tags=["essential"])
                self._registry.register_definition(definition)

                # Immediately instantiate essential services
                self.get(service_cls)

            except Exception as e:
                self._logger.warning(f"Could not register essential service {service_path}: {e}")

    def _import_service_class(self, service_path: str) -> Type[Any]:
        """Import a service class from its full path."""
        parts = service_path.split(".")
        module_path = ".".join(parts[:-1])
        class_name = parts[-1]

        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    def _discover_and_register_services(self) -> None:
        """Discover services with lazy loading and background scanning."""
        
        # ✅ ÉTAPE 1 : Scanner SEULEMENT le core (synchrone, rapide)
        core_path = Path(__file__).resolve().parent.parent
        
        # Configuration des exclusions
        self._excluded_directories = list(self._config.excluded_dirs) + [
            "entity", "entities", "Entity",
            "migration", "migrations", "Migrations",
            "test", "tests", "Test", "Tests",
            "__pycache__", ".pytest_cache", ".mypy_cache",
            "node_modules", "venv", "env", ".env",
            "docs", "documentation",
        ]

        self._excluded_modules = list(self._config.excluded_modules) + [
            "src.entity", "src.entities", "framefox.core.entity",
            "src.migration", "src.migrations", "src.test", "src.tests",
            "framefox.tests", "framefox.test",
        ]

        # Scanner le core immédiatement (essentiel pour le framework)
        self._scan_for_service_definitions(core_path, "framefox.core", self._excluded_directories, self._excluded_modules)
        
        # ✅ ÉTAPE 2 : Préparer le scan src (lazy)
        self._src_paths = self._find_source_paths()
        
        # ✅ ÉTAPE 3 : Démarrer le scan asynchrone si projet important
        if self._should_use_background_scan():
            self._start_background_src_scan()


    def _find_source_paths(self) -> List[Path]:
        """Find potential source paths for service discovery."""
        src_paths = []

        # Development path
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        dev_src_path = project_root / "src"
        if dev_src_path.exists():
            src_paths.append(dev_src_path)

        # Current working directory
        cwd_src_path = Path.cwd() / "src"
        if cwd_src_path.exists() and cwd_src_path not in src_paths:
            src_paths.append(cwd_src_path)

        # Search parent directories
        parent = Path.cwd().parent
        for _ in range(3):
            parent_src = parent / "src"
            if parent_src.exists() and parent_src not in src_paths:
                src_paths.append(parent_src)
            parent = parent.parent

        return src_paths

    def _scan_for_service_definitions(
        self,
        base_path: Path,
        base_package: str,
        excluded_dirs: List[str],
        excluded_modules: List[str],
    ) -> None:
        """Scan directory for service classes and create their definitions."""
        
        for root, dirs, files in os.walk(base_path):
            root_path = Path(root)
            
            if self._should_exclude_directory(root_path, excluded_dirs):
                continue

            for file in files:
                if not self._should_process_file(file):
                    continue

                try:
                    module_name = self._build_module_name(root_path / file, base_path, base_package)

                    if self._should_exclude_module(module_name, excluded_modules):
                        continue

                    self._process_module(module_name)

                except Exception as e:
                    pass

    def _should_exclude_directory(self, path: Path, excluded_dirs: List[str]) -> bool:
        """Check if a directory should be excluded from scanning."""
        dir_name = path.name.lower()
        
        # Always valid exclusions
        always_exclude = {
            "__pycache__", ".pytest_cache", ".mypy_cache",
            "node_modules", "venv", "env", ".env"
            
        }
        
        if dir_name in always_exclude:
            return True
        
        # Contextual exclusions
        contextual_exclusions = {
            "test": ["src", "framefox"],
            "tests": ["src", "framefox"],
            "entity": ["src"],
            "entities": ["src"],
            "migration": ["src", "framefox"],
            "migrations": ["src", "framefox"],
            "templates": ["src"],          
            "static": ["src"],              
            "assets": ["src"],             
            "docs": ["src", "framefox"], 
            "documentation": ["src", "framefox"],
        }
        
        if dir_name in contextual_exclusions:
            allowed_parents = contextual_exclusions[dir_name]
            path_parts = [part.lower() for part in path.parts]
            
            if any(parent in path_parts for parent in allowed_parents):
                return True
        
        # Check configured exclusions
        for excluded_dir in excluded_dirs:
            if dir_name == excluded_dir.lower():
                return True
        
        return False

    def _should_process_file(self, filename: str) -> bool:
        """Check if a file should be processed for service discovery."""

        if not filename.endswith(".py"):
            return False

        ignored_files = [
            "__init__.py",
            "service_container.py",
            "conftest.py",
            "test_*.py",
            "*_test.py",
            "migrations.py",
            "migration.py",
            "settings.py",
            "config.py",
        ]

        for pattern in ignored_files:
            if pattern.startswith("*"):
                if filename.endswith(pattern[1:]):
                    return False
            elif pattern.endswith("*"):
                if filename.startswith(pattern[:-1]):
                    return False
            elif filename == pattern:
                return False

        return True

    def _build_module_name(self, file_path: Path, base_path: Path, base_package: str) -> str:
        """Build module name from file path."""
        rel_path = file_path.relative_to(base_path).with_suffix("").as_posix().replace("/", ".")

        if rel_path:
            return f"{base_package}.{rel_path}"
        else:
            return base_package

    def _should_exclude_module(self, module_name: str, excluded_modules: List[str]) -> bool:
        """Check if a module should be excluded."""
        return any(module_name.startswith(excluded) for excluded in excluded_modules)

    def _process_module(self, module_name: str) -> None:
        """Process a module with enhanced caching."""
        
        # ✅ CACHE : Vérifier si déjà scanné
        if module_name in self._scanned_modules:
            return
            
        # ✅ CACHE : Utiliser le cache si disponible
        if module_name in self._module_scan_cache:
            for service_class in self._module_scan_cache[module_name]:
                if not self._registry.has_definition(service_class):
                    self._create_and_register_definition(service_class)
            self._scanned_modules.add(module_name)
            return

        # ✅ SCAN : Scanner et mettre en cache
        try:
            module = importlib.import_module(module_name)
            discovered_services = []
            
            for attr_name in dir(module):
                try:
                    attr = getattr(module, attr_name)
                    if (inspect.isclass(attr) and 
                        attr.__module__ == module_name and 
                        self._can_be_service(attr)):
                        
                        discovered_services.append(attr)
                        self._create_and_register_definition(attr)
                        
                except Exception:
                    pass
            
            # ✅ CACHE : Mettre en cache les résultats
            self._module_scan_cache[module_name] = discovered_services
            self._scanned_modules.add(module_name)
            
        except (ModuleNotFoundError, ImportError):
            # ✅ CACHE : Marquer comme scanné même en cas d'échec
            self._scanned_modules.add(module_name)

    def _create_and_register_definition(self, service_class: Type[Any]) -> None:
        """Create and register a service definition."""
        is_public = self._config.is_public(service_class)
        autowire = self._config.autowire_enabled
        tags = self._config.get_service_tags(service_class)

        # Add default tag based on the module
        default_tag = self._get_default_tag(service_class)
        if default_tag and default_tag not in tags:
            tags.append(default_tag)

        definition = ServiceDefinition(
            service_class,
            public=is_public,
            tags=tags,
            autowire=autowire,
        )

        self._registry.register_definition(definition)

    def _can_be_service(self, cls: Type) -> bool:
        """Determine if a class can be a service."""
       
        
        if not inspect.isclass(cls):
            return False

        # Ignore exceptions
        if issubclass(cls, Exception):
            return False

        module_name = cls.__module__

        # Check module
        if not (module_name.startswith("framefox.") or module_name.startswith("src.")):
            return False

        # Ignore built-in modules and libraries
        builtin_modules = [
            "builtins",
            "typing",
            "abc",
            "datetime",
            "pathlib",
            "logging",
            "_contextvars",
            "collections",
            "functools",
            "itertools",
            "operator",
            "re",
            "json",
            "urllib",
            "http",
            "ssl",
            "socket",
            "threading",
            "multiprocessing",
            "asyncio",
            "concurrent",
            "queue",
            "time",
        ]

        # Ignore all external libraries that are not part of the core framework
        external_libraries = [
            "fastapi",
            "starlette",
            "pydantic",
            "sqlalchemy",
            "sqlmodel",
            "alembic",
            "jinja2",
            "email",
            "passlib",
            "bcrypt",
            "cryptography",
            "requests",
            "urllib3",
            "certifi",
            "charset_normalizer",
            "idna",
            "bs4",
            "lxml",
            "markupsafe",
            "click",
            "rich",
            "typer",
            "uvicorn",
            "gunicorn",
            "pytest",
            "coverage",
            "mypy",
        ]

        module_name = cls.__module__

        if any(module_name == builtin or module_name.startswith(f"{builtin}.") for builtin in builtin_modules):
            return False

        if any(module_name == lib or module_name.startswith(f"{lib}.") for lib in external_libraries):
            return False

        if (
            hasattr(cls, "__pydantic_self__")
            or hasattr(cls, "__pydantic_model__")
            or hasattr(cls, "__pydantic_core_schema__")
            or hasattr(cls, "model_config")
        ):
            return False

        if cls.__name__.startswith("I") and hasattr(cls, "__abstractmethods__") and len(cls.__abstractmethods__) > 0:
            return False

        if (
            hasattr(cls, "__abstractmethods__")
            and len(cls.__abstractmethods__) > 0
            and len([m for m in dir(cls) if not m.startswith("_") and callable(getattr(cls, m))]) == len(cls.__abstractmethods__)
        ):
            return False

        if cls.__name__.startswith("_"):
            return False

        if hasattr(cls, "__service__") and not cls.__service__:
            return False

        try:
            import enum

            if issubclass(cls, enum.Enum):
                return False
        except (ImportError, TypeError):
            pass

        if hasattr(cls, "__dataclass_fields__") and not hasattr(cls, "__post_init__"):

            custom_methods = [
                name
                for name in dir(cls)
                if not name.startswith("_")
                and callable(getattr(cls, name))
                and name not in ["__dataclass_fields__", "__dataclass_params__"]
            ]
            if len(custom_methods) == 0:
                return False

        if not any(callable(getattr(cls, attr)) and not attr.startswith("_") for attr in dir(cls)):
            return False

        if not (module_name.startswith("framefox.") or module_name.startswith("src.")):
            return False

        if self._config.is_excluded_class(cls.__name__):
            return False

        if self._config.is_excluded_module(cls.__module__):
            return False

        if self._config.is_in_excluded_directory(cls.__module__):
            return False
        if (hasattr(cls, "__pydantic_self__") or 
            hasattr(cls, "__pydantic_model__") or
            hasattr(cls, "__pydantic_core_schema__") or
            hasattr(cls, "model_config")):
            return False

        if cls.__name__.startswith("_"):
            return False

        if hasattr(cls, "__service__") and not cls.__service__:
            return False

        return True

    def _get_default_tag(self, service_class: Type) -> str:
        """Convert the module name to a tag."""
        module_name = service_class.__module__
        parts = module_name.split(".")
        if parts[0] in ["framefox", "src"]:
            parts = parts[1:]
        if len(parts) > 1 and parts[-1] == parts[-2]:
            parts = parts[:-1]

        return ".".join(parts)

    def get(self, service_class: Type[Any]) -> Any:
        """Retrieve or create an instance with lazy src loading."""
        
        # ✅ CACHE : Vérifier d'abord le cache
        if service_class in self._resolution_cache:
            return self._resolution_cache[service_class]

        if service_class in self._instances:
            cached_instance = self._instances[service_class]
            self._resolution_cache[service_class] = cached_instance
            return cached_instance

        # Handle non-class types
        if not inspect.isclass(service_class):
            return service_class

        # Handle primitive types
        if service_class in (str, int, float, bool, list, dict, set, tuple):
            instance = service_class()
            self._instances[service_class] = instance
            self._resolution_cache[service_class] = instance
            return instance

        # ✅ LAZY : Chercher la définition
        definition = self._registry.get_definition(service_class)
        
        # ✅ LAZY : Si pas trouvé ET que c'est un module src, forcer le scan
        if not definition and hasattr(service_class, '__module__'):
            module_name = service_class.__module__
            
            if module_name.startswith('src.'):
                # ✅ LAZY : Forcer le scan src si pas encore fait
                if not self._src_scanned:
                    self._ensure_src_scanned_sync()
                    definition = self._registry.get_definition(service_class)
                
                # ✅ LAZY : Ou scanner le module spécifique s'il n'est pas en cache
                if not definition and module_name not in self._scanned_modules:
                    self._scan_specific_module(module_name)
                    definition = self._registry.get_definition(service_class)

        # Check for circular dependencies
        if service_class in self._circular_detection:
            chain = list(self._circular_detection)
            raise CircularDependencyError(service_class, chain)

        # Use _find_or_create_definition as fallback
        if not definition:
            definition = self._find_or_create_definition(service_class)
            if not definition:
                silent_classes = {"FastAPI", "Depends", "Request", "Response"}
                if service_class.__name__ not in silent_classes:
                    self._logger.debug(f"No service definition found for {service_class.__name__}")
                raise ServiceNotFoundError(service_class)


        # Cannot instantiate abstract classes
        if definition.abstract:
            raise ServiceInstantiationError(
                service_class,
                Exception(f"Cannot instantiate abstract class {service_class.__name__}")
            )

        # Mark as being resolved
        self._circular_detection.add(service_class)

        self._circular_detection.add(service_class)

        try:
            instance = self._create_service_instance(definition)
            if instance is not None:
                self._instances[service_class] = instance
                self._resolution_cache[service_class] = instance
                self._apply_method_calls(instance, definition)
                return instance
            else:
                raise ServiceInstantiationError(service_class, Exception("Failed to create instance"))

        except Exception as e:
            if isinstance(e, (CircularDependencyError, ServiceNotFoundError, ServiceInstantiationError)):
                raise
            raise ServiceInstantiationError(service_class, e)
        finally:
            self._circular_detection.discard(service_class)
    def _find_or_create_definition(self, service_class: Type) -> Optional[ServiceDefinition]:
        """Finds an existing service definition or creates a new one if possible."""
        # First, look for an existing definition
        definition = self._registry.get_definition(service_class)
        if definition:
            return definition

        # If it's not a class, we can't create a definition
        if not inspect.isclass(service_class):
            return None

        # Check if the class can be a service
        if self._can_be_service(service_class):
            # Create a default definition
            tags = []
            default_tag = self._get_default_tag(service_class)
            if default_tag:
                tags.append(default_tag)

            definition = ServiceDefinition(service_class, tags=tags)
            self._registry.register_definition(definition)
            return definition

        return None
    def _create_dynamic_definition(self, service_class: Type[Any]) -> Optional[ServiceDefinition]:
        """Create a service definition dynamically if the class qualifies."""
        if self._can_be_service(service_class):
            definition = ServiceDefinition(service_class, tags=[self._get_default_tag(service_class)])
            self._registry.register_definition(definition)
            return definition
        return None

    def _create_service_instance(self, definition: ServiceDefinition) -> Any:
        """Create a service instance using various strategies."""
        service_class = definition.service_class

        # Use factory if available
        if definition.factory:
            return definition.factory()

        # Try registered service factories
        instance = self._factory_manager.create_service(service_class, self)
        if instance is not None:
            return instance

        # Use explicit arguments if provided
        if definition.arguments:
            return service_class(*definition.arguments)

        # Standard autowiring
        if definition.autowire:
            dependencies = self._resolve_dependencies(service_class)
            return service_class(*dependencies)
        else:
            return service_class()

    def _resolve_dependencies(self, service_class: Type[Any]) -> List[Any]:
        """Resolve the dependencies of a service class for autowiring."""
        dependencies = []

        try:
            constructor = inspect.signature(service_class.__init__)
            params = constructor.parameters

            # Get type annotations
            try:
                module = sys.modules[service_class.__module__]
                type_hints = get_type_hints(
                    service_class.__init__,
                    localns=vars(service_class),
                    globalns=module.__dict__,
                )

                for name, param in params.items():
                    if name == "self":
                        continue

                    dependency_cls = type_hints.get(name)

                    if dependency_cls:
                        # Recursively get the dependency
                        dependency = self.get(dependency_cls)
                        dependencies.append(dependency)
                    elif param.default != inspect.Parameter.empty:
                        # Use the default value if available
                        dependencies.append(param.default)
                    else:
                        # No type annotation and no default value
                        dependencies.append(None)
                        self._logger.warning(f"Parameter {name} of {service_class.__name__} has no type hint and no default value")

            except Exception as e:
                self._logger.error(f"Error getting type hints for {service_class.__name__}: {e}")

        except Exception as e:
            self._logger.error(f"Error analyzing constructor of {service_class.__name__}: {e}")

        return dependencies

    def _apply_method_calls(self, instance: Any, definition: ServiceDefinition) -> None:
        """Apply configured method calls to an instance."""
        for method_name, args in definition.method_calls:
            try:
                method = getattr(instance, method_name)
                method(*args)
            except Exception as e:
                self._logger.error(f"Error calling {method_name} on {definition.service_class.__name__}: {e}")

    def get_by_name(self, class_name: str) -> Optional[Any]:
        """Retrieve a service by its class name."""
        definition = self._registry.get_definition_by_name(class_name)
        if definition:
            return self.get(definition.service_class)

        self._logger.warning(f"Service with name '{class_name}' not found")
        return None

    def get_by_tag(self, tag: str) -> Optional[Any]:
        """Return the first service associated with a tag."""
        definitions = self._registry.get_definitions_by_tag(tag)

        if not definitions:
            return None

        if len(definitions) > 1:
            service_names = [def_.service_class.__name__ for def_ in definitions]
            self._logger.warning(f"Multiple services found for tag '{tag}': {', '.join(service_names)}. Returning first.")

        return self.get(definitions[0].service_class)

    def get_all_by_tag(self, tag: str) -> List[Any]:
        """Return all services associated with a tag."""
        definitions = self._registry.get_definitions_by_tag(tag)
        return [self.get(def_.service_class) for def_ in definitions]

    def has(self, service_class: Type[Any]) -> bool:
        """Check if a service is registered."""
        return self._registry.has_definition(service_class)

    def has_by_name(self, class_name: str) -> bool:
        """Check if a service is registered by name."""
        return self._registry.has_definition_by_name(class_name)

    def set_instance(self, service_class: Type[Any], instance: Any) -> None:
        """Manually set a service instance."""
        self._instances[service_class] = instance
        self._resolution_cache[service_class] = instance

    def register_factory(self, factory) -> None:
        """Register a service factory."""
        self._factory_manager.register_factory(factory)

    def clear_cache(self) -> None:
        """Clear resolution cache (useful for testing)."""
        self._resolution_cache.clear()
        self._logger.debug("Resolution cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get container statistics."""
        registry_stats = self._registry.get_stats()

        return {
            "container_instance": self._instance_counter,
            "instantiated_services": len(self._instances),
            "cached_resolutions": len(self._resolution_cache),
            "registered_factories": len(self._factory_manager.get_factories()),
            **registry_stats,
        }
    def _should_use_background_scan(self) -> bool:
        """Déterminer si utiliser le scan asynchrone."""
        if not self._background_scan_enabled:
            return False
            
        # Compter le nombre de fichiers Python dans src
        total_files = 0
        for src_path in self._src_paths:
            if src_path.exists():
                try:
                    total_files += len(list(src_path.rglob("*.py")))
                except Exception:
                    pass
        
        # ✅ Seuil : + de 30 fichiers = scan async
        should_async = total_files > 30
        if should_async:
            self._logger.debug(f"Background scan enabled: {total_files} Python files detected")
        
        return should_async

    def _start_background_src_scan(self) -> None:
        """Démarrer le scan src en arrière-plan."""
        if self._src_scan_in_progress or self._src_scanned:
            return
        
        self._src_scan_in_progress = True
        
        def background_scan():
            try:
                # Petit délai pour laisser l'app démarrer
                threading.Event().wait(0.1)
                
                self._logger.debug("Starting background src scan...")
                start_time = time.time()
                
                # Scanner tous les paths src
                for src_path in self._src_paths:
                    if src_path.exists():
                        self._scan_for_service_definitions(
                            src_path, "src", 
                            self._excluded_directories, 
                            self._excluded_modules
                        )
                
                self._src_scanned = True
                self._src_scan_in_progress = False
                
                elapsed = time.time() - start_time
                total_services = len(self._registry.get_all_definitions())
                self._logger.debug(f"Background src scan completed in {elapsed:.2f}s. Total services: {total_services}")
                
            except Exception as e:
                self._logger.error(f"Background scan failed: {e}")
                self._src_scan_in_progress = False
        
        # ✅ ASYNCHRONE : Démarrer en thread daemon
        scan_thread = threading.Thread(target=background_scan, daemon=True)
        scan_thread.start()
    def _ensure_src_scanned_sync(self) -> None:
        """Forcer le scan src de manière synchrone si nécessaire."""
        if self._src_scanned:
            return
        
        if self._src_scan_in_progress:
            # Attendre que le scan en cours se termine (max 5 secondes)
            max_wait = 5.0
            wait_interval = 0.1
            waited = 0.0
            
            while self._src_scan_in_progress and waited < max_wait:
                threading.Event().wait(wait_interval)
                waited += wait_interval
            
            if self._src_scanned:
                return
        
        # Scanner immédiatement si pas encore fait
        self._logger.debug("Forcing synchronous src scan...")
        start_time = time.time()
        
        for src_path in self._src_paths:
            if src_path.exists():
                self._scan_for_service_definitions(
                    src_path, "src", 
                    self._excluded_directories, 
                    self._excluded_modules
                )
        
        self._src_scanned = True
        self._src_scan_in_progress = False
        
        elapsed = time.time() - start_time
        self._logger.debug(f"Synchronous src scan completed in {elapsed:.2f}s")
    def _scan_specific_module(self, module_name: str) -> None:
        """Scanner un module spécifique de manière optimisée."""
        if module_name in self._scanned_modules:
            return
        
        self._logger.debug(f"Lazy scanning module: {module_name}")
        
        try:
            # Utiliser le cache si disponible
            if module_name in self._module_scan_cache:
                for service_class in self._module_scan_cache[module_name]:
                    if not self._registry.has_definition(service_class):
                        self._create_and_register_definition(service_class)
            else:
                # Scanner le module
                self._process_module(module_name)
                
        except Exception as e:
            self._logger.debug(f"Failed to lazy scan module {module_name}: {e}")
    def get_scan_status(self) -> Dict[str, Any]:
        """Obtenir le statut du scan pour debugging."""
        return {
            "src_scanned": self._src_scanned,
            "src_scan_in_progress": self._src_scan_in_progress,
            "scanned_modules_count": len(self._scanned_modules),
            "cached_modules_count": len(self._module_scan_cache),
            "src_paths_count": len(self._src_paths),
            "background_scan_enabled": self._background_scan_enabled
        }

    def force_complete_scan(self) -> None:
        """Forcer un scan complet immédiatement (pour debugging)."""
        self._logger.debug("Forcing complete scan...")
        self._ensure_src_scanned_sync()

    def disable_background_scan(self) -> None:
        """Désactiver le scan en arrière-plan."""
        self._background_scan_enabled = False

    def __del__(self):
        """Cleanup des ressources."""
        if hasattr(self, '_executor') and self._executor:
            self._executor.shutdown(wait=False)