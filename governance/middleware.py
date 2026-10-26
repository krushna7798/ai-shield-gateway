# pyrefly: ignore[missing-import]
import json
import io
# pyrefly: ignore[missing-import]
from django.http import JsonResponse
from governance.models import AIModelInventory, ProvenanceLog
from governance.dlp_engine import analyze_prompt_tier

# Document parsing libraries
from pypdf import PdfReader
import docx


class ShadowAIInterceptor:
    """
    Automated Governance & DLP Interceptor Middleware.
    Extracts text from prompt payloads and uploaded documents (.txt, .csv, .pdf, .docx).
    Runs combined content through the Gemini DLP engine to auto-detect data sensitivity tiers.
    Enforces compliance against target model clearance tiers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/send-prompt/'):
            return self.process_ai_request(request)
        return self.get_response(request)

    def extract_file_text(self, uploaded_file):
        """Extracts plain text from standard text, PDF, and DOCX files."""
        filename = uploaded_file.name.lower()

        try:
            if filename.endswith('.pdf'):
                # Read PDF binary stream
                reader = PdfReader(uploaded_file)
                extracted_text = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text.append(text)
                return "\n".join(extracted_text)

            elif filename.endswith('.docx'):
                # Read DOCX binary stream
                doc = docx.Document(uploaded_file)
                return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

            else:
                # Default text decoding for .txt, .csv
                return uploaded_file.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"File Extraction Error: {e}")
            return f"[UNREADABLE FILE CONTENT: {filename}]"

    def process_ai_request(self, request):
        try:
            # Handle both multipart FormData and JSON bodies
            content_type = request.content_type or ''
            if 'multipart/form-data' in content_type:
                target_model_id = request.POST.get('model_id')
                prompt_text = request.POST.get('prompt_text', '')
                user = request.POST.get('user_id') or (
                    request.user.username if getattr(request, 'user', None) and request.user.is_authenticated else 'anonymous'
                )
            else:
                body = json.loads(request.body.decode('utf-8')) if request.body else {}
                target_model_id = body.get('model_id')
                prompt_text = body.get('prompt_text') or body.get('prompt', '')
                user = body.get('user_id') or (
                    request.user.username if getattr(request, 'user', None) and request.user.is_authenticated else 'anonymous'
                )

            # Intercept and extract text from uploaded files
            if 'file_upload' in request.FILES:
                uploaded_file = request.FILES['file_upload']
                file_content = self.extract_file_text(uploaded_file)
                prompt_text = f"{prompt_text}\n\n[FILE CONTENT]: {file_content}"

            # Pass the fully extracted text payload to the Gemini API classifier
            detected_tier = analyze_prompt_tier(prompt_text)

            # Lookup target model by numeric ID or model_name string
            if isinstance(target_model_id, int) or (isinstance(target_model_id, str) and str(target_model_id).isdigit()):
                target_model = AIModelInventory.objects.get(id=int(target_model_id))
            else:
                target_model = AIModelInventory.objects.get(model_name=str(target_model_id))

            if detected_tier > target_model.approved_data_tier:
                action = 'Blocked'
                response = JsonResponse({
                    'error': f'Compliance Violation: Auto-detected Tier {detected_tier} data cannot be sent to a Tier {target_model.approved_data_tier} model.',
                    'action_taken': 'Blocked',
                    'detected_tier': detected_tier,
                    'approved_tier': target_model.approved_data_tier,
                    'model_name': target_model.model_name
                }, status=403)
            else:
                action = 'Approved'
                response = JsonResponse({
                    'success': 'Prompt and document approved and forwarded.',
                    'action_taken': 'Approved',
                    'detected_tier': detected_tier,
                    'approved_tier': target_model.approved_data_tier,
                    'model_name': target_model.model_name
                }, status=200)

            ProvenanceLog.objects.create(
                user_id=user,
                target_model=target_model,
                data_tier_submitted=detected_tier,
                action_taken=action
            )

            return response

        except AIModelInventory.DoesNotExist:
            return JsonResponse({'error': f'Unregistered AI model ({target_model_id}).'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
