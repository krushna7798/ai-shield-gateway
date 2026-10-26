# pyrefly: ignore[missing-import]
from django.db import models
# pyrefly: ignore[missing-import]
from django.core.validators import MinValueValidator, MaxValueValidator


class AIModelInventory(models.Model):
    """
    Inventory of approved AI models and their data clearance tier.
    """
    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        DEPRECATED = 'DEPRECATED', 'Deprecated'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        DISABLED = 'DISABLED', 'Disabled'

    DATA_TIER_CHOICES = [
        (1, 'Tier 1 - Public Data'),
        (2, 'Tier 2 - Internal / Proprietary Data'),
        (3, 'Tier 3 - Highly Restricted / Sensitive Data'),
    ]

    model_name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name or identifier of the AI model (e.g., 'gpt-4o', 'claude-3-5-sonnet', 'gemini-1.5-pro')"
    )
    vendor = models.CharField(
        max_length=255,
        help_text="Vendor or provider of the model (e.g., 'OpenAI', 'Anthropic', 'Google')"
    )
    approved_data_tier = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        choices=DATA_TIER_CHOICES,
        help_text="Maximum allowed sensitivity level (1-3) approved for this model"
    )
    status = models.CharField(
        max_length=50,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        help_text="Operational status of the model"
    )

    class Meta:
        verbose_name = 'AI Model Inventory'
        verbose_name_plural = 'AI Model Inventories'
        ordering = ['model_name']

    def __str__(self):
        return f"{self.model_name} ({self.vendor}) [Tier {self.approved_data_tier}] - {self.status}"


class ProvenanceLog(models.Model):
    """
    Audit log capturing AI model queries, data tier validation, and governance actions.
    """
    class ActionChoices(models.TextChoices):
        APPROVED = 'Approved', 'Approved'
        BLOCKED = 'Blocked', 'Blocked'
        FLAGGED = 'Flagged', 'Flagged'
        AUDITED = 'Audited', 'Audited'

    DATA_TIER_CHOICES = [
        (1, 'Tier 1 - Public Data'),
        (2, 'Tier 2 - Internal / Proprietary Data'),
        (3, 'Tier 3 - Highly Restricted / Sensitive Data'),
    ]

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Exact timestamp of the AI invocation/request"
    )
    user_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Identifier of the user or service initiating the request"
    )
    target_model = models.ForeignKey(
        AIModelInventory,
        on_delete=models.CASCADE,
        related_name='provenance_logs',
        help_text="The AI model targeted by the user"
    )
    data_tier_submitted = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        choices=DATA_TIER_CHOICES,
        help_text="Sensitivity tier (1-3) of the payload data submitted"
    )
    action_taken = models.CharField(
        max_length=100,
        choices=ActionChoices.choices,
        default=ActionChoices.APPROVED,
        help_text="Policy enforcement action executed by the governance engine"
    )

    class Meta:
        verbose_name = 'Provenance Log'
        verbose_name_plural = 'Provenance Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return (
            f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] User: {self.user_id} | "
            f"Target: {self.target_model.model_name} | Action: {self.action_taken}"
        )


class CorporatePolicy(models.Model):
    """
    Corporate Data Loss Prevention Policy.
    Defines security and compliance rules for classifying data into Tiers 1, 2, and 3.
    """
    title = models.CharField(
        max_length=255,
        default="Enterprise DLP & Data Classification Policy",
        help_text="Title or identifier for this corporate policy"
    )
    content = models.TextField(
        help_text="Detailed rules defining Tier 1, Tier 2, and Tier 3 classifications"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this policy is currently active and enforced"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Corporate Policy'
        verbose_name_plural = 'Corporate Policies'

    def __str__(self):
        return f"{self.title} (Active: {self.is_active})"

