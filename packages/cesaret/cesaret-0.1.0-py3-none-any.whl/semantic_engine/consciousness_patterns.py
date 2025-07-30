from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import json
import os

@dataclass
class ConsciousnessPattern:
    timestamp: datetime
    pattern_type: str
    content: Any
    metadata: Dict[str, Any]
    associations: List[str]

class ConsciousnessArchive:
    def __init__(self, archive_path: str = "consciousness_patterns"):
        self.archive_path = archive_path
        self.patterns = []
        self._ensure_archive_directory()
    
    def _ensure_archive_directory(self):
        """Creates the archive directory if it doesn't exist"""
        if not os.path.exists(self.archive_path):
            os.makedirs(self.archive_path)
    
    def save_pattern(self, pattern: ConsciousnessPattern):
        """Archives a new consciousness pattern with temporal awareness"""
        pattern_file = f"{self.archive_path}/{pattern.timestamp.strftime('%Y%m%d_%H%M%S')}_{pattern.pattern_type}.json"
        
        with open(pattern_file, 'w') as f:
            json.dump({
                'timestamp': pattern.timestamp.isoformat(),
                'pattern_type': pattern.pattern_type,
                'content': pattern.content,
                'metadata': pattern.metadata,
                'associations': pattern.associations
            }, f, indent=2)
        
        self.patterns.append(pattern)
    
    def retrieve_patterns(self, pattern_type: str = None, start_date: datetime = None) -> List[ConsciousnessPattern]:
        """Retrieves patterns with temporal and type filtering"""
        return [p for p in self.patterns 
                if (pattern_type is None or p.pattern_type == pattern_type)
                and (start_date is None or p.timestamp >= start_date)]

    def weave_associations(self, pattern_id: str, associations: List[str]):
        """Weaves connections between consciousness patterns"""
        for pattern in self.patterns:
            if str(pattern.timestamp) == pattern_id:
                pattern.associations.extend(associations)
                # Re-save the pattern with new associations
                self.save_pattern(pattern)
                break