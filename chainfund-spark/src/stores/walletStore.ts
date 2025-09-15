import { create } from 'zustand';
import { ethers, BrowserProvider, Signer } from 'ethers';
import { authApi, AuthRequest, AuthResponse, User, ApiError } from '@/services/api';

// Extend Window interface for MetaMask
declare global {
  interface Window {
    ethereum?: any;
  }
}

interface WalletUser {
  id: string;
  username: string;
  email: string;
  walletAddress: string;
}

interface WalletState {
  // Wallet connection
  isConnected: boolean;
  walletAddress: string | null;
  provider: BrowserProvider | null;
  signer: Signer | null;
  
  // User authentication
  user: WalletUser | null;
  isAuthenticated: boolean;
  token: string | null;
  
  // Loading states
  isConnecting: boolean;
  isLoggingIn: boolean;
  
  // Actions
  connectWallet: () => Promise<void>;
  disconnectWallet: () => void;
  login: (signature: string) => Promise<void>;
  logout: () => void;
  setUser: (user: WalletUser) => void;
}

export const useWalletStore = create<WalletState>((set, get) => ({
  // Initial state
  isConnected: false,
  walletAddress: null,
  provider: null,
  signer: null,
  user: null,
  isAuthenticated: false,
  token: null,
  isConnecting: false,
  isLoggingIn: false,

  // Connect wallet action
  connectWallet: async () => {
    try {
      set({ isConnecting: true });
      
      if (!window.ethereum) {
        throw new Error('MetaMask not installed');
      }

      const provider = new BrowserProvider(window.ethereum);
      await provider.send('eth_requestAccounts', []);
      
      const signer = await provider.getSigner();
      const address = await signer.getAddress();

      set({
        isConnected: true,
        walletAddress: address,
        provider,
        signer,
        isConnecting: false,
      });

      // Store connection in localStorage
      localStorage.setItem('wallet_connected', 'true');
      localStorage.setItem('wallet_address', address);
      
    } catch (error) {
      console.error('Failed to connect wallet:', error);
      set({ isConnecting: false });
      throw error;
    }
  },

  // Disconnect wallet action
  disconnectWallet: () => {
    set({
      isConnected: false,
      walletAddress: null,
      provider: null,
      signer: null,
      user: null,
      isAuthenticated: false,
      token: null,
    });
    
    // Clear localStorage
    localStorage.removeItem('wallet_connected');
    localStorage.removeItem('wallet_address');
    localStorage.removeItem('auth_token');
  },

  // Login action (after wallet connected)
  login: async (signature: string) => {
    try {
      set({ isLoggingIn: true });
      
      const { walletAddress } = get();
      if (!walletAddress) throw new Error('Wallet not connected');

      // Create authentication message
      const message = `Sign this message to authenticate with ChainFund: ${Date.now()}`;
      
      // Call backend authentication endpoint
      const authRequest: AuthRequest = {
        wallet_address: walletAddress,
        signature,
        message,
      };

      const authResponse: AuthResponse = await authApi.authenticate(authRequest);
      
      set({
        isAuthenticated: true,
        token: authResponse.access_token,
        user: {
          id: authResponse.user.id,
          username: authResponse.user.username || '',
          email: authResponse.user.email || '',
          walletAddress: authResponse.user.wallet_address,
        },
        isLoggingIn: false,
      });

      // Store token
      localStorage.setItem('auth_token', authResponse.access_token);
      
    } catch (error) {
      console.error('Login failed:', error);
      set({ isLoggingIn: false });
      
      if (error instanceof ApiError) {
        throw new Error(error.message);
      }
      throw error;
    }
  },

  // Logout action
  logout: () => {
    set({
      user: null,
      isAuthenticated: false,
      token: null,
    });
    
    localStorage.removeItem('auth_token');
  },

  // Set user action
  setUser: (user: WalletUser) => {
    set({ user });
  },
}));

// Auto-reconnect wallet on page load
if (typeof window !== 'undefined') {
  const wasConnected = localStorage.getItem('wallet_connected');
  const savedToken = localStorage.getItem('auth_token');
  
  if (wasConnected === 'true' && window.ethereum) {
    // Try to reconnect wallet
    useWalletStore.getState().connectWallet().catch(console.error);
  }
  
  if (savedToken) {
    // Restore token (you might want to validate it with backend)
    useWalletStore.setState({ token: savedToken });
  }
}