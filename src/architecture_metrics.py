"""
Architecture Metrics Module for CodeLve
Provides advanced architectural analysis, pattern detection, and health metrics
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

class ArchitectureMetrics:
    """Calculate code metrics and quality indicators"""
    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
    
    def calculate_complexity_metrics(self, codebase_context):
        """Calculate cyclomatic complexity and other code metrics"""
        lines = codebase_context.split('\n')
        
        # Count complexity indicators
        if_count = sum(1 for line in lines if re.search(r'\b(if|elif)\b', line))
        for_count = sum(1 for line in lines if re.search(r'\b(for|while)\b', line))
        case_count = sum(1 for line in lines if re.search(r'\b(case|switch)\b', line))
        try_count = sum(1 for line in lines if re.search(r'\btry\b', line))
        
        # Basic cyclomatic complexity calculation
        complexity = 1 + if_count + for_count + case_count + try_count
        
        # Normalize by file count (rough estimate)
        file_count = codebase_context.count('filepath:///') or 1
        avg_complexity = round(complexity / file_count, 2)
        
        return {
            'cyclomatic_complexity': avg_complexity,
            'total_conditionals': if_count,
            'total_loops': for_count,
            'total_exceptions': try_count
        }
    
    def calculate_maintainability_index(self, codebase_context):
        """Calculate maintainability index (0-100 scale)"""
        # Simplified maintainability index calculation
        lines = codebase_context.split('\n')
        total_lines = len(lines)
        
        # Factors that improve maintainability
        comment_lines = sum(1 for line in lines if line.strip().startswith(('//', '#', '/*', '*')))
        
        # Factors that decrease maintainability
        long_lines = sum(1 for line in lines if len(line) > 120)
        complex_lines = sum(1 for line in lines if line.count(';') > 1 or line.count('&&') > 2 or line.count('||') > 2)
        
        # Calculate score
        comment_ratio = (comment_lines / max(total_lines, 1)) * 100
        long_line_ratio = (long_lines / max(total_lines, 1)) * 100
        complex_line_ratio = (complex_lines / max(total_lines, 1)) * 100
        
        # Maintainability index formula (simplified)
        mi = 100 - (long_line_ratio * 0.5 + complex_line_ratio * 0.5) + (comment_ratio * 0.3)
        
        return max(0, min(100, round(mi)))


class ArchitecturePatternDetector:
    """Detect architectural and design patterns in codebase"""
    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
    
    def detect_architectural_patterns(self, codebase_context):
        """Detect high-level architectural patterns"""
        patterns = []
        content_lower = codebase_context.lower()
        
        # MVC Pattern
        if all(term in content_lower for term in ['model', 'view', 'controller']):
            patterns.append("**MVC (Model-View-Controller)** - Clear separation of concerns")
        
        # Service-Oriented Architecture
        if 'service' in content_lower and content_lower.count('service') > 5:
            patterns.append("**Service-Oriented Architecture** - Modular service design")
        
        # Component-Based Architecture
        if 'component' in content_lower and content_lower.count('component') > 10:
            patterns.append("**Component-Based Architecture** - Reusable UI components")
        
        # Event-Driven Architecture
        if any(term in content_lower for term in ['event', 'listener', 'emitter', 'subscribe']):
            patterns.append("**Event-Driven Architecture** - Loose coupling through events")
        
        # Layered Architecture
        if any(term in content_lower for term in ['layer', 'tier', 'presentation', 'business', 'data']):
            patterns.append("**Layered Architecture** - Organized in logical layers")
        
        # Repository Pattern
        if 'repository' in content_lower:
            patterns.append("**Repository Pattern** - Data access abstraction")
        
        # Microservices (if multiple service definitions)
        if content_lower.count('service') > 20 and 'api' in content_lower:
            patterns.append("**Microservices Architecture** - Distributed service design")
        
        return patterns if patterns else ["**Monolithic Architecture** - Single unified codebase"]
    
    def analyze_design_patterns(self, codebase_context):
        """Detect common design patterns"""
        patterns = []
        content_lower = codebase_context.lower()
        
        # Factory Pattern
        if 'factory' in content_lower or 'create' in content_lower and 'return new' in content_lower:
            patterns.append("**Factory Pattern** - Object creation abstraction")
        
        # Singleton Pattern
        if 'singleton' in content_lower or 'instance' in content_lower and 'private constructor' in content_lower:
            patterns.append("**Singleton Pattern** - Single instance guarantee")
        
        # Observer Pattern
        if any(term in content_lower for term in ['observer', 'subscribe', 'notify', 'listener']):
            patterns.append("**Observer Pattern** - Event subscription model")
        
        # Decorator Pattern
        if 'decorator' in content_lower or '@' in codebase_context and 'function' in content_lower:
            patterns.append("**Decorator Pattern** - Behavior extension")
        
        # Strategy Pattern
        if 'strategy' in content_lower or 'algorithm' in content_lower:
            patterns.append("**Strategy Pattern** - Algorithm encapsulation")
        
        # Adapter Pattern
        if 'adapter' in content_lower or 'wrapper' in content_lower:
            patterns.append("**Adapter Pattern** - Interface compatibility")
        
        return patterns if patterns else ["**Basic Object-Oriented Design** - Standard OOP principles"]
    
    def analyze_architectural_layers(self, modules):
        """Analyze and categorize modules into architectural layers"""
        layers = {
            'presentation': [],
            'business': [],
            'data': [],
            'infrastructure': [],
            'shared': []
        }
        
        for module_name, module_info in modules.items():
            module_lower = module_name.lower()
            path_lower = module_info.get('path', '').lower()
            
            # Presentation layer
            if any(term in module_lower or term in path_lower for term in 
                   ['component', 'view', 'page', 'ui', 'widget', 'screen', 'layout']):
                layers['presentation'].append(module_name)
            
            # Business layer
            elif any(term in module_lower or term in path_lower for term in 
                     ['service', 'controller', 'handler', 'manager', 'logic', 'processor']):
                layers['business'].append(module_name)
            
            # Data layer
            elif any(term in module_lower or term in path_lower for term in 
                     ['model', 'entity', 'repository', 'dao', 'schema', 'database']):
                layers['data'].append(module_name)
            
            # Infrastructure layer
            elif any(term in module_lower or term in path_lower for term in 
                     ['config', 'util', 'helper', 'middleware', 'adapter', 'provider']):
                layers['infrastructure'].append(module_name)
            
            # Shared layer
            elif any(term in module_lower or term in path_lower for term in 
                     ['common', 'shared', 'core', 'base', 'constants']):
                layers['shared'].append(module_name)
        
        return layers


class DependencyAnalyzer:
    """Analyze dependencies and coupling between modules"""
    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
    
    def analyze_coupling_metrics(self, import_graph):
        """Calculate coupling metrics for the codebase"""
        if not import_graph:
            return {
                'average_dependencies': 0,
                'max_dependencies': 0,
                'coupling_level': 'Low'
            }
        
        # Calculate dependencies per module
        dependency_counts = [len(deps) for deps in import_graph.values()]
        
        avg_deps = sum(dependency_counts) / len(dependency_counts) if dependency_counts else 0
        max_deps = max(dependency_counts) if dependency_counts else 0
        
        # Determine coupling level
        if avg_deps > 10:
            coupling_level = 'High'
        elif avg_deps > 5:
            coupling_level = 'Medium'
        else:
            coupling_level = 'Low'
        
        return {
            'average_dependencies': round(avg_deps, 2),
            'max_dependencies': max_deps,
            'coupling_level': coupling_level
        }
    
    def analyze_circular_dependencies(self, import_graph):
        """Detect circular dependencies in the import graph"""
        circular_deps = []
        visited = set()
        rec_stack = set()
        
        def has_cycle(node, graph, path=[]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            if node in graph:
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        if has_cycle(neighbor, graph, path):
                            return True
                    elif neighbor in rec_stack:
                        # Found cycle
                        cycle_start = path.index(neighbor)
                        cycle = path[cycle_start:] + [neighbor]
                        circular_deps.append(cycle)
                        return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        # Check each node
        for node in import_graph:
            if node not in visited:
                has_cycle(node, import_graph)
        
        return circular_deps
    
    def calculate_instability_metrics(self, modules, import_graph):
        """Calculate instability metrics (I = Ce / (Ca + Ce))"""
        metrics = {}
        
        # Calculate afferent coupling (Ca) - modules that depend on this module
        afferent = {module: 0 for module in modules}
        for module, deps in import_graph.items():
            for dep in deps:
                if dep in afferent:
                    afferent[dep] += 1
        
        # Calculate efferent coupling (Ce) - modules this module depends on
        efferent = {module: len(deps) for module, deps in import_graph.items()}
        
        # Calculate instability
        for module in modules:
            ca = afferent.get(module, 0)
            ce = efferent.get(module, 0)
            
            if ca + ce > 0:
                instability = ce / (ca + ce)
            else:
                instability = 0
            
            metrics[module] = {
                'afferent_coupling': ca,
                'efferent_coupling': ce,
                'instability': round(instability, 2)
            }
        
        return metrics


class CodebaseHealthAnalyzer:
    """Analyze overall codebase health and quality"""
    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
        self.metrics_analyzer = ArchitectureMetrics(framework_detector)
        self.pattern_detector = ArchitecturePatternDetector(framework_detector)
        self.dependency_analyzer = DependencyAnalyzer(framework_detector)
    
    def generate_health_report(self, codebase_context, index_data):
        """Generate comprehensive health report"""
        # Calculate various metrics
        complexity = self.metrics_analyzer.calculate_complexity_metrics(codebase_context)
        maintainability = self.metrics_analyzer.calculate_maintainability_index(codebase_context)
        coupling = self.dependency_analyzer.analyze_coupling_metrics(index_data.get('import_graph', {}))
        circular_deps = self.dependency_analyzer.analyze_circular_dependencies(index_data.get('import_graph', {}))
        
        # Calculate health score
        health_score = self._calculate_health_score(
            complexity, maintainability, coupling, circular_deps, codebase_context
        )
        
        # Detect patterns
        arch_patterns = self.pattern_detector.detect_architectural_patterns(codebase_context)
        
        return f"""## 🏥 **Codebase Health Report**

