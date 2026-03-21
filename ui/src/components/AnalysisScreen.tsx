import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Search, BarChart3, CheckCircle2, AlertCircle } from "lucide-react";
import type { StudentProfile } from "@/lib/admissionEngine";
import { matchAndAnalyze, matchAndAnalyzeDirect, type StudentMatchRequest, type UniversityPipelineResponse } from "@/lib/api";

interface AnalysisScreenProps {
  studentName: string;
  profile: StudentProfile;
  /** When provided (PDF upload flow), sent directly to the pipeline without re-mapping. */
  parsedRequest?: StudentMatchRequest | null;
  onComplete: (result: UniversityPipelineResponse | null) => void;
}

const STEPS = [
  { icon: Brain, label: "Analyzing your academic strength…", duration: 1800 },
  { icon: Search, label: "Evaluating extracurricular impact…", duration: 1500 },
  { icon: BarChart3, label: "Matching with 500+ universities…", duration: 2000 },
  { icon: CheckCircle2, label: "Generating personalized recommendations…", duration: 1200 },
];

const TOTAL_DURATION = STEPS.reduce((a, b) => a + b.duration, 0);

export default function AnalysisScreen({ studentName, profile, parsedRequest, onComplete }: AnalysisScreenProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const apiResultRef = useRef<UniversityPipelineResponse | null>(null);
  const apiDoneRef = useRef(false);
  const animDoneRef = useRef(false);

  // Kick off API call immediately
  useEffect(() => {
    const call = parsedRequest ? matchAndAnalyzeDirect(parsedRequest) : matchAndAnalyze(profile);
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
  }, []);

  // Drive the loading animation; wait for API if it hasn't finished yet
  useEffect(() => {
    let totalElapsed = 0;

    const interval = setInterval(() => {
      totalElapsed += 50;
      setProgress(Math.min((totalElapsed / TOTAL_DURATION) * 100, 100));

      let elapsed = 0;
      for (let i = 0; i < STEPS.length; i++) {
        elapsed += STEPS[i].duration;
        if (totalElapsed < elapsed) { setCurrentStep(i); break; }
        if (i === STEPS.length - 1) setCurrentStep(STEPS.length);
      }
    }, 50);

    const timeout = setTimeout(() => {
      clearInterval(interval);
      animDoneRef.current = true;
      if (apiDoneRef.current) {
        onComplete(apiResultRef.current);
      }
      // else: API call will call onComplete when it finishes
    }, TOTAL_DURATION + 500);

    return () => { clearInterval(interval); clearTimeout(timeout); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
          Analyzing {studentName}'s Profile
        </motion.h2>
        <p className="text-primary-foreground/50 text-sm mb-10">
          Our AI is evaluating your profile across multiple dimensions
        </p>

        <div className="w-full h-1.5 bg-primary-foreground/10 rounded-full mb-10 overflow-hidden">
          <motion.div
            className="h-full bg-accent rounded-full"
            style={{ width: `${progress}%` }}
            transition={{ duration: 0.1 }}
          />
        </div>

        <div className="space-y-4 text-left">
          {STEPS.map((step, i) => {
            const isActive = i === currentStep;
            const isDone = i < currentStep;
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: i <= currentStep ? 1 : 0.3, x: 0 }}
                transition={{ duration: 0.5, delay: i * 0.15 }}
                className={`flex items-center gap-3 rounded-xl px-4 py-3 transition-colors ${
                  isActive ? "bg-accent/10 border border-accent/20" : isDone ? "bg-primary-foreground/5" : ""
                }`}
              >
                <step.icon className={`w-4 h-4 flex-shrink-0 ${isDone ? "text-accent" : isActive ? "text-accent animate-pulse-soft" : "text-primary-foreground/30"}`} />
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
