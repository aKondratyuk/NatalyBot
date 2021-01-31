CREATE DATABASE nataly_schema;
use nataly_schema;

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


INSERT INTO nataly_schema.Categories (category_name)
VALUES ('body_type');
INSERT INTO nataly_schema.Categories (category_name)
VALUES ('children');
INSERT INTO nataly_schema.Categories (category_name)
VALUES ('drinker');
INSERT INTO nataly_schema.Categories (category_name)
VALUES ('education');
INSERT INTO nataly_schema.Categories (category_name)
VALUES ('height');
INSERT INTO nataly_schema.Categories (category_name)
VALUES ('income');
INSERT INTO nataly_schema.Categories (category_name)
VALUES ('looking_for_a_body_type');
INSERT INTO nataly_schema.Categories (category_name)
VALUES ('looking_for_a_height');
INSERT INTO nataly_schema.Categories (category_name)
VALUES ('martial_status');
INSERT INTO nataly_schema.Categories (category_name)
VALUES ('relationship');
INSERT INTO nataly_schema.Categories (category_name)
VALUES ('smoker');
INSERT INTO nataly_schema.Categories (category_name)
VALUES ('want_children');
INSERT INTO nataly_schema.Categories (category_name)
VALUES ('where_children');

INSERT INTO nataly_schema.Countries (country)
VALUES ('American Samoa');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Andorra');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Anguilla');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Antarctica');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Antigua and Barbuda');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Argentina');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Armenia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Aruba');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Australia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Austria');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Azerbaijan');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Bahamas');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Bahrain');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Barbados');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Belarus');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Belgium');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Belize');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Benin');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Bermuda');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Bhutan');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Bolivia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Bosnia/Herzegowina');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Botswana');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Bouvet Island');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Brazil');
INSERT INTO nataly_schema.Countries (country)
VALUES ('British Ind. Ocean');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Brunei Darussalam');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Bulgaria');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Burkina Faso');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Cameroon');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Canada');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Cape Verde');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Cayman Islands');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Chad');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Chile');
INSERT INTO nataly_schema.Countries (country)
VALUES ('China');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Christmas Island');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Cocoa (Keeling) Is.');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Colombia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Comoros');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Costa Rica');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Cote Divoire');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Croatia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Cuba');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Cyprus');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Czech Republic');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Denmark');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Djibouti');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Dominica');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Dominican Republic');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Ecuador');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Egypt');
INSERT INTO nataly_schema.Countries (country)
VALUES ('El Salvador');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Equatorial Guinea');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Estonia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Falkland Islands');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Faroe Islands');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Fiji');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Finland');
INSERT INTO nataly_schema.Countries (country)
VALUES ('France');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Gabon');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Gambia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Georgia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Germany');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Ghana');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Gibraltar');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Greece');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Greenland');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Grenada');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Guadeloupe');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Guam');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Guatemala');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Guinea');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Guinea-Bissau');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Guyana');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Honduras');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Hong Kong');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Hungary');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Iceland');
INSERT INTO nataly_schema.Countries (country)
VALUES ('India');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Iran');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Ireland');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Israel');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Italy');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Jamaica');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Japan');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Jordan');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Kazakhstan');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Kenya');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Kiribati');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Korea');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Kuwait');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Kyrgyzstan');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Latvia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Lebanon');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Lesotho');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Liechtenstein');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Lithuania');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Luxembourg');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Macau');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Macedonia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Madagascar');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Malawi');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Malaysia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Maldives');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Mali');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Malta');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Marshall Islands');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Martinique');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Mauritania');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Mauritius');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Mayotte');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Mexico');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Micronesia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Moldova');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Monaco');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Montenegro');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Montserrat');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Morocco');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Mozambique');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Namibia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Nepal');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Netherlands');
INSERT INTO nataly_schema.Countries (country)
VALUES ('New Caledonia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('New Zealand');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Nicaragua');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Niger');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Niue');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Norfolk Island');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Norway');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Oman');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Pakistan');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Palau');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Panama');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Papua New Guinea');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Paraguay');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Peru');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Philippines');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Pitcairn');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Poland');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Portugal');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Puerto Rico');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Qatar');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Reunion');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Romania');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Russia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Saint Lucia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Samoa');
INSERT INTO nataly_schema.Countries (country)
VALUES ('San Marino');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Saudi Arabia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Senegal');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Serbia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Seychelles');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Singapore');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Slovakia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Slovenia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Solomon Islands');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Somalia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('South Africa');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Spain');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Sri Lanka');
INSERT INTO nataly_schema.Countries (country)
VALUES ('St. Helena');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Swaziland');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Sweden');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Switzerland');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Taiwan');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Tajikistan');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Tanzania');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Thailand');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Togo');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Tokelau');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Tonga');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Trinidad and Tobago');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Tunisia');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Turkey');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Turkmenistan');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Tuvalu');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Uganda');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Ukraine');
INSERT INTO nataly_schema.Countries (country)
VALUES ('United Arab Emirates');
INSERT INTO nataly_schema.Countries (country)
VALUES ('United Kingdom');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Uruguay');
INSERT INTO nataly_schema.Countries (country)
VALUES ('USA');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Uzbekistan');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Vanuatu');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Vatican');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Venezuela');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Viet Nam');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Virgin Islands');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Western Sahara');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Yemen');
INSERT INTO nataly_schema.Countries (country)
VALUES ('Zambia');

