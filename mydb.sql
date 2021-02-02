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
    "permanant" boolean DEFAULT true,
    "pid" integer NOT NULL,
    "switch" integer DEFAULT 0
);


ALTER TABLE public.time_data OWNER TO postgres;

--
-- Name: time_data_pid_seq; Type: SEQUENCE; Schema: public; Owner: nejunesztxrqdw
--

CREATE SEQUENCE "public"."time_data_pid_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.time_data_pid_seq OWNER TO postgres;

--
-- Name: time_data_pid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nejunesztxrqdw
--

ALTER SEQUENCE "public"."time_data_pid_seq" OWNED BY "public"."time_data"."pid";


--
-- Name: time_data pid; Type: DEFAULT; Schema: public; Owner: nejunesztxrqdw
--

ALTER TABLE ONLY "public"."time_data" ALTER COLUMN "pid" SET DEFAULT "nextval"('"public"."time_data_pid_seq"'::"regclass");


--
-- Data for Name: time_data; Type: TABLE DATA; Schema: public; Owner: nejunesztxrqdw
--

COPY "public"."time_data" ("day", "time", "subject", "attendees", "permanant", "pid", "switch") FROM stdin;
5	17:30	bio_	crp	t	1	0
1	12:45	chem	int	t	2	0
1	08:45	comp	int	t	3	0
2	16:00	comp	int	t	4	0
4	16:00	comp	int	t	5	0
3	08:45	comp	int	t	6	0
6	10:30	chem	crp	t	7	0
5	09:00	bio_	int	t	8	0
6	14:30	math	crp	t	9	0
1	15:00	eng_	int	t	10	0
3	15:00	eng_	int	t	11	0
0	09:00	math	int	t	12	0
0	11:15	bio_	int	t	13	0
1	10:00	phy_	int	t	14	0
2	13:30	math	int	t	15	0
2	11:00	bio_	int	t	16	0
3	10:15	chem	int	t	17	0
3	12:45	phy_	int	t	18	0
4	11:00	chem	int	t	19	0
4	13:30	math	int	t	20	0
4	17:30	phy_	crp	t	21	0
5	11:15	phy_	int	t	22	0
\.


--
-- Name: time_data_pid_seq; Type: SEQUENCE SET; Schema: public; Owner: nejunesztxrqdw
--

SELECT pg_catalog.setval('"public"."time_data_pid_seq"', 22, true);


--
-- Name: time_data time_data_pk; Type: CONSTRAINT; Schema: public; Owner: nejunesztxrqdw
--

ALTER TABLE ONLY "public"."time_data"
    ADD CONSTRAINT "time_data_pk" PRIMARY KEY ("pid");


--
-- PostgreSQL database dump complete
--

