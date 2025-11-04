-- =====================================================
-- CONTEXT: Understanding Our Business Questions
-- Before writing complex queries, document what we need to know
-- =====================================================

/*
BUSINESS QUESTIONS (in order of our story):
1. How fast are we growing? (Acquisition)
2. Are we keeping customers? (Churn trends)
3. Which channels deliver value? (LTV:CAC by channel)
4. Why are customers leaving? (Churn composition)
5. What should we do differently? (Recommendations)

AUDIENCE CONSTRAINTS:
- Budget committee sees 100+ presentations/year
- They decide in first 3 minutes if they're interested
- They care about Rand impact, not % improvements
- They need ONE clear action, not five maybes
*/

-- Create schema
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS presentation;
