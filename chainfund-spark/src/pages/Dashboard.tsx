import { useState, useEffect } from "react";
import { Plus, TrendingUp, Target, Clock, DollarSign } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useWalletStore } from "@/stores/walletStore";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { campaignsApi, skillApi, Campaign, SkillScoreData, ApiError } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import { SkillScoreCard } from "@/components/SkillScoreCard";
import { SkillAchievements } from "@/components/SkillAchievements";

export default function Dashboard() {
  const { user } = useWalletStore();
  const navigate = useNavigate();
  const { toast } = useToast();

  // Fetch user's skill data
  const { data: skillData, isLoading: skillLoading } = useQuery({
    queryKey: ['user-skill', user?.walletAddress],
    queryFn: async () => {
      if (!user?.walletAddress) return null;
      try {
        return await skillApi.getSkillScore(user.walletAddress);
      } catch (err) {
        console.log('Skill data not available yet:', err);
        return null;
      }
    },
    enabled: !!user?.walletAddress,
  });

  // Fetch user's campaigns
  const { data: campaigns = [], isLoading: campaignsLoading, error } = useQuery({
    queryKey: ['user-campaigns', user?.walletAddress],
    queryFn: async () => {
      if (!user?.walletAddress) return [];
      try {
        const response = await campaignsApi.getCampaigns();
        // Filter campaigns created by the current user
        return response.campaigns.filter((campaign: Campaign) => campaign.creator_wallet === user.walletAddress);
      } catch (err) {
        const apiError = err as ApiError;
        toast({
          title: "Error loading campaigns",
          description: apiError.message || "Failed to load your campaigns",
          variant: "destructive",
        });
        return [];
      }
    },
    enabled: !!user?.walletAddress,
  });

  // Calculate stats from campaigns data
  const stats = {
    totalCampaigns: campaigns.length,
    totalRaised: campaigns.reduce((sum, campaign) => sum + campaign.total_backed, 0),
    totalBackers: campaigns.reduce((sum, campaign) => sum + campaign.backers.length, 0),
    successRate: campaigns.length > 0 
      ? Math.round((campaigns.filter(c => c.total_backed >= c.goal_amount).length / campaigns.length) * 100)
      : 0,
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-blue-400';
      case 'funded': return 'text-green-400';
      case 'completed': return 'text-purple-400';
      default: return 'text-gray-400';
    }
  };

  const getProgressPercentage = (raised: number, goal: number) => {
    return Math.min((raised / goal) * 100, 100);
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="glass rounded-xl p-8">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold gradient-text mb-2">
              Welcome back, {user?.username || user?.walletAddress?.slice(0, 6) + '...' + user?.walletAddress?.slice(-4) || 'User'}!
            </h1>
            <p className="text-muted-foreground">
              Manage your campaigns and track your fundraising progress.
            </p>
          </div>
          <Button 
            variant="hero" 
            onClick={() => navigate("/create")}
            className="glow-hover"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Campaign
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="glass glow-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Campaigns
            </CardTitle>
            <Target className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">{stats.totalCampaigns}</div>
          </CardContent>
        </Card>

        <Card className="glass glow-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Raised
            </CardTitle>
            <DollarSign className="h-4 w-4 text-secondary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-secondary">
              ${stats.totalRaised.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        <Card className="glass glow-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Backers
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-accent" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-accent">{stats.totalBackers}</div>
          </CardContent>
        </Card>

        <Card className="glass glow-hover">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Success Rate
            </CardTitle>
            <Clock className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">{stats.successRate}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Skill Section */}
      {skillData && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <SkillScoreCard skillData={skillData} />
          </div>
          <div className="lg:col-span-2">
            <SkillAchievements skillData={skillData} />
          </div>
        </div>
      )}

      {/* My Campaigns */}
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">My Campaigns</h2>
          <Button 
            variant="outline" 
            onClick={() => navigate("/my-campaigns")}
          >
            View All
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {campaignsLoading ? (
            // Loading skeleton
            Array.from({ length: 2 }).map((_, index) => (
              <Card key={index} className="glass">
                <CardHeader>
                  <div className="animate-pulse">
                    <div className="h-6 bg-muted/30 rounded mb-2"></div>
                    <div className="h-4 bg-muted/30 rounded w-3/4"></div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="animate-pulse space-y-4">
                    <div className="h-4 bg-muted/30 rounded"></div>
                    <div className="h-2 bg-muted/30 rounded-full"></div>
                    <div className="h-4 bg-muted/30 rounded w-1/2"></div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : campaigns.length > 0 ? (
            campaigns.map((campaign) => (
              <Card 
                key={campaign.id} 
                className="glass glow-hover cursor-pointer transition-all duration-300"
                onClick={() => navigate(`/campaigns/${campaign.id}`)}
              >
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{campaign.title}</CardTitle>
                    <span className={`text-sm font-medium ${getStatusColor(campaign.status)}`}>
                      {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                    </span>
                  </div>
                  <p className="text-muted-foreground text-sm">
                    {campaign.description}
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-muted-foreground">Progress</span>
                        <span className="text-primary">
                          ${campaign.total_backed.toLocaleString()} / ${campaign.goal_amount.toLocaleString()}
                        </span>
                      </div>
                      <div className="w-full bg-muted/30 rounded-full h-2">
                        <div 
                          className="bg-gradient-primary h-2 rounded-full transition-all duration-500"
                          style={{ width: `${getProgressPercentage(campaign.total_backed, campaign.goal_amount)}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <div className="flex justify-between text-sm text-muted-foreground">
                      <span>{campaign.backers.length} backers</span>
                      <span>{getProgressPercentage(campaign.total_backed, campaign.goal_amount).toFixed(1)}% funded</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card className="glass lg:col-span-2">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Target className="w-12 h-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Campaigns Yet</h3>
                <p className="text-muted-foreground text-center mb-6">
                  Create your first campaign to start raising funds for your project.
                </p>
                <Button variant="hero" onClick={() => navigate("/create")}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Campaign
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Recent Activity</h2>
        <Card className="glass">
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex items-center gap-4 p-4 bg-muted/20 rounded-lg">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm">
                    <span className="font-medium">John Doe</span> backed your campaign 
                    <span className="font-medium"> "AI-Powered Health Monitor"</span> with $250
                  </p>
                  <p className="text-xs text-muted-foreground">2 hours ago</p>
                </div>
              </div>
              
              <div className="flex items-center gap-4 p-4 bg-muted/20 rounded-lg">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm">
                    Milestone <span className="font-medium">"Prototype Development"</span> was approved by voters
                  </p>
                  <p className="text-xs text-muted-foreground">1 day ago</p>
                </div>
              </div>
              
              <div className="flex items-center gap-4 p-4 bg-muted/20 rounded-lg">
                <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm">
                    Campaign <span className="font-medium">"Sustainable Water Purification"</span> reached funding goal
                  </p>
                  <p className="text-xs text-muted-foreground">3 days ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}