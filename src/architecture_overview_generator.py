"""
Architecture Overview Generator for CodeLve
Generates business-focused system overviews for new developers
"""

from pathlib import Path

class ArchitectureOverviewGenerator:
    """Generate business-focused architecture overviews"""
    
    def __init__(self, framework_detector):
        self.framework_detector = framework_detector
    
    def generate_system_overview(self, index_data, framework, codebase_context):
        """Generate a comprehensive system overview for new developers"""
        
        # Analyze the system's business domain
        domain_info = self._analyze_business_domain(codebase_context, index_data)
        
        # Identify main functional areas
        functional_areas = self._identify_functional_areas(index_data['modules'], codebase_context)
        
        # Map technical components to business functions
        component_mapping = self._map_components_to_business(functional_areas, index_data)
        
        # Generate the overview
        overview = f"""# 🎯 **System Overview: {domain_info['system_name']}**

## 📋 **What This System Does**
{domain_info['description']}

## 🏢 **Business Purpose**
{domain_info['business_purpose']}

## 🗺️ **System Map - Where to Start**

```
{self._generate_system_map(functional_areas)}
```

## 🚀 **Quick Navigation Guide**

### **For New Developers - Start Here:**

1. **Understanding the Domain**
   - **Start with**: `models/` folder to understand data structures
   - **Key Concepts**: {', '.join(domain_info['key_concepts'])}
   - **Business Rules**: Located in service layer (`apis/*Service.ts`)

2. **Main User Journeys**
{self._format_user_journeys(functional_areas)}

3. **Core Components by Business Function**
{self._format_component_guide(component_mapping)}

## 📁 **Where Everything Lives**

### **By Business Function:**
{self._format_directory_guide(functional_areas, index_data)}

### **By Technical Layer:**
- **User Interface**: `components/pages/` - All user-facing screens
- **Business Logic**: `apis/*Service.ts` - Core business operations  
- **Data Models**: `models/` - TypeScript interfaces and types
- **Shared Utilities**: `utils/` - Common helper functions

## 🔄 **How Things Connect**

### **Typical Request Flow:**
```
User Action → Page Component → API Service → Backend → Response → UI Update
```

### **Example: Creating an Equipment Entry**
1. User fills form in `components/pages/Equipment/AddEquipment.tsx`
2. Form submits to `apis/equipmentService.ts`
3. Service calls backend API endpoint
4. Response updates Redux store
5. UI reflects new equipment in list

## 💡 **Key Technical Decisions**

{self._analyze_technical_decisions(codebase_context, framework)}

## 🎓 **Learning Path for This Codebase**

### **Week 1: Understand the Domain**
- [ ] Read through main models in `models/api/`
- [ ] Explore one complete feature (e.g., Applicant management)
- [ ] Trace a user action from UI to API

### **Week 2: Make Your First Change**
- [ ] Pick a simple bug or enhancement
- [ ] Follow existing patterns in similar components
- [ ] Test your changes thoroughly

### **Week 3: Contribute Meaningfully**
- [ ] Understand the business context of your tasks
- [ ] Propose improvements based on patterns you've learned
- [ ] Help document unclear areas

---

**🎯 Remember**: This is an {domain_info['industry']} system. Understanding the business context is as important as the technical implementation.
"""
        
        return overview
    
    def _analyze_business_domain(self, codebase_context, index_data):
        """Analyze the business domain from code patterns"""
        content_lower = codebase_context.lower()
        
        # Detect domain based on common terms
        domain_info = {
            'system_name': 'System',
            'description': '',
            'business_purpose': '',
            'industry': 'Business',
            'key_concepts': []
        }
        
        # Environmental compliance system detection
        if 'equipment' in content_lower and 'emission' in content_lower:
            domain_info['system_name'] = 'Environmental Compliance & Equipment Management System'
            domain_info['description'] = """This system manages environmental compliance for equipment and vehicles, tracking emissions, 
implementing grant programs (Carl Moyer, Community Air Protection), and ensuring regulatory compliance for air quality standards."""
            domain_info['business_purpose'] = """Enable organizations to:
- Track and manage equipment emissions data
- Apply for and manage environmental grants
- Ensure compliance with air quality regulations  
- Generate reports for regulatory agencies
- Manage equipment lifecycle and replacements"""
            domain_info['industry'] = 'Environmental Compliance'
            domain_info['key_concepts'] = [
                'Equipment', 'Emissions', 'Grants', 'Compliance', 
                'Carl Moyer Program', 'Air Quality', 'Funding'
            ]
        
        # E-commerce system detection
        elif 'product' in content_lower and ('cart' in content_lower or 'order' in content_lower):
            domain_info['system_name'] = 'E-Commerce Platform'
            domain_info['description'] = """This system manages online shopping, product catalogs, orders, and customer interactions."""
            domain_info['business_purpose'] = """Enable businesses to:
- Sell products online
- Manage inventory and orders
- Process payments securely
- Handle customer accounts
- Track shipments and returns"""
            domain_info['industry'] = 'E-Commerce'
            domain_info['key_concepts'] = [
                'Products', 'Orders', 'Cart', 'Customers', 
                'Payments', 'Inventory', 'Shipping'
            ]
        
        # Healthcare system detection
        elif 'patient' in content_lower and ('appointment' in content_lower or 'medical' in content_lower):
            domain_info['system_name'] = 'Healthcare Management System'
            domain_info['description'] = """This system manages patient records, appointments, medical data, and healthcare workflows."""
            domain_info['business_purpose'] = """Enable healthcare providers to:
- Manage patient records securely
- Schedule appointments efficiently
- Track medical history
- Process insurance claims
- Coordinate care between providers"""
            domain_info['industry'] = 'Healthcare'
            domain_info['key_concepts'] = [
                'Patients', 'Appointments', 'Medical Records', 'Providers', 
                'Insurance', 'Prescriptions', 'Care Plans'
            ]
        
        # Financial system detection
        elif 'account' in content_lower and ('transaction' in content_lower or 'payment' in content_lower):
            domain_info['system_name'] = 'Financial Management System'
            domain_info['description'] = """This system manages financial accounts, transactions, payments, and reporting."""
            domain_info['business_purpose'] = """Enable organizations to:
- Track financial transactions
- Manage accounts and balances
- Process payments and transfers
- Generate financial reports
- Ensure regulatory compliance"""
            domain_info['industry'] = 'Financial Services'
            domain_info['key_concepts'] = [
                'Accounts', 'Transactions', 'Payments', 'Reports', 
                'Compliance', 'Balances', 'Statements'
            ]
        
        # Extract more specific concepts from module names
        for module_name in index_data['modules']:
            module_lower = module_name.lower()
            
            # Common business concepts
            if 'user' in module_lower and 'Users' not in domain_info['key_concepts']:
                domain_info['key_concepts'].append('Users')
            if 'dashboard' in module_lower and 'Dashboard' not in domain_info['key_concepts']:
                domain_info['key_concepts'].append('Dashboard')
            if 'report' in module_lower and 'Reports' not in domain_info['key_concepts']:
                domain_info['key_concepts'].append('Reports')
            if 'api' in module_lower and 'APIs' not in domain_info['key_concepts']:
                domain_info['key_concepts'].append('APIs')
        
        # Remove duplicates and limit
        domain_info['key_concepts'] = list(set(domain_info['key_concepts']))[:10]
        
        return domain_info
    
    def _identify_functional_areas(self, modules, codebase_context):
        """Identify main functional areas of the system"""
        functional_areas = {}
        
        # Analyze module names and group by function
        for module_name, module_info in modules.items():
            path_parts = Path(module_info['path']).parts
            module_lower = module_name.lower()
            
            # Equipment Management
            if any(term in module_lower for term in ['equipment', 'vehicle', 'engine']):
                if 'Equipment Management' not in functional_areas:
                    functional_areas['Equipment Management'] = {
                        'modules': [],
                        'description': 'Manage equipment lifecycle, specifications, and compliance',
                        'key_files': []
                    }
                functional_areas['Equipment Management']['modules'].append(module_name)
            
            # Grant Management  
            elif any(term in module_lower for term in ['grant', 'funding', 'moyer', 'disbursement']):
                if 'Grant Management' not in functional_areas:
                    functional_areas['Grant Management'] = {
                        'modules': [],
                        'description': 'Handle grant applications, funding, and disbursements',
                        'key_files': []
                    }
                functional_areas['Grant Management']['modules'].append(module_name)
            
            # Applicant Management
            elif 'applicant' in module_lower:
                if 'Applicant Management' not in functional_areas:
                    functional_areas['Applicant Management'] = {
                        'modules': [],
                        'description': 'Manage applicant profiles, applications, and documentation',
                        'key_files': []
                    }
                functional_areas['Applicant Management']['modules'].append(module_name)
            
            # User Management
            elif any(term in module_lower for term in ['user', 'auth', 'login', 'profile']):
                if 'User Management' not in functional_areas:
                    functional_areas['User Management'] = {
                        'modules': [],
                        'description': 'Handle user accounts, authentication, and authorization',
                        'key_files': []
                    }
                functional_areas['User Management']['modules'].append(module_name)
            
            # Reporting & Compliance
            elif any(term in module_lower for term in ['report', 'compliance', 'attachment', 'document']):
                if 'Reporting & Compliance' not in functional_areas:
                    functional_areas['Reporting & Compliance'] = {
                        'modules': [],
                        'description': 'Generate reports and ensure regulatory compliance',
                        'key_files': []
                    }
                functional_areas['Reporting & Compliance']['modules'].append(module_name)
            
            # Dashboard & Analytics
            elif any(term in module_lower for term in ['dashboard', 'analytics', 'metrics', 'chart']):
                if 'Dashboard & Analytics' not in functional_areas:
                    functional_areas['Dashboard & Analytics'] = {
                        'modules': [],
                        'description': 'Visualize data and provide business insights',
                        'key_files': []
                    }
                functional_areas['Dashboard & Analytics']['modules'].append(module_name)
            
            # API & Integration
            elif any(term in module_lower for term in ['api', 'service', 'integration', 'webhook']):
                if 'API & Integration' not in functional_areas:
                    functional_areas['API & Integration'] = {
                        'modules': [],
                        'description': 'External system integration and API management',
                        'key_files': []
                    }
                functional_areas['API & Integration']['modules'].append(module_name)
        
        # Add key files for each area (top 5 modules)
        for area_name, area_info in functional_areas.items():
            area_info['key_files'] = area_info['modules'][:5]
        
        return functional_areas
    
    def _generate_system_map(self, functional_areas):
        """Generate ASCII system map based on detected functional areas"""
        
        # Default map for environmental compliance system
        if 'Equipment Management' in functional_areas and 'Grant Management' in functional_areas:
            return """┌─────────────────────────────────────────────────────────────────┐
│                 Environmental Compliance System                  │
├─────────────────────────┬───────────────────┬──────────────────┤
│   Applicant Portal      │  Grant Management │    Equipment     │
│   ┌─────────────┐      │  ┌─────────────┐ │  ┌─────────────┐ │
│   │ Registration│      │  │   Carl      │ │  │  Equipment  │ │
│   │ Application │      │  │   Moyer     │ │  │  Database   │ │
│   │ Documents   │      │  │   Program   │ │  │  Tracking   │ │
│   └─────────────┘      │  └─────────────┘ │  └─────────────┘ │
│                        │  ┌─────────────┐ │  ┌─────────────┐ │
│                        │  │ Community   │ │  │  Emission   │ │
│                        │  │ Air Protect │ │  │  Reporting  │ │
│                        │  └─────────────┘ │  └─────────────┘ │
├────────────────────────┴───────────────────┴──────────────────┤
│                    Shared Services & APIs                       │
│  Authentication │ Notifications │ Document Management │ Reports │
└─────────────────────────────────────────────────────────────────┘"""
        
        # Generic business application map
        else:
            areas = list(functional_areas.keys())[:4]  # Top 4 areas
            return f"""┌─────────────────────────────────────────────────────────────────┐
│                      Business Application                        │
├─────────────────────────┬────────────────────────────────────────┤
│   {areas[0] if len(areas) > 0 else 'Core Module':<20} │   {areas[1] if len(areas) > 1 else 'Supporting Module':<20}    │
├─────────────────────────┼────────────────────────────────────────┤
│   {areas[2] if len(areas) > 2 else 'Data Layer':<20} │   {areas[3] if len(areas) > 3 else 'Integration Layer':<20}    │
├─────────────────────────┴────────────────────────────────────────┤
│                    Infrastructure & Utilities                     │
└─────────────────────────────────────────────────────────────────┘"""
    
    def _format_user_journeys(self, functional_areas):
        """Format main user journeys based on functional areas"""
        journeys = []
        
        if 'Applicant Management' in functional_areas:
            journeys.append("""   **📝 Applicant Journey**
   - Register → Apply for Grant → Submit Documents → Track Status
   - **Start at**: `components/pages/Applicant/`""")
        
        if 'Equipment Management' in functional_areas:
            journeys.append("""   **🚛 Equipment Journey**  
   - Add Equipment → Track Emissions → Apply for Replacement → Report Compliance
   - **Start at**: `components/pages/Equipment/`""")
        
        if 'Grant Management' in functional_areas:
            journeys.append("""   **💰 Grant Journey**
   - Create Program → Review Applications → Approve Funding → Disburse Funds
   - **Start at**: `components/pages/Grant/` or specific program folders""")
        
        if 'User Management' in functional_areas:
            journeys.append("""   **👤 User Journey**
   - Register → Login → Manage Profile → Access Features
   - **Start at**: `components/pages/User/` or `auth/`""")
        
        if 'Dashboard & Analytics' in functional_areas:
            journeys.append("""   **📊 Analytics Journey**
   - Login → View Dashboard → Analyze Metrics → Generate Reports
   - **Start at**: `components/pages/Dashboard/`""")
        
        # If no specific journeys found, provide generic journey
        if not journeys:
            journeys.append("""   **🔄 Generic User Journey**
   - Login → Access Features → Perform Actions → View Results
   - **Start at**: `components/pages/`""")
        
        return '\n\n'.join(journeys)
    
    def _format_component_guide(self, component_mapping):
        """Format component guide by business function"""
        guide_lines = []
        
        for function, components in component_mapping.items():
            guide_lines.append(f"**{function}:**")
            for comp in components[:3]:  # Top 3 components
                guide_lines.append(f"- `{comp['name']}` - {comp['purpose']}")
            if len(components) > 3:
                guide_lines.append(f"- ...and {len(components) - 3} more components")
            guide_lines.append("")
        
        return '\n'.join(guide_lines)
    
    def _map_components_to_business(self, functional_areas, index_data):
        """Map technical components to business functions"""
        mapping = {}
        
        for area_name, area_info in functional_areas.items():
            components = []
            
            for module_name in area_info['modules'][:5]:  # Top 5 modules
                if module_name in index_data['modules']:
                    module_info = index_data['modules'][module_name]
                    components.append({
                        'name': module_name,
                        'path': module_info['path'],
                        'purpose': self._infer_component_purpose(module_name, module_info)
                    })
            
            mapping[area_name] = components
        
        return mapping
    
    def _infer_component_purpose(self, module_name, module_info):
        """Infer the purpose of a component from its name and content"""
        name_lower = module_name.lower()
        
        # Service layer components
        if 'service' in name_lower:
            if 'api' in name_lower:
                return "External API integration and data fetching"
            elif 'auth' in name_lower:
                return "Authentication and authorization logic"
            else:
                return "Business logic and data processing"
        
        # Form components
        elif any(term in name_lower for term in ['form', 'add', 'create', 'new']):
            return "Data entry and form validation"
        
        # List/Search components
        elif any(term in name_lower for term in ['list', 'search', 'table', 'grid']):
            return "Data display and search functionality"
        
        # Detail/View components
        elif any(term in name_lower for term in ['detail', 'view', 'info', 'display']):
            return "Detailed information display"
        
        # Dashboard components
        elif 'dashboard' in name_lower:
            return "Data visualization and metrics display"
        
        # Configuration components
        elif any(term in name_lower for term in ['config', 'settings', 'setup']):
            return "Configuration and settings management"
        
        # Utility components
        elif any(term in name_lower for term in ['util', 'helper', 'common']):
            return "Shared utilities and helper functions"
        
        # Model/Type definitions
        elif any(term in name_lower for term in ['model', 'type', 'interface', 'schema']):
            return "Data structure definitions"
        
        else:
            # Try to infer from imports/exports
            if 'exports' in module_info and module_info['exports']:
                export_count = len(module_info['exports'])
                if export_count > 5:
                    return "Multi-purpose module with various exports"
                elif export_count == 1:
                    return "Single-purpose component or utility"
            
            return "Specialized component functionality"
    
    def _format_directory_guide(self, functional_areas, index_data):
        """Format directory guide by business function"""
        guide = []
        
        # Group files by directory
        dir_groups = {}
        for module_name, module_info in index_data['modules'].items():
            path_parts = Path(module_info['path']).parts
            if len(path_parts) > 1:
                dir_name = path_parts[-2]
                if dir_name not in dir_groups:
                    dir_groups[dir_name] = []
                dir_groups[dir_name].append(module_name)
        
        # Format by function
        for area_name, area_info in functional_areas.items():
            guide.append(f"**{area_name}:**")
            
            # Find relevant directories
            relevant_dirs = set()
            for module in area_info['modules']:
                if module in index_data['modules']:
                    path_parts = Path(index_data['modules'][module]['path']).parts
                    if len(path_parts) > 1:
                        relevant_dirs.add(path_parts[-2])
            
            # Sort directories by relevance (number of related files)
            dir_relevance = {}
            for dir_name in relevant_dirs:
                if dir_name in dir_groups:
                    dir_relevance[dir_name] = len(dir_groups[dir_name])
            
            sorted_dirs = sorted(dir_relevance.items(), key=lambda x: x[1], reverse=True)
            
            for dir_name, file_count in sorted_dirs[:5]:
                guide.append(f"- `{dir_name}/` - {file_count} files")
            
            if len(sorted_dirs) > 5:
                guide.append(f"- ...and {len(sorted_dirs) - 5} more directories")
            
            guide.append("")
        
        return '\n'.join(guide)
    
    def _analyze_technical_decisions(self, codebase_context, framework):
        """Analyze and explain key technical decisions"""
        decisions = []
        content_lower = codebase_context.lower()
        
        # Framework choice
        if 'react' in framework.lower():
            decisions.append("- **Framework**: React with TypeScript - Type-safe, component-based UI development")
        elif 'vue' in framework.lower():
            decisions.append("- **Framework**: Vue.js - Progressive, approachable frontend framework")
        elif 'angular' in framework.lower():
            decisions.append("- **Framework**: Angular - Full-featured enterprise framework")
        else:
            decisions.append(f"- **Framework**: {framework} - Modern development framework")
        
        # State management
        if 'redux' in content_lower:
            decisions.append("- **State Management**: Redux - Predictable state container for complex apps")
        elif 'mobx' in content_lower:
            decisions.append("- **State Management**: MobX - Simple, scalable state management")
        elif 'vuex' in content_lower:
            decisions.append("- **State Management**: Vuex - Centralized state management for Vue")
        elif 'context' in content_lower and 'react' in framework.lower():
            decisions.append("- **State Management**: React Context API - Built-in state sharing")
        
        # Authentication
        if 'okta' in content_lower:
            decisions.append("- **Authentication**: Okta - Enterprise-grade identity management")
        elif 'auth0' in content_lower:
            decisions.append("- **Authentication**: Auth0 - Flexible authentication platform")
        elif 'firebase' in content_lower and 'auth' in content_lower:
            decisions.append("- **Authentication**: Firebase Auth - Google's authentication service")
        elif 'jwt' in content_lower:
            decisions.append("- **Authentication**: JWT tokens - Stateless authentication")
        
        # API communication
        if 'axios' in content_lower:
            decisions.append("- **API Client**: Axios - Promise-based HTTP client with interceptors")
        elif 'fetch' in content_lower:
            decisions.append("- **API Client**: Fetch API - Native browser API for HTTP requests")
        elif 'graphql' in content_lower:
            decisions.append("- **API Style**: GraphQL - Flexible query language for APIs")
        
        # UI components
        if 'primereact' in content_lower:
            decisions.append("- **UI Library**: PrimeReact - Rich set of UI components")
        elif 'material-ui' in content_lower or 'mui' in content_lower:
            decisions.append("- **UI Library**: Material-UI - Google's Material Design components")
        elif 'antd' in content_lower or 'ant-design' in content_lower:
            decisions.append("- **UI Library**: Ant Design - Enterprise-focused design language")
        elif 'bootstrap' in content_lower:
            decisions.append("- **UI Library**: Bootstrap - Popular responsive design framework")
        
        # Testing
        if 'jest' in content_lower:
            decisions.append("- **Testing**: Jest - JavaScript testing framework")
        if 'cypress' in content_lower:
            decisions.append("- **E2E Testing**: Cypress - Modern end-to-end testing")
        if 'testing-library' in content_lower:
            decisions.append("- **Testing Utils**: Testing Library - User-centric testing utilities")
        
        # Build tools
        if 'webpack' in content_lower:
            decisions.append("- **Bundler**: Webpack - Powerful module bundler")
        elif 'vite' in content_lower:
            decisions.append("- **Build Tool**: Vite - Lightning-fast frontend tooling")
        elif 'create-react-app' in content_lower or 'react-scripts' in content_lower:
            decisions.append("- **Build Setup**: Create React App - Zero-config React setup")
        
        # Code quality
        if 'eslint' in content_lower:
            decisions.append("- **Linting**: ESLint - JavaScript/TypeScript code quality")
        if 'prettier' in content_lower:
            decisions.append("- **Formatting**: Prettier - Opinionated code formatter")
        
        # Only show top 8 decisions to keep it focused
        return '\n'.join(decisions[:8])