"use client";

import React, { useState, useEffect } from "react";
import { umami } from "@/lib/umami";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";
import {
  MapPin,
  Calendar as CalendarIcon,
  Users,
  DollarSign,
  Heart,
  Home,
  Clock,
  Globe,
  Plane,
  Luggage,
  Plus,
  RefreshCw,
  AlertCircle,
  Trash2,
  Eye,
} from "lucide-react";
import { format } from "date-fns";
import Link from "next/link";
import { toast } from "sonner";

interface TripPlan {
  id: string;
  name: string;
  destination: string;
  startingLocation: string;
  travelDatesStart: string;
  travelDatesEnd?: string;
  dateInputType: string;
  duration?: number;
  travelingWith: string;
  adults: number;
  children: number;
  ageGroups: string[];
  budget: number;
  budgetCurrency: string;
  travelStyle: string;
  budgetFlexible: boolean;
  vibes: string[];
  priorities: string[];
  interests?: string;
  rooms: number;
  pace: number[];
  beenThereBefore?: string;
  lovedPlaces?: string;
  additionalInfo?: string;
  createdAt: string;
  updatedAt: string;
  userId?: string;
}

const formatCurrency = (amount: number, currency: string) => {
  const symbols: Record<string, string> = {
    USD: "$",
    EUR: "€",
    GBP: "£",
    INR: "₹",
    JPY: "¥",
  };
  return `${symbols[currency] || "$"}${amount.toLocaleString()}`;
};

const formatDate = (dateString: string, inputType: string) => {
  if (inputType === "text" || !dateString) {
    return dateString || "Flexible dates";
  }
  try {
    return format(new Date(dateString), "MMM dd, yyyy");
  } catch {
    return dateString;
  }
};

const getPaceDescription = (pace: number[]) => {
  const paceValue = pace[0] || 3;
  const descriptions = {
    1: "Very relaxed",
    2: "Mostly relaxed",
    3: "Balanced",
    4: "Quite busy",
    5: "Action-packed",
  };
  return descriptions[paceValue as keyof typeof descriptions] || "Balanced";
};

