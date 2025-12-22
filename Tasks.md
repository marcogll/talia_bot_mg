# Tasks.md

This document tracks all pending tasks, improvements, and issues identified in the Talia Bot codebase.

## **Critical Security Issues** 🔴

### [SEC-001] File Upload Security Validation
- **Status**: DONE
- **Priority**: High

### [SEC-002] Hardcoded Secrets Management
- **Status**: DONE
- **Priority**: High  

### [SEC-003] SQL Injection Prevention
- **Status**: DONE
- **Priority**: Medium

## **Missing Implementations** 🟡

### [IMP-001] Whisper Transcription Agent
- **Status**: DONE
- **Priority**: High

### [IMP-002] Dynamic Menu Generation
- **Status**: TODO
- **Priority**: Medium
- **Description**: `onboarding.py` has hardcoded menus instead of dynamic generation
- **Action needed**: Implement dynamic menu generation based on user roles

### [IMP-003] Button Dispatcher Agent
- **Status**: TODO
- **Priority**: Low
- **Description**: "Despachador de Botones" mentioned in AGENTS.md but not implemented
- **Action needed**: Create separate button dispatcher agent

## **Architecture & Code Quality** 🟠

### [ARCH-001] Main.py Business Logic Violation
- **Status**: DONE
- **Priority**: Medium

### [ARCH-002] Error Handling Consistency
- **Status**: DONE
- **Priority**: Medium

### [ARCH-003] Code Duplication
- **Status**: TODO
- **Priority**: Low
- **Description**: Database connection patterns repeated, similar menu generation logic
- **Action needed**: Create shared utilities and base classes

## **Performance & Optimization** 🟢

### [PERF-001] Database Connection Pooling
- **Status**: DONE
- **Priority**: Medium

### [PERF-002] Memory Management
- **Status**: TODO
- **Priority**: Medium
- **Description**: Voice files loaded entirely into memory, no cleanup for failed uploads
- **Action needed**: Implement streaming file processing and cleanup mechanisms

### [PERF-003] Flow Engine Memory Usage
- **Status**: TODO
- **Priority**: Low
- **Description**: Flow engine stores all conversation data in memory
- **Action needed**: Implement conversation state persistence and cleanup

## **Dependencies & Configuration** 🔵

### [DEP-001] Python Version Upgrade
- **Status**: DONE
- **Priority**: High

### [DEP-002] Package Security Updates
- **Status**: DONE
- **Priority**: High

### [DEP-003] Docker Security Hardening
- **Status**: TODO
- **Priority**: Medium
- **Description**: Running as root user, missing security hardening
- **Action needed**: Add USER directive, read-only filesystem, health checks

## **Bugs & Logical Errors** 🐛

### [BUG-001] Flow Engine Validation
- **Status**: DONE
- **Priority**: Medium

### [BUG-002] Printer Module IMAP Search
- **Status**: DONE
- **Priority**: Medium

### [BUG-003] Identity Module String Comparison
- **Status**: TODO
- **Priority**: Low
- **Description**: `identity.py:42` string comparison for ADMIN_ID could fail if numeric
- **Action needed**: Fix type handling for user ID comparison

### [BUG-004] Missing sqlite3 import
- **Status**: DONE
- **Priority**: High
- **Description**: `flow_engine.py` missing `sqlite3` import causing NameError
- **Files affected**: `flow_engine.py`
- **Action needed**: Add `import sqlite3`
- **Due**: ASAP

### [BUG-005] Telegram Conflict Error
- **Status**: DONE
- **Priority**: High
- **Description**: `telegram.error.Conflict` indicates multiple bot instances running
- **Files affected**: Runtime
- **Action needed**: Kill all orphan processes and restart
- **Due**: ASAP

## **Documentation & Testing** 📚

### [DOC-001] Documentation Consistency
- **Status**: TODO
- **Priority**: Low
- **Description**: AGENTS.md vs implementation inconsistencies
- **Action needed**: Update documentation to match actual implementation

### [TEST-001] Test Coverage
- **Status**: TODO
- **Priority**: Low
- **Description**: Missing comprehensive test coverage
- **Action needed**: Add unit tests, integration tests, and E2E tests

### [TEST-002] Code Quality Tools
- **Status**: TODO
- **Priority**: Low
- **Description**: Missing code quality tools (black, flake8, mypy)
- **Action needed**: Add code quality tools and CI/CD integration

---

## **Sprint Planning**

### **Previous Sprints**
- **[DONE]** [SEC-001] File upload security validation
- **[DONE]** [DEP-002] Package security updates
- **[DONE]** [IMP-001] Whisper transcription agent
- **[DONE]** [SEC-002] Secret management implementation
- **[DONE]** [SEC-003] Database connection pooling
- **[DONE]** [DEP-001] Python version upgrade
- **[DONE]** [ARCH-001] Main.py refactoring
- **[DONE]** [ARCH-002] Error handling consistency
- **[DONE]** [BUG-001] Flow engine validation
- **[DONE]** [BUG-002] Printer module fixes
- **[DONE]** [PERF-001] Database Connection Pooling

### **Current Sprint**
- [IMP-002] Dynamic Menu Generation
- [DEP-003] Docker Security Hardening
- [BUG-003] Identity Module String Comparison
- [PERF-002] Memory Management

### **Future Iterations**
- [IMP-003] Button Dispatcher Agent
- [ARCH-003] Code Duplication
- [PERF-003] Flow Engine Memory Usage
- [DOC-001] Documentation Consistency
- [TEST-001] Test Coverage
- [TEST-002] Code Quality Tools

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