# Document Templates

## Overview

| Property | Value |
|----------|-------|
| **Module ID** | `doc_templates` |
| **Version** | `1.0.0` |
| **Icon** | `document-text-outline` |
| **Dependencies** | None |

## Models

### `TemplateSettings`

Per-hub document template configuration.

| Field | Type | Details |
|-------|------|---------|
| `default_paper_size` | CharField | max_length=20, choices: thermal_80mm, thermal_58mm, a4, a5, letter |
| `default_font_size` | IntegerField |  |
| `company_logo` | ImageField | max_length=100, optional |
| `company_name` | CharField | max_length=255, optional |
| `company_address` | TextField | optional |
| `company_tax_id` | CharField | max_length=50, optional |
| `company_phone` | CharField | max_length=20, optional |
| `company_email` | EmailField | max_length=254, optional |
| `company_website` | URLField | max_length=200, optional |
| `footer_text` | TextField | optional |

**Methods:**

- `get_settings()` — Get or create settings for a hub.

### `DocumentTemplate`

Template definition for documents.

| Field | Type | Details |
|-------|------|---------|
| `name` | CharField | max_length=200 |
| `doc_type` | CharField | max_length=20, choices: receipt, invoice, quote, credit_note, delivery_note, custom |
| `paper_size` | CharField | max_length=20, choices: thermal_80mm, thermal_58mm, a4, a5, letter |
| `content` | TextField |  |
| `header_content` | TextField | optional |
| `footer_content` | TextField | optional |
| `css_styles` | TextField | optional |
| `is_default` | BooleanField |  |
| `is_active` | BooleanField |  |
| `version` | PositiveIntegerField |  |

**Methods:**

- `render()` — Render the template with variable substitution.

Replaces {{variable}} placeholders with values from context_data.

### `TemplateVariable`

Available variables for document templates.

| Field | Type | Details |
|-------|------|---------|
| `name` | CharField | max_length=100 |
| `description` | TextField | optional |
| `variable_group` | CharField | max_length=20, choices: sale, invoice, customer, product, company, custom |
| `data_type` | CharField | max_length=20, choices: text, number, date, currency, image, list |
| `example_value` | CharField | max_length=255, optional |
| `is_system` | BooleanField |  |

### `GeneratedDocument`

Record of generated documents.

| Field | Type | Details |
|-------|------|---------|
| `template` | ForeignKey | → `doc_templates.DocumentTemplate`, on_delete=SET_NULL, optional |
| `doc_type` | CharField | max_length=50 |
| `source_id` | UUIDField | max_length=32, optional |
| `rendered_content` | TextField |  |
| `file` | FileField | max_length=100, optional |
| `generated_at` | DateTimeField | optional |

## Cross-Module Relationships

| From | Field | To | on_delete | Nullable |
|------|-------|----|-----------|----------|
| `GeneratedDocument` | `template` | `doc_templates.DocumentTemplate` | SET_NULL | Yes |

## URL Endpoints

Base path: `/m/doc_templates/`

| Path | Name | Method |
|------|------|--------|
| `(root)` | `dashboard` | GET |
| `create/` | `template_create` | GET/POST |
| `<uuid:pk>/edit/` | `template_edit` | GET |
| `<uuid:pk>/delete/` | `template_delete` | GET/POST |
| `<uuid:pk>/duplicate/` | `template_duplicate` | GET |
| `<uuid:pk>/preview/` | `template_preview` | GET |
| `<uuid:pk>/set-default/` | `template_set_default` | GET |
| `variables/` | `variables` | GET |
| `variables/create/` | `variable_create` | GET/POST |
| `variables/<uuid:pk>/delete/` | `variable_delete` | GET/POST |
| `api/render/` | `api_render` | GET |
| `settings/` | `settings` | GET |
| `settings/save/` | `settings_save` | GET/POST |

## Permissions

| Permission | Description |
|------------|-------------|
| `doc_templates.view_template` | View Template |
| `doc_templates.add_template` | Add Template |
| `doc_templates.change_template` | Change Template |
| `doc_templates.delete_template` | Delete Template |
| `doc_templates.manage_settings` | Manage Settings |

**Role assignments:**

- **admin**: All permissions
- **manager**: `add_template`, `change_template`, `view_template`
- **employee**: `add_template`, `view_template`

## Navigation

| View | Icon | ID | Fullpage |
|------|------|----|----------|
| Templates | `document-text-outline` | `dashboard` | No |
| Variables | `code-outline` | `variables` | No |
| Settings | `settings-outline` | `settings` | No |

## AI Tools

Tools available for the AI assistant:

### `list_document_templates`

List document templates (receipt, invoice, quote, etc.).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `doc_type` | string | No | receipt, invoice, quote, credit_note, delivery_note, custom |
| `is_active` | boolean | No |  |

### `create_document_template`

Create a document template.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes |  |
| `doc_type` | string | Yes |  |
| `paper_size` | string | No | A4, Letter, etc. |
| `content` | string | No | Template HTML content |
| `header_content` | string | No |  |
| `footer_content` | string | No |  |
| `is_default` | boolean | No |  |

## File Structure

```
README.md
__init__.py
ai_tools.py
apps.py
forms.py
locale/
  en/
    LC_MESSAGES/
      django.po
  es/
    LC_MESSAGES/
      django.po
migrations/
  0001_initial.py
  __init__.py
models.py
module.py
static/
  doc_templates/
    css/
templates/
  doc_templates/
    pages/
      dashboard.html
      settings.html
      template_form.html
      variables.html
    partials/
      dashboard_content.html
      preview.html
      settings_content.html
      template_form_content.html
      variable_form.html
      variables_content.html
tests/
  __init__.py
  conftest.py
  test_models.py
  test_views.py
urls.py
views.py
```
