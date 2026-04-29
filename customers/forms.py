from django import forms
from .models import SearchTask

class SearchTaskForm(forms.ModelForm):
    # 增加搜索引擎选择
    search_engine = forms.ChoiceField(
        choices=[('google', 'Google'), ('baidu', '百度')],
        label='搜索引擎',
        initial='google',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = SearchTask
        fields = ['name', 'keyword', 'max_results', 'target_country', 'search_engine']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'keyword': forms.TextInput(attrs={'class': 'form-control'}),
            'max_results': forms.NumberInput(attrs={'class': 'form-control'}),
            'target_country': forms.TextInput(attrs={'class': 'form-control'}),
        }