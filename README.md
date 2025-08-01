# 🏴‍☠️ Couponing Canada Admin

**Hacker Admin System** - Using Vercel environment variables as a database!

## 🔥 What This Is

A complete admin dashboard for managing deal sites that uses **Vercel's env vars as a database**. Pure genius hacker approach - no traditional backend needed!

## ⚡ Features

- **🎨 Cyberpunk Admin Dashboard** - Dark theme with neon accents
- **⚙️ Live Site Management** - Change site name, themes, colors without code
- **🚀 Scraper Control** - Trigger RSS scrapers via GitHub Actions
- **📡 Feed Management** - Add/remove RSS feeds dynamically
- **🔐 JWT Authentication** - Password-protected admin access
- **📊 Analytics Dashboard** - Site stats and performance metrics

## 🚀 Quick Deploy

### 1. Deploy to Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/danharris923/couponing-canada-admin)

### 2. Add Environment Variables
Copy from `.env.template` and add to Vercel dashboard:

```bash
# Key variables to set:
ADMIN_PASSWORD_HASH=your_hashed_password
ADMIN_SITE_NAME=Your Site Name
ADMIN_THEME=cyberpunk
ADMIN_FEEDS=[{"name":"RSS Name","url":"https://feed.url"}]
GITHUB_TOKEN=your_github_token
```

### 3. Access Admin
Visit `/admin` and use your configured password.

## 🏗️ Architecture

```
Vercel Edge Functions + Env Vars = Database
├── /api/admin/auth.js          # Authentication
├── /api/admin/config/site.js   # Site management
├── /api/admin/scraper/trigger.js # Scraper control
└── React Admin Dashboard
```

## 🔧 Local Development

```bash
npm install
npm start
# Visit http://localhost:3000/admin
```

## 🎯 Admin Features

- **Site Config**: Live editing of site name, colors, themes
- **Scraper Control**: Trigger and monitor RSS scraping
- **Feed Management**: Add/remove RSS sources
- **Custom Cards**: Create manual deal posts
- **Analytics**: View site performance and stats

## 🏴‍☠️ The Hack

Instead of a traditional database, this system uses Vercel's environment variables as storage. Changes update env vars, trigger rebuilds, and deploy automatically. It's serverless, scales infinitely, and costs almost nothing.

**Built with Claude Code** - The future of development is here! 🚀