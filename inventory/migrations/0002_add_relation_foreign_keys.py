from django.db import migrations, models
import django.db.models.deletion


def forwards(apps, schema_editor):
    Stock = apps.get_model('inventory', 'Stock')
    User = apps.get_model('auth', 'User')
    Person = apps.get_model('core', 'Person')

    user_map = {user.username: user for user in User.objects.all()}
    person_map = {person.name: person for person in Person.objects.all()}

    for stock in Stock.objects.all():
        if stock.received_by and not stock.received_by_user_id:
            stock.received_by_user = user_map.get(stock.received_by)
        if stock.issued_by and not stock.issued_by_user_id:
            stock.issued_by_user = user_map.get(stock.issued_by)
        if stock.issued_to and not stock.issued_to_person_id:
            stock.issued_to_person = person_map.get(stock.issued_to)
        stock.save(update_fields=['received_by_user', 'issued_by_user', 'issued_to_person'])


def backwards(apps, schema_editor):
    Stock = apps.get_model('inventory', 'Stock')

    for stock in Stock.objects.all():
        if stock.received_by_user_id and not stock.received_by:
            stock.received_by = stock.received_by_user.username
        if stock.issued_by_user_id and not stock.issued_by:
            stock.issued_by = stock.issued_by_user.username
        if stock.issued_to_person_id and not stock.issued_to:
            stock.issued_to = stock.issued_to_person.name
        stock.save(update_fields=['received_by', 'issued_by', 'issued_to'])


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
        ('core', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='received_by_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stock_received_transactions', to='auth.user'),
        ),
        migrations.AddField(
            model_name='stock',
            name='issued_by_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stock_issued_transactions', to='auth.user'),
        ),
        migrations.AddField(
            model_name='stock',
            name='issued_to_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stock_received_items', to='core.person'),
        ),
        migrations.RunPython(forwards, backwards),
    ]
