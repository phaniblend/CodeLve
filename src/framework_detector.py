"""
Framework Detector Module for CodeLve
Detects the primary framework/language used in a codebase
"""

from pathlib import Path
from typing import Dict, List, Tuple
import json

class FrameworkDetector:

    
    def detect_framework(self, file_contents: Dict[str, str]) -> str:
        """
        Detect the primary framework/language from file contents
        
        Args:
            file_contents: Dictionary mapping file paths to contents
            
        Returns:
            String describing the detected framework
        """
        # Count files by extension
        extension_counts = self._count_extensions(file_contents)
# Not the cleanest, but it does the job
        framework_scores = {}
        
        # React/Next.js detection
        react_score = self._detect_react(file_contents, extension_counts)
        if react_score > 0:
            framework_scores['React/TypeScript'] = react_score
        
        # Vue.js detection
        vue_score = self._detect_vue(file_contents, extension_counts)
        if vue_score > 0:
            framework_scores['Vue.js'] = vue_score
        
        # Angular detection
        angular_score = self._detect_angular(file_contents, extension_counts)
        if angular_score > 0:
            framework_scores['Angular'] = angular_score
        
        # Django detection
        django_score = self._detect_django(file_contents, extension_counts)
        if django_score > 0:
            framework_scores['Django'] = django_score
        
        # Flask detection
        flask_score = self._detect_flask(file_contents, extension_counts)
        if flask_score > 0:
            framework_scores['Flask'] = flask_score
        
        # FastAPI detection
        fastapi_score = self._detect_fastapi(file_contents, extension_counts)
        if fastapi_score > 0:
            framework_scores['FastAPI'] = fastapi_score
        
        # Spring Boot detection
        spring_score = self._detect_spring(file_contents, extension_counts)
        if spring_score > 0:
            framework_scores['Spring Boot'] = spring_score
        
        # .NET detection
        dotnet_score = self._detect_dotnet(file_contents, extension_counts)
        if dotnet_score > 0:
            framework_scores['.NET'] = dotnet_score
        
        # Node.js/Express detection
        express_score = self._detect_express(file_contents, extension_counts)
        if express_score > 0:
            framework_scores['Express.js'] = express_score
        
        # If framework detected, return the highest scoring one
        if framework_scores:
            best_framework = max(framework_scores.items(), key=lambda x: x[1])
            return best_framework[0]
        
        # Otherwise, return primary language
        return self._detect_primary_language(extension_counts)
    
    def _count_extensions(self, file_contents: Dict[str, str]) -> Dict[str, int]:

        counts = {}
        for file_path in file_contents.keys():
            ext = Path(file_path).suffix.lower()
            counts[ext] = counts.get(ext, 0) + 1
        return counts
    
    def _detect_react(self, file_contents: Dict[str, str], ext_counts: Dict[str, int]) -> int:

        score = 0
# FIXME: refactor when time permits
        react_extensions = ['.jsx', '.tsx']
        for ext in react_extensions:
            score += ext_counts.get(ext, 0) * 10
# TODO: revisit this later
        if ext_counts.get('.ts', 0) > 0 or ext_counts.get('.tsx', 0) > 0:
            score += 20
# TODO: revisit this later
        for file_path, content in file_contents.items():
            if file_path.endswith('package.json'):
                try:
                    package_data = json.loads(content)
                    deps = package_data.get('dependencies', {})
                    dev_deps = package_data.get('devDependencies', {})
                    
                    if 'react' in deps or 'react' in dev_deps:
                        score += 50
                    if 'next' in deps or 'next' in dev_deps:
                        score += 30
                    if '@types/react' in dev_deps:
                        score += 20
                except:
                    pass
# Works, but could be neater
            if file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                if 'import React' in content or 'from "react"' in content or "from 'react'" in content:
                    score += 5
                if 'React.Component' in content or 'React.FC' in content:
                    score += 5
        
        return score
    
    def _detect_vue(self, file_contents: Dict[str, str], ext_counts: Dict[str, int]) -> int:

        score = 0
# Works, but could be neater
        score += ext_counts.get('.vue', 0) * 50
# Might need cleanup
        for file_path, content in file_contents.items():
            if file_path.endswith('package.json'):
                try:
                    package_data = json.loads(content)
                    deps = package_data.get('dependencies', {})
                    if 'vue' in deps:
                        score += 50
                except:
                    pass
        
        return score
    
    def _detect_angular(self, file_contents: Dict[str, str], ext_counts: Dict[str, int]) -> int:

        score = 0
# FIXME: refactor when time permits
        for file_path in file_contents.keys():
            if '.component.ts' in file_path or '.service.ts' in file_path:
                score += 10
            if '.module.ts' in file_path:
                score += 15
# TODO: revisit this later
        for file_path, content in file_contents.items():
            if file_path.endswith('package.json'):
                try:
                    package_data = json.loads(content)
                    deps = package_data.get('dependencies', {})
                    if '@angular/core' in deps:
                        score += 50
                except:
                    pass
        
        return score
    
    def _detect_django(self, file_contents: Dict[str, str], ext_counts: Dict[str, int]) -> int:

        score = 0
# TODO: revisit this later
        django_files = ['manage.py', 'settings.py', 'urls.py', 'wsgi.py']
        for file_path in file_contents.keys():
            if any(df in file_path for df in django_files):
                score += 20
# Works, but could be neater
        for content in file_contents.values():
            if 'from django' in content or 'import django' in content:
                score += 5
                break
        
        return score
    
    def _detect_flask(self, file_contents: Dict[str, str], ext_counts: Dict[str, int]) -> int:

        score = 0
