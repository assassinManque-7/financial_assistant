from dotenv import load_dotenv
import os

from google import genai

load_dotenv()

api = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key = api)

def ask_gemma(text):

    extraction_schema_individual = """
      {
        "legal_name": "string or null",
        "date_of_birth": "YYYY-MM-DD or null",
        "place_of_birth": "string or null",
        "nationality": "string or null",
        "gender": "string or null",
        "address": "string or null",
        "tax_id": "string or null",
        "id_numbers": {
          "passport_number": "string or null",
          "aadhaar_last4": "string or null",
          "pan_number": "string or null",
          "voter_id_number": "string or null"
        },
        "watchlist_checks": {
          "pep_status": "boolean or null",
          "unsc_consolidated_list_status": "boolean or null",
          "uapa_mha_status": "boolean or null"
        },
        "document_id": "string or null",
        "document_expiry_date": "YYYY-MM-DD or null",
        "document_issuing_authority": "string or null",
        "screening_timestamp": "ISO 8601 datetime or null"
      }
    """

    extraction_schema_business = """
      {
        "entity_type": "one of: sole_proprietorship, partnership, llp, private_limited, public_limited, trust, huf, other, or null",
        "legal_name": "string or null",
        "trade_name": "string or null",
        "alias_names": ["string"],
        "beneficial_owners": [
          {"name": "string", "ownership_pct": "number or null", "nationality": "string or null", "is_pep" : "boolean or null", "pep_position" : "string", "sanctions_match" : "boolean or null"}
        ],
        "principal_business_activity": "string or null",
        "nic_code": "string or null",
        "registered_address": "string or null",
        "operating_address": "string or null",
        "jurisdiction": "string or null",
        "incorporation_number": "string or null",
        "corporate_id_number": "string or null",
        "gst_id": "string or null",
        "registration_number": "string or null",
        "date_of_incorporation": "YYYY-MM-DD or null",
        "expected_monthly_volume": "number or null",
        "expected_monthly_transaction_frequency": "number or null",
        "source_of_funds": "string or null",
        "source_of_income": "string or null",
        "operating_countries": ["string"],
        "watchlist_checks": {
          "pep_status": "boolean or null",
          "unsc_consolidated_list_status": "boolean or null",
          "uapa_mha_status": "boolean or null"
        },
        "document_number": "string or null",
        "document_expiry_date": "YYYY-MM-DD or null",
        "document_issuing_authority": "string or null",
        "screening_timestamp": "ISO 8601 datetime or null"
      }
    """

    prompt = f"""You are a financial compliance expert. Analyze the onboarding document below.

    Return ONLY a single raw JSON object. No markdown. No backticks. No explanation. No analysis report. No text before or after the JSON.

    Choose the individual schema if the document involves an individual, business schema if it involves a business. Include a confidence score.

    Onboarding document: {text}
    Schema (individual): {extraction_schema_individual}
    Schema (business): {extraction_schema_business}"""

    resp = client.models.generate_content(
        model = "gemma-4-26b-a4b-it",
        contents = prompt
    )

    return resp.text



