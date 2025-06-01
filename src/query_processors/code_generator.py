"""
Code generation module for CodeLve.
Handles pattern-based code generation from the codebase.
"""

import json
import re
from typing import Dict, List, Optional, Any
from collections import defaultdict


class CodeGenerator:
    """Handles code generation based on existing patterns."""
    
    def __init__(self, consolidated_code: str):
        self.consolidated_code = consolidated_code
        self.patterns = self._extract_patterns()
    
    def _extract_patterns(self) -> Dict[str, Any]:
        """Extract common patterns from the codebase."""
        patterns = {
            'imports': defaultdict(set),
            'class_structures': defaultdict(list),
            'function_patterns': defaultdict(list),
            'naming_conventions': self._analyze_naming_conventions(),
            'code_style': self._analyze_code_style()
        }
        
        # Extract imports
        import_pattern = r'^(from\s+[\w.]+\s+import\s+[\w,\s]+|import\s+[\w.]+)'
        for match in re.finditer(import_pattern, self.consolidated_code, re.MULTILINE):
            import_stmt = match.group(0)
            if 'from' in import_stmt:
                module = import_stmt.split('from')[1].split('import')[0].strip()
                patterns['imports'][module].add(import_stmt)
            else:
                module = import_stmt.split('import')[1].strip().split('.')[0]
                patterns['imports'][module].add(import_stmt)
        
        # Extract class structures
        class_pattern = r'class\s+(\w+).*?(?=class\s+\w+|def\s+\w+|$)'
        for match in re.finditer(class_pattern, self.consolidated_code, re.DOTALL):
            class_name = match.group(1)
            class_body = match.group(0)
            patterns['class_structures'][self._get_class_type(class_name)].append({
                'name': class_name,
                'methods': self._extract_methods(class_body),
                'decorators': self._extract_decorators(class_body)
            })
        
        return patterns
    
    def _analyze_naming_conventions(self) -> Dict[str, str]:
        """Analyze naming conventions used in the codebase."""
        conventions = {
            'functions': 'snake_case',
            'classes': 'PascalCase',
            'constants': 'UPPER_SNAKE_CASE',
            'private_methods': '_snake_case'
        }
        
        # Check for actual conventions in code
        if re.search(r'def\s+[a-z]+[A-Z]', self.consolidated_code):
            conventions['functions'] = 'camelCase'
        
        return conventions
    
    def _analyze_code_style(self) -> Dict[str, Any]:
        """Analyze code style preferences."""
        style = {
            'quotes': 'single' if self.consolidated_code.count("'") > self.consolidated_code.count('"') else 'double',
            'indentation': 4,  # Default Python
            'line_length': 88,  # Black default
            'docstring_style': 'google'  # Default assumption
        }
        
        # Check for docstring style
        if '"""' in self.consolidated_code:
            if re.search(r'""".*?:param', self.consolidated_code, re.DOTALL):
                style['docstring_style'] = 'sphinx'
            elif re.search(r'""".*?Args:', self.consolidated_code, re.DOTALL):
                style['docstring_style'] = 'google'
        
        return style
    
    def _get_class_type(self, class_name: str) -> str:
        """Determine the type of class based on name."""
        if class_name.endswith('Model'):
            return 'model'
        elif class_name.endswith('View'):
            return 'view'
        elif class_name.endswith('Controller'):
            return 'controller'
        elif class_name.endswith('Service'):
            return 'service'
        elif class_name.endswith('Handler'):
            return 'handler'
        elif class_name.endswith('Manager'):
            return 'manager'
        elif class_name.endswith('Error') or class_name.endswith('Exception'):
            return 'exception'
        else:
            return 'generic'
    
    def _extract_methods(self, class_body: str) -> List[str]:
        """Extract method names from a class body."""
        methods = []
        method_pattern = r'def\s+(\w+)\s*\('
        for match in re.finditer(method_pattern, class_body):
            methods.append(match.group(1))
        return methods
    
    def _extract_decorators(self, class_body: str) -> List[str]:
        """Extract decorators from a class body."""
        decorators = []
        decorator_pattern = r'@(\w+)'
        for match in re.finditer(decorator_pattern, class_body):
            decorators.append(match.group(1))
        return list(set(decorators))
    
    def generate_code(self, component_type: str, component_name: str, 
                     specifications: Optional[Dict] = None) -> str:
        """Generate code based on existing patterns."""
        if component_type == 'react_component':
            return self._generate_react_component(component_name, specifications)
        elif component_type == 'python_class':
            return self._generate_python_class(component_name, specifications)
        elif component_type == 'api_endpoint':
            return self._generate_api_endpoint(component_name, specifications)
        elif component_type == 'test':
            return self._generate_test(component_name, specifications)
        else:
            return self._generate_generic_code(component_type, component_name, specifications)
    
    def _generate_react_component(self, name: str, specs: Optional[Dict] = None) -> str:
        """Generate a React component based on existing patterns."""
        # Look for existing React components
        react_pattern = r'(function|const)\s+\w+\s*=.*?return\s*\('
        has_react = bool(re.search(react_pattern, self.consolidated_code))
        
        if has_react:
            # Find similar components
            similar = self._find_similar_react_components(name)
            if similar:
                return self._adapt_react_component(similar[0], name, specs)
        
        # Default React component
        return self._default_react_component(name, specs)
    
    def _generate_python_class(self, name: str, specs: Optional[Dict] = None) -> str:
        """Generate a Python class based on existing patterns."""
        class_type = self._get_class_type(name)
        similar_classes = self.patterns['class_structures'].get(class_type, [])
        
        if similar_classes:
            # Use the most recent similar class as template
            template = similar_classes[-1]
            return self._adapt_python_class(template, name, specs)
        
        # Default Python class
        return self._default_python_class(name, specs)
    
    def _generate_api_endpoint(self, name: str, specs: Optional[Dict] = None) -> str:
        """Generate an API endpoint based on existing patterns."""
        # Look for Flask/FastAPI patterns
        flask_pattern = r'@app\.route\(.*?\)\s*def\s+\w+\(.*?\):'
        fastapi_pattern = r'@(app|router)\.(get|post|put|delete)\(.*?\)\s*async\s+def\s+\w+\(.*?\):'
        
        is_flask = bool(re.search(flask_pattern, self.consolidated_code))
        is_fastapi = bool(re.search(fastapi_pattern, self.consolidated_code))
        
        if is_fastapi:
            return self._generate_fastapi_endpoint(name, specs)
        elif is_flask:
            return self._generate_flask_endpoint(name, specs)
        else:
            return self._default_api_endpoint(name, specs)
    
    def _generate_test(self, name: str, specs: Optional[Dict] = None) -> str:
        """Generate a test based on existing patterns."""
        # Look for test patterns
        pytest_pattern = r'def\s+test_\w+\(.*?\):'
        unittest_pattern = r'class\s+Test\w+\(.*?TestCase.*?\):'
        
        uses_pytest = bool(re.search(pytest_pattern, self.consolidated_code))
        uses_unittest = bool(re.search(unittest_pattern, self.consolidated_code))
        
        if uses_pytest:
            return self._generate_pytest(name, specs)
        elif uses_unittest:
            return self._generate_unittest(name, specs)
        else:
            return self._default_test(name, specs)
    
    def _find_similar_react_components(self, name: str) -> List[str]:
        """Find similar React components in the codebase."""
        components = []
        # Implementation would search for similar component patterns
        return components
    
    def _adapt_react_component(self, template: str, name: str, specs: Optional[Dict]) -> str:
        """Adapt an existing React component as a template."""
        # Implementation would modify the template
        return self._default_react_component(name, specs)
    
    def _adapt_python_class(self, template: Dict, name: str, specs: Optional[Dict]) -> str:
        """Adapt an existing Python class as a template."""
        methods = specs.get('methods', []) if specs else []
        base_class = specs.get('base_class', '') if specs else ''
        
        code = f"class {name}"
        if base_class:
            code += f"({base_class})"
        code += ":\n"
        
        # Add docstring
        code += f'    """{name} implementation based on existing patterns."""\n\n'
        
        # Add __init__ if in template
        if '__init__' in template['methods']:
            code += "    def __init__(self):\n"
            code += "        super().__init__()\n\n"
        
        # Add requested methods
        for method in methods:
            code += f"    def {method}(self):\n"
            code += f'        """Implementation for {method}."""\n'
            code += "        pass\n\n"
        
        return code
    
    def _default_react_component(self, name: str, specs: Optional[Dict]) -> str:
        """Generate a default React component."""
        props = specs.get('props', []) if specs else []
        state = specs.get('state', []) if specs else []
        
        code = f"import React, {{ useState, useEffect }} from 'react';\n\n"
        code += f"const {name} = ({{ {', '.join(props)} }}) => {{\n"
        
        # Add state
        for s in state:
            code += f"  const [{s}, set{s.capitalize()}] = useState(null);\n"
        
        code += "\n  return (\n    <div>\n"
        code += f"      <h2>{name}</h2>\n"
        code += "      {/* Component content */}\n"
        code += "    </div>\n  );\n};\n\n"
        code += f"export default {name};"
        
        return code
    
    def _default_python_class(self, name: str, specs: Optional[Dict]) -> str:
        """Generate a default Python class."""
        code = f"class {name}:\n"
        code += f'    """Default implementation for {name}."""\n\n'
        code += "    def __init__(self):\n"
        code += "        pass\n"
        
        return code
    
    def _generate_fastapi_endpoint(self, name: str, specs: Optional[Dict]) -> str:
        """Generate a FastAPI endpoint."""
        method = specs.get('method', 'get').lower() if specs else 'get'
        path = specs.get('path', f'/{name.lower()}') if specs else f'/{name.lower()}'
        
        code = f"@router.{method}('{path}')\n"
        code += f"async def {name}("
        
        if method in ['post', 'put']:
            code += "data: dict"
        
        code += "):\n"
        code += f'    """Handle {method.upper()} {path}."""\n'
        code += "    return {'status': 'success'}\n"
        
        return code
    
    def _generate_flask_endpoint(self, name: str, specs: Optional[Dict]) -> str:
        """Generate a Flask endpoint."""
        method = specs.get('method', 'GET').upper() if specs else 'GET'
        path = specs.get('path', f'/{name.lower()}') if specs else f'/{name.lower()}'
        
        code = f"@app.route('{path}', methods=['{method}'])\n"
        code += f"def {name}():\n"
        code += f'    """Handle {method} {path}."""\n'
        code += "    return jsonify({'status': 'success'})\n"
        
        return code
    
    def _default_api_endpoint(self, name: str, specs: Optional[Dict]) -> str:
        """Generate a generic API endpoint."""
        return self._generate_flask_endpoint(name, specs)
    
    def _generate_pytest(self, name: str, specs: Optional[Dict]) -> str:
        """Generate a pytest test."""
        function_to_test = specs.get('function', name) if specs else name
        
        code = f"def test_{name}():\n"
        code += f'    """Test for {function_to_test}."""\n'
        code += "    # Arrange\n"
        code += "    expected = None\n\n"
        code += "    # Act\n"
        code += f"    result = {function_to_test}()\n\n"
        code += "    # Assert\n"
        code += "    assert result == expected\n"
        
        return code
    
    def _generate_unittest(self, name: str, specs: Optional[Dict]) -> str:
        """Generate a unittest test."""
        class_name = f"Test{name.capitalize()}"
        
        code = f"class {class_name}(unittest.TestCase):\n"
        code += f'    """Test cases for {name}."""\n\n'
        code += f"    def test_{name}(self):\n"
        code += f'        """Test {name} functionality."""\n'
        code += "        self.assertEqual(True, True)\n"
        
        return code
    
    def _default_test(self, name: str, specs: Optional[Dict]) -> str:
        """Generate a default test."""
        return self._generate_pytest(name, specs)
    
    def _generate_generic_code(self, component_type: str, name: str, 
                              specs: Optional[Dict]) -> str:
        """Generate generic code for unrecognized types."""
        code = f"# Generated {component_type}: {name}\n"
        code += f"# Specifications: {json.dumps(specs, indent=2) if specs else 'None'}\n\n"
        code += "# TODO: Implement based on project patterns\n"
        
        return code