export default function PlansList() {
  const [tripPlans, setTripPlans] = useState<TripPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingPlanId, setDeletingPlanId] = useState<string | null>(null);

  const fetchTripPlans = async () => {
    try {
      setLoading(true);
      setError(null);
      umami.track("Refresh Plans");
      const response = await fetch("/api/plans");
      const data = await response.json();

      if (data.success) {
        setTripPlans(data.tripPlans);
      } else {
        setError(data.message || "Failed to fetch trip plans");
      }
    } catch (err) {
      console.error("Error fetching trip plans:", err);
      setError("Failed to fetch trip plans");
    } finally {
      setLoading(false);
    }
  };

  const deleteTripPlan = async (planId: string) => {
    try {
      setDeletingPlanId(planId);
      const response = await fetch(`/api/plans/${planId}`, {
        method: "DELETE",
      });
      const data = await response.json();

      if (data.success) {
        // Remove the plan from the local state
        setTripPlans(tripPlans.filter((plan) => plan.id !== planId));
        toast.success("Trip plan deleted successfully");
        umami.track("Delete Plan", { planId });
      } else {
        toast.error(data.message || "Failed to delete trip plan");
      }
    } catch (err) {
      console.error("Error deleting trip plan:", err);
      toast.error("Failed to delete trip plan");
    } finally {
      setDeletingPlanId(null);
    }
  };

  const handleDeletePlan = (planId: string) => {
    if (
      window.confirm(
        "Are you sure you want to delete this trip plan? This action cannot be undone."
      )
    ) {
      deleteTripPlan(planId);
    }
  };

  useEffect(() => {
    fetchTripPlans();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 py-8 px-4 flex items-center justify-center">
        <motion.div
          className="text-center glass-card p-12 rounded-2xl"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <RefreshCw className="w-12 h-12 text-purple-400 mx-auto mb-4" />
          </motion.div>
          <p className="text-gray-300 text-lg">Loading your trip plans...</p>
        </motion.div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 py-8 px-4 flex items-center justify-center">
        <motion.div
          className="text-center glass-card p-12 rounded-2xl"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold mb-2 text-white">Error Loading Plans</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <Button onClick={fetchTripPlans} variant="outline" className="glass border-white/20">
            <RefreshCw className="w-4 h-4 mr-2" />
            Try Again
          </Button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 py-8 px-4 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-20 right-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </div>

      <div className="max-w-6xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-4xl font-bold gradient-text mb-4 flex items-center justify-center gap-3">
            <Luggage className="w-8 h-8" />
            Your Trip Plans
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Manage and review all your planned adventures ✨
          </p>
        </motion.div>

        {/* Action Bar */}
        <motion.div
          className="flex justify-between items-center mb-8 glass-card p-4 rounded-xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div className="text-sm text-gray-400">
            {tripPlans.length} {tripPlans.length === 1 ? "plan" : "plans"} found
          </div>
          <div className="flex gap-3">
            <Button onClick={fetchTripPlans} variant="outline" size="sm" className="glass border-white/20">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Link href="/plan" onClick={() => umami.track("Create New Trip")}>
              <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                <Plus className="w-4 h-4 mr-2" />
                New Trip Plan
              </Button>
            </Link>
          </div>
        </motion.div>

        {/* Trip Plans Grid */}
        {tripPlans.length === 0 ? (
          <motion.div
            className="text-center py-16 glass-card rounded-2xl"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Globe className="w-16 h-16 text-purple-400/50 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2 text-white">No trip plans yet</h3>
            <p className="text-gray-400 mb-6">
              Start planning your next adventure!
            </p>
            <Link href="/plan" onClick={() => umami.track("Create New Trip")}>
              <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Trip Plan
              </Button>
            </Link>
          </motion.div>
        ) : (
          <motion.div
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
            initial="hidden"
            animate="visible"
            variants={{
              hidden: { opacity: 0 },
              visible: {
                opacity: 1,
                transition: {
                  staggerChildren: 0.1,
                },
              },
            }}
          >
            {tripPlans.map((plan) => (
              <motion.div
                key={plan.id}
                variants={{
                  hidden: { opacity: 0, y: 20 },
                  visible: { opacity: 1, y: 0 },
                }}
                whileHover={{ scale: 1.03, y: -5 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="glass-card border-white/10 h-full hover:border-white/30 transition-all duration-300 group relative overflow-hidden">
                  {/* Gradient Overlay on Hover */}
                  <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                  <CardHeader className="relative">
                    <CardTitle className="flex items-center gap-2 text-xl text-white">
                      <MapPin className="w-5 h-5 text-purple-400" />
                      {plan.destination}
                    </CardTitle>
                    <CardDescription className="text-base font-medium text-gray-400">
                      {plan.name}
                    </CardDescription>
                  </CardHeader>

                  <CardContent className="space-y-4 relative">
                    {/* Travel Details */}
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-sm text-gray-300">
                        <Plane className="w-4 h-4 text-purple-400" />
                        <span>From {plan.startingLocation}</span>
                      </div>

                      <div className="flex items-center gap-2 text-sm text-gray-300">
                        <CalendarIcon className="w-4 h-4 text-purple-400" />
                        <span>
                          {formatDate(plan.travelDatesStart, plan.dateInputType)}
                          {plan.travelDatesEnd &&
                            plan.dateInputType === "picker" && (
                              <>
                                {" - "}
                                {formatDate(
                                  plan.travelDatesEnd,
                                  plan.dateInputType
                                )}
                              </>
                            )}
                        </span>
                      </div>

                      {plan.duration && (
                        <div className="flex items-center gap-2 text-sm text-gray-300">
                          <Clock className="w-4 h-4 text-purple-400" />
                          <span>{plan.duration} days</span>
                        </div>
                      )}

                      <div className="flex items-center gap-2 text-sm text-gray-300">
                        <Users className="w-4 h-4 text-purple-400" />
                        <span>
                          {plan.adults} adult{plan.adults > 1 ? "s" : ""}
                          {plan.children > 0 &&
                            `, ${plan.children} child${
                              plan.children > 1 ? "ren" : ""
                            }`}
                        </span>
                      </div>

                      <div className="flex items-center gap-2 text-sm text-gray-300">
                        <DollarSign className="w-4 h-4 text-purple-400" />
                        <span>
                          {formatCurrency(plan.budget, plan.budgetCurrency)} per
                          person
                        </span>
                      </div>

                      <div className="flex items-center gap-2 text-sm text-gray-300">
                        <Home className="w-4 h-4 text-purple-400" />
                        <span>
                          {plan.rooms} room{plan.rooms > 1 ? "s" : ""},{" "}
                          {plan.travelStyle}
                        </span>
                      </div>
                    </div>

                    {/* Vibes */}
                    {plan.vibes.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium mb-2 flex items-center gap-2 text-white">
                          <Heart className="w-4 h-4 text-pink-400" />
                          Trip Vibes
                        </h4>
                        <div className="flex flex-wrap gap-1">
                          {plan.vibes.slice(0, 3).map((vibe) => (
                            <Badge
                              key={vibe}
                              variant="secondary"
                              className="text-xs bg-purple-500/20 text-purple-300 border-purple-500/30"
                            >
                              {vibe}
                            </Badge>
                          ))}
                          {plan.vibes.length > 3 && (
                            <Badge variant="outline" className="text-xs border-white/20 text-gray-400">
                              +{plan.vibes.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Pace */}
                    <div className="text-sm text-gray-400">
                      <span className="font-medium text-white">Pace:</span>{" "}
                      {getPaceDescription(plan.pace)}
                    </div>

                    {/* Created Date */}
                    <div className="text-xs text-gray-500 pt-2 border-t border-white/10">
                      Created{" "}
                      {format(
                        new Date(plan.createdAt),
                        "MMM dd, yyyy 'at' h:mm a"
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 pt-2">
                      <Link href={`/plan/${plan.id}`} className="flex-1" onClick={() => umami.track("View Plan Details", { planId: plan.id })}>
                        <Button variant="outline" size="sm" className="w-full glass border-white/20 hover:border-white/40">
                          <Eye className="w-4 h-4 mr-2" />
                          View Details
                        </Button>
                      </Link>
                      <Button
                        variant="destructive"
                        size="sm"
                        className="flex-1 bg-red-500/20 hover:bg-red-500/30 border border-red-500/30"
                        onClick={() => handleDeletePlan(plan.id)}
                        disabled={deletingPlanId === plan.id}
                      >
                        {deletingPlanId === plan.id ? (
                          <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4 mr-2" />
                        )}
                        Delete
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
}
