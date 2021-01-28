--
-- PostgreSQL database dump
--

-- Dumped from database version 12.5 (Ubuntu 12.5-1.pgdg16.04+1)
-- Dumped by pg_dump version 12.1

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: time_data; Type: TABLE; Schema: public; Owner: nejunesztxrqdw
--

CREATE TABLE "public"."time_data" (
    "day" integer,
    "time" character varying,
    "subject" character varying,
    "attendees" character varying,
    "permanant" boolean DEFAULT true
);


ALTER TABLE public.time_data OWNER TO postgres;

--
-- Data for Name: time_data; Type: TABLE DATA; Schema: public; Owner: nejunesztxrqdw
--

COPY "public"."time_data" ("day", "time", "subject", "attendees", "permanant") FROM stdin;
5	17:30	bio_	crp	t
1	12:45	chem	int	t
1	08:45	comp	int	t
2	16:00	comp	int	t
4	16:00	comp	int	t
3	08:45	comp	int	t
6	10:30	chem	crp	t
5	09:00	bio_	int	t
6	14:30	math	crp	t
1	15:00	eng_	int	t
3	15:00	eng_	int	t
0	09:00	math	int	t
0	11:15	bio_	int	t
1	10:00	phy_	int	t
2	13:30	math	int	t
2	11:00	bio_	int	t
3	10:15	chem	int	t
3	12:45	phy_	int	t
4	11:00	chem	int	t
4	13:30	math	int	t
4	17:30	phy_	crp	t
5	11:15	phy_	int	t
\.


--
-- PostgreSQL database dump complete
--

