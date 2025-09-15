import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { CheckCircle, Clock, Star, Target, Award, TrendingUp } from 'lucide-react';
import { SkillScoreData } from '@/services/api';

interface SkillAchievementsProps {
  skillData: SkillScoreData;
}

const getDifficultyColor = (difficulty: string) => {
  const colors = {
    'easy': 'text-green-600 bg-green-50',
    'medium': 'text-yellow-600 bg-yellow-50',
    'hard': 'text-red-600 bg-red-50'
  };
  return colors[difficulty as keyof typeof colors] || 'text-gray-600 bg-gray-50';
};

const getDifficultyIcon = (difficulty: string) => {
  const icons = {
    'easy': CheckCircle,
    'medium': Target,
    'hard': Award
  };
  return icons[difficulty as keyof typeof icons] || CheckCircle;
};

export const SkillAchievements: React.FC<SkillAchievementsProps> = ({ skillData }) => {
  const recentAchievements = skillData.recent_achievements.slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Skill Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            <span>Skill Breakdown by Category</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(skillData.skill_breakdown).map(([category, score]) => (
              <div key={category} className="flex items-center justify-between">
                <span className="text-sm font-medium">{category}</span>
                <div className="flex items-center space-x-2">
                  <Progress value={(score / skillData.skill_score) * 100} className="w-20 h-2" />
                  <span className="text-sm text-muted-foreground w-12 text-right">
                    {score.toFixed(1)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Achievements */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Star className="h-5 w-5 text-primary" />
            <span>Recent Achievements</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {recentAchievements.length > 0 ? (
            <div className="space-y-4">
              {recentAchievements.map((achievement, index) => {
                const DifficultyIcon = getDifficultyIcon(achievement.difficulty);
                return (
                  <div key={index} className="flex items-start space-x-3 p-3 rounded-lg border">
                    <DifficultyIcon className="h-5 w-5 text-primary mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {achievement.milestone_title}
                      </p>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge variant="outline" className={`text-xs ${getDifficultyColor(achievement.difficulty)}`}>
                          {achievement.difficulty}
                        </Badge>
                        {achievement.on_time && (
                          <Badge variant="outline" className="text-xs text-green-600 bg-green-50">
                            On Time
                          </Badge>
                        )}
                        <span className="text-xs text-muted-foreground">
                          +{achievement.score_earned.toFixed(1)} pts
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(achievement.completed_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">
              No achievements yet. Complete some milestones to see your progress here!
            </p>
          )}
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Target className="h-4 w-4 text-primary" />
              <div>
                <p className="text-lg font-semibold">{skillData.total_milestones_completed}</p>
                <p className="text-xs text-muted-foreground">Total Milestones</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-primary" />
              <div>
                <p className="text-lg font-semibold">
                  {skillData.average_completion_time ? `${skillData.average_completion_time.toFixed(1)}d` : 'N/A'}
                </p>
                <p className="text-xs text-muted-foreground">Avg Completion</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};