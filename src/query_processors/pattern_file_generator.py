"""
Pattern-Based File Generator
Analyzes existing files and generates new ones following the same patterns
"""

import re
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class PatternFileGenerator:
    """Generate new files following existing patterns in a directory"""
    
    def __init__(self, consolidated_code: str):
        self.consolidated_code = consolidated_code
        self.file_patterns = {}
        
    def extract_directory_patterns(self, directory_path: str) -> Dict[str, any]:
        """Extract patterns from all files in a directory"""
        patterns = {
            'imports': [],
            'component_structure': None,
            'export_style': None,
            'naming_convention': None,
            'common_hooks': [],
            'prop_types': {},
            'file_structure': []
        }
        
        # Find all files in the specified directory
        dir_files = self._find_files_in_directory(directory_path)
        
        if not dir_files:
            return patterns
        
        # Analyze each file
        for file_path, content in dir_files.items():
            file_patterns = self._analyze_file_patterns(content)
            self._merge_patterns(patterns, file_patterns)
        
        # Determine common patterns
        patterns['common_structure'] = self._determine_common_structure(patterns)
        
        return patterns
    
    def _find_files_in_directory(self, directory_path: str) -> Dict[str, str]:
        """Find all files in the specified directory from consolidated code"""
        files = {}
        
        # Normalize directory path
        dir_path = directory_path.replace('\\', '/')
        if not dir_path.endswith('/'):
            dir_path += '/'
        
        # Extract files from consolidated code
        file_pattern = rf'#\s*File:\s*({re.escape(dir_path)}[^/\n]+)\n(.*?)(?=#\s*File:|$)'
        
        for match in re.finditer(file_pattern, self.consolidated_code, re.DOTALL):
            file_path = match.group(1)
            content = match.group(2)
            
            # Only include files from the exact directory (not subdirectories)
            if file_path.count('/') == dir_path.count('/'):
                files[file_path] = content
        
        return files
    
    def _analyze_file_patterns(self, content: str) -> Dict:
        """Analyze patterns in a single file"""
        patterns = {
            'imports': self._extract_imports(content),
            'component_name': self._extract_component_name(content),
            'props': self._extract_props(content),
            'hooks': self._extract_hooks(content),
            'structure': self._extract_structure(content),
            'exports': self._extract_export_style(content)
        }
        
        return patterns
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        imports = []
        import_pattern = r'^import\s+.*?;$'
        
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            imports.append(match.group(0))
        
        return imports
    
    def _extract_component_name(self, content: str) -> Optional[str]:
        """Extract the main component name"""
        # Function component
        pattern = r'(?:export\s+)?(?:const|function)\s+(\w+)(?::\s*React\.FC.*?)?\s*='
        match = re.search(pattern, content)
        
        if match:
            return match.group(1)
        
        return None
    
    def _extract_props(self, content: str) -> Dict:
        """Extract component props"""
        props = {}
        
        # TypeScript interface
        interface_pattern = r'interface\s+\w*Props\s*{\s*((?:[^}])*)\s*}'
        match = re.search(interface_pattern, content)
        
        if match:
            props_content = match.group(1)
            prop_pattern = r'(\w+)\s*:\s*([^;,\n]+)'
            
            for prop_match in re.finditer(prop_pattern, props_content):
                props[prop_match.group(1)] = prop_match.group(2).strip()
        
        return props
    
    def _extract_hooks(self, content: str) -> List[str]:
        """Extract React hooks used"""
        hooks = []
        hook_pattern = r'(use\w+)\s*\('
        
        for match in re.finditer(hook_pattern, content):
            hook = match.group(1)
            if hook not in hooks:
                hooks.append(hook)
        
        return hooks
    
    def _extract_structure(self, content: str) -> Dict:
        """Extract component structure"""
        structure = {
            'has_state': 'useState' in content,
            'has_effects': 'useEffect' in content,
            'has_context': 'useContext' in content,
            'has_memo': 'useMemo' in content or 'useCallback' in content,
            'sections': []
        }
        
        # Extract main sections (comments indicating sections)
        section_pattern = r'//\s*([A-Z][^\n]+)'
        for match in re.finditer(section_pattern, content):
            structure['sections'].append(match.group(1))
        
        return structure
    
    def _extract_export_style(self, content: str) -> str:
        """Determine export style"""
        if 'export default' in content:
            return 'default'
        elif 'export {' in content:
            return 'named'
        else:
            return 'none'
    
    def _merge_patterns(self, target: Dict, source: Dict):
        """Merge patterns from multiple files"""
        # Merge imports (keep unique)
        for imp in source.get('imports', []):
            if imp not in target['imports']:
                target['imports'].append(imp)
        
        # Track all hooks
        for hook in source.get('hooks', []):
            if hook not in target['common_hooks']:
                target['common_hooks'].append(hook)
        
        # Merge props
        if source.get('props'):
            if not target['prop_types']:
                target['prop_types'] = source['props']
    
    def _determine_common_structure(self, patterns: Dict) -> str:
        """Determine the common structure template"""
        # This would analyze all patterns and create a template
        # For now, return a basic structure
        return "functional_component"
    
    def generate_file_from_patterns(self, 
                                  file_name: str,
                                  directory_path: str,
                                  patterns: Dict,
                                  specifications: Optional[Dict] = None) -> str:
        """Generate a new file following the extracted patterns"""
        
        # Extract component name from file name
        component_name = self._filename_to_component_name(file_name)
        
        # Build the file content
        content = ""
        
        # Add imports based on patterns
        content += self._generate_imports(patterns, specifications)
        content += "\n\n"
        
        # Add interfaces if TypeScript
        if self._is_typescript(file_name):
            content += self._generate_interfaces(component_name, patterns, specifications)
            content += "\n\n"
        
        # Add component
        content += self._generate_component(component_name, patterns, specifications)
        content += "\n\n"
        
        # Add export
        content += self._generate_export(component_name, patterns)
        
        return content
    
    def _filename_to_component_name(self, file_name: str) -> str:
        """Convert filename to component name"""
        # Remove extension
        name = file_name.replace('.tsx', '').replace('.jsx', '').replace('.ts', '').replace('.js', '')
        
        # Handle numbered prefixes (e.g., "06_09-OffRoad-Replacement" -> "OffRoadReplacement")
        name = re.sub(r'^\d+_\d+-', '', name)
        
        # Convert to PascalCase
        parts = re.split(r'[-_]', name)
        return ''.join(part.capitalize() for part in parts)
    
    def _is_typescript(self, file_name: str) -> bool:
        """Check if file is TypeScript"""
        return file_name.endswith('.ts') or file_name.endswith('.tsx')
    
    def _generate_imports(self, patterns: Dict, specs: Optional[Dict]) -> str:
        """Generate import statements"""
        imports = []
        
        # Common React imports
        imports.append("import React from 'react';")
        
        # Add hooks if commonly used
        if patterns.get('common_hooks'):
            hooks = ', '.join(patterns['common_hooks'])
            imports.append(f"import {{ {hooks} }} from 'react';")
        
        # Add common imports from patterns
        for imp in patterns.get('imports', []):
            # Skip React imports (already added)
            if 'from \'react\'' not in imp and imp not in imports:
                imports.append(imp)
        
        return '\n'.join(imports)
    
    def _generate_interfaces(self, component_name: str, patterns: Dict, specs: Optional[Dict]) -> str:
        """Generate TypeScript interfaces"""
        code = f"interface {component_name}Props {{\n"
        
        # Add props based on patterns and specifications
        if specs and specs.get('props'):
            for prop, prop_type in specs['props'].items():
                code += f"  {prop}: {prop_type};\n"
        elif patterns.get('prop_types'):
            # Use common props from patterns
            for prop, prop_type in patterns['prop_types'].items():
                code += f"  {prop}?: {prop_type};\n"
        
        code += "}"
        
        return code
    
    def _generate_component(self, component_name: str, patterns: Dict, specs: Optional[Dict]) -> str:
        """Generate the component based on patterns"""
        code = f"const {component_name}: React.FC<{component_name}Props> = ({{"
        
        # Add props
        if specs and specs.get('props'):
            code += ', '.join(specs['props'].keys())
        
        code += "}) => {\n"
        
        # Add hooks based on patterns
        if 'useState' in patterns.get('common_hooks', []):
            code += "  const [loading, setLoading] = useState(false);\n"
        
        if 'useEffect' in patterns.get('common_hooks', []):
            code += "\n  useEffect(() => {\n"
            code += "    // Initialize component\n"
            code += "  }, []);\n"
        
        # Add return statement
        code += "\n  return (\n"
        code += "    <div>\n"
        code += f"      <h2>{component_name}</h2>\n"
        code += "      {/* Add your component content here */}\n"
        code += "    </div>\n"
        code += "  );\n"
        code += "};"
        
        return code
    
    def _generate_export(self, component_name: str, patterns: Dict) -> str:
        """Generate export statement"""
        export_style = patterns.get('export_style', 'default')
        
        if export_style == 'default':
            return f"export default {component_name};"
        else:
            return f"export {{ {component_name} }};"


def generate_file_following_patterns(query: str, consolidated_code: str) -> str:
    """Main function to generate a file following directory patterns"""
    
    # Parse the query to extract file name and directory
    # Handle multiple query formats
    patterns = [
        r'create a new section called (.+?) under (?:the folder )?(.+?) folder',
        r'create a new file called (.+?) in (?:the )?(.+?) folder',
        r'generate (.+?) in (.+?) following',
        r'create (.+?) under (.+?) in the same pattern'
    ]
    
    match = None
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            break
    
    if not match:
        return "Could not parse the file generation request. Please specify the file name and directory."
    
    file_path = match.group(1).strip()
    directory = match.group(2).strip()
    
    # Extract file name
    file_name = os.path.basename(file_path)
    
    # Initialize generator
    generator = PatternFileGenerator(consolidated_code)
    
    # Extract patterns from the directory
    patterns = generator.extract_directory_patterns(directory)
    
    if not patterns['imports']:
        return f"Could not find files in {directory} to analyze patterns."
    
    # Generate the new file
    generated_content = generator.generate_file_from_patterns(
        file_name,
        directory,
        patterns
    )
    
    return f"Generated {file_name} following patterns in {directory}:\n\n```typescript\n{generated_content}\n```"