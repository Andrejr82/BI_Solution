# TestSprite PRD - Agent Solution BI

## Product Overview

**Agent Solution BI** is a full-stack Business Intelligence application with conversational AI capabilities powered by Google Gemini. The application consists of:

- **Frontend**: SolidJS-based reactive UI with 18+ components
- **Backend**: FastAPI REST API with SQL Server integration
- **Authentication**: JWT-based auth with role-based access control (RBAC)
- **Data Layer**: SQL Server for metadata, Parquet files for analytics
- **AI Integration**: Google Gemini 2.5 Flash for natural language queries

## Testing Objectives

### Primary Goals
1. **End-to-End Coverage**: Validate complete user journeys from login to data visualization
2. **API Validation**: Ensure all backend endpoints function correctly
3. **UI Functionality**: Verify all 18+ SolidJS components render and interact properly
4. **Authentication Flow**: Test JWT authentication and RBAC enforcement
5. **Integration Testing**: Validate frontend-backend communication
6. **Performance Validation**: Ensure response times meet targets (<3s initial load, <500ms navigation)

### Success Criteria
- ✅ 100% critical user journey coverage
- ✅ All API endpoints tested (GET, POST, PUT, DELETE)
- ✅ All UI components validated
- ✅ Authentication and authorization flows verified
- ✅ Performance benchmarks met
- ✅ Zero critical bugs in production paths

## Application Architecture

### Frontend (SolidJS)
- **Port**: 3000
- **Framework**: SolidJS with Vite
- **Routing**: @solidjs/router
- **State Management**: @tanstack/solid-query
- **Styling**: TailwindCSS
- **Components**: 18+ UI components (Button, Card, Dialog, Table, etc.)

### Backend (FastAPI)
- **Port**: 8000
- **Framework**: FastAPI with Python 3.11+
- **Database**: SQL Server (ODBC Driver 17)
- **Authentication**: JWT tokens
- **API Documentation**: Auto-generated OpenAPI/Swagger

### Key User Flows

#### 1. Authentication Flow
```
Login Page → Enter Credentials → JWT Token → Dashboard Redirect
```

#### 2. Dashboard Flow
```
Dashboard → Load Metrics → Display Charts → Real-time Updates
```

#### 3. Chat BI Flow
```
Chat Interface → Natural Language Query → Gemini Processing → Data Visualization
```

#### 4. Admin Flow
```
Admin Panel → User Management → CRUD Operations → Audit Logs
```

#### 5. Reports Flow
```
Reports Page → List Reports → View Report → Export Data
```

## Test Scenarios

### 1. Frontend UI Tests

#### Component Tests
- **Skeleton**: Loading animation renders
- **Badge**: All 4 variants (default, secondary, destructive, outline)
- **Button**: All 6 variants and sizes
- **Input**: Text entry, validation
- **Card**: Layout and content rendering
- **Alert**: Message display
- **Avatar**: Image and fallback
- **Tabs**: Tab switching
- **Table**: Data display and sorting
- **Dialog**: Open/close interactions
- **Sheet**: Slide-in panel
- **Toast**: Notifications
- **Select**: Dropdown selection
- **DropdownMenu**: Menu interactions

#### Page Tests
- **Login**: Form validation, error handling
- **Dashboard**: Metrics loading, chart rendering
- **Analytics**: Data visualization, filters
- **Reports**: List view, detail view, export
- **Chat BI**: Message input, streaming responses
- **Admin**: User list, create/edit/delete users
- **Profile**: User data display, update

### 2. Backend API Tests

#### Authentication Endpoints
```
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh
GET /api/auth/me
```

#### User Management
```
GET /api/users
GET /api/users/{id}
POST /api/users
PUT /api/users/{id}
DELETE /api/users/{id}
```

#### Analytics
```
GET /api/analytics/metrics
GET /api/analytics/charts
POST /api/analytics/query
```

#### Reports
```
GET /api/reports
GET /api/reports/{id}
POST /api/reports
PUT /api/reports/{id}
DELETE /api/reports/{id}
```

#### Chat BI
```
POST /api/chat/query
GET /api/chat/history
```

### 3. Integration Tests

#### End-to-End Scenarios
1. **Complete Login Flow**
   - Navigate to login page
   - Enter valid credentials (admin/Admin@2024)
   - Verify JWT token storage
   - Verify redirect to dashboard
   - Verify protected routes accessible

2. **Dashboard Data Flow**
   - Login as admin
   - Navigate to dashboard
   - Verify metrics API call
   - Verify data rendering
   - Verify chart interactions

3. **Chat BI Interaction**
   - Login as user
   - Navigate to Chat BI
   - Send natural language query
   - Verify Gemini API call
   - Verify streaming response
   - Verify data visualization

4. **Admin CRUD Operations**
   - Login as admin
   - Navigate to admin panel
   - Create new user
   - Edit user details
   - Delete user
   - Verify audit logs

5. **Report Generation**
   - Login as user
   - Navigate to reports
   - Select report template
   - Generate report
   - Verify data accuracy
   - Export report

### 4. Error Handling Tests

- Invalid credentials
- Expired JWT tokens
- Network failures
- API timeout scenarios
- Invalid form inputs
- Missing required fields
- Database connection errors
- Permission denied scenarios

### 5. Performance Tests

- Initial page load time (<3s)
- Navigation between pages (<500ms)
- API response times
- Large dataset rendering
- Concurrent user sessions
- Memory leak detection

## Test Data Requirements

### User Accounts
```
Admin: admin / Admin@2024
User: user / User@2024
```

### Database State
- Pre-populated analytics data
- Sample reports
- Chat history
- User records

## Environment Configuration

### Backend (.env)
```
USE_SQL_SERVER=True
DATABASE_URL=<SQL Server connection string>
GEMINI_API_KEY=<API key>
SECRET_KEY=<JWT secret>
```

### Frontend
```
VITE_API_URL=http://127.0.0.1:8000
```

## Test Execution Strategy

### Phase 1: Component Tests
- Run isolated component tests
- Verify all UI components render
- Test component interactions

### Phase 2: API Tests
- Test all endpoints individually
- Verify request/response formats
- Test error scenarios

### Phase 3: Integration Tests
- Test complete user journeys
- Verify frontend-backend communication
- Test authentication flows

### Phase 4: Performance Tests
- Measure load times
- Test under concurrent load
- Monitor resource usage

## Expected Outcomes

### Test Reports
- Detailed test execution logs
- Screenshot/video evidence of failures
- Performance metrics
- Code coverage reports

### Bug Fixes
- Automated bug detection
- AI-suggested fixes
- Regression test generation

### Documentation
- Test case documentation
- API endpoint coverage
- User journey maps
- Performance benchmarks

## Maintenance Plan

- **Daily**: Run smoke tests on critical paths
- **Weekly**: Full regression suite
- **Monthly**: Performance benchmarking
- **Per Release**: Complete test suite execution

## Integration with CI/CD

- Automated test execution on PR
- Test results in PR comments
- Blocking deployments on test failures
- Performance regression alerts
