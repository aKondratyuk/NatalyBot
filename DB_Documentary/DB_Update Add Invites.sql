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
/* Table: Sent_invites                                        */
/*==============================================================*/
create table Sent_invites
(
   invite_id            binary(16) not null  comment '',
   login                varchar(190) not null  comment '',
   primary key (invite_id, login)
);

alter table Sendt_invites add constraint FK_SENT_I_INVITE_HA_INVITES
foreign key (invite_id)
      references Invites (invite_id) on delete restrict on update restrict;

alter table Sendt_invites add constraint FK_SENT_I_USER_HAS__USERS foreign
 key (login)
      references Users (login) on delete restrict on update restrict;