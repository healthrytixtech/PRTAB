# Stitch ZIP → App Route Mapping

## User Pages (User UI ZIP → /app/user/*)
| Zip | Page | Route |
|-----|------|--------|
| 1 | Role Selection (MindfulPath) | /user/role |
| 2 | Onboarding & Signup | /user/signup, /login |
| 3 | Home & Navigation | /user (dashboard) |
| 4 | AI Chat (Compassionate AI) | /user/chat |
| 5 | Self-Care Hub | /user/wellness |
| 6 | Urgent Support / Crisis | /user/support (redirect for Red) |

## Professional Pages (Professional Dashboard UI ZIP → /app/professional/*)
| Zip | Page | Route |
|-----|------|--------|
| 8 | Verification Form | /professional/verify |
| 9 | Dashboard Overview | /professional (dashboard) |
| 10 | Secure Voice Session | /professional/session/[id] |
| 11 | Case Notes & History | /professional/cases, /professional/cases/[id] |
| 12 | Schedule & Availability | /professional/schedule |

## Admin Pages (Admin Dashboard UI ZIP → /app/admin/*)
| Zip | Page | Route |
|-----|------|--------|
| 7 | Triage Dashboard | /admin (live queue, analytics, assign) |

## Shared
- Layout, auth wrapper, theme (Tailwind, Manrope, primary #13ecda)
- No animations/motion per requirements
