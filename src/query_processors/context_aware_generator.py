"""
Context-Aware Code Generator
Generates code that matches the patterns of the loaded codebase
"""

from typing import Dict, List, Optional, Any, Tuple
import re
import json
from pathlib import Path
from query_processors.codebase_pattern_extractor import CodebasePatternExtractor


class ContextAwareGenerator:
    """Generate code that perfectly fits the existing codebase patterns"""
    
    def __init__(self, consolidated_code: str):
        self.pattern_extractor = CodebasePatternExtractor(consolidated_code)
        self.patterns = self.pattern_extractor.patterns
        self.consolidated_code = consolidated_code
    
    def generate_component(self, name: str, specs: Optional[Dict] = None) -> str:
        """Generate a component that matches existing patterns"""
        
        # Determine component style from patterns
        component_style = self.patterns['component_patterns'].get('style', 'functional')
        common_hooks = self.patterns['component_patterns'].get('common_hooks', [])
        prop_patterns = self.patterns['component_patterns'].get('prop_patterns', {})
        
        # Get styling method
        styling_method = self.patterns['styling_patterns'].get('method', 'css')
        
        # Get state management
        state_mgmt = self.patterns['state_patterns']
        
        # Build component based on detected patterns
        if component_style == 'functional':
            return self._generate_functional_component(
                name, specs, common_hooks, prop_patterns, styling_method, state_mgmt
            )
        else:
            return self._generate_class_component(
                name, specs, prop_patterns, styling_method, state_mgmt
            )
    
    def generate_service(self, name: str, specs: Optional[Dict] = None) -> str:
        """Generate a service matching existing service patterns"""
        
        # Find existing service patterns
        service_patterns = self._analyze_service_patterns()
        
        # Get API patterns
        api_patterns = self.patterns['api_patterns']
        
        # Generate service
        return self._generate_service_class(name, specs, service_patterns, api_patterns)
    
    def generate_api_endpoint(self, name: str, specs: Optional[Dict] = None) -> str:
        """Generate API endpoint matching existing patterns"""
        
        # Analyze existing endpoints
        endpoint_patterns = self._analyze_endpoint_patterns()
        
        # Get framework (Express, FastAPI, etc.)
        framework = self._detect_api_framework()
        
        return self._generate_api_endpoint_code(name, specs, endpoint_patterns, framework)
    
    def generate_test(self, name: str, target: str, specs: Optional[Dict] = None) -> str:
        """Generate test matching existing test patterns"""
        
        test_patterns = self.patterns['test_patterns']
        framework = test_patterns.get('framework', 'jest')
        
        return self._generate_test_code(name, target, specs, test_patterns, framework)
    
    def generate_model(self, name: str, specs: Optional[Dict] = None) -> str:
        """Generate model/interface matching existing patterns"""
        
        model_patterns = self._analyze_model_patterns()
        
        return self._generate_model_code(name, specs, model_patterns)
    
    def _generate_functional_component(self, name, specs, hooks, prop_patterns, styling, state_mgmt):
        """Generate functional component matching project patterns"""
        
        # Get import template
        imports_needed = self._determine_needed_imports(specs, hooks, styling, state_mgmt)
        import_section = self.pattern_extractor.get_import_template(imports_needed)
        
        # Determine props interface based on patterns
        props_interface = self._generate_props_interface(name, specs, prop_patterns)
        
        # Component structure based on project patterns
        component_structure = self.patterns['component_patterns'].get('structure', {})
        
        # Generate component
        code = f"{import_section}\n\n"
        
        if props_interface:
            code += f"{props_interface}\n\n"
        
        # Component definition matching project style
        if 'React.FC' in str(self.patterns):
            code += f"const {name}: React.FC<{name}Props> = ({{ "
        else:
            code += f"const {name} = ({{ "
        
        # Add props based on specs and patterns
        if specs and 'props' in specs:
            code += ", ".join(specs['props'])
        code += " }) => {\n"
        
        # Add common hooks from project
        code += self._add_common_hooks(hooks, specs)
        
        # Add custom hooks if detected in patterns
        code += self._add_custom_hooks(name, specs)
        
        # Add event handlers based on patterns
        code += self._add_event_handlers(name, specs)
        
        # Add API calls if needed
        if specs and specs.get('hasApiCalls'):
            code += self._add_api_calls(name, specs)
        
        # Add styling based on project patterns
        code += self._add_styling_setup(styling)
        
        # Return statement matching project patterns
        code += "\n  return (\n"
        code += self._generate_jsx_template(name, styling, specs)
        code += "  );\n"
        code += "};\n\n"
        code += f"export default {name};"
        
        return code
    
    def _generate_class_component(self, name, specs, prop_patterns, styling, state_mgmt):
        """Generate class component matching project patterns"""
        
        imports_needed = self._determine_needed_imports(specs, [], styling, state_mgmt)
        import_section = self.pattern_extractor.get_import_template(imports_needed)
        
        props_interface = self._generate_props_interface(name, specs, prop_patterns)
        state_interface = self._generate_state_interface(name, specs)
        
        code = f"{import_section}\n\n"
        
        if props_interface:
            code += f"{props_interface}\n\n"
        
        if state_interface:
            code += f"{state_interface}\n\n"
        
        code += f"class {name} extends React.Component<{name}Props, {name}State> {{\n"
        code += f"  constructor(props: {name}Props) {{\n"
        code += "    super(props);\n"
        code += "    this.state = {\n"
        code += "      // Initial state\n"
        code += "    };\n"
        code += "  }\n\n"
        
        # Add lifecycle methods based on patterns
        code += self._add_lifecycle_methods(specs)
        
        # Add methods
        code += self._add_class_methods(name, specs)
        
        code += "  render() {\n"
        code += "    return (\n"
        code += self._generate_jsx_template(name, styling, specs)
        code += "    );\n"
        code += "  }\n"
        code += "}\n\n"
        code += f"export default {name};"
        
        return code
    
    def _generate_service_class(self, name, specs, service_patterns, api_patterns):
        """Generate service class based on existing patterns"""
        
        # Detect if using TypeScript
        is_typescript = '.ts' in str(self.patterns) or 'interface' in self.consolidated_code
        
        # Get common service imports
        imports = self._get_service_imports(api_patterns)
        
        code = f"{imports}\n\n"
        
        # Add class definition
        if is_typescript:
            code += f"class {name}Service {{\n"
        else:
            code += f"class {name}Service {{\n"
        
        # Add constructor if needed
        if api_patterns.get('method') == 'axios':
            code += "  private apiClient = axiosInstance;\n\n"
        
        # Add common methods based on patterns
        if specs and specs.get('methods'):
            for method in specs['methods']:
                code += self._generate_service_method(method, api_patterns)
        else:
            # Add default CRUD methods
            code += self._generate_crud_methods(name, api_patterns)
        
        code += "}\n\n"
        code += f"export default new {name}Service();"
        
        return code
    
    def _generate_api_endpoint_code(self, name, specs, endpoint_patterns, framework):
        """Generate API endpoint based on framework"""
        
        if framework == 'express':
            return self._generate_express_endpoint(name, specs, endpoint_patterns)
        elif framework == 'fastapi':
            return self._generate_fastapi_endpoint(name, specs, endpoint_patterns)
        elif framework == 'flask':
            return self._generate_flask_endpoint(name, specs, endpoint_patterns)
        else:
            return self._generate_generic_endpoint(name, specs)
    
    def _generate_test_code(self, name, target, specs, test_patterns, framework):
        """Generate test code based on testing framework"""
        
        if framework == 'jest':
            return self._generate_jest_test(name, target, specs, test_patterns)
        elif framework == 'react-testing-library':
            return self._generate_rtl_test(name, target, specs, test_patterns)
        else:
            return self._generate_generic_test(name, target, specs)
    
    def _generate_model_code(self, name, specs, model_patterns):
        """Generate model/interface based on patterns"""
        
        # Detect if TypeScript interfaces or classes
        use_interface = 'interface' in str(model_patterns)
        
        if use_interface:
            return self._generate_typescript_interface(name, specs, model_patterns)
        else:
            return self._generate_model_class(name, specs, model_patterns)
    
    def _determine_needed_imports(self, specs, hooks, styling, state_mgmt):
        """Determine imports needed based on component requirements"""
        
        imports = []
        
        # React imports
        react_imports = ['React']
        if hooks:
            if 'useState' in hooks:
                react_imports.append('useState')
            if 'useEffect' in hooks:
                react_imports.append('useEffect')
            if 'useContext' in hooks:
                react_imports.append('useContext')
        
        imports.append({
            'module': 'react',
            'imports': react_imports
        })
        
        # State management imports
        if state_mgmt.get('redux'):
            imports.append({
                'module': 'react-redux',
                'imports': ['useSelector', 'useDispatch']
            })
        
        # Styling imports
        if styling == 'styled-components':
            imports.append({
                'module': 'styled-components',
                'imports': ['styled']
            })
        elif styling == 'css-modules':
            imports.append({
                'module': './styles.module.css',
                'imports': ['styles'],
                'default': True
            })
        
        # Custom imports based on specs
        if specs and specs.get('imports'):
            imports.extend(specs['imports'])
        
        return imports
    
    def _generate_props_interface(self, name, specs, prop_patterns):
        """Generate TypeScript props interface"""
        
        if not self._is_typescript():
            return ""
        
        code = f"interface {name}Props {{\n"
        
        # Add props from specs
        if specs and specs.get('props'):
            for prop in specs['props']:
                prop_type = self._infer_prop_type(prop, prop_patterns)
                code += f"  {prop}: {prop_type};\n"
        
        # Add common props from patterns
        common_props = prop_patterns.get('common', [])
        for prop in common_props:
            if specs and specs.get('props') and prop not in specs['props']:
                code += f"  {prop}?: {prop_patterns.get(prop, 'any')};\n"
        
        code += "}"
        
        return code
    
    def _generate_state_interface(self, name, specs):
        """Generate TypeScript state interface"""
        
        if not self._is_typescript():
            return ""
        
        code = f"interface {name}State {{\n"
        
        if specs and specs.get('state'):
            for state_var in specs['state']:
                state_type = self._infer_state_type(state_var)
                code += f"  {state_var}: {state_type};\n"
        else:
            # Default state
            code += "  loading: boolean;\n"
            code += "  error: string | null;\n"
        
        code += "}"
        
        return code
    
    def _add_common_hooks(self, hooks, specs):
        """Add common hooks based on patterns"""
        
        code = ""
        
        if 'useState' in hooks:
            if specs and specs.get('state'):
                for state_var in specs['state']:
                    initial_value = self._get_initial_value(state_var)
                    code += f"  const [{state_var}, set{self._capitalize(state_var)}] = useState({initial_value});\n"
            else:
                code += "  const [loading, setLoading] = useState(false);\n"
                code += "  const [error, setError] = useState(null);\n"
        
        if 'useEffect' in hooks:
            code += "\n  useEffect(() => {\n"
            code += "    // Component initialization\n"
            code += "  }, []);\n"
        
        return code + "\n" if code else ""
    
    def _add_custom_hooks(self, name, specs):
        """Add custom hooks if detected in patterns"""
        
        custom_hooks = self._find_custom_hooks()
        code = ""
        
        for hook in custom_hooks:
            if self._should_use_hook(hook, name, specs):
                code += f"  const {{{hook['returns']}}} = {hook['name']}();\n"
        
        return code + "\n" if code else ""
    
    def _add_event_handlers(self, name, specs):
        """Add event handlers based on component type"""
        
        code = ""
        
        if specs and specs.get('type') == 'form':
            code += "  const handleSubmit = (e: React.FormEvent) => {\n"
            code += "    e.preventDefault();\n"
            code += "    // Handle form submission\n"
            code += "  };\n\n"
        
        if specs and specs.get('handlers'):
            for handler in specs['handlers']:
                code += f"  const {handler} = () => {{\n"
                code += f"    // Handle {handler}\n"
                code += "  };\n\n"
        
        return code
    
    def _add_api_calls(self, name, specs):
        """Add API call patterns"""
        
        api_method = self.patterns['api_patterns'].get('method', 'fetch')
        code = ""
        
        if api_method == 'axios':
            code += "  const fetchData = async () => {\n"
            code += "    try {\n"
            code += "      setLoading(true);\n"
            code += f"      const response = await apiClient.get('/{name.lower()}');\n"
            code += "      // Handle response\n"
            code += "    } catch (error) {\n"
            code += "      setError(error.message);\n"
            code += "    } finally {\n"
            code += "      setLoading(false);\n"
            code += "    }\n"
            code += "  };\n\n"
        
        return code
    
    def _add_styling_setup(self, styling):
        """Add styling setup based on method"""
        
        if styling == 'styled-components':
            return "\n  // Styled components would be defined outside\n"
        elif styling == 'css-modules':
            return "\n  // Styles imported from CSS module\n"
        else:
            return ""
    
    def _generate_jsx_template(self, name, styling, specs):
        """Generate JSX matching project patterns"""
        
        # Check for common UI library patterns
        ui_library = self._detect_ui_library()
        
        if specs and specs.get('type') == 'form':
            return self._generate_form_jsx(name, styling, ui_library)
        elif specs and specs.get('type') == 'list':
            return self._generate_list_jsx(name, styling, ui_library)
        elif specs and specs.get('type') == 'modal':
            return self._generate_modal_jsx(name, styling, ui_library)
        else:
            return self._generate_default_jsx(name, styling, ui_library)
    
    def _generate_form_jsx(self, name, styling, ui_library):
        """Generate form JSX based on patterns"""
        
        if ui_library == 'material-ui':
            return '''    <Box component="form" onSubmit={handleSubmit}>
      <TextField
        label="Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        fullWidth
        margin="normal"
      />
      <Button type="submit" variant="contained" color="primary">
        Submit
      </Button>
    </Box>\n'''
        else:
            return f'''    <form onSubmit={{handleSubmit}}>
      <div className="{self._get_class_name('form-group', styling)}">
        <label htmlFor="name">Name</label>
        <input
          type="text"
          id="name"
          value={{name}}
          onChange={{(e) => setName(e.target.value)}}
        />
      </div>
      <button type="submit">Submit</button>
    </form>\n'''
    
    def _generate_list_jsx(self, name, styling, ui_library):
        """Generate list JSX based on patterns"""
        
        return f'''    <div className="{self._get_class_name('list-container', styling)}">
      <h2>{name}</h2>
      {{items.map((item) => (
        <div key={{item.id}} className="{self._get_class_name('list-item', styling)}">
          {{item.name}}
        </div>
      ))}}
    </div>\n'''
    
    def _generate_modal_jsx(self, name, styling, ui_library):
        """Generate modal JSX based on patterns"""
        
        if ui_library == 'material-ui':
            return '''    <Dialog open={open} onClose={handleClose}>
      <DialogTitle>{name}</DialogTitle>
      <DialogContent>
        {/* Modal content */}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button onClick={handleConfirm} color="primary">
          Confirm
        </Button>
      </DialogActions>
    </Dialog>\n'''
        else:
            return f'''    <div className="{self._get_class_name('modal-overlay', styling)}" onClick={{handleClose}}>
      <div className="{self._get_class_name('modal-content', styling)}" onClick={{(e) => e.stopPropagation()}}>
        <h2>{name}</h2>
        {{/* Modal content */}}
        <button onClick={{handleClose}}>Close</button>
      </div>
    </div>\n'''
    
    def _generate_default_jsx(self, name, styling, ui_library):
        """Generate default JSX"""
        
        if styling == 'tailwind':
            return f'''    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">{name}</h1>
      {{/* Component content */}}
    </div>\n'''
        elif styling == 'css-modules':
            return f'''    <div className={{styles.container}}>
      <h1 className={{styles.title}}>{name}</h1>
      {{/* Component content */}}
    </div>\n'''
        else:
            return f'''    <div>
      <h1>{name}</h1>
      {{/* Component content */}}
    </div>\n'''
    
    def _get_service_imports(self, api_patterns):
        """Get service imports based on API patterns"""
        
        imports = []
        
        if api_patterns.get('method') == 'axios':
            imports.append("import axiosInstance from '../api/axiosInstance';")
        
        # Add common imports from patterns
        common_imports = self._find_common_service_imports()
        imports.extend(common_imports)
        
        return '\n'.join(imports)
    
    def _generate_service_method(self, method_name, api_patterns):
        """Generate a service method"""
        
        if api_patterns.get('method') == 'axios':
            return f'''  async {method_name}(params?: any) {{
    try {{
      const response = await this.apiClient.get('/{method_name}', {{ params }});
      return response.data;
    }} catch (error) {{
      throw this.handleError(error);
    }}
  }}\n\n'''
        else:
            return f'''  async {method_name}(params?: any) {{
    // Implement {method_name} logic
    return {{}};
  }}\n\n'''
    
    def _generate_crud_methods(self, name, api_patterns):
        """Generate standard CRUD methods"""
        
        resource = name.lower()
        code = ""
        
        # GET all
        code += f'''  async getAll() {{
    return this.apiClient.get('/{resource}');
  }}\n\n'''
        
        # GET by ID
        code += f'''  async getById(id: string) {{
    return this.apiClient.get(`/{resource}/${{id}}`);
  }}\n\n'''
        
        # POST
        code += f'''  async create(data: any) {{
    return this.apiClient.post('/{resource}', data);
  }}\n\n'''
        
        # PUT
        code += f'''  async update(id: string, data: any) {{
    return this.apiClient.put(`/{resource}/${{id}}`, data);
  }}\n\n'''
        
        # DELETE
        code += f'''  async delete(id: string) {{
    return this.apiClient.delete(`/{resource}/${{id}}`);
  }}\n\n'''
        
        return code
    
    def _generate_express_endpoint(self, name, specs, patterns):
        """Generate Express endpoint"""
        
        method = specs.get('method', 'get').lower() if specs else 'get'
        path = specs.get('path', f'/{name.lower()}') if specs else f'/{name.lower()}'
        
        code = f'''router.{method}('{path}', async (req, res) => {{
  try {{
    // Validate request
    
    // Process request
    const result = await {name}Service.process(req.body);
    
    // Send response
    res.json({{
      success: true,
      data: result
    }});
  }} catch (error) {{
    res.status(500).json({{
      success: false,
      error: error.message
    }});
  }}
}});'''
        
        return code
    
    def _generate_jest_test(self, name, target, specs, patterns):
        """Generate Jest test"""
        
        code = f'''describe('{target}', () => {{
  beforeEach(() => {{
    // Setup
  }});

  afterEach(() => {{
    // Cleanup
  }});

  it('should {name}', async () => {{
    // Arrange
    const expected = {{}};
    
    // Act
    const result = await {target}();
    
    // Assert
    expect(result).toEqual(expected);
  }});
}});'''
        
        return code
    
    def _generate_typescript_interface(self, name, specs, patterns):
        """Generate TypeScript interface"""
        
        code = f"export interface {name} {{\n"
        
        if specs and specs.get('fields'):
            for field, field_type in specs['fields'].items():
                code += f"  {field}: {field_type};\n"
        else:
            # Add default fields based on patterns
            code += "  id: string;\n"
            code += "  createdAt: Date;\n"
            code += "  updatedAt: Date;\n"
        
        code += "}"
        
        return code
    
    # Helper methods
    
    def _is_typescript(self):
        """Check if project uses TypeScript"""
        return '.ts' in self.consolidated_code or '.tsx' in self.consolidated_code
    
    def _detect_ui_library(self):
        """Detect UI library used"""
        if '@mui' in self.consolidated_code or 'material-ui' in self.consolidated_code:
            return 'material-ui'
        elif 'antd' in self.consolidated_code:
            return 'ant-design'
        elif 'react-bootstrap' in self.consolidated_code:
            return 'react-bootstrap'
        return None
    
    def _get_class_name(self, base_class, styling):
        """Get class name based on styling method"""
        if styling == 'css-modules':
            return f"{{styles.{self._camelCase(base_class)}}}"
        elif styling == 'tailwind':
            # Return tailwind classes
            if base_class == 'container':
                return 'container mx-auto p-4'
            elif base_class == 'form-group':
                return 'mb-4'
            return ''
        return base_class
    
    def _capitalize(self, text):
        """Capitalize first letter"""
        return text[0].upper() + text[1:] if text else ''
    
    def _camelCase(self, text):
        """Convert to camelCase"""
        parts = text.split('-')
        return parts[0] + ''.join(p.capitalize() for p in parts[1:])
    
    def _analyze_service_patterns(self):
        """Analyze existing service patterns"""
        # Implementation to analyze service patterns
        return {}
    
    def _analyze_endpoint_patterns(self):
        """Analyze existing endpoint patterns"""
        # Implementation to analyze endpoint patterns
        return {}
    
    def _analyze_model_patterns(self):
        """Analyze existing model patterns"""
        # Implementation to analyze model patterns
        return {}
    
    def _detect_api_framework(self):
        """Detect API framework"""
        if 'express' in self.consolidated_code:
            return 'express'
        elif 'fastapi' in self.consolidated_code:
            return 'fastapi'
        elif 'flask' in self.consolidated_code:
            return 'flask'
        return 'unknown'
    
    def _find_custom_hooks(self):
        """Find custom hooks in the codebase"""
        # Implementation to find custom hooks
        return []
    
    def _should_use_hook(self, hook, component_name, specs):
        """Determine if a hook should be used"""
        # Implementation to determine hook usage
        return False
    
    def _infer_prop_type(self, prop, patterns):
        """Infer TypeScript type for prop"""
        # Common patterns
        if 'id' in prop.lower():
            return 'string'
        elif 'count' in prop.lower() or 'number' in prop.lower():
            return 'number'
        elif 'is' in prop.lower() or 'has' in prop.lower():
            return 'boolean'
        elif 'on' in prop and 'Click' in prop:
            return '() => void'
        return 'any'
    
    def _infer_state_type(self, state_var):
        """Infer TypeScript type for state variable"""
        if 'loading' in state_var.lower():
            return 'boolean'
        elif 'error' in state_var.lower():
            return 'string | null'
        elif 'items' in state_var.lower() or 'list' in state_var.lower():
            return 'any[]'
        return 'any'
    
    def _get_initial_value(self, state_var):
        """Get initial value for state variable"""
        if 'loading' in state_var.lower():
            return 'false'
        elif 'error' in state_var.lower():
            return 'null'
        elif 'items' in state_var.lower() or 'list' in state_var.lower():
            return '[]'
        elif 'count' in state_var.lower():
            return '0'
        return '""'
    
    def _find_common_service_imports(self):
        """Find common service imports"""
        # Implementation to find common imports
        return []
    
    def _add_lifecycle_methods(self, specs):
        """Add lifecycle methods for class components"""
        code = ""
        
        if specs and specs.get('hasApiCalls'):
            code += "  componentDidMount() {\n"
            code += "    this.fetchData();\n"
            code += "  }\n\n"
        
        return code
    
    def _add_class_methods(self, name, specs):
        """Add methods to class component"""
        code = ""
        
        if specs and specs.get('hasApiCalls'):
            code += "  fetchData = async () => {\n"
            code += "    // Fetch data implementation\n"
            code += "  };\n\n"
        
        return code
    
    def _generate_fastapi_endpoint(self, name, specs, patterns):
        """Generate FastAPI endpoint"""
        method = specs.get('method', 'get').lower() if specs else 'get'
        path = specs.get('path', f'/{name.lower()}') if specs else f'/{name.lower()}'
        
        return f'''@router.{method}("{path}")
async def {name}():
    """
    {name} endpoint
    """
    # Implementation
    return {{"message": "Success"}}'''
    
    def _generate_flask_endpoint(self, name, specs, patterns):
        """Generate Flask endpoint"""
        method = specs.get('method', 'GET').upper() if specs else 'GET'
        path = specs.get('path', f'/{name.lower()}') if specs else f'/{name.lower()}'
        
        return f'''@app.route('{path}', methods=['{method}'])
def {name}():
    """
    {name} endpoint
    """
    # Implementation
    return jsonify({{"message": "Success"}})'''
    
    def _generate_generic_endpoint(self, name, specs):
        """Generate generic endpoint"""
        return f'''// {name} endpoint
function {name}(req, res) {{
    // Implementation
    res.json({{ message: "Success" }});
}}'''
    
    def _generate_rtl_test(self, name, target, specs, patterns):
        """Generate React Testing Library test"""
        return f'''import {{ render, screen }} from '@testing-library/react';
import {target} from './{target}';

describe('{target}', () => {{
  it('renders {name}', () => {{
    render(<{target} />);
    
    // Add assertions
    expect(screen.getByText('{name}')).toBeInTheDocument();
  }});
}});'''
    
    def _generate_generic_test(self, name, target, specs):
        """Generate generic test"""
        return f'''// Test for {target}
test('{name}', () => {{
    // Test implementation
    expect(true).toBe(true);
}});'''
    
    def _generate_model_class(self, name, specs, patterns):
        """Generate model class"""
        return f'''class {name} {{
    constructor() {{
        // Initialize model
    }}
    
    // Model methods
}}

export default {name};'''
    
    def get_patterns_used(self):
        """Get summary of patterns used in generation"""
        return {
            'style': self.patterns['component_patterns'].get('style', 'functional'),
            'state': 'redux' if self.patterns['state_patterns'].get('redux') else 'local',
            'styling': self.patterns['styling_patterns'].get('method', 'css'),
            'patterns': self._get_applied_patterns(),
            'language': 'typescript' if self._is_typescript() else 'javascript'
        }
    
    def _get_applied_patterns(self):
        """Get list of patterns applied"""
        patterns = []
        
        if self.patterns['component_patterns'].get('common_hooks'):
            patterns.append('React Hooks')
        if self.patterns['state_patterns'].get('redux'):
            patterns.append('Redux')
        if self.patterns['styling_patterns'].get('method') == 'styled-components':
            patterns.append('Styled Components')
        
        return patterns