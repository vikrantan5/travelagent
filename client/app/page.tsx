"use client";

// import { Metadata } from "next";
import {
  MapPin,
  Zap,
  Heart,
  Star,
  Plane,
  Calendar,
  Sparkles,
  Globe2,
  Compass,
  Palmtree,
    ArrowLeftRight,
} from "lucide-react";
// import { TrackButton } from "@/components/track-button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { motion } from "framer-motion";
import Link from "next/link";

export default function Home() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
      },
    },
  };

  const cardVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.4,
      },
    },
    hover: {
      scale: 1.05,
      y: -10,
      transition: {
        duration: 0.3,
      },
    },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-20 left-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl"
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
        <motion.div
          className="absolute bottom-20 right-10 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute top-1/2 left-1/2 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.4, 1],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </div>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-12 relative z-10">
        <motion.div
          className="text-center"
          initial="hidden"
          animate="visible"
          variants={containerVariants}
        >
          <motion.div variants={itemVariants} className="flex justify-center mb-6">
            <motion.div
              className="relative"
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <Globe2 className="w-20 h-20 text-purple-400" />
            </motion.div>
          </motion.div>

          <motion.h1
            variants={itemVariants}
            className="text-5xl font-bold sm:text-6xl md:text-7xl mb-4"
          >
            <span className="gradient-text">Travelethic</span>
          </motion.h1>

          <motion.h2
            variants={itemVariants}
            className="text-2xl font-semibold sm:text-3xl mt-4 text-gray-300"
          >
            Your Journey, Perfectly Crafted with Intelligence ✨
          </motion.h2>

          <motion.p
            variants={itemVariants}
            className="mt-8 text-lg leading-8 text-gray-400 max-w-3xl mx-auto"
          >
            Stop juggling dozens of tabs and conflicting travel info. Our
            AI-powered platform turns your travel dreams into reality—complete
            with flights, hotels, activities, and budget—all from a simple
            conversation about your perfect trip.
          </motion.p>

          <motion.div
            variants={itemVariants}
            className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-x-6"
          >
            <Link href="/plan">
              <motion.button
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-4 rounded-xl text-lg font-semibold flex items-center gap-2 shadow-xl w-full sm:w-auto animate-pulse-glow"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Plane className="w-5 h-5" />
                Plan My Trip
              </motion.button>
            </Link>
              <Link href="/compare">
              <motion.button
                className="glass-card text-white px-8 py-4 rounded-xl text-lg font-semibold flex items-center gap-2 w-full sm:w-auto border border-purple-500/30"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <ArrowLeftRight className="w-5 h-5" />
                Compare Destinations
              </motion.button>
            </Link>
            <Link href="/plans">
              <motion.button
                className="glass-card text-white px-8 py-4 rounded-xl text-lg font-semibold flex items-center gap-2 w-full sm:w-auto"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Compass className="w-5 h-5" />
                View My Trips
              </motion.button>
            </Link>
          </motion.div>
        </motion.div>

        {/* How It Works Section */}
        <motion.div
          className="mt-24 md:mt-32"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          variants={containerVariants}
        >
          <motion.h3
            variants={itemVariants}
            className="text-4xl font-bold text-center mb-16 gradient-text"
          >
            How It Works
          </motion.h3>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            {[
              {
                step: "1",
                title: "Fill Once, Dream Big",
                description:
                  "Tell us about your ideal trip—destination, dates, style, budget, and preferences. Our thoughtful form captures everything in minutes.",
                icon: <Sparkles className="w-8 h-8" />,
                color: "from-purple-500 to-pink-500",
              },
              {
                step: "2",
                title: "AI Agents Take Over",
                description:
                  "Specialized AI agents work together on flights, lodging, activities, and budgeting—all happening seamlessly in the background.",
                icon: <Zap className="w-8 h-8" />,
                color: "from-pink-500 to-orange-500",
              },
              {
                step: "3",
                title: "Complete Itinerary Ready",
                description:
                  "Get a full day-by-day plan with flights, accommodations, activities, costs, and booking links—all beautifully organized.",
                icon: <Calendar className="w-8 h-8" />,
                color: "from-orange-500 to-yellow-500",
              },
            ].map((item, index) => (
              <motion.div
                key={index}
                variants={cardVariants}
                whileHover="hover"
                className="text-center glass-card p-8 rounded-2xl relative overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-10 transition-opacity duration-300 from-purple-500 to-pink-500" />
                <motion.div
                  className={`flex items-center justify-center w-20 h-20 bg-gradient-to-br ${item.color} rounded-full mb-6 mx-auto shadow-lg`}
                  animate={{ rotate: [0, 10, -10, 0] }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                >
                  {item.icon}
                </motion.div>
                <h4 className="text-2xl font-semibold mb-4 text-white">
                  {item.title}
                </h4>
                <p className="text-gray-400">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Feature Cards */}
        <motion.div
          className="mt-24 md:mt-32"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={containerVariants}
        >
          <motion.h3
            variants={itemVariants}
            className="text-4xl font-bold text-center mb-16 gradient-text"
          >
            Why Choose Travelethic 
          </motion.h3>
          <motion.div
            className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3"
            variants={containerVariants}
          >
            {[
              {
                icon: <Sparkles className="w-8 h-8" />,
                title: "AI-Powered Intelligence",
                description:
                  "Multi-agent AI system that understands your travel style and crafts personalized itineraries that feel like they were made just for you.",
                gradient: "from-purple-500/20 to-purple-500/5",
              },
              {
                icon: <MapPin className="w-8 h-8" />,
                title: "Hidden Gems Discovery",
                description:
                  "Go beyond tourist traps. We find unique experiences, local events, and offbeat attractions that match your interests perfectly.",
                gradient: "from-pink-500/20 to-pink-500/5",
              },
              {
                icon: <Zap className="w-8 h-8" />,
                title: "Instant Planning",
                description:
                  "No more hours of research and comparison. Get a complete travel plan in moments, with everything balanced perfectly for your needs.",
                gradient: "from-blue-500/20 to-blue-500/5",
              },
              {
                icon: <Star className="w-8 h-8" />,
                title: "Smart Memory",
                description:
                  "Learns from your preferences over time. Each trip becomes more tailored as our AI remembers what you love.",
                gradient: "from-yellow-500/20 to-yellow-500/5",
              },
              {
                icon: <Calendar className="w-8 h-8" />,
                title: "Complete Coordination",
                description:
                  "Flights, hotels, activities, and budget—all coordinated seamlessly. No conflicts, no stress, just a perfect plan ready to execute.",
                gradient: "from-green-500/20 to-green-500/5",
              },
              {
                icon: <Heart className="w-8 h-8" />,
                title: "Crafted with Care",
                description:
                  "Every detail is thoughtfully considered to create not just a trip, but an experience that feels truly magical and personal.",
                gradient: "from-red-500/20 to-red-500/5",
              },
            ].map((feature, index) => (
              <motion.div key={index} variants={cardVariants} whileHover="hover">
                <Card className="glass-card border-white/10 h-full hover:border-white/30 transition-all duration-300 overflow-hidden group">
                  <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
                  <CardHeader className="relative">
                    <div className="flex items-center justify-center w-14 h-14 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl mb-4 shadow-lg">
                      {feature.icon}
                    </div>
                    <CardTitle className="text-xl text-white">
                      {feature.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="relative">
                    <CardDescription className="text-gray-400">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          className="mt-24 md:mt-32 text-center glass-card rounded-3xl py-16 md:py-20 px-6 sm:px-8 relative overflow-hidden"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-pink-600/10" />
          <motion.div
            className="relative z-10"
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          >
            <Palmtree className="w-16 h-16 mx-auto mb-6 text-purple-400" />
          </motion.div>
          <h3 className="text-4xl font-bold mb-6 gradient-text relative z-10">
            Ready to Make Travel Planning Magical?
          </h3>
          <p className="text-lg text-gray-400 mb-10 max-w-2xl mx-auto relative z-10">
            Stop spending hours planning and start experiencing. Let our AI
            create your perfect journey.
          </p>
          <Link href="/plan">
            <motion.button
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-10 py-5 rounded-xl text-lg font-semibold flex items-center gap-2 shadow-2xl mx-auto animate-pulse-glow relative z-10"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Plane className="w-5 h-5" />
              Start Planning Now
            </motion.button>
          </Link>
        </motion.div>
      </main>
    </div>
  );
}
