import { motion } from "framer-motion";
import { RotateCcw } from "lucide-react";
import type { StudentProfile } from "@/lib/admissionEngine";

interface WhatIfSimulatorProps {
  profile: StudentProfile;
  simProfile: StudentProfile;
  onProfileChange: (p: StudentProfile) => void;
}

function SimSlider({
  label,
  value,
  originalValue,
  min,
  max,
  step,
  unit,
  onChange,
}: {
  label: string;
  value: number;
  originalValue: number;
  min: number;
  max: number;
  step: number;
  unit: string;
  onChange: (v: number) => void;
}) {
  const changed = value !== originalValue;
  const diff = value - originalValue;
  
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground">{label}</label>
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold font-mono text-foreground">{value}{unit}</span>
          {changed && (
            <span className={`text-xs font-mono font-medium ${diff > 0 ? "text-accent" : "text-reach"}`}>
              ({diff > 0 ? "+" : ""}{Number.isInteger(diff) ? diff : diff.toFixed(1)})
            </span>
          )}
        </div>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-muted rounded-full appearance-none cursor-pointer
          [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5
          [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-accent
          [&::-webkit-slider-thumb]:shadow-md [&::-webkit-slider-thumb]:cursor-pointer
          [&::-webkit-slider-thumb]:transition-transform [&::-webkit-slider-thumb]:active:scale-110"
      />
      <div className="flex justify-between text-[10px] text-muted-foreground font-mono">
        <span>{min}{unit}</span>
        <span>{max}{unit}</span>
      </div>
    </div>
  );
}

export default function WhatIfSimulator({ profile, simProfile, onProfileChange }: WhatIfSimulatorProps) {
  const isChanged = simProfile.sat !== profile.sat || simProfile.gpa !== profile.gpa || simProfile.leadershipRoles !== profile.leadershipRoles;

  return (
    <div className="bg-card rounded-2xl p-6 bg-card-glow">
      <div className="grid md:grid-cols-3 gap-8">
        <SimSlider
          label="SAT Score"
          value={simProfile.sat}
          originalValue={profile.sat}
          min={800}
          max={1600}
          step={10}
          unit=""
          onChange={(v) => onProfileChange({ ...simProfile, sat: v })}
        />
        <SimSlider
          label="GPA"
          value={simProfile.gpa}
          originalValue={profile.gpa}
          min={2.0}
          max={4.0}
          step={0.05}
          unit=""
          onChange={(v) => onProfileChange({ ...simProfile, gpa: parseFloat(v.toFixed(2)) })}
        />
        <SimSlider
          label="Leadership Roles"
          value={simProfile.leadershipRoles}
          originalValue={profile.leadershipRoles}
          min={0}
          max={5}
          step={1}
          unit=""
          onChange={(v) => onProfileChange({ ...simProfile, leadershipRoles: v })}
        />
      </div>

      {isChanged && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 pt-4 border-t border-border flex items-center justify-between"
        >
          <p className="text-sm text-accent font-medium">
            ✨ Results updated with simulated values
          </p>
          <button
            onClick={() => onProfileChange(profile)}
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors active:scale-95"
          >
            <RotateCcw className="w-3 h-3" /> Reset
          </button>
        </motion.div>
      )}
    </div>
  );
}
