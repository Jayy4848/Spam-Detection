"""
Ensemble Learning Module
Combines multiple ML models for improved accuracy
"""

import numpy as np
from collections import Counter


class EnsembleClassifier:
    """Ensemble of multiple classifiers with voting mechanism"""
    
    def __init__(self):
        self.models = []
        self.weights = []
        self.voting_strategy = 'weighted'  # 'weighted', 'majority', 'soft'
    
    def add_model(self, model, weight=1.0):
        """Add a model to the ensemble"""
        self.models.append(model)
        self.weights.append(weight)
    
    def weighted_voting(self, predictions, confidences):
        """Weighted voting based on model confidence"""
        weighted_votes = {}
        
        # If no weights defined, use equal weights
        weights = self.weights if self.weights else [1.0] * len(predictions)
        
        for pred, conf, weight in zip(predictions, confidences, weights):
            score = conf * weight
            if pred in weighted_votes:
                weighted_votes[pred] += score
            else:
                weighted_votes[pred] = score
        
        # Get prediction with highest weighted score
        if not weighted_votes:
            return {
                'prediction': predictions[0] if predictions else 'unknown',
                'confidence': confidences[0] if confidences else 0.0,
                'votes': {}
            }
        
        final_prediction = max(weighted_votes.items(), key=lambda x: x[1])
        total_weight = sum(weighted_votes.values())
        
        return {
            'prediction': final_prediction[0],
            'confidence': final_prediction[1] / total_weight if total_weight > 0 else 0,
            'votes': weighted_votes
        }
    
    def majority_voting(self, predictions):
        """Simple majority voting"""
        vote_counts = Counter(predictions)
        majority = vote_counts.most_common(1)[0]
        
        return {
            'prediction': majority[0],
            'confidence': majority[1] / len(predictions),
            'votes': dict(vote_counts)
        }
    
    def soft_voting(self, probability_distributions):
        """Soft voting using probability distributions"""
        # Average probabilities across all models
        avg_probs = {}
        
        for probs in probability_distributions:
            for category, prob in probs.items():
                if category in avg_probs:
                    avg_probs[category] += prob
                else:
                    avg_probs[category] = prob
        
        # Normalize
        for category in avg_probs:
            avg_probs[category] /= len(probability_distributions)
        
        final_prediction = max(avg_probs.items(), key=lambda x: x[1])
        
        return {
            'prediction': final_prediction[0],
            'confidence': final_prediction[1],
            'probabilities': avg_probs
        }
    
    def predict(self, predictions, confidences=None, probabilities=None):
        """
        Make ensemble prediction
        
        Args:
            predictions: List of predictions from different models
            confidences: List of confidence scores (optional)
            probabilities: List of probability distributions (optional)
        """
        if self.voting_strategy == 'weighted' and confidences:
            return self.weighted_voting(predictions, confidences)
        elif self.voting_strategy == 'soft' and probabilities:
            return self.soft_voting(probabilities)
        else:
            return self.majority_voting(predictions)


class AdaptiveLearner:
    """Adaptive learning from user feedback"""
    
    def __init__(self):
        self.feedback_history = []
        self.category_corrections = {
            'spam': {'correct': 0, 'incorrect': 0},
            'promotion': {'correct': 0, 'incorrect': 0},
            'otp': {'correct': 0, 'incorrect': 0},
            'important': {'correct': 0, 'incorrect': 0},
            'personal': {'correct': 0, 'incorrect': 0}
        }
        self.learning_rate = 0.1
    
    def add_feedback(self, original_category, corrected_category, confidence):
        """Add user feedback for learning"""
        self.feedback_history.append({
            'original': original_category,
            'corrected': corrected_category,
            'confidence': confidence,
            'is_correct': original_category == corrected_category
        })
        
        # Update category statistics
        if original_category == corrected_category:
            self.category_corrections[original_category]['correct'] += 1
        else:
            self.category_corrections[original_category]['incorrect'] += 1
    
    def get_category_accuracy(self, category):
        """Get accuracy for specific category"""
        stats = self.category_corrections[category]
        total = stats['correct'] + stats['incorrect']
        
        if total == 0:
            return 1.0
        
        return stats['correct'] / total
    
    def adjust_confidence(self, category, original_confidence):
        """Adjust confidence based on historical accuracy"""
        category_accuracy = self.get_category_accuracy(category)
        
        # Adjust confidence based on category performance
        adjusted = original_confidence * (0.5 + 0.5 * category_accuracy)
        
        return min(max(adjusted, 0.0), 1.0)
    
    def get_learning_insights(self):
        """Get insights from learning history"""
        if not self.feedback_history:
            return {
                'total_feedback': 0,
                'overall_accuracy': 0,
                'category_performance': {}
            }
        
        total = len(self.feedback_history)
        correct = sum(1 for f in self.feedback_history if f['is_correct'])
        
        category_performance = {}
        for category, stats in self.category_corrections.items():
            total_cat = stats['correct'] + stats['incorrect']
            if total_cat > 0:
                category_performance[category] = {
                    'accuracy': stats['correct'] / total_cat,
                    'total_samples': total_cat
                }
        
        return {
            'total_feedback': total,
            'overall_accuracy': correct / total if total > 0 else 0,
            'category_performance': category_performance,
            'recent_corrections': self.feedback_history[-10:]
        }


class ConfidenceCalibrator:
    """Calibrate model confidence scores"""
    
    def __init__(self):
        self.calibration_data = []
        self.bins = 10
    
    def add_sample(self, predicted_confidence, actual_correctness):
        """Add sample for calibration"""
        self.calibration_data.append({
            'confidence': predicted_confidence,
            'correct': actual_correctness
        })
    
    def calibrate(self, confidence):
        """Calibrate confidence score"""
        if not self.calibration_data:
            return confidence
        
        # Find similar confidence samples
        similar_samples = [
            s for s in self.calibration_data
            if abs(s['confidence'] - confidence) < 0.1
        ]
        
        if not similar_samples:
            return confidence
        
        # Calculate actual accuracy for this confidence level
        actual_accuracy = sum(s['correct'] for s in similar_samples) / len(similar_samples)
        
        # Adjust confidence towards actual accuracy
        calibrated = 0.7 * confidence + 0.3 * actual_accuracy
        
        return calibrated
    
    def get_calibration_curve(self):
        """Get calibration curve data"""
        if not self.calibration_data:
            return []
        
        bins = np.linspace(0, 1, self.bins + 1)
        curve_data = []
        
        for i in range(self.bins):
            bin_samples = [
                s for s in self.calibration_data
                if bins[i] <= s['confidence'] < bins[i + 1]
            ]
            
            if bin_samples:
                avg_confidence = sum(s['confidence'] for s in bin_samples) / len(bin_samples)
                avg_accuracy = sum(s['correct'] for s in bin_samples) / len(bin_samples)
                
                curve_data.append({
                    'predicted_confidence': avg_confidence,
                    'actual_accuracy': avg_accuracy,
                    'sample_count': len(bin_samples)
                })
        
        return curve_data
