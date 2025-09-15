import { Wallet, LogOut, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { useWalletStore } from "@/stores/walletStore";
import { useToast } from "@/hooks/use-toast";

export function Header() {
  const { 
    isConnected, 
    walletAddress, 
    isAuthenticated, 
    user,
    isConnecting,
    connectWallet, 
    disconnectWallet 
  } = useWalletStore();
  const { toast } = useToast();

  const handleConnectWallet = async () => {
    try {
      await connectWallet();
      toast({
        title: "Wallet Connected",
        description: "MetaMask wallet connected successfully!",
      });
    } catch (error) {
      toast({
        title: "Connection Failed",
        description: "Failed to connect wallet. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleDisconnect = () => {
    disconnectWallet();
    toast({
      title: "Disconnected",
      description: "Wallet disconnected successfully.",
    });
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  return (
    <header className="glass border-b border-glass-border/20 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {isAuthenticated && <SidebarTrigger />}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">C</span>
            </div>
            <h1 className="text-xl font-bold gradient-text">ChainFund</h1>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {isAuthenticated && user && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <User className="w-4 h-4" />
              <span>{user.username}</span>
            </div>
          )}
          
          {isConnected && walletAddress ? (
            <div className="flex items-center gap-2">
              <div className="px-3 py-1 glass rounded-lg text-sm">
                {formatAddress(walletAddress)}
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDisconnect}
              >
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          ) : (
            <Button 
              variant="wallet" 
              onClick={handleConnectWallet}
              disabled={isConnecting}
            >
              <Wallet className="w-4 h-4" />
              {isConnecting ? "Connecting..." : "Connect Wallet"}
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}