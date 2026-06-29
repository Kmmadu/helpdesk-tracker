import re
from typing import Optional

class PriorityDetector:
    """Intelligent priority detection based on keywords and context"""
    
    PRIORITY_RULES = {
        'Critical': {
            'keywords': [
                'down', 'outage', 'emergency', 'critical', 'urgent',
                'production down', 'server down', 'all users', 'system down',
                'not working at all', 'completely down', 'business critical'
            ],
            'weight': 3
        },
        'High': {
            'keywords': [
                'urgent', 'asap', 'immediately', 'cannot work',
                'blocked', 'unable to access', 'major issue',
                'stopped working', 'not accessible'
            ],
            'weight': 2
        },
        'Medium': {
            'keywords': [
                'issue', 'problem', 'not working', 'error',
                'needs attention', 'something wrong', 'having trouble',
                'need help with', 'issue with'
            ],
            'weight': 1
        },
        'Low': {
            'keywords': [
                'question', 'help', 'how to', 'request',
                'suggestion', 'feedback', 'information',
                'clarification', 'guide', 'tutorial'
            ],
            'weight': 0
        }
    }
    
    @staticmethod
    def detect(text: str) -> str:
        """
        Detect priority based on keyword analysis
        Returns: 'Critical', 'High', 'Medium', or 'Low'
        """
        if not text:
            return "Medium"
            
        text_lower = text.lower()
        
        # Score each priority level
        scores = {}
        for priority, rules in PriorityDetector.PRIORITY_RULES.items():
            score = 0
            for keyword in rules['keywords']:
                if keyword in text_lower:
                    score += rules['weight']
            
            # Check for exact phrase matches (higher weight)
            for keyword in rules['keywords']:
                if len(keyword) > 3 and keyword in text_lower:
                    # If the keyword appears as a standalone word or phrase
                    if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                        score += 1
            
            scores[priority] = score
        
        # Find priority with highest score
        max_score = max(scores.values())
        if max_score == 0:
            return "Medium"  # Default
            
        # Get all priorities with max score
        candidates = [p for p, s in scores.items() if s == max_score]
        
        # Return the highest priority among candidates
        priority_order = ['Critical', 'High', 'Medium', 'Low']
        for p in priority_order:
            if p in candidates:
                return p
        
        return "Medium"