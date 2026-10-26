"""
URL configuration for shadow_ai project.
"""
# pyrefly: ignore[missing-import]
from django.contrib import admin
# pyrefly: ignore[missing-import]
from django.urls import path
from governance.views import (
    audit_dashboard,
    employee_simulator,
    employee_portal,
    send_prompt_api,
    privacy_policy,
    terms_and_conditions
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', audit_dashboard, name='dashboard'),
    path('portal/', employee_portal, name='portal'),
    path('simulate/', employee_simulator, name='simulate'),
    path('api/send-prompt/', send_prompt_api, name='send_prompt_api'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('privacy/', privacy_policy, name='privacy_alias'),
    path('terms/', terms_and_conditions, name='terms_and_conditions'),
]
