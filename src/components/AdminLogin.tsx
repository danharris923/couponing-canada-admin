import React, { useState } from 'react';

interface AdminLoginProps {
  onLogin: (token: string) => void;
}

const AdminLogin: React.FC<AdminLoginProps> = ({ onLogin }) => {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/admin/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'login', password })
      });

      const data = await response.json();
      if (response.ok && data.success) {
        onLogin(data.token);
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (error) {
      setError('Network error - check if admin API is deployed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cyber-black flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-cyber-gray rounded-lg border-2 border-neon-pink p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-neon-pink mb-2">🏴‍☠️ ADMIN ACCESS</h1>
          <p className="text-gray-400 text-sm">Hacking Vercel env vars as database</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Access Code
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-cyber-black border border-gray-600 rounded px-3 py-2 text-white focus:border-neon-pink"
              placeholder="Enter admin password"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              First time? Try: <code className="text-neon-green">admin123</code>
            </p>
          </div>

          {error && (
            <div className="bg-red-900/20 border border-red-500 rounded px-4 py-3 text-red-300 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-neon-pink text-white py-3 rounded font-bold hover:bg-neon-orange transition-colors disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : 'HACK THE PLANET'}
          </button>
        </form>

        <div className="mt-6 bg-yellow-900/20 border border-yellow-500 rounded p-3">
          <p className="text-yellow-300 text-xs">
            🚧 <strong>HACKER MODE:</strong> Using Vercel env vars as backend database!
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;