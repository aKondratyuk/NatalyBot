CREATE_TABLES_QUERY = """
create table if not exists "Account"
(
	account_id varchar(10) not null
		constraint account_pk
			primary key,
	account_password varchar(50) not null
);

create table if not exists "Dialogue"
(
	dialogue_id varchar(10) not null
		constraint dialogue_pk
			primary key,
	sender_id varchar(10) not null,
	send_time timestamp not null,
	viewed boolean not null,
	sender_message varchar(50000),
	receiver_id varchar(10) not null
		constraint "DialogueFK"
			references "Account"
				on delete set null
);
"""

DROP_TABLES_QUERY = """
drop table if exists "Dialogue";
drop table if exists "Account";
"""
