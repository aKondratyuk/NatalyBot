create table if not exists Categories
(
    category_name varchar(190) not null
        primary key
)
    charset = utf8mb4;

create table if not exists Chats
(
    chat_id binary(16) not null
        primary key
)
    charset = utf8mb4;

create table if not exists Countries
(
    country varchar(190) default '' not null
        primary key
)
    charset = utf8mb4;

create table if not exists Email_info
(
    email_address     varchar(190) default '' not null
        primary key,
    email_port        int                     null,
    email_host        varchar(190)            null,
    email_password    varchar(190)            null,
    email_subject     varchar(1000)           null,
    email_text        varchar(10000)          null,
    email_description varchar(190)            null
)
    charset = utf8mb4;

create table if not exists Ethnicities
(
    ethnicity_name varchar(190) not null
        primary key
)
    charset = utf8mb4;

create table if not exists Invites
(
    invite_id   binary(16)                          not null
        primary key,
    create_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP
)
    charset = utf8mb4;

create table if not exists Languages
(
    language varchar(190) not null
        primary key
)
    charset = utf8mb4;

create table if not exists Levels
(
    level_name varchar(190) not null
        primary key
)
    charset = utf8mb4;

create table if not exists Category_level
(
    level_name    varchar(190) not null,
    category_name varchar(190) not null,
    primary key (level_name, category_name),
    constraint FK_CATEGORY_CATEGORY__CATEGORI
        foreign key (category_name) references Categories (category_name),
    constraint FK_CATEGORY_CATEGORY__LEVELS
        foreign key (level_name) references Levels (level_name)
)
    charset = utf8mb4;

create table if not exists Privileges
(
    privilege_name varchar(190) not null
        primary key
)
    charset = utf8mb4;

create table if not exists Profiles
(
    profile_id       varchar(20)            not null
        primary key,
    profile_password varchar(190)           null,
    available        tinyint(1) default 1   null,
    can_receive      tinyint(1) default 1   null,
    msg_limit        int        default 999 null,
    profile_type     varchar(190)           null,
    max_age_delta    int(2)     default 10  null
)
    charset = utf8mb4;

create table if not exists Chat_sessions
(
    chat_id       binary(16)   not null,
    profile_id    varchar(20)  not null,
    email_address varchar(190) null,
    primary key (chat_id, profile_id),
    constraint Chat_sessions_Email_info_email_address_fk
        foreign key (email_address) references Email_info (email_address),
    constraint FK_CHAT_SES_CHAT_IN_S_CHATS
        foreign key (chat_id) references Chats (chat_id),
    constraint FK_CHAT_SES_PROFILE_I_PROFILES
        foreign key (profile_id) references Profiles (profile_id)
)
    charset = utf8mb4;

create table if not exists Profile_categories
(
    level_name    varchar(190) not null,
    category_name varchar(190) not null,
    profile_id    varchar(20)  not null,
    primary key (level_name, category_name, profile_id),
    constraint FK_PROFILE__PROFILE_H_CATEGORY
        foreign key (level_name, category_name) references Category_level (level_name, category_name),
    constraint FK_PROFILE__PROFILE_H_PROFILE_
        foreign key (profile_id) references Profiles (profile_id)
)
    charset = utf8mb4;

create table if not exists Profile_languages
(
    language   varchar(190) not null,
    level_name varchar(190) not null,
    profile_id varchar(20)  not null,
    primary key (language, level_name, profile_id),
    constraint FK_PROFILE__PROFILE_K_LANGUAGE
        foreign key (level_name) references Levels (level_name),
    constraint FK_PROFILE__PROFILE_K_PROFILE_
        foreign key (profile_id) references Profiles (profile_id),
    constraint Profile_languages_Languages_language_fk
        foreign key (language) references Languages (language)
)
    charset = utf8mb4;

create table if not exists Religions
(
    religion varchar(190) not null
        primary key
)
    charset = utf8mb4;

create table if not exists Tags
(
    tag       varchar(190)         not null
        primary key,
    forbidden tinyint(1) default 0 null
)
    charset = utf8mb4;

create table if not exists Texts
(
    text_id binary(16)     not null
        primary key,
    text    varchar(10000) not null
);

create table if not exists Message_anchors
(
    profile_id varchar(20) default '' not null,
    text_id    binary(16)             not null,
    primary key (profile_id, text_id),
    constraint Message_anchors_Profiles_profile_id_fk
        foreign key (profile_id) references Profiles (profile_id),
    constraint Message_anchors_Texts_text_id_fk
        foreign key (text_id) references Texts (text_id)
)
    charset = utf8mb4;

create table if not exists Message_templates
(
    profile_id  varchar(20) default '' not null,
    text_id     binary(16)             not null,
    text_number int         default 1  null,
    primary key (profile_id, text_id),
    constraint Message_templates_Profiles_profile_id_fk
        foreign key (profile_id) references Profiles (profile_id),
    constraint Message_templates_Texts_text_id_fk
        foreign key (text_id) references Texts (text_id)
)
    charset = utf8mb4;

