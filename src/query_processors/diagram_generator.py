"""
Diagram generation module for CodeLve.
Creates architecture, dependency, sequence, and flow diagrams.
"""

import re
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict


class DiagramGenerator:
    """Handles diagram generation from codebase analysis."""
    
    def __init__(self, consolidated_code: str):
        self.consolidated_code = consolidated_code
        self.modules = self._extract_modules()
        self.dependencies = self._analyze_dependencies()
        self.classes = self._extract_classes()
        self.functions = self._extract_functions()
    
    def _extract_modules(self) -> Dict[str, List[str]]:
        """Extract module structure from the codebase."""
        modules = defaultdict(list)
        
        # Pattern to match file headers
        file_pattern = r'#\s*File:\s*(.+?)(?:\n|$)'
        current_file = None
        
        for line in self.consolidated_code.split('\n'):
            file_match = re.match(file_pattern, line)
            if file_match:
                current_file = file_match.group(1).strip()
                modules[current_file] = []
            elif current_file:
                modules[current_file].append(line)
        
        return dict(modules)
    
    def _analyze_dependencies(self) -> Dict[str, Set[str]]:
        """Analyze import dependencies between modules."""
        dependencies = defaultdict(set)
        
        import_pattern = r'(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))'
        
        for module, lines in self.modules.items():
            module_code = '\n'.join(lines)
            for match in re.finditer(import_pattern, module_code):
                imported = match.group(1) or match.group(2)
                if imported and not imported.startswith('.'):
                    dependencies[module].add(imported)
        
        return dict(dependencies)
    
    def _extract_classes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract class information from the codebase."""
        classes = defaultdict(list)
        
        class_pattern = r'class\s+(\w+)(?:\((.*?)\))?:\s*\n((?:\s{4,}.*\n)*)'
        
        for module, lines in self.modules.items():
            module_code = '\n'.join(lines)
            for match in re.finditer(class_pattern, module_code):
                class_info = {
                    'name': match.group(1),
                    'base_classes': [b.strip() for b in match.group(2).split(',')] if match.group(2) else [],
                    'methods': self._extract_class_methods(match.group(3)),
                    'module': module
                }
                classes[module].append(class_info)
        
        return dict(classes)
    
    def _extract_class_methods(self, class_body: str) -> List[str]:
        """Extract method names from a class body."""
        methods = []
        method_pattern = r'def\s+(\w+)\s*\('
        for match in re.finditer(method_pattern, class_body):
            methods.append(match.group(1))
        return methods
    
    def _extract_functions(self) -> Dict[str, List[str]]:
        """Extract standalone functions from modules."""
        functions = defaultdict(list)
        
        # Pattern for top-level functions
        function_pattern = r'^def\s+(\w+)\s*\('
        
        for module, lines in self.modules.items():
            for line in lines:
                match = re.match(function_pattern, line)
                if match:
                    functions[module].append(match.group(1))
        
        return dict(functions)
    
    def generate_architecture_diagram(self) -> str:
        """Generate a high-level architecture diagram."""
        mermaid_code = "graph TB\n"
        mermaid_code += "    %% Architecture Overview\n\n"
        
        # Group modules by type
        module_types = self._categorize_modules()
        
        # Create subgraphs for each module type
        for module_type, modules in module_types.items():
            if modules:
                mermaid_code += f"    subgraph {module_type}[{module_type.replace('_', ' ').title()}]\n"
                for module in modules:
                    module_id = module.replace('/', '_').replace('.', '_')
                    mermaid_code += f"        {module_id}[{module}]\n"
                mermaid_code += "    end\n\n"
        
        # Add dependencies between modules
        for module, deps in self.dependencies.items():
            module_id = module.replace('/', '_').replace('.', '_')
            for dep in deps:
                # Only show internal dependencies
                if any(dep.startswith(m) for m in self.modules.keys()):
                    dep_id = dep.replace('/', '_').replace('.', '_')
                    mermaid_code += f"    {module_id} --> {dep_id}\n"
        
        mermaid_code += "\n    %% Styling\n"
        mermaid_code += "    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px\n"
        mermaid_code += "    classDef backend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px\n"
        mermaid_code += "    classDef database fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px\n"
        mermaid_code += "    classDef service fill:#fff3e0,stroke:#e65100,stroke-width:2px\n"
        
        return mermaid_code
    
    def _categorize_modules(self) -> Dict[str, List[str]]:
        """Categorize modules by their type/purpose."""
        categories = defaultdict(list)
        
        for module in self.modules.keys():
            if any(keyword in module.lower() for keyword in ['ui', 'view', 'component', 'frontend']):
                categories['frontend'].append(module)
            elif any(keyword in module.lower() for keyword in ['model', 'db', 'database', 'schema']):
                categories['database'].append(module)
            elif any(keyword in module.lower() for keyword in ['api', 'route', 'endpoint', 'controller']):
                categories['api'].append(module)
            elif any(keyword in module.lower() for keyword in ['service', 'handler', 'processor']):
                categories['services'].append(module)
            elif any(keyword in module.lower() for keyword in ['util', 'helper', 'common']):
                categories['utilities'].append(module)
            else:
                categories['core'].append(module)
        
        return dict(categories)
    
    def generate_dependency_graph(self, module_name: Optional[str] = None) -> str:
        """Generate a dependency graph for a specific module or the entire system."""
        mermaid_code = "graph LR\n"
        mermaid_code += "    %% Dependency Graph\n\n"
        
        if module_name:
            # Generate dependencies for specific module
            deps = self._get_module_dependencies(module_name)
            dependents = self._get_module_dependents(module_name)
            
            module_id = module_name.replace('/', '_').replace('.', '_')
            mermaid_code += f"    {module_id}[{module_name}]\n"
            mermaid_code += f"    style {module_id} fill:#ffeb3b,stroke:#f57f17,stroke-width:3px\n\n"
            
            # Add dependencies
            mermaid_code += "    %% Dependencies (this module depends on)\n"
            for dep in deps:
                dep_id = dep.replace('/', '_').replace('.', '_')
                mermaid_code += f"    {dep_id}[{dep}] --> {module_id}\n"
            
            # Add dependents
            mermaid_code += "\n    %% Dependents (modules that depend on this)\n"
            for dependent in dependents:
                dependent_id = dependent.replace('/', '_').replace('.', '_')
                mermaid_code += f"    {module_id} --> {dependent_id}[{dependent}]\n"
        else:
            # Generate full dependency graph
            for module, deps in self.dependencies.items():
                module_id = module.replace('/', '_').replace('.', '_')
                for dep in deps:
                    dep_id = dep.replace('/', '_').replace('.', '_')
                    mermaid_code += f"    {dep_id} --> {module_id}\n"
        
        return mermaid_code
    
    def _get_module_dependencies(self, module_name: str) -> Set[str]:
        """Get all dependencies of a module."""
        return self.dependencies.get(module_name, set())
    
    def _get_module_dependents(self, module_name: str) -> Set[str]:
        """Get all modules that depend on the given module."""
        dependents = set()
        for module, deps in self.dependencies.items():
            if module_name in deps or any(dep.startswith(module_name) for dep in deps):
                dependents.add(module)
        return dependents
    
    def generate_class_diagram(self, module_name: Optional[str] = None) -> str:
        """Generate a class diagram for a module or the entire system."""
        mermaid_code = "classDiagram\n"
        mermaid_code += "    %% Class Diagram\n\n"
        
        # Filter classes by module if specified
        classes_to_show = self.classes
        if module_name:
            classes_to_show = {module_name: self.classes.get(module_name, [])}
        
        # Add classes and their relationships
        for module, class_list in classes_to_show.items():
            for class_info in class_list:
                class_name = class_info['name']
                
                # Add class definition
                mermaid_code += f"    class {class_name} {{\n"
                
                # Add methods
                for method in class_info['methods']:
                    visibility = "-" if method.startswith('_') else "+"
                    mermaid_code += f"        {visibility}{method}()\n"
                
                mermaid_code += "    }\n\n"
                
                # Add inheritance relationships
                for base_class in class_info['base_classes']:
                    if base_class and base_class != 'object':
                        mermaid_code += f"    {base_class} <|-- {class_name}\n"
        
        # Add associations based on method calls and attributes
        associations = self._analyze_class_associations()
        for (class1, class2), relationship in associations.items():
            mermaid_code += f"    {class1} --> {class2} : {relationship}\n"
        
        return mermaid_code
    
    def _analyze_class_associations(self) -> Dict[Tuple[str, str], str]:
        """Analyze associations between classes."""
        associations = {}
        
        # Simple pattern matching for class instantiation and usage
        for module, class_list in self.classes.items():
            module_code = '\n'.join(self.modules.get(module, []))
            
            for class_info in class_list:
                class_name = class_info['name']
                
                # Look for instantiation patterns
                instantiation_pattern = rf'(\w+)\s*=\s*{class_name}\s*\('
                for match in re.finditer(instantiation_pattern, module_code):
                    var_name = match.group(1)
                    # Look for usage of this variable
                    usage_pattern = rf'{var_name}\.\w+'
                    if re.search(usage_pattern, module_code):
                        # Find the class that uses this
                        for other_class in class_list:
                            if other_class['name'] != class_name:
                                method_bodies = '\n'.join([
                                    self._get_method_body(module_code, other_class['name'], method)
                                    for method in other_class['methods']
                                ])
                                if var_name in method_bodies:
                                    associations[(other_class['name'], class_name)] = "uses"
        
        return associations
    
    def _get_method_body(self, code: str, class_name: str, method_name: str) -> str:
        """Extract method body from code."""
        pattern = rf'class\s+{class_name}.*?def\s+{method_name}\s*\([^)]*\):\s*\n((?:\s{{4,}}.*\n)*)'
        match = re.search(pattern, code, re.DOTALL)
        return match.group(1) if match else ""
    
    def generate_sequence_diagram(self, scenario: str) -> str:
        """Generate a sequence diagram for a specific scenario."""
        mermaid_code = "sequenceDiagram\n"
        mermaid_code += f"    %% Sequence Diagram: {scenario}\n\n"
        
        # Analyze the scenario to identify participants
        participants = self._identify_sequence_participants(scenario)
        
        # Add participants
        for participant in participants:
            mermaid_code += f"    participant {participant}\n"
        
        mermaid_code += "\n"
        
        # Generate interactions based on scenario
        interactions = self._analyze_sequence_interactions(scenario, participants)
        
        for interaction in interactions:
            mermaid_code += f"    {interaction['from']}->>+{interaction['to']}: {interaction['message']}\n"
            if interaction.get('response'):
                mermaid_code += f"    {interaction['to']}-->>-{interaction['from']}: {interaction['response']}\n"
        
        return mermaid_code
    
    def _identify_sequence_participants(self, scenario: str) -> List[str]:
        """Identify participants in a sequence diagram based on scenario."""
        participants = []
        
        # Common participants based on keywords
        if any(word in scenario.lower() for word in ['user', 'client', 'frontend']):
            participants.append('User')
        if any(word in scenario.lower() for word in ['api', 'endpoint', 'server']):
            participants.append('API')
        if any(word in scenario.lower() for word in ['database', 'db', 'storage']):
            participants.append('Database')
        if any(word in scenario.lower() for word in ['service', 'handler', 'processor']):
            participants.append('Service')
        if any(word in scenario.lower() for word in ['cache', 'redis', 'memory']):
            participants.append('Cache')
        
        # Ensure at least basic participants
        if not participants:
            participants = ['Client', 'Server', 'Database']
        
        return participants
    
    def _analyze_sequence_interactions(self, scenario: str, participants: List[str]) -> List[Dict[str, str]]:
        """Analyze and generate sequence interactions."""
        interactions = []
        
        # Generate basic interaction flow based on scenario keywords
        scenario_lower = scenario.lower()
        
        if 'login' in scenario_lower or 'auth' in scenario_lower:
            interactions.extend([
                {'from': 'User', 'to': 'API', 'message': 'Login Request (credentials)'},
                {'from': 'API', 'to': 'Database', 'message': 'Verify Credentials'},
                {'from': 'Database', 'to': 'API', 'message': 'User Data', 'response': 'User Found'},
                {'from': 'API', 'to': 'API', 'message': 'Generate Token'},
                {'from': 'API', 'to': 'User', 'message': 'Login Success', 'response': 'JWT Token'}
            ])
        elif 'create' in scenario_lower or 'add' in scenario_lower:
            interactions.extend([
                {'from': 'User', 'to': 'API', 'message': 'Create Request (data)'},
                {'from': 'API', 'to': 'API', 'message': 'Validate Data'},
                {'from': 'API', 'to': 'Database', 'message': 'Insert Record'},
                {'from': 'Database', 'to': 'API', 'message': 'Success', 'response': 'Record ID'},
                {'from': 'API', 'to': 'User', 'message': 'Created', 'response': 'Resource Created'}
            ])
        elif 'fetch' in scenario_lower or 'get' in scenario_lower or 'retrieve' in scenario_lower:
            interactions.extend([
                {'from': 'User', 'to': 'API', 'message': 'Get Request (id)'},
                {'from': 'API', 'to': 'Cache', 'message': 'Check Cache'},
                {'from': 'Cache', 'to': 'API', 'message': 'Cache Miss'},
                {'from': 'API', 'to': 'Database', 'message': 'Query Data'},
                {'from': 'Database', 'to': 'API', 'message': 'Data', 'response': 'Record Found'},
                {'from': 'API', 'to': 'Cache', 'message': 'Store in Cache'},
                {'from': 'API', 'to': 'User', 'message': 'Response', 'response': 'Requested Data'}
            ])
        else:
            # Generic flow
            interactions.extend([
                {'from': participants[0], 'to': participants[1] if len(participants) > 1 else participants[0], 
                 'message': 'Request'},
                {'from': participants[1] if len(participants) > 1 else participants[0], 
                 'to': participants[2] if len(participants) > 2 else participants[0], 
                 'message': 'Process'},
                {'from': participants[2] if len(participants) > 2 else participants[0], 
                 'to': participants[1] if len(participants) > 1 else participants[0], 
                 'message': 'Response', 'response': 'Success'}
            ])
        
        # Filter interactions to only include available participants
        filtered_interactions = []
        for interaction in interactions:
            if interaction['from'] in participants and interaction['to'] in participants:
                filtered_interactions.append(interaction)
        
        return filtered_interactions
    
    def generate_flow_diagram(self, process_name: str) -> str:
        """Generate a flow diagram for a specific process."""
        mermaid_code = "flowchart TD\n"
        mermaid_code += f"    %% Flow Diagram: {process_name}\n\n"
        
        # Analyze the process to create flow
        flow_steps = self._analyze_process_flow(process_name)
        
        # Generate flow nodes and connections
        for i, step in enumerate(flow_steps):
            node_id = f"step{i}"
            
            # Determine node shape based on step type
            if step['type'] == 'start':
                mermaid_code += f"    {node_id}([{step['label']}])\n"
            elif step['type'] == 'end':
                mermaid_code += f"    {node_id}([{step['label']}])\n"
            elif step['type'] == 'decision':
                mermaid_code += f"    {node_id}{{{{{step['label']}}}}}\n"
            elif step['type'] == 'process':
                mermaid_code += f"    {node_id}[{step['label']}]\n"
            elif step['type'] == 'data':
                mermaid_code += f"    {node_id}[({step['label']})]"
            
            # Add connections
            if i < len(flow_steps) - 1:
                next_id = f"step{i + 1}"
                if step['type'] == 'decision':
                    mermaid_code += f"    {node_id} -->|Yes| {next_id}\n"
                    # Add alternative path for decisions
                    alt_id = f"alt{i}"
                    mermaid_code += f"    {node_id} -->|No| {alt_id}[Handle Alternative]\n"
                    mermaid_code += f"    {alt_id} --> {next_id}\n"
                else:
                    mermaid_code += f"    {node_id} --> {next_id}\n"
        
        # Add styling
        mermaid_code += "\n    %% Styling\n"
        mermaid_code += "    classDef startEnd fill:#90caf9,stroke:#1565c0,stroke-width:2px\n"
        mermaid_code += "    classDef process fill:#a5d6a7,stroke:#2e7d32,stroke-width:2px\n"
        mermaid_code += "    classDef decision fill:#ffcc80,stroke:#ef6c00,stroke-width:2px\n"
        
        return mermaid_code
    
    def _analyze_process_flow(self, process_name: str) -> List[Dict[str, str]]:
        """Analyze a process and generate flow steps."""
        steps = []
        
        # Start node
        steps.append({'type': 'start', 'label': f'Start {process_name}'})
        
        # Analyze process name and code to determine steps
        process_lower = process_name.lower()
        
        if 'validation' in process_lower:
            steps.extend([
                {'type': 'process', 'label': 'Receive Input'},
                {'type': 'decision', 'label': 'Valid Format?'},
                {'type': 'process', 'label': 'Process Data'},
                {'type': 'decision', 'label': 'Business Rules OK?'},
                {'type': 'process', 'label': 'Return Success'}
            ])
        elif 'authentication' in process_lower or 'auth' in process_lower:
            steps.extend([
                {'type': 'process', 'label': 'Receive Credentials'},
                {'type': 'process', 'label': 'Hash Password'},
                {'type': 'data', 'label': 'Query User DB'},
                {'type': 'decision', 'label': 'User Exists?'},
                {'type': 'decision', 'label': 'Password Matches?'},
                {'type': 'process', 'label': 'Generate Token'},
                {'type': 'process', 'label': 'Return Token'}
            ])
        elif 'data processing' in process_lower or 'etl' in process_lower:
            steps.extend([
                {'type': 'process', 'label': 'Extract Data'},
                {'type': 'process', 'label': 'Validate Data'},
                {'type': 'decision', 'label': 'Data Valid?'},
                {'type': 'process', 'label': 'Transform Data'},
                {'type': 'process', 'label': 'Load to Target'},
                {'type': 'decision', 'label': 'Load Successful?'},
                {'type': 'process', 'label': 'Update Status'}
            ])
        else:
            # Generic process flow
            steps.extend([
                {'type': 'process', 'label': 'Initialize Process'},
                {'type': 'process', 'label': 'Execute Main Logic'},
                {'type': 'decision', 'label': 'Success?'},
                {'type': 'process', 'label': 'Handle Result'},
                {'type': 'process', 'label': 'Clean Up'}
            ])
        
        # End node
        steps.append({'type': 'end', 'label': f'End {process_name}'})
        
        return steps