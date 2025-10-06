from django.contrib import admin
from .models import Case, CaseNote


class CaseNoteInline(admin.TabularInline):
    model = CaseNote
    extra = 0
    readonly_fields = ['author', 'created_at']


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'violation', 'investigator', 'status', 'final_penalty',
        'created_at', 'closed_at'
    ]
    list_filter = ['status', 'created_at', 'closed_at']
    search_fields = ['violation__regulated_product__name', 'notes', 'resolution_notes']
    readonly_fields = ['created_at', 'updated_at', 'closed_at']
    inlines = [CaseNoteInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Case Information', {
            'fields': ('violation', 'investigator', 'status')
        }),
        ('Investigation Details', {
            'fields': ('notes', 'resolution_notes', 'final_penalty')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'closed_at')
        }),
    )


@admin.register(CaseNote)
class CaseNoteAdmin(admin.ModelAdmin):
    list_display = ['case', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'case__violation__regulated_product__name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
