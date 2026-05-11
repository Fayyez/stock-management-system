from django import forms

from scrum_board.models import Scrums, ScrumTitles


class AddScrumListForm(forms.ModelForm):
    class Meta:
        model = ScrumTitles
        fields = ['lists']


class AddScrumTaskForm(forms.ModelForm):
    class Meta:
        model = Scrums
        fields = ['task', 'task_description', 'task_date']