create table if not exists Messages
(
    message_token binary(16)                           not null
        primary key,
    chat_id       binary(16)                           not null,
    profile_id    varchar(20)                          not null,
    send_time     timestamp  default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    text_id       binary(16)                           not null,
    viewed        tinyint(1)                           null,
    delay         tinyint(1) default 0                 null,
    constraint FK_MESSAGES_CHAT_CONT_CHAT_SES
        foreign key (chat_id, profile_id) references Chat_sessions (chat_id, profile_id),
    constraint FK_MESSAGES_TEXT_IN_M_Texts
        foreign key (text_id) references Texts (text_id)
)
    charset = utf8mb4;

create table if not exists Tagging
(
    text_id binary(16)   not null,
    tag     varchar(190) not null,
    primary key (text_id, tag),
    constraint FK_TAGGING_TAGGING2_TAGS
        foreign key (tag) references Tags (tag),
    constraint FK_TAGGING_TAGGING_Texts
        foreign key (text_id) references Texts (text_id)
)
    charset = utf8mb4;

create table if not exists Used_anchors
(
    profile_id varchar(20) default '' not null,
    text_id    binary(16)             not null,
    primary key (profile_id, text_id),
    constraint Used_anchors_Message_anchors_text_id_fk
        foreign key (text_id) references Message_anchors (text_id),
    constraint Used_anchors_Profiles_profile_id_fk
        foreign key (profile_id) references Profiles (profile_id)
)
    charset = utf8mb4;

create table if not exists User_roles
(
    user_role varchar(190) not null
        primary key
)
    charset = utf8mb4;

create table if not exists Privileges_assigns
(
    user_role        varchar(190)         not null,
    privilege_name   varchar(190)         not null,
    privilege_status tinyint(1) default 0 null,
    primary key (user_role, privilege_name),
    constraint FK_PREVILEG_PREVILEGE_PRIVILEG
        foreign key (privilege_name) references Privileges (privilege_name),
    constraint FK_PREVILEG_ROLE_HAS__USER_ROL
        foreign key (user_role) references User_roles (user_role)
)
    charset = utf8mb4;

create table if not exists Users
(
    login         varchar(190) not null
        primary key,
    user_password varchar(190) null
)
    charset = utf8mb4;

create table if not exists Logs
(
    log_id      binary(16)                          not null
        primary key,
    login       varchar(190)                        not null,
    category    varchar(190)                        not null,
    message     varchar(10000)                      not null,
    ip          varchar(20)                         null,
    create_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    constraint FK_LOGS_LOGGING_USERS
        foreign key (login) references Users (login)
)
    charset = utf8mb4;

create table if not exists Roles_of_users
(
    login     varchar(190) not null,
    user_role varchar(190) not null,
    primary key (login, user_role),
    constraint FK_ROLES_OF_ROLE_ASSI_USER_ROL
        foreign key (user_role) references User_roles (user_role),
    constraint FK_ROLES_OF_USER_HAS__USERS
        foreign key (login) references Users (login)
)
    charset = utf8mb4;

create table if not exists Sent_invites
(
    invite_id binary(16)   not null,
    login     varchar(190) not null,
    primary key (invite_id, login),
    constraint FK_SENT_I_INVITE_HA_INVITES
        foreign key (invite_id) references Invites (invite_id),
    constraint FK_SENT_I_USER_HAS__USERS
        foreign key (login) references Users (login)
)
    charset = utf8mb4;

create table if not exists Visibility
(
    profile_id varchar(20)  not null,
    login      varchar(190) not null,
    primary key (profile_id, login),
    constraint FK_VISIBILI_VISIBILIT_PROFILES
        foreign key (profile_id) references Profiles (profile_id),
    constraint FK_VISIBILI_VISIBILIT_USERS
        foreign key (login) references Users (login)
)
    charset = utf8mb4;

create table if not exists Zodiacs
(
    zodiac varchar(190) not null
        primary key
)
    charset = utf8mb4;

create table if not exists Profile_description
(
    profile_id               varchar(20)    not null
        primary key,
    zodiac                   varchar(190)   null,
    ethnicity_name           varchar(190)   null,
    religion                 varchar(190)   null,
    country                  varchar(190)   null,
    age                      tinyint        null,
    city                     varchar(190)   null,
    credits_to_open_letter   float          null,
    description              varchar(10000) null,
    income                   varchar(190)   null,
    last_online              varchar(190)   null,
    looking_for_an_age_range varchar(190)   null,
    name                     varchar(190)   null,
    nickname                 varchar(190)   null,
    occupation               varchar(190)   null,
    rate                     float          null,
    sex                      varchar(190)   null,
    votes                    mediumint      null,
    constraint FK_PROFILE__DESCRIPTI_PROFILES
        foreign key (profile_id) references Profiles (profile_id),
    constraint FK_PROFILE__PROFILE_H_ETHNICIT
        foreign key (ethnicity_name) references Ethnicities (ethnicity_name),
    constraint FK_PROFILE__PROFILE_H_RELIGION
        foreign key (religion) references Religions (religion),
    constraint FK_PROFILE__PROFILE_H_ZODIACS
        foreign key (zodiac) references Zodiacs (zodiac),
    constraint Profile_description_Countries_country_name_fk
        foreign key (country) references Countries (country)
)
    charset = utf8mb4;


