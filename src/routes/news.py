from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from src.models.article import Article, db
from src.services.news_service import NewsService
from src.services.translation_service import TranslationService
import logging

logger = logging.getLogger(__name__)

news_bp = Blueprint('news', __name__)
news_service = NewsService()
translation_service = TranslationService()

@news_bp.route('/articles', methods=['GET'])
def get_articles():
    """
    Get translated sports articles with pagination and filtering
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category', 'sports')
        translated_only = request.args.get('translated_only', 'true').lower() == 'true'
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 50)
        
        # Build query
        query = Article.query.filter_by(category=category)
        
        if translated_only:
            query = query.filter_by(is_translated=True)
        
        # Order by publication date (newest first)
        query = query.order_by(Article.published_at.desc())
        
        # Paginate results
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        articles = [article.to_dict() for article in pagination.items]
        
        return jsonify({
            'success': True,
            'articles': articles,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting articles: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve articles'
        }), 500

@news_bp.route('/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    """
    Get a specific article by ID
    """
    try:
        article = Article.query.get_or_404(article_id)
        return jsonify({
            'success': True,
            'article': article.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting article {article_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Article not found'
        }), 404

@news_bp.route('/fetch-news', methods=['POST'])
def fetch_news():
    """
    Fetch new sports news from external APIs
    """
    try:
        # Get parameters
        data = request.get_json() or {}
        locale = data.get('locale', 'us')
        language = data.get('language', 'en')
        limit = min(data.get('limit', 10), 20)  # Limit to prevent abuse
        
        # Fetch news from external API
        articles_data = news_service.get_sports_headlines(locale, language, limit)
        
        # If no articles from API, use demo articles
        if not articles_data:
            articles_data = news_service.get_demo_articles()
        
        new_articles = []
        updated_articles = []
        
        for article_data in articles_data:
            try:
                # Check if article already exists
                existing_article = Article.query.filter_by(uuid=article_data['uuid']).first()
                
                if existing_article:
                    updated_articles.append(existing_article.to_dict())
                    continue
                
                # Parse published date
                published_at = datetime.utcnow()
                if 'published_at' in article_data:
                    try:
                        # Handle different date formats
                        date_str = article_data['published_at']
                        if date_str.endswith('Z'):
                            date_str = date_str[:-1]
                        published_at = datetime.fromisoformat(date_str.replace('T', ' '))
                    except:
                        published_at = datetime.utcnow()
                
                # Create new article
                article = Article(
                    uuid=article_data['uuid'],
                    title=article_data.get('title', ''),
                    description=article_data.get('description', ''),
                    content=article_data.get('snippet', ''),
                    url=article_data.get('url', ''),
                    image_url=article_data.get('image_url', ''),
                    source=article_data.get('source', 'unknown'),
                    language=article_data.get('language', 'en'),
                    category='sports',
                    published_at=published_at
                )
                
                db.session.add(article)
                new_articles.append(article.to_dict())
                
            except Exception as e:
                logger.error(f"Error processing article {article_data.get('uuid', 'unknown')}: {e}")
                continue
        
        # Commit all new articles
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Fetched {len(new_articles)} new articles',
            'new_articles': len(new_articles),
            'existing_articles': len(updated_articles),
            'articles': new_articles
        })
        
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to fetch news'
        }), 500

@news_bp.route('/translate-article/<int:article_id>', methods=['POST'])
def translate_article(article_id):
    """
    Translate a specific article to Bosnian
    """
    try:
        article = Article.query.get_or_404(article_id)
        
        if article.is_translated:
            return jsonify({
                'success': True,
                'message': 'Article already translated',
                'article': article.to_dict()
            })
        
        # Translate title
        if article.title:
            article.title_translated = translation_service.translate_text(
                article.title, 'bs', article.language
            )
        
        # Translate description
        if article.description:
            article.description_translated = translation_service.translate_text(
                article.description, 'bs', article.language
            )
        
        # Translate content
        if article.content:
            article.content_translated = translation_service.translate_text(
                article.content, 'bs', article.language
            )
        
        # Update translation status
        article.is_translated = True
        article.translated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Article translated successfully',
            'article': article.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error translating article {article_id}: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to translate article'
        }), 500

@news_bp.route('/translate-all', methods=['POST'])
def translate_all_articles():
    """
    Translate all untranslated articles
    """
    try:
        # Get untranslated articles
        untranslated_articles = Article.query.filter_by(is_translated=False).limit(10).all()
        
        translated_count = 0
        
        for article in untranslated_articles:
            try:
                # Translate title
                if article.title:
                    article.title_translated = translation_service.translate_text(
                        article.title, 'bs', article.language
                    )
                
                # Translate description
                if article.description:
                    article.description_translated = translation_service.translate_text(
                        article.description, 'bs', article.language
                    )
                
                # Translate content
                if article.content:
                    article.content_translated = translation_service.translate_text(
                        article.content, 'bs', article.language
                    )
                
                # Update translation status
                article.is_translated = True
                article.translated_at = datetime.utcnow()
                translated_count += 1
                
            except Exception as e:
                logger.error(f"Error translating article {article.id}: {e}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Translated {translated_count} articles',
            'translated_count': translated_count
        })
        
    except Exception as e:
        logger.error(f"Error in bulk translation: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to translate articles'
        }), 500

@news_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get statistics about articles and translations
    """
    try:
        total_articles = Article.query.count()
        translated_articles = Article.query.filter_by(is_translated=True).count()
        recent_articles = Article.query.filter(
            Article.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_articles': total_articles,
                'translated_articles': translated_articles,
                'untranslated_articles': total_articles - translated_articles,
                'recent_articles': recent_articles,
                'translation_percentage': round((translated_articles / total_articles * 100) if total_articles > 0 else 0, 1)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get statistics'
        }), 500

