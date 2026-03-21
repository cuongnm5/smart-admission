import { useState, useCallback } from "react";
import HeroSection from "@/components/HeroSection";
import ManualProfileForm from "@/components/ManualProfileForm";
import AnalysisScreen from "@/components/AnalysisScreen";
import ResultsDashboard from "@/components/ResultsDashboard";
import type { StudentProfile } from "@/lib/admissionEngine";
import type { StudentMatchRequest, UniversityPipelineResponse } from "@/lib/api";

type AppState = "landing" | "manual" | "analyzing" | "results";

export default function Index() {
  const [state, setState] = useState<AppState>("landing");
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [parsedRequest, setParsedRequest] = useState<StudentMatchRequest | null>(null);
  const [missingFields, setMissingFields] = useState<string[]>([]);
  const [apiResult, setApiResult] = useState<UniversityPipelineResponse | null>(null);
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [extractionComplete, setExtractionComplete] = useState(false);

  // User dropped a CV → go straight to analyzing (extraction step)
  const handleFileDropped = useCallback((file: File) => {
    setPdfFile(file);
    setExtractionComplete(false);
    setState("analyzing");
  }, []);

  // User clicked "Enter manually"
  const handleEnterManually = useCallback(() => {
    setPdfFile(null);
    setParsedRequest(null);
    setMissingFields([]);
    setState("manual");
  }, []);

  // AnalysisScreen found missing fields during extraction → show manual form
  const handleNeedManualInput = useCallback((partial: StudentMatchRequest, missing: string[]) => {
    setParsedRequest(partial);
    setMissingFields(missing);
    setPdfFile(null);
    setState("manual");
  }, []);

  // Manual form submitted → go to analyzing with extraction step already done
  const handleManualComplete = useCallback((p: StudentProfile, req: StudentMatchRequest) => {
    setProfile(p);
    setParsedRequest(req);
    setPdfFile(null);
    setExtractionComplete(true);
    setState("analyzing");
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
    setPdfFile(null);
    setExtractionComplete(false);
    setState("landing");
  }, []);

  switch (state) {
    case "landing":
      return (
        <HeroSection
          onFileDropped={handleFileDropped}
          onEnterManually={handleEnterManually}
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
      return (
        <AnalysisScreen
          key={extractionComplete ? "post-manual" : "from-pdf"}
          studentName={profile?.name}
          profile={profile}
          parsedRequest={parsedRequest}
          pdfFile={pdfFile}
          extractionComplete={extractionComplete}
          onNeedManualInput={handleNeedManualInput}
          onComplete={handleAnalysisComplete}
        />
      );

    case "results":
      return profile ? (
        <ResultsDashboard profile={profile} apiResult={apiResult} onReset={handleReset} />
      ) : null;
  }
}
