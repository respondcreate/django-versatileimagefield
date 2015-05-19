from django.contrib import admin
from django.forms import ModelForm

from versatileimagefield.widgets import VersatileImagePPOISelectWidget

from .models import VersatileImageTestModel, VersatileImageWidgetTestModel


class VersatileImageTestModelForm(ModelForm):

    class Meta:
        model = VersatileImageTestModel
        fields = (
            'image',
            'img_type',
            'optional_image',
            'optional_image_2',
            'optional_image_3'
        )
        widgets = {
            'optional_image': VersatileImagePPOISelectWidget(),
        }


class VersatileImageTestModelAdmin(admin.ModelAdmin):
    form = VersatileImageTestModelForm


admin.site.register(VersatileImageTestModel, VersatileImageTestModelAdmin)
admin.site.register(VersatileImageWidgetTestModel)
