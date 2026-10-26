# pyrefly: ignore[missing-import]
import json
# pyrefly: ignore[missing-import]
from django.shortcuts import render
# pyrefly: ignore[missing-import]
from django.http import JsonResponse
# pyrefly: ignore[missing-import]
from django.views.decorators.csrf import csrf_exempt
from governance.models import ProvenanceLog, AIModelInventory


def audit_dashboard(request):
    """
    Renders the utilitarian governance audit dashboard.
    Fetches all ProvenanceLog records ordered by timestamp (newest first).
    """
    logs = ProvenanceLog.objects.select_related('target_model').order_by('-timestamp')
    total_logs = logs.count()
    blocked_count = logs.filter(action_taken='Blocked').count()
    approved_count = logs.filter(action_taken='Approved').count()
    registered_models_count = AIModelInventory.objects.count()

    context = {
        'logs': logs,
        'total_logs': total_logs,
        'blocked_count': blocked_count,
        'approved_count': approved_count,
        'registered_models_count': registered_models_count,
    }
    return render(request, 'audit_dashboard.html', context)


def employee_simulator(request):
    """
    Renders the Employee AI Simulator interface.
    Fetches models to populate the model selection dropdown.
    """
    # Seed baseline approved models if registry is currently empty
    if not AIModelInventory.objects.exists():
        AIModelInventory.objects.bulk_create([
            AIModelInventory(
                model_name='gpt-4o',
                vendor='OpenAI',
                approved_data_tier=2,
                status='ACTIVE'
            ),
            AIModelInventory(
                model_name='claude-3-5-sonnet',
                vendor='Anthropic',
                approved_data_tier=3,
                status='ACTIVE'
            ),
            AIModelInventory(
                model_name='gemini-1.5-flash',
                vendor='Google',
                approved_data_tier=1,
                status='ACTIVE'
            ),
            AIModelInventory(
                model_name='llama-3.1-70b',
                vendor='Meta',
                approved_data_tier=2,
                status='ACTIVE'
            ),
        ])

    models = AIModelInventory.objects.filter(status__in=['ACTIVE', 'Active']).order_by('model_name')
    return render(request, 'simulator.html', {'models': models})


def employee_portal(request):
    """
    Renders the employee AI portal simulation interface.
    """
    models = AIModelInventory.objects.filter(status__in=['ACTIVE', 'Active']).order_by('id')
    return render(request, 'employee_portal.html', {'models': models})


@csrf_exempt
def send_prompt_api(request):
    """
    Downstream mock endpoint for /api/send-prompt/.
    Requests passing through ShadowAIInterceptor middleware arrive here.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required.'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8')) if request.body else {}
    except Exception:
        body = {}

    return JsonResponse({
        'status': 'success',
        'message': 'Prompt approved and successfully processed by target model.',
        'model_id': body.get('model_id'),
        'data_tier': body.get('data_tier'),
        'user_id': body.get('user_id'),
    })


def privacy_policy(request):
    """
    Renders the privacy policy page.
    """
    return render(request, 'privacy_policy.html')


def terms_and_conditions(request):
    """
    Renders the terms and conditions page.
    """
    return render(request, 'terms.html')
