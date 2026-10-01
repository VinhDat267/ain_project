#!/usr/bin/env python3
"""Generate the synthetic campus FAQ/notice corpus for Project 12.

Everything this script writes is **fully synthetic, educational English**
campus policy for "Hanoi University" (HANU) — synthetic educational handbook.
It is not real student records or a real institution's live policy, and
this script never crawls a real university website.

Writes, deterministically for a fixed ``--seed`` (default ``42``):

- ``data/faq.json``       — FAQ entries (question/answer, one intent each)
- ``data/notices.json``   — short announcements (title/body, one intent each)
- ``data/intents.csv``    — the 5-10 intent labels used above
- ``data/documents.md``   — a human-readable index of every document id
- ``data/queries_test.csv`` — 100+ evaluation queries: normal / paraphrase /
  typo triplets built from a subset of the FAQ questions, plus out-of-corpus
  queries whose correct behavior is "no document / low confidence", never a
  fabricated answer.

Re-running this script with the same seed reproduces byte-identical output
(see ``tests/test_project_12_sanity.py`` and the kit's parallel-plan recipe,
which hash-compares generator output against committed student data).
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_SEED = 42

# ---------------------------------------------------------------------------
# Intents (5-10, per the spec's suggested list — no need to add more).
# ---------------------------------------------------------------------------
INTENTS: list[tuple[str, str]] = [
    ("course_registration", "Signing up for, dropping, or changing course sections."),
    ("exam", "Final exam scheduling, conflicts, accommodations, and grading."),
    ("tuition", "Tuition payment, installment plans, refunds, and financial aid."),
    ("class_schedule", "Where and when classes meet, rooms, and linked sections."),
    ("student_services", "Advising, health, counseling, tutoring, and campus life."),
    ("graduation", "Applying to graduate, degree audits, and commencement."),
    ("technical_support", "Student Portal, Wi-Fi, VPN, and campus IT accounts."),
]

# ---------------------------------------------------------------------------
# FAQ entries: 12 per intent (84 total). Each is (question, answer).
# ---------------------------------------------------------------------------
FAQ_DATA: dict[str, list[tuple[str, str]]] = {
    "course_registration": [
        ("How do I register for classes at HANU?",
         "Log into the HANU Student Portal, go to \"Course Registration\", pick your intended "
         "session, and add classes before the add/drop deadline listed on the academic calendar."),
        ("What is the add/drop deadline for Fall 2026?",
         "The add/drop deadline for Fall 2026 is the end of the second week of the semester. "
         "After that date, dropping a course records a \"W\" (withdrawal) on the transcript."),
        ("Can I register for a course if I have not completed the prerequisite?",
         "No. The registration system blocks enrollment in courses whose prerequisite has not "
         "been passed. You may request a prerequisite override from the department chair if you "
         "have equivalent experience."),
        ("How many credits can I register for as a first-year student?",
         "First-year students may register for up to 18 credits per semester without an advisor "
         "override; students on academic probation are capped at 12 credits."),
        ("What happens if the course section I want is full?",
         "Join the waitlist through the Student Portal. You will be automatically enrolled if a "
         "seat opens, and you will receive a notification within 24 hours of the seat becoming "
         "available."),
        ("How do I switch from one course section to another?",
         "Use the \"Swap Section\" option in the registration portal before the add/drop "
         "deadline; after that date you need instructor and advisor approval."),
        ("Can I audit a course instead of taking it for credit?",
         "Yes. Select \"Audit\" instead of \"Credit\" during registration. Audited courses do not "
         "count toward your degree credit total and appear on the transcript with a grade of "
         "\"AU\"."),
        ("How do I request an override for a closed course?",
         "Message the course instructor through the portal requesting an override code, then "
         "enter the code on the registration page before the add/drop deadline."),
        ("What is a registration hold and how do I clear it?",
         "A hold blocks registration until an issue (unpaid balance, missing immunization record, "
         "advising sign-off) is resolved. Check the \"Holds\" tab on your Student Portal dashboard "
         "for the reason and the office to contact."),
        ("When does registration open for returning students?",
         "Registration windows open by credit-hours earned, roughly four weeks before the "
         "semester starts; seniors register first, followed by juniors, sophomores, and "
         "first-year students."),
        ("Can I take a class in another department if I am not majoring in it?",
         "Yes, as long as you meet the course prerequisites and there is available capacity; some "
         "departments reserve a fixed number of seats for majors during the first registration "
         "window."),
        ("How do I withdraw from a single course after the semester has started?",
         "Submit a withdrawal request through the Student Portal before the withdrawal deadline; "
         "the course will show a \"W\" grade instead of a letter grade."),
    ],
    "exam": [
        ("When are final exams scheduled?",
         "Final exams are held during exam week, the week following the last day of regular "
         "classes each semester; the exact schedule is posted on the Registrar's exam calendar "
         "page."),
        ("What do I do if two of my final exams are scheduled at the same time?",
         "Report the conflict to the Registrar's Office at least two weeks before exam week; they "
         "will reschedule one exam through the conflict exam process."),
        ("Can I request a makeup exam if I am sick on exam day?",
         "Yes. Submit a medical note to your instructor and the Dean of Students office within 48 "
         "hours; approved requests are rescheduled through the instructor."),
        ("Are calculators allowed during exams?",
         "It depends on the course policy stated on the syllabus; some quantitative courses allow "
         "a basic calculator, while others require a specific approved model or none at all."),
        ("How do I request extra exam time for a documented disability?",
         "Register with the Office of Accessibility Services and submit your accommodation letter "
         "to each instructor at least two weeks before the exam."),
        ("What happens if I miss a final exam without an approved excuse?",
         "An unexcused absence from a final exam results in a grade of zero for that exam "
         "component unless the instructor's syllabus states otherwise."),
        ("Can I see my exam paper after it is graded?",
         "Yes. You may request to review your graded exam during the instructor's posted office "
         "hours within two weeks of grades being released."),
        ("Is there a curve applied to final exam grades?",
         "Grading curves are decided per course by the instructor and, if used, are described on "
         "the syllabus; there is no university-wide curving policy."),
        ("How early can I arrive to prepare for the exam room?",
         "Exam rooms open 15 minutes before the scheduled start time; students arriving more than "
         "30 minutes late may be denied entry at the proctor's discretion."),
        ("What identification do I need to bring to a final exam?",
         "Bring your HANU student ID card; some large lecture courses also check names against the "
         "official class roster."),
        ("Can I take a final exam early if I have a travel conflict?",
         "Early exams are granted only for university-sanctioned travel (athletics, research "
         "conferences) with written approval from the Dean of Students at least three weeks in "
         "advance."),
        ("How do I dispute a final exam grade I believe was miscalculated?",
         "Contact the instructor within one week of grade posting with the specific question you "
         "are disputing; unresolved disputes escalate to the department chair."),
    ],
    "tuition": [
        ("When is tuition due for the semester?",
         "Tuition payment is due two weeks before the first day of classes each semester; the "
         "exact date is posted on the Bursar's payment calendar."),
        ("Can I pay tuition in installments?",
         "Yes. The Bursar's Office offers a four-installment payment plan with a small enrollment "
         "fee; sign up through the Student Portal before the payment deadline."),
        ("What happens if I miss the tuition payment deadline?",
         "A late fee is added to your account and a registration hold is placed, which blocks "
         "course registration and transcript requests until the balance is resolved."),
        ("How do I apply for a need-based tuition grant?",
         "Submit the HANU Financial Aid Application along with your household income documentation "
         "through the Financial Aid portal by the priority deadline each spring."),
        ("Does tuition cover textbooks and course materials?",
         "No. Tuition covers instruction and standard campus fees only; textbooks, lab kits, and "
         "course materials are billed or purchased separately."),
        ("How do I get a refund if I withdraw from all my classes?",
         "Refunds follow a prorated schedule based on the week of withdrawal; the exact percentage "
         "table is published on the Bursar's refund policy page."),
        ("Is there a tuition discount for taking fewer than 12 credits?",
         "Yes. Students enrolled part time (fewer than 12 credits) are billed per credit hour "
         "instead of the flat full-time rate."),
        ("How do I set up a parent or sponsor to pay my tuition bill?",
         "Add an authorized payer through the Student Portal billing tab; the authorized payer "
         "receives their own login to view and pay the bill."),
        ("What fees are included in the mandatory campus fee?",
         "The mandatory campus fee covers the health center, campus shuttle, recreation center, "
         "and student activity funding; it is billed alongside tuition each semester."),
        ("Can international students pay tuition in a different currency?",
         "Payments are processed in US dollars only; the Bursar's Office lists two approved "
         "third-party services that convert foreign currency payments."),
        ("How do I get a tuition statement for tax or reimbursement purposes?",
         "Download the annual tuition statement from the Student Portal billing tab, or request "
         "one by visiting the Bursar's Office in person."),
        ("What is the penalty for a returned or failed tuition payment?",
         "A returned-payment fee is added to your account and the payment is reversed, which may "
         "re-trigger a registration hold until you submit a valid payment."),
    ],
    "class_schedule": [
        ("Where can I find my class schedule?",
         "Your current class schedule is listed under \"My Schedule\" on the Student Portal, "
         "including room numbers and meeting days."),
        ("How do I check if two of my classes overlap in time?",
         "The registration system blocks you from adding a class that overlaps an already-"
         "enrolled section, and \"My Schedule\" displays a weekly grid to double-check manually."),
        ("Can I request a schedule that avoids early morning classes?",
         "There is no guaranteed morning-free schedule, but you can filter sections by start time "
         "when browsing the course catalog before registering."),
        ("How do I find out which building a class meets in?",
         "Each course section lists a building and room number in the course catalog and on your "
         "\"My Schedule\" page; use the campus map link next to the room number."),
        ("What does it mean if a class is listed as TBA for room or time?",
         "TBA means the room or meeting time had not been finalized when the schedule was "
         "published; check back closer to the semester start or contact the department office."),
        ("Can two sections of the same course have different meeting patterns?",
         "Yes. Departments may offer one section that meets twice a week and another that meets "
         "once a week for the same course; check each section's listed pattern before "
         "registering."),
        ("How do I know if a class has a required lab or discussion section?",
         "Courses with a required lab or discussion list a linked section number in the catalog; "
         "you must register for both the lecture and the linked section together."),
        ("Does the class schedule change during university holidays?",
         "Classes do not meet on official university holidays listed in the academic calendar; "
         "instructors post makeup plans for any missed sessions if needed."),
        ("How far in advance is next semester's class schedule published?",
         "The tentative schedule for the next semester is published on the Registrar's site about "
         "six weeks before registration opens."),
        ("Can I see a professor's office hours from the class schedule page?",
         "Office hours are not shown on the schedule page; check the course syllabus or the "
         "instructor's profile on the department website."),
        ("What do the letters after a course number, like L or D, mean on my schedule?",
         "A trailing L marks a linked laboratory section and a trailing D marks a linked "
         "discussion section attached to the main lecture."),
        ("How do I get a printable version of my weekly schedule?",
         "Use the \"Print Schedule\" button on the \"My Schedule\" page to generate a PDF version "
         "of your weekly grid."),
    ],
    "student_services": [
        ("How do I make an appointment with academic advising?",
         "Book an appointment through the Advising tab on the Student Portal, or call the "
         "Advising Center front desk during business hours."),
        ("Where is the campus health center located?",
         "The Student Health Center is on the ground floor of the Wellness Building, next to the "
         "main Recreation Center entrance."),
        ("How do I request a letter confirming my enrollment status?",
         "Request an enrollment verification letter through the Registrar's self-service page; it "
         "is generated automatically for currently enrolled students."),
        ("What mental health support is available on campus?",
         "Counseling and Psychological Services offers free confidential sessions to enrolled "
         "students; book through the Wellness Building front desk or the online portal."),
        ("How do I report an accessibility barrier on campus?",
         "Submit a report through the Office of Accessibility Services online form, describing "
         "the location and the barrier encountered."),
        ("How do I get a replacement student ID card?",
         "Visit the Card Services office in the Student Union with a photo ID; a replacement fee "
         "applies unless the original card was defective."),
        ("Where can I find information about on-campus jobs?",
         "The Student Employment Office maintains a job board on the Student Portal listing open "
         "on-campus positions and application instructions."),
        ("How do I join a student club or organization?",
         "Browse active clubs on the Student Life portal and contact the club's listed officer, "
         "or attend the fall Involvement Fair to sign up in person."),
        ("What tutoring services are available for struggling in a course?",
         "The Academic Success Center offers free peer tutoring by subject; sign up for a session "
         "through the Tutoring tab on the Student Portal."),
        ("How do I request housing accommodations for a medical condition?",
         "Submit a housing accommodation request with supporting documentation to the Office of "
         "Accessibility Services before the housing selection deadline."),
        ("Who do I contact about a dispute with a roommate?",
         "Contact your Resident Assistant first; unresolved conflicts are escalated to the "
         "Residence Life Coordinator for mediation."),
        ("How do I access legal advice as a student?",
         "The Student Legal Services office offers free initial consultations for enrolled "
         "students; schedule through the Student Union front desk."),
    ],
    "graduation": [
        ("How do I apply to graduate?",
         "Submit the graduation application through the Student Portal by the deadline listed on "
         "the academic calendar for your intended graduation term."),
        ("How do I check if I have met all my degree requirements?",
         "Review your Degree Audit report on the Student Portal, which lists completed, "
         "in-progress, and remaining requirements for your major."),
        ("When is the commencement ceremony held?",
         "Commencement is held the weekend after final exams each spring and fall semester; the "
         "exact date is posted on the Commencement website each term."),
        ("Can I participate in commencement if I have one course left to finish over the summer?",
         "Yes, students within one course of completing their degree may petition to walk in "
         "commencement with approval from the Registrar."),
        ("How do I order my cap and gown for graduation?",
         "Order regalia through the campus bookstore's graduation portal at least four weeks "
         "before the ceremony."),
        ("How long does it take to receive my diploma after graduating?",
         "Diplomas are mailed approximately six to eight weeks after final grades are posted and "
         "degree conferral is confirmed."),
        ("What GPA do I need to graduate with honors?",
         "Latin honors cutoffs (cum laude, magna cum laude, summa cum laude) are published on the "
         "Registrar's honors policy page and are based on cumulative GPA at the time of degree "
         "conferral."),
        ("Can I graduate with a double major?",
         "Yes, provided you complete all requirements for both majors and file a double-major "
         "declaration with the Registrar before your final semester."),
        ("How do I request an official transcript after graduating?",
         "Order an official transcript through the Registrar's transcript request service; alumni "
         "pay the same per-copy fee as current students."),
        ("What happens if I fail to apply for graduation by the deadline?",
         "Late applications are reviewed case by case and may push your degree conferral to the "
         "following term; contact the Registrar as soon as possible."),
        ("Can I change my degree conferral date after applying?",
         "Yes, submit a graduation term change request through the Registrar before the original "
         "term's degree audit deadline."),
        ("How do I make sure my name is pronounced correctly at commencement?",
         "Submit a phonetic spelling of your name through the Commencement RSVP form so the "
         "reader can prepare it in advance."),
    ],
    "technical_support": [
        ("How do I reset my Student Portal password?",
         "Use the \"Forgot Password\" link on the login page and follow the identity verification "
         "steps sent to your recovery contact on file."),
        ("Why can't I connect to the campus Wi-Fi network?",
         "Confirm you are using the HANU-Secure network with your Student Portal credentials; "
         "forget and rejoin the network if the connection keeps failing."),
        ("How do I get access to campus-licensed software?",
         "Download campus-licensed software through the IT Services software portal using your "
         "student login; some titles require connecting to the campus VPN first."),
        ("Who do I contact if my course website will not load?",
         "Contact the IT Help Desk through the Student Portal support ticket form, including the "
         "course name and the error message you see."),
        ("How do I set up my campus email on my phone?",
         "Follow the mobile setup guide on the IT Services site, which lists the mail server "
         "settings needed for common phone mail apps."),
        ("What do I do if I am locked out of my account after too many failed logins?",
         "Wait 15 minutes for the automatic lockout to clear, or contact the IT Help Desk to "
         "verify your identity and unlock the account immediately."),
        ("How do I connect to the campus VPN from off campus?",
         "Install the VPN client listed on the IT Services site and log in with your Student "
         "Portal credentials to access restricted campus resources remotely."),
        ("Why did my file upload fail on the course platform?",
         "Check that the file is under the platform's size limit and in an accepted format; "
         "large video files usually need to be shared as a link instead of a direct upload."),
        ("How do I request a laptop loan from the library?",
         "Reserve a laptop through the Library's equipment loan page; loans are first-come, "
         "first-served each semester with a maximum loan period of one week."),
        ("What should I do if I suspect my account was compromised?",
         "Change your password immediately and report the incident to the IT Help Desk so they "
         "can review recent login activity on your account."),
        ("How do I print documents from a campus computer lab?",
         "Send the print job from any lab computer to the shared print queue, then release it "
         "using your student ID card at any lab printer station."),
        ("Why does the course platform log me out so quickly?",
         "The platform enforces a short inactivity timeout for security; save your work "
         "frequently and consider enabling the \"remember this device\" option if offered."),
    ],
}

# ---------------------------------------------------------------------------
# Notices: 4 per intent (28 total). Each is (title, body, date).
# ---------------------------------------------------------------------------
NOTICE_DATA: dict[str, list[tuple[str, str, str]]] = {
    "course_registration": [
        ("Spring 2027 Registration Windows Posted",
         "Registration windows for Spring 2027 are now posted on the Student Portal. Seniors may "
         "register beginning next Monday, followed by juniors, sophomores, and first-year "
         "students in the following days.",
         "2026-11-03"),
        ("New Waitlist Auto-Enroll Policy",
         "Starting this semester, waitlisted students are automatically enrolled when a seat "
         "opens, instead of receiving only a notification. Check your Student Portal messages "
         "for confirmation before assuming you still need to act.",
         "2026-08-18"),
        ("Add/Drop Deadline Reminder",
         "The add/drop deadline for the current semester is this Friday at 11:59 PM. Courses "
         "dropped after this date will show a withdrawal grade on the transcript.",
         "2026-09-02"),
        ("Prerequisite Override Requests Move Online",
         "Prerequisite override requests must now be submitted through the Student Portal "
         "override form instead of paper forms at the department office.",
         "2026-07-21"),
    ],
    "exam": [
        ("Final Exam Schedule Published",
         "The final exam schedule for this semester is now available on the Registrar's exam "
         "calendar page. Review your exam times before the conflict-reporting deadline.",
         "2026-11-10"),
        ("Conflict Exam Request Deadline",
         "Students with two exams scheduled at the same time must submit a conflict exam request "
         "by the date listed on the exam calendar to be rescheduled.",
         "2026-11-17"),
        ("Accommodated Testing Room Assignments",
         "Students approved for extended time or a reduced-distraction room should check the "
         "Office of Accessibility Services portal for their assigned testing room before exam "
         "week.",
         "2026-11-24"),
        ("Exam Week Building Hours Extended",
         "Library and study room hours are extended during exam week; see the Library's "
         "exam-week hours notice for the updated schedule.",
         "2026-12-01"),
    ],
    "tuition": [
        ("Tuition Payment Deadline Approaching",
         "Tuition payment for the upcoming semester is due in two weeks. Set up an installment "
         "plan now if you need to spread out payments.",
         "2026-07-15"),
        ("Installment Plan Enrollment Fee Update",
         "The enrollment fee for the four-installment tuition payment plan has been updated; see "
         "the Bursar's payment plan page for the current amount.",
         "2026-06-20"),
        ("New Authorized Payer Feature Live",
         "Students can now add a parent or sponsor as an authorized payer directly from the "
         "Student Portal billing tab.",
         "2026-05-11"),
        ("Refund Schedule Posted for Withdrawals",
         "The prorated refund schedule for students withdrawing from all classes this semester is "
         "now posted on the Bursar's refund policy page.",
         "2026-08-25"),
    ],
    "class_schedule": [
        ("Next Semester Schedule Preview Available",
         "A tentative preview of next semester's class schedule is now available on the "
         "Registrar's site ahead of the official registration window.",
         "2026-10-06"),
        ("Room Changes Posted for Several Sections",
         "Several course sections have updated room assignments due to building maintenance; "
         "check My Schedule for the latest room numbers.",
         "2026-09-08"),
        ("New Printable Weekly Schedule Option",
         "You can now generate a PDF of your weekly class schedule directly from the My Schedule "
         "page using the new Print Schedule button.",
         "2026-08-04"),
        ("Linked Lab and Discussion Sections Reminder",
         "Remember that courses with a linked lab or discussion section require registering for "
         "both the lecture and the linked section together.",
         "2026-08-12"),
    ],
    "student_services": [
        ("Extended Counseling Hours This Month",
         "Counseling and Psychological Services is offering extended evening hours this month to "
         "accommodate more student appointments.",
         "2026-10-13"),
        ("Involvement Fair Date Announced",
         "The fall Involvement Fair where student clubs recruit new members will be held in the "
         "Student Union Plaza; check the Student Life portal for the exact date.",
         "2026-08-28"),
        ("Tutoring Sign-Ups Open for the Semester",
         "Sign-ups for free peer tutoring through the Academic Success Center are now open for "
         "the current semester on the Student Portal.",
         "2026-09-01"),
        ("ID Card Replacement Fee Waived for Stolen Cards",
         "Card Services is temporarily waiving the replacement fee for students who file a police "
         "report for a stolen student ID card.",
         "2026-09-22"),
    ],
    "graduation": [
        ("Graduation Application Deadline Reminder",
         "The deadline to apply for graduation this term is next Friday. Submit your application "
         "through the Student Portal before the deadline.",
         "2026-10-20"),
        ("Commencement Date Confirmed",
         "The commencement ceremony date for this term has been confirmed; see the Commencement "
         "website for the schedule and guest ticket policy.",
         "2026-10-27"),
        ("Cap and Gown Ordering Window Open",
         "The campus bookstore's graduation portal is now open for ordering caps, gowns, and "
         "regalia for this term's commencement.",
         "2026-11-05"),
        ("Honors Cutoff GPA Updated for This Term",
         "The cumulative GPA cutoffs for Latin honors this term have been posted on the "
         "Registrar's honors policy page.",
         "2026-11-12"),
    ],
    "technical_support": [
        ("Scheduled Wi-Fi Maintenance This Weekend",
         "Campus Wi-Fi, including HANU-Secure, will have brief outages this weekend during "
         "scheduled maintenance overnight.",
         "2026-09-11"),
        ("New Self-Service Password Reset Tool",
         "A new self-service password reset tool is now available on the Student Portal login "
         "page, reducing the need to contact the IT Help Desk directly.",
         "2026-08-07"),
        ("VPN Client Update Required",
         "Students connecting to the campus VPN from off campus must update to the latest VPN "
         "client version listed on the IT Services site.",
         "2026-09-15"),
        ("Laptop Loan Program Extended Hours",
         "The Library's laptop loan desk is extending its hours during the first two weeks of "
         "the semester to meet higher demand.",
         "2026-08-20"),
    ],
}

# ---------------------------------------------------------------------------
# Seed questions used for the required experiment's normal/paraphrase/typo
# triplets. Each entry is (faq_index_within_intent, paraphrase). The index
# is 0-based into FAQ_DATA[intent].
# ---------------------------------------------------------------------------
SEED_PARAPHRASES: dict[str, list[tuple[int, str]]] = {
    "course_registration": [
        (0, "What's the process for signing up for courses at Hanoi University?"),
        (1, "By when do I need to add or drop a class this fall?"),
        (2, "Is it possible to enroll in a class without finishing the required prerequisite first?"),
        (4, "What should I do if the class section I need has no open seats?"),
        (8, "My account has a registration hold - what does that mean and how do I remove it?"),
    ],
    "exam": [
        (0, "When does final exam week happen?"),
        (1, "Two of my finals overlap on the same day - who do I tell?"),
        (2, "If I get sick on the day of my final, can I take it later instead?"),
        (4, "How can I get additional time on exams because of a disability accommodation?"),
        (5, "What's the penalty for skipping a final without a valid excuse?"),
    ],
    "tuition": [
        (0, "What's the payment deadline for this semester's tuition?"),
        (1, "Is there a way to split my tuition payment into smaller chunks?"),
        (2, "What are the consequences of paying my tuition bill late?"),
        (3, "How can I apply for financial aid based on my family's income?"),
        (5, "If I drop every class this semester, how do refunds work?"),
    ],
    "class_schedule": [
        (0, "Where do I go to see my current classes and times?"),
        (1, "How can I tell if my class times conflict with each other?"),
        (3, "Where can I see what building my class is held in?"),
        (4, "My class shows TBA for the room - what does that mean?"),
        (6, "How can I tell whether a course comes with a mandatory lab or discussion?"),
    ],
    "student_services": [
        (0, "How do I book a meeting with an academic advisor?"),
        (1, "Where on campus is the student health center?"),
        (3, "What counseling or mental health resources can I access at HANU?"),
        (5, "I lost my student ID - how do I get a new one?"),
        (8, "Where can I find free tutoring if I'm behind in a class?"),
    ],
    "graduation": [
        (0, "What's the process for applying for graduation?"),
        (1, "How can I confirm I've completed everything needed for my degree?"),
        (2, "When does the graduation ceremony take place?"),
        (4, "Where do I order my graduation cap and gown?"),
        (8, "After I graduate, how do I get an official transcript sent out?"),
    ],
    "technical_support": [
        (0, "I forgot my Student Portal password - how do I reset it?"),
        (1, "My laptop won't join the campus Wi-Fi - what should I check?"),
        (2, "How can I download software that the campus provides a license for?"),
        (5, "My account got locked after failed login attempts - what now?"),
        (6, "How do I use the VPN to reach campus resources from home?"),
    ],
}

# ---------------------------------------------------------------------------
# Out-of-corpus queries: genuinely unanswerable from faq.json/notices.json.
# Correct system behavior is "no document / low confidence", never a
# fabricated answer.
# ---------------------------------------------------------------------------
OUT_OF_CORPUS_QUERIES: list[str] = [
    "What is the weather forecast for this weekend?",
    "Who won the university's last home basketball game?",
    "What is the campus mascot's name?",
    "Can I bring my dog to live with me in the dorm?",
    "Does the university offer a shuttle to the airport on weekends?",
    "What is the current price of gold?",
    "Is there a farmers market near campus on Sundays?",
    "What time does the campus coffee shop close on Fridays?",
    "Does the university have a rooftop stargazing club?",
    "What's the best restaurant near campus for vegan food?",
    "Can I rent a kayak from the campus recreation center?",
    "What is the university president's favorite book?",
    "Are there fireworks on campus for the Fourth of July?",
    "Does the university sell parking permits for food trucks?",
    "What is the score of tonight's professional football game?",
]


def _make_typo(text: str, rng: random.Random) -> str:
    """Deterministically introduce one adjacent-letter-swap typo into ``text``."""
    words = text.split(" ")
    candidates = [i for i, w in enumerate(words) if len(re.sub(r"[^a-zA-Z]", "", w)) >= 5]
    if not candidates:
        candidates = list(range(len(words)))
    for _ in range(len(candidates)):
        idx = rng.choice(candidates)
        word = words[idx]
        letters = [i for i, c in enumerate(word) if c.isalpha()]
        swap_positions = [p for p in letters if p + 1 < len(word) and (p + 1) in letters and word[p] != word[p + 1]]
        if swap_positions:
            p = rng.choice(swap_positions)
            chars = list(word)
            chars[p], chars[p + 1] = chars[p + 1], chars[p]
            new_word = "".join(chars)
            if new_word != word:
                words[idx] = new_word
                result = " ".join(words)
                if result != text:
                    return result
        candidates.remove(idx)
        if not candidates:
            break
    # Fallback: drop one character from the longest word (still a valid,
    # different, "noisy typing" corruption).
    longest_idx = max(range(len(words)), key=lambda i: len(words[i]))
    word = words[longest_idx]
    if len(word) > 3:
        words[longest_idx] = word[:-2] + word[-1]
    return " ".join(words)


def build_faq_entries() -> list[dict[str, Any]]:
    entries = []
    for intent, items in FAQ_DATA.items():
        for i, (question, answer) in enumerate(items, start=1):
            entries.append(
                {
                    "id": f"faq_{intent}_{i:02d}",
                    "intent": intent,
                    "question": question,
                    "answer": answer,
                }
            )
    return entries


def build_notice_entries() -> list[dict[str, Any]]:
    entries = []
    for intent, items in NOTICE_DATA.items():
        for i, (title, body, date) in enumerate(items, start=1):
            entries.append(
                {
                    "id": f"notice_{intent}_{i:02d}",
                    "intent": intent,
                    "title": title,
                    "body": body,
                    "date": date,
                }
            )
    return entries


def build_queries(seed: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    row_index = 0
    for intent, seeds in SEED_PARAPHRASES.items():
        for faq_index, paraphrase in seeds:
            question, _answer = FAQ_DATA[intent][faq_index]
            doc_id = f"faq_{intent}_{faq_index + 1:02d}"
            typo_rng = random.Random(seed * 1000 + row_index)
            typo_query = _make_typo(question, typo_rng)
            rows.append(
                {
                    "query": question,
                    "type": "normal",
                    "expected_intent": intent,
                    "expected_doc_id": doc_id,
                    "notes": "verbatim FAQ question",
                }
            )
            rows.append(
                {
                    "query": paraphrase,
                    "type": "paraphrase",
                    "expected_intent": intent,
                    "expected_doc_id": doc_id,
                    "notes": "reworded, same underlying question",
                }
            )
            rows.append(
                {
                    "query": typo_query,
                    "type": "typo",
                    "expected_intent": intent,
                    "expected_doc_id": doc_id,
                    "notes": "one adjacent-letter-swap typo injected",
                }
            )
            row_index += 1

    for query in OUT_OF_CORPUS_QUERIES:
        rows.append(
            {
                "query": query,
                "type": "out_of_corpus",
                "expected_intent": "",
                "expected_doc_id": "",
                "notes": "correct behavior: no document / low confidence, do not fabricate",
            }
        )

    rng = random.Random(seed)
    rng.shuffle(rows)
    for i, row in enumerate(rows, start=1):
        row_with_id = {"id": f"q_{i:03d}"}
        row_with_id.update(row)
        rows[i - 1] = row_with_id
    return rows


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_intents_csv(path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["intent", "description"])
        for intent, description in INTENTS:
            writer.writerow([intent, description])


def write_queries_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["id", "query", "type", "expected_intent", "expected_doc_id", "notes"]
        )
        writer.writeheader()
        writer.writerows(rows)


def write_documents_md(path: Path, faq_entries: list[dict[str, Any]], notice_entries: list[dict[str, Any]]) -> None:
    lines = [
        "# Document index",
        "",
        "Synthetic, educational \"Hanoi University\" (HANU) FAQ and notice",
        "corpus. Every id below is defined in `faq.json` or `notices.json`.",
        "This file is provided infrastructure (for the starter's document",
        "listing); classifying intent or retrieving the right document for a",
        "query is the graded core (`starter/student_core.py`).",
        "",
    ]
    for intent, _description in INTENTS:
        lines.append(f"## {intent}")
        lines.append("")
        lines.append("| id | type | title/question |")
        lines.append("|---|---|---|")
        for entry in faq_entries:
            if entry["intent"] == intent:
                lines.append(f"| `{entry['id']}` | faq | {entry['question']} |")
        for entry in notice_entries:
            if entry["intent"] == intent:
                lines.append(f"| `{entry['id']}` | notice | {entry['title']} |")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Deterministic seed (default: 42).")
    parser.add_argument("--out", type=Path, default=DATA_DIR, help="Output directory (default: data/).")
    args = parser.parse_args()

    faq_entries = build_faq_entries()
    notice_entries = build_notice_entries()
    queries = build_queries(args.seed)

    args.out.mkdir(parents=True, exist_ok=True)
    write_json(args.out / "faq.json", faq_entries)
    write_json(args.out / "notices.json", notice_entries)
    write_intents_csv(args.out / "intents.csv")
    write_documents_md(args.out / "documents.md", faq_entries, notice_entries)
    write_queries_csv(args.out / "queries_test.csv", queries)

    print(
        f"Wrote {len(faq_entries)} FAQ entries, {len(notice_entries)} notices "
        f"({len(faq_entries) + len(notice_entries)} total documents), "
        f"{len(INTENTS)} intents, and {len(queries)} evaluation queries "
        f"under {args.out} (seed={args.seed})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
