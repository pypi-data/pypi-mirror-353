"""
KnowledgeBase - Durable Object for searchable documentation and FAQs

Maintains a searchable repository of knowledge articles, FAQs, and solutions.
Demonstrates content management patterns with search, versioning, and analytics.
"""

import asyncio
import time
import re
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

from agnt5.durable import durable, DurableObject


class ArticleType(Enum):
    """Types of knowledge articles."""
    FAQ = "faq"
    HOWTO = "howto"
    TROUBLESHOOTING = "troubleshooting"
    POLICY = "policy"
    PRODUCT_INFO = "product_info"
    API_DOCS = "api_docs"


class ArticleStatus(Enum):
    """Article publication status."""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class KnowledgeArticle:
    """Knowledge base article structure."""
    article_id: str
    title: str
    content: str
    article_type: ArticleType
    status: ArticleStatus
    tags: Set[str]
    category: str
    author: str
    created_at: float
    updated_at: float
    version: int = 1
    view_count: int = 0
    helpful_votes: int = 0
    not_helpful_votes: int = 0
    related_articles: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.related_articles is None:
            self.related_articles = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SearchResult:
    """Search result with relevance scoring."""
    article: KnowledgeArticle
    relevance_score: float
    matched_fields: List[str]
    snippet: str


@dataclass
class SearchQuery:
    """Search query structure."""
    query: str
    article_type: Optional[ArticleType] = None
    category: Optional[str] = None
    tags: Optional[Set[str]] = None
    status: ArticleStatus = ArticleStatus.PUBLISHED
    limit: int = 10