### **Overall Health Score: {health_score}/100**

### 📊 **Complexity Metrics**
- **Total Files**: {index_data['stats']['total_files']}
- **Total Lines**: {index_data['stats']['total_lines']:,}
- **Average Lines per File**: {round(index_data['stats']['total_lines'] / max(index_data['stats']['total_files'], 1), 2)}
- **Cyclomatic Complexity**: {complexity['cyclomatic_complexity']}
- **Maintainability Index**: {maintainability}/100

### ✅ **Quality Indicators**
{self._generate_quality_indicators(codebase_context, index_data)}

### 🔗 **Coupling Analysis**
- **Average Dependencies**: {coupling['average_dependencies']}
- **Max Dependencies**: {coupling['max_dependencies']}
- **Coupling Level**: {coupling['coupling_level']}
- **Circular Dependencies**: {len(circular_deps)}

### 🏗️ **Architectural Patterns**
{chr(10).join(f'- {pattern}' for pattern in arch_patterns[:5])}

### 💡 **Recommendations**
{self._generate_health_recommendations(health_score, complexity, coupling, circular_deps)}"""
    
    def _calculate_health_score(self, complexity, maintainability, coupling, circular_deps, codebase_context):
        """Calculate overall health score"""
        score = 100
        
        # Complexity impact
        if complexity['cyclomatic_complexity'] > 10:
            score -= 10
        elif complexity['cyclomatic_complexity'] > 5:
            score -= 5
        
        # Maintainability impact
        if maintainability < 50:
            score -= 10
        elif maintainability < 70:
            score -= 5
        
        # Coupling impact
        if coupling['coupling_level'] == 'High':
            score -= 10
        elif coupling['coupling_level'] == 'Medium':
            score -= 5
        
        # Circular dependencies impact
        if len(circular_deps) > 0:
            score -= min(len(circular_deps) * 2, 10)
        
        # Test coverage impact
        if 'test' not in codebase_context.lower():
            score -= 10
        
        return max(0, min(100, score))
    
    def _generate_quality_indicators(self, codebase_context, index_data):
        """Generate quality indicator checklist"""
        indicators = []
        content_lower = codebase_context.lower()
        
        # Check for tests
        has_tests = 'test' in content_lower or 'spec' in content_lower
        indicators.append(f"- **Has Tests**: {'✅ Yes' if has_tests else '❌ No'}")
        
        # Check for documentation
        has_docs = any(marker in codebase_context for marker in ['/**', '"""', '///'])
        indicators.append(f"- **Has Documentation**: {'✅ Yes' if has_docs else '❌ No'}")
        
        # Check for error handling
        has_error_handling = 'try' in content_lower or 'catch' in content_lower or 'error' in content_lower
        indicators.append(f"- **Has Error Handling**: {'✅ Yes' if has_error_handling else '❌ No'}")
        
        # Check for TypeScript
        uses_typescript = '.ts' in content_lower or '.tsx' in content_lower
        indicators.append(f"- **Uses TypeScript**: {'✅ Yes' if uses_typescript else '❌ No'}")
        
        # Estimate test coverage
        if has_tests:
            test_files = [m for m in index_data.get('modules', {}) if 'test' in m.lower() or 'spec' in m.lower()]
            test_coverage = round(len(test_files) / max(len(index_data.get('modules', {})), 1) * 100)
        else:
            test_coverage = 0
        indicators.append(f"- **Estimated Test Coverage**: {test_coverage}%")
        
        # Calculate quality score
        quality_score = 70  # Base score
        if has_tests: quality_score += 10
        if has_docs: quality_score += 10
        if has_error_handling: quality_score += 5
        if uses_typescript: quality_score += 5
        
        indicators.append(f"- **Quality Score**: {min(100, quality_score)}/100")
        
        return '\n'.join(indicators)
    
    def _generate_health_recommendations(self, health_score, complexity, coupling, circular_deps):
        """Generate health improvement recommendations"""
        recommendations = []
        
        if health_score < 70:
            recommendations.append("- **Priority**: Address critical issues to improve codebase health")
        
        if complexity['cyclomatic_complexity'] > 10:
            recommendations.append("- **Reduce Complexity**: Refactor complex functions into smaller units")
        
        if coupling['coupling_level'] == 'High':
            recommendations.append("- **Reduce Coupling**: Introduce interfaces and dependency injection")
        
        if len(circular_deps) > 0:
            recommendations.append("- **Fix Circular Dependencies**: Refactor to break dependency cycles")
        
        if not recommendations:
            recommendations.append("- **Good Health**: Continue following current practices")
        
        # Always add test coverage recommendation if low
        recommendations.append("- **Increase Test Coverage**: Current coverage is below 50%")
        
        return '\n'.join(recommendations[:5])  # Limit to top 5 recommendations


