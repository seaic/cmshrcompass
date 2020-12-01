from django import forms
from hrcompass.models import Client, Task, Taskname, AuthUser


class DateInput(forms.DateInput):
    input_type = 'date'

class ClientForm(forms.ModelForm):
    class Meta:
        model= Client
        fields = "__all__"

class TaskForm(forms.ModelForm):
    class Meta:
        model= Task
        fields = "__all__"
        widgets = {
            'startdate': DateInput(),
            'duedate': DateInput(),
            'invoiced': DateInput(),
        }
    #def __init__(self, *args, **kwargs):
    #        super(TaskForm, self).__init__(*args, **kwargs)
    #        for field in self.fields.keys():
    #            self.fields[field].widget.attrs.update({'class' : 'forminput'})
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_name'].queryset = Taskname.objects.none()
        #print(self.fields['task_kind'].queryset)
        if 'kind' in self.data:
            try:
                kind_id = int(self.data.get('kind'))
                self.fields['task_name'].queryset = Taskname.objects.filter(task_kind_id=kind_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Taskname queryset
        elif self.instance.pk:
            #print("elif")
            self.fields['task_name'].queryset = self.instance.kind.taskname_set.order_by('name')
        #print(self.instance.pk)

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    email = forms.EmailField(required=False)
    class Meta:
        model = AuthUser
        fields = ('password', 'email',)