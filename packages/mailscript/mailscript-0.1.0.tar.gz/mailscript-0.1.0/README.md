# MailScript

A Python library for simplified email sending with support for templates, attachments, and more.

## Features

- Send plain text and HTML emails
- Template rendering with Jinja2
- Email address validation
- File attachments
- Support for CC and BCC recipients
- TLS/SSL encryption

## Installation

```bash
pip install mailscript
```

## Quick Start

### Basic Usage

```python
from mailscript import Mailer

# Initialize mailer
mailer = Mailer(
    smtp_host="smtp.example.com", 
    smtp_port=587,
    smtp_user="your-email@example.com",
    smtp_password="your-password",
    use_tls=True
)

# Send a simple email
mailer.send(
    sender="your-email@example.com",
    recipients="recipient@example.com",
    subject="Hello from MailScript",
    body="This is a test email from MailScript."
)
```

### HTML Emails

```python
# Send an HTML email
html_content = """
<!DOCTYPE html>
<html>
<body>
    <h1>Hello from MailScript</h1>
    <p>This is an <b>HTML</b> email!</p>
</body>
</html>
"""

mailer.send(
    sender="your-email@example.com",
    recipients="recipient@example.com",
    subject="HTML Email Test",
    body=html_content,
    is_html=True
)
```

### Template Rendering

```python
from mailscript.templates import TemplateRenderer

# Initialize renderer
renderer = TemplateRenderer()

# Render template from string
template = """
<h1>Hello, {{ name }}!</h1>
<p>Welcome to {{ company }}.</p>
"""

context = {"name": "John", "company": "Example Corp"}
html_content = renderer.render_from_string(template, context)

# Send templated email
mailer.send(
    sender="your-email@example.com",
    recipients="recipient@example.com",
    subject="Welcome Email",
    body=html_content,
    is_html=True
)
```

### Built-in Template Methods

```python
# Send an email using a template string directly
context = {
    "name": "John", 
    "features": ["Templates", "Attachments", "HTML Support"]
}

mailer.send_template(
    sender="your-email@example.com",
    recipients="recipient@example.com",
    subject="Welcome Email",
    template_string="<h1>Welcome, {{ name }}!</h1><ul>{% for feature in features %}<li>{{ feature }}</li>{% endfor %}</ul>",
    context=context,
    is_html=True
)

# Send an email using a template file
mailer.send_template_file(
    sender="your-email@example.com",
    recipients="recipient@example.com",
    subject="Newsletter",
    template_name="newsletter.html",
    template_folder="/path/to/templates",
    context={"name": "John", "month": "June"},
    is_html=True
)
)
```

### With Attachments

```python
# Send email with attachment
with open("document.pdf", "rb") as f:
    attachments = {"document.pdf": f}
    
    mailer.send(
        sender="your-email@example.com",
        recipients="recipient@example.com",
        subject="Email with attachment",
        body="Please find the attached document.",
        attachments=attachments
    )
```

## Command Line Usage

MailScript can be used from the command line directly:

```bash
# Send a simple email
python -m mailscript send --host smtp.example.com --port 587 --user "your-user" \
  --from "sender@example.com" --to "recipient@example.com" \
  --subject "Hello from CLI" --body "This is a test email from the command line"

# Send an HTML email from a file
python -m mailscript send --host smtp.example.com --port 587 --user "your-user" \
  --from "sender@example.com" --to "recipient@example.com" \
  --subject "HTML Test" --body-file email.html --html

# Send a templated email
python -m mailscript template --host smtp.example.com --port 587 --user "your-user" \
  --from "sender@example.com" --to "recipient@example.com" \
  --subject "Template Test" --template "templates/welcome.html" \
  --context "name=John" "company=Example Corp"

# Show version
python -m mailscript version
```

For more CLI options, run:

```bash
python -m mailscript send --help
python -m mailscript template --help
```

## License

MIT License
