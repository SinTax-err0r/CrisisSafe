import os
import re
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
from newspaper import Article
from textblob import TextBlob
from duckduckgo_search import DDGS
from archive import get_cached_analysis, store_analysis

# ==================== SETUP ====================

load_dotenv()

def get_api_key():
    """Retrieve API key from env vars or streamlit secrets."""
    # 1. Try environment variable
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
        
    # 2. Try Streamlit secrets
    try:
        if "GITHUB_TOKEN" in st.secrets:
            return st.secrets["GITHUB_TOKEN"]
    except Exception:
        pass
        
    return None

api_key = get_api_key()

# Prevent startup crash if key is missing
# (OpenAI client raises error immediately if api_key is None)
if not api_key:
    api_key = "MISSING_KEY"

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=api_key
)

MODEL_NAME = "gpt-4o-mini"

# ==================== HELPERS ====================

def extract_article_content(url):
    """Extract text content from a URL using newspaper3k."""
    try:
        article = Article(url, language='en')
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Article extraction error: {e}")
        return None


def find_related_articles(query, verdict="UNCERTAIN"):
    """Search for related articles and highlight relevant text."""
    results = []
    try:
        search_query = query[:200] + " english"
        with DDGS() as ddgs:
            # Request US-English results
            search_results = ddgs.text(search_query, region="us-en", max_results=10, backend="lite")
            
            if search_results:
                count = 0
                for r in search_results:
                    if count >= 3:
                        break
                        
                    # strict filtering: check for common CJK unicode ranges
                    content_to_check = r.get("title", "") + r.get("body", "")
                    if re.search(r'[\u4e00-\u9fff]', content_to_check):
                        continue
                        
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "body": r.get("body", ""),
                        "highlighted_body": highlight_with_ai(query, r.get("body", ""), verdict)
                    })
                    count += 1
    except Exception as e:
        print(f"Search error: {e}")
    
    return results


def highlight_with_ai(claim, snippet, verdict="UNCERTAIN"):
    """
    Uses AI to semantically highlight the most relevant sentence using the shared OpenAI client.
    """
    if not snippet or len(snippet) < 10:
        return snippet
    
    # Adjust prompt based on verdict
    if verdict == "TRUE":
        goal = "identify the sentence that CONFIRMS the claim is TRUE"
    elif verdict == "FALSE":
        goal = "identify the sentence that PROVES the claim is FALSE"
    else:
        goal = "identify the SINGLE most relevant sentence"
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a text highlighter. Your goal is to {goal} in the provided text. Return the full text, but wrap that ONE sentence in <mark> tags. Do not change any other text. If no sentence is relevant/aligned with the verdict, return the text unchanged."
                },
                {
                    "role": "user",
                    "content": f"CLAIM: {claim}\nTEXT: {snippet}"
                }
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        highlighted_text = response.choices[0].message.content.strip()
        
        # Safety check: validate output length
        if abs(len(highlighted_text) - len(snippet)) > 100:
             return snippet
             
        # Convert <mark> to styled span
        style = "background-color: #fff2cc; border-bottom: 2px solid #e6b800; font-weight: bold; color: #2d241a;"
        highlighted_text = highlighted_text.replace(
            "<mark>", 
            f"<span style='{style}'>"
        ).replace("</mark>", "</span>")
        
        return highlighted_text

    except Exception as e:
        print(f"Highlighting error: {e}")
        return snippet


# ==================== CORE ANALYSIS ====================

