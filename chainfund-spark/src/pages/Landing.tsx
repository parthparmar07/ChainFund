import { ArrowRight, TrendingUp, Users, Target, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useWalletStore } from "@/stores/walletStore";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import heroImage from "@/assets/hero-bg.jpg";

export default function Landing() {
  const { isConnected, connectWallet, isConnecting } = useWalletStore();
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleConnectWallet = async () => {
    try {
      await connectWallet();
      toast({
        title: "Wallet Connected",
        description: "Welcome to ChainFund! Redirecting to dashboard...",
      });
      setTimeout(() => navigate("/dashboard"), 1500);
    } catch (error) {
      toast({
        title: "Connection Failed",
        description: "Please install MetaMask and try again.",
        variant: "destructive",
      });
    }
  };

  const stats = [
    { label: "Total Campaigns", value: "2,847", icon: Target },
    { label: "Total Funded", value: "$12.4M", icon: TrendingUp },
    { label: "Active Users", value: "15,234", icon: Users },
    { label: "Success Rate", value: "89%", icon: Zap },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section 
        className="relative min-h-[80vh] flex items-center justify-center overflow-hidden"
        style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)), url(${heroImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="absolute inset-0 bg-gradient-primary opacity-20"></div>
        
        <div className="relative z-10 text-center max-w-4xl mx-auto px-6">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-fade-in">
            <span className="gradient-text">ChainFund</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-8 animate-fade-in">
            The Next Generation of Blockchain-Powered Crowdfunding
          </p>
          <p className="text-lg text-gray-400 mb-12 max-w-2xl mx-auto animate-fade-in">
            Launch campaigns, raise funds, and build the future with complete transparency, 
            milestone-based funding, and community governance powered by Web3 technology.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in">
            {!isConnected ? (
              <Button 
                variant="hero" 
                size="lg" 
                onClick={handleConnectWallet}
                disabled={isConnecting}
                className="text-lg px-8 py-6"
              >
                {isConnecting ? "Connecting..." : "Connect Wallet & Start"}
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            ) : (
              <Button 
                variant="hero" 
                size="lg" 
                onClick={() => navigate("/dashboard")}
                className="text-lg px-8 py-6"
              >
                Go to Dashboard
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            )}
            
            <Button 
              variant="outline" 
              size="lg" 
              onClick={() => navigate("/campaigns")}
              className="text-lg px-8 py-6"
            >
              Browse Campaigns
            </Button>
          </div>
        </div>

        {/* Floating animations */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-primary/20 rounded-full animate-float"></div>
        <div className="absolute bottom-32 right-16 w-16 h-16 bg-secondary/20 rounded-full animate-float" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/4 w-12 h-12 bg-accent/20 rounded-full animate-float" style={{ animationDelay: '2s' }}></div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 gradient-text">
            Platform Statistics
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <Card key={stat.label} className="glass glow-hover animate-fade-in" style={{ animationDelay: `${index * 0.1}s` }}>
                <CardContent className="p-6 text-center">
                  <stat.icon className="w-8 h-8 mx-auto mb-4 text-primary" />
                  <div className="text-3xl font-bold text-primary mb-2">{stat.value}</div>
                  <div className="text-muted-foreground">{stat.label}</div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-muted/20">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4 gradient-text">
            Why Choose ChainFund?
          </h2>
          <p className="text-center text-muted-foreground mb-12 max-w-2xl mx-auto">
            Experience the future of crowdfunding with blockchain transparency, 
            smart contract security, and community-driven governance.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="glass glow-hover">
              <CardContent className="p-8 text-center">
                <div className="w-16 h-16 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-6">
                  <Target className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Milestone-Based Funding</h3>
                <p className="text-muted-foreground">
                  Funds are released based on project milestones, ensuring accountability 
                  and reducing risk for both creators and backers.
                </p>
              </CardContent>
            </Card>

            <Card className="glass glow-hover">
              <CardContent className="p-8 text-center">
                <div className="w-16 h-16 bg-gradient-secondary rounded-full flex items-center justify-center mx-auto mb-6">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Blockchain Transparency</h3>
                <p className="text-muted-foreground">
                  Every transaction is recorded on the blockchain, providing complete 
                  transparency and immutable proof of fund allocation.
                </p>
              </CardContent>
            </Card>

            <Card className="glass glow-hover">
              <CardContent className="p-8 text-center">
                <div className="w-16 h-16 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-6">
                  <Users className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Community Governance</h3>
                <p className="text-muted-foreground">
                  Backers vote on milestone completion, ensuring democratic decision-making 
                  and project success through community involvement.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6 gradient-text">
            Ready to Launch Your Project?
          </h2>
          <p className="text-xl text-muted-foreground mb-8">
            Join thousands of creators who are building the future with blockchain technology.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              variant="gradient" 
              size="lg" 
              onClick={() => navigate("/create")}
              className="text-lg px-8 py-6"
            >
              Start a Campaign
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            
            <Button 
              variant="outline" 
              size="lg" 
              onClick={() => navigate("/campaigns")}
              className="text-lg px-8 py-6"
            >
              Explore Projects
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}