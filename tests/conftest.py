"""
Fixtures for doc_templates module tests.
"""

import os
import uuid
import pytest
from decimal import Decimal
from django.test import Client


os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'


@pytest.fixture(autouse=True)
def _set_hub_config(db, settings):
    """Ensure HubConfig + StoreConfig exist."""
    from apps.configuration.models import HubConfig, StoreConfig
    config = HubConfig.get_solo()
    config.save()
    store = StoreConfig.get_solo()
    store.business_name = 'Test Business'
    store.is_configured = True
    store.save()


@pytest.fixture
def hub_id(db):
    from apps.configuration.models import HubConfig
    return HubConfig.get_solo().hub_id


@pytest.fixture
def employee(db):
    """Create a local user (employee)."""
    from apps.accounts.models import LocalUser
    return LocalUser.objects.create(
        name='Test Employee',
        email='employee@test.com',
        role='admin',
        is_active=True,
    )


@pytest.fixture
def auth_client(employee):
    """Authenticated Django test client."""
    client = Client()
    session = client.session
    session['local_user_id'] = str(employee.id)
    session['user_name'] = employee.name
    session['user_email'] = employee.email
    session['user_role'] = employee.role
    session['store_config_checked'] = True
    session.save()
    return client


@pytest.fixture
def template_settings(hub_id):
    """Get or create template settings for the test hub."""
    from doc_templates.models import TemplateSettings
    return TemplateSettings.get_settings(hub_id)


@pytest.fixture
def receipt_template(hub_id):
    """Create a receipt template."""
    from doc_templates.models import DocumentTemplate
    return DocumentTemplate.objects.create(
        hub_id=hub_id,
        name='Default Receipt',
        doc_type='receipt',
        paper_size='thermal_80mm',
        content='Receipt #{{sale.number}}\nDate: {{sale.date}}\nTotal: {{sale.total}}\nThank you, {{customer.name}}!',
        header_content='{{company.name}}',
        footer_content='Thank you for your purchase!',
        is_default=True,
        is_active=True,
    )


@pytest.fixture
def invoice_template(hub_id):
    """Create an invoice template."""
    from doc_templates.models import DocumentTemplate
    return DocumentTemplate.objects.create(
        hub_id=hub_id,
        name='Standard Invoice',
        doc_type='invoice',
        paper_size='a4',
        content='Invoice {{invoice.number}}\nDate: {{invoice.date}}\nDue: {{invoice.due_date}}\nCustomer: {{customer.name}}\nTotal: {{sale.total}}',
        header_content='{{company.name}} - {{company.tax_id}}',
        footer_content='Payment terms: 30 days',
        is_default=True,
        is_active=True,
    )


@pytest.fixture
def system_variable(hub_id):
    """Create a system template variable."""
    from doc_templates.models import TemplateVariable
    return TemplateVariable.objects.create(
        hub_id=hub_id,
        name='sale.total',
        description='Total amount of the sale',
        variable_group='sale',
        data_type='currency',
        example_value='100.00',
        is_system=True,
    )


@pytest.fixture
def custom_variable(hub_id):
    """Create a custom template variable."""
    from doc_templates.models import TemplateVariable
    return TemplateVariable.objects.create(
        hub_id=hub_id,
        name='custom.loyalty_points',
        description='Customer loyalty points',
        variable_group='custom',
        data_type='number',
        example_value='150',
        is_system=False,
    )


@pytest.fixture
def generated_doc(hub_id, receipt_template):
    """Create a generated document record."""
    from doc_templates.models import GeneratedDocument
    return GeneratedDocument.objects.create(
        hub_id=hub_id,
        template=receipt_template,
        doc_type='receipt',
        source_id=uuid.uuid4(),
        rendered_content='Receipt #20260222-0001\nDate: 22/02/2026\nTotal: 100.00\nThank you, Jane Smith!',
    )
