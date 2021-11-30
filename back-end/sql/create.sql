drop table if exists candidates;
drop table if exists applies_for;
drop table if exists votes_for;
drop table if exists applicants;
drop table if exists voters;
drop table if exists nitc_students;
drop table if exists admins;
drop table if exists users;
drop table if exists posts;

create table users(
       id text primary key,
       roll_no text,
       name text not null,
       email text unique not null,
       profile_pic text not null,
       admin boolean not null default false
);

create table admins(
       admin_id serial primary key,
       name text not null,
       phone_no text unique not null,
       email text unique not null
);

create table nitc_students(
       roll_no text primary key,
       name text not null,
       phone_no text unique not null,
       nitc_email text unique not null,
       eligibility_status boolean not null default true,
       admin_id int default null references admins(admin_id) on delete set null
);

create table voters(
       roll_no text primary key references nitc_students(roll_no) on delete cascade,
       voting_status boolean not null default false
);

create table applicants(
       application_no serial primary key,
       position text not null,
       cgpa float not null,
       application_status text not null,
       admin_id int default null references admins(admin_id) on delete set null
);

create table candidates(
       application_no int primary key references applicants(application_no) on delete cascade,
       votes int default 0
);

create table votes_for(
       roll_no text references voters(roll_no) on delete cascade,
       application_no int references applicants(application_no) on delete cascade,
       PRIMARY KEY (roll_no, application_no)
);

create table applies_for(
       roll_no text references voters(roll_no) on delete cascade,
       application_no int primary key references applicants(application_no) on delete cascade
);

create table posts(
       position text primary key
);