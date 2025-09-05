from django.contrib import admin
from .models import Train,Carriage,Seat,TrainSchedule

# Register your models here.
admin.site.site_header = "Train Admin panel"
admin.site.site_title = "Train"
admin.site.index_title = "admin panel"

@admin.action(description="Mark as on time")
def mark_on_time(modeladmin, request, queryset):
    queryset.update(status="on_time")

@admin.action(description="Mark as delayed")
def mark_delayed(modeladmin, request, queryset):
    queryset.update(status="delayed")

@admin.action(description="Mark as cancelled")
def mark_cancelled(modeladmin, request, queryset):
    queryset.update(status="cancelled")

@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ["name", "status"]
    list_filter = ("status",)
    search_fields = ("name",)
    list_editable = ("status",)
    
@admin.register(TrainSchedule)
class TrainScheduleAdmin(admin.ModelAdmin):
    list_display = ["train", "starting_location", "final_destination", "departure_date", "arrival_time", "status"]
    list_filter = ("status", "train")
    search_fields = ("starting_location", "final_destination")
    list_editable = ("status", "departure_date", "arrival_time")
    actions = [mark_on_time, mark_delayed, mark_cancelled]

@admin.register(Carriage)
class CarriageAdmin(admin.ModelAdmin):
    list_display = ["train", "carriage_number", "class_type", "seats"]
    list_filter = ["class_type", "train"]
    search_fields = ["train__name", "carriage_number"]


    
@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ["carriage", "seat_number"]
    list_filter = ["carriage__train", "carriage__class_type"]
    search_fields = ["carriage__train__name", "seat_number"]