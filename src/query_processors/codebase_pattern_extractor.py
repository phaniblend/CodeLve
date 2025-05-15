"""
Codebase Pattern Extractor for Context-Aware Code Generation
Learns patterns from the loaded codebase to generate consistent code
"""

import re
from typing import Dict, List, Set, Any
from collections import defaultdict
from pathlib import Path


class CodebasePatternExtractor:

    
    def __init__(self, consolidated_code: str):
    # TODO: revisit this later
        self.consolidated_code = consolidated_code
        self.patterns = {
            'component_patterns': {},
            'import_patterns': {},
            'state_patterns': {},
            'styling_patterns': {},
            'api_patterns': {},
            'test_patterns': {},
            'file_structure': {}
        }
        self._get_all_patterns()
    
    def _get_all_patterns(self):

        self._get_component_patterns()
        self._get_import_patterns()
        self._get_state_management_patterns()
        self._get_styling_patterns()
        self._get_api_patterns()
        self._get_test_patterns()
        self._check_file_structure()
    
    def _get_component_patterns(self):

        # React Function Component Pattern
        react_fc_pattern = r'(?:export\s+)?(?:const|function)\s+(\w+)(?::\s*React\.FC.*?)?\s*=\s*\([^)]*\)\s*(?:=>\s*)?{\s*\n((?:.*\n)*?)^}'
# Might need cleanup
        components = []
        for match in re.finditer(react_fc_pattern, self.consolidated_code, re.MULTILINE):
            component_name = match.group(1)
            component_body = match.group(2)
            
            components.append({
                'name': component_name,
                'body': component_body,
                'hooks': self._get_hooks(component_body),
                'props': self._get_props(component_body),
                'imports': self._get_component_imports(component_body)
            })
        
        # Analyze patterns
        if components:
            self.patterns['component_patterns'] = {
                'style': self._detect_component_style(components),
                'common_hooks': self._find_common_hooks(components),
                'prop_patterns': self._check_prop_patterns(components),
                'structure': self._check_component_structure(components)
            }
    
    def _get_hooks(self, component_body: str) -> List[str]:

        hook_pattern = r'(use\w+)\s*\('
        return list(set(re.findall(hook_pattern, component_body)))
    
    def _get_props(self, component_body: str) -> Dict[str, Any]:

        # TypeScript interface pattern
        interface_pattern = r'interface\s+\w*Props\s*{\s*((?:[^}])*)\s*}'
        match = re.search(interface_pattern, component_body)
        
        if match:
            props_content = match.group(1)
            props = {}
            prop_pattern = r'(\w+)\s*:\s*([^;,\n]+)'
            for prop_match in re.finditer(prop_pattern, props_content):
                props[prop_match.group(1)] = prop_match.group(2).strip()
            return props
        return {}
    
    def _get_component_imports(self, component_body: str) -> List[str]:

        import_pattern = r'^import\s+.*?;$'
        return re.findall(import_pattern, component_body, re.MULTILINE)
    
    def _detect_component_style(self, components: List[Dict]) -> str:

        functional_count = 0
        class_count = 0
        
        for comp in components:
            if '=>' in comp.get('body', ''):
                functional_count += 1
            else:
                class_count += 1
        
        return 'functional' if functional_count >= class_count else 'class'
    
    def _find_common_hooks(self, components: List[Dict]) -> List[str]:

        hook_counts = defaultdict(int)
        
        for comp in components:
            for hook in comp.get('hooks', []):
                hook_counts[hook] += 1
