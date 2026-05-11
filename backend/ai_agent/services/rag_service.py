"""
RAG (Retrieval-Augmented Generation) Service
Uses TF-IDF vectorization to find relevant telecom knowledge from the database.
"""
import logging
import re
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Try to import sklearn for TF-IDF; fall back to simple keyword matching
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not installed. RAG will use basic keyword matching.")


class RAGService:
    """
    Retrieval-Augmented Generation service.
    Searches all telecom data models for content relevant to the user query,
    then returns formatted context that can be injected into the AI response.
    """

    def __init__(self):
        self.supported_languages = ['en', 'fa', 'ps']
        logger.info(f"RAGService initialized (sklearn={'available' if SKLEARN_AVAILABLE else 'not available'})")

    def retrieve_context(self, query: str, language: str = 'en', top_k: int = 3) -> str:
        """
        Retrieve relevant context from all telecom data models based on the query.
        Uses intent detection to prioritize the most relevant data sources.
        Returns a formatted string of relevant information.
        """
        from ..models import TelecomKnowledgeBase, InternetPackage, CoverageArea, TechnicalSupportFAQ

        intent = self.detect_intent(query)
        context_parts = []

        # Map intents to relevant data sources
        intent_sources = {
            'greeting': ['kb'],
            'balance': ['kb', 'faq'],
            'package': ['package', 'kb'],
            'coverage': ['coverage', 'kb'],
            'sim': ['kb', 'faq'],
            'technical': ['faq', 'kb'],
            'default': ['kb', 'faq', 'package', 'coverage'],
        }

        sources = intent_sources.get(intent, ['kb', 'faq', 'package', 'coverage'])

        for source in sources:
            if source == 'kb':
                entries = self._search_knowledge_base(query, language)
                for entry in entries[:top_k]:
                    answer = self._get_localized(entry, 'answer', language)
                    if answer:
                        context_parts.append(answer)

            elif source == 'package':
                packages = self._search_packages(query, language)
                for pkg in packages[:top_k]:
                    name = self._get_localized(pkg, 'name', language)
                    desc = self._get_localized(pkg, 'description', language)
                    line = f"Package: {name} - {pkg.price_afn} AFN for {pkg.data_amount}, valid {pkg.validity_days} days."
                    if pkg.activation_code:
                        line += f" To activate, dial {pkg.activation_code}."
                    if desc:
                        line += f" {desc}"
                    context_parts.append(line)

            elif source == 'coverage':
                coverage = self._search_coverage(query, language)
                for area in coverage[:top_k]:
                    notes = self._get_localized(area, 'notes', language)
                    line = f"Coverage in {area.city}, {area.province}: {area.get_coverage_type_display()} network - Status: {area.get_status_display()}."
                    if notes:
                        line += f" {notes}"
                    context_parts.append(line)

            elif source == 'faq':
                faqs = self._search_faqs(query, language)
                for faq in faqs[:top_k]:
                    answer = self._get_localized(faq, 'answer', language)
                    if answer:
                        context_parts.append(f"FAQ ({faq.get_category_display()}): {answer}")

        if not context_parts:
            return ""

        return "\n".join(context_parts)

    def _get_localized(self, obj, field_base: str, language: str) -> str:
        """Get the localized version of a field."""
        lang_suffixes = {'en': 'en', 'fa': 'dari', 'ps': 'pashto'}
        suffix = lang_suffixes.get(language, 'en')
        field_name = f"{field_base}_{suffix}"
        value = getattr(obj, field_name, '')
        if not value:
            # Fall back to English
            value = getattr(obj, f"{field_base}_en", '')
        return str(value) if value else ''

    def _search_knowledge_base(self, query: str, language: str) -> list:
        """Search TelecomKnowledgeBase entries."""
        from ..models import TelecomKnowledgeBase
        all_entries = list(TelecomKnowledgeBase.objects.all())
        if not all_entries:
            return []

        texts = []
        for entry in all_entries:
            q = self._get_localized(entry, 'question', language)
            a = self._get_localized(entry, 'answer', language)
            texts.append(f"{q} {a}")

        indices = self._rank_by_relevance(query, texts)
        return [all_entries[i] for i in indices if i < len(all_entries)]

    def _search_packages(self, query: str, language: str) -> list:
        """Search InternetPackage entries."""
        from ..models import InternetPackage
        all_packages = list(InternetPackage.objects.filter(is_active=True))
        if not all_packages:
            return []

        texts = []
        for pkg in all_packages:
            name = self._get_localized(pkg, 'name', language)
            desc = self._get_localized(pkg, 'description', language)
            # Include category keywords to improve matching
            texts.append(f"internet package data plan {name} {pkg.data_amount} {pkg.price_afn} AFN {pkg.validity_days} days {desc}")

        indices = self._rank_by_relevance(query, texts)
        return [all_packages[i] for i in indices if i < len(all_packages)]

    def _search_coverage(self, query: str, language: str) -> list:
        """Search CoverageArea entries."""
        from ..models import CoverageArea
        all_areas = list(CoverageArea.objects.filter(status='active'))
        if not all_areas:
            return []

        texts = []
        for area in all_areas:
            notes = self._get_localized(area, 'notes', language)
            texts.append(f"{area.city} {area.province} {area.get_coverage_type_display()} {notes}")

        indices = self._rank_by_relevance(query, texts)
        return [all_areas[i] for i in indices if i < len(all_areas)]

    def _search_faqs(self, query: str, language: str) -> list:
        """Search TechnicalSupportFAQ entries."""
        from ..models import TechnicalSupportFAQ
        all_faqs = list(TechnicalSupportFAQ.objects.filter(is_published=True))
        if not all_faqs:
            return []

        texts = []
        for faq in all_faqs:
            q = self._get_localized(faq, 'question', language)
            a = self._get_localized(faq, 'answer', language)
            texts.append(f"{q} {a} {faq.get_category_display()}")

        indices = self._rank_by_relevance(query, texts)
        return [all_faqs[i] for i in indices if i < len(all_faqs)]

    def _rank_by_relevance(self, query: str, texts: List[str]) -> List[int]:
        """
        Rank text indices by relevance to the query.
        Uses TF-IDF if sklearn is available, otherwise simple keyword overlap.
        """
        if not texts:
            return []

        if SKLEARN_AVAILABLE:
            return self._tfidf_rank(query, texts)
        else:
            return self._keyword_rank(query, texts)

    def _tfidf_rank(self, query: str, texts: List[str]) -> List[int]:
        """Rank using TF-IDF cosine similarity."""
        try:
            vectorizer = TfidfVectorizer(stop_words='english', min_df=1)
            all_texts = texts + [query]
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            query_vec = tfidf_matrix[-1]
            doc_vecs = tfidf_matrix[:-1]
            similarities = cosine_similarity(query_vec, doc_vecs).flatten()
            # Sort by similarity descending
            ranked = sorted(enumerate(similarities), key=lambda x: x[1], reverse=True)
            # Return all results sorted by relevance (allow low-similarity matches)
            return [idx for idx, score in ranked]
        except Exception as e:
            logger.error(f"TF-IDF ranking error: {e}")
            return self._keyword_rank(query, texts)

    def _keyword_rank(self, query: str, texts: List[str]) -> List[int]:
        """Rank by simple keyword overlap count."""
        query_words = set(re.findall(r'\w+', query.lower()))
        if not query_words:
            return list(range(len(texts)))

        scored = []
        for i, text in enumerate(texts):
            text_words = set(re.findall(r'\w+', text.lower()))
            overlap = len(query_words & text_words)
            scored.append((i, overlap))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [idx for idx, score in scored if score > 0]

    def detect_intent(self, query: str) -> str:
        """
        Detect the intent category of a user query.
        Returns one of: greeting, balance, package, coverage, sim, technical, default
        """
        query_lower = query.lower()

        if any(word in query_lower for word in ['hello', 'hi', 'سلام', 'څنګه', 'greet', 'hey', 'good morning', 'good evening']):
            return 'greeting'
        elif any(word in query_lower for word in ['balance', 'بیلانس', 'بیلانس', 'credit', 'money', 'account', 'wallet', 'charge']):
            return 'balance'
        elif any(word in query_lower for word in ['technical', 'support', 'problem', 'issue', 'connection', 'فنی', 'پشتیبانی', 'تخنیکي', 'ملاتړ', 'ستونزې', 'help', 'trouble', 'error', 'not working', 'broken', 'fix', 'repair', 'reset']):
            return 'technical'
        elif any(word in query_lower for word in ['package', 'internet', 'data', 'بسته', 'انټرنیټ', 'پیکیج', 'باندل', 'plan', 'subscription', 'bundle']):
            return 'package'
        elif any(word in query_lower for word in ['coverage', 'signal', 'network', 'پوشش', 'پوښښ', 'سګنال', 'area', 'zone', 'reception']):
            return 'coverage'
        elif any(word in query_lower for word in ['sim', 'registration', 'سیم', 'ثبت', 'register', 'sim card', 'tazkira']):
            return 'sim'
        else:
            return 'default'
