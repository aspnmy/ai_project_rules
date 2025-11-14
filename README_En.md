# AI Project Rule Management System

This is a rule management system designed specifically for AI-assisted code development projects, providing a complete set of project specifications, automation tools, and synchronization mechanisms.

## 🎯 Project Overview

This project aims to provide a standardized rule management system for AI-assisted code development, ensuring code quality, project consistency, and team collaboration efficiency. Through automated tools and regular synchronization mechanisms, developers always use the latest project specifications.

## 📋 Main Features

### 1. Rule File Management
- **project_rules.md**: Core rule file containing complete project specifications
- **Automated Pull**: Regularly sync the latest rules from GitHub
- **Version Control**: Support for version management and rollback of rule files
- **Backup Mechanism**: Automatically backup historical versions for quick recovery

### 2. Rule Classification System
- **High Priority Rules** (🔴): Mandatory specifications that must be strictly followed
- **Medium Priority Rules** (🟡): Recommended best practices
- **Low Priority Rules** (🟢): Reference suggestions and optimization recommendations

### 3. Conflict Resolution Mechanism
- **Priority Hierarchy Table**: Clear rule priority ordering
- **Automatic Conflict Detection**: Intelligent identification of rule conflicts
- **Solution Suggestions**: Provide standardized conflict handling processes

## 🚀 Quick Start

### Installation and Configuration

1. **Clone the Project**
   ```bash
   git clone https://github.com/aspnmy/ai_project_rules.git
   cd ai_project_rules
   ```

2. **Run the Rule Puller**
   ```bash
   python rule_puller.py update
   ```

3. **Check Status**
   ```bash
   python rule_puller.py status
   ```

### Basic Usage

```bash
# Check and update rule files
```