INSERT INTO nataly_schema.Email_info (email_address, email_port, email_host,
                                      email_password, email_subject,
                                      email_text, email_description)
VALUES ('ladyjuly@a2.kh.ua', 587, 'euhost01.twinservers.net', 'iX}srvOfUH!p',
        'Инструкция для регистрации в системе NatalyBot',
        'Вам выслано приглашение на пользованием сервисом. Перейдите по ссылке и завершите регистрацию: https://natalybot.herokuapp.com/signup',
        'default_register');

INSERT INTO nataly_schema.Ethnicities (ethnicity_name)
VALUES ('African');
INSERT INTO nataly_schema.Ethnicities (ethnicity_name)
VALUES ('African American');
INSERT INTO nataly_schema.Ethnicities (ethnicity_name)
VALUES ('Asian');
INSERT INTO nataly_schema.Ethnicities (ethnicity_name)
VALUES ('Caucasian');
INSERT INTO nataly_schema.Ethnicities (ethnicity_name)
VALUES ('East Indian');
INSERT INTO nataly_schema.Ethnicities (ethnicity_name)
VALUES ('Hispanic');
INSERT INTO nataly_schema.Ethnicities (ethnicity_name)
VALUES ('I prefer not to say');
INSERT INTO nataly_schema.Ethnicities (ethnicity_name)
VALUES ('Indian');
INSERT INTO nataly_schema.Ethnicities (ethnicity_name)
VALUES ('Latino');
INSERT INTO nataly_schema.Ethnicities (ethnicity_name)
VALUES ('Mediterranean');
INSERT INTO nataly_schema.Ethnicities (ethnicity_name)
VALUES ('Middle Eastern');
INSERT INTO nataly_schema.Ethnicities (ethnicity_name)
VALUES ('Mixed');

INSERT INTO nataly_schema.Languages (language)
VALUES ('');
INSERT INTO nataly_schema.Languages (language)
VALUES ('---');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Afrikaans');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Arabic');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Belorussian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Bulgarian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Burmese');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Cantonese');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Croatian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Czech');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Danish');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Dutch');
INSERT INTO nataly_schema.Languages (language)
VALUES ('English');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Esperanto');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Estonian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Finnish');
INSERT INTO nataly_schema.Languages (language)
VALUES ('French');
INSERT INTO nataly_schema.Languages (language)
VALUES ('German');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Greek');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Gujrati');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Hebrew');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Hindi');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Hungarian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Icelandic');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Indian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Indonesian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Italian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Japanese');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Korean');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Latvian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Lithuanian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Malay');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Mandarin');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Marathi');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Moldovian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Nepalese');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Norwegian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Not specified');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Persian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Polish');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Portuguese');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Punjabi');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Romanian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Russian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Serbian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Spanish');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Swedish');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Tagalog');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Taiwanese');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Tamil');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Telugu');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Thai');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Tongan');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Turkish');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Ukrainian');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Urdu');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Vietnamese');
INSERT INTO nataly_schema.Languages (language)
VALUES ('Visayan');

