from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database import get_db
from ..models import KnowledgeArticle
from ..schemas import KnowledgeArticle as KnowledgeSchema, KnowledgeArticleCreate

router = APIRouter()

@router.post("/", response_model=KnowledgeSchema)
def create_article(article: KnowledgeArticleCreate, db: Session = Depends(get_db)):
    db_article = KnowledgeArticle(**article.model_dump())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

@router.get("/", response_model=List[KnowledgeSchema])
def get_articles(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(KnowledgeArticle)
    
    if category:
        query = query.filter(KnowledgeArticle.category == category)
    if search:
        query = query.filter(
            (KnowledgeArticle.title.contains(search)) | 
            (KnowledgeArticle.problem.contains(search))
        )
    
    return query.offset(skip).limit(limit).all()

@router.get("/{article_id}", response_model=KnowledgeSchema)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article