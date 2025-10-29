// Engineering College Departments and Years Configuration

export const DEPARTMENTS = [
  // Undergraduate (UG) - 4 Years
  {
    value: "CSE",
    label: "Computer Science and Engineering (CSE)",
    years: 4,
    type: "UG",
  },
  { value: "IT", label: "Information Technology (IT)", years: 4, type: "UG" },
  {
    value: "ECE",
    label: "Electronics and Communication Engineering (ECE)",
    years: 4,
    type: "UG",
  },
  {
    value: "EEE",
    label: "Electrical and Electronics Engineering (EEE)",
    years: 4,
    type: "UG",
  },
  {
    value: "MECH",
    label: "Mechanical Engineering (MECH)",
    years: 4,
    type: "UG",
  },
  { value: "CIVIL", label: "Civil Engineering (CIVIL)", years: 4, type: "UG" },
  { value: "CHEM", label: "Chemical Engineering (CHEM)", years: 4, type: "UG" },
  {
    value: "AERO",
    label: "Aeronautical Engineering (AERO)",
    years: 4,
    type: "UG",
  },
  {
    value: "AUTO",
    label: "Automobile Engineering (AUTO)",
    years: 4,
    type: "UG",
  },
  {
    value: "BIOMED",
    label: "Biomedical Engineering (BIOMED)",
    years: 4,
    type: "UG",
  },
  { value: "BIOTECH", label: "Biotechnology (BIOTECH)", years: 4, type: "UG" },
  {
    value: "AI-DS",
    label: "Artificial Intelligence and Data Science (AI-DS)",
    years: 4,
    type: "UG",
  },
  {
    value: "AI-ML",
    label: "Artificial Intelligence and Machine Learning (AI-ML)",
    years: 4,
    type: "UG",
  },
  { value: "CYBER", label: "Cyber Security (CYBER)", years: 4, type: "UG" },
  { value: "IOT", label: "Internet of Things (IoT)", years: 4, type: "UG" },
  {
    value: "ROBOTICS",
    label: "Robotics and Automation (ROBOTICS)",
    years: 4,
    type: "UG",
  },

  // Postgraduate (PG) - 2 Years
  {
    value: "M.TECH-CSE",
    label: "M.Tech Computer Science and Engineering",
    years: 2,
    type: "PG",
  },
  { value: "M.TECH-VLSI", label: "M.Tech VLSI Design", years: 2, type: "PG" },
  { value: "M.TECH-PS", label: "M.Tech Power Systems", years: 2, type: "PG" },
  {
    value: "M.TECH-SE",
    label: "M.Tech Software Engineering",
    years: 2,
    type: "PG",
  },
  { value: "M.TECH-CAD", label: "M.Tech CAD/CAM", years: 2, type: "PG" },
  {
    value: "M.TECH-TE",
    label: "M.Tech Thermal Engineering",
    years: 2,
    type: "PG",
  },
  {
    value: "M.TECH-SP",
    label: "M.Tech Signal Processing",
    years: 2,
    type: "PG",
  },
  {
    value: "M.TECH-CN",
    label: "M.Tech Computer Networks",
    years: 2,
    type: "PG",
  },
  {
    value: "M.TECH-ES",
    label: "M.Tech Embedded Systems",
    years: 2,
    type: "PG",
  },

  // MCA - 2 Years
  {
    value: "MCA",
    label: "Master of Computer Applications (MCA)",
    years: 2,
    type: "PG",
  },
];

// Generate year options based on number of years
export const getYearOptions = (departmentValue) => {
  const dept = DEPARTMENTS.find((d) => d.value === departmentValue);
  if (!dept) return [];

  const years = [];
  for (let i = 1; i <= dept.years; i++) {
    years.push({
      value: getYearLabel(i),
      label: getYearLabel(i),
    });
  }
  return years;
};

// Convert number to year label
const getYearLabel = (yearNum) => {
  const labels = ["First Year", "Second Year", "Third Year", "Fourth Year"];
  return labels[yearNum - 1] || `Year ${yearNum}`;
};

// Get all unique years (for filtering)
export const ALL_YEARS = [
  "First Year",
  "Second Year",
  "Third Year",
  "Fourth Year",
];
