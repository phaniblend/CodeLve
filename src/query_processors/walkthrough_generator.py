"""
Walkthrough generation module for CodeLve.
Creates step-by-step guides for implementing features or understanding code.
"""

import re
from typing import Dict, List, Optional, Any
from collections import defaultdict


class WalkthroughGenerator:

    
    def __init__(self, consolidated_code: str):
    # Works, but could be neater
        self.consolidated_code = consolidated_code
        self.file_structure = self._get_file_structure()
        self.patterns = self._get_patterns()
    
    def _get_file_structure(self) -> Dict[str, str]:

        files = {}
        current_file = None
        current_content = []
        
        file_pattern = r'#\s*File:\s*(.+?)(?:\n|$)'
        
        for line in self.consolidated_code.split('\n'):
            file_match = re.match(file_pattern, line)
            if file_match:
                if current_file:
                    files[current_file] = '\n'.join(current_content)
                current_file = file_match.group(1).strip()
                current_content = []
            elif current_file:
                current_content.append(line)
        
        if current_file:
            files[current_file] = '\n'.join(current_content)
        
        return files
    
    def _get_patterns(self) -> Dict[str, Any]:

        patterns = {
            'framework': self._detect_framework(),
            'testing': self._detect_testing_framework(),
            'database': self._detect_database_orm(),
            'auth': self._detect_auth_method()
        }
        return patterns
    
    def _detect_framework(self) -> str:

        if '@app.route' in self.consolidated_code:
            return 'flask'
        elif '@router.' in self.consolidated_code or '@app.get' in self.consolidated_code:
            return 'fastapi'
        elif 'urlpatterns' in self.consolidated_code:
            return 'django'
        elif 'express' in self.consolidated_code:
            return 'express'
        return 'unknown'
    
    def _detect_testing_framework(self) -> str:

        if 'def test_' in self.consolidated_code and 'pytest' in self.consolidated_code:
            return 'pytest'
        elif 'unittest.TestCase' in self.consolidated_code:
            return 'unittest'
        elif 'describe(' in self.consolidated_code:
            return 'jest'
        return 'unknown'
    
    def _detect_database_orm(self) -> str:

        if 'from sqlalchemy' in self.consolidated_code:
            return 'sqlalchemy'
        elif 'from django.db import models' in self.consolidated_code:
            return 'django'
        elif 'mongoose' in self.consolidated_code or 'pymongo' in self.consolidated_code:
            return 'mongodb'
        return 'unknown'
    
    def _detect_auth_method(self) -> str:

        if 'jwt' in self.consolidated_code.lower():
            return 'jwt'
        elif 'session' in self.consolidated_code.lower():
            return 'session'
        elif 'oauth' in self.consolidated_code.lower():
            return 'oauth'
        return 'unknown'
    
    def generate_feature_walkthrough(self, feature_name: str, feature_type: str) -> str:

        # Generate steps based on feature type
        if feature_type == 'api_endpoint':
            steps = self._generate_api_endpoint_steps(feature_name)
        elif feature_type == 'database_model':
            steps = self._generate_database_model_steps(feature_name)
        elif feature_type == 'frontend_component':
            steps = self._generate_frontend_component_steps(feature_name)
        elif feature_type == 'authentication':
            steps = self._generate_auth_steps(feature_name)
        elif feature_type == 'test':
            steps = self._generate_test_steps(feature_name)
        else:
            steps = self._generate_generic_walkthrough(feature_name, feature_type)
        
        return self._format_walkthrough(steps, feature_name, feature_type)
    
    def _generate_api_endpoint_steps(self, endpoint_name: str) -> List[Dict[str, Any]]:

        framework = self.patterns['framework']
        steps = []
