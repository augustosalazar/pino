"""
Difficulty Manager
Handles difficulty adjustments based on user performance
"""

from typing import Dict, List, Tuple
from models import ExerciseWithAnswer, Operator


class DifficultyManager:
    """Manages user difficulty profiles and adjustments"""
    
    def __init__(self):
        pass
    
    def calculate_adjustments(
        self,
        exercises: List[ExerciseWithAnswer],
        current_difficulty: Dict[str, float]
    ) -> Tuple[Dict[str, float], List[Dict]]:
        """
        Calculate difficulty adjustments based on performance
        
        Returns:
            - new_difficulty: Dict mapping operator -> new difficulty
            - adjustment_records: List of adjustment records for database
        """
        # Group exercises by operator
        stats_by_operator = {}
        
        for exercise in exercises:
            op = exercise.operator.value
            if op not in stats_by_operator:
                stats_by_operator[op] = {
                    'correct': 0,
                    'total': 0
                }
            
            stats_by_operator[op]['total'] += 1
            if exercise.is_correct:
                stats_by_operator[op]['correct'] += 1
        
        # Calculate adjustments
        new_difficulty = current_difficulty.copy()
        adjustment_records = []
        
        for operator, stats in stats_by_operator.items():
            if stats['total'] == 0:
                continue
            
            success_rate = (stats['correct'] / stats['total']) * 100
            old_diff = current_difficulty.get(operator, 1.0)
            new_diff = old_diff
            reason = "Maintain level"
            
            # Apply adjustment rules
            if success_rate >= 90:
                new_diff = min(10.0, old_diff + 1.0)
                reason = "Success rate >= 90%"
            elif success_rate >= 80:
                new_diff = min(10.0, old_diff + 0.5)
                reason = "Success rate >= 80%"
            elif success_rate <= 30:
                new_diff = max(1.0, old_diff - 1.0)
                reason = "Success rate <= 30%"
            elif success_rate <= 50:
                new_diff = max(1.0, old_diff - 0.5)
                reason = "Success rate <= 50%"
            # Else: 51-79% - maintain level
            
            new_diff = round(new_diff, 2)
            new_difficulty[operator] = new_diff
            
            # Record adjustment if changed
            if new_diff != old_diff:
                adjustment_records.append({
                    'operator': operator,
                    'previous_difficulty': old_diff,
                    'new_difficulty': new_diff,
                    'reason': reason,
                    'success_rate': round(success_rate, 2),
                    'correct': stats['correct'],
                    'total': stats['total']
                })
        
        return new_difficulty, adjustment_records
    
    def calculate_score(self, exercises: List[ExerciseWithAnswer]) -> int:
        """
        Calculate score earned for the session
        Score = sum(difficulty_level * 10) for each correct answer
        """
        score = 0
        for exercise in exercises:
            if exercise.is_correct:
                score += int(exercise.difficulty_level * 10)
        return score


# Global instance
difficulty_manager = DifficultyManager()
