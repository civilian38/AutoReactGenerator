from django.db import migrations
from django.db.models import Case, When, Value

def update_method_orders(apps, schema_editor):
    APIDoc = apps.get_model('apidoc', 'APIDoc')

    APIDoc.objects.all().update(
        method_order=Case(
            When(http_method='GET', then=Value(1)),
            When(http_method='POST', then=Value(2)),
            When(http_method='PUT', then=Value(3)),
            When(http_method='DELETE', then=Value(4)),
            When(http_method='PATCH', then=Value(5)),
            When(http_method='HEAD', then=Value(6)),
            When(http_method='OPTIONS', then=Value(7)),
            default=Value(99) # 예외 케이스
        )
    )

class Migration(migrations.Migration):

    dependencies = [
        ("apidoc", "0004_alter_apidoc_options_apidoc_method_order"),
    ]

    operations = [
        migrations.RunPython(update_method_orders),
    ]

