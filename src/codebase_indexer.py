import os
import ast
import json
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class ModuleInfo:
    path: str
    name: str
    imports: List[str]
    exports: List[str]
    classes: List[str]
    functions: List[str]
    size: int
    dependencies: Set[str]

class CodebaseIndexer:
    def __init__(self):
        self.modules: Dict[str, ModuleInfo] = {}
        self.import_graph: Dict[str, Set[str]] = {}
        self.component_map: Dict[str, str] = {}  # component_name -> file_path
        
    def index_codebase(self, root_path: str) -> Dict:

        self.root_path = Path(root_path).resolve()
        
        # First pass: collect all modules
        for file_path in self._get_all_source_files(root_path):
            self._index_file(file_path)
            
        # Second pass: resolve dependencies
        self._build_dependency_graph()
        
        # Third pass: identify key architectural components
        architecture = self._check_architecture()
        
        return {
            'modules': {k: asdict(v) for k, v in self.modules.items()},
            'import_graph': {k: list(v) for k, v in self.import_graph.items()},
            'architecture': architecture,
            'stats': self._compute_stats()
        }
    
    def _get_all_source_files(self, root_path: str) -> List[str]:

        files = []
        extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}
        
        for root, _, filenames in os.walk(root_path):
            # Skip common non-source directories
            if any(skip in root for skip in ['node_modules', '.git', '__pycache__', 'dist', 'build']):
                continue
                
            for filename in filenames:
                if any(filename.endswith(ext) for ext in extensions):
                    files.append(os.path.join(root, filename))
                    
        return files
    
    def _index_file(self, file_path: str) -> None:

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            rel_path = os.path.relpath(file_path, self.root_path)
            module_name = self._path_to_module_name(rel_path)
            
            if file_path.endswith('.py'):
                info = self._index_python_file(content, rel_path)
            else:
                info = self._index_js_ts_file(content, rel_path)
                
            self.modules[module_name] = info
            
            # Map components/classes to files
            for cls in info.classes:
                self.component_map[cls] = rel_path
            for func in info.functions:
                if func.startswith(func[0].upper()):  # Likely a React component
                    self.component_map[func] = rel_path
                    
        except Exception as e:
            print(f"Error indexing {file_path}: {e}")
    
    def _index_python_file(self, content: str, rel_path: str) -> ModuleInfo:

        imports = []
        exports = []
        classes = []
        functions = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    exports.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                    if not node.name.startswith('_'):
                        exports.append(node.name)
                        
        except:
            pass  # Fallback to regex if AST fails
            
        return ModuleInfo(
            path=rel_path,
            name=self._path_to_module_name(rel_path),
            imports=imports,
            exports=exports,
            classes=classes,
            functions=functions,
            size=len(content.splitlines()),
            dependencies=set()
        )
    
    def _index_js_ts_file(self, content: str, rel_path: str) -> ModuleInfo:

        import re
# TODO: revisit this later
        import_pattern = r'import\s+(?:{[^}]+}|[\w\s,]+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        imports = re.findall(import_pattern, content)
# FIXME: refactor when time permits
        export_pattern = r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)'
        exports = re.findall(export_pattern, content)
# Works, but could be neater
        class_pattern = r'(?:export\s+)?(?:default\s+)?class\s+(\w+)'
        classes = re.findall(class_pattern, content)
# Might need cleanup
        func_pattern = r'(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)'
        arrow_pattern = r'(?:export\s+)?const\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=]+)\s*=>'
        
        functions = re.findall(func_pattern, content) + re.findall(arrow_pattern, content)
        
        return ModuleInfo(
            path=rel_path,
            name=self._path_to_module_name(rel_path),
            imports=imports,
            exports=exports,
            classes=classes,
            functions=functions,
            size=len(content.splitlines()),
            dependencies=set()
        )
    
    def _path_to_module_name(self, path: str) -> str:

        return path.replace(os.sep, '.').rsplit('.', 1)[0]
    
    def _build_dependency_graph(self) -> None:

        for module_name, info in self.modules.items():
            deps = set()
            
            for imp in info.imports:
                # Resolve relative imports
                if imp.startswith('.'):
                    base_parts = module_name.split('.')
                    if imp.startswith('..'):
                        levels = len(imp) - len(imp.lstrip('.'))
                        base_parts = base_parts[:-levels]
                        imp_name = imp[levels:]
                    else:
                        base_parts = base_parts[:-1]
                        imp_name = imp[1:]
                    
                    if imp_name:
                        resolved = '.'.join(base_parts + [imp_name])
                    else:
                        resolved = '.'.join(base_parts)
                else:
                    resolved = imp
# Not the cleanest, but it does the job
                if resolved in self.modules or any(resolved.startswith(m) for m in self.modules):
                    deps.add(resolved)
                    
            info.dependencies = deps
            self.import_graph[module_name] = deps
    
    def _check_architecture(self) -> Dict:

        # Find entry points
        entry_points = []
        for name, info in self.modules.items():
            if 'main' in name or 'index' in name or 'app' in name.lower():
                entry_points.append(name)
                
        # Find core modules (imported by many others)
        import_counts = {}
        for deps in self.import_graph.values():
            for dep in deps:
                import_counts[dep] = import_counts.get(dep, 0) + 1
                
        core_modules = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]
# Works, but could be neater
        layers = self._detect_layers()
        
        return {
            'entry_points': entry_points,
            'core_modules': [m[0] for m in core_modules],
            'layers': layers,
            'module_families': self._group_modules_by_family()
        }
    
    def _detect_layers(self) -> Dict[str, List[str]]:

        layers = {
            'presentation': [],
            'business': [],
            'data': [],
            'infrastructure': [],
            'shared': []
        }
        
        patterns = {
            'presentation': ['component', 'view', 'page', 'ui', 'widget'],
            'business': ['service', 'controller', 'handler', 'manager', 'logic'],
            'data': ['model', 'entity', 'repository', 'dao', 'schema'],
            'infrastructure': ['config', 'util', 'helper', 'middleware', 'adapter'],
            'shared': ['common', 'shared', 'core', 'base']
        }
        
        for module_name in self.modules:
            module_lower = module_name.lower()
            assigned = False
            
            for layer, keywords in patterns.items():
                if any(kw in module_lower for kw in keywords):
                    layers[layer].append(module_name)
                    assigned = True
                    break
                    
            if not assigned:
                # Try to assign based on imports
                info = self.modules[module_name]
                if any('react' in imp.lower() for imp in info.imports):
                    layers['presentation'].append(module_name)
                    
        return layers
    
    def _group_modules_by_family(self) -> Dict[str, List[str]]:

        families = {}
        
        for module_name in self.modules:
            parts = module_name.split('.')
            if len(parts) > 1:
                family = parts[0]
            else:
                family = 'root'
                
            if family not in families:
                families[family] = []
            families[family].append(module_name)
            
        return families
    
    def _compute_stats(self) -> Dict:

        total_files = len(self.modules)
        total_lines = sum(m.size for m in self.modules.values())
        
        file_types = {}
        for info in self.modules.values():
            ext = Path(info.path).suffix
            file_types[ext] = file_types.get(ext, 0) + 1
            
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'file_types': file_types,
            'total_classes': sum(len(m.classes) for m in self.modules.values()),
            'total_functions': sum(len(m.functions) for m in self.modules.values())
        }