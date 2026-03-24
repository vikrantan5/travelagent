"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MapPin, Image as ImageIcon } from "lucide-react";
import { motion } from "framer-motion";
import Image from "next/image";

interface PlaceImage {
  place: string;
  image_url: string;
}

interface ImageGalleryProps {
  images: PlaceImage[];
  destination: string;
}

export function ImageGallery({ images, destination }: ImageGalleryProps) {
  if (!images || images.length === 0) {
    return null;
  }

  const heroImage = images[0];
  const otherImages = images.slice(1);

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
              <Image
                src={heroImage.image_url}
                alt={heroImage.place}
                fill
                className="object-cover"
                priority
              />
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
                  <Image
                    src={img.image_url}
                    alt={img.place}
                    fill
                    className="object-cover group-hover:scale-110 transition-transform duration-300"
                  />
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
