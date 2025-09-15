import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  ArrowLeft, 
  Share2, 
  Heart, 
  Flag, 
  DollarSign, 
  Users, 
  Calendar,
  CheckCircle,
  Clock,
  Target
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { useWalletStore } from "@/stores/walletStore";
import { useQuery } from "@tanstack/react-query";
import { campaignsApi, Campaign, ApiError } from "@/services/api";

export default function CampaignDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { isConnected, isAuthenticated } = useWalletStore();
  
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [fundingAmount, setFundingAmount] = useState("");
  const [activeTab, setActiveTab] = useState("overview");

  // Mock data - replace with actual API call
  useEffect(() => {
    const mockCampaign: Campaign = {
      id: id || '1',
      title: 'AI-Powered Health Monitor',
      description: `Revolutionary wearable device for continuous health monitoring using advanced AI algorithms. 

Our mission is to democratize healthcare by making continuous health monitoring accessible to everyone. This innovative device combines cutting-edge AI technology with affordable hardware to provide real-time health insights.

Key Features:
• 24/7 continuous monitoring of vital signs
• AI-powered anomaly detection
• Smartphone integration with intuitive app
• Long-lasting battery (7+ days)
• Waterproof and comfortable design
• FDA-approved sensors

The funding will be used to:
1. Complete prototype development and testing
2. Obtain necessary medical certifications
3. Set up manufacturing partnerships
4. Launch marketing and distribution channels

Join us in revolutionizing healthcare technology and making health monitoring accessible to millions worldwide.`,
      goal_amount: 50000,
      total_backed: 32500,
      backers: [],
      status: 'active',
      category: 'health',
      created_at: '2024-01-15',
      updated_at: '2024-01-15',
      end_date: '2024-12-31',
      creator_wallet: 'TechVision Labs',
      milestones: [
        {
          id: '1',
          title: 'Prototype Development',
          description: 'Complete the initial prototype with basic monitoring features',
          amount: 15000,
          status: 'completed',
          votes_for: 45,
          votes_against: 3,
          total_votes: 48,
        },
        {
          id: '2',
          title: 'AI Algorithm Training',
          description: 'Train and optimize AI models for accurate health predictions',
          amount: 20000,
          status: 'active',
          votes_for: 0,
          votes_against: 0,
          total_votes: 0,
        },
        {
          id: '3',
          title: 'Certification & Testing',
          description: 'Obtain FDA approval and conduct comprehensive testing',
          amount: 15000,
          status: 'pending',
          votes_for: 0,
          votes_against: 0,
          total_votes: 0,
        },
      ],
    };

    setCampaign(mockCampaign);
  }, [id]);

  const handleFunding = async () => {
    if (!isConnected || !isAuthenticated) {
      toast({
        title: "Connect Wallet",
        description: "Please connect your wallet to fund this campaign.",
        variant: "destructive",
      });
      return;
    }

    if (!fundingAmount || parseFloat(fundingAmount) <= 0) {
      toast({
        title: "Invalid Amount",
        description: "Please enter a valid funding amount.",
        variant: "destructive",
      });
      return;
    }

    try {
      // Call API to process funding
      await campaignsApi.fundCampaign({
        amount: parseFloat(fundingAmount),
        campaign_id: id || '',
      });

      toast({
        title: "Funding Successful!",
        description: `You've successfully funded $${fundingAmount} to this campaign.`,
      });

      setFundingAmount("");
    } catch (error) {
      console.error('Funding failed:', error);
      toast({
        title: "Funding Failed",
        description: error instanceof ApiError ? error.message : "There was an error processing your funding. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleVote = async (milestoneId: string, vote: 'for' | 'against') => {
    if (!isAuthenticated) {
      toast({
        title: "Login Required",
        description: "You must be logged in to vote on milestones.",
        variant: "destructive",
      });
      return;
    }

    try {
      // Call API to submit vote
      await campaignsApi.voteOnMilestone({
        milestone_id: milestoneId,
        vote,
      });

      toast({
        title: "Vote Submitted",
        description: `Your vote has been recorded for this milestone.`,
      });
    } catch (error) {
      console.error('Vote failed:', error);
      toast({
        title: "Vote Failed",
        description: error instanceof ApiError ? error.message : "There was an error submitting your vote.",
        variant: "destructive",
      });
    }
  };

  if (!campaign) {
    return <div>Loading...</div>;
  }

  const progressPercentage = (campaign.total_backed / campaign.goal_amount) * 100;
  const daysRemaining = Math.ceil(
    (new Date(campaign.end_date || '').getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
  );

  const getMilestoneStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'active': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'pending': return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => navigate("/campaigns")}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Campaigns
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Campaign Header */}
          <Card className="glass">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant="outline" 
                      className={getMilestoneStatusColor(campaign.status)}
                    >
                      {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                    </Badge>
                    <Badge variant="secondary" className="capitalize">
                      {campaign.category}
                    </Badge>
                  </div>
                  <CardTitle className="text-2xl">{campaign.title}</CardTitle>
                  <p className="text-muted-foreground">by {campaign.creator_wallet}</p>
                </div>
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm">
                    <Heart className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Share2 className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Flag className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Tabs */}
          <Card className="glass">
            <CardHeader>
              <div className="flex gap-4">
                {['overview', 'milestones', 'backers'].map((tab) => (
                  <Button
                    key={tab}
                    variant={activeTab === tab ? "default" : "ghost"}
                    size="sm"
                    onClick={() => setActiveTab(tab)}
                    className="capitalize"
                  >
                    {tab}
                  </Button>
                ))}
              </div>
            </CardHeader>
            <CardContent>
              {activeTab === 'overview' && (
                <div className="prose prose-invert max-w-none">
                  <div className="whitespace-pre-line text-foreground">
                    {campaign.description}
                  </div>
                </div>
              )}

              {activeTab === 'milestones' && (
                <div className="space-y-4">
                  {campaign.milestones.map((milestone, index) => (
                    <Card key={milestone.id} className="glass-strong">
                      <CardHeader>
                        <div className="flex justify-between items-start">
                          <div>
                            <CardTitle className="text-lg flex items-center gap-2">
                              {milestone.status === 'completed' && (
                                <CheckCircle className="w-5 h-5 text-green-400" />
                              )}
                              {milestone.status === 'active' && (
                                <Clock className="w-5 h-5 text-blue-400" />
                              )}
                              {milestone.status === 'pending' && (
                                <Target className="w-5 h-5 text-gray-400" />
                              )}
                              Milestone {index + 1}: {milestone.title}
                            </CardTitle>
                            <p className="text-muted-foreground">{milestone.description}</p>
                          </div>
                          <div className="text-right">
                            <Badge 
                              variant="outline" 
                              className={getMilestoneStatusColor(milestone.status)}
                            >
                              {milestone.status}
                            </Badge>
                            <div className="text-lg font-semibold text-primary mt-1">
                              ${milestone.amount.toLocaleString()}
                            </div>
                          </div>
                        </div>
                      </CardHeader>
                      
                      {milestone.status === 'active' && (
                        <CardContent>
                          <div className="space-y-4">
                            <div>
                              <div className="flex justify-between text-sm mb-2">
                                <span>Voting Progress</span>
                                <span>{milestone.total_votes} votes</span>
                              </div>
                              <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                  <span className="text-green-400">For: {milestone.votes_for}</span>
                                  <span className="text-red-400">Against: {milestone.votes_against}</span>
                                </div>
                                <Progress 
                                  value={milestone.total_votes > 0 ? (milestone.votes_for / milestone.total_votes) * 100 : 0} 
                                  className="h-2"
                                />
                              </div>
                            </div>
                            
                            <div className="flex gap-2">
                              <Button 
                                variant="outline" 
                                size="sm" 
                                onClick={() => handleVote(milestone.id, 'for')}
                                className="flex-1"
                              >
                                Vote Approve
                              </Button>
                              <Button 
                                variant="outline" 
                                size="sm" 
                                onClick={() => handleVote(milestone.id, 'against')}
                                className="flex-1"
                              >
                                Vote Reject
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      )}
                    </Card>
                  ))}
                </div>
              )}

              {activeTab === 'backers' && (
                <div className="space-y-4">
                  <p className="text-muted-foreground">
                    {campaign.backers.length} people have backed this campaign
                  </p>
                  
                  {/* Mock backers list */}
                  <div className="space-y-3">
                    {[
                      { name: "Alice Johnson", amount: 500, message: "Great project! Can't wait to see the results." },
                      { name: "Bob Smith", amount: 250, message: "This will revolutionize healthcare." },
                      { name: "Carol Davis", amount: 1000, message: "Excited to support this innovation!" },
                    ].map((backer, index) => (
                      <div key={index} className="p-4 bg-muted/20 rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium">{backer.name}</span>
                          <span className="text-primary font-semibold">${backer.amount}</span>
                        </div>
                        <p className="text-sm text-muted-foreground">{backer.message}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Funding Card */}
          <Card className="glass sticky top-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="w-5 h-5" />
                Fund This Campaign
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Progress */}
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Progress</span>
                  <span className="font-medium">{progressPercentage.toFixed(1)}%</span>
                </div>
                <Progress value={progressPercentage} className="h-3" />
                <div className="flex justify-between">
                  <span className="text-2xl font-bold text-primary">
                    ${campaign.total_backed.toLocaleString()}
                  </span>
                  <span className="text-muted-foreground">
                    of ${campaign.goal_amount.toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-secondary">{campaign.backers.length}</div>
                  <div className="text-sm text-muted-foreground">Backers</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-accent">{daysRemaining}</div>
                  <div className="text-sm text-muted-foreground">Days Left</div>
                </div>
              </div>

              {/* Funding Input */}
              <div className="space-y-3">
                <Input
                  type="number"
                  placeholder="Enter amount (USD)"
                  value={fundingAmount}
                  onChange={(e) => setFundingAmount(e.target.value)}
                  className="glass"
                />
                <Button 
                  variant="hero" 
                  size="lg" 
                  onClick={handleFunding}
                  className="w-full glow-hover"
                  disabled={!isConnected || !fundingAmount}
                >
                  {!isConnected ? "Connect Wallet First" : "Fund Campaign"}
                </Button>
              </div>

              <div className="text-xs text-muted-foreground text-center">
                Funds are released based on milestone completion and community voting.
              </div>
            </CardContent>
          </Card>

          {/* Creator Info */}
          <Card className="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Creator
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-gradient-primary rounded-full flex items-center justify-center">
                  <span className="text-white font-bold">T</span>
                </div>
                <div>
                  <div className="font-semibold">{campaign.creator_wallet}</div>
                  <div className="text-sm text-muted-foreground">
                    Healthcare Innovation Company
                  </div>
                </div>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Leading healthcare technology company focused on making health monitoring accessible worldwide.
              </p>
              <Button variant="outline" size="sm" className="w-full">
                View Profile
              </Button>
            </CardContent>
          </Card>

          {/* Campaign Info */}
          <Card className="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Campaign Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Created</span>
                <span>{new Date(campaign.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">End Date</span>
                <span>{new Date(campaign.end_date || '').toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Category</span>
                <span className="capitalize">{campaign.category}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Milestones</span>
                <span>{campaign.milestones.length}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}