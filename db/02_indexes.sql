USE crm_db;
CREATE INDEX idx_leads_created ON leads(created_at);
CREATE INDEX idx_leads_owner ON leads(owner_id);
CREATE INDEX idx_opps_stage ON opportunities(stage_id);
CREATE INDEX idx_opps_owner ON opportunities(owner_id);
CREATE INDEX idx_activities_created ON activities(created_at);
CREATE INDEX idx_customers_owner ON customers(owner_id);
CREATE INDEX idx_leads_source ON leads(source_id);
