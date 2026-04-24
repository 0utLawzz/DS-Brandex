# Victorian Legal Dashboard UI Theme Guide

**Project:** Brandex Firm Management System (CMS) - IP Law Firm Record Management Dashboard

**Applies to:** Django templates under `cases/templates/` styled via `cases/static/cases/victorian.css`.

**Theme entry point:** `cases/templates/cases/base.html` loads Bootstrap + `victorian.css`.

---

## 🎨 CORE STYLE

**Style:** Victorian Legal Elegance
**Mood:** Premium, archival, authoritative, structured
**Visual Language:** Legal documents, engraved borders, old registry books, official seals

---

## 🎨 COLOR SYSTEM

- **Primary (Main brand / buttons / highlights):** `#722F37` (Deep Burgundy)
- **Secondary (Sidebar / accents):** `#2E5339` (Forest Green)
- **Accent (Gold highlights / borders):** `#B8860B` (Antique Gold)
- **Background:** `#F5E6D3` (Warm parchment)
- **Surface / Cards:** `#FDF5E6` (Soft paper tone)
- **Text Primary:** `#4A2932`
- **Text Muted:** `#7A5C5C`

👉 Use **gold only for emphasis**, not everywhere.

---

## ✍️ TYPOGRAPHY

- **Headings:** `'Playfair Display', serif`
  - Bold, uppercase for titles
  - Slight letter-spacing (0.5px–1px)
- **Body:** `'Inter', sans-serif`
  - Clean for readability

👉 Headings should feel like **legal certificates**
👉 Body text should feel modern & usable

---

## 🧱 GLOBAL DESIGN RULES

- **Border Radius:** `4px` (sharp, formal)
- **Border Width:** `2px–3px`
- **Border Color:** `#B8860B` (gold tone)
- **Shadow:** `0px 4px 0px rgba(0,0,0,0.15)` (hard shadow, not soft blur)
- **Spacing System:** 8px grid
- **Card Padding:** 16px–24px

---

## 🧩 COMPONENT SYSTEM

### 🧭 NAVIGATION (SIDEBAR)

**Style:**

- Background: `#2E5339`
- Text: Light cream
- Active Item:
  - Background: `#722F37`
  - Left gold border strip
- Hover:
  - Slight gold tint overlay

**Menu Items Example:**

- Dashboard
- Trademark Cases
- Clients
- Documents
- Hearings
- Notices
- Reports

👉 Add small **icon + label**
👉 Icons should be minimal (line icons)

---

### 📊 TOP BAR

- Background: parchment tone
- Bottom border: gold line
- Right side:
  - User profile
  - Notifications
- Left:
  - Page title in serif font

---

### 🪪 CARDS (MAIN UI BLOCKS)

**Style:**

- Background: `#FDF5E6`
- Border: 2px solid gold
- Shadow: hard drop

**Variants:**

- Case summary card
- Status card
- Activity card

👉 Add **thin decorative corner lines** (Victorian touch)

---

### 🔘 BUTTON SYSTEM

#### Primary Button

- Background: `#722F37`
- Text: White
- Border: Gold
- Hover: Darker burgundy
- Shadow: Strong

#### Secondary Button

- Background: `#2E5339`
- Text: White

#### Outline Button

- Transparent
- Border: Gold
- Text: Burgundy

#### Disabled

- Greyed parchment tone
- No shadow

👉 Buttons should feel like **official stamps**

---

### 🧾 FORMS

**Inputs:**
- Background: light parchment
- Border: 2px solid gold
- Focus: Burgundy glow

**Labels:**
- Serif font (small caps style)

**Dropdowns:**
- Classic arrow
- Minimal modern behavior

---

### 🏷️ BADGES / STATUS TAGS

Map your legal workflow:
- Stage 1 → Soft gold
- Stage 2 → Green
- Stage 3 → Burgundy
- Stage 4 → Dark gold

**Style:**
- Small rectangular tags
- Bold text
- Slight border

---

### 📑 TABLES (IMPORTANT FOR YOUR SYSTEM)

- Header:
  - Burgundy background
  - White text
- Rows:
  - Alternating parchment shades
- Borders:
  - Thin gold lines

👉 Add hover highlight

---

### 📦 MODALS / POPUPS

- Centered
- Thick gold border
- Slight shadow
- Header in serif font

---

### 📈 DASHBOARD WIDGETS

Include:
- Case Status Overview
- Recent Filings
- Upcoming Hearings
- Alerts / Notices

👉 Use cards with icons + numbers

---

## 🧠 UX BEHAVIOR

