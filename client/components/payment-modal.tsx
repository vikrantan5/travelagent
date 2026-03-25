"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Check, X, Sparkles, Zap, Crown } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  userId: string;
}

export function PaymentModal({ isOpen, onClose, userId }: PaymentModalProps) {
  const [loading, setLoading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const plans = [
    {
      id: "monthly",
      name: "Monthly Plan",
      price: 299,
      currency: "INR",
      features: [
        "Unlimited trip planners",
        "AI-powered recommendations",
        "Flight & hotel search",
        "Budget optimization",
        "Priority support",
      ],
      icon: Zap,
      popular: false,
    },
    {
      id: "yearly",
      name: "Yearly Plan",
      price: 2999,
      currency: "INR",
      features: [
        "Unlimited trip planners",
        "AI-powered recommendations",
        "Flight & hotel search",
        "Budget optimization",
        "Priority support",
        "Save 17% vs monthly",
      ],
      icon: Crown,
      popular: true,
    },
  ];

  const initiatePayment = async (planType: string, amount: number) => {
    try {
      setLoading(true);
      setSelectedPlan(planType);

      // Step 1: Initiate payment on backend
      const response = await fetch("/api/payment/initiate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: userId,
            plan_type: planType,
            amount: amount,
          }),
       });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Failed to initiate payment");
      }

      // Step 2: Open Razorpay checkout
      const options = {
        key: data.razorpay_key_id,
        amount: data.amount,
        currency: data.currency,
        name: "Travelethic",
        description: `${planType.charAt(0).toUpperCase() + planType.slice(1)} Plan`,
        order_id: data.order_id,
        handler: async function (response: any) {
          // Step 3: Verify payment on backend
           const verifyResponse = await fetch("/api/payment/verify", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                user_id: userId,
              }),
             });

          const verifyData = await verifyResponse.json();

          if (verifyData.success) {
            alert("Payment successful! You now have premium access.");
            onClose();
            window.location.reload();
          } else {
            alert("Payment verification failed. Please contact support.");
          }
        },
        prefill: {
          name: "",
          email: "",
          contact: "",
        },
        theme: {
          color: "#9333ea",
        },
      };

      const razorpay = new (window as any).Razorpay(options);
      razorpay.open();
    } catch (error) {
      console.error("Payment error:", error);
      alert("Failed to initiate payment. Please try again.");
    } finally {
      setLoading(false);
      setSelectedPlan(null);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="w-full max-w-4xl max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <Card className="bg-gray-900 border-purple-500/30">
              <CardHeader className="text-center relative">
                <button
                  onClick={onClose}
                  className="absolute right-4 top-4 text-gray-400 hover:text-white"
                >
                  <X className="w-5 h-5" />
                </button>
                <CardTitle className="text-3xl font-bold gradient-text flex items-center justify-center gap-2">
                  <Sparkles className="w-8 h-8" />
                  Upgrade to Premium
                </CardTitle>
                <CardDescription className="text-gray-400 mt-2">
                  Unlock unlimited travel planning with AI-powered features
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                  {plans.map((plan) => {
                    const Icon = plan.icon;
                    return (
                      <motion.div
                        key={plan.id}
                        whileHover={{ scale: 1.02 }}
                        className={`relative glass-card p-6 rounded-xl border-2 ${
                          plan.popular
                            ? "border-purple-500"
                            : "border-gray-700"
                        }`}
                      >
                        {plan.popular && (
                          <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                            <span className="bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                              MOST POPULAR
                            </span>
                          </div>
                        )}
                        <div className="text-center mb-6">
                          <Icon className="w-12 h-12 mx-auto mb-3 text-purple-400" />
                          <h3 className="text-xl font-bold text-white">
                            {plan.name}
                          </h3>
                          <div className="mt-4">
                            <span className="text-4xl font-bold text-white">
                              ₹{plan.price}
                            </span>
                            <span className="text-gray-400">/{plan.id === "monthly" ? "month" : "year"}</span>
                          </div>
                        </div>
                        <ul className="space-y-3 mb-6">
                          {plan.features.map((feature, idx) => (
                            <li
                              key={idx}
                              className="flex items-start gap-2 text-gray-300"
                            >
                              <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                              <span className="text-sm">{feature}</span>
                            </li>
                          ))}
                        </ul>
                        <Button
                          onClick={() => initiatePayment(plan.id, plan.price)}
                          disabled={loading}
                          className={`w-full ${
                            plan.popular
                              ? "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                              : "bg-gray-700 hover:bg-gray-600"
                          }`}
                        >
                          {loading && selectedPlan === plan.id
                            ? "Processing..."
                            : "Choose Plan"}
                        </Button>
                      </motion.div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
