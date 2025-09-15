import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Trophy, Star, Target, Award, TrendingUp } from 'lucide-react';
import { SkillScoreData } from '@/services/api';

interface SkillScoreCardProps {
  skillData: SkillScoreData;
  compact?: boolean;
}

const getSkillLevelColor = (level: string) => {
  const colors = {
    'Novice': 'bg-gray-500',
    'Beginner': 'bg-blue-500',
    'Intermediate': 'bg-green-500',
    'Advanced': 'bg-yellow-500',
    'Expert': 'bg-red-500'
  };
  return colors[level as keyof typeof colors] || 'bg-gray-500';
};

const getSkillLevelIcon = (level: string) => {
  const icons = {
    'Novice': Star,
    'Beginner': Target,
    'Intermediate': Award,
    'Advanced': TrendingUp,
    'Expert': Trophy
  };
  return icons[level as keyof typeof icons] || Star;
};

export const SkillScoreCard: React.FC<SkillScoreCardProps> = ({ skillData, compact = false }) => {
  const LevelIcon = getSkillLevelIcon(skillData.skill_level);
  const progressToNextLevel = (skillData.skill_score / skillData.next_level_threshold) * 100;

  if (compact) {
    return (
      <Card className="w-full">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <LevelIcon className="h-5 w-5 text-primary" />
              <div>
                <p className="text-sm font-medium">{skillData.skill_level}</p>
                <p className="text-xs text-muted-foreground">{skillData.skill_score.toFixed(1)} pts</p>
              </div>
            </div>
            <Badge variant="secondary" className={getSkillLevelColor(skillData.skill_level)}>
              {skillData.skill_level}
            </Badge>
          </div>
          <div className="mt-2">
            <Progress value={progressToNextLevel} className="h-2" />
            <p className="text-xs text-muted-foreground mt-1">
              {skillData.skill_score.toFixed(1)} / {skillData.next_level_threshold} to next level
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <LevelIcon className="h-6 w-6 text-primary" />
          <span>Skill Profile</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold">{skillData.skill_score.toFixed(1)}</h3>
            <p className="text-sm text-muted-foreground">Skill Points</p>
          </div>
          <Badge variant="secondary" className={`${getSkillLevelColor(skillData.skill_level)} text-white`}>
            {skillData.skill_level}
          </Badge>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span>Progress to next level</span>
            <span>{progressToNextLevel.toFixed(1)}%</span>
          </div>
          <Progress value={progressToNextLevel} className="h-3" />
          <p className="text-xs text-muted-foreground mt-1">
            {skillData.skill_score.toFixed(1)} / {skillData.next_level_threshold} points needed
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
          <div className="text-center">
            <p className="text-lg font-semibold">{skillData.total_milestones_completed}</p>
            <p className="text-xs text-muted-foreground">Milestones Completed</p>
          </div>
          <div className="text-center">
            <p className="text-lg font-semibold">{skillData.total_campaigns_participated}</p>
            <p className="text-xs text-muted-foreground">Campaigns Participated</p>
          </div>
        </div>

        {skillData.skill_nft_token_id && (
          <div className="flex items-center space-x-2 p-3 bg-muted rounded-lg">
            <Trophy className="h-4 w-4 text-yellow-500" />
            <div>
              <p className="text-sm font-medium">Skill NFT Minted</p>
              <p className="text-xs text-muted-foreground">Token ID: {skillData.skill_nft_token_id}</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};