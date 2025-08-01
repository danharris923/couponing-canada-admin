export interface Deal {
  id: string;
  title: string;
  imageUrl: string;
  price: number;
  originalPrice: number;
  discountPercent: number;
  category: string;
  description: string;
  affiliateUrl: string;
  featured?: boolean;
  dateAdded: string;
}