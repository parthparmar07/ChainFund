import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Trophy, Medal, Award, Crown } from 'lucide-react';
import { skillApi, SkillLeaderboardEntry } from '@/services/api';

interface SkillLeaderboardProps {
  limit?: number;
}

const getRankIcon = (rank: number) => {
  switch (rank) {
    case 1:
      return <Crown className="h-5 w-5 text-yellow-500" />;
    case 2:
      return <Medal className="h-5 w-5 text-gray-400" />;
    case 3:
      return <Award className="h-5 w-5 text-amber-600" />;
    default:
      return <span className="text-sm font-medium text-muted-foreground">#{rank}</span>;
  }
};

const getRankBadgeColor = (rank: number) => {
  switch (rank) {
    case 1:
      return 'bg-yellow-500';
    case 2:
      return 'bg-gray-400';
    case 3:
      return 'bg-amber-600';
    default:
      return 'bg-muted';
  }
};

export const SkillLeaderboard: React.FC<SkillLeaderboardProps> = ({ limit = 20 }) => {
  const [leaderboard, setLeaderboard] = useState<SkillLeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        setLoading(true);
        const response = await skillApi.getSkillLeaderboard(limit);
        setLeaderboard(response.leaderboard);
      } catch (err) {
        setError('Failed to load leaderboard');
        console.error('Error fetching leaderboard:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, [limit]);

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Trophy className="h-6 w-6 text-primary" />
            <span>Skill Leaderboard</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-center space-x-4 animate-pulse">
                <div className="w-8 h-8 bg-muted rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-muted rounded w-3/4"></div>
                  <div className="h-3 bg-muted rounded w-1/2"></div>
                </div>
                <div className="w-16 h-6 bg-muted rounded"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Trophy className="h-6 w-6 text-primary" />
            <span>Skill Leaderboard</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Trophy className="h-6 w-6 text-primary" />
          <span>Skill Leaderboard</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {leaderboard.map((entry) => (
            <div key={entry.wallet_address} className="flex items-center space-x-4 p-3 rounded-lg hover:bg-muted/50 transition-colors">
              <div className="flex items-center justify-center w-8">
                {getRankIcon(entry.rank)}
              </div>

              <Avatar className="h-10 w-10">
                <AvatarFallback>
                  {entry.username ? entry.username.slice(0, 2).toUpperCase() : entry.wallet_address.slice(0, 2).toUpperCase()}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {entry.username || `${entry.wallet_address.slice(0, 6)}...${entry.wallet_address.slice(-4)}`}
                </p>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="text-xs">
                    {entry.skill_level}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {entry.total_milestones_completed} milestones
                  </span>
                </div>
              </div>

              <div className="text-right">
                <p className="text-lg font-bold">{entry.skill_score.toFixed(1)}</p>
                <p className="text-xs text-muted-foreground">points</p>
              </div>
            </div>
          ))}
        </div>

        {leaderboard.length === 0 && (
          <p className="text-center text-muted-foreground py-8">
            No skill data available yet. Complete some milestones to appear on the leaderboard!
          </p>
        )}
      </CardContent>
    </Card>
  );
};