# Might need cleanup
        if framework == 'fastapi':
            route_code = f"""
@router.get("/{endpoint_name.lower()}")
async def get_{endpoint_name.lower()}(skip: int = 0, limit: int = 100):
    '''Get all {endpoint_name} items.'''
    # Implementation here
    return {{"items": []}}
"""
        elif framework == 'flask':
            route_code = f"""
@app.route('/api/{endpoint_name.lower()}', methods=['GET'])
def get_{endpoint_name.lower()}():
    '''Get all {endpoint_name} items.'''
    # Implementation here
    return jsonify({{"items": []}})
"""
        else:
            route_code = f"# Define your {endpoint_name} endpoint handler here"
        
        steps.append({
            'title': 'Create Route Handler',
            'description': f'Add the endpoint handler for {endpoint_name}',
            'code': route_code,
            'file': self._suggest_file_location('api_endpoint', endpoint_name)
        })
        
        # Add validation
        steps.append({
            'title': 'Add Request Validation',
            'description': 'Create request/response models',
            'code': f"""
class {endpoint_name}Request(BaseModel):
    name: str
    description: Optional[str] = None

class {endpoint_name}Response(BaseModel):
    id: int
    name: str
    description: Optional[str]
""",
            'file': f'src/schemas/{endpoint_name.lower()}.py'
        })
        
        # Add tests
        steps.append({
            'title': 'Write Tests',
            'description': 'Add tests for the endpoint',
            'code': f"""
def test_get_{endpoint_name.lower()}(client):
    response = client.get('/api/{endpoint_name.lower()}')
    assert response.status_code == 200
    assert 'items' in response.json()
""",
            'file': f'tests/test_{endpoint_name.lower()}.py'
        })
        
        return steps
    
    def _generate_database_model_steps(self, model_name: str) -> List[Dict[str, Any]]:

        orm = self.patterns['database']
        steps = []
        
        # Model definition
        if orm == 'sqlalchemy':
            model_code = f"""
class {model_name}(Base):
    __tablename__ = '{model_name.lower()}s'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
"""
        elif orm == 'django':
            model_code = f"""
class {model_name}(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = '{model_name.lower()}s'
"""
        else:
            model_code = f"# Define your {model_name} model here"
        
        steps.append({
            'title': 'Define Model',
            'description': f'Create the {model_name} database model',
            'code': model_code,
            'file': self._suggest_file_location('database_model', model_name)
        })
        
        # Migration
        steps.append({
            'title': 'Create Migration',
            'description': 'Generate database migration',
            'code': f"# Run: alembic revision --autogenerate -m 'Add {model_name}'",
            'file': 'migrations/'
        })
        
        return steps
    
    def _generate_frontend_component_steps(self, component_name: str) -> List[Dict[str, Any]]:

        steps = []
        
        # Component structure
        steps.append({
            'title': 'Create Component',
            'description': f'Create the {component_name} component',
            'code': f"""
import React, {{ useState }} from 'react';

const {component_name} = ({{ data }}) => {{
    const [state, setState] = useState(data);
    
    return (
        <div className="{component_name.lower()}">
            <h2>{component_name}</h2>
            {{/* Component content */}}
        </div>
    );
}};

export default {component_name};
""",
            'file': f'src/components/{component_name}.jsx'
        })
        
        return steps
    
    def _generate_auth_steps(self, feature_name: str) -> List[Dict[str, Any]]:

        auth_method = self.patterns['auth']
        steps = []
        
        # Auth middleware
        steps.append({
            'title': 'Create Auth Middleware',
            'description': 'Set up authentication middleware',
            'code': f"""
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Auth logic here
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({{'error': 'No token provided'}}), 401
        # Verify token
        return f(*args, **kwargs)
    return decorated
""",
            'file': 'src/middleware/auth.py'
        })
        
        return steps
    
    def _generate_test_steps(self, test_name: str) -> List[Dict[str, Any]]:

        test_framework = self.patterns['testing']
        steps = []
        
        if test_framework == 'pytest':
            test_code = f"""
import pytest

def test_{test_name.lower()}_basic():
    '''Test basic {test_name} functionality.'''
    # Test implementation
    assert True

def test_{test_name.lower()}_edge_case():
    '''Test {test_name} edge cases.'''
    # Test implementation
    assert True
"""
        else:
            test_code = f"# Write your {test_name} tests here"
        
        steps.append({
            'title': 'Create Test File',
            'description': f'Set up tests for {test_name}',
            'code': test_code,
            'file': f'tests/test_{test_name.lower()}.py'
        })
        
        return steps
    
    def _generate_generic_walkthrough(self, feature_name: str, feature_type: str) -> List[Dict[str, Any]]:

        steps = []
        
        # Step 1: Analysis
        steps.append({
            'title': 'Analyze Requirements',
            'description': f'Understand what the {feature_name} needs to do',
            'code': f"""
# {feature_name} Requirements Analysis
# 1. Purpose: [Define the main purpose]
# 2. Inputs: [List expected inputs]
# 3. Outputs: [Define expected outputs]
# 4. Dependencies: [List any dependencies]
# 5. Constraints: [Note any constraints or limitations]
""",
            'file': self._suggest_file_location(feature_type, feature_name)
        })
        
        # Step 2: Implementation
        steps.append({
            'title': 'Implement Core Logic',
            'description': 'Build the main functionality',
            'code': f"""
class {feature_name}:
    '''Implementation for {feature_type}.'''
    
    def __init__(self):
        # Initialize component
        pass
    
    def process(self, input_data):
        # Main processing logic
        pass
    
    def validate(self, data):
        # Validation logic
        pass
""",
            'file': self._suggest_file_location(feature_type, feature_name)
        })
        
        # Step 3: Integration
        steps.append({
            'title': 'Integrate with Existing Code',
            'description': 'Connect the new feature to the system',
            'code': f"""
# Import and register the new feature
from {feature_type}.{feature_name.lower()} import {feature_name}

# Add to the appropriate registry or configuration
# Update any relevant routing or service mappings
""",
            'file': 'src/app.py'
        })
        
        # Step 4: Testing
        steps.append({
            'title': 'Add Tests',
            'description': 'Create tests for the feature',
            'code': f"""
import pytest
from {feature_type}.{feature_name.lower()} import {feature_name}

def test_{feature_name.lower()}_initialization():
    instance = {feature_name}()
    assert instance is not None

def test_{feature_name.lower()}_basic_functionality():
    instance = {feature_name}()
    result = instance.process({{'test': 'data'}})
    assert result is not None
""",
            'file': f'tests/test_{feature_name.lower()}.py'
        })
        
        # Step 5: Documentation
        steps.append({
            'title': 'Add Documentation',
            'description': 'Document the new feature',
            'code': f"""
# {feature_name} Documentation

## Overview
{feature_name} is a {feature_type} that provides [describe functionality].

## Usage
```python
from {feature_type}.{feature_name.lower()} import {feature_name}
instance = {feature_name}()
result = instance.process(data)
```

## API Reference
[Document methods and parameters]
""",
            'file': f'docs/{feature_name.lower()}.md'
        })
        
        return steps
    
    def _format_walkthrough(self, steps: List[Dict[str, Any]], feature_name: str, 
                           feature_type: str) -> str:

        output = f"# Step-by-Step Guide: Implementing {feature_name} ({feature_type})\n\n"
        output += f"This guide will walk you through implementing a {feature_type} called {feature_name} "
        output += f"following the patterns and conventions in your codebase.\n\n"
        
        # Add overview
        output += "## Overview\n"
        output += f"Total steps: {len(steps)}\n"
        output += f"Estimated time: {len(steps) * 10}-{len(steps) * 15} minutes\n\n"
        
        # Add detected patterns
        output += "## Detected Patterns\n"
        output += f"- Framework: {self.patterns['framework']}\n"
        output += f"- Testing: {self.patterns['testing']}\n"
        output += f"- Database: {self.patterns['database']}\n"
        output += f"- Auth: {self.patterns['auth']}\n\n"
        
        # Add steps
        output += "## Implementation Steps\n\n"
        
        for i, step in enumerate(steps, 1):
            output += f"### Step {i}: {step['title']}\n\n"
            output += f"{step['description']}\n\n"
            
            if step.get('file'):
                output += f"**File:** `{step['file']}`\n\n"
            
            if step.get('code'):
                output += "```python\n"
                output += step['code'].strip()
                output += "\n```\n\n"
            
            output += "---\n\n"
        
        # Add next steps
        output += "## Next Steps\n\n"
        output += "After completing this implementation:\n"
        output += f"1. Run the tests: `pytest tests/test_{feature_name.lower()}.py`\n"
        output += "2. Update the documentation\n"
        output += "3. Create a pull request with your changes\n"
        output += "4. Deploy to staging for testing\n"
        
        return output
    
    def _suggest_file_location(self, feature_type: str, feature_name: str) -> str:

        # Map feature types to common directory patterns
        type_patterns = {
            'api_endpoint': ['routes', 'api', 'endpoints', 'controllers'],
            'database_model': ['models', 'entities', 'db'],
            'service': ['services', 'business', 'logic'],
            'component': ['components', 'ui', 'views'],
            'utility': ['utils', 'helpers', 'common']
        }
