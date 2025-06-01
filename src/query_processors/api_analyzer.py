"""
API analysis module for CodeLve.
Analyzes API endpoints, payloads, and interactions in the codebase.
"""

import re
import json
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict


class ApiAnalyzer:
    """Analyzes API endpoints, routes, and interactions."""
    
    def __init__(self, consolidated_code: str):
        self.consolidated_code = consolidated_code
        self.endpoints = self._extract_endpoints()
        self.models = self._extract_models()
        self.middleware = self._extract_middleware()
    
    def _extract_endpoints(self) -> List[Dict[str, Any]]:
        """Extract API endpoints from the codebase."""
        endpoints = []
        
        # Flask patterns
        flask_pattern = r'@app\.route\([\'"]([^\'"]*)[\'"]\s*(?:,\s*methods=\[(.*?)\])?\)\s*\ndef\s+(\w+)'
        for match in re.finditer(flask_pattern, self.consolidated_code):
            path, methods_str, func_name = match.groups()
            methods = self._parse_methods(methods_str) if methods_str else ['GET']
            endpoints.append({
                'framework': 'flask',
                'path': path,
                'methods': methods,
                'handler': func_name,
                'type': self._categorize_endpoint(path, func_name)
            })
        
        # FastAPI patterns
        fastapi_patterns = [
            r'@(?:app|router)\.(get|post|put|patch|delete)\([\'"]([^\'"]*)[\'"]\)\s*\n*(?:async\s+)?def\s+(\w+)',
            r'@(?:app|router)\.(get|post|put|patch|delete)\([\'"]([^\'"]*)[\'"]\s*,.*?\)\s*\n*(?:async\s+)?def\s+(\w+)'
        ]
        
        for pattern in fastapi_patterns:
            for match in re.finditer(pattern, self.consolidated_code):
                method, path, func_name = match.groups()
                endpoints.append({
                    'framework': 'fastapi',
                    'path': path,
                    'methods': [method.upper()],
                    'handler': func_name,
                    'type': self._categorize_endpoint(path, func_name),
                    'async': 'async def' in match.group(0)
                })
        
        # Express.js patterns
        express_pattern = r'(?:app|router)\.(get|post|put|patch|delete)\([\'"]([^\'"]*)[\'"]\s*,\s*(?:async\s+)?(?:\(.*?\)\s*=>|function)'
        for match in re.finditer(express_pattern, self.consolidated_code):
            method, path = match.groups()
            endpoints.append({
                'framework': 'express',
                'path': path,
                'methods': [method.upper()],
                'handler': 'anonymous',
                'type': self._categorize_endpoint(path, '')
            })
        
        # Django patterns
        django_pattern = r'path\([\'"]([^\'"]*)[\'"]\s*,\s*(\w+)'
        for match in re.finditer(django_pattern, self.consolidated_code):
            path, view_name = match.groups()
            endpoints.append({
                'framework': 'django',
                'path': path,
                'methods': ['GET', 'POST'],  # Django views typically handle multiple methods
                'handler': view_name,
                'type': self._categorize_endpoint(path, view_name)
            })
        
        return endpoints
    
    def _parse_methods(self, methods_str: str) -> List[str]:
        """Parse HTTP methods from a string."""
        methods = []
        for method in re.findall(r'[\'"](\w+)[\'"]', methods_str):
            methods.append(method.upper())
        return methods if methods else ['GET']
    
    def _categorize_endpoint(self, path: str, handler_name: str) -> str:
        """Categorize endpoint based on path and handler name."""
        path_lower = path.lower()
        handler_lower = handler_name.lower()
        
        # Authentication endpoints
        if any(auth in path_lower or auth in handler_lower for auth in ['login', 'logout', 'auth', 'token', 'register']):
            return 'authentication'
        
        # CRUD operations
        if any(crud in handler_lower for crud in ['create', 'add', 'new']):
            return 'create'
        elif any(crud in handler_lower for crud in ['get', 'read', 'list', 'find', 'search']):
            return 'read'
        elif any(crud in handler_lower for crud in ['update', 'edit', 'modify', 'patch']):
            return 'update'
        elif any(crud in handler_lower for crud in ['delete', 'remove', 'destroy']):
            return 'delete'
        
        # File operations
        elif any(file_op in path_lower for file_op in ['upload', 'download', 'file', 'image']):
            return 'file_operation'
        
        # API patterns
        elif '/api/' in path_lower:
            if path_lower.endswith('s') or path_lower.endswith('es'):
                return 'resource_list'
            elif re.search(r'/\{?\w+\}?/?$', path):
                return 'resource_detail'
            else:
                return 'api_endpoint'
        
        # Admin endpoints
        elif 'admin' in path_lower:
            return 'admin'
        
        # Health checks
        elif any(health in path_lower for health in ['health', 'status', 'ping']):
            return 'health_check'
        
        return 'general'
    
    def _extract_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract data models and schemas."""
        models = defaultdict(list)
        
        # Pydantic models
        pydantic_pattern = r'class\s+(\w+)\((?:.*?BaseModel.*?)\):\s*\n((?:\s{4,}.*\n)*)'
        for match in re.finditer(pydantic_pattern, self.consolidated_code):
            model_name, model_body = match.groups()
            fields = self._extract_pydantic_fields(model_body)
            models['pydantic'].append({
                'name': model_name,
                'fields': fields,
                'type': 'request_model' if 'Request' in model_name else 'response_model'
            })
        
        # SQLAlchemy models
        sqlalchemy_pattern = r'class\s+(\w+)\((?:.*?Base.*?)\):\s*\n((?:\s{4,}.*\n)*)'
        for match in re.finditer(sqlalchemy_pattern, self.consolidated_code):
            model_name, model_body = match.groups()
            if '__tablename__' in model_body:
                fields = self._extract_sqlalchemy_fields(model_body)
                models['sqlalchemy'].append({
                    'name': model_name,
                    'fields': fields,
                    'table': re.search(r'__tablename__\s*=\s*[\'"](\w+)[\'"]', model_body).group(1) if re.search(r'__tablename__\s*=\s*[\'"](\w+)[\'"]', model_body) else None
                })
        
        # Django models
        django_pattern = r'class\s+(\w+)\(.*?models\.Model.*?\):\s*\n((?:\s{4,}.*\n)*)'
        for match in re.finditer(django_pattern, self.consolidated_code):
            model_name, model_body = match.groups()
            fields = self._extract_django_fields(model_body)
            models['django'].append({
                'name': model_name,
                'fields': fields
            })
        
        return dict(models)
    
    def _extract_pydantic_fields(self, model_body: str) -> List[Dict[str, str]]:
        """Extract fields from a Pydantic model."""
        fields = []
        field_pattern = r'(\w+)\s*:\s*([^\n=]+?)(?:\s*=\s*([^\n]+))?$'
        
        for match in re.finditer(field_pattern, model_body, re.MULTILINE):
            field_name, field_type, default = match.groups()
            fields.append({
                'name': field_name,
                'type': field_type.strip(),
                'default': default.strip() if default else None,
                'required': default is None
            })
        
        return fields
    
    def _extract_sqlalchemy_fields(self, model_body: str) -> List[Dict[str, str]]:
        """Extract fields from a SQLAlchemy model."""
        fields = []
        field_pattern = r'(\w+)\s*=\s*Column\((.*?)\)'
        
        for match in re.finditer(field_pattern, model_body):
            field_name, column_def = match.groups()
            field_info = {
                'name': field_name,
                'type': 'Unknown',
                'nullable': 'nullable=False' not in column_def,
                'primary_key': 'primary_key=True' in column_def
            }
            
            # Extract type
            type_match = re.search(r'(Integer|String|Text|DateTime|Boolean|Float)', column_def)
            if type_match:
                field_info['type'] = type_match.group(1)
            
            fields.append(field_info)
        
        return fields
    
    def _extract_django_fields(self, model_body: str) -> List[Dict[str, str]]:
        """Extract fields from a Django model."""
        fields = []
        field_pattern = r'(\w+)\s*=\s*models\.(\w+)\((.*?)\)'
        
        for match in re.finditer(field_pattern, model_body):
            field_name, field_type, field_args = match.groups()
            fields.append({
                'name': field_name,
                'type': field_type,
                'args': field_args
            })
        
        return fields
    
    def _extract_middleware(self) -> List[Dict[str, Any]]:
        """Extract middleware and decorators."""
        middleware = []
        
        # Common middleware patterns
        patterns = [
            (r'@(\w+_required)', 'decorator'),
            (r'@(\w+\.before_request)', 'before_request'),
            (r'@(\w+\.after_request)', 'after_request'),
            (r'app\.use\((\w+)\)', 'express_middleware'),
            (r'middleware\s*=\s*\[(.*?)\]', 'django_middleware')
        ]
        
        for pattern, mw_type in patterns:
            for match in re.finditer(pattern, self.consolidated_code):
                name = match.group(1)
                middleware.append({
                    'name': name,
                    'type': mw_type
                })
        
        return middleware
    
    def analyze_api_structure(self) -> Dict[str, Any]:
        """Analyze overall API structure."""
        analysis = {
            'total_endpoints': len(self.endpoints),
            'endpoints_by_method': defaultdict(int),
            'endpoints_by_type': defaultdict(int),
            'frameworks_used': set(),
            'restful_analysis': self._analyze_restful_compliance(),
            'authentication': self._analyze_authentication(),
            'versioning': self._analyze_versioning()
        }
        
        for endpoint in self.endpoints:
            analysis['frameworks_used'].add(endpoint['framework'])
            analysis['endpoints_by_type'][endpoint['type']] += 1
            for method in endpoint['methods']:
                analysis['endpoints_by_method'][method] += 1
        
        analysis['frameworks_used'] = list(analysis['frameworks_used'])
        
        return analysis
    
    def _analyze_restful_compliance(self) -> Dict[str, Any]:
        """Analyze RESTful API compliance."""
        analysis = {
            'resource_endpoints': 0,
            'uses_http_methods': set(),
            'uses_status_codes': [],
            'uses_json': False,
            'compliance_score': 0
        }
        
        # Check resource-based URLs
        resource_pattern = r'/(?:api/)?(\w+)(?:/\{?\w+\}?)?/?$'
        for endpoint in self.endpoints:
            if re.match(resource_pattern, endpoint['path']):
                analysis['resource_endpoints'] += 1
            analysis['uses_http_methods'].update(endpoint['methods'])
        
        # Check for status codes
        status_patterns = [
            (r'(?:status_code|status)\s*=\s*(\d{3})', 'explicit'),
            (r'return\s+.*?,\s*(\d{3})', 'return_tuple'),
            (r'HTTPException\(status_code=(\d{3})', 'exception')
        ]
        
        for pattern, _ in status_patterns:
            for match in re.finditer(pattern, self.consolidated_code):
                analysis['uses_status_codes'].append(int(match.group(1)))
        
        # Check for JSON usage
        if any(json_indicator in self.consolidated_code for json_indicator in ['jsonify', 'json()', 'JSONResponse', 'application/json']):
            analysis['uses_json'] = True
        
        # Calculate compliance score
        score = 0
        if analysis['resource_endpoints'] > len(self.endpoints) * 0.7:
            score += 25
        if len(analysis['uses_http_methods']) >= 4:
            score += 25
        if analysis['uses_json']:
            score += 25
        if len(set(analysis['uses_status_codes'])) >= 5:
            score += 25
        
        analysis['compliance_score'] = score
        analysis['uses_http_methods'] = list(analysis['uses_http_methods'])
        
        return analysis
    
    def _analyze_authentication(self) -> Dict[str, Any]:
        """Analyze authentication patterns."""
        analysis = {
            'has_auth': False,
            'auth_types': [],
            'protected_endpoints': 0
        }
        
        # Check for authentication patterns
        auth_patterns = {
            'jwt': r'jwt|JWT|JsonWebToken',
            'oauth': r'oauth|OAuth',
            'basic': r'Basic\s+Auth|HTTPBasic',
            'token': r'Token\s+Auth|Bearer',
            'session': r'session\[|flask_login|SessionMiddleware'
        }
        
        for auth_type, pattern in auth_patterns.items():
            if re.search(pattern, self.consolidated_code, re.IGNORECASE):
                analysis['auth_types'].append(auth_type)
                analysis['has_auth'] = True
        
        # Count protected endpoints
        protection_patterns = [
            r'@\w*auth\w*_required',
            r'@\w*login\w*_required',
            r'@protected',
            r'requires_auth'
        ]
        
        for pattern in protection_patterns:
            analysis['protected_endpoints'] += len(re.findall(pattern, self.consolidated_code))
        
        return analysis
    
    def _analyze_versioning(self) -> Dict[str, Any]:
        """Analyze API versioning."""
        analysis = {
            'has_versioning': False,
            'version_pattern': None,
            'versions_found': []
        }
        
        # Check for version patterns in URLs
        version_patterns = [
            (r'/v(\d+)/', 'url_path'),
            (r'/api/v(\d+)/', 'api_path'),
            (r'version\s*=\s*[\'"]v?(\d+)', 'parameter'),
            (r'api_version\s*=\s*[\'"]v?(\d+)', 'variable')
        ]
        
        for pattern, version_type in version_patterns:
            matches = re.findall(pattern, self.consolidated_code)
            if matches:
                analysis['has_versioning'] = True
                analysis['version_pattern'] = version_type
                analysis['versions_found'].extend(matches)
        
        analysis['versions_found'] = list(set(analysis['versions_found']))
        
        return analysis
    
    def analyze_endpoint_interactions(self, endpoint_path: str) -> Dict[str, Any]:
        """Analyze interactions for a specific endpoint."""
        # Find the endpoint
        target_endpoint = None
        for endpoint in self.endpoints:
            if endpoint['path'] == endpoint_path:
                target_endpoint = endpoint
                break
        
        if not target_endpoint:
            return {'error': 'Endpoint not found'}
        
        analysis = {
            'endpoint': target_endpoint,
            'request_model': None,
            'response_model': None,
            'database_operations': [],
            'external_calls': [],
            'validations': []
        }
        
        # Find handler function
        handler_pattern = rf'def\s+{target_endpoint["handler"]}\s*\([^)]*\):\s*\n((?:\s{{4,}}.*\n)*)'
        handler_match = re.search(handler_pattern, self.consolidated_code)
        
        if handler_match:
            handler_body = handler_match.group(1)
            
            # Analyze request/response models
            for model_type, models in self.models.items():
                for model in models:
                    if model['name'] in handler_body:
                        if 'request' in model['name'].lower():
                            analysis['request_model'] = model
                        elif 'response' in model['name'].lower():
                            analysis['response_model'] = model
            
            # Analyze database operations
            db_patterns = [
                (r'\.query\(', 'query'),
                (r'\.filter\(', 'filter'),
                (r'\.create\(', 'create'),
                (r'\.update\(', 'update'),
                (r'\.delete\(', 'delete'),
                (r'\.save\(', 'save')
            ]
            
            for pattern, operation in db_patterns:
                if re.search(pattern, handler_body):
                    analysis['database_operations'].append(operation)
            
            # Analyze external API calls
            api_patterns = [
                r'requests\.(get|post|put|delete)',
                r'http\.(get|post|put|delete)',
                r'fetch\(',
                r'axios\.'
            ]
            
            for pattern in api_patterns:
                matches = re.findall(pattern, handler_body)
                analysis['external_calls'].extend(matches)
            
            # Analyze validations
            validation_patterns = [
                r'validate\(',
                r'is_valid\(',
                r'check_\w+\(',
                r'verify_\w+\('
            ]
            
            for pattern in validation_patterns:
                if re.search(pattern, handler_body):
                    analysis['validations'].append(pattern)
        
        return analysis
    
    def generate_api_documentation(self) -> str:
        """Generate API documentation from analysis."""
        doc = "# API Documentation\n\n"
        
        # Group endpoints by type
        endpoints_by_type = defaultdict(list)
        for endpoint in self.endpoints:
            endpoints_by_type[endpoint['type']].append(endpoint)
        
        # Generate documentation for each type
        for endpoint_type, endpoints in endpoints_by_type.items():
            doc += f"## {endpoint_type.replace('_', ' ').title()}\n\n"
            
            for endpoint in endpoints:
                doc += f"### {' '.join(endpoint['methods'])} {endpoint['path']}\n"
                doc += f"- Handler: `{endpoint['handler']}`\n"
                doc += f"- Framework: {endpoint['framework']}\n"
                
                if endpoint.get('async'):
                    doc += "- Async: Yes\n"
                
                # Try to find more details
                interaction = self.analyze_endpoint_interactions(endpoint['path'])
                
                if interaction.get('request_model'):
                    doc += "\n**Request Model:**\n```json\n{\n"
                    for field in interaction['request_model'].get('fields', []):
                        doc += f'  "{field["name"]}": {field["type"]}'
                        if field.get('required'):
                            doc += ' (required)'
                        doc += ',\n'
                    doc += "}\n```\n"
                
                if interaction.get('response_model'):
                    doc += "\n**Response Model:**\n```json\n{\n"
                    for field in interaction['response_model'].get('fields', []):
                        doc += f'  "{field["name"]}": {field["type"]},\n'
                    doc += "}\n```\n"
                
                if interaction.get('database_operations'):
                    doc += f"\n**Database Operations:** {', '.join(interaction['database_operations'])}\n"
                
                doc += "\n---\n\n"
        
        # Add summary
        analysis = self.analyze_api_structure()
        doc += "## API Summary\n\n"
        doc += f"- Total Endpoints: {analysis['total_endpoints']}\n"
        doc += f"- Frameworks: {', '.join(analysis['frameworks_used'])}\n"
        doc += f"- RESTful Compliance Score: {analysis['restful_analysis']['compliance_score']}%\n"
        
        if analysis['authentication']['has_auth']:
            doc += f"- Authentication Types: {', '.join(analysis['authentication']['auth_types'])}\n"
            doc += f"- Protected Endpoints: {analysis['authentication']['protected_endpoints']}\n"
        
        if analysis['versioning']['has_versioning']:
            doc += f"- API Versions: {', '.join(analysis['versioning']['versions_found'])}\n"
        
        return doc
    
    def find_api_issues(self) -> List[Dict[str, Any]]:
        """Find potential API design issues."""
        issues = []
        
        # Check for missing authentication
        auth_analysis = self._analyze_authentication()
        if not auth_analysis['has_auth'] and len(self.endpoints) > 5:
            issues.append({
                'type': 'missing_authentication',
                'severity': 'high',
                'description': 'No authentication mechanism detected',
                'recommendation': 'Implement authentication for API security'
            })
        
        # Check for inconsistent naming
        path_styles = defaultdict(int)
        for endpoint in self.endpoints:
            if '-' in endpoint['path']:
                path_styles['kebab-case'] += 1
            elif '_' in endpoint['path']:
                path_styles['snake_case'] += 1
            else:
                path_styles['other'] += 1
        
        if len(path_styles) > 1:
            issues.append({
                'type': 'inconsistent_naming',
                'severity': 'low',
                'description': 'Multiple naming styles in API paths',
                'details': dict(path_styles),
                'recommendation': 'Use consistent naming convention for API paths'
            })
        
        # Check for missing error handling
        if not re.search(r'try:|except\s+\w+:|catch\s*\(', self.consolidated_code):
            issues.append({
                'type': 'missing_error_handling',
                'severity': 'medium',
                'description': 'No error handling detected in API code',
                'recommendation': 'Add proper error handling for API endpoints'
            })
        
        # Check for missing input validation
        validation_count = len(re.findall(r'validat|check_|verify_', self.consolidated_code, re.IGNORECASE))
        if validation_count < len(self.endpoints) * 0.5:
            issues.append({
                'type': 'insufficient_validation',
                'severity': 'high',
                'description': 'Insufficient input validation detected',
                'recommendation': 'Add input validation for all API endpoints'
            })
        
        # Check for hardcoded values
        hardcoded_patterns = [
            (r'api_key\s*=\s*[\'"][^\'"]+[\'"]', 'hardcoded_api_key'),
            (r'(?:password|secret)\s*=\s*[\'"][^\'"]+[\'"]', 'hardcoded_secret'),
            (r'(?:http://|https://)[^\s\'",]+', 'hardcoded_url')
        ]
        
        for pattern, issue_type in hardcoded_patterns:
            matches = re.findall(pattern, self.consolidated_code, re.IGNORECASE)
            if matches:
                issues.append({
                    'type': issue_type,
                    'severity': 'high',
                    'description': f'Hardcoded values detected: {issue_type}',
                    'count': len(matches),
                    'recommendation': 'Move sensitive values to environment variables'
                })
        
        return issues