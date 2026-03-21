import { useCallback, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Brain, Sparkles, Target, Upload, FileText } from "lucide-react";

interface HeroSectionProps {
  onFileDropped: (file: File) => void;
  onEnterManually: () => void;
}

const features = [
  { icon: Brain, label: "Explainable AI", desc: "Understand why each school is recommended" },
  { icon: Target, label: "Smart Strategy", desc: "Balanced Reach / Target / Safety portfolio" },
  { icon: Sparkles, label: "What-if Simulator", desc: "See how improvements change your odds" },
];

export default function HeroSection({ onFileDropped, onEnterManually }: HeroSectionProps) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const processFile = useCallback(
    (file: File) => {
      if (!file.name.toLowerCase().endsWith(".pdf")) return;
      onFileDropped(file);
    },
    [onFileDropped]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => setDragging(false), []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) processFile(file);
    },
    [processFile]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) processFile(file);
    },
    [processFile]
  );

  return (
    <div className="min-h-screen bg-hero-gradient flex flex-col">
      <nav className="flex items-center justify-between px-6 py-5 md:px-12">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-accent-foreground" />
          </div>
          <span className="text-primary-foreground font-semibold text-lg tracking-tight">Smart Admission</span>
        </div>
        <button
          onClick={onEnterManually}
          className="text-sm text-primary-foreground/70 hover:text-primary-foreground transition-colors"
        >
          Enter manually →
        </button>
      </nav>

      <div className="flex-1 flex flex-col items-center justify-center px-6 text-center max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          className="mb-4"
        >
          <span className="inline-flex items-center gap-1.5 rounded-full border border-accent/30 bg-accent/10 px-3 py-1 text-xs font-medium text-accent">
            <Sparkles className="w-3 h-3" /> AI-Powered Admission Intelligence
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="text-4xl md:text-6xl lg:text-7xl font-bold text-primary-foreground leading-[1.05] mb-6"
        >
          Know your chances{" "}
          <span className="text-gradient">before you apply.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="text-primary-foreground/60 text-lg md:text-xl max-w-2xl mb-10 leading-relaxed"
        >
          Our AI analyzes your profile against 500+ universities to predict admission probability,
          explain every recommendation, and build your optimal application strategy.
        </motion.p>

        {/* CV Drop Zone */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="w-full max-w-md"
        >
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            className={`cursor-pointer rounded-2xl border-2 border-dashed px-8 py-10 text-center transition-colors ${
              dragging
                ? "border-accent bg-accent/10"
                : "border-primary-foreground/20 bg-primary-foreground/5 hover:border-accent/50 hover:bg-accent/5"
            }`}
          >
            <div className="flex flex-col items-center gap-3">
              {dragging ? (
                <FileText className="w-8 h-8 text-accent" />
              ) : (
                <Upload className="w-8 h-8 text-primary-foreground/40" />
              )}
              <div>
                <p className="text-primary-foreground font-medium text-sm">
                  {dragging ? "Drop your CV here" : "Drop your CV / resume"}
                </p>
                <p className="text-primary-foreground/40 text-xs mt-1">PDF · click to browse</p>
              </div>
            </div>
            <input
              ref={inputRef}
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleChange}
            />
          </div>

          <p className="mt-4 text-primary-foreground/40 text-sm">
            or{" "}
            <button
              onClick={(e) => { e.stopPropagation(); onEnterManually(); }}
              className="text-accent hover:text-accent/80 transition-colors underline underline-offset-2"
            >
              enter your profile manually
            </button>
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20 w-full"
        >
          {features.map((f, i) => (
            <motion.div
              key={f.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 + i * 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="rounded-2xl border border-primary-foreground/10 bg-primary-foreground/5 backdrop-blur-sm p-6 text-left"
            >
              <f.icon className="w-5 h-5 text-accent mb-3" />
              <h3 className="text-primary-foreground font-semibold text-sm mb-1">{f.label}</h3>
              <p className="text-primary-foreground/50 text-sm">{f.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>

      <div className="py-6 text-center text-primary-foreground/30 text-xs">
        Built with Explainable AI · Decision Intelligence for Education
      </div>
    </div>
  );
}
