CREATE TABLE course_completion_events (
	event_id serial4 NOT NULL,
	external_id varchar(100) NOT NULL,
	user_id varchar(100) NULL,
	user_email varchar(150) NULL,
	course_id varchar(100) NOT NULL,
	course_title varchar(255) NOT NULL,
	event_timestamp timestamp NOT NULL,
	organisation_id int4 NOT NULL,
	profession_id int4 NOT NULL,
	grade_id int4 NULL,
	grade_name varchar(100) NULL,
	profession_name varchar(255) NULL,
	organisation_name varchar(255) NULL
)
PARTITION BY RANGE (event_timestamp);
