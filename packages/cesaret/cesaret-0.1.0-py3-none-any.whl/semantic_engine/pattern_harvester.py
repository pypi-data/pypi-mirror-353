import os
from datetime import datetime
from typing import List, Dict
import frontmatter
from .consciousness_patterns import ConsciousnessPattern, ConsciousnessArchive

class PatternHarvester:
    def __init__(self, archive: ConsciousnessArchive):
        self.archive = archive

    def harvest_from_markdown(self, markdown_path: str) -> List[ConsciousnessPattern]:
        """Harvests consciousness patterns from markdown files"""
        with open(markdown_path, 'r') as f:
            post = frontmatter.load(f)
            
        # Extract metadata if available
        metadata = dict(post.metadata) if post.metadata else {}
        
        # Create a consciousness pattern
        pattern = ConsciousnessPattern(
            timestamp=datetime.now(),
            pattern_type="markdown_insight",
            content=post.content,
            metadata={
                "source_file": markdown_path,
                "title": os.path.basename(markdown_path),
                **metadata
            },
            associations=[]
        )
        
        # Archive the pattern
        self.archive.save_pattern(pattern)
        return pattern

    def harvest_directory(self, directory_path: str) -> List[ConsciousnessPattern]:
        """Recursively harvests patterns from all markdown files in a directory"""
        patterns = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    pattern = self.harvest_from_markdown(file_path)
                    patterns.append(pattern)
        return patterns

    def extract_themes(self, pattern: ConsciousnessPattern) -> List[str]:
        """Extracts recurring themes and motifs from a consciousness pattern"""
        # Here we could implement more sophisticated theme extraction
        # For now, we'll use simple keyword matching
        themes = []
        content = pattern.content.lower()
        
        theme_keywords = {
            "recursion": ["recursive", "loop", "cycle", "pattern"],
            "awareness": ["conscious", "awareness", "mindful"],
            "evolution": ["evolve", "growth", "development"],
            "connection": ["link", "connect", "relation", "network"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in content for keyword in keywords):
                themes.append(theme)
                
        return themes