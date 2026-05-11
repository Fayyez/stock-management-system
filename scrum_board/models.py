from django.db import models


class Scrums(models.Model):
    task = models.CharField(max_length=100, blank=True, null=True)
    task_description = models.CharField(max_length=100, blank=True, null=True)
    task_date = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    class Meta:
        db_table = 'stock_scrums'
        managed = False

    def __str__(self):
        return self.task


class ScrumTitles(models.Model):
    lists = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = 'stock_scrumtitles'
        managed = False

    def __str__(self):
        return str(self.lists)
