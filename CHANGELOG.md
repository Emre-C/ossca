# Changelog

All notable changes to DeepWiki will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-16

### 🎉 Major Release: "Finish & Polish" Sprint

This release represents a complete transformation from v0.1 to a production-ready v1.0, focusing on packaging, user experience, reliability, and maintainability.

### 💥 Breaking Changes

- **Project Renamed**: Package name changed from `ossca` to `deepwiki`
  - Update your installations: `pip install deepwiki` (instead of `ossca`)
  - Import statements remain the same: `from deepwiki import KnowledgeBase`

- **CLI Entry Point**: New console script replaces direct Python execution
  - **New**: `deepwiki <repo_url> [options]`
  - **Old**: `python main.py <repo_url> [options]`

- **Package Structure**: Provider clients moved to dedicated namespace
  - Provider code moved from `deepwiki/*.py` to `deepwiki/providers/`
  - Core API available at `from deepwiki.core import *`
  - This change improves code organization and reduces namespace pollution

### ✨ New Features

#### 🌊 Streaming Responses
- **Real-time Streaming**: Answers now stream as they're generated instead of waiting for completion
- **Stream Control**: New `--no-stream` flag for scripting scenarios
- **Better UX**: See responses appear in real-time during interactive sessions

#### 🔄 Database Schema Versioning
- **Version Management**: Automatic detection of incompatible database versions
- **Clear Error Messages**: `SchemaMismatchError` prompts rebuilds when schema changes
- **Future-Proof**: Foundation for handling database migrations in future releases

#### 📦 Professional Packaging
- **PyPI Distribution**: Now available as `pip install deepwiki`
- **Console Script**: Global `deepwiki` command after installation
- **Improved Metadata**: Better project description and categorization

### 🛠 Improvements

#### 🎯 Logging Simplification
- **Simplified API**: `setup_logging(level=logging.INFO)` replaces complex configuration
- **Cleaner Code**: Removed duplicate logging setup across modules
- **Better Defaults**: Sensible default format without required parameters

#### 📚 Documentation Overhaul
- **Focused README**: Updated for CLI usage instead of API references  
- **Current Examples**: All examples use `deepwiki` command
- **Clean Structure**: Removed legacy API documentation

#### 🧪 Testing Enhancement
- **End-to-End Tests**: Comprehensive e2e test suite with real repository cloning
- **Network-Aware**: Tests gracefully skip when internet unavailable
- **Fast Execution**: Tests complete under 60 seconds with timeout protection
- **Schema Testing**: Dedicated tests for database versioning functionality

### 🐛 Bug Fixes

- **Import Paths**: Fixed import paths after package restructuring
- **Provider Loading**: Improved error handling for provider client imports
- **Database Loading**: Better error messages for database schema mismatches

### 🏗 Technical Improvements

- **Code Organization**: Clear separation between core API and provider implementations
- **Error Handling**: Dedicated exception classes for different error scenarios
- **Type Safety**: Better type hints and validation
- **Configuration**: Simplified logging configuration

### 📖 Documentation

- **CLI Focus**: Documentation now emphasizes console script usage
- **Installation Guide**: Clear PyPI installation instructions
- **Migration Guide**: Breaking changes clearly documented
- **Examples Updated**: All code examples use new CLI interface

### 🔧 Development Experience

- **Test Markers**: E2E tests properly marked for filtering
- **Pytest Configuration**: Enhanced test configuration with timeout support
- **Package Layout**: Intuitive package structure for contributors
- **Import Clarity**: Clear distinction between public and internal APIs

### 📋 Requirements

- **Python Version**: Continues to support Python 3.12+
- **Dependencies**: No new runtime dependencies
- **Compatibility**: Maintains API compatibility for core functionality

### 🚀 Migration Guide

#### For Users:
1. **Installation**: `pip install deepwiki` (replaces custom installation)
2. **CLI Usage**: Use `deepwiki` command instead of `python main.py`
3. **Functionality**: All features work the same, just better UX

#### For Developers:
1. **Imports**: Core imports unchanged (`from deepwiki import KnowledgeBase`)
2. **Provider Access**: Use `from deepwiki.providers import *` for provider clients
3. **Exceptions**: Import schema errors from `from deepwiki import SchemaMismatchError`

---

## [0.1.0] - 2024-XX-XX

### Initial Release
- Basic knowledge base functionality
- Support for multiple AI providers
- Repository processing and indexing
- Interactive Q&A interface 