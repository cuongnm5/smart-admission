import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Search, BarChart3, CheckCircle2, AlertCircle, FileText, Loader2 } from "lucide-react";
import type { StudentProfile } from "@/lib/admissionEngine";
import {
  parseProfileFromPDF,
  matchAndAnalyze,
  matchAndAnalyzeDirect,
  type StudentMatchRequest,
  type UniversityPipelineResponse,
} from "@/lib/api";

interface AnalysisScreenProps {
  studentName?: string;
  profile?: StudentProfile | null;
  parsedRequest?: StudentMatchRequest | null;
  /** If provided, step 1 runs parseProfileFromPDF on this file */
  pdfFile?: File | null;
  /** If true, step 1 is shown as already done (came from manual form) */
  extractionComplete?: boolean;
  onNeedManualInput?: (partial: StudentMatchRequest, missing: string[]) => void;
  onComplete: (result: UniversityPipelineResponse | null) => void;
}

const DEFAULT_MISSING = ["intended_major", "academic.gpa", "financial.budget_per_year", "test_scores"];

const ANALYSIS_STEPS = [
  { icon: Brain, label: "Analyzing your academic strength…", duration: 1800 },
  { icon: Search, label: "Matching with 500+ universities…", duration: 2000 },
  { icon: BarChart3, label: "Scoring & ranking results…", duration: 1500 },
  { icon: CheckCircle2, label: "Generating personalized recommendations…", duration: 1200 },
];
const TOTAL_ANALYSIS_DURATION = ANALYSIS_STEPS.reduce((a, b) => a + b.duration, 0);

