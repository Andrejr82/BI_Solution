# Implementation Plan: User Segmentation & Dashboard Storytelling

## Objective
Implement role-based and segment-based access control for "user" level accounts and enhance the "Monitoramento" dashboard with storytelling elements ("Context7" philosophy).

## Phase 1: Backend Authentication Updates
**Goal:** Ensure the frontend receives the user's allowed segments in the JWT.

1.  **Modify `backend/app/api/v1/endpoints/auth.py`**:
    *   Update `login` endpoint:
        *   Retrieve `allowed_segments` from `user_data` (Parquet/DB).
        *   Include `allowed_segments` in the `token_data` dictionary.
    *   Update `refresh_token` endpoint:
        *   Ensure `allowed_segments` is preserved or re-fetched during refresh.
    *   *Note:* The `UserResponse` schema already supports `allowed_segments`, so the API contract is ready.

## Phase 2: Frontend Authentication & Access Control
**Goal:** Restrict "user" access to specific pages and tabs based on the requirements.

1.  **Update `frontend-solid/src/store/auth.ts`**:
    *   Update `User` interface to include `allowed_segments: string[]`.
    *   Update `validateAndDecodeToken` to extract `allowed_segments` from the JWT payload.

2.  **Update `frontend-solid/src/Layout.tsx` (Navigation)**:
    *   Refactor `menuItems` filtering logic.
    *   **Rule:** If role is "user", ONLY show:
        *   Monitoramento (`/dashboard`)
        *   Rupturas Críticas (`/rupturas`)
        *   Transferências (`/transferencias`)
        *   ChatBI (`/chat`)
        *   Alterar Senha (`/change-password` or similar)
    *   Ensure other items (Admin, Settings, etc.) are hidden.

3.  **Update `frontend-solid/src/pages/Help.tsx`**:
    *   Modify the tab rendering logic.
    *   **Rule:** If role is "user", only render tabs:
        *   "Guia Rápido"
        *   "FAQ"

## Phase 3: Dashboard Storytelling ("Context7")
**Goal:** Transform the "Monitoramento" page from a data display to a narrative interface.

1.  **Refactor `frontend-solid/src/pages/Dashboard.tsx`**:
    *   **Header**: Add a dynamic "State of the Business" summary line (e.g., "Status: Healthy" or "Attention Required").
    *   **KPI Cards**: Add "Trend Context" (e.g., "↑ 5% vs last week" - if data allows, or qualitative labels like "Critical" in red).
    *   **Charts**:
        *   Update Chart Titles to be descriptive questions or statements (e.g., "Which categories drive revenue?" instead of "Sales by Category").
        *   Use annotations to highlight the "Top 1" product or critical ruptures.
    *   **Layout**: Reorder components to follow a logical flow:
        1.  **Headline** (Status)
        2.  **Key Metrics** (The "What")
        3.  **Charts** (The "Why/Trends")
        4.  **Action Items** (Ruptures list/Table).

## Execution Strategy
1.  Apply Backend changes.
2.  Apply Frontend Auth changes.
3.  Apply Navigation/Help restrictions.
4.  Apply Dashboard improvements.
5.  Verify with "user" login.
