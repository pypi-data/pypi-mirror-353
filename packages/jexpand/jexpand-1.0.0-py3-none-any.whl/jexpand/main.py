#!/usr/bin/env python3.10
"""
Enhanced file expansion using Jinja2 templates with flexible functionality.

Example usage:



jexpand template.md > expanded.md




This will process Jinja2 templates with custom functions for file inclusion,
code formatting, and more advanced template features.

Template example:
```template.md
You will be given several files, your goal is to convert the implementation.

<source_implementation>
{{ include_file('/path/to/source/file.py') }}
</source_implementation>

<target_framework>
{{ include_file('/path/to/target/framework/example.py', language='python') }}
</target_framework>

<reference_implementation>
{{ include_file('/path/to/reference/implementation.py') | code_block('python') }}
</reference_implementation>

<!-- Advanced features -->
{% if file_exists('/path/to/optional/file.py') %}
<optional_file>
{{ include_file('/path/to/optional/file.py') }}
</optional_file>
{% endif %}

<!-- Loop through multiple files -->
{% for file_path in ['/path/file1.py', '/path/file2.py'] %}
<{{ loop.index }}>
{{ include_file(file_path) }}
</{{ loop.index }}>
{% endfor %}
```
"""

import os
import sys
from pathlib import Path
import fire
from jinja2 import Environment, FileSystemLoader, BaseLoader, Template
from jinja2.exceptions import TemplateNotFound


class StringLoader(BaseLoader):
    """Custom loader for loading templates from strings"""
    def __init__(self, template_string):
        self.template_string = template_string
    
    def get_source(self, environment, template):
        return self.template_string, None, lambda: True


class JinjaFileExpander:
    def __init__(self, template_dir=None, strict_mode=True):
        """
        Initialize the Jinja2 file expander
        
        Args:
            template_dir: Directory to look for template files (optional)
            strict_mode: If True, raises errors for missing files. If False, returns placeholder text.
        """
        self.strict_mode = strict_mode
        
        if template_dir:
            loader = FileSystemLoader(template_dir)
        else:
            loader = FileSystemLoader(os.getcwd())
            
        self.env = Environment(
            loader=loader,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # Register custom functions
        self.env.globals.update({
            'include_file': self._include_file,
            'file_exists': self._file_exists,
            'file_size': self._file_size,
            'file_extension': self._file_extension,
            'basename': self._basename,
            'dirname': self._dirname,
        })
        
        # Register custom filters
        self.env.filters.update({
            'code_block': self._code_block_filter,
            'indent': self._indent_filter,
            'comment_out': self._comment_out_filter,
        })
    
    def _include_file(self, file_path, encoding='utf-8', default=''):
        """Include the contents of a file"""
        if file_path.startswith('~'):
            file_path = os.path.expanduser(file_path)
        try:
            if not os.path.isfile(file_path):
                if self.strict_mode:
                    raise FileNotFoundError(f"File {file_path} does not exist")
                return default or f"<!-- File not found: {file_path} -->"
            
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            if self.strict_mode:
                raise
            return default or f"<!-- Error reading file {file_path}: {str(e)} -->"
    
    def _file_exists(self, file_path):
        """Check if a file exists"""
        return os.path.isfile(file_path)
    
    def _file_size(self, file_path):
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except:
            return 0
    
    def _file_extension(self, file_path):
        """Get file extension"""
        return Path(file_path).suffix
    
    def _basename(self, file_path):
        """Get basename of file"""
        return os.path.basename(file_path)
    
    def _dirname(self, file_path):
        """Get directory name of file"""
        return os.path.dirname(file_path)
    
    def _code_block_filter(self, content, language=''):
        """Wrap content in markdown code block"""
        return f"```{language}\n{content}\n```"
    
    def _indent_filter(self, content, spaces=4):
        """Indent each line with specified number of spaces"""
        indent = ' ' * spaces
        return '\n'.join(indent + line for line in content.splitlines())
    
    def _comment_out_filter(self, content, comment_char='#'):
        """Comment out each line"""
        return '\n'.join(f"{comment_char} {line}" for line in content.splitlines())
    
    def expand_string(self, template_string, context=None):
        """Expand a template string"""
        context = context or {}
        template = Template(template_string, environment=self.env)
        return template.render(**context)
    
    def expand_file(self, template_path, context=None, output_path=None):
        """Expand a template file"""
        context = context or {}
        
        try:
            template = self.env.get_template(os.path.basename(template_path))
        except TemplateNotFound:
            # If not found in template directory, try direct path
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            template = Template(template_content, environment=self.env)
        
        result = template.render(**context)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
        else:
            print(result)
        
        return result


def expand_file(file_path, output_path=None, strict=True, **context):
    """
    Main function for command line usage
    
    Args:
        file_path: Path to template file
        output_path: Optional output file path
        strict: Whether to use strict mode (default: True)
        **context: Additional context variables for template
    """
    expander = JinjaFileExpander(strict_mode=strict)
    return expander.expand_file(file_path, context, output_path)


# Example usage and backward compatibility
def simple_expand(file_path):
    """Simple expansion for backward compatibility with original script"""
    expander = JinjaFileExpander(strict_mode=True)
    
    # Read the file and convert simple {file_path} syntax to Jinja2
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert {/path/to/file} to {{ include_file('/path/to/file') }}
    import re
    converted = re.sub(r'\{([^}]+)\}', r"{{ include_file('\1') }}", content)
    
    result = expander.expand_string(converted)
    print(result)


if __name__ == "__main__":
    fire.Fire(expand_file)