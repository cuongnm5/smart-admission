import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { ArrowUpRight, TrendingUp, Lightbulb, GraduationCap, Trophy, Users, Sparkles, RotateCcw, BookOpen, DollarSign, Award, FlaskConical, ChevronDown } from "lucide-react";
import type { StudentProfile, SchoolResult, ProfileStrength, ImprovementSuggestion } from "@/lib/admissionEngine";
import { getTopSchools, calculateProfileStrength, getImprovementSuggestions } from "@/lib/admissionEngine";
import { pipelineResponseToSchools, type UniversityPipelineResponse, type StudentMatchRequest } from "@/lib/api";
import SchoolCard from "./SchoolCard";
import WhatIfSimulator from "./WhatIfSimulator";

interface ResultsDashboardProps {
  profile: StudentProfile;
  apiResult: UniversityPipelineResponse | null;
  parsedRequest?: StudentMatchRequest | null;
  onReset: () => void;
}

function Tag({ children, color = "default" }: { children: React.ReactNode; color?: "default" | "accent" | "green" | "yellow" }) {
  const cls = {
    default: "bg-muted text-muted-foreground",
    accent: "bg-accent/10 text-accent",
    green: "bg-emerald-500/10 text-emerald-400",
    yellow: "bg-amber-500/10 text-amber-400",
  }[color];
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cls}`}>
      {children}
    </span>
  );
}

function ProfileSnapshot({ profile, request }: { profile: StudentProfile; request?: StudentMatchRequest | null }) {
  const [expanded, setExpanded] = useState(false);

  const gpa = profile.gpa;
  const sat = profile.sat;
  const ielts = profile.ielts || request?.test_scores?.english_tests?.[0]?.score;
  const budget = request?.financial?.budget_per_year;
  const currency = request?.financial?.currency ?? "USD";
  const needScholarship = request?.financial?.need_scholarship;

  const activities = profile.activities.length
    ? profile.activities
    : (request?.extracurriculars ?? []).map((e) => e.activity_name);

  const awards = profile.awards.length
    ? profile.awards
    : (request?.awards ?? []).map((a) => a.award_name);

  const leadership = profile.leadershipRoles > 0
    ? profile.leadershipRoles
    : (request?.leadership ?? []).length;

  const research = profile.researchExperience || (request?.projects ?? []).length > 0;

  const stat = (label: string, value: string | number | null | undefined, suffix = "") =>
    value != null && value !== 0 && value !== "" ? (
      <div className="flex flex-col gap-0.5">
        <span className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</span>
        <span className="text-sm font-bold font-mono text-foreground">{value}{suffix}</span>
      </div>
    ) : null;

  return (
    <div className="bg-card rounded-2xl border border-border overflow-hidden">
      {/* Header row — always visible */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center gap-4 px-6 py-4 text-left hover:bg-muted/20 transition-colors"
      >
        <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
          <BookOpen className="w-4 h-4 text-accent" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-foreground">{profile.name || "Your Profile"}</p>
          <p className="text-xs text-muted-foreground">{profile.major} · GPA {gpa.toFixed(2)} · SAT {sat}</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-xs text-muted-foreground hidden sm:inline">
            {expanded ? "Hide details" : "View extracted data"}
          </span>
          <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform duration-200 ${expanded ? "rotate-180" : ""}`} />
        </div>
      </button>

      {/* Expanded details */}
      {expanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.25 }}
          className="border-t border-border"
        >
          <div className="px-6 py-5 grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Academic */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 mb-3">
                <GraduationCap className="w-3.5 h-3.5 text-accent" />
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Academic</span>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {stat("GPA", gpa.toFixed(2))}
                {stat("SAT", sat)}
                {stat("IELTS", ielts)}
              </div>
            </div>

            {/* Extracurriculars */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 mb-3">
                <Award className="w-3.5 h-3.5 text-accent" />
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Activities & Awards</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {activities.slice(0, 5).map((a) => <Tag key={a}>{a}</Tag>)}
                {activities.length > 5 && <Tag>+{activities.length - 5} more</Tag>}
                {awards.slice(0, 3).map((a) => <Tag key={a} color="yellow">{a}</Tag>)}
              </div>
              <div className="flex flex-wrap gap-2 pt-1">
                {leadership > 0 && (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Users className="w-3 h-3" /> {leadership} leadership role{leadership !== 1 ? "s" : ""}
                  </div>
                )}
                {research && (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <FlaskConical className="w-3 h-3" /> Research experience
                  </div>
                )}
              </div>
            </div>

            {/* Financial */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 mb-3">
                <DollarSign className="w-3.5 h-3.5 text-accent" />
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Financial</span>
              </div>
              {budget ? (
                <div className="flex flex-col gap-0.5">
                  <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Annual Budget</span>
                  <span className="text-sm font-bold font-mono text-foreground">
                    {currency} {budget.toLocaleString()}
                  </span>
                </div>
              ) : (
                <span className="text-xs text-muted-foreground">Not specified</span>
              )}
              {needScholarship && (
                <Tag color="green">Financial aid requested</Tag>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

function ScoreRing({ value, label, color }: { value: number; label: string; color: string }) {
  const circumference = 2 * Math.PI * 36;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-20 h-20">
        <svg className="w-20 h-20 -rotate-90" viewBox="0 0 80 80">
          <circle cx="40" cy="40" r="36" fill="none" stroke="hsl(var(--muted))" strokeWidth="4" />
          <motion.circle
            cx="40" cy="40" r="36" fill="none" stroke={color} strokeWidth="4"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-bold text-foreground font-mono">{value}</span>
        </div>
      </div>
      <span className="text-xs text-muted-foreground font-medium">{label}</span>
    </div>
  );
}

export default function ResultsDashboard({ profile, apiResult, parsedRequest, onReset }: ResultsDashboardProps) {
  const [simProfile, setSimProfile] = useState(profile);
  const strength = useMemo(() => calculateProfileStrength(simProfile), [simProfile]);
  const isSimulating = simProfile.sat !== profile.sat || simProfile.gpa !== profile.gpa || simProfile.leadershipRoles !== profile.leadershipRoles;

  // Use API results for initial display; fall back to local engine when simulating or no API result
  const schools = useMemo<SchoolResult[]>(() => {
    if (!isSimulating && apiResult) return pipelineResponseToSchools(apiResult);
    return getTopSchools(simProfile);
  }, [isSimulating, apiResult, simProfile]);

  const suggestions = useMemo(() => getImprovementSuggestions(simProfile, schools), [simProfile, schools]);

  const reachCount = schools.filter((s) => s.category === "reach").length;
  const targetCount = schools.filter((s) => s.category === "target").length;
  const safetyCount = schools.filter((s) => s.category === "safety").length;

  const fadeUp = {
    initial: { opacity: 0, y: 20, filter: "blur(4px)" },
    animate: { opacity: 1, y: 0, filter: "blur(0px)" },
    transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] as const },
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-accent-foreground" />
            </div>
            <div>
              <h1 className="font-bold text-foreground">ETEST Smart Admission AI</h1>
              <p className="text-xs text-muted-foreground">Results for {profile.name}</p>
            </div>
          </div>
          <button
            onClick={onReset}
            className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-xs font-medium text-muted-foreground hover:text-foreground hover:border-foreground/20 transition-colors active:scale-95"
          >
            <RotateCcw className="w-3 h-3" /> New Analysis
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8 space-y-10">
        {/* Extracted Profile Snapshot */}
        <motion.div {...fadeUp}>
          <ProfileSnapshot profile={profile} request={parsedRequest} />
        </motion.div>

        {/* Section 1: Profile Summary */}
        <motion.section {...fadeUp}>
          <h2 className="text-lg font-bold text-foreground mb-1 flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-accent" /> Profile Strength
          </h2>
          <p className="text-sm text-muted-foreground mb-6">AI-evaluated across academic, extracurricular, and fit dimensions</p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 bg-card rounded-2xl p-6 bg-card-glow">
            <ScoreRing value={strength.overall} label="Overall" color="hsl(var(--accent))" />
            <ScoreRing value={strength.academic} label="Academic" color="hsl(168, 72%, 50%)" />
            <ScoreRing value={strength.activities} label="Activities" color="hsl(42, 92%, 56%)" />
            <ScoreRing value={strength.fit} label="Fit Score" color="hsl(262, 60%, 55%)" />
          </div>
        </motion.section>

        {/* Section 2: Top 10 Schools */}
        <motion.section {...fadeUp} transition={{ ...fadeUp.transition, delay: 0.15 } as const}>
          <div className="flex items-center justify-between mb-1">
            <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
              <Trophy className="w-5 h-5 text-accent" /> Top 10 Best-Fit Schools
            </h2>
            {isSimulating && (
              <span className="inline-flex items-center gap-1 text-xs font-medium text-accent bg-accent/10 rounded-full px-2.5 py-1">
                <TrendingUp className="w-3 h-3" /> Simulated
              </span>
            )}
          </div>
          <p className="text-sm text-muted-foreground mb-4">
            Balanced portfolio: <span className="text-reach font-medium">{reachCount} Reach</span> · <span className="text-target font-medium">{targetCount} Target</span> · <span className="text-safety font-medium">{safetyCount} Safety</span>
          </p>

          <div className="grid gap-4">
            {schools.map((school, i) => (
              <motion.div
                key={school.name}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 + i * 0.06, ease: [0.16, 1, 0.3, 1] }}
              >
                <SchoolCard school={school} rank={i + 1} />
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Section 3: What-if Simulator */}
        <motion.section {...fadeUp} transition={{ ...fadeUp.transition, delay: 0.3 } as const}>
          <h2 className="text-lg font-bold text-foreground mb-1 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-accent" /> What-if Simulator
          </h2>
          <p className="text-sm text-muted-foreground mb-6">Adjust your stats and see how your admission chances change in real-time</p>
          <WhatIfSimulator profile={profile} simProfile={simProfile} onProfileChange={setSimProfile} />
        </motion.section>

        {/* Section 4: Improvement Suggestions */}
        <motion.section {...fadeUp} transition={{ ...fadeUp.transition, delay: 0.45 } as const}>
          <h2 className="text-lg font-bold text-foreground mb-1 flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-accent" /> Improve Your Chances
          </h2>
          <p className="text-sm text-muted-foreground mb-6">Personalized AI suggestions to strengthen your application</p>

          <div className="space-y-3">
            {suggestions.map((sug, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.5 + i * 0.08 }}
                className="bg-card rounded-xl p-5 bg-card-glow flex items-start gap-4"
              >
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                  sug.category === "academic" ? "bg-accent/10" : sug.category === "extracurricular" ? "bg-target/10" : "bg-reach/10"
                }`}>
                  {sug.category === "academic" ? (
                    <GraduationCap className="w-4 h-4 text-accent" />
                  ) : sug.category === "extracurricular" ? (
                    <Users className="w-4 h-4 text-target" />
                  ) : (
                    <ArrowUpRight className="w-4 h-4 text-reach" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground">{sug.action}</p>
                  <p className="text-xs text-accent font-medium mt-1">{sug.impact}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <span className="text-lg font-bold text-accent font-mono">+{sug.delta}%</span>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>
      </div>

      <div className="text-center py-10 text-xs text-muted-foreground">
        ETEST Smart Admission AI · Powered by Explainable AI
      </div>
    </div>
  );
}
