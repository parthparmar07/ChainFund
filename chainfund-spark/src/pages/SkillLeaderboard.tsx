import React from 'react';
import { SkillLeaderboard } from '@/components/SkillLeaderboard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Trophy, Award, Medal, Crown } from 'lucide-react';

export default function SkillLeaderboardPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="glass rounded-xl p-8">
        <div className="flex items-center space-x-3 mb-4">
          <Trophy className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold gradient-text">
              Skill Leaderboard
            </h1>
            <p className="text-muted-foreground">
              Top contributors ranked by their skill scores and achievements
            </p>
          </div>
        </div>

        {/* Achievement Tiers */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mt-6">
          <Card className="text-center p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
            <Crown className="h-6 w-6 text-yellow-600 mx-auto mb-2" />
            <h3 className="font-semibold text-yellow-800">Expert</h3>
            <p className="text-xs text-yellow-700">1000+ points</p>
          </Card>

          <Card className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <Award className="h-6 w-6 text-orange-600 mx-auto mb-2" />
            <h3 className="font-semibold text-orange-800">Advanced</h3>
            <p className="text-xs text-orange-700">500-999 points</p>
          </Card>

          <Card className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <Medal className="h-6 w-6 text-green-600 mx-auto mb-2" />
            <h3 className="font-semibold text-green-800">Intermediate</h3>
            <p className="text-xs text-green-700">200-499 points</p>
          </Card>

          <Card className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <Trophy className="h-6 w-6 text-blue-600 mx-auto mb-2" />
            <h3 className="font-semibold text-blue-800">Beginner</h3>
            <p className="text-xs text-blue-700">50-199 points</p>
          </Card>

          <Card className="text-center p-4 bg-gradient-to-br from-gray-50 to-gray-100 border-gray-200">
            <Award className="h-6 w-6 text-gray-600 mx-auto mb-2" />
            <h3 className="font-semibold text-gray-800">Novice</h3>
            <p className="text-xs text-gray-700">0-49 points</p>
          </Card>
        </div>
      </div>

      {/* Leaderboard */}
      <SkillLeaderboard limit={50} />

      {/* How It Works */}
      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Award className="h-5 w-5 text-primary" />
            <span>How Skill Scores Work</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-2">Earning Points</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Complete milestones to earn base points</li>
                <li>• Higher difficulty = more points</li>
                <li>• On-time completion bonus</li>
                <li>• Peer reviews affect final score</li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Skill Levels</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Novice: 0-49 points</li>
                <li>• Beginner: 50-199 points</li>
                <li>• Intermediate: 200-499 points</li>
                <li>• Advanced: 500-999 points</li>
                <li>• Expert: 1000+ points</li>
              </ul>
            </div>
          </div>

          <div className="mt-6 p-4 bg-muted/50 rounded-lg">
            <p className="text-sm text-center">
              <strong>💎 Soulbound NFTs:</strong> Top contributors receive unique skill NFTs that represent their expertise level.
              These NFTs are non-transferable and serve as permanent proof of your contributions to the ChainFund ecosystem.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}