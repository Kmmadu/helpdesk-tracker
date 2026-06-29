from typing import Dict, List

class CategoryDetector:
    """Smart category detection based on keywords"""
    
    CATEGORY_RULES = {
        'Network': {
            'keywords': [
                'vpn', 'wifi', 'internet', 'network', 'connection', 
                'ethernet', 'router', 'switch', 'firewall', 'ip address',
                'dns', 'dhcp', 'ping', 'latency', 'bandwidth',
                'remote desktop', 'rdp', 'ssh', 'port'
            ],
            'weight': 1
        },
        'Hardware': {
            'keywords': [
                'printer', 'computer', 'laptop', 'monitor', 'keyboard',
                'mouse', 'hard drive', 'ssd', 'battery', 'charger',
                'display', 'screen', 'power', 'fan', 'overheating',
                'hardware', 'device', 'machine'
            ],
            'weight': 1
        },
        'Software': {
            'keywords': [
                'excel', 'word', 'outlook', 'email', 'office',
                'software', 'application', 'app', 'program', 'windows',
                'mac', 'linux', 'update', 'install', 'uninstall',
                'crash', 'freeze', 'bug', 'error message', 'exception',
                'database', 'sql', 'license', 'activation'
            ],
            'weight': 1
        },
        'Access': {
            'keywords': [
                'password', 'login', 'access', 'permission', 'account',
                'locked', 'unlock', 'reset password', 'authorization',
                'authentication', 'mfa', '2fa', 'active directory',
                'ldap', 'single sign on', 'sso', 'role'
            ],
            'weight': 1
        }
    }
    
    @staticmethod
    def detect(text: str) -> str:
        """
        Detect category based on keyword analysis
        Returns: 'Network', 'Hardware', 'Software', or 'Access'
        """
        if not text:
            return "Network"
            
        text_lower = text.lower()
        scores = {}
        
        for category, rules in CategoryDetector.CATEGORY_RULES.items():
            score = 0
            for keyword in rules['keywords']:
                if keyword in text_lower:
                    score += rules['weight']
            scores[category] = score
        
        # Find category with highest score
        max_score = max(scores.values())
        
        # If no keywords matched, default to Network
        if max_score == 0:
            return "Network"
        
        # Get categories with max score
        best_categories = [c for c, s in scores.items() if s == max_score]
        
        # If tie, return first one
        return best_categories[0] if best_categories else "Network"