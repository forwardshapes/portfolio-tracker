# Python/Streamlit Code Review Prompt

## Overview
Please conduct a comprehensive code review of this Python/Streamlit project. Focus on code quality, performance, security, maintainability, and Streamlit-specific best practices.

## Review Areas

### 1. **Code Structure & Organization**
- Is the code well-organized with clear separation of concerns?
- Are functions and classes appropriately sized and focused?
- Is there proper modularization (separate files for different functionality)?
- Are imports organized and necessary?
- Is there a clear project structure with appropriate file naming?

### 2. **Streamlit-Specific Best Practices**
- **Session State Management**: Is `st.session_state` used appropriately? Are there any unnecessary re-runs?
- **Caching**: Are `@st.cache_data` and `@st.cache_resource` used effectively for expensive operations?
- **Layout & UI**: Is the UI intuitive and responsive? Are components used appropriately?
- **Performance**: Are there any unnecessary widget re-renders or expensive operations in the main flow?
- **State Persistence**: Is application state managed correctly across user interactions?

### 3. **Python Code Quality**
- **PEP 8 Compliance**: Does the code follow Python style guidelines?
- **Error Handling**: Are exceptions handled gracefully with user-friendly messages?
- **Type Hints**: Are type annotations used consistently?
- **Documentation**: Are functions and classes properly documented with docstrings?
- **Variable Naming**: Are variables and functions clearly named?

### 4. **Data Handling & Processing**
- Are data operations efficient and properly handled?
- Is data validation implemented where necessary?
- Are large datasets processed appropriately (chunking, streaming, etc.)?
- Is data sanitization and cleaning handled properly?

### 5. **Security Considerations**
- Are user inputs properly validated and sanitized?
- Are file uploads handled securely?
- Are any secrets or API keys properly managed (not hardcoded)?
- Is there protection against common web vulnerabilities?

### 6. **Performance & Scalability**
- Are there any performance bottlenecks?
- Is memory usage optimized?
- Are database queries efficient (if applicable)?
- Can the app handle multiple concurrent users?

### 7. **Testing & Reliability**
- Are there unit tests for core functionality?
- Is error handling comprehensive?
- Are edge cases considered and handled?

### 8. **Dependencies & Environment**
- Are dependencies appropriate and up-to-date?
- Is there a proper requirements.txt or environment specification?
- Are version constraints specified appropriately?

## Specific Issues to Look For

### Common Streamlit Anti-patterns:
- Expensive operations running on every rerun
- Improper use of session state leading to memory leaks
- Missing caching for data loading/processing
- Poor widget organization causing UX issues
- Blocking operations in the main thread

### Python Code Issues:
- Unused imports or variables
- Potential security vulnerabilities
- Inefficient algorithms or data structures
- Poor exception handling
- Memory leaks or resource management issues

## Review Format

Please structure your review as follows:

### 🟢 **Strengths**
- List what the code does well
- Highlight good practices and patterns

### 🟡 **Areas for Improvement**
- Medium priority issues that should be addressed
- Suggestions for better practices

### 🔴 **Critical Issues**
- High priority issues that need immediate attention
- Security vulnerabilities or major bugs

### 📋 **Specific Recommendations**

For each issue, provide:
1. **File/Line Reference**: Specific location of the issue
2. **Issue Description**: What the problem is
3. **Impact**: Why it matters
4. **Suggested Fix**: Concrete solution with code example if possible
5. **Priority**: High/Medium/Low

### 💡 **Additional Suggestions**
- Performance optimizations
- Code organization improvements
- Feature enhancements
- Best practice recommendations

## Code Submission Instructions

Please provide:
1. **Main application files** (especially the main Streamlit app)
2. **Supporting modules** and utility functions
3. **Requirements.txt** or environment specification
4. **Any configuration files**
5. **Brief description** of the application's purpose and key features

Focus your review on maintainability, performance, user experience, and adherence to Python and Streamlit best practices.