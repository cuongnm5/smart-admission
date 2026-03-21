import { useState, useCallback } from "react";
import HeroSection from "@/components/HeroSection";
import ManualProfileForm from "@/components/ManualProfileForm";
import AnalysisScreen from "@/components/AnalysisScreen";
import ResultsDashboard from "@/components/ResultsDashboard";
import type { StudentProfile } from "@/lib/admissionEngine";
import type { StudentMatchRequest, UniversityPipelineResponse } from "@/lib/api";

function profileFromRequest(req: StudentMatchRequest): StudentProfile {
  const rawId = req.student_id ?? "";
  const name = req.student_info?.name ?? (rawId === "unknown" ? "" : rawId.replace(/_/g, " "));
  const gpa = req.academic?.gpa?.[0]?.value ?? 3.0;
  const sat = req.test_scores?.sat?.total ?? 1200;
  const ielts = req.test_scores?.english_tests?.[0]?.score ?? 0;
  return {
    name,
    gpa,
    sat,
    ielts,
    major: req.intended_major ?? "",
    activities: (req.extracurriculars ?? []).map((e) => e.activity_name),
    awards: (req.awards ?? []).map((a) => a.award_name),
    leadershipRoles: (req.leadership ?? []).length,
    communityService: false,
    researchExperience: (req.projects ?? []).length > 0,
  };
}

type AppState = "landing" | "manual" | "analyzing" | "results";

export default function Index() {
  const [state, setState] = useState<AppState>("landing");
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [parsedRequest, setParsedRequest] = useState<StudentMatchRequest | null>(null);
  const [missingFields, setMissingFields] = useState<string[]>([]);
  const [apiResult, setApiResult] = useState<UniversityPipelineResponse | null>(null);
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [extractionComplete, setExtractionComplete] = useState(false);
  const [extractedRequest, setExtractedRequest] = useState<StudentMatchRequest | null>(null);

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

  const handleAnalysisComplete = useCallback((result: UniversityPipelineResponse | null, extracted?: StudentMatchRequest) => {
    setApiResult(result);
    if (extracted) {
      setExtractedRequest(extracted);
      if (!profile) setProfile(profileFromRequest(extracted));
    }
    setState("results");
  }, [profile]);

  const handleReset = useCallback(() => {
    setProfile(null);
    setParsedRequest(null);
    setMissingFields([]);
    setApiResult(null);
    setPdfFile(null);
    setExtractionComplete(false);
    setExtractedRequest(null);
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
        <ResultsDashboard
          profile={profile}
          apiResult={apiResult}
          parsedRequest={extractedRequest ?? parsedRequest}
          onReset={handleReset}
        />
      ) : null;
  }
}