INSERT INTO nataly_schema.Levels (level_name)
VALUES ('');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('$10,000-$30,000/year');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('$10,000/year and less');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('$30,000-$50,000/year');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('$50,000-$70,000/year');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('$70,000/year and more');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('1 child');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('2 children');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('3 children');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('4 children');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('4''10" - 4''11" (146-150cm)');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('4''7" (140cm) or below');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('4''8" - 4''9" (141-145cm)');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('5 children');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('5''0" - 5''1"  (151-155cm)');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('5''10" - 5''11" (176-180cm)');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('5''2" - 5''3"  (156-160cm)');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('5''4" - 5''5"  (161-165cm)');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('5''6" - 5''7"  (166-170cm)');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('5''8" - 5''9" (171-175cm)');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('6 children');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('6''0" - 6''1"  (181-185cm)');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('6''2" - 6''3"  (186-190cm)');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('6''4" (191cm) or above');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('AA (2 years college)');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Activity Partner');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Ample');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Athletic');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Attached');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Attractive');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Average');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('BA/BS (4 years college)');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Basic');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Casual');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('College student');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Divorced');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Doesn''t matter');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Fluent');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Friendship');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Good');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Grad school student');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('High School graduate');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Higher Education');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('I prefer not to say');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('I will tell you later');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Intermediate');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('JD');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('living with me');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('MA/MS/MBA');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Marriage');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Maybe');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('No');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('not living with me');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Often');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Pen Pal');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('PhD/Post doctorate');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Rarely');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Relationship');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Romance');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Single');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Slim');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Some grad school');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('sometimes living with me');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Travel Partner');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Very bad');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Very Cuddly');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Very often');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Widow');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('with children');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('without children');
INSERT INTO nataly_schema.Levels (level_name)
VALUES ('Yes');


INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Ample', 'body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Athletic', 'body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Attractive', 'body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Average', 'body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('I prefer not to say', 'body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Slim', 'body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Very Cuddly', 'body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('1 child', 'children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('2 children', 'children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('3 children', 'children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('4 children', 'children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5 children', 'children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('6 children', 'children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('with children', 'children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('without children', 'children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('I prefer not to say', 'drinker');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('No', 'drinker');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Often', 'drinker');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Rarely', 'drinker');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Very often', 'drinker');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('AA (2 years college)', 'education');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('BA/BS (4 years college)', 'education');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('College student', 'education');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Grad school student', 'education');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('High School graduate', 'education');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Higher Education', 'education');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('I prefer not to say', 'education');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('JD', 'education');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('MA/MS/MBA', 'education');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('PhD/Post doctorate', 'education');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Some grad school', 'education');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('4''10" - 4''11" (146-150cm)', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('4''7" (140cm) or below', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('4''8" - 4''9" (141-145cm)', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5''0" - 5''1"  (151-155cm)', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5''10" - 5''11" (176-180cm)', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5''2" - 5''3"  (156-160cm)', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5''4" - 5''5"  (161-165cm)', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5''6" - 5''7"  (166-170cm)', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5''8" - 5''9" (171-175cm)', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('6''0" - 6''1"  (181-185cm)', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('6''2" - 6''3"  (186-190cm)', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('6''4" (191cm) or above', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('I prefer not to say', 'height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('$10,000-$30,000/year', 'income');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('$10,000/year and less', 'income');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('$30,000-$50,000/year', 'income');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('$50,000-$70,000/year', 'income');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('$70,000/year and more', 'income');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('I prefer not to say', 'income');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Ample', 'looking_for_a_body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Athletic', 'looking_for_a_body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Attractive', 'looking_for_a_body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Average', 'looking_for_a_body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('I prefer not to say', 'looking_for_a_body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Slim', 'looking_for_a_body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Very Cuddly', 'looking_for_a_body_type');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('4''10" - 4''11" (146-150cm)', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('4''7" (140cm) or below', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('4''8" - 4''9" (141-145cm)', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5''0" - 5''1"  (151-155cm)', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5''10" - 5''11" (176-180cm)', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5''2" - 5''3"  (156-160cm)', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5''4" - 5''5"  (161-165cm)', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5''6" - 5''7"  (166-170cm)', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('5''8" - 5''9" (171-175cm)', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('6''0" - 6''1"  (181-185cm)', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('6''2" - 6''3"  (186-190cm)', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('6''4" (191cm) or above', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('I prefer not to say', 'looking_for_a_height');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Attached', 'martial_status');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Divorced', 'martial_status');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('I prefer not to say', 'martial_status');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Single', 'martial_status');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Widow', 'martial_status');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Activity Partner', 'relationship');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Casual', 'relationship');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Friendship', 'relationship');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Marriage', 'relationship');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Pen Pal', 'relationship');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Relationship', 'relationship');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Romance', 'relationship');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Travel Partner', 'relationship');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('I prefer not to say', 'smoker');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('No', 'smoker');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Often', 'smoker');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Rarely', 'smoker');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Very often', 'smoker');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Doesn''t matter', 'want_children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('I will tell you later', 'want_children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Maybe', 'want_children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('No', 'want_children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('Yes', 'want_children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('I will tell you later', 'where_children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('living with me', 'where_children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('not living with me', 'where_children');
INSERT INTO nataly_schema.Category_level (level_name, category_name)
VALUES ('sometimes living with me', 'where_children');

INSERT INTO nataly_schema.Religions (religion)
VALUES ('Adventist');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Agnostic');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Atheist');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Baptist');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Buddhist');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Caodaism');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Catholic');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Christian');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Hindu');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('I prefer not to say');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Iskcon');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Jainism');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Jewish');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Methodist');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Mormon');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Moslem');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Orthodox');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Other');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Pentecostal');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Protestant');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Quaker');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Scientology');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Shinto');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Sikhism');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Spiritual');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Taoism');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Wiccan');
INSERT INTO nataly_schema.Religions (religion)
VALUES ('Zoroastrian');