# Works, but could be neater
        threshold = len(components) * 0.3
        return [hook for hook, count in hook_counts.items() if count >= threshold]
    
    def _check_prop_patterns(self, components: List[Dict]) -> Dict:

        all_props = defaultdict(list)
        
        for comp in components:
            props = comp.get('props', {})
            for prop_name, prop_type in props.items():
                all_props[prop_name].append(prop_type)
        
        # Find common props
        common_props = {}
        for prop_name, types in all_props.items():
            if len(types) >= 2:  # Used in at least 2 components
                # Get most common type
                most_common_type = max(set(types), key=types.count)
                common_props[prop_name] = most_common_type
        
        return {'common': list(common_props.keys()), 'types': common_props}
    
    def _check_component_structure(self, components: List[Dict]) -> Dict:

        structure_patterns = {
            'uses_loading_state': 0,
            'uses_error_handling': 0,
            'uses_data_fetching': 0,
            'uses_form_handling': 0
        }
        
        for comp in components:
            body = comp.get('body', '')
            if 'loading' in body or 'isLoading' in body:
                structure_patterns['uses_loading_state'] += 1
            if 'error' in body or 'catch' in body:
                structure_patterns['uses_error_handling'] += 1
            if 'fetch' in body or 'axios' in body or 'api' in body.lower():
                structure_patterns['uses_data_fetching'] += 1
            if 'onSubmit' in body or 'handleSubmit' in body:
                structure_patterns['uses_form_handling'] += 1
        
        # Convert to percentages
        total = len(components) if components else 1
        for key in structure_patterns:
            structure_patterns[key] = (structure_patterns[key] / total) * 100
        
        return structure_patterns
    
    def _get_import_patterns(self):

        import_groups = defaultdict(list)
        
        # Find all imports
        import_pattern = r'^import\s+(?:{[^}]+}|[\w\s,]+)\s+from\s+[\'"]([^\'"]+)[\'"];?$'
        
        for match in re.finditer(import_pattern, self.consolidated_code, re.MULTILINE):
            import_path = match.group(1)
            full_import = match.group(0)
            
            # Categorize imports
            if import_path.startswith('.'):
                import_groups['local'].append(full_import)
            elif import_path.startswith('@'):
                import_groups['scoped'].append(full_import)
            elif any(pkg in import_path for pkg in ['react', 'vue', 'angular']):
                import_groups['framework'].append(full_import)
            else:
                import_groups['external'].append(full_import)
        
        self.patterns['import_patterns'] = {
            'groups': dict(import_groups),
            'order': self._detect_import_order(),
            'common_imports': self._find_common_imports(import_groups)
        }
    
    def _detect_import_order(self) -> List[str]:

        # Simple detection - can be enhanced
        return ['external', 'framework', 'scoped', 'local']
    
    def _find_common_imports(self, import_groups: Dict) -> List[str]:

        all_imports = []
        for group_imports in import_groups.values():
            all_imports.extend(group_imports)
        
        # Count occurrences
        import_counts = defaultdict(int)
        for imp in all_imports:
            # Normalize import
            normalized = re.sub(r'\s+', ' ', imp).strip()
            import_counts[normalized] += 1
# Works, but could be neater
        sorted_imports = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)
        return [imp[0] for imp in sorted_imports[:10]]
    
    def _get_state_management_patterns(self):

        patterns = {
            'redux': False,
            'context': False,
            'mobx': False,
            'zustand': False,
            'local_state': False
        }
# Not the cleanest, but it does the job
        if 'useSelector' in self.consolidated_code or 'useDispatch' in self.consolidated_code:
            patterns['redux'] = True
            patterns['redux_patterns'] = self._get_redux_patterns()
# Not the cleanest, but it does the job
        if 'useContext' in self.consolidated_code or 'createContext' in self.consolidated_code:
            patterns['context'] = True
            patterns['context_patterns'] = self._get_context_patterns()
# FIXME: refactor when time permits
        if 'useState' in self.consolidated_code:
            patterns['local_state'] = True
            patterns['state_patterns'] = self._get_state_patterns()
        
        self.patterns['state_patterns'] = patterns
    
    def _get_redux_patterns(self) -> Dict:

        return {
            'uses_toolkit': '@reduxjs/toolkit' in self.consolidated_code,
            'uses_thunk': 'redux-thunk' in self.consolidated_code,
            'uses_saga': 'redux-saga' in self.consolidated_code
        }
    
    def _get_context_patterns(self) -> Dict:

        context_pattern = r'const\s+(\w+Context)\s*=\s*(?:React\.)?createContext'
        contexts = re.findall(context_pattern, self.consolidated_code)
        
        return {
            'contexts': contexts,
            'count': len(contexts)
        }
    
    def _get_state_patterns(self) -> Dict:

        state_pattern = r'const\s*\[(\w+),\s*set\w+\]\s*=\s*useState'
        state_vars = re.findall(state_pattern, self.consolidated_code)
        
        # Categorize state variables
        categories = {
            'loading': [],
            'error': [],
            'data': [],
            'form': [],
            'ui': []
        }
        
        for var in state_vars:
            if 'loading' in var.lower() or 'fetching' in var.lower():
                categories['loading'].append(var)
            elif 'error' in var.lower():
                categories['error'].append(var)
            elif 'data' in var.lower() or 'items' in var.lower() or 'list' in var.lower():
                categories['data'].append(var)
            elif 'form' in var.lower() or 'input' in var.lower():
                categories['form'].append(var)
            else:
                categories['ui'].append(var)
        
        return categories
    
    def _get_styling_patterns(self):

        patterns = {
            'method': 'unknown',
            'libraries': []
        }
