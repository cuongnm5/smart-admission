import { useState, useCallback } from "react";
import HeroSection from "@/components/HeroSection";
import PDFUpload from "@/components/PDFUpload";
import ManualProfileForm from "@/components/ManualProfileForm";
import AnalysisScreen from "@/components/AnalysisScreen";
import ResultsDashboard from "@/components/ResultsDashboard";
import type { StudentProfile } from "@/lib/admissionEngine";
import type { StudentMatchRequest, UniversityPipelineResponse } from "@/lib/api";
import { studentProfileFromRequest } from "@/lib/api";

type AppState = "landing" | "upload" | "manual" | "analyzing" | "results";

export default function Index() {
  const [state, setState] = useState<AppState>("landing");
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [parsedRequest, setParsedRequest] = useState<StudentMatchRequest | null>(null);
  const [missingFields, setMissingFields] = useState<string[]>([]);
  const [apiResult, setApiResult] = useState<UniversityPipelineResponse | null>(null);

  // PDF uploaded — go to manual form to confirm / fill missing fields
  const handleUploadComplete = useCallback((request: StudentMatchRequest, missing: string[]) => {
    setParsedRequest(request);
    setMissingFields(missing);
    setState("manual");
  }, []);

  // Manual form submitted with all required fields filled
  const handleManualComplete = useCallback((p: StudentProfile, req: StudentMatchRequest) => {
    setProfile(p);
    setParsedRequest(req);
    setState("analyzing");
  }, []);

  // Skip PDF — go straight to blank manual form
  const handleSkipUpload = useCallback(() => {
    setParsedRequest(null);
    setMissingFields([]);
    setState("manual");
  }, []);

  const handleAnalysisComplete = useCallback((result: UniversityPipelineResponse | null) => {
    setApiResult(result);
    setState("results");
  }, []);

  const handleReset = useCallback(() => {
    setProfile(null);
    setParsedRequest(null);
    setMissingFields([]);
    setApiResult(null);
    setState("landing");
  }, []);

  switch (state) {
    case "landing":
      return <HeroSection onStart={() => setState("upload")} />;

    case "upload":
      return (
        <PDFUpload
          onComplete={handleUploadComplete}
          onSkip={handleSkipUpload}
        />
      );

    case "manual":
      return (
        <ManualProfileForm
          key={parsedRequest ? "prefilled" : "empty"}
          initialData={parsedRequest ?? undefined}
          missingFields={missingFields}
          onComplete={handleManualComplete}
        />
      );

    case "analyzing":
      return profile ? (
        <AnalysisScreen
          studentName={profile.name}
          profile={profile}
          parsedRequest={parsedRequest}
          onComplete={handleAnalysisComplete}
        />
      ) : null;

    case "results":
      return profile ? (
        <ResultsDashboard profile={profile} apiResult={apiResult} onReset={handleReset} />
      ) : null;
  }
}
