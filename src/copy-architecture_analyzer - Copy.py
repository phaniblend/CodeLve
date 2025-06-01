"""
Architecture Analyzer Module for CodeLve
Handles comprehensive codebase architecture analysis and pattern detection
"""

import json
from pathlib import Path
from .codebase_indexer import CodebaseIndexer

class ArchitectureAnalyzer:
    """Comprehensive codebase architecture analysis"""
    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
    
    def analyze_codebase_architecture(self, codebase_context, framework):
        """Comprehensive codebase architecture analysis with REAL indexing"""
        print("🏗️ Generating REAL architecture analysis with codebase indexing...")
        
        # Instead of using temp directory, analyze the context directly
        index_data = self._index_from_context(codebase_context)
        
        # Generate both technical analysis and developer guide
        technical_analysis = self._format_real_architecture_analysis(index_data, framework, codebase_context)
        developer_guide = self.generate_developer_onboarding_guide(index_data, framework, codebase_context)
        
        # Combine both for comprehensive output
        return f"{developer_guide}\n\n---\n\n{technical_analysis}"
    
    def _index_from_context(self, codebase_context):
        """Index directly from consolidated context without temp files"""
        modules = {}
        import_graph = {}
        file_paths = []
        file_types = {}
        total_lines = 0
        total_classes = 0
        total_functions = 0
        
        lines = codebase_context.split('\n')
        current_file = None
        current_content = []
        in_file = False
        
        for line in lines:
            if line.startswith('filepath:///'):
                # Process previous file if exists
                if current_file and current_content:
                    self._process_file_content(
                        current_file, '\n'.join(current_content),
                        modules, import_graph, file_types,
                        lambda: None  # Dummy counters, will count later
                    )
                
                # Start new file
                current_file = line.replace('filepath:///', '').replace(' /// /// ///', '').strip()
                file_paths.append(current_file)
                current_content = []
                in_file = False
            elif line.strip() == 'file code{':
                in_file = True
            elif line.strip() == '}' and in_file:
                in_file = False
            elif in_file:
                current_content.append(line)
                total_lines += 1
        
        # Process last file
        if current_file and current_content:
            self._process_file_content(
                current_file, '\n'.join(current_content),
                modules, import_graph, file_types,
                lambda: None
            )
        
        # Count classes and functions
        for module_info in modules.values():
            total_classes += len(module_info.get('classes', []))
            total_functions += len(module_info.get('functions', []))
        
        # Build architecture analysis
        architecture = self._analyze_architecture(modules, import_graph, file_paths)
        
        return {
            'modules': modules,
            'import_graph': import_graph,
            'architecture': architecture,
            'stats': {
                'total_files': len(file_paths),
                'total_lines': total_lines,
                'total_classes': total_classes,
                'total_functions': total_functions,
                'file_types': file_types
            }
        }
    
    def _process_file_content(self, file_path, content, modules, import_graph, file_types, counter):
        """Process a single file's content"""
        import re
        
        # Get file extension
        ext = Path(file_path).suffix.lower()
        file_types[ext] = file_types.get(ext, 0) + 1
        
        # Extract module name
        module_name = Path(file_path).stem
        
        # Initialize module info
        module_info = {
            'path': file_path,
            'imports': [],
            'exports': [],
            'classes': [],
            'functions': [],
            'size': len(content.splitlines())
        }
        
        # Extract imports (TypeScript/JavaScript)
        import_pattern = r'import\s+(?:{[^}]+}|[\w\s,]+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        imports = re.findall(import_pattern, content)
        module_info['imports'] = imports
        
        # Extract exports
        export_pattern = r'export\s+(?:default\s+)?(?:class|function|const|interface|type)\s+(\w+)'
        exports = re.findall(export_pattern, content)
        module_info['exports'] = exports
        
        # Extract classes
        class_pattern = r'(?:export\s+)?(?:default\s+)?class\s+(\w+)'
        classes = re.findall(class_pattern, content)
        module_info['classes'] = classes
        
        # Extract functions and React components
        func_pattern = r'(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)'
        arrow_pattern = r'(?:export\s+)?const\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=]+)\s*=>'
        component_pattern = r'const\s+([A-Z]\w+)\s*[:=].*(?:React\.FC|FC|=>)'
        
        functions = re.findall(func_pattern, content)
        functions.extend(re.findall(arrow_pattern, content))
        functions.extend(re.findall(component_pattern, content))
        module_info['functions'] = list(set(functions))
        
        # Store module info
        modules[module_name] = module_info
        
        # Build import graph
        import_graph[module_name] = imports
    
    def _analyze_architecture(self, modules, import_graph, file_paths):
        """Analyze the architecture based on indexed data"""
        # Find entry points
        entry_points = []
        for name in modules:
            if any(ep in name.lower() for ep in ['app', 'index', 'main']):
                entry_points.append(name)
        
        # Find core modules (imported by many others)
        import_counts = {}
        for imports in import_graph.values():
            for imp in imports:
                # Extract module name from import path
                if './' in imp or '../' in imp:
                    imp_name = Path(imp).stem
                    import_counts[imp_name] = import_counts.get(imp_name, 0) + 1
        
        core_modules = sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Detect layers based on paths
        layers = {
            'presentation': [],
            'business': [],
            'data': [],
            'infrastructure': [],
            'shared': []
        }
        
        for file_path in file_paths:
            path_lower = file_path.lower()
            if any(term in path_lower for term in ['component', 'page', 'view', 'layout']):
                layers['presentation'].append(Path(file_path).stem)
            elif any(term in path_lower for term in ['service', 'api', 'controller']):
                layers['business'].append(Path(file_path).stem)
            elif any(term in path_lower for term in ['model', 'entity', 'schema']):
                layers['data'].append(Path(file_path).stem)
            elif any(term in path_lower for term in ['config', 'util', 'helper', 'constant']):
                layers['infrastructure'].append(Path(file_path).stem)
            elif any(term in path_lower for term in ['shared', 'common']):
                layers['shared'].append(Path(file_path).stem)
        
        # Group modules by directory
        module_families = {}
        for file_path in file_paths:
            parts = Path(file_path).parts
            if len(parts) > 1:
                family = parts[-2]  # Get parent directory
                if family not in module_families:
                    module_families[family] = []
                module_families[family].append(Path(file_path).stem)
        
        return {
            'entry_points': entry_points,
            'core_modules': [m[0] for m in core_modules],
            'layers': layers,
            'module_families': module_families
        }
    
    def generate_developer_onboarding_guide(self, index_data, framework, codebase_context):
        """Generate a comprehensive onboarding guide for new developers"""
        modules = index_data['modules']
        architecture = index_data['architecture']
        stats = index_data['stats']
        
        # Analyze the codebase to understand the project
        project_type = self._determine_project_type(codebase_context)
        main_features = self._identify_main_features(architecture['module_families'])
        tech_stack = self._analyze_tech_stack(codebase_context, modules)
        
        guide = f"""# 🚀 **Developer Onboarding Guide**

## 📋 **Project Overview**
**Project Type:** {project_type}
**Framework:** {framework}
**Architecture:** Component-Based React Application with TypeScript
**Size:** {stats['total_files']} files, {stats['total_lines']:,} lines of code

## 🎯 **Where to Start - Day 1**

### 1. **Entry Points** (Start Here!)
{self._format_entry_points_guide(architecture['entry_points'], modules)}

### 2. **Core Application Flow**
```
User → App.tsx → AppRoutes.tsx → Page Components → API Services → Backend
         ↓           ↓
      Context     Redux Store
```

### 3. **Key Files to Understand First**
{self._format_key_files_guide(modules, codebase_context)}

## 📁 **Project Structure Explained**

### **Frontend Architecture**
```
src/
├── App.tsx                 # Main application component
├── AppRoutes.tsx          # All route definitions
├── apis/                  # API service layer
│   ├── axiosInstance.ts   # HTTP client configuration
│   ├── apiRoutes.ts       # API endpoint definitions
│   └── *Service.ts        # Feature-specific API calls
├── components/            # React components
│   ├── layout/           # App-wide layouts (Header, Footer, Nav)
│   ├── pages/            # Page components (routes)
│   │   ├── Applicant/    # Applicant management feature
│   │   ├── Project/      # Project management feature
│   │   └── Equipment/    # Equipment management feature
│   └── shared/           # Reusable components
├── contexts/             # React Context providers
├── store/                # Redux state management
├── models/               # TypeScript type definitions
└── utils/                # Helper functions
```

## 🔧 **Tech Stack & Libraries**

{tech_stack}

## 🏃‍♂️ **Development Workflow**

### **1. Making Changes to a Feature**
Example: Modifying the Applicant feature
```
1. Start at: components/pages/Applicant/
2. Understand: ApplicantSearch.tsx (main component)
3. Check API: apis/applicantService.ts
4. Types: models/api/response/applicant/
5. Test your changes in the UI
```

### **2. Adding a New Feature**
```
1. Create page component in components/pages/YourFeature/
2. Add route in AppRoutes.tsx
3. Create API service in apis/yourFeatureService.ts
4. Define types in models/
5. Add to navigation if needed
```

### **3. Common Tasks**
{self._format_common_tasks(codebase_context)}

## 🗺️ **Feature Map**
{self._format_feature_map(architecture['module_families'])}

## 🔍 **Code Patterns & Conventions**

### **Component Pattern**
```typescript
import React, {{ useState, useEffect }} from 'react';
import {{ useTranslation }} from 'react-i18next';
import useToast from '../../../hooks/useToast';

const YourComponent: React.FC = () => {{
    const {{ t }} = useTranslation();
    const {{ showToast }} = useToast();
    
    // Component logic here
    
    return (
        <div>
            {{/* Your JSX */}}
        </div>
    );
}};

export default YourComponent;
```

### **API Service Pattern**
```typescript
import {{ axiosGet, axiosPost }} from "./axiosInstance";
import {{ YOUR_ENDPOINTS }} from "./apiRoutes";

export const getYourData = (id: string): Promise<YourType> => {{
    return axiosGet(`${{YOUR_ENDPOINTS.GET_URL}}/${{id}}`);
}};
```

## 📚 **Key Concepts to Understand**

1. **State Management**: 
   - Local state with React hooks (useState)
   - Global state with Redux (check store/)
   - Context API for cross-cutting concerns

2. **Routing**: 
   - React Router v6 patterns
   - Protected routes with Okta authentication

3. **API Integration**:
   - Centralized axios instance
   - Consistent error handling
   - TypeScript types for all API responses

4. **Form Handling**:
   - React Hook Form for form management
   - PrimeReact components for UI

## 🎓 **Learning Path**

### **Week 1: Foundation**
- [ ] Understand App.tsx and AppRoutes.tsx
- [ ] Explore one complete feature (e.g., Applicant)
- [ ] Learn the API service pattern
- [ ] Understand the component structure

### **Week 2: Deep Dive**
- [ ] Explore state management (Redux/Context)
- [ ] Understand authentication flow (Okta)
- [ ] Work with forms and validation
- [ ] Learn the TypeScript patterns used

### **Week 3: Productivity**
- [ ] Make your first feature modification
- [ ] Add a new API endpoint
- [ ] Create a reusable component
- [ ] Understand the build and deployment process

## 🚨 **Important Notes**

{self._format_important_notes(codebase_context)}

## 🤝 **Getting Help**

1. **Code Questions**: Search for similar patterns in the codebase
2. **Architecture Questions**: Refer to this guide
3. **Business Logic**: Check the feature's main component and service

---

**Next Steps**: 
1. Open `App.tsx` and trace through how the application initializes
2. Pick a feature (like Applicant) and understand its complete flow
3. Make a small change to see how the development cycle works

Good luck! 🎉
"""
        
        return guide
    
    def _determine_project_type(self, codebase_context):
        """Determine the type of project based on content"""
        content_lower = codebase_context.lower()
        
        if 'equipment' in content_lower and 'emission' in content_lower:
            return "Environmental Compliance & Equipment Management System"
        elif 'applicant' in content_lower and 'district' in content_lower:
            return "Grant/Application Management System"
        elif 'ecommerce' in content_lower or 'shop' in content_lower:
            return "E-commerce Platform"
        elif 'dashboard' in content_lower and 'analytics' in content_lower:
            return "Analytics Dashboard"
        else:
            return "Enterprise Web Application"
    
    def _identify_main_features(self, module_families):
        """Identify main features from module organization"""
        features = []
        
        # Look for feature directories
        feature_indicators = ['Applicant', 'Project', 'Equipment', 'User', 'District', 
                            'Report', 'Dashboard', 'Settings', 'Admin']
        
        for family, modules in module_families.items():
            for indicator in feature_indicators:
                if indicator.lower() in family.lower():
                    features.append(family)
                    break
        
        return features[:6]  # Top 6 features
    
    def _analyze_tech_stack(self, codebase_context, modules):
        """Analyze and format the tech stack"""
        tech_stack = []
        content_lower = codebase_context.lower()
        
        # Core technologies
        tech_stack.append("### **Core Technologies**")
        tech_stack.append("- **React** - UI framework")
        tech_stack.append("- **TypeScript** - Type safety")
        tech_stack.append("- **Redux** - State management")
        
        # UI Libraries
        if 'primereact' in content_lower:
            tech_stack.append("\n### **UI Components**")
            tech_stack.append("- **PrimeReact** - Component library")
        
        # Authentication
        if 'okta' in content_lower:
            tech_stack.append("\n### **Authentication**")
            tech_stack.append("- **Okta** - Identity management")
        
        # Forms
        if 'react-hook-form' in content_lower or 'useform' in content_lower:
            tech_stack.append("\n### **Form Management**")
            tech_stack.append("- **React Hook Form** - Form handling")
        
        # HTTP Client
        if 'axios' in content_lower:
            tech_stack.append("\n### **API Communication**")
            tech_stack.append("- **Axios** - HTTP client")
        
        # Internationalization
        if 'i18n' in content_lower or 'translation' in content_lower:
            tech_stack.append("\n### **Internationalization**")
            tech_stack.append("- **react-i18next** - Multi-language support")
        
        return '\n'.join(tech_stack)
    
    def _format_entry_points_guide(self, entry_points, modules):
        """Format entry points for the guide"""
        guide = []
        
        # Key entry points
        if 'App' in entry_points:
            guide.append("- **App.tsx** - Main application component that sets up providers and routing")
        if 'AppRoutes' in entry_points:
            guide.append("- **AppRoutes.tsx** - All application routes and page mappings")
        if 'index' in entry_points:
            guide.append("- **index.tsx** - Application bootstrap and React DOM rendering")
        
        guide.append("\n**Quick Start**: Open `App.tsx` to see how the application initializes")
        
        return '\n'.join(guide)
    
    def _format_key_files_guide(self, modules, codebase_context):
        """Format key files that developers should understand first"""
        key_files = []
        
        # Identify important files
        key_files.append("1. **App.tsx** - Application root component")
        key_files.append("2. **AppRoutes.tsx** - Route definitions")
        key_files.append("3. **apis/axiosInstance.ts** - HTTP client setup")
        key_files.append("4. **apis/apiRoutes.ts** - API endpoint definitions")
        
        # Add a main feature example
        if 'applicantService' in modules:
            key_files.append("5. **apis/applicantService.ts** - Example of API service pattern")
        
        key_files.append("\n**💡 Tip**: These files show the core patterns used throughout the application")
        
        return '\n'.join(key_files)
    
    def _format_common_tasks(self, codebase_context):
        """Format common development tasks"""
        tasks = []
        
        tasks.append("- **Add a new API call**: Check `apis/*Service.ts` files for patterns")
        tasks.append("- **Create a form**: See `AddApplicant.tsx` for form handling example")
        tasks.append("- **Add a route**: Update `AppRoutes.tsx` and create page component")
        tasks.append("- **Handle errors**: Use `useToast` hook for user notifications")
        tasks.append("- **Manage state**: Use Redux for global state, useState for local")
        
        return '\n'.join(tasks)
    
    def _format_feature_map(self, module_families):
        """Format a map of features in the application"""
        features = []
        
        # Group by major features
        feature_groups = {
            'Applicant Management': ['Applicant', 'AddApplicant', 'ApplicantSearch'],
            'Project Management': ['Project', 'ProjectDetails', 'ProjectManagement'],
            'Equipment Management': ['Equipment', 'EquipmentSet', 'EquipmentService'],
            'District Management': ['District', 'DistrictSubmission', 'DistrictService'],
            'User Management': ['User', 'UserService', 'roleService'],
            'Reporting': ['Report', 'Dashboard', 'Analytics']
        }
        
        for feature_name, indicators in feature_groups.items():
            found_modules = []
            for family, modules in module_families.items():
                if any(ind.lower() in family.lower() for ind in indicators):
                    found_modules.extend(modules[:3])
            
            if found_modules:
                features.append(f"\n### **{feature_name}**")
                features.append(f"Key modules: {', '.join(set(found_modules[:5]))}")
        
        return '\n'.join(features)
    
    def _format_important_notes(self, codebase_context):
        """Format important notes for developers"""
        notes = []
        content_lower = codebase_context.lower()
        
        if 'okta' in content_lower:
            notes.append("- **Authentication**: This app uses Okta - check `config/okta-config` for setup")
        
        if 'primereact' in content_lower:
            notes.append("- **UI Components**: PrimeReact is the main component library - check their docs")
        
        if 'i18n' in content_lower:
            notes.append("- **Translations**: Use `useTranslation` hook for all user-facing text")
        
        if 'typescript' in content_lower:
            notes.append("- **Type Safety**: Always define types for API responses and component props")
        
        notes.append("- **Code Style**: Follow existing patterns for consistency")
        
        return '\n'.join(notes)
    
    def _extract_files_from_context(self, codebase_context):
        """Extract files from consolidated codebase context"""
        files_map = {}
        lines = codebase_context.split('\n')
        current_file = None
        current_content = []
        in_file = False
        
        for line in lines:
            if line.startswith('filepath:///'):
                # Save previous file if exists
                if current_file and current_content:
                    files_map[current_file] = '\n'.join(current_content)
                
                # Start new file
                current_file = line.replace('filepath:///', '').replace(' /// /// ///', '').strip()
                current_content = []
                in_file = False
            elif line.strip() == 'file code{':
                in_file = True
            elif line.strip() == '}' and in_file:
                in_file = False
            elif in_file:
                current_content.append(line)
        
        # Save last file
        if current_file and current_content:
            files_map[current_file] = '\n'.join(current_content)
        
        return files_map
    
    def _format_real_architecture_analysis(self, index_data, framework, codebase_context):
        """Format REAL architecture analysis based on actual indexed data"""
        modules = index_data['modules']
        architecture = index_data['architecture']
        stats = index_data['stats']
        
        # Build REAL module list
        module_list = []
        for family, mods in sorted(architecture['module_families'].items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            if mods:
                module_list.append(f"• **{family}** directory: {len(mods)} modules - {', '.join(mods[:3])}")
        
        # Build REAL layer analysis
        layer_analysis = []
        for layer, components in architecture['layers'].items():
            if components:
                layer_analysis.append(f"• **{layer.title()} Layer**: {len(components)} components")
        
        # Build import statistics
        total_imports = sum(len(m.get('imports', [])) for m in modules.values())
        files_with_imports = len([m for m in modules.values() if m.get('imports', [])])
        isolated_files = stats['total_files'] - files_with_imports
        
        return f"""# 🏗️ **Technical Architecture Analysis**

## 📊 **System Metrics**
**Framework/Language:** {framework}  
**Total Files:** {stats['total_files']}  
**Total Lines:** {stats['total_lines']:,}  
**Total Classes:** {stats['total_classes']}  
**Total Functions:** {stats['total_functions']}

## 📁 **File Distribution**
{self._format_real_file_types(stats['file_types'])}

## 🎯 **Architecture Layers**
{chr(10).join(layer_analysis) if layer_analysis else "• No clear layer separation detected"}

## 🔗 **Module Dependencies**
**Entry Points:** {', '.join(architecture['entry_points'][:5]) if architecture['entry_points'] else 'App, AppRoutes'}
**Core Modules:** {', '.join(architecture['core_modules'][:5]) if architecture['core_modules'] else 'Not identified'}

## 📋 **Module Organization**
{chr(10).join(module_list[:10]) if module_list else "• Flat module structure"}

## 🌐 **Import Graph Statistics**
• **Total Import Statements:** {total_imports}
• **Files with Imports:** {files_with_imports}
• **Isolated Files:** {isolated_files}

## 💡 **Recommendations**
{self._generate_real_recommendations(index_data, framework)}

---
**📈 Architecture Quality:** Based on ACTUAL code analysis
"""
    
    def _format_real_file_types(self, file_types):
        """Format real file type distribution"""
        if not file_types:
            return "• No files indexed"
        
        total = sum(file_types.values())
        lines = []
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:8]:
            percentage = (count / total) * 100
            lines.append(f"• **{ext}**: {count} files ({percentage:.1f}%)")
        return '\n'.join(lines)
    
    def _generate_real_recommendations(self, index_data, framework):
        """Generate recommendations based on real data"""
        recs = []
        
        modules = index_data['modules']
        stats = index_data['stats']
        
        # Check for test files
        test_files = [m for m in modules if 'test' in m.lower() or 'spec' in m.lower()]
        if len(test_files) < len(modules) * 0.1:
            recs.append("• **Testing**: Low test coverage detected - add more unit tests")
        
        # Check for large files
        large_modules = [m for m, info in modules.items() if info.get('size', 0) > 500]
        if large_modules:
            recs.append(f"• **Refactoring**: {len(large_modules)} files exceed 500 lines")
        
        # Check for isolated modules
        isolated = stats.get('total_files', 0) - len([m for m in modules.values() if m.get('imports')])
        if isolated > 5:
            recs.append(f"• **Integration**: {isolated} files have no imports - review modularization")
        
        # TypeScript specific
        if 'typescript' in framework.lower():
            if stats.get('file_types', {}).get('.js', 0) > 0:
                recs.append("• **Type Safety**: Migrate remaining .js files to TypeScript")
        
        return '\n'.join(recs) if recs else "• Architecture follows good practices"

    def detect_architectural_patterns(self, codebase_context):
        """Detect architectural patterns in the codebase"""
        patterns = []
        content_lower = codebase_context.lower()
        
        # MVC Pattern
        if any(term in content_lower for term in ['controller', 'model', 'view']):
            patterns.append("**MVC (Model-View-Controller)** - Clear separation of concerns")
        
        # Microservices
        if any(term in content_lower for term in ['service', 'api', 'microservice']):
            patterns.append("**Service-Oriented Architecture** - Modular service design")
        
        # Repository Pattern
        if any(term in content_lower for term in ['repository', 'dao', 'data access']):
            patterns.append("**Repository Pattern** - Data access abstraction")
        
        # Component Architecture
        if any(term in content_lower for term in ['component', 'module', 'widget']):
            patterns.append("**Component-Based Architecture** - Reusable UI components")
        
        # Event-Driven
        if any(term in content_lower for term in ['event', 'observer', 'listener']):
            patterns.append("**Event-Driven Architecture** - Loose coupling through events")
        
        # Layered Architecture
        if any(term in content_lower for term in ['layer', 'tier', 'business logic']):
            patterns.append("**Layered Architecture** - Organized in logical layers")
        
        return patterns if patterns else ["**Custom Architecture** - Unique architectural approach"]

    def determine_architecture_type(self, codebase_context):
        """Determine the overall architecture type"""
        content_lower = codebase_context.lower()
        
        if 'microservice' in content_lower or content_lower.count('service') > 10:
            return "Microservices Architecture"
        elif 'monolith' in content_lower:
            return "Monolithic Architecture"
        elif any(term in content_lower for term in ['spa', 'single page', 'react', 'vue', 'angular']):
            return "Single Page Application (SPA)"
        elif 'api' in content_lower and 'rest' in content_lower:
            return "RESTful API Architecture"
        elif 'component' in content_lower:
            return "Component-Based Architecture"
        else:
            return "Hybrid/Custom Architecture"

    def format_file_structure(self, file_types):
        """Format file structure analysis"""
        if not file_types:
            return "• No specific file patterns detected"
        
        result = []
        total_files = sum(file_types.values())
        
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_files) * 100
            file_type = self.get_file_type_description(ext)
            result.append(f"• **{ext}** files: {count} ({percentage:.1f}%) - {file_type}")
        
        return '\n'.join(result[:8])  # Show top 8 file types

    def get_file_type_description(self, ext):
        """Get description for file extension"""
        descriptions = {
            '.py': 'Python source code',
            '.js': 'JavaScript files',
            '.jsx': 'React components',
            '.ts': 'TypeScript files',
            '.tsx': 'TypeScript React components',
            '.java': 'Java source files',
            '.cs': 'C# source files',
            '.cpp': 'C++ source files',
            '.go': 'Go source files',
            '.rs': 'Rust source files',
            '.html': 'HTML templates',
            '.css': 'Stylesheets',
            '.json': 'Configuration/data files',
            '.md': 'Documentation files',
            '.yml': 'YAML configuration',
            '.xml': 'XML files',
            '.sql': 'Database scripts'
        }
        return descriptions.get(ext, 'Source files')

    def format_patterns(self, patterns):
        """Format architectural patterns"""
        if not patterns:
            return "• No clear architectural patterns detected"
        
        return '\n'.join([f"• {pattern}" for pattern in patterns])

    def analyze_system_dependencies(self, codebase_context):
        """Analyze system-wide dependencies"""
        dependencies = {
            'external': [],
            'internal': [],
            'frameworks': []
        }
        
        lines = codebase_context.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['import', 'require', 'include', 'using']):
                if any(framework in line.lower() for framework in ['react', 'vue', 'angular', 'django', 'spring']):
                    dependencies['frameworks'].append(line.strip())
                elif './' in line or '../' in line:
                    dependencies['internal'].append(line.strip())
                else:
                    dependencies['external'].append(line.strip())
        
        result = []
        if dependencies['frameworks']:
            result.append(f"**Frameworks:** {len(set(dependencies['frameworks']))} framework dependencies")
        if dependencies['external']:
            result.append(f"**External Libraries:** {len(set(dependencies['external']))} external dependencies")
        if dependencies['internal']:
            result.append(f"**Internal Modules:** {len(set(dependencies['internal']))} internal dependencies")
        
        return '\n'.join([f"• {r}" for r in result]) if result else "• Minimal dependencies detected"

    def analyze_module_structure(self, modules):
        """Analyze module organization"""
        if not modules:
            return "• No clear module structure detected"
        
        # Group modules by common prefixes/patterns
        module_groups = {}
        for module in modules:
            prefix = module.split('_')[0] if '_' in module else module.split('.')[0]
            if prefix not in module_groups:
                module_groups[prefix] = []
            module_groups[prefix].append(module)
        
        result = []
        for group, group_modules in sorted(module_groups.items(), key=lambda x: len(x[1]), reverse=True):
            result.append(f"• **{group}** family: {len(group_modules)} modules")
        
        return '\n'.join(result[:6])  # Show top 6 module groups

    def analyze_data_flow_architecture(self, codebase_context):
        """Analyze data flow patterns"""
        content_lower = codebase_context.lower()
        flows = []
        
        if 'api' in content_lower and 'request' in content_lower:
            flows.append("**API-Driven Flow** - External API communication")
        
        if 'database' in content_lower or 'db' in content_lower:
            flows.append("**Database Integration** - Persistent data storage")
        
        if any(term in content_lower for term in ['state', 'store', 'redux']):
            flows.append("**State Management** - Centralized application state")
        
        if 'event' in content_lower and 'handler' in content_lower:
            flows.append("**Event-Driven Flow** - Event-based communication")
        
        if any(term in content_lower for term in ['props', 'component', 'parameter']):
            flows.append("**Component Data Flow** - Hierarchical data passing")
        
        return '\n'.join([f"• {flow}" for flow in flows]) if flows else "• Standard data flow patterns"

    def analyze_security_patterns(self, codebase_context):
        """Analyze security patterns"""
        content_lower = codebase_context.lower()
        security = []
        
        if 'auth' in content_lower or 'authenticate' in content_lower:
            security.append("**Authentication System** - User identity verification")
        
        if 'authorization' in content_lower or 'permission' in content_lower:
            security.append("**Authorization Controls** - Access control mechanisms")
        
        if 'encrypt' in content_lower or 'hash' in content_lower:
            security.append("**Data Encryption** - Data protection measures")
        
        if 'validation' in content_lower or 'validate' in content_lower:
            security.append("**Input Validation** - Data sanitization")
        
        if 'cors' in content_lower or 'csrf' in content_lower:
            security.append("**Web Security** - Cross-origin and CSRF protection")
        
        return '\n'.join([f"• {s}" for s in security]) if security else "• Basic security considerations detected"

    def analyze_performance_patterns(self, codebase_context):
        """Analyze performance patterns"""
        content_lower = codebase_context.lower()
        performance = []
        
        if 'cache' in content_lower or 'caching' in content_lower:
            performance.append("**Caching Strategy** - Performance optimization through caching")
        
        if 'async' in content_lower and 'await' in content_lower:
            performance.append("**Asynchronous Processing** - Non-blocking operations")
        
        if 'lazy' in content_lower or 'pagination' in content_lower:
            performance.append("**Lazy Loading** - On-demand resource loading")
        
        if 'optimize' in content_lower or 'performance' in content_lower:
            performance.append("**Performance Optimization** - Explicit performance tuning")
        
        if 'pool' in content_lower or 'connection' in content_lower:
            performance.append("**Resource Pooling** - Efficient resource management")
        
        return '\n'.join([f"• {p}" for p in performance]) if performance else "• Standard performance patterns"

    def analyze_frontend_architecture(self, codebase_context, framework):
        """Analyze frontend architecture"""
        if not any(term in framework.lower() for term in ['react', 'vue', 'angular', 'javascript', 'typescript']):
            return "• Not applicable - Backend/Server-side application"
        
        content_lower = codebase_context.lower()
        frontend = []
        
        if 'component' in content_lower:
            component_count = content_lower.count('component')
            frontend.append(f"**Component Architecture** - {component_count}+ components detected")
        
        if 'router' in content_lower or 'routing' in content_lower:
            frontend.append("**Client-Side Routing** - SPA navigation")
        
        if 'state' in content_lower and any(term in content_lower for term in ['redux', 'vuex', 'store']):
            frontend.append("**State Management** - Centralized state handling")
        
        if 'css' in content_lower or 'style' in content_lower:
            frontend.append("**Styling System** - Organized styling approach")
        
        return '\n'.join([f"• {f}" for f in frontend]) if frontend else "• Basic frontend structure"

    def analyze_data_layer(self, codebase_context):
        """Analyze data layer architecture"""
        content_lower = codebase_context.lower()
        data_layer = []
        
        if 'database' in content_lower or 'db' in content_lower:
            data_layer.append("**Database Integration** - Persistent data storage")
        
        if 'repository' in content_lower or 'dao' in content_lower:
            data_layer.append("**Repository Pattern** - Data access abstraction")
        
        if 'model' in content_lower or 'entity' in content_lower:
            data_layer.append("**Data Models** - Structured data representation")
        
        if 'migration' in content_lower or 'schema' in content_lower:
            data_layer.append("**Schema Management** - Database structure control")
        
        if 'api' in content_lower:
            data_layer.append("**API Integration** - External data sources")
        
        return '\n'.join([f"• {d}" for d in data_layer]) if data_layer else "• Minimal data layer detected"

    def analyze_build_config(self, codebase_context):
        """Analyze build and deployment configuration"""
        content_lower = codebase_context.lower()
        build_config = []
        
        if 'package.json' in content_lower:
            build_config.append("**NPM/Node.js** - JavaScript package management")
        
        if 'requirements.txt' in content_lower or 'pip' in content_lower:
            build_config.append("**Python Dependencies** - pip package management")
        
        if 'dockerfile' in content_lower or 'docker' in content_lower:
            build_config.append("**Docker Configuration** - Containerized deployment")
        
        if 'webpack' in content_lower or 'build' in content_lower:
            build_config.append("**Build System** - Asset compilation and bundling")
        
        if '.yml' in content_lower or '.yaml' in content_lower:
            build_config.append("**YAML Configuration** - Structured configuration files")
        
        if 'ci' in content_lower or 'cd' in content_lower:
            build_config.append("**CI/CD Pipeline** - Automated deployment")
        
        return '\n'.join([f"• {b}" for b in build_config]) if build_config else "• Basic configuration detected"

    def generate_architecture_recommendations(self, codebase_context, framework):
        """Generate architecture improvement recommendations"""
        recommendations = []
        content_lower = codebase_context.lower()
        
        # Security recommendations
        if 'auth' not in content_lower:
            recommendations.append("**Security**: Consider implementing authentication and authorization")
        
        # Performance recommendations
        if 'cache' not in content_lower and 'performance' not in content_lower:
            recommendations.append("**Performance**: Consider implementing caching strategies")
        
        # Testing recommendations
        if 'test' not in content_lower:
            recommendations.append("**Testing**: Add comprehensive test coverage")
        
        # Documentation recommendations
        if content_lower.count('readme') < 1:
            recommendations.append("**Documentation**: Improve code documentation and README")
        
        # Monitoring recommendations
        if 'log' not in content_lower and 'monitor' not in content_lower:
            recommendations.append("**Monitoring**: Add logging and monitoring capabilities")
        
        return '\n'.join([f"• {r}" for r in recommendations[:5]]) if recommendations else "• Architecture appears well-structured"

    def calculate_architecture_score(self, codebase_context):
        """Calculate architecture health score"""
        score = 50  # Base score
        content_lower = codebase_context.lower()
        
        # Security (+10)
        if 'auth' in content_lower:
            score += 10
        
        # Testing (+10)
        if 'test' in content_lower:
            score += 10
        
        # Documentation (+10)
        if 'readme' in content_lower or content_lower.count('#') > 20:
            score += 10
        
        # Performance (+5)
        if 'cache' in content_lower or 'async' in content_lower:
            score += 5
        
        # Configuration (+5)
        if '.json' in content_lower or '.yml' in content_lower:
            score += 5
        
        # Error handling (+5)
        if 'try' in content_lower or 'catch' in content_lower or 'exception' in content_lower:
            score += 5
        
        # Modularity (+5)
        if content_lower.count('import') > 10:
            score += 5
        
        return min(100, score)

    def identify_architecture_strengths(self, codebase_context):
        """Identify architecture strengths"""
        strengths = []
        content_lower = codebase_context.lower()
        
        if content_lower.count('import') > 20:
            strengths.append("Well-modularized codebase with clear dependencies")
        
        if 'component' in content_lower:
            strengths.append("Component-based architecture promotes reusability")
        
        if 'service' in content_lower:
            strengths.append("Service-oriented design for maintainability")
        
        if 'test' in content_lower:
            strengths.append("Testing infrastructure in place")
        
        if 'config' in content_lower:
            strengths.append("Configuration management implemented")
        
        return '\n'.join([f"• {s}" for s in strengths[:4]]) if strengths else "• Functional architecture with room for enhancement"

    def identify_architecture_improvements(self, codebase_context):
        """Identify areas for improvement"""
        improvements = []
        content_lower = codebase_context.lower()
        
        if 'todo' in content_lower or 'fixme' in content_lower:
            improvements.append("Address TODO items and known issues")
        
        if content_lower.count('test') < 5:
            improvements.append("Increase test coverage for better reliability")
        
        if 'deprecated' in content_lower:
            improvements.append("Update deprecated code and dependencies")
        
        if content_lower.count('#') < 10:
            improvements.append("Add more inline documentation and comments")
        
        if 'error' not in content_lower and 'exception' not in content_lower:
            improvements.append("Implement comprehensive error handling")
        
        return '\n'.join([f"• {i}" for i in improvements[:4]]) if improvements else "• Architecture is well-maintained"


