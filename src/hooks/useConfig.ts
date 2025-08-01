import { useState, useEffect, createContext, useContext } from 'react';
import { SiteConfig } from '../types/Config';

// Default configuration fallback
const defaultConfig: SiteConfig = {
  siteName: "Modern Template",
  tagline: "Content Discovery Made Easy",
  description: "A modern content aggregation platform",
  
  logo: {
    text: "ModernTemplate",
    backgroundColor: "#10B981",
    textColor: "#FFFFFF"
  },
  
  colors: {
    primary: "#10B981",
    primaryHover: "#059669", 
    textDark: "#1F2937",
    cardPink: "#FDF2F8",
    cardBlue: "#EFF6FF",
    cardYellow: "#FFFBEB",
    gradientFrom: "#10B981",
    gradientTo: "#059669"
  },
  
  navigation: {
    showHome: true,
    showDeals: true,
    showCoupons: false,
    showAmazon: false,
    showAbout: true
  },
  
  content: {
    dataFile: "/data.json",
    showFeaturedSidebar: true,
    featuredItemsCount: 5,
    searchPlaceholder: "Search...",
    noResultsMessage: "No results found."
  },
  
  meta: {
    title: "Modern Template",
    description: "A modern content aggregation platform"
  },
  
  footer: {
    companyName: "Modern Template",
    tagline: "Powered by modern technology",
    copyright: "© 2025 Modern Template. All rights reserved."
  }
};

// Configuration Context
export const ConfigContext = createContext<{
  config: SiteConfig;
  loading: boolean;
  error: string | null;
}>({
  config: defaultConfig,
  loading: false,
  error: null
});

// Hook to load configuration from public/config.json
export const useConfigLoader = () => {
  const [config, setConfig] = useState<SiteConfig>(defaultConfig);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadConfig = async () => {
      try {
        setLoading(true);
        const response = await fetch('/config.json');
        
        if (!response.ok) {
          throw new Error(`Failed to load config: ${response.status}`);
        }
        
        const configData = await response.json();
        
        // Merge with default config to ensure all required fields are present
        const mergedConfig: SiteConfig = {
          ...defaultConfig,
          ...configData,
          logo: { ...defaultConfig.logo, ...configData.logo },
          colors: { ...defaultConfig.colors, ...configData.colors },
          navigation: { ...defaultConfig.navigation, ...configData.navigation },
          content: { ...defaultConfig.content, ...configData.content },
          meta: { ...defaultConfig.meta, ...configData.meta },
          footer: { ...defaultConfig.footer, ...configData.footer },
          advanced: { ...defaultConfig.advanced, ...configData.advanced }
        };
        
        setConfig(mergedConfig);
        setError(null);
        
        console.info('Configuration loaded successfully:', mergedConfig.siteName);
        
      } catch (err) {
        console.error('Failed to load configuration, using defaults:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setConfig(defaultConfig);
      } finally {
        setLoading(false);
      }
    };

    loadConfig();
  }, []);

  return { config, loading, error };
};

// Hook to access configuration from context
export const useConfig = () => {
  const context = useContext(ConfigContext);
  if (!context) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
};