import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from newspaper import Article
from textblob import TextBlob
from archive import get_cached_analysis, store_analysis

# ==================== SETUP ====================

load_dotenv()

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN")
)

# ==================== HELPERS ====================

def extract_article_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception:
        return None

# ==================== CORE ANALYSIS ====================

def analyze_content(text):
    # ---------- 0. CHECK ARCHIVE FIRST ----------
    cached_result, is_cached = get_cached_analysis(text, client)
    if is_cached:
        # Return cached result with archive flag
        checklist = cached_result.get("checklist", {})
        return (
            cached_result["score"],
            cached_result["flags"],
            cached_result["ai_report"],
            cached_result["is_subjective"],
            True,  # is_from_archive flag
            checklist
        )
    
    score = 100
    flags = []
    category = "Objective Analysis"
    context_text = text
    checklist = {}  # Track status of each check

    # ---------- 1. SUBJECTIVITY CHECK ----------
    blob = TextBlob(text)
    subj_score = blob.sentiment.subjectivity
    is_subjective = subj_score > 0.5

    # Check for panic patterns and shouting BEFORE setting objective_language
    has_panic_pattern = bool(re.search(r'!!+|\?\?+', text))
    has_shouting = len(re.findall(r'\b[A-Z]{4,}\b', text)) >= 3
    
    # Check if text is mostly/all uppercase (another shouting indicator)
    text_words = text.split()
    if text_words:
        uppercase_ratio = sum(1 for word in text_words if word.isupper() and len(word) > 1) / len(text_words)
        has_excessive_caps = uppercase_ratio > 0.5  # More than 50% of words are all caps
    else:
        has_excessive_caps = False
    
    # Objective language fails if: subjective OR has panic patterns OR has shouting OR excessive caps
    is_objective = not (is_subjective or has_panic_pattern or has_shouting or has_excessive_caps)
    checklist["objective_language"] = is_objective
    
    if is_subjective:
        category = "Subjective Opinion"
        flags.append(
            f"🧠 Subjective language detected (Score: {subj_score:.2f})."
        )

    # ---------- 2. URL EXTRACTION ----------
    url_match = re.search(r'(https?://\S+)', text)
    url_extracted = False
    if url_match:
        url = url_match.group(1)
        article_text = extract_article_content(url)
        if article_text:
            context_text = f"URL: {url}\nArticle Content: {article_text[:1500]}"
            flags.append("ℹ️ Extracted article content from URL.")
            url_extracted = True
        else:
            flags.append("⚠️ Could not extract article content from URL.")
    checklist["url_extraction"] = url_extracted if url_match else None  # None if no URL present

    # ---------- 3. PANIC / STYLE RULES ----------
    checklist["no_panic_pattern"] = not has_panic_pattern
    if has_panic_pattern:
        score -= 25
        flags.append("⚠️ Panic Pattern: Excessive punctuation detected.")

    checklist["no_shouting"] = not (has_shouting or has_excessive_caps)
    if has_shouting or has_excessive_caps:
        score -= 20
        flags.append("⚠️ Shouting Pattern: Excessive uppercase usage detected.")

    # ---------- 4. AI FACT VERIFICATION (GPT-5 via Responses API) ----------
    ai_report = "AI verification unavailable."
    verdict = "UNCERTAIN"
    ai_verification_status = None  # None = unavailable, True = TRUE, False = FALSE, "uncertain" = UNCERTAIN

    try:
        # Try standard OpenAI Chat Completions API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using a standard model name
            messages=[
                {
                    "role": "system",
                    "content": "You are a crisis fact-checker. Classify the claim strictly as one of TRUE, FALSE, or UNCERTAIN. Reply ONLY in this format:\nVERDICT: <TRUE/FALSE/UNCERTAIN>\nEXPLANATION: <one short sentence>"
                },
                {
                    "role": "user",
                    "content": f"CLAIM:\n{context_text}"
                }
            ],
            max_tokens=150
        )

        ai_text = response.choices[0].message.content.strip()
        ai_report = ai_text

        verdict_match = re.search(
            r'VERDICT:\s*(TRUE|FALSE|UNCERTAIN)', ai_text, re.IGNORECASE
        )
        if verdict_match:
            verdict = verdict_match.group(1).upper()
            if verdict == "TRUE":
                ai_verification_status = True
            elif verdict == "FALSE":
                ai_verification_status = False
            else:
                ai_verification_status = "uncertain"

        if verdict == "FALSE":
            score -= 70
            flags.append("❌ AI Verdict: Claim is factually false.")
        elif verdict == "UNCERTAIN":
            score -= 25
            flags.append("⚠️ AI Verdict: Claim cannot be verified confidently.")

    except Exception as e:
        # Log the actual error for debugging
        error_msg = str(e)
        flags.append(f"⚠️ AI verification unavailable: {error_msg[:100]}")
        ai_report = f"AI verification failed: {error_msg}"
        score -= 30
    
    checklist["ai_verification"] = ai_verification_status

    # ---------- 5. DETERMINISTIC SANITY CHECKS ----------
    has_false_claim = "india is not a country" in text.lower()
    
    # Check for other obviously false/exaggerated claims
    false_claim_patterns = [
        r'\b(will kill everyone|kill everyone|everyone will die|everyone dies)\b',
        r'\b(end the world|world will end|end of the world|world ends)\b',
        r'\b(everyone is going to die|everyone dies|all will die)\b',
        r'\b(100% fatal|100% death rate|everyone dies)\b'
    ]
    
    has_exaggerated_claim = any(re.search(pattern, text.lower()) for pattern in false_claim_patterns)
    
    # Sanity check fails if: specific false claim OR exaggerated claim OR AI says FALSE
    sanity_check_passed = not (has_false_claim or has_exaggerated_claim or ai_verification_status is False)
    checklist["sanity_check"] = sanity_check_passed
    
    if has_false_claim:
        score = min(score, 20)
        flags.append("❌ Deterministic Check: India is a sovereign country.")
    elif has_exaggerated_claim:
        score = min(score, 30)
        flags.append("❌ Sanity Check: Detected obviously false or exaggerated claim.")
    elif ai_verification_status is False:
        # AI already flagged this, but we note it in sanity check too
        flags.append("❌ Sanity Check: AI verification indicates false claim.")

    # ---------- FINAL SCORE ----------
    score = min(max(score, 0), 100)

    # ---------- 6. STORE IN ARCHIVE ----------
    analysis_result = {
        "score": score,
        "flags": flags,
        "ai_report": ai_report,
        "is_subjective": is_subjective,
        "checklist": checklist
    }
    store_analysis(text, analysis_result, client)

    return score, flags, ai_report, is_subjective, False, checklist  # is_from_archive = False

# ==================== CLI TEST ====================

if __name__ == "__main__":
    user_input = input("Enter claim / news / URL:\n> ")

    score, flags, ai_report, is_subjective, is_from_archive, checklist = analyze_content(user_input)

    print("\n========== RESULT ==========")
    if is_from_archive:
        print("📦 Pulled from Archive")
    print("Credibility Score:", score, "%")
    print("Is Subjective:", is_subjective)

    print("\nChecklist:")
    for check, status in checklist.items():
        if status is True:
            print(f"✓ {check}")
        elif status is False:
            print(f"✗ {check}")
        elif status == "uncertain":
            print(f"? {check}")
        else:
            print(f"- {check} (N/A)")

    print("\nFlags:")
    for f in flags:
        print("-", f)

    print("\nAI Deep Dive:")
    print(ai_report)
