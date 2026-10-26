from django.contrib import admin
from .models import AIModelInventory, ProvenanceLog, CorporatePolicy


@admin.register(AIModelInventory)
class AIModelInventoryAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'vendor', 'approved_data_tier', 'status')
    list_filter = ('status', 'approved_data_tier', 'vendor')
    search_fields = ('model_name', 'vendor')
    ordering = ('model_name',)


@admin.register(ProvenanceLog)
class ProvenanceLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'timestamp',
        'user_id',
        'target_model',
        'data_tier_submitted',
        'action_taken',
    )
    list_filter = ('action_taken', 'data_tier_submitted', 'target_model')
    search_fields = ('user_id', 'target_model__model_name')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)


@admin.register(CorporatePolicy)
class CorporatePolicyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'updated_at', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'content')
    ordering = ('-updated_at',)

