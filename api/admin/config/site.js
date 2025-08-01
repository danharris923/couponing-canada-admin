// Vercel Edge Function - Site Configuration Management
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

  if (req.method === 'GET') {
    return await getSiteConfig(req, res);
  }
  
  if (req.method === 'POST') {
    return await updateSiteConfig(req, res);
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

async function getSiteConfig(req, res) {
  const config = {
    siteName: process.env.ADMIN_SITE_NAME || 'Smart Deals Canada',
    tagline: process.env.ADMIN_TAGLINE || 'Canadian Deals & Savings',
    theme: process.env.ADMIN_THEME || 'cyberpunk',
    colors: {
      primary: process.env.ADMIN_PRIMARY_COLOR || '#FF0080',
      secondary: process.env.ADMIN_SECONDARY_COLOR || '#FF4500',
      accent: process.env.ADMIN_ACCENT_COLOR || '#00FF41'
    },
    scraper: {
      discountThreshold: parseInt(process.env.ADMIN_DISCOUNT_THRESHOLD) || 79,
      amazonTag: process.env.ADMIN_AMAZON_TAG || 'your-tag-20',
      enabled: process.env.ADMIN_SCRAPER_ENABLED === 'true'
    },
    feeds: JSON.parse(process.env.ADMIN_FEEDS || '[{"name":"SmartCanucks","url":"https://smartcanucks.ca/feed/"}]')
  };
  
  return res.status(200).json({ config });
}

async function updateSiteConfig(req, res) {
  const { siteName, tagline, theme, colors, scraper, feeds } = req.body;
  
  // In production, would use Vercel API to update env vars
  const updates = {};
  
  if (siteName) updates.ADMIN_SITE_NAME = siteName;
  if (tagline) updates.ADMIN_TAGLINE = tagline;
  if (theme) updates.ADMIN_THEME = theme;
  if (colors?.primary) updates.ADMIN_PRIMARY_COLOR = colors.primary;
  if (colors?.secondary) updates.ADMIN_SECONDARY_COLOR = colors.secondary;
  if (colors?.accent) updates.ADMIN_ACCENT_COLOR = colors.accent;
  if (scraper?.discountThreshold) updates.ADMIN_DISCOUNT_THRESHOLD = scraper.discountThreshold.toString();
  if (scraper?.amazonTag) updates.ADMIN_AMAZON_TAG = scraper.amazonTag;
  if (scraper?.enabled !== undefined) updates.ADMIN_SCRAPER_ENABLED = scraper.enabled.toString();
  if (feeds) updates.ADMIN_FEEDS = JSON.stringify(feeds);
  
  console.log('Would update env vars:', updates);
  
  return res.status(200).json({ 
    success: true, 
    message: 'Configuration updated (would trigger rebuild)',
    updates 
  });
}