export default function AnalysisScreen({
  studentName,
  profile,
  parsedRequest,
  pdfFile,
  extractionComplete,
  onNeedManualInput,
  onComplete,
}: AnalysisScreenProps) {
  // phase: "extracting" = waiting for PDF parse; "analyzing" = running analysis steps
  const [phase, setPhase] = useState<"extracting" | "analyzing">(
    pdfFile && !extractionComplete ? "extracting" : "analyzing"
  );
  const [extractionDone, setExtractionDone] = useState(!pdfFile || !!extractionComplete);
  const [analysisStep, setAnalysisStep] = useState(0); // which ANALYSIS_STEPS step is active
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [displayName, setDisplayName] = useState<string>(studentName || "");

  const apiResultRef = useRef<UniversityPipelineResponse | null>(null);
  const apiDoneRef = useRef(false);
  const animDoneRef = useRef(false);
  const extractedRequestRef = useRef<StudentMatchRequest | null>(null);

  // ── Phase 1: PDF extraction ──────────────────────────────────────────────
  useEffect(() => {
    if (phase !== "extracting" || !pdfFile) return;

    parseProfileFromPDF(pdfFile)
      .then((res) => {
        if (res.error || !res.data || (res.missing_fields && res.missing_fields.length > 0)) {
          // Need manual input
          onNeedManualInput?.(
            res.data ?? ({} as StudentMatchRequest),
            res.missing_fields?.length ? res.missing_fields : DEFAULT_MISSING
          );
          return;
        }
        // Success — remember extracted data, advance to analysis
        extractedRequestRef.current = res.data;
        const name = res.data.student_info?.name ?? "";
        if (name) setDisplayName(name);
        setExtractionDone(true);
        setPhase("analyzing");
      })
      .catch(() => {
        onNeedManualInput?.({} as StudentMatchRequest, DEFAULT_MISSING);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Phase 2: Analysis API call ───────────────────────────────────────────
  useEffect(() => {
    if (phase !== "analyzing") return;

    const req = extractedRequestRef.current ?? parsedRequest;
    const call = req ? matchAndAnalyzeDirect(req) : matchAndAnalyze(profile!);
    call
      .then((result) => {
        apiResultRef.current = result;
        apiDoneRef.current = true;
        if (animDoneRef.current) onComplete(result);
      })
      .catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
        apiDoneRef.current = true;
        if (animDoneRef.current) onComplete(null);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase]);

  // ── Phase 2: Analysis animation ──────────────────────────────────────────
  useEffect(() => {
    if (phase !== "analyzing") return;

    let totalElapsed = 0;
    const interval = setInterval(() => {
      totalElapsed += 50;
      setProgress(Math.min((totalElapsed / TOTAL_ANALYSIS_DURATION) * 100, 100));
      let elapsed = 0;
      for (let i = 0; i < ANALYSIS_STEPS.length; i++) {
        elapsed += ANALYSIS_STEPS[i].duration;
        if (totalElapsed < elapsed) { setAnalysisStep(i); break; }
        if (i === ANALYSIS_STEPS.length - 1) setAnalysisStep(ANALYSIS_STEPS.length);
      }
    }, 50);

    const timeout = setTimeout(() => {
      clearInterval(interval);
      animDoneRef.current = true;
      if (apiDoneRef.current) onComplete(apiResultRef.current);
    }, TOTAL_ANALYSIS_DURATION + 500);

    return () => { clearInterval(interval); clearTimeout(timeout); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase]);

  const name = displayName || studentName || "";

  return (
    <div className="min-h-screen bg-hero-gradient flex items-center justify-center px-6">
      <div className="max-w-md w-full text-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 mx-auto mb-8 rounded-2xl bg-accent/20 border border-accent/30 flex items-center justify-center"
        >
          <Brain className="w-7 h-7 text-accent" />
        </motion.div>

        <motion.h2
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-2xl font-bold text-primary-foreground mb-2"
        >
          {name ? `Analyzing ${name}'s Profile` : "Analyzing Your Profile"}
        </motion.h2>
        <p className="text-primary-foreground/50 text-sm mb-10">
          Our AI is evaluating your profile across multiple dimensions
        </p>

        {/* Progress bar — only visible in analysis phase */}
        <div className="w-full h-1.5 bg-primary-foreground/10 rounded-full mb-10 overflow-hidden">
          {phase === "analyzing" ? (
            <motion.div
              className="h-full bg-accent rounded-full"
              style={{ width: `${progress}%` }}
              transition={{ duration: 0.1 }}
            />
          ) : (
            <motion.div
              className="h-full bg-accent/60 rounded-full"
              animate={{ x: ["-100%", "100%"] }}
              transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut" }}
              style={{ width: "40%" }}
            />
          )}
        </div>

        <div className="space-y-4 text-left">
          {/* Step 0 — Extraction */}
          <motion.div
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className={`flex items-center gap-3 rounded-xl px-4 py-3 transition-colors ${
              phase === "extracting"
                ? "bg-accent/10 border border-accent/20"
                : extractionDone
                ? "bg-primary-foreground/5"
                : ""
            }`}
          >
            {phase === "extracting" ? (
              <Loader2 className="w-4 h-4 flex-shrink-0 text-accent animate-spin" />
            ) : (
              <FileText className={`w-4 h-4 flex-shrink-0 ${extractionDone ? "text-accent" : "text-primary-foreground/30"}`} />
            )}
            <span className={`text-sm ${phase === "extracting" ? "text-primary-foreground" : extractionDone ? "text-accent" : "text-primary-foreground/30"}`}>
              {pdfFile && !extractionComplete ? "Extracting your profile from CV…" : "Profile ready"}
            </span>
            {extractionDone && <CheckCircle2 className="w-4 h-4 text-accent ml-auto" />}
          </motion.div>

          {/* Steps 1-4 — Analysis */}
          {ANALYSIS_STEPS.map((step, i) => {
            const isActive = phase === "analyzing" && i === analysisStep;
            const isDone = phase === "analyzing" ? i < analysisStep : false;
            const isPending = phase === "extracting";
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -16 }}
                animate={{
                  opacity: isPending ? 0.2 : i <= analysisStep || isDone ? 1 : 0.3,
                  x: 0,
                }}
                transition={{ duration: 0.5, delay: (i + 1) * 0.15 }}
                className={`flex items-center gap-3 rounded-xl px-4 py-3 transition-colors ${
                  isActive ? "bg-accent/10 border border-accent/20" : isDone ? "bg-primary-foreground/5" : ""
                }`}
              >
                <step.icon
                  className={`w-4 h-4 flex-shrink-0 ${
                    isDone ? "text-accent" : isActive ? "text-accent animate-pulse-soft" : "text-primary-foreground/30"
                  }`}
                />
                <span className={`text-sm ${isDone ? "text-accent" : isActive ? "text-primary-foreground" : "text-primary-foreground/30"}`}>
                  {step.label}
                </span>
                {isDone && <CheckCircle2 className="w-4 h-4 text-accent ml-auto" />}
              </motion.div>
            );
          })}
        </div>

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 flex items-center gap-2 text-xs text-amber-400/80 bg-amber-400/10 rounded-lg px-4 py-3 text-left"
            >
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>API unavailable — showing local estimates instead.</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
