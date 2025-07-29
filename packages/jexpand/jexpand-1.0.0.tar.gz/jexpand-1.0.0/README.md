# JExpand - Jinja2 Template File Expander

Enhanced file expansion using Jinja2 templates with flexible functionality for including files, conditional content, and more.

## Installation

```bash
pip install -e .
```

## Usage

### Command Line

```bash
# Basic usage
jexpand template.md > expanded.md

# With output file
jexpand template.md --output_path expanded.md

# Non-strict mode (won't fail on missing files)
jexpand template.md --strict=False
```

### Python Module

```bash
# Run as module
python -m jexpand template.md > expanded.md
```

### Template Features

JExpand supports powerful Jinja2 templates with custom functions and filters:

#### Custom Functions

- `include_file(path)` - Include the contents of a file
- `file_exists(path)` - Check if a file exists
- `file_size(path)` - Get file size in bytes
- `file_extension(path)` - Get file extension
- `basename(path)` - Get basename of file
- `dirname(path)` - Get directory name of file

#### Custom Filters

- `code_block(language)` - Wrap content in markdown code block
- `indent(spaces)` - Indent each line with specified spaces
- `comment_out(comment_char)` - Comment out each line

#### Example Template

```jinja2
# My Project Documentation

## Source Implementation
{{ include_file('src/main.py') | code_block('python') }}

## Configuration
{% if file_exists('config.yaml') %}
{{ include_file('config.yaml') | code_block('yaml') }}
{% else %}
No configuration file found.
{% endif %}

## Multiple Files
{% for file_path in ['file1.py', 'file2.py'] %}
### {{ basename(file_path) }}
{{ include_file(file_path) | indent(4) }}
{% endfor %}
```

## Development

### Local Installation

```bash
# Install in development mode
pip install -e .

# Test the command
jexpand --help
```

### Package Structure

```
jexpand/
├── jexpand/
│   ├── __init__.py      # Main package code
│   └── __main__.py      # Module entry point
├── pyproject.toml       # Package configuration
├── README.md           # This file
└── setup.py            # Setuptools configuration
```

## License

MIT License 