/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     11.09.2020 1:02:28                           */
/*==============================================================*/


alter table Category_level
    drop foreign key FK_CATEGORY_CATEGORY__LEVELS;

alter table Category_level
    drop foreign key FK_CATEGORY_CATEGORY__CATEGORI;

alter table Chat_sessions
    drop foreign key FK_CHAT_SES_CHAT_IN_S_CHATS;

alter table Chat_sessions
    drop foreign key FK_CHAT_SES_PROFILE_I_PROFILES;

alter table Language_level
    drop foreign key FK_LANGUAGE_LANGUAGE__LANGUAGE;

alter table Language_level
    drop foreign key FK_LANGUAGE_LANGUAGE__LEVELS;

alter table Logs
    drop foreign key FK_LOGS_LOGGING_USERS;

alter table Messages
    drop foreign key FK_MESSAGES_CHAT_CONT_CHAT_SES;

alter table Messages
    drop foreign key FK_MESSAGES_TEXT_IN_M_Texts;

alter table Privileges_assigns
    drop foreign key FK_PREVILEG_PREVILEGE_PRIVILEG;

alter table Privileges_assigns
    drop foreign key FK_PREVILEG_ROLE_HAS__USER_ROL;

alter table Profile_categories
    drop foreign key FK_PROFILE__PROFILE_H_PROFILE_;

alter table Profile_categories
    drop foreign key FK_PROFILE__PROFILE_H_CATEGORY;

alter table Profile_description
    drop foreign key FK_PROFILE__DESCRIPTI_PROFILES;

alter table Profile_description
    drop foreign key FK_PROFILE__PROFILE_H_ETHNICIT;

alter table Profile_description
    drop foreign key FK_PROFILE__PROFILE_H_RELIGION;

alter table Profile_description
    drop foreign key FK_PROFILE__PROFILE_H_ZODIACS;

alter table Profile_languages
    drop foreign key FK_PROFILE__PROFILE_K_PROFILE_;

alter table Profile_languages
    drop foreign key FK_PROFILE__PROFILE_K_LANGUAGE;

alter table Roles_of_users
    drop foreign key FK_ROLES_OF_ROLE_ASSI_USER_ROL;

alter table Roles_of_users
    drop foreign key FK_ROLES_OF_USER_HAS__USERS;

alter table Tagging
    drop foreign key FK_TAGGING_TAGGING_Texts;

alter table Tagging
    drop foreign key FK_TAGGING_TAGGING2_TAGS;

alter table Visibility
    drop foreign key FK_VISIBILI_VISIBILIT_PROFILES;

alter table Visibility
    drop foreign key FK_VISIBILI_VISIBILIT_USERS;

drop table if exists Categories;


alter table Category_level
    drop foreign key FK_CATEGORY_CATEGORY__CATEGORI;

alter table Category_level
    drop foreign key FK_CATEGORY_CATEGORY__LEVELS;

drop table if exists Category_level;


alter table Chat_sessions
    drop foreign key FK_CHAT_SES_PROFILE_I_PROFILES;

alter table Chat_sessions
    drop foreign key FK_CHAT_SES_CHAT_IN_S_CHATS;

drop table if exists Chat_sessions;

drop table if exists Chats;

drop table if exists Ethnicities;


alter table Language_level
    drop foreign key FK_LANGUAGE_LANGUAGE__LEVELS;

alter table Language_level
    drop foreign key FK_LANGUAGE_LANGUAGE__LANGUAGE;

drop table if exists Language_level;

drop table if exists Languages;

drop table if exists Levels;


alter table Logs
    drop foreign key FK_LOGS_LOGGING_USERS;

drop table if exists Logs;


alter table Messages
    drop foreign key FK_MESSAGES_CHAT_CONT_CHAT_SES;

alter table Messages
    drop foreign key FK_MESSAGES_TEXT_IN_M_Texts;

drop table if exists Messages;


alter table Privileges_assigns
    drop foreign key FK_PREVILEG_PREVILEGE_PRIVILEG;

alter table Privileges_assigns
    drop foreign key FK_PREVILEG_ROLE_HAS__USER_ROL;

drop table if exists Privileges_assigns;

drop table if exists Privileges;


alter table Profile_categories
    drop foreign key FK_PROFILE__PROFILE_H_PROFILE_;

