import { useCallback, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, AlertCircle, CheckCircle2, Loader2, Bot } from "lucide-react";
import { parseProfileFromPDF, type StudentMatchRequest } from "@/lib/api";

interface PDFUploadProps {
  onComplete: (request: StudentMatchRequest, missingFields: string[]) => void;
  onSkip: () => void;
}

type UploadState = "idle" | "dragging" | "uploading" | "done" | "error";

export default function PDFUpload({ onComplete, onSkip }: PDFUploadProps) {
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [fileName, setFileName] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const processFile = useCallback(async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setErrorMsg("Please upload a PDF file.");
      setUploadState("error");
      return;
    }
    setFileName(file.name);
    setUploadState("uploading");
    setErrorMsg(null);

    try {
      const res = await parseProfileFromPDF(file);

      if (res.error || !res.data) {
        // Parse failed entirely — go to blank manual form
        setUploadState("error");
        setErrorMsg(res.error ?? "Could not extract data from this PDF.");
        setTimeout(() => onComplete({} as StudentMatchRequest, [
          "intended_major", "academic.gpa", "financial.budget_per_year", "test_scores",
        ]), 1200);
        return;
      }

      setUploadState("done");
      setTimeout(() => onComplete(res.data!, res.missing_fields), 600);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Upload failed.");
      setUploadState("error");
      setTimeout(() => onComplete({} as StudentMatchRequest, [
        "intended_major", "academic.gpa", "financial.budget_per_year", "test_scores",
      ]), 1200);
    }
  }, [onComplete]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setUploadState("idle");
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }, [processFile]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  }, [processFile]);

  const isIdle = uploadState === "idle" || uploadState === "dragging";

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="border-b border-border px-6 py-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
          <Bot className="w-4 h-4 text-accent-foreground" />
        </div>
        <div>
          <h2 className="font-semibold text-sm text-foreground">ETEST AI Advisor</h2>
          <p className="text-xs text-muted-foreground">Upload your CV or resume to get started</p>
        </div>
        <button
          onClick={onSkip}
          className="ml-auto text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          Fill in manually →
        </button>
      </div>

      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-lg">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="text-center mb-10"
          >
            <h1 className="text-2xl font-bold text-foreground mb-2">Upload your profile</h1>
            <p className="text-sm text-muted-foreground">
              Drop your CV, resume, or academic profile as a PDF.<br />
              Our AI will extract everything it needs automatically.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            onDragOver={(e) => { e.preventDefault(); if (isIdle) setUploadState("dragging"); }}
            onDragLeave={() => { if (uploadState === "dragging") setUploadState("idle"); }}
            onDrop={handleDrop}
            onClick={() => isIdle && inputRef.current?.click()}
            className={`relative rounded-2xl border-2 border-dashed transition-all duration-200 p-12 flex flex-col items-center gap-5 text-center
              ${uploadState === "dragging" ? "border-accent bg-accent/5 scale-[1.01]" : "border-border"}
              ${isIdle ? "cursor-pointer hover:border-accent/50 hover:bg-muted/30" : "cursor-default"}
            `}
          >
            <input ref={inputRef} type="file" accept=".pdf,application/pdf" className="hidden" onChange={handleChange} />

            <AnimatePresence mode="wait">
              {uploadState === "uploading" && (
                <motion.div key="uploading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-accent/10 border border-accent/20 flex items-center justify-center">
                    <Loader2 className="w-6 h-6 text-accent animate-spin" />
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">Parsing your profile…</p>
                    <p className="text-sm text-muted-foreground mt-1">{fileName}</p>
                  </div>
                  <p className="text-xs text-muted-foreground">Our AI is extracting your academic and extracurricular data</p>
                </motion.div>
              )}

              {uploadState === "done" && (
                <motion.div key="done" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-accent/10 border border-accent/20 flex items-center justify-center">
                    <CheckCircle2 className="w-6 h-6 text-accent" />
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">Profile extracted!</p>
                    <p className="text-sm text-muted-foreground mt-1">Reviewing extracted data…</p>
                  </div>
                </motion.div>
              )}

              {uploadState === "error" && (
                <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
                    <AlertCircle className="w-6 h-6 text-amber-500" />
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">Couldn't fully parse the PDF</p>
                    <p className="text-sm text-muted-foreground mt-1">{errorMsg}</p>
                  </div>
                  <p className="text-xs text-muted-foreground">Redirecting to manual input…</p>
                </motion.div>
              )}

              {isIdle && (
                <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center gap-4">
                  <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-colors ${uploadState === "dragging" ? "bg-accent/20 border border-accent/30" : "bg-muted border border-border"}`}>
                    {uploadState === "dragging" ? <Upload className="w-6 h-6 text-accent" /> : <FileText className="w-6 h-6 text-muted-foreground" />}
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">
                      {uploadState === "dragging" ? "Drop to upload" : "Drag & drop your PDF here"}
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">or <span className="text-accent">click to browse</span></p>
                  </div>
                  <p className="text-xs text-muted-foreground">PDF only · Max 10 MB</p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {isIdle && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="mt-6 grid grid-cols-3 gap-3"
            >
              {["CV / Resume", "Academic Transcript", "Portfolio PDF"].map((label) => (
                <div key={label} className="bg-card rounded-xl px-3 py-2.5 text-center border border-border">
                  <p className="text-xs text-muted-foreground">{label}</p>
                </div>
              ))}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
