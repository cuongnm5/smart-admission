// ── Types ────────────────────────────────────────────────────────────────────

export interface StudentProfile {
  name: string;
  gpa: number;
  sat: number;
  ielts: number;
  major: string;
  activities: string[];
  awards: string[];
  leadershipRoles: number;
  communityService: boolean;
  researchExperience: boolean;
}

export interface SchoolResult {
  name: string;
  category: "reach" | "target" | "safety";
  location: string;
  ranking: number;
  probability: number;
  explanation: string[];
  acceptanceRate: number;
  avgSAT: number;
  majorStrength: string;
  tuition?: number;
}

export interface ProfileStrength {
  overall: number;
  academic: number;
  activities: number;
  fit: number;
}

export interface ImprovementSuggestion {
  action: string;
  impact: string;
  delta: number;
  category: "academic" | "extracurricular" | "other";
}

// ── Local school database (used by What-if Simulator) ────────────────────────

interface SchoolData {
  name: string;
  location: string;
  ranking: number;
  acceptanceRate: number;
  avgSAT: number;
  minGPA: number;
  majorStrength: string;
  tuition: number; // annual out-of-state / international tuition + fees (USD)
}

const SCHOOL_DATABASE: SchoolData[] = [
  { name: "Massachusetts Institute of Technology", location: "Cambridge, MA", ranking: 1, acceptanceRate: 4, avgSAT: 1545, minGPA: 3.9, majorStrength: "STEM / Engineering", tuition: 59750 },
  { name: "Stanford University", location: "Stanford, CA", ranking: 3, acceptanceRate: 4, avgSAT: 1530, minGPA: 3.9, majorStrength: "CS / Business", tuition: 62484 },
  { name: "Harvard University", location: "Cambridge, MA", ranking: 4, acceptanceRate: 4, avgSAT: 1520, minGPA: 3.9, majorStrength: "Liberal Arts / Law", tuition: 59076 },
  { name: "Carnegie Mellon University", location: "Pittsburgh, PA", ranking: 22, acceptanceRate: 15, avgSAT: 1500, minGPA: 3.8, majorStrength: "CS / Engineering", tuition: 62988 },
  { name: "University of California, Berkeley", location: "Berkeley, CA", ranking: 20, acceptanceRate: 14, avgSAT: 1440, minGPA: 3.8, majorStrength: "STEM / Business", tuition: 44066 },
  { name: "University of Michigan", location: "Ann Arbor, MI", ranking: 25, acceptanceRate: 20, avgSAT: 1430, minGPA: 3.7, majorStrength: "Engineering / Business", tuition: 55334 },
  { name: "Cornell University", location: "Ithaca, NY", ranking: 12, acceptanceRate: 11, avgSAT: 1480, minGPA: 3.8, majorStrength: "Engineering / Agriculture", tuition: 63200 },
  { name: "Duke University", location: "Durham, NC", ranking: 7, acceptanceRate: 8, avgSAT: 1520, minGPA: 3.9, majorStrength: "Medicine / Policy", tuition: 63054 },
  { name: "Georgetown University", location: "Washington, DC", ranking: 23, acceptanceRate: 15, avgSAT: 1440, minGPA: 3.7, majorStrength: "International Affairs", tuition: 63612 },
  { name: "University of Virginia", location: "Charlottesville, VA", ranking: 25, acceptanceRate: 21, avgSAT: 1400, minGPA: 3.7, majorStrength: "Business / Liberal Arts", tuition: 54646 },
  { name: "University of North Carolina", location: "Chapel Hill, NC", ranking: 28, acceptanceRate: 23, avgSAT: 1380, minGPA: 3.6, majorStrength: "Business / Journalism", tuition: 36946 },
  { name: "Purdue University", location: "West Lafayette, IN", ranking: 49, acceptanceRate: 59, avgSAT: 1310, minGPA: 3.3, majorStrength: "Engineering / Agriculture", tuition: 28794 },
  { name: "University of Wisconsin-Madison", location: "Madison, WI", ranking: 42, acceptanceRate: 54, avgSAT: 1330, minGPA: 3.4, majorStrength: "Research / Biomedical", tuition: 39428 },
  { name: "Ohio State University", location: "Columbus, OH", ranking: 51, acceptanceRate: 54, avgSAT: 1310, minGPA: 3.3, majorStrength: "Business / Medicine", tuition: 36722 },
  { name: "Penn State University", location: "State College, PA", ranking: 61, acceptanceRate: 54, avgSAT: 1270, minGPA: 3.2, majorStrength: "Business / Engineering", tuition: 39428 },
  { name: "University of Texas at Austin", location: "Austin, TX", ranking: 38, acceptanceRate: 31, avgSAT: 1330, minGPA: 3.5, majorStrength: "Business / CS", tuition: 40996 },
  { name: "Arizona State University", location: "Tempe, AZ", ranking: 117, acceptanceRate: 90, avgSAT: 1200, minGPA: 2.5, majorStrength: "General", tuition: 28800 },
  { name: "University of Arizona", location: "Tucson, AZ", ranking: 103, acceptanceRate: 85, avgSAT: 1190, minGPA: 2.0, majorStrength: "General", tuition: 38877 },
  { name: "University of Central Florida", location: "Orlando, FL", ranking: 156, acceptanceRate: 43, avgSAT: 1230, minGPA: 3.0, majorStrength: "Engineering / Hospitality", tuition: 22467 },
  { name: "Indiana University", location: "Bloomington, IN", ranking: 68, acceptanceRate: 80, avgSAT: 1210, minGPA: 2.8, majorStrength: "Business / Music", tuition: 38918 },
];

