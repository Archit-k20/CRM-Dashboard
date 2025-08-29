-- A. New leads per week
SELECT YEAR(created_at) AS yr, WEEK(created_at,1) AS wk, COUNT(*) AS new_leads
FROM leads
WHERE created_at BETWEEN '2025-01-01' AND '2025-12-31'
GROUP BY yr, wk
ORDER BY yr, wk;


-- B. Lead → Opportunity conversion rate (period)
-- conversions in period / leads in same period
WITH period_leads AS (
  SELECT COUNT(*) as leads
  FROM leads
  WHERE created_at BETWEEN '2025-01-01' AND '2025-12-31'
),
period_opps AS (
  SELECT COUNT(DISTINCT o.id) as opps
  FROM opportunities o
  WHERE o.created_at BETWEEN '2025-01-01' AND '2025-12-31'
)
SELECT period_opps.opps, period_leads.leads,
       ROUND(100 * period_opps.opps / NULLIF(period_leads.leads,0),2) AS conversion_pct
FROM period_leads, period_opps;



-- C. Pipeline value by stage
SELECT s.name AS stage, SUM(o.value) AS pipeline_value
FROM opportunities o
LEFT JOIN stages s ON o.stage_id = s.id
WHERE o.status <> 'LOST'
GROUP BY s.name
ORDER BY pipeline_value DESC;


-- D. Average time in a stage (days) — using history
SELECT s.name AS stage,
       ROUND(AVG(DATEDIFF(COALESCE(h.left_at, NOW()), h.entered_at)),1) AS avg_days_in_stage
FROM opportunity_stage_history h
JOIN stages s ON h.stage_id = s.id
GROUP BY s.name
ORDER BY avg_days_in_stage DESC;


-- E. Win rate
SELECT COUNT(*) AS total_opps,
       SUM(o.status = 'WON') AS won,
       ROUND(100 * SUM(o.status = 'WON') / NULLIF(COUNT(*),0),2) AS win_rate_pct
FROM opportunities o;


-- F. Top sources by conversion
SELECT l.source_id, s.name AS source_name,
       COUNT(DISTINCT l.id) AS leads,
       COUNT(DISTINCT o.id) AS opps,
       ROUND(100 * COUNT(DISTINCT o.id) / NULLIF(COUNT(DISTINCT l.id),0),2) AS conv_pct
FROM leads l
LEFT JOIN sources s ON l.source_id = s.id
LEFT JOIN opportunities o ON o.lead_id = l.id
GROUP BY l.source_id, s.name
ORDER BY conv_pct DESC
LIMIT 10;
