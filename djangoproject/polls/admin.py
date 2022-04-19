from django.contrib import admin
from .models import Question, Choice
# Register your models here.

# defined Choice UI which should be bound to Question UI
# class ChoiceInline(admin.StackedInline):

# space saver with tabular inline
class ChoiceInline(admin.TabularInline):

    model = Choice
    extra = 3

# defined custom admin subclass for Question model
class QuestionAdmin(admin.ModelAdmin):
    # fieldset takes tupples
    # first element is the title of the fieldset
    # ie: "Date information"
    fieldsets = [
      (None,               {'fields': ['question_text']}),
      ('Date information', {'fields': ['pub_date']}),
    ]
    # bound choice UI with Question UI with "inlines" property
    inlines = [ChoiceInline]

    # display more infor for each question
    list_display = ('question_text', 'pub_date', 'was_published_recently')

    # add date filter on UI
    list_filter = ['pub_date']

    # add serch field for 'qeustion text'
    search_fields = ['question_text']

# admin.site.register(Question)

# register the models with customized subclass
admin.site.register(Question, QuestionAdmin)

# register default Choice admin UI
# admin.site.register(Choice)