// ── Scoring ───────────────────────────────────────────────────────────────────

export function calculateAdmissionProbability(profile: StudentProfile, school: SchoolData): number {
  const satDiff = profile.sat - school.avgSAT;
  const gpaBonus = (profile.gpa - school.minGPA) * 20;
  const activityBonus = Math.min(profile.activities.length * 2, 12);
  const awardBonus = Math.min(profile.awards.length * 3, 15);
  const leadershipBonus = Math.min(profile.leadershipRoles * 5, 20);
  const communityBonus = profile.communityService ? 4 : 0;
  const researchBonus = profile.researchExperience ? 6 : 0;

  const base = school.acceptanceRate;
  const satScore = satDiff > 100 ? 25 : satDiff > 0 ? 15 : satDiff > -100 ? 5 : -10;
  const total = base + satScore + gpaBonus + activityBonus + awardBonus + leadershipBonus + communityBonus + researchBonus;
  return Math.max(1, Math.min(99, Math.round(total)));
}

function classifyCategory(probability: number, school: SchoolData): "reach" | "target" | "safety" {
  if (school.acceptanceRate < 20) return probability < 30 ? "reach" : probability < 60 ? "target" : "safety";
  if (probability < 30) return "reach";
  if (probability < 65) return "target";
  return "safety";
}

function buildExplanation(profile: StudentProfile, school: SchoolData): string[] {
  const lines: string[] = [];
  const satDiff = profile.sat - school.avgSAT;
  lines.push(satDiff >= 0 ? `SAT ${profile.sat} is above the school average of ${school.avgSAT}` : `SAT ${profile.sat} is below the school average of ${school.avgSAT}`);
  if (profile.gpa >= school.minGPA) lines.push(`GPA ${profile.gpa.toFixed(1)} meets the minimum threshold of ${school.minGPA.toFixed(1)}`);
  else lines.push(`GPA ${profile.gpa.toFixed(1)} is below the preferred minimum of ${school.minGPA.toFixed(1)}`);
  if (profile.activities.length > 0) lines.push(`${profile.activities.length} extracurricular${profile.activities.length > 1 ? "s" : ""} strengthen the application`);
  if (profile.leadershipRoles > 0) lines.push(`${profile.leadershipRoles} leadership role${profile.leadershipRoles > 1 ? "s" : ""} demonstrate initiative`);
  if (profile.researchExperience) lines.push("Research experience is a strong differentiator");
  return lines;
}

export function getTopSchools(profile: StudentProfile): SchoolResult[] {
  return SCHOOL_DATABASE
    .map((school) => {
      const probability = calculateAdmissionProbability(profile, school);
      return {
        name: school.name,
        category: classifyCategory(probability, school),
        location: school.location,
        ranking: school.ranking,
        probability,
        explanation: buildExplanation(profile, school),
        acceptanceRate: school.acceptanceRate,
        avgSAT: school.avgSAT,
        majorStrength: school.majorStrength,
        tuition: school.tuition,
      } satisfies SchoolResult;
    })
    .sort((a, b) => {
      const order = { safety: 0, target: 1, reach: 2 };
      if (order[a.category] !== order[b.category]) return order[b.category] - order[a.category];
      return b.probability - a.probability;
    })
    .slice(0, 10);
}

export function calculateProfileStrength(profile: StudentProfile): ProfileStrength {
  const academic = Math.min(100, Math.round(
    ((profile.gpa / 4.0) * 40) +
    ((profile.sat / 1600) * 40) +
    ((profile.ielts / 9.0) * 20)
  ));
  const activities = Math.min(100, Math.round(
    Math.min(profile.activities.length * 8, 40) +
    Math.min(profile.awards.length * 10, 30) +
    Math.min(profile.leadershipRoles * 10, 20) +
    (profile.communityService ? 5 : 0) +
    (profile.researchExperience ? 5 : 0)
  ));
  const fit = Math.round((academic * 0.6 + activities * 0.4));
  const overall = Math.round((academic * 0.5 + activities * 0.3 + fit * 0.2));
  return { overall, academic, activities, fit };
}

export function getImprovementSuggestions(profile: StudentProfile, schools: SchoolResult[]): ImprovementSuggestion[] {
  const suggestions: ImprovementSuggestion[] = [];

  if (profile.sat < 1400) {
    suggestions.push({
      action: "Retake SAT and aim for 1450+",
      impact: "Could upgrade 2–3 target schools to higher tiers",
      delta: 12,
      category: "academic",
    });
  }
  if (profile.gpa < 3.7) {
    suggestions.push({
      action: "Focus on GPA improvement this semester",
      impact: "Opens access to top-30 universities",
      delta: 10,
      category: "academic",
    });
  }
  if (profile.activities.length < 4) {
    suggestions.push({
      action: "Join 1–2 more extracurricular clubs",
      impact: "Strengthens your profile for selective schools",
      delta: 7,
      category: "extracurricular",
    });
  }
  if (profile.leadershipRoles === 0) {
    suggestions.push({
      action: "Take on a leadership position in an existing club",
      impact: "Leadership is a key differentiator for top-20 schools",
      delta: 9,
      category: "extracurricular",
    });
  }
  if (!profile.researchExperience) {
    suggestions.push({
      action: "Pursue a summer research internship or lab assistant role",
      impact: "Research experience is highly valued for STEM programs",
      delta: 8,
      category: "other",
    });
  }
  if (profile.awards.length === 0) {
    suggestions.push({
      action: "Participate in academic competitions (Science Olympiad, Math League)",
      impact: "Awards validate academic excellence for admissions officers",
      delta: 6,
      category: "academic",
    });
  }

  return suggestions.slice(0, 4);
}
