-- PostgreSQL-oriented portfolio data mart. Synthetic data only.
create table if not exists dim_agent (agent_id text primary key, skill_group text not null, active boolean not null default true);
create table if not exists dim_policy_version (policy_id text not null, version text not null, effective_from date not null, effective_to date not null, title text not null, primary key (policy_id, version));
create table if not exists fact_ticket (ticket_id text primary key, created_at timestamptz not null, channel text not null, issue_type text not null, agent_id text references dim_agent(agent_id), status text not null check (status in ('open', 'closed')), reopened boolean not null, handle_minutes integer check (handle_minutes >= 0));
create table if not exists fact_ai_assist (ticket_id text primary key references fact_ticket(ticket_id), policy_id text, policy_version text, retrieval_score numeric, risk_score integer not null, route text not null check (route in ('agent_approval', 'specialist_review')), review_outcome text check (review_outcome in ('approved', 'edited', 'rejected')), latency_ms integer, estimated_cost_usd numeric);

create or replace view mart_daily_cs_kpi as
select date_trunc('day', created_at)::date as kpi_date, issue_type, channel, count(*) as ticket_count,
  count(*) filter (where status = 'closed') as closed_ticket_count,
  round(avg(handle_minutes) filter (where status = 'closed'), 1) as avg_handle_minutes,
  round(avg(reopened::int)::numeric, 3) as reopen_rate,
  round(avg((handle_minutes <= 60)::int)::numeric, 3) as sla_within_60m_rate
from fact_ticket group by 1, 2, 3;

-- Candidate operational anomalies, not confirmed incident root causes.
with daily as (select date_trunc('day', created_at)::date as kpi_date, issue_type, count(*) as ticket_count from fact_ticket group by 1, 2),
baseline as (select *, avg(ticket_count) over (partition by issue_type order by kpi_date rows between 7 preceding and 1 preceding) as trailing_mean from daily)
select kpi_date, issue_type, ticket_count, round(trailing_mean, 1) as trailing_mean from baseline where ticket_count > coalesce(trailing_mean, ticket_count) * 1.5;
