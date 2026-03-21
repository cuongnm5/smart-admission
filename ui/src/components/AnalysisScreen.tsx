import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Search, BarChart3, CheckCircle2 } from "lucide-react";

interface AnalysisScreenProps {
  studentName: string;
  onComplete: () => void;
}

const STEPS = [
  { icon: Brain, label: "Analyzing your academic strength…", duration: 1800 },
  { icon: Search, label: "Evaluating extracurricular impact…", duration: 1500 },
  { icon: BarChart3, label: "Matching with 500+ universities…", duration: 2000 },
  { icon: CheckCircle2, label: "Generating personalized recommendations…", duration: 1200 },
];

export default function AnalysisScreen({ studentName, onComplete }: AnalysisScreenProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let totalElapsed = 0;
    const totalDuration = STEPS.reduce((a, b) => a + b.duration, 0);
    
    const interval = setInterval(() => {
      totalElapsed += 50;
      setProgress(Math.min((totalElapsed / totalDuration) * 100, 100));

      let elapsed = 0;
      for (let i = 0; i < STEPS.length; i++) {
        elapsed += STEPS[i].duration;
        if (totalElapsed < elapsed) {
          setCurrentStep(i);
          break;
        }
        if (i === STEPS.length - 1) setCurrentStep(STEPS.length);
      }
    }, 50);

    const timeout = setTimeout(onComplete, totalDuration + 500);
    return () => { clearInterval(interval); clearTimeout(timeout); };
  }, [onComplete]);

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

        {/* Progress bar */}
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
                {isDone && (
                  <CheckCircle2 className="w-4 h-4 text-accent ml-auto" />
                )}
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
