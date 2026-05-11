# Generated manually for Phase 1 foundation architecture updates

from django.core import validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0005_alter_contacts_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stockhistory',
            options={'ordering': ['-timestamp'], 'verbose_name_plural': 'Stock Histories'},
        ),
        migrations.AlterField(
            model_name='contacts',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='stock/images'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stock.category'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='stock',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='stock/images'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='issue_quantity',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='stock',
            name='quantity',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='stock',
            name='re_order',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='stock',
            name='receive_quantity',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='stockhistory',
            name='issue_quantity',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='stockhistory',
            name='quantity',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='stockhistory',
            name='re_order',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='stockhistory',
            name='receive_quantity',
            field=models.IntegerField(blank=True, default=0, null=True, validators=[validators.MinValueValidator(0)]),
        ),
        migrations.AddIndex(
            model_name='stock',
            index=models.Index(fields=['item_name'], name='stock_stock_item_na_d62049_idx'),
        ),
        migrations.AddIndex(
            model_name='stock',
            index=models.Index(fields=['category'], name='stock_stock_categor_014078_idx'),
        ),
        migrations.AddIndex(
            model_name='stock',
            index=models.Index(fields=['last_updated'], name='stock_stock_last_up_2cd471_idx'),
        ),
        migrations.AddIndex(
            model_name='stockhistory',
            index=models.Index(fields=['item_name'], name='stock_stockh_item_na_26f302_idx'),
        ),
        migrations.AddIndex(
            model_name='stockhistory',
            index=models.Index(fields=['timestamp'], name='stock_stockh_timesta_d8c4d3_idx'),
        ),
    ]
