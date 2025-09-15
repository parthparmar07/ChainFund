import { useState, useEffect } from "react";
import { Search, Filter, Target, Clock, Users, Trophy, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { campaignsApi, skillApi, ApiError, Category, SkillScoreData } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface Campaign {
  id: string;
  title: string;
  description: string;
  goal_amount: number;
  total_backed: number;
  backers: number;
  status: 'active' | 'completed' | 'funded';
  category: string;
  created_at: string;
  end_date: string;
  creator: string;
  image?: string;
}

export default function Campaigns() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedSkillLevel, setSelectedSkillLevel] = useState("all");
  const [creatorSkills, setCreatorSkills] = useState<Record<string, SkillScoreData>>({});

  // Fetch categories
  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: () => campaignsApi.getCategories(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  const categories = categoriesData?.categories || [];

  // Fetch campaigns using TanStack Query
  const {
    data: campaignsResponse,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => campaignsApi.getCampaigns(1, 50), // Get more campaigns for client-side filtering
    retry: 3,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const campaigns = campaignsResponse?.campaigns || [];

  // Fetch skill data for campaign creators
  useEffect(() => {
    const fetchCreatorSkills = async () => {
      const uniqueCreators = [...new Set(campaigns.map(c => c.creator_wallet))];
      const skillPromises = uniqueCreators.map(async (wallet) => {
        try {
          const skillData = await skillApi.getSkillScore(wallet);
          return { wallet, skillData };
        } catch (err) {
          return { wallet, skillData: null };
        }
      });

      const skillResults = await Promise.all(skillPromises);
      const skillMap: Record<string, SkillScoreData> = {};
      skillResults.forEach(({ wallet, skillData }) => {
        if (skillData) {
          skillMap[wallet] = skillData;
        }
      });
      setCreatorSkills(skillMap);
    };

    if (campaigns.length > 0) {
      fetchCreatorSkills();
    }
  }, [campaigns]);

  const filteredCampaigns = campaigns.filter(campaign => {
    const matchesSearch = !searchQuery ||
      campaign.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      campaign.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      campaign.creator_wallet.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesCategory = selectedCategory === "all" ||
      (campaign.category && campaign.category.toLowerCase() === selectedCategory.toLowerCase());

    const matchesSkillLevel = selectedSkillLevel === "all" ||
      (creatorSkills[campaign.creator_wallet] &&
       creatorSkills[campaign.creator_wallet].skill_level.toLowerCase() === selectedSkillLevel.toLowerCase());

    return matchesSearch && matchesCategory && matchesSkillLevel;
  });

  // Show error toast if API fails
  useEffect(() => {
    if (error) {
      toast({
        title: "Error Loading Campaigns",
        description: error instanceof ApiError ? error.message : "Failed to load campaigns",
        variant: "destructive",
      });
    }
  }, [error, toast]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'funded': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'completed': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getProgressPercentage = (raised: number, goal: number) => {
    return Math.min((raised / goal) * 100, 100);
  };

  const getDaysRemaining = (endDate: string) => {
    const today = new Date();
    const end = new Date(endDate);
    const diffTime = end.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="glass rounded-xl p-8">
        <h1 className="text-3xl font-bold gradient-text mb-2">
          Discover Campaigns
        </h1>
        <p className="text-muted-foreground">
          Support innovative projects and help bring ideas to life through blockchain-powered crowdfunding.
        </p>
      </div>

      {/* Filters */}
      <div className="glass rounded-xl p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search campaigns, creators, or keywords..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 glass"
              />
            </div>
          </div>

          <div className="flex gap-2 flex-wrap items-center">
            <Button
              variant={selectedCategory === "all" ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory("all")}
              className="capitalize"
            >
              All ({campaignsResponse?.total || campaigns.length})
            </Button>
            {categories.map((category) => (
              <Button
                key={category.name}
                variant={selectedCategory === category.name ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(category.name)}
                className="capitalize"
                title={category.description}
              >
                {category.name} ({category.count})
              </Button>
            ))}

            <div className="flex items-center gap-2 ml-4 pl-4 border-l">
              <Trophy className="w-4 h-4 text-muted-foreground" />
              <Select value={selectedSkillLevel} onValueChange={setSelectedSkillLevel}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Creator Skill" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Skills</SelectItem>
                  <SelectItem value="novice">
                    <div className="flex items-center gap-2">
                      <Star className="w-4 h-4 text-gray-500" />
                      Novice
                    </div>
                  </SelectItem>
                  <SelectItem value="beginner">
                    <div className="flex items-center gap-2">
                      <Star className="w-4 h-4 text-blue-500" />
                      Beginner
                    </div>
                  </SelectItem>
                  <SelectItem value="intermediate">
                    <div className="flex items-center gap-2">
                      <Star className="w-4 h-4 text-green-500" />
                      Intermediate
                    </div>
                  </SelectItem>
                  <SelectItem value="advanced">
                    <div className="flex items-center gap-2">
                      <Star className="w-4 h-4 text-yellow-500" />
                      Advanced
                    </div>
                  </SelectItem>
                  <SelectItem value="expert">
                    <div className="flex items-center gap-2">
                      <Star className="w-4 h-4 text-red-500" />
                      Expert
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </div>

      {/* Campaign Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="glass">
              <CardHeader>
                <div className="h-4 bg-muted/30 rounded animate-pulse mb-2"></div>
                <div className="h-6 bg-muted/30 rounded animate-pulse mb-2"></div>
                <div className="h-4 bg-muted/30 rounded animate-pulse"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="h-2 bg-muted/30 rounded animate-pulse"></div>
                  <div className="flex justify-between">
                    <div className="h-4 bg-muted/30 rounded animate-pulse w-16"></div>
                    <div className="h-4 bg-muted/30 rounded animate-pulse w-20"></div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCampaigns.map((campaign) => (
            <Card 
              key={campaign.id} 
              className="glass glow-hover cursor-pointer transition-all duration-300 hover:scale-105"
              onClick={() => navigate(`/campaigns/${campaign.id}`)}
            >
              <CardHeader>
                <div className="flex justify-between items-start mb-2">
                  <Badge 
                    variant="outline" 
                    className={`${getStatusColor(campaign.status)} text-xs`}
                  >
                    {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                  </Badge>
                  <Badge variant="secondary" className="text-xs capitalize">
                    {campaign.category}
                  </Badge>
                </div>
                <CardTitle className="text-lg leading-tight">{campaign.title}</CardTitle>
                <p className="text-muted-foreground text-sm line-clamp-2">
                  {campaign.description}
                </p>
                <div className="flex items-center justify-between mt-2">
                  <p className="text-xs text-muted-foreground">
                    by <span className="font-medium">{campaign.creator_wallet.slice(0, 6)}...{campaign.creator_wallet.slice(-4)}</span>
                  </p>
                  {creatorSkills[campaign.creator_wallet] && (
                    <Badge variant="outline" className="text-xs flex items-center gap-1">
                      <Star className="w-3 h-3" />
                      {creatorSkills[campaign.creator_wallet].skill_level}
                    </Badge>
                  )}
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-muted-foreground">Progress</span>
                      <span className="text-primary font-medium">
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
                  
                  <div className="flex justify-between items-center text-sm">
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Users className="w-4 h-4" />
                      <span>{campaign.backers.length} backers</span>
                    </div>
                    
                    {campaign.status === 'active' && (
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Clock className="w-4 h-4" />
                        <span>{getDaysRemaining(campaign.end_date)} days left</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="pt-2">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="w-full"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/campaigns/${campaign.id}`);
                      }}
                    >
                      <Target className="w-4 h-4 mr-2" />
                      View Details
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {filteredCampaigns.length === 0 && (
        <Card className="glass">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Filter className="w-12 h-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Campaigns Found</h3>
            <p className="text-muted-foreground text-center mb-6">
              Try adjusting your search query or filters to find campaigns.
            </p>
            <Button 
              variant="outline" 
              onClick={() => {
                setSearchQuery("");
                setSelectedCategory("all");
              }}
            >
              Clear Filters
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Load More */}
      {filteredCampaigns.length > 0 && (
        <div className="text-center">
          <Button variant="outline" size="lg">
            Load More Campaigns
          </Button>
        </div>
      )}
    </div>
  );
}