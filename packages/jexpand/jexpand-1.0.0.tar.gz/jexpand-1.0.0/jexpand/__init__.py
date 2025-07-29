"""
jexpand - Enhanced file expansion using Jinja2 templates
"""

from .main import expand_file, JinjaFileExpander

__version__ = "1.0.0"
__all__ = ["expand_file", "JinjaFileExpander", "main"]


def main():
    """Main entry point for the jexpand command-line tool"""
    import fire
    fire.Fire(expand_file)


if __name__ == "__main__":
    main() 