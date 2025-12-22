# Tasks.md

This document tracks all pending tasks, improvements, and issues identified in the Talia Bot codebase.

## **Critical Security Issues** 🔴

### [SEC-001] File Upload Security Validation
- **Status**: DONE
- **Priority**: High
- **Description**: `handle_document()` in main.py:168 accepts any file type without validation
- **Files affected**: `main.py`
- **Action needed**: Add file type validation, size limits, and malware scanning
- **Due**: ASAP

### [SEC-002] Hardcoded Secrets Management
- **Priority**: High  
- **Description**: Email credentials stored in plain text environment variables
- **Files affected**: `config.py`, `.env.example`
- **Action needed**: Implement proper secret management (Vault/AWS Secrets Manager)
- **Due**: Next sprint

### [SEC-003] SQL Injection Prevention
- **Priority**: Medium
- **Description**: Database connection lacks connection pooling and timeout configurations
- **Files affected**: `db.py`
- **Action needed**: Add connection pooling, timeouts, and connection limits
- **Due**: Next sprint

## **Missing Implementations** 🟡

### [IMP-001] Whisper Transcription Agent
- **Status**: DONE
- **Priority**: High
- **Description**: AGENTS.md states Whisper agent is "Inexistente" but code references it
- **Files affected**: Need to create `transcription.py`
- **Action needed**: Create dedicated transcription module as per AGENTS.md
- **Due**: Next sprint

### [IMP-002] Dynamic Menu Generation
- **Priority**: Medium
- **Description**: `onboarding.py` has hardcoded menus instead of dynamic generation
- **Files affected**: `onboarding.py`
- **Action needed**: Implement dynamic menu generation based on user roles
- **Due**: Future iteration

### [IMP-003] Button Dispatcher Agent
- **Priority**: Low
- **Description**: "Despachador de Botones" mentioned in AGENTS.md but not implemented
- **Files affected**: Need to create new module
- **Action needed**: Create separate button dispatcher agent
- **Due**: Future iteration

## **Architecture & Code Quality** 🟠

### [ARCH-001] Main.py Business Logic Violation
- **Priority**: Medium
- **Description**: `main.py` contains business logic (lines 56-95) violating "Recepcionista" agent role
- **Files affected**: `main.py`
- **Action needed**: Refactor to follow agent responsibilities, move logic to appropriate agents
- **Due**: Next sprint

### [ARCH-002] Error Handling Consistency
- **Priority**: Medium
- **Description**: Inconsistent error handling across modules, missing try-catch blocks
- **Files affected**: `flow_engine.py`, `printer.py`, multiple modules
- **Action needed**: Add comprehensive error handling and graceful degradation
- **Due**: Next sprint

### [ARCH-003] Code Duplication
- **Priority**: Low
- **Description**: Database connection patterns repeated, similar menu generation logic
- **Files affected**: Multiple files
- **Action needed**: Create shared utilities and base classes
- **Due**: Future iteration

## **Performance & Optimization** 🟢

### [PERF-001] Database Connection Pooling
- **Priority**: Medium
- **Description**: No connection pooling, missing indexes on frequently queried columns
- **Files affected**: `db.py`
- **Action needed**: Add connection pooling and database indexes
- **Due**: Next sprint

### [PERF-002] Memory Management
- **Priority**: Medium
- **Description**: Voice files loaded entirely into memory, no cleanup for failed uploads
- **Files affected**: `llm_engine.py`, `main.py`
- **Action needed**: Implement streaming file processing and cleanup mechanisms
- **Due**: Next sprint

### [PERF-003] Flow Engine Memory Usage
- **Priority**: Low
- **Description**: Flow engine stores all conversation data in memory
- **Files affected**: `flow_engine.py`
- **Action needed**: Implement conversation state persistence and cleanup
- **Due**: Future iteration

## **Dependencies & Configuration** 🔵