def analyze_content(text):
    """
    Analyzes text for credibility using multiple checks.
    """
    
    # ---------- 0. CHECK ARCHIVE FIRST ----------
    cached_result, is_cached = get_cached_analysis(text, client)
    if is_cached:
        checklist = cached_result.get("checklist", {})
        related = cached_result.get("related_articles", [])
        
        if not related:
            try:
                verdict = "UNCERTAIN"
                if cached_result["score"] > 80:
                    verdict = "TRUE"
                elif cached_result["score"] < 40:
                    verdict = "FALSE"
                
                related = find_related_articles(text, verdict)
            except Exception:
                related = []
        
        pointers = cached_result.get("pointers", [])
        return (
            cached_result["score"],
            cached_result["flags"],
            cached_result["ai_report"],
            cached_result["is_subjective"],
            True,
            checklist,
            related,
            pointers
        )
    
    # Initialize
    score = 100
    flags = []
    context_text = text
    checklist = {}
    pointers = []
    
    # ---------- 1. SUBJECTIVITY CHECK ----------
    blob = TextBlob(text)
    subj_score = blob.sentiment.subjectivity
    is_subjective = subj_score > 0.5
    
    has_panic_pattern = bool(re.search(r'!!+|\?\?+', text))
    has_shouting = len(re.findall(r'\b[A-Z]{4,}\b', text)) >= 3
    
    text_words = text.split()
    if text_words:
        uppercase_ratio = sum(1 for word in text_words if word.isupper() and len(word) > 1) / len(text_words)
        has_excessive_caps = uppercase_ratio > 0.5
    else:
        has_excessive_caps = False
    
    is_objective = not (is_subjective or has_panic_pattern or has_shouting or has_excessive_caps)
    checklist["objective_language"] = is_objective
    
    if is_subjective:
        flags.append(f"🧠 Subjective language detected (Score: {subj_score:.2f}).")
    
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
    
    checklist["url_extraction"] = url_extracted if url_match else None
    
    # ---------- 3. PANIC / STYLE RULES ----------
    checklist["no_panic_pattern"] = not has_panic_pattern
    if has_panic_pattern:
        score -= 25
        flags.append("⚠️ Panic Pattern: Excessive punctuation detected.")
    
    checklist["no_shouting"] = not (has_shouting or has_excessive_caps)
    if has_shouting or has_excessive_caps:
        score -= 20
        flags.append("⚠️ Shouting Pattern: Excessive uppercase usage detected.")
    
    # ---------- 4. AI FACT VERIFICATION ----------
    ai_report = "AI verification unavailable."
    verdict = "UNCERTAIN"
    ai_verification_status = None
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict logical fact-checker. You must determine if the CLAIM is Factually Accurate.\n- If the claim contradicts established facts (e.g., 'Sun is not a star'), return FALSE.\n- Pay close attention to negations ('not', 'no', 'never').\n- Classify strictly as TRUE, FALSE, or UNCERTAIN.\n\nReply ONLY in this format:\nVERDICT: <TRUE/FALSE/UNCERTAIN>\nEXPLANATION: <one short sentence>\nPOINTERS: <If the claim is debatable, subjective, or nuanced (Verdict UNCERTAIN), provide 3 short, neutral bullet points for critical thinking to help the user form their own opinion. If the claim is a simple objective FACT (TRUE/FALSE), leave this section empty.>"
                },
                {
                    "role": "user",
                    "content": f"CLAIM:\n{context_text}"
                }
            ],
            max_tokens=250,
            temperature=0.1
        )
        
        ai_text = response.choices[0].message.content.strip()
        
        # Extract pointers
        if "POINTERS:" in ai_text:
            parts = ai_text.split("POINTERS:")
            ai_report = parts[0].strip()
            pointers_text = parts[1].strip()
            for line in pointers_text.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    pointers.append(line[1:].strip())
        else:
            ai_report = ai_text
        
        # Extract verdict
        verdict_match = re.search(r'VERDICT:\s*(TRUE|FALSE|UNCERTAIN)', ai_text, re.IGNORECASE)
        if verdict_match:
            verdict = verdict_match.group(1).upper()
            if verdict == "TRUE":
                ai_verification_status = True
                pointers = []
            elif verdict == "FALSE":
                ai_verification_status = False
                pointers = []
            else:
                ai_verification_status = "uncertain"
        
        # Apply penalties
        if verdict == "FALSE":
            score -= 70
            flags.append("❌ AI Verdict: Claim is factually false.")
        elif verdict == "UNCERTAIN":
            score -= 25
            flags.append("⚠️ AI Verdict: Claim cannot be verified confidently.")
    
    except Exception as e:
        error_msg = str(e)
        flags.append(f"⚠️ AI verification unavailable: {error_msg[:100]}")
        ai_report = f"AI verification failed: {error_msg}"
        score -= 30
    
    checklist["ai_verification"] = ai_verification_status
    
    # ---------- 5. SANITY CHECKS ----------
    has_false_claim = "india is not a country" in text.lower()
    
    false_claim_patterns = [
        r'\b(will kill everyone|kill everyone|everyone will die|everyone dies)\b',
        r'\b(end the world|world will end|end of the world|world ends)\b',
        r'\b(everyone is going to die|everyone dies|all will die)\b',
        r'\b(100% fatal|100% death rate)\b'
    ]
    
    has_exaggerated_claim = any(re.search(pattern, text.lower()) for pattern in false_claim_patterns)
    
    sanity_check_passed = not (has_false_claim or has_exaggerated_claim or ai_verification_status is False)
    checklist["sanity_check"] = sanity_check_passed
    
    if has_false_claim:
        score = min(score, 20)
        flags.append("❌ Deterministic Check: India is a sovereign country.")
    elif has_exaggerated_claim:
        score = min(score, 30)
        flags.append("❌ Sanity Check: Detected obviously false or exaggerated claim.")
    
    # ---------- FINAL SCORE ----------
    score = min(max(score, 0), 100)
    
    # ---------- 6. FIND RELATED ARTICLES ----------
    related_articles = find_related_articles(text, verdict)
    
    # ---------- 7. STORE IN ARCHIVE ----------
    analysis_result = {
        "score": score,
        "flags": flags,
        "ai_report": ai_report,
        "is_subjective": is_subjective,
        "checklist": checklist,
        "related_articles": related_articles,
        "pointers": pointers
    }
    store_analysis(text, analysis_result, client)
    
    return (
        score,
        flags,
        ai_report,
        is_subjective,
        False,
        checklist,
        related_articles,
        pointers
    )


# ==================== CLI TEST ====================

if __name__ == "__main__":
    user_input = input("Enter claim / news / URL:\n> ")
    
    score, flags, ai_report, is_subjective, is_from_archive, checklist, related, pointers = analyze_content(user_input)
    
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
    
    if pointers:
        print("\nCritical Thinking Pointers:")
        for p in pointers:
            print(f"- {p}")
    
    if related:
        print("\nRelated Articles:")
        for i, article in enumerate(related, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   URL: {article['url']}")
            print(f"   Snippet: {article.get('highlighted_body', article.get('body', ''))[:200]}...")