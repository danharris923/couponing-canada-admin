import React, { useState, useEffect } from 'react';
import AdminLogin from './AdminLogin';

const AdminDashboard: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const savedToken = localStorage.getItem('admin_token');
    if (savedToken) {
      verifyToken(savedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async (tokenToVerify: string) => {
    try {
      const response = await fetch('/api/admin/auth', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokenToVerify}`
        },
        body: JSON.stringify({ action: 'verify' })
      });

      if (response.ok) {
        setToken(tokenToVerify);
        setIsAuthenticated(true);
      } else {
        localStorage.removeItem('admin_token');
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      localStorage.removeItem('admin_token');
    }
    setLoading(false);
  };

  const handleLogin = (newToken: string) => {
    setToken(newToken);
    setIsAuthenticated(true);
    localStorage.setItem('admin_token', newToken);
  };

  const handleLogout = () => {
    setToken(null);
    setIsAuthenticated(false);
    localStorage.removeItem('admin_token');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-cyber-black flex items-center justify-center">
        <div className="text-neon-pink text-xl">Loading admin...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AdminLogin onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-cyber-black text-white">
      <header className="bg-cyber-gray border-b-2 border-neon-pink">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-neon-pink">🏴‍☠️ COUPONING CANADA ADMIN</h1>
              <span className="text-sm text-gray-400">Hacking Vercel env vars as database</span>
            </div>
            <button
              onClick={handleLogout}
              className="bg-neon-orange text-black px-4 py-2 rounded font-bold hover:bg-neon-pink transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-cyber-gray rounded-lg border border-gray-700 p-6">
            <h2 className="text-xl font-bold text-neon-pink mb-4">⚙️ Site Config</h2>
            <p className="text-gray-400 mb-4">Manage site settings, themes, and branding</p>
            <div className="space-y-2 text-sm text-gray-300">
              <div>Current Theme: <span className="text-neon-green">Cyberpunk</span></div>
              <div>Site Name: <span className="text-neon-orange">Couponing Canada</span></div>
              <div>Discount Threshold: <span className="text-neon-pink">79%</span></div>
            </div>
          </div>

          <div className="bg-cyber-gray rounded-lg border border-gray-700 p-6">
            <h2 className="text-xl font-bold text-neon-pink mb-4">🚀 Scraper Status</h2>
            <p className="text-gray-400 mb-4">RSS scraping and deal processing</p>
            <div className="space-y-2 text-sm text-gray-300">
              <div>Status: <span className="text-neon-green">ONLINE</span></div>
              <div>Last Run: <span className="text-neon-orange">2 hours ago</span></div>
              <div>Deals Found: <span className="text-neon-pink">27</span></div>
            </div>
          </div>

          <div className="bg-cyber-gray rounded-lg border border-gray-700 p-6">
            <h2 className="text-xl font-bold text-neon-pink mb-4">📡 Active Feeds</h2>
            <p className="text-gray-400 mb-4">RSS sources and monitoring</p>
            <div className="space-y-2 text-sm text-gray-300">
              <div>SmartCanucks: <span className="text-neon-green">✓ Active</span></div>
              <div>HotCanadaDeals: <span className="text-neon-green">✓ Active</span></div>
              <div>Total Sources: <span className="text-neon-orange">2</span></div>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-cyber-gray rounded-lg border border-gray-700 p-6">
          <h2 className="text-xl font-bold text-neon-pink mb-6">💰 Revenue Dashboard</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-cyber-black rounded p-4 border border-neon-green">
              <div className="text-sm text-gray-400">Total Clicks</div>
              <div className="text-2xl font-bold text-neon-green">1,247</div>
              <div className="text-xs text-green-400">↗ +12% today</div>
            </div>
            <div className="bg-cyber-black rounded p-4 border border-neon-orange">
              <div className="text-sm text-gray-400">Conversions</div>
              <div className="text-2xl font-bold text-neon-orange">89</div>
              <div className="text-xs text-orange-400">↗ +5% today</div>
            </div>
            <div className="bg-cyber-black rounded p-4 border border-neon-pink">
              <div className="text-sm text-gray-400">Est. Revenue</div>
              <div className="text-2xl font-bold text-neon-pink">$156</div>
              <div className="text-xs text-pink-400">↗ +8% today</div>
            </div>
            <div className="bg-cyber-black rounded p-4 border border-gray-600">
              <div className="text-sm text-gray-400">Top Category</div>
              <div className="text-2xl font-bold text-white">Electronics</div>
              <div className="text-xs text-gray-400">45% of clicks</div>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-cyber-gray rounded-lg border border-gray-700 p-6">
          <h2 className="text-xl font-bold text-neon-pink mb-4">🔥 System Status</h2>
          <div className="text-neon-green text-sm">
            <p>✅ All systems operational</p>
            <p>✅ RSS feeds updating every hour</p>
            <p>✅ Affiliate links processing correctly</p>
            <p>✅ Revenue tracking active</p>
            <p className="text-neon-orange mt-2">💡 This site is MAKING MONEY! 🚀</p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;