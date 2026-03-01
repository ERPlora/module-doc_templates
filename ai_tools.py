"""AI tools for the Document Templates module."""
from assistant.tools import AssistantTool, register_tool


@register_tool
class ListDocumentTemplates(AssistantTool):
    name = "list_document_templates"
    description = "List document templates (receipt, invoice, quote, etc.)."
    module_id = "doc_templates"
    required_permission = "doc_templates.view_documenttemplate"
    parameters = {
        "type": "object",
        "properties": {"doc_type": {"type": "string", "description": "receipt, invoice, quote, credit_note, delivery_note, custom"}, "is_active": {"type": "boolean"}},
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from doc_templates.models import DocumentTemplate
        qs = DocumentTemplate.objects.all()
        if args.get('doc_type'):
            qs = qs.filter(doc_type=args['doc_type'])
        if 'is_active' in args:
            qs = qs.filter(is_active=args['is_active'])
        return {"templates": [{"id": str(t.id), "name": t.name, "doc_type": t.doc_type, "paper_size": t.paper_size, "is_default": t.is_default, "is_active": t.is_active} for t in qs]}


@register_tool
class CreateDocumentTemplate(AssistantTool):
    name = "create_document_template"
    description = "Create a document template."
    module_id = "doc_templates"
    required_permission = "doc_templates.add_documenttemplate"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}, "doc_type": {"type": "string"},
            "paper_size": {"type": "string", "description": "A4, Letter, etc."},
            "content": {"type": "string", "description": "Template HTML content"},
            "header_content": {"type": "string"}, "footer_content": {"type": "string"},
            "is_default": {"type": "boolean"},
        },
        "required": ["name", "doc_type"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from doc_templates.models import DocumentTemplate
        t = DocumentTemplate.objects.create(
            name=args['name'], doc_type=args['doc_type'],
            paper_size=args.get('paper_size', 'A4'), content=args.get('content', ''),
            header_content=args.get('header_content', ''), footer_content=args.get('footer_content', ''),
            is_default=args.get('is_default', False),
        )
        return {"id": str(t.id), "name": t.name, "created": True}
