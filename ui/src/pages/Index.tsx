import { useState, useCallback } from "react";
import HeroSection from "@/components/HeroSection";
import ChatProfileInput from "@/components/ChatProfileInput";
import AnalysisScreen from "@/components/AnalysisScreen";
import ResultsDashboard from "@/components/ResultsDashboard";
import type { StudentProfile } from "@/lib/admissionEngine";

type AppState = "landing" | "chat" | "analyzing" | "results";

export default function Index() {
  const [state, setState] = useState<AppState>("landing");
  const [profile, setProfile] = useState<StudentProfile | null>(null);

  const handleProfileComplete = useCallback((p: StudentProfile) => {
    setProfile(p);
    setState("analyzing");
  }, []);

  const handleAnalysisComplete = useCallback(() => {
    setState("results");
  }, []);

  const handleReset = useCallback(() => {
    setProfile(null);
    setState("landing");
  }, []);

  switch (state) {
    case "landing":
      return <HeroSection onStart={() => setState("chat")} />;
    case "chat":
      return <ChatProfileInput onComplete={handleProfileComplete} />;
    case "analyzing":
      return <AnalysisScreen studentName={profile?.name || "Student"} onComplete={handleAnalysisComplete} />;
    case "results":
      return profile ? <ResultsDashboard profile={profile} onReset={handleReset} /> : null;
  }
}
