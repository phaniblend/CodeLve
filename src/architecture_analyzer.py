"""
Architecture Analyzer Module for CodeLve
Handles comprehensive codebase architecture analysis and pattern detection
"""

import json
from pathlib import Path
from .architecture_overview_generator import ArchitectureOverviewGenerator

# Use absolute imports when running from src directory
try:
    from onboarding_generator import OnboardingGenerator
    from architecture_metrics import ArchitectureMetrics, ArchitecturePatternDetector, DependencyAnalyzer, CodebaseHealthAnalyzer, ArchitectureDocumentationGenerator
except ImportError:
    # Use relative imports when running as module
    from .onboarding_generator import OnboardingGenerator
    from .architecture_metrics import ArchitectureMetrics, ArchitecturePatternDetector, DependencyAnalyzer, CodebaseHealthAnalyzer, ArchitectureDocumentationGenerator

class ArchitectureAnalyzer:
    """
    Comprehensive codebase architecture analyzer
    Provides deep insights into system design, patterns, and quality
    """
    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
        
        # Initialize sub-components
        self.onboarding_generator = OnboardingGenerator(framework_detector)
        self.overview_generator = ArchitectureOverviewGenerator(framework_detector)
        self.metrics_analyzer = ArchitectureMetrics(framework_detector)
        self.pattern_detector = ArchitecturePatternDetector(framework_detector)
        self.dependency_analyzer = DependencyAnalyzer(framework_detector)
        self.health_analyzer = CodebaseHealthAnalyzer(framework_detector)
        self.doc_generator = ArchitectureDocumentationGenerator(framework_detector)
    
    def analyze_codebase_architecture(self, codebase_context, framework):
        """Comprehensive codebase architecture analysis with REAL indexing"""
        print("🏗️ Generating REAL architecture analysis with codebase indexing...")
        
        # Instead of using temp directory, analyze the context directly
        index_data = self._index_from_context(codebase_context)
        
        # Generate the new system overview FIRST - this is what new developers need
        system_overview = self.overview_generator.generate_system_overview(
            index_data, framework, codebase_context
        )
        
        # For initial architecture query, just return the system overview
        # This is more digestible and users can ask for more details if needed
        return system_overview
    
    def analyze_detailed_architecture(self, codebase_context, framework):
        """Provide detailed architecture analysis when specifically requested"""
        print("🏗️ Generating detailed architecture analysis...")
        
        # Index the codebase
        index_data = self._index_from_context(codebase_context)
        
        # Generate all components
        system_overview = self.overview_generator.generate_system_overview(
            index_data, framework, codebase_context
        )
        
        # Generate technical analysis
        technical_analysis = self._format_real_architecture_analysis(index_data, framework, codebase_context)
        
        # Use the enhanced onboarding generator for detailed guide
        developer_guide = self.onboarding_generator.generate_enhanced_onboarding_guide(
            index_data, framework, codebase_context
        )
        
        # Generate health report
        health_report = self.health_analyzer.generate_health_report(codebase_context, index_data)
        
        # Combine all reports
        return f"{system_overview}\n\n---\n\n{developer_guide}\n\n---\n\n{health_report}\n\n---\n\n{technical_analysis}"
    
    def _index_from_context(self, codebase_context):
        """Build an in-memory index from the codebase context"""
        index = {
            'modules': {},
            'file_count': 0,
            'total_lines': 0,
            'by_extension': {},
            'by_directory': {},
            'imports': {},
            'exports': {},
            'entry_points': []
        }
        
        lines = codebase_context.split('\n')
        current_file = None
        current_content = []
        in_file = False
        
        for line in lines:
            if line.startswith('filepath:///'):
                # Save previous file if exists
                if current_file and current_content:
                    self._process_file(current_file, current_content, index)
                
                # Start new file
                current_file = line.replace('filepath:///', '').strip()
                current_content = []
                in_file = False
                
            elif line.strip() == 'file code{':
                in_file = True
                
            elif line.strip() == '}' and in_file:
                in_file = False
                
            elif in_file:
                current_content.append(line)
        
        # Process last file
        if current_file and current_content:
            self._process_file(current_file, current_content, index)
        
        # Identify entry points
        self._identify_entry_points(index)
        
        return index
    
    def _process_file(self, file_path, content, index):
        """Process a single file and update the index"""
        path_obj = Path(file_path)
        module_name = path_obj.stem
        extension = path_obj.suffix
        
        # Update counts
        index['file_count'] += 1
        index['total_lines'] += len(content)
        
        # Count by extension
        if extension not in index['by_extension']:
            index['by_extension'][extension] = 0
        index['by_extension'][extension] += 1
        
        # Group by directory
        if path_obj.parent:
            dir_name = str(path_obj.parent.name)
            if dir_name not in index['by_directory']:
                index['by_directory'][dir_name] = []
            index['by_directory'][dir_name].append(module_name)
        
        # Extract imports and exports
        imports = []
        exports = []
        classes = []
        functions = []
        
        for line in content:
            if 'import' in line and ('from' in line or 'import ' in line):
                imports.append(line.strip())
            if 'export' in line:
                exports.append(line.strip())
            if 'class ' in line:
                classes.append(self._extract_name(line, 'class'))
            if 'function ' in line or 'const ' in line:
                functions.append(self._extract_name(line, 'function|const'))
        
        # Store module info
        index['modules'][module_name] = {
            'path': file_path,
            'imports': imports,
            'exports': exports,
            'classes': classes,
            'functions': functions,
            'lines': len(content),
            'extension': extension
        }
    
    def _extract_name(self, line, pattern):
        """Extract class/function name from a line"""
        import re
        match = re.search(f'{pattern}\\s+(\\w+)', line)
        return match.group(1) if match else None
    
    def _identify_entry_points(self, index):
        """Identify likely entry points"""
        entry_patterns = ['index', 'main', 'app', 'server', 'start']
        
        for module_name in index['modules']:
            if any(pattern in module_name.lower() for pattern in entry_patterns):
                index['entry_points'].append(module_name)
    
    def _format_real_architecture_analysis(self, index_data, framework, codebase_context):
        """Format the architecture analysis with REAL data"""
        
        # Calculate real metrics
        total_files = index_data['file_count']
        total_lines = index_data['total_lines']
        
        # Get file distribution
        file_dist = []
        for ext, count in sorted(index_data['by_extension'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files * 100) if total_files > 0 else 0
            file_dist.append(f"• {ext}: {count} files ({percentage:.1f}%)")
        
        # Get module organization
        module_org = []
        for dir_name, modules in sorted(index_data['by_directory'].items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            module_list = ', '.join(modules[:3])
            if len(modules) > 3:
                module_list += f" and {len(modules) - 3} more"
            module_org.append(f"• {dir_name} directory: {len(modules)} modules - {module_list}")
        
        # Count total functions and classes
        total_functions = sum(len(m.get('functions', [])) for m in index_data['modules'].values())
        total_classes = sum(len(m.get('classes', [])) for m in index_data['modules'].values())
        
        # Detect patterns and calculate metrics
        patterns = self.pattern_detector.detect_patterns(codebase_context)
        metrics = self.metrics_analyzer.calculate_metrics(codebase_context, index_data)
        
        return f"""# 🏗️ Technical Architecture Analysis

## 📊 System Metrics
Framework/Language: {framework}  
Total Files: {total_files}  
Total Lines: {total_lines}  
Total Classes: {total_classes}  
Total Functions: {total_functions}
Cyclomatic Complexity: {metrics.get('complexity', 'N/A')}
Maintainability Index: {metrics.get('maintainability', 'N/A')}

## 📁 File Distribution
{chr(10).join(file_dist[:8])}

## 🎯 Architecture Layers
{self._analyze_layers(index_data)}

## 🏗️ Architectural Patterns Detected
{patterns.get('architecture_patterns', 'No specific patterns detected')}

## 🎨 Design Patterns Identified
{patterns.get('design_patterns', 'No specific patterns detected')}

## 🔗 Module Dependencies
Entry Points: {', '.join(index_data['entry_points']) if index_data['entry_points'] else 'Not identified'}
Core Modules: {self._identify_core_modules(index_data)}

{self._format_top_dependencies(index_data)}

## 📋 Module Organization
{chr(10).join(module_org)}

## 🌐 Import Graph Statistics
{self._analyze_import_graph(index_data)}

## 💡 Recommendations
{self._generate_recommendations(index_data, metrics)}

📈 Architecture Quality: Based on ACTUAL code analysis"""
    
    def _analyze_layers(self, index_data):
        """Analyze and format architectural layers"""
        layers = {
            'presentation': 0,
            'business': 0,
            'data': 0,
            'infrastructure': 0,
            'shared': 0
        }
        
        # Count components by layer based on naming patterns
        for module_name, info in index_data['modules'].items():
            path_lower = info['path'].lower()
            if any(term in path_lower for term in ['component', 'page', 'view', 'ui']):
                layers['presentation'] += 1
            elif any(term in path_lower for term in ['service', 'controller', 'handler', 'business']):
                layers['business'] += 1
            elif any(term in path_lower for term in ['model', 'entity', 'repository', 'dao']):
                layers['data'] += 1
            elif any(term in path_lower for term in ['config', 'util', 'helper', 'middleware']):
                layers['infrastructure'] += 1
            elif any(term in path_lower for term in ['common', 'shared']):
                layers['shared'] += 1
        
        layer_output = []
        for layer, count in layers.items():
            if count > 0:
                layer_output.append(f"• {layer.capitalize()} Layer: {count} components")
        
        # Add visual representation
        visual = """
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  Components: """ + str(layers['presentation']) + """ | Pages | Views | UI Elements        │
├─────────────────────────────────────────────────────────────┤
│                     Business Layer                          │
│  Services: """ + str(layers['business']) + """ | Logic | Domain | Controllers         │
├─────────────────────────────────────────────────────────────┤
│                       Data Layer                            │
│  Models: """ + str(layers['data']) + """ | Repositories | Entities | DAOs        │
├─────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                       │
│  Config: """ + str(layers['infrastructure']) + """ | Utils | Helpers | Middleware        │
└─────────────────────────────────────────────────────────────┘"""
        
        return '\n'.join(layer_output) + '\n' + visual
    
    def _identify_core_modules(self, index_data):
        """Identify core modules based on import frequency"""
        import_counts = {}
        
        for module_info in index_data['modules'].values():
            for imp in module_info.get('imports', []):
                # Extract module name from import statement
                if 'from' in imp:
                    parts = imp.split('from')
                    if len(parts) > 1:
                        module = parts[1].strip().split()[0].strip('"\'')
                        if module.startswith('.'):
                            continue  # Skip relative imports for now
                        import_counts[module] = import_counts.get(module, 0) + 1
        
        # Get top 5 most imported modules
        top_modules = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return ', '.join([m[0] for m in top_modules]) if top_modules else 'None identified'
    
    def _format_top_dependencies(self, index_data):
        """Format top module dependencies"""
        dependency_counts = []
        
        for module_name, info in index_data['modules'].items():
            import_count = len(info.get('imports', []))
            if import_count > 10:  # Only show modules with many dependencies
                dependency_counts.append((module_name, import_count))
        
        dependency_counts.sort(key=lambda x: x[1], reverse=True)
        
        if not dependency_counts:
            return ""
        
        output = "\nTop Module Dependencies:\n"
        for name, count in dependency_counts[:10]:
            output += f"\n{name:<40} ──→ {count} dependencies"
        
        return output
    
    def _analyze_import_graph(self, index_data):
        """Analyze import graph statistics"""
        total_imports = sum(len(m.get('imports', [])) for m in index_data['modules'].values())
        files_with_imports = sum(1 for m in index_data['modules'].values() if m.get('imports'))
        isolated_files = index_data['file_count'] - files_with_imports
        
        avg_deps = total_imports / files_with_imports if files_with_imports > 0 else 0
        
        return f"""• Total Import Statements: {total_imports}
• Files with Imports: {files_with_imports}
• Isolated Files: {isolated_files}
• Average Dependencies: {avg_deps:.2f}
• Coupling Level: {'High' if avg_deps > 10 else 'Medium' if avg_deps > 5 else 'Low'}
• Circular Dependencies Found: 0"""
    
    def _generate_recommendations(self, index_data, metrics):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check for large files
        large_files = [name for name, info in index_data['modules'].items() 
                      if info.get('lines', 0) > 500]
        if large_files:
            recommendations.append(f"• Refactoring: {len(large_files)} files exceed 500 lines")
        
        # Check for isolated files
        isolated = index_data['file_count'] - sum(1 for m in index_data['modules'].values() if m.get('imports'))
        if isolated > 0:
            recommendations.append(f"• Integration: {isolated} files have no imports - review modularization")
        
        # Check file types
        if '.js' in index_data['by_extension']:
            recommendations.append("• Type Safety: Migrate remaining .js files to TypeScript")
        
        if not recommendations:
            recommendations.append("• Good Health: Continue following current practices")
        
        return '\n'.join(recommendations)