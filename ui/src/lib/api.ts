import type { StudentProfile, SchoolResult } from "./admissionEngine";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// ── OpenAPI types ─────────────────────────────────────────────────────────────

interface GPARecord { year: string; value: number; scale: number }
interface ClassRank { value: number; total_students: number }
interface SchoolProfile { school_name: string; school_type: string; location: string; description: string }
interface TranscriptYear { year: string; subjects?: unknown[] }
interface AcademicProfile {
  gpa: GPARecord[];
  class_rank: ClassRank | null;
  school_profile: SchoolProfile | null;
  transcript: TranscriptYear[];
}

interface EnglishTest { type: string; score: number; section_scores?: Record<string, number> }
interface SATScore { total: number | null; math: number | null; reading_writing: number | null }
interface ACTScore { composite: number | null; sections?: Record<string, number> }
interface APIBScore { subject: string; score: number }
interface TestScores {
  english_tests: EnglishTest[];
  sat: SATScore | null;
  act: ACTScore | null;
  ap_ib: APIBScore[];
}

interface ExtracurricularActivity {
  activity_name: string; role: string; organization: string;
  start_date: string; end_date: string; hours_per_week: number; description: string;
}
interface LeadershipExperience { position: string; organization: string; description: string; duration: string }
interface AwardRecord { award_name: string; organizer: string; level: string; year: number; description: string }
interface ProjectRecord { project_name: string; role: string; description: string; link: string | null; start_date: string; end_date: string }
interface PersonalStatement { content: string }
interface SupplementalEssay { school: string; prompt: string; content: string }
interface Essays { personal_statement: PersonalStatement | null; supplemental_essays: SupplementalEssay[] }
interface RecommendationLetter { from: string; role: string; relationship_duration: string; content_summary: string }
interface FinancialProfile { budget_per_year: number; currency: string; need_scholarship: boolean; scholarship_expectation_percent: number | null; family_income_range: string | null }
interface PreferenceProfile {
  dream_major: string | null; target_schools: string[]; preferred_locations: string[];
  ranking_preference: string | null; school_type_preference: string | null;
}

export interface StudentMatchRequest {
  student_id?: string;
  academic: AcademicProfile;
  test_scores: TestScores;
  intended_major: string;
  extracurriculars: ExtracurricularActivity[];
  leadership: LeadershipExperience[];
  awards: AwardRecord[];
  projects: ProjectRecord[];
  essays: Essays;
  recommendation_letters: RecommendationLetter[];
  financial: FinancialProfile;
  preferences: PreferenceProfile | null;
}

export interface MatchingMeta {
  retrieved_count: number;
  hard_filter_pass_count: number;
  scored_count: number;
  returned_count: number;
  rubric_version: string;
}

export interface StageOneMatchingOutput {
  top_20_university_ids: string[];
  meta: MatchingMeta;
}

export interface StageTwoAnalysisOutput {
  analyzed_university_ids: string[];
  matched_university_id: string | null;
  ranking_summary: Record<string, unknown>[];
  detailed_analysis: Record<string, unknown>;
}

export interface UniversityPipelineResponse {
  stage_1_matching: StageOneMatchingOutput;
  stage_2_analysis: StageTwoAnalysisOutput;
}

// ── Profile mapper ────────────────────────────────────────────────────────────

function toStudentMatchRequest(profile: StudentProfile): StudentMatchRequest {
  return {
    student_id: profile.name.toLowerCase().replace(/\s+/g, "_") || "unknown",
    academic: {
      gpa: [{ year: "current", value: profile.gpa, scale: 4.0 }],
      class_rank: null,
      school_profile: null,
      transcript: [],
    },
    test_scores: {
      sat: { total: profile.sat, math: null, reading_writing: null },
      act: null,
      english_tests: profile.ielts > 0
        ? [{ type: "IELTS", score: profile.ielts, section_scores: {} }]
        : [],
      ap_ib: [],
    },
    intended_major: profile.major,
    extracurriculars: profile.activities.map((act) => ({
      activity_name: act,
      role: "Member",
      organization: act,
      start_date: "2022-09",
      end_date: "2024-06",
      hours_per_week: 5,
      description: act,
    })),
    leadership: Array.from({ length: profile.leadershipRoles }, (_, i) => ({
      position: `Leadership Role ${i + 1}`,
      organization: "School",
      description: "Leadership position",
      duration: "1 year",
    })),
    awards: profile.awards.map((award) => ({
      award_name: award,
      organizer: "Unknown",
      level: "School",
      year: 2023,
      description: award,
    })),
    projects: profile.researchExperience
      ? [{
          project_name: "Research Project",
          role: "Researcher",
          description: "Research experience",
          link: null,
          start_date: "2023-01",
          end_date: "2024-01",
        }]
      : [],
    essays: { personal_statement: null, supplemental_essays: [] },
    recommendation_letters: [],
    financial: {
      budget_per_year: 60000,
      currency: "USD",
      need_scholarship: false,
      scholarship_expectation_percent: null,
      family_income_range: null,
    },
    preferences: {
      dream_major: profile.major,
      target_schools: [],
      preferred_locations: [],
      ranking_preference: null,
      school_type_preference: null,
    },
  };
}

