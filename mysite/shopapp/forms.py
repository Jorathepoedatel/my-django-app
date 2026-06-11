from django import forms
from django.contrib.auth.models import Group

from shopapp.models import Product


# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['name', 'description', 'price', 'discount']
#
#
# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ['user', 'products', 'delivery_address','promocode']


class GroupsForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        return files.getlist(name)


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    # Без этого метода валидация упадёт на списке файлов
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result



class ProductForm(forms.ModelForm):
    images = MultipleFileField(required=False)

    # images = forms.FileField(
    #     widget=MultipleFileInput(),
    #     required=False
    # )
    class Meta:
        model = Product
        fields = ["name", "price", "description", "discount", "preview_image"]


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()