# db_config Directory Description

## Directory Function
This directory is used to store database configuration-related JSON configuration files, including database operations, backup strategies, and other configuration information.

## Configuration File List
- **backup_strategy.json**: Database backup strategy configuration
- **file_operations.json**: File operation related configuration
- **maintenance_plan.json**: Database maintenance plan configuration
- **mcp_config.json**: MCP server configuration file

## Configuration File Description
- All configuration files are in JSON format
- Configuration files should be adjusted according to the actual environment
- Configuration changes should follow the project change management process

## Notes
- Sensitive information should not be directly stored in configuration files
- Configuration files should be regularly backed up
- After modifying configurations, relevant services should be restarted for the configuration to take effect