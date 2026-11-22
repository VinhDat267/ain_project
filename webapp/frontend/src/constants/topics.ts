export interface TopicStyle {
  label: string
  shortLabel: string
  fg: string
  bg: string
  border: string
}

/* Strictly non-violet topic tokens aligned with cool-white-slate ground */
export const TOPIC_STYLES: Record<string, TopicStyle> = {
  course_registration: {
    label: 'Course Registration',
    shortLabel: 'Course Reg',
    fg: '#1e40af',
    bg: '#e7effd',
    border: '#bfd3f8',
  },
  tuition: {
    label: 'Tuition & Fees',
    shortLabel: 'Tuition',
    fg: '#065f46',
    bg: '#e6f4ef',
    border: '#a7dfd0',
  },
  exam: {
    label: 'Examinations',
    shortLabel: 'Examinations',
    fg: '#9f1239',
    bg: '#fdecef',
    border: '#f6b8c7',
  },
  class_schedule: {
    label: 'Class Schedules & Rooms',
    shortLabel: 'Schedules',
    fg: '#1f3038',
    bg: '#e5ebee',
    border: '#c3d0d6',
  },
  student_services: {
    label: 'Student Services & Advising',
    shortLabel: 'Services',
    fg: '#92400e',
    bg: '#fef4e6',
    border: '#f5cf9a',
  },
  graduation: {
    label: 'Graduation & Degree Audit',
    shortLabel: 'Graduation',
    fg: '#7c2d12',
    bg: '#fbeee8',
    border: '#f1c7b6',
  },
  technical_support: {
    label: 'IT & Student Portal',
    shortLabel: 'IT Support',
    fg: '#0b5c66',
    bg: '#e4f3f5',
    border: '#abd9df',
  },
}

export function topicStyle(intent: string): TopicStyle {
  return (
    TOPIC_STYLES[intent] ?? {
      label: intent,
      shortLabel: intent,
      fg: '#1f3038',
      bg: '#ecf0f2',
      border: '#cbd5db',
    }
  )
}

export interface StarterPrompt {
  id: string
  label: string
  query: string
}

export const STARTER_PROMPTS: StarterPrompt[] = [
  {
    id: 'p_tuition',
    label: 'When is tuition due?',
    query: 'When is tuition due for the semester?',
  },
  {
    id: 'p_wifi_typo',
    label: 'Typo: conncet to Wi-Fi',
    query: "Why can't I conncet to the campus Wi-Fi network?",
  },
  {
    id: 'p_id_paraphrase',
    label: 'Lost student ID card',
    query: 'I lost my student ID - how do I get a new one?',
  },
  {
    id: 'p_kayak_ooc',
    label: 'Out-of-corpus: kayak rental',
    query: 'Can I rent a kayak from the campus recreation center?',
  },
]
