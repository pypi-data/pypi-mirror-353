import importlib
import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, get_type_hints

from framefox.core.di.exceptions import (
    CircularDependencyError,
    ServiceInstantiationError,
    ServiceNotFoundError,
)
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

        # Initialization state
        self._instance_counter = 1
        self._initialized = True

        # Initialize container
        self._initialize_container()

    def _ensure_python_path(self) -> None:
        """Ensure project directory is in PYTHONPATH."""
        # 1. Ajouter le répertoire racine du projet framefox (pour le développement)
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        project_root_str = str(project_root)
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)
        
        # 2. ✅ SOLUTION : Ajouter le répertoire de travail actuel (pour les projets utilisateur)
        current_dir = str(Path.cwd())
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            self._logger.debug(f"Added current directory to PYTHONPATH: {current_dir}")
        
        # 3. ✅ SOLUTION ALTERNATIVE : Ajouter explicitement le parent du dossier src
        src_paths = self._find_source_paths()
        for src_path in src_paths:
            if src_path.exists():
                # Ajouter le parent du dossier src au PYTHONPATH
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
        """Discover and register all services from core and src directories."""
        print(f"🔍 [DEBUG] Starting service discovery...")
        
        # Find source paths
        src_paths = self._find_source_paths()
        print(f"🔍 [DEBUG] Found {len(src_paths)} source paths: {[str(p) for p in src_paths]}")

        # Core framework path
        core_path = Path(__file__).resolve().parent.parent
        print(f"🔍 [DEBUG] Core framework path: {core_path}")

        # Configuration for exclusions
        excluded_directories = list(self._config.excluded_dirs) + [
            "entity", "entities", "Entity",
            "migration", "migrations", "Migrations",
            "test", "tests", "Test", "Tests",
            "__pycache__", ".pytest_cache", ".mypy_cache",
            "node_modules", "venv", "env", ".env",
            "templates", "static", "assets", "docs", "documentation",
        ]

        excluded_modules = list(self._config.excluded_modules) + [
            "src.entity", "src.entities", "framefox.core.entity",
            "src.migration", "src.migrations", "src.test", "src.tests",
            "framefox.tests", "framefox.test",
        ]

        print(f"🔍 [DEBUG] Excluded directories: {excluded_directories}")

        # Scan core framework (sans prints pour focus sur src)
        initial_count = len(self._registry.get_all_definitions())
        self._scan_for_service_definitions(core_path, "framefox.core", excluded_directories, excluded_modules)
        after_core_count = len(self._registry.get_all_definitions())
        print(f"🔍 [DEBUG] Services after core scan: {after_core_count} (core added: {after_core_count - initial_count})")

        # Scan user source code avec focus détaillé
        for i, src_path in enumerate(src_paths):
            print(f"🔍 [SRC] ===== SCANNING SOURCE PATH {i+1}/{len(src_paths)} =====")
            print(f"🔍 [SRC] Path: {src_path}")
            print(f"🔍 [SRC] Exists: {src_path.exists()}")
            
            if src_path.exists():
                # Lister le contenu du dossier src
                try:
                    src_contents = list(src_path.iterdir())
                    print(f"🔍 [SRC] Directory contents ({len(src_contents)} items):")
                    for item in src_contents:
                        print(f"🔍 [SRC]   - {item.name} ({'DIR' if item.is_dir() else 'FILE'})")
                except Exception as e:
                    print(f"🔍 [SRC] Error listing directory contents: {e}")
                
                before_src = len(self._registry.get_all_definitions())
                print(f"🔍 [SRC] Services before src scan: {before_src}")
                
                self._scan_for_service_definitions(src_path, "src", excluded_directories, excluded_modules)
                
                after_src = len(self._registry.get_all_definitions())
                print(f"🔍 [SRC] Services after src scan: {after_src} (added: {after_src - before_src})")
            else:
                print(f"🔍 [SRC] ❌ Source path does not exist: {src_path}")

        final_count = len(self._registry.get_all_definitions())
        print(f"🔍 [DEBUG] Final service count: {final_count}")

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
        
        # Seulement afficher les détails pour src
        if base_package == "src":
            print(f"🔍 [SRC_SCAN] ===== DETAILED SRC SCAN =====")
            print(f"🔍 [SRC_SCAN] Scanning {base_package} at {base_path}")
            print(f"🔍 [SRC_SCAN] Excluded dirs: {excluded_dirs}")
            
            files_processed = 0
            dirs_excluded = 0
            files_skipped = 0
            modules_processed = 0
            services_found = 0
            
            for root, dirs, files in os.walk(base_path):
                root_path = Path(root)
                
                print(f"🔍 [SRC_SCAN] Checking directory: {root_path}")
                
                # Test exclusion avec debug
                should_exclude = self._should_exclude_directory(root_path, excluded_dirs)
                print(f"🔍 [SRC_SCAN] Should exclude '{root_path.name}': {should_exclude}")
                
                if should_exclude:
                    dirs_excluded += 1
                    print(f"🔍 [SRC_SCAN] ❌ EXCLUDED directory: {root_path}")
                    continue

                print(f"🔍 [SRC_SCAN] ✅ Processing directory: {root_path}")
                print(f"🔍 [SRC_SCAN] Files in directory: {files}")

                for file in files:
                    print(f"🔍 [SRC_SCAN] Checking file: {file}")
                    
                    if not self._should_process_file(file):
                        files_skipped += 1
                        print(f"🔍 [SRC_SCAN] ❌ Skipped file: {file}")
                        continue

                    files_processed += 1
                    print(f"🔍 [SRC_SCAN] ✅ Processing file: {file}")

                    try:
                        module_name = self._build_module_name(root_path / file, base_path, base_package)
                        print(f"🔍 [SRC_SCAN] Built module name: {module_name}")

                        if self._should_exclude_module(module_name, excluded_modules):
                            print(f"🔍 [SRC_SCAN] ❌ Excluded module: {module_name}")
                            continue

                        modules_processed += 1
                        services_before = len(self._registry.get_all_definitions())
                        
                        print(f"🔍 [SRC_SCAN] Processing module: {module_name}")
                        self._process_module(module_name)
                        
                        services_after = len(self._registry.get_all_definitions())
                        services_added = services_after - services_before
                        services_found += services_added
                        
                        if services_added > 0:
                            print(f"🔍 [SRC_SCAN] ✅ Found {services_added} service(s) in {module_name}")
                        else:
                            print(f"🔍 [SRC_SCAN] ⚠️ No services found in {module_name}")

                    except Exception as e:
                        print(f"🔍 [SRC_SCAN] ❌ Error processing file {root_path / file}: {e}")

            print(f"🔍 [SRC_SCAN] ===== SRC SCAN SUMMARY =====")
            print(f"🔍 [SRC_SCAN] - Directories excluded: {dirs_excluded}")
            print(f"🔍 [SRC_SCAN] - Files processed: {files_processed}")
            print(f"🔍 [SRC_SCAN] - Files skipped: {files_skipped}")
            print(f"🔍 [SRC_SCAN] - Modules processed: {modules_processed}")
            print(f"🔍 [SRC_SCAN] - Services found: {services_found}")
            
        else:
            # Scan normal pour framefox.core sans logs détaillés
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
            
            # Debug pour src uniquement
            if "src" in str(path):
                print(f"🔍 [EXCLUDE] Testing directory: {path}")
                print(f"🔍 [EXCLUDE] Directory name: '{dir_name}'")
                print(f"🔍 [EXCLUDE] Path parts: {path.parts}")
            
            # Exclusions TOUJOURS valides
            always_exclude = {
                "__pycache__", ".pytest_cache", ".mypy_cache",
                "node_modules", "venv", "env", ".env",
                "templates", "static", "assets", "docs", "documentation"
            }
            
            if dir_name in always_exclude:
                if "src" in str(path):
                    print(f"🔍 [EXCLUDE] ❌ Always excluded: {dir_name}")
                return True
            
            # Exclusions CONTEXTUELLES
            contextual_exclusions = {
                "test": ["src", "framefox"],
                "tests": ["src", "framefox"],
                "entity": ["src"],
                "entities": ["src"],
                "migration": ["src", "framefox"],
                "migrations": ["src", "framefox"],
            }
            
            if dir_name in contextual_exclusions:
                allowed_parents = contextual_exclusions[dir_name]
                path_parts = [part.lower() for part in path.parts]
                
                if "src" in str(path):
                    print(f"🔍 [EXCLUDE] Contextual check for '{dir_name}'")
                    print(f"🔍 [EXCLUDE] Allowed parents: {allowed_parents}")
                    print(f"🔍 [EXCLUDE] Path parts: {path_parts}")
                    print(f"🔍 [EXCLUDE] Has allowed parent: {any(parent in path_parts for parent in allowed_parents)}")
                
                if any(parent in path_parts for parent in allowed_parents):
                    if "src" in str(path):
                        print(f"🔍 [EXCLUDE] ❌ Contextually excluded: {dir_name}")
                    return True
            
            # Vérifier les exclusions configurées
            for excluded_dir in excluded_dirs:
                if dir_name == excluded_dir.lower():
                    if "src" in str(path):
                        print(f"🔍 [EXCLUDE] ❌ Configured exclusion: {dir_name}")
                    return True
            
            if "src" in str(path):
                print(f"🔍 [EXCLUDE] ✅ Directory allowed: {dir_name}")
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
        """Process a module and register service definitions."""
        
        # Debug détaillé seulement pour les modules src
        is_src_module = module_name.startswith("src.")
        
        if is_src_module:
            print(f"🔍 [SRC_MODULE] ===== PROCESSING MODULE =====")
            print(f"🔍 [SRC_MODULE] Module: {module_name}")
        
        try:
            module = importlib.import_module(module_name)
            if is_src_module:
                print(f"🔍 [SRC_MODULE] ✅ Successfully imported: {module_name}")
            
            attrs_found = 0
            classes_found = 0
            services_registered = 0
            
            for attr_name in dir(module):
                attrs_found += 1
                try:
                    attr = getattr(module, attr_name)

                    if inspect.isclass(attr):
                        classes_found += 1
                        if is_src_module:
                            print(f"🔍 [SRC_MODULE] Found class: {attr_name}")
                            print(f"🔍 [SRC_MODULE] Class module: {attr.__module__}")
                            print(f"🔍 [SRC_MODULE] Is same module: {attr.__module__ == module_name}")
                        
                        if attr.__module__ == module_name:  # Classe définie dans ce module
                            can_be_service = self._can_be_service(attr)
                            if is_src_module:
                                print(f"🔍 [SRC_MODULE] Can be service: {can_be_service}")
                            
                            if can_be_service:
                                services_registered += 1
                                self._create_and_register_definition(attr)
                                if is_src_module:
                                    print(f"🔍 [SRC_MODULE] ✅ Registered service: {attr_name}")
                            else:
                                if is_src_module:
                                    print(f"🔍 [SRC_MODULE] ❌ Cannot be service: {attr_name}")

                except Exception as e:
                    if "access" not in str(e).lower() and is_src_module:
                        print(f"🔍 [SRC_MODULE] Error inspecting {attr_name}: {e}")

            if is_src_module:
                print(f"🔍 [SRC_MODULE] Module summary:")
                print(f"🔍 [SRC_MODULE] - Total attributes: {attrs_found}")
                print(f"🔍 [SRC_MODULE] - Classes found: {classes_found}")
                print(f"🔍 [SRC_MODULE] - Services registered: {services_registered}")

        except (ModuleNotFoundError, ImportError) as e:
            if is_src_module:
                print(f"🔍 [SRC_MODULE] ❌ Failed to import {module_name}: {e}")
            debug_modules = ["icecream", "devtools", "pytest", "IPython"]
            if not any(debug_module in str(e) for debug_module in debug_modules):
                pass  # Log silencieux pour éviter le spam

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

        # Vérifier le module
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
        """Retrieve or create an instance of the requested service."""
        # Check cache first
        if service_class in self._resolution_cache:
            return self._resolution_cache[service_class]

        # Check existing instances
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

        # Check for circular dependencies
        if service_class in self._circular_detection:
            chain = list(self._circular_detection)
            raise CircularDependencyError(service_class, chain)

        # ✅ UTILISER _find_or_create_definition comme dans l'ancien code
        definition = self._find_or_create_definition(service_class)
        if not definition:
            # List of known external classes to silently ignore
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
