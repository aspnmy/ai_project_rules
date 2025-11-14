# Util Directory Description

The Util directory is the project's utility directory, containing various functionally categorized tool scripts to support daily project management and automated operations.

## 📁 Directory Structure

The Util directory organizes tool scripts into different subdirectories based on functionality:

- **check_tools/**: Check tool scripts for checking gateway domains, project configurations, rule managers, etc.
- **db_management/**: Database management related scripts for managing database file systems, parsing database lists, etc.
- **rules_management/**: Rule management related scripts for managing and pulling rule files
- **setup_tools/**: Installation and setup related scripts for installing MCP servers, Podman, etc.
- **wsl_management/**: WSL development environment management scripts for managing WSL development environments and paths

## 🛠️ Main Tools Description

### check_tools Directory
- `check_gateway_domains.py`: Gateway domain checking tool
- `check_project_config.py`: Project configuration checking tool
- `check_rules_manager.py`: Rule manager checking tool

### db_management Directory
- `db_filesystem_manager.py`: Database file system manager
- `db_filesystem_manager_secure.py`: Secure version of database file system manager
- `db_lists_parser.py`: Database list parser
- `autotest-db-lists-management.py`: Database list management automated test script

### rules_management Directory
- `rules_manager.py`: Rule manager
- `rules_manager_updated.py`: Updated rule manager
- `rule_puller.py`: Rule pulling tool

### setup_tools Directory
- `install_mcp_servers.py`: MCP server installation script
- `install_podman_windows.py`: Windows Podman installation script
- `set_SystemPathVar.py`: System environment variable setting script

### wsl_management Directory
- `wsl_dev_manager.py`: WSL development environment manager
- `wsl_dev_path_manager.py`: WSL development path manager
- `wsl_ide_integrator.py`: WSL IDE integration tool

## 📝 Usage Instructions

Please call the tool scripts in the corresponding directories according to specific functional requirements. Most scripts support command-line parameters, and you can view detailed usage through `python script_name.py --help`.