// ── Response mapper ───────────────────────────────────────────────────────────

export function pipelineResponseToSchools(response: UniversityPipelineResponse): SchoolResult[] {
  const { ranking_summary, detailed_analysis } = response.stage_2_analysis;

  return ranking_summary.slice(0, 10).map((item, index) => {
    const id = (item.university_id ?? item.id ?? item.name ?? `University ${index + 1}`) as string;
    const details = (detailed_analysis[id] ?? {}) as Record<string, unknown>;

    const probability = Math.round(
      typeof item.probability === "number" ? item.probability
      : typeof item.score === "number" ? item.score
      : typeof item.match_score === "number" ? item.match_score
      : Math.max(5, 80 - index * 7)
    );

    const category = (() => {
      const raw = (item.category ?? item.tier ?? details.category ?? details.tier) as string | undefined;
      if (raw) {
        const lower = raw.toLowerCase();
        if (lower.includes("reach")) return "reach" as const;
        if (lower.includes("safe")) return "safety" as const;
        return "target" as const;
      }
      return (probability >= 65 ? "safety" : probability >= 30 ? "target" : "reach") as "reach" | "target" | "safety";
    })();

    const explanation: string[] = (() => {
      const raw = item.explanation ?? item.reasons ?? details.explanation ?? details.strengths;
      if (Array.isArray(raw)) return (raw as unknown[]).map(String);
      if (typeof raw === "string") return [raw];
      return [`Match rank #${index + 1} based on your academic and extracurricular profile`];
    })();

    return {
      name: String(item.university_name ?? item.name ?? id),
      category,
      location: String(item.location ?? details.location ?? "USA"),
      ranking: typeof item.rank === "number" ? item.rank : index + 1,
      probability: Math.min(99, Math.max(1, probability)),
      explanation,
      acceptanceRate: typeof item.acceptance_rate === "number" ? item.acceptance_rate : typeof details.acceptance_rate === "number" ? details.acceptance_rate : 0,
      avgSAT: typeof item.avg_sat === "number" ? item.avg_sat : typeof details.avg_sat === "number" ? details.avg_sat : 0,
      majorStrength: String(item.major_strength ?? details.major_strength ?? item.program_strength ?? "—"),
      tuition: typeof item.tuition === "number" ? item.tuition
        : typeof details.tuition === "number" ? details.tuition
        : typeof item.tuition_per_year === "number" ? item.tuition_per_year
        : typeof details.tuition_per_year === "number" ? details.tuition_per_year
        : undefined,
    } satisfies SchoolResult;
  });
}

// ── API calls ─────────────────────────────────────────────────────────────────

export async function matchAndAnalyze(profile: StudentProfile): Promise<UniversityPipelineResponse> {
  const body = toStudentMatchRequest(profile);
  const res = await fetch(`${API_BASE}/v1/pipeline/match-and-analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json() as Promise<UniversityPipelineResponse>;
}

export async function matchAndAnalyzeDirect(request: StudentMatchRequest): Promise<UniversityPipelineResponse> {
  const res = await fetch(`${API_BASE}/v1/pipeline/match-and-analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json() as Promise<UniversityPipelineResponse>;
}

export interface ParsePDFResponse {
  data?: StudentMatchRequest;
  missing_fields: string[];
  error?: string;
}

export async function parseProfileFromPDF(file: File): Promise<ParsePDFResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/v1/profile/parse-pdf`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json() as Promise<ParsePDFResponse>;
}

/** Derive a lightweight StudentProfile from a parsed StudentMatchRequest for the UI / What-if Simulator */
export function studentProfileFromRequest(req: StudentMatchRequest, name?: string): StudentProfile {
  const gpa = (req.academic as AcademicProfile).gpa?.[0]?.value ?? 3.5;
  const sat = (req.test_scores as TestScores).sat?.total ?? 1300;
  const ielts = (req.test_scores as TestScores).english_tests?.find((t) => t.type === "IELTS")?.score ?? 7.0;
  const activities = ((req.extracurriculars ?? []) as ExtracurricularActivity[]).map((a) => a.activity_name);
  const awards = ((req.awards ?? []) as AwardRecord[]).map((a) => a.award_name);
  const leadershipRoles = ((req.leadership ?? []) as LeadershipExperience[]).length;
  const researchExperience = ((req.projects ?? []) as ProjectRecord[]).length > 0;

  return {
    name: name ?? String((req as Record<string, unknown>).student_id ?? "Student"),
    gpa,
    sat,
    ielts,
    major: (req as Record<string, unknown>).intended_major as string ?? "Undecided",
    activities,
    awards,
    leadershipRoles,
    communityService: false,
    researchExperience,
  };
}