@durable.object
class KnowledgeBase(DurableObject):
    """
    Durable knowledge base object with search and content management.
    
    Provides searchable repository of articles, FAQs, and documentation
    with analytics, versioning, and content lifecycle management.
    """
    
    def __init__(self, kb_id: str = "main"):
        super().__init__()
        self.kb_id = kb_id
        self.created_at = time.time()
        self.last_updated = time.time()
        
        # Core content storage
        self.articles: Dict[str, KnowledgeArticle] = {}
        self.categories: Dict[str, List[str]] = {}  # category -> article_ids
        self.tags: Dict[str, List[str]] = {}        # tag -> article_ids
        
        # Search and indexing
        self.search_index: Dict[str, Set[str]] = {}  # word -> article_ids
        self.category_index: Dict[str, Set[str]] = {}
        self.tag_index: Dict[str, Set[str]] = {}
        
        # Analytics and metrics
        self.search_history: List[Dict[str, Any]] = []
        self.popular_articles: List[str] = []
        self.total_searches = 0
        self.total_views = 0
        
        # Configuration
        self.auto_publish = False
        self.require_review = True
        self.max_search_history = 1000
        
        print(f"📚 Created knowledge base {self.kb_id}")
        
        # Initialize with some default content
        asyncio.create_task(self._initialize_default_content())
    
    async def _initialize_default_content(self) -> None:
        """Initialize knowledge base with default content."""
        default_articles = [
            {
                "title": "How to Reset Your Password",
                "content": "To reset your password: 1) Go to the login page 2) Click 'Forgot Password' 3) Enter your email 4) Check your email for reset link 5) Follow the instructions in the email",
                "article_type": ArticleType.FAQ,
                "category": "account",
                "tags": {"password", "login", "account"},
                "author": "system"
            },
            {
                "title": "Order Status and Tracking",
                "content": "You can track your order by: 1) Logging into your account 2) Going to 'My Orders' 3) Clicking on the order number 4) Viewing the tracking information. Orders typically ship within 1-2 business days.",
                "article_type": ArticleType.FAQ,
                "category": "orders",
                "tags": {"tracking", "orders", "shipping"},
                "author": "system"
            },
            {
                "title": "Refund and Return Policy",
                "content": "We offer full refunds within 30 days of purchase. Items must be in original condition. To initiate a return: 1) Contact customer service 2) Provide order number 3) State reason for return 4) Follow return instructions",
                "article_type": ArticleType.POLICY,
                "category": "returns",
                "tags": {"refund", "return", "policy"},
                "author": "system"
            },
            {
                "title": "Troubleshooting Login Issues",
                "content": "If you can't log in: 1) Clear your browser cache and cookies 2) Try incognito/private mode 3) Check if Caps Lock is on 4) Verify your email address 5) Try password reset 6) Contact support if issues persist",
                "article_type": ArticleType.TROUBLESHOOTING,
                "category": "technical",
                "tags": {"login", "troubleshooting", "technical"},
                "author": "system"
            }
        ]
        
        for article_data in default_articles:
            await self.create_article(**article_data)
    
    async def create_article(
        self,
        title: str,
        content: str,
        article_type: ArticleType,
        category: str,
        tags: Set[str],
        author: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create a new knowledge article."""
        
        article_id = f"art_{int(time.time() * 1000)}"
        current_time = time.time()
        
        article = KnowledgeArticle(
            article_id=article_id,
            title=title,
            content=content,
            article_type=article_type,
            status=ArticleStatus.PUBLISHED if self.auto_publish else ArticleStatus.DRAFT,
            tags=tags,
            category=category,
            author=author,
            created_at=current_time,
            updated_at=current_time,
            metadata=metadata or {}
        )
        
        # Store the article
        self.articles[article_id] = article
        
        # Update indexes
        await self._update_indexes(article)
        
        self.last_updated = current_time
        await self.save()
        
        print(f"📄 Created article '{title}' with ID {article_id}")
        return article_id
    
    async def update_article(
        self,
        article_id: str,
        title: str = None,
        content: str = None,
        tags: Set[str] = None,
        category: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Update an existing article."""
        
        if article_id not in self.articles:
            print(f"❌ Article {article_id} not found")
            return False
        
        article = self.articles[article_id]
        old_article = KnowledgeArticle(**asdict(article))  # Create a copy
        
        # Update fields if provided
        if title is not None:
            article.title = title
        if content is not None:
            article.content = content
        if tags is not None:
            article.tags = tags
        if category is not None:
            article.category = category
        if metadata is not None:
            article.metadata.update(metadata)
        
        # Update version and timestamp
        article.version += 1
        article.updated_at = time.time()
        
        # Update status based on review requirements
        if self.require_review and article.status == ArticleStatus.PUBLISHED:
            article.status = ArticleStatus.REVIEW
        
        # Remove old indexes and add new ones
        await self._remove_from_indexes(old_article)
        await self._update_indexes(article)
        
        self.last_updated = time.time()
        await self.save()
        
        print(f"✏️ Updated article {article_id} to version {article.version}")
        return True
    
    async def publish_article(self, article_id: str) -> bool:
        """Publish an article (make it searchable)."""
        
        if article_id not in self.articles:
            return False
        
        article = self.articles[article_id]
        article.status = ArticleStatus.PUBLISHED
        article.updated_at = time.time()
        
        await self._update_indexes(article)
        await self.save()
        
        print(f"📢 Published article {article_id}")
        return True
    
    async def archive_article(self, article_id: str) -> bool:
        """Archive an article (remove from search but keep for reference)."""
        
        if article_id not in self.articles:
            return False
        
        article = self.articles[article_id]
        old_status = article.status
        article.status = ArticleStatus.ARCHIVED
        article.updated_at = time.time()
        
        # Remove from search indexes if it was published
        if old_status == ArticleStatus.PUBLISHED:
            await self._remove_from_indexes(article)
        
        await self.save()
        
        print(f"📦 Archived article {article_id}")
        return True
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search the knowledge base."""
        
        self.total_searches += 1
        search_time = time.time()
        
        # Log the search
        search_log = {
            "query": query.query,
            "timestamp": search_time,
            "filters": {
                "type": query.article_type.value if query.article_type else None,
                "category": query.category,
                "tags": list(query.tags) if query.tags else None
            }
        }
        
        self.search_history.append(search_log)
        
        # Keep search history limited
        if len(self.search_history) > self.max_search_history:
            self.search_history = self.search_history[-self.max_search_history:]
        
        # Perform the search
        results = await self._perform_search(query)
        
        # Update analytics
        for result in results:
            if result.article.article_id not in self.popular_articles:
                self.popular_articles.append(result.article.article_id)
        
        # Keep only top 20 popular articles
        self.popular_articles = self.popular_articles[-20:]
        
        await self.save()
        
        print(f"🔍 Search for '{query.query}' returned {len(results)} results")
        return results
    
    async def _perform_search(self, query: SearchQuery) -> List[SearchResult]:
        """Internal search implementation."""
        
        # Tokenize search query
        search_terms = self._tokenize(query.query.lower())
        
        # Find candidate articles
        candidate_scores: Dict[str, float] = {}
        matched_fields: Dict[str, List[str]] = {}
        
        for term in search_terms:
            # Search in title, content, and tags
            article_ids = self.search_index.get(term, set())
            
            for article_id in article_ids:
                if article_id not in self.articles:
                    continue
                
                article = self.articles[article_id]
                
                # Skip if doesn't match status filter
                if article.status != query.status:
                    continue
                
                # Skip if doesn't match type filter
                if query.article_type and article.article_type != query.article_type:
                    continue
                
                # Skip if doesn't match category filter
                if query.category and article.category != query.category:
                    continue
                
                # Skip if doesn't match tag filter
                if query.tags and not query.tags.intersection(article.tags):
                    continue
                
                # Calculate relevance score
                score = 0.0
                fields = []
                
                # Title match (high weight)
                if term in article.title.lower():
                    score += 3.0
                    fields.append("title")
                
                # Content match (medium weight)
                if term in article.content.lower():
                    score += 1.0
                    fields.append("content")
                
                # Tag match (medium weight)
                if term in [tag.lower() for tag in article.tags]:
                    score += 2.0
                    fields.append("tags")
                
                # Boost score based on article popularity
                if article_id in self.popular_articles:
                    score *= 1.2
                
                # Boost newer articles slightly
                age_factor = max(0.1, 1.0 - (time.time() - article.created_at) / (86400 * 365))
                score *= (0.9 + 0.1 * age_factor)
                
                candidate_scores[article_id] = candidate_scores.get(article_id, 0) + score
                
                if article_id not in matched_fields:
                    matched_fields[article_id] = []
                matched_fields[article_id].extend(fields)
        
        # Sort by relevance score
        sorted_candidates = sorted(
            candidate_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:query.limit]
        
        # Create search results
        results = []
        for article_id, score in sorted_candidates:
            article = self.articles[article_id]
            
            # Create snippet
            snippet = self._create_snippet(article.content, search_terms)
            
            result = SearchResult(
                article=article,
                relevance_score=score,
                matched_fields=list(set(matched_fields[article_id])),
                snippet=snippet
            )
            
            results.append(result)
        
        return results
    
    async def view_article(self, article_id: str) -> Optional[KnowledgeArticle]:
        """View an article and update view count."""
        
        if article_id not in self.articles:
            return None
        
        article = self.articles[article_id]
        article.view_count += 1
        self.total_views += 1
        
        await self.save()
        
        print(f"👁️ Viewed article {article_id} (views: {article.view_count})")
        return article
    
    async def rate_article(self, article_id: str, helpful: bool) -> bool:
        """Rate an article as helpful or not helpful."""
        
        if article_id not in self.articles:
            return False
        
        article = self.articles[article_id]
        
        if helpful:
            article.helpful_votes += 1
        else:
            article.not_helpful_votes += 1
        
        await self.save()
        
        print(f"👍 Rated article {article_id} as {'helpful' if helpful else 'not helpful'}")
        return True
    
    async def get_categories(self) -> Dict[str, int]:
        """Get all categories with article counts."""
        category_counts = {}
        
        for article in self.articles.values():
            if article.status == ArticleStatus.PUBLISHED:
                category_counts[article.category] = category_counts.get(article.category, 0) + 1
        
        return category_counts
    
    async def get_popular_tags(self, limit: int = 20) -> List[tuple[str, int]]:
        """Get most popular tags with usage counts."""
        tag_counts = {}
        
        for article in self.articles.values():
            if article.status == ArticleStatus.PUBLISHED:
                for tag in article.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by count and return top tags
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_tags[:limit]
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get knowledge base analytics."""
        
        published_articles = [a for a in self.articles.values() if a.status == ArticleStatus.PUBLISHED]
        
        # Calculate average helpfulness
        total_votes = sum(a.helpful_votes + a.not_helpful_votes for a in published_articles)
        helpful_votes = sum(a.helpful_votes for a in published_articles)
        
        helpfulness_ratio = helpful_votes / total_votes if total_votes > 0 else 0
        
        # Recent search trends
        recent_searches = self.search_history[-100:] if len(self.search_history) > 100 else self.search_history
        search_terms = []
        for search in recent_searches:
            search_terms.extend(search["query"].lower().split())
        
        term_counts = {}
        for term in search_terms:
            term_counts[term] = term_counts.get(term, 0) + 1
        
        popular_search_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_articles": len(self.articles),
            "published_articles": len(published_articles),
            "total_searches": self.total_searches,
            "total_views": self.total_views,
            "helpfulness_ratio": helpfulness_ratio,
            "popular_search_terms": popular_search_terms,
            "categories": await self.get_categories(),
            "popular_tags": await self.get_popular_tags(10)
        }
    
    async def _update_indexes(self, article: KnowledgeArticle) -> None:
        """Update search indexes for an article."""
        
        if article.status != ArticleStatus.PUBLISHED:
            return
        
        # Index title and content words
        all_text = f"{article.title} {article.content}".lower()
        words = self._tokenize(all_text)
        
        for word in words:
            if word not in self.search_index:
                self.search_index[word] = set()
            self.search_index[word].add(article.article_id)
        
        # Index tags
        for tag in article.tags:
            tag_lower = tag.lower()
            if tag_lower not in self.search_index:
                self.search_index[tag_lower] = set()
            self.search_index[tag_lower].add(article.article_id)
    
    async def _remove_from_indexes(self, article: KnowledgeArticle) -> None:
        """Remove article from search indexes."""
        
        # Remove from word index
        all_text = f"{article.title} {article.content}".lower()
        words = self._tokenize(all_text)
        
        for word in words:
            if word in self.search_index:
                self.search_index[word].discard(article.article_id)
                if not self.search_index[word]:
                    del self.search_index[word]
        
        # Remove from tag index
        for tag in article.tags:
            tag_lower = tag.lower()
            if tag_lower in self.search_index:
                self.search_index[tag_lower].discard(article.article_id)
                if not self.search_index[tag_lower]:
                    del self.search_index[tag_lower]
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for search indexing."""
        # Simple tokenization - split on whitespace and punctuation
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter out very short words
        return [word for word in words if len(word) > 2]
    
    def _create_snippet(self, content: str, search_terms: List[str]) -> str:
        """Create a search result snippet."""
        
        # Find the first occurrence of any search term
        content_lower = content.lower()
        earliest_pos = len(content)
        
        for term in search_terms:
            pos = content_lower.find(term)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos
        
        # Create snippet around the found term
        start = max(0, earliest_pos - 50)
        end = min(len(content), earliest_pos + 150)
        
        snippet = content[start:end]
        
        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet


# Example usage and testing
async def main():
    """Test the KnowledgeBase durable object."""
    
    print("🧪 Testing KnowledgeBase Durable Object")
    print("=" * 50)
    
    # Create knowledge base
    kb = KnowledgeBase("test_kb")
    
    # Wait for initialization
    await asyncio.sleep(0.1)
    
    # Search for existing content
    query = SearchQuery(query="password reset")
    results = await kb.search(query)
    
    print(f"\n🔍 Search Results for 'password reset':")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result.article.title} (score: {result.relevance_score:.2f})")
        print(f"      Snippet: {result.snippet}")
        print(f"      Matched: {', '.join(result.matched_fields)}")
    
    # View an article
    if results:
        article = await kb.view_article(results[0].article.article_id)
        print(f"\n👁️ Viewed: {article.title}")
    
    # Rate an article
    if results:
        await kb.rate_article(results[0].article.article_id, True)
    
    # Create a new article
    new_article_id = await kb.create_article(
        title="API Rate Limiting Guide",
        content="Our API has rate limits to ensure fair usage. Standard accounts get 1000 requests per hour. Premium accounts get 10000 requests per hour. If you exceed the limit, you'll receive a 429 status code.",
        article_type=ArticleType.API_DOCS,
        category="technical",
        tags={"api", "rate-limiting", "technical"},
        author="tech_writer"
    )
    
    # Publish the article
    await kb.publish_article(new_article_id)
    
    # Search again
    api_query = SearchQuery(query="API rate limit")
    api_results = await kb.search(api_query)
    
    print(f"\n🔍 Search Results for 'API rate limit':")
    for i, result in enumerate(api_results, 1):
        print(f"   {i}. {result.article.title} (score: {result.relevance_score:.2f})")
    
    # Get analytics
    analytics = await kb.get_analytics()
    print(f"\n📊 Knowledge Base Analytics:")
    for key, value in analytics.items():
        print(f"   {key}: {value}")
    
    # Get categories
    categories = await kb.get_categories()
    print(f"\n📁 Categories:")
    for category, count in categories.items():
        print(f"   {category}: {count} articles")
    
    # Test category filtering
    tech_query = SearchQuery(query="login", category="technical")
    tech_results = await kb.search(tech_query)
    print(f"\n🔍 Technical Articles about 'login': {len(tech_results)} results")


if __name__ == "__main__":
    asyncio.run(main())