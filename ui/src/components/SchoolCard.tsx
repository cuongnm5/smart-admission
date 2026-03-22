import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, MapPin, Award, DollarSign, GraduationCap, CheckCircle2, XCircle, BookOpen } from "lucide-react";
import type { SchoolResult } from "@/lib/admissionEngine";

interface SchoolCardProps {
  school: SchoolResult;
  rank: number;
}

const categoryConfig = {
  reach:  { label: "Reach",  dotClass: "bg-reach",  textClass: "text-reach",  bgClass: "bg-reach/10"  },
  target: { label: "Target", dotClass: "bg-target", textClass: "text-target", bgClass: "bg-target/10" },
  safety: { label: "Safety", dotClass: "bg-safety", textClass: "text-safety", bgClass: "bg-safety/10" },
};

function formatTuition(amount: number | undefined): string {
  if (!amount) return "—";
  if (amount >= 1000) return `$${Math.round(amount / 1000)}K`;
  return `$${amount}`;
}

function StatChip({ label, value }: { label: string; value: string }) {
  return (
    <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
      <span className="text-muted-foreground/50">{label}</span>
      <span className="font-medium text-foreground/80">{value}</span>
    </span>
  );
}

export default function SchoolCard({ school, rank }: SchoolCardProps) {
  const [expanded, setExpanded] = useState(false);
  const cat = categoryConfig[school.category];

  return (
    <div
      className="bg-card rounded-xl bg-card-glow hover:bg-card-glow-hover transition-shadow cursor-pointer overflow-hidden"
      onClick={() => setExpanded(!expanded)}
    >
      {/* ── Collapsed row ────────────────────────────────────────────── */}
      <div className="flex items-start gap-4 px-5 py-4">
        <span className="text-xs font-mono text-muted-foreground w-6 text-right flex-shrink-0 pt-0.5">
          #{rank}
        </span>

        <div className="flex-1 min-w-0">
          {/* Name + badge */}
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-sm text-foreground truncate">{school.name}</h3>
            <span className={`inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full flex-shrink-0 ${cat.bgClass} ${cat.textClass}`}>
              {cat.label}
            </span>
          </div>

          {/* Location + rank */}
          <div className="flex items-center gap-3 text-xs text-muted-foreground mb-2">
            {school.location && school.location !== "USA" && (
              <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{school.location}</span>
            )}
            {school.subjectRank ? (
              <span className="flex items-center gap-1">
                <Award className="w-3 h-3" />
                Rank #{school.subjectRank} in {school.subjectLabel}
              </span>
            ) : school.ranking < 9999 ? (
              <span className="flex items-center gap-1">
                <Award className="w-3 h-3" />
                QS #{school.ranking}
              </span>
            ) : null}
          </div>

          {/* Key stats row */}
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
            {school.acceptanceRate > 0 && (
              <StatChip label="Accept" value={`${school.acceptanceRate}%`} />
            )}
            {school.avgSAT > 0 && (
              <StatChip label="Avg SAT" value={school.avgSAT.toString()} />
            )}
            {school.tuition && (
              <StatChip label="Tuition" value={`${formatTuition(school.tuition)}/yr`} />
            )}
            {school.majorStrength && school.majorStrength !== "—" && (
              <StatChip label="Strong in" value={school.majorStrength} />
            )}
          </div>
        </div>

        {/* Probability + chevron */}
        <div className="flex items-center gap-3 flex-shrink-0 pt-0.5">
          <div className="w-24 md:w-32">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-muted-foreground">Match</span>
              <span className={`font-bold font-mono ${cat.textClass}`}>{school.probability}%</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <motion.div
                className={`h-full rounded-full ${cat.dotClass}`}
                initial={{ width: 0 }}
                animate={{ width: `${school.probability}%` }}
                transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
              />
            </div>
          </div>
          <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${expanded ? "rotate-180" : ""}`} />
        </div>
      </div>

      {/* ── Expanded section ─────────────────────────────────────────── */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 pt-1 border-t border-border space-y-5">
              {/* Why you match */}
              <div>
                <div className="flex items-center gap-2 mt-4 mb-3">
                  <CheckCircle2 className="w-3.5 h-3.5 text-accent" />
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Why you match</p>
                </div>
                <ul className="space-y-2">
                  {school.explanation.map((exp, i) => {
                    const isPositive = !exp.toLowerCase().includes("below") && !exp.toLowerCase().includes("miss");
                    return (
                      <li key={i} className="flex items-start gap-2.5">
                        {isPositive
                          ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                          : <XCircle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
                        }
                        <span className="text-sm text-muted-foreground leading-snug">{exp}</span>
                      </li>
                    );
                  })}
                </ul>
              </div>

              {/* University details grid */}
              <div className="border-t border-border pt-4">
                <div className="flex items-center gap-2 mb-3">
                  <BookOpen className="w-3.5 h-3.5 text-accent" />
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">University info</p>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-muted/30 rounded-lg px-3 py-2.5">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 flex items-center gap-1">
                      <GraduationCap className="w-3 h-3" /> Accept Rate
                    </p>
                    <p className="text-sm font-bold font-mono text-foreground">
                      {school.acceptanceRate > 0 ? `${school.acceptanceRate}%` : "—"}
                    </p>
                  </div>
                  <div className="bg-muted/30 rounded-lg px-3 py-2.5">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 flex items-center gap-1">
                      <Hash className="w-3 h-3" /> Avg SAT
                    </p>
                    <p className="text-sm font-bold font-mono text-foreground">
                      {school.avgSAT > 0 ? school.avgSAT : "—"}
                    </p>
                  </div>
                  <div className="bg-muted/30 rounded-lg px-3 py-2.5">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 flex items-center gap-1">
                      <DollarSign className="w-3 h-3" /> Tuition/yr
                    </p>
                    <p className="text-sm font-bold font-mono text-foreground">
                      {school.tuition ? `$${school.tuition.toLocaleString()}` : "—"}
                    </p>
                  </div>
                  <div className="bg-muted/30 rounded-lg px-3 py-2.5">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 flex items-center gap-1">
                      <Award className="w-3 h-3" />
                      {school.subjectRank ? `Rank in ${school.subjectLabel}` : "Major Fit"}
                    </p>
                    <p className="text-sm font-bold text-foreground truncate">
                      {school.subjectRank ? `#${school.subjectRank}` : school.majorStrength !== "—" ? school.majorStrength : "—"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
