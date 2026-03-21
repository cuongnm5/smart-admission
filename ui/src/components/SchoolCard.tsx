import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, MapPin, Hash } from "lucide-react";
import type { SchoolResult } from "@/lib/admissionEngine";

interface SchoolCardProps {
  school: SchoolResult;
  rank: number;
}

const categoryConfig = {
  reach: { label: "Reach", dotClass: "bg-reach", textClass: "text-reach", bgClass: "bg-reach/10" },
  target: { label: "Target", dotClass: "bg-target", textClass: "text-target", bgClass: "bg-target/10" },
  safety: { label: "Safety", dotClass: "bg-safety", textClass: "text-safety", bgClass: "bg-safety/10" },
};

export default function SchoolCard({ school, rank }: SchoolCardProps) {
  const [expanded, setExpanded] = useState(false);
  const cat = categoryConfig[school.category];

  return (
    <div
      className="bg-card rounded-xl bg-card-glow hover:bg-card-glow-hover transition-shadow cursor-pointer overflow-hidden"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-center gap-4 px-5 py-4">
        <span className="text-xs font-mono text-muted-foreground w-6 text-right flex-shrink-0">
          #{rank}
        </span>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <h3 className="font-semibold text-sm text-foreground truncate">{school.name}</h3>
            <span className={`inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full ${cat.bgClass} ${cat.textClass}`}>
              {cat.label}
            </span>
          </div>
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{school.location}</span>
            <span className="flex items-center gap-1"><Hash className="w-3 h-3" />Rank {school.ranking}</span>
          </div>
        </div>

        {/* Probability bar */}
        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="w-24 md:w-32">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-muted-foreground">Probability</span>
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

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 pt-1 border-t border-border">
              <p className="text-xs font-semibold text-foreground mb-2 mt-3">AI Analysis</p>
              <ul className="space-y-1.5">
                {school.explanation.map((exp, i) => (
                  <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                    <span className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${cat.dotClass}`} />
                    {exp}
                  </li>
                ))}
              </ul>
              <div className="grid grid-cols-3 gap-4 mt-4 pt-3 border-t border-border">
                <div>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Accept Rate</p>
                  <p className="text-sm font-semibold font-mono text-foreground">{school.acceptanceRate}%</p>
                </div>
                <div>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Avg SAT</p>
                  <p className="text-sm font-semibold font-mono text-foreground">{school.avgSAT}</p>
                </div>
                <div>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Major Fit</p>
                  <p className="text-sm font-semibold font-mono text-foreground">{school.majorStrength}</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
