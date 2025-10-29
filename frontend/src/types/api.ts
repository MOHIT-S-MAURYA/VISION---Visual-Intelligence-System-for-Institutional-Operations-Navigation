// API Type Definitions for Backend Models

export interface Department {
  id: number;
  code: string;
  name: string;
  degree_type: 'UG' | 'PG';
  duration_years: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Teacher {
  id: number;
  user: number;
  full_name: string;
  employee_id: string;
  email: string | null;
  phone: string | null;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
  assignments?: TeacherAssignment[];
}

export interface Subject {
  id: number;
  department: number; // Foreign key to Department
  department_code?: string; // Read-only from API
  department_name?: string; // Read-only from API
  class_year: string;
  subject_name: string;
  subject_code: string | null;
  credits: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface TeacherSubjectAssignment {
  id: number;
  teacher: number; // Foreign key to Teacher
  subject: number; // Foreign key to Subject
  academic_year: string | null;
  assigned_date: string;
  is_active: boolean;
  notes: string | null;
  // Nested read-only fields from API
  teacher_name?: string;
  subject_name?: string;
  department_code?: string;
}

export interface TeacherAssignment {
  id: number;
  subject: {
    id: number;
    name: string;
    code: string | null;
    class_year: string;
  };
  department: {
    id: number;
    code: string;
    name: string;
    degree_type: 'UG' | 'PG';
  };
  academic_year: string | null;
}

export interface Student {
  id: number;
  roll_number: string;
  full_name: string;
  department: number; // Foreign key to Department
  department_code?: string; // Read-only from API
  department_name?: string; // Read-only from API
  class_year: string;
  email: string | null;
  phone: string | null;
  face_embedding_id: string | null;
  face_image: string | null;
  is_active: boolean;
}

export interface AttendanceSession {
  id: number;
  department: string; // Still stored as string in attendance
  class_year: string;
  subject: string;
  session_date: string;
  start_time: string;
  end_time: string | null;
  is_active: boolean;
  created_by: string;
}

export interface AttendanceRecord {
  id: number;
  session: number;
  student: number;
  student_name?: string;
  confidence: number;
  marked_at: string;
}

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
  is_superuser: boolean;
  teacher: {
    id: number;
    full_name: string;
    employee_id: string;
    email: string | null;
    phone: string | null;
    assignments: TeacherAssignment[];
  } | null;
}

// Constants for choices
export const CLASS_YEARS_UG = [
  'First Year',
  'Second Year',
  'Third Year',
  'Fourth Year',
];

export const CLASS_YEARS_PG = [
  'First Year',
  'Second Year',
];

export const DEGREE_TYPES = [
  { value: 'UG', label: 'Undergraduate' },
  { value: 'PG', label: 'Postgraduate' },
];

// Helper function to get class years based on degree type
export function getClassYears(degreeType: 'UG' | 'PG'): string[] {
  return degreeType === 'UG' ? CLASS_YEARS_UG : CLASS_YEARS_PG;
}

// Helper function to get class years based on department duration
export function getClassYearsForDepartment(department: Department): string[] {
  const years = [];
  for (let i = 1; i <= department.duration_years; i++) {
    const yearNames = ['First', 'Second', 'Third', 'Fourth', 'Fifth'];
    years.push(`${yearNames[i - 1]} Year`);
  }
  return years;
}
