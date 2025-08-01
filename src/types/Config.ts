/**
 * Frontend configuration interface for the Modern Template system.
 * This allows customization of branding, navigation, and appearance.
 */

export interface SiteConfig {
  // Site Identity
  siteName: string;
  tagline: string;
  description: string;
  
  // Branding
  logo?: {
    text?: string;
    imageUrl?: string;
    backgroundColor?: string;
    textColor?: string;
  };
  
  // Theme Colors
  colors: {
    primary: string;
    primaryHover: string;
    textDark: string;
    cardPink: string;
    cardBlue: string;  
    cardYellow: string;
    gradientFrom: string;
    gradientTo: string;
  };
  
  // Navigation
  navigation: {
    showHome: boolean;
    showDeals: boolean;
    showCoupons: boolean;
    showAmazon: boolean;
    showAbout: boolean;
    customLinks?: Array<{
      label: string;
      href: string;
      external?: boolean;
    }>;
  };
  
  // Content Settings
  content: {
    dataFile: string; // path to JSON data file
    itemsPerPage?: number;
    showFeaturedSidebar: boolean;
    featuredItemsCount: number;
    searchPlaceholder: string;
    noResultsMessage: string;
  };
  
  // SEO & Meta
  meta: {
    title: string;
    description: string;
    keywords?: string;
    ogImage?: string;
  };
  
  // Footer
  footer: {
    companyName: string;
    tagline: string;
    copyright: string;
    showSocialLinks?: boolean;
    socialLinks?: Array<{
      platform: string;
      url: string;
      icon?: string;
    }>;
  };
  
  // Advanced Settings
  advanced?: {
    enableAnalytics?: boolean;
    analyticsId?: string;
    enablePWA?: boolean;
    customCSS?: string;
    customScripts?: string[];
  };
}