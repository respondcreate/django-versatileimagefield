from django.contrib import admin
from django.forms import ModelForm

from versatileimagefield.widgets import VersatileImagePPOISelectWidget

from .models import VersatileImageTestModel


class VersatileImageTestModelForm(ModelForm):

    class Meta:
        model = VersatileImageTestModel
        exclude = ('ppoi',)
        widgets = {
            'optional_image': VersatileImagePPOISelectWidget(),
        }


class VersatileImageTestModelAdmin(admin.ModelAdmin):
    form = VersatileImageTestModelForm


admin.site.register(VersatileImageTestModel, VersatileImageTestModelAdmin)