### [DEP-001] Python Version Upgrade
- **Priority**: High
- **Description**: Using Python 3.9 (EOL October 2025) - should upgrade to 3.11+
- **Files affected**: `Dockerfile`, `requirements.txt`
- **Action needed**: Upgrade Python version and test compatibility
- **Due**: Next sprint

### [DEP-002] Package Security Updates
- **Status**: DONE
- **Priority**: High
- **Description**: `python-telegram-bot[job-queue]<22` using outdated version constraint
- **Files affected**: `requirements.txt`
- **Action needed**: Update dependencies and run security audit
- **Due**: ASAP

### [DEP-003] Docker Security Hardening
- **Priority**: Medium
- **Description**: Running as root user, missing security hardening
- **Files affected**: `Dockerfile`, `docker-compose.yml`
- **Action needed**: Add USER directive, read-only filesystem, health checks
- **Due**: Next sprint

## **Bugs & Logical Errors** 🐛

### [BUG-001] Flow Engine Validation
- **Priority**: Medium
- **Description**: `flow_engine.py:72` missing validation for empty steps array
- **Files affected**: `flow_engine.py`
- **Action needed**: Add input validation and error handling
- **Due**: Next sprint

### [BUG-002] Printer Module IMAP Search
- **Priority**: Medium
- **Description**: `printer.py:88` IMAP search doesn't handle large email counts
- **Files affected**: `printer.py`
- **Action needed**: Add email pagination and marking as read
- **Due**: Next sprint

### [BUG-003] Identity Module String Comparison
- **Priority**: Low
- **Description**: `identity.py:42` string comparison for ADMIN_ID could fail if numeric
- **Files affected**: `identity.py`
- **Action needed**: Fix type handling for user ID comparison
- **Due**: Next sprint

## **Documentation & Testing** 📚

### [DOC-001] Documentation Consistency
- **Priority**: Low
- **Description**: AGENTS.md vs implementation inconsistencies
- **Files affected**: `AGENTS.md`, various modules
- **Action needed**: Update documentation to match actual implementation
- **Due**: Future iteration

### [TEST-001] Test Coverage
- **Priority**: Low
- **Description**: Missing comprehensive test coverage
- **Files affected**: All modules
- **Action needed**: Add unit tests, integration tests, and E2E tests
- **Due**: Future iteration

### [TEST-002] Code Quality Tools
- **Priority**: Low
- **Description**: Missing code quality tools (black, flake8, mypy)
- **Files affected**: Repository configuration
- **Action needed**: Add code quality tools and CI/CD integration
- **Due**: Future iteration

---

## **Sprint Planning**

### **Current Sprint (High Priority)**
- **[DONE]** [SEC-001] File upload security validation
- **[DONE]** [DEP-002] Package security updates
- **[DONE]** [IMP-001] Whisper transcription agent

### **Next Sprint (Medium Priority)**
- [SEC-002] Secret management implementation
- [SEC-003] Database connection pooling
- [DEP-001] Python version upgrade
- [ARCH-001] Main.py refactoring
- [ARCH-002] Error handling consistency
- [BUG-001] Flow engine validation
- [BUG-002] Printer module fixes

### **Future Iterations (Low Priority)**
- Dynamic menu generation
- Button dispatcher agent
- Performance optimizations
- Documentation updates
- Test coverage expansion

---

## **Definitions**

- **🔴 Critical**: Security vulnerabilities or production-breaking issues
- **🟡 High**: Important features missing or major functionality gaps  
- **🟠 Medium**: Architecture improvements or code quality issues
- **🟢 Low**: Performance optimizations or nice-to-have features
- **🔵 Configuration**: Dependency updates or configuration changes
- **🐛 Bug**: Logical errors or unexpected behavior
- **📚 Documentation**: Documentation or testing improvements

**Status Legend:**
- `TODO` - Not started
- `IN_PROGRESS` - Currently being worked on
- `IN_REVIEW` - Ready for review
- `DONE` - Completed
- `BLOCKED` - Blocked by dependency