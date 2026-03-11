"""
AI context for the Doc Templates module.
Loaded into the assistant system prompt when this module's tools are active.
"""

CONTEXT = """
## Module Knowledge: Doc Templates

### Models

**TemplateSettings** — singleton per hub with global print defaults.
- `default_paper_size` (choice): thermal_80mm, thermal_58mm, a4, a5, letter (default: thermal_80mm)
- `default_font_size` (int, default 12)
- `company_logo` (image, nullable)
- `company_name`, `company_address`, `company_tax_id`, `company_phone`, `company_email`, `company_website` (str fields)
- `footer_text` (text): default footer for all documents

**DocumentTemplate** — a reusable print/display template.
- `name` (str): template label
- `doc_type` (choice): receipt, invoice, quote, credit_note, delivery_note, custom
- `paper_size` (choice): thermal_80mm, thermal_58mm, a4, a5, letter
- `content` (text): body with `{{variable}}` placeholders
- `header_content`, `footer_content` (text): optional header/footer sections
- `css_styles` (text): custom CSS for HTML rendering
- `is_default` (bool): only one default per doc_type per hub (enforced on save)
- `is_active` (bool)
- `version` (int, default 1)

**TemplateVariable** — catalog of available template variables.
- `name` (str): placeholder name e.g. `sale.total`, `customer.name`
- `description` (text)
- `variable_group` (choice): sale, invoice, customer, product, company, custom
- `data_type` (choice): text, number, date, currency, image, list
- `example_value` (str)
- `is_system` (bool): system variables cannot be deleted

**GeneratedDocument** — archive of rendered documents.
- `template` (FK → DocumentTemplate, nullable): source template used
- `doc_type` (str): document type string
- `source_id` (UUID, nullable): ID of the originating object (sale, invoice, etc.)
- `rendered_content` (text): final HTML/text after variable substitution
- `file` (FileField, nullable): saved PDF/file
- `generated_at` (datetime, auto)

### Key flows

1. **Configure defaults**: update TemplateSettings (singleton, get_settings(hub_id)).
2. **Create a template**: set doc_type, paper_size, content with `{{variable}}` placeholders.
3. **Set as default**: set is_default=True — system automatically unsets the previous default for that doc_type.
4. **Render a document**: call template.render(context_data dict) — replaces `{{key}}` with values; unreplaced placeholders are removed.
5. **Archive rendered output**: create a GeneratedDocument with source_id pointing to the originating sale/invoice.

### Relationships
- GeneratedDocument.source_id → cross-module UUID reference (no FK constraint)
"""