alter table Profile_categories
    drop foreign key FK_PROFILE__PROFILE_H_CATEGORY;

drop table if exists Profile_categories;


alter table Profile_description
    drop foreign key FK_PROFILE__DESCRIPTI_PROFILES;

alter table Profile_description
    drop foreign key FK_PROFILE__PROFILE_H_ZODIACS;

alter table Profile_description
    drop foreign key FK_PROFILE__PROFILE_H_ETHNICIT;

alter table Profile_description
    drop foreign key FK_PROFILE__PROFILE_H_RELIGION;

drop table if exists Profile_description;


alter table Profile_languages
    drop foreign key FK_PROFILE__PROFILE_K_PROFILE_;

alter table Profile_languages
    drop foreign key FK_PROFILE__PROFILE_K_LANGUAGE;

drop table if exists Profile_languages;

drop table if exists Profiles;

drop table if exists Religions;


alter table Roles_of_users
    drop foreign key FK_ROLES_OF_ROLE_ASSI_USER_ROL;

alter table Roles_of_users
    drop foreign key FK_ROLES_OF_USER_HAS__USERS;

drop table if exists Roles_of_users;


alter table Tagging
    drop foreign key FK_TAGGING_TAGGING2_TAGS;

alter table Tagging
    drop foreign key FK_TAGGING_TAGGING_Texts;

drop table if exists Tagging;

drop table if exists Tags;

drop table if exists Texts;

drop table if exists User_roles;

drop table if exists Users;


alter table Visibility
    drop foreign key FK_VISIBILI_VISIBILIT_USERS;

alter table Visibility
    drop foreign key FK_VISIBILI_VISIBILIT_PROFILES;

drop table if exists Visibility;

drop table if exists Zodiacs;

/*==============================================================*/
/* Table: Categories                                            */
/*==============================================================*/
create table Categories
(
    category_name varchar(190) not null comment '',
    primary key (category_name)
);

/*==============================================================*/
/* Table: Category_level                                        */
/*==============================================================*/
create table Category_level
(
    level_name    varchar(190) not null comment '',
    category_name varchar(190) not null comment '',
    primary key (level_name, category_name)
);

/*==============================================================*/
/* Table: Chat_sessions                                         */
/*==============================================================*/
create table Chat_sessions
(
    chat_id    binary(16)  not null comment '',
    profile_id varchar(20) not null comment '',
    primary key (chat_id, profile_id)
);

/*==============================================================*/
/* Table: Chats                                                 */
/*==============================================================*/
create table Chats
(
    chat_id binary(16) not null comment '',
    primary key (chat_id)
);

/*==============================================================*/
/* Table: Ethnicities                                           */
/*==============================================================*/
create table Ethnicities
(
    ethnicity_name varchar(190) not null comment '',
    primary key (ethnicity_name)
);

/*==============================================================*/
/* Table: Language_level                                        */
/*==============================================================*/
create table Language_level
(
    language   varchar(190) not null comment '',
    level_name varchar(190) not null comment '',
    primary key (language, level_name)
);

/*==============================================================*/
/* Table: Languages                                             */
/*==============================================================*/
create table Languages
(
    language varchar(190) not null comment '',
    primary key (language)
);

/*==============================================================*/
/* Table: Levels                                                */
/*==============================================================*/
create table Levels
(
    level_name varchar(190) not null comment '',
    primary key (level_name)
);

/*==============================================================*/
/* Table: Logs                                                  */
/*==============================================================*/
create table Logs
(
    log_id      binary(16)     not null comment '',
    login       varchar(190)   not null comment '',
    category    varchar(190)   not null comment '',
    message     varchar(10000) not null comment '',
    ip          varchar(20) comment '',
    create_time timestamp      not null comment '',
    primary key (log_id)
);

/*==============================================================*/
/* Table: Messages                                              */
/*==============================================================*/
create table Messages
(
    message_token binary(16)  not null comment '',
    chat_id       binary(16)  not null comment '',
    profile_id    varchar(20) not null comment '',
    send_time     timestamp   not null comment '',
    text_id       binary(16)  not null comment '',
    viewed        bool comment '',
    primary key (message_token)
);

/*==============================================================*/
/* Table: Privileges_assigns                                    */
/*==============================================================*/
create table Privileges_assigns
(
    user_role      varchar(190) not null comment '',
    privilege_name varchar(190) not null comment '',
    primary key (user_role, privilege_name)
);

