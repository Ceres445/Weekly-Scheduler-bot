--
-- PostgreSQL database dump
--

-- Dumped from database version 13.1
-- Dumped by pg_dump version 13.1

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
-- Name: time_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.time_data (
    day integer,
    "time" character varying,
    subject character varying,
    attendees character varying,
    permanant boolean DEFAULT true,
    pid integer NOT NULL,
    switch integer DEFAULT 0
);


ALTER TABLE public.time_data OWNER TO postgres;

--
-- Name: time_data_pid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.time_data_pid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.time_data_pid_seq OWNER TO postgres;

--
-- Name: time_data_pid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.time_data_pid_seq OWNED BY public.time_data.pid;


--
-- Name: time_data pid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.time_data ALTER COLUMN pid SET DEFAULT nextval('public.time_data_pid_seq'::regclass);


--
-- Data for Name: time_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.time_data (day, "time", subject, attendees, permanant, pid, switch) FROM stdin;
\.


--
-- Name: time_data_pid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.time_data_pid_seq', 22, true);


--
-- Name: time_data time_data_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.time_data
    ADD CONSTRAINT time_data_pk PRIMARY KEY (pid);


--
-- PostgreSQL database dump complete
--

