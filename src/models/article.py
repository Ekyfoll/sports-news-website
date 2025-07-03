from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    title_translated = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    description_translated = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    content_translated = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(200), nullable=False)
    language = db.Column(db.String(10), nullable=False, default='en')
    category = db.Column(db.String(50), nullable=False, default='sports')
    published_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    translated_at = db.Column(db.DateTime, nullable=True)
    is_translated = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Article {self.title[:50]}...>'

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'title_translated': self.title_translated,
            'description': self.description,
            'description_translated': self.description_translated,
            'content': self.content,
            'content_translated': self.content_translated,
            'url': self.url,
            'image_url': self.image_url,
            'source': self.source,
            'language': self.language,
            'category': self.category,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'translated_at': self.translated_at.isoformat() if self.translated_at else None,
            'is_translated': self.is_translated
        }

