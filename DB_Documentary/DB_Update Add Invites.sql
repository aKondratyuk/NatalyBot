/*==============================================================*/
/* Table: Invites                                               */
/*==============================================================*/
create table Invites
(
   invite_id            binary(16) not null  comment '',
   create_time          timestamp not null  comment '',
   primary key (invite_id)
);

/*==============================================================*/
/* Table: Sended_invites                                        */
/*==============================================================*/
create table Sended_invites
(
   invite_id            binary(16) not null  comment '',
   login                varchar(190) not null  comment '',
   primary key (invite_id, login)
);

alter table Sended_invites add constraint FK_SENDED_I_INVITE_HA_INVITES foreign key (invite_id)
      references Invites (invite_id) on delete restrict on update restrict;

alter table Sended_invites add constraint FK_SENDED_I_USER_HAS__USERS foreign key (login)
      references Users (login) on delete restrict on update restrict;