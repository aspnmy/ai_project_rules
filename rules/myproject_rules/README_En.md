# Development Project Private Specification Configuration Directory

## Directory Description

This directory is used to store private rule configuration files for the development project, containing the following files:

- `myproject_rules.txt` - Private rule definition file
- `myproject_vars.txt` - Private variable definition file

## File Function Description

### myproject_rules.txt

Private rule definition file used to store project-specific rule configurations, including:
- Project path variable definitions
- Specification type settings
- Private rule entry definitions

### myproject_vars.txt

Private variable definition file used to store project-specific variables, all variables are named with the `My_` prefix.

## Usage Method

1. Edit `myproject_rules.txt` to add or modify project rules
2. Edit `myproject_vars.txt` to add or modify project variables
3. Rule files need to be registered in `rules\project_vars.txt` to take effect

## Specification Requirements

- Rule files must use relative paths, absolute paths are prohibited
- Variable naming must comply with the `My_` prefix specification
- After modifying rules, relevant services need to be restarted for the configuration to take effect