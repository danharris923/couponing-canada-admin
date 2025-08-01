// Vercel Edge Function - Admin Authentication
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method === 'POST') {
    try {
      const { password, action } = req.body;
      
      if (action === 'login') {
        return await handleLogin(req, res, password);
      }
      
      if (action === 'verify') {
        return await handleVerify(req, res);
      }
      
      return res.status(400).json({ error: 'Invalid action' });
    } catch (error) {
      console.error('Auth error:', error);
      return res.status(500).json({ error: 'Authentication failed' });
    }
  }
  
  return res.status(405).json({ error: 'Method not allowed' });
}

async function handleLogin(req, res, password) {
  const storedHash = process.env.ADMIN_PASSWORD_HASH;
  const sessionSecret = process.env.ADMIN_SESSION_SECRET || 'default-secret-change-me';
  
  // First-time setup - create admin password if not exists  
  if (!storedHash) {
    if (password === 'admin123') {
      const token = jwt.sign(
        { admin: true, setup: true }, 
        sessionSecret, 
        { expiresIn: '24h' }
      );
      
      return res.status(200).json({ 
        success: true, 
        token,
        message: 'First-time setup - please change default password',
        setup: true
      });
    } else {
      return res.status(401).json({ error: 'Use default password: admin123' });
    }
  }
  
  const isValid = await bcrypt.compare(password, storedHash);
  
  if (!isValid) {
    return res.status(401).json({ error: 'Invalid password' });
  }
  
  const token = jwt.sign(
    { admin: true }, 
    sessionSecret, 
    { expiresIn: '24h' }
  );
  
  return res.status(200).json({ 
    success: true, 
    token,
    message: 'Login successful'
  });
}

async function handleVerify(req, res) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  const token = authHeader.substring(7);
  const sessionSecret = process.env.ADMIN_SESSION_SECRET || 'default-secret-change-me';
  
  try {
    const decoded = jwt.verify(token, sessionSecret);
    
    if (!decoded.admin) {
      return res.status(401).json({ error: 'Invalid token' });
    }
    
    return res.status(200).json({ 
      success: true, 
      admin: true,
      setup: decoded.setup || false
    });
  } catch (error) {
    return res.status(401).json({ error: 'Token expired or invalid' });
  }
}