import { Metadata } from "next";
import AuthForm from "./auth-form";

export const metadata: Metadata = {
  title: "Sign In / Sign Up | Travelethic ",
  description:
    "Access your Travelethic  account or create a new one to start planning your travels with the power of AI.",
  openGraph: {
    title: "Sign In / Sign Up | Travelethic ",
    description: "Join Travelethic  and start creating personalized travel plans.",
    url: "https://tripcraft.amitwani.dev/auth",
  },
  twitter: {
    title: "Sign In / Sign Up | Travelethic ",
    description: "Join Travelethic  and start creating personalized travel plans.",
  },
};

export default function AuthPage() {
  return <AuthForm />;
}
