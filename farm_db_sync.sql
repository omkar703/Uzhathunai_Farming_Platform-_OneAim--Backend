--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4 (Debian 15.4-1.pgdg110+1)
-- Dumped by pg_dump version 15.4 (Debian 15.4-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: tiger; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tiger;


ALTER SCHEMA tiger OWNER TO postgres;

--
-- Name: tiger_data; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tiger_data;


ALTER SCHEMA tiger_data OWNER TO postgres;

--
-- Name: topology; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA topology;


ALTER SCHEMA topology OWNER TO postgres;

--
-- Name: SCHEMA topology; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA topology IS 'PostGIS Topology schema';


--
-- Name: fuzzystrmatch; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch WITH SCHEMA public;


--
-- Name: EXTENSION fuzzystrmatch; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION fuzzystrmatch IS 'determine similarities and distance between strings';


--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: postgis_tiger_geocoder; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder WITH SCHEMA tiger;


--
-- Name: EXTENSION postgis_tiger_geocoder; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_tiger_geocoder IS 'PostGIS tiger geocoder and reverse geocoder';


--
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: audit_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.audit_status AS ENUM (
    'PENDING',
    'DRAFT',
    'IN_PROGRESS',
    'SUBMITTED_FOR_REVIEW',
    'IN_ANALYSIS',
    'SUBMITTED',
    'REVIEWED',
    'FINALIZED',
    'SHARED'
);


ALTER TYPE public.audit_status OWNER TO postgres;

--
-- Name: chat_context_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.chat_context_type AS ENUM (
    'WORK_ORDER',
    'ORGANIZATION',
    'SUPPORT'
);


ALTER TYPE public.chat_context_type OWNER TO postgres;

--
-- Name: crop_lifecycle; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.crop_lifecycle AS ENUM (
    'PLANNED',
    'PLANTED',
    'TRANSPLANTED',
    'PRODUCTION',
    'COMPLETED',
    'TERMINATED',
    'CLOSED'
);


ALTER TYPE public.crop_lifecycle OWNER TO postgres;

--
-- Name: input_item_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.input_item_type AS ENUM (
    'FERTILIZER',
    'PESTICIDE',
    'OTHER'
);


ALTER TYPE public.input_item_type OWNER TO postgres;

--
-- Name: invitation_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.invitation_status AS ENUM (
    'PENDING',
    'ACCEPTED',
    'REJECTED',
    'EXPIRED',
    'CANCELLED'
);


ALTER TYPE public.invitation_status OWNER TO postgres;

--
-- Name: issue_severity; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.issue_severity AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL'
);


ALTER TYPE public.issue_severity OWNER TO postgres;

--
-- Name: TYPE issue_severity; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TYPE public.issue_severity IS 'Severity levels for audit issues: LOW, MEDIUM, HIGH, CRITICAL';


--
-- Name: measurement_unit_category; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.measurement_unit_category AS ENUM (
    'AREA',
    'VOLUME',
    'WEIGHT',
    'LENGTH',
    'COUNT'
);


ALTER TYPE public.measurement_unit_category OWNER TO postgres;

--
-- Name: member_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.member_status AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'SUSPENDED'
);


ALTER TYPE public.member_status OWNER TO postgres;

--
-- Name: message_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.message_type AS ENUM (
    'TEXT',
    'IMAGE',
    'FILE',
    'SYSTEM'
);


ALTER TYPE public.message_type OWNER TO postgres;

--
-- Name: notification_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.notification_type AS ENUM (
    'INFO',
    'SUCCESS',
    'WARNING',
    'ALERT',
    'REMINDER',
    'ERROR'
);


ALTER TYPE public.notification_type OWNER TO postgres;

--
-- Name: organization_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.organization_status AS ENUM (
    'NOT_STARTED',
    'IN_PROGRESS',
    'ACTIVE',
    'INACTIVE',
    'SUSPENDED'
);


ALTER TYPE public.organization_status OWNER TO postgres;

--
-- Name: organization_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.organization_type AS ENUM (
    'FARMING',
    'FSP'
);


ALTER TYPE public.organization_type OWNER TO postgres;

--
-- Name: parameter_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.parameter_type AS ENUM (
    'TEXT',
    'NUMERIC',
    'SINGLE_SELECT',
    'MULTI_SELECT',
    'DATE',
    'BOOLEAN',
    'PHOTO'
);


ALTER TYPE public.parameter_type OWNER TO postgres;

--
-- Name: payment_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.payment_status AS ENUM (
    'PENDING',
    'COMPLETED',
    'FAILED',
    'REFUNDED'
);


ALTER TYPE public.payment_status OWNER TO postgres;

--
-- Name: permission_effect; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.permission_effect AS ENUM (
    'ALLOW',
    'DENY'
);


ALTER TYPE public.permission_effect OWNER TO postgres;

--
-- Name: query_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.query_status AS ENUM (
    'OPEN',
    'IN_PROGRESS',
    'PENDING_CLARIFICATION',
    'RESOLVED',
    'REOPEN',
    'CLOSED'
);


ALTER TYPE public.query_status OWNER TO postgres;

--
-- Name: schedule_change_trigger; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.schedule_change_trigger AS ENUM (
    'MANUAL',
    'QUERY',
    'AUDIT'
);


ALTER TYPE public.schedule_change_trigger OWNER TO postgres;

--
-- Name: service_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.service_status AS ENUM (
    'ACTIVE',
    'INACTIVE'
);


ALTER TYPE public.service_status OWNER TO postgres;

--
-- Name: subscription_plan; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.subscription_plan AS ENUM (
    'FREE',
    'BASIC',
    'PREMIUM',
    'ENTERPRISE'
);


ALTER TYPE public.subscription_plan OWNER TO postgres;

--
-- Name: sync_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.sync_status AS ENUM (
    'pending_sync',
    'synced',
    'sync_failed'
);


ALTER TYPE public.sync_status OWNER TO postgres;

--
-- Name: TYPE sync_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TYPE public.sync_status IS 'Sync status for offline audit operations: pending_sync (queued), synced (completed), sync_failed (error)';


--
-- Name: task_category; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.task_category AS ENUM (
    'FARMING',
    'FSP_CONSULTANCY'
);


ALTER TYPE public.task_category OWNER TO postgres;

--
-- Name: task_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.task_status AS ENUM (
    'NOT_STARTED',
    'IN_PROGRESS',
    'COMPLETED',
    'MISSED',
    'CANCELLED',
    'ON_HOLD'
);


ALTER TYPE public.task_status OWNER TO postgres;

--
-- Name: transaction_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.transaction_type AS ENUM (
    'INCOME',
    'EXPENSE'
);


ALTER TYPE public.transaction_type OWNER TO postgres;

--
-- Name: user_role_scope; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.user_role_scope AS ENUM (
    'SYSTEM',
    'ORGANIZATION'
);


ALTER TYPE public.user_role_scope OWNER TO postgres;

--
-- Name: work_order_scope_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.work_order_scope_type AS ENUM (
    'ORGANIZATION',
    'FARM',
    'PLOT',
    'CROP'
);


ALTER TYPE public.work_order_scope_type OWNER TO postgres;

--
-- Name: work_order_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.work_order_status AS ENUM (
    'PENDING',
    'ACCEPTED',
    'ACTIVE',
    'COMPLETED',
    'CANCELLED',
    'REJECTED'
);


ALTER TYPE public.work_order_status OWNER TO postgres;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_issues; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_issues (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    audit_id uuid NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    severity public.issue_severity,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    recommendation text,
    CONSTRAINT chk_audit_issues_severity_valid CHECK ((severity = ANY (ARRAY['LOW'::public.issue_severity, 'MEDIUM'::public.issue_severity, 'HIGH'::public.issue_severity, 'CRITICAL'::public.issue_severity])))
);


ALTER TABLE public.audit_issues OWNER TO postgres;

--
-- Name: COLUMN audit_issues.severity; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_issues.severity IS 'Issue severity level using issue_severity ENUM: LOW, MEDIUM, HIGH, CRITICAL';


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_log (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    table_name character varying(100) NOT NULL,
    record_id uuid NOT NULL,
    action character varying(20) NOT NULL,
    old_values jsonb,
    new_values jsonb,
    changed_by uuid,
    changed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    ip_address inet,
    user_agent text
);


ALTER TABLE public.audit_log OWNER TO postgres;

--
-- Name: audit_parameter_instances; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_parameter_instances (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    audit_id uuid NOT NULL,
    template_section_id uuid NOT NULL,
    parameter_id uuid NOT NULL,
    sort_order integer DEFAULT 0,
    is_required boolean DEFAULT false,
    parameter_snapshot jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.audit_parameter_instances OWNER TO postgres;

--
-- Name: TABLE audit_parameter_instances; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.audit_parameter_instances IS 'Audit-specific parameter instances with configuration snapshots';


--
-- Name: COLUMN audit_parameter_instances.parameter_snapshot; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_parameter_instances.parameter_snapshot IS 'JSONB: {"parameter_id": "uuid", "code": "PLANT_HEIGHT", "parameter_type": "NUMERIC", "parameter_metadata": {"min_value": 0, "max_value": 500, "unit": "cm"}, "option_set_id": "uuid", "options": [{"option_id": "uuid", "code": "GREEN", "display_text": "Green"}], "translations": {"en": {"name": "Plant Height", "help_text": "Measure from soil"}}, "additional": {...}}';


--
-- Name: audit_recommendations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_recommendations (
    id uuid NOT NULL,
    audit_id uuid NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid
);


ALTER TABLE public.audit_recommendations OWNER TO postgres;

--
-- Name: audit_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_reports (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    audit_id uuid NOT NULL,
    report_html text,
    report_images jsonb DEFAULT '[]'::jsonb,
    pdf_url text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid
);


ALTER TABLE public.audit_reports OWNER TO postgres;

--
-- Name: audit_response_photos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_response_photos (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    audit_response_id uuid,
    file_url character varying(500) NOT NULL,
    file_key character varying(500),
    caption text,
    uploaded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    uploaded_by uuid,
    audit_id uuid NOT NULL,
    is_flagged_for_report boolean DEFAULT false NOT NULL
);


ALTER TABLE public.audit_response_photos OWNER TO postgres;

--
-- Name: TABLE audit_response_photos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.audit_response_photos IS 'Photos attached by auditor to audit responses';


--
-- Name: audit_responses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_responses (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    audit_id uuid NOT NULL,
    audit_parameter_instance_id uuid NOT NULL,
    response_text text,
    response_numeric numeric(15,4),
    response_date date,
    response_options uuid[],
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid
);


ALTER TABLE public.audit_responses OWNER TO postgres;

--
-- Name: TABLE audit_responses; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.audit_responses IS 'Auditor responses to audit parameters';


--
-- Name: audit_review_photos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_review_photos (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    audit_response_photo_id uuid NOT NULL,
    is_flagged_for_report boolean DEFAULT false,
    caption text,
    reviewed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    reviewed_by uuid
);


ALTER TABLE public.audit_review_photos OWNER TO postgres;

--
-- Name: TABLE audit_review_photos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.audit_review_photos IS 'Reviewer annotations on auditor photos';


--
-- Name: audit_reviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_reviews (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    audit_response_id uuid NOT NULL,
    response_text text,
    response_numeric numeric(15,4),
    response_date date,
    response_option_ids uuid[],
    is_flagged_for_report boolean DEFAULT false,
    reviewed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    reviewed_by uuid
);


ALTER TABLE public.audit_reviews OWNER TO postgres;

--
-- Name: TABLE audit_reviews; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.audit_reviews IS 'Reviewer responses that override or supplement auditor responses';


--
-- Name: COLUMN audit_reviews.response_option_ids; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_reviews.response_option_ids IS 'Array of option IDs chosen by reviewer';


--
-- Name: audits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audits (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    fsp_organization_id uuid NOT NULL,
    farming_organization_id uuid NOT NULL,
    work_order_id uuid,
    crop_id uuid NOT NULL,
    template_id uuid NOT NULL,
    audit_number character varying(50),
    name character varying(200) NOT NULL,
    status public.audit_status DEFAULT 'DRAFT'::public.audit_status,
    template_snapshot jsonb,
    audit_date date,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    finalized_at timestamp with time zone,
    finalized_by uuid,
    shared_at timestamp with time zone,
    sync_status public.sync_status DEFAULT 'synced'::public.sync_status,
    assigned_to_user_id uuid,
    analyst_user_id uuid,
    has_report boolean DEFAULT false,
    CONSTRAINT chk_audits_sync_status_valid CHECK ((sync_status = ANY (ARRAY['pending_sync'::public.sync_status, 'synced'::public.sync_status, 'sync_failed'::public.sync_status])))
);


ALTER TABLE public.audits OWNER TO postgres;

--
-- Name: TABLE audits; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.audits IS 'Crop audits conducted by FSPs';


--
-- Name: COLUMN audits.work_order_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audits.work_order_id IS 'Optional work order association - audits can be created independently of work orders';


--
-- Name: COLUMN audits.template_snapshot; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audits.template_snapshot IS 'JSONB: {"template_id": "uuid", "code": "TOMATO_AUDIT_V1", "version": 1, "sections": [{"section_id": "uuid", "code": "PLANT_HEALTH", "name": "Plant Health", "parameters": [{"parameter_id": "uuid", "code": "PLANT_HEIGHT", "parameter_type": "NUMERIC", "is_required": true, "parameter_snapshot": {...}}]}], "additional": {...}}';


--
-- Name: COLUMN audits.sync_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audits.sync_status IS 'Sync status for offline operations: pending_sync (queued for sync), synced (successfully synced), sync_failed (sync error occurred)';


--
-- Name: COLUMN audits.has_report; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audits.has_report IS 'If true, an audit report has been generated for this audit';


--
-- Name: chat_channel_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_channel_members (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    channel_id uuid,
    organization_id uuid,
    joined_at timestamp with time zone DEFAULT now(),
    added_by uuid
);


ALTER TABLE public.chat_channel_members OWNER TO postgres;

--
-- Name: chat_channels; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_channels (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    context_type public.chat_context_type NOT NULL,
    context_id uuid NOT NULL,
    name character varying(255),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    created_by uuid,
    updated_by uuid
);


ALTER TABLE public.chat_channels OWNER TO postgres;

--
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_messages (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    channel_id uuid,
    sender_id uuid,
    sender_org_id uuid,
    message_type public.message_type DEFAULT 'TEXT'::public.message_type NOT NULL,
    content text,
    media_url text,
    is_system_message boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp with time zone
);


ALTER TABLE public.chat_messages OWNER TO postgres;

--
-- Name: crop_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crop_categories (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.crop_categories OWNER TO postgres;

--
-- Name: crop_category_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crop_category_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    crop_category_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    name character varying(200) NOT NULL,
    description text
);


ALTER TABLE public.crop_category_translations OWNER TO postgres;

--
-- Name: crop_lifecycle_photos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crop_lifecycle_photos (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    crop_id uuid NOT NULL,
    file_url character varying(500) NOT NULL,
    file_key character varying(500),
    caption text,
    photo_date date,
    uploaded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    uploaded_by uuid
);


ALTER TABLE public.crop_lifecycle_photos OWNER TO postgres;

--
-- Name: crop_type_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crop_type_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    crop_type_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    name character varying(200) NOT NULL,
    description text
);


ALTER TABLE public.crop_type_translations OWNER TO postgres;

--
-- Name: crop_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crop_types (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    category_id uuid NOT NULL,
    code character varying(50) NOT NULL,
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.crop_types OWNER TO postgres;

--
-- Name: crop_varieties; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crop_varieties (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    crop_type_id uuid NOT NULL,
    code character varying(50) NOT NULL,
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    variety_metadata jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.crop_varieties OWNER TO postgres;

--
-- Name: COLUMN crop_varieties.variety_metadata; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.crop_varieties.variety_metadata IS 'JSONB: {"maturity_days": 90, "yield_potential_kg_per_acre": 15000, "plant_spacing_cm": 60, "row_spacing_cm": 90, "water_requirement": "high", "disease_resistance": ["early_blight", "late_blight"], "suitable_seasons": ["kharif", "rabi"], "additional": {...}}';


--
-- Name: crop_variety_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crop_variety_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    crop_variety_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    name character varying(200) NOT NULL,
    description text
);


ALTER TABLE public.crop_variety_translations OWNER TO postgres;

--
-- Name: crop_yield_photos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crop_yield_photos (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    crop_yield_id uuid NOT NULL,
    photo_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.crop_yield_photos OWNER TO postgres;

--
-- Name: crop_yields; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crop_yields (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    crop_id uuid NOT NULL,
    yield_type character varying(20) NOT NULL,
    harvest_date date,
    quantity numeric(15,4) NOT NULL,
    quantity_unit_id uuid,
    harvest_area numeric(15,4),
    harvest_area_unit_id uuid,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    CONSTRAINT chk_harvest_area_unit CHECK ((((harvest_area IS NULL) AND (harvest_area_unit_id IS NULL)) OR ((harvest_area IS NOT NULL) AND (harvest_area_unit_id IS NOT NULL))))
);


ALTER TABLE public.crop_yields OWNER TO postgres;

--
-- Name: COLUMN crop_yields.harvest_area; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.crop_yields.harvest_area IS 'Actual harvested area (optional). Some harvests are area-based (e.g., vegetables), others are count-based (e.g., coconuts).';


--
-- Name: crops; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crops (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    plot_id uuid NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    crop_type_id uuid,
    crop_variety_id uuid,
    area numeric(15,4),
    area_unit_id uuid,
    plant_count integer,
    lifecycle public.crop_lifecycle DEFAULT 'PLANNED'::public.crop_lifecycle,
    planned_date date,
    planted_date date,
    transplanted_date date,
    production_start_date date,
    completed_date date,
    terminated_date date,
    closed_date date,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    variety_name character varying(200)
);


ALTER TABLE public.crops OWNER TO postgres;

--
-- Name: TABLE crops; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.crops IS 'Crops grown in plots with lifecycle tracking';


--
-- Name: farm_irrigation_modes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.farm_irrigation_modes (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    farm_id uuid NOT NULL,
    irrigation_mode_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.farm_irrigation_modes OWNER TO postgres;

--
-- Name: farm_soil_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.farm_soil_types (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    farm_id uuid NOT NULL,
    soil_type_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.farm_soil_types OWNER TO postgres;

--
-- Name: farm_supervisors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.farm_supervisors (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    farm_id uuid NOT NULL,
    supervisor_id uuid NOT NULL,
    assigned_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    assigned_by uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.farm_supervisors OWNER TO postgres;

--
-- Name: farm_water_sources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.farm_water_sources (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    farm_id uuid NOT NULL,
    water_source_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.farm_water_sources OWNER TO postgres;

--
-- Name: farms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.farms (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    organization_id uuid NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    address text,
    district character varying(100),
    state character varying(100),
    pincode character varying(20),
    location public.geography(Point,4326),
    boundary public.geography(Polygon,4326),
    area numeric(15,4),
    area_unit_id uuid,
    farm_attributes jsonb,
    manager_id uuid,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    city character varying(100)
);


ALTER TABLE public.farms OWNER TO postgres;

--
-- Name: TABLE farms; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.farms IS 'Farms owned by farming organizations with GIS data';


--
-- Name: COLUMN farms.farm_attributes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.farms.farm_attributes IS 'JSONB: {"soil_ec": 2.5, "soil_ph": 6.8, "water_ec": 1.2, "water_ph": 7.0, "additional": {...}}';


--
-- Name: finance_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_categories (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    transaction_type public.transaction_type NOT NULL,
    code character varying(50) NOT NULL,
    is_system_defined boolean DEFAULT true,
    owner_org_id uuid,
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    CONSTRAINT chk_finance_category_ownership CHECK ((((is_system_defined = true) AND (owner_org_id IS NULL)) OR ((is_system_defined = false) AND (owner_org_id IS NOT NULL))))
);


ALTER TABLE public.finance_categories OWNER TO postgres;

--
-- Name: TABLE finance_categories; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.finance_categories IS 'Finance transaction categories (system-defined and organization-specific)';


--
-- Name: COLUMN finance_categories.is_system_defined; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.finance_categories.is_system_defined IS 'true for system-defined categories, false for organization-specific';


--
-- Name: COLUMN finance_categories.owner_org_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.finance_categories.owner_org_id IS 'NULL for system-defined, organization_id for org-specific categories';


--
-- Name: CONSTRAINT chk_finance_category_ownership ON finance_categories; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON CONSTRAINT chk_finance_category_ownership ON public.finance_categories IS 'Ensures system categories have no owner, org categories have owner';


--
-- Name: finance_category_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_category_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    category_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.finance_category_translations OWNER TO postgres;

--
-- Name: TABLE finance_category_translations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.finance_category_translations IS 'Multilingual translations for finance categories (system and org-specific)';


--
-- Name: finance_transaction_attachments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_transaction_attachments (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    transaction_id uuid NOT NULL,
    file_url character varying(500) NOT NULL,
    file_key character varying(500),
    file_name character varying(255),
    file_type character varying(50),
    file_size integer,
    uploaded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    uploaded_by uuid
);


ALTER TABLE public.finance_transaction_attachments OWNER TO postgres;

--
-- Name: finance_transaction_splits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_transaction_splits (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    transaction_id uuid NOT NULL,
    farm_id uuid,
    plot_id uuid,
    crop_id uuid,
    split_amount numeric(15,2) NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    CONSTRAINT chk_split_reference CHECK ((((farm_id IS NOT NULL) AND (plot_id IS NULL) AND (crop_id IS NULL)) OR ((farm_id IS NULL) AND (plot_id IS NOT NULL) AND (crop_id IS NULL)) OR ((farm_id IS NULL) AND (plot_id IS NULL) AND (crop_id IS NOT NULL))))
);


ALTER TABLE public.finance_transaction_splits OWNER TO postgres;

--
-- Name: finance_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_transactions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    organization_id uuid NOT NULL,
    transaction_type public.transaction_type NOT NULL,
    category_id uuid NOT NULL,
    transaction_date date NOT NULL,
    amount numeric(15,2) NOT NULL,
    currency character varying(10) DEFAULT 'INR'::character varying,
    description text,
    reference_number character varying(100),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid
);


ALTER TABLE public.finance_transactions OWNER TO postgres;

--
-- Name: TABLE finance_transactions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.finance_transactions IS 'Income and expense transactions with unified category reference';


--
-- Name: fsp_approval_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fsp_approval_documents (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    fsp_organization_id uuid NOT NULL,
    document_type character varying(100) NOT NULL,
    file_url character varying(500) NOT NULL,
    file_key character varying(500),
    file_name character varying(255),
    uploaded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    uploaded_by uuid
);


ALTER TABLE public.fsp_approval_documents OWNER TO postgres;

--
-- Name: fsp_service_listings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fsp_service_listings (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    fsp_organization_id uuid NOT NULL,
    service_id uuid NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    service_area_districts text[],
    pricing_model character varying(50),
    base_price numeric(15,2),
    currency character varying(10) DEFAULT 'INR'::character varying,
    status public.service_status DEFAULT 'ACTIVE'::public.service_status,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid
);


ALTER TABLE public.fsp_service_listings OWNER TO postgres;

--
-- Name: input_item_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.input_item_categories (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    is_system_defined boolean DEFAULT true,
    owner_org_id uuid,
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    CONSTRAINT chk_input_category_ownership CHECK ((((is_system_defined = true) AND (owner_org_id IS NULL)) OR ((is_system_defined = false) AND (owner_org_id IS NOT NULL))))
);


ALTER TABLE public.input_item_categories OWNER TO postgres;

--
-- Name: TABLE input_item_categories; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.input_item_categories IS 'Input item categories (system-defined and organization-specific)';


--
-- Name: COLUMN input_item_categories.is_system_defined; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.input_item_categories.is_system_defined IS 'true for system-defined categories, false for organization-specific';


--
-- Name: COLUMN input_item_categories.owner_org_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.input_item_categories.owner_org_id IS 'NULL for system-defined, organization_id for org-specific categories';


--
-- Name: CONSTRAINT chk_input_category_ownership ON input_item_categories; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON CONSTRAINT chk_input_category_ownership ON public.input_item_categories IS 'Ensures system categories have no owner, org categories have owner';


--
-- Name: input_item_category_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.input_item_category_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    category_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.input_item_category_translations OWNER TO postgres;

--
-- Name: TABLE input_item_category_translations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.input_item_category_translations IS 'Multilingual translations for input item categories (system and org-specific)';


--
-- Name: input_item_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.input_item_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    input_item_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.input_item_translations OWNER TO postgres;

--
-- Name: TABLE input_item_translations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.input_item_translations IS 'Multilingual translations for input items (system and org-specific)';


--
-- Name: input_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.input_items (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    category_id uuid NOT NULL,
    code character varying(50) NOT NULL,
    is_system_defined boolean DEFAULT true,
    owner_org_id uuid,
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    type public.input_item_type,
    default_unit_id uuid,
    item_metadata jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    CONSTRAINT chk_input_item_ownership CHECK ((((is_system_defined = true) AND (owner_org_id IS NULL)) OR ((is_system_defined = false) AND (owner_org_id IS NOT NULL))))
);


ALTER TABLE public.input_items OWNER TO postgres;

--
-- Name: TABLE input_items; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.input_items IS 'Input items like fertilizers, pesticides (system-defined and organization-specific)';


--
-- Name: COLUMN input_items.is_system_defined; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.input_items.is_system_defined IS 'true for system-defined items, false for organization-specific';


--
-- Name: COLUMN input_items.owner_org_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.input_items.owner_org_id IS 'NULL for system-defined, organization_id for org-specific items';


--
-- Name: COLUMN input_items.item_metadata; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.input_items.item_metadata IS 'JSONB: {"nutrients": ["Nitrogen 46%", "Boron 0.1%"], "npk_ratio": "46-0-0", "active_ingredients": ["imidacloprid 35.8% w/w", "another chemical 1% w/v"], "mode_of_action": ["systemic", "contact", "systemic & contact"], "effective_against": ["thrips", "red mites", "leaf miner"], "application_method": ["soil", "fertigation"], "form": "granular", "solubility": "high", "brand": "Tata", "manufacturer": "Tata Chemicals","storage_instructions": "Keep in cool dry place", "additional": {...}}';


--
-- Name: CONSTRAINT chk_input_item_ownership ON input_items; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON CONSTRAINT chk_input_item_ownership ON public.input_items IS 'Ensures system items have no owner, org items have owner';


--
-- Name: master_service_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.master_service_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    service_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    display_name character varying(200) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.master_service_translations OWNER TO postgres;

--
-- Name: master_services; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.master_services (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    status public.service_status DEFAULT 'ACTIVE'::public.service_status,
    sort_order integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.master_services OWNER TO postgres;

--
-- Name: measurement_unit_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.measurement_unit_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    measurement_unit_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.measurement_unit_translations OWNER TO postgres;

--
-- Name: measurement_units; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.measurement_units (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    category public.measurement_unit_category NOT NULL,
    code character varying(20) NOT NULL,
    symbol character varying(20),
    is_base_unit boolean DEFAULT false,
    conversion_factor numeric(20,10),
    sort_order integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.measurement_units OWNER TO postgres;

--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    organization_id uuid,
    notification_type public.notification_type NOT NULL,
    title character varying(200) NOT NULL,
    message text NOT NULL,
    reference_type character varying(50),
    reference_id uuid,
    is_read boolean DEFAULT false,
    read_at timestamp with time zone,
    is_push_sent boolean DEFAULT false,
    push_sent_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: COLUMN notifications.notification_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.notifications.notification_type IS 'Notification category: INFO (general), SUCCESS (positive), WARNING (caution), ALERT (important), REMINDER (time-based), ERROR (failure)';


--
-- Name: COLUMN notifications.reference_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.notifications.reference_type IS 'Entity type: QUERY, WORK_ORDER, AUDIT, TASK, INVITATION, MEMBER, PAYMENT, SUBSCRIPTION, etc.';


--
-- Name: option_sets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.option_sets (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    is_system_defined boolean DEFAULT true,
    owner_org_id uuid,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_by uuid
);


ALTER TABLE public.option_sets OWNER TO postgres;

--
-- Name: TABLE option_sets; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.option_sets IS 'Reusable option lists for parameters (system or organization-specific)';


--
-- Name: option_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.option_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    option_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    display_text character varying(200) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.option_translations OWNER TO postgres;

--
-- Name: options; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.options (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    option_set_id uuid NOT NULL,
    code character varying(50) NOT NULL,
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.options OWNER TO postgres;

--
-- Name: TABLE options; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.options IS 'Individual options within option sets';


--
-- Name: org_member_invitations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.org_member_invitations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    organization_id uuid NOT NULL,
    inviter_id uuid NOT NULL,
    invitee_email character varying(255) NOT NULL,
    invitee_user_id uuid,
    role_id uuid NOT NULL,
    status public.invitation_status DEFAULT 'PENDING'::public.invitation_status,
    invited_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    responded_at timestamp with time zone,
    expires_at timestamp with time zone,
    message text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.org_member_invitations OWNER TO postgres;

--
-- Name: TABLE org_member_invitations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.org_member_invitations IS 'Invitation workflow for adding members to organizations';


--
-- Name: org_member_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.org_member_roles (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    organization_id uuid,
    role_id uuid NOT NULL,
    is_primary boolean DEFAULT false,
    assigned_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    assigned_by uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.org_member_roles OWNER TO postgres;

--
-- Name: TABLE org_member_roles; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.org_member_roles IS 'User roles within organizations (supports multiple roles)';


--
-- Name: org_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.org_members (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    organization_id uuid NOT NULL,
    status public.member_status DEFAULT 'ACTIVE'::public.member_status,
    joined_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    left_at timestamp with time zone,
    invited_by uuid,
    invitation_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.org_members OWNER TO postgres;

--
-- Name: TABLE org_members; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.org_members IS 'Organization membership with status tracking';


--
-- Name: org_role_permission_overrides; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.org_role_permission_overrides (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    organization_id uuid NOT NULL,
    role_id uuid NOT NULL,
    permission_id uuid NOT NULL,
    effect public.permission_effect NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid
);


ALTER TABLE public.org_role_permission_overrides OWNER TO postgres;

--
-- Name: org_subscription_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.org_subscription_history (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    organization_id uuid NOT NULL,
    subscription_plan_id uuid NOT NULL,
    plan_version integer,
    change_type character varying(50) NOT NULL,
    subscription_start_date date NOT NULL,
    subscription_end_date date,
    billing_cycle character varying(20),
    amount numeric(10,2),
    payment_status public.payment_status DEFAULT 'PENDING'::public.payment_status,
    payment_date timestamp with time zone,
    payment_reference character varying(100),
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid
);


ALTER TABLE public.org_subscription_history OWNER TO postgres;

--
-- Name: organizations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organizations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    logo_url text,
    organization_type public.organization_type NOT NULL,
    status public.organization_status DEFAULT 'NOT_STARTED'::public.organization_status,
    registration_number character varying(100),
    address text,
    district character varying(100),
    state character varying(100),
    pincode character varying(20),
    contact_email character varying(255),
    contact_phone character varying(20),
    subscription_plan_id uuid,
    subscription_start_date date,
    subscription_end_date date,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    is_approved boolean DEFAULT false
);


ALTER TABLE public.organizations OWNER TO postgres;

--
-- Name: TABLE organizations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.organizations IS 'Stores farming and FSP organizations';


--
-- Name: COLUMN organizations.is_approved; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.organizations.is_approved IS 'Approve status for FSP/Farming organizations';


--
-- Name: parameter_option_set_map; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parameter_option_set_map (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    parameter_id uuid NOT NULL,
    option_set_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.parameter_option_set_map OWNER TO postgres;

--
-- Name: parameter_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parameter_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    parameter_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    help_text text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.parameter_translations OWNER TO postgres;

--
-- Name: parameters; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parameters (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    parameter_type public.parameter_type NOT NULL,
    is_system_defined boolean DEFAULT true,
    owner_org_id uuid,
    is_active boolean DEFAULT true,
    parameter_metadata jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid
);


ALTER TABLE public.parameters OWNER TO postgres;

--
-- Name: TABLE parameters; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.parameters IS 'Parameter library for audits (system or organization-specific)';


--
-- Name: COLUMN parameters.parameter_metadata; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.parameters.parameter_metadata IS 'JSONB: {"min_value": 0, "max_value": 100, "unit": "cm", "decimal_places": 2, "min_photos": 0, "max_photos": 3, "validation_rules": {"required": true, "range": [0, 100]}, "display_format": "0.00", "help_text": "Measure from soil level", "additional": {...}}';


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    resource character varying(100) NOT NULL,
    action character varying(50) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: plot_irrigation_modes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plot_irrigation_modes (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    plot_id uuid NOT NULL,
    irrigation_mode_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.plot_irrigation_modes OWNER TO postgres;

--
-- Name: plot_soil_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plot_soil_types (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    plot_id uuid NOT NULL,
    soil_type_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.plot_soil_types OWNER TO postgres;

--
-- Name: plot_water_sources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plot_water_sources (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    plot_id uuid NOT NULL,
    water_source_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.plot_water_sources OWNER TO postgres;

--
-- Name: plots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plots (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    farm_id uuid NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    boundary public.geography(Polygon,4326),
    area numeric(15,4),
    area_unit_id uuid,
    plot_attributes jsonb,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid
);


ALTER TABLE public.plots OWNER TO postgres;

--
-- Name: TABLE plots; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.plots IS 'Subdivisions of farms with GIS boundaries';


--
-- Name: COLUMN plots.plot_attributes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.plots.plot_attributes IS 'JSONB: {"soil_ec": 2.5, "soil_ph": 6.8, "water_ec": 1.2, "water_ph": 7.0, "additional": {...}}';


--
-- Name: push_notification_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.push_notification_tokens (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    device_token character varying(500) NOT NULL,
    device_type character varying(20),
    device_id character varying(200),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.push_notification_tokens OWNER TO postgres;

--
-- Name: queries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.queries (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    farming_organization_id uuid NOT NULL,
    fsp_organization_id uuid NOT NULL,
    work_order_id uuid NOT NULL,
    query_number character varying(50),
    title character varying(200) NOT NULL,
    description text NOT NULL,
    farm_id uuid,
    plot_id uuid,
    crop_id uuid,
    status public.query_status DEFAULT 'OPEN'::public.query_status,
    priority character varying(20) DEFAULT 'MEDIUM'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    resolved_at timestamp with time zone,
    resolved_by uuid,
    closed_at timestamp with time zone
);


ALTER TABLE public.queries OWNER TO postgres;

--
-- Name: TABLE queries; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.queries IS 'Consultation queries from farming orgs to FSPs';


--
-- Name: query_photos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.query_photos (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    query_id uuid,
    query_response_id uuid,
    file_url character varying(500) NOT NULL,
    file_key character varying(500),
    caption text,
    uploaded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    uploaded_by uuid,
    CONSTRAINT chk_query_photos_reference CHECK ((((query_id IS NOT NULL) AND (query_response_id IS NULL)) OR ((query_id IS NULL) AND (query_response_id IS NOT NULL))))
);


ALTER TABLE public.query_photos OWNER TO postgres;

--
-- Name: TABLE query_photos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.query_photos IS 'Photos attached to queries (when submitted) or query responses (when FSP responds)';


--
-- Name: CONSTRAINT chk_query_photos_reference ON query_photos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON CONSTRAINT chk_query_photos_reference ON public.query_photos IS 'Photo must be linked to either query OR query_response, not both';


--
-- Name: query_responses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.query_responses (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    query_id uuid NOT NULL,
    response_text text NOT NULL,
    has_recommendation boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid
);


ALTER TABLE public.query_responses OWNER TO postgres;

--
-- Name: reference_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reference_data (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    type_id uuid NOT NULL,
    code character varying(100) NOT NULL,
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    reference_metadata jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.reference_data OWNER TO postgres;

--
-- Name: COLUMN reference_data.reference_metadata; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.reference_data.reference_metadata IS 'JSONB: {"capacity_liters": 50000, "depth_meters": 15, "water_quality": "good", "seasonal_availability": ["summer", "winter"], "maintenance_required": true, "last_cleaned": "2024-01-15", "additional": {...}}';


--
-- Name: reference_data_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reference_data_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    reference_data_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    display_name character varying(200) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.reference_data_translations OWNER TO postgres;

--
-- Name: reference_data_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reference_data_types (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.reference_data_types OWNER TO postgres;

--
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.refresh_tokens (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    token_hash character varying(255) NOT NULL,
    device_info jsonb,
    expires_at timestamp with time zone NOT NULL,
    is_revoked boolean DEFAULT false,
    revoked_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.refresh_tokens OWNER TO postgres;

--
-- Name: TABLE refresh_tokens; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.refresh_tokens IS 'Stores refresh tokens for JWT authentication';


--
-- Name: COLUMN refresh_tokens.token_hash; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.refresh_tokens.token_hash IS 'SHA-256 hash of the refresh token for security';


--
-- Name: COLUMN refresh_tokens.device_info; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.refresh_tokens.device_info IS 'JSONB: {"device_type": "mobile", "device_name": "iPhone 12", "os": "iOS 15", "app_version": "2.0.0"}';


--
-- Name: COLUMN refresh_tokens.is_revoked; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.refresh_tokens.is_revoked IS 'True when user logs out or changes password';


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    role_id uuid NOT NULL,
    permission_id uuid NOT NULL,
    effect public.permission_effect DEFAULT 'ALLOW'::public.permission_effect,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    display_name character varying(200) NOT NULL,
    scope public.user_role_scope NOT NULL,
    description text,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: schedule_change_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedule_change_log (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    schedule_id uuid NOT NULL,
    trigger_type public.schedule_change_trigger NOT NULL,
    trigger_reference_id uuid,
    change_type character varying(20) NOT NULL,
    task_id uuid,
    task_details_before jsonb,
    task_details_after jsonb,
    change_description text,
    is_applied boolean DEFAULT false,
    applied_at timestamp with time zone,
    applied_by uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid
);


ALTER TABLE public.schedule_change_log OWNER TO postgres;

--
-- Name: TABLE schedule_change_log; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.schedule_change_log IS 'Tracks all schedule changes from manual edits, queries, and audits with before/after task details';


--
-- Name: COLUMN schedule_change_log.task_details_before; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.schedule_change_log.task_details_before IS 'JSONB: Same structure as schedule_tasks.task_details. NULL for ADD operations';


--
-- Name: COLUMN schedule_change_log.task_details_after; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.schedule_change_log.task_details_after IS 'JSONB: Same structure as schedule_tasks.task_details. NULL for DELETE operations';


--
-- Name: schedule_tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedule_tasks (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    schedule_id uuid NOT NULL,
    task_id uuid NOT NULL,
    due_date date NOT NULL,
    status public.task_status DEFAULT 'NOT_STARTED'::public.task_status,
    completed_date date,
    task_details jsonb,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    task_name character varying(200)
);


ALTER TABLE public.schedule_tasks OWNER TO postgres;

--
-- Name: TABLE schedule_tasks; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.schedule_tasks IS 'Individual tasks within schedules with flexible JSONB task_details';


--
-- Name: COLUMN schedule_tasks.task_details; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.schedule_tasks.task_details IS 'JSONB structure: {"input_items": [{"input_item_id": "uuid", "quantity": 10.5, "quantity_unit_id": "uuid"}], "labor": {"estimated_hours": 8, "worker_count": 3}, "machinery": {"equipment_type": "text", "estimated_hours": 2}, "concentration": {"total_solution_volume": 80000, "total_solution_volume_unit_id": "uuid", "ingredients": [{"input_item_id": "uuid", "total_quantity": 240, "quantity_unit_id": "uuid", "concentration_per_liter": 3}]}}';


--
-- Name: schedule_template_tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedule_template_tasks (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    schedule_template_id uuid NOT NULL,
    task_id uuid NOT NULL,
    day_offset integer NOT NULL,
    task_details_template jsonb NOT NULL,
    sort_order integer DEFAULT 0,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    task_name character varying(200)
);


ALTER TABLE public.schedule_template_tasks OWNER TO postgres;

--
-- Name: TABLE schedule_template_tasks; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.schedule_template_tasks IS 'Tasks within schedule templates with calculation metadata';


--
-- Name: COLUMN schedule_template_tasks.day_offset; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.schedule_template_tasks.day_offset IS 'Days offset from schedule start date (0 = start date)';


--
-- Name: COLUMN schedule_template_tasks.task_details_template; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.schedule_template_tasks.task_details_template IS 'JSONB with quantities and calculation_basis (per_acre, per_plant, fixed). Structure: {"input_items": [{"input_item_id": "uuid", "quantity": 100, "quantity_unit_id": "uuid", "calculation_basis": "per_acre"}], "labor": {"estimated_hours": 8, "calculation_basis": "per_acre"}, "machinery": {"equipment_type": "tractor", "estimated_hours": 3.5, "calculation_basis": "per_acre"}, "concentration": {"solution_volume": 80, "solution_volume_unit_id": "uuid", "calculation_basis": "per_plant", "ingredients": [{"input_item_id": "uuid", "concentration_per_liter": 3, "concentration_unit_id": "uuid"}]}}';


--
-- Name: schedule_template_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedule_template_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    schedule_template_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.schedule_template_translations OWNER TO postgres;

--
-- Name: TABLE schedule_template_translations; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.schedule_template_translations IS 'Multilingual translations for schedule templates';


--
-- Name: COLUMN schedule_template_translations.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.schedule_template_translations.description IS 'User-facing description (translated)';


--
-- Name: schedule_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedule_templates (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    crop_type_id uuid,
    crop_variety_id uuid,
    is_system_defined boolean DEFAULT true,
    owner_org_id uuid,
    version integer DEFAULT 1,
    is_active boolean DEFAULT true,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    CONSTRAINT chk_schedule_template_ownership CHECK ((((is_system_defined = true) AND (owner_org_id IS NULL)) OR ((is_system_defined = false) AND (owner_org_id IS NOT NULL))))
);


ALTER TABLE public.schedule_templates OWNER TO postgres;

--
-- Name: TABLE schedule_templates; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.schedule_templates IS 'Reusable schedule templates for crops (system-defined and organization-specific)';


--
-- Name: COLUMN schedule_templates.notes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.schedule_templates.notes IS 'Internal notes for administrators (not translated)';


--
-- Name: schedules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedules (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    crop_id uuid NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    template_id uuid,
    template_parameters jsonb,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid
);


ALTER TABLE public.schedules OWNER TO postgres;

--
-- Name: TABLE schedules; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.schedules IS 'Operation schedules for crops (can be created from templates)';


--
-- Name: COLUMN schedules.template_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.schedules.template_id IS 'Reference to template if schedule was created from template';


--
-- Name: COLUMN schedules.template_parameters; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.schedules.template_parameters IS 'JSONB: {"area": 2.5, "area_unit_id": "uuid", "plant_count": 800, "start_date": "2024-09-25", "created_from_template_version": 1}';


--
-- Name: section_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.section_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    section_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.section_translations OWNER TO postgres;

--
-- Name: sections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sections (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    is_system_defined boolean DEFAULT true,
    owner_org_id uuid,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid
);


ALTER TABLE public.sections OWNER TO postgres;

--
-- Name: TABLE sections; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sections IS 'Section library for organizing audit parameters (system or organization-specific)';


--
-- Name: subscription_plan_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscription_plan_history (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    plan_id uuid NOT NULL,
    version integer NOT NULL,
    display_name character varying(100) NOT NULL,
    description text,
    category public.organization_type,
    resource_limits jsonb,
    features jsonb,
    pricing_details jsonb,
    effective_from timestamp with time zone NOT NULL,
    effective_to timestamp with time zone,
    changed_by uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.subscription_plan_history OWNER TO postgres;

--
-- Name: subscription_plans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscription_plans (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name public.subscription_plan NOT NULL,
    display_name character varying(100) NOT NULL,
    description text,
    category public.organization_type,
    resource_limits jsonb,
    features jsonb,
    pricing_details jsonb,
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.subscription_plans OWNER TO postgres;

--
-- Name: COLUMN subscription_plans.category; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.subscription_plans.category IS 'Plan category: FARMING, FSP, or NULL for universal plans';


--
-- Name: COLUMN subscription_plans.resource_limits; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.subscription_plans.resource_limits IS 'JSONB: {"crops": 50, "users": 10, "queries": 100, "audits": 20, "storage_gb": 5}';


--
-- Name: COLUMN subscription_plans.pricing_details; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.subscription_plans.pricing_details IS 'JSONB: {"currency": "INR", "billing_cycles": {"monthly": 1000, "quarterly": 2700, "yearly": 10000}}';


--
-- Name: task_actuals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_actuals (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    schedule_id uuid,
    schedule_task_id uuid,
    task_id uuid NOT NULL,
    is_planned boolean NOT NULL,
    crop_id uuid,
    plot_id uuid,
    actual_date date NOT NULL,
    task_details jsonb,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    CONSTRAINT chk_task_actuals_planned CHECK ((((is_planned = true) AND (schedule_task_id IS NOT NULL)) OR ((is_planned = false) AND (schedule_task_id IS NULL))))
);


ALTER TABLE public.task_actuals OWNER TO postgres;

--
-- Name: TABLE task_actuals; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.task_actuals IS 'Consolidated table for both planned and adhoc task actuals';


--
-- Name: COLUMN task_actuals.is_planned; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.task_actuals.is_planned IS 'true = planned task from schedule, false = adhoc unplanned task';


--
-- Name: COLUMN task_actuals.crop_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.task_actuals.crop_id IS 'Nullable to support plot-level tasks without specific crop';


--
-- Name: COLUMN task_actuals.task_details; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.task_actuals.task_details IS 'JSONB structure: Same as schedule_tasks.task_details - stores actual values for input items, labor, machinery, concentration used';


--
-- Name: task_photos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_photos (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    task_actual_id uuid NOT NULL,
    file_url character varying(500) NOT NULL,
    file_key character varying(500),
    caption text,
    uploaded_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    uploaded_by uuid
);


ALTER TABLE public.task_photos OWNER TO postgres;

--
-- Name: TABLE task_photos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.task_photos IS 'Photos for task actuals (both planned and adhoc)';


--
-- Name: task_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    task_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    name character varying(200) NOT NULL,
    description text
);


ALTER TABLE public.task_translations OWNER TO postgres;

--
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    category public.task_category NOT NULL,
    requires_input_items boolean DEFAULT false,
    requires_concentration boolean DEFAULT false,
    requires_machinery boolean DEFAULT false,
    requires_labor boolean DEFAULT false,
    sort_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- Name: template_parameters; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.template_parameters (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    template_section_id uuid NOT NULL,
    parameter_id uuid NOT NULL,
    is_required boolean DEFAULT false,
    sort_order integer DEFAULT 0,
    parameter_snapshot jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.template_parameters OWNER TO postgres;

--
-- Name: COLUMN template_parameters.parameter_snapshot; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.template_parameters.parameter_snapshot IS 'JSONB: {"parameter_id": "uuid", "code": "PLANT_HEIGHT", "parameter_type": "NUMERIC", "parameter_metadata": {"min_value": 0, "max_value": 500, "unit": "cm"}, "option_set_id": "uuid", "options": [{"option_id": "uuid", "code": "GREEN", "display_text": "Green"}], "translations": {"en": {"name": "Plant Height", "help_text": "Measure from soil"}}, "additional": {...}}';


--
-- Name: template_sections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.template_sections (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    template_id uuid NOT NULL,
    section_id uuid NOT NULL,
    sort_order integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.template_sections OWNER TO postgres;

--
-- Name: template_translations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.template_translations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    template_id uuid NOT NULL,
    language_code character varying(10) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.template_translations OWNER TO postgres;

--
-- Name: templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.templates (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(50) NOT NULL,
    is_system_defined boolean DEFAULT true,
    owner_org_id uuid,
    crop_type_id uuid,
    is_active boolean DEFAULT true,
    version integer DEFAULT 1,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid
);


ALTER TABLE public.templates OWNER TO postgres;

--
-- Name: TABLE templates; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.templates IS 'Template library for audit structures (system or organization-specific)';


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(20),
    password_hash character varying(255) NOT NULL,
    first_name character varying(100),
    last_name character varying(100),
    is_active boolean DEFAULT true,
    is_verified boolean DEFAULT false,
    last_login timestamp with time zone,
    preferred_language character varying(10) DEFAULT 'en'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    bio text,
    address text,
    profile_picture_url character varying(500),
    specialization character varying(200)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: TABLE users; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.users IS 'Application users with authentication details';


--
-- Name: COLUMN users.bio; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.bio IS 'User biography/description for member profile';


--
-- Name: COLUMN users.address; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.address IS 'User physical address';


--
-- Name: COLUMN users.profile_picture_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.profile_picture_url IS 'URL to user profile picture/avatar';


--
-- Name: work_order_scope; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.work_order_scope (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    work_order_id uuid NOT NULL,
    scope public.work_order_scope_type NOT NULL,
    scope_id uuid NOT NULL,
    access_permissions jsonb DEFAULT '{"read": true, "track": false, "write": false}'::jsonb,
    sort_order integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid
);


ALTER TABLE public.work_order_scope OWNER TO postgres;

--
-- Name: TABLE work_order_scope; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.work_order_scope IS 'Defines the scope of resources covered by a work order (can include multiple farms, plots, crops)';


--
-- Name: COLUMN work_order_scope.access_permissions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_order_scope.access_permissions IS 'JSONB permissions per scope item: {"read": true, "write": false, "track": false}. Default is read-only.';


--
-- Name: work_orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.work_orders (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    farming_organization_id uuid NOT NULL,
    fsp_organization_id uuid NOT NULL,
    service_listing_id uuid,
    work_order_number character varying(50),
    title character varying(200) NOT NULL,
    description text,
    status public.work_order_status DEFAULT 'PENDING'::public.work_order_status,
    terms_and_conditions text,
    scope_metadata jsonb,
    start_date date,
    end_date date,
    total_amount numeric(15,2),
    currency character varying(10) DEFAULT 'INR'::character varying,
    service_snapshot jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by uuid,
    updated_by uuid,
    accepted_at timestamp with time zone,
    accepted_by uuid,
    completed_at timestamp with time zone,
    cancelled_at timestamp with time zone,
    assigned_to_user_id uuid,
    access_granted boolean DEFAULT true,
    completion_notes text,
    completion_photo_url character varying(500),
    CONSTRAINT chk_work_order_scope_metadata CHECK (((scope_metadata IS NULL) OR ((jsonb_typeof(scope_metadata) = 'object'::text) AND ((scope_metadata ? 'total_items'::text) OR (scope_metadata ? 'farms'::text) OR (scope_metadata ? 'plots'::text) OR (scope_metadata ? 'crops'::text) OR (scope_metadata ? 'organizations'::text)))))
);


ALTER TABLE public.work_orders OWNER TO postgres;

--
-- Name: TABLE work_orders; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.work_orders IS 'Contracts between farming orgs and FSPs';


--
-- Name: COLUMN work_orders.scope_metadata; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_orders.scope_metadata IS 'JSONB summary of scope items: {"farms": 2, "plots": 3, "crops": 1, "total_items": 6}';


--
-- Name: COLUMN work_orders.service_snapshot; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_orders.service_snapshot IS 'JSONB snapshot of service details at the time of creation: {"name": "...", "description": "..."}';


--
-- Name: COLUMN work_orders.access_granted; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_orders.access_granted IS 'If true, FSP has read access to all resources in visibility/scope belonging to the farming org';


--
-- Name: COLUMN work_orders.completion_notes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_orders.completion_notes IS 'Notes added when work order is completed';


--
-- Name: COLUMN work_orders.completion_photo_url; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.work_orders.completion_photo_url IS 'URL to completion photo stored in S3';


--
-- Data for Name: audit_issues; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_issues (id, audit_id, title, description, severity, created_at, created_by, recommendation) FROM stdin;
f65d062b-57ce-4626-81fd-b08700bc0a5f	a4ba5400-35ae-4cc6-880b-9aac13cceddd	Soil Acidity	pH checking	MEDIUM	2026-02-01 10:34:22.239978+00	b46ab366-7dcb-4ee5-a558-dc328db04159	\N
73565b1c-8a7b-4318-824a-8b03c4d76b6a	a4723a72-f91c-4f12-a268-8809d0da3d7f	Soil Acidity	pH checking	MEDIUM	2026-02-01 10:34:42.8161+00	979cfcfd-a872-40df-8380-dbe81f29e7a5	\N
43e02a60-f96f-4563-ab3d-cf923d0dd831	20095d3d-e585-4320-b1f8-cfcc30752b5f	Soil Acidity	pH checking	MEDIUM	2026-02-01 10:35:08.153032+00	810cc398-af79-4d96-9eee-af0f1bbf8683	\N
b408c6a0-92d4-4ce9-aef4-ea80f0ff96d4	79739771-770e-44a9-ab0b-b347e6ebe770	Soil Acidity	pH checking	MEDIUM	2026-02-01 10:35:48.351914+00	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	\N
6056654d-331e-4abd-9bc1-e6d0a4c6d64b	d90be630-cd0b-401d-99f2-9ae0ba0066e7	Soil Acidity	pH checking	MEDIUM	2026-02-01 10:36:44.321695+00	ef5984b4-54b6-47cf-a9bb-ca02cadc0180	\N
b7e196be-76c3-4a60-996d-59fada66f5f9	0cfc963d-fe8b-4ca3-b720-49ab3696623a	Soil Acidity	pH checking	MEDIUM	2026-02-01 10:37:05.410354+00	70904796-fe39-4007-b892-a8aa3c8e0e8f	\N
1fb15d5c-b4c2-4ba9-bdf1-5874eec91bda	4bfdee24-2fd6-45c7-80fd-4a7513ca3037	Soil Acidity	pH checking	MEDIUM	2026-02-01 10:38:13.571718+00	1ce1ba48-b899-4217-8fd9-2124dd4765c6	\N
623b7f14-575f-4061-be0a-8eee473ec820	41acc9c4-1f08-40f1-90cf-e85c80e17de2	Soil Acidity	pH checking	MEDIUM	2026-02-01 10:38:59.475792+00	05e362b8-0b73-44ed-bded-ef4e0a40dd47	\N
ec4948a3-740e-44eb-9be7-f39998c739fe	34c22a9d-d7da-44d5-a18c-d9f706b11299	Soil Acidity	pH checking	MEDIUM	2026-02-01 11:01:39.887744+00	b9c25548-e5ba-4200-9dc9-1ba98f332540	\N
5a90b137-1b64-4309-8813-fba64380aa26	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	Soil Acidity	pH checking	MEDIUM	2026-02-01 11:06:39.640996+00	a30a9865-926a-4d26-af0d-42e44657b429	\N
b5b0793b-3f5b-4536-990d-81035007c600	55e89250-15fc-4f9b-be3b-01337d242b3e	sasdasd	asdasdasd	MEDIUM	2026-02-05 20:35:50.063372+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
f93dd44d-791b-4ff4-b1e0-ecc0a087d728	55e89250-15fc-4f9b-be3b-01337d242b3e	asdasd	asdasda	MEDIUM	2026-02-05 20:36:03.734105+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
8eb243b3-6792-4f88-933b-b594df5e72f4	55e89250-15fc-4f9b-be3b-01337d242b3e	sdfsdf	sdfsdf	MEDIUM	2026-02-05 20:39:04.161617+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
32bbd80f-3667-4727-b2a0-31dcef870433	55e89250-15fc-4f9b-be3b-01337d242b3e	dasdasdasd	asdas	MEDIUM	2026-02-05 20:43:23.24966+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
45000b9b-6721-422f-bce1-30d0c1b22da8	55e89250-15fc-4f9b-be3b-01337d242b3e	asdasd	asdas	MEDIUM	2026-02-05 20:46:10.588449+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
74acd1d8-4062-41db-aeee-25738663820a	55e89250-15fc-4f9b-be3b-01337d242b3e	asdasd	asdasd	MEDIUM	2026-02-05 20:56:20.084915+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
b2a9d0f0-1d45-4afd-b67b-a9a32acded7c	55e89250-15fc-4f9b-be3b-01337d242b3e	asdasdasd	asd	MEDIUM	2026-02-05 21:09:37.630916+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
aa45d12a-a353-44c6-a6b0-d4e9915c7939	55e89250-15fc-4f9b-be3b-01337d242b3e	asdas	dasdasd	MEDIUM	2026-02-05 22:44:27.508654+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
f134d023-1a90-41bf-b75a-7bf28ae23121	55e89250-15fc-4f9b-be3b-01337d242b3e	asd	asdasd	MEDIUM	2026-02-05 22:57:25.059097+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
4fa509fe-cb04-4431-b8e1-fb2d4b4a240c	99678697-d020-427b-9fab-b06977c030ad	asdasdasdasdasdasdasd	asdasd	MEDIUM	2026-02-05 23:09:02.525918+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
edb65645-b950-4bc6-9a35-ab41289eb10a	6afc1849-9bba-466f-bf59-5b6f2bc5f145	asdasd	asdasd	MEDIUM	2026-02-06 11:29:27.211373+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
659cd78f-c502-4f88-95c5-89f274fac226	f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4	rg	dfghsdg	MEDIUM	2026-02-09 18:55:37.66888+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
41e285fa-a7e8-4e41-b008-e9eaa75213dc	a316e7a5-0bca-4a61-a7a7-11f3fbde3258	Soil is no more fertilized	Use organic fertilizer instead of this chemical one	MEDIUM	2026-02-09 19:20:29.777226+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
f55fac83-83c6-4de1-bc16-38526a1b9b21	14d407bc-29ca-4a37-a5fd-85911e2eed9e	dfg	dfgdfg	MEDIUM	2026-02-11 09:15:07.418979+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
e6f6571c-78d9-4279-8826-2ea5fb1ac172	14d407bc-29ca-4a37-a5fd-85911e2eed9e	asdasda	qeasad	MEDIUM	2026-02-11 09:17:16.941825+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
\.


--
-- Data for Name: audit_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_log (id, table_name, record_id, action, old_values, new_values, changed_by, changed_at, ip_address, user_agent) FROM stdin;
\.


--
-- Data for Name: audit_parameter_instances; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_parameter_instances (id, audit_id, template_section_id, parameter_id, sort_order, is_required, parameter_snapshot, created_at, created_by, updated_at) FROM stdin;
f5819c8a-65da-495a-ac3c-acde697ab0e5	71ea2a9e-9f30-42de-95ce-23492dde9081	565a134b-03c7-4740-a8e4-071bac67ed50	e89b6487-1da6-4f25-801c-a3e340814738	0	t	{"code": "SOIL_MOISTURE", "parameter_id": "e89b6487-1da6-4f25-801c-a3e340814738", "parameter_type": "SINGLE_SELECT", "parameter_metadata": null}	2026-01-30 00:10:57.715119+00	\N	2026-01-30 00:10:57.715119+00
3c4f2f1f-0fd4-49fa-bd86-8dc9d4bf820a	55e89250-15fc-4f9b-be3b-01337d242b3e	0404e697-424a-401f-a41d-91c913239acc	e5db1148-7a6f-4fae-80f5-e602f35e5cbd	4	f	{"code": "PRM_fa6d_4_1510", "options": [], "parameter_id": "e5db1148-7a6f-4fae-80f5-e602f35e5cbd", "translations": {"en": {"name": "Plant Height (cm)", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-01-30T20:36:36.999985", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-01-30 20:36:36.949929+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 20:36:36.949929+00
063af9a8-6c91-4489-b2a9-59d13613d47e	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	eefe2319-3eb6-43bb-9d78-7c734561b947	1	t	{"code": "P1_1769943998", "options": [], "parameter_id": "eefe2319-3eb6-43bb-9d78-7c734561b947", "translations": {"en": {"name": "Param 1", "help_text": null, "description": "Measure 1"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.253834", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.239746+00	a30a9865-926a-4d26-af0d-42e44657b429	2026-02-01 11:06:39.239746+00
4c0a07e1-5bd3-4b3c-8e4b-92b557c6bb43	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	5684267d-6f41-454e-8429-2f094efe38b9	2	t	{"code": "P2_1769943998", "options": [], "parameter_id": "5684267d-6f41-454e-8429-2f094efe38b9", "translations": {"en": {"name": "Param 2", "help_text": null, "description": "Measure 2"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.255227", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.239746+00	a30a9865-926a-4d26-af0d-42e44657b429	2026-02-01 11:06:39.239746+00
e4103236-56c4-48e1-8ef7-a1b2216acb9e	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	b2d71394-a99d-4ff6-a333-4d8ebf1c1ec4	3	t	{"code": "P3_1769943998", "options": [], "parameter_id": "b2d71394-a99d-4ff6-a333-4d8ebf1c1ec4", "translations": {"en": {"name": "Param 3", "help_text": null, "description": "Measure 3"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.256535", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.239746+00	a30a9865-926a-4d26-af0d-42e44657b429	2026-02-01 11:06:39.239746+00
8a8ba3c8-0a3d-4d9f-ad24-d5113a85dfcc	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	7e469f84-0b9d-4f70-b737-ce0444148245	4	t	{"code": "P4_1769943998", "options": [], "parameter_id": "7e469f84-0b9d-4f70-b737-ce0444148245", "translations": {"en": {"name": "Param 4", "help_text": null, "description": "Measure 4"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.257800", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.239746+00	a30a9865-926a-4d26-af0d-42e44657b429	2026-02-01 11:06:39.239746+00
830c1db9-f276-4431-89a7-ac90ead62205	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	46640045-7bdf-48eb-af82-61a3fc7c2d4a	5	t	{"code": "P5_1769943999", "options": [], "parameter_id": "46640045-7bdf-48eb-af82-61a3fc7c2d4a", "translations": {"en": {"name": "Param 5", "help_text": null, "description": "Measure 5"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.259172", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.239746+00	a30a9865-926a-4d26-af0d-42e44657b429	2026-02-01 11:06:39.239746+00
b4a661a0-3491-4ea7-8ea4-6d78665ce56e	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	f517e506-6c88-4cfb-8426-ae5f1d516154	6	t	{"code": "P6_1769943999", "options": [], "parameter_id": "f517e506-6c88-4cfb-8426-ae5f1d516154", "translations": {"en": {"name": "Param 6", "help_text": null, "description": "Measure 6"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.260450", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.239746+00	a30a9865-926a-4d26-af0d-42e44657b429	2026-02-01 11:06:39.239746+00
219d6b6b-19db-45b3-91e3-ade7ea886074	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	89151732-fc61-4617-a477-17685bbee9da	7	t	{"code": "P7_1769943999", "options": [], "parameter_id": "89151732-fc61-4617-a477-17685bbee9da", "translations": {"en": {"name": "Param 7", "help_text": null, "description": "Measure 7"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.262134", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.239746+00	a30a9865-926a-4d26-af0d-42e44657b429	2026-02-01 11:06:39.239746+00
2c2317ee-d526-4265-a83c-f3f8ec89f77b	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	8bea7626-d387-455c-aa0b-2436f2824e78	8	t	{"code": "P8_1769943999", "options": [], "parameter_id": "8bea7626-d387-455c-aa0b-2436f2824e78", "translations": {"en": {"name": "Param 8", "help_text": null, "description": "Measure 8"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.263447", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.239746+00	a30a9865-926a-4d26-af0d-42e44657b429	2026-02-01 11:06:39.239746+00
06a8b4e1-0df9-4cae-9ecc-5f4771cd2f7d	b20782d9-2f2c-4504-bc61-f9ae81b84037	3653a901-5e50-49a1-8d6f-eaf6c30d3104	90ac4202-513e-4e0e-9de6-a32262857ed3	1	t	{"code": "P1_1770327572", "options": [], "parameter_id": "90ac4202-513e-4e0e-9de6-a32262857ed3", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:39:33.841104", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:39:33.826868+00	fc5165e6-6519-496f-a3dd-1435bc308b5f	2026-02-05 21:39:33.826868+00
f703dd94-2057-4c38-9e5c-f06805a897de	b20782d9-2f2c-4504-bc61-f9ae81b84037	3653a901-5e50-49a1-8d6f-eaf6c30d3104	4a1add6d-2be5-4eb4-93d2-51ebbf5e1672	2	t	{"code": "P2_1770327572", "options": [], "parameter_id": "4a1add6d-2be5-4eb4-93d2-51ebbf5e1672", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:39:33.842554", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:39:33.826868+00	fc5165e6-6519-496f-a3dd-1435bc308b5f	2026-02-05 21:39:33.826868+00
1bc7bc86-89dd-45f5-9f83-881f65df2578	b20782d9-2f2c-4504-bc61-f9ae81b84037	3653a901-5e50-49a1-8d6f-eaf6c30d3104	689e5a3e-cc7a-4148-b408-f92ec941b37e	3	t	{"code": "P3_1770327572", "options": [{"code": "opt1", "option_id": "6baefc9c-88e8-4aa1-a021-8cae81a905ed", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "44c9d328-fc27-4a2c-9a01-9167b8f9c84f", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "689e5a3e-cc7a-4148-b408-f92ec941b37e", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "b0fe6edb-193c-4e20-a6f4-5cbaaf817536", "snapshot_date": "2026-02-05T21:39:33.843942", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:39:33.826868+00	fc5165e6-6519-496f-a3dd-1435bc308b5f	2026-02-05 21:39:33.826868+00
8fb82770-4575-49cb-ae8b-f0d63f717cab	c2366bab-e199-490f-aab5-d78f72bd6150	ab035ef9-1fb5-4594-946e-5b06c036494a	c863d9ae-337e-4ea5-a846-3b9a8bd04020	1	t	{"code": "P1_1770327636", "options": [], "parameter_id": "c863d9ae-337e-4ea5-a846-3b9a8bd04020", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:40:37.730220", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:40:37.714777+00	d655e067-4edd-4516-b1b6-821c3c33cfc5	2026-02-05 21:40:37.714777+00
7694c5aa-f77f-408f-8657-7f3f5d0cdaa3	c2366bab-e199-490f-aab5-d78f72bd6150	ab035ef9-1fb5-4594-946e-5b06c036494a	a74d7503-f495-4a7b-942d-2e6d64aab25f	2	t	{"code": "P2_1770327636", "options": [], "parameter_id": "a74d7503-f495-4a7b-942d-2e6d64aab25f", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:40:37.731776", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:40:37.714777+00	d655e067-4edd-4516-b1b6-821c3c33cfc5	2026-02-05 21:40:37.714777+00
b53c25f3-3b7a-459e-adaa-279928009959	c2366bab-e199-490f-aab5-d78f72bd6150	ab035ef9-1fb5-4594-946e-5b06c036494a	7acb91dd-9a2b-482c-9fc6-2eefb815aeb3	3	t	{"code": "P3_1770327636", "options": [{"code": "opt1", "option_id": "cc1a045b-0ce5-4c07-afed-eca7a4d7896f", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "6f01b763-30d8-414c-9af9-bf605ac00ae7", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "7acb91dd-9a2b-482c-9fc6-2eefb815aeb3", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "ba3f1425-1907-48fc-a9f4-7ee1a85c0b90", "snapshot_date": "2026-02-05T21:40:37.733396", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:40:37.714777+00	d655e067-4edd-4516-b1b6-821c3c33cfc5	2026-02-05 21:40:37.714777+00
51bacee2-7f70-4b7c-90b2-0e0d33c69d15	55e89250-15fc-4f9b-be3b-01337d242b3e	0404e697-424a-401f-a41d-91c913239acc	f32bc43e-7842-4aff-97d0-c999804e2f44	0	f	{"code": "PRM_fa6d_0_1143", "options": [], "parameter_id": "f32bc43e-7842-4aff-97d0-c999804e2f44", "translations": {"en": {"name": "sadfsdfsdf", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-01-30T20:36:36.985704", "parameter_type": "DATE", "parameter_metadata": {}}	2026-01-30 20:36:36.949929+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 20:36:36.949929+00
74a4b0e3-00b8-4ccb-9d3b-df9f479e79e5	55e89250-15fc-4f9b-be3b-01337d242b3e	0404e697-424a-401f-a41d-91c913239acc	7ada24d6-b7ad-413d-893d-25e1271d9841	1	f	{"code": "PRM_fa6d_1_1243", "options": [], "parameter_id": "7ada24d6-b7ad-413d-893d-25e1271d9841", "translations": {"en": {"name": "Plant Height (cm)", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-01-30T20:36:36.987634", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-01-30 20:36:36.949929+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 20:36:36.949929+00
1b022ef2-7906-4a69-9825-25ddcb4dda82	55e89250-15fc-4f9b-be3b-01337d242b3e	0404e697-424a-401f-a41d-91c913239acc	1d0cbbc3-1354-49d6-a16a-5ba0d6fd2f04	2	f	{"code": "PRM_fa6d_2_1310", "options": [{"code": "GREEN", "option_id": "059974e2-a761-487f-9e52-2629100b504a", "sort_order": 0, "translations": {"en": "Green"}}, {"code": "YELLOW", "option_id": "6d7cbc48-8d1a-4ba5-bf1d-fd8b794a404b", "sort_order": 1, "translations": {"en": "Yellow"}}, {"code": "BROWN", "option_id": "c643a809-e612-4807-9a90-0b29f0f9508c", "sort_order": 2, "translations": {"en": "Brown"}}], "parameter_id": "1d0cbbc3-1354-49d6-a16a-5ba0d6fd2f04", "translations": {"en": {"name": "Leaf Color", "help_text": null, "description": null}}, "option_set_id": "0345db82-bf99-4f32-b222-6ae0a7c07c00", "snapshot_date": "2026-01-30T20:36:36.989467", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-01-30 20:36:36.949929+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 20:36:36.949929+00
ec608ef9-15d0-4efc-958e-29c5181fa8a3	55e89250-15fc-4f9b-be3b-01337d242b3e	0404e697-424a-401f-a41d-91c913239acc	1b4c0c1b-7516-439a-af12-4e9735291848	3	f	{"code": "PRM_fa6d_3_1410", "options": [{"code": "YES", "option_id": "0c80853b-5a5b-4b87-8ba9-943fcf02bb3b", "sort_order": 0, "translations": {"en": "Yes"}}, {"code": "NO", "option_id": "af79f344-cacf-4679-9426-ff4f2507deb0", "sort_order": 1, "translations": {"en": "No"}}], "parameter_id": "1b4c0c1b-7516-439a-af12-4e9735291848", "translations": {"en": {"name": "Pest Presence", "help_text": null, "description": null}}, "option_set_id": "dfdd3646-a211-4edf-9458-3fd5dfdb7a76", "snapshot_date": "2026-01-30T20:36:36.995465", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-01-30 20:36:36.949929+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 20:36:36.949929+00
e5ec51ce-2c4b-40af-8a9a-9d5c7ea87e14	55e89250-15fc-4f9b-be3b-01337d242b3e	0404e697-424a-401f-a41d-91c913239acc	69900480-cef3-4145-adc7-651cf4eb1c38	5	f	{"code": "PRM_fa6d_5_1576", "options": [{"code": "DRY", "option_id": "ceba3c16-431a-4ddd-b565-51a899129e34", "sort_order": 0, "translations": {"en": "Dry"}}, {"code": "MOIST", "option_id": "72bd150c-a989-42a6-8a19-7c0c46e21195", "sort_order": 1, "translations": {"en": "Moist"}}, {"code": "WET", "option_id": "bce6372f-fb3a-492a-986d-9c2a151d765b", "sort_order": 2, "translations": {"en": "Wet"}}], "parameter_id": "69900480-cef3-4145-adc7-651cf4eb1c38", "translations": {"en": {"name": "Soil Moisture Level", "help_text": null, "description": null}}, "option_set_id": "9a006dfc-05c1-48d7-a1d9-d0a6f6e2ccba", "snapshot_date": "2026-01-30T20:36:37.001888", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-01-30 20:36:36.949929+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 20:36:36.949929+00
a308b693-d7f0-4037-9f5a-3d36468ce737	78983c2b-01c0-4c2e-8b46-c3773b1a8b6e	bb7863b4-5ab9-42c2-a9dc-960ebb1a071c	71826bac-4f3a-4e8e-b7d7-dcfdb27c2f62	1	t	{"code": "PH_1769941969", "options": [], "parameter_id": "71826bac-4f3a-4e8e-b7d7-dcfdb27c2f62", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:32:49.464397", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:32:49.448247+00	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c	2026-02-01 10:32:49.448247+00
e5c9f421-f171-4d96-85bb-7faa56dde183	def41ef5-6c84-4840-b991-65f5ca1b95b7	ed7822b9-a67a-4c6d-836a-dfd4c510c892	7940e041-2bd8-4b4c-829b-5c080b601709	1	t	{"code": "PH_1769941990", "options": [], "parameter_id": "7940e041-2bd8-4b4c-829b-5c080b601709", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:33:10.190774", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:33:10.178091+00	bf660c8b-3818-4cf7-85f1-3071c0a7943c	2026-02-01 10:33:10.178091+00
c0849ffa-2b80-450d-bd1a-e2764499d5fd	4ce704ad-c335-4c99-bc24-1a8a66877c08	7e5e1be0-27ef-4a08-8368-3651f7c279b4	940dd88b-e133-440b-af51-95365af25909	1	t	{"code": "PH_1769942012", "options": [], "parameter_id": "940dd88b-e133-440b-af51-95365af25909", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:33:32.206653", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:33:32.196017+00	c7a092a7-d354-498d-b23a-d4802d99ccb4	2026-02-01 10:33:32.196017+00
ba122b1e-178e-4954-8e48-cdc057cf6505	71fb6a9e-6f74-48cd-af01-fe4fcd86975b	b9fb0eb6-5a90-47dd-8695-a24ffe3afc15	10f12a98-15d3-446f-90b0-5e5e353c3809	1	t	{"code": "PH_1769942044", "options": [], "parameter_id": "10f12a98-15d3-446f-90b0-5e5e353c3809", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:34:04.605436", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:34:04.593909+00	2199f334-fccd-46ff-b45c-2cd81aadeca2	2026-02-01 10:34:04.593909+00
720dbf19-4931-4ead-a894-f892ea5482e4	a4ba5400-35ae-4cc6-880b-9aac13cceddd	b53d7e01-c5db-4ab4-b985-ec803c3305af	1ad2e581-5dce-41ce-af2a-8e832ebbcc54	1	t	{"code": "PH_1769942062", "options": [], "parameter_id": "1ad2e581-5dce-41ce-af2a-8e832ebbcc54", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:34:22.154906", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:34:22.144221+00	b46ab366-7dcb-4ee5-a558-dc328db04159	2026-02-01 10:34:22.144221+00
50e7c163-b8df-4fe2-94fd-21da5e54bdbf	a4723a72-f91c-4f12-a268-8809d0da3d7f	aa0c9387-e1ea-43af-8bdf-70de57e12da9	4ec21239-4ac2-46b7-bd9b-d1c065591f62	1	t	{"code": "PH_1769942082", "options": [], "parameter_id": "4ec21239-4ac2-46b7-bd9b-d1c065591f62", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:34:42.738227", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:34:42.72706+00	979cfcfd-a872-40df-8380-dbe81f29e7a5	2026-02-01 10:34:42.72706+00
959621f3-ac7f-443b-9d94-3501d65cdbd1	20095d3d-e585-4320-b1f8-cfcc30752b5f	5228ba9f-7d49-4466-927b-84eb6492afba	ebfb0b55-7017-496c-9e98-d0d55159a831	1	t	{"code": "PH_1769942107", "options": [], "parameter_id": "ebfb0b55-7017-496c-9e98-d0d55159a831", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:35:08.076989", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:35:08.065114+00	810cc398-af79-4d96-9eee-af0f1bbf8683	2026-02-01 10:35:08.065114+00
216d7cf9-c477-4cc3-9234-f37bdd99be61	79739771-770e-44a9-ab0b-b347e6ebe770	8f9bffa5-2817-4251-93a8-a07baa03cf6d	7325f2cc-97ed-4dcc-a191-1ea0c56e04bd	1	t	{"code": "PH_1769942148", "options": [], "parameter_id": "7325f2cc-97ed-4dcc-a191-1ea0c56e04bd", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:35:48.278003", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:35:48.266528+00	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	2026-02-01 10:35:48.266528+00
9fedc85b-3fd4-4a2d-aaee-28c47adfab51	d90be630-cd0b-401d-99f2-9ae0ba0066e7	f2f6975e-267f-4d99-a126-9ed1d82cb15e	e68e3073-4957-4a89-80e3-f27e8136bf3b	1	t	{"code": "PH_1769942204", "options": [], "parameter_id": "e68e3073-4957-4a89-80e3-f27e8136bf3b", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:36:44.211561", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:36:44.191133+00	ef5984b4-54b6-47cf-a9bb-ca02cadc0180	2026-02-01 10:36:44.191133+00
b1b33dc8-b68a-4f11-a3da-e60d9279c7a9	0cfc963d-fe8b-4ca3-b720-49ab3696623a	ad013930-0d06-46cc-aee9-a65be6cc324f	314226b3-58f0-40c3-8a79-a040f41f3867	1	t	{"code": "PH_1769942225", "options": [], "parameter_id": "314226b3-58f0-40c3-8a79-a040f41f3867", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:37:05.333402", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:37:05.32135+00	70904796-fe39-4007-b892-a8aa3c8e0e8f	2026-02-01 10:37:05.32135+00
9a410db0-f030-428c-a457-aaea3143ab30	4bfdee24-2fd6-45c7-80fd-4a7513ca3037	071025c2-1738-4e4d-b0b8-cced4f66094f	fca6b05f-39da-4323-a92d-d2fc7eceabff	1	t	{"code": "PH_1769942293", "options": [], "parameter_id": "fca6b05f-39da-4323-a92d-d2fc7eceabff", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:38:13.507489", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:38:13.497221+00	1ce1ba48-b899-4217-8fd9-2124dd4765c6	2026-02-01 10:38:13.497221+00
ca426fc5-3e31-4110-b467-fdab4b78f694	41acc9c4-1f08-40f1-90cf-e85c80e17de2	a6554583-4fc4-434f-a837-74fe2848fa21	710a7d66-5394-4c0a-af26-5dc0512fae77	1	t	{"code": "PH_1769942339", "options": [], "parameter_id": "710a7d66-5394-4c0a-af26-5dc0512fae77", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:38:59.369720", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:38:59.350506+00	05e362b8-0b73-44ed-bded-ef4e0a40dd47	2026-02-01 10:38:59.350506+00
99aaf6d4-9ed0-4319-b66d-b7bbfc5db7a1	34c22a9d-d7da-44d5-a18c-d9f706b11299	56d9fb7a-e631-4882-9a7e-cb169b0b0f54	e9799730-1c13-4c5f-b9ed-2a7fd9c1538e	1	t	{"code": "PH_1769943699", "options": [], "parameter_id": "e9799730-1c13-4c5f-b9ed-2a7fd9c1538e", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:01:39.812601", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 11:01:39.802424+00	b9c25548-e5ba-4200-9dc9-1ba98f332540	2026-02-01 11:01:39.802424+00
219931e8-f3d3-44ff-971d-7ee598bde9fd	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	d7147d11-034b-4c26-8c23-6921d316d28a	9	t	{"code": "P9_1769943999", "options": [], "parameter_id": "d7147d11-034b-4c26-8c23-6921d316d28a", "translations": {"en": {"name": "Param 9", "help_text": null, "description": "Measure 9"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.264831", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.239746+00	a30a9865-926a-4d26-af0d-42e44657b429	2026-02-01 11:06:39.239746+00
367c700b-40d6-4c26-b0de-753d98d8245a	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	9f963e85-c94c-4dec-b2aa-b0e745431c39	10	t	{"code": "P10_1769943999", "options": [], "parameter_id": "9f963e85-c94c-4dec-b2aa-b0e745431c39", "translations": {"en": {"name": "Param 10", "help_text": null, "description": "Measure 10"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.266145", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.239746+00	a30a9865-926a-4d26-af0d-42e44657b429	2026-02-01 11:06:39.239746+00
f2fa2bc2-0235-4c54-a9da-7a624793a3b3	8864a618-4dcc-47b9-901f-9859b539c579	834d23a5-e7ec-4d4e-8a69-f35ecdd38d23	78a8d90e-d189-4e0c-9815-618f465f4195	1	t	{"code": "P1_1770327102", "options": [], "parameter_id": "78a8d90e-d189-4e0c-9815-618f465f4195", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:31:42.854016", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:31:42.814584+00	53126f3a-94da-4363-b20d-61a85c99574a	2026-02-05 21:31:42.814584+00
19cee73e-6e9e-4a49-b6aa-7c4b400ccd8e	8864a618-4dcc-47b9-901f-9859b539c579	834d23a5-e7ec-4d4e-8a69-f35ecdd38d23	f01ac19f-b2ff-4bc9-b16a-5edb10315b41	2	t	{"code": "P2_1770327102", "options": [], "parameter_id": "f01ac19f-b2ff-4bc9-b16a-5edb10315b41", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:31:42.854863", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:31:42.814584+00	53126f3a-94da-4363-b20d-61a85c99574a	2026-02-05 21:31:42.814584+00
1862cf2b-c0eb-4df7-b6cd-9ca94015970e	8864a618-4dcc-47b9-901f-9859b539c579	834d23a5-e7ec-4d4e-8a69-f35ecdd38d23	5e0e278c-ed24-4ae6-b259-8a430b6ff804	3	t	{"code": "P3_1770327102", "options": [{"code": "opt1", "option_id": "b7c70d96-0f02-48ae-972d-b003cbfc3b89", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "4126b50a-880e-44a6-b28a-985081f32d4c", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "5e0e278c-ed24-4ae6-b259-8a430b6ff804", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "7d1bfc37-3b1b-4421-a3f9-104690c6e487", "snapshot_date": "2026-02-05T21:31:42.855595", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:31:42.814584+00	53126f3a-94da-4363-b20d-61a85c99574a	2026-02-05 21:31:42.814584+00
67447ad3-6ef9-4b36-afeb-eb2e68b4df78	9b38d720-a2fa-4be2-a767-c01a2deb5386	a44f7299-8392-4c30-8f9e-3bef71205bae	467998d6-634b-40aa-8eb8-728fab704ba7	1	t	{"code": "P1_1770327224", "options": [], "parameter_id": "467998d6-634b-40aa-8eb8-728fab704ba7", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:33:45.334500", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:33:45.323923+00	1214c599-c7c2-490b-a895-e45b985b027b	2026-02-05 21:33:45.323923+00
f835ae13-e0df-4137-95dd-8367e61bd3d2	9b38d720-a2fa-4be2-a767-c01a2deb5386	a44f7299-8392-4c30-8f9e-3bef71205bae	82c060ef-fec1-4d82-9e63-44b301715425	2	t	{"code": "P2_1770327224", "options": [], "parameter_id": "82c060ef-fec1-4d82-9e63-44b301715425", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:33:45.335565", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:33:45.323923+00	1214c599-c7c2-490b-a895-e45b985b027b	2026-02-05 21:33:45.323923+00
f0427230-81bf-4314-a2f3-0d61341975b1	9b38d720-a2fa-4be2-a767-c01a2deb5386	a44f7299-8392-4c30-8f9e-3bef71205bae	28230270-0fcf-4662-8c5b-8bb0ad5c57b3	3	t	{"code": "P3_1770327224", "options": [{"code": "opt1", "option_id": "68b94446-68e1-4ec5-8b41-cc9842033394", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "1c17baf7-b36c-464e-9a73-3e829cc103db", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "28230270-0fcf-4662-8c5b-8bb0ad5c57b3", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "b409cb79-5f90-4322-b935-5c13fe396f9c", "snapshot_date": "2026-02-05T21:33:45.336539", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:33:45.323923+00	1214c599-c7c2-490b-a895-e45b985b027b	2026-02-05 21:33:45.323923+00
4a1b45ae-44d3-41a1-99ee-b2158d35bd97	873f22dc-071a-4f69-8a95-5a98759a6741	7a2df06a-eeac-4f95-8f3a-6af6463183b3	e016e813-99bf-46ae-93e0-43fcc999ecff	1	t	{"code": "P1_1770327280", "options": [], "parameter_id": "e016e813-99bf-46ae-93e0-43fcc999ecff", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:34:41.335110", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:34:41.3216+00	d9cd5b64-e423-4710-bcfe-73606bcca78c	2026-02-05 21:34:41.3216+00
a8f243f7-8386-4f91-aa85-3929d15fbaa2	873f22dc-071a-4f69-8a95-5a98759a6741	7a2df06a-eeac-4f95-8f3a-6af6463183b3	0124f9d8-df14-40e1-a628-2fb28cfcd89b	2	t	{"code": "P2_1770327280", "options": [], "parameter_id": "0124f9d8-df14-40e1-a628-2fb28cfcd89b", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:34:41.336502", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:34:41.3216+00	d9cd5b64-e423-4710-bcfe-73606bcca78c	2026-02-05 21:34:41.3216+00
8ff19dcd-835f-42f0-993b-c3abd9421008	873f22dc-071a-4f69-8a95-5a98759a6741	7a2df06a-eeac-4f95-8f3a-6af6463183b3	5b9d413c-0d24-4b1c-bee8-2a800c357b62	3	t	{"code": "P3_1770327280", "options": [{"code": "opt1", "option_id": "ee25c5c6-aadd-4c6a-ab13-3070b40ddf05", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "ab2b8972-8292-4e21-a8f6-66d8bf133921", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "5b9d413c-0d24-4b1c-bee8-2a800c357b62", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "a9bf577e-4d74-495e-b9d9-c1677621be45", "snapshot_date": "2026-02-05T21:34:41.337907", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:34:41.3216+00	d9cd5b64-e423-4710-bcfe-73606bcca78c	2026-02-05 21:34:41.3216+00
43ebd3cb-9790-4493-b86e-03a5b27047b5	ce3ea838-c6df-42ce-a9bf-06856078f13b	98fc0861-9afb-41f1-b1e9-da223f7e1acf	baa7fe1d-099f-49de-9531-dcad3694b914	1	t	{"code": "P1_1770327392", "options": [], "parameter_id": "baa7fe1d-099f-49de-9531-dcad3694b914", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:36:32.777288", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:36:32.767626+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	2026-02-05 21:36:32.767626+00
74d32f8f-2605-43a1-b77f-dd957678295d	ce3ea838-c6df-42ce-a9bf-06856078f13b	98fc0861-9afb-41f1-b1e9-da223f7e1acf	56a72950-a19d-481b-a0db-3aa0940d1b7a	2	t	{"code": "P2_1770327392", "options": [], "parameter_id": "56a72950-a19d-481b-a0db-3aa0940d1b7a", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:36:32.778245", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:36:32.767626+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	2026-02-05 21:36:32.767626+00
7576e4fd-603a-40be-99b5-12cb7b682f7f	ce3ea838-c6df-42ce-a9bf-06856078f13b	98fc0861-9afb-41f1-b1e9-da223f7e1acf	6699f225-e68a-4e39-a43f-a6202cda40d5	3	t	{"code": "P3_1770327392", "options": [{"code": "opt1", "option_id": "c2b584fc-e308-4562-ba68-3bdc7c1f8ecc", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "afb0f1b3-8447-4a23-a961-cf6affd8bfa0", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "6699f225-e68a-4e39-a43f-a6202cda40d5", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "cdc29b9f-35fb-4abb-a9a6-21272b56173a", "snapshot_date": "2026-02-05T21:36:32.779053", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:36:32.767626+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	2026-02-05 21:36:32.767626+00
c042d163-ee00-4ab5-b557-366a7946877c	114aecdb-ebf1-4077-94ab-ff9e56ec3791	35efd64c-30d9-4c9a-a581-8ea712a613c2	76452429-682f-4ba0-917e-bb4b9ffd349f	1	t	{"code": "P1_1770327706", "options": [], "parameter_id": "76452429-682f-4ba0-917e-bb4b9ffd349f", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:41:47.455525", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:41:47.441165+00	13ac055f-b943-4f6d-8182-babe636544df	2026-02-05 21:41:47.441165+00
2bad393e-5c28-4fdc-b875-47ad3fdc541e	114aecdb-ebf1-4077-94ab-ff9e56ec3791	35efd64c-30d9-4c9a-a581-8ea712a613c2	e46db86a-72f6-4606-8eb2-560b6b3ec315	2	t	{"code": "P2_1770327706", "options": [], "parameter_id": "e46db86a-72f6-4606-8eb2-560b6b3ec315", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:41:47.457296", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:41:47.441165+00	13ac055f-b943-4f6d-8182-babe636544df	2026-02-05 21:41:47.441165+00
0790ce02-cebe-4875-ba68-eebf6740c31f	114aecdb-ebf1-4077-94ab-ff9e56ec3791	35efd64c-30d9-4c9a-a581-8ea712a613c2	222948be-c818-4310-bf8d-fef35d5d979c	3	t	{"code": "P3_1770327706", "options": [{"code": "opt1", "option_id": "8337ba01-c7bc-4553-86d0-672c65399b38", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "5811ced6-2e79-4c9e-b7a1-f48134203521", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "222948be-c818-4310-bf8d-fef35d5d979c", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "e67b95a8-8819-4939-9557-bd2d5379e96c", "snapshot_date": "2026-02-05T21:41:47.458759", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:41:47.441165+00	13ac055f-b943-4f6d-8182-babe636544df	2026-02-05 21:41:47.441165+00
74b02351-8066-4945-b6ee-1a2f7d9bd16c	4617c18f-c346-432a-bd36-25804c526fd1	da3ff4de-da78-4c58-9ac5-1e7eb467e664	b664898c-45cf-4723-8fff-b74c1232898f	1	t	{"code": "P1_1770327821", "options": [], "parameter_id": "b664898c-45cf-4723-8fff-b74c1232898f", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:43:42.874006", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:43:42.856334+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	2026-02-05 21:43:42.856334+00
53225349-67b7-4cfa-8aff-5ed4c2bfc4a5	4617c18f-c346-432a-bd36-25804c526fd1	da3ff4de-da78-4c58-9ac5-1e7eb467e664	9700c6e5-2190-443e-83b2-5183b59625e2	2	t	{"code": "P2_1770327821", "options": [], "parameter_id": "9700c6e5-2190-443e-83b2-5183b59625e2", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:43:42.874882", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:43:42.856334+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	2026-02-05 21:43:42.856334+00
dc214121-294b-4750-a4f0-ddb7fe601419	4617c18f-c346-432a-bd36-25804c526fd1	da3ff4de-da78-4c58-9ac5-1e7eb467e664	78f901de-8e0c-42a6-ba39-94adadbe3193	3	t	{"code": "P3_1770327821", "options": [{"code": "opt1", "option_id": "3f3b03fa-ef0e-42fe-9546-c33af35d1681", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "a77d9560-5597-493c-a16d-99af12c82df6", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "78f901de-8e0c-42a6-ba39-94adadbe3193", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "53a4bc06-e667-4f37-b16e-9aa98563aa2f", "snapshot_date": "2026-02-05T21:43:42.876003", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:43:42.856334+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	2026-02-05 21:43:42.856334+00
14c86060-a606-421e-9388-334d38f0d70f	8c0183d7-2bbf-4354-a646-2e60339b3ff6	401c4821-37e9-4fe4-afbb-1e5a781f5a42	21f3a466-ed7c-4630-8715-9dbeca7fb00f	1	t	{"code": "P1_1770328194", "options": [], "parameter_id": "21f3a466-ed7c-4630-8715-9dbeca7fb00f", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:49:55.253368", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:49:55.233216+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	2026-02-05 21:49:55.233216+00
a462112e-b2d9-4c8c-acf5-a08159f6ed0e	8c0183d7-2bbf-4354-a646-2e60339b3ff6	401c4821-37e9-4fe4-afbb-1e5a781f5a42	2ad12225-e5db-458e-9a8a-7d3ff1051d4c	2	t	{"code": "P2_1770328194", "options": [], "parameter_id": "2ad12225-e5db-458e-9a8a-7d3ff1051d4c", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:49:55.254260", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:49:55.233216+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	2026-02-05 21:49:55.233216+00
745de89d-d546-4817-aad9-c14b12755667	8c0183d7-2bbf-4354-a646-2e60339b3ff6	401c4821-37e9-4fe4-afbb-1e5a781f5a42	fc1d516b-4410-42df-8d1a-2420b8d0927b	3	t	{"code": "P3_1770328194", "options": [{"code": "opt1", "option_id": "2c2e893a-cd32-4855-b766-681bb293adb7", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "3384b3d2-89b2-45f7-82a2-28e23fa1dc1f", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "fc1d516b-4410-42df-8d1a-2420b8d0927b", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "e86a83d1-b3e4-44cc-95ad-b63d2b7a931d", "snapshot_date": "2026-02-05T21:49:55.255034", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:49:55.233216+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	2026-02-05 21:49:55.233216+00
06e71089-6255-41c5-a9b4-8400d15046c7	f8795176-fd75-422c-ba05-c620e4d00967	74bac9ba-a6ee-4587-97f2-ea34c720f4b2	bee24a5b-c963-4451-86cc-068d3d4b9309	1	t	{"code": "P1_1770328337", "options": [], "parameter_id": "bee24a5b-c963-4451-86cc-068d3d4b9309", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:52:19.073755", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:52:19.042484+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	2026-02-05 21:52:19.042484+00
8b10872e-79ad-4658-b2e0-be5322459ce1	f8795176-fd75-422c-ba05-c620e4d00967	74bac9ba-a6ee-4587-97f2-ea34c720f4b2	458fd9c3-1e3b-4526-90c5-b791616862e3	2	t	{"code": "P2_1770328337", "options": [], "parameter_id": "458fd9c3-1e3b-4526-90c5-b791616862e3", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:52:19.075228", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:52:19.042484+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	2026-02-05 21:52:19.042484+00
2ea4f300-635c-4e4a-abef-58a0d3b16e99	f8795176-fd75-422c-ba05-c620e4d00967	74bac9ba-a6ee-4587-97f2-ea34c720f4b2	3bbea4bb-bdd5-4465-b6d1-001830971892	3	t	{"code": "P3_1770328337", "options": [{"code": "opt1", "option_id": "74519a03-49e9-43a4-adbf-4f87f5ea49b9", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "d4ae2cd6-4259-436a-8a91-f9003f839b13", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "3bbea4bb-bdd5-4465-b6d1-001830971892", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "f8998096-2833-488c-b41e-08dedfcfc32c", "snapshot_date": "2026-02-05T21:52:19.076642", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:52:19.042484+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	2026-02-05 21:52:19.042484+00
703b133b-cb73-4a3f-9629-87a79c35456d	1baaf778-6fda-4e39-be88-3b138bc82f59	58fc5011-88a7-436c-b4a4-c6bb63cdff8c	02f8b306-97b5-4dde-afdb-91725dfec46f	1	t	{"code": "P1_1770328517", "options": [], "parameter_id": "02f8b306-97b5-4dde-afdb-91725dfec46f", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:55:18.764649", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:55:18.748911+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	2026-02-05 21:55:18.748911+00
7d3493c0-58cf-40d3-a013-6b85589c4411	1baaf778-6fda-4e39-be88-3b138bc82f59	58fc5011-88a7-436c-b4a4-c6bb63cdff8c	a9958b3e-69bf-42ac-a56d-c8d16d67d06b	2	t	{"code": "P2_1770328517", "options": [], "parameter_id": "a9958b3e-69bf-42ac-a56d-c8d16d67d06b", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:55:18.765837", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:55:18.748911+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	2026-02-05 21:55:18.748911+00
ff0c67d4-1c81-4718-ad7b-dac7e9af1ba2	1baaf778-6fda-4e39-be88-3b138bc82f59	58fc5011-88a7-436c-b4a4-c6bb63cdff8c	ad806e19-cd1d-4a40-ae12-bd0c5c203b9b	3	t	{"code": "P3_1770328517", "options": [{"code": "opt1", "option_id": "acfc1f03-a09d-408d-88c9-28563d8d9f9a", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "25dd033d-3220-4738-8685-4163540c3b74", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "ad806e19-cd1d-4a40-ae12-bd0c5c203b9b", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "6c5d8da2-26c9-424a-9b09-5f0b70e2c080", "snapshot_date": "2026-02-05T21:55:18.767064", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:55:18.748911+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	2026-02-05 21:55:18.748911+00
c9e74ab3-ffdf-42c3-8290-7a464242fa7e	99678697-d020-427b-9fab-b06977c030ad	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	74d9d4a6-aac1-4ec4-aaa0-b8733a55def7	0	f	{"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T23:08:22.545586", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 23:08:22.499398+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-05 23:08:22.499398+00
f6fbf62f-23f4-445c-96f8-61466a7db198	99678697-d020-427b-9fab-b06977c030ad	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	5c5ea765-416e-49c7-b577-9c075bcfa073	1	f	{"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T23:08:22.550650", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 23:08:22.499398+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-05 23:08:22.499398+00
f7ea5e4a-f7cf-4de7-bcf9-3b58e2d68ebb	99678697-d020-427b-9fab-b06977c030ad	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	326b6dee-185a-42c1-b2d2-c82694e19f86	2	f	{"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T23:08:22.553030", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 23:08:22.499398+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-05 23:08:22.499398+00
8d5f0373-bbc9-488a-9f65-4f9980921a7d	f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	74d9d4a6-aac1-4ec4-aaa0-b8733a55def7	0	f	{"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T23:29:37.241575", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 23:29:37.192094+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-05 23:29:37.192094+00
e93ca77f-28b3-46d4-a4a7-243c38a8fe22	f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	5c5ea765-416e-49c7-b577-9c075bcfa073	1	f	{"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T23:29:37.246750", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 23:29:37.192094+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-05 23:29:37.192094+00
ff46e3c7-0359-4b7d-8758-aa030988bf29	f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	326b6dee-185a-42c1-b2d2-c82694e19f86	2	f	{"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T23:29:37.248412", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 23:29:37.192094+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-05 23:29:37.192094+00
cfbc94f6-5499-425b-bed8-e2f4f0228db7	6afc1849-9bba-466f-bf59-5b6f2bc5f145	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	74d9d4a6-aac1-4ec4-aaa0-b8733a55def7	0	f	{"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-06T11:19:18.440355", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-06 11:19:18.404951+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-06 11:19:18.404951+00
c9105814-8c11-4791-9db0-cc4350e8f792	6afc1849-9bba-466f-bf59-5b6f2bc5f145	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	5c5ea765-416e-49c7-b577-9c075bcfa073	1	f	{"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-06T11:19:18.443012", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-06 11:19:18.404951+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-06 11:19:18.404951+00
aa7c0ac3-f3be-478f-aea9-c0458f3fab26	6afc1849-9bba-466f-bf59-5b6f2bc5f145	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	326b6dee-185a-42c1-b2d2-c82694e19f86	2	f	{"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-06T11:19:18.444729", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-06 11:19:18.404951+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-06 11:19:18.404951+00
412e3fcc-cae5-418e-aac7-d7e8e5b43d31	a316e7a5-0bca-4a61-a7a7-11f3fbde3258	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	74d9d4a6-aac1-4ec4-aaa0-b8733a55def7	0	f	{"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-09T19:10:50.565015", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-09 19:10:50.355687+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-09 19:10:50.355687+00
bb1a8f73-f25c-44dc-b017-b605d6eaf52e	a316e7a5-0bca-4a61-a7a7-11f3fbde3258	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	5c5ea765-416e-49c7-b577-9c075bcfa073	1	f	{"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-09T19:10:50.569926", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-09 19:10:50.355687+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-09 19:10:50.355687+00
787f416e-a631-4885-8009-b8fac277337b	a316e7a5-0bca-4a61-a7a7-11f3fbde3258	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	326b6dee-185a-42c1-b2d2-c82694e19f86	2	f	{"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-09T19:10:50.571122", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-09 19:10:50.355687+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-09 19:10:50.355687+00
9cb44b2d-a65b-4b3a-a732-b33dace86fa4	d18c02c8-4408-4e0f-93b0-ebeb8022f92e	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	74d9d4a6-aac1-4ec4-aaa0-b8733a55def7	0	f	{"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-11T08:20:13.167268", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-11 08:20:13.077943+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-11 08:20:13.077943+00
86f432f9-5947-40bb-8383-bdfafaad0947	d18c02c8-4408-4e0f-93b0-ebeb8022f92e	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	5c5ea765-416e-49c7-b577-9c075bcfa073	1	f	{"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-11T08:20:13.170919", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-11 08:20:13.077943+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-11 08:20:13.077943+00
97b49cd1-551e-4832-823d-00892ebe584d	d18c02c8-4408-4e0f-93b0-ebeb8022f92e	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	326b6dee-185a-42c1-b2d2-c82694e19f86	2	f	{"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-11T08:20:13.172604", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-11 08:20:13.077943+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-11 08:20:13.077943+00
1aa3815a-d912-4964-8d0d-5650890ec678	14d407bc-29ca-4a37-a5fd-85911e2eed9e	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	74d9d4a6-aac1-4ec4-aaa0-b8733a55def7	0	f	{"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-11T08:38:48.104595", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-11 08:38:48.071579+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-11 08:38:48.071579+00
4f350a40-0fc1-4aac-ba5f-047df31627c8	14d407bc-29ca-4a37-a5fd-85911e2eed9e	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	5c5ea765-416e-49c7-b577-9c075bcfa073	1	f	{"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-11T08:38:48.107209", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-11 08:38:48.071579+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-11 08:38:48.071579+00
ccea8977-e9e6-4d6b-a6b3-169f25ee0d7a	14d407bc-29ca-4a37-a5fd-85911e2eed9e	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	326b6dee-185a-42c1-b2d2-c82694e19f86	2	f	{"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-11T08:38:48.109346", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-11 08:38:48.071579+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-11 08:38:48.071579+00
\.


--
-- Data for Name: audit_recommendations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_recommendations (id, audit_id, title, description, created_at, created_by) FROM stdin;
30b692f5-c298-41e4-a998-03ca0a5d33e9	9b38d720-a2fa-4be2-a767-c01a2deb5386	Buy Seeds	High yield seeds	2026-02-05 21:33:45.480244+00	1214c599-c7c2-490b-a895-e45b985b027b
c0ef3ba9-56a5-4262-844e-3ad3f4770833	873f22dc-071a-4f69-8a95-5a98759a6741	Buy Seeds	High yield seeds	2026-02-05 21:34:41.478243+00	d9cd5b64-e423-4710-bcfe-73606bcca78c
c30e4480-3832-4d20-86cc-b6e9c553c569	ce3ea838-c6df-42ce-a9bf-06856078f13b	Buy Seeds	High yield seeds	2026-02-05 21:36:32.890047+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
a501532a-b467-4758-8a66-fa9a8fd5aaf5	b20782d9-2f2c-4504-bc61-f9ae81b84037	Buy Seeds	High yield seeds	2026-02-05 21:39:34.023036+00	fc5165e6-6519-496f-a3dd-1435bc308b5f
671cff9f-1f74-4a7a-b353-8374c16b9f09	c2366bab-e199-490f-aab5-d78f72bd6150	Buy Seeds	High yield seeds	2026-02-05 21:40:37.883311+00	d655e067-4edd-4516-b1b6-821c3c33cfc5
197c68fc-bea0-4e3f-a200-89c580010a65	114aecdb-ebf1-4077-94ab-ff9e56ec3791	Buy Seeds	High yield seeds	2026-02-05 21:41:47.603236+00	13ac055f-b943-4f6d-8182-babe636544df
e59481d1-62ad-4fec-bf3c-6b9be763bdb2	4617c18f-c346-432a-bd36-25804c526fd1	Buy Seeds	High yield seeds	2026-02-05 21:43:43.001359+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
0d86ece3-2dab-45ee-a764-a5ab6c8c02f1	8c0183d7-2bbf-4354-a646-2e60339b3ff6	Buy Seeds	High yield seeds	2026-02-05 21:49:55.374174+00	ebc86578-b9a2-456f-b884-f964c1fb26f9
dfa14c3b-2591-4e3e-a25e-4e811f84b7a7	f8795176-fd75-422c-ba05-c620e4d00967	Buy Seeds	High yield seeds	2026-02-05 21:52:19.253193+00	7eddd813-1060-42a3-aa36-abc2c6529e0f
a422dff3-562d-4124-a768-2ba391ad6c90	1baaf778-6fda-4e39-be88-3b138bc82f59	Buy Seeds	High yield seeds	2026-02-05 21:55:18.910174+00	021aea9d-7fe9-4488-ae61-eebf6d2af731
987e20d0-a7ab-4e67-a160-f7c79eb6c788	f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4	fdgs	fdsgfdg	2026-02-09 18:55:42.894937+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
2c90d25f-fcc3-49d4-8c5a-bbdc2ced5a45	14d407bc-29ca-4a37-a5fd-85911e2eed9e	dfgdfgdfgdfg	dfgdfgdfg	2026-02-11 09:15:19.930191+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
55000b8e-f711-4993-928f-0f66569e89ce	d18c02c8-4408-4e0f-93b0-ebeb8022f92e	asdasd	asdasdasdasasdasa	2026-02-11 09:20:07.106253+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
\.


--
-- Data for Name: audit_reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_reports (id, audit_id, report_html, report_images, pdf_url, created_at, updated_at, created_by) FROM stdin;
5910dd6d-6ee7-4379-8b49-4654191d81ad	55e89250-15fc-4f9b-be3b-01337d242b3e		[]	\N	2026-02-05 18:48:14.929169+00	2026-02-05 20:17:45.722783+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
af32d2c5-e8a5-4ad5-b682-ba3aec48f4fe	99678697-d020-427b-9fab-b06977c030ad		[]	\N	2026-02-05 23:08:43.175729+00	2026-02-05 23:08:43.175729+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
3167ac98-570f-4e7f-a5b0-2fb98b98f497	6afc1849-9bba-466f-bf59-5b6f2bc5f145		[]	\N	2026-02-06 11:20:01.320136+00	2026-02-06 11:20:01.320136+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
8de31332-0622-4b57-9a9e-516c3ad10f9e	f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4	<div>ashfjkash</div>	[]	\N	2026-02-06 09:45:16.785426+00	2026-02-09 13:08:02.701639+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
56ad86e0-8380-44d1-940e-df2a40908fba	a316e7a5-0bca-4a61-a7a7-11f3fbde3258	<div>ok so I have written this note . how are u buddy&nbsp;</div>	[]	\N	2026-02-09 19:11:45.61666+00	2026-02-09 19:12:50.221523+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
a7e76928-f929-4d25-b52a-c81ec6d13dbc	71ea2a9e-9f30-42de-95ce-23492dde9081	<div>sdasdasdasdasdasdasdasdasd</div>	[]	\N	2026-02-11 08:12:50.209909+00	2026-02-11 08:18:49.718708+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
302c7bc9-818f-4762-983e-67d1f7f85dc2	d18c02c8-4408-4e0f-93b0-ebeb8022f92e	<div>hey there its shaurya&nbsp;</div>	[]	\N	2026-02-11 08:20:32.172606+00	2026-02-11 08:20:32.172606+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
21b0c7f3-1f48-4695-9d8f-e1dff73f5619	14d407bc-29ca-4a37-a5fd-85911e2eed9e	<div>SDasda sdasd asd asd asdasdaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaasdas</div>	[]	\N	2026-02-11 08:39:24.715568+00	2026-02-11 08:39:24.715568+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
\.


--
-- Data for Name: audit_response_photos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_response_photos (id, audit_response_id, file_url, file_key, caption, uploaded_at, uploaded_by, audit_id, is_flagged_for_report) FROM stdin;
92309126-f0a1-412f-a253-680869cc9ccf	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_183216.jpg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_183216.jpg	\N	2026-02-04 18:32:15.930238+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
ff9c8278-4df9-4b2a-9e70-4371165424b8	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_183608.jpg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_183608.jpg	\N	2026-02-04 18:36:07.996016+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
b977dd92-bc79-49d0-8aaa-c036c6a6409c	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_184705.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_184705.jpeg	\N	2026-02-04 18:47:05.852701+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
8a6e8436-5a8d-411d-97c8-a9a95da27b4e	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_184710.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_184710.jpeg	\N	2026-02-04 18:47:09.941625+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
1ba4fb22-f30c-45aa-b549-fdc4d80c03cc	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_184731.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_184731.jpeg	\N	2026-02-04 18:47:31.262905+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
30053c50-4faf-4af6-bde9-7a1c9cbb8935	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_184938.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_184938.jpeg	\N	2026-02-04 18:49:38.485588+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
040e09f8-b9d8-4bae-8bf8-8adbfc004d04	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_185359.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_185359.jpeg	\N	2026-02-04 18:53:59.039258+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
0ab1d459-05ba-4371-a695-90a2833c2889	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_185951.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_185951.jpeg	\N	2026-02-04 18:59:51.074976+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
6393b989-f6f9-484c-88f7-c76c90892ec3	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_190059.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_190059.jpeg	\N	2026-02-04 19:00:59.078087+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
d70782ec-7eb0-49b3-8811-99a901dcb4f6	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_190113.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_190113.jpeg	\N	2026-02-04 19:01:13.763319+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
a9b495f5-6003-4c42-8c0f-d88c1959ea67	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_190314.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_190314.jpeg	\N	2026-02-04 19:03:14.340342+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
b614f1fa-6fd6-4c20-8394-09e29283ac78	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_190331.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_190331.jpeg	\N	2026-02-04 19:03:31.487858+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
714217c8-e3dc-4745-a067-5c7446b25f13	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_190833.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_190833.jpeg	\N	2026-02-04 19:08:33.590286+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
7ef75148-d65b-44f9-8006-9550e9e6af3a	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_191739.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_191739.jpeg	\N	2026-02-04 19:17:39.040246+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
b3c724e1-804b-4054-b3dd-fca3a6129d26	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_191842.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260204_191842.jpeg	\N	2026-02-04 19:18:42.069794+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
d57d7fc0-e349-494d-8ee4-961755c383be	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_190601.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_190601.jpeg	\N	2026-02-05 19:06:01.538001+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
455f9200-4a6f-46be-beff-e746bb77092b	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_191144.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_191144.jpeg	\N	2026-02-05 19:11:44.290422+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
42157adb-d748-49af-b9ef-1765222c6c0c	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_191209.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_191209.jpeg	\N	2026-02-05 19:12:09.666884+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
fa39061e-5b69-41f9-b461-aaf0984e304c	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_191426.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_191426.jpeg	\N	2026-02-05 19:14:26.394752+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
085a51ae-5449-4bd1-9ce0-888e8f5855f8	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_192520.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_192520.jpeg	\N	2026-02-05 19:25:20.405851+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
bf681263-2c3e-4ded-a369-eaafae8e418a	7f009411-b5a9-4c12-a50d-14b45a0e807a	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_192851.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_192851.jpeg	\N	2026-02-05 19:28:51.611812+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
3f8cf466-50a6-40d2-9a1e-debf35a08f7f	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193141.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193141.jpeg	\N	2026-02-05 19:31:41.375774+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
0b79d79d-1db2-4e8c-9269-75b7dd83b026	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193151.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193151.jpeg	\N	2026-02-05 19:31:51.596059+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
79e67b62-9b72-4dd3-a526-6fc3ee2ece81	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193339.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193339.jpeg	\N	2026-02-05 19:33:39.197945+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
abd968b1-1acb-4a74-809c-6c1d97ca24b5	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193343.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193343.jpeg	\N	2026-02-05 19:33:43.579138+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
d4528e6d-f725-4487-a48e-7534890de928	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193507.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193507.jpeg	\N	2026-02-05 19:35:07.839693+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
b68df977-ae3d-4e83-9089-5bd58593a62a	\N	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193521.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193521.jpeg	\N	2026-02-05 19:35:20.998583+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
42bdb6bc-a967-4ba4-b92e-03ad52294291	881b2ddd-2417-4b66-b7bc-9596c6365df7	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193832.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_193832.jpeg	\N	2026-02-05 19:38:32.446367+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
19a6ac9f-ce2a-40c1-885e-70bd348ac409	2d980be8-baa6-432b-ba11-eb2155739c32	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_201143.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_201143.jpeg	\N	2026-02-05 20:11:43.650485+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
1a706760-b7bb-4945-a26d-85960e088cf2	406dcd4d-bb23-4e57-9fbe-bd968fede31c	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_201114.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_201114.jpeg	\N	2026-02-05 20:11:14.854013+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
3398326a-34a4-4dc5-a2e0-5bf2b7b9894e	2d980be8-baa6-432b-ba11-eb2155739c32	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_201119.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_201119.jpeg	\N	2026-02-05 20:11:19.741472+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
b595a221-b6ac-46f7-8f3e-c4973ae522d9	7f009411-b5a9-4c12-a50d-14b45a0e807a	/uploads/audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_201021.jpeg	audits/55e89250-15fc-4f9b-be3b-01337d242b3e/evidence/20260205_201021.jpeg	\N	2026-02-05 20:10:21.731286+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	55e89250-15fc-4f9b-be3b-01337d242b3e	f
6a57c6a5-0e3d-45a8-9ca3-f56ed6d98e0d	538c8fb2-2896-4db9-ba33-db1b07235ccd	/uploads/audits/99678697-d020-427b-9fab-b06977c030ad/evidence/20260205_230833.jpeg	audits/99678697-d020-427b-9fab-b06977c030ad/evidence/20260205_230833.jpeg	\N	2026-02-05 23:08:33.2762+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	99678697-d020-427b-9fab-b06977c030ad	f
80c7a12e-60c1-4988-b819-53afc22b80e4	11c937cd-3075-4007-b79b-983584b0ec26	/uploads/audits/99678697-d020-427b-9fab-b06977c030ad/evidence/20260205_230829.jpeg	audits/99678697-d020-427b-9fab-b06977c030ad/evidence/20260205_230829.jpeg	\N	2026-02-05 23:08:29.403203+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	99678697-d020-427b-9fab-b06977c030ad	f
f28f258b-6266-43fd-a78d-15a7d974f808	\N	/uploads/audits/f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4/evidence/20260205_232958.jpeg	audits/f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4/evidence/20260205_232958.jpeg	\N	2026-02-05 23:29:57.595092+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4	f
a66648c8-daa9-4501-b606-69b56bd90606	\N	https://uzhathunai-uploads.s3.us-east-1.amazonaws.com/audits/f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4/evidence/20260206_094017.jpeg	audits/f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4/evidence/20260206_094017.jpeg	\N	2026-02-06 09:40:17.282767+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4	f
1bb8ad18-81b6-47f1-8717-efc79cad093e	\N	https://uzhathunai-uploads.s3.us-east-1.amazonaws.com/audits/f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4/evidence/20260206_094523.jpeg	audits/f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4/evidence/20260206_094523.jpeg	\N	2026-02-06 09:45:23.392248+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4	f
9f5c0be6-bf3b-408b-b630-afcf9773ed7b	2e292af3-6758-4637-85c4-6c7a464c62a7	https://uzhathunai-uploads.s3.ap-south-1.amazonaws.com/audits/6afc1849-9bba-466f-bf59-5b6f2bc5f145/evidence/20260206_111946.jpeg	audits/6afc1849-9bba-466f-bf59-5b6f2bc5f145/evidence/20260206_111946.jpeg	\N	2026-02-06 11:19:46.124142+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	6afc1849-9bba-466f-bf59-5b6f2bc5f145	f
76296df1-ff2d-431e-a753-bb7e71d964a8	5d21a6c7-7ca5-49b9-b403-673a8aae27c3	https://uzhathunai-uploads.s3.ap-south-1.amazonaws.com/audits/a316e7a5-0bca-4a61-a7a7-11f3fbde3258/evidence/20260209_191227.jpeg	audits/a316e7a5-0bca-4a61-a7a7-11f3fbde3258/evidence/20260209_191227.jpeg	\N	2026-02-09 19:12:27.675843+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	a316e7a5-0bca-4a61-a7a7-11f3fbde3258	f
\.


--
-- Data for Name: audit_responses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_responses (id, audit_id, audit_parameter_instance_id, response_text, response_numeric, response_date, response_options, notes, created_at, updated_at, created_by) FROM stdin;
0ba5972d-969e-4982-919d-e9a98393f846	71ea2a9e-9f30-42de-95ce-23492dde9081	f5819c8a-65da-495a-ac3c-acde697ab0e5	\N	\N	\N	{}	\N	2026-01-30 00:10:57.715119+00	2026-01-30 00:10:57.715119+00	08c368c7-0ea2-4dad-a5fe-5e8e180b0b44
517d3fc3-66cd-4993-a7db-6efe641a3bbf	8864a618-4dcc-47b9-901f-9859b539c579	f2fa2bc2-0235-4c54-a9da-7a624793a3b3	\N	50.5000	\N	\N	\N	2026-02-05 21:31:42.952101+00	2026-02-05 21:31:42.952101+00	53126f3a-94da-4363-b20d-61a85c99574a
fbfcd00e-bd53-4c9a-bdee-c51f7b3cfb7b	8864a618-4dcc-47b9-901f-9859b539c579	19cee73e-6e9e-4a49-b6aa-7c4b400ccd8e	Good condition	\N	\N	\N	\N	2026-02-05 21:31:42.981402+00	2026-02-05 21:31:42.981402+00	53126f3a-94da-4363-b20d-61a85c99574a
52f455b3-4533-4de6-8f83-bc4a35d05235	9b38d720-a2fa-4be2-a767-c01a2deb5386	67447ad3-6ef9-4b36-afeb-eb2e68b4df78	\N	50.5000	\N	\N	\N	2026-02-05 21:33:45.366701+00	2026-02-05 21:33:45.366701+00	1214c599-c7c2-490b-a895-e45b985b027b
8e6424c6-87b3-465e-af94-e75acd69fa8f	9b38d720-a2fa-4be2-a767-c01a2deb5386	f835ae13-e0df-4137-95dd-8367e61bd3d2	Good condition	\N	\N	\N	\N	2026-02-05 21:33:45.382147+00	2026-02-05 21:33:45.382147+00	1214c599-c7c2-490b-a895-e45b985b027b
361fdfea-e93e-40bc-934b-12496ca8594a	9b38d720-a2fa-4be2-a767-c01a2deb5386	f0427230-81bf-4314-a2f3-0d61341975b1	\N	\N	\N	{68b94446-68e1-4ec5-8b41-cc9842033394}	\N	2026-02-05 21:33:45.397484+00	2026-02-05 21:33:45.397484+00	1214c599-c7c2-490b-a895-e45b985b027b
85afc05f-c8bf-46f7-b07a-06871ce9e7a5	873f22dc-071a-4f69-8a95-5a98759a6741	4a1b45ae-44d3-41a1-99ee-b2158d35bd97	\N	50.5000	\N	\N	\N	2026-02-05 21:34:41.37312+00	2026-02-05 21:34:41.37312+00	d9cd5b64-e423-4710-bcfe-73606bcca78c
d88eae4a-c324-4988-b490-da735720077b	873f22dc-071a-4f69-8a95-5a98759a6741	a8f243f7-8386-4f91-aa85-3929d15fbaa2	Good condition	\N	\N	\N	\N	2026-02-05 21:34:41.390808+00	2026-02-05 21:34:41.390808+00	d9cd5b64-e423-4710-bcfe-73606bcca78c
d77cfa5f-4096-4dbe-99e7-29d5d836abfe	873f22dc-071a-4f69-8a95-5a98759a6741	8ff19dcd-835f-42f0-993b-c3abd9421008	\N	\N	\N	{ee25c5c6-aadd-4c6a-ab13-3070b40ddf05}	\N	2026-02-05 21:34:41.408407+00	2026-02-05 21:34:41.408407+00	d9cd5b64-e423-4710-bcfe-73606bcca78c
44721e2e-0b38-4701-bed6-60340ec2d23d	ce3ea838-c6df-42ce-a9bf-06856078f13b	43ebd3cb-9790-4493-b86e-03a5b27047b5	\N	50.5000	\N	\N	\N	2026-02-05 21:36:32.806841+00	2026-02-05 21:36:32.806841+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
e8f97fc6-4316-43fc-be95-bd4996992d68	ce3ea838-c6df-42ce-a9bf-06856078f13b	74d32f8f-2605-43a1-b77f-dd957678295d	Good condition	\N	\N	\N	\N	2026-02-05 21:36:32.819669+00	2026-02-05 21:36:32.819669+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
531b8d9f-9729-4892-b4fb-3a06c6f7cfb5	ce3ea838-c6df-42ce-a9bf-06856078f13b	7576e4fd-603a-40be-99b5-12cb7b682f7f	\N	\N	\N	{c2b584fc-e308-4562-ba68-3bdc7c1f8ecc}	\N	2026-02-05 21:36:32.8349+00	2026-02-05 21:36:32.8349+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
1a347840-f3a8-45e0-a944-f8ca5d0abcc5	b20782d9-2f2c-4504-bc61-f9ae81b84037	06a8b4e1-0df9-4cae-9ecc-5f4771cd2f7d	\N	50.5000	\N	\N	\N	2026-02-05 21:39:33.887819+00	2026-02-05 21:39:33.887819+00	fc5165e6-6519-496f-a3dd-1435bc308b5f
0bec0840-c841-4346-bc37-fd138bb47215	b20782d9-2f2c-4504-bc61-f9ae81b84037	f703dd94-2057-4c38-9e5c-f06805a897de	Good condition	\N	\N	\N	\N	2026-02-05 21:39:33.909549+00	2026-02-05 21:39:33.909549+00	fc5165e6-6519-496f-a3dd-1435bc308b5f
581539dc-7fe4-4269-887d-a375c2f63094	b20782d9-2f2c-4504-bc61-f9ae81b84037	1bc7bc86-89dd-45f5-9f83-881f65df2578	\N	\N	\N	{6baefc9c-88e8-4aa1-a021-8cae81a905ed}	\N	2026-02-05 21:39:33.929495+00	2026-02-05 21:39:33.929495+00	fc5165e6-6519-496f-a3dd-1435bc308b5f
12a35bbe-c5bf-4738-b237-34b4c400f3ad	c2366bab-e199-490f-aab5-d78f72bd6150	8fb82770-4575-49cb-ae8b-f0d63f717cab	\N	50.5000	\N	\N	\N	2026-02-05 21:40:37.779052+00	2026-02-05 21:40:37.779052+00	d655e067-4edd-4516-b1b6-821c3c33cfc5
0e2e99e8-4c34-464c-b585-f58b41e44a5a	c2366bab-e199-490f-aab5-d78f72bd6150	7694c5aa-f77f-408f-8657-7f3f5d0cdaa3	Good condition	\N	\N	\N	\N	2026-02-05 21:40:37.797461+00	2026-02-05 21:40:37.797461+00	d655e067-4edd-4516-b1b6-821c3c33cfc5
6ca7b0fe-101b-4329-acfe-444b2cd0fb09	c2366bab-e199-490f-aab5-d78f72bd6150	b53c25f3-3b7a-459e-adaa-279928009959	\N	\N	\N	{cc1a045b-0ce5-4c07-afed-eca7a4d7896f}	\N	2026-02-05 21:40:37.815546+00	2026-02-05 21:40:37.815546+00	d655e067-4edd-4516-b1b6-821c3c33cfc5
5ffd49aa-b156-4150-9f99-c8c559a825df	114aecdb-ebf1-4077-94ab-ff9e56ec3791	c042d163-ee00-4ab5-b557-366a7946877c	\N	50.5000	\N	\N	\N	2026-02-05 21:41:47.496125+00	2026-02-05 21:41:47.496125+00	13ac055f-b943-4f6d-8182-babe636544df
63475a69-4022-460e-913e-b1010153aa16	114aecdb-ebf1-4077-94ab-ff9e56ec3791	2bad393e-5c28-4fdc-b875-47ad3fdc541e	Good condition	\N	\N	\N	\N	2026-02-05 21:41:47.512196+00	2026-02-05 21:41:47.512196+00	13ac055f-b943-4f6d-8182-babe636544df
321b3a61-2abd-41c5-8d07-63797363bf05	114aecdb-ebf1-4077-94ab-ff9e56ec3791	0790ce02-cebe-4875-ba68-eebf6740c31f	\N	\N	\N	{8337ba01-c7bc-4553-86d0-672c65399b38}	\N	2026-02-05 21:41:47.53022+00	2026-02-05 21:41:47.53022+00	13ac055f-b943-4f6d-8182-babe636544df
6b66a4f6-9467-45f8-a141-afc4ebde9af6	4617c18f-c346-432a-bd36-25804c526fd1	74b02351-8066-4945-b6ee-1a2f7d9bd16c	\N	50.5000	\N	\N	\N	2026-02-05 21:43:42.91757+00	2026-02-05 21:43:42.91757+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
d25a0f04-f5d0-4e82-99da-1d420825e6cd	4617c18f-c346-432a-bd36-25804c526fd1	53225349-67b7-4cfa-8aff-5ed4c2bfc4a5	Good condition	\N	\N	\N	\N	2026-02-05 21:43:42.933749+00	2026-02-05 21:43:42.933749+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
7fa6b329-e3b3-45a3-9836-ad16d5e531d4	4617c18f-c346-432a-bd36-25804c526fd1	dc214121-294b-4750-a4f0-ddb7fe601419	\N	\N	\N	{3f3b03fa-ef0e-42fe-9546-c33af35d1681}	\N	2026-02-05 21:43:42.945828+00	2026-02-05 21:43:42.945828+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
852fd8fe-dad4-46f7-822e-65b495ad0706	8c0183d7-2bbf-4354-a646-2e60339b3ff6	14c86060-a606-421e-9388-334d38f0d70f	\N	50.5000	\N	\N	\N	2026-02-05 21:49:55.295562+00	2026-02-05 21:49:55.295562+00	ebc86578-b9a2-456f-b884-f964c1fb26f9
18efabb8-fefc-4b0f-af53-7bc9b468a1ae	8c0183d7-2bbf-4354-a646-2e60339b3ff6	a462112e-b2d9-4c8c-acf5-a08159f6ed0e	Good condition	\N	\N	\N	\N	2026-02-05 21:49:55.310823+00	2026-02-05 21:49:55.310823+00	ebc86578-b9a2-456f-b884-f964c1fb26f9
99cea9cf-4c31-46dc-a61f-ccde674b143e	8c0183d7-2bbf-4354-a646-2e60339b3ff6	745de89d-d546-4817-aad9-c14b12755667	\N	\N	\N	{2c2e893a-cd32-4855-b766-681bb293adb7}	\N	2026-02-05 21:49:55.323961+00	2026-02-05 21:49:55.323961+00	ebc86578-b9a2-456f-b884-f964c1fb26f9
77ec08e6-4947-4b09-891e-6a331b4066c5	f8795176-fd75-422c-ba05-c620e4d00967	06e71089-6255-41c5-a9b4-8400d15046c7	\N	50.5000	\N	\N	\N	2026-02-05 21:52:19.143876+00	2026-02-05 21:52:19.143876+00	7eddd813-1060-42a3-aa36-abc2c6529e0f
57d5eeaa-38f1-4fea-a5c5-1be1e9de786e	f8795176-fd75-422c-ba05-c620e4d00967	8b10872e-79ad-4658-b2e0-be5322459ce1	Good condition	\N	\N	\N	\N	2026-02-05 21:52:19.167468+00	2026-02-05 21:52:19.167468+00	7eddd813-1060-42a3-aa36-abc2c6529e0f
6a8fc36e-bdc7-461c-bd08-b603a7c8275b	f8795176-fd75-422c-ba05-c620e4d00967	2ea4f300-635c-4e4a-abef-58a0d3b16e99	\N	\N	\N	{74519a03-49e9-43a4-adbf-4f87f5ea49b9}	\N	2026-02-05 21:52:19.187676+00	2026-02-05 21:52:19.187676+00	7eddd813-1060-42a3-aa36-abc2c6529e0f
518c8fe9-bb22-4176-812c-d85f29781de8	1baaf778-6fda-4e39-be88-3b138bc82f59	703b133b-cb73-4a3f-9629-87a79c35456d	\N	50.5000	\N	\N	\N	2026-02-05 21:55:18.809386+00	2026-02-05 21:55:18.809386+00	021aea9d-7fe9-4488-ae61-eebf6d2af731
f3ab6547-5093-494a-8b5d-420902c42ee8	4bfdee24-2fd6-45c7-80fd-4a7513ca3037	9a410db0-f030-428c-a457-aaea3143ab30	\N	7.0000	\N	\N	\N	2026-02-01 10:38:13.527837+00	2026-02-01 10:38:13.527837+00	1ce1ba48-b899-4217-8fd9-2124dd4765c6
7b13c033-a6e0-40df-abe9-c749a4104e49	41acc9c4-1f08-40f1-90cf-e85c80e17de2	ca426fc5-3e31-4110-b467-fdab4b78f694	\N	7.0000	\N	\N	\N	2026-02-01 10:38:59.411031+00	2026-02-01 10:38:59.411031+00	05e362b8-0b73-44ed-bded-ef4e0a40dd47
099983cf-9251-42f0-84b5-ace82a94ce56	1baaf778-6fda-4e39-be88-3b138bc82f59	7d3493c0-58cf-40d3-a013-6b85589c4411	Good condition	\N	\N	\N	\N	2026-02-05 21:55:18.826769+00	2026-02-05 21:55:18.826769+00	021aea9d-7fe9-4488-ae61-eebf6d2af731
8fd51bf8-2eac-4668-a4f4-b2de7a178a7e	34c22a9d-d7da-44d5-a18c-d9f706b11299	99aaf6d4-9ed0-4319-b66d-b7bbfc5db7a1	\N	7.0000	\N	\N	\N	2026-02-01 11:01:39.834276+00	2026-02-01 11:01:39.834276+00	b9c25548-e5ba-4200-9dc9-1ba98f332540
09e3babf-c021-42c3-9b9e-d29b05121750	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	063af9a8-6c91-4489-b2a9-59d13613d47e	\N	10.0000	\N	\N	\N	2026-02-01 11:06:39.299062+00	2026-02-01 11:06:39.299062+00	a30a9865-926a-4d26-af0d-42e44657b429
e1313494-ccb7-401a-b3e7-bf61b7134498	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	4c0a07e1-5bd3-4b3c-8e4b-92b557c6bb43	\N	11.0000	\N	\N	\N	2026-02-01 11:06:39.314437+00	2026-02-01 11:06:39.314437+00	a30a9865-926a-4d26-af0d-42e44657b429
5a925ea6-84c5-43a8-b9a7-3d4b6525dcdd	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	e4103236-56c4-48e1-8ef7-a1b2216acb9e	\N	12.0000	\N	\N	\N	2026-02-01 11:06:39.33148+00	2026-02-01 11:06:39.33148+00	a30a9865-926a-4d26-af0d-42e44657b429
12f57026-ebce-4826-b0b4-5bbf08fb5533	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	8a8ba3c8-0a3d-4d9f-ad24-d5113a85dfcc	\N	13.0000	\N	\N	\N	2026-02-01 11:06:39.347811+00	2026-02-01 11:06:39.347811+00	a30a9865-926a-4d26-af0d-42e44657b429
ca27b20a-72ce-42c7-ac72-7ecea4520adb	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	830c1db9-f276-4431-89a7-ac90ead62205	\N	14.0000	\N	\N	\N	2026-02-01 11:06:39.36336+00	2026-02-01 11:06:39.36336+00	a30a9865-926a-4d26-af0d-42e44657b429
261f7b25-f6f3-4254-8407-323f22ee5c91	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	b4a661a0-3491-4ea7-8ea4-6d78665ce56e	\N	15.0000	\N	\N	\N	2026-02-01 11:06:39.378318+00	2026-02-01 11:06:39.378318+00	a30a9865-926a-4d26-af0d-42e44657b429
27d7e870-651d-4b16-85fe-0e8e8916e174	78983c2b-01c0-4c2e-8b46-c3773b1a8b6e	a308b693-d7f0-4037-9f5a-3d36468ce737	\N	7.0000	\N	\N	\N	2026-02-01 10:32:49.497231+00	2026-02-01 10:32:49.497231+00	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c
0d768080-9f54-477a-b885-7d0aa86fd0d3	def41ef5-6c84-4840-b991-65f5ca1b95b7	e5c9f421-f171-4d96-85bb-7faa56dde183	\N	7.0000	\N	\N	\N	2026-02-01 10:33:10.217362+00	2026-02-01 10:33:10.217362+00	bf660c8b-3818-4cf7-85f1-3071c0a7943c
512229c1-3f67-498f-b943-3ea791e9002f	4ce704ad-c335-4c99-bc24-1a8a66877c08	c0849ffa-2b80-450d-bd1a-e2764499d5fd	\N	7.0000	\N	\N	\N	2026-02-01 10:33:32.230892+00	2026-02-01 10:33:32.230892+00	c7a092a7-d354-498d-b23a-d4802d99ccb4
ef860ebf-3462-4bc5-a399-426ca8e59d8e	71fb6a9e-6f74-48cd-af01-fe4fcd86975b	ba122b1e-178e-4954-8e48-cdc057cf6505	\N	7.0000	\N	\N	\N	2026-02-01 10:34:04.630946+00	2026-02-01 10:34:04.630946+00	2199f334-fccd-46ff-b45c-2cd81aadeca2
579405d9-13c7-4dfc-badc-f4edfb916e2a	a4ba5400-35ae-4cc6-880b-9aac13cceddd	720dbf19-4931-4ead-a894-f892ea5482e4	\N	7.0000	\N	\N	\N	2026-02-01 10:34:22.179006+00	2026-02-01 10:34:22.179006+00	b46ab366-7dcb-4ee5-a558-dc328db04159
aec02c05-7841-4f6b-a219-e47cbe5c6f78	a4723a72-f91c-4f12-a268-8809d0da3d7f	50e7c163-b8df-4fe2-94fd-21da5e54bdbf	\N	7.0000	\N	\N	\N	2026-02-01 10:34:42.761757+00	2026-02-01 10:34:42.761757+00	979cfcfd-a872-40df-8380-dbe81f29e7a5
53cd674c-0152-45ec-aa73-9a8c99147f0a	20095d3d-e585-4320-b1f8-cfcc30752b5f	959621f3-ac7f-443b-9d94-3501d65cdbd1	\N	7.0000	\N	\N	\N	2026-02-01 10:35:08.101085+00	2026-02-01 10:35:08.101085+00	810cc398-af79-4d96-9eee-af0f1bbf8683
9a0a64b7-0c85-41ea-9190-d56f55edb6cf	79739771-770e-44a9-ab0b-b347e6ebe770	216d7cf9-c477-4cc3-9234-f37bdd99be61	\N	7.0000	\N	\N	\N	2026-02-01 10:35:48.302343+00	2026-02-01 10:35:48.302343+00	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a
4d69d487-6e79-4e43-9257-264c527b90cd	d90be630-cd0b-401d-99f2-9ae0ba0066e7	9fedc85b-3fd4-4a2d-aaee-28c47adfab51	\N	7.0000	\N	\N	\N	2026-02-01 10:36:44.255958+00	2026-02-01 10:36:44.255958+00	ef5984b4-54b6-47cf-a9bb-ca02cadc0180
17c0a2c9-954f-4dcd-b975-d16a3304d7fa	0cfc963d-fe8b-4ca3-b720-49ab3696623a	b1b33dc8-b68a-4f11-a3da-e60d9279c7a9	\N	7.0000	\N	\N	\N	2026-02-01 10:37:05.357848+00	2026-02-01 10:37:05.357848+00	70904796-fe39-4007-b892-a8aa3c8e0e8f
7fb56f52-a3bd-4672-abc1-8b1258107e89	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	219d6b6b-19db-45b3-91e3-ade7ea886074	\N	16.0000	\N	\N	\N	2026-02-01 11:06:39.393259+00	2026-02-01 11:06:39.393259+00	a30a9865-926a-4d26-af0d-42e44657b429
17db2bc0-d445-4e9c-b6c9-4a9388b69cc7	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	2c2317ee-d526-4265-a83c-f3f8ec89f77b	\N	17.0000	\N	\N	\N	2026-02-01 11:06:39.408471+00	2026-02-01 11:06:39.408471+00	a30a9865-926a-4d26-af0d-42e44657b429
9f1a4278-cc34-4e17-8c88-b877d9344837	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	219931e8-f3d3-44ff-971d-7ee598bde9fd	\N	18.0000	\N	\N	\N	2026-02-01 11:06:39.423749+00	2026-02-01 11:06:39.423749+00	a30a9865-926a-4d26-af0d-42e44657b429
f44ee6d0-15c5-4120-a1dd-1c2278a1bf06	6ec94163-4bb8-4b65-85e9-dd4a37678d8e	367c700b-40d6-4c26-b0de-753d98d8245a	\N	19.0000	\N	\N	\N	2026-02-01 11:06:39.439626+00	2026-02-01 11:06:39.439626+00	a30a9865-926a-4d26-af0d-42e44657b429
e15b50ca-5c46-464d-9371-7760d3a82ee5	55e89250-15fc-4f9b-be3b-01337d242b3e	3c4f2f1f-0fd4-49fa-bd86-8dc9d4bf820a	\N	234234.0000	\N	\N	\N	2026-02-05 19:39:08.568963+00	2026-02-05 19:39:08.568963+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
28d409ad-036a-49d8-b140-29c1f4003723	55e89250-15fc-4f9b-be3b-01337d242b3e	e5ec51ce-2c4b-40af-8a9a-9d5c7ea87e14	\N	\N	\N	{ceba3c16-431a-4ddd-b565-51a899129e34}	\N	2026-02-05 19:38:03.022763+00	2026-02-05 20:14:27.641707+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
7f009411-b5a9-4c12-a50d-14b45a0e807a	55e89250-15fc-4f9b-be3b-01337d242b3e	51bacee2-7f70-4b7c-90b2-0e0d33c69d15	\N	\N	\N	\N	\N	2026-02-05 19:05:20.965965+00	2026-02-05 20:17:45.686307+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
406dcd4d-bb23-4e57-9fbe-bd968fede31c	55e89250-15fc-4f9b-be3b-01337d242b3e	74a4b0e3-00b8-4ccb-9d3b-df9f479e79e5	\N	\N	\N	\N	\N	2026-02-05 19:05:44.757734+00	2026-02-05 20:17:45.686307+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
2d980be8-baa6-432b-ba11-eb2155739c32	55e89250-15fc-4f9b-be3b-01337d242b3e	1b022ef2-7906-4a69-9825-25ddcb4dda82	\N	\N	\N	\N	\N	2026-02-05 19:39:08.568963+00	2026-02-05 20:17:45.686307+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
881b2ddd-2417-4b66-b7bc-9596c6365df7	55e89250-15fc-4f9b-be3b-01337d242b3e	ec608ef9-15d0-4efc-958e-29c5181fa8a3	\N	\N	\N	{0c80853b-5a5b-4b87-8ba9-943fcf02bb3b}	\N	2026-02-05 19:39:08.568963+00	2026-02-05 20:17:45.686307+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
35a32abf-12d3-4496-a93b-9e92573eb821	1baaf778-6fda-4e39-be88-3b138bc82f59	ff0c67d4-1c81-4718-ad7b-dac7e9af1ba2	\N	\N	\N	{acfc1f03-a09d-408d-88c9-28563d8d9f9a}	\N	2026-02-05 21:55:18.844298+00	2026-02-05 21:55:18.844298+00	021aea9d-7fe9-4488-ae61-eebf6d2af731
11c937cd-3075-4007-b79b-983584b0ec26	99678697-d020-427b-9fab-b06977c030ad	c9e74ab3-ffdf-42c3-8290-7a464242fa7e	asdasdasdasdasd	\N	\N	\N	\N	2026-02-05 23:08:43.195669+00	2026-02-05 23:08:43.195669+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
538c8fb2-2896-4db9-ba33-db1b07235ccd	99678697-d020-427b-9fab-b06977c030ad	f6fbf62f-23f4-445c-96f8-61466a7db198	asdasdasdasdasd	\N	\N	\N	\N	2026-02-05 23:08:43.195669+00	2026-02-05 23:08:43.195669+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
b86166bd-d293-466b-b284-77ec39a38e62	f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4	8d5f0373-bbc9-488a-9f65-4f9980921a7d	asdasdasdasd	\N	\N	\N	\N	2026-02-06 09:45:16.800536+00	2026-02-06 09:45:16.800536+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
2e292af3-6758-4637-85c4-6c7a464c62a7	6afc1849-9bba-466f-bf59-5b6f2bc5f145	cfbc94f6-5499-425b-bed8-e2f4f0228db7	https://uzhathunai-uploads.s3.ap-south-1.amazonaws.com/audits/6afc1849-9bba-466f-bf59-5b6f2bc5f145/evidence/20260206_111946.jpeg	\N	\N	\N	\N	2026-02-06 11:20:01.334334+00	2026-02-06 11:20:01.334334+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
9b2c6482-8305-4455-912a-e68103229f6b	6afc1849-9bba-466f-bf59-5b6f2bc5f145	c9105814-8c11-4791-9db0-cc4350e8f792	sdfsdf	\N	\N	\N	\N	2026-02-06 11:20:01.334334+00	2026-02-06 11:20:01.334334+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
a2e859ce-d546-4eda-a019-c77615a9bf9a	6afc1849-9bba-466f-bf59-5b6f2bc5f145	aa7c0ac3-f3be-478f-aea9-c0458f3fab26	\N	234.0000	\N	\N	\N	2026-02-06 11:20:01.334334+00	2026-02-06 11:20:01.334334+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
5d21a6c7-7ca5-49b9-b403-673a8aae27c3	a316e7a5-0bca-4a61-a7a7-11f3fbde3258	412e3fcc-cae5-418e-aac7-d7e8e5b43d31	Mother marry pls help me 	\N	\N	\N	NUN II	2026-02-09 19:12:50.099006+00	2026-02-09 19:12:50.099006+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
81a09a3e-c286-4548-9012-9727c14d7fa6	a316e7a5-0bca-4a61-a7a7-11f3fbde3258	bb1a8f73-f25c-44dc-b017-b605d6eaf52e	Ok so everything's is fine	\N	\N	\N	\N	2026-02-09 19:12:50.099006+00	2026-02-09 19:12:50.099006+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
260ad3f3-e671-47f4-8be3-4df9efc05f06	a316e7a5-0bca-4a61-a7a7-11f3fbde3258	787f416e-a631-4885-8009-b8fac277337b	\N	23.0000	\N	\N	\N	2026-02-09 19:12:50.099006+00	2026-02-09 19:12:50.099006+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
765b9aa5-a291-4017-9357-f5bdc4f3443b	d18c02c8-4408-4e0f-93b0-ebeb8022f92e	9cb44b2d-a65b-4b3a-a732-b33dace86fa4	asdasdas	\N	\N	\N	\N	2026-02-11 08:20:32.064147+00	2026-02-11 08:20:32.064147+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
62ad4db6-647a-4d7d-acbb-2e70f065c18f	d18c02c8-4408-4e0f-93b0-ebeb8022f92e	86f432f9-5947-40bb-8383-bdfafaad0947	dasdasdads	\N	\N	\N	\N	2026-02-11 08:20:32.064147+00	2026-02-11 08:20:32.064147+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
ce56da4f-be14-44de-91c9-e5da813b33ed	d18c02c8-4408-4e0f-93b0-ebeb8022f92e	97b49cd1-551e-4832-823d-00892ebe584d	\N	234.0000	\N	\N	\N	2026-02-11 08:20:32.064147+00	2026-02-11 08:20:32.064147+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
b91f797f-825c-40e7-bc08-b130dafd5292	14d407bc-29ca-4a37-a5fd-85911e2eed9e	1aa3815a-d912-4964-8d0d-5650890ec678	asdasd	\N	\N	\N	\N	2026-02-11 08:39:24.572463+00	2026-02-11 08:39:24.572463+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
82df39fe-87b9-4086-a6fe-8e1b95e026bc	14d407bc-29ca-4a37-a5fd-85911e2eed9e	4f350a40-0fc1-4aac-ba5f-047df31627c8	asdasdsada	\N	\N	\N	\N	2026-02-11 08:39:24.572463+00	2026-02-11 08:39:24.572463+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
a2793d46-4248-482a-87fc-835f3f5d22fa	14d407bc-29ca-4a37-a5fd-85911e2eed9e	ccea8977-e9e6-4d6b-a6b3-169f25ee0d7a	\N	123.0000	\N	\N	\N	2026-02-11 08:39:24.572463+00	2026-02-11 08:39:24.572463+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
\.


--
-- Data for Name: audit_review_photos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_review_photos (id, audit_response_photo_id, is_flagged_for_report, caption, reviewed_at, reviewed_by) FROM stdin;
1eadce8d-f826-4150-a48b-7964591ec101	80c7a12e-60c1-4988-b819-53afc22b80e4	t	Flagged for farmer report	2026-02-05 23:18:03.857452+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
6e801a33-eca0-408a-9141-22b21d5cc077	6a57c6a5-0e3d-45a8-9ca3-f56ed6d98e0d	t	Flagged for farmer report	2026-02-05 23:18:03.857452+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
\.


--
-- Data for Name: audit_reviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_reviews (id, audit_response_id, response_text, response_numeric, response_date, response_option_ids, is_flagged_for_report, reviewed_at, reviewed_by) FROM stdin;
4574b9dc-d198-495d-a9b7-4b10422fbcd2	579405d9-13c7-4dfc-badc-f4edfb916e2a	Correction based on lab data	6.5000	\N	\N	t	2026-02-01 10:34:22.220972+00	b46ab366-7dcb-4ee5-a558-dc328db04159
6b90e85a-7772-4e8a-9ea4-473d4b032a13	aec02c05-7841-4f6b-a219-e47cbe5c6f78	Correction based on lab data	6.5000	\N	\N	t	2026-02-01 10:34:42.803159+00	979cfcfd-a872-40df-8380-dbe81f29e7a5
08d145df-ef8e-4e74-9d07-8d1c9fbec7be	53cd674c-0152-45ec-aa73-9a8c99147f0a	Correction based on lab data	6.5000	\N	\N	t	2026-02-01 10:35:08.141542+00	810cc398-af79-4d96-9eee-af0f1bbf8683
b45464e8-6c04-42c9-b86d-85b61c83fa93	9a0a64b7-0c85-41ea-9190-d56f55edb6cf	Correction based on lab data	6.5000	\N	\N	t	2026-02-01 10:35:48.340221+00	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a
4bd45826-1249-4d05-bcf1-ff03b1a2aa7c	4d69d487-6e79-4e43-9257-264c527b90cd	Correction based on lab data	6.5000	\N	\N	t	2026-02-01 10:36:44.303972+00	ef5984b4-54b6-47cf-a9bb-ca02cadc0180
1e4cacfd-ed01-4beb-9831-9ee6bbb7e721	17c0a2c9-954f-4dcd-b975-d16a3304d7fa	Correction based on lab data	6.5000	\N	\N	t	2026-02-01 10:37:05.39844+00	70904796-fe39-4007-b892-a8aa3c8e0e8f
3a114a81-1667-4e10-bed4-bd8559218b5b	f3ab6547-5093-494a-8b5d-420902c42ee8	Correction based on lab data	6.5000	\N	\N	t	2026-02-01 10:38:13.561493+00	1ce1ba48-b899-4217-8fd9-2124dd4765c6
fc5a47ce-d1e4-4a64-a012-a107762f5662	7b13c033-a6e0-40df-abe9-c749a4104e49	Correction based on lab data	6.5000	\N	\N	t	2026-02-01 10:38:59.457968+00	05e362b8-0b73-44ed-bded-ef4e0a40dd47
a117e7c0-c40e-47c5-a5ed-3bce676b5285	8fd51bf8-2eac-4668-a4f4-b2de7a178a7e	Correction based on lab data	6.5000	\N	\N	t	2026-02-01 11:01:39.875548+00	b9c25548-e5ba-4200-9dc9-1ba98f332540
4edf31c0-9482-4097-9e17-8239b705ca6c	09e3babf-c021-42c3-9b9e-d29b05121750	Review comment for Param 1	10.5000	\N	\N	t	2026-02-01 11:06:39.489187+00	a30a9865-926a-4d26-af0d-42e44657b429
62774520-3fdf-4cac-9dcc-9652f9c43faf	e1313494-ccb7-401a-b3e7-bf61b7134498	Review comment for Param 2	11.5000	\N	\N	f	2026-02-01 11:06:39.503076+00	a30a9865-926a-4d26-af0d-42e44657b429
da39b9e2-d79e-489d-a083-079208e0146f	5a925ea6-84c5-43a8-b9a7-3d4b6525dcdd	Review comment for Param 3	12.5000	\N	\N	f	2026-02-01 11:06:39.51826+00	a30a9865-926a-4d26-af0d-42e44657b429
edc30031-6929-4def-8738-e429a999d5b4	12f57026-ebce-4826-b0b4-5bbf08fb5533	Review comment for Param 4	13.5000	\N	\N	f	2026-02-01 11:06:39.532185+00	a30a9865-926a-4d26-af0d-42e44657b429
76a34f14-9a0d-4397-b8ba-248190e3444f	ca27b20a-72ce-42c7-ac72-7ecea4520adb	Review comment for Param 5	14.5000	\N	\N	t	2026-02-01 11:06:39.546114+00	a30a9865-926a-4d26-af0d-42e44657b429
5ffafea8-9b14-43d7-832e-ab13cfe328a6	261f7b25-f6f3-4254-8407-323f22ee5c91	Review comment for Param 6	15.5000	\N	\N	f	2026-02-01 11:06:39.560348+00	a30a9865-926a-4d26-af0d-42e44657b429
b44b9beb-dde6-4288-9da5-bdb9beb59f2c	7fb56f52-a3bd-4672-abc1-8b1258107e89	Review comment for Param 7	16.5000	\N	\N	f	2026-02-01 11:06:39.574723+00	a30a9865-926a-4d26-af0d-42e44657b429
0256863a-bf78-4d06-8ada-079e626c18c2	17db2bc0-d445-4e9c-b6c9-4a9388b69cc7	Review comment for Param 8	17.5000	\N	\N	f	2026-02-01 11:06:39.589041+00	a30a9865-926a-4d26-af0d-42e44657b429
ebb6a889-cbcd-4449-820b-ae5c50912257	9f1a4278-cc34-4e17-8c88-b877d9344837	Review comment for Param 9	18.5000	\N	\N	f	2026-02-01 11:06:39.603494+00	a30a9865-926a-4d26-af0d-42e44657b429
43febed2-cdb6-419d-96d9-9249b2254a23	f44ee6d0-15c5-4120-a1dd-1c2278a1bf06	Review comment for Param 10	19.5000	\N	\N	t	2026-02-01 11:06:39.618316+00	a30a9865-926a-4d26-af0d-42e44657b429
6eca65ff-ca09-4c20-b60e-6e5f41076cf9	52f455b3-4533-4de6-8f83-bc4a35d05235	\N	\N	\N	\N	t	2026-02-05 21:33:45.41739+00	1214c599-c7c2-490b-a895-e45b985b027b
45d21b6e-f376-4b18-b399-c986e48873b2	8e6424c6-87b3-465e-af94-e75acd69fa8f	\N	\N	\N	\N	t	2026-02-05 21:33:45.449032+00	1214c599-c7c2-490b-a895-e45b985b027b
53ecd258-8067-43bf-a134-3d65a74dfe9e	361fdfea-e93e-40bc-934b-12496ca8594a	\N	\N	\N	\N	t	2026-02-05 21:33:45.464765+00	1214c599-c7c2-490b-a895-e45b985b027b
c276c07f-ce99-44a2-a6c6-c683d733fa9f	85afc05f-c8bf-46f7-b07a-06871ce9e7a5	\N	\N	\N	\N	t	2026-02-05 21:34:41.426217+00	d9cd5b64-e423-4710-bcfe-73606bcca78c
72bb1faa-6ab5-40a1-b137-ecb0cdd5406d	d88eae4a-c324-4988-b490-da735720077b	\N	\N	\N	\N	t	2026-02-05 21:34:41.443644+00	d9cd5b64-e423-4710-bcfe-73606bcca78c
23b50fcc-ad9b-44e8-9a61-88d62d5bcb5a	d77cfa5f-4096-4dbe-99e7-29d5d836abfe	\N	\N	\N	\N	t	2026-02-05 21:34:41.460216+00	d9cd5b64-e423-4710-bcfe-73606bcca78c
e22d559d-4284-42ba-8bb2-d6269e289160	44721e2e-0b38-4701-bed6-60340ec2d23d	\N	\N	\N	\N	t	2026-02-05 21:36:32.848183+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
0eb5d3d8-61d9-4781-a850-4a11421bfa38	e8f97fc6-4316-43fc-be95-bd4996992d68	\N	\N	\N	\N	t	2026-02-05 21:36:32.863191+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
28f4bf90-b8a3-4002-8d6a-254cb96efc62	531b8d9f-9729-4892-b4fb-3a06c6f7cfb5	\N	\N	\N	\N	t	2026-02-05 21:36:32.877258+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
d307d537-363c-4cbe-b7e6-991cad5972a0	1a347840-f3a8-45e0-a944-f8ca5d0abcc5	\N	\N	\N	\N	t	2026-02-05 21:39:33.951051+00	fc5165e6-6519-496f-a3dd-1435bc308b5f
149b239d-5c3a-4a03-8089-9c1b6ca9539b	0bec0840-c841-4346-bc37-fd138bb47215	\N	\N	\N	\N	t	2026-02-05 21:39:33.980225+00	fc5165e6-6519-496f-a3dd-1435bc308b5f
833349ce-f09b-49d9-bb36-e25e2607d185	581539dc-7fe4-4269-887d-a375c2f63094	\N	\N	\N	\N	t	2026-02-05 21:39:34.002433+00	fc5165e6-6519-496f-a3dd-1435bc308b5f
a87dfedd-49e2-4023-82e6-a36c2c3b6645	12a35bbe-c5bf-4738-b237-34b4c400f3ad	\N	\N	\N	\N	t	2026-02-05 21:40:37.83331+00	d655e067-4edd-4516-b1b6-821c3c33cfc5
03c4595c-c340-4c6b-bcf8-16f3eacbbaf6	0e2e99e8-4c34-464c-b585-f58b41e44a5a	\N	\N	\N	\N	t	2026-02-05 21:40:37.849509+00	d655e067-4edd-4516-b1b6-821c3c33cfc5
a5ee8f8c-c60c-4c9a-ac35-4765c30ea966	6ca7b0fe-101b-4329-acfe-444b2cd0fb09	\N	\N	\N	\N	t	2026-02-05 21:40:37.866607+00	d655e067-4edd-4516-b1b6-821c3c33cfc5
188742a4-b4be-49da-b1ed-6443528bf28a	5ffd49aa-b156-4150-9f99-c8c559a825df	\N	\N	\N	\N	t	2026-02-05 21:41:47.548043+00	13ac055f-b943-4f6d-8182-babe636544df
68ae9a6b-6ca0-40af-ad06-771e1c121871	63475a69-4022-460e-913e-b1010153aa16	\N	\N	\N	\N	t	2026-02-05 21:41:47.565851+00	13ac055f-b943-4f6d-8182-babe636544df
86dc91e2-7433-435c-81cf-dc86d8cdd543	321b3a61-2abd-41c5-8d07-63797363bf05	\N	\N	\N	\N	t	2026-02-05 21:41:47.585026+00	13ac055f-b943-4f6d-8182-babe636544df
41102b50-de76-4908-ae57-e2f274bba9c1	6b66a4f6-9467-45f8-a141-afc4ebde9af6	\N	\N	\N	\N	t	2026-02-05 21:43:42.958297+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
9bb1014c-abb8-409c-9947-3c7fa0b05446	d25a0f04-f5d0-4e82-99da-1d420825e6cd	\N	\N	\N	\N	t	2026-02-05 21:43:42.975384+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
fe13968a-e3e2-4a36-b8bd-896a6435dfc8	7fa6b329-e3b3-45a3-9836-ad16d5e531d4	\N	\N	\N	\N	t	2026-02-05 21:43:42.98721+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
fbad197a-e5ee-423b-9b61-e4f51eee598c	852fd8fe-dad4-46f7-822e-65b495ad0706	\N	\N	\N	\N	t	2026-02-05 21:49:55.336268+00	ebc86578-b9a2-456f-b884-f964c1fb26f9
11e1c54a-0043-4dc4-b6fd-8772156f3ef8	18efabb8-fefc-4b0f-af53-7bc9b468a1ae	\N	\N	\N	\N	t	2026-02-05 21:49:55.35093+00	ebc86578-b9a2-456f-b884-f964c1fb26f9
b049b54d-b5bf-48ac-8a95-257b48aa7923	99cea9cf-4c31-46dc-a61f-ccde674b143e	\N	\N	\N	\N	t	2026-02-05 21:49:55.362646+00	ebc86578-b9a2-456f-b884-f964c1fb26f9
7d8149f1-4a7a-43f4-af63-923429ea1464	77ec08e6-4947-4b09-891e-6a331b4066c5	\N	\N	\N	\N	t	2026-02-05 21:52:19.206843+00	7eddd813-1060-42a3-aa36-abc2c6529e0f
89837bc2-2f1f-4b4b-8d10-5cbe97fe6a73	57d5eeaa-38f1-4fea-a5c5-1be1e9de786e	\N	\N	\N	\N	t	2026-02-05 21:52:19.225449+00	7eddd813-1060-42a3-aa36-abc2c6529e0f
f50b5cfa-2016-446c-b18f-4acaa7131e1c	6a8fc36e-bdc7-461c-bd08-b603a7c8275b	\N	\N	\N	\N	t	2026-02-05 21:52:19.239796+00	7eddd813-1060-42a3-aa36-abc2c6529e0f
cf04bfa9-854f-4abc-8efa-1ae26d0530a1	518c8fe9-bb22-4176-812c-d85f29781de8	\N	\N	\N	\N	t	2026-02-05 21:55:18.861418+00	021aea9d-7fe9-4488-ae61-eebf6d2af731
dead2abd-4e33-497e-8bb3-945e5028fe15	099983cf-9251-42f0-84b5-ace82a94ce56	\N	\N	\N	\N	t	2026-02-05 21:55:18.878882+00	021aea9d-7fe9-4488-ae61-eebf6d2af731
56f30bee-bff4-4a1c-8218-f46b54337813	35a32abf-12d3-4496-a93b-9e92573eb821	\N	\N	\N	\N	t	2026-02-05 21:55:18.894509+00	021aea9d-7fe9-4488-ae61-eebf6d2af731
607fb0cc-077d-4f4e-99c8-a940e1307c97	7f009411-b5a9-4c12-a50d-14b45a0e807a	\N	\N	\N	\N	t	2026-02-05 22:57:19.238007+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
1f2c2a86-5595-4419-aa0d-d9c57ddb118f	406dcd4d-bb23-4e57-9fbe-bd968fede31c	\N	\N	\N	\N	t	2026-02-05 22:57:20.648934+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
fdd2373b-951c-46f9-8509-0d67fd030cdf	b86166bd-d293-466b-b284-77ec39a38e62	\N	\N	\N	\N	t	2026-02-09 18:55:29.577703+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
a7258ab1-9f80-4e94-88c2-8201846b5475	765b9aa5-a291-4017-9357-f5bdc4f3443b	\N	\N	\N	\N	t	2026-02-11 09:20:09.204326+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
\.


--
-- Data for Name: audits; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audits (id, fsp_organization_id, farming_organization_id, work_order_id, crop_id, template_id, audit_number, name, status, template_snapshot, audit_date, created_at, updated_at, created_by, finalized_at, finalized_by, shared_at, sync_status, assigned_to_user_id, analyst_user_id, has_report) FROM stdin;
55e89250-15fc-4f9b-be3b-01337d242b3e	8b411c61-9885-4672-ba08-e45709934575	5ae66809-e7de-448a-8f42-920a192c8704	f58e5039-b46a-442c-9b84-314ac917fd9c	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	8ec8cff9-c42c-4c23-b8db-608759e6a85e	AUD-2026-0003	Audit - test	FINALIZED	{"code": "CODE0001", "version": 1, "sections": [{"code": "SEC_881A_0970", "parameters": [{"sort_order": 0, "is_required": false, "parameter_id": "f32bc43e-7842-4aff-97d0-c999804e2f44", "parameter_snapshot": {"code": "PRM_fa6d_0_1143", "options": [], "parameter_id": "f32bc43e-7842-4aff-97d0-c999804e2f44", "translations": {"en": {"name": "sadfsdfsdf", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-01-30T20:36:36.985704", "parameter_type": "DATE", "parameter_metadata": {}}}, {"sort_order": 1, "is_required": false, "parameter_id": "7ada24d6-b7ad-413d-893d-25e1271d9841", "parameter_snapshot": {"code": "PRM_fa6d_1_1243", "options": [], "parameter_id": "7ada24d6-b7ad-413d-893d-25e1271d9841", "translations": {"en": {"name": "Plant Height (cm)", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-01-30T20:36:36.987634", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": false, "parameter_id": "1d0cbbc3-1354-49d6-a16a-5ba0d6fd2f04", "parameter_snapshot": {"code": "PRM_fa6d_2_1310", "options": [{"code": "GREEN", "option_id": "059974e2-a761-487f-9e52-2629100b504a", "sort_order": 0, "translations": {"en": "Green"}}, {"code": "YELLOW", "option_id": "6d7cbc48-8d1a-4ba5-bf1d-fd8b794a404b", "sort_order": 1, "translations": {"en": "Yellow"}}, {"code": "BROWN", "option_id": "c643a809-e612-4807-9a90-0b29f0f9508c", "sort_order": 2, "translations": {"en": "Brown"}}], "parameter_id": "1d0cbbc3-1354-49d6-a16a-5ba0d6fd2f04", "translations": {"en": {"name": "Leaf Color", "help_text": null, "description": null}}, "option_set_id": "0345db82-bf99-4f32-b222-6ae0a7c07c00", "snapshot_date": "2026-01-30T20:36:36.989467", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}, {"sort_order": 3, "is_required": false, "parameter_id": "1b4c0c1b-7516-439a-af12-4e9735291848", "parameter_snapshot": {"code": "PRM_fa6d_3_1410", "options": [{"code": "YES", "option_id": "0c80853b-5a5b-4b87-8ba9-943fcf02bb3b", "sort_order": 0, "translations": {"en": "Yes"}}, {"code": "NO", "option_id": "af79f344-cacf-4679-9426-ff4f2507deb0", "sort_order": 1, "translations": {"en": "No"}}], "parameter_id": "1b4c0c1b-7516-439a-af12-4e9735291848", "translations": {"en": {"name": "Pest Presence", "help_text": null, "description": null}}, "option_set_id": "dfdd3646-a211-4edf-9458-3fd5dfdb7a76", "snapshot_date": "2026-01-30T20:36:36.995465", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}, {"sort_order": 4, "is_required": false, "parameter_id": "e5db1148-7a6f-4fae-80f5-e602f35e5cbd", "parameter_snapshot": {"code": "PRM_fa6d_4_1510", "options": [], "parameter_id": "e5db1148-7a6f-4fae-80f5-e602f35e5cbd", "translations": {"en": {"name": "Plant Height (cm)", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-01-30T20:36:36.999985", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 5, "is_required": false, "parameter_id": "69900480-cef3-4145-adc7-651cf4eb1c38", "parameter_snapshot": {"code": "PRM_fa6d_5_1576", "options": [{"code": "DRY", "option_id": "ceba3c16-431a-4ddd-b565-51a899129e34", "sort_order": 0, "translations": {"en": "Dry"}}, {"code": "MOIST", "option_id": "72bd150c-a989-42a6-8a19-7c0c46e21195", "sort_order": 1, "translations": {"en": "Moist"}}, {"code": "WET", "option_id": "bce6372f-fb3a-492a-986d-9c2a151d765b", "sort_order": 2, "translations": {"en": "Wet"}}], "parameter_id": "69900480-cef3-4145-adc7-651cf4eb1c38", "translations": {"en": {"name": "Soil Moisture Level", "help_text": null, "description": null}}, "option_set_id": "9a006dfc-05c1-48d7-a1d9-d0a6f6e2ccba", "snapshot_date": "2026-01-30T20:36:37.001888", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}], "section_id": "fa6dd296-6f04-4b0f-ad84-bc1947cf953d", "sort_order": 0, "translations": {"en": {"name": "sectpn 1", "description": ""}}}, {"code": "SEC_BE52_1676", "parameters": [], "section_id": "68deb228-aee8-4fff-8bb5-d285ac1f7d89", "sort_order": 1, "translations": {"en": {"name": "New Section", "description": ""}}}], "template_id": "8ec8cff9-c42c-4c23-b8db-608759e6a85e", "crop_type_id": null, "translations": {"en": {"name": "test", "description": "asdasdasdasdasdsad"}}, "snapshot_date": "2026-01-30T20:36:36.977576"}	2026-01-30	2026-01-30 20:36:36.949929+00	2026-02-05 23:02:00.211735+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-05 23:02:00.230787+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	pending_sync	\N	\N	t
71ea2a9e-9f30-42de-95ce-23492dde9081	8b411c61-9885-4672-ba08-e45709934575	1455677e-0753-44c1-959e-06c542a28884	\N	eb4f9b72-93cc-4ab0-b485-eaf889ce420e	3087bfd4-926c-450c-8ef1-bae06f734c4e	\N	Verification Audit 1769731857	DRAFT	\N	2026-01-30	2026-01-30 00:10:57.715119+00	2026-02-11 08:12:50.209909+00	08c368c7-0ea2-4dad-a5fe-5e8e180b0b44	\N	\N	\N	pending_sync	\N	\N	t
78983c2b-01c0-4c2e-8b46-c3773b1a8b6e	9463b7f0-b657-467c-bc0e-0f21817e623c	23f17148-f316-4fb6-8fd4-c4f2045ae401	\N	c17e06d6-19e8-4e6b-8882-55456eecd307	90041e86-a367-4409-91ff-a5f038af8dfd	AUD-2026-0004	Initial Audit	DRAFT	{"code": "TEMP_1769941969", "version": 1, "sections": [{"code": "SEC_1769941969", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "71826bac-4f3a-4e8e-b7d7-dcfdb27c2f62", "parameter_snapshot": {"code": "PH_1769941969", "options": [], "parameter_id": "71826bac-4f3a-4e8e-b7d7-dcfdb27c2f62", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:32:49.464397", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "c09aa38d-26fd-4cbb-af97-1aac41916ca5", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "90041e86-a367-4409-91ff-a5f038af8dfd", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T10:32:49.460642"}	2025-02-01	2026-02-01 10:32:49.448247+00	2026-02-01 10:32:49.448247+00	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c	\N	\N	\N	pending_sync	\N	\N	f
def41ef5-6c84-4840-b991-65f5ca1b95b7	1118a620-482f-4241-b722-35653792fda9	cc35b76b-375c-4261-8fa4-24b833a63cdb	\N	575e84c3-81b6-4926-afdf-108fff49c94a	6a95e0e1-6db5-47a8-87c4-d38238a26063	AUD-2026-0005	Initial Audit	DRAFT	{"code": "TEMP_1769941990", "version": 1, "sections": [{"code": "SEC_1769941990", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "7940e041-2bd8-4b4c-829b-5c080b601709", "parameter_snapshot": {"code": "PH_1769941990", "options": [], "parameter_id": "7940e041-2bd8-4b4c-829b-5c080b601709", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:33:10.190774", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "457af481-e0fc-4884-9141-9c2bb0828752", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "6a95e0e1-6db5-47a8-87c4-d38238a26063", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T10:33:10.187604"}	2025-02-01	2026-02-01 10:33:10.178091+00	2026-02-01 10:33:10.178091+00	bf660c8b-3818-4cf7-85f1-3071c0a7943c	\N	\N	\N	pending_sync	\N	\N	f
4ce704ad-c335-4c99-bc24-1a8a66877c08	cbbff567-e72f-46ff-ad79-4cf26c3260c8	13bd2caa-40a9-450f-9df0-7a7c110e49ac	\N	fd80c1fa-87e4-46ae-a9dc-77a1e648ebe1	54eb95ab-0a2b-45ab-9e4e-bf8bd03c976e	AUD-2026-0006	Initial Audit	DRAFT	{"code": "TEMP_1769942012", "version": 1, "sections": [{"code": "SEC_1769942012", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "940dd88b-e133-440b-af51-95365af25909", "parameter_snapshot": {"code": "PH_1769942012", "options": [], "parameter_id": "940dd88b-e133-440b-af51-95365af25909", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:33:32.206653", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "bec4a33a-c2f5-4bd5-b0b8-3662ff6a2239", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "54eb95ab-0a2b-45ab-9e4e-bf8bd03c976e", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T10:33:32.203914"}	2025-02-01	2026-02-01 10:33:32.196017+00	2026-02-01 10:33:32.196017+00	c7a092a7-d354-498d-b23a-d4802d99ccb4	\N	\N	\N	pending_sync	\N	\N	f
71fb6a9e-6f74-48cd-af01-fe4fcd86975b	6bf71e9a-2b50-4a27-9ff9-972b5a52eb8e	65e03c0d-7af5-4622-b2a2-8a867cf708a5	\N	ac7398b4-78f6-48c2-8b3b-b3c4583fa268	d9ef1e5d-1ac3-4999-9aef-770c72ff1875	AUD-2026-0007	Initial Audit	DRAFT	{"code": "TEMP_1769942044", "version": 1, "sections": [{"code": "SEC_1769942044", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "10f12a98-15d3-446f-90b0-5e5e353c3809", "parameter_snapshot": {"code": "PH_1769942044", "options": [], "parameter_id": "10f12a98-15d3-446f-90b0-5e5e353c3809", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:34:04.605436", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "3e3b1f73-e82a-4dfd-bb7f-b3a902093c4f", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "d9ef1e5d-1ac3-4999-9aef-770c72ff1875", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T10:34:04.602223"}	2025-02-01	2026-02-01 10:34:04.593909+00	2026-02-01 10:34:04.593909+00	2199f334-fccd-46ff-b45c-2cd81aadeca2	\N	\N	\N	pending_sync	\N	\N	f
4bfdee24-2fd6-45c7-80fd-4a7513ca3037	c4a4f415-3907-463e-86e0-2d7148e90d28	aa001d98-fda0-4f0f-971e-361f1af462ad	\N	af65b918-c058-4eda-81df-72063572aaec	669fbf0b-9a3b-4630-89ce-2310a74dcc8c	AUD-2026-0014	Initial Audit	SHARED	{"code": "TEMP_1769942293", "version": 1, "sections": [{"code": "SEC_1769942293", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "fca6b05f-39da-4323-a92d-d2fc7eceabff", "parameter_snapshot": {"code": "PH_1769942293", "options": [], "parameter_id": "fca6b05f-39da-4323-a92d-d2fc7eceabff", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:38:13.507489", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "5099dbd1-f710-4e0f-9175-0fd2ad1333ca", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "669fbf0b-9a3b-4630-89ce-2310a74dcc8c", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T10:38:13.505261"}	2025-02-01	2026-02-01 10:38:13.497221+00	2026-02-01 10:38:13.601149+00	1ce1ba48-b899-4217-8fd9-2124dd4765c6	\N	\N	\N	pending_sync	\N	\N	f
a4ba5400-35ae-4cc6-880b-9aac13cceddd	461445ad-b03d-418c-8049-49cbadf6519b	c883192d-5000-4f2a-882c-3e8d3d49d4f6	\N	08707817-10ee-472b-99a8-5e6365f756e7	ee720a1c-e1ee-442c-9e19-0d3338bef64a	AUD-2026-0008	Initial Audit	SUBMITTED	{"code": "TEMP_1769942062", "version": 1, "sections": [{"code": "SEC_1769942062", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "1ad2e581-5dce-41ce-af2a-8e832ebbcc54", "parameter_snapshot": {"code": "PH_1769942062", "options": [], "parameter_id": "1ad2e581-5dce-41ce-af2a-8e832ebbcc54", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:34:22.154906", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "8abedb5c-b0bf-46e1-97b5-d970f77f4866", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "ee720a1c-e1ee-442c-9e19-0d3338bef64a", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T10:34:22.152138"}	2025-02-01	2026-02-01 10:34:22.144221+00	2026-02-01 10:34:22.205998+00	b46ab366-7dcb-4ee5-a558-dc328db04159	\N	\N	\N	pending_sync	\N	\N	f
a4723a72-f91c-4f12-a268-8809d0da3d7f	c6957a10-58cf-4f2d-ab85-b8b0dbd6ed7c	bc9ba376-ec2d-4293-a39d-22daa59a0236	\N	2faf16a9-07f4-42d5-b177-52c9315b2a68	c5bbdecb-6b9f-4f1c-b5ab-7693309dd40e	AUD-2026-0009	Initial Audit	REVIEWED	{"code": "TEMP_1769942082", "version": 1, "sections": [{"code": "SEC_1769942082", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "4ec21239-4ac2-46b7-bd9b-d1c065591f62", "parameter_snapshot": {"code": "PH_1769942082", "options": [], "parameter_id": "4ec21239-4ac2-46b7-bd9b-d1c065591f62", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:34:42.738227", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "0cd7b48c-642c-420e-b12f-87a256c5b99c", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "c5bbdecb-6b9f-4f1c-b5ab-7693309dd40e", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T10:34:42.735413"}	2025-02-01	2026-02-01 10:34:42.72706+00	2026-02-01 10:34:42.828128+00	979cfcfd-a872-40df-8380-dbe81f29e7a5	\N	\N	\N	pending_sync	\N	\N	f
20095d3d-e585-4320-b1f8-cfcc30752b5f	36acd251-59ee-4f22-a3e3-f14e91a16706	bf66b4c8-e589-4240-9949-928683f45020	\N	5ffd8d1f-7101-4a4a-bf41-a1b4b32cadf4	abf126ce-5adc-48b2-ac79-604d3ea7f052	AUD-2026-0010	Initial Audit	FINALIZED	{"code": "TEMP_1769942107", "version": 1, "sections": [{"code": "SEC_1769942107", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "ebfb0b55-7017-496c-9e98-d0d55159a831", "parameter_snapshot": {"code": "PH_1769942107", "options": [], "parameter_id": "ebfb0b55-7017-496c-9e98-d0d55159a831", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:35:08.076989", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "24580d64-53bb-4727-b455-19e1271f5d54", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "abf126ce-5adc-48b2-ac79-604d3ea7f052", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T10:35:08.073884"}	2025-02-01	2026-02-01 10:35:08.065114+00	2026-02-01 10:35:08.177077+00	810cc398-af79-4d96-9eee-af0f1bbf8683	\N	\N	\N	pending_sync	\N	\N	f
79739771-770e-44a9-ab0b-b347e6ebe770	ba0154e3-56bb-4d8d-9db9-b143367cbc85	ea925230-a27d-4bf3-9187-877dab140c8b	\N	479e4492-6844-401f-90f9-716668c94aa1	a11b8083-cfb6-4ed5-bc09-2066a41ae2c9	AUD-2026-0011	Initial Audit	FINALIZED	{"code": "TEMP_1769942148", "version": 1, "sections": [{"code": "SEC_1769942148", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "7325f2cc-97ed-4dcc-a191-1ea0c56e04bd", "parameter_snapshot": {"code": "PH_1769942148", "options": [], "parameter_id": "7325f2cc-97ed-4dcc-a191-1ea0c56e04bd", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:35:48.278003", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "1bb7d226-89f2-4474-b39c-fc2fa66a1f03", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "a11b8083-cfb6-4ed5-bc09-2066a41ae2c9", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T10:35:48.275041"}	2025-02-01	2026-02-01 10:35:48.266528+00	2026-02-01 10:35:48.37547+00	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	\N	\N	\N	pending_sync	\N	\N	f
d90be630-cd0b-401d-99f2-9ae0ba0066e7	eb79439d-c6df-4d41-8c3d-0619964d91e1	5d712ef0-dfcc-4e49-ba75-0d15424f0409	\N	31faaa66-c5a6-49a6-8000-e03aecd71319	889fabe6-54ee-44f0-85d8-0ef1ca3868b5	AUD-2026-0012	Initial Audit	SHARED	{"code": "TEMP_1769942204", "version": 1, "sections": [{"code": "SEC_1769942204", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "e68e3073-4957-4a89-80e3-f27e8136bf3b", "parameter_snapshot": {"code": "PH_1769942204", "options": [], "parameter_id": "e68e3073-4957-4a89-80e3-f27e8136bf3b", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:36:44.211561", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "a5665aaf-aa67-437c-b997-4e7a7f655db4", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "889fabe6-54ee-44f0-85d8-0ef1ca3868b5", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T10:36:44.206844"}	2025-02-01	2026-02-01 10:36:44.191133+00	2026-02-01 10:36:44.365247+00	ef5984b4-54b6-47cf-a9bb-ca02cadc0180	\N	\N	\N	pending_sync	\N	\N	f
0cfc963d-fe8b-4ca3-b720-49ab3696623a	d1a8266c-b125-4c57-b1d9-69f785e7e7ec	e69d30db-071e-4079-9a43-3267a66927a9	\N	c25d7a3f-cb3b-484d-9cd4-0399615ff566	9e290045-8193-4647-86bd-eb2ffb3b9cbf	AUD-2026-0013	Initial Audit	SHARED	{"code": "TEMP_1769942225", "version": 1, "sections": [{"code": "SEC_1769942225", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "314226b3-58f0-40c3-8a79-a040f41f3867", "parameter_snapshot": {"code": "PH_1769942225", "options": [], "parameter_id": "314226b3-58f0-40c3-8a79-a040f41f3867", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:37:05.333402", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "1f3556bc-f866-4104-99a3-b16d256cf44c", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "9e290045-8193-4647-86bd-eb2ffb3b9cbf", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T10:37:05.329851"}	2025-02-01	2026-02-01 10:37:05.32135+00	2026-02-01 10:37:05.445162+00	70904796-fe39-4007-b892-a8aa3c8e0e8f	\N	\N	\N	pending_sync	\N	\N	f
41acc9c4-1f08-40f1-90cf-e85c80e17de2	ab3df532-1696-45db-a97f-ebd3afaee92c	62656d65-00b9-4446-b11a-586d60d38c8c	\N	8d2c89ad-a3b1-479f-b186-c467627b20fd	5036a6fb-a067-42ac-800d-ba2f503b50a4	AUD-2026-0015	Initial Audit	SHARED	{"code": "TEMP_1769942339", "version": 1, "sections": [{"code": "SEC_1769942339", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "710a7d66-5394-4c0a-af26-5dc0512fae77", "parameter_snapshot": {"code": "PH_1769942339", "options": [], "parameter_id": "710a7d66-5394-4c0a-af26-5dc0512fae77", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:38:59.369720", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "fd36c2ac-bcfd-4aae-ad65-1e7780e7b697", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "5036a6fb-a067-42ac-800d-ba2f503b50a4", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T10:38:59.365048"}	2025-02-01	2026-02-01 10:38:59.350506+00	2026-02-01 10:38:59.514904+00	05e362b8-0b73-44ed-bded-ef4e0a40dd47	\N	\N	\N	pending_sync	\N	\N	f
34c22a9d-d7da-44d5-a18c-d9f706b11299	c0fbcba5-fca1-4960-88fb-5a5aeb9684e3	f4b08735-4038-49dd-bed2-4cb44e9c9287	\N	aa2294ec-75a5-41d8-8140-152503c6db23	4fde31a6-7e88-4856-bb4b-7a8159162cca	AUD-2026-0016	Initial Audit	SHARED	{"code": "TEMP_1769943699", "version": 1, "sections": [{"code": "SEC_1769943699", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "e9799730-1c13-4c5f-b9ed-2a7fd9c1538e", "parameter_snapshot": {"code": "PH_1769943699", "options": [], "parameter_id": "e9799730-1c13-4c5f-b9ed-2a7fd9c1538e", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:01:39.812601", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}}], "section_id": "4da68809-e9cb-498a-b97c-1c0a5d0ca109", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "4fde31a6-7e88-4856-bb4b-7a8159162cca", "crop_type_id": null, "translations": {"en": {"name": "Audit Template", "description": "Test"}}, "snapshot_date": "2026-02-01T11:01:39.809994"}	2025-02-01	2026-02-01 11:01:39.802424+00	2026-02-01 11:01:39.924129+00	b9c25548-e5ba-4200-9dc9-1ba98f332540	\N	\N	\N	pending_sync	\N	\N	f
6ec94163-4bb8-4b65-85e9-dd4a37678d8e	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	2ec2a2b1-87f2-4962-8649-c029973d9504	\N	54c34b1f-298c-47c7-a82a-a2253b679c08	d4273ff7-eeba-4465-8e77-ddc8bc83d30c	AUD-2026-0017	Initial Audit	SHARED	{"code": "TEMP_1769943999", "version": 1, "sections": [{"code": "SEC_1769943998", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "eefe2319-3eb6-43bb-9d78-7c734561b947", "parameter_snapshot": {"code": "P1_1769943998", "options": [], "parameter_id": "eefe2319-3eb6-43bb-9d78-7c734561b947", "translations": {"en": {"name": "Param 1", "help_text": null, "description": "Measure 1"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.253834", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}}, {"sort_order": 2, "is_required": true, "parameter_id": "5684267d-6f41-454e-8429-2f094efe38b9", "parameter_snapshot": {"code": "P2_1769943998", "options": [], "parameter_id": "5684267d-6f41-454e-8429-2f094efe38b9", "translations": {"en": {"name": "Param 2", "help_text": null, "description": "Measure 2"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.255227", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}}, {"sort_order": 3, "is_required": true, "parameter_id": "b2d71394-a99d-4ff6-a333-4d8ebf1c1ec4", "parameter_snapshot": {"code": "P3_1769943998", "options": [], "parameter_id": "b2d71394-a99d-4ff6-a333-4d8ebf1c1ec4", "translations": {"en": {"name": "Param 3", "help_text": null, "description": "Measure 3"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.256535", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}}, {"sort_order": 4, "is_required": true, "parameter_id": "7e469f84-0b9d-4f70-b737-ce0444148245", "parameter_snapshot": {"code": "P4_1769943998", "options": [], "parameter_id": "7e469f84-0b9d-4f70-b737-ce0444148245", "translations": {"en": {"name": "Param 4", "help_text": null, "description": "Measure 4"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.257800", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}}, {"sort_order": 5, "is_required": true, "parameter_id": "46640045-7bdf-48eb-af82-61a3fc7c2d4a", "parameter_snapshot": {"code": "P5_1769943999", "options": [], "parameter_id": "46640045-7bdf-48eb-af82-61a3fc7c2d4a", "translations": {"en": {"name": "Param 5", "help_text": null, "description": "Measure 5"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.259172", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}}, {"sort_order": 6, "is_required": true, "parameter_id": "f517e506-6c88-4cfb-8426-ae5f1d516154", "parameter_snapshot": {"code": "P6_1769943999", "options": [], "parameter_id": "f517e506-6c88-4cfb-8426-ae5f1d516154", "translations": {"en": {"name": "Param 6", "help_text": null, "description": "Measure 6"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.260450", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}}, {"sort_order": 7, "is_required": true, "parameter_id": "89151732-fc61-4617-a477-17685bbee9da", "parameter_snapshot": {"code": "P7_1769943999", "options": [], "parameter_id": "89151732-fc61-4617-a477-17685bbee9da", "translations": {"en": {"name": "Param 7", "help_text": null, "description": "Measure 7"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.262134", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}}, {"sort_order": 8, "is_required": true, "parameter_id": "8bea7626-d387-455c-aa0b-2436f2824e78", "parameter_snapshot": {"code": "P8_1769943999", "options": [], "parameter_id": "8bea7626-d387-455c-aa0b-2436f2824e78", "translations": {"en": {"name": "Param 8", "help_text": null, "description": "Measure 8"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.263447", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}}, {"sort_order": 9, "is_required": true, "parameter_id": "d7147d11-034b-4c26-8c23-6921d316d28a", "parameter_snapshot": {"code": "P9_1769943999", "options": [], "parameter_id": "d7147d11-034b-4c26-8c23-6921d316d28a", "translations": {"en": {"name": "Param 9", "help_text": null, "description": "Measure 9"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.264831", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}}, {"sort_order": 10, "is_required": true, "parameter_id": "9f963e85-c94c-4dec-b2aa-b0e745431c39", "parameter_snapshot": {"code": "P10_1769943999", "options": [], "parameter_id": "9f963e85-c94c-4dec-b2aa-b0e745431c39", "translations": {"en": {"name": "Param 10", "help_text": null, "description": "Measure 10"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.266145", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}}], "section_id": "0588aa5f-54d5-4544-a0b6-9535a4787776", "sort_order": 1, "translations": {"en": {"name": "Test Section", "description": "Desc"}}}], "template_id": "d4273ff7-eeba-4465-8e77-ddc8bc83d30c", "crop_type_id": null, "translations": {"en": {"name": "10 Param Template", "description": "Test"}}, "snapshot_date": "2026-02-01T11:06:39.249841"}	2025-02-01	2026-02-01 11:06:39.239746+00	2026-02-01 11:06:39.69736+00	a30a9865-926a-4d26-af0d-42e44657b429	\N	\N	\N	pending_sync	\N	\N	f
8864a618-4dcc-47b9-901f-9859b539c579	27227759-8c29-4ba3-8ba5-153607db5c4c	675f5900-0a12-48ea-a2a9-c121508fc23e	\N	00ac9d42-2f56-4064-898a-1643ffe6c5c4	92b3bb28-b5d7-4c2c-b70d-0d078921f12f	AUD-2026-0018	Final Test Audit	DRAFT	{"code": "T_1770327102", "version": 1, "sections": [{"code": "S1_1770327102", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "78a8d90e-d189-4e0c-9815-618f465f4195", "parameter_snapshot": {"code": "P1_1770327102", "options": [], "parameter_id": "78a8d90e-d189-4e0c-9815-618f465f4195", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:31:42.854016", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": true, "parameter_id": "f01ac19f-b2ff-4bc9-b16a-5edb10315b41", "parameter_snapshot": {"code": "P2_1770327102", "options": [], "parameter_id": "f01ac19f-b2ff-4bc9-b16a-5edb10315b41", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:31:42.854863", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 3, "is_required": true, "parameter_id": "5e0e278c-ed24-4ae6-b259-8a430b6ff804", "parameter_snapshot": {"code": "P3_1770327102", "options": [{"code": "opt1", "option_id": "b7c70d96-0f02-48ae-972d-b003cbfc3b89", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "4126b50a-880e-44a6-b28a-985081f32d4c", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "5e0e278c-ed24-4ae6-b259-8a430b6ff804", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "7d1bfc37-3b1b-4421-a3f9-104690c6e487", "snapshot_date": "2026-02-05T21:31:42.855595", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}], "section_id": "bc41c3da-9a29-4ce5-834f-52fd21432ba8", "sort_order": 1, "translations": {"en": {"name": "Section 1", "description": null}}}], "template_id": "92b3bb28-b5d7-4c2c-b70d-0d078921f12f", "crop_type_id": null, "translations": {"en": {"name": "Report Test", "description": null}}, "snapshot_date": "2026-02-05T21:31:42.849306"}	2026-02-05	2026-02-05 21:31:42.814584+00	2026-02-05 21:31:42.814584+00	53126f3a-94da-4363-b20d-61a85c99574a	\N	\N	\N	pending_sync	\N	\N	f
9b38d720-a2fa-4be2-a767-c01a2deb5386	bc651c65-73d1-41c9-a03a-275b47df7b10	92a020f4-c327-4f4d-8df3-c7ed0d120871	\N	03779288-b39e-419b-9579-cf6db53132e4	b33df655-1719-43dd-b133-95dbf63a5372	AUD-2026-0019	Final Test Audit	DRAFT	{"code": "T_1770327224", "version": 1, "sections": [{"code": "S1_1770327224", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "467998d6-634b-40aa-8eb8-728fab704ba7", "parameter_snapshot": {"code": "P1_1770327224", "options": [], "parameter_id": "467998d6-634b-40aa-8eb8-728fab704ba7", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:33:45.334500", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": true, "parameter_id": "82c060ef-fec1-4d82-9e63-44b301715425", "parameter_snapshot": {"code": "P2_1770327224", "options": [], "parameter_id": "82c060ef-fec1-4d82-9e63-44b301715425", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:33:45.335565", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 3, "is_required": true, "parameter_id": "28230270-0fcf-4662-8c5b-8bb0ad5c57b3", "parameter_snapshot": {"code": "P3_1770327224", "options": [{"code": "opt1", "option_id": "68b94446-68e1-4ec5-8b41-cc9842033394", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "1c17baf7-b36c-464e-9a73-3e829cc103db", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "28230270-0fcf-4662-8c5b-8bb0ad5c57b3", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "b409cb79-5f90-4322-b935-5c13fe396f9c", "snapshot_date": "2026-02-05T21:33:45.336539", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}], "section_id": "a300e7fd-5eb0-48a3-ba12-00b16750b2d0", "sort_order": 1, "translations": {"en": {"name": "Section 1", "description": null}}}], "template_id": "b33df655-1719-43dd-b133-95dbf63a5372", "crop_type_id": null, "translations": {"en": {"name": "Report Test", "description": null}}, "snapshot_date": "2026-02-05T21:33:45.332238"}	2026-02-05	2026-02-05 21:33:45.323923+00	2026-02-05 21:33:45.323923+00	1214c599-c7c2-490b-a895-e45b985b027b	\N	\N	\N	pending_sync	\N	\N	f
873f22dc-071a-4f69-8a95-5a98759a6741	0a61f5ac-582c-4856-8072-27fcad588698	96ce9467-4d9c-42ac-8fd7-6b4980cb4662	\N	da16da3c-4ccd-4bc4-94cb-ee93c45a3b26	9bba228a-4cf1-4d30-b630-3cc2ca29a4ec	AUD-2026-0020	Final Test Audit	DRAFT	{"code": "T_1770327280", "version": 1, "sections": [{"code": "S1_1770327280", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "e016e813-99bf-46ae-93e0-43fcc999ecff", "parameter_snapshot": {"code": "P1_1770327280", "options": [], "parameter_id": "e016e813-99bf-46ae-93e0-43fcc999ecff", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:34:41.335110", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": true, "parameter_id": "0124f9d8-df14-40e1-a628-2fb28cfcd89b", "parameter_snapshot": {"code": "P2_1770327280", "options": [], "parameter_id": "0124f9d8-df14-40e1-a628-2fb28cfcd89b", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:34:41.336502", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 3, "is_required": true, "parameter_id": "5b9d413c-0d24-4b1c-bee8-2a800c357b62", "parameter_snapshot": {"code": "P3_1770327280", "options": [{"code": "opt1", "option_id": "ee25c5c6-aadd-4c6a-ab13-3070b40ddf05", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "ab2b8972-8292-4e21-a8f6-66d8bf133921", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "5b9d413c-0d24-4b1c-bee8-2a800c357b62", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "a9bf577e-4d74-495e-b9d9-c1677621be45", "snapshot_date": "2026-02-05T21:34:41.337907", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}], "section_id": "7957ddf4-2552-4349-92a5-eaa1cc60769e", "sort_order": 1, "translations": {"en": {"name": "Section 1", "description": null}}}], "template_id": "9bba228a-4cf1-4d30-b630-3cc2ca29a4ec", "crop_type_id": null, "translations": {"en": {"name": "Report Test", "description": null}}, "snapshot_date": "2026-02-05T21:34:41.331736"}	2026-02-05	2026-02-05 21:34:41.3216+00	2026-02-05 21:34:41.3216+00	d9cd5b64-e423-4710-bcfe-73606bcca78c	\N	\N	\N	pending_sync	\N	\N	f
ce3ea838-c6df-42ce-a9bf-06856078f13b	88810bde-bf96-43e8-9791-937cd4a7e062	2328d476-0c17-4452-adc8-7cf00f24669b	\N	4fd6402f-2f98-4485-9544-7e77ab3549ae	d54eebdb-8fdc-408d-bee3-546f4ba63edd	AUD-2026-0021	Final Test Audit	DRAFT	{"code": "T_1770327392", "version": 1, "sections": [{"code": "S1_1770327392", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "baa7fe1d-099f-49de-9531-dcad3694b914", "parameter_snapshot": {"code": "P1_1770327392", "options": [], "parameter_id": "baa7fe1d-099f-49de-9531-dcad3694b914", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:36:32.777288", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": true, "parameter_id": "56a72950-a19d-481b-a0db-3aa0940d1b7a", "parameter_snapshot": {"code": "P2_1770327392", "options": [], "parameter_id": "56a72950-a19d-481b-a0db-3aa0940d1b7a", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:36:32.778245", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 3, "is_required": true, "parameter_id": "6699f225-e68a-4e39-a43f-a6202cda40d5", "parameter_snapshot": {"code": "P3_1770327392", "options": [{"code": "opt1", "option_id": "c2b584fc-e308-4562-ba68-3bdc7c1f8ecc", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "afb0f1b3-8447-4a23-a961-cf6affd8bfa0", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "6699f225-e68a-4e39-a43f-a6202cda40d5", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "cdc29b9f-35fb-4abb-a9a6-21272b56173a", "snapshot_date": "2026-02-05T21:36:32.779053", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}], "section_id": "26d6feb1-d647-4e02-a01f-af767914367f", "sort_order": 1, "translations": {"en": {"name": "Section 1", "description": null}}}], "template_id": "d54eebdb-8fdc-408d-bee3-546f4ba63edd", "crop_type_id": null, "translations": {"en": {"name": "Report Test", "description": null}}, "snapshot_date": "2026-02-05T21:36:32.774800"}	2026-02-05	2026-02-05 21:36:32.767626+00	2026-02-05 21:36:32.767626+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	\N	\N	\N	pending_sync	\N	\N	f
b20782d9-2f2c-4504-bc61-f9ae81b84037	5e03962b-3b0c-4bd5-9f17-6349e82083cb	9e0c3eda-2c52-4792-abd4-288131229066	\N	db79839b-599c-463d-ba0d-c1953ae6861d	1eb8bc24-4288-4979-8d7f-7ce480afc939	AUD-2026-0022	Final Test Audit	DRAFT	{"code": "T_1770327572", "version": 1, "sections": [{"code": "S1_1770327572", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "90ac4202-513e-4e0e-9de6-a32262857ed3", "parameter_snapshot": {"code": "P1_1770327572", "options": [], "parameter_id": "90ac4202-513e-4e0e-9de6-a32262857ed3", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:39:33.841104", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": true, "parameter_id": "4a1add6d-2be5-4eb4-93d2-51ebbf5e1672", "parameter_snapshot": {"code": "P2_1770327572", "options": [], "parameter_id": "4a1add6d-2be5-4eb4-93d2-51ebbf5e1672", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:39:33.842554", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 3, "is_required": true, "parameter_id": "689e5a3e-cc7a-4148-b408-f92ec941b37e", "parameter_snapshot": {"code": "P3_1770327572", "options": [{"code": "opt1", "option_id": "6baefc9c-88e8-4aa1-a021-8cae81a905ed", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "44c9d328-fc27-4a2c-9a01-9167b8f9c84f", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "689e5a3e-cc7a-4148-b408-f92ec941b37e", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "b0fe6edb-193c-4e20-a6f4-5cbaaf817536", "snapshot_date": "2026-02-05T21:39:33.843942", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}], "section_id": "d00e94a1-caa9-48f3-9db3-e4bac9b4c096", "sort_order": 1, "translations": {"en": {"name": "Section 1", "description": null}}}], "template_id": "1eb8bc24-4288-4979-8d7f-7ce480afc939", "crop_type_id": null, "translations": {"en": {"name": "Report Test", "description": null}}, "snapshot_date": "2026-02-05T21:39:33.837391"}	2026-02-05	2026-02-05 21:39:33.826868+00	2026-02-05 21:39:33.826868+00	fc5165e6-6519-496f-a3dd-1435bc308b5f	\N	\N	\N	pending_sync	\N	\N	f
c2366bab-e199-490f-aab5-d78f72bd6150	8bb34a8d-f5bb-41cf-ba29-87e5c652c03f	c5992875-1ecb-42f0-b461-e177f1775d46	\N	c4252796-b498-4307-9312-e1e69858946e	160ff178-2184-4618-ab2b-62adc37483a0	AUD-2026-0023	Final Test Audit	DRAFT	{"code": "T_1770327636", "version": 1, "sections": [{"code": "S1_1770327636", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "c863d9ae-337e-4ea5-a846-3b9a8bd04020", "parameter_snapshot": {"code": "P1_1770327636", "options": [], "parameter_id": "c863d9ae-337e-4ea5-a846-3b9a8bd04020", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:40:37.730220", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": true, "parameter_id": "a74d7503-f495-4a7b-942d-2e6d64aab25f", "parameter_snapshot": {"code": "P2_1770327636", "options": [], "parameter_id": "a74d7503-f495-4a7b-942d-2e6d64aab25f", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:40:37.731776", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 3, "is_required": true, "parameter_id": "7acb91dd-9a2b-482c-9fc6-2eefb815aeb3", "parameter_snapshot": {"code": "P3_1770327636", "options": [{"code": "opt1", "option_id": "cc1a045b-0ce5-4c07-afed-eca7a4d7896f", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "6f01b763-30d8-414c-9af9-bf605ac00ae7", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "7acb91dd-9a2b-482c-9fc6-2eefb815aeb3", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "ba3f1425-1907-48fc-a9f4-7ee1a85c0b90", "snapshot_date": "2026-02-05T21:40:37.733396", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}], "section_id": "900f4f8d-8d2a-465a-84c8-8659ce9eb7b9", "sort_order": 1, "translations": {"en": {"name": "Section 1", "description": null}}}], "template_id": "160ff178-2184-4618-ab2b-62adc37483a0", "crop_type_id": null, "translations": {"en": {"name": "Report Test", "description": null}}, "snapshot_date": "2026-02-05T21:40:37.726170"}	2026-02-05	2026-02-05 21:40:37.714777+00	2026-02-05 21:40:37.714777+00	d655e067-4edd-4516-b1b6-821c3c33cfc5	\N	\N	\N	pending_sync	\N	\N	f
114aecdb-ebf1-4077-94ab-ff9e56ec3791	f3200c57-c6b8-4f2d-80fe-24b9a6359f6c	f878c129-1bbb-4dca-bcfc-d21ea54fb41f	\N	efb39005-5e09-4d9f-9d37-1bbd405ea5eb	94741211-61de-44fe-b564-1984e1620f66	AUD-2026-0024	Final Test Audit	DRAFT	{"code": "T_1770327706", "version": 1, "sections": [{"code": "S1_1770327706", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "76452429-682f-4ba0-917e-bb4b9ffd349f", "parameter_snapshot": {"code": "P1_1770327706", "options": [], "parameter_id": "76452429-682f-4ba0-917e-bb4b9ffd349f", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:41:47.455525", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": true, "parameter_id": "e46db86a-72f6-4606-8eb2-560b6b3ec315", "parameter_snapshot": {"code": "P2_1770327706", "options": [], "parameter_id": "e46db86a-72f6-4606-8eb2-560b6b3ec315", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:41:47.457296", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 3, "is_required": true, "parameter_id": "222948be-c818-4310-bf8d-fef35d5d979c", "parameter_snapshot": {"code": "P3_1770327706", "options": [{"code": "opt1", "option_id": "8337ba01-c7bc-4553-86d0-672c65399b38", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "5811ced6-2e79-4c9e-b7a1-f48134203521", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "222948be-c818-4310-bf8d-fef35d5d979c", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "e67b95a8-8819-4939-9557-bd2d5379e96c", "snapshot_date": "2026-02-05T21:41:47.458759", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}], "section_id": "45d63ea1-0e12-4bf3-b620-12d572fba1cd", "sort_order": 1, "translations": {"en": {"name": "Section 1", "description": null}}}], "template_id": "94741211-61de-44fe-b564-1984e1620f66", "crop_type_id": null, "translations": {"en": {"name": "Report Test", "description": null}}, "snapshot_date": "2026-02-05T21:41:47.452367"}	2026-02-05	2026-02-05 21:41:47.441165+00	2026-02-05 21:41:47.441165+00	13ac055f-b943-4f6d-8182-babe636544df	\N	\N	\N	pending_sync	\N	\N	f
4617c18f-c346-432a-bd36-25804c526fd1	f7028cb1-7e87-4fd7-8aa1-4ea8b97ccb43	1d66de05-6ab3-461b-94d0-0750153aa2d9	\N	0c6d3034-08a1-4e76-8e84-719585abf527	fd9c6a36-14ed-4e6b-8dc0-60b324fc0caf	AUD-2026-0025	Final Test Audit	REVIEWED	{"code": "T_1770327821", "version": 1, "sections": [{"code": "S1_1770327821", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "b664898c-45cf-4723-8fff-b74c1232898f", "parameter_snapshot": {"code": "P1_1770327821", "options": [], "parameter_id": "b664898c-45cf-4723-8fff-b74c1232898f", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:43:42.874006", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": true, "parameter_id": "9700c6e5-2190-443e-83b2-5183b59625e2", "parameter_snapshot": {"code": "P2_1770327821", "options": [], "parameter_id": "9700c6e5-2190-443e-83b2-5183b59625e2", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:43:42.874882", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 3, "is_required": true, "parameter_id": "78f901de-8e0c-42a6-ba39-94adadbe3193", "parameter_snapshot": {"code": "P3_1770327821", "options": [{"code": "opt1", "option_id": "3f3b03fa-ef0e-42fe-9546-c33af35d1681", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "a77d9560-5597-493c-a16d-99af12c82df6", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "78f901de-8e0c-42a6-ba39-94adadbe3193", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "53a4bc06-e667-4f37-b16e-9aa98563aa2f", "snapshot_date": "2026-02-05T21:43:42.876003", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}], "section_id": "813222ab-33b9-4937-a23c-bf6059a12713", "sort_order": 1, "translations": {"en": {"name": "Section 1", "description": null}}}], "template_id": "fd9c6a36-14ed-4e6b-8dc0-60b324fc0caf", "crop_type_id": null, "translations": {"en": {"name": "Report Test", "description": null}}, "snapshot_date": "2026-02-05T21:43:42.870407"}	2026-02-05	2026-02-05 21:43:42.856334+00	2026-02-05 21:43:43.028138+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	\N	\N	\N	pending_sync	\N	\N	f
8c0183d7-2bbf-4354-a646-2e60339b3ff6	e33b94b6-cfc5-4d7e-98a4-2259867e45b4	8229af4d-838a-4d32-ac0b-9eadffbbcff8	\N	23cc371e-1fbd-47f4-a44f-8f9894a61d73	6a8b1f80-60c2-497b-94e7-62540c020943	AUD-2026-0026	Final Test Audit	FINALIZED	{"code": "T_1770328194", "version": 1, "sections": [{"code": "S1_1770328194", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "21f3a466-ed7c-4630-8715-9dbeca7fb00f", "parameter_snapshot": {"code": "P1_1770328194", "options": [], "parameter_id": "21f3a466-ed7c-4630-8715-9dbeca7fb00f", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:49:55.253368", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": true, "parameter_id": "2ad12225-e5db-458e-9a8a-7d3ff1051d4c", "parameter_snapshot": {"code": "P2_1770328194", "options": [], "parameter_id": "2ad12225-e5db-458e-9a8a-7d3ff1051d4c", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:49:55.254260", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 3, "is_required": true, "parameter_id": "fc1d516b-4410-42df-8d1a-2420b8d0927b", "parameter_snapshot": {"code": "P3_1770328194", "options": [{"code": "opt1", "option_id": "2c2e893a-cd32-4855-b766-681bb293adb7", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "3384b3d2-89b2-45f7-82a2-28e23fa1dc1f", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "fc1d516b-4410-42df-8d1a-2420b8d0927b", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "e86a83d1-b3e4-44cc-95ad-b63d2b7a931d", "snapshot_date": "2026-02-05T21:49:55.255034", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}], "section_id": "d33388e3-082c-4c2b-9885-85cfd4705373", "sort_order": 1, "translations": {"en": {"name": "Section 1", "description": null}}}], "template_id": "6a8b1f80-60c2-497b-94e7-62540c020943", "crop_type_id": null, "translations": {"en": {"name": "Report Test", "description": null}}, "snapshot_date": "2026-02-05T21:49:55.249813"}	2026-02-05	2026-02-05 21:49:55.233216+00	2026-02-05 21:49:55.42358+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	2026-02-05 21:49:55.42782+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	\N	pending_sync	\N	\N	f
f8795176-fd75-422c-ba05-c620e4d00967	718996de-ba3d-4b71-9a19-a6e97d2947ee	b86839bf-62f6-4f3c-8748-5bdeaaa323a6	\N	74296790-e066-4bc9-b1ac-d88ddd03f23c	7556d0cb-dcd5-4677-accf-3bb7b8ba963e	AUD-2026-0027	Final Test Audit	FINALIZED	{"code": "T_1770328337", "version": 1, "sections": [{"code": "S1_1770328337", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "bee24a5b-c963-4451-86cc-068d3d4b9309", "parameter_snapshot": {"code": "P1_1770328337", "options": [], "parameter_id": "bee24a5b-c963-4451-86cc-068d3d4b9309", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:52:19.073755", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": true, "parameter_id": "458fd9c3-1e3b-4526-90c5-b791616862e3", "parameter_snapshot": {"code": "P2_1770328337", "options": [], "parameter_id": "458fd9c3-1e3b-4526-90c5-b791616862e3", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:52:19.075228", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 3, "is_required": true, "parameter_id": "3bbea4bb-bdd5-4465-b6d1-001830971892", "parameter_snapshot": {"code": "P3_1770328337", "options": [{"code": "opt1", "option_id": "74519a03-49e9-43a4-adbf-4f87f5ea49b9", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "d4ae2cd6-4259-436a-8a91-f9003f839b13", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "3bbea4bb-bdd5-4465-b6d1-001830971892", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "f8998096-2833-488c-b41e-08dedfcfc32c", "snapshot_date": "2026-02-05T21:52:19.076642", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}], "section_id": "9123b919-fdbe-478d-9757-c06c16606b63", "sort_order": 1, "translations": {"en": {"name": "Section 1", "description": null}}}], "template_id": "7556d0cb-dcd5-4677-accf-3bb7b8ba963e", "crop_type_id": null, "translations": {"en": {"name": "Report Test", "description": null}}, "snapshot_date": "2026-02-05T21:52:19.067487"}	2026-02-05	2026-02-05 21:52:19.042484+00	2026-02-05 21:52:19.304277+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	2026-02-05 21:52:19.309526+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	\N	pending_sync	\N	\N	f
1baaf778-6fda-4e39-be88-3b138bc82f59	f9761969-f234-4bb8-9b46-2ea70ad5b735	dcb6e693-f204-46fd-bbca-8eab795cc81a	\N	ff134ab3-d339-4d48-bf9c-a7ca3b095ebd	d19b7fe8-28a1-4957-a684-38586eeaa293	AUD-2026-0028	Final Test Audit	FINALIZED	{"code": "T_1770328517", "version": 1, "sections": [{"code": "S1_1770328517", "parameters": [{"sort_order": 1, "is_required": true, "parameter_id": "02f8b306-97b5-4dde-afdb-91725dfec46f", "parameter_snapshot": {"code": "P1_1770328517", "options": [], "parameter_id": "02f8b306-97b5-4dde-afdb-91725dfec46f", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:55:18.764649", "parameter_type": "NUMERIC", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": true, "parameter_id": "a9958b3e-69bf-42ac-a56d-c8d16d67d06b", "parameter_snapshot": {"code": "P2_1770328517", "options": [], "parameter_id": "a9958b3e-69bf-42ac-a56d-c8d16d67d06b", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:55:18.765837", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 3, "is_required": true, "parameter_id": "ad806e19-cd1d-4a40-ae12-bd0c5c203b9b", "parameter_snapshot": {"code": "P3_1770328517", "options": [{"code": "opt1", "option_id": "acfc1f03-a09d-408d-88c9-28563d8d9f9a", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "25dd033d-3220-4738-8685-4163540c3b74", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "ad806e19-cd1d-4a40-ae12-bd0c5c203b9b", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "6c5d8da2-26c9-424a-9b09-5f0b70e2c080", "snapshot_date": "2026-02-05T21:55:18.767064", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}}], "section_id": "8ed4cf1b-282b-4ab8-8983-2209bd440373", "sort_order": 1, "translations": {"en": {"name": "Section 1", "description": null}}}], "template_id": "d19b7fe8-28a1-4957-a684-38586eeaa293", "crop_type_id": null, "translations": {"en": {"name": "Report Test", "description": null}}, "snapshot_date": "2026-02-05T21:55:18.761151"}	2026-02-05	2026-02-05 21:55:18.748911+00	2026-02-05 21:55:18.964571+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	2026-02-05 21:55:18.969931+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	\N	pending_sync	\N	\N	f
99678697-d020-427b-9fab-b06977c030ad	8b411c61-9885-4672-ba08-e45709934575	5ae66809-e7de-448a-8f42-920a192c8704	35d78a67-1a03-43d9-afd4-3bdae8cec61d	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	e581e980-4eb2-4aed-97ae-6bba90e6dce4	AUD-2026-0029	Audit - Wrting questions	FINALIZED	{"code": "CODE-1212", "version": 1, "sections": [{"code": "SEC_5827_6984", "parameters": [{"sort_order": 0, "is_required": false, "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "parameter_snapshot": {"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T23:08:22.545586", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 1, "is_required": false, "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "parameter_snapshot": {"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T23:08:22.550650", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": false, "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "parameter_snapshot": {"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T23:08:22.553030", "parameter_type": "NUMERIC", "parameter_metadata": {}}}], "section_id": "8d28777c-3ec1-401b-a3f7-abe8af032686", "sort_order": 0, "translations": {"en": {"name": "General Info", "description": ""}}}], "template_id": "e581e980-4eb2-4aed-97ae-6bba90e6dce4", "crop_type_id": null, "translations": {"en": {"name": "Wrting questions", "description": "For testing the stuff at the end"}}, "snapshot_date": "2026-02-05T23:08:22.523411"}	2026-02-05	2026-02-05 23:08:22.499398+00	2026-02-05 23:11:35.487761+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-05 23:11:35.513713+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	pending_sync	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	t
6afc1849-9bba-466f-bf59-5b6f2bc5f145	8b411c61-9885-4672-ba08-e45709934575	5ae66809-e7de-448a-8f42-920a192c8704	eeb986d9-59ef-4158-9305-75d6993fe75e	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	e581e980-4eb2-4aed-97ae-6bba90e6dce4	AUD-2026-0031	Audit - Wrting questions	FINALIZED	{"code": "CODE-1212", "version": 1, "sections": [{"code": "SEC_5827_6984", "parameters": [{"sort_order": 0, "is_required": false, "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "parameter_snapshot": {"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-06T11:19:18.440355", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 1, "is_required": false, "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "parameter_snapshot": {"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-06T11:19:18.443012", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": false, "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "parameter_snapshot": {"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-06T11:19:18.444729", "parameter_type": "NUMERIC", "parameter_metadata": {}}}], "section_id": "8d28777c-3ec1-401b-a3f7-abe8af032686", "sort_order": 0, "translations": {"en": {"name": "General Info", "description": ""}}}], "template_id": "e581e980-4eb2-4aed-97ae-6bba90e6dce4", "crop_type_id": null, "translations": {"en": {"name": "Wrting questions", "description": "For testing the stuff at the end"}}, "snapshot_date": "2026-02-06T11:19:18.428399"}	2026-02-06	2026-02-06 11:19:18.404951+00	2026-02-06 11:30:16.444346+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-06 11:30:16.453213+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	pending_sync	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	t
f15bcb9e-8ecb-4bc3-8ca1-ffd86272e6e4	8b411c61-9885-4672-ba08-e45709934575	5ae66809-e7de-448a-8f42-920a192c8704	35d78a67-1a03-43d9-afd4-3bdae8cec61d	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	e581e980-4eb2-4aed-97ae-6bba90e6dce4	AUD-2026-0030	Audit - Wrting questions	SUBMITTED	{"code": "CODE-1212", "version": 1, "sections": [{"code": "SEC_5827_6984", "parameters": [{"sort_order": 0, "is_required": false, "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "parameter_snapshot": {"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T23:29:37.241575", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 1, "is_required": false, "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "parameter_snapshot": {"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T23:29:37.246750", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": false, "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "parameter_snapshot": {"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T23:29:37.248412", "parameter_type": "NUMERIC", "parameter_metadata": {}}}], "section_id": "8d28777c-3ec1-401b-a3f7-abe8af032686", "sort_order": 0, "translations": {"en": {"name": "General Info", "description": ""}}}], "template_id": "e581e980-4eb2-4aed-97ae-6bba90e6dce4", "crop_type_id": null, "translations": {"en": {"name": "Wrting questions", "description": "For testing the stuff at the end"}}, "snapshot_date": "2026-02-05T23:29:37.214952"}	2026-02-05	2026-02-05 23:29:37.192094+00	2026-02-09 13:08:02.729011+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	\N	\N	pending_sync	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	t
a316e7a5-0bca-4a61-a7a7-11f3fbde3258	8b411c61-9885-4672-ba08-e45709934575	5ae66809-e7de-448a-8f42-920a192c8704	b08d5b7e-0cd2-4525-8575-b04be01c8817	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	e581e980-4eb2-4aed-97ae-6bba90e6dce4	AUD-2026-0032	Audit - Wrting questions	FINALIZED	{"code": "CODE-1212", "version": 1, "sections": [{"code": "SEC_5827_6984", "parameters": [{"sort_order": 0, "is_required": false, "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "parameter_snapshot": {"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-09T19:10:50.565015", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 1, "is_required": false, "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "parameter_snapshot": {"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-09T19:10:50.569926", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": false, "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "parameter_snapshot": {"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-09T19:10:50.571122", "parameter_type": "NUMERIC", "parameter_metadata": {}}}], "section_id": "8d28777c-3ec1-401b-a3f7-abe8af032686", "sort_order": 0, "translations": {"en": {"name": "General Info", "description": ""}}}], "template_id": "e581e980-4eb2-4aed-97ae-6bba90e6dce4", "crop_type_id": null, "translations": {"en": {"name": "Wrting questions", "description": "For testing the stuff at the end"}}, "snapshot_date": "2026-02-09T19:10:50.519074"}	2026-02-09	2026-02-09 19:10:50.355687+00	2026-02-09 19:20:48.83016+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-09 19:20:48.843269+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	pending_sync	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	t
14d407bc-29ca-4a37-a5fd-85911e2eed9e	8b411c61-9885-4672-ba08-e45709934575	5ae66809-e7de-448a-8f42-920a192c8704	43b19d72-aa87-4c79-b241-81dcdb6d29af	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	e581e980-4eb2-4aed-97ae-6bba90e6dce4	AUD-2026-0034	Audit - Wrting questions	FINALIZED	{"code": "CODE-1212", "version": 1, "sections": [{"code": "SEC_5827_6984", "parameters": [{"sort_order": 0, "is_required": false, "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "parameter_snapshot": {"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-11T08:38:48.104595", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 1, "is_required": false, "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "parameter_snapshot": {"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-11T08:38:48.107209", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": false, "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "parameter_snapshot": {"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-11T08:38:48.109346", "parameter_type": "NUMERIC", "parameter_metadata": {}}}], "section_id": "8d28777c-3ec1-401b-a3f7-abe8af032686", "sort_order": 0, "translations": {"en": {"name": "General Info", "description": ""}}}], "template_id": "e581e980-4eb2-4aed-97ae-6bba90e6dce4", "crop_type_id": null, "translations": {"en": {"name": "Wrting questions", "description": "For testing the stuff at the end"}}, "snapshot_date": "2026-02-11T08:38:48.092223"}	2026-02-11	2026-02-11 08:38:48.071579+00	2026-02-11 09:17:24.981255+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-11 09:17:24.985976+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	pending_sync	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	t
d18c02c8-4408-4e0f-93b0-ebeb8022f92e	8b411c61-9885-4672-ba08-e45709934575	5ae66809-e7de-448a-8f42-920a192c8704	43b19d72-aa87-4c79-b241-81dcdb6d29af	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	e581e980-4eb2-4aed-97ae-6bba90e6dce4	AUD-2026-0033	Audit - Wrting questions	FINALIZED	{"code": "CODE-1212", "version": 1, "sections": [{"code": "SEC_5827_6984", "parameters": [{"sort_order": 0, "is_required": false, "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "parameter_snapshot": {"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-11T08:20:13.167268", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 1, "is_required": false, "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "parameter_snapshot": {"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-11T08:20:13.170919", "parameter_type": "TEXT", "parameter_metadata": {}}}, {"sort_order": 2, "is_required": false, "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "parameter_snapshot": {"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-11T08:20:13.172604", "parameter_type": "NUMERIC", "parameter_metadata": {}}}], "section_id": "8d28777c-3ec1-401b-a3f7-abe8af032686", "sort_order": 0, "translations": {"en": {"name": "General Info", "description": ""}}}], "template_id": "e581e980-4eb2-4aed-97ae-6bba90e6dce4", "crop_type_id": null, "translations": {"en": {"name": "Wrting questions", "description": "For testing the stuff at the end"}}, "snapshot_date": "2026-02-11T08:20:13.145892"}	2026-02-11	2026-02-11 08:20:13.077943+00	2026-02-11 09:20:14.234216+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-11 09:20:14.23872+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	pending_sync	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	t
\.


--
-- Data for Name: chat_channel_members; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_channel_members (id, channel_id, organization_id, joined_at, added_by) FROM stdin;
\.


--
-- Data for Name: chat_channels; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_channels (id, context_type, context_id, name, is_active, created_at, updated_at, created_by, updated_by) FROM stdin;
\.


--
-- Data for Name: chat_messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_messages (id, channel_id, sender_id, sender_org_id, message_type, content, media_url, is_system_message, created_at, updated_at, deleted_at) FROM stdin;
\.


--
-- Data for Name: crop_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crop_categories (id, code, sort_order, is_active, created_at, updated_at) FROM stdin;
b3a15f38-afb6-408b-bdcf-aef70cd22942	VEGETABLES	1	t	2026-01-30 00:05:41.265897+00	2026-01-30 00:05:41.265897+00
32bb70ee-9af4-4c14-8b91-05b85f29112f	FRUITS	2	t	2026-01-30 00:05:41.265897+00	2026-01-30 00:05:41.265897+00
7eb7d897-1bcf-4c77-b8e2-eaf5fff94008	CEREALS	3	t	2026-01-30 00:05:41.265897+00	2026-01-30 00:05:41.265897+00
d483c59a-7c5e-4d10-b8d2-6076fa14ad94	PULSES	4	t	2026-01-30 00:05:41.265897+00	2026-01-30 00:05:41.265897+00
d091d46f-c089-4542-964f-d08777aadb79	SPICES	5	t	2026-01-30 00:05:41.265897+00	2026-01-30 00:05:41.265897+00
\.


--
-- Data for Name: crop_category_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crop_category_translations (id, crop_category_id, language_code, name, description) FROM stdin;
2324582e-befc-4abf-a96c-91fe0616476a	b3a15f38-afb6-408b-bdcf-aef70cd22942	en	Vegetables	\N
6952416d-0305-4be0-8e93-11f05dbe1569	32bb70ee-9af4-4c14-8b91-05b85f29112f	en	Fruits	\N
fdbe5ba5-430d-413e-ab40-6b75ee312e57	7eb7d897-1bcf-4c77-b8e2-eaf5fff94008	en	Cereals	\N
9584c113-aedf-48d3-803d-6b460dbdddc6	d483c59a-7c5e-4d10-b8d2-6076fa14ad94	en	Pulses	\N
b2d1d382-f511-453a-9585-fc2c23226fa2	d091d46f-c089-4542-964f-d08777aadb79	en	Spices	\N
dcb18c80-51b1-4474-bc66-33a742d618de	b3a15f38-afb6-408b-bdcf-aef70cd22942	ta	காய்கறிகள்	\N
545a354d-6662-43c4-a651-c88ed6a5e94d	32bb70ee-9af4-4c14-8b91-05b85f29112f	ta	பழங்கள்	\N
300b0697-e8fb-4b46-8967-77ee75d50045	7eb7d897-1bcf-4c77-b8e2-eaf5fff94008	ta	தானியங்கள்	\N
e6a1b681-d613-4620-9839-750c395750ee	d483c59a-7c5e-4d10-b8d2-6076fa14ad94	ta	பருப்பு வகைகள்	\N
80a98474-3eb1-4a8e-9d05-95d2c43878c2	d091d46f-c089-4542-964f-d08777aadb79	ta	மசாலா பொருட்கள்	\N
db1f6c06-9d88-4ecb-a98a-deefb2f82c7e	b3a15f38-afb6-408b-bdcf-aef70cd22942	ml	പച്ചക്കറികൾ	\N
9ae34fdf-4579-4693-9f5f-c6b60dfa859f	32bb70ee-9af4-4c14-8b91-05b85f29112f	ml	പഴങ്ങൾ	\N
cb896fc4-c9fd-4a38-84c3-bdf5013b2078	7eb7d897-1bcf-4c77-b8e2-eaf5fff94008	ml	ധാന്യങ്ങൾ	\N
a3933580-0819-4253-a301-d5da0a794265	d483c59a-7c5e-4d10-b8d2-6076fa14ad94	ml	പയർ വർഗ്ഗങ്ങൾ	\N
85cd0ed6-f4a3-4e50-a155-d3ecc51840ab	d091d46f-c089-4542-964f-d08777aadb79	ml	സുഗന്ധവ്യഞ്ജനങ്ങൾ	\N
\.


--
-- Data for Name: crop_lifecycle_photos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crop_lifecycle_photos (id, crop_id, file_url, file_key, caption, photo_date, uploaded_at, uploaded_by) FROM stdin;
\.


--
-- Data for Name: crop_type_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crop_type_translations (id, crop_type_id, language_code, name, description) FROM stdin;
d6f143a8-e83c-4052-9f22-1ad386a1690b	420b1d7d-7f33-429c-9da3-69ecc4d42145	en	Tomato	\N
e34424b6-7461-4d4b-b5ec-eeca16120666	cad4f739-cd58-4ae4-a0e9-ae390bb37cc4	en	Chili	\N
71714eca-be9b-43a7-a606-a19d502b794b	1326a84d-dbf2-4a62-8179-2dedf76d034d	en	Banana	\N
ccfe98fb-def2-47a4-87f6-d71e23926249	b72d3c6d-6994-441f-a6e2-2b175e1c0fc2	en	Mango	\N
21580e48-377b-4594-ae4c-57eb833c85c3	420b1d7d-7f33-429c-9da3-69ecc4d42145	ta	தக்காளி	\N
596b557f-e6d6-44b1-9337-0bd7ef07a75a	cad4f739-cd58-4ae4-a0e9-ae390bb37cc4	ta	மிளகாய்	\N
7b9903cf-3e9f-4189-b69f-89b834eb9bd3	1326a84d-dbf2-4a62-8179-2dedf76d034d	ta	வாழை	\N
d418d06e-aa0e-43e1-80d8-6485be5b8d29	b72d3c6d-6994-441f-a6e2-2b175e1c0fc2	ta	மாம்பழம்	\N
dc17f3e8-71c3-44a6-a849-996fad52b556	420b1d7d-7f33-429c-9da3-69ecc4d42145	ml	തക്കാളി	\N
aa86e458-2e64-4c2f-bdbf-71792c8d358f	cad4f739-cd58-4ae4-a0e9-ae390bb37cc4	ml	മുളക്	\N
45be74f7-4025-4bd2-8ef5-6519af72ab88	1326a84d-dbf2-4a62-8179-2dedf76d034d	ml	വാഴപ്പഴം	\N
dc143b63-712e-49f3-86f8-0d0501bcfe0b	b72d3c6d-6994-441f-a6e2-2b175e1c0fc2	ml	മാങ്ങ	\N
b1a6366c-1440-4957-b242-8e596863fade	a2cb831e-fa82-4646-8f59-68cb0093220f	en	Wheat	Wheat crop
\.


--
-- Data for Name: crop_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crop_types (id, category_id, code, sort_order, is_active, created_at, updated_at) FROM stdin;
420b1d7d-7f33-429c-9da3-69ecc4d42145	b3a15f38-afb6-408b-bdcf-aef70cd22942	TOMATO	1	t	2026-01-30 00:05:41.286809+00	2026-01-30 00:05:41.286809+00
cad4f739-cd58-4ae4-a0e9-ae390bb37cc4	b3a15f38-afb6-408b-bdcf-aef70cd22942	CHILI	2	t	2026-01-30 00:05:41.286809+00	2026-01-30 00:05:41.286809+00
1326a84d-dbf2-4a62-8179-2dedf76d034d	32bb70ee-9af4-4c14-8b91-05b85f29112f	BANANA	1	t	2026-01-30 00:05:41.286809+00	2026-01-30 00:05:41.286809+00
b72d3c6d-6994-441f-a6e2-2b175e1c0fc2	32bb70ee-9af4-4c14-8b91-05b85f29112f	MANGO	2	t	2026-01-30 00:05:41.286809+00	2026-01-30 00:05:41.286809+00
a2cb831e-fa82-4646-8f59-68cb0093220f	7eb7d897-1bcf-4c77-b8e2-eaf5fff94008	WHEAT	0	t	2026-01-30 00:08:39.002834+00	2026-01-30 00:08:39.002834+00
\.


--
-- Data for Name: crop_varieties; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crop_varieties (id, crop_type_id, code, sort_order, is_active, variety_metadata, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: crop_variety_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crop_variety_translations (id, crop_variety_id, language_code, name, description) FROM stdin;
\.


--
-- Data for Name: crop_yield_photos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crop_yield_photos (id, crop_yield_id, photo_id, created_at) FROM stdin;
\.


--
-- Data for Name: crop_yields; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crop_yields (id, crop_id, yield_type, harvest_date, quantity, quantity_unit_id, harvest_area, harvest_area_unit_id, notes, created_at, created_by) FROM stdin;
8e1c0e26-eb21-4d9f-81ae-6ef11c92eac8	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	ACTUAL	2026-02-09	34.0000	08607b68-5102-45f3-a0e8-d0da2686b742	\N	\N	fstgfg	2026-02-09 12:49:46.457738+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
\.


--
-- Data for Name: crops; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crops (id, plot_id, name, description, crop_type_id, crop_variety_id, area, area_unit_id, plant_count, lifecycle, planned_date, planted_date, transplanted_date, production_start_date, completed_date, terminated_date, closed_date, created_at, updated_at, created_by, updated_by, variety_name) FROM stdin;
eb4f9b72-93cc-4ab0-b485-eaf889ce420e	914cf77a-e929-4e0a-8d59-3f98ff892d6d	Wheat Season 2026	\N	a2cb831e-fa82-4646-8f59-68cb0093220f	\N	\N	\N	\N	PRODUCTION	\N	2026-01-30	\N	\N	\N	\N	\N	2026-01-30 00:08:39.016633+00	2026-01-30 00:08:39.016633+00	fe4d1e04-7569-409d-8bfc-f7319e7ea582	\N	\N
56e4d5c0-f344-45cb-92cd-1c884d501698	5ab1b928-57fb-404c-b246-930d976276d9	Debug Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:06:48.858049+00	2026-02-01 10:06:48.858049+00	a7c620dc-005f-41e4-a09c-84a578fdff32	a7c620dc-005f-41e4-a09c-84a578fdff32	\N
a64e36f2-9bd3-4acc-b874-f30230610613	8ae3d1d3-d808-49ca-a90c-b609893dab46	Quick Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:10:07.561198+00	2026-02-01 10:10:07.561198+00	eb63636b-e512-4cd7-9296-f0d38d62f74d	eb63636b-e512-4cd7-9296-f0d38d62f74d	\N
539b816d-0f95-4735-bda6-14281cab4406	558ba3d7-a42b-4139-a773-388d0daa6db2	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:31:21.393741+00	2026-02-01 10:31:21.393741+00	aec76aa4-0bf4-40bb-9307-de54a5d205a5	aec76aa4-0bf4-40bb-9307-de54a5d205a5	\N
c17e06d6-19e8-4e6b-8882-55456eecd307	09d1b952-ebef-4c29-a0f5-cb453d4b6763	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:32:49.43754+00	2026-02-01 10:32:49.43754+00	ee6157bd-176f-4f75-8cea-64adb841884f	ee6157bd-176f-4f75-8cea-64adb841884f	\N
575e84c3-81b6-4926-afdf-108fff49c94a	19088941-3e7a-4a63-8db2-5e2e77cdf844	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:33:10.163138+00	2026-02-01 10:33:10.163138+00	ee193894-167a-4355-8899-7c19ba395e9f	ee193894-167a-4355-8899-7c19ba395e9f	\N
fd80c1fa-87e4-46ae-a9dc-77a1e648ebe1	26c45f11-5e57-490e-b1a4-b0f8bfc88559	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:33:32.183884+00	2026-02-01 10:33:32.183884+00	3c1aab18-4eb2-4ab2-bcca-993c37e7fab1	3c1aab18-4eb2-4ab2-bcca-993c37e7fab1	\N
ac7398b4-78f6-48c2-8b3b-b3c4583fa268	7ec57c8e-3050-4d33-98df-9b5ba0c07e1f	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:34:04.579035+00	2026-02-01 10:34:04.579035+00	3e72bdbc-89a7-4009-a93e-bba6fec86530	3e72bdbc-89a7-4009-a93e-bba6fec86530	\N
08707817-10ee-472b-99a8-5e6365f756e7	11597ed7-c2b0-47eb-82c1-4ae1ac768449	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:34:22.13176+00	2026-02-01 10:34:22.13176+00	c5e779fa-7e25-4b84-b410-a55bd0c9e219	c5e779fa-7e25-4b84-b410-a55bd0c9e219	\N
2faf16a9-07f4-42d5-b177-52c9315b2a68	ea57e5a0-ae34-428d-ad8c-08f0144272d5	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:34:42.714647+00	2026-02-01 10:34:42.714647+00	b8cf8398-0dff-42c3-99ab-aaa2bcf646e6	b8cf8398-0dff-42c3-99ab-aaa2bcf646e6	\N
5ffd8d1f-7101-4a4a-bf41-a1b4b32cadf4	ad4a57f6-b5cd-44ea-87c8-f3c21da1ed2b	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:35:08.052768+00	2026-02-01 10:35:08.052768+00	a031994b-5afb-4fa2-9d8a-8004d7e8c9a3	a031994b-5afb-4fa2-9d8a-8004d7e8c9a3	\N
479e4492-6844-401f-90f9-716668c94aa1	b341f53a-3b73-4e63-940b-f73b84874a02	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:35:48.253588+00	2026-02-01 10:35:48.253588+00	2e6f6fed-9d3d-4b85-87d0-a134932d0dd7	2e6f6fed-9d3d-4b85-87d0-a134932d0dd7	\N
31faaa66-c5a6-49a6-8000-e03aecd71319	1c69b5a0-3c13-4ee6-8470-00199374b770	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:36:44.174093+00	2026-02-01 10:36:44.174093+00	d77da629-52f1-46c9-9118-dbe7fe92c333	d77da629-52f1-46c9-9118-dbe7fe92c333	\N
c25d7a3f-cb3b-484d-9cd4-0399615ff566	bcb351aa-b8dc-4784-9e5e-88fdc2717edb	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:37:05.309204+00	2026-02-01 10:37:05.309204+00	66d51b1b-c21b-4f8c-99ba-c2854ceeab97	66d51b1b-c21b-4f8c-99ba-c2854ceeab97	\N
af65b918-c058-4eda-81df-72063572aaec	0d4cf2f4-4a9f-47d3-8be3-e3549a18a3c4	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:38:13.4847+00	2026-02-01 10:38:13.4847+00	3f82b4a7-b270-4d68-9e02-e9068eaa668f	3f82b4a7-b270-4d68-9e02-e9068eaa668f	\N
8d2c89ad-a3b1-479f-b186-c467627b20fd	cf02c06e-973e-4d58-83c4-7d948f9e1eaf	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 10:38:59.332887+00	2026-02-01 10:38:59.332887+00	d5104c40-d4cc-47ac-a700-0c7414c1b26a	d5104c40-d4cc-47ac-a700-0c7414c1b26a	\N
aa2294ec-75a5-41d8-8140-152503c6db23	9c7de365-ad4e-4f28-85ce-b4f0effa7386	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 11:01:39.787816+00	2026-02-01 11:01:39.787816+00	fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1	fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1	\N
54c34b1f-298c-47c7-a82a-a2253b679c08	4123d9ec-4f1f-4acf-b797-aa2eb18f6fda	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-01 11:06:39.224048+00	2026-02-01 11:06:39.224048+00	1a8f4448-290b-48ff-9f17-2d76e841a1f3	1a8f4448-290b-48ff-9f17-2d76e841a1f3	\N
39e9fb39-bcf9-4514-8429-02fa26595670	bafaa4d4-8461-4cbd-af31-760abbc0214c	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:28:20.415524+00	2026-02-05 21:28:20.415524+00	5847755d-a7ef-4f01-ad83-b96116cc5b06	5847755d-a7ef-4f01-ad83-b96116cc5b06	\N
c6296bf7-c40b-4b4b-9ce4-b1dfbafd1d11	539d5974-df3d-473d-a7b2-103c18e314ff	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:30:53.605331+00	2026-02-05 21:30:53.605331+00	3ca9cf6b-c372-4530-bc35-3440c68f858f	3ca9cf6b-c372-4530-bc35-3440c68f858f	\N
00ac9d42-2f56-4064-898a-1643ffe6c5c4	c37e7e74-11b6-4191-a4d2-967137792659	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:31:42.629937+00	2026-02-05 21:31:42.629937+00	09b95fab-3a52-4e54-8957-76e81ebf668a	09b95fab-3a52-4e54-8957-76e81ebf668a	\N
03779288-b39e-419b-9579-cf6db53132e4	aa9c75f2-8264-49e7-9218-634341955404	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:33:45.185972+00	2026-02-05 21:33:45.185972+00	39219340-21cb-4a88-a939-93baf1a0e840	39219340-21cb-4a88-a939-93baf1a0e840	\N
da16da3c-4ccd-4bc4-94cb-ee93c45a3b26	f8ebbe83-8611-4672-8a18-75dea56e2535	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:34:41.18269+00	2026-02-05 21:34:41.18269+00	5368cfba-bae0-4132-88e4-4fde67d9e523	5368cfba-bae0-4132-88e4-4fde67d9e523	\N
4fd6402f-2f98-4485-9544-7e77ab3549ae	4e9c8e28-bcd1-4252-bf4c-a2b93fa8c21a	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:36:32.663026+00	2026-02-05 21:36:32.663026+00	222968c5-f7cd-46a9-80a7-ae6d0557b5c3	222968c5-f7cd-46a9-80a7-ae6d0557b5c3	\N
db79839b-599c-463d-ba0d-c1953ae6861d	11f72f4e-1fd9-4ce2-8da1-d6a75a1e9b31	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:39:33.647229+00	2026-02-05 21:39:33.647229+00	2b8bb712-3cfe-435e-84f7-49dfe73d641b	2b8bb712-3cfe-435e-84f7-49dfe73d641b	\N
c4252796-b498-4307-9312-e1e69858946e	3a40152d-4f4b-4b62-b299-d7c5e6314dd9	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:40:37.566598+00	2026-02-05 21:40:37.566598+00	ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f	ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f	\N
efb39005-5e09-4d9f-9d37-1bbd405ea5eb	bf759bec-0219-4b5a-b643-5e75f263b1a3	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:41:47.310238+00	2026-02-05 21:41:47.310238+00	eb271702-3161-48b2-a4c9-8747819b7ae7	eb271702-3161-48b2-a4c9-8747819b7ae7	\N
0c6d3034-08a1-4e76-8e84-719585abf527	63dee78b-f015-4b3f-ae62-0ef30f0ddba1	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:43:42.722563+00	2026-02-05 21:43:42.722563+00	31148b05-1512-43ce-8b01-fd3b423fca6e	31148b05-1512-43ce-8b01-fd3b423fca6e	\N
23cc371e-1fbd-47f4-a44f-8f9894a61d73	02467fc1-7bc3-474d-adb7-e6ca4f7f13a8	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:49:55.09998+00	2026-02-05 21:49:55.09998+00	3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167	3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167	\N
74296790-e066-4bc9-b1ac-d88ddd03f23c	08b684c6-9193-439d-a1ef-faa33218a7b1	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:52:18.858211+00	2026-02-05 21:52:18.858211+00	83e1d52b-a86b-461a-b995-e79e2ac57878	83e1d52b-a86b-461a-b995-e79e2ac57878	\N
ff134ab3-d339-4d48-bf9c-a7ca3b095ebd	bf7294d2-e398-47cc-ad8c-955564e3f690	Rice	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 21:55:18.592724+00	2026-02-05 21:55:18.592724+00	1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3	1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3	\N
17c3b971-a482-4761-90ce-0460e6eba521	ca345bb0-75ea-41ae-8f8f-c9a68cbb63d2	Test Rice Crop	\N	\N	\N	\N	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-05 22:33:46.492376+00	2026-02-05 22:33:46.492376+00	723079fb-4d41-408d-958c-a1d417576d82	723079fb-4d41-408d-958c-a1d417576d82	\N
4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	4aa5abad-51da-4c92-b667-ab53a855d533	potato	\N	\N	\N	30.0000	\N	\N	TERMINATED	\N	2026-02-04	2026-02-09	\N	\N	2026-02-09	\N	2026-01-30 00:16:16.055145+00	2026-02-09 18:26:05.41565+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
22086444-0094-4b87-bb63-a24c03614344	4aa5abad-51da-4c92-b667-ab53a855d533	Rice	\N	\N	\N	50.0000	\N	\N	COMPLETED	\N	2025-12-15	2026-02-10	2026-02-10	2026-02-10	\N	\N	2026-01-30 00:15:49.873703+00	2026-02-10 23:16:10.846708+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	Kufri Jyoti
0d320da5-ce59-4288-b1d3-f6d7d077454a	5680d5e1-aea2-457a-864a-3db5386056dc	sdfsdf	\N	\N	\N	3245.0000	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-10 23:17:10.354815+00	2026-02-10 23:17:10.354815+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
9aa6aef8-8ba8-4073-80b3-87e5d4fbabcb	5680d5e1-aea2-457a-864a-3db5386056dc	asdasd	\N	\N	\N	12.0000	\N	\N	PLANNED	\N	\N	\N	\N	\N	\N	\N	2026-02-10 23:33:29.111323+00	2026-02-10 23:33:29.111323+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	aasdasdasd
e576216b-8001-4575-b8b0-f744753c2625	5680d5e1-aea2-457a-864a-3db5386056dc	tytyt	\N	\N	\N	23.0000	\N	\N	PLANTED	\N	2026-02-10	\N	\N	\N	\N	\N	2026-02-10 23:38:01.412851+00	2026-02-10 23:38:01.412851+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	tytyty
fe85e77f-09e9-457b-a3ac-36b42c3b8140	4aa5abad-51da-4c92-b667-ab53a855d533	sadasd	\N	\N	\N	123.0000	\N	\N	PLANTED	\N	2026-02-11	\N	\N	\N	\N	\N	2026-02-10 23:28:22.872475+00	2026-02-11 09:30:45.232655+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	New one year
c056f362-9d57-498d-8c8c-5637a7de2f95	4aa5abad-51da-4c92-b667-ab53a855d533	Banana	\N	\N	\N	25.0000	\N	\N	PLANTED	\N	2026-02-11	\N	\N	\N	\N	\N	2026-02-10 23:10:46.990843+00	2026-02-11 09:30:57.667589+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
\.


--
-- Data for Name: farm_irrigation_modes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.farm_irrigation_modes (id, farm_id, irrigation_mode_id, created_at) FROM stdin;
\.


--
-- Data for Name: farm_soil_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.farm_soil_types (id, farm_id, soil_type_id, created_at) FROM stdin;
158e9710-b766-4075-8762-659bbb83bce4	748bf7fa-ee25-49a9-b735-eb86c450e8ae	2e7fba12-cb3d-4e66-80c8-d984530d043c	2026-02-09 13:55:34.790382+00
\.


--
-- Data for Name: farm_supervisors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.farm_supervisors (id, farm_id, supervisor_id, assigned_at, assigned_by, created_at) FROM stdin;
\.


--
-- Data for Name: farm_water_sources; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.farm_water_sources (id, farm_id, water_source_id, created_at) FROM stdin;
a1cf7cd3-51bb-4ad6-8388-a2cfa10c4237	748bf7fa-ee25-49a9-b735-eb86c450e8ae	07f65611-5b1b-40ad-b25b-16839eb9b098	2026-02-09 13:55:34.790382+00
\.


--
-- Data for Name: farms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.farms (id, organization_id, name, description, address, district, state, pincode, location, boundary, area, area_unit_id, farm_attributes, manager_id, is_active, created_at, updated_at, created_by, updated_by, city) FROM stdin;
e165dd58-1298-4f46-9d62-f5e614aa934f	1455677e-0753-44c1-959e-06c542a28884	Green Valley Farm	\N	\N	\N	\N	\N	\N	\N	10.0000	1c6b90ac-ff6b-4c5f-be90-5f33c91725d4	\N	\N	t	2026-01-30 00:08:38.967921+00	2026-01-30 00:08:38.967921+00	fe4d1e04-7569-409d-8bfc-f7319e7ea582	\N	\N
26172374-47c4-4f4b-b43a-70e9436e84c3	6ccc83ff-6dd6-45b8-9285-d189eec284e9	Test Farm 1769940298	Test farm for audit E2E testing	\N	\N	\N	\N	0101000020E6100000E78C28ED0D6653405396218E75F12940	0103000020E61000000100000005000000BC74931804665340FED478E926F12940AE47E17A14665340FED478E926F12940AE47E17A146653408B6CE7FBA9F12940BC749318046653408B6CE7FBA9F12940BC74931804665340FED478E926F12940	10.5000	\N	{}	\N	t	2026-02-01 10:04:58.653995+00	2026-02-01 10:04:58.653995+00	bfdafb1c-258c-487a-84a9-8df88d6f7efd	bfdafb1c-258c-487a-84a9-8df88d6f7efd	\N
13b4a813-2a7e-4eea-9014-e79a65177f11	9a08dd9e-37f1-466a-9cce-b38722c3c08d	Debug Farm 1769940408	Debug farm	\N	\N	\N	\N	0101000020E61000000000000000605340CDCCCCCCCCCC2940	0103000020E610000001000000050000008FC2F5285C5F534048E17A14AEC72940713D0AD7A360534048E17A14AEC72940713D0AD7A360534052B81E85EBD129408FC2F5285C5F534052B81E85EBD129408FC2F5285C5F534048E17A14AEC72940	5.0000	\N	{}	\N	t	2026-02-01 10:06:48.804391+00	2026-02-01 10:06:48.804391+00	a7c620dc-005f-41e4-a09c-84a578fdff32	a7c620dc-005f-41e4-a09c-84a578fdff32	\N
e61be074-9ef2-4cbb-8a7f-c472b58c20d8	d21c407f-5ec7-4940-9863-903fc66fb45f	Quick Farm 1769940607	Quick test	\N	\N	\N	\N	0101000020E61000000000000000605340CDCCCCCCCCCC2940	0103000020E610000001000000050000008FC2F5285C5F534048E17A14AEC72940713D0AD7A360534048E17A14AEC72940713D0AD7A360534052B81E85EBD129408FC2F5285C5F534052B81E85EBD129408FC2F5285C5F534048E17A14AEC72940	5.0000	\N	{}	\N	t	2026-02-01 10:10:07.515901+00	2026-02-01 10:10:07.515901+00	eb63636b-e512-4cd7-9296-f0d38d62f74d	eb63636b-e512-4cd7-9296-f0d38d62f74d	\N
5df6ac85-ae46-4296-a5c4-4842b38a5e34	efa7b0ac-291d-489e-94f5-b7e09ee61211	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:31:21.360523+00	2026-02-01 10:31:21.360523+00	aec76aa4-0bf4-40bb-9307-de54a5d205a5	aec76aa4-0bf4-40bb-9307-de54a5d205a5	\N
a88af18a-ba32-4e29-918d-241a96c84d73	23f17148-f316-4fb6-8fd4-c4f2045ae401	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:32:49.410456+00	2026-02-01 10:32:49.410456+00	ee6157bd-176f-4f75-8cea-64adb841884f	ee6157bd-176f-4f75-8cea-64adb841884f	\N
569aa75f-1b29-49a0-b8a9-11d3471d548e	cc35b76b-375c-4261-8fa4-24b833a63cdb	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:33:10.121971+00	2026-02-01 10:33:10.121971+00	ee193894-167a-4355-8899-7c19ba395e9f	ee193894-167a-4355-8899-7c19ba395e9f	\N
45591473-684c-4220-940f-e1264a23c4f9	13bd2caa-40a9-450f-9df0-7a7c110e49ac	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:33:32.150218+00	2026-02-01 10:33:32.150218+00	3c1aab18-4eb2-4ab2-bcca-993c37e7fab1	3c1aab18-4eb2-4ab2-bcca-993c37e7fab1	\N
5bb12bfc-8c01-40b9-8a8b-380fc5d41287	65e03c0d-7af5-4622-b2a2-8a867cf708a5	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:34:04.54496+00	2026-02-01 10:34:04.54496+00	3e72bdbc-89a7-4009-a93e-bba6fec86530	3e72bdbc-89a7-4009-a93e-bba6fec86530	\N
9959213c-442e-4fa1-b1dd-fb2171548a99	c883192d-5000-4f2a-882c-3e8d3d49d4f6	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:34:22.099712+00	2026-02-01 10:34:22.099712+00	c5e779fa-7e25-4b84-b410-a55bd0c9e219	c5e779fa-7e25-4b84-b410-a55bd0c9e219	\N
3cb1d1f8-48d2-4d0d-a336-414a170268e7	bc9ba376-ec2d-4293-a39d-22daa59a0236	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:34:42.681638+00	2026-02-01 10:34:42.681638+00	b8cf8398-0dff-42c3-99ab-aaa2bcf646e6	b8cf8398-0dff-42c3-99ab-aaa2bcf646e6	\N
8ba032c0-9cee-47ff-a19f-216bb806d53f	bf66b4c8-e589-4240-9949-928683f45020	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:35:08.022526+00	2026-02-01 10:35:08.022526+00	a031994b-5afb-4fa2-9d8a-8004d7e8c9a3	a031994b-5afb-4fa2-9d8a-8004d7e8c9a3	\N
6b080a02-6e8c-4860-883c-36eab3a1034a	ea925230-a27d-4bf3-9187-877dab140c8b	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:35:48.222413+00	2026-02-01 10:35:48.222413+00	2e6f6fed-9d3d-4b85-87d0-a134932d0dd7	2e6f6fed-9d3d-4b85-87d0-a134932d0dd7	\N
a6ea6658-aabd-401e-b705-b7412e042a4f	5d712ef0-dfcc-4e49-ba75-0d15424f0409	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:36:44.106073+00	2026-02-01 10:36:44.106073+00	d77da629-52f1-46c9-9118-dbe7fe92c333	d77da629-52f1-46c9-9118-dbe7fe92c333	\N
a2cdb712-e445-411a-bb3f-70010fa01bcc	e69d30db-071e-4079-9a43-3267a66927a9	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:37:05.275315+00	2026-02-01 10:37:05.275315+00	66d51b1b-c21b-4f8c-99ba-c2854ceeab97	66d51b1b-c21b-4f8c-99ba-c2854ceeab97	\N
a7da74c5-e783-4da3-8389-a7293d2eadc4	aa001d98-fda0-4f0f-971e-361f1af462ad	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:38:13.454318+00	2026-02-01 10:38:13.454318+00	3f82b4a7-b270-4d68-9e02-e9068eaa668f	3f82b4a7-b270-4d68-9e02-e9068eaa668f	\N
97e8f08d-7aef-41f1-919a-9c284e0680c7	62656d65-00b9-4446-b11a-586d60d38c8c	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 10:38:59.273623+00	2026-02-01 10:38:59.273623+00	d5104c40-d4cc-47ac-a700-0c7414c1b26a	d5104c40-d4cc-47ac-a700-0c7414c1b26a	\N
49303b32-b426-4909-8d02-1e572a8a83b4	f4b08735-4038-49dd-bed2-4cb44e9c9287	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 11:01:39.752685+00	2026-02-01 11:01:39.752685+00	fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1	fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1	\N
51aabf82-b0ba-401b-9201-6886cb4c0ce5	2ec2a2b1-87f2-4962-8649-c029973d9504	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-01 11:06:39.184023+00	2026-02-01 11:06:39.184023+00	1a8f4448-290b-48ff-9f17-2d76e841a1f3	1a8f4448-290b-48ff-9f17-2d76e841a1f3	\N
488cf92d-00da-4a11-9051-a0fc96336a79	11a75d4a-ecef-4ae0-9767-790dcf59ba5c	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:25:33.822972+00	2026-02-05 21:25:33.822972+00	5526632a-9523-4219-b2ca-708559772fb8	5526632a-9523-4219-b2ca-708559772fb8	\N
e6258a38-cf90-4e0d-ac99-8cee5de538d7	e5faaf23-44f2-419b-8226-8d3b25615c9a	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:28:20.249609+00	2026-02-05 21:28:20.249609+00	5847755d-a7ef-4f01-ad83-b96116cc5b06	5847755d-a7ef-4f01-ad83-b96116cc5b06	\N
757e3cc4-c50a-43a9-8311-c5b9729a3b29	8aac186d-15a6-4ce9-94d7-89e8b6eee47d	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:30:53.568152+00	2026-02-05 21:30:53.568152+00	3ca9cf6b-c372-4530-bc35-3440c68f858f	3ca9cf6b-c372-4530-bc35-3440c68f858f	\N
188b63e7-c8ae-4814-86dd-ec23230acade	675f5900-0a12-48ea-a2a9-c121508fc23e	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:31:42.599794+00	2026-02-05 21:31:42.599794+00	09b95fab-3a52-4e54-8957-76e81ebf668a	09b95fab-3a52-4e54-8957-76e81ebf668a	\N
c0ff0571-68ae-4653-9aa5-e4da8d62c869	92a020f4-c327-4f4d-8df3-c7ed0d120871	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:33:45.141969+00	2026-02-05 21:33:45.141969+00	39219340-21cb-4a88-a939-93baf1a0e840	39219340-21cb-4a88-a939-93baf1a0e840	\N
d6104529-6570-4fe5-bc22-fa3a9d232ce1	96ce9467-4d9c-42ac-8fd7-6b4980cb4662	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:34:41.143243+00	2026-02-05 21:34:41.143243+00	5368cfba-bae0-4132-88e4-4fde67d9e523	5368cfba-bae0-4132-88e4-4fde67d9e523	\N
3eb45481-89c5-4a87-8e3d-91d4a2d60819	2328d476-0c17-4452-adc8-7cf00f24669b	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:36:32.634085+00	2026-02-05 21:36:32.634085+00	222968c5-f7cd-46a9-80a7-ae6d0557b5c3	222968c5-f7cd-46a9-80a7-ae6d0557b5c3	\N
23bd05f9-b2e7-412d-95e2-3ff7b45cbb46	9e0c3eda-2c52-4792-abd4-288131229066	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:39:33.585828+00	2026-02-05 21:39:33.585828+00	2b8bb712-3cfe-435e-84f7-49dfe73d641b	2b8bb712-3cfe-435e-84f7-49dfe73d641b	\N
44d4750b-3477-47c4-91c3-585d41b5d6df	c5992875-1ecb-42f0-b461-e177f1775d46	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:40:37.527586+00	2026-02-05 21:40:37.527586+00	ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f	ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f	\N
0a974e46-ced3-4a5c-bd2e-63cc1272cd1d	f878c129-1bbb-4dca-bcfc-d21ea54fb41f	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:41:47.269923+00	2026-02-05 21:41:47.269923+00	eb271702-3161-48b2-a4c9-8747819b7ae7	eb271702-3161-48b2-a4c9-8747819b7ae7	\N
11921704-4567-49d4-ab50-389eb3244c9f	1d66de05-6ab3-461b-94d0-0750153aa2d9	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:43:42.645666+00	2026-02-05 21:43:42.645666+00	31148b05-1512-43ce-8b01-fd3b423fca6e	31148b05-1512-43ce-8b01-fd3b423fca6e	\N
d5c905a8-e8bc-461f-9a4b-59f7222b96ca	8229af4d-838a-4d32-ac0b-9eadffbbcff8	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:49:55.033421+00	2026-02-05 21:49:55.033421+00	3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167	3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167	\N
2b7519d8-2dab-470d-8de5-ca41a7684e13	b86839bf-62f6-4f3c-8748-5bdeaaa323a6	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:52:18.764933+00	2026-02-05 21:52:18.764933+00	83e1d52b-a86b-461a-b995-e79e2ac57878	83e1d52b-a86b-461a-b995-e79e2ac57878	\N
a765e151-2bc0-4030-a764-4471e772b546	dcb6e693-f204-46fd-bbca-8eab795cc81a	Test Farm	\N	\N	\N	\N	\N	0101000020E610000000000000000000000000000000000000	0103000020E6100000010000000500000000000000000000000000000000000000000000000000F03F0000000000000000000000000000F03F000000000000F03F0000000000000000000000000000F03F00000000000000000000000000000000	10.0000	\N	{}	\N	t	2026-02-05 21:55:18.536409+00	2026-02-05 21:55:18.536409+00	1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3	1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3	\N
e5fa230d-d05d-4afa-b672-f097057c8993	f2d7a38d-6265-4cd5-9743-be932e8693c0	Test Farm 1770328661	Test farm for audit E2E testing	\N	\N	\N	\N	0101000020E6100000E78C28ED0D6653405396218E75F12940	0103000020E61000000100000005000000BC74931804665340FED478E926F12940AE47E17A14665340FED478E926F12940AE47E17A146653408B6CE7FBA9F12940BC749318046653408B6CE7FBA9F12940BC74931804665340FED478E926F12940	10.5000	\N	{}	\N	t	2026-02-05 21:57:41.74848+00	2026-02-05 21:57:41.74848+00	088ad156-635f-4689-8a9f-31187419e964	088ad156-635f-4689-8a9f-31187419e964	\N
fe011730-4986-4034-9815-f7650216b5a5	a7bc280f-69bc-4b03-98d8-de195f8f95bf	Test Farm 1770330826	Test farm for audit E2E testing	\N	\N	\N	\N	0101000020E6100000E78C28ED0D6653405396218E75F12940	0103000020E61000000100000005000000BC74931804665340FED478E926F12940AE47E17A14665340FED478E926F12940AE47E17A146653408B6CE7FBA9F12940BC749318046653408B6CE7FBA9F12940BC74931804665340FED478E926F12940	10.5000	\N	{}	\N	t	2026-02-05 22:33:46.382136+00	2026-02-05 22:33:46.382136+00	723079fb-4d41-408d-958c-a1d417576d82	723079fb-4d41-408d-958c-a1d417576d82	\N
748bf7fa-ee25-49a9-b735-eb86c450e8ae	5ae66809-e7de-448a-8f42-920a192c8704	Sagdara	sadasd	Pune 	Pune	Maharshtra 	413401	0101000020E61000007B14AE47E1EA5040EC51B81E852B4140	\N	234.0000	\N	{"ownership_type": "owned", "irrigation_mode_ids": ["sprinkler"]}	\N	t	2026-01-30 00:15:18.081526+00	2026-02-09 13:55:34.790382+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	Pune
\.


--
-- Data for Name: finance_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_categories (id, transaction_type, code, is_system_defined, owner_org_id, sort_order, is_active, created_at, updated_at, created_by, updated_by) FROM stdin;
dc0ad4cb-1f62-46b4-b535-d720ae5537ac	INCOME	CROP_SALE	t	\N	1	t	2026-01-30 00:05:41.371909+00	2026-01-30 00:05:41.371909+00	\N	\N
fffabea9-8b9c-4af2-81a2-07f50bb7363b	INCOME	SUBSIDY	t	\N	2	t	2026-01-30 00:05:41.371909+00	2026-01-30 00:05:41.371909+00	\N	\N
32e502f5-0a9f-4ab0-8574-3a6220b70a70	INCOME	GRANT	t	\N	3	t	2026-01-30 00:05:41.371909+00	2026-01-30 00:05:41.371909+00	\N	\N
cddf03b5-19b3-4344-b8b8-750bebac98a5	INCOME	OTHER_INCOME	t	\N	4	t	2026-01-30 00:05:41.371909+00	2026-01-30 00:05:41.371909+00	\N	\N
eec660d1-6f65-49e7-ad48-2a9461838ff6	EXPENSE	SEEDS	t	\N	1	t	2026-01-30 00:05:41.382289+00	2026-01-30 00:05:41.382289+00	\N	\N
dc3ecb50-29e0-45c9-b48e-971a9f98a30c	EXPENSE	FERTILIZER	t	\N	2	t	2026-01-30 00:05:41.382289+00	2026-01-30 00:05:41.382289+00	\N	\N
10a962cd-2df5-41c9-83af-824b60c81663	EXPENSE	PESTICIDE	t	\N	3	t	2026-01-30 00:05:41.382289+00	2026-01-30 00:05:41.382289+00	\N	\N
403b700e-f3ac-4b64-9cda-6aa0b27bfa4b	EXPENSE	LABOR	t	\N	4	t	2026-01-30 00:05:41.382289+00	2026-01-30 00:05:41.382289+00	\N	\N
f74b02da-cb64-4b69-8379-f9f96c87ae4e	EXPENSE	EQUIPMENT	t	\N	5	t	2026-01-30 00:05:41.382289+00	2026-01-30 00:05:41.382289+00	\N	\N
634afbd4-71d5-4402-b8a5-07c7e03a0882	EXPENSE	IRRIGATION	t	\N	6	t	2026-01-30 00:05:41.382289+00	2026-01-30 00:05:41.382289+00	\N	\N
da0e27d8-f78c-44cf-8941-a95bd5a070c6	EXPENSE	TRANSPORT	t	\N	7	t	2026-01-30 00:05:41.382289+00	2026-01-30 00:05:41.382289+00	\N	\N
9043a9a8-3835-4ad9-a26b-c4112e0568a3	EXPENSE	CONSULTANCY	t	\N	8	t	2026-01-30 00:05:41.382289+00	2026-01-30 00:05:41.382289+00	\N	\N
5602d555-e5e4-4fc4-822e-9d9cda9c18cf	EXPENSE	OTHER_EXPENSE	t	\N	9	t	2026-01-30 00:05:41.382289+00	2026-01-30 00:05:41.382289+00	\N	\N
\.


--
-- Data for Name: finance_category_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_category_translations (id, category_id, language_code, name, description, created_at) FROM stdin;
a7bdc08d-6532-4bd3-a7e9-c155fbfcb5b8	dc0ad4cb-1f62-46b4-b535-d720ae5537ac	en	Crop Sale	\N	2026-01-30 00:05:41.392958+00
9af32a1c-46a1-44c5-9aa8-cd5cacd40e34	fffabea9-8b9c-4af2-81a2-07f50bb7363b	en	Subsidy	\N	2026-01-30 00:05:41.392958+00
9cd4f748-43aa-4af5-9612-9c55fc033b7e	32e502f5-0a9f-4ab0-8574-3a6220b70a70	en	Grant	\N	2026-01-30 00:05:41.392958+00
8a0bbf12-9541-45d9-a27d-6727a3ef63ab	cddf03b5-19b3-4344-b8b8-750bebac98a5	en	Other Income	\N	2026-01-30 00:05:41.392958+00
6e412142-5908-4220-a003-f6ef0ac77eca	eec660d1-6f65-49e7-ad48-2a9461838ff6	en	Seeds	\N	2026-01-30 00:05:41.392958+00
82325b10-1d21-4150-99bb-040944de2ae1	dc3ecb50-29e0-45c9-b48e-971a9f98a30c	en	Fertilizer	\N	2026-01-30 00:05:41.392958+00
e3557f01-fb00-43be-84c0-30288cc5de04	10a962cd-2df5-41c9-83af-824b60c81663	en	Pesticide	\N	2026-01-30 00:05:41.392958+00
54cd0e7d-bed7-432f-ad3c-6615a96565ca	403b700e-f3ac-4b64-9cda-6aa0b27bfa4b	en	Labor	\N	2026-01-30 00:05:41.392958+00
fec5833c-6aeb-468e-b5bb-38e5a59a03e8	f74b02da-cb64-4b69-8379-f9f96c87ae4e	en	Equipment	\N	2026-01-30 00:05:41.392958+00
9cc4ccec-b4eb-4c60-b113-0d974f689b5a	634afbd4-71d5-4402-b8a5-07c7e03a0882	en	Irrigation	\N	2026-01-30 00:05:41.392958+00
b5c65859-45bb-4418-850e-97848d51511f	da0e27d8-f78c-44cf-8941-a95bd5a070c6	en	Transport	\N	2026-01-30 00:05:41.392958+00
9c2cc128-ad89-4a15-8703-59b15fccc693	9043a9a8-3835-4ad9-a26b-c4112e0568a3	en	Consultancy	\N	2026-01-30 00:05:41.392958+00
a8ce5767-c117-4ca5-947d-d35ff51a525a	5602d555-e5e4-4fc4-822e-9d9cda9c18cf	en	Other Expense	\N	2026-01-30 00:05:41.392958+00
7d0fdd16-9792-41c4-85ff-0c0044f4609d	dc0ad4cb-1f62-46b4-b535-d720ae5537ac	ta	பயிர் விற்பனை	\N	2026-01-30 00:05:41.392958+00
5cdfaf3c-7518-4032-93aa-c781bc2399ba	fffabea9-8b9c-4af2-81a2-07f50bb7363b	ta	மானியம்	\N	2026-01-30 00:05:41.392958+00
cd718807-64c8-43de-a851-66426e4151c8	32e502f5-0a9f-4ab0-8574-3a6220b70a70	ta	நிதி உதவி	\N	2026-01-30 00:05:41.392958+00
e611e481-5439-4b39-86b6-3cda2a4fda1f	cddf03b5-19b3-4344-b8b8-750bebac98a5	ta	மற்ற வருமானம்	\N	2026-01-30 00:05:41.392958+00
a43e2e2a-c7ba-4c08-a70c-d97e3935f508	eec660d1-6f65-49e7-ad48-2a9461838ff6	ta	விதைகள்	\N	2026-01-30 00:05:41.392958+00
fd6ecf95-8b5a-443c-a58e-6b19c97ffe99	dc3ecb50-29e0-45c9-b48e-971a9f98a30c	ta	உரம்	\N	2026-01-30 00:05:41.392958+00
405cf985-2c7b-468e-991a-88876caa5f47	10a962cd-2df5-41c9-83af-824b60c81663	ta	பூச்சிக்கொல்லி	\N	2026-01-30 00:05:41.392958+00
0406edf2-2e18-4f92-bbe7-e5ce026fde5c	403b700e-f3ac-4b64-9cda-6aa0b27bfa4b	ta	தொழிலாளர்	\N	2026-01-30 00:05:41.392958+00
d4f27483-b590-42c8-9a33-a07924305330	f74b02da-cb64-4b69-8379-f9f96c87ae4e	ta	உபகரணங்கள்	\N	2026-01-30 00:05:41.392958+00
bb9b0953-1a84-4ec1-8e20-bc78a1dec06d	634afbd4-71d5-4402-b8a5-07c7e03a0882	ta	நீர்ப்பாசனம்	\N	2026-01-30 00:05:41.392958+00
8ec3a740-0b60-4d00-b942-9a36b82bb18b	da0e27d8-f78c-44cf-8941-a95bd5a070c6	ta	போக்குவரத்து	\N	2026-01-30 00:05:41.392958+00
2a138e56-2d12-4658-90d1-8cfadbc243cd	9043a9a8-3835-4ad9-a26b-c4112e0568a3	ta	ஆலோசனை	\N	2026-01-30 00:05:41.392958+00
58009e78-bfb2-42cf-ba2a-7574746fc480	5602d555-e5e4-4fc4-822e-9d9cda9c18cf	ta	மற்ற செலவு	\N	2026-01-30 00:05:41.392958+00
\.


--
-- Data for Name: finance_transaction_attachments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_transaction_attachments (id, transaction_id, file_url, file_key, file_name, file_type, file_size, uploaded_at, uploaded_by) FROM stdin;
\.


--
-- Data for Name: finance_transaction_splits; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_transaction_splits (id, transaction_id, farm_id, plot_id, crop_id, split_amount, notes, created_at, created_by) FROM stdin;
\.


--
-- Data for Name: finance_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_transactions (id, organization_id, transaction_type, category_id, transaction_date, amount, currency, description, reference_number, created_at, updated_at, created_by, updated_by) FROM stdin;
\.


--
-- Data for Name: fsp_approval_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fsp_approval_documents (id, fsp_organization_id, document_type, file_url, file_key, file_name, uploaded_at, uploaded_by) FROM stdin;
\.


--
-- Data for Name: fsp_service_listings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fsp_service_listings (id, fsp_organization_id, service_id, title, description, service_area_districts, pricing_model, base_price, currency, status, created_at, updated_at, created_by, updated_by) FROM stdin;
3fca08f9-b0f2-4bcb-a2dc-6ba2483830fa	8b411c61-9885-4672-ba08-e45709934575	0f1af256-34e6-471a-a661-5302b4377e1a	GreenOps Expert Consultation	Expert advice from our top agronomists	\N	FIXED	1000.00	INR	ACTIVE	2026-01-30 00:08:38.912363+00	2026-01-30 00:08:38.912363+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
55543d74-5711-48e2-8c7f-e518c295c578	8b411c61-9885-4672-ba08-e45709934575	3ab70420-d250-4756-bb4c-a7c65c57c67c	Standard Soil Audit	Professional soil testing and analysis service	{Erode,Coimbatore}	FIXED	501.00	INR	ACTIVE	2026-01-30 00:09:33.180136+00	2026-02-09 17:56:17.75158+00	08c368c7-0ea2-4dad-a5fe-5e8e180b0b44	3f3a3a39-d867-45a8-b901-74a7e27c95f3
\.


--
-- Data for Name: input_item_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.input_item_categories (id, code, is_system_defined, owner_org_id, sort_order, is_active, created_at, updated_at, created_by, updated_by) FROM stdin;
d78d88cf-5750-4dcf-8ed4-5128c182b56d	FERTILIZER	t	\N	1	t	2026-01-30 00:05:41.307788+00	2026-01-30 00:05:41.307788+00	\N	\N
278f12d7-eb75-4869-842e-65b5cfb107f8	PESTICIDE	t	\N	2	t	2026-01-30 00:05:41.307788+00	2026-01-30 00:05:41.307788+00	\N	\N
b1cea713-56a3-4627-9d5d-c7639fa3bb0c	HERBICIDE	t	\N	3	t	2026-01-30 00:05:41.307788+00	2026-01-30 00:05:41.307788+00	\N	\N
0f0edcfc-088b-4783-a7a9-1388aad240ca	FYM	t	\N	4	t	2026-01-30 00:05:41.307788+00	2026-01-30 00:05:41.307788+00	\N	\N
e09038a0-35d8-47c3-ac22-4673910e1780	GROWTH_REGULATOR	t	\N	5	t	2026-01-30 00:05:41.307788+00	2026-01-30 00:05:41.307788+00	\N	\N
e0b78688-2e4c-4c8c-a46e-e791f18df3dc	BIO	t	\N	0	t	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00	\N	\N
a7f120d6-7bfb-4acf-b602-ac191c1762a7	ORGANIC	t	\N	0	t	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00	\N	\N
\.


--
-- Data for Name: input_item_category_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.input_item_category_translations (id, category_id, language_code, name, description, created_at) FROM stdin;
4eddc98a-e42c-45d9-8fcc-136c8c07e791	d78d88cf-5750-4dcf-8ed4-5128c182b56d	en	Fertilizer	\N	2026-01-30 00:05:41.318395+00
a1e685fc-de4a-4b46-b140-410ea3d46bde	278f12d7-eb75-4869-842e-65b5cfb107f8	en	Pesticide	\N	2026-01-30 00:05:41.318395+00
80687239-e1d4-4bb4-90a7-0c48c68e6a49	b1cea713-56a3-4627-9d5d-c7639fa3bb0c	en	Herbicide	\N	2026-01-30 00:05:41.318395+00
6a49aad6-b5d2-4efb-86f5-6232f1316dbf	0f0edcfc-088b-4783-a7a9-1388aad240ca	en	Farm Yard Manure	\N	2026-01-30 00:05:41.318395+00
10654185-b6f9-4f25-a6ae-e9b7e4024590	e09038a0-35d8-47c3-ac22-4673910e1780	en	Growth Regulator	\N	2026-01-30 00:05:41.318395+00
1cf6c17e-e3aa-43a3-a99b-b880e9c6e2b3	d78d88cf-5750-4dcf-8ed4-5128c182b56d	ta	உரம்	\N	2026-01-30 00:05:41.318395+00
329cac94-5026-49e2-9765-26aa8ab5079d	278f12d7-eb75-4869-842e-65b5cfb107f8	ta	பூச்சிக்கொல்லி	\N	2026-01-30 00:05:41.318395+00
1fa5dd5d-176e-47c3-9e66-89388b12913c	b1cea713-56a3-4627-9d5d-c7639fa3bb0c	ta	களைக்கொல்லி	\N	2026-01-30 00:05:41.318395+00
60194509-95d5-4c2b-b47e-017cd7aa994d	0f0edcfc-088b-4783-a7a9-1388aad240ca	ta	தொழு உரம்	\N	2026-01-30 00:05:41.318395+00
fb7540c6-f57d-41cf-bce7-dd02cfcb37cb	e09038a0-35d8-47c3-ac22-4673910e1780	ta	வளர்ச்சி ஊக்கி	\N	2026-01-30 00:05:41.318395+00
081e5646-f7db-4b90-bd9a-448c7035d05e	d78d88cf-5750-4dcf-8ed4-5128c182b56d	ml	വളം	\N	2026-01-30 00:05:41.318395+00
811d8758-9943-4aa7-9c8d-4639c2036727	278f12d7-eb75-4869-842e-65b5cfb107f8	ml	കീടനാശിനി	\N	2026-01-30 00:05:41.318395+00
d8ffa12f-c140-4d67-b064-8a4ff48fdea8	b1cea713-56a3-4627-9d5d-c7639fa3bb0c	ml	കളനാശിനി	\N	2026-01-30 00:05:41.318395+00
b8922c9e-b34e-434a-b4f5-a8d4ec7158f5	0f0edcfc-088b-4783-a7a9-1388aad240ca	ml	ജൈവവളം	\N	2026-01-30 00:05:41.318395+00
f2f1251e-8438-4491-977d-09591a83413e	e09038a0-35d8-47c3-ac22-4673910e1780	ml	വളർച്ച നിയന്ത്രകം	\N	2026-01-30 00:05:41.318395+00
9d3b7975-9eff-488a-8168-6b479a0af27f	e0b78688-2e4c-4c8c-a46e-e791f18df3dc	en	Bio	Biological inputs	2026-01-30 10:00:39.742302+00
87d029c2-b94f-483b-a16d-484fe647b2c1	a7f120d6-7bfb-4acf-b602-ac191c1762a7	en	Organic	Organic fertilizers and inputs	2026-01-30 10:00:39.742302+00
\.


--
-- Data for Name: input_item_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.input_item_translations (id, input_item_id, language_code, name, description, created_at) FROM stdin;
5a73a7b2-67c3-43a8-9700-ded841b8177c	748c9b60-5f96-4145-a656-07f2fffdeab1	en	Urea	\N	2026-01-30 00:05:41.339466+00
2f38583a-9a90-4ec7-b61d-e6ecfc9dc433	cd016288-5777-4cb2-ae8e-020efc8e0ef1	en	DAP (Di-Ammonium Phosphate)	\N	2026-01-30 00:05:41.339466+00
3e29e36e-2972-4ab7-a5e8-1957e4e10023	ef392715-3980-4a4a-9181-d87de2f4108f	en	NPK 19:19:19	\N	2026-01-30 00:05:41.339466+00
6dafcef5-26be-434f-9ff2-c0fb6d83a1b3	748c9b60-5f96-4145-a656-07f2fffdeab1	ta	யூரியா	\N	2026-01-30 00:05:41.339466+00
cda481dc-53fc-402c-afb6-a8de91899ed5	cd016288-5777-4cb2-ae8e-020efc8e0ef1	ta	டி.ஏ.பி	\N	2026-01-30 00:05:41.339466+00
64ba49a6-c192-43e0-8385-1c8170685855	ef392715-3980-4a4a-9181-d87de2f4108f	ta	என்.பி.கே 19:19:19	\N	2026-01-30 00:05:41.339466+00
90abf60d-173c-4d62-9036-68748ff4a834	748c9b60-5f96-4145-a656-07f2fffdeab1	ml	യൂറിയ	\N	2026-01-30 00:05:41.339466+00
4a6fc431-14c6-4b22-866a-e58c9df2ec15	cd016288-5777-4cb2-ae8e-020efc8e0ef1	ml	ഡി.എ.പി	\N	2026-01-30 00:05:41.339466+00
294a471c-b5c6-4adc-9761-acc820e66dcf	ef392715-3980-4a4a-9181-d87de2f4108f	ml	എൻ.പി.കെ 19:19:19	\N	2026-01-30 00:05:41.339466+00
b192b080-ff47-4fe5-9ee8-4a065b025ad1	41d27f6d-799e-4ed6-8322-2604c920825c	en	Potassium Nitrate	\N	2026-01-30 00:05:41.829048+00
e2546726-437f-4f0c-87b0-a53887c6c32f	ffd160cc-4f56-46fc-bfa5-f8de3deaebb7	en	Calcium Nitrate	\N	2026-01-30 00:05:41.829048+00
d31d6db6-5086-4839-875b-8c81ca103fca	8888fe1b-9278-4700-a5a9-665110c55603	en	Magnesium Nitrate	\N	2026-01-30 00:05:41.829048+00
f936eb42-11c6-46ea-9fca-706daef34f19	7e0d3feb-ca99-407b-b594-e3ee6793fe4c	en	Ferrous Sulphate	\N	2026-01-30 00:05:41.829048+00
3c5034df-986e-47f9-95f8-10012ae59c71	06a705e8-db05-44aa-a059-ce210dcba56c	en	Zinc Sulphate	\N	2026-01-30 00:05:41.829048+00
e2d8cbf5-fff3-41c3-9b10-cb94d91b25d4	93c16bb1-e4d0-4d83-a0b1-c44d8a645f69	en	Magnesium Sulphate	\N	2026-01-30 00:05:41.829048+00
0d2b1691-24f8-4cf8-a17c-a1c43ee5c369	8486fd0d-200a-4494-9689-a2f2bdce86dc	en	Sulphate of Potash (SOP)	\N	2026-01-30 00:05:41.829048+00
97170629-748e-4b74-a653-9fd694342e76	16c72432-bcf3-4e13-9a9a-156fa369bf68	en	Mono Ammonium Phosphate (MAP)	\N	2026-01-30 00:05:41.829048+00
2d5124ef-9b93-4db3-ae61-00b43ef904e6	3af7fc16-0a87-4b0c-aff7-cac7e8c7e13f	en	Mono Potassium Phosphate (MKP)	\N	2026-01-30 00:05:41.829048+00
e1840a0e-dd6c-4ed2-8a82-3880955a2dd9	d3d6e49e-8956-42c9-9a6b-437da6205031	en	Boron (Boric acid / Borax)	\N	2026-01-30 00:05:41.829048+00
37f68aeb-5b92-4321-a149-a097184238f9	4e740fd0-c987-4dd5-9dc5-b5f4063a75dc	en	Copper Sulphate	\N	2026-01-30 00:05:41.829048+00
e3f34ef0-c12d-4594-aff9-952279eb7b33	9ae383cf-fbbe-46e3-ab7e-0ed0ad45247f	en	Manganese Sulphate	\N	2026-01-30 00:05:41.829048+00
6abd6227-e707-4a81-a916-89d1a5634759	522995e6-bdcc-4458-9047-930cd35abed5	en	Fe EDTA 12%	\N	2026-01-30 00:05:41.829048+00
a46ed3c0-439a-4385-aa68-33d318c44a64	c239d36d-654d-43a6-9783-ada387d1415d	en	Zn EDTA 12%	\N	2026-01-30 00:05:41.829048+00
7363c6c9-89bd-42ee-9801-def71831368a	864c67db-6df4-4c9b-825f-cf6cb3d5fac7	en	Ca EDTA (Chelated Calcium)	\N	2026-01-30 00:05:41.829048+00
29578060-7c18-4400-945e-d5ccf159f701	0b9f39be-d821-4071-b231-1d57bb67ee39	en	Ammonium Sulphate	\N	2026-01-30 00:05:41.829048+00
2771939b-6281-4b94-9c45-aa419c1dc51d	41d27f6d-799e-4ed6-8322-2604c920825c	ta	பொட்டாசியம் நைட்ரேட்	\N	2026-01-30 00:05:41.829048+00
18e80a4b-1e2e-4b89-abcc-6ee145f93975	ffd160cc-4f56-46fc-bfa5-f8de3deaebb7	ta	கால்சியம் நைட்ரேட்	\N	2026-01-30 00:05:41.829048+00
eaeca813-3845-427f-8318-6a5aff0b37d3	8888fe1b-9278-4700-a5a9-665110c55603	ta	மெக்னீசியம் நைட்ரேட்	\N	2026-01-30 00:05:41.829048+00
be9b1300-36e5-49c0-9f0d-6a40fff850f3	7e0d3feb-ca99-407b-b594-e3ee6793fe4c	ta	இரும்பு சல்பேட்	\N	2026-01-30 00:05:41.829048+00
2d88c7d6-86d3-476b-b206-dcb217b1e774	06a705e8-db05-44aa-a059-ce210dcba56c	ta	துத்தநாக சல்பேட்	\N	2026-01-30 00:05:41.829048+00
53ac36da-9484-4ee5-9a6d-0467db11546a	93c16bb1-e4d0-4d83-a0b1-c44d8a645f69	ta	மெக்னீசியம் சல்பேட்	\N	2026-01-30 00:05:41.829048+00
0101dc5a-34bf-4007-aafc-2496ebc0da03	8486fd0d-200a-4494-9689-a2f2bdce86dc	ta	பொட்டாஷ் சல்பேட் (SOP)	\N	2026-01-30 00:05:41.829048+00
c4f0ff55-51fb-4ef9-a3dd-ba9d8e5c7945	16c72432-bcf3-4e13-9a9a-156fa369bf68	ta	மோனோ அம்மோனியம் பாஸ்பேட் (MAP)	\N	2026-01-30 00:05:41.829048+00
6e3f374d-0b6a-4bea-863c-3310be7ff6f0	3af7fc16-0a87-4b0c-aff7-cac7e8c7e13f	ta	மோனோ பொட்டாசியம் பாஸ்பேட் (MKP)	\N	2026-01-30 00:05:41.829048+00
01a9e7cd-474c-47b7-b7ad-14a8ffb04699	d3d6e49e-8956-42c9-9a6b-437da6205031	ta	போரான் (போரிக் அமிலம் / போராக்ஸ்)	\N	2026-01-30 00:05:41.829048+00
f22cbddd-da7a-4553-a434-1177e0aaa2d3	4e740fd0-c987-4dd5-9dc5-b5f4063a75dc	ta	காப்பர் சல்பேட்	\N	2026-01-30 00:05:41.829048+00
f903dc65-97ff-4d2f-b203-5d43728c8aa5	9ae383cf-fbbe-46e3-ab7e-0ed0ad45247f	ta	மாங்கனீசு சல்பேட்	\N	2026-01-30 00:05:41.829048+00
f75376c5-49c5-4a4a-9458-a6e4e6d8c1ed	522995e6-bdcc-4458-9047-930cd35abed5	ta	Fe EDTA 12%	\N	2026-01-30 00:05:41.829048+00
476cbff7-fc61-4638-8219-3ec2845e7851	c239d36d-654d-43a6-9783-ada387d1415d	ta	Zn EDTA 12%	\N	2026-01-30 00:05:41.829048+00
6afe6c2c-402c-41a3-b536-34c239e6aa76	864c67db-6df4-4c9b-825f-cf6cb3d5fac7	ta	Ca EDTA (சேலேட்டட் கால்சியம்)	\N	2026-01-30 00:05:41.829048+00
5e3e2e8f-1f30-43df-9222-2a3fd83bd097	0b9f39be-d821-4071-b231-1d57bb67ee39	ta	அம்மோனியம் சல்பேட்	\N	2026-01-30 00:05:41.829048+00
a5bcf9d8-4cb2-46d8-85f8-9fe163c7883a	41d27f6d-799e-4ed6-8322-2604c920825c	ml	പൊട്ടാസ്യം നൈട്രേറ്റ്	\N	2026-01-30 00:05:41.829048+00
287474cb-797c-40b0-9124-0806d1e164cb	ffd160cc-4f56-46fc-bfa5-f8de3deaebb7	ml	കാൽസ്യം നൈട്രേറ്റ്	\N	2026-01-30 00:05:41.829048+00
b506491f-5127-426e-a243-e0e4a5e390ae	8888fe1b-9278-4700-a5a9-665110c55603	ml	മഗ്നീഷ്യം നൈട്രേറ്റ്	\N	2026-01-30 00:05:41.829048+00
0aaaf308-e7d3-481a-b3ee-53a2e2e398cc	7e0d3feb-ca99-407b-b594-e3ee6793fe4c	ml	ഫെറസ് സൾഫേറ്റ്	\N	2026-01-30 00:05:41.829048+00
fa8b00c2-a17a-4430-902c-0b98f3571c39	06a705e8-db05-44aa-a059-ce210dcba56c	ml	സിങ്ക് സൾഫേറ്റ്	\N	2026-01-30 00:05:41.829048+00
9392118d-9cd9-478c-9337-bd6d5d3f426f	93c16bb1-e4d0-4d83-a0b1-c44d8a645f69	ml	മഗ്നീഷ്യം സൾഫേറ്റ്	\N	2026-01-30 00:05:41.829048+00
6a3ba741-f7f9-44f6-8f36-53da891ed3e2	8486fd0d-200a-4494-9689-a2f2bdce86dc	ml	സൾഫേറ്റ് ഓഫ് പൊട്ടാഷ് (SOP)	\N	2026-01-30 00:05:41.829048+00
34c73d06-8fb9-4aa8-b200-530a698f7581	16c72432-bcf3-4e13-9a9a-156fa369bf68	ml	മോണോ അമോണിയം ഫോസ്ഫേറ്റ് (MAP)	\N	2026-01-30 00:05:41.829048+00
4b8ae6d8-491d-46be-b43d-f140a258fafa	3af7fc16-0a87-4b0c-aff7-cac7e8c7e13f	ml	മോണോ പൊട്ടാസ്യം ഫോസ്ഫേറ്റ് (MKP)	\N	2026-01-30 00:05:41.829048+00
0907b53f-596f-4cc5-a4d5-82b2edf4086a	d3d6e49e-8956-42c9-9a6b-437da6205031	ml	ബോറോൺ (ബോറിക് ആസിഡ് / ബോറാക്സ്)	\N	2026-01-30 00:05:41.829048+00
5ea3c0f1-2afb-454c-8f4a-ec763608052b	4e740fd0-c987-4dd5-9dc5-b5f4063a75dc	ml	കോപ്പർ സൾഫേറ്റ്	\N	2026-01-30 00:05:41.829048+00
58e6d06f-1f08-47e2-ab6f-692ad68bb835	9ae383cf-fbbe-46e3-ab7e-0ed0ad45247f	ml	മാംഗനീസ് സൾഫേറ്റ്	\N	2026-01-30 00:05:41.829048+00
b430fc42-ae00-47b5-b4dc-fcc074895fa3	522995e6-bdcc-4458-9047-930cd35abed5	ml	Fe EDTA 12%	\N	2026-01-30 00:05:41.829048+00
58dece7a-2fed-41c1-aede-1f8db6a5c6fe	c239d36d-654d-43a6-9783-ada387d1415d	ml	Zn EDTA 12%	\N	2026-01-30 00:05:41.829048+00
3454a067-46bc-4835-b870-bf97fc7cde2a	864c67db-6df4-4c9b-825f-cf6cb3d5fac7	ml	Ca EDTA (ചീലേറ്റഡ് കാൽസ്യം)	\N	2026-01-30 00:05:41.829048+00
3e1bd3f7-9e8a-4f6e-a786-53c467075a89	0b9f39be-d821-4071-b231-1d57bb67ee39	ml	അമോണിയം സൾഫേറ്റ്	\N	2026-01-30 00:05:41.829048+00
0fa7ad28-1e94-4177-bdd3-c659a5c6d8c1	59b05679-3c61-4744-9c73-2e0b4268d322	en	Actara	\N	2026-01-30 00:05:41.860224+00
e4e1b354-d027-450c-a754-1c92d99a925b	bf2e83f7-398c-469a-bcd5-139e5b9b0f8e	en	Admire	\N	2026-01-30 00:05:41.860224+00
949965b9-00e1-4913-bedb-2d045030f938	76e29b28-548c-4e85-9548-f2d422aa1fdb	en	Confidor	\N	2026-01-30 00:05:41.860224+00
f0c2ff86-893c-4268-8013-54f67ab90b6d	e6728d28-188b-4d2f-9cb1-04ce41929e35	en	Coragen	\N	2026-01-30 00:05:41.860224+00
e7152980-a364-4283-814f-8d9df7d63f4d	28cd3f1c-f239-4f05-acd7-a7e9ebfb03c3	en	Jump	\N	2026-01-30 00:05:41.860224+00
52cdae53-8055-4a1f-82b0-86c82e672ece	23581a2d-de51-46c7-81be-2419def344e5	en	Karate	\N	2026-01-30 00:05:41.860224+00
1d754474-c284-4e97-9a25-49e8758d5417	1735558e-2395-42e5-8f02-ce2f3c68ffed	en	Magister	\N	2026-01-30 00:05:41.860224+00
ee36e4bf-1971-4022-927e-03efb20ad4bc	602fa7f7-8f85-41ac-bf9a-7cebad415014	en	Pegasus	\N	2026-01-30 00:05:41.860224+00
75cb392a-2c6f-4342-bad9-7fdcea4f313c	4916cc1b-2acd-4195-b3df-07c3c09ed699	en	Proclaim	\N	2026-01-30 00:05:41.860224+00
0bef35fa-018a-4738-9099-a6bff14d4be5	47b892ed-fdf5-4ba7-a6d2-174b190755fa	en	Regent	\N	2026-01-30 00:05:41.860224+00
2d6e7ea2-20ad-49c3-866a-f52ade2bf6fd	f2c83414-062f-412c-809f-aa5ba1851ac1	en	Rogor	\N	2026-01-30 00:05:41.860224+00
1cb68050-0380-4465-964c-fa03663e29c2	46f58e98-4515-46bb-9a10-bd08d7b64a74	en	Ulala	\N	2026-01-30 00:05:41.860224+00
6b6b8a97-b7e2-439f-867b-a086b2b38b25	d46a9f8d-9b1f-4254-9411-933ec9f67a0c	en	Gracia	\N	2026-01-30 00:05:41.860224+00
6497b9ce-142d-4b10-8222-afeccf9d317f	15732749-409d-4697-80de-942a3bc4af6f	en	Exponus	\N	2026-01-30 00:05:41.860224+00
dc0ef819-9d20-4b49-b0eb-051dbfcb383a	9cb35d90-246a-4459-b112-03d500d519f0	en	Simodis	\N	2026-01-30 00:05:41.860224+00
4037d594-bad3-4459-b1a9-0624f4949a2a	27475b96-5997-4a2f-b92c-8bfe8cc64aa1	en	Movento Energy	\N	2026-01-30 00:05:41.860224+00
9841afc9-7024-4c9a-8680-05cd849d5e22	a3bb3069-b5b3-47b5-b3c8-d7e43fee16f3	en	Amistar	\N	2026-01-30 00:05:41.860224+00
07e38ccc-cbfb-4f36-a763-8103f75ac24f	7003ade2-773a-4895-b551-fb39cf1cfb7a	en	Amistar Top	\N	2026-01-30 00:05:41.860224+00
d43c100d-0c18-4833-a4a8-a1b78fd38593	e5a7c32d-34a8-4320-b697-1a857f5a2d83	en	Bavistin	\N	2026-01-30 00:05:41.860224+00
487c71ed-9d42-400a-aecc-99cce3d6773b	52c8943a-8212-4ed0-b00a-938db3026083	en	Equation Pro	\N	2026-01-30 00:05:41.860224+00
a6149e4d-2273-40dc-b860-2131d02ca815	c25bc415-46ea-4317-a1e7-c7fafd70625c	en	Kocide	\N	2026-01-30 00:05:41.860224+00
15a41365-fd60-4471-aee6-3c2a4c62cdb4	9e0ce26e-c035-4ddd-80c8-a2538ba2a550	en	Nativo	\N	2026-01-30 00:05:41.860224+00
54912381-b3d2-463a-9e35-15abbfaacf72	e5e5a618-3b14-47d5-8610-b27825170dc6	en	Profiler	\N	2026-01-30 00:05:41.860224+00
87ba9c72-e5b7-40b9-bcc4-2c24bf3d4f16	168e30b0-a0b8-42cc-a5c9-a26159039a2b	en	Ridomil Gold	\N	2026-01-30 00:05:41.860224+00
e199f8e7-3174-4a62-b203-3c99548c088f	c9130bc5-444e-4462-a396-ccc85055f633	en	Galileo Sensa	\N	2026-01-30 00:05:41.860224+00
93d9b149-5461-467d-9119-b413ed11aea4	fb1b4948-a554-4ed1-8359-34b98280befd	en	Safina	\N	2026-01-30 00:05:41.860224+00
f7807e75-f195-4de5-996b-64d1ebce5c08	5baab36f-8a25-4782-bf4f-ab6ed8bac32d	en	Sumiprempt	\N	2026-01-30 00:05:41.860224+00
09691b43-7cef-43fb-8581-aa54fed19a0e	283d93e8-573e-46eb-be76-491a73b43884	en	Custodia	\N	2026-01-30 00:05:41.860224+00
5622e4c7-086c-4d24-8e40-ccd1cba573a6	59fae22e-fcb7-4313-8423-f7207446b95a	en	Salibro	\N	2026-01-30 00:05:41.860224+00
a8cfe2b3-aa41-40a7-bcc4-f58444b77217	2c68eeaf-71ab-463e-b992-5887e2bfb654	en	Tagmycin	\N	2026-01-30 00:05:41.860224+00
5e0ccfeb-8857-49db-9e03-ae7a5406b468	59b05679-3c61-4744-9c73-2e0b4268d322	ta	ஆக்டரா	\N	2026-01-30 00:05:41.860224+00
d554b4ef-449e-400a-8a64-304afe2f83a3	bf2e83f7-398c-469a-bcd5-139e5b9b0f8e	ta	அட்மைர்	\N	2026-01-30 00:05:41.860224+00
9b0311c2-df19-4247-bbd5-ee51818f01fa	76e29b28-548c-4e85-9548-f2d422aa1fdb	ta	கான்ஃபிடர்	\N	2026-01-30 00:05:41.860224+00
4135de67-0e20-4d95-b3ad-3e7fc0358576	e6728d28-188b-4d2f-9cb1-04ce41929e35	ta	கோரஜென்	\N	2026-01-30 00:05:41.860224+00
8d58b2d3-73c5-4a46-b60c-9b9c6fb8ddf9	28cd3f1c-f239-4f05-acd7-a7e9ebfb03c3	ta	ஜம்ப்	\N	2026-01-30 00:05:41.860224+00
98415395-1654-4053-a654-df62b15cd26b	23581a2d-de51-46c7-81be-2419def344e5	ta	கராத்தே	\N	2026-01-30 00:05:41.860224+00
312fc0d8-6626-49ad-b4c8-24bc7e180173	1735558e-2395-42e5-8f02-ce2f3c68ffed	ta	மாஜிஸ்டர்	\N	2026-01-30 00:05:41.860224+00
afaa817f-5292-49d7-b263-35e3f69b66ae	602fa7f7-8f85-41ac-bf9a-7cebad415014	ta	பெகாசஸ்	\N	2026-01-30 00:05:41.860224+00
318e7072-2d4a-4c1c-a67f-97a1c04c9962	4916cc1b-2acd-4195-b3df-07c3c09ed699	ta	பிராக்ளேம்	\N	2026-01-30 00:05:41.860224+00
31c56864-77af-4585-a2b6-273b4fc40dbf	47b892ed-fdf5-4ba7-a6d2-174b190755fa	ta	ரீஜண்ட்	\N	2026-01-30 00:05:41.860224+00
99e9d0b8-c92b-475c-83d2-fcd1d29de693	f2c83414-062f-412c-809f-aa5ba1851ac1	ta	ரோகோர்	\N	2026-01-30 00:05:41.860224+00
97c8d313-f6ae-4256-a2a5-fce3dad1f24e	46f58e98-4515-46bb-9a10-bd08d7b64a74	ta	உலால	\N	2026-01-30 00:05:41.860224+00
aee08048-8d0b-4d54-b490-07255f511595	d46a9f8d-9b1f-4254-9411-933ec9f67a0c	ta	கிரேசியா	\N	2026-01-30 00:05:41.860224+00
af7c781d-29cd-40f9-8998-4f75bd80860c	15732749-409d-4697-80de-942a3bc4af6f	ta	எக்ஸ்போனஸ்	\N	2026-01-30 00:05:41.860224+00
877324b7-2d7c-4f42-a217-f547f6a7a87f	9cb35d90-246a-4459-b112-03d500d519f0	ta	சிமோடிஸ்	\N	2026-01-30 00:05:41.860224+00
3af328b8-ada9-41f3-bf16-59519882451d	27475b96-5997-4a2f-b92c-8bfe8cc64aa1	ta	மூவெண்டோ எனர்ஜி	\N	2026-01-30 00:05:41.860224+00
6db7bec8-12b5-4365-afb1-b41fe0086a78	a3bb3069-b5b3-47b5-b3c8-d7e43fee16f3	ta	அமிஸ்டர்	\N	2026-01-30 00:05:41.860224+00
c514cc5f-416e-4ebd-acdc-d6e53643ed3c	7003ade2-773a-4895-b551-fb39cf1cfb7a	ta	அமிஸ்டர் டாப்	\N	2026-01-30 00:05:41.860224+00
6ea60671-8e07-4231-9ff3-d7ba9ec9a4fc	e5a7c32d-34a8-4320-b697-1a857f5a2d83	ta	பாவிஸ்டின்	\N	2026-01-30 00:05:41.860224+00
ec8648bc-5c09-48d2-8d30-d26cd1e514c1	52c8943a-8212-4ed0-b00a-938db3026083	ta	ஈக்குவேஷன் ப்ரோ	\N	2026-01-30 00:05:41.860224+00
ee3a3d19-7665-4d89-858d-75e2a319220a	c25bc415-46ea-4317-a1e7-c7fafd70625c	ta	கோசைட்	\N	2026-01-30 00:05:41.860224+00
eaa49709-387d-4c20-b14c-43f4fecde8a8	9e0ce26e-c035-4ddd-80c8-a2538ba2a550	ta	நேட்டிவோ	\N	2026-01-30 00:05:41.860224+00
44ea51b3-bbd8-4d08-abbd-3c5ab001bb79	e5e5a618-3b14-47d5-8610-b27825170dc6	ta	பிரோஃபைலர்	\N	2026-01-30 00:05:41.860224+00
62bea6dd-096f-47fd-820e-65110727b381	168e30b0-a0b8-42cc-a5c9-a26159039a2b	ta	ரிடோமில் கோல்டு	\N	2026-01-30 00:05:41.860224+00
324135dd-2a94-404c-95e0-846572ae595f	c9130bc5-444e-4462-a396-ccc85055f633	ta	கலிலியோ சென்சா	\N	2026-01-30 00:05:41.860224+00
e7136e27-5491-4697-b6e4-3e8a27a6cef9	fb1b4948-a554-4ed1-8359-34b98280befd	ta	சஃபினா	\N	2026-01-30 00:05:41.860224+00
3364039c-43d3-4729-a5a0-8d793d2ecfac	5baab36f-8a25-4782-bf4f-ab6ed8bac32d	ta	சுமிப்ரெம்ப்ட்	\N	2026-01-30 00:05:41.860224+00
805afa99-b3c1-47db-b5f1-ccea7deb4ee2	283d93e8-573e-46eb-be76-491a73b43884	ta	கஸ்டோடியா	\N	2026-01-30 00:05:41.860224+00
a7fe3f06-3edd-4a78-9f47-9a9fb98a2bfc	59fae22e-fcb7-4313-8423-f7207446b95a	ta	சாலிப்ரோ	\N	2026-01-30 00:05:41.860224+00
3b846492-a0e0-4b28-a4ef-040870ea51a3	2c68eeaf-71ab-463e-b992-5887e2bfb654	ta	டாக்மைசின்	\N	2026-01-30 00:05:41.860224+00
6522b1f7-01a7-46e7-b3d8-8df55c36c5df	59b05679-3c61-4744-9c73-2e0b4268d322	ml	ആക്താര	\N	2026-01-30 00:05:41.860224+00
134923ef-9677-48cf-9ec5-f75628b00b3a	bf2e83f7-398c-469a-bcd5-139e5b9b0f8e	ml	അഡ്‌മയർ	\N	2026-01-30 00:05:41.860224+00
fd7a6150-9a43-4da9-b673-cdfbbe90f0cc	76e29b28-548c-4e85-9548-f2d422aa1fdb	ml	കോൺഫിഡോർ	\N	2026-01-30 00:05:41.860224+00
0eee7c2a-f5f6-4811-a3f7-2038448f0fb2	e6728d28-188b-4d2f-9cb1-04ce41929e35	ml	കോരജൻ	\N	2026-01-30 00:05:41.860224+00
90229b8a-1f58-4ace-a634-ef831cf6f1f2	28cd3f1c-f239-4f05-acd7-a7e9ebfb03c3	ml	ജമ്പ്	\N	2026-01-30 00:05:41.860224+00
823fd642-36b7-4bd9-96ed-f021d0ab95f1	23581a2d-de51-46c7-81be-2419def344e5	ml	കരാട്ടെ	\N	2026-01-30 00:05:41.860224+00
0d5fb36c-8e5c-45df-a89a-1cdee55dfc67	1735558e-2395-42e5-8f02-ce2f3c68ffed	ml	മജിസ്റ്റർ	\N	2026-01-30 00:05:41.860224+00
d0444ddf-a425-4f0a-8560-cfe46145a212	602fa7f7-8f85-41ac-bf9a-7cebad415014	ml	പെഗാസസ്	\N	2026-01-30 00:05:41.860224+00
d43aa759-0869-4e0a-b407-8089475d1500	4916cc1b-2acd-4195-b3df-07c3c09ed699	ml	പ്രോക്ലെയിം	\N	2026-01-30 00:05:41.860224+00
634a4750-fc00-4dff-aa30-adf710145434	47b892ed-fdf5-4ba7-a6d2-174b190755fa	ml	റീജൻ്റ്	\N	2026-01-30 00:05:41.860224+00
5131965f-737c-4d40-b91c-7f19375677f8	f2c83414-062f-412c-809f-aa5ba1851ac1	ml	റോഗോർ	\N	2026-01-30 00:05:41.860224+00
d29bcd43-e080-4764-82b7-1f1b27966680	46f58e98-4515-46bb-9a10-bd08d7b64a74	ml	ഉലാല	\N	2026-01-30 00:05:41.860224+00
91e85267-ef7f-415d-a08f-ac090ca80521	d46a9f8d-9b1f-4254-9411-933ec9f67a0c	ml	ഗ്രേഷ്യ	\N	2026-01-30 00:05:41.860224+00
bedbbd05-d57b-4217-b05a-8ac9a4c93d6b	15732749-409d-4697-80de-942a3bc4af6f	ml	എക്സ്പോണസ്	\N	2026-01-30 00:05:41.860224+00
1c83212b-9c3b-4690-ae0f-8c05e251fc07	9cb35d90-246a-4459-b112-03d500d519f0	ml	സിമോഡിസ്	\N	2026-01-30 00:05:41.860224+00
2aed41df-5475-4c6c-ab7a-ba4f273a51cc	27475b96-5997-4a2f-b92c-8bfe8cc64aa1	ml	Movento എനർജി	\N	2026-01-30 00:05:41.860224+00
eb35107d-9aae-4c97-963d-28af78e98628	a3bb3069-b5b3-47b5-b3c8-d7e43fee16f3	ml	അമിസ്റ്റാർ	\N	2026-01-30 00:05:41.860224+00
0fa02f0d-25f8-466c-98a6-25c1e03ed48b	7003ade2-773a-4895-b551-fb39cf1cfb7a	ml	അമിസ്റ്റാർ ടോപ്പ്	\N	2026-01-30 00:05:41.860224+00
e5d9616c-3981-4b2e-af67-f0a7f867cf94	e5a7c32d-34a8-4320-b697-1a857f5a2d83	ml	ബാവിസ്റ്റിൻ	\N	2026-01-30 00:05:41.860224+00
87b617a1-800e-47a1-8201-57a68ac2e5c5	52c8943a-8212-4ed0-b00a-938db3026083	ml	 ഇക്വേഷൻ പ്രോ	\N	2026-01-30 00:05:41.860224+00
6878f9d1-67cf-41e6-b3ba-c48fea2db529	c25bc415-46ea-4317-a1e7-c7fafd70625c	ml	കോസിഡെ	\N	2026-01-30 00:05:41.860224+00
13bae0f4-12f1-4b99-99b8-739bb95f00d1	9e0ce26e-c035-4ddd-80c8-a2538ba2a550	ml	നേറ്റിവോ	\N	2026-01-30 00:05:41.860224+00
3dbef5da-f68e-4cdb-bf99-209c954ae22b	e5e5a618-3b14-47d5-8610-b27825170dc6	ml	പ്രൊഫൈലർ	\N	2026-01-30 00:05:41.860224+00
0d339f4d-444f-4a85-b422-9369bc08cf50	168e30b0-a0b8-42cc-a5c9-a26159039a2b	ml	റിഡോമിൽ ഗോൾഡ്	\N	2026-01-30 00:05:41.860224+00
69ea8be2-06c0-4035-9aa1-827fa9f61fd5	c9130bc5-444e-4462-a396-ccc85055f633	ml	ഗലീലിയോ സെൻസ	\N	2026-01-30 00:05:41.860224+00
8c4d0dce-514e-4a12-a99d-d2857d43dd72	fb1b4948-a554-4ed1-8359-34b98280befd	ml	സഫീന	\N	2026-01-30 00:05:41.860224+00
69ab12a4-cc54-4109-9a4f-c21fb9fd632c	5baab36f-8a25-4782-bf4f-ab6ed8bac32d	ml	സുമിപ്രേംപ്റ്റ്	\N	2026-01-30 00:05:41.860224+00
b3d6a0dd-67b2-4b43-9680-c24b75a87975	283d93e8-573e-46eb-be76-491a73b43884	ml	കസ്റ്റോഡിയ	\N	2026-01-30 00:05:41.860224+00
92434323-b589-4401-823a-53df8525e46f	59fae22e-fcb7-4313-8423-f7207446b95a	ml	സാലിബ്രോ	\N	2026-01-30 00:05:41.860224+00
01b5df36-afbe-4021-bfce-517edfb74f89	2c68eeaf-71ab-463e-b992-5887e2bfb654	ml	ടാഗ്മൈസിൻ	\N	2026-01-30 00:05:41.860224+00
\.


--
-- Data for Name: input_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.input_items (id, category_id, code, is_system_defined, owner_org_id, sort_order, is_active, type, default_unit_id, item_metadata, created_at, updated_at, created_by, updated_by) FROM stdin;
748c9b60-5f96-4145-a656-07f2fffdeab1	d78d88cf-5750-4dcf-8ed4-5128c182b56d	UREA	t	\N	1	t	\N	\N	{"npk": "46-0-0"}	2026-01-30 00:05:41.32902+00	2026-01-30 00:05:41.32902+00	\N	\N
cd016288-5777-4cb2-ae8e-020efc8e0ef1	d78d88cf-5750-4dcf-8ed4-5128c182b56d	DAP	t	\N	2	t	\N	\N	{"npk": "18-46-0"}	2026-01-30 00:05:41.32902+00	2026-01-30 00:05:41.32902+00	\N	\N
ef392715-3980-4a4a-9181-d87de2f4108f	d78d88cf-5750-4dcf-8ed4-5128c182b56d	NPK_19_19_19	t	\N	3	t	\N	\N	{"npk": "19-19-19"}	2026-01-30 00:05:41.32902+00	2026-01-30 00:05:41.32902+00	\N	\N
41d27f6d-799e-4ed6-8322-2604c920825c	d78d88cf-5750-4dcf-8ed4-5128c182b56d	POTASSIUM_NITRATE	t	\N	1	t	\N	\N	{"form": "water soluble crystalline / granules", "brand": "Multi-brands", "category": "macronutrient (K,N)", "npk_ratio": "13-0-46", "nutrients": ["Nitrogen 13% (NO3)", "Potassium (K2O) 46%"], "additional": {"common_uses": "foliar spray, fertigation"}, "solubility": "high (water soluble)", "trade_name": "Potassium Nitrate", "manufacturer": "Multi-brands (e.g., Haifa, IFFCO, Mahadhan)", "storage_instructions": "Store in dry, cool place; keep away from moisture"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
ffd160cc-4f56-46fc-bfa5-f8de3deaebb7	d78d88cf-5750-4dcf-8ed4-5128c182b56d	CALCIUM_NITRATE	t	\N	1	t	\N	\N	{"form": "granular / soluble", "brand": "Multi-brands", "category": "secondary nutrient (Ca, N)", "npk_ratio": "15.5-0-0; Ca 18.5%", "nutrients": ["Nitrogen 15.5% (NO3)", "Calcium 18.5% (Ca)"], "additional": {"common_uses": "correct calcium deficiency, foliar and fertigation"}, "solubility": "high (water soluble)", "trade_name": "Calcium Nitrate", "manufacturer": "Multi-brands (e.g., ICL, Utkarsh, Positive Plus)", "storage_instructions": "Keep dry; do not mix with phosphate-containing fertilizers"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
8888fe1b-9278-4700-a5a9-665110c55603	d78d88cf-5750-4dcf-8ed4-5128c182b56d	MAGNESIUM_NITRATE	t	\N	1	t	\N	\N	{"form": "water soluble crystalline", "brand": "Multi-brands", "category": "secondary nutrient (Mg, N)", "npk_ratio": "11-0-0; Mg ~9.6%", "nutrients": ["Nitrogen 11% (NO3)", "Magnesium ~9.6% (Mg)"], "additional": {"note": "Often sold as hexahydrate or other hydrates"}, "solubility": "high", "trade_name": "Magnesium Nitrate", "manufacturer": "Multi-brands (e.g., Haifa, Shiv Chemicals, Utkarsh)", "storage_instructions": "Store dry; avoid mixing with phosphates"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
7e0d3feb-ca99-407b-b594-e3ee6793fe4c	d78d88cf-5750-4dcf-8ed4-5128c182b56d	FERROUS_SULPHATE	t	\N	1	t	\N	\N	{"form": "crystalline powder / granules", "brand": "Multi-brands", "category": "micronutrient (Fe)", "npk_ratio": "Fe ~20%", "nutrients": ["Iron (Fe) ~20% (as FeSO4Â·7H2O)"], "additional": {"common_uses": "soil amendment, foliar Fe source; treat iron chlorosis"}, "solubility": "water soluble", "trade_name": "Ferrous Sulphate", "manufacturer": "Multi-brands (industrial/Ag suppliers)", "storage_instructions": "Store in cool dry place; protect from moisture"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
06a705e8-db05-44aa-a059-ce210dcba56c	d78d88cf-5750-4dcf-8ed4-5128c182b56d	ZINC_SULPHATE	t	\N	1	t	\N	\N	{"form": "crystalline powder / granular", "brand": "Multi-brands", "category": "micronutrient (Zn)", "npk_ratio": "Zn ~21%", "nutrients": ["Zinc (Zn) ~21% (as ZnSO4Â·7H2O)"], "additional": {"common_uses": "soil and foliar application to correct Zn deficiency"}, "solubility": "water soluble", "trade_name": "Zinc Sulphate", "manufacturer": "Multi-brands", "storage_instructions": "Keep dry; store in sealed packaging"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
93c16bb1-e4d0-4d83-a0b1-c44d8a645f69	d78d88cf-5750-4dcf-8ed4-5128c182b56d	MAGNESIUM_SULPHATE	t	\N	1	t	\N	\N	{"form": "crystalline / powder", "brand": "Multi-brands", "category": "secondary nutrient (Mg,S)", "npk_ratio": "Mg ~9.8%; S ~12%", "nutrients": ["Magnesium (Mg) ~9.8% (as MgSO4Â·7H2O)", "Sulfur (S) ~12% (approx)"], "additional": {"common_uses": "foliar and soil application; correct Mg deficiency"}, "solubility": "high (water soluble)", "trade_name": "Magnesium Sulphate", "manufacturer": "Multi-brands", "storage_instructions": "Store dry; hygroscopic"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
8486fd0d-200a-4494-9689-a2f2bdce86dc	d78d88cf-5750-4dcf-8ed4-5128c182b56d	SULPHATE_OF_POTASH_(SOP)	t	\N	1	t	\N	\N	{"form": "crystalline / granule", "brand": "Multi-brands", "category": "macronutrient (K)", "npk_ratio": "0-0-50", "nutrients": ["Potassium (K2O) ~50%"], "additional": {"common_uses": "foliar, fertigation, basal potash source for chloride-sensitive crops"}, "solubility": "moderate to high (water soluble)", "trade_name": "Sulphate of Potash (SOP)", "manufacturer": "Multi-brands (e.g., Haifa, IFFCO)", "storage_instructions": "Keep dry; avoid mixing with chloride-sensitive crops"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
16c72432-bcf3-4e13-9a9a-156fa369bf68	d78d88cf-5750-4dcf-8ed4-5128c182b56d	MONO_AMMONIUM_PHOSPHATE_(MAP)	t	\N	1	t	\N	\N	{"form": "crystalline / water soluble", "brand": "Multi-brands", "category": "macronutrient (N,P)", "npk_ratio": "12-61-0", "nutrients": ["Nitrogen 12% (N)", "P2O5 61% (P)"], "additional": {"common_uses": "starter fertilizer, foliar and fertigation (specialty soluble grades)"}, "solubility": "high", "trade_name": "Mono Ammonium Phosphate (MAP)", "manufacturer": "Multi-brands (e.g., IFFCO, Mahadhan)", "storage_instructions": "Store dry; hygroscopic; avoid mixing with alkaline substances"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
3af7fc16-0a87-4b0c-aff7-cac7e8c7e13f	d78d88cf-5750-4dcf-8ed4-5128c182b56d	MONO_POTASSIUM_PHOSPHATE_(MKP)	t	\N	1	t	\N	\N	{"form": "water soluble crystalline", "brand": "Multi-brands", "category": "macronutrient (P,K)", "npk_ratio": "0-52-34", "nutrients": ["P2O5 52%", "K2O 34%"], "additional": {"common_uses": "foliar, fertigation; pH neutral source of P and K"}, "solubility": "high", "trade_name": "Mono Potassium Phosphate (MKP)", "manufacturer": "Multi-brands (e.g., IFFCO, Haifa)", "storage_instructions": "Store dry in sealed packaging"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
d3d6e49e-8956-42c9-9a6b-437da6205031	d78d88cf-5750-4dcf-8ed4-5128c182b56d	BORON_(BORIC_ACID_/_BORAX)	t	\N	1	t	\N	\N	{"form": "powder / crystalline", "brand": "Multi-brands", "category": "micronutrient (B)", "npk_ratio": "B 17.5% (boric acid) / B ~11% (borax)", "nutrients": ["Boron (B) 17.5% (as boric acid) or ~11% (as borax)"], "additional": {"note": "Specify whether product is boric acid or borax when listing"}, "solubility": "moderate (varies by salt)", "trade_name": "Boron (Boric acid / Borax)", "manufacturer": "Multi-brands", "storage_instructions": "Keep dry; avoid over-application (narrow range)"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
4e740fd0-c987-4dd5-9dc5-b5f4063a75dc	d78d88cf-5750-4dcf-8ed4-5128c182b56d	COPPER_SULPHATE	t	\N	1	t	\N	\N	{"form": "crystalline powder", "brand": "Multi-brands", "category": "micronutrient (Cu)", "npk_ratio": "Cu ~25%", "nutrients": ["Copper (Cu) ~25% (as CuSO4Â·5H2O)"], "additional": {"common_uses": "correct copper deficiency; fungicidal properties in some mixes"}, "solubility": "water soluble", "trade_name": "Copper Sulphate", "manufacturer": "Multi-brands", "storage_instructions": "Store dry; corrosive to metals; keep sealed"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
9ae383cf-fbbe-46e3-ab7e-0ed0ad45247f	d78d88cf-5750-4dcf-8ed4-5128c182b56d	MANGANESE_SULPHATE	t	\N	1	t	\N	\N	{"form": "powder / crystalline", "brand": "Multi-brands", "category": "micronutrient (Mn)", "npk_ratio": "Mn ~30%", "nutrients": ["Manganese (Mn) ~30% (typical anhydrous equiv; hydrate levels vary)"], "additional": {"common_uses": "correct manganese deficiency; foliar and soil application"}, "solubility": "water soluble", "trade_name": "Manganese Sulphate", "manufacturer": "Multi-brands", "storage_instructions": "Store dry; sensitive to air/moisture"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
522995e6-bdcc-4458-9047-930cd35abed5	d78d88cf-5750-4dcf-8ed4-5128c182b56d	FE_EDTA_12%	t	\N	1	t	\N	\N	{"form": "water soluble chelated powder", "brand": "Multi-brands", "category": "chelates (Fe)", "npk_ratio": "Fe 12%", "nutrients": ["Iron (Fe) 12% (as Fe-EDTA chelate)"], "additional": {"application": "foliar spray and fertigation; effective for correcting iron chlorosis"}, "solubility": "high (water soluble)", "trade_name": "Fe EDTA 12%", "manufacturer": "Multi-brands (e.g., Katyayani, Instacheal)", "storage_instructions": "Store in cool dry place; protect from sunlight and moisture"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
c239d36d-654d-43a6-9783-ada387d1415d	d78d88cf-5750-4dcf-8ed4-5128c182b56d	ZN_EDTA_12%	t	\N	1	t	\N	\N	{"form": "water soluble chelated powder", "brand": "Multi-brands", "category": "chelates (Zn)", "npk_ratio": "Zn 12%", "nutrients": ["Zinc (Zn) 12% (as Zn-EDTA chelate)"], "additional": {"application": "foliar spray and fertigation"}, "solubility": "high", "trade_name": "Zn EDTA 12%", "manufacturer": "Multi-brands (e.g., ZinGap, Sahib)", "storage_instructions": "Store dry; avoid alkaline mixing"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
864c67db-6df4-4c9b-825f-cf6cb3d5fac7	d78d88cf-5750-4dcf-8ed4-5128c182b56d	CA_EDTA_(CHELATED_CALCIUM)	t	\N	1	t	\N	\N	{"form": "water soluble chelated powder/liquid", "brand": "Multi-brands", "category": "chelates (Ca)", "npk_ratio": "Ca ~10%", "nutrients": ["Calcium (Ca) ~10% (typical Ca-EDTA)"], "additional": {"note": "Chelated calcium useful for foliar correction where Ca uptake is limited"}, "solubility": "high", "trade_name": "Ca EDTA (Chelated Calcium)", "manufacturer": "Multi-brands", "storage_instructions": "Store cool dry; label dependent"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
0b9f39be-d821-4071-b231-1d57bb67ee39	d78d88cf-5750-4dcf-8ed4-5128c182b56d	AMMONIUM_SULPHATE	t	\N	1	t	\N	\N	{"form": "granular / crystalline", "brand": "Multi-brands", "category": "macronutrient (N,S)", "npk_ratio": "21-0-0; S ~24%", "nutrients": ["Nitrogen 21% (as NH4)", "Sulfur ~24% (as SO4)"], "additional": {"common_uses": "acidifying nitrogen source; soil and fertigation use"}, "solubility": "water soluble", "trade_name": "Ammonium Sulphate", "manufacturer": "Multi-brands (e.g., Coromandel, Nagarjuna)", "storage_instructions": "Store dry; hygroscopic; keep away from alkalies"}	2026-01-30 00:05:41.821968+00	2026-01-30 00:05:41.821968+00	\N	\N
59b05679-3c61-4744-9c73-2e0b4268d322	278f12d7-eb75-4869-842e-65b5cfb107f8	ACTARA	t	\N	1	t	\N	\N	{"form": "WG (Water Dispersible Granule)", "brand": "Syngenta", "category": "insecticide (systemic)", "additional": {}, "solubility": "water dispersible", "trade_name": "Actara", "manufacturer": "Syngenta India Ltd.", "mode_of_action": ["systemic", "translaminar", "ingestion/contact"], "effective_against": ["aphids", "whiteflies", "thrips", "jassids", "leafhoppers"], "active_ingredients": ["Thiamethoxam 25% WG"], "application_method": ["foliar spray", "seed treatment (label dependent)"], "storage_instructions": "Store in original container in a cool, dry place away from direct sunlight and food/feed."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
bf2e83f7-398c-469a-bcd5-139e5b9b0f8e	278f12d7-eb75-4869-842e-65b5cfb107f8	ADMIRE	t	\N	1	t	\N	\N	{"form": "WG (Water Dispersible Granule)", "brand": "Bayer", "category": "insecticide (systemic, neonicotinoid)", "additional": {}, "solubility": "water dispersible", "trade_name": "Admire", "manufacturer": "Bayer CropScience Ltd.", "mode_of_action": ["systemic", "ingestion/contact"], "effective_against": ["sap sucking pests: aphids, jassids, whiteflies, thrips"], "active_ingredients": ["Imidacloprid 70% WG"], "application_method": ["soil drench", "foliar spray", "seed treatment (SKU dependent)"], "storage_instructions": "Keep in original container in cool, dry place; avoid direct sunlight."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
76e29b28-548c-4e85-9548-f2d422aa1fdb	278f12d7-eb75-4869-842e-65b5cfb107f8	CONFIDOR	t	\N	1	t	\N	\N	{"form": "SL (Soluble Liquid)", "brand": "Bayer", "category": "insecticide (systemic, neonicotinoid)", "additional": {}, "solubility": "soluble liquid", "trade_name": "Confidor", "manufacturer": "Bayer CropScience Ltd.", "mode_of_action": ["systemic", "ingestion/contact"], "effective_against": ["aphids, whitefly, thrips, other sucking pests"], "active_ingredients": ["Imidacloprid 17.8% SL"], "application_method": ["foliar spray", "soil application", "seed treatment (label dependent)"], "storage_instructions": "Store in a cool, dry, locked place away from food and feed."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
e6728d28-188b-4d2f-9cb1-04ce41929e35	278f12d7-eb75-4869-842e-65b5cfb107f8	CORAGEN	t	\N	1	t	\N	\N	{"form": "SC (Suspension Concentrate)", "brand": "FMC", "category": "insecticide (anthranilic diamide)", "additional": {"mode_of_action_group": "IRAC Group 28"}, "solubility": "suspension", "trade_name": "Coragen", "manufacturer": "FMC India Pvt. Ltd.", "mode_of_action": ["ingestion/systemic; ryanodine receptor activator (IRAC Group 28)"], "effective_against": ["lepidopteran pests (caterpillars, borers, loopers)"], "active_ingredients": ["Chlorantraniliprole 18.5% SC"], "application_method": ["foliar spray"], "storage_instructions": "Store in original container, tightly closed, in a cool dry place."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
28cd3f1c-f239-4f05-acd7-a7e9ebfb03c3	278f12d7-eb75-4869-842e-65b5cfb107f8	JUMP	t	\N	1	t	\N	\N	{"form": "WG", "brand": "Bayer", "category": "insecticide (phenylpyrazole)", "additional": {}, "solubility": "water dispersible", "trade_name": "Jump", "manufacturer": "Bayer", "mode_of_action": ["contact, stomach action; GABA-gated chloride channel blocker"], "effective_against": ["stem borer, leaf folder, thrips, diamondback moth"], "active_ingredients": ["Fipronil 80% WG"], "application_method": ["foliar spray"], "storage_instructions": "Store in cool dry place."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
23581a2d-de51-46c7-81be-2419def344e5	278f12d7-eb75-4869-842e-65b5cfb107f8	KARATE	t	\N	1	t	\N	\N	{"form": "EC", "brand": "Syngenta", "category": "insecticide (pyrethroid)", "additional": {}, "solubility": "emulsifiable", "trade_name": "Karate", "manufacturer": "Syngenta", "mode_of_action": ["contact and ingestion (sodium channel modulator)"], "effective_against": ["chewing and sucking pests"], "active_ingredients": ["Lambda-cyhalothrin 5% EC"], "application_method": ["foliar spray"], "storage_instructions": "Store in cool dry place."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
1735558e-2395-42e5-8f02-ce2f3c68ffed	278f12d7-eb75-4869-842e-65b5cfb107f8	MAGISTER	t	\N	1	t	\N	\N	{"form": "EC", "brand": "Corteva", "category": "miticide", "additional": {}, "solubility": "emulsifiable", "trade_name": "Magister", "manufacturer": "Corteva", "mode_of_action": ["contact/ingestion"], "effective_against": ["mite pests"], "active_ingredients": ["Fenazaquin 10% EC"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
602fa7f7-8f85-41ac-bf9a-7cebad415014	278f12d7-eb75-4869-842e-65b5cfb107f8	PEGASUS	t	\N	1	t	\N	\N	{"form": "WP", "brand": "Syngenta", "category": "insecticide/miticide", "additional": {}, "solubility": "suspendable", "trade_name": "Pegasus", "manufacturer": "Syngenta", "mode_of_action": ["contact/prolonged residual"], "effective_against": ["mites, some chewing insects"], "active_ingredients": ["Diafenthiuron 50% WP"], "application_method": ["foliar spray"], "storage_instructions": "Store dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
4916cc1b-2acd-4195-b3df-07c3c09ed699	278f12d7-eb75-4869-842e-65b5cfb107f8	PROCLAIM	t	\N	1	t	\N	\N	{"form": "SG", "brand": "Syngenta", "category": "insecticide (avermectin group)", "additional": {}, "solubility": "water dispersible", "trade_name": "Proclaim", "manufacturer": "Syngenta", "mode_of_action": ["ingestion, translaminar"], "effective_against": ["lepidopteran larvae"], "active_ingredients": ["Emamectin benzoate 5% SG"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
47b892ed-fdf5-4ba7-a6d2-174b190755fa	278f12d7-eb75-4869-842e-65b5cfb107f8	REGENT	t	\N	1	t	\N	\N	{"form": "GR", "brand": "Bayer", "category": "insecticide (phenylpyrazole)", "additional": {}, "solubility": "granular", "trade_name": "Regent", "manufacturer": "Bayer", "mode_of_action": ["contact & stomach action"], "effective_against": ["stem borer, leaf folder"], "active_ingredients": ["Fipronil 0.6% GR"], "application_method": ["soil application"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
f2c83414-062f-412c-809f-aa5ba1851ac1	278f12d7-eb75-4869-842e-65b5cfb107f8	ROGOR	t	\N	1	t	\N	\N	{"form": "EC", "brand": "FMC", "category": "insecticide (organophosphate)", "additional": {}, "solubility": "emulsifiable", "trade_name": "Rogor", "manufacturer": "FMC", "mode_of_action": ["systemic/contact"], "effective_against": ["aphids, thrips, mites"], "active_ingredients": ["Dimethoate 30% EC"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
46f58e98-4515-46bb-9a10-bd08d7b64a74	278f12d7-eb75-4869-842e-65b5cfb107f8	ULALA	t	\N	1	t	\N	\N	{"form": "WG", "brand": "UPL", "category": "insecticide (sucking pest)", "additional": {}, "solubility": "water dispersible", "trade_name": "Ulala", "manufacturer": "UPL", "mode_of_action": ["feeding blocker"], "effective_against": ["aphids, jassids, whiteflies"], "active_ingredients": ["Flonicamid 50% WG"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
d46a9f8d-9b1f-4254-9411-933ec9f67a0c	278f12d7-eb75-4869-842e-65b5cfb107f8	GRACIA	t	\N	1	t	\N	\N	{"form": "EC", "brand": "Godrej Agrovet", "category": "insecticide", "additional": {}, "solubility": "emulsifiable", "trade_name": "Gracia", "manufacturer": "Godrej Agrovet", "mode_of_action": ["ingestion/contact"], "effective_against": ["caterpillars"], "active_ingredients": ["Fluxametamide 10% EC"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
15732749-409d-4697-80de-942a3bc4af6f	278f12d7-eb75-4869-842e-65b5cfb107f8	EXPONUS	t	\N	1	t	\N	\N	{"form": "SC", "brand": "BASF", "category": "insecticide", "additional": {}, "solubility": "suspension", "trade_name": "Exponus", "manufacturer": "BASF", "mode_of_action": ["GABA modulator"], "effective_against": ["borers, chewing pests"], "active_ingredients": ["Broflanilide 300 g/L SC"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
9cb35d90-246a-4459-b112-03d500d519f0	278f12d7-eb75-4869-842e-65b5cfb107f8	SIMODIS	t	\N	1	t	\N	\N	{"form": "DC", "brand": "Syngenta", "category": "insecticide", "additional": {}, "solubility": "dispersible", "trade_name": "Simodis", "manufacturer": "Syngenta", "mode_of_action": ["GABA modulator"], "effective_against": ["sucking & chewing pests"], "active_ingredients": ["Isocycloseram 10% DC"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
27475b96-5997-4a2f-b92c-8bfe8cc64aa1	278f12d7-eb75-4869-842e-65b5cfb107f8	MOVENTO_ENERGY	t	\N	1	t	\N	\N	{"form": "OD", "brand": "Bayer", "category": "insecticide (systemic)", "additional": {}, "solubility": "oil dispersion", "trade_name": "Movento Energy", "manufacturer": "Bayer", "mode_of_action": ["two-way systemic"], "effective_against": ["sucking pests"], "active_ingredients": ["Spirotetramat 150 OD"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
a3bb3069-b5b3-47b5-b3c8-d7e43fee16f3	278f12d7-eb75-4869-842e-65b5cfb107f8	AMISTAR	t	\N	1	t	\N	\N	{"form": "SC", "brand": "Syngenta", "category": "fungicide", "additional": {}, "solubility": "suspension", "trade_name": "Amistar", "manufacturer": "Syngenta", "mode_of_action": ["QoI"], "effective_against": ["rust, blight, leaf spot"], "active_ingredients": ["Azoxystrobin 23% SC"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
7003ade2-773a-4895-b551-fb39cf1cfb7a	278f12d7-eb75-4869-842e-65b5cfb107f8	AMISTAR_TOP	t	\N	1	t	\N	\N	{"form": "SC", "brand": "Syngenta", "category": "fungicide (mix)", "additional": {}, "solubility": "suspension", "trade_name": "Amistar Top", "manufacturer": "Syngenta", "mode_of_action": ["QoI + DMI"], "effective_against": ["blights, leaf spots"], "active_ingredients": ["Azoxystrobin 18.2% + Difenoconazole 11.4% SC"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
e5a7c32d-34a8-4320-b697-1a857f5a2d83	278f12d7-eb75-4869-842e-65b5cfb107f8	BAVISTIN	t	\N	1	t	\N	\N	{"form": "WP", "brand": "Multiple", "category": "fungicide", "additional": {}, "solubility": "suspendable", "trade_name": "Bavistin", "manufacturer": "Multiple", "mode_of_action": ["systemic"], "effective_against": ["wilt, rot diseases"], "active_ingredients": ["Carbendazim 50% WP"], "application_method": ["seed treatment", "soil drench", "foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
52c8943a-8212-4ed0-b00a-938db3026083	278f12d7-eb75-4869-842e-65b5cfb107f8	EQUATION_PRO	t	\N	1	t	\N	\N	{"form": "SC/WG", "brand": "Corteva", "category": "fungicide", "additional": {}, "solubility": "varies", "trade_name": "Equation Pro", "manufacturer": "Corteva", "mode_of_action": ["protectant + curative"], "effective_against": ["oomycetes"], "active_ingredients": ["(varies; Corteva SKU)"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
c25bc415-46ea-4317-a1e7-c7fafd70625c	278f12d7-eb75-4869-842e-65b5cfb107f8	KOCIDE	t	\N	1	t	\N	\N	{"form": "DF/WG", "brand": "Corteva", "category": "fungicide/bactericide", "additional": {}, "solubility": "suspendable", "trade_name": "Kocide", "manufacturer": "Corteva", "mode_of_action": ["contact"], "effective_against": ["leaf spots, blights"], "active_ingredients": ["Copper hydroxide"], "application_method": ["foliar spray"], "storage_instructions": "Store dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
9e0ce26e-c035-4ddd-80c8-a2538ba2a550	278f12d7-eb75-4869-842e-65b5cfb107f8	NATIVO	t	\N	1	t	\N	\N	{"form": "WG", "brand": "Bayer", "category": "fungicide (mix)", "additional": {}, "solubility": "water dispersible", "trade_name": "Nativo", "manufacturer": "Bayer", "mode_of_action": ["QoI + DMI"], "effective_against": ["broad fungal diseases"], "active_ingredients": ["Trifloxystrobin 25% + Tebuconazole 50% WG"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
e5e5a618-3b14-47d5-8610-b27825170dc6	278f12d7-eb75-4869-842e-65b5cfb107f8	PROFILER	t	\N	1	t	\N	\N	{"form": "WG", "brand": "Bayer", "category": "fungicide", "additional": {}, "solubility": "water dispersible", "trade_name": "Profiler", "manufacturer": "Bayer", "mode_of_action": ["systemic + contact"], "effective_against": ["downy mildew"], "active_ingredients": ["Fluopicolide 4.44% + Fosetyl-Al 66.67% WG"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
168e30b0-a0b8-42cc-a5c9-a26159039a2b	278f12d7-eb75-4869-842e-65b5cfb107f8	RIDOMIL_GOLD	t	\N	1	t	\N	\N	{"form": "WP", "brand": "Syngenta", "category": "fungicide", "additional": {}, "solubility": "suspendable", "trade_name": "Ridomil Gold", "manufacturer": "Syngenta", "mode_of_action": ["systemic + protectant"], "effective_against": ["late blight, downy mildew"], "active_ingredients": ["Metalaxyl-M 4% + Mancozeb 64% WP"], "application_method": ["foliar spray", "soil drench"], "storage_instructions": "Store dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
c9130bc5-444e-4462-a396-ccc85055f633	278f12d7-eb75-4869-842e-65b5cfb107f8	GALILEO_SENSA	t	\N	1	t	\N	\N	{"form": "SC/WG", "brand": "Corteva", "category": "fungicide", "additional": {}, "solubility": "varies", "trade_name": "Galileo Sensa", "manufacturer": "Corteva", "mode_of_action": ["preventive + curative"], "effective_against": ["blast, mildew"], "active_ingredients": ["(Corteva SKU)"], "application_method": ["foliar spray"], "storage_instructions": "Store dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
fb1b4948-a554-4ed1-8359-34b98280befd	278f12d7-eb75-4869-842e-65b5cfb107f8	SAFINA	t	\N	1	t	\N	\N	{"form": null, "brand": "Multiple", "category": "unknown", "additional": {"notes": "Ambiguous SKU name"}, "solubility": null, "trade_name": "Safina", "manufacturer": null, "mode_of_action": [null], "effective_against": [null], "active_ingredients": [null], "application_method": [null], "storage_instructions": null}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
5baab36f-8a25-4782-bf4f-ab6ed8bac32d	278f12d7-eb75-4869-842e-65b5cfb107f8	SUMIPREMPT	t	\N	1	t	\N	\N	{"form": "EC", "brand": "Sumitomo", "category": "insecticide (mix)", "additional": {}, "solubility": "emulsifiable", "trade_name": "Sumiprempt", "manufacturer": "Sumitomo", "mode_of_action": ["growth regulator + sodium channel modulator"], "effective_against": ["whiteflies", "borers"], "active_ingredients": ["Pyriproxyfen 5% + Fenpropathrin 15% EC"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
283d93e8-573e-46eb-be76-491a73b43884	278f12d7-eb75-4869-842e-65b5cfb107f8	CUSTODIA	t	\N	1	t	\N	\N	{"form": "SC", "brand": "Adama", "category": "fungicide (mix)", "additional": {}, "solubility": "suspension", "trade_name": "Custodia", "manufacturer": "Adama", "mode_of_action": ["QoI + DMI"], "effective_against": ["broad fungal diseases"], "active_ingredients": ["Azoxystrobin 11% + Tebuconazole 18.3% SC"], "application_method": ["foliar spray"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
59fae22e-fcb7-4313-8423-f7207446b95a	278f12d7-eb75-4869-842e-65b5cfb107f8	SALIBRO	t	\N	1	t	\N	\N	{"form": "liquid", "brand": "Corteva", "category": "nematicide", "additional": {}, "solubility": "varies", "trade_name": "Salibro", "manufacturer": "Corteva", "mode_of_action": ["nematicidal"], "effective_against": ["nematodes"], "active_ingredients": ["(Corteva SKU)"], "application_method": ["soil application"], "storage_instructions": "Store cool dry."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
2c68eeaf-71ab-463e-b992-5887e2bfb654	278f12d7-eb75-4869-842e-65b5cfb107f8	TAGMYCIN	t	\N	1	t	\N	\N	{"form": "powder", "brand": "Multiple", "category": "bactericide (antibiotic)", "additional": {"regulatory_note": "Use regulated"}, "solubility": "water soluble", "trade_name": "Tagmycin", "manufacturer": "Multiple", "mode_of_action": ["bactericidal"], "effective_against": ["bacterial leaf spots"], "active_ingredients": ["Streptomycin + Tetracycline"], "application_method": ["foliar spray"], "storage_instructions": "Store away from sunlight."}	2026-01-30 00:05:41.849415+00	2026-01-30 00:05:41.849415+00	\N	\N
\.


--
-- Data for Name: master_service_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.master_service_translations (id, service_id, language_code, display_name, description, created_at) FROM stdin;
cc2bea78-b442-4145-960d-67d41094c81b	3ab70420-d250-4756-bb4c-a7c65c57c67c	en	Consultancy	Agricultural consultancy and advisory services	2026-01-30 00:05:41.120315+00
48690970-1e2c-4f73-a446-bc49e67a5abd	daf88e54-3273-4af6-b12c-9a040c0506fe	en	Training	Training and capacity building services	2026-01-30 00:05:41.120315+00
1de8f84f-3799-44bd-80a4-2f525e54f829	ecff85d0-4a02-4911-a875-13fed994be0b	en	Labor Service	Farm labor and workforce services	2026-01-30 00:05:41.120315+00
e00d1d52-d052-4ea8-aae1-6a9b24676a23	5662c168-5565-483b-8d7e-c009b6d82375	en	Equipment Rental	Farm equipment and machinery rental	2026-01-30 00:05:41.120315+00
8f2db917-908d-4c16-acd6-d27aa04c236b	2d7c2524-9610-44f5-9b06-226d5653cc2f	en	Transport	Agricultural produce transportation services	2026-01-30 00:05:41.120315+00
66f83c15-4d5f-4852-a681-610ca7442b71	3ab70420-d250-4756-bb4c-a7c65c57c67c	ta	ஆலோசனை	Agricultural consultancy and advisory services	2026-01-30 00:05:41.120315+00
d8481ccd-5b2e-4de4-9ead-edfdc354853c	daf88e54-3273-4af6-b12c-9a040c0506fe	ta	பயிற்சி	Training and capacity building services	2026-01-30 00:05:41.120315+00
9e36a732-41aa-4477-824e-413065e1cb38	ecff85d0-4a02-4911-a875-13fed994be0b	ta	தொழிலாளர் சேவை	Farm labor and workforce services	2026-01-30 00:05:41.120315+00
6afbf0d2-6958-41c8-be67-64544ea23c39	5662c168-5565-483b-8d7e-c009b6d82375	ta	உபகரண வாடகை	Farm equipment and machinery rental	2026-01-30 00:05:41.120315+00
746d1315-de7e-4153-aec9-a693550eb861	2d7c2524-9610-44f5-9b06-226d5653cc2f	ta	போக்குவரத்து	Agricultural produce transportation services	2026-01-30 00:05:41.120315+00
2103a8a9-3813-4ec2-8df8-68cbe545e4c8	3ab70420-d250-4756-bb4c-a7c65c57c67c	ml	കൺസൾട്ടൻസി	Agricultural consultancy and advisory services	2026-01-30 00:05:41.120315+00
d5bc9b69-0079-4d44-8f52-04895e31ec11	daf88e54-3273-4af6-b12c-9a040c0506fe	ml	പരിശീലനം	Training and capacity building services	2026-01-30 00:05:41.120315+00
9ccec7dc-bb24-4951-91a5-fc071dbcb925	ecff85d0-4a02-4911-a875-13fed994be0b	ml	തൊഴിൽ സേവനം	Farm labor and workforce services	2026-01-30 00:05:41.120315+00
59a79515-3ce9-4c91-ac06-00668c37bfd6	5662c168-5565-483b-8d7e-c009b6d82375	ml	ഉപകരണ വാടക	Farm equipment and machinery rental	2026-01-30 00:05:41.120315+00
b7c42ca6-286a-4d4f-8e1b-461602aa7623	2d7c2524-9610-44f5-9b06-226d5653cc2f	ml	ഗതാഗതം	Agricultural produce transportation services	2026-01-30 00:05:41.120315+00
07f96f65-b046-44e2-b119-3cdc1ab0f3ba	0f1af256-34e6-471a-a661-5302b4377e1a	en	General Crop Consultation	General consultation for crop health and yield	2026-01-30 00:08:38.908582+00
\.


--
-- Data for Name: master_services; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.master_services (id, code, name, description, status, sort_order, created_at, updated_at) FROM stdin;
3ab70420-d250-4756-bb4c-a7c65c57c67c	CONSULTANCY	Consultancy	Agricultural consultancy and advisory services	ACTIVE	1	2026-01-30 00:05:41.109134+00	2026-01-30 00:05:41.109134+00
daf88e54-3273-4af6-b12c-9a040c0506fe	TRAINING	Training	Training and capacity building services	INACTIVE	2	2026-01-30 00:05:41.109134+00	2026-01-30 00:05:41.109134+00
ecff85d0-4a02-4911-a875-13fed994be0b	LABOR_SERVICE	Labor Service	Farm labor and workforce services	INACTIVE	3	2026-01-30 00:05:41.109134+00	2026-01-30 00:05:41.109134+00
5662c168-5565-483b-8d7e-c009b6d82375	EQUIPMENT_RENTAL	Equipment Rental	Farm equipment and machinery rental	INACTIVE	4	2026-01-30 00:05:41.109134+00	2026-01-30 00:05:41.109134+00
2d7c2524-9610-44f5-9b06-226d5653cc2f	TRANSPORT	Transport	Agricultural produce transportation services	INACTIVE	5	2026-01-30 00:05:41.109134+00	2026-01-30 00:05:41.109134+00
0f1af256-34e6-471a-a661-5302b4377e1a	GEN_CROP_CONSULT	General Crop Consultation	General consultation for crop health and yield	ACTIVE	0	2026-01-30 00:08:38.902461+00	2026-01-30 00:08:38.902461+00
\.


--
-- Data for Name: measurement_unit_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.measurement_unit_translations (id, measurement_unit_id, language_code, name, description, created_at) FROM stdin;
4bc234d8-4cda-49c1-91ca-74cd412229e9	27c45cfe-3f18-417c-be00-de9a0d4ddcf4	en	Square Meter	\N	2026-01-30 00:05:41.255297+00
923f7ecc-57a8-4a6b-b405-21b8323fe01e	7bbe2739-eed9-4892-a070-3495819360dd	en	Square Feet	\N	2026-01-30 00:05:41.255297+00
158e5608-7454-42de-81ca-8b644e90ff44	1f8042a9-b954-4d7f-b17f-2c6ba0a6dbfb	en	Cent	\N	2026-01-30 00:05:41.255297+00
93c84dd6-2bd9-4316-927c-c5ed8aca3c1d	1c6b90ac-ff6b-4c5f-be90-5f33c91725d4	en	Acre	\N	2026-01-30 00:05:41.255297+00
f0a9975d-70e3-4a91-81bf-48c09c193001	687e0563-f59c-4b16-9b84-a5786b0b2ab3	en	Hectare	\N	2026-01-30 00:05:41.255297+00
78139ec8-cf36-4cff-b417-c74318f388d8	904cd0d4-9654-4108-858d-28701fc229be	en	Milliliter	\N	2026-01-30 00:05:41.255297+00
c62306e7-e9a8-4717-9df9-b69214e01ab1	40e5d650-d6b1-4000-8731-ba64b30e74ff	en	Liter	\N	2026-01-30 00:05:41.255297+00
3758c3cb-3507-4b96-83df-fa710a92441f	63a8e7eb-686c-4e4a-b25c-7e59f38e7ce1	en	Gallon	\N	2026-01-30 00:05:41.255297+00
4132cc4f-833b-45c6-b333-8733194eb99f	d3dabbf4-d72e-4df4-83af-362c416c9093	en	Cubic Meter	\N	2026-01-30 00:05:41.255297+00
2e5a9680-4626-42ea-91da-5473edb0b282	0c4fbc7f-b88a-457e-a55b-dd1413ba7ac1	en	Gram	\N	2026-01-30 00:05:41.255297+00
450c6a5e-0ed3-4c29-8633-5e5153d3a633	08607b68-5102-45f3-a0e8-d0da2686b742	en	Kilogram	\N	2026-01-30 00:05:41.255297+00
e0c94147-9828-4001-b41a-3e54b967a8c6	2bf8b40b-ffed-4163-a0e1-94bd4315f574	en	Quintal	\N	2026-01-30 00:05:41.255297+00
406364df-c6bb-4bed-b03e-4f64de85a5cf	f1add34c-1f5f-4388-b7b0-e2132983bc99	en	Tonne	\N	2026-01-30 00:05:41.255297+00
e2812bca-e8f1-4ecd-b9a2-c4d0e2db43fd	327f42a9-a084-4758-bb1b-827af61788fc	en	Pound	\N	2026-01-30 00:05:41.255297+00
ae379f81-5a93-48f0-943a-31e3849a1a7a	011691a3-d6fb-4b00-a7a1-bca1e29362ef	en	Centimeter	\N	2026-01-30 00:05:41.255297+00
ff66bac3-17f5-4077-b271-abed9c2c15ff	4747b9e6-9688-48d7-86fc-009c6ed49064	en	Inch	\N	2026-01-30 00:05:41.255297+00
1714b5bc-851c-4451-8cb6-c11389f544fc	c0c6386d-4cad-429f-99e0-60a6616cc4e8	en	Feet	\N	2026-01-30 00:05:41.255297+00
23909974-636b-4fac-8af7-adb23d640264	aeebcc57-0991-43ce-863b-2454b6c354cc	en	Meter	\N	2026-01-30 00:05:41.255297+00
4ac36b72-22eb-4ad8-8d5c-fd5cb9d9c9bc	826c0489-55be-4e31-86d7-688d93723ee2	en	Kilometer	\N	2026-01-30 00:05:41.255297+00
4e2b1e4a-1e62-4a01-b192-0ea7ea4450d0	7b170349-3c5f-4255-9c2d-fc1314da41df	en	Unit	\N	2026-01-30 00:05:41.255297+00
5fd0bc86-6e86-4d40-9635-1f8ffb4fc68c	9a00f259-2499-46a6-9e57-9917718b67f5	en	Dozen	\N	2026-01-30 00:05:41.255297+00
e33ad9a0-70b8-4ae3-aebf-b5dec92f4249	a3e13992-8d3f-49de-9e40-a7679dea4470	en	Hundred	\N	2026-01-30 00:05:41.255297+00
a4d5bd97-8a8e-43a4-aa1d-234ecdaacf49	27c45cfe-3f18-417c-be00-de9a0d4ddcf4	ta	சதுர மீட்டர்	\N	2026-01-30 00:05:41.255297+00
7be1c93c-5a2d-4cb4-afdb-85e5d8a140cb	7bbe2739-eed9-4892-a070-3495819360dd	ta	சதுர அடி	\N	2026-01-30 00:05:41.255297+00
90146eae-6c1e-4680-bb1d-4704c5095f02	1f8042a9-b954-4d7f-b17f-2c6ba0a6dbfb	ta	சென்ட்	\N	2026-01-30 00:05:41.255297+00
11ecce55-22ea-481a-be5d-23bb1899c339	1c6b90ac-ff6b-4c5f-be90-5f33c91725d4	ta	ஏக்கர்	\N	2026-01-30 00:05:41.255297+00
74cbd8d4-e279-4a37-a5f2-754615c76059	687e0563-f59c-4b16-9b84-a5786b0b2ab3	ta	ஹெக்டேர்	\N	2026-01-30 00:05:41.255297+00
11eab63f-c039-4ca6-be26-6e2d7651389a	904cd0d4-9654-4108-858d-28701fc229be	ta	மில்லி லிட்டர்	\N	2026-01-30 00:05:41.255297+00
7f771ff8-f257-43fb-a765-19cfacd8619c	40e5d650-d6b1-4000-8731-ba64b30e74ff	ta	லிட்டர்	\N	2026-01-30 00:05:41.255297+00
86a3e0d8-1792-4734-80a4-433bea359177	63a8e7eb-686c-4e4a-b25c-7e59f38e7ce1	ta	கேலன்	\N	2026-01-30 00:05:41.255297+00
2b327f87-4f43-496f-a407-bbd77d3b79b0	d3dabbf4-d72e-4df4-83af-362c416c9093	ta	கன மீட்டர்	\N	2026-01-30 00:05:41.255297+00
10b76bbd-ee1c-42ad-8491-660504a3ea04	0c4fbc7f-b88a-457e-a55b-dd1413ba7ac1	ta	கிராம்	\N	2026-01-30 00:05:41.255297+00
57db6fdc-2110-42cf-845f-dc008178e51e	08607b68-5102-45f3-a0e8-d0da2686b742	ta	கிலோகிராம்	\N	2026-01-30 00:05:41.255297+00
3bf997b1-0e0d-453e-96c3-e217f01debb3	2bf8b40b-ffed-4163-a0e1-94bd4315f574	ta	குவிண்டால்	\N	2026-01-30 00:05:41.255297+00
f37deb6a-c83d-4814-9850-e13c564ae489	f1add34c-1f5f-4388-b7b0-e2132983bc99	ta	டன்	\N	2026-01-30 00:05:41.255297+00
3a28923f-f7fe-4356-ab69-72b885f502ce	327f42a9-a084-4758-bb1b-827af61788fc	ta	பவுண்ட்	\N	2026-01-30 00:05:41.255297+00
c796129e-1fb4-4b2d-a45f-a4ec80e4ac34	011691a3-d6fb-4b00-a7a1-bca1e29362ef	ta	சென்டிமீட்டர்	\N	2026-01-30 00:05:41.255297+00
e23e3570-5e63-4f59-9403-29aaf1ed9721	4747b9e6-9688-48d7-86fc-009c6ed49064	ta	அங்குலம்	\N	2026-01-30 00:05:41.255297+00
00a5355a-38da-438d-a812-90d9f588d3ab	c0c6386d-4cad-429f-99e0-60a6616cc4e8	ta	அடி	\N	2026-01-30 00:05:41.255297+00
dfa3920d-fa3b-4f86-9636-104ca263036c	aeebcc57-0991-43ce-863b-2454b6c354cc	ta	மீட்டர்	\N	2026-01-30 00:05:41.255297+00
4138e216-3737-4dcb-897e-0921b2b5be19	826c0489-55be-4e31-86d7-688d93723ee2	ta	கிலோமீட்டர்	\N	2026-01-30 00:05:41.255297+00
8ea67985-821e-45a5-b17a-ed484ba0aea7	7b170349-3c5f-4255-9c2d-fc1314da41df	ta	அலகு	\N	2026-01-30 00:05:41.255297+00
6e6e9924-8992-4354-9138-e2f80d07bc23	9a00f259-2499-46a6-9e57-9917718b67f5	ta	டஜன்	\N	2026-01-30 00:05:41.255297+00
0f23e9ca-7eb5-4aad-93ef-0207cb1eaac7	a3e13992-8d3f-49de-9e40-a7679dea4470	ta	நூறு	\N	2026-01-30 00:05:41.255297+00
f24493d2-d753-4390-81bc-b0a7fd92fc9b	27c45cfe-3f18-417c-be00-de9a0d4ddcf4	ml	ചതുരശ്ര മീറ്റർ	\N	2026-01-30 00:05:41.255297+00
e488e55e-340d-4c87-8eed-261adc8bc8ff	7bbe2739-eed9-4892-a070-3495819360dd	ml	ചതുരശ്ര അടി	\N	2026-01-30 00:05:41.255297+00
5527c27a-74d7-4f1b-9e6b-08fe8a7c85a5	1f8042a9-b954-4d7f-b17f-2c6ba0a6dbfb	ml	സെന്റ്	\N	2026-01-30 00:05:41.255297+00
0590b427-7206-45fa-9749-e4502c82ed7f	1c6b90ac-ff6b-4c5f-be90-5f33c91725d4	ml	ഏക്കർ	\N	2026-01-30 00:05:41.255297+00
3744d4bf-2a9e-44a2-80cc-a5e91bc22547	687e0563-f59c-4b16-9b84-a5786b0b2ab3	ml	ഹെക്ടർ	\N	2026-01-30 00:05:41.255297+00
74529315-36c6-4a02-81a8-e756492c4a83	904cd0d4-9654-4108-858d-28701fc229be	ml	മില്ലി ലിറ്റർ	\N	2026-01-30 00:05:41.255297+00
336ee2fc-8b9b-4dac-8e02-bd8970b6ae8a	40e5d650-d6b1-4000-8731-ba64b30e74ff	ml	ലിറ്റർ	\N	2026-01-30 00:05:41.255297+00
2f712be6-0120-4e66-8a3c-58088029d453	63a8e7eb-686c-4e4a-b25c-7e59f38e7ce1	ml	ഗാലൻ	\N	2026-01-30 00:05:41.255297+00
d2c2427b-b703-4d4d-9454-891118062885	d3dabbf4-d72e-4df4-83af-362c416c9093	ml	ക്യൂബിക് മീറ്റർ	\N	2026-01-30 00:05:41.255297+00
1446f106-405d-4c6f-a152-f0e3bd5e4546	0c4fbc7f-b88a-457e-a55b-dd1413ba7ac1	ml	ഗ്രാം	\N	2026-01-30 00:05:41.255297+00
118dad92-d009-432b-9338-7dd39cc4555e	08607b68-5102-45f3-a0e8-d0da2686b742	ml	കിലോഗ്രാം	\N	2026-01-30 00:05:41.255297+00
0f2d0b0c-fa96-44cb-b878-d1892650efae	2bf8b40b-ffed-4163-a0e1-94bd4315f574	ml	ക്വിന്റൽ	\N	2026-01-30 00:05:41.255297+00
b58bec44-509c-4de9-a61b-bbbe7bd47994	f1add34c-1f5f-4388-b7b0-e2132983bc99	ml	ടൺ	\N	2026-01-30 00:05:41.255297+00
0493a603-7968-430c-a24b-dcca406982de	327f42a9-a084-4758-bb1b-827af61788fc	ml	പൗണ്ട്	\N	2026-01-30 00:05:41.255297+00
8d1eccfb-3ed6-4ce4-9864-7efa098ef325	011691a3-d6fb-4b00-a7a1-bca1e29362ef	ml	സെന്റിമീറ്റർ	\N	2026-01-30 00:05:41.255297+00
bf845214-41dd-4c88-91bf-bed5d25b02b6	4747b9e6-9688-48d7-86fc-009c6ed49064	ml	ഇഞ്ച്	\N	2026-01-30 00:05:41.255297+00
31f2d387-4f69-4870-a987-746d3637bd72	c0c6386d-4cad-429f-99e0-60a6616cc4e8	ml	അടി	\N	2026-01-30 00:05:41.255297+00
a9a4e06a-ae13-4c6d-9e9e-e47572430afa	aeebcc57-0991-43ce-863b-2454b6c354cc	ml	മീറ്റർ	\N	2026-01-30 00:05:41.255297+00
b6215a4f-9585-45c3-a369-1cac1637a929	826c0489-55be-4e31-86d7-688d93723ee2	ml	കിലോമീറ്റർ	\N	2026-01-30 00:05:41.255297+00
d023d12f-5863-4b80-98fc-c0cb6d0fd056	7b170349-3c5f-4255-9c2d-fc1314da41df	ml	യൂണിറ്റ്	\N	2026-01-30 00:05:41.255297+00
8351f44f-6860-4fec-95af-d34967b4b036	9a00f259-2499-46a6-9e57-9917718b67f5	ml	ഡസൻ	\N	2026-01-30 00:05:41.255297+00
cac320f8-ae52-421f-870f-534e816afa70	a3e13992-8d3f-49de-9e40-a7679dea4470	ml	നൂറ്	\N	2026-01-30 00:05:41.255297+00
9a473df7-7888-4c9b-ba0a-671652fb1e0b	20675456-7924-42a5-939c-5076ab819b2b	en	Gram	\N	2026-01-30 10:00:39.742302+00
2b7d4b10-91dc-49d7-95a1-bad28975c588	2e81f573-5eb5-4ff9-b839-c2e9a7fef2bc	en	Milligram	\N	2026-01-30 10:00:39.742302+00
b278e3f4-0dbf-43f4-8522-d59ccda1304c	0ce37de3-46af-4700-8122-d4e6df1f48c8	en	Liter	\N	2026-01-30 10:00:39.742302+00
7c84fc2f-c778-4eaf-8349-df83540640b9	a1d5cbe4-2812-429e-81f8-4baa34d5a28d	en	Milliliter	\N	2026-01-30 10:00:39.742302+00
497592ae-99ac-4058-8526-5416f4d0184c	828bc850-78b4-4fb8-b80a-dd15b04c5166	en	Pieces	\N	2026-01-30 10:00:39.742302+00
e5ee24c2-eecb-42e7-8bce-f7fa61f77a1c	dc68ef21-6aac-4b2e-bf30-016c6ee06dac	en	Plants	\N	2026-01-30 10:00:39.742302+00
\.


--
-- Data for Name: measurement_units; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.measurement_units (id, category, code, symbol, is_base_unit, conversion_factor, sort_order, created_at, updated_at) FROM stdin;
27c45cfe-3f18-417c-be00-de9a0d4ddcf4	AREA	SQ_M	m²	t	1.0000000000	1	2026-01-30 00:05:41.211635+00	2026-01-30 00:05:41.211635+00
7bbe2739-eed9-4892-a070-3495819360dd	AREA	SQ_FT	ft²	f	0.0929030000	2	2026-01-30 00:05:41.211635+00	2026-01-30 00:05:41.211635+00
1f8042a9-b954-4d7f-b17f-2c6ba0a6dbfb	AREA	CENT	cent	f	40.4686000000	3	2026-01-30 00:05:41.211635+00	2026-01-30 00:05:41.211635+00
1c6b90ac-ff6b-4c5f-be90-5f33c91725d4	AREA	ACRE	ac	f	4046.8600000000	4	2026-01-30 00:05:41.211635+00	2026-01-30 00:05:41.211635+00
687e0563-f59c-4b16-9b84-a5786b0b2ab3	AREA	HECTARE	ha	f	10000.0000000000	5	2026-01-30 00:05:41.211635+00	2026-01-30 00:05:41.211635+00
904cd0d4-9654-4108-858d-28701fc229be	VOLUME	MILLILITER	mL	f	0.0010000000	1	2026-01-30 00:05:41.222219+00	2026-01-30 00:05:41.222219+00
40e5d650-d6b1-4000-8731-ba64b30e74ff	VOLUME	LITER	L	t	1.0000000000	2	2026-01-30 00:05:41.222219+00	2026-01-30 00:05:41.222219+00
63a8e7eb-686c-4e4a-b25c-7e59f38e7ce1	VOLUME	GALLON	gal	f	3.7854100000	3	2026-01-30 00:05:41.222219+00	2026-01-30 00:05:41.222219+00
d3dabbf4-d72e-4df4-83af-362c416c9093	VOLUME	CUBIC_M	m³	f	1000.0000000000	4	2026-01-30 00:05:41.222219+00	2026-01-30 00:05:41.222219+00
0c4fbc7f-b88a-457e-a55b-dd1413ba7ac1	WEIGHT	GRAM	g	f	0.0010000000	1	2026-01-30 00:05:41.232917+00	2026-01-30 00:05:41.232917+00
08607b68-5102-45f3-a0e8-d0da2686b742	WEIGHT	KG	kg	t	1.0000000000	2	2026-01-30 00:05:41.232917+00	2026-01-30 00:05:41.232917+00
2bf8b40b-ffed-4163-a0e1-94bd4315f574	WEIGHT	QUINTAL	q	f	100.0000000000	3	2026-01-30 00:05:41.232917+00	2026-01-30 00:05:41.232917+00
f1add34c-1f5f-4388-b7b0-e2132983bc99	WEIGHT	TONNE	t	f	1000.0000000000	4	2026-01-30 00:05:41.232917+00	2026-01-30 00:05:41.232917+00
327f42a9-a084-4758-bb1b-827af61788fc	WEIGHT	POUND	lb	f	0.4535920000	5	2026-01-30 00:05:41.232917+00	2026-01-30 00:05:41.232917+00
011691a3-d6fb-4b00-a7a1-bca1e29362ef	LENGTH	CENTIMETER	cm	f	0.0100000000	1	2026-01-30 00:05:41.243547+00	2026-01-30 00:05:41.243547+00
4747b9e6-9688-48d7-86fc-009c6ed49064	LENGTH	INCH	in	f	0.0254000000	2	2026-01-30 00:05:41.243547+00	2026-01-30 00:05:41.243547+00
c0c6386d-4cad-429f-99e0-60a6616cc4e8	LENGTH	FEET	ft	f	0.3048000000	3	2026-01-30 00:05:41.243547+00	2026-01-30 00:05:41.243547+00
aeebcc57-0991-43ce-863b-2454b6c354cc	LENGTH	METER	m	t	1.0000000000	4	2026-01-30 00:05:41.243547+00	2026-01-30 00:05:41.243547+00
826c0489-55be-4e31-86d7-688d93723ee2	LENGTH	KILOMETER	km	f	1000.0000000000	5	2026-01-30 00:05:41.243547+00	2026-01-30 00:05:41.243547+00
7b170349-3c5f-4255-9c2d-fc1314da41df	COUNT	UNIT	unit	t	1.0000000000	1	2026-01-30 00:05:41.254171+00	2026-01-30 00:05:41.254171+00
9a00f259-2499-46a6-9e57-9917718b67f5	COUNT	DOZEN	doz	f	12.0000000000	2	2026-01-30 00:05:41.254171+00	2026-01-30 00:05:41.254171+00
a3e13992-8d3f-49de-9e40-a7679dea4470	COUNT	HUNDRED	100	f	100.0000000000	3	2026-01-30 00:05:41.254171+00	2026-01-30 00:05:41.254171+00
20675456-7924-42a5-939c-5076ab819b2b	WEIGHT	G	g	f	0.0010000000	0	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00
2e81f573-5eb5-4ff9-b839-c2e9a7fef2bc	WEIGHT	MG	mg	f	0.0000010000	0	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00
0ce37de3-46af-4700-8122-d4e6df1f48c8	VOLUME	L	l	t	1.0000000000	0	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00
a1d5cbe4-2812-429e-81f8-4baa34d5a28d	VOLUME	ML	ml	f	0.0010000000	0	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00
828bc850-78b4-4fb8-b80a-dd15b04c5166	COUNT	PIECES	pcs	t	1.0000000000	0	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00
dc68ef21-6aac-4b2e-bf30-016c6ee06dac	COUNT	PLANTS	plants	f	1.0000000000	0	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notifications (id, user_id, organization_id, notification_type, title, message, reference_type, reference_id, is_read, read_at, is_push_sent, push_sent_at, created_at) FROM stdin;
\.


--
-- Data for Name: option_sets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.option_sets (id, code, is_system_defined, owner_org_id, is_active, created_at, created_by, updated_at, updated_by) FROM stdin;
d9b092af-26d2-4bad-be2f-c459e999e778	LEAF_COLOR_OPTIONS	t	\N	t	2026-01-30 00:05:41.403553+00	\N	2026-01-30 00:05:41.403553+00	\N
d3ab8840-8a6e-4251-9c55-94f23f12405e	YES_NO_OPTIONS	t	\N	t	2026-01-30 00:05:41.403553+00	\N	2026-01-30 00:05:41.403553+00	\N
e5183c0d-bad4-44d3-8329-f4048f1df704	SOIL_MOISTURE_OPTIONS	t	\N	t	2026-01-30 00:05:41.403553+00	\N	2026-01-30 00:05:41.403553+00	\N
49c22604-b83e-4ec6-b024-aed71d28f5dd	OS_PRM_b3ab_0_2653	f	8b411c61-9885-4672-ba08-e45709934575	t	2026-01-30 00:21:13.085603+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 00:21:13.085603+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
c39059bb-e98e-43e5-955d-1f87b7450684	OS_PRM_b3ab_1_2786	f	8b411c61-9885-4672-ba08-e45709934575	t	2026-01-30 00:21:13.218845+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 00:21:13.218845+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
0b082300-cb93-4098-8b68-4c5f2492d0ea	OS_PRM_b3ab_3_2969	f	8b411c61-9885-4672-ba08-e45709934575	t	2026-01-30 00:21:13.401629+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 00:21:13.401629+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
12462a9c-7649-4b3c-bb96-adbe08432626	OS_PRM_GDFGDFG_6319	f	8b411c61-9885-4672-ba08-e45709934575	t	2026-01-30 20:34:37.466543+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 20:34:37.466543+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
0345db82-bf99-4f32-b222-6ae0a7c07c00	OS_PRM_fa6d_2_1310	f	8b411c61-9885-4672-ba08-e45709934575	t	2026-01-30 20:36:02.456146+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 20:36:02.456146+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
dfdd3646-a211-4edf-9458-3fd5dfdb7a76	OS_PRM_fa6d_3_1410	f	8b411c61-9885-4672-ba08-e45709934575	t	2026-01-30 20:36:02.556638+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 20:36:02.556638+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
9a006dfc-05c1-48d7-a1d9-d0a6f6e2ccba	OS_PRM_fa6d_5_1576	f	8b411c61-9885-4672-ba08-e45709934575	t	2026-01-30 20:36:02.721817+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 20:36:02.721817+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
7d1bfc37-3b1b-4421-a3f9-104690c6e487	OS_P3_1770327102	f	27227759-8c29-4ba3-8ba5-153607db5c4c	t	2026-02-05 21:31:42.68565+00	53126f3a-94da-4363-b20d-61a85c99574a	2026-02-05 21:31:42.68565+00	53126f3a-94da-4363-b20d-61a85c99574a
b409cb79-5f90-4322-b935-5c13fe396f9c	OS_P3_1770327224	f	bc651c65-73d1-41c9-a03a-275b47df7b10	t	2026-02-05 21:33:45.250961+00	1214c599-c7c2-490b-a895-e45b985b027b	2026-02-05 21:33:45.250961+00	1214c599-c7c2-490b-a895-e45b985b027b
a9bf577e-4d74-495e-b9d9-c1677621be45	OS_P3_1770327280	f	0a61f5ac-582c-4856-8072-27fcad588698	t	2026-02-05 21:34:41.255709+00	d9cd5b64-e423-4710-bcfe-73606bcca78c	2026-02-05 21:34:41.255709+00	d9cd5b64-e423-4710-bcfe-73606bcca78c
cdc29b9f-35fb-4abb-a9a6-21272b56173a	OS_P3_1770327392	f	88810bde-bf96-43e8-9791-937cd4a7e062	t	2026-02-05 21:36:32.718074+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	2026-02-05 21:36:32.718074+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
b0fe6edb-193c-4e20-a6f4-5cbaaf817536	OS_P3_1770327572	f	5e03962b-3b0c-4bd5-9f17-6349e82083cb	t	2026-02-05 21:39:33.763321+00	fc5165e6-6519-496f-a3dd-1435bc308b5f	2026-02-05 21:39:33.763321+00	fc5165e6-6519-496f-a3dd-1435bc308b5f
ba3f1425-1907-48fc-a9f4-7ee1a85c0b90	OS_P3_1770327636	f	8bb34a8d-f5bb-41cf-ba29-87e5c652c03f	t	2026-02-05 21:40:37.642982+00	d655e067-4edd-4516-b1b6-821c3c33cfc5	2026-02-05 21:40:37.642982+00	d655e067-4edd-4516-b1b6-821c3c33cfc5
e67b95a8-8819-4939-9557-bd2d5379e96c	OS_P3_1770327706	f	f3200c57-c6b8-4f2d-80fe-24b9a6359f6c	t	2026-02-05 21:41:47.381531+00	13ac055f-b943-4f6d-8182-babe636544df	2026-02-05 21:41:47.381531+00	13ac055f-b943-4f6d-8182-babe636544df
53a4bc06-e667-4f37-b16e-9aa98563aa2f	OS_P3_1770327821	f	f7028cb1-7e87-4fd7-8aa1-4ea8b97ccb43	t	2026-02-05 21:43:42.795572+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	2026-02-05 21:43:42.795572+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
e86a83d1-b3e4-44cc-95ad-b63d2b7a931d	OS_P3_1770328194	f	e33b94b6-cfc5-4d7e-98a4-2259867e45b4	t	2026-02-05 21:49:55.171024+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	2026-02-05 21:49:55.171024+00	ebc86578-b9a2-456f-b884-f964c1fb26f9
f8998096-2833-488c-b41e-08dedfcfc32c	OS_P3_1770328337	f	718996de-ba3d-4b71-9a19-a6e97d2947ee	t	2026-02-05 21:52:18.955239+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	2026-02-05 21:52:18.955239+00	7eddd813-1060-42a3-aa36-abc2c6529e0f
6c5d8da2-26c9-424a-9b09-5f0b70e2c080	OS_P3_1770328517	f	f9761969-f234-4bb8-9b46-2ea70ad5b735	t	2026-02-05 21:55:18.68093+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	2026-02-05 21:55:18.68093+00	021aea9d-7fe9-4488-ae61-eebf6d2af731
\.


--
-- Data for Name: option_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.option_translations (id, option_id, language_code, display_text, created_at) FROM stdin;
d2cc2ca8-0068-49aa-ab90-634c958aec04	db2523df-6488-4a1b-b7ec-aaed3239f5f2	en	Green	2026-01-30 00:05:41.446099+00
51a45224-17ad-400a-ad8b-b4a5029e3cd6	f3ea4886-beb7-4d2d-80bc-a6d5869f7782	en	Yellow	2026-01-30 00:05:41.446099+00
282d1d97-cb2a-41e8-8df3-7bc724bbd547	f533cea3-8d39-42f4-90a7-719f87acaa5a	en	Brown	2026-01-30 00:05:41.446099+00
4b81ba83-23bc-44c5-9054-ae3c8f8190ec	4f893b62-1cd5-48d3-a136-1bd38ad0584a	en	Yes	2026-01-30 00:05:41.446099+00
25ae442e-8f75-49ff-9fcb-d7a8a7526538	423687b2-1f99-44a4-9998-d7eb87939b95	en	No	2026-01-30 00:05:41.446099+00
d7052fe0-715a-4925-9b60-5a9e9fd9ca98	5333b874-7068-4acb-928a-8d6246a1e405	en	Dry	2026-01-30 00:05:41.446099+00
615e40cc-9b86-4eaf-be09-df4516f6b366	b788b87a-2534-4af6-8c92-4e9b74fcac9e	en	Moist	2026-01-30 00:05:41.446099+00
6868604a-c877-4645-a367-b6e5c5a7d111	def2f1b6-37e1-4c8e-8754-f1cbee3fd75c	en	Wet	2026-01-30 00:05:41.446099+00
840b3780-01c1-49be-ac7e-1f3450ededb8	db2523df-6488-4a1b-b7ec-aaed3239f5f2	ta	பச்சை	2026-01-30 00:05:41.446099+00
afdf716e-b5f8-4bf0-a21d-ab71534d8370	f3ea4886-beb7-4d2d-80bc-a6d5869f7782	ta	மஞ்சள்	2026-01-30 00:05:41.446099+00
fbe53353-b278-4e4a-ba60-63b6b40e3070	f533cea3-8d39-42f4-90a7-719f87acaa5a	ta	பழுப்பு	2026-01-30 00:05:41.446099+00
33a4a509-f5fd-4e85-829e-2e4bd14bfdbb	4f893b62-1cd5-48d3-a136-1bd38ad0584a	ta	ஆம்	2026-01-30 00:05:41.446099+00
e0db8506-2528-40d1-a82a-671df0468262	423687b2-1f99-44a4-9998-d7eb87939b95	ta	இல்லை	2026-01-30 00:05:41.446099+00
3fbe86c2-c769-4341-b5a5-3968408bad40	5333b874-7068-4acb-928a-8d6246a1e405	ta	வறண்ட	2026-01-30 00:05:41.446099+00
f331b2f8-85f9-42f3-9d53-c0b6d62bbf46	b788b87a-2534-4af6-8c92-4e9b74fcac9e	ta	ஈரமான	2026-01-30 00:05:41.446099+00
a746c905-3af9-4f0b-84e6-87563df0fe91	def2f1b6-37e1-4c8e-8754-f1cbee3fd75c	ta	நனைந்த	2026-01-30 00:05:41.446099+00
288ad8a8-1ed2-4aa6-8e0e-e355ab8255c5	ccbc5fe8-e077-4487-8bf7-a807afaadeb9	en	Green	2026-01-30 00:21:13.085603+00
960ab005-3117-4f08-90cc-ee68528876c5	3661417e-ea73-4b11-82da-0846d2a89567	en	Yellow	2026-01-30 00:21:13.085603+00
0295b921-a448-4771-899a-2252851dd61e	cb28cd9a-9c87-45be-ba22-b92076e2f4f7	en	Brown	2026-01-30 00:21:13.085603+00
4e7d976f-ee19-4536-ae36-5647b4efd177	e1e48690-f91d-48b6-9d1e-6cd31518f138	en	Yes	2026-01-30 00:21:13.218845+00
7d4bf089-21f4-45e4-b579-a783faaab7b1	3718494a-aec8-44e5-bfd4-1cfc615c78ea	en	No	2026-01-30 00:21:13.218845+00
01c96e48-9084-4d9b-9635-52ce4f08fc34	0909eb6a-4e53-412a-a760-d23a5bd8e0e2	en	Dry	2026-01-30 00:21:13.401629+00
196df286-b8ab-44b7-b71a-bd76b4652a4e	5a70955a-94e0-4f47-90ec-9c7caf3284f3	en	Moist	2026-01-30 00:21:13.401629+00
525201cd-cca7-438a-8f45-0dbb1cc6e112	739bdc7c-5082-473e-8a36-9dca94909a3a	en	Wet	2026-01-30 00:21:13.401629+00
2c6f2d5c-ffc8-4525-be11-2104c3617eff	d0cfe6c1-a722-4e08-a141-f6e7201c9d99	en	dfgdfg	2026-01-30 20:34:37.466543+00
7b76dfb9-8ed7-483e-93d0-7f7bdb5e03e4	059974e2-a761-487f-9e52-2629100b504a	en	Green	2026-01-30 20:36:02.456146+00
49d0e0a1-1780-44c7-82c4-fac575d196ed	6d7cbc48-8d1a-4ba5-bf1d-fd8b794a404b	en	Yellow	2026-01-30 20:36:02.456146+00
453cf6dc-b6a2-4bf3-8169-59e850bf1a82	c643a809-e612-4807-9a90-0b29f0f9508c	en	Brown	2026-01-30 20:36:02.456146+00
ed834118-39bb-4b90-9731-80a7160204f9	0c80853b-5a5b-4b87-8ba9-943fcf02bb3b	en	Yes	2026-01-30 20:36:02.556638+00
295a0a89-98e9-416f-82e6-4d298983e287	af79f344-cacf-4679-9426-ff4f2507deb0	en	No	2026-01-30 20:36:02.556638+00
bea1145d-0db7-4190-81ae-750853b953c5	ceba3c16-431a-4ddd-b565-51a899129e34	en	Dry	2026-01-30 20:36:02.721817+00
fd0f416e-bf26-4b68-a6d9-afe7f7fd9f09	72bd150c-a989-42a6-8a19-7c0c46e21195	en	Moist	2026-01-30 20:36:02.721817+00
3268ccde-ba22-4687-97c3-2941118ac10c	bce6372f-fb3a-492a-986d-9c2a151d765b	en	Wet	2026-01-30 20:36:02.721817+00
32a1deaf-b556-4d07-a64e-8c7650ecb723	b7c70d96-0f02-48ae-972d-b003cbfc3b89	en	Organic	2026-02-05 21:31:42.68565+00
9bdd2a9e-a459-404e-81a9-f6431c6fc910	4126b50a-880e-44a6-b28a-985081f32d4c	en	Chemical	2026-02-05 21:31:42.68565+00
4fea401a-c532-4ba7-9953-5df6679f14dd	68b94446-68e1-4ec5-8b41-cc9842033394	en	Organic	2026-02-05 21:33:45.250961+00
a99a0daa-3b04-4fdb-a0c5-51c9cb6804a4	1c17baf7-b36c-464e-9a73-3e829cc103db	en	Chemical	2026-02-05 21:33:45.250961+00
057b187e-1db8-4fe3-8623-1ee52dde1170	ee25c5c6-aadd-4c6a-ab13-3070b40ddf05	en	Organic	2026-02-05 21:34:41.255709+00
f9ad96b7-f6bc-48b0-aca8-c7c3132b7b3c	ab2b8972-8292-4e21-a8f6-66d8bf133921	en	Chemical	2026-02-05 21:34:41.255709+00
68b8c708-99af-4f5f-afca-5088e2245a2a	c2b584fc-e308-4562-ba68-3bdc7c1f8ecc	en	Organic	2026-02-05 21:36:32.718074+00
e9c7e6a2-0794-4e9d-8106-3a00641baf30	afb0f1b3-8447-4a23-a961-cf6affd8bfa0	en	Chemical	2026-02-05 21:36:32.718074+00
351db918-ce04-406b-b7b6-aed9211fdfcb	6baefc9c-88e8-4aa1-a021-8cae81a905ed	en	Organic	2026-02-05 21:39:33.763321+00
051df73b-e17b-4939-aa38-5392d1cebf4c	44c9d328-fc27-4a2c-9a01-9167b8f9c84f	en	Chemical	2026-02-05 21:39:33.763321+00
f875bda4-7acf-45b4-9292-0ab95dde1f9d	cc1a045b-0ce5-4c07-afed-eca7a4d7896f	en	Organic	2026-02-05 21:40:37.642982+00
a1090c28-ef05-4357-a5a5-aca139436e34	6f01b763-30d8-414c-9af9-bf605ac00ae7	en	Chemical	2026-02-05 21:40:37.642982+00
0f1e2565-adba-4f4b-97d7-424f63285fef	8337ba01-c7bc-4553-86d0-672c65399b38	en	Organic	2026-02-05 21:41:47.381531+00
3a3577a4-27c1-4395-bec3-f1d7b6b4a1f8	5811ced6-2e79-4c9e-b7a1-f48134203521	en	Chemical	2026-02-05 21:41:47.381531+00
9b5d4f7a-2a76-49c4-92e7-41ee28b0e26a	3f3b03fa-ef0e-42fe-9546-c33af35d1681	en	Organic	2026-02-05 21:43:42.795572+00
b9efa78a-a46d-486f-bce2-ac1955ba0602	a77d9560-5597-493c-a16d-99af12c82df6	en	Chemical	2026-02-05 21:43:42.795572+00
8f02c5b2-0421-43e0-b0b8-7dc2d18c6f20	2c2e893a-cd32-4855-b766-681bb293adb7	en	Organic	2026-02-05 21:49:55.171024+00
a4ced591-f9cd-4b4f-8034-a3cd382d4b41	3384b3d2-89b2-45f7-82a2-28e23fa1dc1f	en	Chemical	2026-02-05 21:49:55.171024+00
b6130c05-9344-4a0e-98b6-c9a1f80bf313	74519a03-49e9-43a4-adbf-4f87f5ea49b9	en	Organic	2026-02-05 21:52:18.955239+00
b27df9db-6a11-453c-9502-a30b9ec13634	d4ae2cd6-4259-436a-8a91-f9003f839b13	en	Chemical	2026-02-05 21:52:18.955239+00
61bf1be9-a6a3-4982-b7f1-bf74f052dda2	acfc1f03-a09d-408d-88c9-28563d8d9f9a	en	Organic	2026-02-05 21:55:18.68093+00
3098aa90-3565-46e7-9b01-8fdec5a47a3c	25dd033d-3220-4738-8685-4163540c3b74	en	Chemical	2026-02-05 21:55:18.68093+00
\.


--
-- Data for Name: options; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.options (id, option_set_id, code, sort_order, is_active, created_at) FROM stdin;
db2523df-6488-4a1b-b7ec-aaed3239f5f2	d9b092af-26d2-4bad-be2f-c459e999e778	GREEN	1	t	2026-01-30 00:05:41.414269+00
f3ea4886-beb7-4d2d-80bc-a6d5869f7782	d9b092af-26d2-4bad-be2f-c459e999e778	YELLOW	2	t	2026-01-30 00:05:41.414269+00
f533cea3-8d39-42f4-90a7-719f87acaa5a	d9b092af-26d2-4bad-be2f-c459e999e778	BROWN	3	t	2026-01-30 00:05:41.414269+00
4f893b62-1cd5-48d3-a136-1bd38ad0584a	d3ab8840-8a6e-4251-9c55-94f23f12405e	YES	1	t	2026-01-30 00:05:41.424968+00
423687b2-1f99-44a4-9998-d7eb87939b95	d3ab8840-8a6e-4251-9c55-94f23f12405e	NO	2	t	2026-01-30 00:05:41.424968+00
5333b874-7068-4acb-928a-8d6246a1e405	e5183c0d-bad4-44d3-8329-f4048f1df704	DRY	1	t	2026-01-30 00:05:41.435598+00
b788b87a-2534-4af6-8c92-4e9b74fcac9e	e5183c0d-bad4-44d3-8329-f4048f1df704	MOIST	2	t	2026-01-30 00:05:41.435598+00
def2f1b6-37e1-4c8e-8754-f1cbee3fd75c	e5183c0d-bad4-44d3-8329-f4048f1df704	WET	3	t	2026-01-30 00:05:41.435598+00
ccbc5fe8-e077-4487-8bf7-a807afaadeb9	49c22604-b83e-4ec6-b024-aed71d28f5dd	GREEN	0	t	2026-01-30 00:21:13.085603+00
3661417e-ea73-4b11-82da-0846d2a89567	49c22604-b83e-4ec6-b024-aed71d28f5dd	YELLOW	1	t	2026-01-30 00:21:13.085603+00
cb28cd9a-9c87-45be-ba22-b92076e2f4f7	49c22604-b83e-4ec6-b024-aed71d28f5dd	BROWN	2	t	2026-01-30 00:21:13.085603+00
e1e48690-f91d-48b6-9d1e-6cd31518f138	c39059bb-e98e-43e5-955d-1f87b7450684	YES	0	t	2026-01-30 00:21:13.218845+00
3718494a-aec8-44e5-bfd4-1cfc615c78ea	c39059bb-e98e-43e5-955d-1f87b7450684	NO	1	t	2026-01-30 00:21:13.218845+00
0909eb6a-4e53-412a-a760-d23a5bd8e0e2	0b082300-cb93-4098-8b68-4c5f2492d0ea	DRY	0	t	2026-01-30 00:21:13.401629+00
5a70955a-94e0-4f47-90ec-9c7caf3284f3	0b082300-cb93-4098-8b68-4c5f2492d0ea	MOIST	1	t	2026-01-30 00:21:13.401629+00
739bdc7c-5082-473e-8a36-9dca94909a3a	0b082300-cb93-4098-8b68-4c5f2492d0ea	WET	2	t	2026-01-30 00:21:13.401629+00
d0cfe6c1-a722-4e08-a141-f6e7201c9d99	12462a9c-7649-4b3c-bb96-adbe08432626	dfgdfg	0	t	2026-01-30 20:34:37.466543+00
059974e2-a761-487f-9e52-2629100b504a	0345db82-bf99-4f32-b222-6ae0a7c07c00	GREEN	0	t	2026-01-30 20:36:02.456146+00
6d7cbc48-8d1a-4ba5-bf1d-fd8b794a404b	0345db82-bf99-4f32-b222-6ae0a7c07c00	YELLOW	1	t	2026-01-30 20:36:02.456146+00
c643a809-e612-4807-9a90-0b29f0f9508c	0345db82-bf99-4f32-b222-6ae0a7c07c00	BROWN	2	t	2026-01-30 20:36:02.456146+00
0c80853b-5a5b-4b87-8ba9-943fcf02bb3b	dfdd3646-a211-4edf-9458-3fd5dfdb7a76	YES	0	t	2026-01-30 20:36:02.556638+00
af79f344-cacf-4679-9426-ff4f2507deb0	dfdd3646-a211-4edf-9458-3fd5dfdb7a76	NO	1	t	2026-01-30 20:36:02.556638+00
ceba3c16-431a-4ddd-b565-51a899129e34	9a006dfc-05c1-48d7-a1d9-d0a6f6e2ccba	DRY	0	t	2026-01-30 20:36:02.721817+00
72bd150c-a989-42a6-8a19-7c0c46e21195	9a006dfc-05c1-48d7-a1d9-d0a6f6e2ccba	MOIST	1	t	2026-01-30 20:36:02.721817+00
bce6372f-fb3a-492a-986d-9c2a151d765b	9a006dfc-05c1-48d7-a1d9-d0a6f6e2ccba	WET	2	t	2026-01-30 20:36:02.721817+00
b7c70d96-0f02-48ae-972d-b003cbfc3b89	7d1bfc37-3b1b-4421-a3f9-104690c6e487	opt1	0	t	2026-02-05 21:31:42.68565+00
4126b50a-880e-44a6-b28a-985081f32d4c	7d1bfc37-3b1b-4421-a3f9-104690c6e487	opt2	1	t	2026-02-05 21:31:42.68565+00
68b94446-68e1-4ec5-8b41-cc9842033394	b409cb79-5f90-4322-b935-5c13fe396f9c	opt1	0	t	2026-02-05 21:33:45.250961+00
1c17baf7-b36c-464e-9a73-3e829cc103db	b409cb79-5f90-4322-b935-5c13fe396f9c	opt2	1	t	2026-02-05 21:33:45.250961+00
ee25c5c6-aadd-4c6a-ab13-3070b40ddf05	a9bf577e-4d74-495e-b9d9-c1677621be45	opt1	0	t	2026-02-05 21:34:41.255709+00
ab2b8972-8292-4e21-a8f6-66d8bf133921	a9bf577e-4d74-495e-b9d9-c1677621be45	opt2	1	t	2026-02-05 21:34:41.255709+00
c2b584fc-e308-4562-ba68-3bdc7c1f8ecc	cdc29b9f-35fb-4abb-a9a6-21272b56173a	opt1	0	t	2026-02-05 21:36:32.718074+00
afb0f1b3-8447-4a23-a961-cf6affd8bfa0	cdc29b9f-35fb-4abb-a9a6-21272b56173a	opt2	1	t	2026-02-05 21:36:32.718074+00
6baefc9c-88e8-4aa1-a021-8cae81a905ed	b0fe6edb-193c-4e20-a6f4-5cbaaf817536	opt1	0	t	2026-02-05 21:39:33.763321+00
44c9d328-fc27-4a2c-9a01-9167b8f9c84f	b0fe6edb-193c-4e20-a6f4-5cbaaf817536	opt2	1	t	2026-02-05 21:39:33.763321+00
cc1a045b-0ce5-4c07-afed-eca7a4d7896f	ba3f1425-1907-48fc-a9f4-7ee1a85c0b90	opt1	0	t	2026-02-05 21:40:37.642982+00
6f01b763-30d8-414c-9af9-bf605ac00ae7	ba3f1425-1907-48fc-a9f4-7ee1a85c0b90	opt2	1	t	2026-02-05 21:40:37.642982+00
8337ba01-c7bc-4553-86d0-672c65399b38	e67b95a8-8819-4939-9557-bd2d5379e96c	opt1	0	t	2026-02-05 21:41:47.381531+00
5811ced6-2e79-4c9e-b7a1-f48134203521	e67b95a8-8819-4939-9557-bd2d5379e96c	opt2	1	t	2026-02-05 21:41:47.381531+00
3f3b03fa-ef0e-42fe-9546-c33af35d1681	53a4bc06-e667-4f37-b16e-9aa98563aa2f	opt1	0	t	2026-02-05 21:43:42.795572+00
a77d9560-5597-493c-a16d-99af12c82df6	53a4bc06-e667-4f37-b16e-9aa98563aa2f	opt2	1	t	2026-02-05 21:43:42.795572+00
2c2e893a-cd32-4855-b766-681bb293adb7	e86a83d1-b3e4-44cc-95ad-b63d2b7a931d	opt1	0	t	2026-02-05 21:49:55.171024+00
3384b3d2-89b2-45f7-82a2-28e23fa1dc1f	e86a83d1-b3e4-44cc-95ad-b63d2b7a931d	opt2	1	t	2026-02-05 21:49:55.171024+00
74519a03-49e9-43a4-adbf-4f87f5ea49b9	f8998096-2833-488c-b41e-08dedfcfc32c	opt1	0	t	2026-02-05 21:52:18.955239+00
d4ae2cd6-4259-436a-8a91-f9003f839b13	f8998096-2833-488c-b41e-08dedfcfc32c	opt2	1	t	2026-02-05 21:52:18.955239+00
acfc1f03-a09d-408d-88c9-28563d8d9f9a	6c5d8da2-26c9-424a-9b09-5f0b70e2c080	opt1	0	t	2026-02-05 21:55:18.68093+00
25dd033d-3220-4738-8685-4163540c3b74	6c5d8da2-26c9-424a-9b09-5f0b70e2c080	opt2	1	t	2026-02-05 21:55:18.68093+00
\.


--
-- Data for Name: org_member_invitations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.org_member_invitations (id, organization_id, inviter_id, invitee_email, invitee_user_id, role_id, status, invited_at, responded_at, expires_at, message, created_at, updated_at) FROM stdin;
4bdeb7cb-2b48-4a62-82aa-51e454c211a5	f2d7a38d-6265-4cd5-9743-be932e8693c0	c5154fda-1c6a-4c09-bd67-0482fe81f7d8	amit@gmail.com	c5154fda-1c6a-4c09-bd67-0482fe81f7d8	c73b0952-76fb-4651-9914-2a90c0204945	PENDING	2026-02-09 14:44:24.273239+00	\N	2026-03-11 14:44:24.273239+00	Request to join organization	2026-02-09 14:44:24.265235+00	2026-02-09 14:44:24.265235+00
33cdd1b7-9d9b-4ff8-993b-5fbfefa68ace	8b411c61-9885-4672-ba08-e45709934575	c5154fda-1c6a-4c09-bd67-0482fe81f7d8	amit@gmail.com	c5154fda-1c6a-4c09-bd67-0482fe81f7d8	c73b0952-76fb-4651-9914-2a90c0204945	PENDING	2026-02-09 14:44:39.724841+00	\N	2026-03-11 14:44:39.724841+00	Request to join organization	2026-02-09 14:44:39.71339+00	2026-02-09 14:44:39.71339+00
67f5002d-3204-4004-9296-513f47b8e98f	5ae66809-e7de-448a-8f42-920a192c8704	c5154fda-1c6a-4c09-bd67-0482fe81f7d8	amit@gmail.com	c5154fda-1c6a-4c09-bd67-0482fe81f7d8	c73b0952-76fb-4651-9914-2a90c0204945	REJECTED	2026-02-09 14:32:13.546642+00	2026-02-09 14:45:32.176294+00	2026-03-11 14:32:13.546642+00	Request to join organization	2026-02-09 14:32:13.531881+00	2026-02-09 14:45:32.169829+00
85bfbaa4-1565-4e43-b86a-f6440dbd4985	5ae66809-e7de-448a-8f42-920a192c8704	3f3a3a39-d867-45a8-b901-74a7e27c95f3	amit@gmail.com	c5154fda-1c6a-4c09-bd67-0482fe81f7d8	aa22c090-2bef-4796-96e9-885a3c206545	ACCEPTED	2026-02-09 14:45:49.461599+00	2026-02-09 14:46:47.509266+00	2026-02-16 14:45:49.461599+00	Invitation to join organization with role SUPERVISOR	2026-02-09 14:45:49.447658+00	2026-02-09 14:46:47.499889+00
\.


--
-- Data for Name: org_member_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.org_member_roles (id, user_id, organization_id, role_id, is_primary, assigned_at, assigned_by, created_at) FROM stdin;
5eddc302-e982-4dd9-830b-c950bff4fcba	7ebef8e8-4a6d-4420-ac3a-e01a33f6c975	\N	a8613649-0857-4f6a-8589-45580a027f22	t	2026-01-30 00:05:35.616224+00	\N	2026-01-30 00:05:35.616224+00
7994c34b-9fd6-42ec-a429-0b2d38031193	3f3a3a39-d867-45a8-b901-74a7e27c95f3	8b411c61-9885-4672-ba08-e45709934575	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-01-30 00:08:38.868186+00	\N	2026-01-30 00:08:38.868186+00
887764fa-b851-404b-9d5c-2ab827d47ceb	08c368c7-0ea2-4dad-a5fe-5e8e180b0b44	8b411c61-9885-4672-ba08-e45709934575	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	t	2026-01-30 00:08:38.878468+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 00:08:38.878468+00
5135f0dd-e834-4160-905e-fa1941ca32bd	f5f9ef2a-8a6f-4973-900c-0e0bca8ee95c	8b411c61-9885-4672-ba08-e45709934575	b56b143c-ecb1-41b7-a21b-ccd6fd7e11f9	t	2026-01-30 00:08:38.888877+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 00:08:38.888877+00
7d24bf54-c8df-4fd3-a88e-0a67d606e088	7bd0073c-4c78-429f-9421-d5d52db3fd53	8b411c61-9885-4672-ba08-e45709934575	0ca36331-1393-48be-b0f4-b41d07e7cd49	t	2026-01-30 00:08:38.89581+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 00:08:38.89581+00
ed810a15-6e8a-4c0b-8af1-7f3a37800fc3	fe4d1e04-7569-409d-8bfc-f7319e7ea582	1455677e-0753-44c1-959e-06c542a28884	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-01-30 00:08:38.963073+00	\N	2026-01-30 00:08:38.963073+00
f4153b2b-db6e-4502-91b9-0851586c17c5	3f3a3a39-d867-45a8-b901-74a7e27c95f3	5ae66809-e7de-448a-8f42-920a192c8704	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-01-30 00:12:20.656935+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 00:12:20.626621+00
542382ad-78f0-4b2b-8b37-33c38fee3689	3be02ab8-a88f-4a03-b781-3fffa07e5096	\N	893a1f71-b524-4995-91a0-c1f44db37066	t	2026-02-01 10:04:58.325545+00	\N	2026-02-01 10:04:58.325545+00
dc400559-5938-4e7f-9f3c-c0d31e8217c2	bfdafb1c-258c-487a-84a9-8df88d6f7efd	6ccc83ff-6dd6-45b8-9285-d189eec284e9	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:04:58.639504+00	bfdafb1c-258c-487a-84a9-8df88d6f7efd	2026-02-01 10:04:58.583848+00
fc9e8a87-fc2d-46e9-bd8e-be11025d9634	a7c620dc-005f-41e4-a09c-84a578fdff32	9a08dd9e-37f1-466a-9cce-b38722c3c08d	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:06:48.532013+00	a7c620dc-005f-41e4-a09c-84a578fdff32	2026-02-01 10:06:48.520888+00
40922414-cfe6-4e4d-b633-424dd45f09d5	ea72b36b-fe10-483e-acca-7274bdab7600	74faf449-2f3a-4cdf-a1a6-6294eabc51b9	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:06:48.553056+00	ea72b36b-fe10-483e-acca-7274bdab7600	2026-02-01 10:06:48.540544+00
b55592f7-aa3c-44cc-8356-e3802bc1fd25	eb63636b-e512-4cd7-9296-f0d38d62f74d	d21c407f-5ec7-4940-9863-903fc66fb45f	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:10:07.286651+00	eb63636b-e512-4cd7-9296-f0d38d62f74d	2026-02-01 10:10:07.26914+00
254440e8-0747-41ce-84e7-e4d2cbe816b7	fc777437-f8d9-4e04-bc0a-011507805218	5986b068-6433-4eb3-907f-79e9e5ae4bd2	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:10:07.311649+00	fc777437-f8d9-4e04-bc0a-011507805218	2026-02-01 10:10:07.29576+00
3221c2b0-ca79-42af-af61-15492235c9a5	26872c85-6000-4eec-baab-a1a4b8a27258	4309e43b-b68e-4834-8de3-a824a0bf37ab	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:30:00.50867+00	26872c85-6000-4eec-baab-a1a4b8a27258	2026-02-01 10:30:00.498111+00
67db6bf9-ab60-459a-be5c-08a248152c8b	d24c619c-0783-4510-949c-49445cea0202	bc9a3480-c0ad-43c6-ab08-5fc8362d34b2	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:30:00.526215+00	d24c619c-0783-4510-949c-49445cea0202	2026-02-01 10:30:00.515811+00
58291498-8d4f-4a3f-83c9-d94017dc7601	aec76aa4-0bf4-40bb-9307-de54a5d205a5	efa7b0ac-291d-489e-94f5-b7e09ee61211	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:31:21.074429+00	aec76aa4-0bf4-40bb-9307-de54a5d205a5	2026-02-01 10:31:21.06163+00
2998ba96-2ec7-4902-bf73-255e262a3e1d	5b010aef-d0b8-40cc-bc0e-6b6c133cac49	db3950f7-2c3d-40ec-8646-9548956aa267	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:31:21.093439+00	5b010aef-d0b8-40cc-bc0e-6b6c133cac49	2026-02-01 10:31:21.08214+00
8d4d539d-b8cb-491e-8571-d0acbf0bdfcf	ee6157bd-176f-4f75-8cea-64adb841884f	23f17148-f316-4fb6-8fd4-c4f2045ae401	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:32:49.169134+00	ee6157bd-176f-4f75-8cea-64adb841884f	2026-02-01 10:32:49.157574+00
0bc604ba-f830-4bad-ae26-1b711d031bc5	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c	9463b7f0-b657-467c-bc0e-0f21817e623c	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:32:49.187167+00	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c	2026-02-01 10:32:49.176666+00
f6327143-09e3-4b56-9fc3-a308cf34f5ce	ee193894-167a-4355-8899-7c19ba395e9f	cc35b76b-375c-4261-8fa4-24b833a63cdb	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:33:09.875809+00	ee193894-167a-4355-8899-7c19ba395e9f	2026-02-01 10:33:09.863454+00
e45598bd-489c-42d0-915b-415b1e9517f4	bf660c8b-3818-4cf7-85f1-3071c0a7943c	1118a620-482f-4241-b722-35653792fda9	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:33:09.894433+00	bf660c8b-3818-4cf7-85f1-3071c0a7943c	2026-02-01 10:33:09.883035+00
5d7324d8-21f2-4a3c-ad91-d32ce2d3421d	3c1aab18-4eb2-4ab2-bcca-993c37e7fab1	13bd2caa-40a9-450f-9df0-7a7c110e49ac	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:33:31.907578+00	3c1aab18-4eb2-4ab2-bcca-993c37e7fab1	2026-02-01 10:33:31.896879+00
a9c81651-0727-4714-85f5-690967b14542	c7a092a7-d354-498d-b23a-d4802d99ccb4	cbbff567-e72f-46ff-ad79-4cf26c3260c8	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:33:31.926243+00	c7a092a7-d354-498d-b23a-d4802d99ccb4	2026-02-01 10:33:31.914688+00
5ca905de-d5da-4004-8ec8-8c21dc6a6952	3e72bdbc-89a7-4009-a93e-bba6fec86530	65e03c0d-7af5-4622-b2a2-8a867cf708a5	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:34:04.298955+00	3e72bdbc-89a7-4009-a93e-bba6fec86530	2026-02-01 10:34:04.288135+00
3e8f1b7b-e711-4947-9dbe-35d3924758c7	2199f334-fccd-46ff-b45c-2cd81aadeca2	6bf71e9a-2b50-4a27-9ff9-972b5a52eb8e	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:34:04.316669+00	2199f334-fccd-46ff-b45c-2cd81aadeca2	2026-02-01 10:34:04.305723+00
94719340-3951-4978-b8e1-5e4d82b4f4d9	c5e779fa-7e25-4b84-b410-a55bd0c9e219	c883192d-5000-4f2a-882c-3e8d3d49d4f6	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:34:21.850424+00	c5e779fa-7e25-4b84-b410-a55bd0c9e219	2026-02-01 10:34:21.83799+00
09559f62-9488-4d6c-9234-83501910fe2d	b46ab366-7dcb-4ee5-a558-dc328db04159	461445ad-b03d-418c-8049-49cbadf6519b	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:34:21.86989+00	b46ab366-7dcb-4ee5-a558-dc328db04159	2026-02-01 10:34:21.858165+00
3ed0147b-a1b5-4c36-8b87-c5e9f916a980	b8cf8398-0dff-42c3-99ab-aaa2bcf646e6	bc9ba376-ec2d-4293-a39d-22daa59a0236	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:34:42.439094+00	b8cf8398-0dff-42c3-99ab-aaa2bcf646e6	2026-02-01 10:34:42.423614+00
7911ef0e-af54-4bad-a178-76a56b42e695	979cfcfd-a872-40df-8380-dbe81f29e7a5	c6957a10-58cf-4f2d-ab85-b8b0dbd6ed7c	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:34:42.466858+00	979cfcfd-a872-40df-8380-dbe81f29e7a5	2026-02-01 10:34:42.450061+00
fe88e5f0-cab2-4723-af4e-b0dd033823ae	a031994b-5afb-4fa2-9d8a-8004d7e8c9a3	bf66b4c8-e589-4240-9949-928683f45020	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:35:07.781358+00	a031994b-5afb-4fa2-9d8a-8004d7e8c9a3	2026-02-01 10:35:07.770218+00
9b8fef3f-dc86-4e41-a53c-9a9599f798b2	810cc398-af79-4d96-9eee-af0f1bbf8683	36acd251-59ee-4f22-a3e3-f14e91a16706	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:35:07.801875+00	810cc398-af79-4d96-9eee-af0f1bbf8683	2026-02-01 10:35:07.78949+00
99d403c9-1897-4296-a011-a85cf693b1d2	2e6f6fed-9d3d-4b85-87d0-a134932d0dd7	ea925230-a27d-4bf3-9187-877dab140c8b	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:35:47.947648+00	2e6f6fed-9d3d-4b85-87d0-a134932d0dd7	2026-02-01 10:35:47.935151+00
b5626acf-26a5-4d35-ae99-c3593be0fbb6	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	ba0154e3-56bb-4d8d-9db9-b143367cbc85	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:35:47.964821+00	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	2026-02-01 10:35:47.954813+00
fb359fae-5cd1-48ab-a3bd-02f8eef14011	d77da629-52f1-46c9-9118-dbe7fe92c333	5d712ef0-dfcc-4e49-ba75-0d15424f0409	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:36:43.835907+00	d77da629-52f1-46c9-9118-dbe7fe92c333	2026-02-01 10:36:43.810068+00
49f8e2d4-59bd-4a77-865b-905a42bd3a51	ef5984b4-54b6-47cf-a9bb-ca02cadc0180	eb79439d-c6df-4d41-8c3d-0619964d91e1	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:36:43.854601+00	ef5984b4-54b6-47cf-a9bb-ca02cadc0180	2026-02-01 10:36:43.844231+00
d00e0efe-15fe-42b2-b542-2da63982efe2	66d51b1b-c21b-4f8c-99ba-c2854ceeab97	e69d30db-071e-4079-9a43-3267a66927a9	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:37:05.029789+00	66d51b1b-c21b-4f8c-99ba-c2854ceeab97	2026-02-01 10:37:05.016176+00
80bd2596-4c2e-4e72-a78d-92bac96ab983	70904796-fe39-4007-b892-a8aa3c8e0e8f	d1a8266c-b125-4c57-b1d9-69f785e7e7ec	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:37:05.050712+00	70904796-fe39-4007-b892-a8aa3c8e0e8f	2026-02-01 10:37:05.038749+00
2926d45c-a4c2-4e4a-be60-68e3860a9c7a	3f82b4a7-b270-4d68-9e02-e9068eaa668f	aa001d98-fda0-4f0f-971e-361f1af462ad	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:38:13.185955+00	3f82b4a7-b270-4d68-9e02-e9068eaa668f	2026-02-01 10:38:13.173852+00
d50960ba-33c5-41d2-ac73-b06d03d29255	1ce1ba48-b899-4217-8fd9-2124dd4765c6	c4a4f415-3907-463e-86e0-2d7148e90d28	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:38:13.203356+00	1ce1ba48-b899-4217-8fd9-2124dd4765c6	2026-02-01 10:38:13.192723+00
dd25d5ce-560a-42a7-bfde-926046dc2d25	d5104c40-d4cc-47ac-a700-0c7414c1b26a	62656d65-00b9-4446-b11a-586d60d38c8c	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 10:38:59.000194+00	d5104c40-d4cc-47ac-a700-0c7414c1b26a	2026-02-01 10:38:58.972558+00
e9afd4df-0d90-42f9-bfd7-1684402f321e	05e362b8-0b73-44ed-bded-ef4e0a40dd47	ab3df532-1696-45db-a97f-ebd3afaee92c	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 10:38:59.029379+00	05e362b8-0b73-44ed-bded-ef4e0a40dd47	2026-02-01 10:38:59.014481+00
8a89cb49-700e-4bc5-80e7-81033192e931	fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1	f4b08735-4038-49dd-bed2-4cb44e9c9287	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 11:01:39.511651+00	fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1	2026-02-01 11:01:39.499064+00
f7fbeb95-472a-44d6-830e-b798b9c296f3	b9c25548-e5ba-4200-9dc9-1ba98f332540	c0fbcba5-fca1-4960-88fb-5a5aeb9684e3	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 11:01:39.528569+00	b9c25548-e5ba-4200-9dc9-1ba98f332540	2026-02-01 11:01:39.51794+00
dd1e56c6-86ac-462c-b55f-0e9fca618473	1a8f4448-290b-48ff-9f17-2d76e841a1f3	2ec2a2b1-87f2-4962-8649-c029973d9504	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-01 11:06:38.548366+00	1a8f4448-290b-48ff-9f17-2d76e841a1f3	2026-02-01 11:06:38.534223+00
0f11a1dc-4752-44e2-8bf9-404aa3bf9c26	a30a9865-926a-4d26-af0d-42e44657b429	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-01 11:06:38.570913+00	a30a9865-926a-4d26-af0d-42e44657b429	2026-02-01 11:06:38.557163+00
2e4d5517-ad86-4a14-8512-f936b7e2716f	43a76c7a-3acb-40a9-8c3c-9e0235d9a13f	88d1dc02-6962-4103-a0b1-141c0553ebb4	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:25:33.382028+00	43a76c7a-3acb-40a9-8c3c-9e0235d9a13f	2026-02-05 21:25:33.314326+00
9aec0de9-3b64-4da5-9764-58bb1d3d9e90	5526632a-9523-4219-b2ca-708559772fb8	11a75d4a-ecef-4ae0-9767-790dcf59ba5c	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:25:33.405515+00	5526632a-9523-4219-b2ca-708559772fb8	2026-02-05 21:25:33.393877+00
57ee3257-532f-46d0-a6a0-aadcd6581e25	dcc8f7e0-c4a6-4f72-b21e-78331c825d3e	e21f1598-e198-4e06-b82e-c53822730dc8	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:28:19.956562+00	dcc8f7e0-c4a6-4f72-b21e-78331c825d3e	2026-02-05 21:28:19.885149+00
a8f1cc44-e4f0-4733-b64f-4d4d6928575b	5847755d-a7ef-4f01-ad83-b96116cc5b06	e5faaf23-44f2-419b-8226-8d3b25615c9a	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:28:19.988681+00	5847755d-a7ef-4f01-ad83-b96116cc5b06	2026-02-05 21:28:19.975005+00
129db253-4e88-4d71-b690-24606ca0204c	274bca62-6a26-40f4-ab29-482816286c94	a33afb2d-870e-4263-88fa-9e2cb085a8f7	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:30:53.406171+00	274bca62-6a26-40f4-ab29-482816286c94	2026-02-05 21:30:53.394261+00
e6adad6c-09fe-43fe-942a-8608f9eda451	3ca9cf6b-c372-4530-bc35-3440c68f858f	8aac186d-15a6-4ce9-94d7-89e8b6eee47d	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:30:53.426003+00	3ca9cf6b-c372-4530-bc35-3440c68f858f	2026-02-05 21:30:53.415111+00
22505656-e22e-4921-a859-1c9d85029cd5	53126f3a-94da-4363-b20d-61a85c99574a	27227759-8c29-4ba3-8ba5-153607db5c4c	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:31:42.444981+00	53126f3a-94da-4363-b20d-61a85c99574a	2026-02-05 21:31:42.432788+00
aa5b2259-4c17-49d9-82f4-fc2fd2ae2948	09b95fab-3a52-4e54-8957-76e81ebf668a	675f5900-0a12-48ea-a2a9-c121508fc23e	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:31:42.463809+00	09b95fab-3a52-4e54-8957-76e81ebf668a	2026-02-05 21:31:42.452616+00
3d0eaa60-cd18-4bbb-a1c7-acb177e5794c	1214c599-c7c2-490b-a895-e45b985b027b	bc651c65-73d1-41c9-a03a-275b47df7b10	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:33:44.837462+00	1214c599-c7c2-490b-a895-e45b985b027b	2026-02-05 21:33:44.820324+00
65147056-840c-4ae1-a1ba-984127629587	39219340-21cb-4a88-a939-93baf1a0e840	92a020f4-c327-4f4d-8df3-c7ed0d120871	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:33:44.85871+00	39219340-21cb-4a88-a939-93baf1a0e840	2026-02-05 21:33:44.846462+00
fe34b4f3-8ae4-4129-9854-a67e2901a1ea	d9cd5b64-e423-4710-bcfe-73606bcca78c	0a61f5ac-582c-4856-8072-27fcad588698	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:34:40.951588+00	d9cd5b64-e423-4710-bcfe-73606bcca78c	2026-02-05 21:34:40.938633+00
6e29fc54-beff-4587-97ee-6296bb64694e	5368cfba-bae0-4132-88e4-4fde67d9e523	96ce9467-4d9c-42ac-8fd7-6b4980cb4662	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:34:40.973271+00	5368cfba-bae0-4132-88e4-4fde67d9e523	2026-02-05 21:34:40.96158+00
8ca21102-d220-4296-a466-a50834fbfcf3	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	88810bde-bf96-43e8-9791-937cd4a7e062	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:36:32.471718+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	2026-02-05 21:36:32.459385+00
815d9d99-2266-4add-b474-0ec7b860242e	222968c5-f7cd-46a9-80a7-ae6d0557b5c3	2328d476-0c17-4452-adc8-7cf00f24669b	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:36:32.491799+00	222968c5-f7cd-46a9-80a7-ae6d0557b5c3	2026-02-05 21:36:32.480874+00
12e51b51-adc6-476a-b6b8-a18ba31629fe	fc5165e6-6519-496f-a3dd-1435bc308b5f	5e03962b-3b0c-4bd5-9f17-6349e82083cb	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:39:33.245079+00	fc5165e6-6519-496f-a3dd-1435bc308b5f	2026-02-05 21:39:33.231881+00
be0440c5-1894-4790-bebd-e13681576836	2b8bb712-3cfe-435e-84f7-49dfe73d641b	9e0c3eda-2c52-4792-abd4-288131229066	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:39:33.295616+00	2b8bb712-3cfe-435e-84f7-49dfe73d641b	2026-02-05 21:39:33.280683+00
1a03937f-fb88-4f6b-a603-30d12963d28f	021aea9d-7fe9-4488-ae61-eebf6d2af731	f9761969-f234-4bb8-9b46-2ea70ad5b735	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:55:18.064121+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	2026-02-05 21:55:18.035785+00
f7ff3717-02ca-4915-b052-3c84bb97724f	1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3	dcb6e693-f204-46fd-bbca-8eab795cc81a	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:55:18.092079+00	1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3	2026-02-05 21:55:18.07477+00
307795b9-1e74-4ad8-bb98-cf96aba84429	d655e067-4edd-4516-b1b6-821c3c33cfc5	8bb34a8d-f5bb-41cf-ba29-87e5c652c03f	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:40:37.248291+00	d655e067-4edd-4516-b1b6-821c3c33cfc5	2026-02-05 21:40:37.227805+00
66e28af3-3c68-4aa2-8bb3-6711431a6c54	ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f	c5992875-1ecb-42f0-b461-e177f1775d46	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:40:37.277463+00	ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f	2026-02-05 21:40:37.261894+00
342ae634-1ddb-4f43-9d13-f8ce1d7931c0	2e7c5e4c-423c-4bd0-9f3d-e359054f285a	\N	893a1f71-b524-4995-91a0-c1f44db37066	t	2026-02-05 21:57:41.374707+00	\N	2026-02-05 21:57:41.374707+00
e611cd21-f654-438d-800f-31bf3661b19c	13ac055f-b943-4f6d-8182-babe636544df	f3200c57-c6b8-4f2d-80fe-24b9a6359f6c	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:41:47.04882+00	13ac055f-b943-4f6d-8182-babe636544df	2026-02-05 21:41:47.032031+00
af58bb29-fc67-402e-968d-db2a91a0d5b4	eb271702-3161-48b2-a4c9-8747819b7ae7	f878c129-1bbb-4dca-bcfc-d21ea54fb41f	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:41:47.073069+00	eb271702-3161-48b2-a4c9-8747819b7ae7	2026-02-05 21:41:47.058236+00
381e3715-4d01-47e7-a1c6-99d743ef6048	088ad156-635f-4689-8a9f-31187419e964	f2d7a38d-6265-4cd5-9743-be932e8693c0	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:57:41.72729+00	088ad156-635f-4689-8a9f-31187419e964	2026-02-05 21:57:41.707705+00
d3e9f789-2186-43c8-887e-f3ef84d7d05c	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	f7028cb1-7e87-4fd7-8aa1-4ea8b97ccb43	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:43:42.409332+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	2026-02-05 21:43:42.370197+00
c17fa73d-5c0b-4999-a6f8-af9f57c00e05	31148b05-1512-43ce-8b01-fd3b423fca6e	1d66de05-6ab3-461b-94d0-0750153aa2d9	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:43:42.428486+00	31148b05-1512-43ce-8b01-fd3b423fca6e	2026-02-05 21:43:42.418516+00
153011a7-7a33-4634-b924-6c92a690a348	723079fb-4d41-408d-958c-a1d417576d82	a7bc280f-69bc-4b03-98d8-de195f8f95bf	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 22:33:46.126563+00	723079fb-4d41-408d-958c-a1d417576d82	2026-02-05 22:33:46.084547+00
25b23d7c-9147-4957-873f-71985898e2e6	ebc86578-b9a2-456f-b884-f964c1fb26f9	e33b94b6-cfc5-4d7e-98a4-2259867e45b4	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:49:54.797765+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	2026-02-05 21:49:54.762913+00
14996ef2-3fa7-4c18-ab6f-745cb289f8e4	3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167	8229af4d-838a-4d32-ac0b-9eadffbbcff8	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:49:54.815736+00	3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167	2026-02-05 21:49:54.805663+00
f4375c66-2f95-4c4d-9f2b-31e2d023719a	b1dd0b01-8388-41bb-a686-f75f5aa559b9	e8718468-ad6e-4157-bbc8-3ad3a0047082	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 22:33:46.152792+00	b1dd0b01-8388-41bb-a686-f75f5aa559b9	2026-02-05 22:33:46.136131+00
5e38190c-074c-4156-ac85-02ee96ae977a	7eddd813-1060-42a3-aa36-abc2c6529e0f	718996de-ba3d-4b71-9a19-a6e97d2947ee	a98b7297-3bd8-4084-8dd4-ca156371f1c5	t	2026-02-05 21:52:18.511186+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	2026-02-05 21:52:18.471949+00
34ec27fb-bc13-403d-9615-18b66abba066	83e1d52b-a86b-461a-b995-e79e2ac57878	b86839bf-62f6-4f3c-8748-5bdeaaa323a6	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	t	2026-02-05 21:52:18.535541+00	83e1d52b-a86b-461a-b995-e79e2ac57878	2026-02-05 21:52:18.522191+00
8672eb34-3ec2-4e1a-a543-f85bc6d63741	c5154fda-1c6a-4c09-bd67-0482fe81f7d8	5ae66809-e7de-448a-8f42-920a192c8704	aa22c090-2bef-4796-96e9-885a3c206545	t	2026-02-09 14:46:47.509266+00	c5154fda-1c6a-4c09-bd67-0482fe81f7d8	2026-02-09 14:46:47.499889+00
\.


--
-- Data for Name: org_members; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.org_members (id, user_id, organization_id, status, joined_at, left_at, invited_by, invitation_id, created_at, updated_at) FROM stdin;
b041d8be-3dab-4b37-9548-6ec506ff08a4	3f3a3a39-d867-45a8-b901-74a7e27c95f3	8b411c61-9885-4672-ba08-e45709934575	ACTIVE	2026-01-30 00:08:38.868186+00	\N	\N	\N	2026-01-30 00:08:38.868186+00	2026-01-30 00:08:38.868186+00
c135cee7-d306-442f-afef-fa83cb954f88	08c368c7-0ea2-4dad-a5fe-5e8e180b0b44	8b411c61-9885-4672-ba08-e45709934575	ACTIVE	2026-01-30 00:08:38.878468+00	\N	\N	\N	2026-01-30 00:08:38.878468+00	2026-01-30 00:08:38.878468+00
324890c3-2960-41fb-919a-0926a6cfa377	f5f9ef2a-8a6f-4973-900c-0e0bca8ee95c	8b411c61-9885-4672-ba08-e45709934575	ACTIVE	2026-01-30 00:08:38.888877+00	\N	\N	\N	2026-01-30 00:08:38.888877+00	2026-01-30 00:08:38.888877+00
5f397e89-a86d-49af-81d3-f63706b26a04	7bd0073c-4c78-429f-9421-d5d52db3fd53	8b411c61-9885-4672-ba08-e45709934575	ACTIVE	2026-01-30 00:08:38.89581+00	\N	\N	\N	2026-01-30 00:08:38.89581+00	2026-01-30 00:08:38.89581+00
6b91c0c9-18eb-44f0-bd08-e964553f8bee	fe4d1e04-7569-409d-8bfc-f7319e7ea582	1455677e-0753-44c1-959e-06c542a28884	ACTIVE	2026-01-30 00:08:38.963073+00	\N	\N	\N	2026-01-30 00:08:38.963073+00	2026-01-30 00:08:38.963073+00
35e3433c-5416-4d3c-a314-e9a34984215e	3f3a3a39-d867-45a8-b901-74a7e27c95f3	5ae66809-e7de-448a-8f42-920a192c8704	ACTIVE	2026-01-30 00:12:20.649738+00	\N	\N	\N	2026-01-30 00:12:20.626621+00	2026-01-30 00:12:20.626621+00
0310dd9c-f771-429b-a035-86f55493b1b5	bfdafb1c-258c-487a-84a9-8df88d6f7efd	6ccc83ff-6dd6-45b8-9285-d189eec284e9	ACTIVE	2026-02-01 10:04:58.636319+00	\N	\N	\N	2026-02-01 10:04:58.583848+00	2026-02-01 10:04:58.583848+00
f6c90c74-97e5-4aad-a385-5652cbc8591c	a7c620dc-005f-41e4-a09c-84a578fdff32	9a08dd9e-37f1-466a-9cce-b38722c3c08d	ACTIVE	2026-02-01 10:06:48.531139+00	\N	\N	\N	2026-02-01 10:06:48.520888+00	2026-02-01 10:06:48.520888+00
55b52c12-6fcf-447b-b438-27fc57150800	ea72b36b-fe10-483e-acca-7274bdab7600	74faf449-2f3a-4cdf-a1a6-6294eabc51b9	ACTIVE	2026-02-01 10:06:48.552142+00	\N	\N	\N	2026-02-01 10:06:48.540544+00	2026-02-01 10:06:48.540544+00
95b9cc40-eee3-41cd-a4dc-58e012edff37	eb63636b-e512-4cd7-9296-f0d38d62f74d	d21c407f-5ec7-4940-9863-903fc66fb45f	ACTIVE	2026-02-01 10:10:07.285509+00	\N	\N	\N	2026-02-01 10:10:07.26914+00	2026-02-01 10:10:07.26914+00
c1287731-b0a2-48d1-bbeb-7618b09b9666	fc777437-f8d9-4e04-bc0a-011507805218	5986b068-6433-4eb3-907f-79e9e5ae4bd2	ACTIVE	2026-02-01 10:10:07.310369+00	\N	\N	\N	2026-02-01 10:10:07.29576+00	2026-02-01 10:10:07.29576+00
3002dd0b-bd5e-4be7-a4a6-74570c33032e	26872c85-6000-4eec-baab-a1a4b8a27258	4309e43b-b68e-4834-8de3-a824a0bf37ab	ACTIVE	2026-02-01 10:30:00.507868+00	\N	\N	\N	2026-02-01 10:30:00.498111+00	2026-02-01 10:30:00.498111+00
c7b57ab1-bdc9-47b9-8458-487470cded44	d24c619c-0783-4510-949c-49445cea0202	bc9a3480-c0ad-43c6-ab08-5fc8362d34b2	ACTIVE	2026-02-01 10:30:00.525537+00	\N	\N	\N	2026-02-01 10:30:00.515811+00	2026-02-01 10:30:00.515811+00
616f3ee8-214b-4f96-809b-a8759910d4a2	aec76aa4-0bf4-40bb-9307-de54a5d205a5	efa7b0ac-291d-489e-94f5-b7e09ee61211	ACTIVE	2026-02-01 10:31:21.073547+00	\N	\N	\N	2026-02-01 10:31:21.06163+00	2026-02-01 10:31:21.06163+00
7ddf63d7-973f-4869-9ce7-7fcb944ae1e6	5b010aef-d0b8-40cc-bc0e-6b6c133cac49	db3950f7-2c3d-40ec-8646-9548956aa267	ACTIVE	2026-02-01 10:31:21.092691+00	\N	\N	\N	2026-02-01 10:31:21.08214+00	2026-02-01 10:31:21.08214+00
dd869093-5402-461a-b5e6-85a834b0bf1c	ee6157bd-176f-4f75-8cea-64adb841884f	23f17148-f316-4fb6-8fd4-c4f2045ae401	ACTIVE	2026-02-01 10:32:49.168213+00	\N	\N	\N	2026-02-01 10:32:49.157574+00	2026-02-01 10:32:49.157574+00
f9979332-310f-4c87-8375-3245083b5ce5	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c	9463b7f0-b657-467c-bc0e-0f21817e623c	ACTIVE	2026-02-01 10:32:49.186457+00	\N	\N	\N	2026-02-01 10:32:49.176666+00	2026-02-01 10:32:49.176666+00
6a8db71e-c72f-4904-846d-213fa7c48230	ee193894-167a-4355-8899-7c19ba395e9f	cc35b76b-375c-4261-8fa4-24b833a63cdb	ACTIVE	2026-02-01 10:33:09.874939+00	\N	\N	\N	2026-02-01 10:33:09.863454+00	2026-02-01 10:33:09.863454+00
4424cab6-0562-44a9-8c7e-eccc6ba2d92c	bf660c8b-3818-4cf7-85f1-3071c0a7943c	1118a620-482f-4241-b722-35653792fda9	ACTIVE	2026-02-01 10:33:09.8935+00	\N	\N	\N	2026-02-01 10:33:09.883035+00	2026-02-01 10:33:09.883035+00
a870db60-1687-457e-b335-282ca3cde382	3c1aab18-4eb2-4ab2-bcca-993c37e7fab1	13bd2caa-40a9-450f-9df0-7a7c110e49ac	ACTIVE	2026-02-01 10:33:31.906835+00	\N	\N	\N	2026-02-01 10:33:31.896879+00	2026-02-01 10:33:31.896879+00
a7bdb44c-0adb-4be4-b18c-ae1441e63052	c7a092a7-d354-498d-b23a-d4802d99ccb4	cbbff567-e72f-46ff-ad79-4cf26c3260c8	ACTIVE	2026-02-01 10:33:31.925512+00	\N	\N	\N	2026-02-01 10:33:31.914688+00	2026-02-01 10:33:31.914688+00
023b1c1a-c327-4e1e-915c-6f0f0448b4bd	3e72bdbc-89a7-4009-a93e-bba6fec86530	65e03c0d-7af5-4622-b2a2-8a867cf708a5	ACTIVE	2026-02-01 10:34:04.298281+00	\N	\N	\N	2026-02-01 10:34:04.288135+00	2026-02-01 10:34:04.288135+00
5c049678-e613-46fe-babe-ace929cfd9bb	2199f334-fccd-46ff-b45c-2cd81aadeca2	6bf71e9a-2b50-4a27-9ff9-972b5a52eb8e	ACTIVE	2026-02-01 10:34:04.315913+00	\N	\N	\N	2026-02-01 10:34:04.305723+00	2026-02-01 10:34:04.305723+00
bfa18c92-b3c4-4739-b1b7-ec379dbdb90a	c5e779fa-7e25-4b84-b410-a55bd0c9e219	c883192d-5000-4f2a-882c-3e8d3d49d4f6	ACTIVE	2026-02-01 10:34:21.849714+00	\N	\N	\N	2026-02-01 10:34:21.83799+00	2026-02-01 10:34:21.83799+00
86eb8cbf-6ea7-48d8-a8ed-753b1d6b2ccc	b46ab366-7dcb-4ee5-a558-dc328db04159	461445ad-b03d-418c-8049-49cbadf6519b	ACTIVE	2026-02-01 10:34:21.869115+00	\N	\N	\N	2026-02-01 10:34:21.858165+00	2026-02-01 10:34:21.858165+00
108eac7d-131a-4c58-ab00-97ebc1a26d58	b8cf8398-0dff-42c3-99ab-aaa2bcf646e6	bc9ba376-ec2d-4293-a39d-22daa59a0236	ACTIVE	2026-02-01 10:34:42.438044+00	\N	\N	\N	2026-02-01 10:34:42.423614+00	2026-02-01 10:34:42.423614+00
9b1c9d15-d96b-4151-85cb-f9121ed86e80	979cfcfd-a872-40df-8380-dbe81f29e7a5	c6957a10-58cf-4f2d-ab85-b8b0dbd6ed7c	ACTIVE	2026-02-01 10:34:42.46575+00	\N	\N	\N	2026-02-01 10:34:42.450061+00	2026-02-01 10:34:42.450061+00
ccbcd106-dac1-4f32-bba5-21b196c27377	a031994b-5afb-4fa2-9d8a-8004d7e8c9a3	bf66b4c8-e589-4240-9949-928683f45020	ACTIVE	2026-02-01 10:35:07.780396+00	\N	\N	\N	2026-02-01 10:35:07.770218+00	2026-02-01 10:35:07.770218+00
2d4b6178-9f09-4f33-a9f6-d219ebb3ca9a	810cc398-af79-4d96-9eee-af0f1bbf8683	36acd251-59ee-4f22-a3e3-f14e91a16706	ACTIVE	2026-02-01 10:35:07.800993+00	\N	\N	\N	2026-02-01 10:35:07.78949+00	2026-02-01 10:35:07.78949+00
22d823d0-54c8-464e-8091-5283e524e73a	2e6f6fed-9d3d-4b85-87d0-a134932d0dd7	ea925230-a27d-4bf3-9187-877dab140c8b	ACTIVE	2026-02-01 10:35:47.946887+00	\N	\N	\N	2026-02-01 10:35:47.935151+00	2026-02-01 10:35:47.935151+00
784e5e83-e466-4663-92b7-1c9dabc954e3	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	ba0154e3-56bb-4d8d-9db9-b143367cbc85	ACTIVE	2026-02-01 10:35:47.964086+00	\N	\N	\N	2026-02-01 10:35:47.954813+00	2026-02-01 10:35:47.954813+00
806a2da4-9956-43ab-b2c1-3629940ff127	d77da629-52f1-46c9-9118-dbe7fe92c333	5d712ef0-dfcc-4e49-ba75-0d15424f0409	ACTIVE	2026-02-01 10:36:43.834339+00	\N	\N	\N	2026-02-01 10:36:43.810068+00	2026-02-01 10:36:43.810068+00
9e001a16-266e-4f54-b5b8-7b1217d7fdbc	ef5984b4-54b6-47cf-a9bb-ca02cadc0180	eb79439d-c6df-4d41-8c3d-0619964d91e1	ACTIVE	2026-02-01 10:36:43.85389+00	\N	\N	\N	2026-02-01 10:36:43.844231+00	2026-02-01 10:36:43.844231+00
83336ac8-a3f0-4968-b9aa-4cda1e9b6f28	66d51b1b-c21b-4f8c-99ba-c2854ceeab97	e69d30db-071e-4079-9a43-3267a66927a9	ACTIVE	2026-02-01 10:37:05.028864+00	\N	\N	\N	2026-02-01 10:37:05.016176+00	2026-02-01 10:37:05.016176+00
5789c464-2dbe-4403-bde8-b2e1a4c83653	70904796-fe39-4007-b892-a8aa3c8e0e8f	d1a8266c-b125-4c57-b1d9-69f785e7e7ec	ACTIVE	2026-02-01 10:37:05.049875+00	\N	\N	\N	2026-02-01 10:37:05.038749+00	2026-02-01 10:37:05.038749+00
796b4142-ed31-447e-8f29-dd1c6920770f	3f82b4a7-b270-4d68-9e02-e9068eaa668f	aa001d98-fda0-4f0f-971e-361f1af462ad	ACTIVE	2026-02-01 10:38:13.184994+00	\N	\N	\N	2026-02-01 10:38:13.173852+00	2026-02-01 10:38:13.173852+00
db154914-43eb-40a4-8d29-7a1e8b74d1f1	1ce1ba48-b899-4217-8fd9-2124dd4765c6	c4a4f415-3907-463e-86e0-2d7148e90d28	ACTIVE	2026-02-01 10:38:13.202584+00	\N	\N	\N	2026-02-01 10:38:13.192723+00	2026-02-01 10:38:13.192723+00
4c6b5cd5-4733-453a-9601-983b79bd8a12	d5104c40-d4cc-47ac-a700-0c7414c1b26a	62656d65-00b9-4446-b11a-586d60d38c8c	ACTIVE	2026-02-01 10:38:58.998461+00	\N	\N	\N	2026-02-01 10:38:58.972558+00	2026-02-01 10:38:58.972558+00
7e4a0cea-e82f-4505-8c7d-b8321152380e	05e362b8-0b73-44ed-bded-ef4e0a40dd47	ab3df532-1696-45db-a97f-ebd3afaee92c	ACTIVE	2026-02-01 10:38:59.028356+00	\N	\N	\N	2026-02-01 10:38:59.014481+00	2026-02-01 10:38:59.014481+00
fc04ccda-7cc2-46d6-b77a-fbaac67eb3c7	fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1	f4b08735-4038-49dd-bed2-4cb44e9c9287	ACTIVE	2026-02-01 11:01:39.510804+00	\N	\N	\N	2026-02-01 11:01:39.499064+00	2026-02-01 11:01:39.499064+00
9be1cdc8-9453-4bea-898f-15edab62f2e7	b9c25548-e5ba-4200-9dc9-1ba98f332540	c0fbcba5-fca1-4960-88fb-5a5aeb9684e3	ACTIVE	2026-02-01 11:01:39.527786+00	\N	\N	\N	2026-02-01 11:01:39.51794+00	2026-02-01 11:01:39.51794+00
0fef2215-10c2-47b0-95a2-2a382e1d6407	1a8f4448-290b-48ff-9f17-2d76e841a1f3	2ec2a2b1-87f2-4962-8649-c029973d9504	ACTIVE	2026-02-01 11:06:38.547327+00	\N	\N	\N	2026-02-01 11:06:38.534223+00	2026-02-01 11:06:38.534223+00
814358b1-815e-4da2-8325-e370207df0be	a30a9865-926a-4d26-af0d-42e44657b429	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	ACTIVE	2026-02-01 11:06:38.569857+00	\N	\N	\N	2026-02-01 11:06:38.557163+00	2026-02-01 11:06:38.557163+00
10d4b199-df82-45a8-aa0e-1d54099fec73	43a76c7a-3acb-40a9-8c3c-9e0235d9a13f	88d1dc02-6962-4103-a0b1-141c0553ebb4	ACTIVE	2026-02-05 21:25:33.377354+00	\N	\N	\N	2026-02-05 21:25:33.314326+00	2026-02-05 21:25:33.314326+00
7de9cbe8-4174-4034-bede-258b69082775	5526632a-9523-4219-b2ca-708559772fb8	11a75d4a-ecef-4ae0-9767-790dcf59ba5c	ACTIVE	2026-02-05 21:25:33.404848+00	\N	\N	\N	2026-02-05 21:25:33.393877+00	2026-02-05 21:25:33.393877+00
1a2e0f7b-1a53-4929-af70-52a64431a3e4	dcc8f7e0-c4a6-4f72-b21e-78331c825d3e	e21f1598-e198-4e06-b82e-c53822730dc8	ACTIVE	2026-02-05 21:28:19.954073+00	\N	\N	\N	2026-02-05 21:28:19.885149+00	2026-02-05 21:28:19.885149+00
b9cae418-1354-40d9-ad8c-03dc0f3934b2	5847755d-a7ef-4f01-ad83-b96116cc5b06	e5faaf23-44f2-419b-8226-8d3b25615c9a	ACTIVE	2026-02-05 21:28:19.98781+00	\N	\N	\N	2026-02-05 21:28:19.975005+00	2026-02-05 21:28:19.975005+00
9fd79eb2-d7b0-4f73-af91-f360f1aae2bf	274bca62-6a26-40f4-ab29-482816286c94	a33afb2d-870e-4263-88fa-9e2cb085a8f7	ACTIVE	2026-02-05 21:30:53.40536+00	\N	\N	\N	2026-02-05 21:30:53.394261+00	2026-02-05 21:30:53.394261+00
5991b8db-f5df-484e-ba49-aecd3a14495c	3ca9cf6b-c372-4530-bc35-3440c68f858f	8aac186d-15a6-4ce9-94d7-89e8b6eee47d	ACTIVE	2026-02-05 21:30:53.425328+00	\N	\N	\N	2026-02-05 21:30:53.415111+00	2026-02-05 21:30:53.415111+00
22b7509b-d756-41a1-aad4-abf2e4bd7a79	53126f3a-94da-4363-b20d-61a85c99574a	27227759-8c29-4ba3-8ba5-153607db5c4c	ACTIVE	2026-02-05 21:31:42.44446+00	\N	\N	\N	2026-02-05 21:31:42.432788+00	2026-02-05 21:31:42.432788+00
c63b88d6-5c84-44fe-8e1c-5483ef09e096	09b95fab-3a52-4e54-8957-76e81ebf668a	675f5900-0a12-48ea-a2a9-c121508fc23e	ACTIVE	2026-02-05 21:31:42.463157+00	\N	\N	\N	2026-02-05 21:31:42.452616+00	2026-02-05 21:31:42.452616+00
8480dd95-4eaa-49a3-b2f3-0af7fe81a434	1214c599-c7c2-490b-a895-e45b985b027b	bc651c65-73d1-41c9-a03a-275b47df7b10	ACTIVE	2026-02-05 21:33:44.836336+00	\N	\N	\N	2026-02-05 21:33:44.820324+00	2026-02-05 21:33:44.820324+00
13d1262d-bd6f-4fb1-bedd-f2e7002fc06b	39219340-21cb-4a88-a939-93baf1a0e840	92a020f4-c327-4f4d-8df3-c7ed0d120871	ACTIVE	2026-02-05 21:33:44.858094+00	\N	\N	\N	2026-02-05 21:33:44.846462+00	2026-02-05 21:33:44.846462+00
1d7b3cf0-6a73-4968-b559-8d2904c72108	d9cd5b64-e423-4710-bcfe-73606bcca78c	0a61f5ac-582c-4856-8072-27fcad588698	ACTIVE	2026-02-05 21:34:40.950773+00	\N	\N	\N	2026-02-05 21:34:40.938633+00	2026-02-05 21:34:40.938633+00
80d47b15-bd1d-4068-8be9-5dc3839918d2	5368cfba-bae0-4132-88e4-4fde67d9e523	96ce9467-4d9c-42ac-8fd7-6b4980cb4662	ACTIVE	2026-02-05 21:34:40.972412+00	\N	\N	\N	2026-02-05 21:34:40.96158+00	2026-02-05 21:34:40.96158+00
0523e7dd-4753-4c35-9f0c-6072c3643ca8	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	88810bde-bf96-43e8-9791-937cd4a7e062	ACTIVE	2026-02-05 21:36:32.470968+00	\N	\N	\N	2026-02-05 21:36:32.459385+00	2026-02-05 21:36:32.459385+00
43374709-676e-4dda-af6f-0e4a96b2b635	222968c5-f7cd-46a9-80a7-ae6d0557b5c3	2328d476-0c17-4452-adc8-7cf00f24669b	ACTIVE	2026-02-05 21:36:32.491135+00	\N	\N	\N	2026-02-05 21:36:32.480874+00	2026-02-05 21:36:32.480874+00
3a48487b-a32f-4ae6-b788-62fd0c7f611b	fc5165e6-6519-496f-a3dd-1435bc308b5f	5e03962b-3b0c-4bd5-9f17-6349e82083cb	ACTIVE	2026-02-05 21:39:33.244121+00	\N	\N	\N	2026-02-05 21:39:33.231881+00	2026-02-05 21:39:33.231881+00
dfcc25e5-3922-42b2-8da1-0f0312134b40	2b8bb712-3cfe-435e-84f7-49dfe73d641b	9e0c3eda-2c52-4792-abd4-288131229066	ACTIVE	2026-02-05 21:39:33.294873+00	\N	\N	\N	2026-02-05 21:39:33.280683+00	2026-02-05 21:39:33.280683+00
11f974e1-5cab-4cc6-967e-eeb007f590a6	d655e067-4edd-4516-b1b6-821c3c33cfc5	8bb34a8d-f5bb-41cf-ba29-87e5c652c03f	ACTIVE	2026-02-05 21:40:37.246785+00	\N	\N	\N	2026-02-05 21:40:37.227805+00	2026-02-05 21:40:37.227805+00
33cada64-e411-4b64-9a3a-43e0eb30317a	ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f	c5992875-1ecb-42f0-b461-e177f1775d46	ACTIVE	2026-02-05 21:40:37.276386+00	\N	\N	\N	2026-02-05 21:40:37.261894+00	2026-02-05 21:40:37.261894+00
f650ff2d-3702-4991-891c-d09d2e61fc0b	13ac055f-b943-4f6d-8182-babe636544df	f3200c57-c6b8-4f2d-80fe-24b9a6359f6c	ACTIVE	2026-02-05 21:41:47.047896+00	\N	\N	\N	2026-02-05 21:41:47.032031+00	2026-02-05 21:41:47.032031+00
7fe03609-bd67-46dc-95a9-b97d94eef081	eb271702-3161-48b2-a4c9-8747819b7ae7	f878c129-1bbb-4dca-bcfc-d21ea54fb41f	ACTIVE	2026-02-05 21:41:47.071835+00	\N	\N	\N	2026-02-05 21:41:47.058236+00	2026-02-05 21:41:47.058236+00
74d5802c-2fcc-4fc4-977d-8f4616e20c59	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	f7028cb1-7e87-4fd7-8aa1-4ea8b97ccb43	ACTIVE	2026-02-05 21:43:42.40706+00	\N	\N	\N	2026-02-05 21:43:42.370197+00	2026-02-05 21:43:42.370197+00
e1ee1584-9b3a-446b-a853-98098ee8e375	31148b05-1512-43ce-8b01-fd3b423fca6e	1d66de05-6ab3-461b-94d0-0750153aa2d9	ACTIVE	2026-02-05 21:43:42.427669+00	\N	\N	\N	2026-02-05 21:43:42.418516+00	2026-02-05 21:43:42.418516+00
77ac6b0b-4daf-4cde-bdee-74c461efb726	ebc86578-b9a2-456f-b884-f964c1fb26f9	e33b94b6-cfc5-4d7e-98a4-2259867e45b4	ACTIVE	2026-02-05 21:49:54.796351+00	\N	\N	\N	2026-02-05 21:49:54.762913+00	2026-02-05 21:49:54.762913+00
f8c373c3-30df-4a4c-895e-8ab5008fa68c	3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167	8229af4d-838a-4d32-ac0b-9eadffbbcff8	ACTIVE	2026-02-05 21:49:54.814976+00	\N	\N	\N	2026-02-05 21:49:54.805663+00	2026-02-05 21:49:54.805663+00
ff51fc2a-b6ec-4f14-9d97-2df91473cf84	7eddd813-1060-42a3-aa36-abc2c6529e0f	718996de-ba3d-4b71-9a19-a6e97d2947ee	ACTIVE	2026-02-05 21:52:18.508707+00	\N	\N	\N	2026-02-05 21:52:18.471949+00	2026-02-05 21:52:18.471949+00
d422e0c3-72d4-4789-ad82-02d09b8690a3	83e1d52b-a86b-461a-b995-e79e2ac57878	b86839bf-62f6-4f3c-8748-5bdeaaa323a6	ACTIVE	2026-02-05 21:52:18.534706+00	\N	\N	\N	2026-02-05 21:52:18.522191+00	2026-02-05 21:52:18.522191+00
e4afc672-4bc1-49a6-96ca-d135e7c3dc68	021aea9d-7fe9-4488-ae61-eebf6d2af731	f9761969-f234-4bb8-9b46-2ea70ad5b735	ACTIVE	2026-02-05 21:55:18.062481+00	\N	\N	\N	2026-02-05 21:55:18.035785+00	2026-02-05 21:55:18.035785+00
0adca222-a20a-4e6e-9b16-fbd8313be3aa	1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3	dcb6e693-f204-46fd-bbca-8eab795cc81a	ACTIVE	2026-02-05 21:55:18.088214+00	\N	\N	\N	2026-02-05 21:55:18.07477+00	2026-02-05 21:55:18.07477+00
2df30acb-7edd-4a62-a7ee-c366c82d3638	088ad156-635f-4689-8a9f-31187419e964	f2d7a38d-6265-4cd5-9743-be932e8693c0	ACTIVE	2026-02-05 21:57:41.725657+00	\N	\N	\N	2026-02-05 21:57:41.707705+00	2026-02-05 21:57:41.707705+00
d1cce9fe-6d82-42d4-9262-95ce70a320c3	723079fb-4d41-408d-958c-a1d417576d82	a7bc280f-69bc-4b03-98d8-de195f8f95bf	ACTIVE	2026-02-05 22:33:46.124091+00	\N	\N	\N	2026-02-05 22:33:46.084547+00	2026-02-05 22:33:46.084547+00
db3a6a1f-e2c1-47ee-aebc-8bed820a21a5	b1dd0b01-8388-41bb-a686-f75f5aa559b9	e8718468-ad6e-4157-bbc8-3ad3a0047082	ACTIVE	2026-02-05 22:33:46.151712+00	\N	\N	\N	2026-02-05 22:33:46.136131+00	2026-02-05 22:33:46.136131+00
627e4e62-8feb-4a92-85b2-799906e1fd83	c5154fda-1c6a-4c09-bd67-0482fe81f7d8	5ae66809-e7de-448a-8f42-920a192c8704	ACTIVE	2026-02-09 14:46:47.509266+00	\N	3f3a3a39-d867-45a8-b901-74a7e27c95f3	85bfbaa4-1565-4e43-b86a-f6440dbd4985	2026-02-09 14:46:47.499889+00	2026-02-09 14:46:47.499889+00
\.


--
-- Data for Name: org_role_permission_overrides; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.org_role_permission_overrides (id, organization_id, role_id, permission_id, effect, created_at, created_by) FROM stdin;
\.


--
-- Data for Name: org_subscription_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.org_subscription_history (id, organization_id, subscription_plan_id, plan_version, change_type, subscription_start_date, subscription_end_date, billing_cycle, amount, payment_status, payment_date, payment_reference, notes, created_at, created_by) FROM stdin;
\.


--
-- Data for Name: organizations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.organizations (id, name, description, logo_url, organization_type, status, registration_number, address, district, state, pincode, contact_email, contact_phone, subscription_plan_id, subscription_start_date, subscription_end_date, created_at, updated_at, created_by, updated_by, is_approved) FROM stdin;
1455677e-0753-44c1-959e-06c542a28884	Green Valley Farm Stats	\N	\N	FARMING	ACTIVE	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-01-30 00:08:38.9577+00	2026-01-30 00:08:38.9577+00	fe4d1e04-7569-409d-8bfc-f7319e7ea582	fe4d1e04-7569-409d-8bfc-f7319e7ea582	f
5ae66809-e7de-448a-8f42-920a192c8704	One Aim	\N	\N	FARMING	ACTIVE	\N	Pune 	\N	\N	\N	oneaim@gmail.com	234234234324	23972749-fd43-4f74-9ff3-4528018e89e9	2026-01-30	2026-03-01	2026-01-30 00:12:20.626621+00	2026-01-30 00:12:20.626621+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	f
8b411c61-9885-4672-ba08-e45709934575	GreenOps FSP Services	\N	\N	FSP	IN_PROGRESS	\N	\N	\N	\N	\N	contact@greenops.com	\N	\N	\N	\N	2026-01-30 00:08:38.859372+00	2026-01-30 20:06:06.674431+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	f
6ccc83ff-6dd6-45b8-9285-d189eec284e9	Test Farm Org 1769940298	Test farming organization for audit E2E testing	\N	FARMING	ACTIVE	\N	\N	Bangalore	\N	560001	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:04:58.583848+00	2026-02-01 10:04:58.583848+00	bfdafb1c-258c-487a-84a9-8df88d6f7efd	bfdafb1c-258c-487a-84a9-8df88d6f7efd	f
cc35b76b-375c-4261-8fa4-24b833a63cdb	Farm Org 1769941989	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:33:09.863454+00	2026-02-01 10:33:10.045678+00	ee193894-167a-4355-8899-7c19ba395e9f	ee193894-167a-4355-8899-7c19ba395e9f	t
1118a620-482f-4241-b722-35653792fda9	FSP Org 1769941989	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:33:09.883035+00	2026-02-01 10:33:10.045678+00	bf660c8b-3818-4cf7-85f1-3071c0a7943c	bf660c8b-3818-4cf7-85f1-3071c0a7943c	t
9a08dd9e-37f1-466a-9cce-b38722c3c08d	Debug Farm Org 1769940408	Debug farming org	\N	FARMING	ACTIVE	\N	\N	Test District	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:06:48.520888+00	2026-02-01 10:06:48.786879+00	a7c620dc-005f-41e4-a09c-84a578fdff32	a7c620dc-005f-41e4-a09c-84a578fdff32	t
74faf449-2f3a-4cdf-a1a6-6294eabc51b9	Debug FSP Org 1769940408	Debug FSP org	\N	FSP	ACTIVE	\N	\N	Test District	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:06:48.540544+00	2026-02-01 10:06:48.786879+00	ea72b36b-fe10-483e-acca-7274bdab7600	ea72b36b-fe10-483e-acca-7274bdab7600	t
d21c407f-5ec7-4940-9863-903fc66fb45f	Quick Farm 1769940607	Quick test farm	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:10:07.26914+00	2026-02-01 10:10:07.496195+00	eb63636b-e512-4cd7-9296-f0d38d62f74d	eb63636b-e512-4cd7-9296-f0d38d62f74d	t
5986b068-6433-4eb3-907f-79e9e5ae4bd2	Quick FSP 1769940607	Quick test FSP	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:10:07.29576+00	2026-02-01 10:10:07.496195+00	fc777437-f8d9-4e04-bc0a-011507805218	fc777437-f8d9-4e04-bc0a-011507805218	t
c6957a10-58cf-4f2d-ab85-b8b0dbd6ed7c	FSP Org 1769942082	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:34:42.450061+00	2026-02-01 10:34:42.615854+00	979cfcfd-a872-40df-8380-dbe81f29e7a5	979cfcfd-a872-40df-8380-dbe81f29e7a5	t
4309e43b-b68e-4834-8de3-a824a0bf37ab	Farm Org 1769941800	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:30:00.498111+00	2026-02-01 10:30:00.688708+00	26872c85-6000-4eec-baab-a1a4b8a27258	26872c85-6000-4eec-baab-a1a4b8a27258	t
bc9a3480-c0ad-43c6-ab08-5fc8362d34b2	FSP Org 1769941800	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:30:00.515811+00	2026-02-01 10:30:00.688708+00	d24c619c-0783-4510-949c-49445cea0202	d24c619c-0783-4510-949c-49445cea0202	t
13bd2caa-40a9-450f-9df0-7a7c110e49ac	Farm Org 1769942011	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:33:31.896879+00	2026-02-01 10:33:32.080195+00	3c1aab18-4eb2-4ab2-bcca-993c37e7fab1	3c1aab18-4eb2-4ab2-bcca-993c37e7fab1	t
cbbff567-e72f-46ff-ad79-4cf26c3260c8	FSP Org 1769942011	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:33:31.914688+00	2026-02-01 10:33:32.080195+00	c7a092a7-d354-498d-b23a-d4802d99ccb4	c7a092a7-d354-498d-b23a-d4802d99ccb4	t
efa7b0ac-291d-489e-94f5-b7e09ee61211	Farm Org 1769941881	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:31:21.06163+00	2026-02-01 10:31:21.263873+00	aec76aa4-0bf4-40bb-9307-de54a5d205a5	aec76aa4-0bf4-40bb-9307-de54a5d205a5	t
db3950f7-2c3d-40ec-8646-9548956aa267	FSP Org 1769941881	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:31:21.08214+00	2026-02-01 10:31:21.263873+00	5b010aef-d0b8-40cc-bc0e-6b6c133cac49	5b010aef-d0b8-40cc-bc0e-6b6c133cac49	t
bc9ba376-ec2d-4293-a39d-22daa59a0236	Farm Org 1769942082	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:34:42.423614+00	2026-02-01 10:34:42.615854+00	b8cf8398-0dff-42c3-99ab-aaa2bcf646e6	b8cf8398-0dff-42c3-99ab-aaa2bcf646e6	t
23f17148-f316-4fb6-8fd4-c4f2045ae401	Farm Org 1769941969	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:32:49.157574+00	2026-02-01 10:32:49.345421+00	ee6157bd-176f-4f75-8cea-64adb841884f	ee6157bd-176f-4f75-8cea-64adb841884f	t
9463b7f0-b657-467c-bc0e-0f21817e623c	FSP Org 1769941969	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:32:49.176666+00	2026-02-01 10:32:49.345421+00	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c	t
65e03c0d-7af5-4622-b2a2-8a867cf708a5	Farm Org 1769942044	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:34:04.288135+00	2026-02-01 10:34:04.473035+00	3e72bdbc-89a7-4009-a93e-bba6fec86530	3e72bdbc-89a7-4009-a93e-bba6fec86530	t
6bf71e9a-2b50-4a27-9ff9-972b5a52eb8e	FSP Org 1769942044	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:34:04.305723+00	2026-02-01 10:34:04.473035+00	2199f334-fccd-46ff-b45c-2cd81aadeca2	2199f334-fccd-46ff-b45c-2cd81aadeca2	t
bf66b4c8-e589-4240-9949-928683f45020	Farm Org 1769942107	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:35:07.770218+00	2026-02-01 10:35:07.956814+00	a031994b-5afb-4fa2-9d8a-8004d7e8c9a3	a031994b-5afb-4fa2-9d8a-8004d7e8c9a3	t
c883192d-5000-4f2a-882c-3e8d3d49d4f6	Farm Org 1769942061	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:34:21.83799+00	2026-02-01 10:34:22.03047+00	c5e779fa-7e25-4b84-b410-a55bd0c9e219	c5e779fa-7e25-4b84-b410-a55bd0c9e219	t
461445ad-b03d-418c-8049-49cbadf6519b	FSP Org 1769942061	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:34:21.858165+00	2026-02-01 10:34:22.03047+00	b46ab366-7dcb-4ee5-a558-dc328db04159	b46ab366-7dcb-4ee5-a558-dc328db04159	t
5d712ef0-dfcc-4e49-ba75-0d15424f0409	Farm Org 1769942203	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:36:43.810068+00	2026-02-01 10:36:44.012388+00	d77da629-52f1-46c9-9118-dbe7fe92c333	d77da629-52f1-46c9-9118-dbe7fe92c333	t
36acd251-59ee-4f22-a3e3-f14e91a16706	FSP Org 1769942107	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:35:07.78949+00	2026-02-01 10:35:07.956814+00	810cc398-af79-4d96-9eee-af0f1bbf8683	810cc398-af79-4d96-9eee-af0f1bbf8683	t
eb79439d-c6df-4d41-8c3d-0619964d91e1	FSP Org 1769942203	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:36:43.844231+00	2026-02-01 10:36:44.012388+00	ef5984b4-54b6-47cf-a9bb-ca02cadc0180	ef5984b4-54b6-47cf-a9bb-ca02cadc0180	t
ea925230-a27d-4bf3-9187-877dab140c8b	Farm Org 1769942147	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:35:47.935151+00	2026-02-01 10:35:48.156103+00	2e6f6fed-9d3d-4b85-87d0-a134932d0dd7	2e6f6fed-9d3d-4b85-87d0-a134932d0dd7	t
ba0154e3-56bb-4d8d-9db9-b143367cbc85	FSP Org 1769942147	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:35:47.954813+00	2026-02-01 10:35:48.156103+00	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	t
e69d30db-071e-4079-9a43-3267a66927a9	Farm Org 1769942225	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:37:05.016176+00	2026-02-01 10:37:05.207216+00	66d51b1b-c21b-4f8c-99ba-c2854ceeab97	66d51b1b-c21b-4f8c-99ba-c2854ceeab97	t
d1a8266c-b125-4c57-b1d9-69f785e7e7ec	FSP Org 1769942225	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:37:05.038749+00	2026-02-01 10:37:05.207216+00	70904796-fe39-4007-b892-a8aa3c8e0e8f	70904796-fe39-4007-b892-a8aa3c8e0e8f	t
aa001d98-fda0-4f0f-971e-361f1af462ad	Farm Org 1769942293	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:38:13.173852+00	2026-02-01 10:38:13.377069+00	3f82b4a7-b270-4d68-9e02-e9068eaa668f	3f82b4a7-b270-4d68-9e02-e9068eaa668f	t
c4a4f415-3907-463e-86e0-2d7148e90d28	FSP Org 1769942293	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:38:13.192723+00	2026-02-01 10:38:13.377069+00	1ce1ba48-b899-4217-8fd9-2124dd4765c6	1ce1ba48-b899-4217-8fd9-2124dd4765c6	t
62656d65-00b9-4446-b11a-586d60d38c8c	Farm Org 1769942338	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:38:58.972558+00	2026-02-01 10:38:59.181255+00	d5104c40-d4cc-47ac-a700-0c7414c1b26a	d5104c40-d4cc-47ac-a700-0c7414c1b26a	t
ab3df532-1696-45db-a97f-ebd3afaee92c	FSP Org 1769942339	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 10:38:59.014481+00	2026-02-01 10:38:59.181255+00	05e362b8-0b73-44ed-bded-ef4e0a40dd47	05e362b8-0b73-44ed-bded-ef4e0a40dd47	t
f4b08735-4038-49dd-bed2-4cb44e9c9287	Farm Org 1769943699	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 11:01:39.499064+00	2026-02-01 11:01:39.682822+00	fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1	fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1	t
c0fbcba5-fca1-4960-88fb-5a5aeb9684e3	FSP Org 1769943699	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 11:01:39.51794+00	2026-02-01 11:01:39.682822+00	b9c25548-e5ba-4200-9dc9-1ba98f332540	b9c25548-e5ba-4200-9dc9-1ba98f332540	t
2ec2a2b1-87f2-4962-8649-c029973d9504	Farm Org 1769943998	Test Farm Org	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 11:06:38.534223+00	2026-02-01 11:06:38.910551+00	1a8f4448-290b-48ff-9f17-2d76e841a1f3	1a8f4448-290b-48ff-9f17-2d76e841a1f3	t
a7602188-54e2-4c7e-b10a-f8971dd2c1c7	FSP Org 1769943998	Test FSP Org	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-01	2026-03-03	2026-02-01 11:06:38.557163+00	2026-02-01 11:06:38.910551+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429	t
88d1dc02-6962-4103-a0b1-141c0553ebb4	FSP_1770326732	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:25:33.314326+00	2026-02-05 21:25:33.732907+00	43a76c7a-3acb-40a9-8c3c-9e0235d9a13f	43a76c7a-3acb-40a9-8c3c-9e0235d9a13f	t
11a75d4a-ecef-4ae0-9767-790dcf59ba5c	Farm_1770326732	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:25:33.393877+00	2026-02-05 21:25:33.732907+00	5526632a-9523-4219-b2ca-708559772fb8	5526632a-9523-4219-b2ca-708559772fb8	t
1d66de05-6ab3-461b-94d0-0750153aa2d9	Farm_1770327821	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:43:42.418516+00	2026-02-05 21:43:42.631516+00	31148b05-1512-43ce-8b01-fd3b423fca6e	31148b05-1512-43ce-8b01-fd3b423fca6e	t
e21f1598-e198-4e06-b82e-c53822730dc8	FSP_1770326899	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:28:19.885149+00	2026-02-05 21:28:20.223884+00	dcc8f7e0-c4a6-4f72-b21e-78331c825d3e	dcc8f7e0-c4a6-4f72-b21e-78331c825d3e	t
e5faaf23-44f2-419b-8226-8d3b25615c9a	Farm_1770326899	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:28:19.975005+00	2026-02-05 21:28:20.223884+00	5847755d-a7ef-4f01-ad83-b96116cc5b06	5847755d-a7ef-4f01-ad83-b96116cc5b06	t
0a61f5ac-582c-4856-8072-27fcad588698	FSP_1770327280	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:34:40.938633+00	2026-02-05 21:34:41.128441+00	d9cd5b64-e423-4710-bcfe-73606bcca78c	d9cd5b64-e423-4710-bcfe-73606bcca78c	t
96ce9467-4d9c-42ac-8fd7-6b4980cb4662	Farm_1770327280	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:34:40.96158+00	2026-02-05 21:34:41.128441+00	5368cfba-bae0-4132-88e4-4fde67d9e523	5368cfba-bae0-4132-88e4-4fde67d9e523	t
a33afb2d-870e-4263-88fa-9e2cb085a8f7	FSP_1770327052	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:30:53.394261+00	2026-02-05 21:30:53.554736+00	274bca62-6a26-40f4-ab29-482816286c94	274bca62-6a26-40f4-ab29-482816286c94	t
8aac186d-15a6-4ce9-94d7-89e8b6eee47d	Farm_1770327052	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:30:53.415111+00	2026-02-05 21:30:53.554736+00	3ca9cf6b-c372-4530-bc35-3440c68f858f	3ca9cf6b-c372-4530-bc35-3440c68f858f	t
f7028cb1-7e87-4fd7-8aa1-4ea8b97ccb43	FSP_1770327821	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:43:42.370197+00	2026-02-05 21:43:42.631516+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	t
27227759-8c29-4ba3-8ba5-153607db5c4c	FSP_1770327102	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:31:42.432788+00	2026-02-05 21:31:42.586221+00	53126f3a-94da-4363-b20d-61a85c99574a	53126f3a-94da-4363-b20d-61a85c99574a	t
675f5900-0a12-48ea-a2a9-c121508fc23e	Farm_1770327102	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:31:42.452616+00	2026-02-05 21:31:42.586221+00	09b95fab-3a52-4e54-8957-76e81ebf668a	09b95fab-3a52-4e54-8957-76e81ebf668a	t
bc651c65-73d1-41c9-a03a-275b47df7b10	FSP_1770327224	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:33:44.820324+00	2026-02-05 21:33:45.126228+00	1214c599-c7c2-490b-a895-e45b985b027b	1214c599-c7c2-490b-a895-e45b985b027b	t
92a020f4-c327-4f4d-8df3-c7ed0d120871	Farm_1770327224	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:33:44.846462+00	2026-02-05 21:33:45.126228+00	39219340-21cb-4a88-a939-93baf1a0e840	39219340-21cb-4a88-a939-93baf1a0e840	t
88810bde-bf96-43e8-9791-937cd4a7e062	FSP_1770327392	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:36:32.459385+00	2026-02-05 21:36:32.618934+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	t
2328d476-0c17-4452-adc8-7cf00f24669b	Farm_1770327392	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:36:32.480874+00	2026-02-05 21:36:32.618934+00	222968c5-f7cd-46a9-80a7-ae6d0557b5c3	222968c5-f7cd-46a9-80a7-ae6d0557b5c3	t
f2d7a38d-6265-4cd5-9743-be932e8693c0	Test Farm Org 1770328661	Test farming organization for audit E2E testing	\N	FARMING	ACTIVE	\N	\N	Bangalore	\N	560001	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:57:41.707705+00	2026-02-05 21:57:41.707705+00	088ad156-635f-4689-8a9f-31187419e964	088ad156-635f-4689-8a9f-31187419e964	f
5e03962b-3b0c-4bd5-9f17-6349e82083cb	FSP_1770327572	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:39:33.231881+00	2026-02-05 21:39:33.546484+00	fc5165e6-6519-496f-a3dd-1435bc308b5f	fc5165e6-6519-496f-a3dd-1435bc308b5f	t
9e0c3eda-2c52-4792-abd4-288131229066	Farm_1770327572	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:39:33.280683+00	2026-02-05 21:39:33.546484+00	2b8bb712-3cfe-435e-84f7-49dfe73d641b	2b8bb712-3cfe-435e-84f7-49dfe73d641b	t
e33b94b6-cfc5-4d7e-98a4-2259867e45b4	FSP_1770328194	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:49:54.762913+00	2026-02-05 21:49:55.018451+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	ebc86578-b9a2-456f-b884-f964c1fb26f9	t
8bb34a8d-f5bb-41cf-ba29-87e5c652c03f	FSP_1770327636	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:40:37.227805+00	2026-02-05 21:40:37.501774+00	d655e067-4edd-4516-b1b6-821c3c33cfc5	d655e067-4edd-4516-b1b6-821c3c33cfc5	t
c5992875-1ecb-42f0-b461-e177f1775d46	Farm_1770327636	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:40:37.261894+00	2026-02-05 21:40:37.501774+00	ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f	ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f	t
8229af4d-838a-4d32-ac0b-9eadffbbcff8	Farm_1770328194	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:49:54.805663+00	2026-02-05 21:49:55.018451+00	3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167	3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167	t
f3200c57-c6b8-4f2d-80fe-24b9a6359f6c	FSP_1770327706	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:41:47.032031+00	2026-02-05 21:41:47.254858+00	13ac055f-b943-4f6d-8182-babe636544df	13ac055f-b943-4f6d-8182-babe636544df	t
f878c129-1bbb-4dca-bcfc-d21ea54fb41f	Farm_1770327706	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:41:47.058236+00	2026-02-05 21:41:47.254858+00	eb271702-3161-48b2-a4c9-8747819b7ae7	eb271702-3161-48b2-a4c9-8747819b7ae7	t
718996de-ba3d-4b71-9a19-a6e97d2947ee	FSP_1770328337	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:52:18.471949+00	2026-02-05 21:52:18.750171+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	7eddd813-1060-42a3-aa36-abc2c6529e0f	t
b86839bf-62f6-4f3c-8748-5bdeaaa323a6	Farm_1770328337	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:52:18.522191+00	2026-02-05 21:52:18.750171+00	83e1d52b-a86b-461a-b995-e79e2ac57878	83e1d52b-a86b-461a-b995-e79e2ac57878	t
a7bc280f-69bc-4b03-98d8-de195f8f95bf	Test Farm Org 1770330826	Test farming organization for audit E2E testing	\N	FARMING	ACTIVE	\N	\N	Bangalore	\N	560001	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 22:33:46.084547+00	2026-02-05 22:33:46.362724+00	723079fb-4d41-408d-958c-a1d417576d82	723079fb-4d41-408d-958c-a1d417576d82	t
e8718468-ad6e-4157-bbc8-3ad3a0047082	Test FSP Org 1770330826	Test FSP organization for audit services	\N	FSP	ACTIVE	\N	\N	Bangalore	\N	560002	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 22:33:46.136131+00	2026-02-05 22:33:46.362724+00	b1dd0b01-8388-41bb-a686-f75f5aa559b9	b1dd0b01-8388-41bb-a686-f75f5aa559b9	t
f9761969-f234-4bb8-9b46-2ea70ad5b735	FSP_1770328517	Test	\N	FSP	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:55:18.035785+00	2026-02-05 21:55:18.517682+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	021aea9d-7fe9-4488-ae61-eebf6d2af731	t
dcb6e693-f204-46fd-bbca-8eab795cc81a	Farm_1770328517	Test	\N	FARMING	ACTIVE	\N	\N	Test	\N	123456	\N	\N	23972749-fd43-4f74-9ff3-4528018e89e9	2026-02-05	2026-03-07	2026-02-05 21:55:18.07477+00	2026-02-05 21:55:18.517682+00	1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3	1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3	t
\.


--
-- Data for Name: parameter_option_set_map; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parameter_option_set_map (id, parameter_id, option_set_id, created_at) FROM stdin;
c3b662d2-d3d2-4e71-ad26-83b781daabd9	a5216629-46c0-444a-b51e-51495f8190db	d9b092af-26d2-4bad-be2f-c459e999e778	2026-01-30 00:05:41.498556+00
0e46ee67-e96b-45e2-bd5c-ca891a8d4d75	c7d572e6-37e1-463d-a31d-364cc87e9fb5	d3ab8840-8a6e-4251-9c55-94f23f12405e	2026-01-30 00:05:41.498556+00
f20a9478-f5c4-492d-90ab-298931d694d8	e89b6487-1da6-4f25-801c-a3e340814738	e5183c0d-bad4-44d3-8329-f4048f1df704	2026-01-30 00:05:41.498556+00
6cb14c41-66f2-419a-88d4-1c7703e1e8f5	22815f14-8679-4b16-903e-890f1193261a	49c22604-b83e-4ec6-b024-aed71d28f5dd	2026-01-30 00:21:13.085603+00
b763098e-e059-4bc7-b691-e1c3e659a344	a1dad50b-b1a3-49bb-a0f5-268c2fb82c14	c39059bb-e98e-43e5-955d-1f87b7450684	2026-01-30 00:21:13.218845+00
c09e544a-6e0d-418d-8157-a22128901ff2	46310718-ce6f-4e69-8da2-0583bf5554b0	0b082300-cb93-4098-8b68-4c5f2492d0ea	2026-01-30 00:21:13.401629+00
2ed18c86-18f1-442e-9821-67bb60ab6bec	548d14de-1868-4c6e-8324-68af43157e85	12462a9c-7649-4b3c-bb96-adbe08432626	2026-01-30 20:34:37.466543+00
219c5ab6-739a-4591-8cc3-d3cb327b8683	1d0cbbc3-1354-49d6-a16a-5ba0d6fd2f04	0345db82-bf99-4f32-b222-6ae0a7c07c00	2026-01-30 20:36:02.456146+00
cf7bf670-6b6e-4020-992f-f0799926385f	1b4c0c1b-7516-439a-af12-4e9735291848	dfdd3646-a211-4edf-9458-3fd5dfdb7a76	2026-01-30 20:36:02.556638+00
1325d8e9-bc99-4c61-bcce-57396e7a9983	69900480-cef3-4145-adc7-651cf4eb1c38	9a006dfc-05c1-48d7-a1d9-d0a6f6e2ccba	2026-01-30 20:36:02.721817+00
37bb5984-7b91-4bb2-8527-ac2d0020b277	5e0e278c-ed24-4ae6-b259-8a430b6ff804	7d1bfc37-3b1b-4421-a3f9-104690c6e487	2026-02-05 21:31:42.68565+00
2ba09fc2-afc5-40b4-9ba5-aa73775113f0	28230270-0fcf-4662-8c5b-8bb0ad5c57b3	b409cb79-5f90-4322-b935-5c13fe396f9c	2026-02-05 21:33:45.250961+00
06b8a476-c551-42a0-8dd0-87595d57d8f0	5b9d413c-0d24-4b1c-bee8-2a800c357b62	a9bf577e-4d74-495e-b9d9-c1677621be45	2026-02-05 21:34:41.255709+00
5ec82384-4309-4eee-9e8b-6ad88564f6ef	6699f225-e68a-4e39-a43f-a6202cda40d5	cdc29b9f-35fb-4abb-a9a6-21272b56173a	2026-02-05 21:36:32.718074+00
b2a7ada9-75d7-457f-8b51-6a239bc6367a	689e5a3e-cc7a-4148-b408-f92ec941b37e	b0fe6edb-193c-4e20-a6f4-5cbaaf817536	2026-02-05 21:39:33.763321+00
9d5302af-81c9-48c1-8771-3615f6aecafe	7acb91dd-9a2b-482c-9fc6-2eefb815aeb3	ba3f1425-1907-48fc-a9f4-7ee1a85c0b90	2026-02-05 21:40:37.642982+00
34d03efd-4330-4bdc-99b7-e56dd05e4a9a	222948be-c818-4310-bf8d-fef35d5d979c	e67b95a8-8819-4939-9557-bd2d5379e96c	2026-02-05 21:41:47.381531+00
cc2c6bc1-099d-4b52-ab1d-2692008dd98d	78f901de-8e0c-42a6-ba39-94adadbe3193	53a4bc06-e667-4f37-b16e-9aa98563aa2f	2026-02-05 21:43:42.795572+00
4e9de531-ca8b-4387-9293-582d6cae1a41	fc1d516b-4410-42df-8d1a-2420b8d0927b	e86a83d1-b3e4-44cc-95ad-b63d2b7a931d	2026-02-05 21:49:55.171024+00
f8e7ba32-650d-417b-9b9e-ec65dc5ad210	3bbea4bb-bdd5-4465-b6d1-001830971892	f8998096-2833-488c-b41e-08dedfcfc32c	2026-02-05 21:52:18.955239+00
d60bc1fa-4d33-4644-8cf1-d1ed28d3ae52	ad806e19-cd1d-4a40-ae12-bd0c5c203b9b	6c5d8da2-26c9-424a-9b09-5f0b70e2c080	2026-02-05 21:55:18.68093+00
\.


--
-- Data for Name: parameter_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parameter_translations (id, parameter_id, language_code, name, description, help_text, created_at) FROM stdin;
eb97b26d-b04b-4d3f-af3f-2a55bdebbb64	1b6879c4-7300-42f8-9ef6-24669b8e31ae	en	Plant Height (cm)	\N	\N	2026-01-30 00:05:41.488146+00
fb01768c-a1c6-42d4-8e54-19acd5ed3c6e	a5216629-46c0-444a-b51e-51495f8190db	en	Leaf Color	\N	\N	2026-01-30 00:05:41.488146+00
fc51a23e-df13-4e4b-b9e7-ebcb273e242a	c7d572e6-37e1-463d-a31d-364cc87e9fb5	en	Pest Presence	\N	\N	2026-01-30 00:05:41.488146+00
10b72eaa-66a0-4652-b1ff-f26630a310d2	e89b6487-1da6-4f25-801c-a3e340814738	en	Soil Moisture Level	\N	\N	2026-01-30 00:05:41.488146+00
0bf60256-7120-4481-88dd-03fda7a3b6fe	22815f14-8679-4b16-903e-890f1193261a	en	Leaf Color	\N	\N	2026-01-30 00:21:13.085603+00
21c815df-8c58-43e2-8934-3a48ad04b70f	a1dad50b-b1a3-49bb-a0f5-268c2fb82c14	en	Pest Presence	\N	\N	2026-01-30 00:21:13.218845+00
f112447f-2477-49cb-9647-d1d4fb3c5c81	39cb34e6-9d92-4270-820f-80fd2e47ce1e	en	Plant Height (cm)	\N	\N	2026-01-30 00:21:13.318109+00
469b6983-989c-49b7-a83b-603884c31792	46310718-ce6f-4e69-8da2-0583bf5554b0	en	Soil Moisture Level	\N	\N	2026-01-30 00:21:13.401629+00
89ee1b4c-7fdf-4b4c-9d28-de3af7bdd00e	548d14de-1868-4c6e-8324-68af43157e85	en	gdfgdfg		\N	2026-01-30 20:34:37.466543+00
53e34fde-1b3d-4631-a875-5efa6ff09139	f32bc43e-7842-4aff-97d0-c999804e2f44	en	sadfsdfsdf	\N	\N	2026-01-30 20:36:02.289296+00
21658498-aa64-4cae-b4c9-10fd776c4ccc	7ada24d6-b7ad-413d-893d-25e1271d9841	en	Plant Height (cm)	\N	\N	2026-01-30 20:36:02.389207+00
89d32235-a910-4eff-b502-220d8672538e	1d0cbbc3-1354-49d6-a16a-5ba0d6fd2f04	en	Leaf Color	\N	\N	2026-01-30 20:36:02.456146+00
dba85714-4ce8-40df-962a-0b515f6409af	1b4c0c1b-7516-439a-af12-4e9735291848	en	Pest Presence	\N	\N	2026-01-30 20:36:02.556638+00
e145dab2-4392-457d-8f04-3809863fbf4b	e5db1148-7a6f-4fae-80f5-e602f35e5cbd	en	Plant Height (cm)	\N	\N	2026-01-30 20:36:02.655771+00
c8b05b5b-0943-463a-b1fc-940b3f42381f	69900480-cef3-4145-adc7-651cf4eb1c38	en	Soil Moisture Level	\N	\N	2026-01-30 20:36:02.721817+00
44c79911-685b-426a-83fb-fe5e2163f9e6	07da6e2b-1ce2-4af9-ba9f-ccd09a7d37de	en	Soil pH	Measure pH	\N	2026-02-01 10:31:21.293862+00
6631c946-9f86-48a7-a65b-7b565ae2a5e5	71826bac-4f3a-4e8e-b7d7-dcfdb27c2f62	en	Soil pH	Measure pH	\N	2026-02-01 10:32:49.3748+00
406ed118-54a7-4e55-ac45-53b7645c01e9	7940e041-2bd8-4b4c-829b-5c080b601709	en	Soil pH	Measure pH	\N	2026-02-01 10:33:10.07723+00
0fd91fba-cae1-4e9d-b80d-072392e0877e	940dd88b-e133-440b-af51-95365af25909	en	Soil pH	Measure pH	\N	2026-02-01 10:33:32.108177+00
1353ab92-94f5-4cbf-9651-dd1442a0347b	10f12a98-15d3-446f-90b0-5e5e353c3809	en	Soil pH	Measure pH	\N	2026-02-01 10:34:04.503594+00
d11be385-fe51-4ad2-9742-9e5f04ba0488	1ad2e581-5dce-41ce-af2a-8e832ebbcc54	en	Soil pH	Measure pH	\N	2026-02-01 10:34:22.05862+00
7de77ec5-aae4-4be6-a598-c40a00374d8f	4ec21239-4ac2-46b7-bd9b-d1c065591f62	en	Soil pH	Measure pH	\N	2026-02-01 10:34:42.643669+00
bc0ee74f-e9d2-4e5d-a430-9be790c20122	ebfb0b55-7017-496c-9e98-d0d55159a831	en	Soil pH	Measure pH	\N	2026-02-01 10:35:07.98513+00
dd070337-e682-45ce-9754-e8cb9e4edfa0	7325f2cc-97ed-4dcc-a191-1ea0c56e04bd	en	Soil pH	Measure pH	\N	2026-02-01 10:35:48.183205+00
7db116ff-4168-4762-a92a-01481f98f3e9	e68e3073-4957-4a89-80e3-f27e8136bf3b	en	Soil pH	Measure pH	\N	2026-02-01 10:36:44.049383+00
82bfe2eb-baed-4543-900b-b0d557479eeb	314226b3-58f0-40c3-8a79-a040f41f3867	en	Soil pH	Measure pH	\N	2026-02-01 10:37:05.234566+00
63b91d78-e209-42d6-bdc0-ed88fcd4c071	fca6b05f-39da-4323-a92d-d2fc7eceabff	en	Soil pH	Measure pH	\N	2026-02-01 10:38:13.410196+00
8021d122-a2e8-4c7a-81af-9cc2cd3ba238	710a7d66-5394-4c0a-af26-5dc0512fae77	en	Soil pH	Measure pH	\N	2026-02-01 10:38:59.217349+00
1720047b-c2dd-4b03-a519-fe348ecaef0a	e9799730-1c13-4c5f-b9ed-2a7fd9c1538e	en	Soil pH	Measure pH	\N	2026-02-01 11:01:39.711932+00
724cd40e-d4df-4d74-b059-5a507edab018	eefe2319-3eb6-43bb-9d78-7c734561b947	en	Param 1	Measure 1	\N	2026-02-01 11:06:38.944469+00
b567f6f7-3a7d-42f9-8683-a117b89ad926	5684267d-6f41-454e-8429-2f094efe38b9	en	Param 2	Measure 2	\N	2026-02-01 11:06:38.962761+00
74ae82b4-5c08-4c4f-ba2b-4fc3f3b4dfca	b2d71394-a99d-4ff6-a333-4d8ebf1c1ec4	en	Param 3	Measure 3	\N	2026-02-01 11:06:38.980527+00
951a8efd-e362-438f-8291-e231bd69bc37	7e469f84-0b9d-4f70-b737-ce0444148245	en	Param 4	Measure 4	\N	2026-02-01 11:06:38.996995+00
cdadb056-f441-4c33-91ba-4cd2141aba4b	46640045-7bdf-48eb-af82-61a3fc7c2d4a	en	Param 5	Measure 5	\N	2026-02-01 11:06:39.015017+00
470d4d69-c6d2-4a82-af7b-5810b9cad46b	f517e506-6c88-4cfb-8426-ae5f1d516154	en	Param 6	Measure 6	\N	2026-02-01 11:06:39.031882+00
99ace271-29d1-422c-b866-c8ed4482c694	89151732-fc61-4617-a477-17685bbee9da	en	Param 7	Measure 7	\N	2026-02-01 11:06:39.049312+00
78cc3398-6957-4385-b9a2-8e5ce271a8ea	8bea7626-d387-455c-aa0b-2436f2824e78	en	Param 8	Measure 8	\N	2026-02-01 11:06:39.067524+00
fba05975-e8ad-48ab-a028-5f937e616e49	d7147d11-034b-4c26-8c23-6921d316d28a	en	Param 9	Measure 9	\N	2026-02-01 11:06:39.085465+00
86c5e431-dcd3-4d9a-9b54-6a3208d965d9	9f963e85-c94c-4dec-b2aa-b0e745431c39	en	Param 10	Measure 10	\N	2026-02-01 11:06:39.102874+00
33fb5ad2-c3d7-4886-9787-2f1c803bce13	74d9d4a6-aac1-4ec4-aaa0-b8733a55def7	en	asdasdasdasdasd	\N	\N	2026-02-05 19:49:07.61694+00
91fbd1ac-2130-4367-bfff-81666e8b34f2	5c5ea765-416e-49c7-b577-9c075bcfa073	en	Answer this questions as well now thats it buddy	\N	\N	2026-02-05 19:49:07.74207+00
7d0d1b52-688c-4bcb-a2e5-4cc38f42d66b	326b6dee-185a-42c1-b2d2-c82694e19f86	en	Only numbers got it now	\N	\N	2026-02-05 19:49:07.825485+00
352770c7-db46-40a9-9ac9-04bb6d43d6eb	d5ade5a9-4c6d-49f6-b107-6b7a74723241	en	Yield	\N	\N	2026-02-05 21:28:20.539859+00
17a42b12-b953-4c31-b0ff-5fbbfdc2bdf8	9bd7290b-57b6-4f20-a183-5508e4b4057b	en	Health	\N	\N	2026-02-05 21:28:20.600134+00
92da8ff6-5fda-43f0-8e52-190717631196	2816a6d8-0b5d-411c-8bb6-78097507e5fc	en	Yield	\N	\N	2026-02-05 21:30:53.635077+00
28d33f7b-ccdb-4c3b-aa98-4cfb639f38be	0b93a1e8-49ab-4535-be33-dfbfb7b86748	en	Health	\N	\N	2026-02-05 21:30:53.650004+00
250aeb72-b600-4efe-9256-f20b578be080	78a8d90e-d189-4e0c-9815-618f465f4195	en	Yield	\N	\N	2026-02-05 21:31:42.656766+00
27b38379-0d18-462f-a149-b5d3eeed027d	f01ac19f-b2ff-4bc9-b16a-5edb10315b41	en	Health	\N	\N	2026-02-05 21:31:42.670963+00
ef71e6a9-76ba-4ad4-90dc-eeb84c75f989	5e0e278c-ed24-4ae6-b259-8a430b6ff804	en	Type	\N	\N	2026-02-05 21:31:42.68565+00
b64c82be-b921-480f-9407-e87b2621da31	467998d6-634b-40aa-8eb8-728fab704ba7	en	Yield	\N	\N	2026-02-05 21:33:45.22181+00
7e3d31d6-1085-4348-80e0-a1265b898b6c	82c060ef-fec1-4d82-9e63-44b301715425	en	Health	\N	\N	2026-02-05 21:33:45.237775+00
1cb89648-864c-46a7-80ee-65a9a1065dba	28230270-0fcf-4662-8c5b-8bb0ad5c57b3	en	Type	\N	\N	2026-02-05 21:33:45.250961+00
916066b2-28a3-4daa-a780-91ad0785dc3e	e016e813-99bf-46ae-93e0-43fcc999ecff	en	Yield	\N	\N	2026-02-05 21:34:41.218974+00
46ae34fd-2030-4653-a49a-a5c02dd20a98	0124f9d8-df14-40e1-a628-2fb28cfcd89b	en	Health	\N	\N	2026-02-05 21:34:41.237611+00
0d8b7020-32ee-42e2-b09d-72b6e8bc1116	5b9d413c-0d24-4b1c-bee8-2a800c357b62	en	Type	\N	\N	2026-02-05 21:34:41.255709+00
1f00d2c6-1985-4854-86de-abf209016489	baa7fe1d-099f-49de-9531-dcad3694b914	en	Yield	\N	\N	2026-02-05 21:36:32.689164+00
9134fbd2-6632-4f55-824f-24b1b1a94f1a	56a72950-a19d-481b-a0db-3aa0940d1b7a	en	Health	\N	\N	2026-02-05 21:36:32.704143+00
b9cc57c1-bd81-4aba-9e1b-142085a4c986	6699f225-e68a-4e39-a43f-a6202cda40d5	en	Type	\N	\N	2026-02-05 21:36:32.718074+00
2307287f-8e50-4780-8c93-fe9c70e79266	90ac4202-513e-4e0e-9de6-a32262857ed3	en	Yield	\N	\N	2026-02-05 21:39:33.709983+00
e34109ff-4816-433f-9466-348e7683142c	4a1add6d-2be5-4eb4-93d2-51ebbf5e1672	en	Health	\N	\N	2026-02-05 21:39:33.745072+00
5eb77e29-751e-4810-a3b6-c940164641de	689e5a3e-cc7a-4148-b408-f92ec941b37e	en	Type	\N	\N	2026-02-05 21:39:33.763321+00
6f9b5917-25c0-4191-985f-4b84848fc32a	c863d9ae-337e-4ea5-a846-3b9a8bd04020	en	Yield	\N	\N	2026-02-05 21:40:37.601754+00
b0366ce2-0b68-42c2-b533-a40b621414d3	a74d7503-f495-4a7b-942d-2e6d64aab25f	en	Health	\N	\N	2026-02-05 21:40:37.622185+00
92d09594-5f4a-4fa6-855b-56b5b002fbfa	7acb91dd-9a2b-482c-9fc6-2eefb815aeb3	en	Type	\N	\N	2026-02-05 21:40:37.642982+00
28f4eb7e-bf51-41f4-8389-ff22efea98e7	76452429-682f-4ba0-917e-bb4b9ffd349f	en	Yield	\N	\N	2026-02-05 21:41:47.343601+00
ab7e86d2-89ac-4f5b-9e11-7ae03fe52f12	e46db86a-72f6-4606-8eb2-560b6b3ec315	en	Health	\N	\N	2026-02-05 21:41:47.363958+00
97408b0e-9592-4392-9445-5a671f82ebb9	222948be-c818-4310-bf8d-fef35d5d979c	en	Type	\N	\N	2026-02-05 21:41:47.381531+00
e8f05325-27aa-411e-af06-0eddc78af780	b664898c-45cf-4723-8fff-b74c1232898f	en	Yield	\N	\N	2026-02-05 21:43:42.756468+00
d16aff9a-95c9-4764-9b0f-e0bc134f5280	9700c6e5-2190-443e-83b2-5183b59625e2	en	Health	\N	\N	2026-02-05 21:43:42.781578+00
95d62c3b-888d-4ae2-b56c-700ae5525de0	78f901de-8e0c-42a6-ba39-94adadbe3193	en	Type	\N	\N	2026-02-05 21:43:42.795572+00
af39d3e9-763e-437f-9105-fceee5479aff	21f3a466-ed7c-4630-8715-9dbeca7fb00f	en	Yield	\N	\N	2026-02-05 21:49:55.136751+00
efc9ff7e-6044-49a3-af5d-8fbeb57000ed	2ad12225-e5db-458e-9a8a-7d3ff1051d4c	en	Health	\N	\N	2026-02-05 21:49:55.156535+00
028641f3-f07a-4839-92a4-437097bc6f41	fc1d516b-4410-42df-8d1a-2420b8d0927b	en	Type	\N	\N	2026-02-05 21:49:55.171024+00
7c5bd58d-8a2d-47ae-9ed4-427b050f2e73	bee24a5b-c963-4451-86cc-068d3d4b9309	en	Yield	\N	\N	2026-02-05 21:52:18.909202+00
e21662d5-bc2b-463c-adbb-26d90f229d61	458fd9c3-1e3b-4526-90c5-b791616862e3	en	Health	\N	\N	2026-02-05 21:52:18.936877+00
8750ea4e-b206-432d-8055-2c90996c3860	3bbea4bb-bdd5-4465-b6d1-001830971892	en	Type	\N	\N	2026-02-05 21:52:18.955239+00
275d9c8e-7ab2-4a2f-b3c4-df6021f3717b	02f8b306-97b5-4dde-afdb-91725dfec46f	en	Yield	\N	\N	2026-02-05 21:55:18.641195+00
2c9e4670-51a8-4447-9569-9e6cce2a69e7	a9958b3e-69bf-42ac-a56d-c8d16d67d06b	en	Health	\N	\N	2026-02-05 21:55:18.664262+00
4fa29149-3ce2-42fb-9cf1-9b1686cb7ca7	ad806e19-cd1d-4a40-ae12-bd0c5c203b9b	en	Type	\N	\N	2026-02-05 21:55:18.68093+00
\.


--
-- Data for Name: parameters; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parameters (id, code, parameter_type, is_system_defined, owner_org_id, is_active, parameter_metadata, created_at, updated_at, created_by, updated_by) FROM stdin;
1b6879c4-7300-42f8-9ef6-24669b8e31ae	PLANT_HEIGHT	NUMERIC	t	\N	t	\N	2026-01-30 00:05:41.477656+00	2026-01-30 00:05:41.477656+00	\N	\N
a5216629-46c0-444a-b51e-51495f8190db	LEAF_COLOR	SINGLE_SELECT	t	\N	t	\N	2026-01-30 00:05:41.477656+00	2026-01-30 00:05:41.477656+00	\N	\N
c7d572e6-37e1-463d-a31d-364cc87e9fb5	PEST_PRESENCE	SINGLE_SELECT	t	\N	t	\N	2026-01-30 00:05:41.477656+00	2026-01-30 00:05:41.477656+00	\N	\N
e89b6487-1da6-4f25-801c-a3e340814738	SOIL_MOISTURE	SINGLE_SELECT	t	\N	t	\N	2026-01-30 00:05:41.477656+00	2026-01-30 00:05:41.477656+00	\N	\N
22815f14-8679-4b16-903e-890f1193261a	PRM_b3ab_0_2653	SINGLE_SELECT	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-01-30 00:21:13.085603+00	2026-01-30 00:21:13.085603+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
a1dad50b-b1a3-49bb-a0f5-268c2fb82c14	PRM_b3ab_1_2786	SINGLE_SELECT	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-01-30 00:21:13.218845+00	2026-01-30 00:21:13.218845+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
39cb34e6-9d92-4270-820f-80fd2e47ce1e	PRM_b3ab_2_2886	NUMERIC	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-01-30 00:21:13.318109+00	2026-01-30 00:21:13.318109+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
46310718-ce6f-4e69-8da2-0583bf5554b0	PRM_b3ab_3_2969	SINGLE_SELECT	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-01-30 00:21:13.401629+00	2026-01-30 00:21:13.401629+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
548d14de-1868-4c6e-8324-68af43157e85	PRM_GDFGDFG_6319	SINGLE_SELECT	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-01-30 20:34:37.466543+00	2026-01-30 20:34:37.466543+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
f32bc43e-7842-4aff-97d0-c999804e2f44	PRM_fa6d_0_1143	DATE	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-01-30 20:36:02.289296+00	2026-01-30 20:36:02.289296+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
7ada24d6-b7ad-413d-893d-25e1271d9841	PRM_fa6d_1_1243	NUMERIC	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-01-30 20:36:02.389207+00	2026-01-30 20:36:02.389207+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
1d0cbbc3-1354-49d6-a16a-5ba0d6fd2f04	PRM_fa6d_2_1310	SINGLE_SELECT	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-01-30 20:36:02.456146+00	2026-01-30 20:36:02.456146+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
1b4c0c1b-7516-439a-af12-4e9735291848	PRM_fa6d_3_1410	SINGLE_SELECT	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-01-30 20:36:02.556638+00	2026-01-30 20:36:02.556638+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
e5db1148-7a6f-4fae-80f5-e602f35e5cbd	PRM_fa6d_4_1510	NUMERIC	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-01-30 20:36:02.655771+00	2026-01-30 20:36:02.655771+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
69900480-cef3-4145-adc7-651cf4eb1c38	PRM_fa6d_5_1576	SINGLE_SELECT	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-01-30 20:36:02.721817+00	2026-01-30 20:36:02.721817+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
07da6e2b-1ce2-4af9-ba9f-ccd09a7d37de	PH_1769941881	NUMERIC	f	db3950f7-2c3d-40ec-8646-9548956aa267	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:31:21.293862+00	2026-02-01 10:31:21.293862+00	5b010aef-d0b8-40cc-bc0e-6b6c133cac49	5b010aef-d0b8-40cc-bc0e-6b6c133cac49
71826bac-4f3a-4e8e-b7d7-dcfdb27c2f62	PH_1769941969	NUMERIC	f	9463b7f0-b657-467c-bc0e-0f21817e623c	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:32:49.3748+00	2026-02-01 10:32:49.3748+00	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c
7940e041-2bd8-4b4c-829b-5c080b601709	PH_1769941990	NUMERIC	f	1118a620-482f-4241-b722-35653792fda9	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:33:10.07723+00	2026-02-01 10:33:10.07723+00	bf660c8b-3818-4cf7-85f1-3071c0a7943c	bf660c8b-3818-4cf7-85f1-3071c0a7943c
940dd88b-e133-440b-af51-95365af25909	PH_1769942012	NUMERIC	f	cbbff567-e72f-46ff-ad79-4cf26c3260c8	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:33:32.108177+00	2026-02-01 10:33:32.108177+00	c7a092a7-d354-498d-b23a-d4802d99ccb4	c7a092a7-d354-498d-b23a-d4802d99ccb4
10f12a98-15d3-446f-90b0-5e5e353c3809	PH_1769942044	NUMERIC	f	6bf71e9a-2b50-4a27-9ff9-972b5a52eb8e	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:34:04.503594+00	2026-02-01 10:34:04.503594+00	2199f334-fccd-46ff-b45c-2cd81aadeca2	2199f334-fccd-46ff-b45c-2cd81aadeca2
1ad2e581-5dce-41ce-af2a-8e832ebbcc54	PH_1769942062	NUMERIC	f	461445ad-b03d-418c-8049-49cbadf6519b	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:34:22.05862+00	2026-02-01 10:34:22.05862+00	b46ab366-7dcb-4ee5-a558-dc328db04159	b46ab366-7dcb-4ee5-a558-dc328db04159
4ec21239-4ac2-46b7-bd9b-d1c065591f62	PH_1769942082	NUMERIC	f	c6957a10-58cf-4f2d-ab85-b8b0dbd6ed7c	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:34:42.643669+00	2026-02-01 10:34:42.643669+00	979cfcfd-a872-40df-8380-dbe81f29e7a5	979cfcfd-a872-40df-8380-dbe81f29e7a5
ebfb0b55-7017-496c-9e98-d0d55159a831	PH_1769942107	NUMERIC	f	36acd251-59ee-4f22-a3e3-f14e91a16706	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:35:07.98513+00	2026-02-01 10:35:07.98513+00	810cc398-af79-4d96-9eee-af0f1bbf8683	810cc398-af79-4d96-9eee-af0f1bbf8683
7325f2cc-97ed-4dcc-a191-1ea0c56e04bd	PH_1769942148	NUMERIC	f	ba0154e3-56bb-4d8d-9db9-b143367cbc85	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:35:48.183205+00	2026-02-01 10:35:48.183205+00	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a
e68e3073-4957-4a89-80e3-f27e8136bf3b	PH_1769942204	NUMERIC	f	eb79439d-c6df-4d41-8c3d-0619964d91e1	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:36:44.049383+00	2026-02-01 10:36:44.049383+00	ef5984b4-54b6-47cf-a9bb-ca02cadc0180	ef5984b4-54b6-47cf-a9bb-ca02cadc0180
314226b3-58f0-40c3-8a79-a040f41f3867	PH_1769942225	NUMERIC	f	d1a8266c-b125-4c57-b1d9-69f785e7e7ec	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:37:05.234566+00	2026-02-01 10:37:05.234566+00	70904796-fe39-4007-b892-a8aa3c8e0e8f	70904796-fe39-4007-b892-a8aa3c8e0e8f
fca6b05f-39da-4323-a92d-d2fc7eceabff	PH_1769942293	NUMERIC	f	c4a4f415-3907-463e-86e0-2d7148e90d28	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:38:13.410196+00	2026-02-01 10:38:13.410196+00	1ce1ba48-b899-4217-8fd9-2124dd4765c6	1ce1ba48-b899-4217-8fd9-2124dd4765c6
710a7d66-5394-4c0a-af26-5dc0512fae77	PH_1769942339	NUMERIC	f	ab3df532-1696-45db-a97f-ebd3afaee92c	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 10:38:59.217349+00	2026-02-01 10:38:59.217349+00	05e362b8-0b73-44ed-bded-ef4e0a40dd47	05e362b8-0b73-44ed-bded-ef4e0a40dd47
e9799730-1c13-4c5f-b9ed-2a7fd9c1538e	PH_1769943699	NUMERIC	f	c0fbcba5-fca1-4960-88fb-5a5aeb9684e3	t	{"unit": "pH", "max_value": 14, "min_value": 0}	2026-02-01 11:01:39.711932+00	2026-02-01 11:01:39.711932+00	b9c25548-e5ba-4200-9dc9-1ba98f332540	b9c25548-e5ba-4200-9dc9-1ba98f332540
eefe2319-3eb6-43bb-9d78-7c734561b947	P1_1769943998	NUMERIC	f	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	t	{"unit": "units", "max_value": 100, "min_value": 0}	2026-02-01 11:06:38.944469+00	2026-02-01 11:06:38.944469+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429
5684267d-6f41-454e-8429-2f094efe38b9	P2_1769943998	NUMERIC	f	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	t	{"unit": "units", "max_value": 100, "min_value": 0}	2026-02-01 11:06:38.962761+00	2026-02-01 11:06:38.962761+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429
b2d71394-a99d-4ff6-a333-4d8ebf1c1ec4	P3_1769943998	NUMERIC	f	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	t	{"unit": "units", "max_value": 100, "min_value": 0}	2026-02-01 11:06:38.980527+00	2026-02-01 11:06:38.980527+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429
7e469f84-0b9d-4f70-b737-ce0444148245	P4_1769943998	NUMERIC	f	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	t	{"unit": "units", "max_value": 100, "min_value": 0}	2026-02-01 11:06:38.996995+00	2026-02-01 11:06:38.996995+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429
46640045-7bdf-48eb-af82-61a3fc7c2d4a	P5_1769943999	NUMERIC	f	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	t	{"unit": "units", "max_value": 100, "min_value": 0}	2026-02-01 11:06:39.015017+00	2026-02-01 11:06:39.015017+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429
f517e506-6c88-4cfb-8426-ae5f1d516154	P6_1769943999	NUMERIC	f	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	t	{"unit": "units", "max_value": 100, "min_value": 0}	2026-02-01 11:06:39.031882+00	2026-02-01 11:06:39.031882+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429
89151732-fc61-4617-a477-17685bbee9da	P7_1769943999	NUMERIC	f	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	t	{"unit": "units", "max_value": 100, "min_value": 0}	2026-02-01 11:06:39.049312+00	2026-02-01 11:06:39.049312+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429
8bea7626-d387-455c-aa0b-2436f2824e78	P8_1769943999	NUMERIC	f	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	t	{"unit": "units", "max_value": 100, "min_value": 0}	2026-02-01 11:06:39.067524+00	2026-02-01 11:06:39.067524+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429
d7147d11-034b-4c26-8c23-6921d316d28a	P9_1769943999	NUMERIC	f	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	t	{"unit": "units", "max_value": 100, "min_value": 0}	2026-02-01 11:06:39.085465+00	2026-02-01 11:06:39.085465+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429
9f963e85-c94c-4dec-b2aa-b0e745431c39	P10_1769943999	NUMERIC	f	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	t	{"unit": "units", "max_value": 100, "min_value": 0}	2026-02-01 11:06:39.102874+00	2026-02-01 11:06:39.102874+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429
74d9d4a6-aac1-4ec4-aaa0-b8733a55def7	PRM_8d28_0_7135	TEXT	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-02-05 19:49:07.61694+00	2026-02-05 19:49:07.61694+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
5c5ea765-416e-49c7-b577-9c075bcfa073	PRM_8d28_1_7259	TEXT	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-02-05 19:49:07.74207+00	2026-02-05 19:49:07.74207+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
326b6dee-185a-42c1-b2d2-c82694e19f86	PRM_8d28_2_7342	NUMERIC	f	8b411c61-9885-4672-ba08-e45709934575	t	{}	2026-02-05 19:49:07.825485+00	2026-02-05 19:49:07.825485+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
d5ade5a9-4c6d-49f6-b107-6b7a74723241	P1_1770326899	NUMERIC	f	e21f1598-e198-4e06-b82e-c53822730dc8	t	{}	2026-02-05 21:28:20.539859+00	2026-02-05 21:28:20.539859+00	dcc8f7e0-c4a6-4f72-b21e-78331c825d3e	dcc8f7e0-c4a6-4f72-b21e-78331c825d3e
9bd7290b-57b6-4f20-a183-5508e4b4057b	P2_1770326899	TEXT	f	e21f1598-e198-4e06-b82e-c53822730dc8	t	{}	2026-02-05 21:28:20.600134+00	2026-02-05 21:28:20.600134+00	dcc8f7e0-c4a6-4f72-b21e-78331c825d3e	dcc8f7e0-c4a6-4f72-b21e-78331c825d3e
2816a6d8-0b5d-411c-8bb6-78097507e5fc	P1_1770327052	NUMERIC	f	a33afb2d-870e-4263-88fa-9e2cb085a8f7	t	{}	2026-02-05 21:30:53.635077+00	2026-02-05 21:30:53.635077+00	274bca62-6a26-40f4-ab29-482816286c94	274bca62-6a26-40f4-ab29-482816286c94
0b93a1e8-49ab-4535-be33-dfbfb7b86748	P2_1770327052	TEXT	f	a33afb2d-870e-4263-88fa-9e2cb085a8f7	t	{}	2026-02-05 21:30:53.650004+00	2026-02-05 21:30:53.650004+00	274bca62-6a26-40f4-ab29-482816286c94	274bca62-6a26-40f4-ab29-482816286c94
78a8d90e-d189-4e0c-9815-618f465f4195	P1_1770327102	NUMERIC	f	27227759-8c29-4ba3-8ba5-153607db5c4c	t	{}	2026-02-05 21:31:42.656766+00	2026-02-05 21:31:42.656766+00	53126f3a-94da-4363-b20d-61a85c99574a	53126f3a-94da-4363-b20d-61a85c99574a
f01ac19f-b2ff-4bc9-b16a-5edb10315b41	P2_1770327102	TEXT	f	27227759-8c29-4ba3-8ba5-153607db5c4c	t	{}	2026-02-05 21:31:42.670963+00	2026-02-05 21:31:42.670963+00	53126f3a-94da-4363-b20d-61a85c99574a	53126f3a-94da-4363-b20d-61a85c99574a
5e0e278c-ed24-4ae6-b259-8a430b6ff804	P3_1770327102	SINGLE_SELECT	f	27227759-8c29-4ba3-8ba5-153607db5c4c	t	{}	2026-02-05 21:31:42.68565+00	2026-02-05 21:31:42.68565+00	53126f3a-94da-4363-b20d-61a85c99574a	53126f3a-94da-4363-b20d-61a85c99574a
467998d6-634b-40aa-8eb8-728fab704ba7	P1_1770327224	NUMERIC	f	bc651c65-73d1-41c9-a03a-275b47df7b10	t	{}	2026-02-05 21:33:45.22181+00	2026-02-05 21:33:45.22181+00	1214c599-c7c2-490b-a895-e45b985b027b	1214c599-c7c2-490b-a895-e45b985b027b
82c060ef-fec1-4d82-9e63-44b301715425	P2_1770327224	TEXT	f	bc651c65-73d1-41c9-a03a-275b47df7b10	t	{}	2026-02-05 21:33:45.237775+00	2026-02-05 21:33:45.237775+00	1214c599-c7c2-490b-a895-e45b985b027b	1214c599-c7c2-490b-a895-e45b985b027b
28230270-0fcf-4662-8c5b-8bb0ad5c57b3	P3_1770327224	SINGLE_SELECT	f	bc651c65-73d1-41c9-a03a-275b47df7b10	t	{}	2026-02-05 21:33:45.250961+00	2026-02-05 21:33:45.250961+00	1214c599-c7c2-490b-a895-e45b985b027b	1214c599-c7c2-490b-a895-e45b985b027b
e016e813-99bf-46ae-93e0-43fcc999ecff	P1_1770327280	NUMERIC	f	0a61f5ac-582c-4856-8072-27fcad588698	t	{}	2026-02-05 21:34:41.218974+00	2026-02-05 21:34:41.218974+00	d9cd5b64-e423-4710-bcfe-73606bcca78c	d9cd5b64-e423-4710-bcfe-73606bcca78c
0124f9d8-df14-40e1-a628-2fb28cfcd89b	P2_1770327280	TEXT	f	0a61f5ac-582c-4856-8072-27fcad588698	t	{}	2026-02-05 21:34:41.237611+00	2026-02-05 21:34:41.237611+00	d9cd5b64-e423-4710-bcfe-73606bcca78c	d9cd5b64-e423-4710-bcfe-73606bcca78c
5b9d413c-0d24-4b1c-bee8-2a800c357b62	P3_1770327280	SINGLE_SELECT	f	0a61f5ac-582c-4856-8072-27fcad588698	t	{}	2026-02-05 21:34:41.255709+00	2026-02-05 21:34:41.255709+00	d9cd5b64-e423-4710-bcfe-73606bcca78c	d9cd5b64-e423-4710-bcfe-73606bcca78c
baa7fe1d-099f-49de-9531-dcad3694b914	P1_1770327392	NUMERIC	f	88810bde-bf96-43e8-9791-937cd4a7e062	t	{}	2026-02-05 21:36:32.689164+00	2026-02-05 21:36:32.689164+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
56a72950-a19d-481b-a0db-3aa0940d1b7a	P2_1770327392	TEXT	f	88810bde-bf96-43e8-9791-937cd4a7e062	t	{}	2026-02-05 21:36:32.704143+00	2026-02-05 21:36:32.704143+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
6699f225-e68a-4e39-a43f-a6202cda40d5	P3_1770327392	SINGLE_SELECT	f	88810bde-bf96-43e8-9791-937cd4a7e062	t	{}	2026-02-05 21:36:32.718074+00	2026-02-05 21:36:32.718074+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
90ac4202-513e-4e0e-9de6-a32262857ed3	P1_1770327572	NUMERIC	f	5e03962b-3b0c-4bd5-9f17-6349e82083cb	t	{}	2026-02-05 21:39:33.709983+00	2026-02-05 21:39:33.709983+00	fc5165e6-6519-496f-a3dd-1435bc308b5f	fc5165e6-6519-496f-a3dd-1435bc308b5f
4a1add6d-2be5-4eb4-93d2-51ebbf5e1672	P2_1770327572	TEXT	f	5e03962b-3b0c-4bd5-9f17-6349e82083cb	t	{}	2026-02-05 21:39:33.745072+00	2026-02-05 21:39:33.745072+00	fc5165e6-6519-496f-a3dd-1435bc308b5f	fc5165e6-6519-496f-a3dd-1435bc308b5f
689e5a3e-cc7a-4148-b408-f92ec941b37e	P3_1770327572	SINGLE_SELECT	f	5e03962b-3b0c-4bd5-9f17-6349e82083cb	t	{}	2026-02-05 21:39:33.763321+00	2026-02-05 21:39:33.763321+00	fc5165e6-6519-496f-a3dd-1435bc308b5f	fc5165e6-6519-496f-a3dd-1435bc308b5f
c863d9ae-337e-4ea5-a846-3b9a8bd04020	P1_1770327636	NUMERIC	f	8bb34a8d-f5bb-41cf-ba29-87e5c652c03f	t	{}	2026-02-05 21:40:37.601754+00	2026-02-05 21:40:37.601754+00	d655e067-4edd-4516-b1b6-821c3c33cfc5	d655e067-4edd-4516-b1b6-821c3c33cfc5
a74d7503-f495-4a7b-942d-2e6d64aab25f	P2_1770327636	TEXT	f	8bb34a8d-f5bb-41cf-ba29-87e5c652c03f	t	{}	2026-02-05 21:40:37.622185+00	2026-02-05 21:40:37.622185+00	d655e067-4edd-4516-b1b6-821c3c33cfc5	d655e067-4edd-4516-b1b6-821c3c33cfc5
7acb91dd-9a2b-482c-9fc6-2eefb815aeb3	P3_1770327636	SINGLE_SELECT	f	8bb34a8d-f5bb-41cf-ba29-87e5c652c03f	t	{}	2026-02-05 21:40:37.642982+00	2026-02-05 21:40:37.642982+00	d655e067-4edd-4516-b1b6-821c3c33cfc5	d655e067-4edd-4516-b1b6-821c3c33cfc5
76452429-682f-4ba0-917e-bb4b9ffd349f	P1_1770327706	NUMERIC	f	f3200c57-c6b8-4f2d-80fe-24b9a6359f6c	t	{}	2026-02-05 21:41:47.343601+00	2026-02-05 21:41:47.343601+00	13ac055f-b943-4f6d-8182-babe636544df	13ac055f-b943-4f6d-8182-babe636544df
e46db86a-72f6-4606-8eb2-560b6b3ec315	P2_1770327706	TEXT	f	f3200c57-c6b8-4f2d-80fe-24b9a6359f6c	t	{}	2026-02-05 21:41:47.363958+00	2026-02-05 21:41:47.363958+00	13ac055f-b943-4f6d-8182-babe636544df	13ac055f-b943-4f6d-8182-babe636544df
222948be-c818-4310-bf8d-fef35d5d979c	P3_1770327706	SINGLE_SELECT	f	f3200c57-c6b8-4f2d-80fe-24b9a6359f6c	t	{}	2026-02-05 21:41:47.381531+00	2026-02-05 21:41:47.381531+00	13ac055f-b943-4f6d-8182-babe636544df	13ac055f-b943-4f6d-8182-babe636544df
b664898c-45cf-4723-8fff-b74c1232898f	P1_1770327821	NUMERIC	f	f7028cb1-7e87-4fd7-8aa1-4ea8b97ccb43	t	{}	2026-02-05 21:43:42.756468+00	2026-02-05 21:43:42.756468+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
9700c6e5-2190-443e-83b2-5183b59625e2	P2_1770327821	TEXT	f	f7028cb1-7e87-4fd7-8aa1-4ea8b97ccb43	t	{}	2026-02-05 21:43:42.781578+00	2026-02-05 21:43:42.781578+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
78f901de-8e0c-42a6-ba39-94adadbe3193	P3_1770327821	SINGLE_SELECT	f	f7028cb1-7e87-4fd7-8aa1-4ea8b97ccb43	t	{}	2026-02-05 21:43:42.795572+00	2026-02-05 21:43:42.795572+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
21f3a466-ed7c-4630-8715-9dbeca7fb00f	P1_1770328194	NUMERIC	f	e33b94b6-cfc5-4d7e-98a4-2259867e45b4	t	{}	2026-02-05 21:49:55.136751+00	2026-02-05 21:49:55.136751+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	ebc86578-b9a2-456f-b884-f964c1fb26f9
2ad12225-e5db-458e-9a8a-7d3ff1051d4c	P2_1770328194	TEXT	f	e33b94b6-cfc5-4d7e-98a4-2259867e45b4	t	{}	2026-02-05 21:49:55.156535+00	2026-02-05 21:49:55.156535+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	ebc86578-b9a2-456f-b884-f964c1fb26f9
fc1d516b-4410-42df-8d1a-2420b8d0927b	P3_1770328194	SINGLE_SELECT	f	e33b94b6-cfc5-4d7e-98a4-2259867e45b4	t	{}	2026-02-05 21:49:55.171024+00	2026-02-05 21:49:55.171024+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	ebc86578-b9a2-456f-b884-f964c1fb26f9
bee24a5b-c963-4451-86cc-068d3d4b9309	P1_1770328337	NUMERIC	f	718996de-ba3d-4b71-9a19-a6e97d2947ee	t	{}	2026-02-05 21:52:18.909202+00	2026-02-05 21:52:18.909202+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	7eddd813-1060-42a3-aa36-abc2c6529e0f
458fd9c3-1e3b-4526-90c5-b791616862e3	P2_1770328337	TEXT	f	718996de-ba3d-4b71-9a19-a6e97d2947ee	t	{}	2026-02-05 21:52:18.936877+00	2026-02-05 21:52:18.936877+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	7eddd813-1060-42a3-aa36-abc2c6529e0f
3bbea4bb-bdd5-4465-b6d1-001830971892	P3_1770328337	SINGLE_SELECT	f	718996de-ba3d-4b71-9a19-a6e97d2947ee	t	{}	2026-02-05 21:52:18.955239+00	2026-02-05 21:52:18.955239+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	7eddd813-1060-42a3-aa36-abc2c6529e0f
02f8b306-97b5-4dde-afdb-91725dfec46f	P1_1770328517	NUMERIC	f	f9761969-f234-4bb8-9b46-2ea70ad5b735	t	{}	2026-02-05 21:55:18.641195+00	2026-02-05 21:55:18.641195+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	021aea9d-7fe9-4488-ae61-eebf6d2af731
a9958b3e-69bf-42ac-a56d-c8d16d67d06b	P2_1770328517	TEXT	f	f9761969-f234-4bb8-9b46-2ea70ad5b735	t	{}	2026-02-05 21:55:18.664262+00	2026-02-05 21:55:18.664262+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	021aea9d-7fe9-4488-ae61-eebf6d2af731
ad806e19-cd1d-4a40-ae12-bd0c5c203b9b	P3_1770328517	SINGLE_SELECT	f	f9761969-f234-4bb8-9b46-2ea70ad5b735	t	{}	2026-02-05 21:55:18.68093+00	2026-02-05 21:55:18.68093+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	021aea9d-7fe9-4488-ae61-eebf6d2af731
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permissions (id, code, name, resource, action, description, created_at, updated_at) FROM stdin;
3279687a-523e-45b8-8bfc-e615eba9f71c	FARM_CREATE	farm.create	farm	create	Create new farms	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
25716ced-e201-45fd-bcfd-8e872be07e63	FARM_READ	farm.read	farm	read	View farm details	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
5a1b2123-6018-44eb-9503-72867b17df79	FARM_UPDATE	farm.update	farm	update	Update farm information	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
e6bd71a2-7683-4d7a-ab37-2bb221bc18ed	FARM_DELETE	farm.delete	farm	delete	Delete farms	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
fc6a4a81-9cbf-41f3-b968-b0d9bb8fa51e	PLOT_CREATE	plot.create	plot	create	Create new plots	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
2a5b41d5-0131-4272-a2f2-9158438693e7	PLOT_READ	plot.read	plot	read	View plot details	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
89b4ae84-6be5-4ed3-b6c3-3a28c273edcb	PLOT_UPDATE	plot.update	plot	update	Update plot information	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
4b87b0a2-b70f-40b7-b647-a6c7f236f444	PLOT_DELETE	plot.delete	plot	delete	Delete plots	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
0e6e0b98-98c3-47f7-a0bd-35712eb93f04	CROP_CREATE	crop.create	crop	create	Create new crops	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
ecd4582c-c751-475d-af73-311ec1752356	CROP_READ	crop.read	crop	read	View crop details	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
f934b0e0-66cd-444e-a1af-3b823a960771	CROP_UPDATE	crop.update	crop	update	Update crop information	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
7812443e-1cee-496e-a5c0-5a4db85f708e	CROP_DELETE	crop.delete	crop	delete	Delete crops	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
d4ac6877-f662-4ace-94b2-12a9c8083f0b	SCHEDULE_CREATE	schedule.create	schedule	create	Create schedules	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
5d533f13-d917-4364-912d-946b50aa9dfe	SCHEDULE_READ	schedule.read	schedule	read	View schedules	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
bf37032b-327f-4905-9fbf-611dcbf97950	SCHEDULE_UPDATE	schedule.update	schedule	update	Update schedules	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
ab0c28ab-215b-484f-a294-63197cd5d1c5	SCHEDULE_DELETE	schedule.delete	schedule	delete	Delete schedules	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
947a701f-d0b1-47e5-aeeb-9fa55f98ed85	ORGANIZATION_UPDATE	organization.update	organization	update	Update Organization	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
0955ca9c-40f9-4585-995d-b65cb8cd7584	ORGANIZATION_DELETE	organization.delete	organization	delete	Delete Organization	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
369f06f4-5732-4251-a6af-c63c32de9724	FINANCE_CREATE	finance.create	finance	create	Create finance transactions	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
2b6ac6e3-46ed-4b86-90d1-43afc2f0b3c4	FINANCE_READ	finance.read	finance	read	View finance transactions	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
e8f06654-e8e2-4a79-92de-1bfffe186cc6	FINANCE_UPDATE	finance.update	finance	update	Update finance transactions	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
b9f92af7-ceac-45d2-ba16-18e738e90dbd	FINANCE_DELETE	finance.delete	finance	delete	Delete finance transactions	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
84ac15a9-49cc-40bb-87ca-84d4a48b4f30	USER_INVITE	user.invite	user	invite	Invite users to organization	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
93682dcf-a18b-4dca-8729-b1f5c78be118	USER_MANAGE	user.manage	user	manage	Manage organization users	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
982cccb5-d195-4be6-b906-106b9480b4a5	QUERY_CREATE	query.create	query	create	Create queries	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
f0d3536e-56a1-4a2e-82d0-8f78306a36bd	QUERY_READ	query.read	query	read	View queries	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
2464590f-a6db-4ef7-98b2-5260db2c713d	QUERY_RESPOND	query.respond	query	respond	Respond to queries	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
90ce1518-17e5-455e-a1f2-5eb260fc515b	AUDIT_CREATE	audit.create	audit	create	Create audits	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
3c7f39c7-7bbf-4421-afe6-be1d67eda567	AUDIT_READ	audit.read	audit	read	View audits	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
14a4b32a-236e-4df4-b688-403e7c30f869	AUDIT_UPDATE	audit.update	audit	update	Update audits	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
f8b297b7-efed-4740-a42d-78c67aaed679	AUDIT_REVIEW	audit.review	audit	review	Review and finalize audits	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
8f1b6b31-4557-445e-996e-cdd0e52ac8b6	AUDIT_SHARE	audit.share	audit	share	Share audit reports	2026-01-30 00:05:41.10697+00	2026-01-30 00:05:41.10697+00
69ccf11a-5be5-4924-bdf6-c75abb0d7a1a	AUDIT_TEMPLATE_CREATE	audit.template.create	audit_template	create	Create audit templates	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
2dcad9a8-25b0-4cb6-b3d6-95223e1e81da	AUDIT_TEMPLATE_READ	audit.template.read	audit_template	read	View audit templates	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
c99f9d36-dc2a-4144-9c31-da03ff702ca0	AUDIT_TEMPLATE_UPDATE	audit.template.update	audit_template	update	Update audit templates	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
933be4e7-29f7-44db-bfcf-d0c7de9a5c6e	AUDIT_TEMPLATE_DELETE	audit.template.delete	audit_template	delete	Delete audit templates	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
2c945f75-f3ca-4e61-a89f-536f645a6c42	AUDIT_TEMPLATE_COPY	audit.template.copy	audit_template	copy	Copy audit templates	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
970309fe-cedf-484c-8caa-52b1967c4c28	AUDIT_RESPONSE	audit.response	audit	response	Submit audit responses and upload photos	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
1db3e8dc-cafd-4a15-96f4-49924f01f191	AUDIT_FINALIZE	audit.finalize	audit	finalize	Finalize audits and lock data	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
7f570664-7927-4a2d-a84c-aff34c6ca920	AUDIT_RECOMMENDATION_APPROVE	audit.recommendation.approve	audit	recommendation_approve	Approve or reject audit recommendations. For farmers	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
a2b84945-9fa5-4ede-a916-d75eddf74e7f	QUERY_RECOMMENDATION_APPROVE	query.recommendation.approve	query	recommendation_approve	Approve or reject query recommendations. For farmers	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
7da820fe-aecc-4a58-bfe2-a70c6049dcce	AUDIT_REPORT_GENERATE	audit.report.generate	audit	report_generate	Generate audit reports	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
bd3307be-da32-4397-8a93-2d2cd4d5711a	SCHEDULE_TEMPLATE_CREATE	schedule.template.create	schedule_template	create	Create schedule templates	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
de186c8e-e00a-415f-a0df-4d9b7c677b9d	SCHEDULE_TEMPLATE_READ	schedule.template.read	schedule_template	read	View schedule templates	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
93acbbc5-d363-457b-a501-9d0f48973ffe	SCHEDULE_TEMPLATE_UPDATE	schedule.template.update	schedule_template	update	Update schedule templates	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
5afd63fb-a962-45bb-a048-57470429012a	SCHEDULE_TEMPLATE_DELETE	schedule.template.delete	schedule_template	delete	Delete schedule templates	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
6473217c-70c0-494b-bcfe-7037e66f1477	SCHEDULE_TEMPLATE_COPY	schedule.template.copy	schedule_template	copy	Copy schedule templates	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
5fabd302-e953-4841-afd6-e4f0960e0305	SYSTEM_MANAGE	system.manage	system	manage	Full access to the system	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
a6c3920b-3756-4554-b73c-a0e91cb1ab9b	FSP_SERVICE_MANAGE	fsp_service.manage	fsp_service	manage	Manage FSP services which includes CRUD and all other permissions too	2026-01-30 00:05:41.66325+00	2026-01-30 00:05:41.66325+00
\.


--
-- Data for Name: plot_irrigation_modes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plot_irrigation_modes (id, plot_id, irrigation_mode_id, created_at) FROM stdin;
\.


--
-- Data for Name: plot_soil_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plot_soil_types (id, plot_id, soil_type_id, created_at) FROM stdin;
\.


--
-- Data for Name: plot_water_sources; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plot_water_sources (id, plot_id, water_source_id, created_at) FROM stdin;
\.


--
-- Data for Name: plots; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plots (id, farm_id, name, description, boundary, area, area_unit_id, plot_attributes, is_active, created_at, updated_at, created_by, updated_by) FROM stdin;
914cf77a-e929-4e0a-8d59-3f98ff892d6d	e165dd58-1298-4f46-9d62-f5e614aa934f	Plot A - North Field	\N	\N	2.5000	\N	\N	t	2026-01-30 00:08:38.991965+00	2026-01-30 00:08:38.991965+00	fe4d1e04-7569-409d-8bfc-f7319e7ea582	\N
5680d5e1-aea2-457a-864a-3db5386056dc	748bf7fa-ee25-49a9-b735-eb86c450e8ae	North	\N	\N	23423.0000	\N	{}	t	2026-01-30 00:15:18.140803+00	2026-01-30 00:15:18.140803+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
5ab1b928-57fb-404c-b246-930d976276d9	13b4a813-2a7e-4eea-9014-e79a65177f11	Debug Plot 1769940408	Debug plot	\N	2.5000	\N	{}	t	2026-02-01 10:06:48.823302+00	2026-02-01 10:06:48.823302+00	a7c620dc-005f-41e4-a09c-84a578fdff32	a7c620dc-005f-41e4-a09c-84a578fdff32
8ae3d1d3-d808-49ca-a90c-b609893dab46	e61be074-9ef2-4cbb-8a7f-c472b58c20d8	Quick Plot 1769940607	Quick test	\N	2.5000	\N	{}	t	2026-02-01 10:10:07.53895+00	2026-02-01 10:10:07.53895+00	eb63636b-e512-4cd7-9296-f0d38d62f74d	eb63636b-e512-4cd7-9296-f0d38d62f74d
558ba3d7-a42b-4139-a773-388d0daa6db2	5df6ac85-ae46-4296-a5c4-4842b38a5e34	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:31:21.37691+00	2026-02-01 10:31:21.37691+00	aec76aa4-0bf4-40bb-9307-de54a5d205a5	aec76aa4-0bf4-40bb-9307-de54a5d205a5
09d1b952-ebef-4c29-a0f5-cb453d4b6763	a88af18a-ba32-4e29-918d-241a96c84d73	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:32:49.423534+00	2026-02-01 10:32:49.423534+00	ee6157bd-176f-4f75-8cea-64adb841884f	ee6157bd-176f-4f75-8cea-64adb841884f
19088941-3e7a-4a63-8db2-5e2e77cdf844	569aa75f-1b29-49a0-b8a9-11d3471d548e	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:33:10.142534+00	2026-02-01 10:33:10.142534+00	ee193894-167a-4355-8899-7c19ba395e9f	ee193894-167a-4355-8899-7c19ba395e9f
26c45f11-5e57-490e-b1a4-b0f8bfc88559	45591473-684c-4220-940f-e1264a23c4f9	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:33:32.167716+00	2026-02-01 10:33:32.167716+00	3c1aab18-4eb2-4ab2-bcca-993c37e7fab1	3c1aab18-4eb2-4ab2-bcca-993c37e7fab1
7ec57c8e-3050-4d33-98df-9b5ba0c07e1f	5bb12bfc-8c01-40b9-8a8b-380fc5d41287	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:34:04.562207+00	2026-02-01 10:34:04.562207+00	3e72bdbc-89a7-4009-a93e-bba6fec86530	3e72bdbc-89a7-4009-a93e-bba6fec86530
11597ed7-c2b0-47eb-82c1-4ae1ac768449	9959213c-442e-4fa1-b1dd-fb2171548a99	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:34:22.116113+00	2026-02-01 10:34:22.116113+00	c5e779fa-7e25-4b84-b410-a55bd0c9e219	c5e779fa-7e25-4b84-b410-a55bd0c9e219
ea57e5a0-ae34-428d-ad8c-08f0144272d5	3cb1d1f8-48d2-4d0d-a336-414a170268e7	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:34:42.698668+00	2026-02-01 10:34:42.698668+00	b8cf8398-0dff-42c3-99ab-aaa2bcf646e6	b8cf8398-0dff-42c3-99ab-aaa2bcf646e6
ad4a57f6-b5cd-44ea-87c8-f3c21da1ed2b	8ba032c0-9cee-47ff-a19f-216bb806d53f	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:35:08.037632+00	2026-02-01 10:35:08.037632+00	a031994b-5afb-4fa2-9d8a-8004d7e8c9a3	a031994b-5afb-4fa2-9d8a-8004d7e8c9a3
b341f53a-3b73-4e63-940b-f73b84874a02	6b080a02-6e8c-4860-883c-36eab3a1034a	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:35:48.23782+00	2026-02-01 10:35:48.23782+00	2e6f6fed-9d3d-4b85-87d0-a134932d0dd7	2e6f6fed-9d3d-4b85-87d0-a134932d0dd7
1c69b5a0-3c13-4ee6-8470-00199374b770	a6ea6658-aabd-401e-b705-b7412e042a4f	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:36:44.151107+00	2026-02-01 10:36:44.151107+00	d77da629-52f1-46c9-9118-dbe7fe92c333	d77da629-52f1-46c9-9118-dbe7fe92c333
bcb351aa-b8dc-4784-9e5e-88fdc2717edb	a2cdb712-e445-411a-bb3f-70010fa01bcc	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:37:05.292459+00	2026-02-01 10:37:05.292459+00	66d51b1b-c21b-4f8c-99ba-c2854ceeab97	66d51b1b-c21b-4f8c-99ba-c2854ceeab97
0d4cf2f4-4a9f-47d3-8be3-e3549a18a3c4	a7da74c5-e783-4da3-8389-a7293d2eadc4	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:38:13.469809+00	2026-02-01 10:38:13.469809+00	3f82b4a7-b270-4d68-9e02-e9068eaa668f	3f82b4a7-b270-4d68-9e02-e9068eaa668f
cf02c06e-973e-4d58-83c4-7d948f9e1eaf	97e8f08d-7aef-41f1-919a-9c284e0680c7	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 10:38:59.309372+00	2026-02-01 10:38:59.309372+00	d5104c40-d4cc-47ac-a700-0c7414c1b26a	d5104c40-d4cc-47ac-a700-0c7414c1b26a
9c7de365-ad4e-4f28-85ce-b4f0effa7386	49303b32-b426-4909-8d02-1e572a8a83b4	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 11:01:39.770977+00	2026-02-01 11:01:39.770977+00	fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1	fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1
4123d9ec-4f1f-4acf-b797-aa2eb18f6fda	51aabf82-b0ba-401b-9201-6886cb4c0ce5	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-01 11:06:39.203724+00	2026-02-01 11:06:39.203724+00	1a8f4448-290b-48ff-9f17-2d76e841a1f3	1a8f4448-290b-48ff-9f17-2d76e841a1f3
bafaa4d4-8461-4cbd-af31-760abbc0214c	e6258a38-cf90-4e0d-ac99-8cee5de538d7	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:28:20.337515+00	2026-02-05 21:28:20.337515+00	5847755d-a7ef-4f01-ad83-b96116cc5b06	5847755d-a7ef-4f01-ad83-b96116cc5b06
539d5974-df3d-473d-a7b2-103c18e314ff	757e3cc4-c50a-43a9-8311-c5b9729a3b29	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:30:53.589657+00	2026-02-05 21:30:53.589657+00	3ca9cf6b-c372-4530-bc35-3440c68f858f	3ca9cf6b-c372-4530-bc35-3440c68f858f
c37e7e74-11b6-4191-a4d2-967137792659	188b63e7-c8ae-4814-86dd-ec23230acade	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:31:42.618641+00	2026-02-05 21:31:42.618641+00	09b95fab-3a52-4e54-8957-76e81ebf668a	09b95fab-3a52-4e54-8957-76e81ebf668a
aa9c75f2-8264-49e7-9218-634341955404	c0ff0571-68ae-4653-9aa5-e4da8d62c869	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:33:45.168639+00	2026-02-05 21:33:45.168639+00	39219340-21cb-4a88-a939-93baf1a0e840	39219340-21cb-4a88-a939-93baf1a0e840
f8ebbe83-8611-4672-8a18-75dea56e2535	d6104529-6570-4fe5-bc22-fa3a9d232ce1	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:34:41.165175+00	2026-02-05 21:34:41.165175+00	5368cfba-bae0-4132-88e4-4fde67d9e523	5368cfba-bae0-4132-88e4-4fde67d9e523
4e9c8e28-bcd1-4252-bf4c-a2b93fa8c21a	3eb45481-89c5-4a87-8e3d-91d4a2d60819	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:36:32.65132+00	2026-02-05 21:36:32.65132+00	222968c5-f7cd-46a9-80a7-ae6d0557b5c3	222968c5-f7cd-46a9-80a7-ae6d0557b5c3
11f72f4e-1fd9-4ce2-8da1-d6a75a1e9b31	23bd05f9-b2e7-412d-95e2-3ff7b45cbb46	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:39:33.619589+00	2026-02-05 21:39:33.619589+00	2b8bb712-3cfe-435e-84f7-49dfe73d641b	2b8bb712-3cfe-435e-84f7-49dfe73d641b
3a40152d-4f4b-4b62-b299-d7c5e6314dd9	44d4750b-3477-47c4-91c3-585d41b5d6df	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:40:37.549756+00	2026-02-05 21:40:37.549756+00	ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f	ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f
bf759bec-0219-4b5a-b643-5e75f263b1a3	0a974e46-ced3-4a5c-bd2e-63cc1272cd1d	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:41:47.294533+00	2026-02-05 21:41:47.294533+00	eb271702-3161-48b2-a4c9-8747819b7ae7	eb271702-3161-48b2-a4c9-8747819b7ae7
63dee78b-f015-4b3f-ae62-0ef30f0ddba1	11921704-4567-49d4-ab50-389eb3244c9f	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:43:42.704716+00	2026-02-05 21:43:42.704716+00	31148b05-1512-43ce-8b01-fd3b423fca6e	31148b05-1512-43ce-8b01-fd3b423fca6e
02467fc1-7bc3-474d-adb7-e6ca4f7f13a8	d5c905a8-e8bc-461f-9a4b-59f7222b96ca	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:49:55.078868+00	2026-02-05 21:49:55.078868+00	3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167	3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167
08b684c6-9193-439d-a1ef-faa33218a7b1	2b7519d8-2dab-470d-8de5-ca41a7684e13	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:52:18.83393+00	2026-02-05 21:52:18.83393+00	83e1d52b-a86b-461a-b995-e79e2ac57878	83e1d52b-a86b-461a-b995-e79e2ac57878
bf7294d2-e398-47cc-ad8c-955564e3f690	a765e151-2bc0-4030-a764-4471e772b546	Plot 1	\N	\N	5.0000	\N	{}	t	2026-02-05 21:55:18.573068+00	2026-02-05 21:55:18.573068+00	1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3	1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3
ca345bb0-75ea-41ae-8f8f-c9a68cbb63d2	fe011730-4986-4034-9815-f7650216b5a5	Test Plot 1770330826	Test plot for crops	\N	5.0000	\N	{}	t	2026-02-05 22:33:46.460052+00	2026-02-05 22:33:46.460052+00	723079fb-4d41-408d-958c-a1d417576d82	723079fb-4d41-408d-958c-a1d417576d82
4aa5abad-51da-4c92-b667-ab53a855d533	748bf7fa-ee25-49a9-b735-eb86c450e8ae	south	\N	\N	23.0000	1c6b90ac-ff6b-4c5f-be90-5f33c91725d4	{"area_unit_id": "1c6b90ac-ff6b-4c5f-be90-5f33c91725d4", "soil_type_id": "5f832dc9-7c97-4c7a-bd20-c766cca64016", "water_source_ids": ["07f65611-5b1b-40ad-b25b-16839eb9b098"]}	t	2026-01-30 00:15:18.189217+00	2026-02-09 12:51:44.698087+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
\.


--
-- Data for Name: push_notification_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.push_notification_tokens (id, user_id, device_token, device_type, device_id, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: queries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.queries (id, farming_organization_id, fsp_organization_id, work_order_id, query_number, title, description, farm_id, plot_id, crop_id, status, priority, created_at, updated_at, created_by, updated_by, resolved_at, resolved_by, closed_at) FROM stdin;
\.


--
-- Data for Name: query_photos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.query_photos (id, query_id, query_response_id, file_url, file_key, caption, uploaded_at, uploaded_by) FROM stdin;
\.


--
-- Data for Name: query_responses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.query_responses (id, query_id, response_text, has_recommendation, created_at, created_by) FROM stdin;
\.


--
-- Data for Name: reference_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reference_data (id, type_id, code, sort_order, is_active, reference_metadata, created_at, updated_at) FROM stdin;
72aa34a3-34b0-492b-a1ac-83ccd6ec5e77	24901a7b-551d-4177-9057-0aa850cdaba6	WELL	1	t	\N	2026-01-30 00:05:41.143397+00	2026-01-30 00:05:41.143397+00
07f65611-5b1b-40ad-b25b-16839eb9b098	24901a7b-551d-4177-9057-0aa850cdaba6	BOREWELL	2	t	\N	2026-01-30 00:05:41.143397+00	2026-01-30 00:05:41.143397+00
214ee942-e66b-4f9a-8db6-3dd0afcbffe7	24901a7b-551d-4177-9057-0aa850cdaba6	RIVER	3	t	\N	2026-01-30 00:05:41.143397+00	2026-01-30 00:05:41.143397+00
2a26d1e1-e962-404d-ba06-c276035c79ab	24901a7b-551d-4177-9057-0aa850cdaba6	CANAL	4	t	\N	2026-01-30 00:05:41.143397+00	2026-01-30 00:05:41.143397+00
6ba172f9-07bc-42e8-ba76-b425be982115	24901a7b-551d-4177-9057-0aa850cdaba6	POND	5	t	\N	2026-01-30 00:05:41.143397+00	2026-01-30 00:05:41.143397+00
58a3afa0-2632-400d-82ce-dfa38e560ecf	24901a7b-551d-4177-9057-0aa850cdaba6	RAINWATER_ONLY	6	t	\N	2026-01-30 00:05:41.143397+00	2026-01-30 00:05:41.143397+00
5f832dc9-7c97-4c7a-bd20-c766cca64016	0d17dd3a-11b0-4309-9bbd-2f19976535f4	SAND	1	t	\N	2026-01-30 00:05:41.166483+00	2026-01-30 00:05:41.166483+00
2e7fba12-cb3d-4e66-80c8-d984530d043c	0d17dd3a-11b0-4309-9bbd-2f19976535f4	CLAY	2	t	\N	2026-01-30 00:05:41.166483+00	2026-01-30 00:05:41.166483+00
a92c2610-98d2-4511-b0c9-27a3d598c2f3	0d17dd3a-11b0-4309-9bbd-2f19976535f4	LOAM	3	t	\N	2026-01-30 00:05:41.166483+00	2026-01-30 00:05:41.166483+00
56a2f3b2-59cb-4a03-941d-04e3225d9017	0d17dd3a-11b0-4309-9bbd-2f19976535f4	CLAY_LOAM	4	t	\N	2026-01-30 00:05:41.166483+00	2026-01-30 00:05:41.166483+00
3d10eaef-93f0-4c19-b54d-8ea5ff59df70	0d17dd3a-11b0-4309-9bbd-2f19976535f4	BLACK_COTTON	5	t	\N	2026-01-30 00:05:41.166483+00	2026-01-30 00:05:41.166483+00
70dba4e0-4629-42d9-bd61-967ca33e6db0	0d17dd3a-11b0-4309-9bbd-2f19976535f4	RED_SOIL	6	t	\N	2026-01-30 00:05:41.166483+00	2026-01-30 00:05:41.166483+00
92852b64-7ff6-4887-9b49-ee3189d5ba6b	97fa9b1d-f650-4329-8352-419bd0ab5438	DRIP	1	t	\N	2026-01-30 00:05:41.189608+00	2026-01-30 00:05:41.189608+00
07958c09-840f-42b6-acc2-cb005e6ec32b	97fa9b1d-f650-4329-8352-419bd0ab5438	SPRINKLER	2	t	\N	2026-01-30 00:05:41.189608+00	2026-01-30 00:05:41.189608+00
3618cfa2-9eab-407c-870e-b16d9feccb61	97fa9b1d-f650-4329-8352-419bd0ab5438	MICRO_SPRINKLER	3	t	\N	2026-01-30 00:05:41.189608+00	2026-01-30 00:05:41.189608+00
e065ce2a-9eaf-4c49-b6f0-259ed2814af2	97fa9b1d-f650-4329-8352-419bd0ab5438	FLOOD	4	t	\N	2026-01-30 00:05:41.189608+00	2026-01-30 00:05:41.189608+00
b6b69773-e056-45eb-bdea-a343b749e0a7	1580fcd5-9e2f-49cb-b068-3e3c5c3bdbf9	FOLIAR_SPRAY	1	t	{"requires_concentration": true}	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00
39dad72b-ab7c-4823-957f-0dbba2f2d4db	1580fcd5-9e2f-49cb-b068-3e3c5c3bdbf9	SOIL_APPLICATION	2	t	{"requires_concentration": false}	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00
7233de84-b65b-42fb-b45e-0c631f6aa50d	1580fcd5-9e2f-49cb-b068-3e3c5c3bdbf9	DRIP_IRRIGATION	3	t	{"requires_concentration": true}	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00
7c0671fe-5746-47f5-880b-1a22b37abd1c	1580fcd5-9e2f-49cb-b068-3e3c5c3bdbf9	BROADCASTING	4	t	{"requires_concentration": false}	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00
1d8178d2-7686-498c-bdf0-4dc31cb1f4c9	1580fcd5-9e2f-49cb-b068-3e3c5c3bdbf9	SEED_TREATMENT	5	t	{"requires_concentration": true}	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00
b05cf9fd-f070-4923-a2fe-2a2944c8864a	1580fcd5-9e2f-49cb-b068-3e3c5c3bdbf9	DRENCHING	6	t	{"requires_concentration": true}	2026-01-30 10:00:39.742302+00	2026-01-30 10:00:39.742302+00
\.


--
-- Data for Name: reference_data_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reference_data_translations (id, reference_data_id, language_code, display_name, description, created_at) FROM stdin;
871ec77e-58c7-4f24-92d0-0ac1de837d79	72aa34a3-34b0-492b-a1ac-83ccd6ec5e77	en	Well	\N	2026-01-30 00:05:41.15497+00
bb80952e-a063-48b4-bacf-34f911e987ec	07f65611-5b1b-40ad-b25b-16839eb9b098	en	Borewell	\N	2026-01-30 00:05:41.15497+00
76c76b69-9084-4d15-8368-0ca6ab78261f	214ee942-e66b-4f9a-8db6-3dd0afcbffe7	en	River	\N	2026-01-30 00:05:41.15497+00
a38a8861-120b-4fcb-824e-23f1500953af	2a26d1e1-e962-404d-ba06-c276035c79ab	en	Canal	\N	2026-01-30 00:05:41.15497+00
b726d539-52f3-4816-a9ad-2e2162c989a1	6ba172f9-07bc-42e8-ba76-b425be982115	en	Pond	\N	2026-01-30 00:05:41.15497+00
cefd2c8c-c849-4ae6-b85f-af7a7acec32d	58a3afa0-2632-400d-82ce-dfa38e560ecf	en	Rainwater Only	\N	2026-01-30 00:05:41.15497+00
0ee3b026-908b-4213-8550-6806df9d8b4f	72aa34a3-34b0-492b-a1ac-83ccd6ec5e77	ta	கிணறு	\N	2026-01-30 00:05:41.15497+00
25b5d2e8-475c-426b-bee0-c2a928ebc542	07f65611-5b1b-40ad-b25b-16839eb9b098	ta	ஆழ்துளை கிணறு	\N	2026-01-30 00:05:41.15497+00
32799b34-669c-4049-9ae3-8291fec9600d	214ee942-e66b-4f9a-8db6-3dd0afcbffe7	ta	ஆறு	\N	2026-01-30 00:05:41.15497+00
a36edb4c-adfb-4c29-884c-0b1937053119	2a26d1e1-e962-404d-ba06-c276035c79ab	ta	கால்வாய்	\N	2026-01-30 00:05:41.15497+00
e52d6cae-944c-42ea-9cda-ba304e4987d6	6ba172f9-07bc-42e8-ba76-b425be982115	ta	குளம்	\N	2026-01-30 00:05:41.15497+00
21349447-fd9e-472f-8489-50d1bebf78ea	58a3afa0-2632-400d-82ce-dfa38e560ecf	ta	மழை நீர் மட்டும்	\N	2026-01-30 00:05:41.15497+00
e65e0e17-6d2e-4f3f-a3b2-3f60d2212bb1	72aa34a3-34b0-492b-a1ac-83ccd6ec5e77	ml	കിണർ	\N	2026-01-30 00:05:41.15497+00
56d893c4-6943-45d3-be63-c9904a881e5c	07f65611-5b1b-40ad-b25b-16839eb9b098	ml	ബോർവെൽ	\N	2026-01-30 00:05:41.15497+00
db253f0a-f257-4668-9559-30b18a226e12	214ee942-e66b-4f9a-8db6-3dd0afcbffe7	ml	നദി	\N	2026-01-30 00:05:41.15497+00
44197b59-6cc8-403c-b8c1-6cd60c600906	2a26d1e1-e962-404d-ba06-c276035c79ab	ml	കനാൽ	\N	2026-01-30 00:05:41.15497+00
92464636-796f-4d5a-8876-12ef5493163d	6ba172f9-07bc-42e8-ba76-b425be982115	ml	കുളം	\N	2026-01-30 00:05:41.15497+00
94d4e7cf-8d5f-4dbe-bbdf-9f16510e57c0	58a3afa0-2632-400d-82ce-dfa38e560ecf	ml	മഴവെള്ളം മാത്രം	\N	2026-01-30 00:05:41.15497+00
d8bbafa5-2f2a-459b-a382-cc1a8941d31f	5f832dc9-7c97-4c7a-bd20-c766cca64016	en	Sand	\N	2026-01-30 00:05:41.177924+00
51e57c60-5719-40cc-b2e0-f9386fd3c01c	2e7fba12-cb3d-4e66-80c8-d984530d043c	en	Clay	\N	2026-01-30 00:05:41.177924+00
7cfa369e-a9c8-421c-86bf-5066845fe6b8	a92c2610-98d2-4511-b0c9-27a3d598c2f3	en	Loam	\N	2026-01-30 00:05:41.177924+00
7080935e-c4c3-4969-969a-0760b47afa46	56a2f3b2-59cb-4a03-941d-04e3225d9017	en	Clay Loam	\N	2026-01-30 00:05:41.177924+00
9690b7b6-6a4c-45f5-bef6-dff34255655a	3d10eaef-93f0-4c19-b54d-8ea5ff59df70	en	Black Cotton	\N	2026-01-30 00:05:41.177924+00
a57ff602-04f3-4771-aad0-1b0be5574449	70dba4e0-4629-42d9-bd61-967ca33e6db0	en	Red Soil	\N	2026-01-30 00:05:41.177924+00
bf08a955-62b4-4470-8a55-503372fe2864	5f832dc9-7c97-4c7a-bd20-c766cca64016	ta	மணல்	\N	2026-01-30 00:05:41.177924+00
50790702-2bfc-4da7-9b59-bffc9a343e08	2e7fba12-cb3d-4e66-80c8-d984530d043c	ta	களிமண்	\N	2026-01-30 00:05:41.177924+00
897400e0-8632-40e2-9ae3-9f47d1f75520	a92c2610-98d2-4511-b0c9-27a3d598c2f3	ta	வண்டல்	\N	2026-01-30 00:05:41.177924+00
0ae227f3-6064-4ff5-9d3c-100461af6ef1	56a2f3b2-59cb-4a03-941d-04e3225d9017	ta	களிமண் வண்டல்	\N	2026-01-30 00:05:41.177924+00
6d2b3adf-bd6a-4781-8344-5a450786835c	3d10eaef-93f0-4c19-b54d-8ea5ff59df70	ta	கருப்பு பருத்தி மண்	\N	2026-01-30 00:05:41.177924+00
03854661-e4d0-4a35-a11e-8d06255f20a9	70dba4e0-4629-42d9-bd61-967ca33e6db0	ta	சிவப்பு மண்	\N	2026-01-30 00:05:41.177924+00
363b4ed1-d6a4-4c31-9a6f-cee63532bad0	5f832dc9-7c97-4c7a-bd20-c766cca64016	ml	മണൽ	\N	2026-01-30 00:05:41.177924+00
9da09904-cfa2-4632-9d50-92003d5a97a0	2e7fba12-cb3d-4e66-80c8-d984530d043c	ml	കളിമണ്ണ്	\N	2026-01-30 00:05:41.177924+00
1282248f-b6eb-41a0-b9eb-c3021707ff4e	a92c2610-98d2-4511-b0c9-27a3d598c2f3	ml	ലോം	\N	2026-01-30 00:05:41.177924+00
79df00e2-63e0-4a4a-a199-a58766e24d95	56a2f3b2-59cb-4a03-941d-04e3225d9017	ml	കളിമണ്ണ് ലോം	\N	2026-01-30 00:05:41.177924+00
b046d9a7-f620-45b9-81b0-6de770674114	3d10eaef-93f0-4c19-b54d-8ea5ff59df70	ml	കറുത്ത പരുത്തി മണ്ണ്	\N	2026-01-30 00:05:41.177924+00
23914337-f390-4ab8-a06f-3c9406ece210	70dba4e0-4629-42d9-bd61-967ca33e6db0	ml	ചുവന്ന മണ്ണ്	\N	2026-01-30 00:05:41.177924+00
0e403a50-ec18-4ca3-8dc2-3a0c10020e5d	92852b64-7ff6-4887-9b49-ee3189d5ba6b	en	Drip	\N	2026-01-30 00:05:41.201106+00
e967e36c-56b7-4337-9fc2-12c6e1cda53a	07958c09-840f-42b6-acc2-cb005e6ec32b	en	Sprinkler	\N	2026-01-30 00:05:41.201106+00
a2ee92e5-89dc-4d57-a117-775eabf2f76d	3618cfa2-9eab-407c-870e-b16d9feccb61	en	Micro Sprinkler	\N	2026-01-30 00:05:41.201106+00
fd47161c-6d01-45a0-b9e4-eee6765c29ed	e065ce2a-9eaf-4c49-b6f0-259ed2814af2	en	Flood	\N	2026-01-30 00:05:41.201106+00
4ec290bd-2359-44ff-9e6c-ff4f136b0e08	92852b64-7ff6-4887-9b49-ee3189d5ba6b	ta	சொட்டு நீர்	\N	2026-01-30 00:05:41.201106+00
360969f0-994b-487c-aa2e-af46d4ea1994	07958c09-840f-42b6-acc2-cb005e6ec32b	ta	தெளிப்பான்	\N	2026-01-30 00:05:41.201106+00
e1bdaf80-563d-4ea4-8f4e-72ed9ae50fe1	3618cfa2-9eab-407c-870e-b16d9feccb61	ta	நுண் தெளிப்பான்	\N	2026-01-30 00:05:41.201106+00
d11f2d25-9385-4c53-9e90-d2ece1549147	e065ce2a-9eaf-4c49-b6f0-259ed2814af2	ta	வெள்ள நீர்ப்பாசனம்	\N	2026-01-30 00:05:41.201106+00
afedc43f-e737-4249-8762-1db33f185e3f	92852b64-7ff6-4887-9b49-ee3189d5ba6b	ml	ഡ്രിപ്പ്	\N	2026-01-30 00:05:41.201106+00
11e71a2d-7b39-458f-90cb-a8fa4e4756d1	07958c09-840f-42b6-acc2-cb005e6ec32b	ml	സ്പ്രിങ്ക്ലർ	\N	2026-01-30 00:05:41.201106+00
954ec231-79cd-4dac-b6d5-5f73d0c7ff50	3618cfa2-9eab-407c-870e-b16d9feccb61	ml	മൈക്രോ സ്പ്രിങ്ക്ലർ	\N	2026-01-30 00:05:41.201106+00
fbabc880-4215-4563-9b9a-a326649d5d3e	e065ce2a-9eaf-4c49-b6f0-259ed2814af2	ml	വെള്ളപ്പൊക്ക ജലസേചനം	\N	2026-01-30 00:05:41.201106+00
e9a083ff-9e0d-4162-89d4-ae1bb73383e3	b6b69773-e056-45eb-bdea-a343b749e0a7	en	Foliar Spray	Foliar Spray	2026-01-30 10:00:39.742302+00
1a959ae5-4261-43ae-b01d-f5eac2db536d	39dad72b-ab7c-4823-957f-0dbba2f2d4db	en	Soil Application	Soil Application	2026-01-30 10:00:39.742302+00
796dda5c-7f59-48d3-8bc9-db9477804fe5	7233de84-b65b-42fb-b45e-0c631f6aa50d	en	Drip Irrigation	Drip Irrigation	2026-01-30 10:00:39.742302+00
d71dae9d-4909-416f-85a2-9986fb172725	7c0671fe-5746-47f5-880b-1a22b37abd1c	en	Broadcasting	Broadcasting	2026-01-30 10:00:39.742302+00
35dd9332-c897-44b7-88ae-79a67a656fba	1d8178d2-7686-498c-bdf0-4dc31cb1f4c9	en	Seed Treatment	Seed Treatment	2026-01-30 10:00:39.742302+00
d0c467ef-fe00-43ee-afc2-4b927631a991	b05cf9fd-f070-4923-a2fe-2a2944c8864a	en	Drenching	Drenching	2026-01-30 10:00:39.742302+00
\.


--
-- Data for Name: reference_data_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reference_data_types (id, code, name, description, created_at) FROM stdin;
24901a7b-551d-4177-9057-0aa850cdaba6	WATER_SOURCE	Water Sources	Types of water sources for irrigation	2026-01-30 00:05:41.131595+00
0d17dd3a-11b0-4309-9bbd-2f19976535f4	SOIL_TYPE	Soil Types	Types of soil	2026-01-30 00:05:41.131595+00
97fa9b1d-f650-4329-8352-419bd0ab5438	IRRIGATION_MODE	Irrigation Modes	Methods of irrigation	2026-01-30 00:05:41.131595+00
1580fcd5-9e2f-49cb-b068-3e3c5c3bdbf9	application_methods	Application Methods	Methods of applying inputs like fertilizer or pesticide	2026-01-30 10:00:39.742302+00
\.


--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.refresh_tokens (id, user_id, token_hash, device_info, expires_at, is_revoked, revoked_at, created_at) FROM stdin;
d53e9893-a29d-4749-b44d-7ecf228db321	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2966695976894de6bb167078ec89462aab6cce43b500fe66cd221b480127b484	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 00:10:54.968411+00	f	\N	2026-01-30 00:10:54.943193+00
f94c7402-caeb-45e9-bf3e-e5fec7b043b1	3f3a3a39-d867-45a8-b901-74a7e27c95f3	42b554e25fd92e5fce2362af03185d9d49aff48d589a0c3d1c92009c822b41c6	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 00:34:32.534226+00	f	\N	2026-01-30 00:34:32.454657+00
3fabcd03-860b-43d9-99ab-b95f9f35639b	3f3a3a39-d867-45a8-b901-74a7e27c95f3	1e3b35911beb82c5c962c6934da0bef433cf3f458619f15770b1652e3b4e9ef9	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 01:11:33.525689+00	f	\N	2026-01-30 01:11:33.503573+00
129be796-bb73-44e6-ba6d-7a571d0da805	3f3a3a39-d867-45a8-b901-74a7e27c95f3	d5076d0ad23b3d41a53c7609a25b93b5e25e5b4ef77caab4a155258f6071d498	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 01:11:48.207935+00	f	\N	2026-01-30 01:11:48.20296+00
f764b371-364f-4eb3-bc57-7ea667665d1d	3f3a3a39-d867-45a8-b901-74a7e27c95f3	da03c801a9572503d37f2d0e471ab879299500217a59a75900fc41b88ed1df86	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 01:14:07.178359+00	f	\N	2026-01-30 01:14:07.156371+00
1924fa1c-2c72-4936-9a8e-e9ddcb0c0cb0	3f3a3a39-d867-45a8-b901-74a7e27c95f3	0b08559368897c3d95dcda493ee56804145f3e8cb0a4b01f96d605fe4afc9178	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 07:04:55.440448+00	f	\N	2026-01-30 07:04:55.424264+00
ae2f7d16-7559-4242-bd17-76f78050be1a	3f3a3a39-d867-45a8-b901-74a7e27c95f3	6adb798f1709dc4edc54984d46878a0043f3df4e6a19d0c0d4454781e08748c1	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 07:25:22.862306+00	f	\N	2026-01-30 07:25:22.830436+00
94f48244-385e-43d4-b57f-f3b576c2a59a	3f3a3a39-d867-45a8-b901-74a7e27c95f3	e002e3bb701b04693ef275b9a846cbf2d6b63aafbb2a2b351a46cf0de20f5166	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 07:59:10.845127+00	f	\N	2026-01-30 07:59:10.801312+00
54594818-5f1a-4e74-bdeb-e6a14c591159	3f3a3a39-d867-45a8-b901-74a7e27c95f3	247558813c0517b22fe867d2ab34f644491c274c80169d1acdff8f0070e47e36	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 08:36:21.311508+00	f	\N	2026-01-30 08:36:21.30664+00
32708702-7e0c-47e6-8f77-924f5bd235c3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	76d427c55e0bcb9e46fa8c59c3727e519ed515079556119312ea9715fd0431fc	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 08:43:03.349527+00	f	\N	2026-01-30 08:43:03.343406+00
23de43ae-f8d8-4c0c-b87e-31de0d256ab4	3f3a3a39-d867-45a8-b901-74a7e27c95f3	060e2746f76494ef7de745b4e046b3e6c2ab09bacd6d98026f896a7db59b0962	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 09:12:21.090842+00	f	\N	2026-01-30 09:12:21.062496+00
6f76fa65-b4a3-4d71-afc2-7083e3655c31	3f3a3a39-d867-45a8-b901-74a7e27c95f3	a2d90f8d3acc053a120b59c14882b316702f70a4003d4919b6d1ba87b9edad51	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 09:42:41.769175+00	f	\N	2026-01-30 09:42:41.72281+00
9547dbfc-2842-4e5b-b050-4a249116710c	3f3a3a39-d867-45a8-b901-74a7e27c95f3	210b567d2ba15c91db72d12149fa534fb1cf83e68cfcd347dda96ceb8e4a6242	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 10:08:04.35796+00	f	\N	2026-01-30 10:08:04.339657+00
a68c4a65-f4d1-4ac8-b78a-3f8f9ebd26ee	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2e2cbf1fa6066093498dbcc712f23dcb8178c6f01cc842ced827ac33aa75e6dc	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 10:17:59.454107+00	f	\N	2026-01-30 10:17:59.438451+00
cc308460-400d-4961-bbbe-a78f59c647ac	3f3a3a39-d867-45a8-b901-74a7e27c95f3	4861010e63a042c3741a7c768e36b96eadbd6e876fc3b0432394ba939af89a03	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 10:54:45.429869+00	f	\N	2026-01-30 10:54:45.407286+00
4754cdf5-4435-47e6-b125-cf3e80f54c9f	3f3a3a39-d867-45a8-b901-74a7e27c95f3	65c25548a2d5fbff5c74a9ed85d43e575216d1b5481c3af268cc3d40b60c1d3c	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 11:03:38.520667+00	f	\N	2026-01-30 11:03:38.502338+00
5c03f74d-45e3-4d5e-838e-1a14d001260b	3f3a3a39-d867-45a8-b901-74a7e27c95f3	ecd6675bd977c3d108bb52bf402596c05b07d3b11e45cec9e37813d1ba64e939	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 12:44:43.624546+00	f	\N	2026-01-30 12:44:43.4915+00
5efd46ff-9597-4f58-8cc2-45ebc8952d8e	3f3a3a39-d867-45a8-b901-74a7e27c95f3	412081a8ce10beb6e8b43f6bf229e7c119d39af2488959d4adaf30abd233560c	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 13:18:41.790971+00	f	\N	2026-01-30 13:18:41.767287+00
36714155-50bb-4068-abf4-a7e6289ebd41	3f3a3a39-d867-45a8-b901-74a7e27c95f3	8a104dd95b600c451bdb7bbcddc88f8f50ffe455c94c824ea5e98597adff3ab9	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 13:27:57.240325+00	f	\N	2026-01-30 13:27:57.235533+00
948a104a-083e-4ef6-b242-007790e17ab5	3f3a3a39-d867-45a8-b901-74a7e27c95f3	59e9600a3f4a7a48498abba0c834351f77fda0cb667f1e7bc52aff29f9bf9b81	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 14:00:38.670292+00	f	\N	2026-01-30 14:00:38.641967+00
e27c59c7-5ddb-4880-89a4-485a3a86ca48	3f3a3a39-d867-45a8-b901-74a7e27c95f3	a97f6ee54c24526da61fa0bff372e06ae20b6ca5cfd0591aca879a4c05e4e918	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 15:09:52.621513+00	f	\N	2026-01-30 15:09:52.599983+00
a92ca792-16d0-4e0e-a204-7e386d50f800	3f3a3a39-d867-45a8-b901-74a7e27c95f3	ce76d191687ee784db062ddd549943285bf219c0712ba1e4c2c46205a360e8ee	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 15:17:53.524383+00	f	\N	2026-01-30 15:17:53.501229+00
3f207337-4b25-480f-902b-1074f8a58864	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2dd2ee20259433faf1a5b553d7097ec246b14197d3998728c00015c7e0c3777c	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 15:31:04.450064+00	f	\N	2026-01-30 15:31:04.425236+00
efb2e3d6-ca7f-4487-be4c-e56f098ad1da	3f3a3a39-d867-45a8-b901-74a7e27c95f3	5811d3ae4740924eaee692f960529c54631d37edc160338de03026d98c7dd021	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 15:39:51.227689+00	f	\N	2026-01-30 15:39:51.216518+00
aeeb3cf0-3c89-4981-ab2b-71432fa42cc7	3f3a3a39-d867-45a8-b901-74a7e27c95f3	49f642290460cd67d53176b700135a3b04a79f836eb7d3ed4139e87093162faa	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 15:41:47.139385+00	f	\N	2026-01-30 15:41:47.114306+00
d20eb3b9-fdb4-4a19-b4b1-c3d56b4c2f7f	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3627eed27b957c90c105cfa684100e0d25a0352d5dc9c33f662f28064de6b289	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 15:47:11.761175+00	f	\N	2026-01-30 15:47:11.74986+00
a1ded9c0-5459-4b8d-8325-525273e1997c	3f3a3a39-d867-45a8-b901-74a7e27c95f3	bf4cb08cb62cea22dcfc5931c260dfea3e369d30da7674d78cf7fe73f72a5fb8	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 15:58:06.506942+00	f	\N	2026-01-30 15:58:06.4753+00
82c9c6ce-e614-4337-a386-99b29872c844	3f3a3a39-d867-45a8-b901-74a7e27c95f3	a87b14c5c9591cc118a2005500a844910fabfc1d46100b1cfab51e11cc35515f	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 19:29:20.74733+00	f	\N	2026-01-30 19:29:20.727104+00
bb816c4b-38ca-406f-b94f-36c19b15b3b3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	432d6693d0a34a273d6d698403127d35f2d420fcc4d9fd3dd2bbc3ea1ebf037a	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 19:30:41.339639+00	f	\N	2026-01-30 19:30:41.32801+00
81c24196-cbfe-450f-8651-5d55fe6f0e56	3f3a3a39-d867-45a8-b901-74a7e27c95f3	d922a10a46957cdb308a10256c9823632e4268fdc79aed84fdc8c5b5da88405c	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 19:39:51.167503+00	f	\N	2026-01-30 19:39:51.158246+00
64987e5b-46f4-4367-9e30-9afb4484cb61	3f3a3a39-d867-45a8-b901-74a7e27c95f3	fe5fc9ceca7eb21f47b3f2d52cb62269cf73c02c6e2088d5727310959b2e55ce	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 19:43:55.194022+00	f	\N	2026-01-30 19:43:55.136908+00
088e7cbb-b96c-427a-bc9b-e837116b4a67	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3be79b98f25df0ede5b9cfe247e0db8559a0578068d17fde792694e4a9b86f3d	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 19:46:58.716533+00	f	\N	2026-01-30 19:46:58.689049+00
9b618de2-2a6c-4166-b649-1a655268ef70	3f3a3a39-d867-45a8-b901-74a7e27c95f3	053cf3dfe1687a97cef98697d678078664fc4bcb84710a6e81dfe3b4aaeb353c	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 19:50:27.965999+00	f	\N	2026-01-30 19:50:27.935316+00
face48a1-50c8-4047-a0f9-04101753ee51	3f3a3a39-d867-45a8-b901-74a7e27c95f3	8c804d91add77133fdbfc5070396ea9b7ca262746e5e8a643bdf020e664b7d9d	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 20:02:57.583026+00	f	\N	2026-01-30 20:02:57.573702+00
7deba8fc-e66e-4eda-a261-d88debc5e2df	3f3a3a39-d867-45a8-b901-74a7e27c95f3	05dd8ed2d92a25f8eef339dc602f7814cef82da063b9a41c661231d38c845876	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 20:05:25.982777+00	f	\N	2026-01-30 20:05:25.968624+00
65b6c631-a626-4e75-96ca-46700f665475	3f3a3a39-d867-45a8-b901-74a7e27c95f3	9f7d973d59f15f3479bebb1add62d18a586d2565d540291ea82e7904305c57c7	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 20:32:10.891853+00	f	\N	2026-01-30 20:32:10.861427+00
7286cd6b-fd42-4cf4-ad28-77d73810de99	3f3a3a39-d867-45a8-b901-74a7e27c95f3	03054cad567112be9fcd8409fb67b92692c4d156c7c4ea6e949af0e2f2fa2971	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 20:51:06.135942+00	f	\N	2026-01-30 20:51:06.100009+00
207c77ef-6810-4c2d-8e41-e045778e7cfd	3f3a3a39-d867-45a8-b901-74a7e27c95f3	648c8a6b6adfadfa7711f62ca6b566a1351949fc786748e353de47bb1b105c92	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 21:29:21.048327+00	f	\N	2026-01-30 21:29:21.028205+00
67a15b34-ff96-41eb-830e-90b46f3addcb	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3840ac4058e70005282ba105b8d919f2d878837345f3392f2f49d018619dd62a	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 22:15:42.612079+00	f	\N	2026-01-30 22:15:42.558088+00
d5a15377-6012-4998-b8b1-c9373076fc2c	3f3a3a39-d867-45a8-b901-74a7e27c95f3	d25b683a25873fda1cc4a43eae0e54f4b7d845b1f5d1dec6d2f8b2e2a201a2c1	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 22:20:39.593028+00	f	\N	2026-01-30 22:20:39.545803+00
0f2ddc2f-1e74-4c30-b1ec-e3c965a9f121	3f3a3a39-d867-45a8-b901-74a7e27c95f3	7af5fb8b2493afc8d4fe3ae600050c6277c0513b01d65b2e18be26873f44b480	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-06 22:26:14.857282+00	f	\N	2026-01-30 22:26:14.781351+00
ccfbe2a1-05ee-44e1-8a53-fa9aa29608be	3f3a3a39-d867-45a8-b901-74a7e27c95f3	d1c87d57bed826d3040bc5a745ac69f27bf40c62359a77265e298a756ced81dd	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 01:42:26.623811+00	f	\N	2026-01-31 01:42:26.557388+00
fd37efe6-43cf-49bf-a899-a8c3d2bcabea	3f3a3a39-d867-45a8-b901-74a7e27c95f3	6ac01dfb4f51425c9b84d926eb6002e628c912b53b02d2b57e17f6f786014e59	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 01:52:08.66821+00	f	\N	2026-01-31 01:52:08.624926+00
64739575-d918-4738-8220-d47c818cbde8	3f3a3a39-d867-45a8-b901-74a7e27c95f3	79894130225527c6570cc60487c49a2775589269e1acea169a0934dbd8ea4c55	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 03:47:51.667253+00	f	\N	2026-01-31 03:47:51.614393+00
0e5f56c3-2b28-4883-b632-2c6a9fb1a18f	3f3a3a39-d867-45a8-b901-74a7e27c95f3	c7d89a62badaf7015f1d1342f7ed0771a99a46be8da4d149dbaa513aa2e45395	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 03:53:07.984699+00	f	\N	2026-01-31 03:53:07.945433+00
d864bfd4-bb54-473f-a2ca-42498a6b35fc	3f3a3a39-d867-45a8-b901-74a7e27c95f3	92dc50f28079c1b9a5b56abf93b46a730e744de27f9208df75ff3d2191cc1acd	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 03:58:02.779298+00	f	\N	2026-01-31 03:58:02.760156+00
ba7ee9bf-63d4-4256-90ff-8dc1baaebb25	3f3a3a39-d867-45a8-b901-74a7e27c95f3	0336a9d552a1d5aa243f6c81568b28df7089e7bbfcf903dc790bc1b2fdbf5edc	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 04:12:25.721845+00	f	\N	2026-01-31 04:12:25.713551+00
66123ba7-94b3-4039-9ce7-fa577e2e3ee9	3f3a3a39-d867-45a8-b901-74a7e27c95f3	ec2b35a4091d6e7a7ecbb3ca9c940b98b806c1f4ce64c0c7b77446fc48a61f72	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 04:19:55.050664+00	f	\N	2026-01-31 04:19:54.981612+00
17c819b7-1cfa-4b94-9434-c1d01e6160ab	3f3a3a39-d867-45a8-b901-74a7e27c95f3	96dc203578e4f814385725749b5f05da45c9eb38b9e180fea1c82f5b070002dc	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 04:20:18.95127+00	f	\N	2026-01-31 04:20:18.946054+00
3d047588-6fab-46c5-b7cf-8c844cb363d2	3f3a3a39-d867-45a8-b901-74a7e27c95f3	4f9955d18e781d6038831990b63a515e3c22ef5f83d0555b8eaae52e2b4bc66b	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 04:27:45.843298+00	f	\N	2026-01-31 04:27:45.825025+00
bd410177-3e08-4eaf-b09c-bd95a68117c1	3f3a3a39-d867-45a8-b901-74a7e27c95f3	d82865a23846ce1b8f5e3c1e061adef4e3aca1fa1ba07bb8d8171a6fd33b85cc	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 05:01:55.954746+00	f	\N	2026-01-31 05:01:55.936507+00
efeb2594-c39d-444e-9f67-74bce4881560	3f3a3a39-d867-45a8-b901-74a7e27c95f3	f9692532f8ee64e99cd7c2a9c1ae9526a09d7457046294da302bf8449e304843	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 05:26:59.813353+00	f	\N	2026-01-31 05:26:59.799973+00
b0c19d53-8d20-482b-b0e5-44ef0b805133	3f3a3a39-d867-45a8-b901-74a7e27c95f3	7c001b6b660469740c33c9859ad396269a1494fb5592e8595308413e47f206b7	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 05:31:50.443167+00	f	\N	2026-01-31 05:31:50.434528+00
72de4532-13a5-4046-b6fe-26d3f28b709d	3f3a3a39-d867-45a8-b901-74a7e27c95f3	1241b1b6c01ac8a4ad05963828b0f9197b95be969c3b3fab524b80b9e7d63acb	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 05:43:52.499219+00	f	\N	2026-01-31 05:43:52.493231+00
7886d9b0-1f86-4aaf-8492-8c320163ff43	3f3a3a39-d867-45a8-b901-74a7e27c95f3	0eae3ca61c41b0a254c565151b68753c9b18866120bf0dc7d67b1262b76274f8	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 05:48:32.440768+00	f	\N	2026-01-31 05:48:32.389172+00
57fd556b-bec2-4eeb-979e-80d0effc2f32	3f3a3a39-d867-45a8-b901-74a7e27c95f3	4f7252089fe14321dd79be88b95fb98496eb75577bbda951da9c24be76ddfc4d	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 05:54:39.02+00	f	\N	2026-01-31 05:54:39.005908+00
0ba198b4-427c-45c7-a26e-87d5b2fc20f7	3f3a3a39-d867-45a8-b901-74a7e27c95f3	5f0d7d1d98b9c9cb7be756c4499006fe6f6a4bc18ed948abf83d3f5eaba72808	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 05:59:21.695069+00	f	\N	2026-01-31 05:59:21.67782+00
98268784-3491-44db-98ac-91f34d70adbc	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3619c895393a0e8fa1dd4489ccff71650d6d76c359a826772012868cbbe8ad12	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 06:23:37.021644+00	f	\N	2026-01-31 06:23:36.910034+00
a2346b92-2855-4dc5-b034-e687eb383397	3f3a3a39-d867-45a8-b901-74a7e27c95f3	72ce87c306cdd2d7f4b3ec973fdab560d059a4a184df8b87a5589f2f42775010	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 06:26:16.722792+00	f	\N	2026-01-31 06:26:16.716252+00
7f4fa698-9978-4714-8e6e-9749a9ad8ca7	3f3a3a39-d867-45a8-b901-74a7e27c95f3	120671a0b1e8d4f63ca98b6d81900a67790656fb3859e9d6abea04bbf7a66b9f	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 06:28:41.913029+00	f	\N	2026-01-31 06:28:41.906969+00
f7b3617c-f730-45c7-939b-48b9cb277e40	3f3a3a39-d867-45a8-b901-74a7e27c95f3	ebacb7f473adba53bc947746c7b146b5cdab9582a695007270618e6e6c7d19ef	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 06:33:41.396984+00	f	\N	2026-01-31 06:33:41.374376+00
771b660a-2d3c-4a5c-a6f9-28dc7075fe03	3f3a3a39-d867-45a8-b901-74a7e27c95f3	d377d6ac6cfb68a5c72120ef8db02f5157c76848596aa1d701bf2c5d9d7d2a33	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 06:46:36.733472+00	f	\N	2026-01-31 06:46:36.715087+00
3ccb720d-17a8-47b8-9406-596e3103322d	3f3a3a39-d867-45a8-b901-74a7e27c95f3	f0bcaecc06919a2a277e03b9a8e77d607106874773d41e84c991b29de467da3b	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 06:52:50.881481+00	f	\N	2026-01-31 06:52:50.866426+00
db67e015-cea6-4a0d-b276-16ad3e01df60	3f3a3a39-d867-45a8-b901-74a7e27c95f3	1731fcd0eb79b943f3cab9aa391d55661e59a4b698c9407951fb7577bc7f3695	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 07:01:45.680342+00	f	\N	2026-01-31 07:01:45.653978+00
094f9be4-1b98-4680-a60c-9f23e51e1dcd	3f3a3a39-d867-45a8-b901-74a7e27c95f3	eb2ee5eb2424a67baf9eca2ec1636f69c462683f892ad1c0e0d699a5f391e06d	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 07:21:05.955989+00	f	\N	2026-01-31 07:21:05.942553+00
f8d9855d-ee7b-4ca1-ba03-acf5237d3cf3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	caff8d42da697a60569f20bd006b2039ae23ff809fbae43ebcf97d07a2264577	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 07:25:42.052877+00	f	\N	2026-01-31 07:25:42.047403+00
6270f731-af8c-4f27-971c-caf7e66a7e52	3f3a3a39-d867-45a8-b901-74a7e27c95f3	8bf0834d10f1e44d414362105adb419ad7865d0f0d07ad4ac74dbd7bb39a6c45	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 07:56:52.315628+00	f	\N	2026-01-31 07:56:52.305108+00
62f7a90f-ae97-4c48-bc77-108306c21cda	3f3a3a39-d867-45a8-b901-74a7e27c95f3	61c7523b64b4027dd94089709565821ea92262dfa895614911e606fb5d46b393	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 09:18:37.841946+00	f	\N	2026-01-31 09:18:37.814189+00
ed8170bf-f1f3-440d-8fe5-e69ae616a684	3f3a3a39-d867-45a8-b901-74a7e27c95f3	7f9864d6ba1d63fe20bcbc29f0954505a47d57900db293e4c57898cae14e3066	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 09:22:09.210529+00	f	\N	2026-01-31 09:22:09.183055+00
5ea96132-0d10-4635-9f5e-ec70a1f8fc8e	3f3a3a39-d867-45a8-b901-74a7e27c95f3	306739433ca25c992d6ef08aed23c95ea961b36c96d3f3a2e5cc0fb7dc218e23	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 09:33:29.744105+00	f	\N	2026-01-31 09:33:29.693115+00
0425b549-5912-4e88-a62c-1188930e9d04	3f3a3a39-d867-45a8-b901-74a7e27c95f3	491317b16bbbd82fb6a229e23faf3653c2271326c66cc77c6b2d9d839bef6fc5	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 09:36:30.397979+00	f	\N	2026-01-31 09:36:30.380191+00
3022eb48-e510-4820-8039-49e296504787	3f3a3a39-d867-45a8-b901-74a7e27c95f3	8c2c5f7fa93cef5a77df018f40e56e964934e3fad064230ab9b15fb1fc3e1c1d	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 09:39:17.259305+00	f	\N	2026-01-31 09:39:17.237714+00
f375e018-f811-4f92-ba68-9dba153e0fc2	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3ae1368b4f32fc2d91e65bbbacfbaa10b2038c96252a7a91bd6296b4546b03f2	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-07 11:35:39.096729+00	f	\N	2026-01-31 11:35:39.065293+00
7d1d0c70-9c8b-4fc4-bb28-2dcde73c159d	3f3a3a39-d867-45a8-b901-74a7e27c95f3	f754955b96ce3fe9d8eb7de312acd8703a1006bba9a8d6c7824c2e236a10e2aa	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-08 05:39:30.954906+00	f	\N	2026-02-01 05:39:30.910202+00
a5d1b439-28b0-48b9-8959-bae1f8d82899	3f3a3a39-d867-45a8-b901-74a7e27c95f3	bdb78801b90796dbace20bdb7d8827d788c0d5e0f1dd5ac0b7d13d2961799d7e	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-08 05:52:51.729906+00	f	\N	2026-02-01 05:52:51.697728+00
59111667-92aa-4b55-a3eb-88b6ab455e55	3f3a3a39-d867-45a8-b901-74a7e27c95f3	a30f7f25ccb9d98dc3e2bcf8774c25068d6ab9ecfe5413ce9a8df6ebde043b29	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-08 06:39:08.783825+00	f	\N	2026-02-01 06:39:08.75626+00
bc74b0b4-d382-4e6c-9763-61a6ffc85b15	3f3a3a39-d867-45a8-b901-74a7e27c95f3	345c0f3794a6f721bbf01474fbf43eb3004e475f4e99cbca9f698a1a63766780	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-08 06:47:22.727088+00	f	\N	2026-02-01 06:47:22.696701+00
cf13d591-3024-4fd6-b703-6c37373f3871	bfdafb1c-258c-487a-84a9-8df88d6f7efd	6231d4ca554988f559be2351e642d8e7f29456c90b95aa4569bd381b0ce215c3	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:04:58.308773+00	f	\N	2026-02-01 10:04:58.292605+00
88b9a2d6-45ed-4a32-a2b4-de0bd6719d0f	3be02ab8-a88f-4a03-b781-3fffa07e5096	ae8133d3112f3c31514d513815607b68abd46c58d88be672fc2f54a0990c137a	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:04:58.568865+00	f	\N	2026-02-01 10:04:58.5682+00
c52f0215-7ad0-4ed8-bd63-9fe5ab554328	a7c620dc-005f-41e4-a09c-84a578fdff32	1b2005714d3677ba84342b2a652569856f8ab709c10d056a5ca2d348298dfcb3	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:06:48.262619+00	f	\N	2026-02-01 10:06:48.262059+00
1bc45454-8271-458b-bfee-995f3045d1b2	ea72b36b-fe10-483e-acca-7274bdab7600	bfbf5d251706789c55cff051678a84ef90f90a4637e423239414abec4a6da385	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:06:48.513535+00	f	\N	2026-02-01 10:06:48.513079+00
cc580e7c-2fa6-40fb-ab77-1354bda60d0d	eb63636b-e512-4cd7-9296-f0d38d62f74d	218e6778a3eec7c97e532a33d295627e62d3c89e0b1cd69e3a728d31e38c909b	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:10:06.924091+00	f	\N	2026-02-01 10:10:06.923544+00
313a2399-5930-4612-9556-85743f53e940	fc777437-f8d9-4e04-bc0a-011507805218	88a58d7fd35b5f0ecbb524effe5cbca2923c027855e2d330f6b179fb77573d01	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:10:07.259961+00	f	\N	2026-02-01 10:10:07.259321+00
d42ac4d6-1b3b-4a08-a5dd-12a24cd58ca8	26872c85-6000-4eec-baab-a1a4b8a27258	254681d05dd955833f967b82b9c3f5f6d2f5349c05eece094498398a234d1907	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:30:00.182119+00	f	\N	2026-02-01 10:30:00.181529+00
76ec5f21-8905-4eb7-8534-48dcf6e571b7	d24c619c-0783-4510-949c-49445cea0202	4c3d16c8a1e5748c6ed5daf19a61ddae3ac4b8f73a9caf9a8776b002754c76c8	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:30:00.49175+00	f	\N	2026-02-01 10:30:00.491169+00
418c9aa2-d4d5-4822-86be-69d14c4ecc0e	aec76aa4-0bf4-40bb-9307-de54a5d205a5	255f9dfb8ef94120ec05b35c68442bf84a0d3ffa868239acef51ac6002649533	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:31:20.803527+00	f	\N	2026-02-01 10:31:20.80286+00
dd85180c-424b-4520-a2c0-dddd14dd2f90	5b010aef-d0b8-40cc-bc0e-6b6c133cac49	acbeca51dac8b8954ce8192901694ede3c2b0f6ec2b1f4021f85da519075c10c	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:31:21.053861+00	f	\N	2026-02-01 10:31:21.053317+00
c78f4fc8-91dc-4534-b297-58ec008ace72	ee6157bd-176f-4f75-8cea-64adb841884f	2d611bca974fc054f226086c6b06ba80b1fa72291768f3cdb8e6a60beb016819	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:32:48.899508+00	f	\N	2026-02-01 10:32:48.898832+00
46a32cbd-1487-4873-b6cc-3cc33b9e78fd	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c	9bb80102e14d65a5de7790036a81158b0c214793c196dd0ad6178a6f58af5b54	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:32:49.15058+00	f	\N	2026-02-01 10:32:49.150068+00
64466c61-39ea-4be3-9a86-e034a3cad8f2	ee193894-167a-4355-8899-7c19ba395e9f	aceed9cd06fd8ebc2de3a7ff6134ae04b7d15ad9d2d0b880b388fb596c00aa6b	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:33:09.603316+00	f	\N	2026-02-01 10:33:09.602833+00
4ee4bf9d-b08e-472a-bc05-e61d98ee2dca	bf660c8b-3818-4cf7-85f1-3071c0a7943c	47968060f65c3d52da2016cdc1aefbc62ef35f2c782942d9fd82e158cb69a4b4	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:33:09.855044+00	f	\N	2026-02-01 10:33:09.854334+00
c4583446-c8f6-4119-9d8b-e6dc704b199c	3c1aab18-4eb2-4ab2-bcca-993c37e7fab1	2659a5e528258463693864dd1d2fedbf5288adbd48fb577c35cc4f5a882f4262	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:33:31.640683+00	f	\N	2026-02-01 10:33:31.640065+00
f22a4e40-6663-4351-95be-d8c44268a8a5	c7a092a7-d354-498d-b23a-d4802d99ccb4	2939065d04763e6284561f28743e2eee263817a9a000e957b8186c292aff5b9f	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:33:31.890358+00	f	\N	2026-02-01 10:33:31.889845+00
dee1eb8a-bc6a-420f-9861-7c2ac55032e0	3e72bdbc-89a7-4009-a93e-bba6fec86530	593d3bfd84d19a0b9ae32481cdabde9a8d2d5457b8513c360626358d1a0dc463	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:34:04.029508+00	f	\N	2026-02-01 10:34:04.028984+00
60f9bde1-2540-4c0d-b617-91183de3b895	2199f334-fccd-46ff-b45c-2cd81aadeca2	cf0e90840519b277e3a98a9c7e30c50e370a7cd70caf32b35b04daaa2675169d	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:34:04.281088+00	f	\N	2026-02-01 10:34:04.280542+00
c93ec729-8406-443f-b2d1-c39bd5a97089	c5e779fa-7e25-4b84-b410-a55bd0c9e219	9d16579f1a7854aff091b4ccfffe8aae9c5d21af526567561dc9538eeee63266	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:34:21.574598+00	f	\N	2026-02-01 10:34:21.573973+00
b2b863db-9b77-4a54-a355-b662c9ff9384	b46ab366-7dcb-4ee5-a558-dc328db04159	c7b73c8eba3c45a22f36d60b57fad47f763d3a7143b74c62740c7e1367df04bf	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:34:21.830175+00	f	\N	2026-02-01 10:34:21.829517+00
2a40a7ab-7aed-4446-9b77-b3b48acb1494	b8cf8398-0dff-42c3-99ab-aaa2bcf646e6	e5b8f7ffb0cdefdf2f1e0ee2d19585bda7b7b487d97b971d9758ac5c7c5d9f19	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:34:42.165172+00	f	\N	2026-02-01 10:34:42.164595+00
9f1eb05b-cdac-437b-b6ec-236c9ce50d45	979cfcfd-a872-40df-8380-dbe81f29e7a5	c07a5382662f35edcb4439e5b4fce8e12bc8c5e5b2ed0f1f9ec19dea3c566181	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:34:42.414986+00	f	\N	2026-02-01 10:34:42.414306+00
081cf2a9-2299-4c2e-8922-0b688e7999ec	a031994b-5afb-4fa2-9d8a-8004d7e8c9a3	05a1b3136a9893865583b0ac46772cebe9e7d7e5dc003deb6bf7d55a292202b6	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:35:07.511744+00	f	\N	2026-02-01 10:35:07.511181+00
2ef14d4e-a8dc-4f79-9cba-5ffebf7dd28b	810cc398-af79-4d96-9eee-af0f1bbf8683	65f32c4f2ab52aa64a888a9fc25d0381b25ca1368189d3958be084bed8f1e363	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:35:07.762031+00	f	\N	2026-02-01 10:35:07.761474+00
e89ea836-f9e8-485d-b12d-ddc27282694c	2e6f6fed-9d3d-4b85-87d0-a134932d0dd7	085a9f673d120982db14c3d2b67353e39dae9e38b33b015493c809fcb234dd00	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:35:47.677548+00	f	\N	2026-02-01 10:35:47.677127+00
cb4c5335-05a0-433c-b565-c439786d247e	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	370d0eb547c9ecb0c442966208c799c4f3cae1955b307976c4563493bdcd8647	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:35:47.927374+00	f	\N	2026-02-01 10:35:47.926797+00
16f31a62-feec-4050-b4dc-b7bc49d93799	d77da629-52f1-46c9-9118-dbe7fe92c333	637b0165ec10108e4bf2d973408e60a79caa95700b51b6eebf6c02d50096b8a9	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:36:43.546011+00	f	\N	2026-02-01 10:36:43.541284+00
8242709f-fbdc-45e0-a2f4-52a24db45b7f	ef5984b4-54b6-47cf-a9bb-ca02cadc0180	6238af4586111ef695929c82666371cf403fbb7e9ba64406f7abf5096fe8b5fc	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:36:43.80071+00	f	\N	2026-02-01 10:36:43.800124+00
65db8bcb-fc1d-4749-9827-cbc23c142164	66d51b1b-c21b-4f8c-99ba-c2854ceeab97	e1b0d1c231ea8b3ef1e4ae7c8c7dd175fa03dbdecd226dc1b180292d5aa1fd5c	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:37:04.760547+00	f	\N	2026-02-01 10:37:04.760078+00
b383058c-223e-4caa-af33-602b20125ca9	70904796-fe39-4007-b892-a8aa3c8e0e8f	e65d78a37f83dbcb63e7b1faa417e65d405211246ef2cc0d337ba69c51c6c693	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:37:05.009038+00	f	\N	2026-02-01 10:37:05.008488+00
3957b525-932f-401c-ad5c-4cbbeb8a916e	3f82b4a7-b270-4d68-9e02-e9068eaa668f	74e08e02399eacbf704a3555aa166d5e62e01e21b659bfb38604a8d5fc6c6f5e	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:38:12.920036+00	f	\N	2026-02-01 10:38:12.919541+00
d698aac0-b20c-43c0-b00d-a85bfb2297b0	1ce1ba48-b899-4217-8fd9-2124dd4765c6	83db09061da061f7fc794d16692459eed357d18f7108bafb4597b3110e4719f2	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:38:13.16659+00	f	\N	2026-02-01 10:38:13.166168+00
fd71bf16-9e20-4362-a392-3ff36b2b1a24	d5104c40-d4cc-47ac-a700-0c7414c1b26a	f8c75f69a53f848124b83befc5233c29e07fc294a629746f2e3b989719b1d0f7	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:38:58.710638+00	f	\N	2026-02-01 10:38:58.708576+00
68524530-c253-4135-970d-7322b298a406	05e362b8-0b73-44ed-bded-ef4e0a40dd47	b7400af41c0c43cfdd02b699d54f5c79ece41e75ec8b0e16394546ab7ffc8b3f	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 10:38:58.964428+00	f	\N	2026-02-01 10:38:58.963942+00
d36f3c99-02f4-40d0-a209-e7ba94e0d99d	fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1	f9337233c21cb9ddcd42019b32a2292e5e8da38d4b030db159318a050bbc51c9	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 11:01:39.245576+00	f	\N	2026-02-01 11:01:39.237942+00
7ab5f608-0e6c-407f-944a-c61b89579130	b9c25548-e5ba-4200-9dc9-1ba98f332540	b716026d4ea80c362d94542ca6c6eb929298188138c298d11414e0dff174df46	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 11:01:39.49063+00	f	\N	2026-02-01 11:01:39.490121+00
d425d893-04e5-4e21-b9c5-df109eedbcd9	1a8f4448-290b-48ff-9f17-2d76e841a1f3	4f9923b1cb3bcca6ada6d8ea99ae559301b21d63a169b6ded974c25ee3590c4f	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 11:06:38.202069+00	f	\N	2026-02-01 11:06:38.201196+00
7896ccc4-7b9a-48b4-8484-c5d8314a6373	a30a9865-926a-4d26-af0d-42e44657b429	9d3bf5c7f24399c68590f4154065de77574335ee85346aa17f9961f6df046bd2	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-08 11:06:38.526593+00	f	\N	2026-02-01 11:06:38.525905+00
d3e8f133-86e6-4186-963f-a050a58b9cdc	3f3a3a39-d867-45a8-b901-74a7e27c95f3	b53e08f30ec7e62df4f30304d9861fea8091c499edef128b9c102870c91eeb9a	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-08 19:38:38.836391+00	f	\N	2026-02-01 19:38:38.784894+00
3d42e779-f2e5-4d7b-b45d-494457488bdf	3f3a3a39-d867-45a8-b901-74a7e27c95f3	4cb00a353e9b3debe41311c1519c7c7a49b063d11d4f5047f0a4fbbfe229a66e	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-09 06:18:52.955934+00	f	\N	2026-02-02 06:18:52.915849+00
0d1045f8-51ad-4166-b2e6-bb8c817386c7	3f3a3a39-d867-45a8-b901-74a7e27c95f3	6ce799eeee2148434ef7e628976585d614f00d9ac05f07214747b7109d20d70e	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-09 11:01:10.381769+00	f	\N	2026-02-02 11:01:10.354604+00
d23191ee-3eb0-4c18-bebe-976c1a9bbaf7	3f3a3a39-d867-45a8-b901-74a7e27c95f3	dab98cb2563b95e2300a65c773282b25949b188ff29918cf73fbd8499b76a5a5	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 12:36:53.698249+00	f	\N	2026-02-03 12:36:53.645229+00
8b360b7a-2598-4c13-ad63-c9b2f1bb3f58	3f3a3a39-d867-45a8-b901-74a7e27c95f3	dad0fbaff4d34cb6e7ae09ae141bd33d583a17c35315c5f766a5713218c8d184	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 12:42:30.518123+00	f	\N	2026-02-03 12:42:30.431019+00
aaca7304-0384-41d5-a33a-575eb3d812cd	3f3a3a39-d867-45a8-b901-74a7e27c95f3	8202ae4d1e5b9c96646aa46d049df8a45881d92ebd5e10a6c76c2bc7e5600cc2	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 13:39:10.661923+00	f	\N	2026-02-03 13:39:10.638263+00
e81ecec4-ef5a-4baa-a56b-0b76bdb34222	7ebef8e8-4a6d-4420-ac3a-e01a33f6c975	18c28377475bc559fec65d63b20f1e985d1e6b7990636cc9af94b5165cecb107	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 13:56:14.206812+00	f	\N	2026-02-03 13:56:14.203731+00
3f9c3953-ea85-4a74-b806-c88eed549d55	3f3a3a39-d867-45a8-b901-74a7e27c95f3	ecf694eba3a25f28b17552bd22ef99a7b50fd969f0c09239d29817a048e8f1a8	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 13:57:31.926013+00	f	\N	2026-02-03 13:57:31.919007+00
ea53d309-e1d0-4a1b-b20f-25543513bfe0	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3de335ae25fd5c815083a1488951aa00f0d6c87d25241b9ad84c62b17b544508	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 14:05:01.245206+00	f	\N	2026-02-03 14:05:01.234344+00
455e610e-4a65-4048-beec-dff84eb91c01	3f3a3a39-d867-45a8-b901-74a7e27c95f3	a29496e68212c162e9394ea9765131de12a4831b7e5ef06f219d88fa928c3f21	{"ip_address": "172.18.0.1", "user_agent": "curl/8.12.1"}	2026-02-10 14:21:37.552585+00	f	\N	2026-02-03 14:21:37.534983+00
c5b654dd-148d-4ac6-bbbf-285505bd4ab1	3f3a3a39-d867-45a8-b901-74a7e27c95f3	503ea53a9c565ef29ef9f7ae523e199edff8cddea6c503ba5689706c32cb2623	{"ip_address": "172.18.0.1", "user_agent": "curl/8.12.1"}	2026-02-10 14:21:53.555504+00	f	\N	2026-02-03 14:21:53.551211+00
2346d12a-60a4-4679-8e00-c3cfe4e2dd79	3f3a3a39-d867-45a8-b901-74a7e27c95f3	34d656798d2592551fef08192b2d0a4029a9cddfa6b6aadd6f5eee5a3e8b2ede	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 15:24:14.234389+00	f	\N	2026-02-03 15:24:14.213329+00
37d82790-bfb0-4706-90e4-8acdf7dbb5d9	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3bda7d3115c7174dad5825e07358ac895bfcda8c734569aa878bd8dc907ece1c	{"ip_address": "172.18.0.1", "user_agent": "curl/8.12.1"}	2026-02-10 15:37:33.587201+00	f	\N	2026-02-03 15:37:33.575001+00
91d14e64-3dc8-4f33-a3fc-94dcbfa1542d	3f3a3a39-d867-45a8-b901-74a7e27c95f3	ab659d0a7821ade39155a9da7383ed493ba43fea84ab68ba03b123c613c47a47	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 15:43:59.38262+00	f	\N	2026-02-03 15:43:59.353313+00
248a5975-baea-4507-b06b-2dc0370d58ea	3f3a3a39-d867-45a8-b901-74a7e27c95f3	ab3b9fb6b559d9acadaea8e372476ff2f91a2618201e1fa2f7e21dd2b371cdd6	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 16:04:49.66952+00	f	\N	2026-02-03 16:04:49.634904+00
1fb1fea2-0a6f-408c-a368-f69cfc3f1ecb	3f3a3a39-d867-45a8-b901-74a7e27c95f3	0caf88da3a7b48e2a1eadf30cd36734faee1225f3233b3aa4438c1b3a6d226ab	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 16:12:42.120136+00	f	\N	2026-02-03 16:12:42.08336+00
22a213a8-92f3-491a-9ade-f6e0ba265a52	3f3a3a39-d867-45a8-b901-74a7e27c95f3	900e956affcc168e04fec2684989842ba8e450eea5416313b11ff8f4ba3d9383	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 16:20:50.806795+00	f	\N	2026-02-03 16:20:50.777113+00
70e11be0-17c4-4c78-a769-4c9f1dbf3e4c	3f3a3a39-d867-45a8-b901-74a7e27c95f3	4495e6985ce0cd383221491af2472b841a558b23e38b9498782c4032afe78a01	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 16:25:11.551598+00	f	\N	2026-02-03 16:25:11.513348+00
0c7bc6ea-458c-42f8-a012-81109d91b963	3f3a3a39-d867-45a8-b901-74a7e27c95f3	83e01fdf4588d742f79dc27908d6efaaffc4752e9709814a3f31b96133ee2173	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-10 16:53:54.410114+00	f	\N	2026-02-03 16:53:54.382044+00
246938fb-bc6c-4d11-89b4-ded4c736b8f6	3f3a3a39-d867-45a8-b901-74a7e27c95f3	c97909df6b8583632632b4a90b590d882ce2831a1a00100a680fc52e938ba91c	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-11 08:49:57.932688+00	f	\N	2026-02-04 08:49:57.891833+00
5567b0c9-5c92-4b61-b72a-6c1ec00f0f92	3f3a3a39-d867-45a8-b901-74a7e27c95f3	6c927cd4a90b006db10c2d093958b2de2525daaf1e747a8dc4ea634b610ab766	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-11 18:16:28.329538+00	f	\N	2026-02-04 18:16:28.298206+00
74e94e19-52e6-4aca-8d99-4a86e8ffa1c0	3f3a3a39-d867-45a8-b901-74a7e27c95f3	1b7101ed85bfc0fe2218461a358b5309d5f7423ce59fd92162fa93ca245638e6	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-11 18:30:48.31047+00	f	\N	2026-02-04 18:30:48.29904+00
17f811b4-75d1-4ad4-8f28-e20b8ee9b5cd	3f3a3a39-d867-45a8-b901-74a7e27c95f3	b8a15166c1e54c7d8ca8af49c173d6bb30c67fc47f3edf429adc5e11c7c38143	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-11 18:40:50.580711+00	f	\N	2026-02-04 18:40:50.566777+00
b18767e9-6ddd-4b6a-8f27-7c22d703eaf1	3f3a3a39-d867-45a8-b901-74a7e27c95f3	dbcffffe872aba4e3e78fb5f6e36a5d9f858bd627203deeaa43760fe9021a790	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-11 18:53:43.219423+00	f	\N	2026-02-04 18:53:43.20702+00
329fa884-897e-41b8-bdd3-af222e5a0438	3f3a3a39-d867-45a8-b901-74a7e27c95f3	f0957beab176d1e7c805b615bc373c1b6b5f413d5398716ae23148da6eeab6cf	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-11 19:01:45.123795+00	f	\N	2026-02-04 19:01:45.115912+00
76e9bbbe-ba6d-4b9e-848e-7bf104841015	3f3a3a39-d867-45a8-b901-74a7e27c95f3	90b913ccc484c2158d954d56259ce5e81f25d8519206032a82ff7a4b7dcf0d11	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-11 19:03:06.298408+00	f	\N	2026-02-04 19:03:06.294609+00
af5a2ac9-080b-4fde-802f-5b401806fea9	3f3a3a39-d867-45a8-b901-74a7e27c95f3	117d580b7a6a5c59c660c9bd6afabf005e4db1212be4cc8d6ea5142074a22ac7	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-11 19:04:39.595031+00	f	\N	2026-02-04 19:04:39.59019+00
64659f20-6f92-4cf4-a123-91bdd3cc70ac	3f3a3a39-d867-45a8-b901-74a7e27c95f3	b4b6ca17e1d338db816989d68f1616e1d57f958d6719f55739cea8f3cbf4aa6a	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-12 18:47:34.367185+00	f	\N	2026-02-05 18:47:34.344265+00
702c2231-4685-4bb4-a367-22e7b2a6b888	3f3a3a39-d867-45a8-b901-74a7e27c95f3	c74db20039b2a0d4519bff4f012752c992cbc5dbeb64c55f0ea5aa6222636286	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-12 19:04:58.553183+00	f	\N	2026-02-05 19:04:58.542265+00
6bed8984-2fb7-4808-ba81-17ab27110059	3f3a3a39-d867-45a8-b901-74a7e27c95f3	0039d95d249bf5366c21773954920a3cb1f9e153e8befbc180fba6dbb2546763	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-12 19:21:26.677619+00	f	\N	2026-02-05 19:21:26.642426+00
cf9c53a6-d2f8-41d3-8393-359b09dd6c47	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2b2e144bd706ad5b199775725a5db204b9bc1db3e7381de77644852b9b260f2c	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-12 19:25:12.793277+00	f	\N	2026-02-05 19:25:12.790149+00
7c4f2510-017c-4634-9745-83822ef5547c	3f3a3a39-d867-45a8-b901-74a7e27c95f3	40d75f4a53cd558647c11137fa46499a8e6c2fb5eddc3eeef6c8b8215aed514c	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-12 19:58:47.580446+00	f	\N	2026-02-05 19:58:47.541291+00
d7b73a3f-0c0a-47a2-a706-6be7cab65191	3f3a3a39-d867-45a8-b901-74a7e27c95f3	b839676c1f5a82ec3dad2550e7a246ea9aa5053421a8c2bdf2a2c7ee4f9d7f80	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-12 20:00:41.403359+00	f	\N	2026-02-05 20:00:41.396087+00
bc7c6f20-6f1f-43b9-9bed-07e4aa4c0c93	3f3a3a39-d867-45a8-b901-74a7e27c95f3	bbdbe7be196dcc73a75254e0f37e45d07d71cbbd1fc490b451248c8e3f0fe297	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-12 20:02:32.621751+00	f	\N	2026-02-05 20:02:32.543608+00
12ca00ef-6aa6-4874-93f0-f1dd3b1c5904	3f3a3a39-d867-45a8-b901-74a7e27c95f3	1861a671b0e398977d754c0a8a213829a291630dca8daf1d910e6f6eaeaa5f40	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-12 20:09:41.762312+00	f	\N	2026-02-05 20:09:41.703312+00
40507a5a-835d-4e1a-a4b3-f2670efffb6b	3f3a3a39-d867-45a8-b901-74a7e27c95f3	4a61b9e8bf934c26958a81ccf85bf3705c5433653b3c6b8a22b8a1501b0aef24	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-12 20:42:42.700172+00	f	\N	2026-02-05 20:42:42.630319+00
b6059171-0082-45dc-8d7c-82ab2b818b4c	3f3a3a39-d867-45a8-b901-74a7e27c95f3	e0c96c92e973d378389188d40873c5eed729173701c8ba346fdc3a4dc26e090b	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-12 20:56:02.127626+00	f	\N	2026-02-05 20:56:02.0389+00
24aee6ee-dc28-4d85-a44d-a93ec1d68377	43a76c7a-3acb-40a9-8c3c-9e0235d9a13f	33c81c453eecbbc1b92fc7744329296219f75ff3e42988646e4fe6d3a7844195	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:25:33.088166+00	f	\N	2026-02-05 21:25:33.06951+00
af93cd19-5231-4f30-951b-fc7f271b28b0	5526632a-9523-4219-b2ca-708559772fb8	85a2957e347d04afaf107d7088ae1790e671ba0c218ccb5ad89f32d07fe20c24	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:25:33.298757+00	f	\N	2026-02-05 21:25:33.298179+00
963ce423-1740-49f0-903a-0e445e5c005d	dcc8f7e0-c4a6-4f72-b21e-78331c825d3e	3cfe7c75b3213b54371d2f528dad69c899a3457672980dbbb04a68d9e2ef2f3c	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:28:19.575837+00	f	\N	2026-02-05 21:28:19.567297+00
6d1c4802-2274-461c-8fa3-6b398231710d	5847755d-a7ef-4f01-ad83-b96116cc5b06	f2c35c58db785f3b894f2b1d622e8ea89aea7efdbcc10eaf79b2802391ee7baa	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:28:19.854298+00	f	\N	2026-02-05 21:28:19.853699+00
2b73aa40-8a7a-4d1d-8dfb-fb08c2ad8793	274bca62-6a26-40f4-ab29-482816286c94	3fb19ecc493282bbe5e0d421f6ecc8bfe9d876a4b1351950460743e08320695e	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:30:53.157779+00	f	\N	2026-02-05 21:30:53.157132+00
9edd39c8-ff5d-4a41-a57b-0ef4e2d15236	3ca9cf6b-c372-4530-bc35-3440c68f858f	dbb494cc243e1c3d4b650c87b70fb29f832bc5a7076419e4d89f5d92a0a2c45c	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:30:53.377851+00	f	\N	2026-02-05 21:30:53.37739+00
ae194ff9-2dec-42ac-adaf-af7da86b384f	53126f3a-94da-4363-b20d-61a85c99574a	8c2243752978c712d5daf6adbca9ba1d3187638e68bc261356002942bb880931	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:31:42.237027+00	f	\N	2026-02-05 21:31:42.23624+00
651f1051-009e-4e6d-be22-5beb0ba13743	09b95fab-3a52-4e54-8957-76e81ebf668a	91d60fe7611af1dfa84c8d5db4fc21fd940e43313f531ed94c06226eaaa3aae3	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:31:42.424679+00	f	\N	2026-02-05 21:31:42.424299+00
30cf526c-2917-44fc-a158-a0aee6677da8	1214c599-c7c2-490b-a895-e45b985b027b	26d5943ef4465cce6d867ebb91ceeb84f7c5266400141e4aedf5d188875828da	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:33:44.606678+00	f	\N	2026-02-05 21:33:44.603907+00
467dd5fe-e81f-4b01-9028-5f157ac3599e	39219340-21cb-4a88-a939-93baf1a0e840	c3ae47c0fe8b733a4dea7517ffe8300affe9903f2ed80a69494ca0b928843bd3	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:33:44.811153+00	f	\N	2026-02-05 21:33:44.810639+00
cf69c6df-08f0-41b6-b3c4-6f72b57af6c1	d9cd5b64-e423-4710-bcfe-73606bcca78c	9a793f1256921afbff3c2bacf1fd0d1b8e6c4632bb681cfbf30d7a5465d6959a	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:34:40.66739+00	f	\N	2026-02-05 21:34:40.666814+00
db0cf6d8-c80e-44eb-984e-05d23e475d05	5368cfba-bae0-4132-88e4-4fde67d9e523	34285a627942d7db71ab2e5354dfe045cab2f73c7cdd5a5524494f0a3bd546c7	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:34:40.929749+00	f	\N	2026-02-05 21:34:40.929122+00
5a0fde71-1081-4af9-9a15-46d42560205c	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	26156adceb9bbd868852641f9e64ea23dbf518a9215ee6cb7949265a1226fd07	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:36:32.261318+00	f	\N	2026-02-05 21:36:32.260826+00
8a9b6b53-6c58-4702-bab2-eeb86124a311	222968c5-f7cd-46a9-80a7-ae6d0557b5c3	6a4cb276457bc097ee89335f929d62cbf32ce498e42342c8e10d5b99ab8c75ee	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:36:32.45117+00	f	\N	2026-02-05 21:36:32.450515+00
2f1b814a-d612-40f2-9952-27a378d53bba	fc5165e6-6519-496f-a3dd-1435bc308b5f	171ca68165c2fb1585e8c53d8e9b4d5dbb1dee27c39b254137d3d14eb8172b4c	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:39:32.921406+00	f	\N	2026-02-05 21:39:32.915128+00
861a1f32-ca04-4853-b175-59610086e3b6	2b8bb712-3cfe-435e-84f7-49dfe73d641b	86fe640e373bf8df49616ad51d07d8e7c74ab88e7a149b6ed9328264af404d12	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:39:33.205455+00	f	\N	2026-02-05 21:39:33.204872+00
124f2261-5108-453f-ab87-0d73a6580be6	d655e067-4edd-4516-b1b6-821c3c33cfc5	69fad3f51914a374e74907618d8e6a1bd0cc460376c0dd136fb49a5c281cb598	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:40:36.960295+00	f	\N	2026-02-05 21:40:36.958121+00
75c30ce0-c6e6-426c-a9ca-9eea791df2db	ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f	a7794077919e7fbf3411eb45909b2c33aabd17ab21e64d642411d11415afc132	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:40:37.217331+00	f	\N	2026-02-05 21:40:37.216705+00
9b43ebca-0e31-48a0-a47e-a73e3f4e9a29	13ac055f-b943-4f6d-8182-babe636544df	1d4b156f9a2d3984861c32fffcda0f146b8f79358fddbc3ca77548a6b6f98090	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:41:46.767812+00	f	\N	2026-02-05 21:41:46.766192+00
8816be5e-82bb-46d0-9dc8-8d7bf0f428ca	eb271702-3161-48b2-a4c9-8747819b7ae7	a3873a3f8bf36accee072816928292ee4c3e02162e1b54e032bd389ba23180bd	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:41:47.021815+00	f	\N	2026-02-05 21:41:47.021287+00
b741bd4b-6ee9-4b2e-9b7c-d63de679e99f	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	07deadb115225dbeb084d0a9a9196181b97003a237dd96d37bec9e8a5990505c	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:43:42.144564+00	f	\N	2026-02-05 21:43:42.137398+00
73955d83-aeb2-46d2-9048-1e32d28ab59d	31148b05-1512-43ce-8b01-fd3b423fca6e	195bedc9281b740253610f6d0e0a6cb0d6190c74bf4ea53c566bf7bed2bb1b16	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:43:42.348926+00	f	\N	2026-02-05 21:43:42.348346+00
b51a1d3a-4ecd-4944-b2fb-9fb1b4c1df8b	ebc86578-b9a2-456f-b884-f964c1fb26f9	a02e0ce0f0cfac9881e7819421b5a1aaae1d4edd336005d5d8b34364b966bca7	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:49:54.568608+00	f	\N	2026-02-05 21:49:54.563954+00
2f35b97b-f243-4577-a811-16cad2eb6672	3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167	cd9ebbc979d456a0c4f472a77bbcccf58d3bca367ec1309c22a7225d01922bc3	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:49:54.754256+00	f	\N	2026-02-05 21:49:54.753902+00
30532e70-b701-4c41-a92e-c8ba8c7fce46	7eddd813-1060-42a3-aa36-abc2c6529e0f	9b843ddbe22fb27aefdcb18c0d4d331b38a8aa8e26db1a637fdf9ef065add43c	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:52:18.187919+00	f	\N	2026-02-05 21:52:18.16907+00
f4695886-b582-42ff-976d-aaf931946766	83e1d52b-a86b-461a-b995-e79e2ac57878	e3441a9cbf515b26262d428e30bf650cfedb60771ba0053cd29b7ee31f58a2d1	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:52:18.458152+00	f	\N	2026-02-05 21:52:18.457594+00
70759ae5-31d6-4b03-9eb3-85cd08b0dd6e	021aea9d-7fe9-4488-ae61-eebf6d2af731	f045a7f1f745e6e471458037c756bd22050227459c9da205006ef6a226ed94c0	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:55:17.754692+00	f	\N	2026-02-05 21:55:17.742459+00
3c8b7287-3635-49fc-b193-256bb3e6874b	1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3	55373035703bae406b12bb409c2b13fcab1e8a848656d4c414d37bca53350161	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:55:18.02394+00	f	\N	2026-02-05 21:55:18.023406+00
196d09b6-d066-46fc-b02c-8aa3bd3ac574	088ad156-635f-4689-8a9f-31187419e964	86bb0595e190322043c7d6ce3841fbaca61f489787b6c4b53194c8b7c1a62b70	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:57:41.349266+00	f	\N	2026-02-05 21:57:41.330776+00
c9fe3ef0-d151-40dd-a382-8de812df521b	2e7c5e4c-423c-4bd0-9f3d-e359054f285a	b63ae00f894cb7d83a7445279242dcb8b6fca6ed1af29911985c8a6d7b438fca	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 21:57:41.672118+00	f	\N	2026-02-05 21:57:41.671562+00
0fb5cf55-88f8-45e8-9d9d-5fc7594e76a0	723079fb-4d41-408d-958c-a1d417576d82	c586bad0e1b8a296971d9deaa55171b894625de9b5f8de7e76ba5e4ad3b56721	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 22:33:45.66181+00	f	\N	2026-02-05 22:33:45.653871+00
9fa315c8-571a-4f71-95e8-1a82c5fff4cc	b1dd0b01-8388-41bb-a686-f75f5aa559b9	01fe4eabc15df54e0e8ad918974fb8fb2bfe90a3f89689e7320ca85a0b7e3c0c	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 22:33:45.859698+00	f	\N	2026-02-05 22:33:45.859211+00
c7dbafe9-d6b0-49cd-a540-8fc088d9c45c	723079fb-4d41-408d-958c-a1d417576d82	e7976bb5f4184c852ebd89336ba1caa684b8e5f9639f17f27201d0b4dffc0dad	{"ip_address": "172.18.0.1", "user_agent": "python-requests/2.32.3"}	2026-02-12 22:33:46.076175+00	f	\N	2026-02-05 22:33:46.070708+00
31092d2d-43df-4da2-9f61-d5fc232a578a	3f3a3a39-d867-45a8-b901-74a7e27c95f3	f034d82f911d8199e680683aba2e3130b2ea91238ca266a6b4033d4b4add89d8	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-12 22:43:54.706435+00	f	\N	2026-02-05 22:43:54.675468+00
f03c2bc0-426a-4cba-b6f3-2b22e0de7632	3f3a3a39-d867-45a8-b901-74a7e27c95f3	9d81463f244d74e51365f6c760318393f82b8a41329dcb20c6caa7a110aa5ebd	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-12 23:04:54.579963+00	f	\N	2026-02-05 23:04:54.573881+00
ed0104dd-2397-48bd-8556-949f52392de0	3f3a3a39-d867-45a8-b901-74a7e27c95f3	78e8d474e1aa7b2c0ea3115dee3118cd94cba2408428d8bd63479088b8b82c92	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-13 09:36:31.995125+00	f	\N	2026-02-06 09:36:31.920378+00
9d390600-0546-4209-b1c2-d1ca34698754	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2d83d99645a56d1ccbc03012ac8d83b6fb5ca1b96126d98d1503c13102cb69ca	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-13 11:09:39.313477+00	f	\N	2026-02-06 11:09:39.275322+00
cdf05795-f33c-4e60-a517-545b76e0b100	7ebef8e8-4a6d-4420-ac3a-e01a33f6c975	509262af5b0f3f46669bad3e78b7232f04bb3d40e8b494fa85a7f54b5a024006	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-15 07:10:33.511454+00	f	\N	2026-02-08 07:10:33.49738+00
eb84cd23-d232-4b19-be02-c30c9ecde332	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3fb37f4219b028035ef2ed6e61d230a7dfe2afc7f28c69f3a86f60ef8d1ec77a	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-16 12:44:16.97812+00	f	\N	2026-02-09 12:44:16.933206+00
1149d9df-313b-4efe-9896-60e4dbd6755d	3f3a3a39-d867-45a8-b901-74a7e27c95f3	035d44f540c1e6e84721d8ee0b52b88000102a5ca6d58dc8189015fec52d2172	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-16 13:49:52.848992+00	f	\N	2026-02-09 13:49:52.817992+00
ce147739-06e7-4b11-b797-bf72a09bfeaa	3f3a3a39-d867-45a8-b901-74a7e27c95f3	21b44748c2cccbdb8950312dd37120cce8320b53f31c11002e5e67331a374b69	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-16 14:11:37.58729+00	f	\N	2026-02-09 14:11:37.581976+00
b4a5117d-001f-4c59-925a-e9e2d426afc2	c5154fda-1c6a-4c09-bd67-0482fe81f7d8	8b03b8d613d9aa268ad07df95df8da1b76e7e376da9d30cdc07f615855f55d0c	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-16 14:25:30.821903+00	f	\N	2026-02-09 14:25:30.821215+00
d2181226-b01f-4c29-b24b-b7155c61a021	3f3a3a39-d867-45a8-b901-74a7e27c95f3	5ab41f759be43653eba961d701dbdb8fcf737e99b0dade8afabe4c60755533c5	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-16 14:45:07.389204+00	f	\N	2026-02-09 14:45:07.380606+00
38501c8c-1cb5-4706-b546-3c878d33d0b3	c5154fda-1c6a-4c09-bd67-0482fe81f7d8	1518b26101ed87e5c77e3ea90dde02faaefbdcd790de57ee6554a47c36ae3de0	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-16 14:46:39.938292+00	f	\N	2026-02-09 14:46:39.936898+00
33981f59-9192-4eb2-969d-d8e8886ad565	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2142ee8ff76cf9973028511deccb7ff0969834c8009f8498aefe653d7111a1e9	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-16 14:48:36.084369+00	f	\N	2026-02-09 14:48:36.079379+00
9fcdf771-edeb-45b8-a33e-c4aaefa35fa4	3f3a3a39-d867-45a8-b901-74a7e27c95f3	eb0ba4c42ff4885a7c239a508192a5a4e314ed26d71aa745c4564070b328495d	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-16 16:22:38.982036+00	f	\N	2026-02-09 16:22:38.958916+00
dae930c8-796c-4610-81b6-3387af20b7e1	3f3a3a39-d867-45a8-b901-74a7e27c95f3	e39526809c53ff3b2a69bec834820d3a529f87c362d73b07cc5285838f7a85bd	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-16 16:50:19.891383+00	f	\N	2026-02-09 16:50:19.868073+00
3f5bab38-adbe-4a53-afa2-19a7502883d5	3f3a3a39-d867-45a8-b901-74a7e27c95f3	07361950c282863110168d277002dc2785369fc9ce3a0db1560817ef487fb58b	{"ip_address": "172.18.0.1", "user_agent": "curl/8.12.1"}	2026-02-16 17:19:21.253487+00	f	\N	2026-02-09 17:19:21.247918+00
facadb60-c4ff-48b9-9231-e191cf995169	3f3a3a39-d867-45a8-b901-74a7e27c95f3	6d80d7596971d326f2fe1332fded261333143d79dc70499b1d6bdac3d63117da	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-16 17:23:33.898004+00	f	\N	2026-02-09 17:23:33.873548+00
b55e7a95-f4ec-4a6a-8520-c35527a266ef	3f3a3a39-d867-45a8-b901-74a7e27c95f3	29b3c516cd78d1f4c85f8b4767f0853790059d08dc7be61513895d7320567bd6	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-16 18:25:33.59922+00	f	\N	2026-02-09 18:25:33.58313+00
b62de4e0-b922-4660-8394-85e002d4e8a9	3f3a3a39-d867-45a8-b901-74a7e27c95f3	c9f1f92db5c64568cfdec5b348e92f2c67c29af5f6497ca8fdd2a09e187f168c	{"ip_address": "172.18.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-16 19:27:39.079479+00	f	\N	2026-02-09 19:27:39.061142+00
86f687bf-ac96-408e-8d64-264dbdfb4fb2	3f3a3a39-d867-45a8-b901-74a7e27c95f3	01008d7768b6e067f20690ef37ece7cafc2ae7762c34de3a651241021bbca230	{"ip_address": "172.20.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-17 22:47:38.462646+00	f	\N	2026-02-10 22:47:38.428851+00
ba71900f-4ef3-4def-82c8-87367669ecfe	3f3a3a39-d867-45a8-b901-74a7e27c95f3	64bc00f1a8b46fac75c1cb625a660f7f5290bac0d65fc91cd99279d0e9fab7d1	{"ip_address": "172.20.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-17 23:19:24.765761+00	f	\N	2026-02-10 23:19:24.739393+00
5efee0c1-f099-4c29-ab86-3b21d246d974	3f3a3a39-d867-45a8-b901-74a7e27c95f3	12c6136220a94dce3af9185ebb95afce651f3133c6a49d7a05cf15b9655f0942	{"ip_address": "172.20.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-18 08:08:41.53961+00	f	\N	2026-02-11 08:08:41.471441+00
6faaba8c-e136-4d83-9949-ce8bd1843e2e	3f3a3a39-d867-45a8-b901-74a7e27c95f3	fd72e41579614f175a276cfa9fc19d158a3eedbb26d20b925ce128e43644ed96	{"ip_address": "172.20.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-18 08:08:59.891757+00	f	\N	2026-02-11 08:08:59.888433+00
44037655-1703-4a72-9dbc-b28db95977b1	3f3a3a39-d867-45a8-b901-74a7e27c95f3	c02f0af5dec8f6e78b8a0c6588a986910e48261f69613f5423dedb270a5db26a	{"ip_address": "172.20.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-18 08:16:11.491463+00	f	\N	2026-02-11 08:16:11.476946+00
db33dced-ea9d-4a4e-9cdb-6e6f1e540806	3f3a3a39-d867-45a8-b901-74a7e27c95f3	1b119346d277ffd8b1ee726d1f522a1cf02d892a8d4e717e239fbe132fd34a50	{"ip_address": "172.20.0.1", "user_agent": "okhttp/4.12.0"}	2026-02-18 08:18:37.608377+00	f	\N	2026-02-11 08:18:37.592387+00
59bd4817-cb65-484f-be37-f46e7df96e88	fe4d1e04-7569-409d-8bfc-f7319e7ea582	1e16c9e8ed1752ddd448e635e7e3a5fb01f03d3db61d0353cdc7d79d3114b4de	{"ip_address": "172.20.0.1", "user_agent": "okhttp/4.12.0"}	2027-02-11 08:37:22.204767+00	f	\N	2026-02-11 08:37:22.193514+00
2e7c348c-18e7-4cfe-a7eb-ac0ff6f4807b	3f3a3a39-d867-45a8-b901-74a7e27c95f3	0565f75afa313bf800cea73015476d74d6a2a6e578cd4b7f2952c16a0aaabf07	{"ip_address": "172.20.0.1", "user_agent": "okhttp/4.12.0"}	2027-02-11 08:38:06.98196+00	f	\N	2026-02-11 08:38:06.976169+00
2ac748e0-b9de-4f2c-ac1b-9056962c6c1f	3f3a3a39-d867-45a8-b901-74a7e27c95f3	c1598f800acc430774121a073c23788981b48af61c9995b86746f424a1cfaf0b	{"ip_address": "172.20.0.1", "user_agent": "okhttp/4.12.0"}	2027-02-11 09:14:03.643813+00	f	\N	2026-02-11 09:14:03.635747+00
f7437185-8dc2-4546-b195-d1368b8b4e09	3f3a3a39-d867-45a8-b901-74a7e27c95f3	7c653d44b90ba7b749d1363c7d115aa388fbda1fd4d00fad3ed22d3e0e8c334d	{"ip_address": "172.20.0.1", "user_agent": "okhttp/4.12.0"}	2027-02-11 09:14:53.243326+00	f	\N	2026-02-11 09:14:53.235943+00
82ce3fe7-e5b3-4e7f-926b-06ce5a166fff	3f3a3a39-d867-45a8-b901-74a7e27c95f3	62e9ba5d85aa01b9d8fd72033a53b42f47730f01f79b3a6eb0f926a80a4eee3e	{"ip_address": "172.20.0.1", "user_agent": "okhttp/4.12.0"}	2027-02-11 09:25:32.152657+00	f	\N	2026-02-11 09:25:32.143801+00
92bc877f-6f60-4150-ad01-f0163adb0f66	3f3a3a39-d867-45a8-b901-74a7e27c95f3	1c1144e2c25c9597da4915a5fc0113429cd749955cd7a10995413bdfee85da0d	{"ip_address": "172.20.0.1", "user_agent": "okhttp/4.12.0"}	2027-02-11 09:30:26.414834+00	f	\N	2026-02-11 09:30:26.409416+00
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permissions (id, role_id, permission_id, effect, created_at) FROM stdin;
ac6a3369-d2be-43c0-aa3d-3c61391fbcf4	a8613649-0857-4f6a-8589-45580a027f22	3279687a-523e-45b8-8bfc-e615eba9f71c	ALLOW	2026-01-30 00:05:41.665991+00
ea7667a1-41f7-454c-b94c-41fab4165e9e	a8613649-0857-4f6a-8589-45580a027f22	25716ced-e201-45fd-bcfd-8e872be07e63	ALLOW	2026-01-30 00:05:41.665991+00
9f092147-5486-4362-b9c8-2452d9da215b	a8613649-0857-4f6a-8589-45580a027f22	5a1b2123-6018-44eb-9503-72867b17df79	ALLOW	2026-01-30 00:05:41.665991+00
cffe0b86-ed2e-4ebb-9c02-c41cf341c692	a8613649-0857-4f6a-8589-45580a027f22	e6bd71a2-7683-4d7a-ab37-2bb221bc18ed	ALLOW	2026-01-30 00:05:41.665991+00
1825b9ef-ce64-463c-bab4-f64e6d004031	a8613649-0857-4f6a-8589-45580a027f22	fc6a4a81-9cbf-41f3-b968-b0d9bb8fa51e	ALLOW	2026-01-30 00:05:41.665991+00
6d865667-37b3-4b9e-a2a1-e82b5e47f87e	a8613649-0857-4f6a-8589-45580a027f22	2a5b41d5-0131-4272-a2f2-9158438693e7	ALLOW	2026-01-30 00:05:41.665991+00
f462b09c-f2d4-4b99-8f09-47fd835215fe	a8613649-0857-4f6a-8589-45580a027f22	89b4ae84-6be5-4ed3-b6c3-3a28c273edcb	ALLOW	2026-01-30 00:05:41.665991+00
d7817043-3ee9-4f88-99b2-d78dcc8ed0b2	a8613649-0857-4f6a-8589-45580a027f22	4b87b0a2-b70f-40b7-b647-a6c7f236f444	ALLOW	2026-01-30 00:05:41.665991+00
7de81453-5d27-4a51-a372-a87664e56da7	a8613649-0857-4f6a-8589-45580a027f22	0e6e0b98-98c3-47f7-a0bd-35712eb93f04	ALLOW	2026-01-30 00:05:41.665991+00
505652ba-857f-4044-8019-764f440487e6	a8613649-0857-4f6a-8589-45580a027f22	ecd4582c-c751-475d-af73-311ec1752356	ALLOW	2026-01-30 00:05:41.665991+00
83b5cfa0-4972-473f-8021-2cf9c1b5833e	a8613649-0857-4f6a-8589-45580a027f22	f934b0e0-66cd-444e-a1af-3b823a960771	ALLOW	2026-01-30 00:05:41.665991+00
9099a64d-6caa-4681-9af0-9ef57d890d1c	a8613649-0857-4f6a-8589-45580a027f22	7812443e-1cee-496e-a5c0-5a4db85f708e	ALLOW	2026-01-30 00:05:41.665991+00
3b14a0a6-a644-4b89-9d10-10cb1694bd1a	a8613649-0857-4f6a-8589-45580a027f22	d4ac6877-f662-4ace-94b2-12a9c8083f0b	ALLOW	2026-01-30 00:05:41.665991+00
169baf3c-62c0-45c1-80cf-e3266a23fb11	a8613649-0857-4f6a-8589-45580a027f22	5d533f13-d917-4364-912d-946b50aa9dfe	ALLOW	2026-01-30 00:05:41.665991+00
c610ccf0-94d4-4540-90eb-e60bf78edc1c	a8613649-0857-4f6a-8589-45580a027f22	bf37032b-327f-4905-9fbf-611dcbf97950	ALLOW	2026-01-30 00:05:41.665991+00
cb11ca56-7bf1-4756-b5ae-d65188c9c772	a8613649-0857-4f6a-8589-45580a027f22	ab0c28ab-215b-484f-a294-63197cd5d1c5	ALLOW	2026-01-30 00:05:41.665991+00
54569ce6-f8b9-42b8-bd00-ffe92e35dd46	a8613649-0857-4f6a-8589-45580a027f22	947a701f-d0b1-47e5-aeeb-9fa55f98ed85	ALLOW	2026-01-30 00:05:41.665991+00
f03fec1c-ca68-4379-ace5-c19de55029d7	a8613649-0857-4f6a-8589-45580a027f22	0955ca9c-40f9-4585-995d-b65cb8cd7584	ALLOW	2026-01-30 00:05:41.665991+00
44e7f318-ac64-4e68-93c3-94fd3d7e3241	a8613649-0857-4f6a-8589-45580a027f22	369f06f4-5732-4251-a6af-c63c32de9724	ALLOW	2026-01-30 00:05:41.665991+00
b5fd773c-d99a-405b-96ef-29a5f4163743	a8613649-0857-4f6a-8589-45580a027f22	2b6ac6e3-46ed-4b86-90d1-43afc2f0b3c4	ALLOW	2026-01-30 00:05:41.665991+00
9facb5a7-d54e-47f9-b65e-00c4485537fb	a8613649-0857-4f6a-8589-45580a027f22	e8f06654-e8e2-4a79-92de-1bfffe186cc6	ALLOW	2026-01-30 00:05:41.665991+00
9cc49ccf-8a30-45fd-81be-bb2c71bb6670	a8613649-0857-4f6a-8589-45580a027f22	b9f92af7-ceac-45d2-ba16-18e738e90dbd	ALLOW	2026-01-30 00:05:41.665991+00
5f2e581f-fa71-472c-883f-9dee2e951ab3	a8613649-0857-4f6a-8589-45580a027f22	84ac15a9-49cc-40bb-87ca-84d4a48b4f30	ALLOW	2026-01-30 00:05:41.665991+00
a1d8558c-109d-463c-9e1a-24f4f5f01b82	a8613649-0857-4f6a-8589-45580a027f22	93682dcf-a18b-4dca-8729-b1f5c78be118	ALLOW	2026-01-30 00:05:41.665991+00
09dd4dff-2bc6-438e-a91b-7b21bf2d1d41	a8613649-0857-4f6a-8589-45580a027f22	982cccb5-d195-4be6-b906-106b9480b4a5	ALLOW	2026-01-30 00:05:41.665991+00
ea5eade4-2227-4b96-be93-c04cf64e05e7	a8613649-0857-4f6a-8589-45580a027f22	f0d3536e-56a1-4a2e-82d0-8f78306a36bd	ALLOW	2026-01-30 00:05:41.665991+00
7b8abd5e-4f53-46d6-88b3-778539d3b02b	a8613649-0857-4f6a-8589-45580a027f22	2464590f-a6db-4ef7-98b2-5260db2c713d	ALLOW	2026-01-30 00:05:41.665991+00
c774ebd5-1f66-4545-8b8f-cee811106bab	a8613649-0857-4f6a-8589-45580a027f22	90ce1518-17e5-455e-a1f2-5eb260fc515b	ALLOW	2026-01-30 00:05:41.665991+00
1acef45d-08ac-4745-a447-3548dcd03604	a8613649-0857-4f6a-8589-45580a027f22	3c7f39c7-7bbf-4421-afe6-be1d67eda567	ALLOW	2026-01-30 00:05:41.665991+00
40f90d6f-0ce4-4e5c-98fc-298a6ab9f7b1	a8613649-0857-4f6a-8589-45580a027f22	14a4b32a-236e-4df4-b688-403e7c30f869	ALLOW	2026-01-30 00:05:41.665991+00
8f3904d1-1b7a-4b3f-984f-6ddb8c86548e	a8613649-0857-4f6a-8589-45580a027f22	f8b297b7-efed-4740-a42d-78c67aaed679	ALLOW	2026-01-30 00:05:41.665991+00
ae7d7b8f-aae3-4a5b-b009-8501bdc27d5a	a8613649-0857-4f6a-8589-45580a027f22	8f1b6b31-4557-445e-996e-cdd0e52ac8b6	ALLOW	2026-01-30 00:05:41.665991+00
4e582b93-f3e5-4a5f-a8ad-d92df917a633	a8613649-0857-4f6a-8589-45580a027f22	69ccf11a-5be5-4924-bdf6-c75abb0d7a1a	ALLOW	2026-01-30 00:05:41.665991+00
315eeaf2-7ed8-4ec2-b329-0f07b4aacc7b	a8613649-0857-4f6a-8589-45580a027f22	2dcad9a8-25b0-4cb6-b3d6-95223e1e81da	ALLOW	2026-01-30 00:05:41.665991+00
fd30f679-af02-40c3-af19-b9d8281f3329	a8613649-0857-4f6a-8589-45580a027f22	c99f9d36-dc2a-4144-9c31-da03ff702ca0	ALLOW	2026-01-30 00:05:41.665991+00
108d043c-daa7-4425-94f7-3b01e6f8f907	a8613649-0857-4f6a-8589-45580a027f22	933be4e7-29f7-44db-bfcf-d0c7de9a5c6e	ALLOW	2026-01-30 00:05:41.665991+00
75c0d214-1a9d-44f4-bb23-f42184b72ce1	a8613649-0857-4f6a-8589-45580a027f22	2c945f75-f3ca-4e61-a89f-536f645a6c42	ALLOW	2026-01-30 00:05:41.665991+00
048a7d1e-c809-4163-b2c5-f562e0a2fb43	a8613649-0857-4f6a-8589-45580a027f22	970309fe-cedf-484c-8caa-52b1967c4c28	ALLOW	2026-01-30 00:05:41.665991+00
2b3e69cc-c020-424c-906a-68b674d18221	a8613649-0857-4f6a-8589-45580a027f22	1db3e8dc-cafd-4a15-96f4-49924f01f191	ALLOW	2026-01-30 00:05:41.665991+00
3159dc74-2705-4aae-8ac4-b7a12f2831f5	a8613649-0857-4f6a-8589-45580a027f22	7f570664-7927-4a2d-a84c-aff34c6ca920	ALLOW	2026-01-30 00:05:41.665991+00
189a629b-4839-48fe-952c-d0d6a3f33db7	a8613649-0857-4f6a-8589-45580a027f22	a2b84945-9fa5-4ede-a916-d75eddf74e7f	ALLOW	2026-01-30 00:05:41.665991+00
6e9b04bc-2e86-479f-a619-633a83b4fe51	a8613649-0857-4f6a-8589-45580a027f22	7da820fe-aecc-4a58-bfe2-a70c6049dcce	ALLOW	2026-01-30 00:05:41.665991+00
03d98dcb-683d-4e57-b624-41ba1e91b015	a8613649-0857-4f6a-8589-45580a027f22	bd3307be-da32-4397-8a93-2d2cd4d5711a	ALLOW	2026-01-30 00:05:41.665991+00
361822ac-f110-45e2-8ca2-6c434ee0eead	a8613649-0857-4f6a-8589-45580a027f22	de186c8e-e00a-415f-a0df-4d9b7c677b9d	ALLOW	2026-01-30 00:05:41.665991+00
64857535-e7b5-4dc4-8eb9-cf87b2ad5aa6	a8613649-0857-4f6a-8589-45580a027f22	93acbbc5-d363-457b-a501-9d0f48973ffe	ALLOW	2026-01-30 00:05:41.665991+00
a094f51a-585c-483f-a45a-22effe3718a8	a8613649-0857-4f6a-8589-45580a027f22	5afd63fb-a962-45bb-a048-57470429012a	ALLOW	2026-01-30 00:05:41.665991+00
10a44f0c-b900-4ea7-b974-82a5f506f0af	a8613649-0857-4f6a-8589-45580a027f22	6473217c-70c0-494b-bcfe-7037e66f1477	ALLOW	2026-01-30 00:05:41.665991+00
39b34e61-7e04-4fef-aba0-e9eea654419c	a8613649-0857-4f6a-8589-45580a027f22	5fabd302-e953-4841-afd6-e4f0960e0305	ALLOW	2026-01-30 00:05:41.665991+00
dd34f754-fcbf-4033-a0ee-e9ac98966d56	a8613649-0857-4f6a-8589-45580a027f22	a6c3920b-3756-4554-b73c-a0e91cb1ab9b	ALLOW	2026-01-30 00:05:41.665991+00
7a85d6b5-5a21-43cf-979c-c11eadb6f608	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	3279687a-523e-45b8-8bfc-e615eba9f71c	ALLOW	2026-01-30 00:05:41.676838+00
9ca9a598-8dbc-4c1f-964e-7f2b759eac68	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	25716ced-e201-45fd-bcfd-8e872be07e63	ALLOW	2026-01-30 00:05:41.676838+00
4b624ab9-5a7c-4c9c-92da-8c0c8e67c52f	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	5a1b2123-6018-44eb-9503-72867b17df79	ALLOW	2026-01-30 00:05:41.676838+00
838c2b92-e50a-4ff0-814b-68d28f93865e	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	e6bd71a2-7683-4d7a-ab37-2bb221bc18ed	ALLOW	2026-01-30 00:05:41.676838+00
0a23f041-a15a-4417-8b11-804ae896f074	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	fc6a4a81-9cbf-41f3-b968-b0d9bb8fa51e	ALLOW	2026-01-30 00:05:41.676838+00
a2619314-9957-4de5-b499-ba2d1ba44319	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	2a5b41d5-0131-4272-a2f2-9158438693e7	ALLOW	2026-01-30 00:05:41.676838+00
c32eef86-75c5-4188-ae3e-66bb25bc1d92	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	89b4ae84-6be5-4ed3-b6c3-3a28c273edcb	ALLOW	2026-01-30 00:05:41.676838+00
a037d9d4-ad40-41c0-892f-944a329a46e9	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	4b87b0a2-b70f-40b7-b647-a6c7f236f444	ALLOW	2026-01-30 00:05:41.676838+00
ae3231ec-0a66-41fc-b188-fbcf529d6ea5	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	0e6e0b98-98c3-47f7-a0bd-35712eb93f04	ALLOW	2026-01-30 00:05:41.676838+00
711719cf-100a-41fa-94b1-61b1dc3f809e	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	ecd4582c-c751-475d-af73-311ec1752356	ALLOW	2026-01-30 00:05:41.676838+00
91939854-d63e-4f28-92b9-a9e367fcc42c	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	f934b0e0-66cd-444e-a1af-3b823a960771	ALLOW	2026-01-30 00:05:41.676838+00
eb097628-d189-4af9-b6c1-5554adf02967	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	7812443e-1cee-496e-a5c0-5a4db85f708e	ALLOW	2026-01-30 00:05:41.676838+00
f079daf7-09b7-407f-9711-6871851df831	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	d4ac6877-f662-4ace-94b2-12a9c8083f0b	ALLOW	2026-01-30 00:05:41.676838+00
355938d9-c238-419c-b5b8-2b69e435a9b7	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	5d533f13-d917-4364-912d-946b50aa9dfe	ALLOW	2026-01-30 00:05:41.676838+00
faa3bb7e-4291-4431-bde4-a5690eaa6455	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	bf37032b-327f-4905-9fbf-611dcbf97950	ALLOW	2026-01-30 00:05:41.676838+00
79838236-4028-4a6b-ac1f-b2dc1aab9b3c	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	ab0c28ab-215b-484f-a294-63197cd5d1c5	ALLOW	2026-01-30 00:05:41.676838+00
5acca373-137a-45c0-8306-d0594be1c8da	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	947a701f-d0b1-47e5-aeeb-9fa55f98ed85	ALLOW	2026-01-30 00:05:41.676838+00
0dff1b28-8490-4af8-8af0-1055fe5a8c60	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	0955ca9c-40f9-4585-995d-b65cb8cd7584	ALLOW	2026-01-30 00:05:41.676838+00
f2a24353-972a-4885-8678-c8632635eb6c	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	84ac15a9-49cc-40bb-87ca-84d4a48b4f30	ALLOW	2026-01-30 00:05:41.676838+00
2e40dc68-fbd2-4950-af1b-03f07dc79ab2	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	93682dcf-a18b-4dca-8729-b1f5c78be118	ALLOW	2026-01-30 00:05:41.676838+00
d4da2e2e-118a-46ab-828f-c4544f806be4	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	982cccb5-d195-4be6-b906-106b9480b4a5	ALLOW	2026-01-30 00:05:41.676838+00
f6641b66-97ca-4c1d-a81a-4c3defa83221	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	f0d3536e-56a1-4a2e-82d0-8f78306a36bd	ALLOW	2026-01-30 00:05:41.676838+00
34356359-d3b7-410f-baad-2173709d5a31	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	3c7f39c7-7bbf-4421-afe6-be1d67eda567	ALLOW	2026-01-30 00:05:41.676838+00
89ce5c5d-94d2-4e84-a1a8-2d857cb3b946	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	7f570664-7927-4a2d-a84c-aff34c6ca920	ALLOW	2026-01-30 00:05:41.676838+00
4a91474a-792b-457f-a261-4a3ca8d71278	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	a2b84945-9fa5-4ede-a916-d75eddf74e7f	ALLOW	2026-01-30 00:05:41.676838+00
a2af108b-8487-4ea2-9285-2ef6343f2720	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	7da820fe-aecc-4a58-bfe2-a70c6049dcce	ALLOW	2026-01-30 00:05:41.676838+00
57f1f80b-ba12-4e89-8d93-75935dbfd84e	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	bd3307be-da32-4397-8a93-2d2cd4d5711a	ALLOW	2026-01-30 00:05:41.676838+00
8e81a8e5-cae0-40e0-a5b5-7bff748a45a3	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	de186c8e-e00a-415f-a0df-4d9b7c677b9d	ALLOW	2026-01-30 00:05:41.676838+00
533ae934-8101-44f1-a319-476e3aa4bb9a	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	93acbbc5-d363-457b-a501-9d0f48973ffe	ALLOW	2026-01-30 00:05:41.676838+00
92298327-de3e-485c-bb99-2ab3c29aba18	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	5afd63fb-a962-45bb-a048-57470429012a	ALLOW	2026-01-30 00:05:41.676838+00
4af5306f-d3e6-418d-aaf6-f66724ced63c	fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	6473217c-70c0-494b-bcfe-7037e66f1477	ALLOW	2026-01-30 00:05:41.676838+00
f493da59-0f71-48da-9b03-a93945bcf4f2	2a4340f7-7832-478b-9729-a7705e4cd3b1	25716ced-e201-45fd-bcfd-8e872be07e63	ALLOW	2026-01-30 00:05:41.687508+00
10d18568-acd2-4c45-ba8a-c76aa205a38f	2a4340f7-7832-478b-9729-a7705e4cd3b1	5a1b2123-6018-44eb-9503-72867b17df79	ALLOW	2026-01-30 00:05:41.687508+00
aee5d311-8ab3-49cc-a8b2-69ed7474ba35	2a4340f7-7832-478b-9729-a7705e4cd3b1	2a5b41d5-0131-4272-a2f2-9158438693e7	ALLOW	2026-01-30 00:05:41.687508+00
13f5c5df-7bbf-41b3-888f-566c587fb121	2a4340f7-7832-478b-9729-a7705e4cd3b1	89b4ae84-6be5-4ed3-b6c3-3a28c273edcb	ALLOW	2026-01-30 00:05:41.687508+00
1e2294c7-59d3-42cd-8eaf-0b1656a3f136	2a4340f7-7832-478b-9729-a7705e4cd3b1	0e6e0b98-98c3-47f7-a0bd-35712eb93f04	ALLOW	2026-01-30 00:05:41.687508+00
87a7aa80-6dc1-4c38-b499-afbc0d6e2830	2a4340f7-7832-478b-9729-a7705e4cd3b1	ecd4582c-c751-475d-af73-311ec1752356	ALLOW	2026-01-30 00:05:41.687508+00
8116a3c0-f251-4946-ab5a-f769e139febf	2a4340f7-7832-478b-9729-a7705e4cd3b1	f934b0e0-66cd-444e-a1af-3b823a960771	ALLOW	2026-01-30 00:05:41.687508+00
8edcd59b-62d7-4245-b3c2-614772f78e4e	2a4340f7-7832-478b-9729-a7705e4cd3b1	d4ac6877-f662-4ace-94b2-12a9c8083f0b	ALLOW	2026-01-30 00:05:41.687508+00
71123093-ac96-45ab-8ac0-b2b79493575f	2a4340f7-7832-478b-9729-a7705e4cd3b1	5d533f13-d917-4364-912d-946b50aa9dfe	ALLOW	2026-01-30 00:05:41.687508+00
0252f7c1-4848-4247-88e1-16fa02e39987	2a4340f7-7832-478b-9729-a7705e4cd3b1	bf37032b-327f-4905-9fbf-611dcbf97950	ALLOW	2026-01-30 00:05:41.687508+00
d6b552f6-f8d3-4f9c-a100-7a7fd45e5f0b	2a4340f7-7832-478b-9729-a7705e4cd3b1	ab0c28ab-215b-484f-a294-63197cd5d1c5	ALLOW	2026-01-30 00:05:41.687508+00
fadb1886-bd55-4682-aadd-ddf3f8a805fa	2a4340f7-7832-478b-9729-a7705e4cd3b1	982cccb5-d195-4be6-b906-106b9480b4a5	ALLOW	2026-01-30 00:05:41.687508+00
71c2eadf-fccc-47f9-8e6a-233cb9a183c0	2a4340f7-7832-478b-9729-a7705e4cd3b1	f0d3536e-56a1-4a2e-82d0-8f78306a36bd	ALLOW	2026-01-30 00:05:41.687508+00
696faa8b-df80-4f05-af77-0a370833edb2	2a4340f7-7832-478b-9729-a7705e4cd3b1	3c7f39c7-7bbf-4421-afe6-be1d67eda567	ALLOW	2026-01-30 00:05:41.687508+00
92c1641d-7cd8-48f6-b24b-90e97585d2a8	2a4340f7-7832-478b-9729-a7705e4cd3b1	7f570664-7927-4a2d-a84c-aff34c6ca920	ALLOW	2026-01-30 00:05:41.687508+00
41bda711-23e6-483b-8cc5-8f0959957f62	2a4340f7-7832-478b-9729-a7705e4cd3b1	a2b84945-9fa5-4ede-a916-d75eddf74e7f	ALLOW	2026-01-30 00:05:41.687508+00
9b671928-8ae5-4718-b2a9-f1db14fc417e	2a4340f7-7832-478b-9729-a7705e4cd3b1	7da820fe-aecc-4a58-bfe2-a70c6049dcce	ALLOW	2026-01-30 00:05:41.687508+00
4fa6af3e-caa8-4840-a8ab-a0a62058d657	2a4340f7-7832-478b-9729-a7705e4cd3b1	bd3307be-da32-4397-8a93-2d2cd4d5711a	ALLOW	2026-01-30 00:05:41.687508+00
c46e1786-d407-4d80-91db-e72c6768135d	2a4340f7-7832-478b-9729-a7705e4cd3b1	de186c8e-e00a-415f-a0df-4d9b7c677b9d	ALLOW	2026-01-30 00:05:41.687508+00
1d9320a2-0c8f-4838-9bd7-87c65b861dc0	2a4340f7-7832-478b-9729-a7705e4cd3b1	93acbbc5-d363-457b-a501-9d0f48973ffe	ALLOW	2026-01-30 00:05:41.687508+00
781b407d-8534-4e39-bdc4-13c84563ab2e	2a4340f7-7832-478b-9729-a7705e4cd3b1	5afd63fb-a962-45bb-a048-57470429012a	ALLOW	2026-01-30 00:05:41.687508+00
2191973d-f34e-46a3-add8-613fbc1167ff	2a4340f7-7832-478b-9729-a7705e4cd3b1	6473217c-70c0-494b-bcfe-7037e66f1477	ALLOW	2026-01-30 00:05:41.687508+00
d44d7a3a-d0f6-469e-96eb-dedd81c09400	a98b7297-3bd8-4084-8dd4-ca156371f1c5	25716ced-e201-45fd-bcfd-8e872be07e63	ALLOW	2026-01-30 00:05:41.698295+00
3aae4184-84fa-44a7-82c1-d4b6047a9925	a98b7297-3bd8-4084-8dd4-ca156371f1c5	2a5b41d5-0131-4272-a2f2-9158438693e7	ALLOW	2026-01-30 00:05:41.698295+00
3a874c36-5825-4671-93e6-fad72b8dcda1	a98b7297-3bd8-4084-8dd4-ca156371f1c5	ecd4582c-c751-475d-af73-311ec1752356	ALLOW	2026-01-30 00:05:41.698295+00
bccd3c35-0674-4ecf-b3b5-68ae8f29a70d	a98b7297-3bd8-4084-8dd4-ca156371f1c5	f934b0e0-66cd-444e-a1af-3b823a960771	ALLOW	2026-01-30 00:05:41.698295+00
eba88c41-db4f-4539-aea5-4b01fa265855	a98b7297-3bd8-4084-8dd4-ca156371f1c5	d4ac6877-f662-4ace-94b2-12a9c8083f0b	ALLOW	2026-01-30 00:05:41.698295+00
767540bd-de8e-49ff-8eec-d7ff6ba03bd5	a98b7297-3bd8-4084-8dd4-ca156371f1c5	5d533f13-d917-4364-912d-946b50aa9dfe	ALLOW	2026-01-30 00:05:41.698295+00
ecc5a91c-bebf-4afe-a8e7-dc72ee11a27b	a98b7297-3bd8-4084-8dd4-ca156371f1c5	bf37032b-327f-4905-9fbf-611dcbf97950	ALLOW	2026-01-30 00:05:41.698295+00
7101b82c-4193-4b7a-b323-14c1cd2cc2e8	a98b7297-3bd8-4084-8dd4-ca156371f1c5	ab0c28ab-215b-484f-a294-63197cd5d1c5	ALLOW	2026-01-30 00:05:41.698295+00
eb7fa1b5-16b1-40ae-a256-fb94f0b37fb6	a98b7297-3bd8-4084-8dd4-ca156371f1c5	947a701f-d0b1-47e5-aeeb-9fa55f98ed85	ALLOW	2026-01-30 00:05:41.698295+00
f340d418-66a0-4542-8577-dfee42d60bb8	a98b7297-3bd8-4084-8dd4-ca156371f1c5	0955ca9c-40f9-4585-995d-b65cb8cd7584	ALLOW	2026-01-30 00:05:41.698295+00
845e31cc-310e-4196-b13c-447ae6c97213	a98b7297-3bd8-4084-8dd4-ca156371f1c5	84ac15a9-49cc-40bb-87ca-84d4a48b4f30	ALLOW	2026-01-30 00:05:41.698295+00
d39e5c7e-537d-45e1-8dc8-394450b42e55	a98b7297-3bd8-4084-8dd4-ca156371f1c5	93682dcf-a18b-4dca-8729-b1f5c78be118	ALLOW	2026-01-30 00:05:41.698295+00
6dc31660-af78-4a1c-b21b-27ad6e9b11e5	a98b7297-3bd8-4084-8dd4-ca156371f1c5	f0d3536e-56a1-4a2e-82d0-8f78306a36bd	ALLOW	2026-01-30 00:05:41.698295+00
04fdd06f-6541-4729-9fa2-3650838a71b0	a98b7297-3bd8-4084-8dd4-ca156371f1c5	2464590f-a6db-4ef7-98b2-5260db2c713d	ALLOW	2026-01-30 00:05:41.698295+00
d3ede896-c809-4b73-b7fd-acd0e3e71276	a98b7297-3bd8-4084-8dd4-ca156371f1c5	90ce1518-17e5-455e-a1f2-5eb260fc515b	ALLOW	2026-01-30 00:05:41.698295+00
33ce40d5-c7f7-4ec7-80f7-7db7771a03d5	a98b7297-3bd8-4084-8dd4-ca156371f1c5	14a4b32a-236e-4df4-b688-403e7c30f869	ALLOW	2026-01-30 00:05:41.698295+00
06fa6873-cb89-4504-89b3-79f937ae4490	a98b7297-3bd8-4084-8dd4-ca156371f1c5	f8b297b7-efed-4740-a42d-78c67aaed679	ALLOW	2026-01-30 00:05:41.698295+00
5576eabc-5ba8-4b30-ac3b-2c12e02e2b44	a98b7297-3bd8-4084-8dd4-ca156371f1c5	8f1b6b31-4557-445e-996e-cdd0e52ac8b6	ALLOW	2026-01-30 00:05:41.698295+00
93cb046d-a0f1-46c7-b253-e1a05a6d1f9f	a98b7297-3bd8-4084-8dd4-ca156371f1c5	69ccf11a-5be5-4924-bdf6-c75abb0d7a1a	ALLOW	2026-01-30 00:05:41.698295+00
19265ad8-4c9a-4ee0-8e89-96b8cb2d330b	a98b7297-3bd8-4084-8dd4-ca156371f1c5	2dcad9a8-25b0-4cb6-b3d6-95223e1e81da	ALLOW	2026-01-30 00:05:41.698295+00
ffbd389d-3330-4195-899e-eea959b0e524	a98b7297-3bd8-4084-8dd4-ca156371f1c5	c99f9d36-dc2a-4144-9c31-da03ff702ca0	ALLOW	2026-01-30 00:05:41.698295+00
f626151b-1001-4120-ac8a-d48062e1572d	a98b7297-3bd8-4084-8dd4-ca156371f1c5	933be4e7-29f7-44db-bfcf-d0c7de9a5c6e	ALLOW	2026-01-30 00:05:41.698295+00
31fd4e0a-c7f1-4755-977a-9e0e3b1f8933	a98b7297-3bd8-4084-8dd4-ca156371f1c5	2c945f75-f3ca-4e61-a89f-536f645a6c42	ALLOW	2026-01-30 00:05:41.698295+00
c5e481db-6832-4095-a95b-5e03c0a0d320	a98b7297-3bd8-4084-8dd4-ca156371f1c5	970309fe-cedf-484c-8caa-52b1967c4c28	ALLOW	2026-01-30 00:05:41.698295+00
54629121-507c-463f-96a1-a03beaee2d97	a98b7297-3bd8-4084-8dd4-ca156371f1c5	1db3e8dc-cafd-4a15-96f4-49924f01f191	ALLOW	2026-01-30 00:05:41.698295+00
aa2b8c27-6cdb-493e-aacb-5e123d3c5e9e	a98b7297-3bd8-4084-8dd4-ca156371f1c5	7da820fe-aecc-4a58-bfe2-a70c6049dcce	ALLOW	2026-01-30 00:05:41.698295+00
6312ba65-2c06-4543-b176-d29af75a032c	a98b7297-3bd8-4084-8dd4-ca156371f1c5	bd3307be-da32-4397-8a93-2d2cd4d5711a	ALLOW	2026-01-30 00:05:41.698295+00
14b36000-0368-4841-b37f-b04ff9335bd6	a98b7297-3bd8-4084-8dd4-ca156371f1c5	de186c8e-e00a-415f-a0df-4d9b7c677b9d	ALLOW	2026-01-30 00:05:41.698295+00
70f85e43-d2ae-4106-a36d-f43d715df213	a98b7297-3bd8-4084-8dd4-ca156371f1c5	93acbbc5-d363-457b-a501-9d0f48973ffe	ALLOW	2026-01-30 00:05:41.698295+00
bfccb460-047a-4e22-b1cd-ce8cf0571d9b	a98b7297-3bd8-4084-8dd4-ca156371f1c5	5afd63fb-a962-45bb-a048-57470429012a	ALLOW	2026-01-30 00:05:41.698295+00
bc18a9c7-9e32-4167-b13f-8b47945023ef	a98b7297-3bd8-4084-8dd4-ca156371f1c5	6473217c-70c0-494b-bcfe-7037e66f1477	ALLOW	2026-01-30 00:05:41.698295+00
4f27201b-b70e-4469-90d2-5f272deb85d5	a98b7297-3bd8-4084-8dd4-ca156371f1c5	a6c3920b-3756-4554-b73c-a0e91cb1ab9b	ALLOW	2026-01-30 00:05:41.698295+00
c16f9119-3fe3-4204-9277-661c1669411b	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	25716ced-e201-45fd-bcfd-8e872be07e63	ALLOW	2026-01-30 00:05:41.709096+00
73d93a84-53b7-45f8-a22f-88cdcfd9f6a3	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	2a5b41d5-0131-4272-a2f2-9158438693e7	ALLOW	2026-01-30 00:05:41.709096+00
7f9b5140-926f-406b-8eef-0439fe142a52	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	ecd4582c-c751-475d-af73-311ec1752356	ALLOW	2026-01-30 00:05:41.709096+00
cb6fc381-863e-478b-b660-748fa398448f	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	f934b0e0-66cd-444e-a1af-3b823a960771	ALLOW	2026-01-30 00:05:41.709096+00
6dd5d326-4d8b-436e-b076-b6aa46c0f1a4	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	d4ac6877-f662-4ace-94b2-12a9c8083f0b	ALLOW	2026-01-30 00:05:41.709096+00
3c199bf8-68d5-4ff3-bd34-1dd6f2d0e0f2	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	5d533f13-d917-4364-912d-946b50aa9dfe	ALLOW	2026-01-30 00:05:41.709096+00
b7f42a9c-1cfd-4666-b08f-5af68e1055dd	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	bf37032b-327f-4905-9fbf-611dcbf97950	ALLOW	2026-01-30 00:05:41.709096+00
a5fdf8b6-2d8d-45cc-840e-6197d5269492	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	ab0c28ab-215b-484f-a294-63197cd5d1c5	ALLOW	2026-01-30 00:05:41.709096+00
192d7611-ae25-4faf-8071-0cd1cd400512	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	f0d3536e-56a1-4a2e-82d0-8f78306a36bd	ALLOW	2026-01-30 00:05:41.709096+00
570011b7-fd28-4507-9aa2-7342a398fa99	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	2464590f-a6db-4ef7-98b2-5260db2c713d	ALLOW	2026-01-30 00:05:41.709096+00
eaba95e6-3cde-46eb-a65d-42351d838a0f	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	90ce1518-17e5-455e-a1f2-5eb260fc515b	ALLOW	2026-01-30 00:05:41.709096+00
e8a5a216-804a-4e46-9d56-81685ce389f1	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	14a4b32a-236e-4df4-b688-403e7c30f869	ALLOW	2026-01-30 00:05:41.709096+00
ffe9a155-74f7-4a98-8279-3d4c199c9215	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	f8b297b7-efed-4740-a42d-78c67aaed679	ALLOW	2026-01-30 00:05:41.709096+00
428d2800-6ac9-4926-969c-0818a07996c7	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	8f1b6b31-4557-445e-996e-cdd0e52ac8b6	ALLOW	2026-01-30 00:05:41.709096+00
59ce0025-8cf7-4e40-9f22-efbce45af4bc	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	69ccf11a-5be5-4924-bdf6-c75abb0d7a1a	ALLOW	2026-01-30 00:05:41.709096+00
c6e2992a-9ed1-4fb9-bad2-8e9e29c290ec	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	2dcad9a8-25b0-4cb6-b3d6-95223e1e81da	ALLOW	2026-01-30 00:05:41.709096+00
0be6276a-e419-4902-a633-52a4a8151fc9	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	c99f9d36-dc2a-4144-9c31-da03ff702ca0	ALLOW	2026-01-30 00:05:41.709096+00
52b8d608-584b-4c2a-acda-b6019a33053f	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	933be4e7-29f7-44db-bfcf-d0c7de9a5c6e	ALLOW	2026-01-30 00:05:41.709096+00
62c590de-0081-4465-8016-97fb4dcc7723	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	2c945f75-f3ca-4e61-a89f-536f645a6c42	ALLOW	2026-01-30 00:05:41.709096+00
9bf3740c-2ddf-4282-9dff-c88be9a86b50	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	970309fe-cedf-484c-8caa-52b1967c4c28	ALLOW	2026-01-30 00:05:41.709096+00
4f46959a-de65-400b-a880-86db2e724d47	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	1db3e8dc-cafd-4a15-96f4-49924f01f191	ALLOW	2026-01-30 00:05:41.709096+00
f10894dd-aaf9-404c-b162-1f8048281171	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	7da820fe-aecc-4a58-bfe2-a70c6049dcce	ALLOW	2026-01-30 00:05:41.709096+00
0e5c0533-4405-430f-8341-659ad97b01f6	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	bd3307be-da32-4397-8a93-2d2cd4d5711a	ALLOW	2026-01-30 00:05:41.709096+00
1ea1181c-627a-4714-82fb-5adf4b0d5624	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	de186c8e-e00a-415f-a0df-4d9b7c677b9d	ALLOW	2026-01-30 00:05:41.709096+00
fb0b60ba-aece-43ec-892f-0262b8690303	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	93acbbc5-d363-457b-a501-9d0f48973ffe	ALLOW	2026-01-30 00:05:41.709096+00
8ea9712a-64c7-4926-9637-fda3e4d5850c	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	5afd63fb-a962-45bb-a048-57470429012a	ALLOW	2026-01-30 00:05:41.709096+00
cf9ace6c-80c3-4ba8-b1be-4a29c56e793f	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	6473217c-70c0-494b-bcfe-7037e66f1477	ALLOW	2026-01-30 00:05:41.709096+00
fca8dcac-d65c-45b5-b61c-99f7b798503c	58d7088d-dde1-4bf6-b0c9-5dbde555e46c	a6c3920b-3756-4554-b73c-a0e91cb1ab9b	ALLOW	2026-01-30 00:05:41.709096+00
5f8aadad-a457-4b79-b3ce-4496eb490d5d	c3d36b6d-6bb1-435c-8634-9316f42c09a0	25716ced-e201-45fd-bcfd-8e872be07e63	ALLOW	2026-01-30 00:05:41.719944+00
d94e74a9-34ed-43e7-8c53-67a3e64d2721	c3d36b6d-6bb1-435c-8634-9316f42c09a0	2a5b41d5-0131-4272-a2f2-9158438693e7	ALLOW	2026-01-30 00:05:41.719944+00
94baa058-d51c-42a6-b394-63c334834462	c3d36b6d-6bb1-435c-8634-9316f42c09a0	ecd4582c-c751-475d-af73-311ec1752356	ALLOW	2026-01-30 00:05:41.719944+00
27a68744-7d95-4943-894c-4e7ed853c8b7	c3d36b6d-6bb1-435c-8634-9316f42c09a0	f934b0e0-66cd-444e-a1af-3b823a960771	ALLOW	2026-01-30 00:05:41.719944+00
0d8d16a1-eed0-4ce4-914a-70ac6eb5072c	c3d36b6d-6bb1-435c-8634-9316f42c09a0	d4ac6877-f662-4ace-94b2-12a9c8083f0b	ALLOW	2026-01-30 00:05:41.719944+00
a258a178-2438-42c8-bdf4-f12b99324c70	c3d36b6d-6bb1-435c-8634-9316f42c09a0	5d533f13-d917-4364-912d-946b50aa9dfe	ALLOW	2026-01-30 00:05:41.719944+00
6dbbe4b5-8eef-452d-9683-998e31f46ee3	c3d36b6d-6bb1-435c-8634-9316f42c09a0	bf37032b-327f-4905-9fbf-611dcbf97950	ALLOW	2026-01-30 00:05:41.719944+00
96eba76a-5a1e-4cfc-815b-dff6ecc7563a	c3d36b6d-6bb1-435c-8634-9316f42c09a0	ab0c28ab-215b-484f-a294-63197cd5d1c5	ALLOW	2026-01-30 00:05:41.719944+00
78dff57a-61e6-4998-8c0c-99fb72f6c45c	c3d36b6d-6bb1-435c-8634-9316f42c09a0	f0d3536e-56a1-4a2e-82d0-8f78306a36bd	ALLOW	2026-01-30 00:05:41.719944+00
02a3c157-b511-4ba2-94c1-c139aeae9119	c3d36b6d-6bb1-435c-8634-9316f42c09a0	2464590f-a6db-4ef7-98b2-5260db2c713d	ALLOW	2026-01-30 00:05:41.719944+00
59c02234-06fb-4134-a091-877866c9fb46	c3d36b6d-6bb1-435c-8634-9316f42c09a0	90ce1518-17e5-455e-a1f2-5eb260fc515b	ALLOW	2026-01-30 00:05:41.719944+00
a9db4264-a34f-4e8e-8a64-d1738ccbfad8	c3d36b6d-6bb1-435c-8634-9316f42c09a0	14a4b32a-236e-4df4-b688-403e7c30f869	ALLOW	2026-01-30 00:05:41.719944+00
1a9c1c50-4f5d-4b3b-8870-03cd873c8202	c3d36b6d-6bb1-435c-8634-9316f42c09a0	f8b297b7-efed-4740-a42d-78c67aaed679	ALLOW	2026-01-30 00:05:41.719944+00
c7da4ab9-4499-42c2-b5c3-ff95621ae416	c3d36b6d-6bb1-435c-8634-9316f42c09a0	8f1b6b31-4557-445e-996e-cdd0e52ac8b6	ALLOW	2026-01-30 00:05:41.719944+00
d895304f-0a51-479d-8460-6b64cf7966f2	c3d36b6d-6bb1-435c-8634-9316f42c09a0	69ccf11a-5be5-4924-bdf6-c75abb0d7a1a	ALLOW	2026-01-30 00:05:41.719944+00
372d6e56-1bc4-4e78-988e-5d17e9852baa	c3d36b6d-6bb1-435c-8634-9316f42c09a0	2dcad9a8-25b0-4cb6-b3d6-95223e1e81da	ALLOW	2026-01-30 00:05:41.719944+00
516b9410-737a-42dc-917c-48b009ff9a23	c3d36b6d-6bb1-435c-8634-9316f42c09a0	c99f9d36-dc2a-4144-9c31-da03ff702ca0	ALLOW	2026-01-30 00:05:41.719944+00
fbc71661-4ab4-432d-a1ff-83f45fccc189	c3d36b6d-6bb1-435c-8634-9316f42c09a0	933be4e7-29f7-44db-bfcf-d0c7de9a5c6e	ALLOW	2026-01-30 00:05:41.719944+00
603ee5e1-ff1c-416b-bb30-3c94a07dd565	c3d36b6d-6bb1-435c-8634-9316f42c09a0	2c945f75-f3ca-4e61-a89f-536f645a6c42	ALLOW	2026-01-30 00:05:41.719944+00
508894cc-e32e-41ab-a288-e4b960e3c74e	c3d36b6d-6bb1-435c-8634-9316f42c09a0	970309fe-cedf-484c-8caa-52b1967c4c28	ALLOW	2026-01-30 00:05:41.719944+00
0eb451d2-13f3-4a52-a422-76c1455d2e0b	c3d36b6d-6bb1-435c-8634-9316f42c09a0	1db3e8dc-cafd-4a15-96f4-49924f01f191	ALLOW	2026-01-30 00:05:41.719944+00
f2395dad-7895-494a-906c-2958bac410af	c3d36b6d-6bb1-435c-8634-9316f42c09a0	7da820fe-aecc-4a58-bfe2-a70c6049dcce	ALLOW	2026-01-30 00:05:41.719944+00
f8385665-f157-41bc-b200-bd8f8cc2ce38	c3d36b6d-6bb1-435c-8634-9316f42c09a0	bd3307be-da32-4397-8a93-2d2cd4d5711a	ALLOW	2026-01-30 00:05:41.719944+00
dc615e29-ab2d-4935-adbe-0fc9a359b8e5	c3d36b6d-6bb1-435c-8634-9316f42c09a0	de186c8e-e00a-415f-a0df-4d9b7c677b9d	ALLOW	2026-01-30 00:05:41.719944+00
237883a8-c43a-4615-8268-4e28788413e3	c3d36b6d-6bb1-435c-8634-9316f42c09a0	93acbbc5-d363-457b-a501-9d0f48973ffe	ALLOW	2026-01-30 00:05:41.719944+00
fd966031-134e-4eca-a4c4-0dd4cfe974f0	c3d36b6d-6bb1-435c-8634-9316f42c09a0	5afd63fb-a962-45bb-a048-57470429012a	ALLOW	2026-01-30 00:05:41.719944+00
adf485c8-c1a4-44c5-aa0c-f6f090d1e88f	c3d36b6d-6bb1-435c-8634-9316f42c09a0	6473217c-70c0-494b-bcfe-7037e66f1477	ALLOW	2026-01-30 00:05:41.719944+00
0425fa34-f454-48f1-94cb-27460c1a2ab7	0ca36331-1393-48be-b0f4-b41d07e7cd49	25716ced-e201-45fd-bcfd-8e872be07e63	ALLOW	2026-01-30 00:05:41.730722+00
be793ce5-365a-445b-bc08-0559c97d8196	0ca36331-1393-48be-b0f4-b41d07e7cd49	2a5b41d5-0131-4272-a2f2-9158438693e7	ALLOW	2026-01-30 00:05:41.730722+00
59947892-0c01-4190-90b2-392850b6d705	0ca36331-1393-48be-b0f4-b41d07e7cd49	ecd4582c-c751-475d-af73-311ec1752356	ALLOW	2026-01-30 00:05:41.730722+00
11e1524f-928d-4455-9127-16271962d529	0ca36331-1393-48be-b0f4-b41d07e7cd49	f934b0e0-66cd-444e-a1af-3b823a960771	ALLOW	2026-01-30 00:05:41.730722+00
facbfd70-df74-442f-b956-cdb927283b0b	0ca36331-1393-48be-b0f4-b41d07e7cd49	d4ac6877-f662-4ace-94b2-12a9c8083f0b	ALLOW	2026-01-30 00:05:41.730722+00
5f1de862-3524-4f57-a9bc-90e99a9b474c	0ca36331-1393-48be-b0f4-b41d07e7cd49	5d533f13-d917-4364-912d-946b50aa9dfe	ALLOW	2026-01-30 00:05:41.730722+00
127f5c3d-d6ba-4dac-8e1b-4919005f584a	0ca36331-1393-48be-b0f4-b41d07e7cd49	bf37032b-327f-4905-9fbf-611dcbf97950	ALLOW	2026-01-30 00:05:41.730722+00
2491cc5c-2214-4c9a-bb90-ece8113a7590	0ca36331-1393-48be-b0f4-b41d07e7cd49	ab0c28ab-215b-484f-a294-63197cd5d1c5	ALLOW	2026-01-30 00:05:41.730722+00
94808f84-a2fb-4f86-bd6c-cd925598248c	0ca36331-1393-48be-b0f4-b41d07e7cd49	f0d3536e-56a1-4a2e-82d0-8f78306a36bd	ALLOW	2026-01-30 00:05:41.730722+00
5d6cedf6-0c44-43ff-84d9-cf139ae1ff7a	0ca36331-1393-48be-b0f4-b41d07e7cd49	2464590f-a6db-4ef7-98b2-5260db2c713d	ALLOW	2026-01-30 00:05:41.730722+00
8b0ee875-d035-4b4f-b1b6-5b1245327cfa	0ca36331-1393-48be-b0f4-b41d07e7cd49	90ce1518-17e5-455e-a1f2-5eb260fc515b	ALLOW	2026-01-30 00:05:41.730722+00
c39509b2-dbf8-4aee-9467-2ad2fb883433	0ca36331-1393-48be-b0f4-b41d07e7cd49	14a4b32a-236e-4df4-b688-403e7c30f869	ALLOW	2026-01-30 00:05:41.730722+00
1f45d766-befd-4429-9c3a-dd16bf4b2d93	0ca36331-1393-48be-b0f4-b41d07e7cd49	f8b297b7-efed-4740-a42d-78c67aaed679	ALLOW	2026-01-30 00:05:41.730722+00
3cf309e2-37f6-4eec-8c1f-2e0ba6c6236f	0ca36331-1393-48be-b0f4-b41d07e7cd49	69ccf11a-5be5-4924-bdf6-c75abb0d7a1a	ALLOW	2026-01-30 00:05:41.730722+00
2d646eaa-c87c-4760-8d30-5115ee57b3b8	0ca36331-1393-48be-b0f4-b41d07e7cd49	2dcad9a8-25b0-4cb6-b3d6-95223e1e81da	ALLOW	2026-01-30 00:05:41.730722+00
c00bab08-e621-405b-b006-19c95db4edda	0ca36331-1393-48be-b0f4-b41d07e7cd49	c99f9d36-dc2a-4144-9c31-da03ff702ca0	ALLOW	2026-01-30 00:05:41.730722+00
cbe919d2-178b-4df0-9085-c84b3201c0e1	0ca36331-1393-48be-b0f4-b41d07e7cd49	970309fe-cedf-484c-8caa-52b1967c4c28	ALLOW	2026-01-30 00:05:41.730722+00
875a6739-1c0c-44c4-a9c2-afc6c25584cb	0ca36331-1393-48be-b0f4-b41d07e7cd49	1db3e8dc-cafd-4a15-96f4-49924f01f191	ALLOW	2026-01-30 00:05:41.730722+00
88e11968-c940-42a2-aaea-f5af202e0070	0ca36331-1393-48be-b0f4-b41d07e7cd49	7da820fe-aecc-4a58-bfe2-a70c6049dcce	ALLOW	2026-01-30 00:05:41.730722+00
2102f1ce-0b1e-4fa4-90a6-ad93c8354ea6	0ca36331-1393-48be-b0f4-b41d07e7cd49	de186c8e-e00a-415f-a0df-4d9b7c677b9d	ALLOW	2026-01-30 00:05:41.730722+00
0fd4de61-74fe-4388-8d0e-58725ba8ebdf	231da65a-3870-4908-a5fe-350380627ed2	25716ced-e201-45fd-bcfd-8e872be07e63	ALLOW	2026-01-30 00:05:41.741647+00
b4e6093c-ef38-4f03-9ce5-1dac9b984ee6	231da65a-3870-4908-a5fe-350380627ed2	2a5b41d5-0131-4272-a2f2-9158438693e7	ALLOW	2026-01-30 00:05:41.741647+00
841dcf25-ee48-43c0-8daa-3785178f4676	231da65a-3870-4908-a5fe-350380627ed2	ecd4582c-c751-475d-af73-311ec1752356	ALLOW	2026-01-30 00:05:41.741647+00
862bf6e1-ad3d-4608-b820-563ab4a6d298	231da65a-3870-4908-a5fe-350380627ed2	f934b0e0-66cd-444e-a1af-3b823a960771	ALLOW	2026-01-30 00:05:41.741647+00
fe60ca8b-23d5-48e2-9ff1-ac76ea918488	231da65a-3870-4908-a5fe-350380627ed2	f0d3536e-56a1-4a2e-82d0-8f78306a36bd	ALLOW	2026-01-30 00:05:41.741647+00
42cccb49-2f94-4131-89dd-fcc55a21c1c5	231da65a-3870-4908-a5fe-350380627ed2	2464590f-a6db-4ef7-98b2-5260db2c713d	ALLOW	2026-01-30 00:05:41.741647+00
eaba85ff-5ce5-4a6d-bf3e-070fa888f706	231da65a-3870-4908-a5fe-350380627ed2	90ce1518-17e5-455e-a1f2-5eb260fc515b	ALLOW	2026-01-30 00:05:41.741647+00
6a894464-cc47-485c-9d04-0da825c0226b	231da65a-3870-4908-a5fe-350380627ed2	14a4b32a-236e-4df4-b688-403e7c30f869	ALLOW	2026-01-30 00:05:41.741647+00
c5b8e6ae-b261-4b5a-abf3-32d695b0257e	231da65a-3870-4908-a5fe-350380627ed2	970309fe-cedf-484c-8caa-52b1967c4c28	ALLOW	2026-01-30 00:05:41.741647+00
5126932f-9385-4298-892c-44895b648ddb	231da65a-3870-4908-a5fe-350380627ed2	7da820fe-aecc-4a58-bfe2-a70c6049dcce	ALLOW	2026-01-30 00:05:41.741647+00
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, code, name, display_name, scope, description, is_active, created_at, updated_at) FROM stdin;
a8613649-0857-4f6a-8589-45580a027f22	SUPER_ADMIN	SUPER_ADMIN	Super Admin	SYSTEM	System administrator with full access	t	2026-01-30 00:05:41.062057+00	2026-01-30 00:05:41.062057+00
23b656a9-27b4-4ffb-a00b-9dc0d798f4d3	BILLING_ADMIN	BILLING_ADMIN	Billing Admin	SYSTEM	Manages billing and subscriptions	t	2026-01-30 00:05:41.062057+00	2026-01-30 00:05:41.062057+00
9bffe53a-a928-4b51-b6a7-e08400b0eef4	SUPPORT_AGENT	SUPPORT_AGENT	Support Agent	SYSTEM	Customer support representative	t	2026-01-30 00:05:41.062057+00	2026-01-30 00:05:41.062057+00
893a1f71-b524-4995-91a0-c1f44db37066	FREELANCER	FREELANCER	Freelancer	SYSTEM	Independent user without organization	t	2026-01-30 00:05:41.062057+00	2026-01-30 00:05:41.062057+00
fdb82da8-4d0c-4219-aaf9-09dc5d3a9bcd	OWNER	OWNER	Owner	ORGANIZATION	Farming organization owner	t	2026-01-30 00:05:41.073059+00	2026-01-30 00:05:41.073059+00
ee2d80b4-5aa7-4955-9170-0f626194deda	ADMIN	ADMIN	Admin	ORGANIZATION	Farming organization administrator	t	2026-01-30 00:05:41.073059+00	2026-01-30 00:05:41.073059+00
2a4340f7-7832-478b-9729-a7705e4cd3b1	MANAGER	MANAGER	Manager	ORGANIZATION	Farming organization manager	t	2026-01-30 00:05:41.073059+00	2026-01-30 00:05:41.073059+00
aa22c090-2bef-4796-96e9-885a3c206545	SUPERVISOR	SUPERVISOR	Supervisor	ORGANIZATION	Farming organization supervisor	t	2026-01-30 00:05:41.073059+00	2026-01-30 00:05:41.073059+00
c73b0952-76fb-4651-9914-2a90c0204945	WORKER	WORKER	Worker	ORGANIZATION	Farming organization worker	t	2026-01-30 00:05:41.073059+00	2026-01-30 00:05:41.073059+00
a98b7297-3bd8-4084-8dd4-ca156371f1c5	FSP_OWNER	FSP_OWNER	FSP Owner	ORGANIZATION	FSP organization owner	t	2026-01-30 00:05:41.084598+00	2026-01-30 00:05:41.084598+00
86b35eb9-6131-404a-ad7a-44bf2ddbd6c1	FSP_ADMIN	FSP_ADMIN	FSP Admin	ORGANIZATION	FSP organization administrator	t	2026-01-30 00:05:41.084598+00	2026-01-30 00:05:41.084598+00
58d7088d-dde1-4bf6-b0c9-5dbde555e46c	FSP_MANAGER	FSP_MANAGER	FSP Manager	ORGANIZATION	FSP organization manager	t	2026-01-30 00:05:41.084598+00	2026-01-30 00:05:41.084598+00
b56b143c-ecb1-41b7-a21b-ccd6fd7e11f9	FSP_SUPERVISOR	FSP_SUPERVISOR	FSP Supervisor	ORGANIZATION	FSP organization supervisor	t	2026-01-30 00:05:41.084598+00	2026-01-30 00:05:41.084598+00
c3d36b6d-6bb1-435c-8634-9316f42c09a0	SENIOR_CONSULTANT	SENIOR_CONSULTANT	Senior Consultant	ORGANIZATION	Senior consultant for FSP	t	2026-01-30 00:05:41.095832+00	2026-01-30 00:05:41.095832+00
0ca36331-1393-48be-b0f4-b41d07e7cd49	CONSULTANT	CONSULTANT	Consultant	ORGANIZATION	Consultant for FSP	t	2026-01-30 00:05:41.095832+00	2026-01-30 00:05:41.095832+00
231da65a-3870-4908-a5fe-350380627ed2	TECHNICAL_ANALYST	TECHNICAL_ANALYST	Technical Analyst	ORGANIZATION	Technical analyst for FSP	t	2026-01-30 00:05:41.095832+00	2026-01-30 00:05:41.095832+00
\.


--
-- Data for Name: schedule_change_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedule_change_log (id, schedule_id, trigger_type, trigger_reference_id, change_type, task_id, task_details_before, task_details_after, change_description, is_applied, applied_at, applied_by, created_at, created_by) FROM stdin;
\.


--
-- Data for Name: schedule_tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedule_tasks (id, schedule_id, task_id, due_date, status, completed_date, task_details, notes, created_at, updated_at, created_by, updated_by, task_name) FROM stdin;
ab11d057-2573-4483-bd3b-13ab5c921cb7	3ec9e158-42cf-40f3-851d-04a7c3216f41	f6d249bf-44ce-48df-8b85-87849abb420f	2026-01-30	NOT_STARTED	\N	{"input_items": [{"quantity": 12300.0, "input_item_id": "748c9b60-5f96-4145-a656-07f2fffdeab1", "quantity_unit_id": "08607b68-5102-45f3-a0e8-d0da2686b742"}, {"quantity": 9225.0, "input_item_id": "cd016288-5777-4cb2-ae8e-020efc8e0ef1", "quantity_unit_id": "08607b68-5102-45f3-a0e8-d0da2686b742"}]}	Apply before planting	2026-01-30 10:10:04.132054+00	2026-01-30 10:10:04.132054+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
12df915b-bea2-4405-9bac-33708792ae4b	3ec9e158-42cf-40f3-851d-04a7c3216f41	654439a3-9d92-4be5-b0ad-0a01a7fb776f	2026-02-04	NOT_STARTED	\N	{"machinery": {"equipment_type": "tractor", "estimated_hours": 430.5}}	Deep ploughing required	2026-01-30 10:10:04.132054+00	2026-01-30 10:10:04.132054+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
e168890e-bf70-400d-8bcf-25e281bf73ac	3ec9e158-42cf-40f3-851d-04a7c3216f41	99530824-fba5-42a8-9529-619692a89acd	2026-02-05	NOT_STARTED	\N	{"concentration": {"ingredients": [{"input_item_id": null, "total_quantity": 296.15999999999997, "quantity_unit_id": null, "concentration_per_liter": 3}], "total_solution_volume": 98720.0, "total_solution_volume_unit_id": null}}	Apply around root zone	2026-01-30 10:10:04.132054+00	2026-01-30 10:10:04.132054+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
2c06ac74-39c2-4e66-8094-067b2891bb95	3ec9e158-42cf-40f3-851d-04a7c3216f41	e188c4a0-a402-4bf8-8bcd-0b381bf10195	2026-02-14	NOT_STARTED	\N	{"input_items": [{"quantity": 615.0, "input_item_id": "ef392715-3980-4a4a-9181-d87de2f4108f", "quantity_unit_id": "08607b68-5102-45f3-a0e8-d0da2686b742"}]}	Apply through drip irrigation	2026-01-30 10:10:04.132054+00	2026-01-30 10:10:04.132054+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
89075bc0-ee7e-4972-b644-65db94e2d418	3ec9e158-42cf-40f3-851d-04a7c3216f41	7da3b074-e1f1-4648-bf84-84133fe6c105	2026-02-16	NOT_STARTED	\N	{"concentration": {"ingredients": [], "total_solution_volume": 3690.0, "total_solution_volume_unit_id": null}}	Spray during early morning or evening	2026-01-30 10:10:04.132054+00	2026-01-30 10:10:04.132054+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
e9a6ebab-9163-4dae-876f-6873c2e060cd	3ec9e158-42cf-40f3-851d-04a7c3216f41	6d78b9e3-a9e3-40fb-9b0c-3c99a71d8290	2026-03-01	NOT_STARTED	\N	{"input_items": [{"quantity": 12340.0, "input_item_id": "748c9b60-5f96-4145-a656-07f2fffdeab1", "quantity_unit_id": null}]}	Apply around plant base	2026-01-30 10:10:04.132054+00	2026-01-30 10:10:04.132054+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
b548ce31-e70d-4a2a-8433-bae05b3e7dc9	3559bc04-25a8-411f-a967-459c07851b14	654439a3-9d92-4be5-b0ad-0a01a7fb776f	2026-02-04	NOT_STARTED	\N	{}	\N	2026-01-30 11:26:26.472705+00	2026-01-30 11:26:26.472705+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
dc69fb87-2fd2-482e-855e-979d1b2d93ab	3559bc04-25a8-411f-a967-459c07851b14	654439a3-9d92-4be5-b0ad-0a01a7fb776f	2026-02-11	NOT_STARTED	\N	{}	\N	2026-01-30 11:26:26.472705+00	2026-01-30 11:26:26.472705+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
2f848320-3f6d-4735-878d-f5eb36c6c253	a2ea30cb-57cf-4b04-9ab1-75f5f909e700	654439a3-9d92-4be5-b0ad-0a01a7fb776f	2026-02-12	NOT_STARTED	\N	{}	\N	2026-01-30 20:41:38.565+00	2026-01-30 20:41:38.565+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
f9930655-4fd4-4092-8c6d-6ea4102bd8b7	a2ea30cb-57cf-4b04-9ab1-75f5f909e700	654439a3-9d92-4be5-b0ad-0a01a7fb776f	2026-02-17	NOT_STARTED	\N	{}	\N	2026-01-30 20:41:38.565+00	2026-01-30 20:41:38.565+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
73d9cc3e-e666-41a6-b728-02441e8bc016	c07a8445-b16a-48cf-8a66-7553ea04a29b	654439a3-9d92-4be5-b0ad-0a01a7fb776f	2026-03-02	NOT_STARTED	\N	{}	\N	2026-02-03 15:37:56.916744+00	2026-02-03 15:37:56.916744+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
13badb96-ee5a-44b6-a5d6-5e8f335346df	c07a8445-b16a-48cf-8a66-7553ea04a29b	654439a3-9d92-4be5-b0ad-0a01a7fb776f	2026-03-07	NOT_STARTED	\N	{}	\N	2026-02-03 15:37:56.916744+00	2026-02-03 15:37:56.916744+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
9822764d-d288-4ed7-8532-77c15355fff6	9ae45d56-e3ac-4a46-a1e7-21bf8a793c8a	654439a3-9d92-4be5-b0ad-0a01a7fb776f	2026-05-03	MISSED	\N	{}	\N	2026-02-03 15:40:05.681367+00	2026-02-03 17:00:54.678092+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
b41611f9-0157-4635-999b-63aa9a9199e7	42b337aa-09da-43a2-b0f6-3f50ca83c417	654439a3-9d92-4be5-b0ad-0a01a7fb776f	2026-02-07	NOT_STARTED	\N	{"input_items": [{"dosage": {"per": "PLANT", "unit": "g", "amount": 12}, "quantity": 1476.0, "input_item_id": "0b9f39be-d821-4071-b231-1d57bb67ee39", "quantity_unit_id": "g", "application_method_id": "39dad72b-ab7c-4823-957f-0dbba2f2d4db"}]}	\N	2026-02-06 11:17:05.547343+00	2026-02-06 11:17:05.547343+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
2716895e-7555-4301-9b71-0d9075fcd477	42b337aa-09da-43a2-b0f6-3f50ca83c417	654439a3-9d92-4be5-b0ad-0a01a7fb776f	2026-02-09	NOT_STARTED	\N	{"input_items": [{"dosage": {"per": "ACRE", "unit": "L", "amount": 12}, "quantity": 144.0, "input_item_id": "59b05679-3c61-4744-9c73-2e0b4268d322", "quantity_unit_id": "L", "application_method_id": "b6b69773-e056-45eb-bdea-a343b749e0a7"}]}	\N	2026-02-06 11:17:05.547343+00	2026-02-06 11:17:05.547343+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
\.


--
-- Data for Name: schedule_template_tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedule_template_tasks (id, schedule_template_id, task_id, day_offset, task_details_template, sort_order, notes, created_at, updated_at, created_by, updated_by, task_name) FROM stdin;
f0290513-d101-4598-b195-3e0fd63cf890	bc9bae1f-67b4-4ebc-a5c4-c74d2d785412	f6d249bf-44ce-48df-8b85-87849abb420f	0	{"input_items": [{"quantity": 100, "input_item_id": "748c9b60-5f96-4145-a656-07f2fffdeab1", "quantity_unit_id": "08607b68-5102-45f3-a0e8-d0da2686b742", "calculation_basis": "per_acre"}, {"quantity": 75, "input_item_id": "cd016288-5777-4cb2-ae8e-020efc8e0ef1", "quantity_unit_id": "08607b68-5102-45f3-a0e8-d0da2686b742", "calculation_basis": "per_acre"}]}	1	Apply before planting	2026-01-30 00:05:41.530411+00	2026-01-30 00:05:41.530411+00	\N	\N	\N
dfcc1442-a8bf-4385-bced-a787ab174bfe	bc9bae1f-67b4-4ebc-a5c4-c74d2d785412	654439a3-9d92-4be5-b0ad-0a01a7fb776f	5	{"machinery": {"equipment_type": "tractor", "estimated_hours": 3.5, "calculation_basis": "per_acre"}}	2	Deep ploughing required	2026-01-30 00:05:41.541166+00	2026-01-30 00:05:41.541166+00	\N	\N	\N
5630f996-f0c7-43cf-8405-2dafcd8ee462	bc9bae1f-67b4-4ebc-a5c4-c74d2d785412	99530824-fba5-42a8-9529-619692a89acd	6	{"concentration": {"ingredients": [{"input_item_id": null, "concentration_unit_id": null, "concentration_per_liter": 3}], "solution_volume": 80, "calculation_basis": "per_plant", "solution_volume_unit_id": null}}	3	Apply around root zone	2026-01-30 00:05:41.551799+00	2026-01-30 00:05:41.551799+00	\N	\N	\N
c6911364-7ced-44f7-a728-57330d3c9f1a	bc9bae1f-67b4-4ebc-a5c4-c74d2d785412	e188c4a0-a402-4bf8-8bcd-0b381bf10195	15	{"input_items": [{"quantity": 5, "input_item_id": "ef392715-3980-4a4a-9181-d87de2f4108f", "quantity_unit_id": "08607b68-5102-45f3-a0e8-d0da2686b742", "calculation_basis": "per_acre"}]}	4	Apply through drip irrigation	2026-01-30 00:05:41.562434+00	2026-01-30 00:05:41.562434+00	\N	\N	\N
091f414a-d6f2-4fef-a350-de65c7878673	bc9bae1f-67b4-4ebc-a5c4-c74d2d785412	7da3b074-e1f1-4648-bf84-84133fe6c105	17	{"concentration": {"ingredients": [], "solution_volume": 30, "calculation_basis": "per_acre", "solution_volume_unit_id": null}}	5	Spray during early morning or evening	2026-01-30 00:05:41.573093+00	2026-01-30 00:05:41.573093+00	\N	\N	\N
5b9f8d1f-5312-4c75-a9d3-0686b942b732	bc9bae1f-67b4-4ebc-a5c4-c74d2d785412	6d78b9e3-a9e3-40fb-9b0c-3c99a71d8290	30	{"input_items": [{"quantity": 10, "input_item_id": "748c9b60-5f96-4145-a656-07f2fffdeab1", "quantity_unit_id": null, "calculation_basis": "per_plant"}]}	6	Apply around plant base	2026-01-30 00:05:41.583789+00	2026-01-30 00:05:41.583789+00	\N	\N	\N
e79f018a-740c-4495-9e54-8f9826ab0632	ada14f1f-c7f5-4975-bdea-2769788da9c9	654439a3-9d92-4be5-b0ad-0a01a7fb776f	5	{}	1	\N	2026-01-30 00:08:38.941435+00	2026-01-30 00:08:38.941435+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	\N
22e42bc1-35f4-4706-a2ab-30a9ba381df3	cd39d453-8aa5-495d-81e8-572aa1862651	654439a3-9d92-4be5-b0ad-0a01a7fb776f	5	{"notes": null, "dosage_per": "ACRE", "dosage_unit": "kg", "dosage_amount": 0}	0	\N	2026-01-30 10:43:42.196163+00	2026-01-30 10:43:42.196163+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
985bf8bc-d6c8-49db-8dde-e24ed7dc34c2	cd39d453-8aa5-495d-81e8-572aa1862651	654439a3-9d92-4be5-b0ad-0a01a7fb776f	12	{"notes": "123123", "dosage_per": "PLANT", "dosage_unit": "kg", "dosage_amount": 123, "input_item_id": "0b9f39be-d821-4071-b231-1d57bb67ee39", "application_method_id": "b6b69773-e056-45eb-bdea-a343b749e0a7"}	0	\N	2026-01-30 10:43:42.196163+00	2026-01-30 10:43:42.196163+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
6f8a47ce-86f4-46d3-8006-40d7f45ca990	98a8ee01-661f-406f-b816-4f512b3cc3e8	654439a3-9d92-4be5-b0ad-0a01a7fb776f	0	{"dosage_per": "ACRE", "dosage_unit": "kg", "dosage_amount": 0}	0	\N	2026-01-30 11:43:47.455756+00	2026-01-30 11:43:47.455756+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
6b36854a-2f77-4acb-a09c-287b2ad3fcba	98a8ee01-661f-406f-b816-4f512b3cc3e8	654439a3-9d92-4be5-b0ad-0a01a7fb776f	0	{"notes": "gazfsgdfgbv", "dosage_per": "LITER_WATER", "dosage_unit": "kg", "dosage_amount": 200, "input_item_id": "748c9b60-5f96-4145-a656-07f2fffdeab1", "input_item_name": "Urea", "concentration_amount": 345, "application_method_id": "b6b69773-e056-45eb-bdea-a343b749e0a7", "application_method_name": "Foliar Spray"}	0	\N	2026-01-30 11:43:47.455756+00	2026-01-30 11:43:47.455756+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
1b6ebc3b-5640-48f9-bd8d-748932030a7e	2bba72e7-0d5b-49aa-b3f3-9036a893f99b	654439a3-9d92-4be5-b0ad-0a01a7fb776f	1	{"notes": "asdasdasd", "dosage_per": "ACRE", "dosage_unit": "kg", "dosage_amount": 10, "input_item_id": "748c9b60-5f96-4145-a656-07f2fffdeab1", "input_item_name": "Urea", "application_method_id": "39dad72b-ab7c-4823-957f-0dbba2f2d4db", "application_method_name": "Soil Application"}	0	\N	2026-01-30 20:40:22.37489+00	2026-01-30 20:40:22.37489+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
a406fd12-4253-4452-86bf-b9dbb0969c16	2bba72e7-0d5b-49aa-b3f3-9036a893f99b	654439a3-9d92-4be5-b0ad-0a01a7fb776f	6	{"notes": "asdasdasd", "dosage_per": "PLANT", "dosage_unit": "kg", "dosage_amount": 23, "input_item_id": "bf2e83f7-398c-469a-bcd5-139e5b9b0f8e", "input_item_name": "Admire", "concentration_amount": 23, "application_method_id": "b6b69773-e056-45eb-bdea-a343b749e0a7", "application_method_name": "Foliar Spray"}	0	\N	2026-01-30 20:40:22.37489+00	2026-01-30 20:40:22.37489+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
5c85c764-0b0f-4967-bb04-1e931992410a	9f44eb7f-0992-4a03-a694-8ab73964ffb5	654439a3-9d92-4be5-b0ad-0a01a7fb776f	2	{"task_name": "Premium Fertilization", "dosage_per": "ACRE", "dosage_unit": "kg", "dosage_amount": 2.5, "input_item_id": "748c9b60-5f96-4145-a656-07f2fffdeab1", "input_item_name": "Urea", "application_method_id": "72368c0f-2358-4034-9279-d5945398aebd", "application_method_name": "Foliar Spray"}	0	\N	2026-02-03 15:40:04.068498+00	2026-02-03 15:40:04.068498+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
371ca5ba-2966-4018-94f8-53ab61a45fd0	b61728f5-5d7f-4a77-8a96-021ed53e9fd0	654439a3-9d92-4be5-b0ad-0a01a7fb776f	1	{"notes": "Nothing ", "task_name": "tast1", "dosage_per": "PLANT", "dosage_unit": "g", "dosage_amount": 12, "input_item_id": "0b9f39be-d821-4071-b231-1d57bb67ee39", "input_item_name": "Ammonium Sulphate", "application_method_id": "39dad72b-ab7c-4823-957f-0dbba2f2d4db", "application_method_name": "Soil Application"}	0	\N	2026-02-06 11:16:00.13356+00	2026-02-06 11:16:00.13356+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
f8c3f1c4-045d-400d-a404-801df8386f99	b61728f5-5d7f-4a77-8a96-021ed53e9fd0	654439a3-9d92-4be5-b0ad-0a01a7fb776f	3	{"notes": "nothign", "task_name": "Tast 2", "dosage_per": "ACRE", "dosage_unit": "L", "dosage_amount": 12, "input_item_id": "59b05679-3c61-4744-9c73-2e0b4268d322", "input_item_name": "Actara", "concentration_amount": 12, "application_method_id": "b6b69773-e056-45eb-bdea-a343b749e0a7", "application_method_name": "Foliar Spray"}	0	\N	2026-02-06 11:16:00.13356+00	2026-02-06 11:16:00.13356+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
\.


--
-- Data for Name: schedule_template_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedule_template_translations (id, schedule_template_id, language_code, name, description, created_at) FROM stdin;
ace1d981-aba3-4e47-9072-7f537cec14ad	bc9bae1f-67b4-4ebc-a5c4-c74d2d785412	en	Tomato Standard Package	Complete fertigation and pest management schedule for tomato cultivation (1 acre, 400 plants)	2026-01-30 00:05:41.519542+00
03b0a43c-8ecb-4812-850b-bfbdd7df30b1	bc9bae1f-67b4-4ebc-a5c4-c74d2d785412	ta	தக்காளி நிலையான தொகுப்பு	தக்காளி சாகுபடிக்கான முழுமையான நீர் உரம் மற்றும் பூச்சி மேலாண்மை அட்டவணை (1 ஏக்கர், 400 செடிகள்)	2026-01-30 00:05:41.519542+00
fc31366c-a53b-4ce1-ab85-0eeae204382d	ada14f1f-c7f5-4975-bdea-2769788da9c9	en	Wheat 120-Day Plan	Standard schedule for Wheat 120-Day Plan	2026-01-30 00:08:38.941435+00
ed18eec3-8e17-4a5f-9e3c-62501d85d5e5	cd39d453-8aa5-495d-81e8-572aa1862651	en	Tomato Fertilization Cycle	Standard schedule for Tomato Fertilization Cycle	2026-01-30 00:08:38.951684+00
25d0c993-a3d6-428b-b971-f6aca48a7b5e	98a8ee01-661f-406f-b816-4f512b3cc3e8	en	Standard Soil Audit	Schedule task for soil audit execution	2026-01-30 00:09:33.180136+00
49cabf7b-e855-4352-83bc-6c7b741d31d6	2bba72e7-0d5b-49aa-b3f3-9036a893f99b	en	test1	asdasdasdasdasdasd	2026-01-30 20:40:22.37489+00
e8b02e4a-e965-461f-86c5-cc4c8aaa9c89	9f44eb7f-0992-4a03-a694-8ab73964ffb5	en	Live Verification Template	Tomato growth verification	2026-02-03 15:40:04.068498+00
1bc40a40-3ad1-4ded-ab64-fa2038f85011	b61728f5-5d7f-4a77-8a96-021ed53e9fd0	en	test1212	test1212	2026-02-06 11:16:00.13356+00
\.


--
-- Data for Name: schedule_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedule_templates (id, code, crop_type_id, crop_variety_id, is_system_defined, owner_org_id, version, is_active, notes, created_at, updated_at, created_by, updated_by) FROM stdin;
bc9bae1f-67b4-4ebc-a5c4-c74d2d785412	TOMATO_STANDARD_PACKAGE	420b1d7d-7f33-429c-9da3-69ecc4d42145	\N	t	\N	1	t	Standard package of practice for tomato cultivation	2026-01-30 00:05:41.509073+00	2026-01-30 00:05:41.509073+00	\N	\N
ada14f1f-c7f5-4975-bdea-2769788da9c9	WHEAT_120_PLAN	\N	\N	f	8b411c61-9885-4672-ba08-e45709934575	1	t	\N	2026-01-30 00:08:38.941435+00	2026-01-30 00:08:38.941435+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
cd39d453-8aa5-495d-81e8-572aa1862651	tomato_fertilization_cycle	\N	\N	f	8b411c61-9885-4672-ba08-e45709934575	1	t	\N	2026-01-30 00:08:38.951684+00	2026-01-30 10:43:42.196163+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
98a8ee01-661f-406f-b816-4f512b3cc3e8	standard_soil_audit	\N	\N	f	8b411c61-9885-4672-ba08-e45709934575	1	t	Schedule for Soil Audit Work Order	2026-01-30 00:09:33.180136+00	2026-01-30 11:43:47.455756+00	08c368c7-0ea2-4dad-a5fe-5e8e180b0b44	3f3a3a39-d867-45a8-b901-74a7e27c95f3
2bba72e7-0d5b-49aa-b3f3-9036a893f99b	test1	\N	\N	f	8b411c61-9885-4672-ba08-e45709934575	1	t	\N	2026-01-30 20:40:22.37489+00	2026-01-30 20:40:22.37489+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
9f44eb7f-0992-4a03-a694-8ab73964ffb5	VERIFY_V1	420b1d7d-7f33-429c-9da3-69ecc4d42145	\N	f	8b411c61-9885-4672-ba08-e45709934575	1	t	\N	2026-02-03 15:40:04.068498+00	2026-02-03 15:40:04.068498+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
b61728f5-5d7f-4a77-8a96-021ed53e9fd0	test1212	\N	\N	f	8b411c61-9885-4672-ba08-e45709934575	1	t	\N	2026-02-06 11:16:00.13356+00	2026-02-06 11:16:00.13356+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
\.


--
-- Data for Name: schedules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedules (id, crop_id, name, description, template_id, template_parameters, is_active, created_at, updated_at, created_by, updated_by) FROM stdin;
7e84df94-6155-46b9-a5e3-704fa77bf4ba	22086444-0094-4b87-bb63-a24c03614344	this is for the test of rice 	\N	\N	{"area": 234, "start_date": "2026-01-30", "plant_count": 0, "area_unit_id": "27c45cfe-3f18-417c-be00-de9a0d4ddcf4"}	t	2026-01-30 10:05:35.884496+00	2026-01-30 10:05:35.884496+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
3ec9e158-42cf-40f3-851d-04a7c3216f41	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	From fsp	Created from template: TOMATO_STANDARD_PACKAGE	bc9bae1f-67b4-4ebc-a5c4-c74d2d785412	{"area": 123, "start_date": "2026-01-30", "plant_count": 1234, "area_unit_id": "1c6b90ac-ff6b-4c5f-be90-5f33c91725d4"}	t	2026-01-30 10:10:04.132054+00	2026-01-30 10:10:04.132054+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
3559bc04-25a8-411f-a967-459c07851b14	22086444-0094-4b87-bb63-a24c03614344	for the meeting on 30	Created from template: tomato_fertilization_cycle	cd39d453-8aa5-495d-81e8-572aa1862651	{"area": 234, "start_date": "2026-01-30", "plant_count": 234234, "area_unit_id": "27c45cfe-3f18-417c-be00-de9a0d4ddcf4"}	t	2026-01-30 11:26:26.472705+00	2026-01-30 11:26:26.472705+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
a2ea30cb-57cf-4b04-9ab1-75f5f909e700	22086444-0094-4b87-bb63-a24c03614344	scedule for sagdara	Created from template: test1	2bba72e7-0d5b-49aa-b3f3-9036a893f99b	{"area": 123, "start_date": "2026-02-11", "plant_count": 234234, "area_unit_id": "27c45cfe-3f18-417c-be00-de9a0d4ddcf4"}	t	2026-01-30 20:41:38.565+00	2026-01-30 20:41:38.565+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
9a9ac45d-9b05-4125-b272-e628a124b3de	22086444-0094-4b87-bb63-a24c03614344	Ywf	\N	\N	{"area": 34, "start_date": "2026-01-15", "plant_count": 43, "area_unit_id": "27c45cfe-3f18-417c-be00-de9a0d4ddcf4"}	t	2026-01-31 01:55:22.71444+00	2026-01-31 01:55:22.71444+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
c07a8445-b16a-48cf-8a66-7553ea04a29b	22086444-0094-4b87-bb63-a24c03614344	Verification Schedule	Created from template: test1	2bba72e7-0d5b-49aa-b3f3-9036a893f99b	{"area": 10.5, "start_date": "2026-03-01", "area_unit_id": "27c45cfe-3f18-417c-be00-de9a0d4ddcf4"}	t	2026-02-03 15:37:56.916744+00	2026-02-03 15:37:56.916744+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
9ae45d56-e3ac-4a46-a1e7-21bf8a793c8a	22086444-0094-4b87-bb63-a24c03614344	Final Verification Schedule V1	Created from template: VERIFY_V1	9f44eb7f-0992-4a03-a694-8ab73964ffb5	{"area": 20, "start_date": "2026-05-01", "area_unit_id": "27c45cfe-3f18-417c-be00-de9a0d4ddcf4"}	t	2026-02-03 15:40:05.681367+00	2026-02-03 15:40:05.681367+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
42b337aa-09da-43a2-b0f6-3f50ca83c417	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	test1212	Created from template: test1212	b61728f5-5d7f-4a77-8a96-021ed53e9fd0	{"area": 12, "start_date": "2026-02-06", "plant_count": 123, "area_unit_id": "1c6b90ac-ff6b-4c5f-be90-5f33c91725d4"}	t	2026-02-06 11:17:05.547343+00	2026-02-06 11:17:05.547343+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
\.


--
-- Data for Name: section_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.section_translations (id, section_id, language_code, name, description, created_at) FROM stdin;
206ade97-8de9-4de8-9a75-0875941a8677	d0c1ff07-1a65-452b-85ca-88cb673d1755	en	Plant Health	\N	2026-01-30 00:05:41.467162+00
aa7cdd5b-35e5-4bb2-8aac-7f7e78388c79	b1af410d-1ef3-4455-b17d-69b8c5a7ea26	en	Soil Condition	\N	2026-01-30 00:05:41.467162+00
d0040d67-bd48-4cf3-a7f0-0c94fe63c7f4	1d21dc48-2699-4839-88fc-63a562160da0	en	Pest & Disease	\N	2026-01-30 00:05:41.467162+00
1123eb09-c681-4ab2-a63f-3b4edf7be6a8	4b01a593-7ec0-4756-b80d-0d69667a4f1c	en	Irrigation	\N	2026-01-30 00:05:41.467162+00
def4f162-4abe-4f6a-9465-9443bfdfb6c5	d0c1ff07-1a65-452b-85ca-88cb673d1755	ta	தாவர ஆரோக்கியம்	\N	2026-01-30 00:05:41.467162+00
fc0855ba-d543-47dd-9c20-f219caa79af5	b1af410d-1ef3-4455-b17d-69b8c5a7ea26	ta	மண் நிலை	\N	2026-01-30 00:05:41.467162+00
41477a7f-8d3a-4403-bb92-fdd2ddc440b4	1d21dc48-2699-4839-88fc-63a562160da0	ta	பூச்சி & நோய்	\N	2026-01-30 00:05:41.467162+00
6899bb17-9ef1-42e9-9595-baf8855727e9	4b01a593-7ec0-4756-b80d-0d69667a4f1c	ta	நீர்ப்பாசனம்	\N	2026-01-30 00:05:41.467162+00
e6ed7359-8d8b-4ac8-9f9d-f42229f98a99	b3aba901-3184-45be-b815-2017625d5011	en	points		2026-01-30 00:21:12.952927+00
a2590b72-4de9-404f-9e2b-feba94d4aa3e	fa6dd296-6f04-4b0f-ad84-bc1947cf953d	en	sectpn 1		2026-01-30 20:36:02.122639+00
ad66a619-eecb-44db-8120-b797bd0916f2	68deb228-aee8-4fff-8bb5-d285ac1f7d89	en	New Section		2026-01-30 20:36:02.822372+00
d4fe275d-5338-48ff-8b83-f7e12a6e9b43	44c5bd87-8f49-4d80-928c-e7e8e2e2f432	en	Test Section	Desc	2026-02-01 10:30:00.703787+00
6925eeba-5eed-4701-bc4d-eb8a355fd6bf	106e6e0b-658d-48e6-8232-d099c7cdaca2	en	Test Section	Desc	2026-02-01 10:31:21.279674+00
78b8ff81-c886-480e-bbf0-7d5224b00bf4	c09aa38d-26fd-4cbb-af97-1aac41916ca5	en	Test Section	Desc	2026-02-01 10:32:49.358953+00
1045cbce-fe47-49e0-9b5e-d9613a6e79f6	457af481-e0fc-4884-9141-9c2bb0828752	en	Test Section	Desc	2026-02-01 10:33:10.062203+00
008c5190-bfd5-4b13-b097-14c9b8028ebf	bec4a33a-c2f5-4bd5-b0b8-3662ff6a2239	en	Test Section	Desc	2026-02-01 10:33:32.093845+00
ebcc5781-ea91-4041-a7a4-bf9dddfb3073	3e3b1f73-e82a-4dfd-bb7f-b3a902093c4f	en	Test Section	Desc	2026-02-01 10:34:04.488899+00
4d5b7074-2887-442e-b0e5-4305f2c9fc7f	8abedb5c-b0bf-46e1-97b5-d970f77f4866	en	Test Section	Desc	2026-02-01 10:34:22.043803+00
31fc376c-da3d-48b7-8b60-60ea29b9672f	0cd7b48c-642c-420e-b12f-87a256c5b99c	en	Test Section	Desc	2026-02-01 10:34:42.630315+00
90c8d818-db92-4be7-97ed-c5ea1cd0bac1	24580d64-53bb-4727-b455-19e1271f5d54	en	Test Section	Desc	2026-02-01 10:35:07.970745+00
77508fdb-5a8c-43aa-97ae-352293fdffc5	1bb7d226-89f2-4474-b39c-fc2fa66a1f03	en	Test Section	Desc	2026-02-01 10:35:48.169682+00
0f99445f-ebb9-4a36-8763-c5a01fb30666	a5665aaf-aa67-437c-b997-4e7a7f655db4	en	Test Section	Desc	2026-02-01 10:36:44.02709+00
a8a8c992-989f-4fff-947c-c4f179c4a9ba	1f3556bc-f866-4104-99a3-b16d256cf44c	en	Test Section	Desc	2026-02-01 10:37:05.219976+00
6eb49177-5648-4999-b82e-cff02941c3f3	5099dbd1-f710-4e0f-9175-0fd2ad1333ca	en	Test Section	Desc	2026-02-01 10:38:13.393018+00
377b3621-3052-43d7-8a99-300fcf2a8d05	fd36c2ac-bcfd-4aae-ad65-1e7780e7b697	en	Test Section	Desc	2026-02-01 10:38:59.195024+00
46ef5d6e-a438-4ac3-a2d8-de45370e971d	4da68809-e9cb-498a-b97c-1c0a5d0ca109	en	Test Section	Desc	2026-02-01 11:01:39.695961+00
2a3d02ee-9cfc-4b5a-883d-f3ef57668a60	0588aa5f-54d5-4544-a0b6-9535a4787776	en	Test Section	Desc	2026-02-01 11:06:38.927241+00
19e5eae5-7ac6-4562-af74-409794bd676f	8d28777c-3ec1-401b-a3f7-abe8af032686	en	General Info		2026-02-05 19:49:07.46739+00
3514c62d-e122-4b61-90d7-2e9ddf574ee1	f8b05511-90f1-481c-aca8-168906684cea	en	Section 1	\N	2026-02-05 21:28:20.479325+00
026b1d96-c86f-4576-a55f-74130c0ba4d9	b0292705-1384-4b45-9d1a-ecf33ef7ed7e	en	Section 1	\N	2026-02-05 21:30:53.620969+00
06c0085e-86f6-4af0-beb2-0ca63dd145fd	bc41c3da-9a29-4ce5-834f-52fd21432ba8	en	Section 1	\N	2026-02-05 21:31:42.643456+00
cba6af3e-fdcc-4be4-bebf-5829facf6ff7	a300e7fd-5eb0-48a3-ba12-00b16750b2d0	en	Section 1	\N	2026-02-05 21:33:45.203857+00
31c6f155-df70-46dc-9ec8-9aa29071ede8	7957ddf4-2552-4349-92a5-eaa1cc60769e	en	Section 1	\N	2026-02-05 21:34:41.200243+00
5530e4ac-2148-4354-9779-db8e3ec90dad	26d6feb1-d647-4e02-a01f-af767914367f	en	Section 1	\N	2026-02-05 21:36:32.675647+00
7095fb9f-cbf7-41de-8fc7-2d7d348a42a7	d00e94a1-caa9-48f3-9db3-e4bac9b4c096	en	Section 1	\N	2026-02-05 21:39:33.679131+00
61af9611-f627-4c29-89d6-d1b3b9a9dcfa	900f4f8d-8d2a-465a-84c8-8659ce9eb7b9	en	Section 1	\N	2026-02-05 21:40:37.582584+00
923c5e65-4570-4444-b964-40c67b0495c6	45d63ea1-0e12-4bf3-b620-12d572fba1cd	en	Section 1	\N	2026-02-05 21:41:47.326337+00
2c1564ff-6272-4725-ba2a-e6329da5d4e5	813222ab-33b9-4937-a23c-bf6059a12713	en	Section 1	\N	2026-02-05 21:43:42.738659+00
7b9fdf1f-89df-4450-ab7d-6efa9b980b41	d33388e3-082c-4c2b-9885-85cfd4705373	en	Section 1	\N	2026-02-05 21:49:55.119532+00
24bcd278-1565-4576-9a87-b92cf481ae18	9123b919-fdbe-478d-9757-c06c16606b63	en	Section 1	\N	2026-02-05 21:52:18.881068+00
2fe4ea67-866c-4ac9-9675-d7c7a0d2d6e1	8ed4cf1b-282b-4ab8-8983-2209bd440373	en	Section 1	\N	2026-02-05 21:55:18.620729+00
\.


--
-- Data for Name: sections; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sections (id, code, is_system_defined, owner_org_id, is_active, created_at, updated_at, created_by, updated_by) FROM stdin;
d0c1ff07-1a65-452b-85ca-88cb673d1755	PLANT_HEALTH	t	\N	t	2026-01-30 00:05:41.456691+00	2026-01-30 00:05:41.456691+00	\N	\N
b1af410d-1ef3-4455-b17d-69b8c5a7ea26	SOIL_CONDITION	t	\N	t	2026-01-30 00:05:41.456691+00	2026-01-30 00:05:41.456691+00	\N	\N
1d21dc48-2699-4839-88fc-63a562160da0	PEST_DISEASE	t	\N	t	2026-01-30 00:05:41.456691+00	2026-01-30 00:05:41.456691+00	\N	\N
4b01a593-7ec0-4756-b80d-0d69667a4f1c	IRRIGATION	t	\N	t	2026-01-30 00:05:41.456691+00	2026-01-30 00:05:41.456691+00	\N	\N
b3aba901-3184-45be-b815-2017625d5011	SEC_324D_2520	f	8b411c61-9885-4672-ba08-e45709934575	t	2026-01-30 00:21:12.952927+00	2026-01-30 00:21:12.952927+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
fa6dd296-6f04-4b0f-ad84-bc1947cf953d	SEC_881A_0970	f	8b411c61-9885-4672-ba08-e45709934575	t	2026-01-30 20:36:02.122639+00	2026-01-30 20:36:02.122639+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
68deb228-aee8-4fff-8bb5-d285ac1f7d89	SEC_BE52_1676	f	8b411c61-9885-4672-ba08-e45709934575	t	2026-01-30 20:36:02.822372+00	2026-01-30 20:36:02.822372+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
44c5bd87-8f49-4d80-928c-e7e8e2e2f432	SEC_1769941800	f	bc9a3480-c0ad-43c6-ab08-5fc8362d34b2	t	2026-02-01 10:30:00.703787+00	2026-02-01 10:30:00.703787+00	d24c619c-0783-4510-949c-49445cea0202	d24c619c-0783-4510-949c-49445cea0202
106e6e0b-658d-48e6-8232-d099c7cdaca2	SEC_1769941881	f	db3950f7-2c3d-40ec-8646-9548956aa267	t	2026-02-01 10:31:21.279674+00	2026-02-01 10:31:21.279674+00	5b010aef-d0b8-40cc-bc0e-6b6c133cac49	5b010aef-d0b8-40cc-bc0e-6b6c133cac49
c09aa38d-26fd-4cbb-af97-1aac41916ca5	SEC_1769941969	f	9463b7f0-b657-467c-bc0e-0f21817e623c	t	2026-02-01 10:32:49.358953+00	2026-02-01 10:32:49.358953+00	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c
457af481-e0fc-4884-9141-9c2bb0828752	SEC_1769941990	f	1118a620-482f-4241-b722-35653792fda9	t	2026-02-01 10:33:10.062203+00	2026-02-01 10:33:10.062203+00	bf660c8b-3818-4cf7-85f1-3071c0a7943c	bf660c8b-3818-4cf7-85f1-3071c0a7943c
bec4a33a-c2f5-4bd5-b0b8-3662ff6a2239	SEC_1769942012	f	cbbff567-e72f-46ff-ad79-4cf26c3260c8	t	2026-02-01 10:33:32.093845+00	2026-02-01 10:33:32.093845+00	c7a092a7-d354-498d-b23a-d4802d99ccb4	c7a092a7-d354-498d-b23a-d4802d99ccb4
3e3b1f73-e82a-4dfd-bb7f-b3a902093c4f	SEC_1769942044	f	6bf71e9a-2b50-4a27-9ff9-972b5a52eb8e	t	2026-02-01 10:34:04.488899+00	2026-02-01 10:34:04.488899+00	2199f334-fccd-46ff-b45c-2cd81aadeca2	2199f334-fccd-46ff-b45c-2cd81aadeca2
8abedb5c-b0bf-46e1-97b5-d970f77f4866	SEC_1769942062	f	461445ad-b03d-418c-8049-49cbadf6519b	t	2026-02-01 10:34:22.043803+00	2026-02-01 10:34:22.043803+00	b46ab366-7dcb-4ee5-a558-dc328db04159	b46ab366-7dcb-4ee5-a558-dc328db04159
0cd7b48c-642c-420e-b12f-87a256c5b99c	SEC_1769942082	f	c6957a10-58cf-4f2d-ab85-b8b0dbd6ed7c	t	2026-02-01 10:34:42.630315+00	2026-02-01 10:34:42.630315+00	979cfcfd-a872-40df-8380-dbe81f29e7a5	979cfcfd-a872-40df-8380-dbe81f29e7a5
24580d64-53bb-4727-b455-19e1271f5d54	SEC_1769942107	f	36acd251-59ee-4f22-a3e3-f14e91a16706	t	2026-02-01 10:35:07.970745+00	2026-02-01 10:35:07.970745+00	810cc398-af79-4d96-9eee-af0f1bbf8683	810cc398-af79-4d96-9eee-af0f1bbf8683
1bb7d226-89f2-4474-b39c-fc2fa66a1f03	SEC_1769942148	f	ba0154e3-56bb-4d8d-9db9-b143367cbc85	t	2026-02-01 10:35:48.169682+00	2026-02-01 10:35:48.169682+00	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a
a5665aaf-aa67-437c-b997-4e7a7f655db4	SEC_1769942204	f	eb79439d-c6df-4d41-8c3d-0619964d91e1	t	2026-02-01 10:36:44.02709+00	2026-02-01 10:36:44.02709+00	ef5984b4-54b6-47cf-a9bb-ca02cadc0180	ef5984b4-54b6-47cf-a9bb-ca02cadc0180
1f3556bc-f866-4104-99a3-b16d256cf44c	SEC_1769942225	f	d1a8266c-b125-4c57-b1d9-69f785e7e7ec	t	2026-02-01 10:37:05.219976+00	2026-02-01 10:37:05.219976+00	70904796-fe39-4007-b892-a8aa3c8e0e8f	70904796-fe39-4007-b892-a8aa3c8e0e8f
5099dbd1-f710-4e0f-9175-0fd2ad1333ca	SEC_1769942293	f	c4a4f415-3907-463e-86e0-2d7148e90d28	t	2026-02-01 10:38:13.393018+00	2026-02-01 10:38:13.393018+00	1ce1ba48-b899-4217-8fd9-2124dd4765c6	1ce1ba48-b899-4217-8fd9-2124dd4765c6
fd36c2ac-bcfd-4aae-ad65-1e7780e7b697	SEC_1769942339	f	ab3df532-1696-45db-a97f-ebd3afaee92c	t	2026-02-01 10:38:59.195024+00	2026-02-01 10:38:59.195024+00	05e362b8-0b73-44ed-bded-ef4e0a40dd47	05e362b8-0b73-44ed-bded-ef4e0a40dd47
4da68809-e9cb-498a-b97c-1c0a5d0ca109	SEC_1769943699	f	c0fbcba5-fca1-4960-88fb-5a5aeb9684e3	t	2026-02-01 11:01:39.695961+00	2026-02-01 11:01:39.695961+00	b9c25548-e5ba-4200-9dc9-1ba98f332540	b9c25548-e5ba-4200-9dc9-1ba98f332540
0588aa5f-54d5-4544-a0b6-9535a4787776	SEC_1769943998	f	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	t	2026-02-01 11:06:38.927241+00	2026-02-01 11:06:38.927241+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429
8d28777c-3ec1-401b-a3f7-abe8af032686	SEC_5827_6984	f	8b411c61-9885-4672-ba08-e45709934575	t	2026-02-05 19:49:07.46739+00	2026-02-05 19:49:07.46739+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
f8b05511-90f1-481c-aca8-168906684cea	S1_1770326899	f	e21f1598-e198-4e06-b82e-c53822730dc8	t	2026-02-05 21:28:20.479325+00	2026-02-05 21:28:20.479325+00	dcc8f7e0-c4a6-4f72-b21e-78331c825d3e	dcc8f7e0-c4a6-4f72-b21e-78331c825d3e
b0292705-1384-4b45-9d1a-ecf33ef7ed7e	S1_1770327052	f	a33afb2d-870e-4263-88fa-9e2cb085a8f7	t	2026-02-05 21:30:53.620969+00	2026-02-05 21:30:53.620969+00	274bca62-6a26-40f4-ab29-482816286c94	274bca62-6a26-40f4-ab29-482816286c94
bc41c3da-9a29-4ce5-834f-52fd21432ba8	S1_1770327102	f	27227759-8c29-4ba3-8ba5-153607db5c4c	t	2026-02-05 21:31:42.643456+00	2026-02-05 21:31:42.643456+00	53126f3a-94da-4363-b20d-61a85c99574a	53126f3a-94da-4363-b20d-61a85c99574a
a300e7fd-5eb0-48a3-ba12-00b16750b2d0	S1_1770327224	f	bc651c65-73d1-41c9-a03a-275b47df7b10	t	2026-02-05 21:33:45.203857+00	2026-02-05 21:33:45.203857+00	1214c599-c7c2-490b-a895-e45b985b027b	1214c599-c7c2-490b-a895-e45b985b027b
7957ddf4-2552-4349-92a5-eaa1cc60769e	S1_1770327280	f	0a61f5ac-582c-4856-8072-27fcad588698	t	2026-02-05 21:34:41.200243+00	2026-02-05 21:34:41.200243+00	d9cd5b64-e423-4710-bcfe-73606bcca78c	d9cd5b64-e423-4710-bcfe-73606bcca78c
26d6feb1-d647-4e02-a01f-af767914367f	S1_1770327392	f	88810bde-bf96-43e8-9791-937cd4a7e062	t	2026-02-05 21:36:32.675647+00	2026-02-05 21:36:32.675647+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
d00e94a1-caa9-48f3-9db3-e4bac9b4c096	S1_1770327572	f	5e03962b-3b0c-4bd5-9f17-6349e82083cb	t	2026-02-05 21:39:33.679131+00	2026-02-05 21:39:33.679131+00	fc5165e6-6519-496f-a3dd-1435bc308b5f	fc5165e6-6519-496f-a3dd-1435bc308b5f
900f4f8d-8d2a-465a-84c8-8659ce9eb7b9	S1_1770327636	f	8bb34a8d-f5bb-41cf-ba29-87e5c652c03f	t	2026-02-05 21:40:37.582584+00	2026-02-05 21:40:37.582584+00	d655e067-4edd-4516-b1b6-821c3c33cfc5	d655e067-4edd-4516-b1b6-821c3c33cfc5
45d63ea1-0e12-4bf3-b620-12d572fba1cd	S1_1770327706	f	f3200c57-c6b8-4f2d-80fe-24b9a6359f6c	t	2026-02-05 21:41:47.326337+00	2026-02-05 21:41:47.326337+00	13ac055f-b943-4f6d-8182-babe636544df	13ac055f-b943-4f6d-8182-babe636544df
813222ab-33b9-4937-a23c-bf6059a12713	S1_1770327821	f	f7028cb1-7e87-4fd7-8aa1-4ea8b97ccb43	t	2026-02-05 21:43:42.738659+00	2026-02-05 21:43:42.738659+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
d33388e3-082c-4c2b-9885-85cfd4705373	S1_1770328194	f	e33b94b6-cfc5-4d7e-98a4-2259867e45b4	t	2026-02-05 21:49:55.119532+00	2026-02-05 21:49:55.119532+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	ebc86578-b9a2-456f-b884-f964c1fb26f9
9123b919-fdbe-478d-9757-c06c16606b63	S1_1770328337	f	718996de-ba3d-4b71-9a19-a6e97d2947ee	t	2026-02-05 21:52:18.881068+00	2026-02-05 21:52:18.881068+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	7eddd813-1060-42a3-aa36-abc2c6529e0f
8ed4cf1b-282b-4ab8-8983-2209bd440373	S1_1770328517	f	f9761969-f234-4bb8-9b46-2ea70ad5b735	t	2026-02-05 21:55:18.620729+00	2026-02-05 21:55:18.620729+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	021aea9d-7fe9-4488-ae61-eebf6d2af731
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: subscription_plan_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subscription_plan_history (id, plan_id, version, display_name, description, category, resource_limits, features, pricing_details, effective_from, effective_to, changed_by, created_at) FROM stdin;
\.


--
-- Data for Name: subscription_plans; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subscription_plans (id, name, display_name, description, category, resource_limits, features, pricing_details, sort_order, is_active, created_at, updated_at) FROM stdin;
23972749-fd43-4f74-9ff3-4528018e89e9	FREE	Free Plan	Basic features for small farmers	FARMING	{"crops": 10, "users": 2, "queries": 5}	{"api_access": false, "marketplace": false, "advanced_analytics": false}	{"currency": "INR", "billing_cycles": {"yearly": 0, "monthly": 0, "quarterly": 0}}	1	t	2026-01-30 00:05:41.059288+00	2026-01-30 00:05:41.059288+00
a9ea8f63-049a-484e-af95-89681efa8919	BASIC	Basic Plan	Essential features for growing farms	FARMING	{"crops": 50, "users": 5, "queries": 50}	{"api_access": false, "marketplace": true, "advanced_analytics": false}	{"currency": "INR", "billing_cycles": {"yearly": 4990, "monthly": 499, "quarterly": 1397}}	2	t	2026-01-30 00:05:41.059288+00	2026-01-30 00:05:41.059288+00
b3494cfc-4766-4e3f-94eb-1c9bb413f8e5	PREMIUM	Premium Plan	Advanced features for professional farms	FARMING	{"crops": 200, "users": 20, "queries": 200}	{"api_access": false, "marketplace": true, "advanced_analytics": true}	{"currency": "INR", "billing_cycles": {"yearly": 19990, "monthly": 1999, "quarterly": 5597}}	3	t	2026-01-30 00:05:41.059288+00	2026-01-30 00:05:41.059288+00
7b5e4717-0dde-4612-9e87-c68eb79da1ba	ENTERPRISE	Enterprise Plan	Full features for large organizations	\N	{"crops": null, "users": null, "queries": null}	{"api_access": true, "marketplace": true, "advanced_analytics": true, "custom_integrations": true}	{"currency": "INR", "billing_cycles": {"yearly": null, "monthly": null, "quarterly": null}, "custom_pricing": true}	4	t	2026-01-30 00:05:41.059288+00	2026-01-30 00:05:41.059288+00
\.


--
-- Data for Name: task_actuals; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_actuals (id, schedule_id, schedule_task_id, task_id, is_planned, crop_id, plot_id, actual_date, task_details, notes, created_at, created_by) FROM stdin;
\.


--
-- Data for Name: task_photos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_photos (id, task_actual_id, file_url, file_key, caption, uploaded_at, uploaded_by) FROM stdin;
\.


--
-- Data for Name: task_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_translations (id, task_id, language_code, name, description) FROM stdin;
956409d7-1424-49f9-bb8f-330d3be0e7db	654439a3-9d92-4be5-b0ad-0a01a7fb776f	en	Ploughing	\N
82489f31-58ce-45a1-b7c7-b1f7e565e0d9	a8445e07-5c5f-4d75-a820-0a76f4df6c62	en	Weeding	\N
c558584a-833d-4adf-a5e8-4cbc1f51f3ae	f9e21c77-de70-4d70-83ca-576f3aeb3019	en	Pruning	\N
d2bca57b-07a4-4184-9248-5c8714a7786e	de4abc8e-84ce-4d59-88a6-3286874b67d9	en	Trellising	\N
da0cfe21-0518-4b50-bb15-89368d2c9866	199dcb09-bc9e-474e-bb54-9f1136a88ab3	en	Harvesting	\N
c29e0b22-2a41-4b1e-a0c1-44776eba85b8	f6d249bf-44ce-48df-8b85-87849abb420f	en	Basal Dose	\N
0cd0c5e1-7d43-4f59-9102-55db86627a1a	e188c4a0-a402-4bf8-8bcd-0b381bf10195	en	Fertigation	\N
c2dec9ab-e10e-4104-ab6f-5e8acb42f66a	7da3b074-e1f1-4648-bf84-84133fe6c105	en	Foliar Spray	\N
cc19405d-99b0-4058-abc9-ebe8bc9b0d2d	99530824-fba5-42a8-9529-619692a89acd	en	Drenching	\N
762bbdce-d136-418e-805c-465d8a76b258	6d78b9e3-a9e3-40fb-9b0c-3c99a71d8290	en	Top Dressing	\N
49e95ca9-3a54-4191-81ae-d5bd17a5674b	b3f0a5d7-f1f6-4e26-91f0-84561b3b6f57	en	Root Feeding	\N
58a9ae6d-a3f9-429b-874a-145fd0521fdc	972e9dc6-f4bf-4279-b3ec-8cca2516f419	en	SOP Schedule Generation	\N
338bda3f-b4f8-42a0-a260-21b939df6b61	5a967f86-8db9-4838-9dca-5e112da067aa	en	Crop Audit	\N
64a2124e-ed49-43bd-a931-5135d84fd678	ff98494c-028a-442f-9656-077ac93e812a	en	Remote Audit	\N
a05049c3-67b9-4418-9215-6adf341033ff	33f346dd-d12e-488e-b457-202d79989132	en	Query Resolution	\N
e0f27064-174e-470c-ae0a-c8f528070f90	654439a3-9d92-4be5-b0ad-0a01a7fb776f	ta	உழவு	\N
73a9a64c-b5e7-4e0f-87c9-b029564d7c72	a8445e07-5c5f-4d75-a820-0a76f4df6c62	ta	களை எடுத்தல்	\N
21ca554f-b1b3-40cc-a0e6-78cd20de10d6	f9e21c77-de70-4d70-83ca-576f3aeb3019	ta	கிளை வெட்டுதல்	\N
ff2ccf4e-6f6c-4845-9419-9ce471c7db69	de4abc8e-84ce-4d59-88a6-3286874b67d9	ta	தாங்கு கட்டுதல்	\N
b01673b3-95c6-4a67-b76c-b53c4c801e6d	199dcb09-bc9e-474e-bb54-9f1136a88ab3	ta	அறுவடை	\N
9ce9f378-28b5-4ebc-9a66-ef43604d6d3b	f6d249bf-44ce-48df-8b85-87849abb420f	ta	அடி உரம்	\N
c72ce04e-bbf1-4e6c-ae0a-a20b0b906bea	e188c4a0-a402-4bf8-8bcd-0b381bf10195	ta	நீர் உரம்	\N
2db2ea08-b3b4-4951-a65c-6513959db89e	7da3b074-e1f1-4648-bf84-84133fe6c105	ta	இலை தெளிப்பு	\N
9f6bcf9c-4a7c-4cca-8ff4-d2f5f0e8657e	99530824-fba5-42a8-9529-619692a89acd	ta	வேர் ஊற்றுதல்	\N
2222164c-570d-4627-ad10-5860773d468d	6d78b9e3-a9e3-40fb-9b0c-3c99a71d8290	ta	மேல் உரம்	\N
cf382117-899a-4d58-8641-496e6df862ed	b3f0a5d7-f1f6-4e26-91f0-84561b3b6f57	ta	வேர் உணவு	\N
efddedae-146a-4aae-80c1-11d649135d05	972e9dc6-f4bf-4279-b3ec-8cca2516f419	ta	எஸ்.ஓ.பி அட்டவணை உருவாக்கம்	\N
7b10eef3-2fd2-4422-9c2c-e2faf8ac9e0d	5a967f86-8db9-4838-9dca-5e112da067aa	ta	பயிர் தணிக்கை	\N
86817ecb-f157-4b52-b1ba-7750822ccfcb	ff98494c-028a-442f-9656-077ac93e812a	ta	தொலை தணிக்கை	\N
8b5615e1-d82d-4165-9dfb-971fee183418	33f346dd-d12e-488e-b457-202d79989132	ta	வினா தீர்வு	\N
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tasks (id, code, category, requires_input_items, requires_concentration, requires_machinery, requires_labor, sort_order, is_active, created_at, updated_at) FROM stdin;
654439a3-9d92-4be5-b0ad-0a01a7fb776f	PLOUGHING	FARMING	f	f	t	t	1	t	2026-01-30 00:05:41.349998+00	2026-01-30 00:05:41.349998+00
a8445e07-5c5f-4d75-a820-0a76f4df6c62	WEEDING	FARMING	f	f	f	t	2	t	2026-01-30 00:05:41.349998+00	2026-01-30 00:05:41.349998+00
f9e21c77-de70-4d70-83ca-576f3aeb3019	PRUNING	FARMING	f	f	f	t	3	t	2026-01-30 00:05:41.349998+00	2026-01-30 00:05:41.349998+00
de4abc8e-84ce-4d59-88a6-3286874b67d9	TRELLISING	FARMING	f	f	f	t	4	t	2026-01-30 00:05:41.349998+00	2026-01-30 00:05:41.349998+00
199dcb09-bc9e-474e-bb54-9f1136a88ab3	HARVESTING	FARMING	f	f	f	t	5	t	2026-01-30 00:05:41.349998+00	2026-01-30 00:05:41.349998+00
f6d249bf-44ce-48df-8b85-87849abb420f	BASAL_DOSE	FARMING	t	f	f	t	6	t	2026-01-30 00:05:41.349998+00	2026-01-30 00:05:41.349998+00
e188c4a0-a402-4bf8-8bcd-0b381bf10195	FERTIGATION	FARMING	t	t	f	t	7	t	2026-01-30 00:05:41.349998+00	2026-01-30 00:05:41.349998+00
7da3b074-e1f1-4648-bf84-84133fe6c105	FOLIAR_SPRAY	FARMING	t	t	t	t	8	t	2026-01-30 00:05:41.349998+00	2026-01-30 00:05:41.349998+00
99530824-fba5-42a8-9529-619692a89acd	DRENCHING	FARMING	t	t	f	t	9	t	2026-01-30 00:05:41.349998+00	2026-01-30 00:05:41.349998+00
6d78b9e3-a9e3-40fb-9b0c-3c99a71d8290	TOP_DRESSING	FARMING	t	f	f	t	10	t	2026-01-30 00:05:41.349998+00	2026-01-30 00:05:41.349998+00
b3f0a5d7-f1f6-4e26-91f0-84561b3b6f57	ROOT_FEEDING	FARMING	t	t	f	t	11	t	2026-01-30 00:05:41.349998+00	2026-01-30 00:05:41.349998+00
972e9dc6-f4bf-4279-b3ec-8cca2516f419	SOP_SCHEDULE_GENERATION	FSP_CONSULTANCY	f	f	f	f	1	t	2026-01-30 00:05:41.360565+00	2026-01-30 00:05:41.360565+00
5a967f86-8db9-4838-9dca-5e112da067aa	CROP_AUDIT	FSP_CONSULTANCY	f	f	f	f	2	t	2026-01-30 00:05:41.360565+00	2026-01-30 00:05:41.360565+00
ff98494c-028a-442f-9656-077ac93e812a	REMOTE_AUDIT	FSP_CONSULTANCY	f	f	f	f	3	t	2026-01-30 00:05:41.360565+00	2026-01-30 00:05:41.360565+00
33f346dd-d12e-488e-b457-202d79989132	QUERY_RESOLUTION	FSP_CONSULTANCY	f	f	f	f	4	t	2026-01-30 00:05:41.360565+00	2026-01-30 00:05:41.360565+00
\.


--
-- Data for Name: template_parameters; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.template_parameters (id, template_section_id, parameter_id, is_required, sort_order, parameter_snapshot, created_at) FROM stdin;
2d984673-9d6e-4b9d-b2fa-aed1016f0938	097ebd03-5b70-4130-a713-0377a18be1d3	e89b6487-1da6-4f25-801c-a3e340814738	t	1	{"code": "SOIL_MOISTURE", "parameter_type": "SINGLE_SELECT", "parameter_metadata": null}	2026-01-30 00:08:38.921321+00
91068f04-9b38-43f8-aecf-5cb7835d882e	565a134b-03c7-4740-a8e4-071bac67ed50	e89b6487-1da6-4f25-801c-a3e340814738	t	1	{"code": "SOIL_MOISTURE", "parameter_id": "e89b6487-1da6-4f25-801c-a3e340814738", "parameter_type": "SINGLE_SELECT", "parameter_metadata": null}	2026-01-30 00:09:33.180136+00
3a454dff-074c-4878-9f76-836f43e011cc	046b86e2-a0fb-43fd-a637-389a81957107	22815f14-8679-4b16-903e-890f1193261a	f	0	{"code": "PRM_b3ab_0_2653", "options": [{"code": "GREEN", "option_id": "ccbc5fe8-e077-4487-8bf7-a807afaadeb9", "sort_order": 0, "translations": {"en": "Green"}}, {"code": "YELLOW", "option_id": "3661417e-ea73-4b11-82da-0846d2a89567", "sort_order": 1, "translations": {"en": "Yellow"}}, {"code": "BROWN", "option_id": "cb28cd9a-9c87-45be-ba22-b92076e2f4f7", "sort_order": 2, "translations": {"en": "Brown"}}], "parameter_id": "22815f14-8679-4b16-903e-890f1193261a", "translations": {"en": {"name": "Leaf Color", "help_text": null, "description": null}}, "option_set_id": "49c22604-b83e-4ec6-b024-aed71d28f5dd", "snapshot_date": "2026-01-30T00:21:13.175967", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-01-30 00:21:13.152504+00
51de0c1e-62c8-4e2e-8597-5ff79ed43a8e	046b86e2-a0fb-43fd-a637-389a81957107	a1dad50b-b1a3-49bb-a0f5-268c2fb82c14	f	1	{"code": "PRM_b3ab_1_2786", "options": [{"code": "YES", "option_id": "e1e48690-f91d-48b6-9d1e-6cd31518f138", "sort_order": 0, "translations": {"en": "Yes"}}, {"code": "NO", "option_id": "3718494a-aec8-44e5-bfd4-1cfc615c78ea", "sort_order": 1, "translations": {"en": "No"}}], "parameter_id": "a1dad50b-b1a3-49bb-a0f5-268c2fb82c14", "translations": {"en": {"name": "Pest Presence", "help_text": null, "description": null}}, "option_set_id": "c39059bb-e98e-43e5-955d-1f87b7450684", "snapshot_date": "2026-01-30T00:21:13.286013", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-01-30 00:21:13.268124+00
5a6c86b0-b4c8-4d16-8072-400fd8f7b2e9	046b86e2-a0fb-43fd-a637-389a81957107	39cb34e6-9d92-4270-820f-80fd2e47ce1e	f	2	{"code": "PRM_b3ab_2_2886", "options": [], "parameter_id": "39cb34e6-9d92-4270-820f-80fd2e47ce1e", "translations": {"en": {"name": "Plant Height (cm)", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-01-30T00:21:13.367082", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-01-30 00:21:13.351447+00
25b8f2e7-5c88-4625-9ebf-444824212ab2	046b86e2-a0fb-43fd-a637-389a81957107	46310718-ce6f-4e69-8da2-0583bf5554b0	f	3	{"code": "PRM_b3ab_3_2969", "options": [{"code": "DRY", "option_id": "0909eb6a-4e53-412a-a760-d23a5bd8e0e2", "sort_order": 0, "translations": {"en": "Dry"}}, {"code": "MOIST", "option_id": "5a70955a-94e0-4f47-90ec-9c7caf3284f3", "sort_order": 1, "translations": {"en": "Moist"}}, {"code": "WET", "option_id": "739bdc7c-5082-473e-8a36-9dca94909a3a", "sort_order": 2, "translations": {"en": "Wet"}}], "parameter_id": "46310718-ce6f-4e69-8da2-0583bf5554b0", "translations": {"en": {"name": "Soil Moisture Level", "help_text": null, "description": null}}, "option_set_id": "0b082300-cb93-4098-8b68-4c5f2492d0ea", "snapshot_date": "2026-01-30T00:21:13.468449", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-01-30 00:21:13.452578+00
aae3c628-3f70-41d4-8bdf-1d9d2454babe	0404e697-424a-401f-a41d-91c913239acc	f32bc43e-7842-4aff-97d0-c999804e2f44	f	0	{"code": "PRM_fa6d_0_1143", "options": [], "parameter_id": "f32bc43e-7842-4aff-97d0-c999804e2f44", "translations": {"en": {"name": "sadfsdfsdf", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-01-30T20:36:02.350296", "parameter_type": "DATE", "parameter_metadata": {}}	2026-01-30 20:36:02.324467+00
7e3eff31-8b20-42c8-8775-305fa41ad051	0404e697-424a-401f-a41d-91c913239acc	7ada24d6-b7ad-413d-893d-25e1271d9841	f	1	{"code": "PRM_fa6d_1_1243", "options": [], "parameter_id": "7ada24d6-b7ad-413d-893d-25e1271d9841", "translations": {"en": {"name": "Plant Height (cm)", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-01-30T20:36:02.438430", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-01-30 20:36:02.423027+00
31f62779-fe28-4a64-919b-89a14b2216d5	0404e697-424a-401f-a41d-91c913239acc	1d0cbbc3-1354-49d6-a16a-5ba0d6fd2f04	f	2	{"code": "PRM_fa6d_2_1310", "options": [{"code": "GREEN", "option_id": "059974e2-a761-487f-9e52-2629100b504a", "sort_order": 0, "translations": {"en": "Green"}}, {"code": "YELLOW", "option_id": "6d7cbc48-8d1a-4ba5-bf1d-fd8b794a404b", "sort_order": 1, "translations": {"en": "Yellow"}}, {"code": "BROWN", "option_id": "c643a809-e612-4807-9a90-0b29f0f9508c", "sort_order": 2, "translations": {"en": "Brown"}}], "parameter_id": "1d0cbbc3-1354-49d6-a16a-5ba0d6fd2f04", "translations": {"en": {"name": "Leaf Color", "help_text": null, "description": null}}, "option_set_id": "0345db82-bf99-4f32-b222-6ae0a7c07c00", "snapshot_date": "2026-01-30T20:36:02.522959", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-01-30 20:36:02.505975+00
f6597fa3-3158-4c7c-8637-b6dc3a90cbc8	0404e697-424a-401f-a41d-91c913239acc	1b4c0c1b-7516-439a-af12-4e9735291848	f	3	{"code": "PRM_fa6d_3_1410", "options": [{"code": "YES", "option_id": "0c80853b-5a5b-4b87-8ba9-943fcf02bb3b", "sort_order": 0, "translations": {"en": "Yes"}}, {"code": "NO", "option_id": "af79f344-cacf-4679-9426-ff4f2507deb0", "sort_order": 1, "translations": {"en": "No"}}], "parameter_id": "1b4c0c1b-7516-439a-af12-4e9735291848", "translations": {"en": {"name": "Pest Presence", "help_text": null, "description": null}}, "option_set_id": "dfdd3646-a211-4edf-9458-3fd5dfdb7a76", "snapshot_date": "2026-01-30T20:36:02.619125", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-01-30 20:36:02.605686+00
739ac86c-8970-4c0f-bdd1-524adef41c37	0404e697-424a-401f-a41d-91c913239acc	e5db1148-7a6f-4fae-80f5-e602f35e5cbd	f	4	{"code": "PRM_fa6d_4_1510", "options": [], "parameter_id": "e5db1148-7a6f-4fae-80f5-e602f35e5cbd", "translations": {"en": {"name": "Plant Height (cm)", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-01-30T20:36:02.702436", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-01-30 20:36:02.688629+00
211a8cef-01df-41d1-b0be-3378090d0615	0404e697-424a-401f-a41d-91c913239acc	69900480-cef3-4145-adc7-651cf4eb1c38	f	5	{"code": "PRM_fa6d_5_1576", "options": [{"code": "DRY", "option_id": "ceba3c16-431a-4ddd-b565-51a899129e34", "sort_order": 0, "translations": {"en": "Dry"}}, {"code": "MOIST", "option_id": "72bd150c-a989-42a6-8a19-7c0c46e21195", "sort_order": 1, "translations": {"en": "Moist"}}, {"code": "WET", "option_id": "bce6372f-fb3a-492a-986d-9c2a151d765b", "sort_order": 2, "translations": {"en": "Wet"}}], "parameter_id": "69900480-cef3-4145-adc7-651cf4eb1c38", "translations": {"en": {"name": "Soil Moisture Level", "help_text": null, "description": null}}, "option_set_id": "9a006dfc-05c1-48d7-a1d9-d0a6f6e2ccba", "snapshot_date": "2026-01-30T20:36:02.786042", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-01-30 20:36:02.7724+00
99d57b92-123a-471d-ab56-a777ce086dfa	d562b9a2-ed43-41e8-9765-199eac46ca44	07da6e2b-1ce2-4af9-ba9f-ccd09a7d37de	t	1	{"code": "PH_1769941881", "options": [], "parameter_id": "07da6e2b-1ce2-4af9-ba9f-ccd09a7d37de", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:31:21.336090", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:31:21.319471+00
2ab2a6ae-11ef-4895-82a2-819aa5e59f21	bb7863b4-5ab9-42c2-a9dc-960ebb1a071c	71826bac-4f3a-4e8e-b7d7-dcfdb27c2f62	t	1	{"code": "PH_1769941969", "options": [], "parameter_id": "71826bac-4f3a-4e8e-b7d7-dcfdb27c2f62", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:32:49.396616", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:32:49.389184+00
2c11106f-d0d9-4dfd-8106-ab790fda12ed	ed7822b9-a67a-4c6d-836a-dfd4c510c892	7940e041-2bd8-4b4c-829b-5c080b601709	t	1	{"code": "PH_1769941990", "options": [], "parameter_id": "7940e041-2bd8-4b4c-829b-5c080b601709", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:33:10.105644", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:33:10.094334+00
72143d9f-36f1-4759-afbf-f65c5c0803fd	7e5e1be0-27ef-4a08-8368-3651f7c279b4	940dd88b-e133-440b-af51-95365af25909	t	1	{"code": "PH_1769942012", "options": [], "parameter_id": "940dd88b-e133-440b-af51-95365af25909", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:33:32.134050", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:33:32.123187+00
23dc17d6-cc0a-4219-a9f7-5af381a2579b	b9fb0eb6-5a90-47dd-8695-a24ffe3afc15	10f12a98-15d3-446f-90b0-5e5e353c3809	t	1	{"code": "PH_1769942044", "options": [], "parameter_id": "10f12a98-15d3-446f-90b0-5e5e353c3809", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:34:04.529862", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:34:04.519984+00
89df7226-630a-45be-aeee-0499a5b93401	b53d7e01-c5db-4ab4-b985-ec803c3305af	1ad2e581-5dce-41ce-af2a-8e832ebbcc54	t	1	{"code": "PH_1769942062", "options": [], "parameter_id": "1ad2e581-5dce-41ce-af2a-8e832ebbcc54", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:34:22.083863", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:34:22.073425+00
96519724-297e-4917-9683-048c22e59f3f	aa0c9387-e1ea-43af-8bdf-70de57e12da9	4ec21239-4ac2-46b7-bd9b-d1c065591f62	t	1	{"code": "PH_1769942082", "options": [], "parameter_id": "4ec21239-4ac2-46b7-bd9b-d1c065591f62", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:34:42.666250", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:34:42.657536+00
39bd2643-0d03-4c69-899e-ef82723b9583	5228ba9f-7d49-4466-927b-84eb6492afba	ebfb0b55-7017-496c-9e98-d0d55159a831	t	1	{"code": "PH_1769942107", "options": [], "parameter_id": "ebfb0b55-7017-496c-9e98-d0d55159a831", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:35:08.007957", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:35:07.998738+00
05242278-1ef3-4906-9990-16b85ac6f239	8f9bffa5-2817-4251-93a8-a07baa03cf6d	7325f2cc-97ed-4dcc-a191-1ea0c56e04bd	t	1	{"code": "PH_1769942148", "options": [], "parameter_id": "7325f2cc-97ed-4dcc-a191-1ea0c56e04bd", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:35:48.206544", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:35:48.197658+00
141f5cda-8bf7-4fb9-855d-a4a82df1aef3	f2f6975e-267f-4d99-a126-9ed1d82cb15e	e68e3073-4957-4a89-80e3-f27e8136bf3b	t	1	{"code": "PH_1769942204", "options": [], "parameter_id": "e68e3073-4957-4a89-80e3-f27e8136bf3b", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:36:44.084423", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:36:44.070629+00
8aa85e90-5b86-48ac-8833-8b9851e4d9a9	ad013930-0d06-46cc-aee9-a65be6cc324f	314226b3-58f0-40c3-8a79-a040f41f3867	t	1	{"code": "PH_1769942225", "options": [], "parameter_id": "314226b3-58f0-40c3-8a79-a040f41f3867", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:37:05.260857", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:37:05.249738+00
90fc747b-f9ba-4d30-b51a-53b2f2ef2378	071025c2-1738-4e4d-b0b8-cced4f66094f	fca6b05f-39da-4323-a92d-d2fc7eceabff	t	1	{"code": "PH_1769942293", "options": [], "parameter_id": "fca6b05f-39da-4323-a92d-d2fc7eceabff", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:38:13.439365", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:38:13.428731+00
c0bb0799-4b59-410d-afcf-19a165b54177	a6554583-4fc4-434f-a837-74fe2848fa21	710a7d66-5394-4c0a-af26-5dc0512fae77	t	1	{"code": "PH_1769942339", "options": [], "parameter_id": "710a7d66-5394-4c0a-af26-5dc0512fae77", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T10:38:59.251995", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 10:38:59.238128+00
6d15f02b-004e-4fbb-aeed-522c1fad9870	56d9fb7a-e631-4882-9a7e-cb169b0b0f54	e9799730-1c13-4c5f-b9ed-2a7fd9c1538e	t	1	{"code": "PH_1769943699", "options": [], "parameter_id": "e9799730-1c13-4c5f-b9ed-2a7fd9c1538e", "translations": {"en": {"name": "Soil pH", "help_text": null, "description": "Measure pH"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:01:39.739227", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "pH", "max_value": 14, "min_value": 0}}	2026-02-01 11:01:39.728247+00
1c5ff669-fe72-4023-a2a1-3a8bf3ee87be	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	eefe2319-3eb6-43bb-9d78-7c734561b947	t	1	{"code": "P1_1769943998", "options": [], "parameter_id": "eefe2319-3eb6-43bb-9d78-7c734561b947", "translations": {"en": {"name": "Param 1", "help_text": null, "description": "Measure 1"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.130850", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.119869+00
60186c57-2f42-4e17-878b-67ca97c8d86b	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	5684267d-6f41-454e-8429-2f094efe38b9	t	2	{"code": "P2_1769943998", "options": [], "parameter_id": "5684267d-6f41-454e-8429-2f094efe38b9", "translations": {"en": {"name": "Param 2", "help_text": null, "description": "Measure 2"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.132908", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.119869+00
d2781b61-612f-4e9a-bcd5-523e0886b98a	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	b2d71394-a99d-4ff6-a333-4d8ebf1c1ec4	t	3	{"code": "P3_1769943998", "options": [], "parameter_id": "b2d71394-a99d-4ff6-a333-4d8ebf1c1ec4", "translations": {"en": {"name": "Param 3", "help_text": null, "description": "Measure 3"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.134914", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.119869+00
0f0dc0d0-2d1d-47f1-9623-8b8d4c072bb4	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	7e469f84-0b9d-4f70-b737-ce0444148245	t	4	{"code": "P4_1769943998", "options": [], "parameter_id": "7e469f84-0b9d-4f70-b737-ce0444148245", "translations": {"en": {"name": "Param 4", "help_text": null, "description": "Measure 4"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.137324", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.119869+00
e7b6b4cf-ff55-4b0f-8019-31af6107feda	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	46640045-7bdf-48eb-af82-61a3fc7c2d4a	t	5	{"code": "P5_1769943999", "options": [], "parameter_id": "46640045-7bdf-48eb-af82-61a3fc7c2d4a", "translations": {"en": {"name": "Param 5", "help_text": null, "description": "Measure 5"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.140000", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.119869+00
b11303c0-967f-4ba7-a292-90b69fe49a92	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	f517e506-6c88-4cfb-8426-ae5f1d516154	t	6	{"code": "P6_1769943999", "options": [], "parameter_id": "f517e506-6c88-4cfb-8426-ae5f1d516154", "translations": {"en": {"name": "Param 6", "help_text": null, "description": "Measure 6"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.142182", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.119869+00
adf8d101-fc06-4884-956a-e58e985d9df5	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	89151732-fc61-4617-a477-17685bbee9da	t	7	{"code": "P7_1769943999", "options": [], "parameter_id": "89151732-fc61-4617-a477-17685bbee9da", "translations": {"en": {"name": "Param 7", "help_text": null, "description": "Measure 7"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.144252", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.119869+00
479a7e32-9b35-49d5-ac49-3d3b7f085d6a	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	8bea7626-d387-455c-aa0b-2436f2824e78	t	8	{"code": "P8_1769943999", "options": [], "parameter_id": "8bea7626-d387-455c-aa0b-2436f2824e78", "translations": {"en": {"name": "Param 8", "help_text": null, "description": "Measure 8"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.146434", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.119869+00
61bdc206-3ce7-4f35-990d-45b7ea3152a8	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	d7147d11-034b-4c26-8c23-6921d316d28a	t	9	{"code": "P9_1769943999", "options": [], "parameter_id": "d7147d11-034b-4c26-8c23-6921d316d28a", "translations": {"en": {"name": "Param 9", "help_text": null, "description": "Measure 9"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.148816", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.119869+00
aa5b1ca5-8ffc-43aa-a9ce-ee3b2ce625fe	92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	9f963e85-c94c-4dec-b2aa-b0e745431c39	t	10	{"code": "P10_1769943999", "options": [], "parameter_id": "9f963e85-c94c-4dec-b2aa-b0e745431c39", "translations": {"en": {"name": "Param 10", "help_text": null, "description": "Measure 10"}}, "option_set_id": null, "snapshot_date": "2026-02-01T11:06:39.150831", "parameter_type": "NUMERIC", "parameter_metadata": {"unit": "units", "max_value": 100, "min_value": 0}}	2026-02-01 11:06:39.119869+00
5ad9ad99-fc13-4e00-97cd-c4a1f5632951	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	74d9d4a6-aac1-4ec4-aaa0-b8733a55def7	f	0	{"code": "PRM_8d28_0_7135", "options": [], "parameter_id": "74d9d4a6-aac1-4ec4-aaa0-b8733a55def7", "translations": {"en": {"name": "asdasdasdasdasd", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T19:49:07.700102", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 19:49:07.672761+00
3e6427c8-e9ae-45a1-a289-a1ab036d3e05	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	5c5ea765-416e-49c7-b577-9c075bcfa073	f	1	{"code": "PRM_8d28_1_7259", "options": [], "parameter_id": "5c5ea765-416e-49c7-b577-9c075bcfa073", "translations": {"en": {"name": "Answer this questions as well now thats it buddy", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T19:49:07.793429", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 19:49:07.775855+00
1afb3c99-1380-4399-8abf-63df13156035	2ad0d4b2-53f7-446a-8ebf-50854fb0713c	326b6dee-185a-42c1-b2d2-c82694e19f86	f	2	{"code": "PRM_8d28_2_7342", "options": [], "parameter_id": "326b6dee-185a-42c1-b2d2-c82694e19f86", "translations": {"en": {"name": "Only numbers got it now", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T19:49:07.876452", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 19:49:07.858619+00
14488251-1519-4c8f-b41d-4e6e1bea887c	834d23a5-e7ec-4d4e-8a69-f35ecdd38d23	78a8d90e-d189-4e0c-9815-618f465f4195	t	1	{"code": "P1_1770327102", "options": [], "parameter_id": "78a8d90e-d189-4e0c-9815-618f465f4195", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:31:42.767109", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:31:42.733716+00
22dadcaa-915e-4fdd-8572-bd6c32368e6c	834d23a5-e7ec-4d4e-8a69-f35ecdd38d23	f01ac19f-b2ff-4bc9-b16a-5edb10315b41	t	2	{"code": "P2_1770327102", "options": [], "parameter_id": "f01ac19f-b2ff-4bc9-b16a-5edb10315b41", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:31:42.770435", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:31:42.733716+00
56d975ce-2cb7-4437-b3b9-f5e3d569c59f	834d23a5-e7ec-4d4e-8a69-f35ecdd38d23	5e0e278c-ed24-4ae6-b259-8a430b6ff804	t	3	{"code": "P3_1770327102", "options": [{"code": "opt1", "option_id": "b7c70d96-0f02-48ae-972d-b003cbfc3b89", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "4126b50a-880e-44a6-b28a-985081f32d4c", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "5e0e278c-ed24-4ae6-b259-8a430b6ff804", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "7d1bfc37-3b1b-4421-a3f9-104690c6e487", "snapshot_date": "2026-02-05T21:31:42.771897", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:31:42.733716+00
cb22dd88-3b5a-44a1-933c-7bf69da998f6	a44f7299-8392-4c30-8f9e-3bef71205bae	467998d6-634b-40aa-8eb8-728fab704ba7	t	1	{"code": "P1_1770327224", "options": [], "parameter_id": "467998d6-634b-40aa-8eb8-728fab704ba7", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:33:45.303161", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:33:45.294825+00
b0d73f70-875e-45f7-a6fd-a2c50e49a581	a44f7299-8392-4c30-8f9e-3bef71205bae	82c060ef-fec1-4d82-9e63-44b301715425	t	2	{"code": "P2_1770327224", "options": [], "parameter_id": "82c060ef-fec1-4d82-9e63-44b301715425", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:33:45.304988", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:33:45.294825+00
f954a1c7-30cc-4a59-9bea-1c356775dd28	a44f7299-8392-4c30-8f9e-3bef71205bae	28230270-0fcf-4662-8c5b-8bb0ad5c57b3	t	3	{"code": "P3_1770327224", "options": [{"code": "opt1", "option_id": "68b94446-68e1-4ec5-8b41-cc9842033394", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "1c17baf7-b36c-464e-9a73-3e829cc103db", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "28230270-0fcf-4662-8c5b-8bb0ad5c57b3", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "b409cb79-5f90-4322-b935-5c13fe396f9c", "snapshot_date": "2026-02-05T21:33:45.306452", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:33:45.294825+00
9661afdf-cbd2-4ac8-884a-5822d575077f	7a2df06a-eeac-4f95-8f3a-6af6463183b3	e016e813-99bf-46ae-93e0-43fcc999ecff	t	1	{"code": "P1_1770327280", "options": [], "parameter_id": "e016e813-99bf-46ae-93e0-43fcc999ecff", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:34:41.294678", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:34:41.282782+00
3993ecf5-fb5b-4081-a705-e7037b3a84bb	7a2df06a-eeac-4f95-8f3a-6af6463183b3	0124f9d8-df14-40e1-a628-2fb28cfcd89b	t	2	{"code": "P2_1770327280", "options": [], "parameter_id": "0124f9d8-df14-40e1-a628-2fb28cfcd89b", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:34:41.296416", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:34:41.282782+00
5e4cf3e0-ba23-4fcd-a2b4-0ffba4c97c26	7a2df06a-eeac-4f95-8f3a-6af6463183b3	5b9d413c-0d24-4b1c-bee8-2a800c357b62	t	3	{"code": "P3_1770327280", "options": [{"code": "opt1", "option_id": "ee25c5c6-aadd-4c6a-ab13-3070b40ddf05", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "ab2b8972-8292-4e21-a8f6-66d8bf133921", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "5b9d413c-0d24-4b1c-bee8-2a800c357b62", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "a9bf577e-4d74-495e-b9d9-c1677621be45", "snapshot_date": "2026-02-05T21:34:41.298038", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:34:41.282782+00
ae123a65-7da4-4db6-82e6-1ca655b0f09c	98fc0861-9afb-41f1-b1e9-da223f7e1acf	baa7fe1d-099f-49de-9531-dcad3694b914	t	1	{"code": "P1_1770327392", "options": [], "parameter_id": "baa7fe1d-099f-49de-9531-dcad3694b914", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:36:32.747856", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:36:32.738996+00
6ebf3b9b-8b42-4caa-ab13-51ca63e4b025	98fc0861-9afb-41f1-b1e9-da223f7e1acf	56a72950-a19d-481b-a0db-3aa0940d1b7a	t	2	{"code": "P2_1770327392", "options": [], "parameter_id": "56a72950-a19d-481b-a0db-3aa0940d1b7a", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:36:32.749566", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:36:32.738996+00
aaddcdf3-9f6d-42c2-8f1c-f10728c5a6a4	98fc0861-9afb-41f1-b1e9-da223f7e1acf	6699f225-e68a-4e39-a43f-a6202cda40d5	t	3	{"code": "P3_1770327392", "options": [{"code": "opt1", "option_id": "c2b584fc-e308-4562-ba68-3bdc7c1f8ecc", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "afb0f1b3-8447-4a23-a961-cf6affd8bfa0", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "6699f225-e68a-4e39-a43f-a6202cda40d5", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "cdc29b9f-35fb-4abb-a9a6-21272b56173a", "snapshot_date": "2026-02-05T21:36:32.751132", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:36:32.738996+00
1e07201d-000d-44bb-9f82-98f352bfd36b	3653a901-5e50-49a1-8d6f-eaf6c30d3104	90ac4202-513e-4e0e-9de6-a32262857ed3	t	1	{"code": "P1_1770327572", "options": [], "parameter_id": "90ac4202-513e-4e0e-9de6-a32262857ed3", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:39:33.802102", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:39:33.790585+00
22352c4d-fe0b-4d96-a2f2-0d7c4b5ddced	3653a901-5e50-49a1-8d6f-eaf6c30d3104	4a1add6d-2be5-4eb4-93d2-51ebbf5e1672	t	2	{"code": "P2_1770327572", "options": [], "parameter_id": "4a1add6d-2be5-4eb4-93d2-51ebbf5e1672", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:39:33.804114", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:39:33.790585+00
c454e056-707a-49a4-ba9b-87eb87030eeb	3653a901-5e50-49a1-8d6f-eaf6c30d3104	689e5a3e-cc7a-4148-b408-f92ec941b37e	t	3	{"code": "P3_1770327572", "options": [{"code": "opt1", "option_id": "6baefc9c-88e8-4aa1-a021-8cae81a905ed", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "44c9d328-fc27-4a2c-9a01-9167b8f9c84f", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "689e5a3e-cc7a-4148-b408-f92ec941b37e", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "b0fe6edb-193c-4e20-a6f4-5cbaaf817536", "snapshot_date": "2026-02-05T21:39:33.806111", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:39:33.790585+00
9f0eb65a-d748-48ed-98d4-4f8e49837a25	ab035ef9-1fb5-4594-946e-5b06c036494a	c863d9ae-337e-4ea5-a846-3b9a8bd04020	t	1	{"code": "P1_1770327636", "options": [], "parameter_id": "c863d9ae-337e-4ea5-a846-3b9a8bd04020", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:40:37.685657", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:40:37.669699+00
37026b03-84a2-46c1-8914-0828449a3eee	ab035ef9-1fb5-4594-946e-5b06c036494a	a74d7503-f495-4a7b-942d-2e6d64aab25f	t	2	{"code": "P2_1770327636", "options": [], "parameter_id": "a74d7503-f495-4a7b-942d-2e6d64aab25f", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:40:37.688788", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:40:37.669699+00
f11f2ae6-069b-45b9-b010-2921adbf6ae7	ab035ef9-1fb5-4594-946e-5b06c036494a	7acb91dd-9a2b-482c-9fc6-2eefb815aeb3	t	3	{"code": "P3_1770327636", "options": [{"code": "opt1", "option_id": "cc1a045b-0ce5-4c07-afed-eca7a4d7896f", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "6f01b763-30d8-414c-9af9-bf605ac00ae7", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "7acb91dd-9a2b-482c-9fc6-2eefb815aeb3", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "ba3f1425-1907-48fc-a9f4-7ee1a85c0b90", "snapshot_date": "2026-02-05T21:40:37.691176", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:40:37.669699+00
f9911466-a68c-4c61-9538-abf29e59d2ea	35efd64c-30d9-4c9a-a581-8ea712a613c2	76452429-682f-4ba0-917e-bb4b9ffd349f	t	1	{"code": "P1_1770327706", "options": [], "parameter_id": "76452429-682f-4ba0-917e-bb4b9ffd349f", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:41:47.418386", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:41:47.40626+00
d31aa367-dc5c-49cc-af22-20c31531f4e6	35efd64c-30d9-4c9a-a581-8ea712a613c2	e46db86a-72f6-4606-8eb2-560b6b3ec315	t	2	{"code": "P2_1770327706", "options": [], "parameter_id": "e46db86a-72f6-4606-8eb2-560b6b3ec315", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:41:47.420069", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:41:47.40626+00
23064d8e-c2f3-467b-9eef-709e90b2127a	35efd64c-30d9-4c9a-a581-8ea712a613c2	222948be-c818-4310-bf8d-fef35d5d979c	t	3	{"code": "P3_1770327706", "options": [{"code": "opt1", "option_id": "8337ba01-c7bc-4553-86d0-672c65399b38", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "5811ced6-2e79-4c9e-b7a1-f48134203521", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "222948be-c818-4310-bf8d-fef35d5d979c", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "e67b95a8-8819-4939-9557-bd2d5379e96c", "snapshot_date": "2026-02-05T21:41:47.421582", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:41:47.40626+00
d482346e-285e-4e1c-9160-4638139b8d13	da3ff4de-da78-4c58-9ac5-1e7eb467e664	b664898c-45cf-4723-8fff-b74c1232898f	t	1	{"code": "P1_1770327821", "options": [], "parameter_id": "b664898c-45cf-4723-8fff-b74c1232898f", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:43:42.832610", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:43:42.819662+00
9244cacf-3709-48d1-918c-7d6a71439985	da3ff4de-da78-4c58-9ac5-1e7eb467e664	9700c6e5-2190-443e-83b2-5183b59625e2	t	2	{"code": "P2_1770327821", "options": [], "parameter_id": "9700c6e5-2190-443e-83b2-5183b59625e2", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:43:42.834146", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:43:42.819662+00
a8ef1438-5092-4bb7-a8b3-782e79a9efb2	da3ff4de-da78-4c58-9ac5-1e7eb467e664	78f901de-8e0c-42a6-ba39-94adadbe3193	t	3	{"code": "P3_1770327821", "options": [{"code": "opt1", "option_id": "3f3b03fa-ef0e-42fe-9546-c33af35d1681", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "a77d9560-5597-493c-a16d-99af12c82df6", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "78f901de-8e0c-42a6-ba39-94adadbe3193", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "53a4bc06-e667-4f37-b16e-9aa98563aa2f", "snapshot_date": "2026-02-05T21:43:42.835558", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:43:42.819662+00
1a7341a4-9bfd-4db2-ab5b-3fe7e023c79b	401c4821-37e9-4fe4-afbb-1e5a781f5a42	21f3a466-ed7c-4630-8715-9dbeca7fb00f	t	1	{"code": "P1_1770328194", "options": [], "parameter_id": "21f3a466-ed7c-4630-8715-9dbeca7fb00f", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:49:55.209255", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:49:55.196534+00
9e808037-7d87-4442-be05-28fadade7226	401c4821-37e9-4fe4-afbb-1e5a781f5a42	2ad12225-e5db-458e-9a8a-7d3ff1051d4c	t	2	{"code": "P2_1770328194", "options": [], "parameter_id": "2ad12225-e5db-458e-9a8a-7d3ff1051d4c", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:49:55.210844", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:49:55.196534+00
0e970e02-855a-493e-87f2-bf1e77bfbaab	401c4821-37e9-4fe4-afbb-1e5a781f5a42	fc1d516b-4410-42df-8d1a-2420b8d0927b	t	3	{"code": "P3_1770328194", "options": [{"code": "opt1", "option_id": "2c2e893a-cd32-4855-b766-681bb293adb7", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "3384b3d2-89b2-45f7-82a2-28e23fa1dc1f", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "fc1d516b-4410-42df-8d1a-2420b8d0927b", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "e86a83d1-b3e4-44cc-95ad-b63d2b7a931d", "snapshot_date": "2026-02-05T21:49:55.212063", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:49:55.196534+00
504e4a99-d3a9-4ecc-8080-147701b5a205	74bac9ba-a6ee-4587-97f2-ea34c720f4b2	bee24a5b-c963-4451-86cc-068d3d4b9309	t	1	{"code": "P1_1770328337", "options": [], "parameter_id": "bee24a5b-c963-4451-86cc-068d3d4b9309", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:52:19.007031", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:52:18.988815+00
d41f7e2d-f651-4fde-a825-24f73205c41d	74bac9ba-a6ee-4587-97f2-ea34c720f4b2	458fd9c3-1e3b-4526-90c5-b791616862e3	t	2	{"code": "P2_1770328337", "options": [], "parameter_id": "458fd9c3-1e3b-4526-90c5-b791616862e3", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:52:19.009221", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:52:18.988815+00
3903a29b-f41f-42c7-8b25-6debc623c28b	74bac9ba-a6ee-4587-97f2-ea34c720f4b2	3bbea4bb-bdd5-4465-b6d1-001830971892	t	3	{"code": "P3_1770328337", "options": [{"code": "opt1", "option_id": "74519a03-49e9-43a4-adbf-4f87f5ea49b9", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "d4ae2cd6-4259-436a-8a91-f9003f839b13", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "3bbea4bb-bdd5-4465-b6d1-001830971892", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "f8998096-2833-488c-b41e-08dedfcfc32c", "snapshot_date": "2026-02-05T21:52:19.011353", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:52:18.988815+00
eb1d4494-a224-4f4a-8ad1-5c001b572b1f	58fc5011-88a7-436c-b4a4-c6bb63cdff8c	02f8b306-97b5-4dde-afdb-91725dfec46f	t	1	{"code": "P1_1770328517", "options": [], "parameter_id": "02f8b306-97b5-4dde-afdb-91725dfec46f", "translations": {"en": {"name": "Yield", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:55:18.722928", "parameter_type": "NUMERIC", "parameter_metadata": {}}	2026-02-05 21:55:18.708994+00
86ce3e6c-4be2-41dc-8d1a-e0099a224c6a	58fc5011-88a7-436c-b4a4-c6bb63cdff8c	a9958b3e-69bf-42ac-a56d-c8d16d67d06b	t	2	{"code": "P2_1770328517", "options": [], "parameter_id": "a9958b3e-69bf-42ac-a56d-c8d16d67d06b", "translations": {"en": {"name": "Health", "help_text": null, "description": null}}, "option_set_id": null, "snapshot_date": "2026-02-05T21:55:18.724726", "parameter_type": "TEXT", "parameter_metadata": {}}	2026-02-05 21:55:18.708994+00
dc74cfb2-9f90-4b97-98b8-69f0419c49dd	58fc5011-88a7-436c-b4a4-c6bb63cdff8c	ad806e19-cd1d-4a40-ae12-bd0c5c203b9b	t	3	{"code": "P3_1770328517", "options": [{"code": "opt1", "option_id": "acfc1f03-a09d-408d-88c9-28563d8d9f9a", "sort_order": 0, "translations": {"en": "Organic"}}, {"code": "opt2", "option_id": "25dd033d-3220-4738-8685-4163540c3b74", "sort_order": 1, "translations": {"en": "Chemical"}}], "parameter_id": "ad806e19-cd1d-4a40-ae12-bd0c5c203b9b", "translations": {"en": {"name": "Type", "help_text": null, "description": null}}, "option_set_id": "6c5d8da2-26c9-424a-9b09-5f0b70e2c080", "snapshot_date": "2026-02-05T21:55:18.726167", "parameter_type": "SINGLE_SELECT", "parameter_metadata": {}}	2026-02-05 21:55:18.708994+00
\.


--
-- Data for Name: template_sections; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.template_sections (id, template_id, section_id, sort_order, created_at) FROM stdin;
097ebd03-5b70-4130-a713-0377a18be1d3	553119c9-7384-4f72-8885-e461679761de	b1af410d-1ef3-4455-b17d-69b8c5a7ea26	1	2026-01-30 00:08:38.921321+00
565a134b-03c7-4740-a8e4-071bac67ed50	3087bfd4-926c-450c-8ef1-bae06f734c4e	b1af410d-1ef3-4455-b17d-69b8c5a7ea26	1	2026-01-30 00:09:33.180136+00
046b86e2-a0fb-43fd-a637-389a81957107	3087bfd4-926c-450c-8ef1-bae06f734c4e	b3aba901-3184-45be-b815-2017625d5011	1	2026-01-30 00:21:13.052024+00
0404e697-424a-401f-a41d-91c913239acc	8ec8cff9-c42c-4c23-b8db-608759e6a85e	fa6dd296-6f04-4b0f-ad84-bc1947cf953d	0	2026-01-30 20:36:02.24342+00
dc1004db-add4-47ee-a576-0087ba386d01	8ec8cff9-c42c-4c23-b8db-608759e6a85e	68deb228-aee8-4fff-8bb5-d285ac1f7d89	1	2026-01-30 20:36:02.906507+00
d562b9a2-ed43-41e8-9765-199eac46ca44	b834e7f4-b342-4c80-83f7-c72f7a0e1949	106e6e0b-658d-48e6-8232-d099c7cdaca2	1	2026-02-01 10:31:21.319471+00
bb7863b4-5ab9-42c2-a9dc-960ebb1a071c	90041e86-a367-4409-91ff-a5f038af8dfd	c09aa38d-26fd-4cbb-af97-1aac41916ca5	1	2026-02-01 10:32:49.389184+00
ed7822b9-a67a-4c6d-836a-dfd4c510c892	6a95e0e1-6db5-47a8-87c4-d38238a26063	457af481-e0fc-4884-9141-9c2bb0828752	1	2026-02-01 10:33:10.094334+00
7e5e1be0-27ef-4a08-8368-3651f7c279b4	54eb95ab-0a2b-45ab-9e4e-bf8bd03c976e	bec4a33a-c2f5-4bd5-b0b8-3662ff6a2239	1	2026-02-01 10:33:32.123187+00
b9fb0eb6-5a90-47dd-8695-a24ffe3afc15	d9ef1e5d-1ac3-4999-9aef-770c72ff1875	3e3b1f73-e82a-4dfd-bb7f-b3a902093c4f	1	2026-02-01 10:34:04.519984+00
b53d7e01-c5db-4ab4-b985-ec803c3305af	ee720a1c-e1ee-442c-9e19-0d3338bef64a	8abedb5c-b0bf-46e1-97b5-d970f77f4866	1	2026-02-01 10:34:22.073425+00
aa0c9387-e1ea-43af-8bdf-70de57e12da9	c5bbdecb-6b9f-4f1c-b5ab-7693309dd40e	0cd7b48c-642c-420e-b12f-87a256c5b99c	1	2026-02-01 10:34:42.657536+00
5228ba9f-7d49-4466-927b-84eb6492afba	abf126ce-5adc-48b2-ac79-604d3ea7f052	24580d64-53bb-4727-b455-19e1271f5d54	1	2026-02-01 10:35:07.998738+00
8f9bffa5-2817-4251-93a8-a07baa03cf6d	a11b8083-cfb6-4ed5-bc09-2066a41ae2c9	1bb7d226-89f2-4474-b39c-fc2fa66a1f03	1	2026-02-01 10:35:48.197658+00
f2f6975e-267f-4d99-a126-9ed1d82cb15e	889fabe6-54ee-44f0-85d8-0ef1ca3868b5	a5665aaf-aa67-437c-b997-4e7a7f655db4	1	2026-02-01 10:36:44.070629+00
ad013930-0d06-46cc-aee9-a65be6cc324f	9e290045-8193-4647-86bd-eb2ffb3b9cbf	1f3556bc-f866-4104-99a3-b16d256cf44c	1	2026-02-01 10:37:05.249738+00
071025c2-1738-4e4d-b0b8-cced4f66094f	669fbf0b-9a3b-4630-89ce-2310a74dcc8c	5099dbd1-f710-4e0f-9175-0fd2ad1333ca	1	2026-02-01 10:38:13.428731+00
a6554583-4fc4-434f-a837-74fe2848fa21	5036a6fb-a067-42ac-800d-ba2f503b50a4	fd36c2ac-bcfd-4aae-ad65-1e7780e7b697	1	2026-02-01 10:38:59.238128+00
56d9fb7a-e631-4882-9a7e-cb169b0b0f54	4fde31a6-7e88-4856-bb4b-7a8159162cca	4da68809-e9cb-498a-b97c-1c0a5d0ca109	1	2026-02-01 11:01:39.728247+00
92cfe0d9-5711-4e8a-9beb-eeb7ab0f0f98	d4273ff7-eeba-4465-8e77-ddc8bc83d30c	0588aa5f-54d5-4544-a0b6-9535a4787776	1	2026-02-01 11:06:39.119869+00
2ad0d4b2-53f7-446a-8ebf-50854fb0713c	e581e980-4eb2-4aed-97ae-6bba90e6dce4	8d28777c-3ec1-401b-a3f7-abe8af032686	0	2026-02-05 19:49:07.559226+00
834d23a5-e7ec-4d4e-8a69-f35ecdd38d23	92b3bb28-b5d7-4c2c-b70d-0d078921f12f	bc41c3da-9a29-4ce5-834f-52fd21432ba8	1	2026-02-05 21:31:42.733716+00
a44f7299-8392-4c30-8f9e-3bef71205bae	b33df655-1719-43dd-b133-95dbf63a5372	a300e7fd-5eb0-48a3-ba12-00b16750b2d0	1	2026-02-05 21:33:45.294825+00
7a2df06a-eeac-4f95-8f3a-6af6463183b3	9bba228a-4cf1-4d30-b630-3cc2ca29a4ec	7957ddf4-2552-4349-92a5-eaa1cc60769e	1	2026-02-05 21:34:41.282782+00
98fc0861-9afb-41f1-b1e9-da223f7e1acf	d54eebdb-8fdc-408d-bee3-546f4ba63edd	26d6feb1-d647-4e02-a01f-af767914367f	1	2026-02-05 21:36:32.738996+00
3653a901-5e50-49a1-8d6f-eaf6c30d3104	1eb8bc24-4288-4979-8d7f-7ce480afc939	d00e94a1-caa9-48f3-9db3-e4bac9b4c096	1	2026-02-05 21:39:33.790585+00
ab035ef9-1fb5-4594-946e-5b06c036494a	160ff178-2184-4618-ab2b-62adc37483a0	900f4f8d-8d2a-465a-84c8-8659ce9eb7b9	1	2026-02-05 21:40:37.669699+00
35efd64c-30d9-4c9a-a581-8ea712a613c2	94741211-61de-44fe-b564-1984e1620f66	45d63ea1-0e12-4bf3-b620-12d572fba1cd	1	2026-02-05 21:41:47.40626+00
da3ff4de-da78-4c58-9ac5-1e7eb467e664	fd9c6a36-14ed-4e6b-8dc0-60b324fc0caf	813222ab-33b9-4937-a23c-bf6059a12713	1	2026-02-05 21:43:42.819662+00
401c4821-37e9-4fe4-afbb-1e5a781f5a42	6a8b1f80-60c2-497b-94e7-62540c020943	d33388e3-082c-4c2b-9885-85cfd4705373	1	2026-02-05 21:49:55.196534+00
74bac9ba-a6ee-4587-97f2-ea34c720f4b2	7556d0cb-dcd5-4677-accf-3bb7b8ba963e	9123b919-fdbe-478d-9757-c06c16606b63	1	2026-02-05 21:52:18.988815+00
58fc5011-88a7-436c-b4a4-c6bb63cdff8c	d19b7fe8-28a1-4957-a684-38586eeaa293	8ed4cf1b-282b-4ab8-8983-2209bd440373	1	2026-02-05 21:55:18.708994+00
\.


--
-- Data for Name: template_translations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.template_translations (id, template_id, language_code, name, description, created_at) FROM stdin;
2b3d9915-afcb-4d2b-ac2d-573d85fb23d3	553119c9-7384-4f72-8885-e461679761de	en	General Crop Health Audit	Audit for general crop health	2026-01-30 00:08:38.921321+00
5cd600e6-4f48-42f4-9be7-adcb8716c126	3087bfd4-926c-450c-8ef1-bae06f734c4e	en	Standard Soil Audit	Comprehensive soil health analysis	2026-01-30 00:21:12.757619+00
66007f25-486a-46d4-8d85-5cb8ceb625dd	8ec8cff9-c42c-4c23-b8db-608759e6a85e	en	test	asdasdasdasdasdsad	2026-01-30 20:36:01.949808+00
6a8914ac-1ded-4446-af00-2da094f1c4d8	b834e7f4-b342-4c80-83f7-c72f7a0e1949	en	Audit Template	Test	2026-02-01 10:31:21.319471+00
5fc76c3b-52cb-4973-b458-32d45217ac98	90041e86-a367-4409-91ff-a5f038af8dfd	en	Audit Template	Test	2026-02-01 10:32:49.389184+00
c861c511-2bf2-40b0-938c-a27b48f6b64b	6a95e0e1-6db5-47a8-87c4-d38238a26063	en	Audit Template	Test	2026-02-01 10:33:10.094334+00
0314a0f5-01f3-44be-a363-f76933019fa2	54eb95ab-0a2b-45ab-9e4e-bf8bd03c976e	en	Audit Template	Test	2026-02-01 10:33:32.123187+00
101feaf0-e231-472a-88b1-f45c8b4046e5	d9ef1e5d-1ac3-4999-9aef-770c72ff1875	en	Audit Template	Test	2026-02-01 10:34:04.519984+00
7601b790-a531-441e-b33b-bafa730c4a9e	ee720a1c-e1ee-442c-9e19-0d3338bef64a	en	Audit Template	Test	2026-02-01 10:34:22.073425+00
368c126c-1bd8-44e6-9a7f-2b9e5c62542c	c5bbdecb-6b9f-4f1c-b5ab-7693309dd40e	en	Audit Template	Test	2026-02-01 10:34:42.657536+00
1ff5fc29-008c-4254-8a8c-986516842e9c	abf126ce-5adc-48b2-ac79-604d3ea7f052	en	Audit Template	Test	2026-02-01 10:35:07.998738+00
4f2c3c42-d4d6-4b6c-bd6d-65ef242a0245	a11b8083-cfb6-4ed5-bc09-2066a41ae2c9	en	Audit Template	Test	2026-02-01 10:35:48.197658+00
d6ab6363-1875-4e51-9aa3-e88c4372f425	889fabe6-54ee-44f0-85d8-0ef1ca3868b5	en	Audit Template	Test	2026-02-01 10:36:44.070629+00
cd8d2144-4f51-4c03-89e5-41831b4bebfd	9e290045-8193-4647-86bd-eb2ffb3b9cbf	en	Audit Template	Test	2026-02-01 10:37:05.249738+00
f6abeeaa-eb47-4a2f-9a4e-6baf2bcea551	669fbf0b-9a3b-4630-89ce-2310a74dcc8c	en	Audit Template	Test	2026-02-01 10:38:13.428731+00
a8199ea6-6375-4b44-a96f-1c702b6e0dff	5036a6fb-a067-42ac-800d-ba2f503b50a4	en	Audit Template	Test	2026-02-01 10:38:59.238128+00
28af7797-d144-449e-bed8-5d53d21adab7	4fde31a6-7e88-4856-bb4b-7a8159162cca	en	Audit Template	Test	2026-02-01 11:01:39.728247+00
55813543-eb7b-4f78-813a-b94430c62fd2	d4273ff7-eeba-4465-8e77-ddc8bc83d30c	en	10 Param Template	Test	2026-02-01 11:06:39.119869+00
a95a2d85-c91e-4ef4-9b7b-e8450d223ee3	e581e980-4eb2-4aed-97ae-6bba90e6dce4	en	Wrting questions	For testing the stuff at the end	2026-02-05 19:49:07.387068+00
99296693-f9ba-4c7f-be52-6115556233c6	92b3bb28-b5d7-4c2c-b70d-0d078921f12f	en	Report Test	\N	2026-02-05 21:31:42.733716+00
b399b5c5-e9bc-4306-9d01-e8c0914079d1	b33df655-1719-43dd-b133-95dbf63a5372	en	Report Test	\N	2026-02-05 21:33:45.294825+00
3f4847c6-1148-4391-afde-ff142b401b1a	9bba228a-4cf1-4d30-b630-3cc2ca29a4ec	en	Report Test	\N	2026-02-05 21:34:41.282782+00
9d7c41c6-667a-4c30-a192-7b95306c5d8d	d54eebdb-8fdc-408d-bee3-546f4ba63edd	en	Report Test	\N	2026-02-05 21:36:32.738996+00
71059cd0-7392-4de7-88ae-f98dda53fb87	1eb8bc24-4288-4979-8d7f-7ce480afc939	en	Report Test	\N	2026-02-05 21:39:33.790585+00
a280517f-256d-453f-a749-da85050b1c8b	160ff178-2184-4618-ab2b-62adc37483a0	en	Report Test	\N	2026-02-05 21:40:37.669699+00
cb56876a-2dcc-4909-a6d3-e598bd1351a3	94741211-61de-44fe-b564-1984e1620f66	en	Report Test	\N	2026-02-05 21:41:47.40626+00
70491eb3-82bb-4349-90c3-603486f06a98	fd9c6a36-14ed-4e6b-8dc0-60b324fc0caf	en	Report Test	\N	2026-02-05 21:43:42.819662+00
09927935-34b4-435c-bb81-d7e091cfa33d	6a8b1f80-60c2-497b-94e7-62540c020943	en	Report Test	\N	2026-02-05 21:49:55.196534+00
1dd13f37-f653-4234-a538-87a13cde04dc	7556d0cb-dcd5-4677-accf-3bb7b8ba963e	en	Report Test	\N	2026-02-05 21:52:18.988815+00
5e990c9c-34d9-48c9-b7d3-702597e53fd0	d19b7fe8-28a1-4957-a684-38586eeaa293	en	Report Test	\N	2026-02-05 21:55:18.708994+00
\.


--
-- Data for Name: templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.templates (id, code, is_system_defined, owner_org_id, crop_type_id, is_active, version, created_at, updated_at, created_by, updated_by) FROM stdin;
553119c9-7384-4f72-8885-e461679761de	GEN_CROP_HEALTH_V1	f	8b411c61-9885-4672-ba08-e45709934575	\N	t	1	2026-01-30 00:08:38.921321+00	2026-01-30 00:08:38.921321+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N
3087bfd4-926c-450c-8ef1-bae06f734c4e	SOIL_AUDIT_V1	f	8b411c61-9885-4672-ba08-e45709934575	\N	t	1	2026-01-30 00:09:33.180136+00	2026-01-30 00:21:12.757619+00	08c368c7-0ea2-4dad-a5fe-5e8e180b0b44	3f3a3a39-d867-45a8-b901-74a7e27c95f3
8ec8cff9-c42c-4c23-b8db-608759e6a85e	CODE0001	f	8b411c61-9885-4672-ba08-e45709934575	\N	t	1	2026-01-30 20:36:01.949808+00	2026-01-30 20:36:01.949808+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
b834e7f4-b342-4c80-83f7-c72f7a0e1949	TEMP_1769941881	f	db3950f7-2c3d-40ec-8646-9548956aa267	\N	t	1	2026-02-01 10:31:21.319471+00	2026-02-01 10:31:21.319471+00	5b010aef-d0b8-40cc-bc0e-6b6c133cac49	5b010aef-d0b8-40cc-bc0e-6b6c133cac49
90041e86-a367-4409-91ff-a5f038af8dfd	TEMP_1769941969	f	9463b7f0-b657-467c-bc0e-0f21817e623c	\N	t	1	2026-02-01 10:32:49.389184+00	2026-02-01 10:32:49.389184+00	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c	b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c
6a95e0e1-6db5-47a8-87c4-d38238a26063	TEMP_1769941990	f	1118a620-482f-4241-b722-35653792fda9	\N	t	1	2026-02-01 10:33:10.094334+00	2026-02-01 10:33:10.094334+00	bf660c8b-3818-4cf7-85f1-3071c0a7943c	bf660c8b-3818-4cf7-85f1-3071c0a7943c
54eb95ab-0a2b-45ab-9e4e-bf8bd03c976e	TEMP_1769942012	f	cbbff567-e72f-46ff-ad79-4cf26c3260c8	\N	t	1	2026-02-01 10:33:32.123187+00	2026-02-01 10:33:32.123187+00	c7a092a7-d354-498d-b23a-d4802d99ccb4	c7a092a7-d354-498d-b23a-d4802d99ccb4
d9ef1e5d-1ac3-4999-9aef-770c72ff1875	TEMP_1769942044	f	6bf71e9a-2b50-4a27-9ff9-972b5a52eb8e	\N	t	1	2026-02-01 10:34:04.519984+00	2026-02-01 10:34:04.519984+00	2199f334-fccd-46ff-b45c-2cd81aadeca2	2199f334-fccd-46ff-b45c-2cd81aadeca2
ee720a1c-e1ee-442c-9e19-0d3338bef64a	TEMP_1769942062	f	461445ad-b03d-418c-8049-49cbadf6519b	\N	t	1	2026-02-01 10:34:22.073425+00	2026-02-01 10:34:22.073425+00	b46ab366-7dcb-4ee5-a558-dc328db04159	b46ab366-7dcb-4ee5-a558-dc328db04159
c5bbdecb-6b9f-4f1c-b5ab-7693309dd40e	TEMP_1769942082	f	c6957a10-58cf-4f2d-ab85-b8b0dbd6ed7c	\N	t	1	2026-02-01 10:34:42.657536+00	2026-02-01 10:34:42.657536+00	979cfcfd-a872-40df-8380-dbe81f29e7a5	979cfcfd-a872-40df-8380-dbe81f29e7a5
abf126ce-5adc-48b2-ac79-604d3ea7f052	TEMP_1769942107	f	36acd251-59ee-4f22-a3e3-f14e91a16706	\N	t	1	2026-02-01 10:35:07.998738+00	2026-02-01 10:35:07.998738+00	810cc398-af79-4d96-9eee-af0f1bbf8683	810cc398-af79-4d96-9eee-af0f1bbf8683
a11b8083-cfb6-4ed5-bc09-2066a41ae2c9	TEMP_1769942148	f	ba0154e3-56bb-4d8d-9db9-b143367cbc85	\N	t	1	2026-02-01 10:35:48.197658+00	2026-02-01 10:35:48.197658+00	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a
889fabe6-54ee-44f0-85d8-0ef1ca3868b5	TEMP_1769942204	f	eb79439d-c6df-4d41-8c3d-0619964d91e1	\N	t	1	2026-02-01 10:36:44.070629+00	2026-02-01 10:36:44.070629+00	ef5984b4-54b6-47cf-a9bb-ca02cadc0180	ef5984b4-54b6-47cf-a9bb-ca02cadc0180
9e290045-8193-4647-86bd-eb2ffb3b9cbf	TEMP_1769942225	f	d1a8266c-b125-4c57-b1d9-69f785e7e7ec	\N	t	1	2026-02-01 10:37:05.249738+00	2026-02-01 10:37:05.249738+00	70904796-fe39-4007-b892-a8aa3c8e0e8f	70904796-fe39-4007-b892-a8aa3c8e0e8f
669fbf0b-9a3b-4630-89ce-2310a74dcc8c	TEMP_1769942293	f	c4a4f415-3907-463e-86e0-2d7148e90d28	\N	t	1	2026-02-01 10:38:13.428731+00	2026-02-01 10:38:13.428731+00	1ce1ba48-b899-4217-8fd9-2124dd4765c6	1ce1ba48-b899-4217-8fd9-2124dd4765c6
5036a6fb-a067-42ac-800d-ba2f503b50a4	TEMP_1769942339	f	ab3df532-1696-45db-a97f-ebd3afaee92c	\N	t	1	2026-02-01 10:38:59.238128+00	2026-02-01 10:38:59.238128+00	05e362b8-0b73-44ed-bded-ef4e0a40dd47	05e362b8-0b73-44ed-bded-ef4e0a40dd47
4fde31a6-7e88-4856-bb4b-7a8159162cca	TEMP_1769943699	f	c0fbcba5-fca1-4960-88fb-5a5aeb9684e3	\N	t	1	2026-02-01 11:01:39.728247+00	2026-02-01 11:01:39.728247+00	b9c25548-e5ba-4200-9dc9-1ba98f332540	b9c25548-e5ba-4200-9dc9-1ba98f332540
d4273ff7-eeba-4465-8e77-ddc8bc83d30c	TEMP_1769943999	f	a7602188-54e2-4c7e-b10a-f8971dd2c1c7	\N	t	1	2026-02-01 11:06:39.119869+00	2026-02-01 11:06:39.119869+00	a30a9865-926a-4d26-af0d-42e44657b429	a30a9865-926a-4d26-af0d-42e44657b429
e581e980-4eb2-4aed-97ae-6bba90e6dce4	CODE-1212	f	8b411c61-9885-4672-ba08-e45709934575	\N	t	1	2026-02-05 19:49:07.387068+00	2026-02-05 19:49:07.387068+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3
92b3bb28-b5d7-4c2c-b70d-0d078921f12f	T_1770327102	f	27227759-8c29-4ba3-8ba5-153607db5c4c	\N	t	1	2026-02-05 21:31:42.733716+00	2026-02-05 21:31:42.733716+00	53126f3a-94da-4363-b20d-61a85c99574a	53126f3a-94da-4363-b20d-61a85c99574a
b33df655-1719-43dd-b133-95dbf63a5372	T_1770327224	f	bc651c65-73d1-41c9-a03a-275b47df7b10	\N	t	1	2026-02-05 21:33:45.294825+00	2026-02-05 21:33:45.294825+00	1214c599-c7c2-490b-a895-e45b985b027b	1214c599-c7c2-490b-a895-e45b985b027b
9bba228a-4cf1-4d30-b630-3cc2ca29a4ec	T_1770327280	f	0a61f5ac-582c-4856-8072-27fcad588698	\N	t	1	2026-02-05 21:34:41.282782+00	2026-02-05 21:34:41.282782+00	d9cd5b64-e423-4710-bcfe-73606bcca78c	d9cd5b64-e423-4710-bcfe-73606bcca78c
d54eebdb-8fdc-408d-bee3-546f4ba63edd	T_1770327392	f	88810bde-bf96-43e8-9791-937cd4a7e062	\N	t	1	2026-02-05 21:36:32.738996+00	2026-02-05 21:36:32.738996+00	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc
1eb8bc24-4288-4979-8d7f-7ce480afc939	T_1770327572	f	5e03962b-3b0c-4bd5-9f17-6349e82083cb	\N	t	1	2026-02-05 21:39:33.790585+00	2026-02-05 21:39:33.790585+00	fc5165e6-6519-496f-a3dd-1435bc308b5f	fc5165e6-6519-496f-a3dd-1435bc308b5f
160ff178-2184-4618-ab2b-62adc37483a0	T_1770327636	f	8bb34a8d-f5bb-41cf-ba29-87e5c652c03f	\N	t	1	2026-02-05 21:40:37.669699+00	2026-02-05 21:40:37.669699+00	d655e067-4edd-4516-b1b6-821c3c33cfc5	d655e067-4edd-4516-b1b6-821c3c33cfc5
94741211-61de-44fe-b564-1984e1620f66	T_1770327706	f	f3200c57-c6b8-4f2d-80fe-24b9a6359f6c	\N	t	1	2026-02-05 21:41:47.40626+00	2026-02-05 21:41:47.40626+00	13ac055f-b943-4f6d-8182-babe636544df	13ac055f-b943-4f6d-8182-babe636544df
fd9c6a36-14ed-4e6b-8dc0-60b324fc0caf	T_1770327821	f	f7028cb1-7e87-4fd7-8aa1-4ea8b97ccb43	\N	t	1	2026-02-05 21:43:42.819662+00	2026-02-05 21:43:42.819662+00	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	5a96c5d0-7467-44d3-9f9b-614ce91f0bfc
6a8b1f80-60c2-497b-94e7-62540c020943	T_1770328194	f	e33b94b6-cfc5-4d7e-98a4-2259867e45b4	\N	t	1	2026-02-05 21:49:55.196534+00	2026-02-05 21:49:55.196534+00	ebc86578-b9a2-456f-b884-f964c1fb26f9	ebc86578-b9a2-456f-b884-f964c1fb26f9
7556d0cb-dcd5-4677-accf-3bb7b8ba963e	T_1770328337	f	718996de-ba3d-4b71-9a19-a6e97d2947ee	\N	t	1	2026-02-05 21:52:18.988815+00	2026-02-05 21:52:18.988815+00	7eddd813-1060-42a3-aa36-abc2c6529e0f	7eddd813-1060-42a3-aa36-abc2c6529e0f
d19b7fe8-28a1-4957-a684-38586eeaa293	T_1770328517	f	f9761969-f234-4bb8-9b46-2ea70ad5b735	\N	t	1	2026-02-05 21:55:18.708994+00	2026-02-05 21:55:18.708994+00	021aea9d-7fe9-4488-ae61-eebf6d2af731	021aea9d-7fe9-4488-ae61-eebf6d2af731
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, phone, password_hash, first_name, last_name, is_active, is_verified, last_login, preferred_language, created_at, updated_at, bio, address, profile_picture_url, specialization) FROM stdin;
f5f9ef2a-8a6f-4973-900c-0e0bca8ee95c	fsp_agent@gmail.com	+914885168083	$2b$12$YmcE.N7WiD0QFQwMq1xKeeoVVGf9XdVVqAieYNCf71JCen7ciebdO	FSP	Agent	t	t	\N	en	2026-01-30 00:08:38.37044+00	2026-01-30 00:08:38.37044+00	\N	\N	\N	\N
7bd0073c-4c78-429f-9421-d5d52db3fd53	fsp_expert@gmail.com	+911306237160	$2b$12$VcodyrY0jwxsB1bjM604CetrexONBZ2lUbfeNPC1cqNqn6L2WmPE.	FSP	Expert	t	t	\N	en	2026-01-30 00:08:38.612916+00	2026-01-30 00:08:38.612916+00	\N	\N	\N	\N
d77da629-52f1-46c9-9118-dbe7fe92c333	farmer_1769942202@test.com	\N	$2b$12$qn0j9Mglee5xCWqv0szxB.LXDZ99FdGwlOeY7L.mt0Igrz8VFUuqm	Farmer	Test	t	f	\N	en	2026-02-01 10:36:43.263164+00	2026-02-01 10:36:43.263164+00	\N	\N	\N	\N
ef5984b4-54b6-47cf-a9bb-ca02cadc0180	fsp_1769942203@test.com	\N	$2b$12$qVS/aswZhZcq4Nmuu7lnce9pkb3FnEJ/Ag/FV9C8x78Fvh2R.EDmq	FSP	Admin	t	f	\N	en	2026-02-01 10:36:43.557632+00	2026-02-01 10:36:43.557632+00	\N	\N	\N	\N
66d51b1b-c21b-4f8c-99ba-c2854ceeab97	farmer_1769942224@test.com	\N	$2b$12$5mRvK8aN4AUbF9FZdoFrOOGgkbpa/NTtjZzc/1mGWNpy88MLJxeku	Farmer	Test	t	f	\N	en	2026-02-01 10:37:04.517434+00	2026-02-01 10:37:04.517434+00	\N	\N	\N	\N
70904796-fe39-4007-b892-a8aa3c8e0e8f	fsp_1769942224@test.com	\N	$2b$12$ACLYeh0xOCjFAnBs4/R.r.Jf/ZeVoxMVM0ZlsQuMO7dICgivAHz8u	FSP	Admin	t	f	\N	en	2026-02-01 10:37:04.767399+00	2026-02-01 10:37:04.767399+00	\N	\N	\N	\N
3f82b4a7-b270-4d68-9e02-e9068eaa668f	farmer_1769942292@test.com	\N	$2b$12$IlemFRcOe0C8S.qYUe5HSurXdocNF7QThphgstLtC8pbskJDjEdqO	Farmer	Test	t	f	\N	en	2026-02-01 10:38:12.676785+00	2026-02-01 10:38:12.676785+00	\N	\N	\N	\N
1ce1ba48-b899-4217-8fd9-2124dd4765c6	fsp_1769942292@test.com	\N	$2b$12$9AAN3HmnquFzNsDv3oklEubNj/U6Uiz3dN89NTUVY4tyKojMyFoOi	FSP	Admin	t	f	\N	en	2026-02-01 10:38:12.927986+00	2026-02-01 10:38:12.927986+00	\N	\N	\N	\N
d5104c40-d4cc-47ac-a700-0c7414c1b26a	farmer_1769942338@test.com	\N	$2b$12$k.itjXkk21TVsnq1rJcwEOJ32TWStIOirQM8fXHEyAET.s5a/m5Zq	Farmer	Test	t	f	\N	en	2026-02-01 10:38:58.438532+00	2026-02-01 10:38:58.438532+00	\N	\N	\N	\N
05e362b8-0b73-44ed-bded-ef4e0a40dd47	fsp_1769942338@test.com	\N	$2b$12$NkHriBE3BTX7tQx7vT8J6eWmOubbA4D3WTysMg504dOKa1xwop2Pi	FSP	Admin	t	f	\N	en	2026-02-01 10:38:58.721+00	2026-02-01 10:38:58.721+00	\N	\N	\N	\N
bfdafb1c-258c-487a-84a9-8df88d6f7efd	farmer.test.1769940297@example.com	\N	$2b$12$OlhmQtaq6bp1CS82Bah0reoOhBR.21IAKT9F5dM.fPHteF1IPocq2	Ramesh	Kumar	t	f	\N	en	2026-02-01 10:04:57.931374+00	2026-02-01 10:04:57.931374+00	\N	\N	\N	\N
3be02ab8-a88f-4a03-b781-3fffa07e5096	fsp.test.1769940298@example.com	\N	$2b$12$RpSh6xPTQYPWhdkxn8JuK.Mwyj3erMMEIuDad8icz0wZFsfzXxx9K	Suresh	Reddy	t	f	\N	en	2026-02-01 10:04:58.325545+00	2026-02-01 10:04:58.325545+00	\N	\N	\N	\N
a7c620dc-005f-41e4-a09c-84a578fdff32	debug_farmer_1769940408@test.com	\N	$2b$12$hjyxZC9YDRvbeq9G5a03QuZosIeuwB9tu6B2WL76HlckaEkJ6nDsu	Test	Farmer	t	f	\N	en	2026-02-01 10:06:48.007461+00	2026-02-01 10:06:48.007461+00	\N	\N	\N	\N
ea72b36b-fe10-483e-acca-7274bdab7600	debug_fsp_1769940408@test.com	\N	$2b$12$REnD8GboklsnsTvSBHJT8O8D8q.95X9fm1roG12tjF8YY7vwnyTE2	Test	FSP	t	f	\N	en	2026-02-01 10:06:48.270951+00	2026-02-01 10:06:48.270951+00	\N	\N	\N	\N
eb63636b-e512-4cd7-9296-f0d38d62f74d	quick_farmer_1769940606@test.com	\N	$2b$12$/NEXyipNfWo51oDaZoqzyOWfRlUqb4liTg3zoDLfkqOXs76yeOsYa	Quick	Farmer	t	f	\N	en	2026-02-01 10:10:06.602916+00	2026-02-01 10:10:06.602916+00	\N	\N	\N	\N
fc777437-f8d9-4e04-bc0a-011507805218	quick_fsp_1769940606@test.com	\N	$2b$12$kK7lP4Y.Sj7BOtpwFsH7XuEBJr2FXorFCgudPeu4NunYvtWApV77K	Quick	FSP	t	f	\N	en	2026-02-01 10:10:06.933671+00	2026-02-01 10:10:06.933671+00	\N	\N	\N	\N
26872c85-6000-4eec-baab-a1a4b8a27258	farmer_1769941799@test.com	\N	$2b$12$hGDt4QILPH5nRLV1CBQjcusPSZdrVvyYgi8XZ0hYcCfQURBuH95Vq	Farmer	Test	t	f	\N	en	2026-02-01 10:29:59.8606+00	2026-02-01 10:29:59.8606+00	\N	\N	\N	\N
d24c619c-0783-4510-949c-49445cea0202	fsp_1769941800@test.com	\N	$2b$12$7gmk.Tvo9AyydwJxx1n8huS1PmvjtbrR3wfyQu0l7ARwDxcN5kaR.	FSP	Admin	t	f	\N	en	2026-02-01 10:30:00.190946+00	2026-02-01 10:30:00.190946+00	\N	\N	\N	\N
aec76aa4-0bf4-40bb-9307-de54a5d205a5	farmer_1769941880@test.com	\N	$2b$12$CBzys1CQ1RvapLiAFg5lWuhNtqmeNj69s/VIAbvMCfG7bDSMa3jWe	Farmer	Test	t	f	\N	en	2026-02-01 10:31:20.558812+00	2026-02-01 10:31:20.558812+00	\N	\N	\N	\N
5b010aef-d0b8-40cc-bc0e-6b6c133cac49	fsp_1769941880@test.com	\N	$2b$12$0DrdTtCFYOy2wPixAu5lAevaULPKKMlL59UjoPm0V65qTX6O8Csv.	FSP	Admin	t	f	\N	en	2026-02-01 10:31:20.810947+00	2026-02-01 10:31:20.810947+00	\N	\N	\N	\N
ee6157bd-176f-4f75-8cea-64adb841884f	farmer_1769941968@test.com	\N	$2b$12$zJPjyfFuFZyLTmRAyQA8Pe5eEbHSI/zWu4AS7Na4dC7oSw4e/ZCpS	Farmer	Test	t	f	\N	en	2026-02-01 10:32:48.651763+00	2026-02-01 10:32:48.651763+00	\N	\N	\N	\N
b5634c7d-f77c-4a7b-bd3d-79bfeb5a7e0c	fsp_1769941968@test.com	\N	$2b$12$1eb4nUtRHUNeC449s0VnFeFXfALwg/PG45AQ1XVrf/V72Q1kQ9vt6	FSP	Admin	t	f	\N	en	2026-02-01 10:32:48.908549+00	2026-02-01 10:32:48.908549+00	\N	\N	\N	\N
ee193894-167a-4355-8899-7c19ba395e9f	farmer_1769941989@test.com	\N	$2b$12$PZS3l/WCY0nwMFr4OvhaX.QtBJy4Ou7bSPxlyFqKJRBxUdJgfHLvG	Farmer	Test	t	f	\N	en	2026-02-01 10:33:09.361929+00	2026-02-01 10:33:09.361929+00	\N	\N	\N	\N
bf660c8b-3818-4cf7-85f1-3071c0a7943c	fsp_1769941989@test.com	\N	$2b$12$sD.nZiiB6B1wlwMCQKU9Vei2vBsxpH5m1JDodAWHOMJSASnS/Iqxq	FSP	Admin	t	f	\N	en	2026-02-01 10:33:09.610292+00	2026-02-01 10:33:09.610292+00	\N	\N	\N	\N
3c1aab18-4eb2-4ab2-bcca-993c37e7fab1	farmer_1769942011@test.com	\N	$2b$12$YD9FcnbAgEelibfLMgRngeW08RdLQ4OkGrmF.JgM15rLkp5tCS1Xe	Farmer	Test	t	f	\N	en	2026-02-01 10:33:31.398239+00	2026-02-01 10:33:31.398239+00	\N	\N	\N	\N
c7a092a7-d354-498d-b23a-d4802d99ccb4	fsp_1769942011@test.com	\N	$2b$12$B1ahl71VgsP5HP2b017QjO5vQa8Vzr8ngk3vF/vCwEj6kDg855P6O	FSP	Admin	t	f	\N	en	2026-02-01 10:33:31.648167+00	2026-02-01 10:33:31.648167+00	\N	\N	\N	\N
3e72bdbc-89a7-4009-a93e-bba6fec86530	farmer_1769942043@test.com	\N	$2b$12$ONTwkqVxQp2xUfuaugEUluY8cRlRz1NOP6oHlv9Z1qIE1RoKLXgfe	Farmer	Test	t	f	\N	en	2026-02-01 10:34:03.787045+00	2026-02-01 10:34:03.787045+00	\N	\N	\N	\N
2199f334-fccd-46ff-b45c-2cd81aadeca2	fsp_1769942044@test.com	\N	$2b$12$RWvd1USsJvVSLKVZM9x0S.Giiji1qO2dlXiqdLQ85BU5Udq/c0CEK	FSP	Admin	t	f	\N	en	2026-02-01 10:34:04.037527+00	2026-02-01 10:34:04.037527+00	\N	\N	\N	\N
c5e779fa-7e25-4b84-b410-a55bd0c9e219	farmer_1769942061@test.com	\N	$2b$12$Za7rMUWjIawsIwmTXY3E7OlFbWMx2Cu3JEQM7gOIXaq..Uk151bPm	Farmer	Test	t	f	\N	en	2026-02-01 10:34:21.332909+00	2026-02-01 10:34:21.332909+00	\N	\N	\N	\N
b46ab366-7dcb-4ee5-a558-dc328db04159	fsp_1769942061@test.com	\N	$2b$12$ETgONLTzHl.LgluW.2.3aebNtHxhhl8zGCULj5OIJccfAiFY/4hP2	FSP	Admin	t	f	\N	en	2026-02-01 10:34:21.583361+00	2026-02-01 10:34:21.583361+00	\N	\N	\N	\N
b8cf8398-0dff-42c3-99ab-aaa2bcf646e6	farmer_1769942081@test.com	\N	$2b$12$spLFAY.Vl8j3nqDQ2Y.VHORl6fFcD2lG1fcrJkt0RDp3UbDELqpQ6	Farmer	Test	t	f	\N	en	2026-02-01 10:34:41.922359+00	2026-02-01 10:34:41.922359+00	\N	\N	\N	\N
979cfcfd-a872-40df-8380-dbe81f29e7a5	fsp_1769942082@test.com	\N	$2b$12$UUt7k9mFB75xcmk89qDiyu1eNhQ31tfPZOcvbl.BU2vfXYP5ioXUi	FSP	Admin	t	f	\N	en	2026-02-01 10:34:42.172658+00	2026-02-01 10:34:42.172658+00	\N	\N	\N	\N
a031994b-5afb-4fa2-9d8a-8004d7e8c9a3	farmer_1769942107@test.com	\N	$2b$12$FnMzp2vAVwRJb7EnKlWnOO1mqv3MLnCZi.jhoPLlJBgrekKUJp/Se	Farmer	Test	t	f	\N	en	2026-02-01 10:35:07.272123+00	2026-02-01 10:35:07.272123+00	\N	\N	\N	\N
810cc398-af79-4d96-9eee-af0f1bbf8683	fsp_1769942107@test.com	\N	$2b$12$5EpEIVfrUt.bGpCcJR3kq.ZGy5URmKMVX1mLU8vNIW9Zyi.o/G/E6	FSP	Admin	t	f	\N	en	2026-02-01 10:35:07.51942+00	2026-02-01 10:35:07.51942+00	\N	\N	\N	\N
2e6f6fed-9d3d-4b85-87d0-a134932d0dd7	farmer_1769942147@test.com	\N	$2b$12$kSUvwyswJXhaZlt5Rt7uq.o0ehJ8R9mHWqwovZhZd/fUWVANyLRnO	Farmer	Test	t	f	\N	en	2026-02-01 10:35:47.438405+00	2026-02-01 10:35:47.438405+00	\N	\N	\N	\N
fc3a30d9-ca2c-435c-a0f1-b80f47cd7bc1	farmer_1769943698@test.com	\N	$2b$12$8oWU6JZ/9mPTScwwOsH9TuhI9b4JWXqjzAMgYpIBk1gzVuJpVi9pS	Farmer	Test	t	f	\N	en	2026-02-01 11:01:38.993699+00	2026-02-01 11:01:38.993699+00	\N	\N	\N	\N
e1c90e5e-ad8f-4c88-9bfa-c1e2f7fe618a	fsp_1769942147@test.com	\N	$2b$12$0dd9.kwmZ4vX1FS3y9MVMOPKbHnWJKsGkez.UX907h/3ghnkzupb2	FSP	Admin	t	f	\N	en	2026-02-01 10:35:47.683852+00	2026-02-01 10:35:47.683852+00	\N	\N	\N	\N
b9c25548-e5ba-4200-9dc9-1ba98f332540	fsp_1769943699@test.com	\N	$2b$12$Rkwgf9vvp7YsnHNfoSPB3eucUQzIJpy6SZEMid2.goPljME8AmnK2	FSP	Admin	t	f	\N	en	2026-02-01 11:01:39.260549+00	2026-02-01 11:01:39.260549+00	\N	\N	\N	\N
1a8f4448-290b-48ff-9f17-2d76e841a1f3	farmer_1769943997@test.com	\N	$2b$12$O3CFFQcaINf.INZDFtJRGedcnSpOwIQ1JAsZJWEhCqmPlwMVPZkTS	Farmer	Test	t	f	\N	en	2026-02-01 11:06:37.884134+00	2026-02-01 11:06:37.884134+00	\N	\N	\N	\N
a30a9865-926a-4d26-af0d-42e44657b429	fsp_1769943998@test.com	\N	$2b$12$unbOEFPnSOTGuk2pRcNHr.L2t8XHdJ8ENCRsH6e1Z3KNmKt8Uc7Bu	FSP	Admin	t	f	\N	en	2026-02-01 11:06:38.210829+00	2026-02-01 11:06:38.210829+00	\N	\N	\N	\N
fe4d1e04-7569-409d-8bfc-f7319e7ea582	niren@gmail.com	+912647632604	$2b$12$NTtoq3fz2/g5KeT/R4Oa2OSIPwPLaDaBBHyhu41YuHGSLyS8DW0dW	Niren	Farmer	t	t	2026-02-11 08:37:22.17909+00	en	2026-01-30 00:08:37.884635+00	2026-02-11 08:37:21.833715+00	\N	\N	\N	\N
08c368c7-0ea2-4dad-a5fe-5e8e180b0b44	fsp_manager@gmail.com	+918459985708	$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYILSBHe3Uy	FSP	Manager	t	t	\N	en	2026-01-30 00:08:38.130447+00	2026-02-05 22:38:15.259701+00	\N	\N	\N	\N
7ebef8e8-4a6d-4420-ac3a-e01a33f6c975	superadmin@uzhathunai.com	+919000000001	$2b$12$eGp1amhJ0g/DHz3PVwdCN.JKTcGSBhwp72IfMEFfNlg.a4FQDm5Pm	System	Admin	t	t	2026-02-08 07:10:33.477303+00	en	2026-01-30 00:05:35.616224+00	2026-02-08 07:10:33.16151+00	\N	\N	\N	\N
1cba4cd7-a5a2-407a-b391-5bea5f6f2aa3	farmer_1770328517@test.com	\N	$2b$12$MPpiqL85rMX6MtZbV4BP1.1LeVm1P.qB40FkSnwrRD7QBto059TQe	Farmer	User	t	f	\N	en	2026-02-05 21:55:17.777637+00	2026-02-05 21:55:17.777637+00	\N	\N	\N	\N
088ad156-635f-4689-8a9f-31187419e964	farmer.test.1770328660@example.com	\N	$2b$12$a4iCSxbZB0bS4vWrP1f6vuhWyz9AwhjsIJH9R/.0zIanzR4d8mnX.	Ramesh	Kumar	t	f	\N	en	2026-02-05 21:57:40.976895+00	2026-02-05 21:57:40.976895+00	\N	\N	\N	\N
2e7c5e4c-423c-4bd0-9f3d-e359054f285a	fsp.test.1770328661@example.com	\N	$2b$12$qo3jFANuQMMRWJyFU5L0lOozP5D3Hi3HcJf8RRo9QZ.tdF7gEcKou	Suresh	Reddy	t	f	\N	en	2026-02-05 21:57:41.374707+00	2026-02-05 21:57:41.374707+00	\N	\N	\N	\N
b1dd0b01-8388-41bb-a686-f75f5aa559b9	fsp.test.1770330825@example.com	\N	$2b$12$h2uPL8X4YIQYCVzHrjyy9..1YGaI.jZ0.nDrMT7Ge.evPtah5OT96	Suresh	Reddy	t	f	\N	en	2026-02-05 22:33:45.676541+00	2026-02-05 22:33:45.676541+00	\N	\N	\N	\N
723079fb-4d41-408d-958c-a1d417576d82	farmer.test.1770330825@example.com	\N	$2b$12$if8iM9RT1D0KKUHHF3VKCu4Pw2K4FWoLD9FRBM7KaX/6RHa75q4/.	Ramesh	Kumar	t	f	2026-02-05 22:33:46.046924+00	en	2026-02-05 22:33:45.443237+00	2026-02-05 22:33:45.866224+00	\N	\N	\N	\N
c5154fda-1c6a-4c09-bd67-0482fe81f7d8	amit@gmail.com	9876543210	$2b$12$Coizq.v/1iTwH1jjtRds7e1h/z35s.2DJJ4appCoL6VQ3NBnHKamK	Amit	Shah	t	f	2026-02-09 14:46:39.930037+00	en	2026-02-09 14:25:30.496339+00	2026-02-09 14:46:39.615386+00	\N	\N	\N	\N
43a76c7a-3acb-40a9-8c3c-9e0235d9a13f	fsp_1770326732@test.com	\N	$2b$12$AVCbyuJrj.po6eQ3JX1MXeYF2O36dtN7qbYh6JcYyhmAEvqTiIQO.	FSP	User	t	f	\N	en	2026-02-05 21:25:32.7188+00	2026-02-05 21:25:32.7188+00	\N	\N	\N	\N
5526632a-9523-4219-b2ca-708559772fb8	farmer_1770326732@test.com	\N	$2b$12$6BwedppVpOuQOOyTiahrze/90ryiseyPVeHCE87auS9HusCXLCax.	Farmer	User	t	f	\N	en	2026-02-05 21:25:33.119487+00	2026-02-05 21:25:33.119487+00	\N	\N	\N	\N
dcc8f7e0-c4a6-4f72-b21e-78331c825d3e	fsp_1770326899@test.com	\N	$2b$12$R7lMaUfVd0.ywdmTLL1e/OqUk5.sLCLY3LqymLZbOvRZQis9YVyZ.	FSP	User	t	f	\N	en	2026-02-05 21:28:19.2248+00	2026-02-05 21:28:19.2248+00	\N	\N	\N	\N
3f3a3a39-d867-45a8-b901-74a7e27c95f3	fsp1@gmail.com	+916666284187	$2b$12$B0snjjkKmIlPPY8mtTi.n.s2irXm3s3R4py1eY0MfxGKu.ExyZUnq	FSP	Admin	t	t	2026-02-11 09:30:26.380285+00	en	2026-01-30 00:08:37.606204+00	2026-02-11 09:30:26.062312+00	\N	\N	\N	\N
5847755d-a7ef-4f01-ad83-b96116cc5b06	farmer_1770326899@test.com	\N	$2b$12$JDwRKN2Rprs6MPTqNqFKoe4W/l/datvOVLtOg7Mv3NbfJtuGNIIzC	Farmer	User	t	f	\N	en	2026-02-05 21:28:19.606347+00	2026-02-05 21:28:19.606347+00	\N	\N	\N	\N
274bca62-6a26-40f4-ab29-482816286c94	fsp_1770327052@test.com	\N	$2b$12$tlYuKYdQwEl.277DLskD1eQ5b7sO8Cm49ATsaEAEEOgH35tBRWKgu	FSP	User	t	f	\N	en	2026-02-05 21:30:52.914405+00	2026-02-05 21:30:52.914405+00	\N	\N	\N	\N
3ca9cf6b-c372-4530-bc35-3440c68f858f	farmer_1770327052@test.com	\N	$2b$12$BYqDDsJVJo7PJ/1pfEAY5OGteRvGUV6zAPGAzwY2wziYwImLjsyfK	Farmer	User	t	f	\N	en	2026-02-05 21:30:53.170274+00	2026-02-05 21:30:53.170274+00	\N	\N	\N	\N
53126f3a-94da-4363-b20d-61a85c99574a	fsp_1770327102@test.com	\N	$2b$12$JEoUZBt.LZZSPgbhgR8LIuRU/lVsLRon2LESrWfLYykxq8OsmFvsq	FSP	User	t	f	\N	en	2026-02-05 21:31:42.051474+00	2026-02-05 21:31:42.051474+00	\N	\N	\N	\N
09b95fab-3a52-4e54-8957-76e81ebf668a	farmer_1770327102@test.com	\N	$2b$12$ohvSQX/5KN.yGcBj5F59FOxAyne/HJdz1vzXkv97wmAklZ7jytPVi	Farmer	User	t	f	\N	en	2026-02-05 21:31:42.246312+00	2026-02-05 21:31:42.246312+00	\N	\N	\N	\N
1214c599-c7c2-490b-a895-e45b985b027b	fsp_1770327224@test.com	\N	$2b$12$rsuRIQpNnG039YWmVpK4PONISdzXcsAgmk3NVxqSAx4izLfFtvDlq	FSP	User	t	f	\N	en	2026-02-05 21:33:44.413182+00	2026-02-05 21:33:44.413182+00	\N	\N	\N	\N
39219340-21cb-4a88-a939-93baf1a0e840	farmer_1770327224@test.com	\N	$2b$12$yhUFq71tdrk0HMEk3X46JukEk9mm12beZCcmBmXykqJcJSkx1FtVu	Farmer	User	t	f	\N	en	2026-02-05 21:33:44.622026+00	2026-02-05 21:33:44.622026+00	\N	\N	\N	\N
d9cd5b64-e423-4710-bcfe-73606bcca78c	fsp_1770327280@test.com	\N	$2b$12$Qoj6NXEqutQnCiyBMkwQqO2i.ZH4NRMkkFdoEdnCfk8r9NVA2j9f2	FSP	User	t	f	\N	en	2026-02-05 21:34:40.419838+00	2026-02-05 21:34:40.419838+00	\N	\N	\N	\N
5368cfba-bae0-4132-88e4-4fde67d9e523	farmer_1770327280@test.com	\N	$2b$12$l3DLV1HFBvPZY5czO1irPusaGbEwG2I3axWiTW7X4QRWtr/MgFWaK	Farmer	User	t	f	\N	en	2026-02-05 21:34:40.681024+00	2026-02-05 21:34:40.681024+00	\N	\N	\N	\N
4c68aa4c-c3bb-4f51-b947-59b1c98fdcdc	fsp_1770327392@test.com	\N	$2b$12$NuFFRqNMegg87ZcTABULK.ehMw5vaL.KvHIJ8ser3tEs4twGTNPo2	FSP	User	t	f	\N	en	2026-02-05 21:36:32.0808+00	2026-02-05 21:36:32.0808+00	\N	\N	\N	\N
222968c5-f7cd-46a9-80a7-ae6d0557b5c3	farmer_1770327392@test.com	\N	$2b$12$Rts8kv06C6yHKI3mU6JJLeVOMukHYMpNlYForYxofcG6wDuaRV7Ja	Farmer	User	t	f	\N	en	2026-02-05 21:36:32.268949+00	2026-02-05 21:36:32.268949+00	\N	\N	\N	\N
fc5165e6-6519-496f-a3dd-1435bc308b5f	fsp_1770327572@test.com	\N	$2b$12$41byl7HzADarAXVbezszvOl4zN8arZEvJfDqVCXf5skkqDuKLyyf6	FSP	User	t	f	\N	en	2026-02-05 21:39:32.657216+00	2026-02-05 21:39:32.657216+00	\N	\N	\N	\N
2b8bb712-3cfe-435e-84f7-49dfe73d641b	farmer_1770327572@test.com	\N	$2b$12$BuYBbpNShOnYFfi4LmIePOpD0SxJtg0ta5B/EYuh2fajAqMrt.rz6	Farmer	User	t	f	\N	en	2026-02-05 21:39:32.939032+00	2026-02-05 21:39:32.939032+00	\N	\N	\N	\N
d655e067-4edd-4516-b1b6-821c3c33cfc5	fsp_1770327636@test.com	\N	$2b$12$sgAQMs23nnoMu7MFJSMjD.ME45XvkfUSoe2spBJlziw1Qcx/OCgRe	FSP	User	t	f	\N	en	2026-02-05 21:40:36.712727+00	2026-02-05 21:40:36.712727+00	\N	\N	\N	\N
ee2e22fd-d69b-4b55-a51b-8cf1d7c22c9f	farmer_1770327636@test.com	\N	$2b$12$0ErFuqwwVUuU3CNvKWFy1uZM8MuzClQ40kTWT3LnuTGEOk1UcKJme	Farmer	User	t	f	\N	en	2026-02-05 21:40:36.970834+00	2026-02-05 21:40:36.970834+00	\N	\N	\N	\N
13ac055f-b943-4f6d-8182-babe636544df	fsp_1770327706@test.com	\N	$2b$12$qTRq.GS1nwpPMZb/NqVR8eNGyyA.q4pvOzbPrKkGc8YbqlrkfqYe2	FSP	User	t	f	\N	en	2026-02-05 21:41:46.51643+00	2026-02-05 21:41:46.51643+00	\N	\N	\N	\N
eb271702-3161-48b2-a4c9-8747819b7ae7	farmer_1770327706@test.com	\N	$2b$12$hJU6R9euHLeDSl82xJcUIOTDRAw39obOzsdxsuZZS9uQqCy3ZlQNC	Farmer	User	t	f	\N	en	2026-02-05 21:41:46.779275+00	2026-02-05 21:41:46.779275+00	\N	\N	\N	\N
5a96c5d0-7467-44d3-9f9b-614ce91f0bfc	fsp_1770327821@test.com	\N	$2b$12$3rfRcbUtEAIDaD6v0lAmPOepzYCS5URT4oZzDSIwRR/SzvnHbwsLO	FSP	User	t	f	\N	en	2026-02-05 21:43:41.93674+00	2026-02-05 21:43:41.93674+00	\N	\N	\N	\N
31148b05-1512-43ce-8b01-fd3b423fca6e	farmer_1770327821@test.com	\N	$2b$12$pd0pJlsuKI0ds99U9uLwleVHpAjRc36m.y3bc6SRMAzM8ZcNEafEu	Farmer	User	t	f	\N	en	2026-02-05 21:43:42.166002+00	2026-02-05 21:43:42.166002+00	\N	\N	\N	\N
ebc86578-b9a2-456f-b884-f964c1fb26f9	fsp_1770328194@test.com	\N	$2b$12$L1Z466WAeNWC2.9SlC24G.75HFoZUTACvs/MkzFlkO7WR2YJL2xJe	FSP	User	t	f	\N	en	2026-02-05 21:49:54.360749+00	2026-02-05 21:49:54.360749+00	\N	\N	\N	\N
3bffa9be-bbdb-4ddf-ad2b-8d8cd3460167	farmer_1770328194@test.com	\N	$2b$12$1s.sHWnnQYCCA0uPwu/GoOIi.JEekd.iErbWYv4q/y/yEimIBqUnC	Farmer	User	t	f	\N	en	2026-02-05 21:49:54.58254+00	2026-02-05 21:49:54.58254+00	\N	\N	\N	\N
7eddd813-1060-42a3-aa36-abc2c6529e0f	fsp_1770328337@test.com	\N	$2b$12$SkoEfs.2RiPk3LdaI1E2KOz5l9vZibhKc8YfXVlOTC6jIE8/WjIr.	FSP	User	t	f	\N	en	2026-02-05 21:52:17.891069+00	2026-02-05 21:52:17.891069+00	\N	\N	\N	\N
83e1d52b-a86b-461a-b995-e79e2ac57878	farmer_1770328337@test.com	\N	$2b$12$SrI.Tcv9KRkmTrEM4Ot5NeIl3L2203HAA/X9J9QWJA9nEax0J9dq.	Farmer	User	t	f	\N	en	2026-02-05 21:52:18.209834+00	2026-02-05 21:52:18.209834+00	\N	\N	\N	\N
021aea9d-7fe9-4488-ae61-eebf6d2af731	fsp_1770328517@test.com	\N	$2b$12$jWkgiqAhoAhAODHw6qoOXOdOVdcs5SSz3Sn8gkIZ8RWT3Sqmt4J4.	FSP	User	t	f	\N	en	2026-02-05 21:55:17.432754+00	2026-02-05 21:55:17.432754+00	\N	\N	\N	\N
\.


--
-- Data for Name: work_order_scope; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.work_order_scope (id, work_order_id, scope, scope_id, access_permissions, sort_order, created_at, created_by) FROM stdin;
1282f897-e17e-4838-be7e-47bd99698f29	b08d5b7e-0cd2-4525-8575-b04be01c8817	FARM	748bf7fa-ee25-49a9-b735-eb86c450e8ae	{"read": true, "track": false, "write": false}	0	2026-01-30 00:17:00.456848+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
1b2b81c9-a018-4b14-9863-673ab0b32c2e	b08d5b7e-0cd2-4525-8575-b04be01c8817	PLOT	4aa5abad-51da-4c92-b667-ab53a855d533	{"read": true, "track": false, "write": false}	0	2026-01-30 00:17:00.456848+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
0dfe22fb-fea9-4f78-8d97-470d89367124	b08d5b7e-0cd2-4525-8575-b04be01c8817	CROP	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	{"read": true, "track": false, "write": false}	0	2026-01-30 00:17:00.456848+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
41320932-eefc-46fa-9454-a3dfeb6cb02f	b08d5b7e-0cd2-4525-8575-b04be01c8817	CROP	22086444-0094-4b87-bb63-a24c03614344	{"read": true, "track": false, "write": false}	0	2026-01-30 00:17:00.456848+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
86e6d3f9-4179-4789-8e85-2aca17ebcdd2	6d820468-db09-4512-88cd-f4236e8ea04b	FARM	748bf7fa-ee25-49a9-b735-eb86c450e8ae	{"read": true, "track": false, "write": false}	0	2026-01-30 11:10:24.212116+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
c64bf4ca-0a4a-4c02-b61a-69d5341d91c2	6d820468-db09-4512-88cd-f4236e8ea04b	PLOT	4aa5abad-51da-4c92-b667-ab53a855d533	{"read": true, "track": false, "write": false}	0	2026-01-30 11:10:24.212116+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
6bca31a0-a842-4bae-b60f-1951581889df	6d820468-db09-4512-88cd-f4236e8ea04b	CROP	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	{"read": true, "track": false, "write": false}	0	2026-01-30 11:10:24.212116+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
2a0f6a2a-54a3-45d2-8653-df0223a6a2b7	6d820468-db09-4512-88cd-f4236e8ea04b	CROP	22086444-0094-4b87-bb63-a24c03614344	{"read": true, "track": false, "write": false}	0	2026-01-30 11:10:24.212116+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
26c86680-4af8-4b97-ac24-da37b5c71b8a	35d78a67-1a03-43d9-afd4-3bdae8cec61d	FARM	748bf7fa-ee25-49a9-b735-eb86c450e8ae	{"read": true, "track": false, "write": false}	0	2026-01-30 19:33:48.571062+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
6253a1ff-1e6d-418c-ac62-2114b17d690b	35d78a67-1a03-43d9-afd4-3bdae8cec61d	PLOT	5680d5e1-aea2-457a-864a-3db5386056dc	{"read": true, "track": false, "write": false}	0	2026-01-30 19:33:48.571062+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
efd6ecd7-f095-4bc5-9bf1-70175d43adb4	35d78a67-1a03-43d9-afd4-3bdae8cec61d	PLOT	4aa5abad-51da-4c92-b667-ab53a855d533	{"read": true, "track": false, "write": false}	0	2026-01-30 19:33:48.571062+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
94bad641-5d38-4030-a1e8-2113043140c2	35d78a67-1a03-43d9-afd4-3bdae8cec61d	CROP	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	{"read": true, "track": false, "write": false}	0	2026-01-30 19:33:48.571062+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
4cc95617-b159-4985-9038-19633c88568d	35d78a67-1a03-43d9-afd4-3bdae8cec61d	CROP	22086444-0094-4b87-bb63-a24c03614344	{"read": true, "track": false, "write": false}	0	2026-01-30 19:33:48.571062+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
7cadc11b-b195-4500-b1ee-068e4aa683d6	f58e5039-b46a-442c-9b84-314ac917fd9c	FARM	748bf7fa-ee25-49a9-b735-eb86c450e8ae	{"read": true, "track": false, "write": false}	0	2026-01-30 20:32:45.965145+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
e64c1ea5-7b59-4e1b-96e8-778572ba4def	f58e5039-b46a-442c-9b84-314ac917fd9c	PLOT	4aa5abad-51da-4c92-b667-ab53a855d533	{"read": true, "track": false, "write": false}	0	2026-01-30 20:32:45.965145+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
1909ca04-ff4c-4af5-8706-9166a93989f8	f58e5039-b46a-442c-9b84-314ac917fd9c	CROP	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	{"read": true, "track": false, "write": false}	0	2026-01-30 20:32:45.965145+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
1a378473-20d8-473a-9612-577a625b27c8	f58e5039-b46a-442c-9b84-314ac917fd9c	CROP	22086444-0094-4b87-bb63-a24c03614344	{"read": true, "track": false, "write": false}	0	2026-01-30 20:32:45.965145+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
a089de38-6fb3-4610-a149-23c9d09217d5	aa50f386-a701-4cc9-86a5-b1489ed3ffff	FARM	13b4a813-2a7e-4eea-9014-e79a65177f11	{"read": true, "track": true, "write": true}	0	2026-02-01 10:06:48.912563+00	a7c620dc-005f-41e4-a09c-84a578fdff32
4ca1f18a-4b03-4470-8b47-c91ac166dda8	ed8678d9-26e1-48a9-b97a-da8f8bb9f9b4	FARM	e61be074-9ef2-4cbb-8a7f-c472b58c20d8	{"read": true, "track": true, "write": true}	0	2026-02-01 10:10:07.595797+00	eb63636b-e512-4cd7-9296-f0d38d62f74d
a811ca46-35e6-4966-a9e1-bbecf5ab87cc	00e4ca22-0da3-4527-802d-a01663cd0090	FARM	fe011730-4986-4034-9815-f7650216b5a5	{"read": true, "track": true, "write": true}	0	2026-02-05 22:33:46.541314+00	723079fb-4d41-408d-958c-a1d417576d82
09c2b754-af33-4fd9-9a43-4965085cc2e8	eeb986d9-59ef-4158-9305-75d6993fe75e	FARM	748bf7fa-ee25-49a9-b735-eb86c450e8ae	{"read": true, "track": false, "write": false}	0	2026-02-06 11:12:54.452253+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
116c9eee-532b-4bcb-b3d1-3c4afd2b26a1	eeb986d9-59ef-4158-9305-75d6993fe75e	PLOT	4aa5abad-51da-4c92-b667-ab53a855d533	{"read": true, "track": false, "write": false}	0	2026-02-06 11:12:54.452253+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
3f9a6413-434d-4985-93cd-36c0a706e270	eeb986d9-59ef-4158-9305-75d6993fe75e	CROP	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	{"read": true, "track": false, "write": false}	0	2026-02-06 11:12:54.452253+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
58612c6a-49e7-408b-a876-504e2ab78c5e	eeb986d9-59ef-4158-9305-75d6993fe75e	CROP	22086444-0094-4b87-bb63-a24c03614344	{"read": true, "track": false, "write": false}	0	2026-02-06 11:12:54.452253+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
74e87361-d349-431a-9393-185221101231	75cabfc4-df2f-4812-967c-63a835a826d5	FARM	748bf7fa-ee25-49a9-b735-eb86c450e8ae	{"read": true, "track": false, "write": false}	0	2026-02-09 13:02:54.75844+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
850038ac-f780-4777-b556-ac47f48d74f5	75cabfc4-df2f-4812-967c-63a835a826d5	PLOT	4aa5abad-51da-4c92-b667-ab53a855d533	{"read": true, "track": false, "write": false}	0	2026-02-09 13:02:54.75844+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
24d7aa35-f773-4bfe-97cd-8e3fb35576ac	75cabfc4-df2f-4812-967c-63a835a826d5	CROP	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	{"read": true, "track": false, "write": false}	0	2026-02-09 13:02:54.75844+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
b306651a-f4eb-4447-ab1a-98e2f0e28712	75cabfc4-df2f-4812-967c-63a835a826d5	CROP	22086444-0094-4b87-bb63-a24c03614344	{"read": true, "track": false, "write": false}	0	2026-02-09 13:02:54.75844+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
512f53c0-f554-4bcc-a998-668bd2164f12	43b19d72-aa87-4c79-b241-81dcdb6d29af	FARM	748bf7fa-ee25-49a9-b735-eb86c450e8ae	{"read": true, "track": false, "write": false}	0	2026-02-09 16:26:04.255245+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
ccdf5e20-c030-4b73-9728-988073b2ad11	43b19d72-aa87-4c79-b241-81dcdb6d29af	PLOT	4aa5abad-51da-4c92-b667-ab53a855d533	{"read": true, "track": false, "write": false}	0	2026-02-09 16:26:04.255245+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
9d5bc74f-b9d8-4392-9641-5e5c7761d233	43b19d72-aa87-4c79-b241-81dcdb6d29af	CROP	4a2ab6e3-64a6-4ec4-a048-39fc0da9a392	{"read": true, "track": false, "write": false}	0	2026-02-09 16:26:04.255245+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
197358ca-4070-4aee-8dc4-fac8d92406f1	43b19d72-aa87-4c79-b241-81dcdb6d29af	CROP	22086444-0094-4b87-bb63-a24c03614344	{"read": true, "track": false, "write": false}	0	2026-02-09 16:26:04.255245+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3
\.


--
-- Data for Name: work_orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.work_orders (id, farming_organization_id, fsp_organization_id, service_listing_id, work_order_number, title, description, status, terms_and_conditions, scope_metadata, start_date, end_date, total_amount, currency, service_snapshot, created_at, updated_at, created_by, updated_by, accepted_at, accepted_by, completed_at, cancelled_at, assigned_to_user_id, access_granted, completion_notes, completion_photo_url) FROM stdin;
b08d5b7e-0cd2-4525-8575-b04be01c8817	5ae66809-e7de-448a-8f42-920a192c8704	8b411c61-9885-4672-ba08-e45709934575	3fca08f9-b0f2-4bcb-a2dc-6ba2483830fa	WO-2026-0001	Service Request	this is the audit i created now \n\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]	ACTIVE	Standard terms apply.	{"crops": 0, "farms": 0, "plots": 0, "total_items": 0, "organizations": 0}	2026-01-30	2026-05-22	1000.00	INR	{"name": "Service Request", "description": "this is the audit i created now \\n\\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]"}	2026-01-30 00:17:00.43525+00	2026-01-30 10:09:33.582108+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 00:17:34.930142+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	\N	\N	t	\N	\N
6d820468-db09-4512-88cd-f4236e8ea04b	5ae66809-e7de-448a-8f42-920a192c8704	8b411c61-9885-4672-ba08-e45709934575	55543d74-5711-48e2-8c7f-e518c295c578	WO-2026-0002	Service Request	asd\n\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]	ACTIVE	Standard terms apply.	{"crops": 0, "farms": 0, "plots": 0, "total_items": 0, "organizations": 0}	2026-01-30	2026-02-06	500.00	INR	{"name": "Service Request", "description": "asd\\n\\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]"}	2026-01-30 11:10:24.078307+00	2026-01-30 11:12:58.796822+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 11:12:30.293013+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	\N	\N	t	\N	\N
35d78a67-1a03-43d9-afd4-3bdae8cec61d	5ae66809-e7de-448a-8f42-920a192c8704	8b411c61-9885-4672-ba08-e45709934575	3fca08f9-b0f2-4bcb-a2dc-6ba2483830fa	WO-2026-0003	Service Request	cmvncvbnc\n\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]	ACTIVE	Standard terms apply.	{"crops": 0, "farms": 0, "plots": 0, "total_items": 0, "organizations": 0}	2026-01-30	2026-02-06	1000.00	INR	{"name": "Service Request", "description": "cmvncvbnc\\n\\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]"}	2026-01-30 19:33:48.524801+00	2026-01-30 19:35:12.602089+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 19:34:32.318704+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	\N	\N	t	\N	\N
f58e5039-b46a-442c-9b84-314ac917fd9c	5ae66809-e7de-448a-8f42-920a192c8704	8b411c61-9885-4672-ba08-e45709934575	55543d74-5711-48e2-8c7f-e518c295c578	WO-2026-0004	Service Request	dfghfghfgfgh\n\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]	COMPLETED	Standard terms apply.	{"crops": 0, "farms": 0, "plots": 0, "total_items": 0, "organizations": 0}	2026-01-30	2026-02-06	500.00	INR	{"name": "Service Request", "description": "dfghfghfgfgh\\n\\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]"}	2026-01-30 20:32:45.927841+00	2026-01-31 02:02:30.467041+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-30 20:33:13.030412+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-01-31 02:02:30.476277+00	\N	\N	t	\N	\N
aa50f386-a701-4cc9-86a5-b1489ed3ffff	9a08dd9e-37f1-466a-9cce-b38722c3c08d	74faf449-2f3a-4cdf-a1a6-6294eabc51b9	\N	WO-2026-0005	Debug Work Order 1769940408	Debug work order	ACTIVE	\N	{"crops": 0, "farms": 0, "plots": 0, "total_items": 0, "organizations": 0}	2026-02-01	2026-03-03	5000.00	INR	{"name": "Debug Work Order 1769940408", "description": "Debug work order"}	2026-02-01 10:06:48.886383+00	2026-02-01 10:06:48.958295+00	a7c620dc-005f-41e4-a09c-84a578fdff32	ea72b36b-fe10-483e-acca-7274bdab7600	2026-02-01 10:06:48.946348+00	ea72b36b-fe10-483e-acca-7274bdab7600	\N	\N	\N	t	\N	\N
ed8678d9-26e1-48a9-b97a-da8f8bb9f9b4	d21c407f-5ec7-4940-9863-903fc66fb45f	5986b068-6433-4eb3-907f-79e9e5ae4bd2	\N	WO-2026-0006	Quick WO 1769940607	Quick test	ACTIVE	\N	{"crops": 0, "farms": 0, "plots": 0, "total_items": 0, "organizations": 0}	2026-02-01	2026-03-03	5000.00	INR	{"name": "Quick WO 1769940607", "description": "Quick test"}	2026-02-01 10:10:07.581598+00	2026-02-01 10:10:07.634039+00	eb63636b-e512-4cd7-9296-f0d38d62f74d	fc777437-f8d9-4e04-bc0a-011507805218	2026-02-01 10:10:07.62281+00	fc777437-f8d9-4e04-bc0a-011507805218	\N	\N	\N	t	\N	\N
00e4ca22-0da3-4527-802d-a01663cd0090	a7bc280f-69bc-4b03-98d8-de195f8f95bf	e8718468-ad6e-4157-bbc8-3ad3a0047082	\N	WO-2026-0007	Test Audit Work Order 1770330826	Work order for audit testing	ACTIVE	\N	{"crops": 0, "farms": 0, "plots": 0, "total_items": 0, "organizations": 0}	2026-02-06	2026-03-08	10000.00	INR	{"name": "Test Audit Work Order 1770330826", "description": "Work order for audit testing"}	2026-02-05 22:33:46.518182+00	2026-02-05 22:33:46.591838+00	723079fb-4d41-408d-958c-a1d417576d82	b1dd0b01-8388-41bb-a686-f75f5aa559b9	2026-02-05 22:33:46.581583+00	b1dd0b01-8388-41bb-a686-f75f5aa559b9	\N	\N	\N	t	\N	\N
eeb986d9-59ef-4158-9305-75d6993fe75e	5ae66809-e7de-448a-8f42-920a192c8704	8b411c61-9885-4672-ba08-e45709934575	3fca08f9-b0f2-4bcb-a2dc-6ba2483830fa	WO-2026-0008	Service Request	Nothing \n\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]	ACTIVE	Standard terms apply.	{"crops": 0, "farms": 0, "plots": 0, "total_items": 0, "organizations": 0}	2026-02-06	2026-02-13	1000.00	INR	{"name": "Service Request", "description": "Nothing \\n\\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]"}	2026-02-06 11:12:54.429226+00	2026-02-06 11:14:05.547253+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-06 11:13:21.78201+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	\N	\N	t	\N	\N
75cabfc4-df2f-4812-967c-63a835a826d5	5ae66809-e7de-448a-8f42-920a192c8704	8b411c61-9885-4672-ba08-e45709934575	3fca08f9-b0f2-4bcb-a2dc-6ba2483830fa	WO-2026-0009	Service Request	uchto\n\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]	ACTIVE	Standard terms apply.	{"crops": 2, "farms": 1, "plots": 1, "total_items": 4, "organizations": 0}	2026-02-17	2026-04-17	1000.00	INR	{"name": "Service Request", "description": "uchto\\n\\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]"}	2026-02-09 13:02:54.738284+00	2026-02-09 13:04:21.225572+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-09 13:04:17.264047+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	\N	\N	t	\N	\N
43b19d72-aa87-4c79-b241-81dcdb6d29af	5ae66809-e7de-448a-8f42-920a192c8704	8b411c61-9885-4672-ba08-e45709934575	3fca08f9-b0f2-4bcb-a2dc-6ba2483830fa	WO-2026-0010	Service Request	\n\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]	ACTIVE	Standard terms apply.	{"crops": 2, "farms": 1, "plots": 1, "total_items": 4, "organizations": 0}	2026-02-09	2026-02-16	1000.00	INR	{"name": "Service Request", "description": "\\n\\n[Data Access Granted: The FSP is authorized to view historical data for these fields.]"}	2026-02-09 16:26:04.221656+00	2026-02-09 16:26:39.865257+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	3f3a3a39-d867-45a8-b901-74a7e27c95f3	2026-02-09 16:26:37.584368+00	3f3a3a39-d867-45a8-b901-74a7e27c95f3	\N	\N	\N	t	\N	\N
\.


--
-- Data for Name: geocode_settings; Type: TABLE DATA; Schema: tiger; Owner: postgres
--

COPY tiger.geocode_settings (name, setting, unit, category, short_desc) FROM stdin;
\.


--
-- Data for Name: pagc_gaz; Type: TABLE DATA; Schema: tiger; Owner: postgres
--

COPY tiger.pagc_gaz (id, seq, word, stdword, token, is_custom) FROM stdin;
\.


--
-- Data for Name: pagc_lex; Type: TABLE DATA; Schema: tiger; Owner: postgres
--

COPY tiger.pagc_lex (id, seq, word, stdword, token, is_custom) FROM stdin;
\.


--
-- Data for Name: pagc_rules; Type: TABLE DATA; Schema: tiger; Owner: postgres
--

COPY tiger.pagc_rules (id, rule, is_custom) FROM stdin;
\.


--
-- Data for Name: topology; Type: TABLE DATA; Schema: topology; Owner: postgres
--

COPY topology.topology (id, name, srid, "precision", hasz) FROM stdin;
\.


--
-- Data for Name: layer; Type: TABLE DATA; Schema: topology; Owner: postgres
--

COPY topology.layer (topology_id, layer_id, schema_name, table_name, feature_column, feature_type, level, child_id) FROM stdin;
\.


--
-- Name: topology_id_seq; Type: SEQUENCE SET; Schema: topology; Owner: postgres
--

SELECT pg_catalog.setval('topology.topology_id_seq', 1, false);


--
-- Name: audit_issues audit_issues_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_issues
    ADD CONSTRAINT audit_issues_pkey PRIMARY KEY (id);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: audit_parameter_instances audit_parameter_instances_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_parameter_instances
    ADD CONSTRAINT audit_parameter_instances_pkey PRIMARY KEY (id);


--
-- Name: audit_recommendations audit_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_recommendations
    ADD CONSTRAINT audit_recommendations_pkey PRIMARY KEY (id);


--
-- Name: audit_reports audit_reports_audit_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_reports
    ADD CONSTRAINT audit_reports_audit_id_key UNIQUE (audit_id);


--
-- Name: audit_reports audit_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_reports
    ADD CONSTRAINT audit_reports_pkey PRIMARY KEY (id);


--
-- Name: audit_response_photos audit_response_photos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_response_photos
    ADD CONSTRAINT audit_response_photos_pkey PRIMARY KEY (id);


--
-- Name: audit_responses audit_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_responses
    ADD CONSTRAINT audit_responses_pkey PRIMARY KEY (id);


--
-- Name: audit_review_photos audit_review_photos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_review_photos
    ADD CONSTRAINT audit_review_photos_pkey PRIMARY KEY (id);


--
-- Name: audit_reviews audit_reviews_audit_response_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_reviews
    ADD CONSTRAINT audit_reviews_audit_response_id_key UNIQUE (audit_response_id);


--
-- Name: audit_reviews audit_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_reviews
    ADD CONSTRAINT audit_reviews_pkey PRIMARY KEY (id);


--
-- Name: audits audits_audit_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT audits_audit_number_key UNIQUE (audit_number);


--
-- Name: audits audits_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT audits_pkey PRIMARY KEY (id);


--
-- Name: chat_channel_members chat_channel_members_channel_id_organization_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_channel_members
    ADD CONSTRAINT chat_channel_members_channel_id_organization_id_key UNIQUE (channel_id, organization_id);


--
-- Name: chat_channel_members chat_channel_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_channel_members
    ADD CONSTRAINT chat_channel_members_pkey PRIMARY KEY (id);


--
-- Name: chat_channels chat_channels_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_channels
    ADD CONSTRAINT chat_channels_pkey PRIMARY KEY (id);


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- Name: crop_categories crop_categories_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_categories
    ADD CONSTRAINT crop_categories_code_key UNIQUE (code);


--
-- Name: crop_categories crop_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_categories
    ADD CONSTRAINT crop_categories_pkey PRIMARY KEY (id);


--
-- Name: crop_category_translations crop_category_translations_crop_category_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_category_translations
    ADD CONSTRAINT crop_category_translations_crop_category_id_language_code_key UNIQUE (crop_category_id, language_code);


--
-- Name: crop_category_translations crop_category_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_category_translations
    ADD CONSTRAINT crop_category_translations_pkey PRIMARY KEY (id);


--
-- Name: crop_lifecycle_photos crop_lifecycle_photos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_lifecycle_photos
    ADD CONSTRAINT crop_lifecycle_photos_pkey PRIMARY KEY (id);


--
-- Name: crop_type_translations crop_type_translations_crop_type_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_type_translations
    ADD CONSTRAINT crop_type_translations_crop_type_id_language_code_key UNIQUE (crop_type_id, language_code);


--
-- Name: crop_type_translations crop_type_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_type_translations
    ADD CONSTRAINT crop_type_translations_pkey PRIMARY KEY (id);


--
-- Name: crop_types crop_types_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_types
    ADD CONSTRAINT crop_types_code_key UNIQUE (code);


--
-- Name: crop_types crop_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_types
    ADD CONSTRAINT crop_types_pkey PRIMARY KEY (id);


--
-- Name: crop_varieties crop_varieties_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_varieties
    ADD CONSTRAINT crop_varieties_code_key UNIQUE (code);


--
-- Name: crop_varieties crop_varieties_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_varieties
    ADD CONSTRAINT crop_varieties_pkey PRIMARY KEY (id);


--
-- Name: crop_variety_translations crop_variety_translations_crop_variety_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_variety_translations
    ADD CONSTRAINT crop_variety_translations_crop_variety_id_language_code_key UNIQUE (crop_variety_id, language_code);


--
-- Name: crop_variety_translations crop_variety_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_variety_translations
    ADD CONSTRAINT crop_variety_translations_pkey PRIMARY KEY (id);


--
-- Name: crop_yield_photos crop_yield_photos_crop_yield_id_photo_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_yield_photos
    ADD CONSTRAINT crop_yield_photos_crop_yield_id_photo_id_key UNIQUE (crop_yield_id, photo_id);


--
-- Name: crop_yield_photos crop_yield_photos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_yield_photos
    ADD CONSTRAINT crop_yield_photos_pkey PRIMARY KEY (id);


--
-- Name: crop_yields crop_yields_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_yields
    ADD CONSTRAINT crop_yields_pkey PRIMARY KEY (id);


--
-- Name: crops crops_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crops
    ADD CONSTRAINT crops_pkey PRIMARY KEY (id);


--
-- Name: farm_irrigation_modes farm_irrigation_modes_farm_id_irrigation_mode_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_irrigation_modes
    ADD CONSTRAINT farm_irrigation_modes_farm_id_irrigation_mode_id_key UNIQUE (farm_id, irrigation_mode_id);


--
-- Name: farm_irrigation_modes farm_irrigation_modes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_irrigation_modes
    ADD CONSTRAINT farm_irrigation_modes_pkey PRIMARY KEY (id);


--
-- Name: farm_soil_types farm_soil_types_farm_id_soil_type_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_soil_types
    ADD CONSTRAINT farm_soil_types_farm_id_soil_type_id_key UNIQUE (farm_id, soil_type_id);


--
-- Name: farm_soil_types farm_soil_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_soil_types
    ADD CONSTRAINT farm_soil_types_pkey PRIMARY KEY (id);


--
-- Name: farm_supervisors farm_supervisors_farm_id_supervisor_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_supervisors
    ADD CONSTRAINT farm_supervisors_farm_id_supervisor_id_key UNIQUE (farm_id, supervisor_id);


--
-- Name: farm_supervisors farm_supervisors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_supervisors
    ADD CONSTRAINT farm_supervisors_pkey PRIMARY KEY (id);


--
-- Name: farm_water_sources farm_water_sources_farm_id_water_source_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_water_sources
    ADD CONSTRAINT farm_water_sources_farm_id_water_source_id_key UNIQUE (farm_id, water_source_id);


--
-- Name: farm_water_sources farm_water_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_water_sources
    ADD CONSTRAINT farm_water_sources_pkey PRIMARY KEY (id);


--
-- Name: farms farms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farms
    ADD CONSTRAINT farms_pkey PRIMARY KEY (id);


--
-- Name: finance_categories finance_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_categories
    ADD CONSTRAINT finance_categories_pkey PRIMARY KEY (id);


--
-- Name: finance_categories finance_categories_transaction_type_code_is_system_defined__key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_categories
    ADD CONSTRAINT finance_categories_transaction_type_code_is_system_defined__key UNIQUE (transaction_type, code, is_system_defined, owner_org_id);


--
-- Name: finance_category_translations finance_category_translations_category_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_category_translations
    ADD CONSTRAINT finance_category_translations_category_id_language_code_key UNIQUE (category_id, language_code);


--
-- Name: finance_category_translations finance_category_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_category_translations
    ADD CONSTRAINT finance_category_translations_pkey PRIMARY KEY (id);


--
-- Name: finance_transaction_attachments finance_transaction_attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transaction_attachments
    ADD CONSTRAINT finance_transaction_attachments_pkey PRIMARY KEY (id);


--
-- Name: finance_transaction_splits finance_transaction_splits_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transaction_splits
    ADD CONSTRAINT finance_transaction_splits_pkey PRIMARY KEY (id);


--
-- Name: finance_transactions finance_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transactions
    ADD CONSTRAINT finance_transactions_pkey PRIMARY KEY (id);


--
-- Name: fsp_approval_documents fsp_approval_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fsp_approval_documents
    ADD CONSTRAINT fsp_approval_documents_pkey PRIMARY KEY (id);


--
-- Name: fsp_service_listings fsp_service_listings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fsp_service_listings
    ADD CONSTRAINT fsp_service_listings_pkey PRIMARY KEY (id);


--
-- Name: input_item_categories input_item_categories_code_is_system_defined_owner_org_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_item_categories
    ADD CONSTRAINT input_item_categories_code_is_system_defined_owner_org_id_key UNIQUE (code, is_system_defined, owner_org_id);


--
-- Name: input_item_categories input_item_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_item_categories
    ADD CONSTRAINT input_item_categories_pkey PRIMARY KEY (id);


--
-- Name: input_item_category_translations input_item_category_translations_category_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_item_category_translations
    ADD CONSTRAINT input_item_category_translations_category_id_language_code_key UNIQUE (category_id, language_code);


--
-- Name: input_item_category_translations input_item_category_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_item_category_translations
    ADD CONSTRAINT input_item_category_translations_pkey PRIMARY KEY (id);


--
-- Name: input_item_translations input_item_translations_input_item_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_item_translations
    ADD CONSTRAINT input_item_translations_input_item_id_language_code_key UNIQUE (input_item_id, language_code);


--
-- Name: input_item_translations input_item_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_item_translations
    ADD CONSTRAINT input_item_translations_pkey PRIMARY KEY (id);


--
-- Name: input_items input_items_category_id_code_is_system_defined_owner_org_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_items
    ADD CONSTRAINT input_items_category_id_code_is_system_defined_owner_org_id_key UNIQUE (category_id, code, is_system_defined, owner_org_id);


--
-- Name: input_items input_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_items
    ADD CONSTRAINT input_items_pkey PRIMARY KEY (id);


--
-- Name: master_service_translations master_service_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.master_service_translations
    ADD CONSTRAINT master_service_translations_pkey PRIMARY KEY (id);


--
-- Name: master_service_translations master_service_translations_service_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.master_service_translations
    ADD CONSTRAINT master_service_translations_service_id_language_code_key UNIQUE (service_id, language_code);


--
-- Name: master_services master_services_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.master_services
    ADD CONSTRAINT master_services_code_key UNIQUE (code);


--
-- Name: master_services master_services_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.master_services
    ADD CONSTRAINT master_services_pkey PRIMARY KEY (id);


--
-- Name: measurement_unit_translations measurement_unit_translations_measurement_unit_id_language__key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurement_unit_translations
    ADD CONSTRAINT measurement_unit_translations_measurement_unit_id_language__key UNIQUE (measurement_unit_id, language_code);


--
-- Name: measurement_unit_translations measurement_unit_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurement_unit_translations
    ADD CONSTRAINT measurement_unit_translations_pkey PRIMARY KEY (id);


--
-- Name: measurement_units measurement_units_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurement_units
    ADD CONSTRAINT measurement_units_code_key UNIQUE (code);


--
-- Name: measurement_units measurement_units_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurement_units
    ADD CONSTRAINT measurement_units_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: option_sets option_sets_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.option_sets
    ADD CONSTRAINT option_sets_code_key UNIQUE (code);


--
-- Name: option_sets option_sets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.option_sets
    ADD CONSTRAINT option_sets_pkey PRIMARY KEY (id);


--
-- Name: option_translations option_translations_option_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.option_translations
    ADD CONSTRAINT option_translations_option_id_language_code_key UNIQUE (option_id, language_code);


--
-- Name: option_translations option_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.option_translations
    ADD CONSTRAINT option_translations_pkey PRIMARY KEY (id);


--
-- Name: options options_option_set_id_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.options
    ADD CONSTRAINT options_option_set_id_code_key UNIQUE (option_set_id, code);


--
-- Name: options options_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.options
    ADD CONSTRAINT options_pkey PRIMARY KEY (id);


--
-- Name: org_member_invitations org_member_invitations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_member_invitations
    ADD CONSTRAINT org_member_invitations_pkey PRIMARY KEY (id);


--
-- Name: org_member_roles org_member_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_member_roles
    ADD CONSTRAINT org_member_roles_pkey PRIMARY KEY (id);


--
-- Name: org_member_roles org_member_roles_user_id_organization_id_role_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_member_roles
    ADD CONSTRAINT org_member_roles_user_id_organization_id_role_id_key UNIQUE (user_id, organization_id, role_id);


--
-- Name: org_members org_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_members
    ADD CONSTRAINT org_members_pkey PRIMARY KEY (id);


--
-- Name: org_members org_members_user_id_organization_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_members
    ADD CONSTRAINT org_members_user_id_organization_id_key UNIQUE (user_id, organization_id);


--
-- Name: org_role_permission_overrides org_role_permission_overrides_organization_id_role_id_permi_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_role_permission_overrides
    ADD CONSTRAINT org_role_permission_overrides_organization_id_role_id_permi_key UNIQUE (organization_id, role_id, permission_id);


--
-- Name: org_role_permission_overrides org_role_permission_overrides_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_role_permission_overrides
    ADD CONSTRAINT org_role_permission_overrides_pkey PRIMARY KEY (id);


--
-- Name: org_subscription_history org_subscription_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_subscription_history
    ADD CONSTRAINT org_subscription_history_pkey PRIMARY KEY (id);


--
-- Name: organizations organizations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);


--
-- Name: parameter_option_set_map parameter_option_set_map_parameter_id_option_set_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parameter_option_set_map
    ADD CONSTRAINT parameter_option_set_map_parameter_id_option_set_id_key UNIQUE (parameter_id, option_set_id);


--
-- Name: parameter_option_set_map parameter_option_set_map_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parameter_option_set_map
    ADD CONSTRAINT parameter_option_set_map_pkey PRIMARY KEY (id);


--
-- Name: parameter_translations parameter_translations_parameter_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parameter_translations
    ADD CONSTRAINT parameter_translations_parameter_id_language_code_key UNIQUE (parameter_id, language_code);


--
-- Name: parameter_translations parameter_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parameter_translations
    ADD CONSTRAINT parameter_translations_pkey PRIMARY KEY (id);


--
-- Name: parameters parameters_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parameters
    ADD CONSTRAINT parameters_code_key UNIQUE (code);


--
-- Name: parameters parameters_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parameters
    ADD CONSTRAINT parameters_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_code_key UNIQUE (code);


--
-- Name: permissions permissions_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_name_key UNIQUE (name);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: plot_irrigation_modes plot_irrigation_modes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plot_irrigation_modes
    ADD CONSTRAINT plot_irrigation_modes_pkey PRIMARY KEY (id);


--
-- Name: plot_irrigation_modes plot_irrigation_modes_plot_id_irrigation_mode_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plot_irrigation_modes
    ADD CONSTRAINT plot_irrigation_modes_plot_id_irrigation_mode_id_key UNIQUE (plot_id, irrigation_mode_id);


--
-- Name: plot_soil_types plot_soil_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plot_soil_types
    ADD CONSTRAINT plot_soil_types_pkey PRIMARY KEY (id);


--
-- Name: plot_soil_types plot_soil_types_plot_id_soil_type_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plot_soil_types
    ADD CONSTRAINT plot_soil_types_plot_id_soil_type_id_key UNIQUE (plot_id, soil_type_id);


--
-- Name: plot_water_sources plot_water_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plot_water_sources
    ADD CONSTRAINT plot_water_sources_pkey PRIMARY KEY (id);


--
-- Name: plot_water_sources plot_water_sources_plot_id_water_source_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plot_water_sources
    ADD CONSTRAINT plot_water_sources_plot_id_water_source_id_key UNIQUE (plot_id, water_source_id);


--
-- Name: plots plots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plots
    ADD CONSTRAINT plots_pkey PRIMARY KEY (id);


--
-- Name: push_notification_tokens push_notification_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.push_notification_tokens
    ADD CONSTRAINT push_notification_tokens_pkey PRIMARY KEY (id);


--
-- Name: push_notification_tokens push_notification_tokens_user_id_device_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.push_notification_tokens
    ADD CONSTRAINT push_notification_tokens_user_id_device_token_key UNIQUE (user_id, device_token);


--
-- Name: queries queries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_pkey PRIMARY KEY (id);


--
-- Name: queries queries_query_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_query_number_key UNIQUE (query_number);


--
-- Name: query_photos query_photos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.query_photos
    ADD CONSTRAINT query_photos_pkey PRIMARY KEY (id);


--
-- Name: query_responses query_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.query_responses
    ADD CONSTRAINT query_responses_pkey PRIMARY KEY (id);


--
-- Name: reference_data reference_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reference_data
    ADD CONSTRAINT reference_data_pkey PRIMARY KEY (id);


--
-- Name: reference_data_translations reference_data_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reference_data_translations
    ADD CONSTRAINT reference_data_translations_pkey PRIMARY KEY (id);


--
-- Name: reference_data_translations reference_data_translations_reference_data_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reference_data_translations
    ADD CONSTRAINT reference_data_translations_reference_data_id_language_code_key UNIQUE (reference_data_id, language_code);


--
-- Name: reference_data reference_data_type_id_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reference_data
    ADD CONSTRAINT reference_data_type_id_code_key UNIQUE (type_id, code);


--
-- Name: reference_data_types reference_data_types_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reference_data_types
    ADD CONSTRAINT reference_data_types_code_key UNIQUE (code);


--
-- Name: reference_data_types reference_data_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reference_data_types
    ADD CONSTRAINT reference_data_types_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (id);


--
-- Name: role_permissions role_permissions_role_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_permission_id_key UNIQUE (role_id, permission_id);


--
-- Name: roles roles_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_code_key UNIQUE (code);


--
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: schedule_change_log schedule_change_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_change_log
    ADD CONSTRAINT schedule_change_log_pkey PRIMARY KEY (id);


--
-- Name: schedule_tasks schedule_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_tasks
    ADD CONSTRAINT schedule_tasks_pkey PRIMARY KEY (id);


--
-- Name: schedule_template_tasks schedule_template_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_template_tasks
    ADD CONSTRAINT schedule_template_tasks_pkey PRIMARY KEY (id);


--
-- Name: schedule_template_translations schedule_template_translation_schedule_template_id_language_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_template_translations
    ADD CONSTRAINT schedule_template_translation_schedule_template_id_language_key UNIQUE (schedule_template_id, language_code);


--
-- Name: schedule_template_translations schedule_template_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_template_translations
    ADD CONSTRAINT schedule_template_translations_pkey PRIMARY KEY (id);


--
-- Name: schedule_templates schedule_templates_code_is_system_defined_owner_org_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_templates
    ADD CONSTRAINT schedule_templates_code_is_system_defined_owner_org_id_key UNIQUE (code, is_system_defined, owner_org_id);


--
-- Name: schedule_templates schedule_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_templates
    ADD CONSTRAINT schedule_templates_pkey PRIMARY KEY (id);


--
-- Name: schedules schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_pkey PRIMARY KEY (id);


--
-- Name: section_translations section_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_translations
    ADD CONSTRAINT section_translations_pkey PRIMARY KEY (id);


--
-- Name: section_translations section_translations_section_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_translations
    ADD CONSTRAINT section_translations_section_id_language_code_key UNIQUE (section_id, language_code);


--
-- Name: sections sections_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_code_key UNIQUE (code);


--
-- Name: sections sections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_pkey PRIMARY KEY (id);


--
-- Name: subscription_plan_history subscription_plan_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscription_plan_history
    ADD CONSTRAINT subscription_plan_history_pkey PRIMARY KEY (id);


--
-- Name: subscription_plan_history subscription_plan_history_plan_id_version_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscription_plan_history
    ADD CONSTRAINT subscription_plan_history_plan_id_version_key UNIQUE (plan_id, version);


--
-- Name: subscription_plans subscription_plans_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscription_plans
    ADD CONSTRAINT subscription_plans_name_key UNIQUE (name);


--
-- Name: subscription_plans subscription_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscription_plans
    ADD CONSTRAINT subscription_plans_pkey PRIMARY KEY (id);


--
-- Name: task_actuals task_actuals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_actuals
    ADD CONSTRAINT task_actuals_pkey PRIMARY KEY (id);


--
-- Name: task_photos task_photos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_photos
    ADD CONSTRAINT task_photos_pkey PRIMARY KEY (id);


--
-- Name: task_translations task_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_translations
    ADD CONSTRAINT task_translations_pkey PRIMARY KEY (id);


--
-- Name: task_translations task_translations_task_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_translations
    ADD CONSTRAINT task_translations_task_id_language_code_key UNIQUE (task_id, language_code);


--
-- Name: tasks tasks_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_code_key UNIQUE (code);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: template_parameters template_parameters_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.template_parameters
    ADD CONSTRAINT template_parameters_pkey PRIMARY KEY (id);


--
-- Name: template_sections template_sections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.template_sections
    ADD CONSTRAINT template_sections_pkey PRIMARY KEY (id);


--
-- Name: template_translations template_translations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.template_translations
    ADD CONSTRAINT template_translations_pkey PRIMARY KEY (id);


--
-- Name: template_translations template_translations_template_id_language_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.template_translations
    ADD CONSTRAINT template_translations_template_id_language_code_key UNIQUE (template_id, language_code);


--
-- Name: templates templates_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.templates
    ADD CONSTRAINT templates_code_key UNIQUE (code);


--
-- Name: templates templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.templates
    ADD CONSTRAINT templates_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: work_order_scope work_order_scope_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_order_scope
    ADD CONSTRAINT work_order_scope_pkey PRIMARY KEY (id);


--
-- Name: work_order_scope work_order_scope_work_order_id_scope_scope_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_order_scope
    ADD CONSTRAINT work_order_scope_work_order_id_scope_scope_id_key UNIQUE (work_order_id, scope, scope_id);


--
-- Name: work_orders work_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_orders
    ADD CONSTRAINT work_orders_pkey PRIMARY KEY (id);


--
-- Name: work_orders work_orders_work_order_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_orders
    ADD CONSTRAINT work_orders_work_order_number_key UNIQUE (work_order_number);


--
-- Name: idx_audit_issues_audit; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_issues_audit ON public.audit_issues USING btree (audit_id);


--
-- Name: idx_audit_issues_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_issues_created_at ON public.audit_issues USING btree (created_at);


--
-- Name: idx_audit_issues_severity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_issues_severity ON public.audit_issues USING btree (severity);


--
-- Name: idx_audit_log_changed_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_changed_at ON public.audit_log USING btree (changed_at);


--
-- Name: idx_audit_log_record; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_record ON public.audit_log USING btree (record_id);


--
-- Name: idx_audit_log_table; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_log_table ON public.audit_log USING btree (table_name);


--
-- Name: idx_audit_param_instances_audit; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_param_instances_audit ON public.audit_parameter_instances USING btree (audit_id);


--
-- Name: idx_audit_param_instances_param; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_param_instances_param ON public.audit_parameter_instances USING btree (parameter_id);


--
-- Name: idx_audit_param_instances_section; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_param_instances_section ON public.audit_parameter_instances USING btree (template_section_id);


--
-- Name: idx_audit_reports_audit_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_reports_audit_id ON public.audit_reports USING btree (audit_id);


--
-- Name: idx_audit_response_photos_audit; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_response_photos_audit ON public.audit_response_photos USING btree (audit_id);


--
-- Name: idx_audit_response_photos_response; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_response_photos_response ON public.audit_response_photos USING btree (audit_response_id);


--
-- Name: idx_audit_responses_audit; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_responses_audit ON public.audit_responses USING btree (audit_id);


--
-- Name: idx_audit_responses_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_responses_created_at ON public.audit_responses USING btree (created_at);


--
-- Name: idx_audit_responses_created_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_responses_created_by ON public.audit_responses USING btree (created_by);


--
-- Name: idx_audit_responses_param_instance; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_responses_param_instance ON public.audit_responses USING btree (audit_parameter_instance_id);


--
-- Name: idx_audit_review_photos_photo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_review_photos_photo ON public.audit_review_photos USING btree (audit_response_photo_id);


--
-- Name: idx_audit_review_photos_reviewer; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_review_photos_reviewer ON public.audit_review_photos USING btree (reviewed_by);


--
-- Name: idx_audit_reviews_flagged; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_reviews_flagged ON public.audit_reviews USING btree (is_flagged_for_report) WHERE (is_flagged_for_report = true);


--
-- Name: idx_audit_reviews_response; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_reviews_response ON public.audit_reviews USING btree (audit_response_id);


--
-- Name: idx_audit_reviews_reviewed_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_reviews_reviewed_at ON public.audit_reviews USING btree (reviewed_at);


--
-- Name: idx_audit_reviews_reviewer; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_reviews_reviewer ON public.audit_reviews USING btree (reviewed_by);


--
-- Name: idx_audits_analyst; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_analyst ON public.audits USING btree (analyst_user_id);


--
-- Name: idx_audits_assigned_to; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_assigned_to ON public.audits USING btree (assigned_to_user_id);


--
-- Name: idx_audits_crop; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_crop ON public.audits USING btree (crop_id);


--
-- Name: idx_audits_crop_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_crop_status ON public.audits USING btree (crop_id, status);


--
-- Name: idx_audits_farming_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_farming_org ON public.audits USING btree (farming_organization_id);


--
-- Name: idx_audits_farming_org_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_farming_org_status ON public.audits USING btree (farming_organization_id, status);


--
-- Name: idx_audits_finalized_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_finalized_at ON public.audits USING btree (finalized_at) WHERE (finalized_at IS NOT NULL);


--
-- Name: idx_audits_fsp_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_fsp_org ON public.audits USING btree (fsp_organization_id);


--
-- Name: idx_audits_fsp_org_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_fsp_org_status ON public.audits USING btree (fsp_organization_id, status);


--
-- Name: idx_audits_shared_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_shared_at ON public.audits USING btree (shared_at) WHERE (shared_at IS NOT NULL);


--
-- Name: idx_audits_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_status ON public.audits USING btree (status);


--
-- Name: idx_audits_sync_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_sync_status ON public.audits USING btree (sync_status);


--
-- Name: idx_audits_template; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_template ON public.audits USING btree (template_id);


--
-- Name: idx_audits_work_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audits_work_order ON public.audits USING btree (work_order_id);


--
-- Name: idx_chat_channels_context; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_chat_channels_context ON public.chat_channels USING btree (context_type, context_id);


--
-- Name: idx_chat_members_channel; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_chat_members_channel ON public.chat_channel_members USING btree (channel_id);


--
-- Name: idx_chat_members_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_chat_members_org ON public.chat_channel_members USING btree (organization_id);


--
-- Name: idx_chat_messages_channel_dt; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_chat_messages_channel_dt ON public.chat_messages USING btree (channel_id, created_at DESC);


--
-- Name: idx_crop_lifecycle_photos_crop; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_crop_lifecycle_photos_crop ON public.crop_lifecycle_photos USING btree (crop_id);


--
-- Name: idx_crop_lifecycle_photos_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_crop_lifecycle_photos_date ON public.crop_lifecycle_photos USING btree (photo_date);


--
-- Name: idx_crop_yield_photos_photo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_crop_yield_photos_photo ON public.crop_yield_photos USING btree (photo_id);


--
-- Name: idx_crop_yield_photos_yield; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_crop_yield_photos_yield ON public.crop_yield_photos USING btree (crop_yield_id);


--
-- Name: idx_crop_yields_crop; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_crop_yields_crop ON public.crop_yields USING btree (crop_id);


--
-- Name: idx_crops_lifecycle; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_crops_lifecycle ON public.crops USING btree (lifecycle);


--
-- Name: idx_crops_name_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_crops_name_trgm ON public.crops USING gin (name public.gin_trgm_ops);


--
-- Name: idx_crops_plot; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_crops_plot ON public.crops USING btree (plot_id);


--
-- Name: idx_crops_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_crops_type ON public.crops USING btree (crop_type_id);


--
-- Name: idx_farm_supervisors_farm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_farm_supervisors_farm ON public.farm_supervisors USING btree (farm_id);


--
-- Name: idx_farm_supervisors_supervisor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_farm_supervisors_supervisor ON public.farm_supervisors USING btree (supervisor_id);


--
-- Name: idx_farms_attributes; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_farms_attributes ON public.farms USING gin (farm_attributes);


--
-- Name: idx_farms_boundary; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_farms_boundary ON public.farms USING gist (boundary);


--
-- Name: idx_farms_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_farms_location ON public.farms USING gist (location);


--
-- Name: idx_farms_manager; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_farms_manager ON public.farms USING btree (manager_id);


--
-- Name: idx_farms_name_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_farms_name_trgm ON public.farms USING gin (name public.gin_trgm_ops);


--
-- Name: idx_farms_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_farms_org ON public.farms USING btree (organization_id);


--
-- Name: idx_finance_attachments_trans; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_attachments_trans ON public.finance_transaction_attachments USING btree (transaction_id);


--
-- Name: idx_finance_categories_owner; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_categories_owner ON public.finance_categories USING btree (owner_org_id);


--
-- Name: idx_finance_categories_system; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_categories_system ON public.finance_categories USING btree (is_system_defined);


--
-- Name: idx_finance_categories_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_categories_type ON public.finance_categories USING btree (transaction_type);


--
-- Name: idx_finance_category_translations_lang; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_category_translations_lang ON public.finance_category_translations USING btree (language_code);


--
-- Name: idx_finance_splits_crop; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_splits_crop ON public.finance_transaction_splits USING btree (crop_id);


--
-- Name: idx_finance_splits_farm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_splits_farm ON public.finance_transaction_splits USING btree (farm_id);


--
-- Name: idx_finance_splits_plot; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_splits_plot ON public.finance_transaction_splits USING btree (plot_id);


--
-- Name: idx_finance_splits_trans; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_splits_trans ON public.finance_transaction_splits USING btree (transaction_id);


--
-- Name: idx_finance_trans_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_trans_category ON public.finance_transactions USING btree (category_id);


--
-- Name: idx_finance_trans_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_trans_date ON public.finance_transactions USING btree (transaction_date);


--
-- Name: idx_finance_trans_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_trans_org ON public.finance_transactions USING btree (organization_id);


--
-- Name: idx_finance_trans_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_finance_trans_type ON public.finance_transactions USING btree (transaction_type);


--
-- Name: idx_fsp_docs_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fsp_docs_org ON public.fsp_approval_documents USING btree (fsp_organization_id);


--
-- Name: idx_fsp_listings_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fsp_listings_org ON public.fsp_service_listings USING btree (fsp_organization_id);


--
-- Name: idx_fsp_listings_service; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fsp_listings_service ON public.fsp_service_listings USING btree (service_id);


--
-- Name: idx_fsp_listings_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fsp_listings_status ON public.fsp_service_listings USING btree (status);


--
-- Name: idx_input_item_categories_owner; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_input_item_categories_owner ON public.input_item_categories USING btree (owner_org_id);


--
-- Name: idx_input_item_categories_system; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_input_item_categories_system ON public.input_item_categories USING btree (is_system_defined);


--
-- Name: idx_input_item_categories_system_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_input_item_categories_system_code ON public.input_item_categories USING btree (code, is_system_defined) WHERE (is_system_defined = true);


--
-- Name: idx_input_item_category_translations_lang; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_input_item_category_translations_lang ON public.input_item_category_translations USING btree (language_code);


--
-- Name: idx_input_item_translations_lang; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_input_item_translations_lang ON public.input_item_translations USING btree (language_code);


--
-- Name: idx_input_items_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_input_items_category ON public.input_items USING btree (category_id);


--
-- Name: idx_input_items_owner; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_input_items_owner ON public.input_items USING btree (owner_org_id);


--
-- Name: idx_input_items_system; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_input_items_system ON public.input_items USING btree (is_system_defined);


--
-- Name: idx_input_items_system_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_input_items_system_code ON public.input_items USING btree (code, is_system_defined) WHERE (is_system_defined = true);


--
-- Name: idx_measurement_unit_translations_lang; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_measurement_unit_translations_lang ON public.measurement_unit_translations USING btree (language_code);


--
-- Name: idx_measurement_units_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_measurement_units_category ON public.measurement_units USING btree (category);


--
-- Name: idx_notifications_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notifications_created ON public.notifications USING btree (created_at);


--
-- Name: idx_notifications_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notifications_org ON public.notifications USING btree (organization_id);


--
-- Name: idx_notifications_read; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notifications_read ON public.notifications USING btree (is_read);


--
-- Name: idx_notifications_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notifications_type ON public.notifications USING btree (notification_type);


--
-- Name: idx_notifications_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notifications_user ON public.notifications USING btree (user_id);


--
-- Name: idx_option_sets_owner; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_option_sets_owner ON public.option_sets USING btree (owner_org_id);


--
-- Name: idx_option_sets_system; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_option_sets_system ON public.option_sets USING btree (is_system_defined);


--
-- Name: idx_option_translations_lang; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_option_translations_lang ON public.option_translations USING btree (language_code);


--
-- Name: idx_options_option_set; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_options_option_set ON public.options USING btree (option_set_id);


--
-- Name: idx_options_set; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_options_set ON public.options USING btree (option_set_id);


--
-- Name: idx_options_sort; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_options_sort ON public.options USING btree (option_set_id, sort_order);


--
-- Name: idx_org_member_invitations_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_member_invitations_email ON public.org_member_invitations USING btree (invitee_email);


--
-- Name: idx_org_member_invitations_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_member_invitations_org ON public.org_member_invitations USING btree (organization_id);


--
-- Name: idx_org_member_invitations_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_member_invitations_status ON public.org_member_invitations USING btree (status);


--
-- Name: idx_org_member_roles_composite; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_member_roles_composite ON public.org_member_roles USING btree (user_id, organization_id, role_id);


--
-- Name: idx_org_member_roles_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_member_roles_org ON public.org_member_roles USING btree (organization_id);


--
-- Name: idx_org_member_roles_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_member_roles_user ON public.org_member_roles USING btree (user_id);


--
-- Name: idx_org_members_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_members_org ON public.org_members USING btree (organization_id);


--
-- Name: idx_org_members_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_members_status ON public.org_members USING btree (status);


--
-- Name: idx_org_members_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_members_user ON public.org_members USING btree (user_id);


--
-- Name: idx_org_sub_history_dates; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_sub_history_dates ON public.org_subscription_history USING btree (subscription_start_date, subscription_end_date);


--
-- Name: idx_org_sub_history_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_sub_history_org ON public.org_subscription_history USING btree (organization_id);


--
-- Name: idx_org_sub_history_plan; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_org_sub_history_plan ON public.org_subscription_history USING btree (subscription_plan_id);


--
-- Name: idx_organizations_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_organizations_status ON public.organizations USING btree (status);


--
-- Name: idx_organizations_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_organizations_type ON public.organizations USING btree (organization_type);


--
-- Name: idx_param_option_map_optset; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_param_option_map_optset ON public.parameter_option_set_map USING btree (option_set_id);


--
-- Name: idx_param_option_map_param; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_param_option_map_param ON public.parameter_option_set_map USING btree (parameter_id);


--
-- Name: idx_parameter_option_set_map_option_set; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_parameter_option_set_map_option_set ON public.parameter_option_set_map USING btree (option_set_id);


--
-- Name: idx_parameter_option_set_map_param; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_parameter_option_set_map_param ON public.parameter_option_set_map USING btree (parameter_id);


--
-- Name: idx_parameter_translations_lang; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_parameter_translations_lang ON public.parameter_translations USING btree (language_code);


--
-- Name: idx_parameters_owner; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_parameters_owner ON public.parameters USING btree (owner_org_id);


--
-- Name: idx_parameters_system; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_parameters_system ON public.parameters USING btree (is_system_defined);


--
-- Name: idx_parameters_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_parameters_type ON public.parameters USING btree (parameter_type);


--
-- Name: idx_plan_history_effective; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_plan_history_effective ON public.subscription_plan_history USING btree (effective_from, effective_to);


--
-- Name: idx_plan_history_plan; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_plan_history_plan ON public.subscription_plan_history USING btree (plan_id);


--
-- Name: idx_plots_attributes; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_plots_attributes ON public.plots USING gin (plot_attributes);


--
-- Name: idx_plots_boundary; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_plots_boundary ON public.plots USING gist (boundary);


--
-- Name: idx_plots_farm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_plots_farm ON public.plots USING btree (farm_id);


--
-- Name: idx_plots_name_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_plots_name_trgm ON public.plots USING gin (name public.gin_trgm_ops);


--
-- Name: idx_push_tokens_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_push_tokens_user ON public.push_notification_tokens USING btree (user_id);


--
-- Name: idx_queries_crop; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_queries_crop ON public.queries USING btree (crop_id);


--
-- Name: idx_queries_farming_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_queries_farming_org ON public.queries USING btree (farming_organization_id);


--
-- Name: idx_queries_fsp_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_queries_fsp_org ON public.queries USING btree (fsp_organization_id);


--
-- Name: idx_queries_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_queries_status ON public.queries USING btree (status);


--
-- Name: idx_queries_title_trgm; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_queries_title_trgm ON public.queries USING gin (title public.gin_trgm_ops);


--
-- Name: idx_queries_work_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_queries_work_order ON public.queries USING btree (work_order_id);


--
-- Name: idx_query_photos_query; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_query_photos_query ON public.query_photos USING btree (query_id);


--
-- Name: idx_query_photos_response; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_query_photos_response ON public.query_photos USING btree (query_response_id);


--
-- Name: idx_query_responses_query; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_query_responses_query ON public.query_responses USING btree (query_id);


--
-- Name: idx_ref_data_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ref_data_type ON public.reference_data USING btree (type_id);


--
-- Name: idx_ref_translations_lang; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ref_translations_lang ON public.reference_data_translations USING btree (language_code);


--
-- Name: idx_refresh_tokens_expires; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_refresh_tokens_expires ON public.refresh_tokens USING btree (expires_at);


--
-- Name: idx_refresh_tokens_revoked; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_refresh_tokens_revoked ON public.refresh_tokens USING btree (is_revoked);


--
-- Name: idx_refresh_tokens_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_refresh_tokens_user ON public.refresh_tokens USING btree (user_id);


--
-- Name: idx_schedule_change_log_details_after; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_change_log_details_after ON public.schedule_change_log USING gin (task_details_after);


--
-- Name: idx_schedule_change_log_details_before; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_change_log_details_before ON public.schedule_change_log USING gin (task_details_before);


--
-- Name: idx_schedule_change_log_is_applied; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_change_log_is_applied ON public.schedule_change_log USING btree (is_applied) WHERE (is_applied = false);


--
-- Name: idx_schedule_change_log_schedule; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_change_log_schedule ON public.schedule_change_log USING btree (schedule_id);


--
-- Name: idx_schedule_change_log_trigger; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_change_log_trigger ON public.schedule_change_log USING btree (trigger_type, trigger_reference_id);


--
-- Name: idx_schedule_change_log_trigger_audit; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_change_log_trigger_audit ON public.schedule_change_log USING btree (trigger_type, trigger_reference_id) WHERE (trigger_type = 'AUDIT'::public.schedule_change_trigger);


--
-- Name: idx_schedule_tasks_composite; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_tasks_composite ON public.schedule_tasks USING btree (schedule_id, status, due_date);


--
-- Name: idx_schedule_tasks_details; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_tasks_details ON public.schedule_tasks USING gin (task_details);


--
-- Name: idx_schedule_tasks_due_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_tasks_due_date ON public.schedule_tasks USING btree (due_date);


--
-- Name: idx_schedule_tasks_schedule; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_tasks_schedule ON public.schedule_tasks USING btree (schedule_id);


--
-- Name: idx_schedule_tasks_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_tasks_status ON public.schedule_tasks USING btree (status);


--
-- Name: idx_schedule_tasks_task; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_tasks_task ON public.schedule_tasks USING btree (task_id);


--
-- Name: idx_schedule_template_tasks_details; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_template_tasks_details ON public.schedule_template_tasks USING gin (task_details_template);


--
-- Name: idx_schedule_template_tasks_offset; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_template_tasks_offset ON public.schedule_template_tasks USING btree (day_offset);


--
-- Name: idx_schedule_template_tasks_task; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_template_tasks_task ON public.schedule_template_tasks USING btree (task_id);


--
-- Name: idx_schedule_template_tasks_template; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_template_tasks_template ON public.schedule_template_tasks USING btree (schedule_template_id);


--
-- Name: idx_schedule_template_translations_lang; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_template_translations_lang ON public.schedule_template_translations USING btree (language_code);


--
-- Name: idx_schedule_templates_crop_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_templates_crop_type ON public.schedule_templates USING btree (crop_type_id);


--
-- Name: idx_schedule_templates_crop_variety; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_templates_crop_variety ON public.schedule_templates USING btree (crop_variety_id);


--
-- Name: idx_schedule_templates_owner; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_templates_owner ON public.schedule_templates USING btree (owner_org_id);


--
-- Name: idx_schedule_templates_system; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedule_templates_system ON public.schedule_templates USING btree (is_system_defined);


--
-- Name: idx_schedules_crop; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedules_crop ON public.schedules USING btree (crop_id);


--
-- Name: idx_schedules_template; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_schedules_template ON public.schedules USING btree (template_id);


--
-- Name: idx_section_translations_lang; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_section_translations_lang ON public.section_translations USING btree (language_code);


--
-- Name: idx_sections_owner; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sections_owner ON public.sections USING btree (owner_org_id);


--
-- Name: idx_sections_system; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sections_system ON public.sections USING btree (is_system_defined);


--
-- Name: idx_task_actuals_crop; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_actuals_crop ON public.task_actuals USING btree (crop_id);


--
-- Name: idx_task_actuals_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_actuals_date ON public.task_actuals USING btree (actual_date);


--
-- Name: idx_task_actuals_details; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_actuals_details ON public.task_actuals USING gin (task_details);


--
-- Name: idx_task_actuals_is_planned; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_actuals_is_planned ON public.task_actuals USING btree (is_planned);


--
-- Name: idx_task_actuals_plot; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_actuals_plot ON public.task_actuals USING btree (plot_id);


--
-- Name: idx_task_actuals_schedule; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_actuals_schedule ON public.task_actuals USING btree (schedule_id);


--
-- Name: idx_task_actuals_schedule_task; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_actuals_schedule_task ON public.task_actuals USING btree (schedule_task_id);


--
-- Name: idx_task_actuals_task; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_actuals_task ON public.task_actuals USING btree (task_id);


--
-- Name: idx_task_photos_actual; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_task_photos_actual ON public.task_photos USING btree (task_actual_id);


--
-- Name: idx_template_parameters_section; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_template_parameters_section ON public.template_parameters USING btree (template_section_id);


--
-- Name: idx_template_parameters_sort; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_template_parameters_sort ON public.template_parameters USING btree (template_section_id, sort_order);


--
-- Name: idx_template_params_parameter; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_template_params_parameter ON public.template_parameters USING btree (parameter_id);


--
-- Name: idx_template_params_section; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_template_params_section ON public.template_parameters USING btree (template_section_id);


--
-- Name: idx_template_sections_section; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_template_sections_section ON public.template_sections USING btree (section_id);


--
-- Name: idx_template_sections_sort; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_template_sections_sort ON public.template_sections USING btree (template_id, sort_order);


--
-- Name: idx_template_sections_template; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_template_sections_template ON public.template_sections USING btree (template_id);


--
-- Name: idx_template_translations_lang; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_template_translations_lang ON public.template_translations USING btree (language_code);


--
-- Name: idx_templates_crop_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_templates_crop_type ON public.templates USING btree (crop_type_id);


--
-- Name: idx_templates_owner; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_templates_owner ON public.templates USING btree (owner_org_id);


--
-- Name: idx_templates_system; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_templates_system ON public.templates USING btree (is_system_defined);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: idx_users_phone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_phone ON public.users USING btree (phone);


--
-- Name: idx_work_order_scope_permissions; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_work_order_scope_permissions ON public.work_order_scope USING gin (access_permissions);


--
-- Name: idx_work_order_scope_scope_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_work_order_scope_scope_id ON public.work_order_scope USING btree (scope, scope_id);


--
-- Name: idx_work_order_scope_work_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_work_order_scope_work_order ON public.work_order_scope USING btree (work_order_id);


--
-- Name: idx_work_orders_assigned_to; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_work_orders_assigned_to ON public.work_orders USING btree (assigned_to_user_id);


--
-- Name: idx_work_orders_composite; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_work_orders_composite ON public.work_orders USING btree (farming_organization_id, fsp_organization_id, status);


--
-- Name: idx_work_orders_farming_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_work_orders_farming_org ON public.work_orders USING btree (farming_organization_id);


--
-- Name: idx_work_orders_fsp_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_work_orders_fsp_org ON public.work_orders USING btree (fsp_organization_id);


--
-- Name: idx_work_orders_scope_metadata; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_work_orders_scope_metadata ON public.work_orders USING gin (scope_metadata);


--
-- Name: idx_work_orders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_work_orders_status ON public.work_orders USING btree (status);


--
-- Name: audit_parameter_instances update_audit_param_instances_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_audit_param_instances_updated_at BEFORE UPDATE ON public.audit_parameter_instances FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: audit_responses update_audit_responses_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_audit_responses_updated_at BEFORE UPDATE ON public.audit_responses FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: audits update_audits_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_audits_updated_at BEFORE UPDATE ON public.audits FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: crops update_crops_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_crops_updated_at BEFORE UPDATE ON public.crops FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: farms update_farms_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_farms_updated_at BEFORE UPDATE ON public.farms FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: finance_categories update_finance_categories_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_finance_categories_updated_at BEFORE UPDATE ON public.finance_categories FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: finance_transactions update_finance_transactions_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_finance_transactions_updated_at BEFORE UPDATE ON public.finance_transactions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: input_item_categories update_input_item_categories_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_input_item_categories_updated_at BEFORE UPDATE ON public.input_item_categories FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: input_items update_input_items_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_input_items_updated_at BEFORE UPDATE ON public.input_items FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: option_sets update_option_sets_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_option_sets_updated_at BEFORE UPDATE ON public.option_sets FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: organizations update_organizations_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON public.organizations FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: parameters update_parameters_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_parameters_updated_at BEFORE UPDATE ON public.parameters FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: plots update_plots_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_plots_updated_at BEFORE UPDATE ON public.plots FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: queries update_queries_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_queries_updated_at BEFORE UPDATE ON public.queries FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: schedule_tasks update_schedule_tasks_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_schedule_tasks_updated_at BEFORE UPDATE ON public.schedule_tasks FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: schedule_template_tasks update_schedule_template_tasks_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_schedule_template_tasks_updated_at BEFORE UPDATE ON public.schedule_template_tasks FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: schedule_templates update_schedule_templates_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_schedule_templates_updated_at BEFORE UPDATE ON public.schedule_templates FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: schedules update_schedules_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_schedules_updated_at BEFORE UPDATE ON public.schedules FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: sections update_sections_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_sections_updated_at BEFORE UPDATE ON public.sections FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: templates update_templates_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON public.templates FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: users update_users_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: work_orders update_work_orders_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_work_orders_updated_at BEFORE UPDATE ON public.work_orders FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: audit_issues audit_issues_audit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_issues
    ADD CONSTRAINT audit_issues_audit_id_fkey FOREIGN KEY (audit_id) REFERENCES public.audits(id) ON DELETE CASCADE;


--
-- Name: audit_issues audit_issues_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_issues
    ADD CONSTRAINT audit_issues_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: audit_log audit_log_changed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES public.users(id);


--
-- Name: audit_parameter_instances audit_parameter_instances_audit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_parameter_instances
    ADD CONSTRAINT audit_parameter_instances_audit_id_fkey FOREIGN KEY (audit_id) REFERENCES public.audits(id) ON DELETE CASCADE;


--
-- Name: audit_parameter_instances audit_parameter_instances_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_parameter_instances
    ADD CONSTRAINT audit_parameter_instances_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: audit_parameter_instances audit_parameter_instances_parameter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_parameter_instances
    ADD CONSTRAINT audit_parameter_instances_parameter_id_fkey FOREIGN KEY (parameter_id) REFERENCES public.parameters(id);


--
-- Name: audit_parameter_instances audit_parameter_instances_template_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_parameter_instances
    ADD CONSTRAINT audit_parameter_instances_template_section_id_fkey FOREIGN KEY (template_section_id) REFERENCES public.template_sections(id);


--
-- Name: audit_recommendations audit_recommendations_audit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_recommendations
    ADD CONSTRAINT audit_recommendations_audit_id_fkey FOREIGN KEY (audit_id) REFERENCES public.audits(id) ON DELETE CASCADE;


--
-- Name: audit_recommendations audit_recommendations_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_recommendations
    ADD CONSTRAINT audit_recommendations_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: audit_reports audit_reports_audit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_reports
    ADD CONSTRAINT audit_reports_audit_id_fkey FOREIGN KEY (audit_id) REFERENCES public.audits(id) ON DELETE CASCADE;


--
-- Name: audit_reports audit_reports_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_reports
    ADD CONSTRAINT audit_reports_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: audit_response_photos audit_response_photos_audit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_response_photos
    ADD CONSTRAINT audit_response_photos_audit_id_fkey FOREIGN KEY (audit_id) REFERENCES public.audits(id) ON DELETE CASCADE;


--
-- Name: audit_response_photos audit_response_photos_audit_response_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_response_photos
    ADD CONSTRAINT audit_response_photos_audit_response_id_fkey FOREIGN KEY (audit_response_id) REFERENCES public.audit_responses(id) ON DELETE CASCADE;


--
-- Name: audit_response_photos audit_response_photos_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_response_photos
    ADD CONSTRAINT audit_response_photos_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- Name: audit_responses audit_responses_audit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_responses
    ADD CONSTRAINT audit_responses_audit_id_fkey FOREIGN KEY (audit_id) REFERENCES public.audits(id) ON DELETE CASCADE;


--
-- Name: audit_responses audit_responses_audit_parameter_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_responses
    ADD CONSTRAINT audit_responses_audit_parameter_instance_id_fkey FOREIGN KEY (audit_parameter_instance_id) REFERENCES public.audit_parameter_instances(id) ON DELETE CASCADE;


--
-- Name: audit_responses audit_responses_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_responses
    ADD CONSTRAINT audit_responses_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: audit_review_photos audit_review_photos_audit_response_photo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_review_photos
    ADD CONSTRAINT audit_review_photos_audit_response_photo_id_fkey FOREIGN KEY (audit_response_photo_id) REFERENCES public.audit_response_photos(id) ON DELETE CASCADE;


--
-- Name: audit_review_photos audit_review_photos_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_review_photos
    ADD CONSTRAINT audit_review_photos_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id);


--
-- Name: audit_reviews audit_reviews_audit_response_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_reviews
    ADD CONSTRAINT audit_reviews_audit_response_id_fkey FOREIGN KEY (audit_response_id) REFERENCES public.audit_responses(id) ON DELETE CASCADE;


--
-- Name: audit_reviews audit_reviews_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_reviews
    ADD CONSTRAINT audit_reviews_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id);


--
-- Name: audits audits_analyst_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT audits_analyst_user_id_fkey FOREIGN KEY (analyst_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: audits audits_assigned_to_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT audits_assigned_to_user_id_fkey FOREIGN KEY (assigned_to_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: audits audits_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT audits_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: audits audits_crop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT audits_crop_id_fkey FOREIGN KEY (crop_id) REFERENCES public.crops(id) ON DELETE CASCADE;


--
-- Name: audits audits_farming_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT audits_farming_organization_id_fkey FOREIGN KEY (farming_organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: audits audits_finalized_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT audits_finalized_by_fkey FOREIGN KEY (finalized_by) REFERENCES public.users(id);


--
-- Name: audits audits_fsp_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT audits_fsp_organization_id_fkey FOREIGN KEY (fsp_organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: audits audits_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT audits_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.templates(id);


--
-- Name: audits audits_work_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT audits_work_order_id_fkey FOREIGN KEY (work_order_id) REFERENCES public.work_orders(id) ON DELETE CASCADE;


--
-- Name: chat_channel_members chat_channel_members_added_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_channel_members
    ADD CONSTRAINT chat_channel_members_added_by_fkey FOREIGN KEY (added_by) REFERENCES public.users(id);


--
-- Name: chat_channel_members chat_channel_members_channel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_channel_members
    ADD CONSTRAINT chat_channel_members_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.chat_channels(id) ON DELETE CASCADE;


--
-- Name: chat_channel_members chat_channel_members_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_channel_members
    ADD CONSTRAINT chat_channel_members_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: chat_channels chat_channels_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_channels
    ADD CONSTRAINT chat_channels_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: chat_channels chat_channels_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_channels
    ADD CONSTRAINT chat_channels_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: chat_messages chat_messages_channel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.chat_channels(id) ON DELETE CASCADE;


--
-- Name: chat_messages chat_messages_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id);


--
-- Name: chat_messages chat_messages_sender_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_sender_org_id_fkey FOREIGN KEY (sender_org_id) REFERENCES public.organizations(id);


--
-- Name: crop_category_translations crop_category_translations_crop_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_category_translations
    ADD CONSTRAINT crop_category_translations_crop_category_id_fkey FOREIGN KEY (crop_category_id) REFERENCES public.crop_categories(id) ON DELETE CASCADE;


--
-- Name: crop_lifecycle_photos crop_lifecycle_photos_crop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_lifecycle_photos
    ADD CONSTRAINT crop_lifecycle_photos_crop_id_fkey FOREIGN KEY (crop_id) REFERENCES public.crops(id) ON DELETE CASCADE;


--
-- Name: crop_lifecycle_photos crop_lifecycle_photos_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_lifecycle_photos
    ADD CONSTRAINT crop_lifecycle_photos_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- Name: crop_type_translations crop_type_translations_crop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_type_translations
    ADD CONSTRAINT crop_type_translations_crop_type_id_fkey FOREIGN KEY (crop_type_id) REFERENCES public.crop_types(id) ON DELETE CASCADE;


--
-- Name: crop_types crop_types_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_types
    ADD CONSTRAINT crop_types_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.crop_categories(id) ON DELETE CASCADE;


--
-- Name: crop_varieties crop_varieties_crop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_varieties
    ADD CONSTRAINT crop_varieties_crop_type_id_fkey FOREIGN KEY (crop_type_id) REFERENCES public.crop_types(id) ON DELETE CASCADE;


--
-- Name: crop_variety_translations crop_variety_translations_crop_variety_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_variety_translations
    ADD CONSTRAINT crop_variety_translations_crop_variety_id_fkey FOREIGN KEY (crop_variety_id) REFERENCES public.crop_varieties(id) ON DELETE CASCADE;


--
-- Name: crop_yield_photos crop_yield_photos_crop_yield_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_yield_photos
    ADD CONSTRAINT crop_yield_photos_crop_yield_id_fkey FOREIGN KEY (crop_yield_id) REFERENCES public.crop_yields(id) ON DELETE CASCADE;


--
-- Name: crop_yield_photos crop_yield_photos_photo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_yield_photos
    ADD CONSTRAINT crop_yield_photos_photo_id_fkey FOREIGN KEY (photo_id) REFERENCES public.crop_lifecycle_photos(id) ON DELETE CASCADE;


--
-- Name: crop_yields crop_yields_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_yields
    ADD CONSTRAINT crop_yields_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: crop_yields crop_yields_crop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_yields
    ADD CONSTRAINT crop_yields_crop_id_fkey FOREIGN KEY (crop_id) REFERENCES public.crops(id) ON DELETE CASCADE;


--
-- Name: crop_yields crop_yields_harvest_area_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_yields
    ADD CONSTRAINT crop_yields_harvest_area_unit_id_fkey FOREIGN KEY (harvest_area_unit_id) REFERENCES public.measurement_units(id);


--
-- Name: crop_yields crop_yields_quantity_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crop_yields
    ADD CONSTRAINT crop_yields_quantity_unit_id_fkey FOREIGN KEY (quantity_unit_id) REFERENCES public.measurement_units(id);


--
-- Name: crops crops_area_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crops
    ADD CONSTRAINT crops_area_unit_id_fkey FOREIGN KEY (area_unit_id) REFERENCES public.measurement_units(id);


--
-- Name: crops crops_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crops
    ADD CONSTRAINT crops_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: crops crops_crop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crops
    ADD CONSTRAINT crops_crop_type_id_fkey FOREIGN KEY (crop_type_id) REFERENCES public.crop_types(id);


--
-- Name: crops crops_crop_variety_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crops
    ADD CONSTRAINT crops_crop_variety_id_fkey FOREIGN KEY (crop_variety_id) REFERENCES public.crop_varieties(id);


--
-- Name: crops crops_plot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crops
    ADD CONSTRAINT crops_plot_id_fkey FOREIGN KEY (plot_id) REFERENCES public.plots(id) ON DELETE CASCADE;


--
-- Name: crops crops_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crops
    ADD CONSTRAINT crops_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: farm_irrigation_modes farm_irrigation_modes_farm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_irrigation_modes
    ADD CONSTRAINT farm_irrigation_modes_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES public.farms(id) ON DELETE CASCADE;


--
-- Name: farm_irrigation_modes farm_irrigation_modes_irrigation_mode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_irrigation_modes
    ADD CONSTRAINT farm_irrigation_modes_irrigation_mode_id_fkey FOREIGN KEY (irrigation_mode_id) REFERENCES public.reference_data(id);


--
-- Name: farm_soil_types farm_soil_types_farm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_soil_types
    ADD CONSTRAINT farm_soil_types_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES public.farms(id) ON DELETE CASCADE;


--
-- Name: farm_soil_types farm_soil_types_soil_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_soil_types
    ADD CONSTRAINT farm_soil_types_soil_type_id_fkey FOREIGN KEY (soil_type_id) REFERENCES public.reference_data(id);


--
-- Name: farm_supervisors farm_supervisors_assigned_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_supervisors
    ADD CONSTRAINT farm_supervisors_assigned_by_fkey FOREIGN KEY (assigned_by) REFERENCES public.users(id);


--
-- Name: farm_supervisors farm_supervisors_farm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_supervisors
    ADD CONSTRAINT farm_supervisors_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES public.farms(id) ON DELETE CASCADE;


--
-- Name: farm_supervisors farm_supervisors_supervisor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_supervisors
    ADD CONSTRAINT farm_supervisors_supervisor_id_fkey FOREIGN KEY (supervisor_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: farm_water_sources farm_water_sources_farm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_water_sources
    ADD CONSTRAINT farm_water_sources_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES public.farms(id) ON DELETE CASCADE;


--
-- Name: farm_water_sources farm_water_sources_water_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farm_water_sources
    ADD CONSTRAINT farm_water_sources_water_source_id_fkey FOREIGN KEY (water_source_id) REFERENCES public.reference_data(id);


--
-- Name: farms farms_area_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farms
    ADD CONSTRAINT farms_area_unit_id_fkey FOREIGN KEY (area_unit_id) REFERENCES public.measurement_units(id);


--
-- Name: farms farms_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farms
    ADD CONSTRAINT farms_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: farms farms_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farms
    ADD CONSTRAINT farms_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- Name: farms farms_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farms
    ADD CONSTRAINT farms_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: farms farms_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.farms
    ADD CONSTRAINT farms_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: finance_categories finance_categories_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_categories
    ADD CONSTRAINT finance_categories_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: finance_categories finance_categories_owner_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_categories
    ADD CONSTRAINT finance_categories_owner_org_id_fkey FOREIGN KEY (owner_org_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: finance_categories finance_categories_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_categories
    ADD CONSTRAINT finance_categories_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: finance_category_translations finance_category_translations_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_category_translations
    ADD CONSTRAINT finance_category_translations_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.finance_categories(id) ON DELETE CASCADE;


--
-- Name: finance_transaction_attachments finance_transaction_attachments_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transaction_attachments
    ADD CONSTRAINT finance_transaction_attachments_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.finance_transactions(id) ON DELETE CASCADE;


--
-- Name: finance_transaction_attachments finance_transaction_attachments_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transaction_attachments
    ADD CONSTRAINT finance_transaction_attachments_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- Name: finance_transaction_splits finance_transaction_splits_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transaction_splits
    ADD CONSTRAINT finance_transaction_splits_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: finance_transaction_splits finance_transaction_splits_crop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transaction_splits
    ADD CONSTRAINT finance_transaction_splits_crop_id_fkey FOREIGN KEY (crop_id) REFERENCES public.crops(id);


--
-- Name: finance_transaction_splits finance_transaction_splits_farm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transaction_splits
    ADD CONSTRAINT finance_transaction_splits_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES public.farms(id);


--
-- Name: finance_transaction_splits finance_transaction_splits_plot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transaction_splits
    ADD CONSTRAINT finance_transaction_splits_plot_id_fkey FOREIGN KEY (plot_id) REFERENCES public.plots(id);


--
-- Name: finance_transaction_splits finance_transaction_splits_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transaction_splits
    ADD CONSTRAINT finance_transaction_splits_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.finance_transactions(id) ON DELETE CASCADE;


--
-- Name: finance_transactions finance_transactions_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transactions
    ADD CONSTRAINT finance_transactions_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.finance_categories(id);


--
-- Name: finance_transactions finance_transactions_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transactions
    ADD CONSTRAINT finance_transactions_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: finance_transactions finance_transactions_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transactions
    ADD CONSTRAINT finance_transactions_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: finance_transactions finance_transactions_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_transactions
    ADD CONSTRAINT finance_transactions_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: fsp_approval_documents fsp_approval_documents_fsp_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fsp_approval_documents
    ADD CONSTRAINT fsp_approval_documents_fsp_organization_id_fkey FOREIGN KEY (fsp_organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: fsp_approval_documents fsp_approval_documents_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fsp_approval_documents
    ADD CONSTRAINT fsp_approval_documents_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- Name: fsp_service_listings fsp_service_listings_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fsp_service_listings
    ADD CONSTRAINT fsp_service_listings_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: fsp_service_listings fsp_service_listings_fsp_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fsp_service_listings
    ADD CONSTRAINT fsp_service_listings_fsp_organization_id_fkey FOREIGN KEY (fsp_organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: fsp_service_listings fsp_service_listings_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fsp_service_listings
    ADD CONSTRAINT fsp_service_listings_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.master_services(id);


--
-- Name: fsp_service_listings fsp_service_listings_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fsp_service_listings
    ADD CONSTRAINT fsp_service_listings_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: input_item_categories input_item_categories_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_item_categories
    ADD CONSTRAINT input_item_categories_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: input_item_categories input_item_categories_owner_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_item_categories
    ADD CONSTRAINT input_item_categories_owner_org_id_fkey FOREIGN KEY (owner_org_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: input_item_categories input_item_categories_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_item_categories
    ADD CONSTRAINT input_item_categories_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: input_item_category_translations input_item_category_translations_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_item_category_translations
    ADD CONSTRAINT input_item_category_translations_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.input_item_categories(id) ON DELETE CASCADE;


--
-- Name: input_item_translations input_item_translations_input_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_item_translations
    ADD CONSTRAINT input_item_translations_input_item_id_fkey FOREIGN KEY (input_item_id) REFERENCES public.input_items(id) ON DELETE CASCADE;


--
-- Name: input_items input_items_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_items
    ADD CONSTRAINT input_items_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.input_item_categories(id) ON DELETE CASCADE;


--
-- Name: input_items input_items_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_items
    ADD CONSTRAINT input_items_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: input_items input_items_default_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_items
    ADD CONSTRAINT input_items_default_unit_id_fkey FOREIGN KEY (default_unit_id) REFERENCES public.measurement_units(id);


--
-- Name: input_items input_items_owner_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_items
    ADD CONSTRAINT input_items_owner_org_id_fkey FOREIGN KEY (owner_org_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: input_items input_items_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_items
    ADD CONSTRAINT input_items_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: master_service_translations master_service_translations_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.master_service_translations
    ADD CONSTRAINT master_service_translations_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.master_services(id) ON DELETE CASCADE;


--
-- Name: measurement_unit_translations measurement_unit_translations_measurement_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.measurement_unit_translations
    ADD CONSTRAINT measurement_unit_translations_measurement_unit_id_fkey FOREIGN KEY (measurement_unit_id) REFERENCES public.measurement_units(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: option_sets option_sets_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.option_sets
    ADD CONSTRAINT option_sets_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: option_sets option_sets_owner_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.option_sets
    ADD CONSTRAINT option_sets_owner_org_id_fkey FOREIGN KEY (owner_org_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: option_sets option_sets_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.option_sets
    ADD CONSTRAINT option_sets_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: option_translations option_translations_option_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.option_translations
    ADD CONSTRAINT option_translations_option_id_fkey FOREIGN KEY (option_id) REFERENCES public.options(id) ON DELETE CASCADE;


--
-- Name: options options_option_set_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.options
    ADD CONSTRAINT options_option_set_id_fkey FOREIGN KEY (option_set_id) REFERENCES public.option_sets(id) ON DELETE CASCADE;


--
-- Name: org_member_invitations org_member_invitations_invitee_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_member_invitations
    ADD CONSTRAINT org_member_invitations_invitee_user_id_fkey FOREIGN KEY (invitee_user_id) REFERENCES public.users(id);


--
-- Name: org_member_invitations org_member_invitations_inviter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_member_invitations
    ADD CONSTRAINT org_member_invitations_inviter_id_fkey FOREIGN KEY (inviter_id) REFERENCES public.users(id);


--
-- Name: org_member_invitations org_member_invitations_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_member_invitations
    ADD CONSTRAINT org_member_invitations_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: org_member_invitations org_member_invitations_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_member_invitations
    ADD CONSTRAINT org_member_invitations_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: org_member_roles org_member_roles_assigned_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_member_roles
    ADD CONSTRAINT org_member_roles_assigned_by_fkey FOREIGN KEY (assigned_by) REFERENCES public.users(id);


--
-- Name: org_member_roles org_member_roles_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_member_roles
    ADD CONSTRAINT org_member_roles_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: org_member_roles org_member_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_member_roles
    ADD CONSTRAINT org_member_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: org_member_roles org_member_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_member_roles
    ADD CONSTRAINT org_member_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: org_members org_members_invitation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_members
    ADD CONSTRAINT org_members_invitation_id_fkey FOREIGN KEY (invitation_id) REFERENCES public.org_member_invitations(id);


--
-- Name: org_members org_members_invited_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_members
    ADD CONSTRAINT org_members_invited_by_fkey FOREIGN KEY (invited_by) REFERENCES public.users(id);


--
-- Name: org_members org_members_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_members
    ADD CONSTRAINT org_members_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: org_members org_members_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_members
    ADD CONSTRAINT org_members_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: org_role_permission_overrides org_role_permission_overrides_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_role_permission_overrides
    ADD CONSTRAINT org_role_permission_overrides_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: org_role_permission_overrides org_role_permission_overrides_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_role_permission_overrides
    ADD CONSTRAINT org_role_permission_overrides_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: org_role_permission_overrides org_role_permission_overrides_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_role_permission_overrides
    ADD CONSTRAINT org_role_permission_overrides_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: org_role_permission_overrides org_role_permission_overrides_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_role_permission_overrides
    ADD CONSTRAINT org_role_permission_overrides_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: org_subscription_history org_subscription_history_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_subscription_history
    ADD CONSTRAINT org_subscription_history_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: org_subscription_history org_subscription_history_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_subscription_history
    ADD CONSTRAINT org_subscription_history_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: org_subscription_history org_subscription_history_subscription_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.org_subscription_history
    ADD CONSTRAINT org_subscription_history_subscription_plan_id_fkey FOREIGN KEY (subscription_plan_id) REFERENCES public.subscription_plans(id);


--
-- Name: organizations organizations_subscription_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_subscription_plan_id_fkey FOREIGN KEY (subscription_plan_id) REFERENCES public.subscription_plans(id);


--
-- Name: parameter_option_set_map parameter_option_set_map_option_set_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parameter_option_set_map
    ADD CONSTRAINT parameter_option_set_map_option_set_id_fkey FOREIGN KEY (option_set_id) REFERENCES public.option_sets(id) ON DELETE CASCADE;


--
-- Name: parameter_option_set_map parameter_option_set_map_parameter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parameter_option_set_map
    ADD CONSTRAINT parameter_option_set_map_parameter_id_fkey FOREIGN KEY (parameter_id) REFERENCES public.parameters(id) ON DELETE CASCADE;


--
-- Name: parameter_translations parameter_translations_parameter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parameter_translations
    ADD CONSTRAINT parameter_translations_parameter_id_fkey FOREIGN KEY (parameter_id) REFERENCES public.parameters(id) ON DELETE CASCADE;


--
-- Name: parameters parameters_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parameters
    ADD CONSTRAINT parameters_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: parameters parameters_owner_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parameters
    ADD CONSTRAINT parameters_owner_org_id_fkey FOREIGN KEY (owner_org_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: parameters parameters_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parameters
    ADD CONSTRAINT parameters_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: plot_irrigation_modes plot_irrigation_modes_irrigation_mode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plot_irrigation_modes
    ADD CONSTRAINT plot_irrigation_modes_irrigation_mode_id_fkey FOREIGN KEY (irrigation_mode_id) REFERENCES public.reference_data(id);


--
-- Name: plot_irrigation_modes plot_irrigation_modes_plot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plot_irrigation_modes
    ADD CONSTRAINT plot_irrigation_modes_plot_id_fkey FOREIGN KEY (plot_id) REFERENCES public.plots(id) ON DELETE CASCADE;


--
-- Name: plot_soil_types plot_soil_types_plot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plot_soil_types
    ADD CONSTRAINT plot_soil_types_plot_id_fkey FOREIGN KEY (plot_id) REFERENCES public.plots(id) ON DELETE CASCADE;


--
-- Name: plot_soil_types plot_soil_types_soil_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plot_soil_types
    ADD CONSTRAINT plot_soil_types_soil_type_id_fkey FOREIGN KEY (soil_type_id) REFERENCES public.reference_data(id);


--
-- Name: plot_water_sources plot_water_sources_plot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plot_water_sources
    ADD CONSTRAINT plot_water_sources_plot_id_fkey FOREIGN KEY (plot_id) REFERENCES public.plots(id) ON DELETE CASCADE;


--
-- Name: plot_water_sources plot_water_sources_water_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plot_water_sources
    ADD CONSTRAINT plot_water_sources_water_source_id_fkey FOREIGN KEY (water_source_id) REFERENCES public.reference_data(id);


--
-- Name: plots plots_area_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plots
    ADD CONSTRAINT plots_area_unit_id_fkey FOREIGN KEY (area_unit_id) REFERENCES public.measurement_units(id);


--
-- Name: plots plots_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plots
    ADD CONSTRAINT plots_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: plots plots_farm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plots
    ADD CONSTRAINT plots_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES public.farms(id) ON DELETE CASCADE;


--
-- Name: plots plots_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plots
    ADD CONSTRAINT plots_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: push_notification_tokens push_notification_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.push_notification_tokens
    ADD CONSTRAINT push_notification_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: queries queries_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: queries queries_crop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_crop_id_fkey FOREIGN KEY (crop_id) REFERENCES public.crops(id);


--
-- Name: queries queries_farm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES public.farms(id);


--
-- Name: queries queries_farming_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_farming_organization_id_fkey FOREIGN KEY (farming_organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: queries queries_fsp_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_fsp_organization_id_fkey FOREIGN KEY (fsp_organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: queries queries_plot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_plot_id_fkey FOREIGN KEY (plot_id) REFERENCES public.plots(id);


--
-- Name: queries queries_resolved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_resolved_by_fkey FOREIGN KEY (resolved_by) REFERENCES public.users(id);


--
-- Name: queries queries_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: queries queries_work_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queries
    ADD CONSTRAINT queries_work_order_id_fkey FOREIGN KEY (work_order_id) REFERENCES public.work_orders(id) ON DELETE CASCADE;


--
-- Name: query_photos query_photos_query_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.query_photos
    ADD CONSTRAINT query_photos_query_id_fkey FOREIGN KEY (query_id) REFERENCES public.queries(id) ON DELETE CASCADE;


--
-- Name: query_photos query_photos_query_response_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.query_photos
    ADD CONSTRAINT query_photos_query_response_id_fkey FOREIGN KEY (query_response_id) REFERENCES public.query_responses(id) ON DELETE CASCADE;


--
-- Name: query_photos query_photos_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.query_photos
    ADD CONSTRAINT query_photos_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- Name: query_responses query_responses_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.query_responses
    ADD CONSTRAINT query_responses_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: query_responses query_responses_query_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.query_responses
    ADD CONSTRAINT query_responses_query_id_fkey FOREIGN KEY (query_id) REFERENCES public.queries(id) ON DELETE CASCADE;


--
-- Name: reference_data_translations reference_data_translations_reference_data_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reference_data_translations
    ADD CONSTRAINT reference_data_translations_reference_data_id_fkey FOREIGN KEY (reference_data_id) REFERENCES public.reference_data(id) ON DELETE CASCADE;


--
-- Name: reference_data reference_data_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reference_data
    ADD CONSTRAINT reference_data_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.reference_data_types(id) ON DELETE CASCADE;


--
-- Name: refresh_tokens refresh_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: schedule_change_log schedule_change_log_applied_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_change_log
    ADD CONSTRAINT schedule_change_log_applied_by_fkey FOREIGN KEY (applied_by) REFERENCES public.users(id);


--
-- Name: schedule_change_log schedule_change_log_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_change_log
    ADD CONSTRAINT schedule_change_log_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: schedule_change_log schedule_change_log_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_change_log
    ADD CONSTRAINT schedule_change_log_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.schedules(id) ON DELETE CASCADE;


--
-- Name: schedule_change_log schedule_change_log_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_change_log
    ADD CONSTRAINT schedule_change_log_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.schedule_tasks(id);


--
-- Name: schedule_tasks schedule_tasks_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_tasks
    ADD CONSTRAINT schedule_tasks_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: schedule_tasks schedule_tasks_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_tasks
    ADD CONSTRAINT schedule_tasks_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.schedules(id) ON DELETE CASCADE;


--
-- Name: schedule_tasks schedule_tasks_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_tasks
    ADD CONSTRAINT schedule_tasks_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: schedule_tasks schedule_tasks_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_tasks
    ADD CONSTRAINT schedule_tasks_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: schedule_template_tasks schedule_template_tasks_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_template_tasks
    ADD CONSTRAINT schedule_template_tasks_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: schedule_template_tasks schedule_template_tasks_schedule_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_template_tasks
    ADD CONSTRAINT schedule_template_tasks_schedule_template_id_fkey FOREIGN KEY (schedule_template_id) REFERENCES public.schedule_templates(id) ON DELETE CASCADE;


--
-- Name: schedule_template_tasks schedule_template_tasks_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_template_tasks
    ADD CONSTRAINT schedule_template_tasks_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: schedule_template_tasks schedule_template_tasks_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_template_tasks
    ADD CONSTRAINT schedule_template_tasks_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: schedule_template_translations schedule_template_translations_schedule_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_template_translations
    ADD CONSTRAINT schedule_template_translations_schedule_template_id_fkey FOREIGN KEY (schedule_template_id) REFERENCES public.schedule_templates(id) ON DELETE CASCADE;


--
-- Name: schedule_templates schedule_templates_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_templates
    ADD CONSTRAINT schedule_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: schedule_templates schedule_templates_crop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_templates
    ADD CONSTRAINT schedule_templates_crop_type_id_fkey FOREIGN KEY (crop_type_id) REFERENCES public.crop_types(id);


--
-- Name: schedule_templates schedule_templates_crop_variety_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_templates
    ADD CONSTRAINT schedule_templates_crop_variety_id_fkey FOREIGN KEY (crop_variety_id) REFERENCES public.crop_varieties(id);


--
-- Name: schedule_templates schedule_templates_owner_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_templates
    ADD CONSTRAINT schedule_templates_owner_org_id_fkey FOREIGN KEY (owner_org_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: schedule_templates schedule_templates_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule_templates
    ADD CONSTRAINT schedule_templates_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: schedules schedules_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: schedules schedules_crop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_crop_id_fkey FOREIGN KEY (crop_id) REFERENCES public.crops(id) ON DELETE CASCADE;


--
-- Name: schedules schedules_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.schedule_templates(id);


--
-- Name: schedules schedules_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedules
    ADD CONSTRAINT schedules_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: section_translations section_translations_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.section_translations
    ADD CONSTRAINT section_translations_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id) ON DELETE CASCADE;


--
-- Name: sections sections_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: sections sections_owner_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_owner_org_id_fkey FOREIGN KEY (owner_org_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: sections sections_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: subscription_plan_history subscription_plan_history_changed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscription_plan_history
    ADD CONSTRAINT subscription_plan_history_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES public.users(id);


--
-- Name: subscription_plan_history subscription_plan_history_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscription_plan_history
    ADD CONSTRAINT subscription_plan_history_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.subscription_plans(id) ON DELETE CASCADE;


--
-- Name: task_actuals task_actuals_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_actuals
    ADD CONSTRAINT task_actuals_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: task_actuals task_actuals_crop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_actuals
    ADD CONSTRAINT task_actuals_crop_id_fkey FOREIGN KEY (crop_id) REFERENCES public.crops(id) ON DELETE CASCADE;


--
-- Name: task_actuals task_actuals_plot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_actuals
    ADD CONSTRAINT task_actuals_plot_id_fkey FOREIGN KEY (plot_id) REFERENCES public.plots(id);


--
-- Name: task_actuals task_actuals_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_actuals
    ADD CONSTRAINT task_actuals_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.schedules(id);


--
-- Name: task_actuals task_actuals_schedule_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_actuals
    ADD CONSTRAINT task_actuals_schedule_task_id_fkey FOREIGN KEY (schedule_task_id) REFERENCES public.schedule_tasks(id) ON DELETE CASCADE;


--
-- Name: task_actuals task_actuals_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_actuals
    ADD CONSTRAINT task_actuals_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: task_photos task_photos_task_actual_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_photos
    ADD CONSTRAINT task_photos_task_actual_id_fkey FOREIGN KEY (task_actual_id) REFERENCES public.task_actuals(id) ON DELETE CASCADE;


--
-- Name: task_photos task_photos_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_photos
    ADD CONSTRAINT task_photos_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- Name: task_translations task_translations_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_translations
    ADD CONSTRAINT task_translations_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id) ON DELETE CASCADE;


--
-- Name: template_parameters template_parameters_parameter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.template_parameters
    ADD CONSTRAINT template_parameters_parameter_id_fkey FOREIGN KEY (parameter_id) REFERENCES public.parameters(id);


--
-- Name: template_parameters template_parameters_template_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.template_parameters
    ADD CONSTRAINT template_parameters_template_section_id_fkey FOREIGN KEY (template_section_id) REFERENCES public.template_sections(id) ON DELETE CASCADE;


--
-- Name: template_sections template_sections_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.template_sections
    ADD CONSTRAINT template_sections_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: template_sections template_sections_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.template_sections
    ADD CONSTRAINT template_sections_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.templates(id) ON DELETE CASCADE;


--
-- Name: template_translations template_translations_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.template_translations
    ADD CONSTRAINT template_translations_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.templates(id) ON DELETE CASCADE;


--
-- Name: templates templates_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.templates
    ADD CONSTRAINT templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: templates templates_crop_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.templates
    ADD CONSTRAINT templates_crop_type_id_fkey FOREIGN KEY (crop_type_id) REFERENCES public.crop_types(id);


--
-- Name: templates templates_owner_org_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.templates
    ADD CONSTRAINT templates_owner_org_id_fkey FOREIGN KEY (owner_org_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: templates templates_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.templates
    ADD CONSTRAINT templates_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: work_order_scope work_order_scope_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_order_scope
    ADD CONSTRAINT work_order_scope_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: work_order_scope work_order_scope_work_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_order_scope
    ADD CONSTRAINT work_order_scope_work_order_id_fkey FOREIGN KEY (work_order_id) REFERENCES public.work_orders(id) ON DELETE CASCADE;


--
-- Name: work_orders work_orders_accepted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_orders
    ADD CONSTRAINT work_orders_accepted_by_fkey FOREIGN KEY (accepted_by) REFERENCES public.users(id);


--
-- Name: work_orders work_orders_assigned_to_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_orders
    ADD CONSTRAINT work_orders_assigned_to_user_id_fkey FOREIGN KEY (assigned_to_user_id) REFERENCES public.users(id);


--
-- Name: work_orders work_orders_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_orders
    ADD CONSTRAINT work_orders_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: work_orders work_orders_farming_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_orders
    ADD CONSTRAINT work_orders_farming_organization_id_fkey FOREIGN KEY (farming_organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: work_orders work_orders_fsp_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_orders
    ADD CONSTRAINT work_orders_fsp_organization_id_fkey FOREIGN KEY (fsp_organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: work_orders work_orders_service_listing_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_orders
    ADD CONSTRAINT work_orders_service_listing_id_fkey FOREIGN KEY (service_listing_id) REFERENCES public.fsp_service_listings(id);


--
-- Name: work_orders work_orders_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.work_orders
    ADD CONSTRAINT work_orders_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- Name: audits; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.audits ENABLE ROW LEVEL SECURITY;

--
-- Name: crops; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.crops ENABLE ROW LEVEL SECURITY;

--
-- Name: farms; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.farms ENABLE ROW LEVEL SECURITY;

--
-- Name: finance_transactions; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.finance_transactions ENABLE ROW LEVEL SECURITY;

--
-- Name: org_members; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.org_members ENABLE ROW LEVEL SECURITY;

--
-- Name: organizations; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;

--
-- Name: plots; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.plots ENABLE ROW LEVEL SECURITY;

--
-- Name: queries; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.queries ENABLE ROW LEVEL SECURITY;

--
-- Name: schedule_tasks; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.schedule_tasks ENABLE ROW LEVEL SECURITY;

--
-- Name: schedules; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.schedules ENABLE ROW LEVEL SECURITY;

--
-- Name: work_orders; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.work_orders ENABLE ROW LEVEL SECURITY;

--
-- PostgreSQL database dump complete
--

