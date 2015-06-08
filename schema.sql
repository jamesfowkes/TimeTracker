BEGIN TRANSACTION;
CREATE TABLE Tasks (
Job TEXT,
ClientID TEXT,
Description TEXT,
Rate INTEGER,
Start INTEGER,
Finish INTEGER,
FOREIGN KEY(ClientID) REFERENCES Clients(ClientID),
FOREIGN KEY(Job) REFERENCES Jobs(Name),
PRIMARY KEY(Job, ClientID, Description, Start, Finish)
);
INSERT INTO `Tasks` VALUES('ColourVolt','ML','Coding',1500,1411633800,1411662600);
INSERT INTO `Tasks` VALUES('ColourVolt','ML','Coding',1500,1412238600,1412248500);
INSERT INTO `Tasks` VALUES('ColourVolt','ML','Coding',1500,1412251200,1412269200);
INSERT INTO `Tasks` VALUES('ColourVolt','ML','Coding',1500,1413367200,1413392400);
INSERT INTO `Tasks` VALUES('ColourVolt','ML','Coding',1500,1413451800,1413476100);
INSERT INTO `Tasks` VALUES('CSV Software','ML','Python Coding',1500,1414137600,1414154700);
INSERT INTO `Tasks` VALUES('CSV Software','ML','Python Coding',1500,1414159200,1414170000);
INSERT INTO `Tasks` VALUES('Maker Faire','DSM','Workshop',5000,1414328400,1414335600);
INSERT INTO `Tasks` VALUES('CSV Software','ML','Python Coding',1500,1414661400,1414663200);
INSERT INTO `Tasks` VALUES('CSV Software','ML','Python Coding',1500,1414666800,1414672200);
INSERT INTO `Tasks` VALUES('CSV Software','ML','Python Coding',1500,1414674000,1414692000);
INSERT INTO `Tasks` VALUES('CSV Software','ML','Python Coding',1500,1415268000,1415296800);
INSERT INTO `Tasks` VALUES('Latrine Logger','ML','Software Debugging',1500,1415731500,1415736000);
INSERT INTO `Tasks` VALUES('CSV Software','ML','Python Coding',1500,1415961000,1415970000);
INSERT INTO `Tasks` VALUES('CSV Software','ML','Python Coding',1500,1415971800,1415988000);
CREATE TABLE "OneOffs" (
	`Name`	TEXT,
	`ClientID`	TEXT,
	`Charge`	INTEGER,
	`Description`	TEXT,
	FOREIGN KEY(ClientID) REFERENCES Clients(ClientID),
	PRIMARY KEY(Name,ClientID)
);
CREATE TABLE Jobs (
Name TEXT,
ClientID TEXT,
DefaultRate INTEGER,
Active BOOLEAN,
FOREIGN KEY(ClientID) REFERENCES Clients(ClientID),
PRIMARY KEY(Name, ClientID)
);
INSERT INTO `Jobs` VALUES('ColourVolt','ML',1500,1);
INSERT INTO `Jobs` VALUES('CSV Software','ML',1500,1);
INSERT INTO `Jobs` VALUES('Shunt Regulator','ML',1500,1);
INSERT INTO `Jobs` VALUES('Maker Faire','DSM',5000,1);
INSERT INTO `Jobs` VALUES('Latrine Logger','ML',1500,1);
CREATE TABLE Clients (
ClientID TEXT PRIMARY KEY,
Name TEXT,
Address TEXT,
Email TEXT
);
INSERT INTO `Clients` VALUES('ML','Dr. Matt Little','Renewable Energy Innovation<br>Hopkinson Gallery<br>21 Station Street<br>Nottingham<br>NG2 3AJ','matt@re-innovation.co.uk');
INSERT INTO `Clients` VALUES('DSM','Chris Keady','Derby Silk Mill<br>Silk Mill Lane<br>Derby<br>DE1 3AF','chris2@derbymuseums.org');
INSERT INTO `Clients` VALUES('RK','Ross Kemp','The Studio<br>Loughborough Design School<br>LDS1.25<br>Loughborough University<br>LE11 3TU
','ross@asapwatercrafts.com');
;
;
;
;
COMMIT;
