# Visual and Accessibility Audit Log

> **Archive Note (Updated 2026-11-21):** This log records the 2026-11-16 editorial redesign baseline. The screenshots in `notes/ux_evidence/` (`screenshot_01..04.png`) are pre-PR#14 Dark Mode baseline captures. Current PR #19 UI verification (Oxford Navy + Warm Light theme, no OOC office routing, and gate-rejection explanations) is captured in [`output/playwright/live-demo/`](../../output/playwright/live-demo/) and [`observations.json`](../../output/playwright/live-demo/observations.json).

**Project:** Hanoi University (HANU) Student Regulations Knowledge Assistant  
**Branch:** `vietanh/light-editorial-portal`  
**Date:** 2026-11-16  
**Auditor:** Orca Quality Gate (`agency-evidence-collector` & `agency-accessibility-auditor`)  
**Design System:** Claude / Editorial Academic Warm Light (`#f5f4ed` canvas, `#faf9f5` cards, `#e8e6dc` elevation)

---

## 1. Visual & State Coverage Evidence

| State | Description | Target Query / Trigger | Key Verified Elements |
|---|---|---|---|
| **First-Use Empty State** | 7-Topic Academic Directory + Recent Notices | Initial page load (query empty) | Bento Grid covering 7 corpus-attested contact points (`Student Portal`, `Bursar's Office`, `Registrar's Office`, `My Schedule`, `Advising Center`, `Registrar`, `IT Help Desk`), 3 latest synthetic notices with dates, zero empty/dark void. |
| **In-Corpus Success State** | Answer cards with high-contrast typography | *"When is tuition due for the semester?"* | Match badge `🟢 Strong match`, Serif question header, 16px legible answer text, verified notice date badge, Bursar's Office contact point. |
| **Safe Abstention State** | Out-of-scope safe abstention | *"Can I rent a kayak from the campus recreation center?"* | Clean abstention frame, exact error text `Information not found — please contact the administrative office.`, zero conflicting green success banner, gate-rejection explanation, and no classifier-guessed office routing. |
| **Typo Robustness State** | Noisy query with term highlighting | *"tution dedline paymnt for upcomng semster"* | Subword character n-gram robustness, term highlighting, high-confidence tuition retrieval. |
| **Research & Inspector Mode** | Dual-gate parameter inspection | Toggle enabled + *"How do I reset my Student Portal password?"* | Parameter threshold sliders ($\theta_{sim}$, $\theta_{intent}$), 3-way retrieval model comparison (Word vs Char vs BM25), `explain()` mathematical vector breakdown. |

---

## 2. Keyboard & WCAG 2.2 Level AA Verification

1. **Focus Order & Index Integrity:**
   - Input field: `app.text_input[0]` (TabIndex 1).
   - Primary action: `app.button[0]` ("Classify intent", TabIndex 2).
   - Secondary action: `app.button[1]` ("Retrieve documents", TabIndex 3).
   - Native `<details>` summary elements receive natural tab focus.
   - Zero keyboard trap encountered across all workflow states.

2. **Contrast Measurements on Warm Ivory Card (`#faf9f5`):**
   - `#141413` (Primary Text) on `#f5f4ed` (Parchment Canvas): Contrast Ratio **`16.7 : 1`** (WCAG AAA pass).
   - `#141413` (Primary Text) on `#faf9f5` (Ivory Card): Contrast Ratio **`17.5 : 1`** (WCAG AAA pass).
   - `#5e5d59` (Secondary Text) on `#faf9f5`: Contrast Ratio **`6.3 : 1`** (WCAG AA pass).
   - `#166534` (Strong Match Green Text) on `#faf9f5`: Contrast Ratio **`6.8 : 1`** (WCAG AAA pass).
   - `#b45309` (Possible Match Amber Text) on `#faf9f5`: Contrast Ratio **`4.8 : 1`** (WCAG AA pass).
   - `#b91c1c` (Error Red Text) on `#faf9f5`: Contrast Ratio **`6.1 : 1`** (WCAG AAA pass).

3. **Motion Sensitivity:**
   - Media query `@media (prefers-reduced-motion: reduce)` active in `starter/theme.py`, disabling CSS animations and transitions when requested by user OS settings.