# Not the cleanest, but it does the job
        if 'styled-components' in self.consolidated_code or 'styled.' in self.consolidated_code:
            patterns['method'] = 'styled-components'
            patterns['libraries'].append('styled-components')
        elif 'styles.' in self.consolidated_code and '.module.' in self.consolidated_code:
            patterns['method'] = 'css-modules'
        elif 'className=' in self.consolidated_code and any(tw in self.consolidated_code for tw in ['tw-', 'tailwind']):
            patterns['method'] = 'tailwind'
            patterns['libraries'].append('tailwindcss')
        elif 'makeStyles' in self.consolidated_code or '@mui' in self.consolidated_code:
            patterns['method'] = 'material-ui'
            patterns['libraries'].append('@mui/material')
# FIXME: refactor when time permits
        patterns['className_patterns'] = self._get_className_patterns()
        
        self.patterns['styling_patterns'] = patterns
    
    def _get_className_patterns(self) -> List[str]:

        className_pattern = r'className=["\']([^"\']+)["\']'
        classNames = re.findall(className_pattern, self.consolidated_code)
        
        # Count occurrences
        className_counts = defaultdict(int)
        for cn in classNames:
            className_counts[cn] += 1
# Might need cleanup
        sorted_classes = sorted(className_counts.items(), key=lambda x: x[1], reverse=True)
        return [cls[0] for cls in sorted_classes[:20]]
    
    def _get_api_patterns(self):

        patterns = {
            'method': 'unknown',
            'libraries': [],
            'patterns': []
        }
# Might need cleanup
        if 'axios' in self.consolidated_code:
            patterns['method'] = 'axios'
            patterns['libraries'].append('axios')
            patterns['patterns'] = self._get_axios_patterns()
# Not the cleanest, but it does the job
        elif 'fetch(' in self.consolidated_code:
            patterns['method'] = 'fetch'
            patterns['patterns'] = self._get_fetch_patterns()
# FIXME: refactor when time permits
        patterns['service_patterns'] = self._get_service_patterns()
        
        self.patterns['api_patterns'] = patterns
    
    def _get_axios_patterns(self) -> Dict:

        patterns = {
            'uses_interceptors': 'interceptors' in self.consolidated_code,
            'uses_instance': 'axios.create' in self.consolidated_code,
            'common_configs': []
        }
# Not the cleanest, but it does the job
        config_pattern = r'axios\.create\(\{([^}]+)\}'
        configs = re.findall(config_pattern, self.consolidated_code, re.DOTALL)
        
        for config in configs:
            if 'baseURL' in config:
                patterns['common_configs'].append('baseURL')
            if 'timeout' in config:
                patterns['common_configs'].append('timeout')
            if 'headers' in config:
                patterns['common_configs'].append('headers')
        
        return patterns
    
    def _get_fetch_patterns(self) -> Dict:

        patterns = {
            'uses_async_await': 'async' in self.consolidated_code and 'await fetch' in self.consolidated_code,
            'uses_then_catch': '.then(' in self.consolidated_code and 'fetch(' in self.consolidated_code,
            'common_options': []
        }
# FIXME: refactor when time permits
        fetch_pattern = r'fetch\([^,]+,\s*\{([^}]+)\}'
        options = re.findall(fetch_pattern, self.consolidated_code, re.DOTALL)
        
        for option in options:
            if 'method:' in option:
                patterns['common_options'].append('method')
            if 'headers:' in option:
                patterns['common_options'].append('headers')
            if 'body:' in option:
                patterns['common_options'].append('body')
        
        return patterns
    
    def _get_service_patterns(self) -> List[str]:

        service_pattern = r'class\s+(\w*Service)\s*{'
        services = re.findall(service_pattern, self.consolidated_code)
        
        return services
    
    def _get_test_patterns(self):

        patterns = {
            'framework': 'unknown',
            'patterns': []
        }