INSERT INTO nataly_schema.Tags (tag, forbidden)
VALUES ('Администрация', 1);
INSERT INTO nataly_schema.Tags (tag, forbidden)
VALUES ('повлечет проблемы', 1);
INSERT INTO nataly_schema.Tags (tag, forbidden)
VALUES ('проблемы', 1);
INSERT INTO nataly_schema.Tags (tag, forbidden)
VALUES ('проверка', 1);
INSERT INTO nataly_schema.Tags (tag, forbidden)
VALUES ('рассылка программой', 1);
INSERT INTO nataly_schema.Tags (tag, forbidden)
VALUES ('сайт', 1);
INSERT INTO nataly_schema.Tags (tag, forbidden)
VALUES ('Test profile', 1);
INSERT INTO nataly_schema.Tags (tag, forbidden)
VALUES ('check system', 1);
INSERT INTO nataly_schema.Tags (tag, forbidden)
VALUES ('bot profile', 1);

INSERT INTO nataly_schema.Privileges (privilege_name)
VALUES ('PROFILES_VISIBILITY');
INSERT INTO nataly_schema.Privileges (privilege_name)
VALUES ('USER_EDIT');

INSERT INTO nataly_schema.User_roles (user_role)
VALUES ('admin');
INSERT INTO nataly_schema.User_roles (user_role)
VALUES ('default');
INSERT INTO nataly_schema.User_roles (user_role)
VALUES ('deleted');
INSERT INTO nataly_schema.User_roles (user_role)
VALUES ('moderator');

INSERT INTO nataly_schema.Privileges_assigns (user_role, privilege_name, privilege_status)
VALUES ('admin', 'PROFILES_VISIBILITY', 1);
INSERT INTO nataly_schema.Privileges_assigns (user_role, privilege_name, privilege_status)
VALUES ('admin', 'USER_EDIT', 1);

INSERT INTO nataly_schema.Users (login, user_password)
VALUES ('server', 'server');
INSERT INTO nataly_schema.Users (login, user_password)
VALUES ('anonymous', 'anonymous');
INSERT INTO nataly_schema.Users (login, user_password)
VALUES ('admin3@gmail.com',
        'sha256$g5s9XzFP$c4c197fa413f9873b3241493f635890827f841b8e8093e418028642ebd5fac20');
INSERT INTO nataly_schema.Users (login, user_password)
VALUES ('admin@gmail.com',
        'sha256$RgDpo8YJ$c4a830dfa1b1665a8411787d1e54b30102d7e4d3ccca9f3729e44e50d479d525');

INSERT INTO nataly_schema.Roles_of_users (login, user_role)
VALUES ('admin3@gmail.com', 'default');
INSERT INTO nataly_schema.Roles_of_users (login, user_role)
VALUES ('admin@gmail.com', 'admin');


INSERT INTO nataly_schema.Zodiacs (zodiac)
VALUES ('Aquarius');
INSERT INTO nataly_schema.Zodiacs (zodiac)
VALUES ('Aries');
INSERT INTO nataly_schema.Zodiacs (zodiac)
VALUES ('Cancer');
INSERT INTO nataly_schema.Zodiacs (zodiac)
VALUES ('Capricorn');
INSERT INTO nataly_schema.Zodiacs (zodiac)
VALUES ('Gemini');
INSERT INTO nataly_schema.Zodiacs (zodiac)
VALUES ('Leo');
INSERT INTO nataly_schema.Zodiacs (zodiac)
VALUES ('Libra');
INSERT INTO nataly_schema.Zodiacs (zodiac)
VALUES ('Pisces');
INSERT INTO nataly_schema.Zodiacs (zodiac)
VALUES ('Sagittarius');
INSERT INTO nataly_schema.Zodiacs (zodiac)
VALUES ('Scorpio');
INSERT INTO nataly_schema.Zodiacs (zodiac)
VALUES ('Taurus');
INSERT INTO nataly_schema.Zodiacs (zodiac)
VALUES ('Virgo');