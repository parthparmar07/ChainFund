from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from app.models.user import User, SkillHistory
from app.db import get_database
import math


class SkillScoreService:
    def __init__(self):
        self.db = get_database()

    def calculate_skill_score(self, user: User) -> float:
        """
        Calculate the overall skill score for a user based on their history
        """
        if not user.skill_history:
            return 0.0

        total_score = 0.0
        weights = {
            'completion': 0.4,
            'difficulty': 0.3,
            'timeliness': 0.2,
            'peer_review': 0.1
        }

        for activity in user.skill_history:
            # Base completion score
            completion_score = activity.score_earned

            # Difficulty multiplier
            difficulty_multiplier = self._get_difficulty_multiplier(activity.difficulty_rating)

            # Timeliness bonus
            timeliness_bonus = 1.1 if activity.on_time_completion else 1.0

            # Peer review average
            peer_review_avg = sum(activity.peer_reviews) / len(activity.peer_reviews) if activity.peer_reviews else 1.0
            peer_review_multiplier = peer_review_avg / 5.0  # Normalize to 0-1

            # Calculate weighted score for this activity
            activity_score = (
                completion_score * difficulty_multiplier * timeliness_bonus * peer_review_multiplier
            )

            total_score += activity_score

        # Apply diminishing returns for very high scores
        if total_score > 1000:
            total_score = 1000 + math.log(total_score - 999) * 100

        return round(total_score, 2)

    def _get_difficulty_multiplier(self, difficulty: str) -> float:
        """Get multiplier based on milestone difficulty"""
        multipliers = {
            'easy': 1.0,
            'medium': 1.5,
            'hard': 2.0
        }
        return multipliers.get(difficulty.lower(), 1.0)

    def determine_skill_level(self, skill_score: float) -> str:
        """Determine skill level based on score"""
        if skill_score >= 1000:
            return "Expert"
        elif skill_score >= 500:
            return "Advanced"
        elif skill_score >= 200:
            return "Intermediate"
        elif skill_score >= 50:
            return "Beginner"
        else:
            return "Novice"

    def calculate_average_completion_time(self, user: User) -> Optional[float]:
        """Calculate average completion time in days"""
        if not user.skill_history:
            return None

        total_days = 0
        count = 0

        for activity in user.skill_history:
            # Assuming we have start_date in the future, for now use a mock calculation
            # In real implementation, we'd need start_date in SkillHistory
            total_days += 7  # Mock: assume 7 days average
            count += 1

        return round(total_days / count, 1) if count > 0 else None

    def get_skill_breakdown_by_category(self, user: User) -> Dict[str, float]:
        """Get skill score breakdown by campaign categories"""
        # This would require campaign data to map campaign_id to category
        # For now, return a mock breakdown
        return {
            "Technology": 45.5,
            "Healthcare": 32.1,
            "Environment": 28.7,
            "Education": 15.3
        }

    def get_recent_achievements(self, user: User, limit: int = 5) -> List[Dict]:
        """Get recent skill-earning achievements"""
        recent_activities = sorted(
            user.skill_history,
            key=lambda x: x.completed_at,
            reverse=True
        )[:limit]

        achievements = []
        for activity in recent_activities:
            achievements.append({
                "campaign_id": activity.campaign_id,
                "milestone_title": activity.milestone_title,
                "score_earned": activity.score_earned,
                "completed_at": activity.completed_at.isoformat(),
                "difficulty": activity.difficulty_rating,
                "on_time": activity.on_time_completion
            })

        return achievements

    def get_next_level_threshold(self, current_score: float) -> float:
        """Get the score needed to reach the next level"""
        current_level = self.determine_skill_level(current_score)

        thresholds = {
            "Novice": 50,
            "Beginner": 200,
            "Intermediate": 500,
            "Advanced": 1000,
            "Expert": float('inf')
        }

        return thresholds.get(current_level, float('inf'))

    async def update_user_skill_score(self, wallet_address: str) -> Optional[User]:
        """Update a user's skill score and related fields"""
        user = await User.find_one(User.wallet_address == wallet_address)
        if not user:
            return None

        # Calculate new skill score
        new_score = self.calculate_skill_score(user)
        new_level = self.determine_skill_level(new_score)
        avg_completion_time = self.calculate_average_completion_time(user)

        # Update user fields
        user.skill_score = new_score
        user.skill_level = new_level
        user.average_completion_time = avg_completion_time
        user.updated_at = datetime.utcnow()

        await user.save()
        return user

    async def add_skill_activity(self, wallet_address: str, activity_data: Dict) -> Optional[User]:
        """Add a new skill-earning activity to user's history"""
        user = await User.find_one(User.wallet_address == wallet_address)
        if not user:
            return None

        # Create new skill history entry
        skill_activity = SkillHistory(
            campaign_id=activity_data["campaign_id"],
            milestone_id=activity_data["milestone_id"],
            milestone_title=activity_data["milestone_title"],
            score_earned=activity_data["score_earned"],
            completed_at=datetime.utcnow(),
            difficulty_rating=activity_data.get("difficulty", "medium"),
            on_time_completion=activity_data.get("on_time", True),
            peer_reviews=activity_data.get("peer_reviews", [])
        )

        # Add to user's history
        user.skill_history.append(skill_activity)
        user.total_milestones_completed += 1

        # Update campaign participation if this is a new campaign
        campaign_ids = {activity.campaign_id for activity in user.skill_history}
        user.total_campaigns_participated = len(campaign_ids)

        # Recalculate skill score
        user.skill_score = self.calculate_skill_score(user)
        user.skill_level = self.determine_skill_level(user.skill_score)
        user.updated_at = datetime.utcnow()

        await user.save()
        return user

    async def get_skill_score_data(self, wallet_address: str) -> Optional[Dict]:
        """Get comprehensive skill score data for a user"""
        user = await User.find_one(User.wallet_address == wallet_address)
        if not user:
            return None

        skill_breakdown = self.get_skill_breakdown_by_category(user)
        recent_achievements = self.get_recent_achievements(user)
        next_threshold = self.get_next_level_threshold(user.skill_score)

        return {
            "wallet_address": user.wallet_address,
            "skill_score": user.skill_score,
            "skill_level": user.skill_level,
            "skill_nft_token_id": user.skill_nft_token_id,
            "total_milestones_completed": user.total_milestones_completed,
            "total_campaigns_participated": user.total_campaigns_participated,
            "average_completion_time": user.average_completion_time,
            "skill_breakdown": skill_breakdown,
            "recent_achievements": recent_achievements,
            "next_level_threshold": next_threshold
        }


# Global service instance
skill_score_service = SkillScoreService()