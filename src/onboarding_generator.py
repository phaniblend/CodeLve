"""
Enhanced Developer Onboarding Guide Generator for CodeLve
Generates comprehensive onboarding documentation with practical examples
"""

import re
from pathlib import Path

class OnboardingGenerator:

    
    def __init__(self, framework_detector):
    # Works, but could be neater
        self.framework_detector = framework_detector
    
    def generate_enhanced_onboarding_guide(self, index_data, framework, codebase_context):

        modules = index_data['modules']
        architecture = index_data['architecture']
        stats = index_data['stats']
        
        # Analyze the codebase to understand the project
        project_info = self._check_project_info(codebase_context)
        tech_stack = self._check_tech_stack(codebase_context, modules)
        
        guide = f"""# 🚀 Enhanced Developer Onboarding Guide
## {project_info['project_type']}

---



### Prerequisites Check
- [ ] Node.js version: {project_info.get('node_version', '14.x or higher')}
- [ ] npm/yarn installed
- [ ] IDE with TypeScript support (VS Code recommended)
- [ ] Git access to repository
{self._generate_auth_prerequisites(codebase_context)}

### Initial Setup Commands
```bash
# Clone the repository
git clone [repository-url]
cd [project-name]

# Install dependencies
npm install  # or yarn install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your credentials:
{self._generate_env_template(codebase_context)}

# Start development server
npm start  # Runs on http://localhost:3000
```

---

## 🏗️ Architecture Deep Dive

### Data Flow Diagram
{self._generate_data_flow_diagram(architecture, codebase_context)}

### State Management Architecture
{self._generate_state_management_diagram(codebase_context)}

---



{self._generate_common_scenarios(codebase_context, framework)}

---

## 🛠️ Code Patterns & Best Practices

{self._generate_code_patterns(codebase_context, framework)}

---

## 🐛 Debugging Guide

{self._generate_debugging_guide(codebase_context, framework)}

---



{self._generate_project_knowledge(codebase_context, modules)}

---

## 🔧 Development Tools & Commands

### Useful Scripts
```bash
# Development
npm start              # Start dev server
npm run build         # Build for production
npm test              # Run tests
npm run lint          # Run ESLint
npm run type-check    # Run TypeScript compiler

# Debugging
npm run analyze       # Bundle size analyzer
npm run why [package] # Check why a package is installed
```

### VS Code Extensions (Recommended)
- ESLint
- Prettier
- TypeScript Error Lens
- React Developer Tools
- Redux DevTools

### Browser Extensions
- React Developer Tools
- Redux DevTools
{self._generate_framework_specific_tools(framework)}

---

## 📚 Quick Reference

### File Naming Conventions
{self._generate_naming_conventions(codebase_context)}

### Import Order
{self._generate_import_order_example(framework)}

### Git Commit Message Format
```
type(scope): subject

Examples:
feat(applicant): add phone number field to form
fix(auth): resolve token refresh issue
docs(readme): update setup instructions
```

---

## 🚨 When You're Stuck

### Internal Resources
1. **Similar Patterns**: Search codebase for similar implementations
2. **Test Files**: Look for `*.test.tsx` files for usage examples
3. **Type Definitions**: Check `models/` folder for data structures

### Debugging Checklist
- [ ] Check browser console for errors
- [ ] Verify network requests in DevTools
- [ ] Confirm data structure matches TypeScript types
- [ ] Check if similar feature works correctly
- [ ] Verify environment variables are set
- [ ] Clear browser cache and localStorage

### Key Contacts
- **Architecture Questions**: [Lead Developer]
- **Business Logic**: [Product Owner]
- **DevOps/Deployment**: [DevOps Team]
- **UI/UX Questions**: [Design Team]

---

## 📈 Performance Optimization Tips

{self._generate_performance_tips(framework)}

---

This guide should significantly reduce trial-and-error debugging by providing:
1. Concrete code examples for common scenarios
2. Debugging strategies with specific solutions
3. Clear patterns to follow
4. Troubleshooting checklist
5. Performance considerations

Remember: When in doubt, find a similar working example in the codebase and adapt it to your needs!"""
        
        return guide
    
    def _check_project_info(self, codebase_context):

        content_lower = codebase_context.lower()
        
        project_info = {
            'project_type': self._determine_project_type(codebase_context),
            'has_typescript': '.tsx' in content_lower or '.ts' in content_lower,
            'has_tests': 'test' in content_lower or 'spec' in content_lower,
            'uses_docker': 'dockerfile' in content_lower,
            'node_version': self._get_node_version(codebase_context)
        }
        
        return project_info
    
    def _determine_project_type(self, codebase_context):

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
    
    def _get_node_version(self, codebase_context):

        # Look for engines field in package.json
        if '"engines"' in codebase_context:
            match = re.search(r'"node":\s*"([^"]+)"', codebase_context)
            if match:
                return match.group(1)
        return "14.x or higher"
    
    def _generate_auth_prerequisites(self, codebase_context):

        content_lower = codebase_context.lower()
        auth_prereqs = []
        
        if 'okta' in content_lower:
            auth_prereqs.append("- [ ] Okta developer account credentials")
        if 'auth0' in content_lower:
            auth_prereqs.append("- [ ] Auth0 account access")
        if 'firebase' in content_lower:
            auth_prereqs.append("- [ ] Firebase project access")
            
        return '\n'.join(auth_prereqs)
    
    def _generate_env_template(self, codebase_context):

        content_lower = codebase_context.lower()
        env_vars = []
        
        # Common patterns
        if 'react_app_' in content_lower:
            env_vars.append("# REACT_APP_API_BASE_URL=http://localhost:8080")
        if 'okta' in content_lower:
            env_vars.extend([
                "# REACT_APP_OKTA_CLIENT_ID=your_client_id",
                "# REACT_APP_OKTA_DOMAIN=your_domain"
            ])
        if 'database_url' in content_lower:
            env_vars.append("# DATABASE_URL=postgresql://user:pass@localhost:5432/db")
        
        return '\n'.join(env_vars) if env_vars else "# Add your environment variables here"
    
    def _generate_data_flow_diagram(self, architecture, codebase_context):

        return """```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   Browser   │────▶│  App.tsx     │────▶│  AppRoutes  │────▶│ Page         │
│   Request   │     │  (Providers) │     │  (Routing)  │     │ Components   │
└─────────────┘     └──────────────┘     └─────────────┘     └──────┬───────┘
                                                                      │
                    ┌──────────────┐     ┌─────────────┐     ┌──────▼───────┐
                    │   Backend    │◀────│ Axios       │◀────│ API Services │
                    │   Server     │     │ Instance    │     │ (*Service.ts)│
                    └──────────────┘     └─────────────┘     └──────────────┘
```"""
    
    def _generate_state_management_diagram(self, codebase_context):

        content_lower = codebase_context.lower()
        
        if 'redux' in content_lower:
            return """```
Global State (Redux)              Local State (React)         Server State
├── User Info                    ├── Form Data              ├── Cached API Data
├── Authentication Status        ├── UI State               ├── Pagination Info
├── App Configuration           └── Component Toggle        └── Filter Results
└── Notification Queue
```"""
        else:
            return """```
Global State (Context)            Local State (React)         Server State
├── User Context                 ├── Form Data              ├── API Response Cache
├── Theme Context               ├── UI State               ├── Loading States
└── App Settings                └── Component State        └── Error States
```"""
    
    def _generate_common_scenarios(self, codebase_context, framework):

        scenarios = []
        
        # Scenario 1: Finding data source
        scenarios.append("""### Scenario 1: Finding Where Data Comes From
**Problem**: "Where does the applicant list data come from?"

**Solution Path**:
1. Start at the UI component: `components/pages/Applicant/ApplicantSearch.tsx`
2. Look for data fetching hooks/effects:
   ```typescript
   // Look for patterns like:
   useEffect(() => {
     fetchApplicants();
   }, []);
   ```
3. Trace the API call: `apis/applicantService.ts`
   ```typescript
   export const getApplicants = (params: SearchParams): Promise<ApplicantResponse> => {
     return axiosGet(`${APPLICANT_ENDPOINTS.SEARCH}`, { params });
   };
   ```
4. Find the endpoint: `apis/apiRoutes.ts`
   ```typescript
   export const APPLICANT_ENDPOINTS = {
     SEARCH: '/api/v1/applicants/search',
     // ...
   };
   ```""")
        
        # Scenario 2: Adding form field
        scenarios.append("""### Scenario 2: Adding a New Field to a Form
**Problem**: "Add a 'phone number' field to the Add Applicant form"

**Solution Path**:
1. **Update the TypeScript interface**: `models/api/request/applicant/ApplicantRequest.ts`
   ```typescript
   export interface ApplicantRequest {
     name: string;
     email: string;
     phoneNumber?: string; // Add this
   }
   ```

2. **Update the form component**: `components/pages/Applicant/AddApplicant.tsx`
   ```typescript
   // Add to form schema
   const schema = yup.object({
     phoneNumber: yup.string().matches(/^\\d{10}$/, 'Invalid phone number')
   });

   // Add form field
   <Controller
     name="phoneNumber"
     control={control}
     render={({ field }) => (
       <InputText {...field} placeholder="Phone Number" />
     )}
   />
   ```

3. **Update API service if needed**: `apis/applicantService.ts`
   ```typescript
   // No changes needed if using the same endpoint
   ```""")
        
        # Scenario 3: Debugging errors
        scenarios.append("""### Scenario 3: Debugging API Errors
**Problem**: "Getting 401 Unauthorized errors"

**Debug Path**:
1. **Check Network Tab**: Look for failed requests
2. **Check axios interceptors**: `apis/axiosInstance.ts`
   ```typescript
   // Look for request interceptor
   axios.interceptors.request.use((config) => {
     // Check if auth token is being added
     const token = getAuthToken();
     if (token) {
       config.headers.Authorization = `Bearer ${token}`;
     }
     return config;
   });
   ```
3. **Verify Okta configuration**: `config/okta-config.ts`
4. **Check token expiry**: Browser DevTools > Application > Local Storage""")
        
        return '\n\n'.join(scenarios)
    
    def _generate_code_patterns(self, codebase_context, framework):

        patterns = []
        
        # Pattern 1: API Service
        patterns.append("""### Pattern 1: API Service with Error Handling
```typescript
// apis/yourService.ts
import { axiosGet, axiosPost } from './axiosInstance';
import { showErrorToast } from '../utils/toast';

export const fetchData = async (id: string): Promise<YourType | null> => {
  try {
    const response = await axiosGet(`/api/v1/your-endpoint/${id}`);
    return response.data;
  } catch (error) {
    // Global error handling in axios interceptor
    console.error('Error fetching data:', error);
    return null;
  }
};
```""")
        
        # Pattern 2: Component with loading
        patterns.append("""### Pattern 2: Component with Loading States
```typescript
const YourComponent: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<YourType | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchData('123');
        setData(result);
      } catch (err) {
        setError('Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, []);

  if (loading) return <ProgressSpinner />;
  if (error) return <Message severity="error" text={error} />;
  if (!data) return <Message severity="info" text="No data found" />;
  
  return <div>{/* Render your data */}</div>;
};
```""")
        
        # Pattern 3: Form with validation
        patterns.append("""### Pattern 3: Form with Validation
```typescript
import { useForm, Controller } from 'react-hook-form';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';

const schema = yup.object({
  name: yup.string().required('Name is required'),
  email: yup.string().email('Invalid email').required('Email is required')
});

const FormComponent: React.FC = () => {
  const { control, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema),
    defaultValues: { name: '', email: '' }
  });

  const onSubmit = async (data: FormData) => {
    try {
      await saveData(data);
      showToast('Success', 'Data saved successfully');
    } catch (error) {
      showToast('Error', 'Failed to save data');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Controller
        name="name"
        control={control}
        render={({ field }) => (
          <div>
            <InputText {...field} className={errors.name ? 'p-invalid' : ''} />
            {errors.name && <small className="p-error">{errors.name.message}</small>}
          </div>
        )}
      />
      {/* More fields... */}
    </form>
  );
};
```""")
        
        return '\n\n'.join(patterns)
    
    def _generate_debugging_guide(self, codebase_context, framework):

        guide_sections = []
        
        # Common issues
        guide_sections.append("""### Common Issues & Solutions

#### 1. "Cannot read property of undefined"
**Symptoms**: App crashes with undefined errors
**Common Causes**:
- API response structure changed
- Missing null checks
- Async data not loaded yet

**Solution**:
```typescript
// Bad
const userName = user.profile.name; // Crashes if user or profile is undefined

// Good
const userName = user?.profile?.name || 'Unknown';
```""")
        
        # Framework-specific issues
        if 'primereact' in codebase_context.lower():
            guide_sections.append("""#### 2. "PrimeReact component not rendering correctly"
**Symptoms**: Component appears but looks broken
**Common Causes**:
- Missing PrimeReact CSS imports
- Theme not configured

**Solution**:
```typescript
// In index.tsx or App.tsx
import 'primereact/resources/themes/lara-light-indigo/theme.css';
import 'primereact/resources/primereact.min.css';
import 'primeicons/primeicons.css';
```""")
        
        # State update issues
        guide_sections.append("""#### 3. "State not updating"
**Symptoms**: UI doesn't reflect state changes
**Common Causes**:
- Mutating state directly
- Stale closure in useEffect

**Solution**:
```typescript
// Bad
const updateArray = () => {
  items.push(newItem); // Mutating directly
  setItems(items);
};

// Good
const updateArray = () => {
  setItems([...items, newItem]); // Creating new array
};
```""")
        
        return '\n\n'.join(guide_sections)
    
    def _generate_project_knowledge(self, codebase_context, modules):

        knowledge = []
        
        # API patterns
        knowledge.append("""### API Response Patterns
All API responses follow this structure:
```typescript
interface ApiResponse<T> {
  data: T;
  meta: {
    total: number;
    page: number;
    pageSize: number;
  };
  errors?: ApiError[];
}
```""")
        
        # Authentication flow
        if 'okta' in codebase_context.lower():
            knowledge.append("""### Authentication Flow
```
1. User lands on app → Redirected to Okta login
2. Successful login → Okta redirects back with token
3. Token stored in localStorage as 'okta-token-storage'
4. Axios interceptor adds token to all requests
5. Token refresh handled automatically by Okta SDK
```""")
        
        # Form validation
        knowledge.append("""### Form Validation Rules
- All forms use React Hook Form + Yup
- Validation messages come from i18n translations
- Server-side validation errors displayed via toast notifications""")
        
        # State management
        knowledge.append("""### State Management Decision Tree
```
Is it used by multiple components?
├── Yes → Use Redux
│   └── Examples: User info, app config
└── No → Use local state (useState)
    └── Is it server data?
        ├── Yes → Use custom hook with API call
        └── No → Simple useState
```""")
        
        return '\n\n'.join(knowledge)
    
    def _generate_framework_specific_tools(self, framework):

        framework_lower = framework.lower()
        
        if 'react' in framework_lower:
            return "- Okta Browser Plugin (for testing)"
        elif 'vue' in framework_lower:
            return "- Vue DevTools"
        elif 'angular' in framework_lower:
            return "- Angular DevTools"
        else:
            return ""
    
    def _generate_naming_conventions(self, codebase_context):

        return """- Components: `PascalCase.tsx` (e.g., `ApplicantSearch.tsx`)
- Services: `camelCase.ts` (e.g., `applicantService.ts`)
- Types/Interfaces: `PascalCase.ts` (e.g., `ApplicantRequest.ts`)
- Utils: `kebab-case.ts` (e.g., `date-helper.ts`)"""
    
    def _generate_import_order_example(self, framework):

        return """```typescript
// 1. External libraries
import React from 'react';
import { useTranslation } from 'react-i18next';

// 2. Internal absolute imports
import { useToast } from '@/hooks/useToast';

// 3. Relative imports
import { ApplicantForm } from './ApplicantForm';

// 4. Types
import type { ApplicantRequest } from '@/models/api/request/applicant';

// 5. Styles
import './styles.css';
```"""
    
    def _generate_performance_tips(self, framework):

        tips = []
        
        # Code splitting
        tips.append("""### Code Splitting
```typescript
// Lazy load heavy components
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));

// Use with Suspense
<Suspense fallback={<Loading />}>
  <HeavyComponent />
</Suspense>
```""")
        
        # Memoization
        tips.append("""### Memoization
```typescript
// Memoize expensive calculations
const expensiveValue = useMemo(() => {
  return calculateExpensiveValue(data);
}, [data]);

// Memoize callbacks
const handleClick = useCallback(() => {
  doSomething(id);
}, [id]);
```""")
        
        return '\n\n'.join(tips)
    
    def _check_tech_stack(self, codebase_context, modules):

        tech_stack = []
        content_lower = codebase_context.lower()
        
        # Core technologies
        tech_stack.append("### **Core Technologies**")
        if 'react' in content_lower:
            tech_stack.append("- **React** - UI framework")
        if 'typescript' in content_lower or '.tsx' in content_lower:
            tech_stack.append("- **TypeScript** - Type safety")
        if 'redux' in content_lower:
            tech_stack.append("- **Redux** - State management")
        
        # UI Libraries
        if 'primereact' in content_lower:
            tech_stack.append("\n### **UI Components**")
            tech_stack.append("- **PrimeReact** - Component library")
        elif 'material-ui' in content_lower or '@mui' in content_lower:
            tech_stack.append("\n### **UI Components**")
            tech_stack.append("- **Material-UI** - Component library")
        
        # Authentication
        if 'okta' in content_lower:
            tech_stack.append("\n### **Authentication**")
            tech_stack.append("- **Okta** - Identity management")
        elif 'auth0' in content_lower:
            tech_stack.append("\n### **Authentication**")
            tech_stack.append("- **Auth0** - Identity platform")
        
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