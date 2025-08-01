// Vercel Edge Function - Scraper Management
import jwt from 'jsonwebtoken';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const isAuthed = await verifyAdmin(req);
  if (!isAuthed) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (req.method === 'POST') {
    return await triggerScraper(req, res);
  }
  
  if (req.method === 'GET') {
    return await getScraperStatus(req, res);
  }
  
  return res.status(405).json({ error: 'Method not allowed' });
}

async function verifyAdmin(req) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader?.startsWith('Bearer ')) {
    return false;
  }
  
  const token = authHeader.substring(7);
  const sessionSecret = process.env.ADMIN_SESSION_SECRET || 'default-secret-change-me';
  
  try {
    const decoded = jwt.verify(token, sessionSecret);
    return decoded.admin === true;
  } catch {
    return false;
  }
}

async function triggerScraper(req, res) {
  const { action } = req.body;
  
  if (action === 'run') {
    const githubToken = process.env.GITHUB_TOKEN;
    const repoOwner = process.env.GITHUB_REPO_OWNER;
    const repoName = process.env.GITHUB_REPO_NAME;
    
    if (!githubToken || !repoOwner || !repoName) {
      return res.status(500).json({ 
        error: 'GitHub integration not configured',
        message: 'Set GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME env vars'
      });
    }
    
    try {
      const response = await fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/dispatches`, {
        method: 'POST',
        headers: {
          'Authorization': `token ${githubToken}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          event_type: 'run-scraper',
          client_payload: {
            triggered_by: 'admin-dashboard',
            timestamp: new Date().toISOString()
          }
        })
      });
      
      if (response.ok) {
        return res.status(200).json({ 
          success: true, 
          message: 'Scraper triggered successfully',
          workflow: 'GitHub Action dispatched'
        });
      } else {
        const error = await response.text();
        return res.status(500).json({ 
          error: 'Failed to trigger scraper',
          details: error
        });
      }
    } catch (error) {
      return res.status(500).json({ 
        error: 'GitHub API error',
        message: error.message
      });
    }
  }
  
  return res.status(400).json({ error: 'Invalid action' });
}

async function getScraperStatus(req, res) {
  const status = {
    enabled: process.env.ADMIN_SCRAPER_ENABLED === 'true',
    lastRun: process.env.ADMIN_LAST_SCRAPER_RUN || 'Never',
    lastStatus: process.env.ADMIN_LAST_SCRAPER_STATUS || 'Unknown',
    feedCount: JSON.parse(process.env.ADMIN_FEEDS || '[]').length,
    dealsGenerated: parseInt(process.env.ADMIN_LAST_DEALS_COUNT) || 0,
    config: {
      discountThreshold: parseInt(process.env.ADMIN_DISCOUNT_THRESHOLD) || 79,
      amazonTag: process.env.ADMIN_AMAZON_TAG || 'Not set'
    }
  };
  
  return res.status(200).json({ status });
}