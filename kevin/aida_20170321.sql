/* Drop Tables */

DROP TABLE IF EXISTS allowed_users;
DROP TABLE IF EXISTS exchanges;
DROP TABLE IF EXISTS exchange_type;
DROP TABLE IF EXISTS group_roles;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS global_role_types;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS tasks_schedule;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS group_role_types;
DROP TABLE IF EXISTS task_type;




/* Create Tables */

CREATE TABLE allowed_users
(
	allowed_user_id serial NOT NULL,
	user_id int NOT NULL,
	task_schedule_id int NOT NULL,
	PRIMARY KEY (allowed_user_id)
) WITHOUT OIDS;


CREATE TABLE exchanges
(
	exchange_id serial NOT NULL,
	task_subnode_id int,
	start_timestamp timestamp with time zone,
	exchange_context_obj text,
	is_complete boolean,
	was_successful boolean,
	created_date timestamp with time zone DEFAULT now(),
	updated_date timestamp with time zone DEFAULT now(),
	exchange_type_id int NOT NULL,
	task_id int NOT NULL,
	PRIMARY KEY (exchange_id)
) WITHOUT OIDS;


CREATE TABLE exchange_type
(
	exchange_type_id serial NOT NULL,
	label text,
	description text,
	exchange_handler text,
	handler_url text,
	PRIMARY KEY (exchange_type_id)
) WITHOUT OIDS;


CREATE TABLE global_role_types
(
	global_role_type_id serial NOT NULL,
	label text,
	description text,
	PRIMARY KEY (global_role_type_id)
) WITHOUT OIDS;


CREATE TABLE groups
(
	group_id serial NOT NULL,
	label text,
	description text,
	group_context_object text,
	is_Active boolean,
	created_date timestamp with time zone DEFAULT now() NOT NULL,
	updated_date timestamp with time zone DEFAULT now(),
	PRIMARY KEY (group_id)
) WITHOUT OIDS;


CREATE TABLE group_roles
(
	group_roles_id serial NOT NULL,
	created_date timestamp with time zone,
	updated_date timestamp with time zone,
	user_id int NOT NULL,
	group_id int NOT NULL,
	group_role_type_id int NOT NULL,
	PRIMARY KEY (group_roles_id)
) WITHOUT OIDS;


CREATE TABLE group_role_types
(
	group_role_type_id serial NOT NULL,
	label text,
	description text,
	PRIMARY KEY (group_role_type_id)
) WITHOUT OIDS;


CREATE TABLE tasks
(
	task_id serial NOT NULL,
	task_context_obj text,
	is_complete boolean,
	was_successful boolean,
	assigned_caregiver_id int,
	outcomes_obj text,
	outcomes_obj_id text,
	created_date timestamp with time zone DEFAULT now(),
	updated_date timestamp with time zone DEFAULT now(),
	task_schedule_id int NOT NULL,
	Notes text,
	PRIMARY KEY (task_id)
) WITHOUT OIDS;


CREATE TABLE tasks_schedule
(
	task_schedule_id serial NOT NULL,
	task_schedule_time time with time zone,
	start_Date date,
	end_Date date,
	frequency text,
	type text,
	status text,
	timezone text,
	start_date_string text,
	end_date_string text,
	task_Name text,
	days text,
	fullfillment_Type text,
	created_date timestamp with time zone,
	updated_date timestamp with time zone,
	group_id int NOT NULL,
	task_type_id int NOT NULL,
	PRIMARY KEY (task_schedule_id)
) WITHOUT OIDS;


CREATE TABLE task_type
(
	task_type_id serial NOT NULL,
	label text,
	description text,
	PRIMARY KEY (task_type_id)
) WITHOUT OIDS;


CREATE TABLE users
(
	user_id serial NOT NULL,
	username text,
	login_type text,
	hashed_password text,
	firstname text,
	lastname text,
	email text,
	mobile_number text,
	birth_Date date,
	is_female boolean,
	user_context_object text,
	is_Active boolean,
	created_date timestamp with time zone,
	updated_date timestamp with time zone,
	global_role_type_id int NOT NULL,
	PRIMARY KEY (user_id)
) WITHOUT OIDS;



/* Create Foreign Keys */

ALTER TABLE exchanges
	ADD FOREIGN KEY (exchange_type_id)
	REFERENCES exchange_type (exchange_type_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE users
	ADD FOREIGN KEY (global_role_type_id)
	REFERENCES global_role_types (global_role_type_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE group_roles
	ADD FOREIGN KEY (group_id)
	REFERENCES groups (group_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE tasks_schedule
	ADD FOREIGN KEY (group_id)
	REFERENCES groups (group_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE group_roles
	ADD FOREIGN KEY (group_role_type_id)
	REFERENCES group_role_types (group_role_type_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE exchanges
	ADD FOREIGN KEY (task_id)
	REFERENCES tasks (task_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE allowed_users
	ADD FOREIGN KEY (task_schedule_id)
	REFERENCES tasks_schedule (task_schedule_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;

ALTER TABLE allowed_users
	ADD FOREIGN KEY (user_id)
	REFERENCES users (user_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;

ALTER TABLE tasks
	ADD FOREIGN KEY (task_schedule_id)
	REFERENCES tasks_schedule (task_schedule_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;

ALTER TABLE tasks
	ADD FOREIGN KEY (assigned_caregiver_id)
	REFERENCES users (user_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;

ALTER TABLE tasks_schedule
	ADD FOREIGN KEY (task_type_id)
	REFERENCES task_type (task_type_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;


ALTER TABLE group_roles
	ADD FOREIGN KEY (user_id)
	REFERENCES users (user_id)
	ON UPDATE RESTRICT
	ON DELETE RESTRICT
;

insert into group_role_types(label,description) values ('Patient','Everyone else is helping this person feel supported.');
insert into group_role_types(label,description) values ('Primary caregiver','This person is the lead, the administrator, the primer mover in any given care group.');
insert into group_role_types(label,description) values ('Other family member','Another family member who helps with caregiving.');