- Smooth but minimal animations (150–200ms)
- No flashy modern gradients
- Focus on **clarity + authority**

---

## 🪄 DECORATIVE ELEMENTS (IMPORTANT)

- Thin ornamental borders
- Subtle corner flourishes
- Divider lines (gold)
- Avoid clutter

👉 Think: **old legal book meets modern SaaS**

---

## 🧩 EXTRA (FOR YOUR IP SYSTEM)

Add modules like:
- Trademark Timeline Tracker
- Document Vault
- Client Ledger
- Notice Alerts System

---

## 🧭 How To Apply This Theme (Project Instructions)

### 1) Where to change theme styles

- **Global theme file:** `cases/static/cases/victorian.css`
- **Base layout:** `cases/templates/cases/base.html`

Rule: keep theme decisions inside `victorian.css` (colors, borders, typography). Pages should mostly apply **classes**, not inline styles.

### 2) Typography rules (important)

- **Body text:** Inter (default on `body.victorian-bg`)
- **Headings / section titles:** Playfair Display (already applied to `.victorian-title` and `.victorian-card .card-header`)
- **Small caps:** only add when needed via `.small-cap` (do not force small caps on the whole page)

Custom fonts (self-hosted):

- **Headings:** `Syndra-SemiBold.otf` (loaded via `@font-face` as `Syndra`)
- **Body:** `Mision.ttf` (loaded via `@font-face` as `Mision`)

Rule: do not apply `font-variant: small-caps;` globally. Only use the `.small-cap` utility class on labels/headings.

### 3) Component recipes (copy/paste patterns)

#### Cards

- Use: `class="victorian-card card"`
- For header/title: Bootstrap header element with `small-cap`

Example structure:

```html
<div class="victorian-card card">
  <div class="card-header py-3 small-cap">Section Title</div>
  <div class="card-body">...</div>
</div>
```

#### Buttons

- **Primary (default):** `class="btn victorian-btn"`
- **Secondary:** `class="btn victorian-btn btn-secondary"`
- **Outline:** `class="btn victorian-btn victorian-btn-outline"`

Rule: buttons should look like an official stamp. Avoid modern gradients.

#### Links

- Use: `class="victorian-link"`

#### Forms

- Inputs/select/textarea: add `victorian-input`
- Labels that should appear “certificate-like”: add `small-cap` (theme will apply serif label styling)

Example:

```html
<label class="form-label small-cap">Deadline</label>
<input class="form-control victorian-input" type="date" />
```

#### Tables

- Use: `class="table victorian-table"`

Rules:
- Table header is burgundy with white text.
- Rows alternate parchment shades.
- Borders are thin gold lines.

#### Modals

- Use `victorian-card` on `.modal-content` to inherit border/shadow.

Example:

```html
<div class="modal-content victorian-card">
  <div class="card-header py-3 small-cap">Modal Title</div>
  <div class="card-body">...</div>
</div>
```

### 4) Spacing & layout

- Use Bootstrap spacing utilities (`p-3`, `py-3`, `mb-3`, `gap-2`, etc.) aligned to an **8px grid**.
- For dashboard/detail layouts, use existing `dst-*` layout helpers (e.g. `dst-grid`, `dst-span-2`).

### 5) Theme rules for contributors (Do / Don’t)

- **Do:** use `var(--primary)`, `var(--secondary)`, `var(--accent)` in CSS when adding new rules.
- **Do:** keep border radius at `4px` and borders at `2px–3px`.
- **Do:** use the hard shadow `0px 4px 0px rgba(0,0,0,0.15)` style.
- **Do:** keep animations minimal (150–200ms) and subtle.

- **Don’t:** use heavy blur shadows.
- **Don’t:** introduce neon colors, gradients, or glassmorphism.
- **Don’t:** spam gold everywhere; gold is for emphasis/borders.

---

## 📋 IMPLEMENTATION CHECKLIST

- [ ] Colors match exactly as specified
- [ ] Playfair Display font for headings
- [ ] Inter font for body text
- [ ] Border radius set to 4px
- [ ] Border width 2px-3px
- [ ] Gold border color (#B8860B) used correctly
- [ ] Hard shadow (0px 4px 0px rgba(0,0,0,0.15))
- [ ] Small caps applied to headings and labels
- [ ] Cards have decorative corner elements
- [ ] Buttons feel like official stamps
- [ ] Tables have burgundy headers with gold borders
- [ ] Modals have thick gold borders
- [ ] No flashy gradients
- [ ] Focus on clarity and authority
