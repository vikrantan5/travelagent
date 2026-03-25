"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ShoppingBag, ExternalLink, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

interface Product {
  name: string;
  category?: string;
  reason?: string;
  why_needed?: string;
  price_range?: string;
  priority?: string;
  amazon_url?: string;
  link?: string;
}

interface ProductSuggestionsProps {
  products: Product[];
}

export function ProductSuggestions({ products }: ProductSuggestionsProps) {
  // Add safe guard for products
  const safeProducts = Array.isArray(products) ? products : [];
  
  if (!safeProducts || safeProducts.length === 0) {
    return null;
  }

  const getCategoryColor = (category?: string) => {
    switch (category?.toLowerCase()) {
      case "clothing":
        return "bg-blue-500/20 text-blue-400";
      case "gadgets":
      case "electronics":
        return "bg-purple-500/20 text-purple-400";
      case "accessories":
        return "bg-green-500/20 text-green-400";
      case "health":
      case "safety":
        return "bg-red-500/20 text-red-400";
      default:
        return "bg-gray-500/20 text-gray-400";
    }
  };

  const getPriorityBadge = (priority?: string) => {
    if (priority?.toLowerCase().includes("must") || priority?.toLowerCase().includes("essential")) {
      return <Badge className="bg-red-500/20 text-red-400 text-xs">Must Have</Badge>;
    }
    return <Badge className="bg-blue-500/20 text-blue-400 text-xs">Recommended</Badge>;
  };

  return (
    <section className="mt-12">
      <div className="flex items-center gap-3 mb-6">
        <ShoppingBag className="w-7 h-7 text-purple-400" />
        <h2 className="text-3xl font-bold gradient-text">Recommended Products</h2>
      </div>
      <p className="text-gray-400 mb-6">
        Essential items to make your trip more comfortable and enjoyable
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {safeProducts.map((product, index) => {
          const productUrl = product.amazon_url || product.link || "#";
          const reason = product.reason || product.why_needed || "Useful for your trip";
          
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="glass-card border-purple-500/20 hover:border-purple-500/40 transition-all duration-300 h-full flex flex-col">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <CardTitle className="text-lg text-white leading-tight">
                      {product.name}
                    </CardTitle>
                    {product.priority && getPriorityBadge(product.priority)}
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    {product.category && (
                      <Badge className={getCategoryColor(product.category)}>
                        {product.category}
                      </Badge>
                    )}
                    {product.price_range && (
                      <Badge variant="outline" className="text-gray-400 border-gray-600">
                        {product.price_range}
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col">
                  <p className="text-sm text-gray-300 mb-4 flex-1">{reason}</p>
                  <a
                    href={productUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full"
                  >
                    <Button
                      variant="outline"
                      className="w-full bg-purple-500/10 border-purple-500/30 hover:bg-purple-500/20 text-purple-300"
                    >
                      <ExternalLink className="w-4 h-4 mr-2" />
                      View on Amazon
                    </Button>
                  </a>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
