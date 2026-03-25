"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Luggage, Menu, X, User } from "lucide-react";

export default function Header() {
  const router = useRouter();
  const { user, loading, logout } = useAuth();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  async function handleLogout() {
    try {
      await logout();
      toast.success("Logged out successfully");
      router.push("/");
    } catch (error) {
      toast.error("Failed to log out");
      console.error("Logout error:", error);
    }
  }

  return (
    <header className="bg-card shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4 md:py-6">
          <div className="flex items-center gap-8">
            <Link href="/" className="hover:opacity-80 transition-opacity">
              <h1 className="text-2xl font-bold text-accent">TripCraft AI</h1>
            </Link>
          </div>

          {/* Desktop Menu */}
          <nav className="hidden md:flex items-center gap-6">
            <Link
              href="/compare"
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              Compare Destinations
            </Link>
            {user && (
              <Link
                href="/plans"
                className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                <Luggage className="w-4 h-4" />
                My Plans
              </Link>
            )}
          </nav>

          <div className="hidden md:flex items-center gap-4">
            {loading ? (
              <div className="w-24 h-8 bg-muted/50 animate-pulse rounded-md" />
            ) : user ? (
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className="text-sm hidden lg:block">
                    <span className="text-muted-foreground">Welcome, </span>
                    <span className="font-medium">{user.name}</span>
                  </div>
                  {user.is_premium && (
                    <span className="text-xs bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-2 py-1 rounded-full font-semibold">
                      Premium
                    </span>
                  )}
                </div>
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  Logout
                </Button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link href="/auth">
                  <Button variant="outline" size="sm">
                    Sign In
                  </Button>
                </Link>
                <Link href="/plan">
                  <Button size="sm" className="bg-primary hover:bg-primary/90">
                    Get Started
                  </Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-muted-foreground hover:text-foreground transition-colors"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Toggle menu"
          >
            {isMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-border py-4 space-y-4">
            <nav className="space-y-3">
              <Link
                href="/compare"
                className="block text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                onClick={() => setIsMenuOpen(false)}
              >
                Compare Destinations
              </Link>
              {user && (
                <Link
                  href="/plans"
                  className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <Luggage className="w-4 h-4" />
                  My Plans
                </Link>
              )}
            </nav>

            <div className="pt-3 border-t border-border space-y-3">
              {user ? (
                <>
                  <div className="flex items-center gap-2 text-sm">
                    <User className="w-4 h-4 text-muted-foreground" />
                    <span className="font-medium">{user.name}</span>
                    {user.is_premium && (
                      <span className="text-xs bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-2 py-1 rounded-full font-semibold">
                        Premium
                      </span>
                    )}
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      handleLogout();
                      setIsMenuOpen(false);
                    }}
                    className="w-full"
                  >
                    Logout
                  </Button>
                </>
              ) : (
                <div className="space-y-2">
                  <Link href="/auth" onClick={() => setIsMenuOpen(false)}>
                    <Button variant="outline" size="sm" className="w-full">
                      Sign In
                    </Button>
                  </Link>
                  <Link href="/plan" onClick={() => setIsMenuOpen(false)}>
                    <Button size="sm" className="w-full bg-primary hover:bg-primary/90">
                      Get Started
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