/*==============================================================*/
/* Table: Privileges                                            */
/*==============================================================*/
create table Privileges
(
    privilege_name   varchar(190) not null comment '',
    privilege_status bool         not null comment '',
    primary key (privilege_name)
);

/*==============================================================*/
/* Table: Profile_categories                                    */
/*==============================================================*/
create table Profile_categories
(
    level_name    varchar(190) not null comment '',
    category_name varchar(190) not null comment '',
    profile_id    varchar(20)  not null comment '',
    primary key (level_name, category_name, profile_id)
);

/*==============================================================*/
/* Table: Profile_description                                   */
/*==============================================================*/
create table Profile_description
(
    profile_id               varchar(20) not null comment '',
    zodiac                   varchar(190) comment '',
    ethnicity_name           varchar(190) comment '',
    religion                 varchar(190) comment '',
    age                      tinyint comment '',
    city                     varchar(190) comment '',
    credits_to_open_letter   float comment '',
    description              varchar(10000) comment '',
    income                   varchar(190) comment '',
    last_online              varchar(190) comment '',
    looking_for_an_age_range varchar(190) comment '',
    name                     varchar(190) comment '',
    nickname                 varchar(190) comment '',
    occupation               varchar(190) comment '',
    rate                     float comment '',
    sex                      varchar(190) comment '',
    votes                    MEDIUMINT comment '',
    primary key (profile_id)
);

/*==============================================================*/
/* Table: Profile_languages                                     */
/*==============================================================*/
create table Profile_languages
(
    language   varchar(190) not null comment '',
    level_name varchar(190) not null comment '',
    profile_id varchar(20)  not null comment '',
    primary key (language, level_name, profile_id)
);

/*==============================================================*/
/* Table: Profiles                                              */
/*==============================================================*/
create table Profiles
(
    profile_id       varchar(20) not null comment '',
    profile_password varchar(190) comment '',
    available        bool comment '',
    can_receive      bool comment '',
    msg_limit        int comment '',
    profile_type     varchar(190) comment '',
    primary key (profile_id)
);

/*==============================================================*/
/* Table: Religions                                             */
/*==============================================================*/
create table Religions
(
    religion varchar(190) not null comment '',
    primary key (religion)
);

/*==============================================================*/
/* Table: Roles_of_users                                        */
/*==============================================================*/
create table Roles_of_users
(
    login     varchar(190) not null comment '',
    user_role varchar(190) not null comment '',
    primary key (login, user_role)
);

/*==============================================================*/
/* Table: Tagging                                               */
/*==============================================================*/
create table Tagging
(
    text_id binary(16)   not null comment '',
    tag     varchar(190) not null comment '',
    primary key (text_id, tag)
);

/*==============================================================*/
/* Table: Tags                                                  */
/*==============================================================*/
create table Tags
(
    tag varchar(190) not null comment '',
    primary key (tag)
);

/*==============================================================*/
/* Table: Texts                                                */
/*==============================================================*/
create table Texts
(
    text_id binary(16)     not null comment '',
    text    varchar(10000) not null comment '',
    primary key (text_id)
);

/*==============================================================*/
/* Table: User_roles                                            */
/*==============================================================*/
create table User_roles
(
    user_role varchar(190) not null comment '',
    primary key (user_role)
);

/*==============================================================*/
/* Table: Users                                                 */
/*==============================================================*/
create table Users
(
    login         varchar(190) not null comment '',
    user_password varchar(190) comment '',
    primary key (login)
);

/*==============================================================*/
/* Table: Visibility                                            */
/*==============================================================*/
create table Visibility
(
    profile_id varchar(20)  not null comment '',
    login      varchar(190) not null comment '',
    primary key (profile_id, login)
);

/*==============================================================*/
/* Table: Zodiacs                                               */
/*==============================================================*/
create table Zodiacs
(
    zodiac varchar(190) not null comment '',
    primary key (zodiac)
);

alter table Category_level
    add constraint FK_CATEGORY_CATEGORY__LEVELS foreign key (level_name)
        references Levels (level_name) on delete restrict on update restrict;