# Not the cleanest, but it does the job
        patterns = type_patterns.get(feature_type, [])
        for pattern in patterns:
            for file_path in self.file_structure.keys():
                if pattern in file_path.lower():
                    dir_path = '/'.join(file_path.split('/')[:-1])
                    return f"{dir_path}/{feature_name.lower()}.py"
        
        # Default location
        return f"src/{feature_type}/{feature_name.lower()}.py"
    
    def generate_understanding_walkthrough(self, component_name: str) -> str:

        output = f"# Understanding: {component_name}\n\n"
        
        # Find relevant files
        relevant_files = []
        for file_path, content in self.file_structure.items():
            if component_name.lower() in file_path.lower() or component_name in content:
                relevant_files.append(file_path)
        
        output += f"## Related Files ({len(relevant_files)} found)\n"
        for file_path in relevant_files[:10]:  # Limit to 10 files
            output += f"- `{file_path}`\n"
        output += "\n"
        
        # Analyze component structure
        output += "## Component Analysis\n\n"
        
        # Find class definitions
        class_pattern = rf'class\s+{component_name}.*?:'
        if re.search(class_pattern, self.consolidated_code):
            output += f"### Class Definition Found\n"
            output += f"The `{component_name}` class is defined in the codebase.\n\n"
        
        # Find function definitions
        func_pattern = rf'def\s+{component_name.lower()}.*?\('
        if re.search(func_pattern, self.consolidated_code):
            output += f"### Function Definition Found\n"
            output += f"Functions related to `{component_name}` are defined.\n\n"
        
        # Find imports
        import_pattern = rf'(?:from\s+\S+\s+)?import\s+.*?{component_name}'
        imports = re.findall(import_pattern, self.consolidated_code)
        if imports:
            output += f"### Import Statements ({len(imports)} found)\n"
            output += "This component is imported in multiple places.\n\n"
        
        # Find usages
        usage_pattern = rf'{component_name}\s*\('
        usages = re.findall(usage_pattern, self.consolidated_code)
        if usages:
            output += f"### Usage Examples ({len(usages)} found)\n"
            output += f"The component is used {len(usages)} times in the codebase.\n\n"
        
        # Provide exploration steps
        output += "## Exploration Steps\n\n"
        output += "1. **Start with the main definition** - Look for the class or function definition\n"
        output += "2. **Trace the imports** - See where the component is imported and used\n"
        output += "3. **Analyze dependencies** - Check what this component imports and depends on\n"
        output += "4. **Find test files** - Look for test files to understand expected behavior\n"
        output += "5. **Check documentation** - Look for docstrings and comments\n"
        
        return output