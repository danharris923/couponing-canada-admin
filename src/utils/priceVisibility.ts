/**
 * Determines whether to show price or "Check Price" button
 * Only 10% of deals show prices upfront to create curiosity and drive clicks
 */

export function shouldShowPrice(dealId: string | number): boolean {
  // Use deal ID as seed for consistent but pseudo-random selection
  // This ensures the same deals always show/hide prices consistently
  const hash = hashString(String(dealId));
  
  // Show price for 20% of deals
  return hash % 5 === 0;
}

export function getCheckPriceMessages(): string[] {
  return [
    "Check Price on Amazon",
    "See Price at Amazon", 
    "View Amazon Price",
    "Get Best Price",
    "Check Current Price",
    "See Deal Price",
    "Amazon Price Check",
    "View Special Price"
  ];
}

export function getRandomCheckPriceMessage(dealId: string | number): string {
  const messages = getCheckPriceMessages();
  const hash = hashString(String(dealId));
  return messages[hash % messages.length];
}

// Simple hash function to convert string to number
function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash);
}

export interface PriceVisibilityResult {
  showPrice: boolean;
  checkPriceMessage?: string;
}

export function getPriceVisibility(dealId: string | number): PriceVisibilityResult {
  const showPrice = shouldShowPrice(dealId);
  
  return {
    showPrice,
    checkPriceMessage: showPrice ? undefined : getRandomCheckPriceMessage(dealId)
  };
}