"""
MailScript - A Python library for simplified email sending.

This package provides tools to easily send emails with support for:
- Plain text and HTML emails
- Template rendering
- File attachments
- Email validation
"""

__version__ = "0.1.0"

from .mailer import Mailer

__all__ = ["Mailer"]
