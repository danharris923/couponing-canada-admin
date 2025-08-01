export interface DealLabelResult {
  primary: string;
  secondary?: string;
  showPercent: boolean;
}

export function getSmartDealLabel(originalPrice: number, currentPrice: number, realDiscountPercent?: number): DealLabelResult {
  // Only use scraped discount data - no calculations
  if (!realDiscountPercent || realDiscountPercent <= 0) {
    return {
      primary: "",
      secondary: undefined,
      showPercent: false
    };
  }
  
  // Only show red percentage tags for deals with scraped discount over 20%
  if (realDiscountPercent >= 20) {
    return {
      primary: `${realDiscountPercent}% OFF`,
      secondary: undefined,
      showPercent: true
    };
  } else {
    // Don't show any badge for deals under 20% off
    return {
      primary: "",
      secondary: undefined,
      showPercent: false
    };
  }
}

export function getPriceDisplay(originalPrice: number, currentPrice: number, realDiscountPercent?: number) {
  // Only use scraped discount data - no price calculations
  if (!realDiscountPercent || realDiscountPercent <= 0) {
    return {
      current: `$${currentPrice.toFixed(2)}`,
      original: null,
      badge: null
    };
  }
  
  const dealLabel = getSmartDealLabel(originalPrice, currentPrice, realDiscountPercent);
  
  return {
    current: `$${currentPrice.toFixed(2)}`,
    original: `$${originalPrice.toFixed(2)}`,
    badge: dealLabel
  };
}