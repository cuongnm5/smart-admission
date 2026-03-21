import { useState } from "react";
import { motion } from "framer-motion";
import { GraduationCap, Activity, DollarSign, User, AlertCircle } from "lucide-react";
import type { StudentMatchRequest } from "@/lib/api";
import type { StudentProfile } from "@/lib/admissionEngine";

interface ManualProfileFormProps {
  /** Pre-filled from a partial PDF parse — can be undefined for a blank form */
  initialData?: StudentMatchRequest;
  /** Which fields the server flagged as missing */
  missingFields?: string[];
  onComplete: (profile: StudentProfile, request: StudentMatchRequest) => void;
}

interface FormState {
  name: string;
  major: string;
  gpa: string;
  sat: string;
  ielts: string;
  activities: string;
  awards: string;
  leadershipRoles: string;
  researchExperience: boolean;
  communityService: boolean;
  budget: string;
  currency: string;
  needScholarship: boolean;
}

function num(v: number | null | undefined): string {
  return v != null && v !== 0 ? String(v) : "";
}

function deriveInitial(data?: StudentMatchRequest): FormState {
  if (!data || !data.academic) {
    return {
      name: "", major: "", gpa: "", sat: "", ielts: "",
      activities: "", awards: "", leadershipRoles: "0",
      researchExperience: false, communityService: false,
      budget: "", currency: "USD", needScholarship: false,
    };
  }

  const gpaVal = data.academic.gpa?.[0]?.value;
  const satVal = data.test_scores?.sat?.total;
  const englishTest = data.test_scores?.english_tests?.[0]; // IELTS or TOEFL
  const ieltsVal = englishTest?.score;

  const activities = (data.extracurriculars ?? []).map((a) => a.activity_name).join(", ");
  const awards = (data.awards ?? []).map((a) => a.award_name).join(", ");
  const leadershipRoles = String((data.leadership ?? []).length);
  const researchExperience = (data.projects ?? []).length > 0;

  const rawId = data.student_id ?? "";
  const name = rawId === "unknown" || rawId === "" ? "" : rawId.replace(/_/g, " ");

  const major = data.intended_major && data.intended_major !== "Undecided" ? data.intended_major : "";

  const budget = data.financial?.budget_per_year != null && data.financial.budget_per_year > 0
    ? String(data.financial.budget_per_year)
    : "";

  return {
    name,
    major,
    gpa: num(gpaVal),
    sat: num(satVal),
    ielts: num(ieltsVal),
    activities,
    awards,
    leadershipRoles,
    researchExperience,
    communityService: false,
    budget,
    currency: data.financial?.currency ?? "USD",
    needScholarship: data.financial?.need_scholarship ?? false,
  };
}

