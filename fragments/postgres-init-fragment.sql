-- Create search_local_land_charges database
CREATE DATABASE search_local_land_charges;

--Create user for search_local_land_charges DB
CREATE ROLE search_local_land_charges_user with LOGIN password 'search_local_land_charges_password';

\c search_local_land_charges;
CREATE EXTENSION postgis;