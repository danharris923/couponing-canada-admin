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
              <h1 className="text-2xl font-bold text-neon-pink">🏴‍☠️ ADMIN DASHBOARD</h1>
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
            <button className="bg-neon-pink text-white px-4 py-2 rounded font-bold hover:bg-neon-orange transition-colors">
              Configure Site
            </button>
          </div>

          <div className="bg-cyber-gray rounded-lg border border-gray-700 p-6">
            <h2 className="text-xl font-bold text-neon-pink mb-4">🚀 Scraper Control</h2>
            <p className="text-gray-400 mb-4">Trigger RSS scraping and monitor status</p>
            <button className="bg-neon-orange text-black px-4 py-2 rounded font-bold hover:bg-neon-pink transition-colors">
              Run Scraper
            </button>
          </div>

          <div className="bg-cyber-gray rounded-lg border border-gray-700 p-6">
            <h2 className="text-xl font-bold text-neon-pink mb-4">📡 Feed Manager</h2>
            <p className="text-gray-400 mb-4">Add/remove RSS feeds and sources</p>
            <button className="bg-neon-green text-black px-4 py-2 rounded font-bold hover:bg-neon-pink transition-colors">
              Manage Feeds
            </button>
          </div>
        </div>

        <div className="mt-8 bg-cyber-gray rounded-lg border border-gray-700 p-6">
          <h2 className="text-xl font-bold text-neon-pink mb-4">📊 System Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-cyber-black rounded p-4">
              <div className="text-sm text-gray-400">Active Feeds</div>
              <div className="text-2xl font-bold text-neon-green">2</div>
            </div>
            <div className="bg-cyber-black rounded p-4">
              <div className="text-sm text-gray-400">Total Deals</div>
              <div className="text-2xl font-bold text-neon-orange">27</div>
            </div>
            <div className="bg-cyber-black rounded p-4">
              <div className="text-sm text-gray-400">Last Scrape</div>
              <div className="text-2xl font-bold text-neon-pink">2h ago</div>
            </div>
            <div className="bg-cyber-black rounded p-4">
              <div className="text-sm text-gray-400">Status</div>
              <div className="text-2xl font-bold text-neon-green">ONLINE</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;