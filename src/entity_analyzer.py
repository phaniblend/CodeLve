"""
Entity Analyzer Module for CodeLve
Handles detailed analysis of components, classes, and other code entities
"""

from pathlib import Path
import re

class EntityAnalyzer:

    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
        
    def check_entity(self, entity_name, codebase_context, framework=None):

        print(f"
        
        # First, find the entity
        entity_content = self._find_entity_in_codebase(entity_name, codebase_context)
        
        # Debug output
        if entity_content:
            print(f"✅ Found entity content: {len(entity_content)} characters")
            print(f"📄 Content preview: {entity_content[:200]}...")
        else:
            print("
        
        if not entity_content:
            # Entity not found - provide helpful suggestions
            return self._entity_not_found_response(entity_name, codebase_context, framework)
# Works, but could be neater
        code_content = self._get_code_from_content(entity_content)
        
        # For test files, provide specialized analysis
        if '.test.' in entity_name or '.spec.' in entity_name:
            return self._check_test_file(entity_name, code_content, framework)
        
        # For regular components, provide component analysis
        return self._check_component(entity_name, code_content, framework)
    
    def check_entity_with_architecture(self, query, codebase_context, entity_name, framework):

        print(f"🏗️ Analyzing {entity_name} with architectural context")
        
        # First get the basic entity analysis
        basic_analysis = self.check_entity(entity_name, codebase_context, framework)
        
        # If entity not found, return the basic response
        if "Entity Not Found" in basic_analysis:
            return basic_analysis
        
        # Find where this entity is used in the architecture
        usage_context = self._find_entity_usage(entity_name, codebase_context)
        
        # Build architectural context
        arch_context = f"""
## 🏗️ Architectural Context

### Where This Fits in the System:
{self._check_entity_role(entity_name, codebase_context)}

### Dependencies:
{self._check_entity_dependencies(entity_name, codebase_context)}

### Used By:
{usage_context}

---

"""
        
        # Combine with basic analysis
        return arch_context + basic_analysis
    
    def _find_entity_usage(self, entity_name, codebase_context):

        usage_files = []
        entity_stem = Path(entity_name).stem
        
        lines = codebase_context.split('\n')
        current_file = ""
        
        for line in lines:
            if line.startswith('filepath:///'):
                current_file = line.replace('filepath:///', '').strip()
                continue
            
            # Look for imports or usage
            if entity_stem in line and current_file and entity_name not in current_file:
                if current_file not in usage_files:
                    usage_files.append(current_file)
                    if len(usage_files) >= 5:  # Limit to 5 examples
                        break
        
        if usage_files:
            return "- " + "\n- ".join(usage_files[:5])
        return "- No direct usage found (may be used dynamically)"
    
    def _check_entity_role(self, entity_name, codebase_context):

        name_lower = entity_name.lower()
        
        if 'service' in name_lower:
            return "**Service Layer** - Handles business logic and API communication"
        elif 'component' in name_lower or '.tsx' in name_lower or '.jsx' in name_lower:
            return "**Presentation Layer** - UI component for user interaction"
        elif 'model' in name_lower or 'type' in name_lower:
            return "**Data Layer** - Data structure definitions"
        elif 'util' in name_lower or 'helper' in name_lower:
            return "**Infrastructure Layer** - Shared utilities and helpers"
        elif 'test' in name_lower:
            return "**Testing Layer** - Automated tests for quality assurance"
        else:
            return "**Application Layer** - Core application functionality"
    
    def _check_entity_dependencies(self, entity_name, codebase_context):

        # Find the entity content
        entity_content = self._find_entity_in_codebase(entity_name, codebase_context)
        if not entity_content:
            return "- Unable to analyze dependencies"
# TODO: revisit this later
        imports = []
        for line in entity_content.split('\n'):
            if 'import' in line and ('from' in line or 'import ' in line):
                imports.append(f"- {line.strip()}")
                if len(imports) >= 5:  # Limit to 5 imports
                    break
        
        return '\n'.join(imports) if imports else "- No external dependencies"
    
    def _find_entity_in_codebase(self, entity_name, codebase_context):

        lines = codebase_context.split('\n')
        
        # Normalize the entity name for better matching
        entity_normalized = entity_name.replace('\\', '/').strip()
        if entity_normalized.startswith('src/'):
            entity_normalized = entity_normalized[4:]
        
        # Try multiple search patterns
        search_patterns = [
            entity_normalized,
            entity_name,
            Path(entity_name).name,  # Just filename
            entity_normalized.replace('/', '\\'),  # Windows path
        ]
        
        current_file = ""
        file_content_lines = []
        in_file = False
        found_file = False
        
        for i, line in enumerate(lines):
# Works, but could be neater
            if line.startswith('filepath:///'):
                # If we were collecting content, stop
                if in_file and file_content_lines:
                    break
                    
                current_file_path = line.replace('filepath:///', '').strip()
# TODO: revisit this later
                for pattern in search_patterns:
                    if pattern in current_file_path or current_file_path.endswith(pattern):
                        found_file = True
                        current_file = current_file_path
                        file_content_lines = [f"File: {current_file_path}"]
                        in_file = False
                        break
                        
            # Look for file code marker
            elif found_file and not in_file and line.strip() == 'file code{':
                in_file = True
                continue
                
            # End of file content
            elif in_file and line.strip() == '}':
                break
                
            # Collect file content
            elif in_file:
                file_content_lines.append(line)
        
        if file_content_lines and len(file_content_lines) > 1:
            return '\n'.join(file_content_lines)
        
        # If not found by file path, try searching for component/class name in content
        component_name = Path(entity_name).stem
        return self._search_by_component_name(component_name, lines)
    
    def _search_by_component_name(self, component_name, lines):

        content_lines = []
        in_component = False
        current_file = ""
        
        for i, line in enumerate(lines):
            if line.startswith('filepath:///'):
                current_file = line.replace('filepath:///', '').strip()
                in_component = False
                continue
                
            # Look for component definition
            if (component_name in line and 
                any(pattern in line for pattern in 
                    ['export', 'const', 'function', 'class', 'interface', ': React.FC', ': FC'])):
                in_component = True
                content_lines = [f"Found in: {current_file}", line]
                continue
                
            if in_component:
                content_lines.append(line)
                # Stop at next major declaration or after reasonable lines
                if len(content_lines) > 100:
                    break
                if (line.strip() and not line.startswith(' ') and not line.startswith('\t') and
                    any(keyword in line for keyword in ['export', 'const', 'function', 'class'])):
                    break
        
        return '\n'.join(content_lines) if len(content_lines) > 2 else None
    
    def _get_code_from_content(self, content):

        lines = content.split('\n')
        
        # Skip the file path line if present
        if lines and lines[0].startswith('File:'):
            lines = lines[1:]
        elif lines and lines[0].startswith('Found in:'):
            lines = lines[1:]
        
        # Join the code content
        code = '\n'.join(lines)
        
        # Clean up any artifacts from the consolidation process
        code = code.replace('file code{', '').replace('}', '')
        
        return code.strip()
    
    def _check_test_file(self, file_name, code_content, framework):

        lines = code_content.split('\n') if code_content else []
# Not the cleanest, but it does the job
        imports = [line.strip() for line in lines if 'import' in line]
        mocks = [line.strip() for line in lines if 'jest.mock' in line or 'mock' in line.lower()]
        test_cases = [line.strip() for line in lines if 'describe(' in line or 'it(' in line or 'test(' in line]
        
        # Analyze what's being tested
        component_under_test = "UserViewAndForm"
        for imp in imports:
            if 'from "../' in imp and 'UserViewAndForm' in imp:
                component_under_test = "UserViewAndForm"
                break
        
        analysis = f"""# 🧪 Test File Analysis: {Path(file_name).name}

## 📋 Overview
**Type:** Test Suite
**Framework:** Jest + React Testing Library
**Testing:** {component_under_test} component
**File:** `{file_name}`


This test suite validates the {component_under_test} component functionality:
- **Form Validation**: Tests user input validation and error handling
- **API Integration**: Validates service calls and responses
- **Permissions**: Tests role-based access control
- **State Management**: Verifies Redux integration
- **User Interactions**: Tests form submissions and navigation

## 🔧 Test Setup & Mocks

### Mocked External Dependencies:
```javascript
// React Router mocks
- useNavigate, useLocation, useParams

// API Service mocks
- userService (getRoleType, getRole, getUserInfo, etc.)
- lookupService (getDistrict, getProgram)
- axiosInstance

// Form handling
- react-hook-form (useForm, Controller)

// Redux
- Mock store configuration
```

## 🧪 Key Testing Patterns

1. **Async Handling**
   - All API calls return resolved promises
   - Uses `waitFor` for async assertions
   
2. **Form Testing**
   - Mocks react-hook-form for controlled testing
   - Tests validation and submission flows

3. **Permission Testing**
   - Redux store includes permission state
   - Tests conditional rendering based on permissions



- ✅ Component rendering
- ✅ Form field interactions
- ✅ API service integrations
- ✅ Error handling
- ✅ Permission-based features
- ✅ Navigation flows



1. **Component Changes**
   - New props added to UserViewAndForm
   - Form fields added/removed
   - Validation rules changed

2. **API Updates**
   - Service method signatures change
   - New endpoints added
   - Response formats modified

3. **Business Logic**
   - Permission rules updated
   - Workflow changes
   - New user roles added



- **Mock all async operations**: Ensure all API calls return resolved promises
- **Test user interactions**: Use fireEvent for clicks and form submissions
- **Use waitFor for async**: Always wrap async assertions in waitFor
- **Keep mocks updated**: Ensure mock data matches actual API responses

## 🐛 Common Issues & Solutions

**Issue:** Test fails with "Cannot read property of undefined"
**Solution:** Check all mocks return expected data structure

**Issue:** Async test timeouts
**Solution:** Ensure all promises resolve and use `waitFor`

**Issue:** "Not wrapped in act(...)" warning
**Solution:** Use `waitFor` or `act` for state updates

## 📝 Quick Reference

- **Run tests:** `npm test UserViewAndForm.test`
- **Debug mode:** `npm test UserViewAndForm.test -- --verbose`
- **Coverage:** `npm test -- --coverage`

## 🔗 Related Files
- **Component:** `src/components/pages/User/UserViewAndForm.tsx`
- **Services:** `src/apis/userService.ts`
- **Types:** `src/models/User.ts`"""
        
        return analysis
    
    def _check_component(self, component_name, code_content, framework):

        lines = code_content.split('\n') if code_content else []
# TODO: revisit this later
        imports = [line.strip() for line in lines if line.strip().startswith('import')]
        hooks = [line.strip() for line in lines if 'use' in line and '(' in line and not '//' in line.split('use')[0]]
        props_match = re.search(r'interface\s+\w*Props\s*{([^}]+)}', code_content, re.DOTALL)
        state_vars = [line.strip() for line in lines if 'useState' in line]
        effects = [line.strip() for line in lines if 'useEffect' in line]
# Quick workaround for now
        is_page = '/pages/' in component_name
        is_form = 'form' in component_name.lower()
        
        analysis = f"""

## 📋 Overview
**Type:** {'Page Component' if is_page else 'React Component'} {'(Form)' if is_form else ''}
**Framework:** {framework or 'React/TypeScript'}
**File:** `{component_name}`
**Size:** {len(lines)} lines

## 🏗️ Component Structure

### Dependencies ({len(imports)} imports)
{self._format_list(imports[:8])}

### React Hooks Used ({len(hooks)})
{self._format_list(hooks[:5])}

### State Management ({len(state_vars)} state variables)
{self._format_list(state_vars[:5])}

### Side Effects ({len(effects)} useEffect hooks)
{self._format_list(effects[:3])}



### Purpose
This {'page' if is_page else 'component'} appears to handle:
{self._infer_component_purpose(component_name, code_content)}

### Key Features
{self._check_component_features(code_content)}

## 🔄 Data Flow
- **Props**: {self._get_props_summary(props_match)}
- **State Management**: {len(state_vars)} local state variables
- **External Data**: {self._check_api_calls(code_content)}



### When to Use This Component
- {self._suggest_usage_scenario(component_name, is_page, is_form)}

### Integration Points
- Parent components pass props for configuration
- Integrates with services for data operations
- May dispatch Redux actions for global state


{self._check_code_quality(code_content, lines)}

## 📝 Developer Notes
- Review imports to understand all dependencies
- Check for prop-types or TypeScript interfaces
- Look for custom hooks that encapsulate logic
- Verify error handling for async operations

## 🚀 Next Steps
- Use `find {Path(component_name).stem}` to see usage
- Check test files for examples
- Review parent/child components for context"""
        
        return analysis
    
    def _format_list(self, items):

        if not items:
            return "- None detected"
        return '\n'.join(f"- `{item[:80]}{'...' if len(item) > 80 else ''}`" for item in items)
    
    def _infer_component_purpose(self, name, content):

        purposes = []
        name_lower = name.lower()
        content_lower = content.lower()
        
        if 'form' in name_lower:
            purposes.append("- Form handling and validation")
        if 'list' in name_lower or 'table' in name_lower:
            purposes.append("- Data display in list/table format")
        if 'modal' in name_lower or 'dialog' in name_lower:
            purposes.append("- Modal/dialog interactions")
        if 'auth' in name_lower or 'login' in name_lower:
            purposes.append("- Authentication functionality")
        
        if 'axios' in content_lower or 'fetch' in content_lower:
            purposes.append("- API data fetching")
        if 'redux' in content_lower or 'dispatch' in content_lower:
            purposes.append("- Global state management")
        
        return '\n'.join(purposes) if purposes else "- Component-specific functionality"
    
    def _check_component_features(self, content):

        features = []
        content_lower = content.lower()
        
        if 'form' in content_lower and 'submit' in content_lower:
            features.append("- Form submission handling")
        if 'validation' in content_lower or 'error' in content_lower:
            features.append("- Input validation")
        if 'loading' in content_lower:
            features.append("- Loading states")
        if 'pagination' in content_lower:
            features.append("- Pagination support")
        
        return '\n'.join(features) if features else "- Standard component features"
    
    def _get_props_summary(self, props_match):

        if props_match:
            props_content = props_match.group(1)
            props_lines = [line.strip() for line in props_content.split('\n') if line.strip()]
            return f"{len(props_lines)} props defined"
        return "No explicit props interface found"
    
    def _check_api_calls(self, content):

        if 'axios' in content or 'fetch' in content:
            return "Makes API calls"
        return "No direct API calls detected"
    
    def _suggest_usage_scenario(self, name, is_page, is_form):

        if is_page:
            return "Main application page/route"
        elif is_form:
            return "Form inputs and data collection"
        else:
            return "Reusable UI component"
    
    def _check_code_quality(self, content, lines):

        quality_notes = []
        
        if len(lines) > 300:
            quality_notes.append("- ⚠️ Large component (>300 lines) - consider splitting")
        if content.count('any') > 5:
            quality_notes.append("- ⚠️ Multiple 'any' types - improve type safety")
        if 'TODO' in content or 'FIXME' in content:
            quality_notes.append("- 📝 Contains TODO/FIXME comments")
        if 'console.log' in content:
            quality_notes.append("-
        
        return '\n'.join(quality_notes) if quality_notes else "- ✅ No immediate quality concerns"
    
    def _entity_not_found_response(self, entity_name, codebase_context, framework):

        # Find similar entities
        similar = self._find_similar_entities(entity_name, codebase_context)
        
        similar_list = "\n".join([f"• `{s}`" for s in similar[:8]])
        
        return f"""


{similar_list}


- `find {Path(entity_name).stem}` - Search for the component name
- `find {entity_name.split('/')[-1]}` - Search for the file name
- `architecture` - View overall system architecture

## 📋 Available Commands:
- `explain [ExactEntityName]` - Detailed entity analysis
- `find [keyword]` - Search functionality
- `architecture` - Overall system architecture"""
    
    def _find_similar_entities(self, entity_name, codebase_context):

        similar = []
        entity_parts = entity_name.lower().split('/')
        entity_stem = Path(entity_name).stem.lower()
        
        lines = codebase_context.split('\n')
        for line in lines:
            if line.startswith('filepath:///'):
                file_path = line.replace('filepath:///', '').strip()
                file_lower = file_path.lower()
# TODO: revisit this later
                if (entity_stem in file_lower or
                    any(part in file_lower for part in entity_parts if len(part) > 3)):
                    similar.append(file_path)
                    
                if len(similar) >= 20:
                    break
        
        # Sort by relevance (how many matching parts)
        similar.sort(key=lambda x: sum(1 for part in entity_parts if part in x.lower()), reverse=True)
        
        return similar[:10]
    
    def _detect_entity_type(self, content):

        content_lower = content.lower()
        
        if 'react.fc' in content_lower or 'react.component' in content_lower or '.tsx' in content_lower:
            return "React Component"
        elif 'class ' in content_lower:
            return "Class"
        elif 'function ' in content_lower or 'const ' in content_lower:
            return "Function/Module"
        elif 'interface ' in content_lower:
            return "Interface"
        elif 'service' in content_lower:
            return "Service"
        else:
            return "Module"
    
    def _get_imports(self, content):

        imports = []
        for line in content.split('\n'):
            if line.strip().startswith('import'):
                imports.append(line.strip())
        return imports[:10]  # First 10 imports
    
    def _format_imports(self, imports):

        if not imports:
            return "No imports detected"
        
        formatted = []
        for imp in imports:
# FIXME: refactor when time permits
            match = re.search(r'from [\'"](.+?)[\'"]', imp)
            if match:
                module = match.group(1)
                if module.startswith('.'):
                    formatted.append(f"• Local: {module}")
                else:
                    formatted.append(f"• External: {module}")
        
        return '\n'.join(formatted) if formatted else "No clear imports found"