function Field({
  label, required, missing, hint, children,
}: {
  label: string;
  required?: boolean;
  missing?: boolean;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <label className="flex items-center gap-1.5 text-sm font-medium text-foreground">
        {label}
        {required && <span className="text-destructive">*</span>}
        {missing && (
          <span className="inline-flex items-center gap-1 text-[10px] font-medium text-amber-500 bg-amber-500/10 rounded-full px-2 py-0.5">
            <AlertCircle className="w-2.5 h-2.5" /> required
          </span>
        )}
      </label>
      {children}
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}

const inputCls = "w-full rounded-xl border border-border bg-card px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring";

export default function ManualProfileForm({ initialData, missingFields = [], onComplete }: ManualProfileFormProps) {
  const [form, setForm] = useState<FormState>(() => deriveInitial(initialData));
  const [submitted, setSubmitted] = useState(false);

  const set = (key: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((prev) => ({ ...prev, [key]: e.target.value }));

  const setCheck = (key: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [key]: e.target.checked }));

  const isFieldMissing = (field: string) => missingFields.includes(field);

  const errors = {
    name: submitted && !form.name.trim(),
    major: submitted && !form.major.trim(),
    gpa: submitted && (!form.gpa || isNaN(parseFloat(form.gpa)) || parseFloat(form.gpa) < 0 || parseFloat(form.gpa) > 4),
    budget: submitted && (!form.budget || isNaN(parseFloat(form.budget)) || parseFloat(form.budget) <= 0),
    testScore: submitted && !form.sat && !form.ielts,
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    if (errors.name || errors.major || errors.gpa || errors.budget || errors.testScore) return;

    const gpa = parseFloat(form.gpa);
    const sat = form.sat ? parseInt(form.sat) : null;
    const ielts = form.ielts ? parseFloat(form.ielts) : null;
    const activities = form.activities.split(",").map((s) => s.trim()).filter(Boolean);
    const awards = form.awards.split(",").map((s) => s.trim()).filter(Boolean);
    const leadershipRoles = parseInt(form.leadershipRoles) || 0;
    const budget = parseFloat(form.budget);
    const studentId = form.name.trim().toLowerCase().replace(/\s+/g, "_");

    const request: StudentMatchRequest = {
      ...(initialData ?? {}),
      student_id: studentId,
      intended_major: form.major.trim(),
      academic: {
        gpa: [{ year: "current", value: gpa, scale: 4.0 }],
        class_rank: initialData?.academic?.class_rank ?? null,
        school_profile: initialData?.academic?.school_profile ?? null,
        transcript: initialData?.academic?.transcript ?? [],
      },
      test_scores: {
        sat: sat ? { total: sat, math: null, reading_writing: null } : (initialData?.test_scores?.sat ?? null),
        act: initialData?.test_scores?.act ?? null,
        english_tests: ielts
          ? [{ type: "IELTS", score: ielts, section_scores: {} }]
          : (initialData?.test_scores?.english_tests ?? []),
        ap_ib: initialData?.test_scores?.ap_ib ?? [],
      },
      extracurriculars: activities.map((act) => ({
        activity_name: act, role: "Member", organization: act,
        start_date: "2022-09", end_date: "2024-06", hours_per_week: 5, description: act,
      })),
      leadership: Array.from({ length: leadershipRoles }, (_, i) => ({
        position: `Leadership Role ${i + 1}`, organization: "School",
        description: "Leadership position", duration: "1 year",
      })),
      awards: awards.map((award) => ({
        award_name: award, organizer: "Unknown", level: "School", year: 2023, description: award,
      })),
      projects: form.researchExperience
        ? [{ project_name: "Research Project", role: "Researcher", description: "Research experience", link: null, start_date: "2023-01", end_date: "2024-01" }]
        : (initialData?.projects ?? []),
      essays: initialData?.essays ?? { personal_statement: null, supplemental_essays: [] },
      recommendation_letters: initialData?.recommendation_letters ?? [],
      financial: {
        budget_per_year: budget,
        currency: form.currency,
        need_scholarship: form.needScholarship,
        scholarship_expectation_percent: null,
        family_income_range: null,
      },
      preferences: initialData?.preferences ?? null,
    } as unknown as StudentMatchRequest;

    const profile: StudentProfile = {
      name: form.name.trim(),
      gpa,
      sat: sat ?? 1200,
      ielts: ielts ?? 0,
      major: form.major.trim(),
      activities,
      awards,
      leadershipRoles,
      communityService: form.communityService,
      researchExperience: form.researchExperience,
    };

    onComplete(profile, request);
  };

  const sections = [
    {
      icon: User,
      title: "Basic Info",
      fields: (
        <div className="grid md:grid-cols-2 gap-4">
          <Field label="Full Name" required missing={isFieldMissing("student_id")}>
            <input className={`${inputCls} ${errors.name ? "border-destructive" : ""}`} placeholder="e.g. Alex Johnson" value={form.name} onChange={set("name")} />
            {errors.name && <p className="text-xs text-destructive mt-1">Name is required</p>}
          </Field>
          <Field label="Intended Major" required missing={isFieldMissing("intended_major")}>
            <input className={`${inputCls} ${errors.major ? "border-destructive" : ""}`} placeholder="e.g. Computer Science" value={form.major} onChange={set("major")} />
            {errors.major && <p className="text-xs text-destructive mt-1">Major is required</p>}
          </Field>
        </div>
      ),
    },
    {
      icon: GraduationCap,
      title: "Academic & Test Scores",
      fields: (
        <div className="space-y-4">
          <div className="grid md:grid-cols-3 gap-4">
            <Field label="GPA" required missing={isFieldMissing("academic.gpa")} hint="On a 4.0 scale">
              <input type="number" min="0" max="4" step="0.01" className={`${inputCls} ${errors.gpa ? "border-destructive" : ""}`} placeholder="e.g. 3.8" value={form.gpa} onChange={set("gpa")} />
              {errors.gpa && <p className="text-xs text-destructive mt-1">Valid GPA (0–4) required</p>}
            </Field>
            <Field label="SAT Score" missing={isFieldMissing("test_scores")} hint="Out of 1600">
              <input type="number" min="400" max="1600" className={`${inputCls} ${errors.testScore && !form.ielts ? "border-destructive" : ""}`} placeholder="e.g. 1420" value={form.sat} onChange={set("sat")} />
            </Field>
            <Field label="IELTS Score" hint="Out of 9.0">
              <input type="number" min="0" max="9" step="0.5" className={`${inputCls} ${errors.testScore && !form.sat ? "border-destructive" : ""}`} placeholder="e.g. 7.5" value={form.ielts} onChange={set("ielts")} />
            </Field>
          </div>
          {errors.testScore && (
            <p className="text-xs text-destructive">At least one test score (SAT or IELTS) is required</p>
          )}
        </div>
      ),
    },
    {
      icon: Activity,
      title: "Extracurriculars & Achievements",
      fields: (
        <div className="space-y-4">
          <Field label="Extracurricular Activities" hint="Separate with commas">
            <textarea rows={2} className={inputCls} placeholder="e.g. Debate Club, Robotics Team, Volunteering" value={form.activities} onChange={set("activities")} />
          </Field>
          <div className="grid md:grid-cols-2 gap-4">
            <Field label="Awards & Honors" hint="Separate with commas">
              <textarea rows={2} className={inputCls} placeholder="e.g. Science Olympiad Gold, Dean's List" value={form.awards} onChange={set("awards")} />
            </Field>
            <div className="space-y-4">
              <Field label="Leadership Roles" hint="Number of positions held">
                <input type="number" min="0" max="20" className={inputCls} placeholder="e.g. 2" value={form.leadershipRoles} onChange={set("leadershipRoles")} />
              </Field>
              <div className="flex flex-col gap-2 pt-1">
                <label className="flex items-center gap-2 text-sm text-foreground cursor-pointer">
                  <input type="checkbox" checked={form.researchExperience} onChange={setCheck("researchExperience")} className="rounded" />
                  Research experience
                </label>
                <label className="flex items-center gap-2 text-sm text-foreground cursor-pointer">
                  <input type="checkbox" checked={form.communityService} onChange={setCheck("communityService")} className="rounded" />
                  Community service
                </label>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      icon: DollarSign,
      title: "Financial",
      fields: (
        <div className="grid md:grid-cols-3 gap-4">
          <Field label="Annual Budget" required missing={isFieldMissing("financial.budget_per_year")} hint="Per year">
            <input type="number" min="0" className={`${inputCls} ${errors.budget ? "border-destructive" : ""}`} placeholder="e.g. 60000" value={form.budget} onChange={set("budget")} />
            {errors.budget && <p className="text-xs text-destructive mt-1">Budget is required</p>}
          </Field>
          <Field label="Currency">
            <select className={inputCls} value={form.currency} onChange={set("currency")}>
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
              <option value="VND">VND</option>
              <option value="SGD">SGD</option>
            </select>
          </Field>
          <Field label="Scholarship">
            <label className="flex items-center gap-2 text-sm text-foreground cursor-pointer mt-2.5">
              <input type="checkbox" checked={form.needScholarship} onChange={setCheck("needScholarship")} className="rounded" />
              Need financial aid
            </label>
          </Field>
        </div>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b border-border bg-card px-6 py-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center">
          <GraduationCap className="w-4 h-4 text-accent-foreground" />
        </div>
        <div>
          <h2 className="font-semibold text-sm text-foreground">Complete Your Profile</h2>
          <p className="text-xs text-muted-foreground">
            {missingFields.length > 0
              ? `${missingFields.length} required field${missingFields.length > 1 ? "s" : ""} need${missingFields.length === 1 ? "s" : ""} your input`
              : "Fill in your details to get started"}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} noValidate>
        <div className="max-w-3xl mx-auto px-6 py-8 space-y-8">
          {missingFields.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-start gap-3 bg-amber-500/10 border border-amber-500/20 rounded-xl px-4 py-3"
            >
              <AlertCircle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-amber-600 dark:text-amber-400">
                Some fields couldn't be extracted from your PDF. Please fill them in below — fields marked <span className="font-semibold">required</span> must be completed before proceeding.
              </p>
            </motion.div>
          )}

          {sections.map((section, i) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] }}
              className="bg-card rounded-2xl p-6 space-y-4 border border-border"
            >
              <div className="flex items-center gap-2 mb-2">
                <section.icon className="w-4 h-4 text-accent" />
                <h3 className="font-semibold text-sm text-foreground">{section.title}</h3>
              </div>
              {section.fields}
            </motion.div>
          ))}

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="flex justify-end pb-8"
          >
            <button
              type="submit"
              className="rounded-xl bg-accent px-8 py-3 text-sm font-semibold text-accent-foreground hover:opacity-90 active:scale-95 transition-all"
            >
              Analyze My Profile →
            </button>
          </motion.div>
        </div>
      </form>
    </div>
  );
}
