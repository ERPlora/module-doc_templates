# Document Templates Module

Customizable document templates for receipts, invoices, and reports.

## Features

- Create and manage document templates for receipts, invoices, quotes, credit notes, delivery notes, and custom documents
- Support for multiple paper sizes: Thermal 80mm, Thermal 58mm, A4, A5, Letter
- Variable placeholder system using `{{variable}}` syntax with automatic substitution
- Template variables organized by group: Sale, Invoice, Customer, Product, Company, Custom
- Variable data types: Text, Number, Date, Currency, Image, List
- Custom CSS styles per template
- Separate header and footer content sections
- Default template per document type (one default enforced per type per hub)
- Template versioning
- Company branding settings: logo, name, address, tax ID, phone, email, website
- Generated document history with rendered content and file storage
- System vs. custom variable distinction

## Installation

This module is installed automatically via the ERPlora Marketplace.

## Configuration

Access settings via: **Menu > Templates > Settings**

Settings include:
- Default paper size and font size
- Company logo, name, address, and contact information
- Tax ID
- Footer text

## Usage

Access via: **Menu > Templates**

### Views

| View | URL | Description |
|------|-----|-------------|
| Templates | `/m/doc_templates/dashboard/` | List, create and manage document templates |
| Variables | `/m/doc_templates/variables/` | View and manage template variables |
| Settings | `/m/doc_templates/settings/` | Module and company branding configuration |

## Models

| Model | Description |
|-------|-------------|
| `TemplateSettings` | Per-hub configuration for paper size, font size, company branding, and footer text |
| `DocumentTemplate` | A document template with name, type, paper size, content (with variable placeholders), header, footer, CSS, default flag, and version |
| `TemplateVariable` | An available variable for templates with name, group, data type, example value, and system flag |
| `GeneratedDocument` | Record of a rendered document with template reference, source ID, rendered content, and generated file |

## Permissions

| Permission | Description |
|------------|-------------|
| `doc_templates.view_template` | View document templates |
| `doc_templates.add_template` | Create new document templates |
| `doc_templates.change_template` | Edit existing document templates |
| `doc_templates.delete_template` | Delete document templates |
| `doc_templates.manage_settings` | Manage module settings |

## License

MIT

## Author

ERPlora Team - support@erplora.com
