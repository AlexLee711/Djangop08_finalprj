from django.contrib import admin
from mysite import models
from mysite.models import Post

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display=('user','build', 'floor','household')
    ordering=('build', 'floor', 'household')

class MailAdmin(admin.ModelAdmin):
    list_display=('user','mail_type','time', 'note','status')
    ordering=('-time', 'user', 'status')
    
class OptionAdmin(admin.ModelAdmin):
    list_display=('poll_id','title','count')
    ordering=('poll_id', '-count')

class PollAdmin(admin.ModelAdmin):
    list_display=('subject','date_created', 'end_date','enabled')
    ordering=('subject', '-date_created', '-end_date')

class ManagementFeeAdmin(admin.ModelAdmin):
    list_display = ('building', 'floor', 'household', 'title', 'amount', 'due_date', 'status')
    ordering=('-due_date', '-payment_date', 'status')
    def building(self, obj):
        return f"{obj.profile.build}棟"

    def floor(self, obj):
        return f"{obj.profile.floor}樓"

    def household(self, obj):
        return f"{obj.profile.household}戶"
    
    building.short_description = '棟數'
    floor.short_description = '樓層'
    household.short_description = '戶別'
    
class ActivityAdmin(admin.ModelAdmin):
    list_display=('name','date', 'location','current_participants','max_particioants')
    ordering=('name', 'date')

admin.site.register(Post)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.Mail, MailAdmin)
admin.site.register(models.Forum)
admin.site.register(models.Comment)
admin.site.register(models.Poll, PollAdmin)
admin.site.register(models.Option, OptionAdmin)
admin.site.register(models.ManagementFee, ManagementFeeAdmin)
admin.site.register(models.Activity, ActivityAdmin)
admin.site.register(models.ActivityApplication)