alter table Category_level
    add constraint FK_CATEGORY_CATEGORY__CATEGORI foreign key (category_name)
        references Categories (category_name) on delete restrict on update restrict;

alter table Chat_sessions
    add constraint FK_CHAT_SES_CHAT_IN_S_CHATS foreign key (chat_id)
        references Chats (chat_id) on delete restrict on update restrict;

alter table Chat_sessions
    add constraint FK_CHAT_SES_PROFILE_I_PROFILES foreign key (profile_id)
        references Profiles (profile_id) on delete restrict on update restrict;

alter table Language_level
    add constraint FK_LANGUAGE_LANGUAGE__LANGUAGE foreign key (language)
        references Languages (language) on delete restrict on update restrict;

alter table Language_level
    add constraint FK_LANGUAGE_LANGUAGE__LEVELS foreign key (level_name)
        references Levels (level_name) on delete restrict on update restrict;

alter table Logs
    add constraint FK_LOGS_LOGGING_USERS foreign key (login)
        references Users (login) on delete restrict on update restrict;

alter table Messages
    add constraint FK_MESSAGES_CHAT_CONT_CHAT_SES foreign key (chat_id, profile_id)
        references Chat_sessions (chat_id, profile_id) on delete restrict on update restrict;

alter table Messages
    add constraint FK_MESSAGES_TEXT_IN_M_Texts foreign key (text_id)
        references Texts (text_id) on delete restrict on update restrict;

alter table Privileges_assigns
    add constraint FK_PREVILEG_PREVILEGE_PRIVILEG foreign key (privilege_name)
        references Privileges (privilege_name) on delete restrict on update restrict;

alter table Privileges_assigns
    add constraint FK_PREVILEG_ROLE_HAS__USER_ROL foreign key (user_role)
        references User_roles (user_role) on delete restrict on update restrict;

alter table Profile_categories
    add constraint FK_PROFILE__PROFILE_H_PROFILE_ foreign key (profile_id)
        references Profile_description (profile_id) on delete restrict on update restrict;

alter table Profile_categories
    add constraint FK_PROFILE__PROFILE_H_CATEGORY foreign key (level_name, category_name)
        references Category_level (level_name, category_name) on delete restrict on update restrict;

alter table Profile_description
    add constraint FK_PROFILE__DESCRIPTI_PROFILES foreign key (profile_id)
        references Profiles (profile_id) on delete restrict on update restrict;

alter table Profile_description
    add constraint FK_PROFILE__PROFILE_H_ETHNICIT foreign key (ethnicity_name)
        references Ethnicities (ethnicity_name) on delete restrict on update restrict;

alter table Profile_description
    add constraint FK_PROFILE__PROFILE_H_RELIGION foreign key (religion)
        references Religions (religion) on delete restrict on update restrict;

alter table Profile_description
    add constraint FK_PROFILE__PROFILE_H_ZODIACS foreign key (zodiac)
        references Zodiacs (zodiac) on delete restrict on update restrict;

alter table Profile_languages
    add constraint FK_PROFILE__PROFILE_K_PROFILE_ foreign key (profile_id)
        references Profile_description (profile_id) on delete restrict on update restrict;

alter table Profile_languages
    add constraint FK_PROFILE__PROFILE_K_LANGUAGE foreign key (language, level_name)
        references Language_level (language, level_name) on delete restrict on update restrict;

alter table Roles_of_users
    add constraint FK_ROLES_OF_ROLE_ASSI_USER_ROL foreign key (user_role)
        references User_roles (user_role) on delete restrict on update restrict;

alter table Roles_of_users
    add constraint FK_ROLES_OF_USER_HAS__USERS foreign key (login)
        references Users (login) on delete restrict on update restrict;

alter table Tagging
    add constraint FK_TAGGING_TAGGING_Texts foreign key (text_id)
        references Texts (text_id) on delete restrict on update restrict;

alter table Tagging
    add constraint FK_TAGGING_TAGGING2_TAGS foreign key (tag)
        references Tags (tag) on delete restrict on update restrict;

alter table Visibility
    add constraint FK_VISIBILI_VISIBILIT_PROFILES foreign key (profile_id)
        references Profiles (profile_id) on delete restrict on update restrict;

alter table Visibility
    add constraint FK_VISIBILI_VISIBILIT_USERS foreign key (login)
        references Users (login) on delete restrict on update restrict;

