"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  MapPin,
  Plane,
  DollarSign,
  Heart,
  Users,
  Waves,
  Star,
  TrendingUp,
  Loader2,
} from "lucide-react";
import { motion } from "framer-motion";

interface ComparisonResult {
  place_1: string;
  place_2: string;
  best_for: {
    budget: string;
    nightlife: string;
    luxury_honeymoon: string;
    water_sports: string;
    family_trip: string;
  };
  pros_cons: {
    [key: string]: {
      pros: string[];
      cons: string[];
    };
  };
  final_recommendation: {
    best_option: string;
    reason: string;
  };
}

export default function ComparePage() {
  const [place1, setPlace1] = useState("");
  const [place2, setPlace2] = useState("");
  const [budget, setBudget] = useState("moderate");
  const [travelStyle, setTravelStyle] = useState("balanced");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ComparisonResult | null>(null);

  const handleCompare = async () => {
    if (!place1 || !place2) {
      alert("Please enter both destinations");
      return;
    }

    setLoading(true);
    try {
         const response = await fetch("/api/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          place_1: place1,
          place_2: place2,
          budget,
          travel_style: travelStyle,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setResult(data);
      } else {
        alert("Failed to compare destinations. Please try again.");
      }
    } catch (error) {
      console.error("Comparison error:", error);
      alert("Failed to compare destinations. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const categoryIcons: { [key: string]: any } = {
    budget: DollarSign,
    nightlife: Star,
    luxury_honeymoon: Heart,
    water_sports: Waves,
    family_trip: Users,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold gradient-text mb-4">
            Compare Destinations
          </h1>
          <p className="text-gray-400 text-lg">
            Get AI-powered insights to help you choose the perfect destination
          </p>
        </motion.div>

        <Card className="glass-card border-purple-500/30 mb-8">
          <CardHeader>
            <CardTitle className="text-white">Enter Destinations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="text-gray-300 text-sm mb-2 block">
                  Destination 1
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <Input
                    value={place1}
                    onChange={(e) => setPlace1(e.target.value)}
                    placeholder="e.g., Goa, India"
                    className="pl-10 bg-gray-800/50 border-gray-700 text-white"
                  />
                </div>
              </div>
              <div>
                <label className="text-gray-300 text-sm mb-2 block">
                  Destination 2
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <Input
                    value={place2}
                    onChange={(e) => setPlace2(e.target.value)}
                    placeholder="e.g., Bali, Indonesia"
                    className="pl-10 bg-gray-800/50 border-gray-700 text-white"
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="text-gray-300 text-sm mb-2 block">
                  Budget
                </label>
                <select
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                  className="w-full p-2 rounded-md bg-gray-800/50 border border-gray-700 text-white"
                >
                  <option value="budget">Budget</option>
                  <option value="moderate">Moderate</option>
                  <option value="luxury">Luxury</option>
                </select>
              </div>
              <div>
                <label className="text-gray-300 text-sm mb-2 block">
                  Travel Style
                </label>
                <select
                  value={travelStyle}
                  onChange={(e) => setTravelStyle(e.target.value)}
                  className="w-full p-2 rounded-md bg-gray-800/50 border border-gray-700 text-white"
                >
                  <option value="relaxed">Relaxed</option>
                  <option value="balanced">Balanced</option>
                  <option value="adventure">Adventure</option>
                </select>
              </div>
            </div>

            <Button
              onClick={handleCompare}
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Comparing...
                </>
              ) : (
                <>
                  <Plane className="w-5 h-5 mr-2" />
                  Compare Destinations
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Best For Categories */}
            <Card className="glass-card border-purple-500/30">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <TrendingUp className="w-6 h-6 text-purple-400" />
                  Best For
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  {Object.entries(result.best_for).map(([category, winner]) => {
                    const Icon = categoryIcons[category] || MapPin;
                    return (
                      <div
                        key={category}
                        className="bg-gray-800/50 p-4 rounded-lg text-center"
                      >
                        <Icon className="w-6 h-6 mx-auto mb-2 text-purple-400" />
                        <p className="text-xs text-gray-400 mb-1 capitalize">
                          {category.replace("_", " ")}
                        </p>
                        <p className="text-sm font-semibold text-white">
                          {winner}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Pros & Cons Comparison */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
             {result?.pros_cons &&
  Object.entries(result.pros_cons).map(([place, data]) => (
    <Card key={place} className="glass-card border-purple-500/30">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <MapPin className="w-5 h-5 text-purple-400" />
          {place}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <h4 className="text-green-400 font-semibold mb-2 flex items-center gap-2">
              <Badge className="bg-green-500/20 text-green-400">Pros</Badge>
            </h4>
            <ul className="space-y-2">
              {data?.pros?.map((pro, idx) => (
                <li key={idx} className="text-gray-300 text-sm flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  {pro}
                </li>
              ))}
            </ul>
          </div>

          <Separator className="bg-gray-700" />

          <div>
            <h4 className="text-red-400 font-semibold mb-2 flex items-center gap-2">
              <Badge className="bg-red-500/20 text-red-400">Cons</Badge>
            </h4>
            <ul className="space-y-2">
              {data?.cons?.map((con, idx) => (
                <li key={idx} className="text-gray-300 text-sm flex items-start gap-2">
                  <span className="text-red-400 mt-1">✗</span>
                  {con}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  ))}
            </div>

            {/* Final Recommendation */}
            <Card className="glass-card border-2 border-purple-500">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Star className="w-6 h-6 text-yellow-400" />
                  Our Recommendation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-4">
                  <h3 className="text-3xl font-bold gradient-text mb-4">
                    {result.final_recommendation.best_option}
                  </h3>
                  <p className="text-gray-300 text-lg">
                    {result.final_recommendation.reason}
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
}