# Might need cleanup
        if 'describe(' in self.consolidated_code and 'it(' in self.consolidated_code:
            patterns['framework'] = 'jest'
        elif 'test(' in self.consolidated_code:
            patterns['framework'] = 'jest'
        elif '@testing-library' in self.consolidated_code:
            patterns['framework'] = 'react-testing-library'
# Not the cleanest, but it does the job
        patterns['structure'] = self._get_test_structure()
        
        self.patterns['test_patterns'] = patterns
    
    def _get_test_structure(self) -> Dict:

        structure = {
            'uses_describe_blocks': 'describe(' in self.consolidated_code,
            'uses_beforeEach': 'beforeEach(' in self.consolidated_code,
            'uses_afterEach': 'afterEach(' in self.consolidated_code,
            'uses_mocks': 'jest.mock' in self.consolidated_code or 'mock' in self.consolidated_code
        }
        
        return structure
    
    def _check_file_structure(self):

        file_pattern = r'#\s*File:\s*([^\n]+)'
        files = re.findall(file_pattern, self.consolidated_code)
        
        structure = {
            'total_files': len(files),
            'file_types': defaultdict(int),
            'folder_structure': defaultdict(list)
        }
        
        for file_path in files:
# Not the cleanest, but it does the job
            if '.' in file_path:
                ext = file_path.split('.')[-1]
                structure['file_types'][ext] += 1
# FIXME: refactor when time permits
            parts = file_path.split('/')
            if len(parts) > 1:
                folder = '/'.join(parts[:-1])
                structure['folder_structure'][folder].append(parts[-1])
        
        self.patterns['file_structure'] = dict(structure)
    
    def get_component_template(self, component_type: str = 'default') -> str:

        # This will be used by the code generator
        return self._build_component_template(component_type)
    
    def get_import_template(self, imports_needed: List[Dict]) -> str:

        return self._build_import_template(imports_needed)
    
    def _build_component_template(self, component_type: str) -> str:

        # This is a simplified version - can be enhanced
        style = self.patterns['component_patterns'].get('style', 'functional')
        
        if style == 'functional':
            template = "const {name} = () => {\n"
            template += "  // Component logic\n"
            template += "  return (\n"
            template += "    <div>\n"
            template += "      {/* Component content */}\n"
            template += "    </div>\n"
            template += "  );\n"
            template += "};"
        else:
            template = "class {name} extends React.Component {\n"
            template += "  render() {\n"
            template += "    return (\n"
            template += "      <div>\n"
            template += "        {/* Component content */}\n"
            template += "      </div>\n"
            template += "    );\n"
            template += "  }\n"
            template += "}"
        
        return template
    
    def _build_import_template(self, imports_needed: List[Dict]) -> str:

        import_lines = []
        
        # Group imports by type
        external_imports = []
        framework_imports = []
        scoped_imports = []
        local_imports = []
        
        for imp in imports_needed:
            module = imp.get('module', '')
            imports = imp.get('imports', [])
            is_default = imp.get('default', False)
            
            if is_default:
                import_line = f"import {imports[0]} from '{module}';"
            else:
                import_line = f"import {{ {', '.join(imports)} }} from '{module}';"
            
            # Categorize
            if module.startswith('.'):
                local_imports.append(import_line)
            elif module.startswith('@'):
                scoped_imports.append(import_line)
            elif any(pkg in module for pkg in ['react', 'vue', 'angular']):
                framework_imports.append(import_line)
            else:
                external_imports.append(import_line)
        
        # Combine in order
        order = self.patterns['import_patterns'].get('order', ['external', 'framework', 'scoped', 'local'])
        
        for group_name in order:
            if group_name == 'external' and external_imports:
                import_lines.extend(external_imports)
                import_lines.append('')  # Empty line between groups
            elif group_name == 'framework' and framework_imports:
                import_lines.extend(framework_imports)
                import_lines.append('')
            elif group_name == 'scoped' and scoped_imports:
                import_lines.extend(scoped_imports)
                import_lines.append('')
            elif group_name == 'local' and local_imports:
                import_lines.extend(local_imports)
        
        # Remove trailing empty line
        if import_lines and import_lines[-1] == '':
            import_lines.pop()
        
        return '\n'.join(import_lines)