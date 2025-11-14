# rules Directory Description

The rules directory is the project's rule file storage directory, containing the project's core rule definitions, file rules, and project variable configurations.

## 📁 Directory File Description

### Core Rule Files
- **project_rules_backup.txt**: Backup version of the project rule file
- **project_vars.txt**: Project variable configuration file, defining global variables
- **files_rules.txt**: File path rule records, defining file naming and classification rules
- **update_rules.txt**: Update rule configuration file

### Database Related Configuration
- **db_lists.txt**: Database list configuration file

## 📝 Rule File Description

### project_rules_backup.txt
- Backup version of the core project rule file
- Used for recovery when the main rule file is damaged or needs to be rolled back
- Must be updated in sync with the main rule file

### project_vars.txt
- Defines global variables used in the project
- Variable types include system_path_var, debug_var, and project_var
- Uses the `${var_name}|${var_type}|${var_title}` format for definition
- New variables must be registered in this file

### files_rules.txt
- Records naming rules and classifications for various files in the project
- Includes classifications for production code, test code, temporary files, etc.
- Defines the functional description and usage scenarios of files
- Records the correspondence between docs files and csdn_md files

### update_rules.txt
- Defines policies and methods for rule updates
- Configures parameters for rule pulling and synchronization

### db_lists.txt
- Defines database lists and related configurations
- Supports reading and using system environment variables

## 🔒 Rule File Management

- Updates to rule files must follow project specifications
- Important rule files must be backed up regularly
- Rule changes need to record change history
- Please do not modify rule files directly, updates should be made through the rule manager