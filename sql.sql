create table users
(
    id char(20) primary key,
    name char(20),
    sex char(20),
    birth varchar(40),
	phone_number varchar(50)
);

create table accounts
(
	id char(20),
	number varchar(50) primary key,
	password varchar(50),
	balance float
);

create table cards
(
	number varchar(50),
	card_id char(20),
	primary key(number,card_id)
)

create table records
(
	number varchar(50),
	card char(20),
	time varchar(50),
	abstract char(20),
	other_number varchar(50),
	amount float,
	balance_before float,
	balance_after float,
	primary key(number,card,time,abstract)
);

#插入初始数据
INSERT INTO users VALUES
('2018201700','杰克','male','2011-03-09','189273');

INSERT INTO accounts VALUES
('2018201700','100','123456',1000);

INSERT INTO cards VALUES
('100','1');

INSERT INTO cards VALUES
('100','2');

INSERT INTO records(number,card,time,abstract,amount,balance_before,balance_after) VALUES
('100','1','Sun Jun 1 11:15:30 2020'，'开户',1000.0,0.0,1000.0);