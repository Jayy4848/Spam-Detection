"""
Deep Learning Features Simulation
Simulates neural network-based analysis
"""

import re
import numpy as np


class NeuralFeatureExtractor:
    """Extract deep features from text"""
    
    def __init__(self):
        self.embedding_dim = 128
        self.max_sequence_length = 100
    
    def extract_features(self, text):
        """
        Extract neural network-style features
        Simulates embedding and feature extraction
        """
        # Character-level features
        char_features = self._extract_char_features(text)
        
        # Word-level features
        word_features = self._extract_word_features(text)
        
        # Sequence features
        sequence_features = self._extract_sequence_features(text)
        
        # Attention-like features
        attention_features = self._extract_attention_features(text)
        
        return {
            'char_features': char_features,
            'word_features': word_features,
            'sequence_features': sequence_features,
            'attention_features': attention_features,
            'combined_score': self._combine_features(
                char_features, word_features, sequence_features, attention_features
            )
        }
    
    def _extract_char_features(self, text):
        """Extract character-level features"""
        if not text:
            return {'diversity': 0, 'entropy': 0}
        
        # Character diversity
        unique_chars = len(set(text))
        total_chars = len(text)
        diversity = unique_chars / total_chars if total_chars > 0 else 0
        
        # Character entropy (simplified)
        char_freq = {}
        for char in text:
            char_freq[char] = char_freq.get(char, 0) + 1
        
        entropy = 0
        for freq in char_freq.values():
            p = freq / total_chars
            entropy -= p * np.log2(p) if p > 0 else 0
        
        return {
            'diversity': round(diversity, 4),
            'entropy': round(entropy, 4),
            'unique_chars': unique_chars,
            'total_chars': total_chars
        }
    
    def _extract_word_features(self, text):
        """Extract word-level features"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return {'diversity': 0, 'avg_length': 0}
        
        # Word diversity
        unique_words = len(set(words))
        total_words = len(words)
        diversity = unique_words / total_words if total_words > 0 else 0
        
        # Average word length
        avg_length = sum(len(word) for word in words) / total_words
        
        # Vocabulary richness
        vocab_richness = unique_words / np.sqrt(total_words) if total_words > 0 else 0
        
        return {
            'diversity': round(diversity, 4),
            'avg_length': round(avg_length, 2),
            'vocab_richness': round(vocab_richness, 4),
            'unique_words': unique_words,
            'total_words': total_words
        }
    
    def _extract_sequence_features(self, text):
        """Extract sequence-based features"""
        words = text.split()
        
        if len(words) < 2:
            return {'coherence': 0, 'flow': 0}
        
        # Sequence coherence (simplified)
        # Measures consistency in word lengths
        word_lengths = [len(word) for word in words]
        coherence = 1.0 - (np.std(word_lengths) / (np.mean(word_lengths) + 1))
        
        # Flow score (based on punctuation and structure)
        punctuation_count = sum(1 for char in text if char in '.,!?;:')
        flow = min(punctuation_count / len(words), 1.0)
        
        return {
            'coherence': round(coherence, 4),
            'flow': round(flow, 4),
            'sequence_length': len(words)
        }
    
    def _extract_attention_features(self, text):
        """
        Extract attention-like features
        Identifies important words/phrases
        """
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return {'important_words': [], 'attention_scores': {}}
        
        # Simulate attention mechanism
        # Words that are longer, capitalized, or repeated get higher attention
        attention_scores = {}
        
        for word in set(words):
            score = 0.0
            
            # Length-based attention
            score += min(len(word) / 10, 1.0) * 0.3
            
            # Frequency-based attention
            frequency = words.count(word)
            score += min(frequency / len(words), 1.0) * 0.3
            
            # Position-based attention (first and last words)
            if word == words[0] or word == words[-1]:
                score += 0.2
            
            # Capitalization in original text
            if word.upper() in text:
                score += 0.2
            
            attention_scores[word] = round(score, 4)
        
        # Get top attention words
        top_words = sorted(attention_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'important_words': [word for word, _ in top_words],
            'attention_scores': dict(top_words),
            'avg_attention': round(np.mean(list(attention_scores.values())), 4)
        }
    
    def _combine_features(self, char_feat, word_feat, seq_feat, attn_feat):
        """Combine all features into a single score"""
        # Weighted combination
        score = (
            char_feat['diversity'] * 0.2 +
            word_feat['diversity'] * 0.3 +
            seq_feat['coherence'] * 0.3 +
            attn_feat['avg_attention'] * 0.2
        )
        
        return round(score, 4)


class TransferLearningSimulator:
    """Simulate transfer learning from pre-trained models"""
    
    def __init__(self):
        self.base_knowledge = {
            'spam_indicators': ['win', 'free', 'prize', 'click', 'urgent'],
            'legitimate_indicators': ['thank', 'please', 'regards', 'meeting'],
            'financial_terms': ['bank', 'account', 'payment', 'transaction'],
            'personal_terms': ['hi', 'hello', 'how', 'you', 'me']
        }
    
    def apply_transfer_learning(self, text, category):
        """
        Apply transfer learning concepts
        Uses pre-trained knowledge to enhance predictions
        """
        text_lower = text.lower()
        
        # Calculate alignment with base knowledge
        alignments = {}
        
        for knowledge_type, indicators in self.base_knowledge.items():
            matches = sum(1 for indicator in indicators if indicator in text_lower)
            alignment = matches / len(indicators) if indicators else 0
            alignments[knowledge_type] = round(alignment, 4)
        
        # Determine if transfer learning helps
        max_alignment = max(alignments.values())
        transfer_benefit = max_alignment > 0.3
        
        # Calculate confidence boost from transfer learning
        confidence_boost = max_alignment * 0.1 if transfer_benefit else 0
        
        return {
            'alignments': alignments,
            'transfer_benefit': transfer_benefit,
            'confidence_boost': round(confidence_boost, 4),
            'dominant_knowledge': max(alignments.items(), key=lambda x: x[1])[0]
        }


class AttentionMechanism:
    """Attention mechanism for highlighting important parts"""
    
    def __init__(self):
        self.attention_heads = 4
    
    def compute_attention(self, text, query_type='threat'):
        """
        Compute attention weights for text
        
        Args:
            text: Input text
            query_type: Type of attention ('threat', 'sentiment', 'urgency')
        """
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return {'attention_map': {}, 'focused_words': []}
        
        # Define query vectors (what to pay attention to)
        queries = {
            'threat': ['urgent', 'click', 'win', 'free', 'expire', 'act', 'now'],
            'sentiment': ['good', 'bad', 'great', 'terrible', 'love', 'hate'],
            'urgency': ['urgent', 'immediately', 'asap', 'now', 'today', 'hurry']
        }
        
        query_words = queries.get(query_type, queries['threat'])
        
        # Compute attention scores
        attention_map = {}
        
        for i, word in enumerate(words):
            score = 0.0
            
            # Query matching
            if word in query_words:
                score += 0.5
            
            # Position-based attention
            position_weight = 1.0 - (i / len(words))
            score += position_weight * 0.2
            
            # Context-based attention (neighboring words)
            if i > 0 and words[i-1] in query_words:
                score += 0.2
            if i < len(words) - 1 and words[i+1] in query_words:
                score += 0.2
            
            # Length-based attention
            score += min(len(word) / 10, 0.1)
            
            attention_map[word] = round(score, 4)
        
        # Get top attended words
        focused_words = sorted(attention_map.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'attention_map': attention_map,
            'focused_words': [word for word, _ in focused_words],
            'attention_distribution': self._normalize_attention(attention_map)
        }
    
    def _normalize_attention(self, attention_map):
        """Normalize attention scores to sum to 1"""
        total = sum(attention_map.values())
        
        if total == 0:
            return attention_map
        
        return {word: round(score / total, 4) for word, score in attention_map.items()}
    
    def multi_head_attention(self, text):
        """Apply multi-head attention"""
        heads = []
        
        for query_type in ['threat', 'sentiment', 'urgency']:
            attention = self.compute_attention(text, query_type)
            heads.append({
                'query_type': query_type,
                'focused_words': attention['focused_words'],
                'top_score': max(attention['attention_map'].values()) if attention['attention_map'] else 0
            })
        
        return {
            'attention_heads': heads,
            'combined_focus': self._combine_heads(heads)
        }
    
    def _combine_heads(self, heads):
        """Combine multiple attention heads"""
        all_words = []
        for head in heads:
            all_words.extend(head['focused_words'])
        
        # Count frequency across heads
        word_freq = {}
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get words that appear in multiple heads
        important_words = [word for word, freq in word_freq.items() if freq > 1]
        
        return important_words if important_words else all_words[:3]