class ArchitectureMetrics:
    """Calculate various architecture metrics"""
    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
    
    def calculate_complexity_metrics(self, codebase_context):
        """Calculate complexity metrics for the codebase"""
        lines = codebase_context.split('\n')
        
        # Basic metrics
        total_files = len([line for line in lines if line.startswith('filepath:///')])
        total_lines = len([line for line in lines if line.strip() and not line.startswith('filepath:///')])
        
        # Complexity indicators
        complexity_keywords = ['if', 'for', 'while', 'switch', 'case', 'try', 'catch']
        complexity_score = sum(codebase_context.lower().count(keyword) for keyword in complexity_keywords)
        
        # Calculate cyclomatic complexity approximation
        cyclomatic_complexity = complexity_score / max(total_files, 1)
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'complexity_score': complexity_score,
            'cyclomatic_complexity': round(cyclomatic_complexity, 2),
            'avg_lines_per_file': round(total_lines / max(total_files, 1), 2)
        }
    
    def calculate_maintainability_index(self, codebase_context):
        """Calculate maintainability index"""
        metrics = self.calculate_complexity_metrics(codebase_context)
        
        # Simplified maintainability index calculation
        # Real formula is more complex, this is an approximation
        lines_factor = max(0, 171 - 5.2 * (metrics['total_lines'] / 1000))
        complexity_factor = max(0, 50 - metrics['cyclomatic_complexity'] * 2)
        
        maintainability_index = (lines_factor + complexity_factor) / 2
        return max(0, min(100, round(maintainability_index, 1)))