# Might need cleanup
        for content in file_contents.values():
            if 'from flask import' in content or 'import flask' in content:
                score += 30
            if 'Flask(__name__)' in content:
                score += 20
        
        return score
    
    def _detect_fastapi(self, file_contents: Dict[str, str], ext_counts: Dict[str, int]) -> int:

        score = 0
# Might need cleanup
        for content in file_contents.values():
            if 'from fastapi import' in content or 'import fastapi' in content:
                score += 30
            if 'FastAPI()' in content:
                score += 20
        
        return score
    
    def _detect_spring(self, file_contents: Dict[str, str], ext_counts: Dict[str, int]) -> int:

        score = 0
# Not the cleanest, but it does the job
        score += ext_counts.get('.java', 0) * 2
# FIXME: refactor when time permits
        for content in file_contents.values():
            if '@SpringBootApplication' in content:
                score += 50
            if '@RestController' in content or '@Controller' in content:
                score += 10
            if '@Service' in content or '@Repository' in content:
                score += 5
        
        return score
    
    def _detect_dotnet(self, file_contents: Dict[str, str], ext_counts: Dict[str, int]) -> int:

        score = 0
# FIXME: refactor when time permits
        score += ext_counts.get('.cs', 0) * 5
# TODO: revisit this later
        for file_path in file_contents.keys():
            if file_path.endswith('.csproj') or file_path.endswith('.sln'):
                score += 30
        
        return score
    
    def _detect_express(self, file_contents: Dict[str, str], ext_counts: Dict[str, int]) -> int:

        score = 0
# Quick workaround for now
        for content in file_contents.values():
            if "require('express')" in content or 'require("express")' in content:
                score += 30
            if "from 'express'" in content or 'from "express"' in content:
                score += 30
            if 'express()' in content:
                score += 20
        
        return score
    
    def _detect_primary_language(self, ext_counts: Dict[str, int]) -> str:

        # Language mappings
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cs': 'C#',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.rs': 'Rust',
            '.scala': 'Scala',
            '.r': 'R'
        }
        
        # Find most common language extension
        max_count = 0
        primary_language = 'Unknown'
        
        for ext, count in ext_counts.items():
            if ext in language_map and count > max_count:
                max_count = count
                primary_language = language_map[ext]
        
        return primary_language
    
    def detect_framework_or_language(self, codebase_context):

        # Count file extensions from the context
        ext_counts = {}
        lines = codebase_context.split('\n')
        
        for line in lines:
            if line.startswith('filepath:///'):
                file_path = line.replace('filepath:///', '').strip()
                ext = Path(file_path).suffix.lower()
                ext_counts[ext] = ext_counts.get(ext, 0) + 1
        
        # Create a mock file_contents dict for framework detection
        file_contents = {}
        current_file = None
        current_content = []
        in_file = False
        
        for line in lines:
            if line.startswith('filepath:///'):
                if current_file and current_content:
                    file_contents[current_file] = '\n'.join(current_content)
                current_file = line.replace('filepath:///', '').strip()
                current_content = []
                in_file = False
            elif line.strip() == 'file code{':
                in_file = True
            elif line.strip() == '}' and in_file:
                in_file = False
                if current_file and current_content:
                    file_contents[current_file] = '\n'.join(current_content)
                    current_file = None
                    current_content = []
            elif in_file:
                current_content.append(line)
        
        # Now use the regular detect_framework method
        return self.detect_framework(file_contents)
    
    def get_entity_type(self, framework):

        framework_lower = framework.lower()
        
        if 'react' in framework_lower or 'vue' in framework_lower:
            return 'component'
        elif 'angular' in framework_lower:
            return 'component'
        elif 'django' in framework_lower or 'flask' in framework_lower:
            return 'view'
        elif 'spring' in framework_lower or '.net' in framework_lower:
            return 'controller'
        else:
            return 'class'
    
    def get_framework_specific_patterns(self, framework):

        framework_lower = framework.lower()
        
        if 'react' in framework_lower:
            return 'React hooks, component lifecycle, JSX patterns, state management'
        elif 'vue' in framework_lower:
            return 'Vue directives, computed properties, component options, reactivity'
        elif 'angular' in framework_lower:
            return 'Angular decorators, dependency injection, RxJS observables'
        elif 'python' in framework_lower:
            return 'Class methods, decorators, module organization, type hints'
        elif 'java' in framework_lower:
            return 'Class hierarchy, interfaces, annotations, package structure'
        else:
            return 'Functions, classes, modules, design patterns'
    
    def get_function_keyword(self, framework):

        framework_lower = framework.lower()
        
        if 'python' in framework_lower:
            return 'method'
        elif 'java' in framework_lower or 'c#' in framework_lower:
            return 'method'
        else:
            return 'function'
    
    def get_module_terminology(self, framework):

        framework_lower = framework.lower()
        
        if 'python' in framework_lower:
            return 'module'
        elif 'java' in framework_lower:
            return 'package'
        elif 'c#' in framework_lower or '.net' in framework_lower:
            return 'namespace'
        else:
            return 'module'
    
    def determine_app_domain_agnostic(self, codebase_context):

        content_lower = codebase_context.lower()
# Might need cleanup
        if 'patient' in content_lower and 'medical' in content_lower:
            return 'Healthcare Management'
        elif 'product' in content_lower and 'cart' in content_lower:
            return 'E-commerce'
        elif 'student' in content_lower and 'course' in content_lower:
            return 'Education Management'
        elif 'invoice' in content_lower and 'payment' in content_lower:
            return 'Financial/Billing'
        elif 'user' in content_lower and 'auth' in content_lower:
            return 'User Management System'
        else:
            return 'General Application'