class ArchitectureDocumentationGenerator:
    """Generate architecture diagrams and documentation"""
    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
    
    def generate_architecture_diagram(self, architecture):
        """Generate ASCII architecture diagram"""
        layers = architecture.get('layers', {})
        
        # Count components in each layer
        presentation_count = len(layers.get('presentation', []))
        business_count = len(layers.get('business', []))
        data_count = len(layers.get('data', []))
        infra_count = len(layers.get('infrastructure', []))
        
        return f"""```
┌───────────────────────────────────────────────────────────────────────────┐
│                    Presentation Layer                                     │
│  Components: {presentation_count:<4} │ Pages │ Views │ UI Elements        │
├───────────────────────────────────────────────────────────────────────────┤
│                     Business Layer                                        │
│  Services: {business_count:<6} │ Logic │ Domain │ Controllers             │
├───────────────────────────────────────────────────────────────────────────┤
│                       Data Layer                                          │
│  Models: {data_count:<8} │ Repositories │ Entities │ DAOs                 │
├───────────────────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                                     │
│  Config: {infra_count:<8} │ Utils │ Helpers │ Middleware                  │
└───────────────────────────────────────────────────────────────────────────┘
```"""
    
    def generate_module_relationship_diagram(self, import_graph):
        """Generate module relationship diagram"""
        if not import_graph:
            return "```\nNo module relationships detected\n```"
        
        # Find top modules by import count
        import_counts = {}
        for module, imports in import_graph.items():
            import_counts[module] = len(imports)
        
        top_modules = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        diagram_lines = ["```", "Top Module Dependencies:", ""]
        for module, count in top_modules:
            bar = "─" * min(count, 40)
            diagram_lines.append(f"{module:<30} ──→ {count} dependencies")
        diagram_lines.append("```")
        
        return '\n'.join(diagram_lines)
    
    def generate_component_diagram(self, modules, framework):
        """Generate component relationship diagram"""
        # This would generate more detailed component diagrams
        # For now, returning a placeholder
        return "Component diagram generation not implemented yet"