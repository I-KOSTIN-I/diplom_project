from django.contrib import admin

from goals.models import GoalCategory, Goal, GoalComment


class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated")
    search_fields = ("title", "user")


class GoalAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'category', 'status', 'priority')
    search_fields = ('title', 'description')


class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'text')
    readonly_fields = ('created', 'updated')


admin.site.register(GoalCategory, GoalCategoryAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(GoalComment, GoalCommentAdmin)
