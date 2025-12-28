import json
import hashlib
import os
import re
from datetime import datetime

ARCHIVE_FILE = "analysis_archive.json"

# Cache for normalized claims to avoid repeated AI calls
_normalization_cache = {}

def normalize_claim_semantically(text, client=None):
    """
    Normalize a claim to a canonical form using AI.
    This helps match semantically similar claims like:
    "Is covid Contagious" and "Is the Virus Covid-19 Contagious"
    """
    # Check cache first
    cache_key = text.lower().strip()
    if cache_key in _normalization_cache:
        return _normalization_cache[cache_key]
    
    # If no client provided, do basic normalization
    if client is None:
        normalized = basic_normalize(text)
        _normalization_cache[cache_key] = normalized
        return normalized
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a text normalizer. Convert the given claim/question to a canonical, standardized form. Remove filler words, normalize terminology (e.g., 'covid', 'covid-19', 'coronavirus' → 'COVID-19'), and standardize phrasing. Return ONLY the normalized text, nothing else."
                },
                {
                    "role": "user",
                    "content": f"Normalize this claim to canonical form:\n{text[:500]}"
                }
            ],
            max_tokens=100,
            temperature=0.1  # Low temperature for consistency
        )
        
        normalized = response.choices[0].message.content.strip()
        # Fallback to basic normalization if AI returns something weird
        if len(normalized) < 3 or len(normalized) > 500:
            normalized = basic_normalize(text)
        
        _normalization_cache[cache_key] = normalized
        return normalized
    except Exception:
        # Fallback to basic normalization
        normalized = basic_normalize(text)
        _normalization_cache[cache_key] = normalized
        return normalized

def basic_normalize(text):
    """
    Basic normalization without AI - handles common variations.
    """
    # Normalize common COVID-19 variations
    text = re.sub(r'\b(covid|covid-19|coronavirus|sars-cov-2)\b', 'covid-19', text.lower(), flags=re.IGNORECASE)
    
    # Remove articles and common filler words
    text = re.sub(r'\b(the|a|an|is|are|was|were)\b', '', text.lower())
    
    # Normalize whitespace
    text = ' '.join(text.strip().split())
    
    # Remove punctuation for matching
    text = re.sub(r'[^\w\s]', '', text)
    
    return text.strip()

def get_claim_hash(text, client=None):
    """
    Create a hash of the semantically normalized claim text.
    Uses AI to normalize similar claims to the same canonical form.
    """
    normalized = normalize_claim_semantically(text, client)
    return hashlib.sha256(normalized.encode()).hexdigest()

def load_archive():
    """Load the archive from JSON file."""
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_archive(archive_data):
    """Save the archive to JSON file."""
    try:
        with open(ARCHIVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving archive: {e}")

def get_cached_analysis(text, client=None):
    """
    Check if analysis exists in archive.
    Returns (analysis_data, is_cached) tuple.
    If cached, returns the data and True. Otherwise returns (None, False).
    Uses semantic normalization to match similar claims.
    """
    claim_hash = get_claim_hash(text, client)
    archive = load_archive()
    
    if claim_hash in archive:
        return archive[claim_hash], True
    return None, False

def store_analysis(text, analysis_result, client=None):
    """
    Store analysis result in archive.
    analysis_result should be a dict with: score, flags, ai_report, is_subjective
    Uses semantic normalization to store claims in canonical form.
    """
    claim_hash = get_claim_hash(text, client)
    archive = load_archive()
    
    # Get normalized form for storage
    normalized_claim = normalize_claim_semantically(text, client)
    
    archive[claim_hash] = {
        **analysis_result,
        "timestamp": datetime.now().isoformat(),
        "claim_preview": text[:200],  # Store original text preview
        "normalized_claim": normalized_claim  # Store normalized form for reference
    }
    
    save_archive(archive)

