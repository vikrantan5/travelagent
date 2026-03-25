"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Image as ImageIcon } from "lucide-react";
import { motion } from "framer-motion";
import Image from "next/image";
import { useState } from "react";

interface PlaceImage {
  place: string;
  image_url: string;
}

interface ImageGalleryProps {
  images: PlaceImage[];
  destination: string;
}

// Fallback placeholder for failed images
const ImageFallback = ({ place }: { place: string }) => (
  <div className="w-full h-full bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center">
    <div className="text-center p-4">
      <ImageIcon className="w-12 h-12 mx-auto text-purple-400/50 mb-2" />
      <p className="text-sm text-muted-foreground">{place}</p>
    </div>
  </div>
);

export function ImageGallery({ images, destination }: ImageGalleryProps) {
   // Add safe guard for images
  const safeImages = Array.isArray(images) ? images.filter(img => img && img.image_url) : [];
  
  if (!safeImages || safeImages.length === 0) {
    return null;
  }

  const heroImage = safeImages[0];
  const otherImages = safeImages.slice(1);

  return (
    <section className="mt-12">
      <div className="flex items-center gap-3 mb-6">
        <ImageIcon className="w-7 h-7 text-purple-400" />
        <h2 className="text-3xl font-bold gradient-text">Destination Highlights</h2>
      </div>
      
      {/* Hero Image */}
      {heroImage && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mb-6"
        >
          <Card className="overflow-hidden border-2 border-purple-500/30">
            <div className="relative h-96 w-full">
              <HeroImageWithFallback image={heroImage} />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-6">
                <Badge className="bg-purple-500/80 text-white mb-2">
                  <MapPin className="w-3 h-3 mr-1" />
                  Featured Location
                </Badge>
                <h3 className="text-2xl font-bold text-white">{heroImage.place}</h3>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* Image Grid */}
      {otherImages.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {otherImages.map((img, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="overflow-hidden border border-purple-500/20 hover:border-purple-500/40 transition-all duration-300 group">
                <div className="relative h-48 w-full">
                  <GridImageWithFallback image={img} />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <div className="absolute bottom-0 left-0 right-0 p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <p className="text-white text-sm font-semibold truncate">
                      {img.place}
                    </p>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </section>
  );
}

// Component for hero image with fallback
function HeroImageWithFallback({ image }: { image: PlaceImage }) {
  const [error, setError] = useState(false);
  
  if (error || !image.image_url) {
    return <ImageFallback place={image.place} />;
  }
  
  return (
    <Image
      src={image.image_url}
      alt={image.place}
      fill
      className="object-cover"
      priority
      onError={() => setError(true)}
    />
  );
}

// Component for grid images with fallback
function GridImageWithFallback({ image }: { image: PlaceImage }) {
  const [error, setError] = useState(false);
  
  if (error || !image.image_url) {
    return <ImageFallback place={image.place} />;
  }
  
  return (
    <Image
      src={image.image_url}
      alt={image.place}
      fill
      className="object-cover group-hover:scale-110 transition-transform duration-300"
      onError={() => setError(true)}
    />
  );
}
