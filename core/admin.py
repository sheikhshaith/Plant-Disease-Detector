from django.contrib import admin
from .models import *

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Plant._meta.fields]

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Disease._meta.fields]

@admin.register(DiseaseHistory)
class DiseaseHistoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DiseaseHistory._meta.fields]

@admin.register(FeedbackRating)
class FeedbackRatingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FeedbackRating._meta.fields]

@admin.register(EditHistory)
class EditHistoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EditHistory._meta.fields]

@admin.register(DeleteHistory)
class DeleteHistoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DeleteHistory._meta.fields]


