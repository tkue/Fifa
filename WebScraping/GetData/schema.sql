CREATE TABLE IF NOT EXISTS `Site` (
    `SiteId` integer NOT NULL PRIMARY KEY AUTOINCREMENT
    ,`Name` text
    ,`Url` text
    ,`CreatedOn` date DEFAULT (datetime('now','localtime'))
    ,CONSTRAINT site_unique_name UNIQUE (`Name`)
);

CREATE TABLE IF NOT EXISTS `FifaVersion` (
    `FifaVersionId` integer NOT NULL PRIMARY KEY AUTOINCREMENT
    ,`Name` text
    ,`CreatedOn` date DEFAULT (datetime('now','localtime'))
    ,CONSTRAINT fifaversion_unique_name UNIQUE (`Name`)
);

CREATE TABLE IF NOT EXISTS `Player` (
    `PlayerId` integer NOT NULL PRIMARY KEY AUTOINCREMENT
    ,`SiteId` integer
    ,`Url` text
    ,`Name` text
    ,`Nationality` text
    ,`League` text
    ,`Club` text
    ,`Position` text
    ,`General_Cost` text
    ,`Playstation_Cost` text
    ,`Xbox_Cost` text
    ,`Pc_Cost` text
    ,`Overall` integer
    ,`Pace` integer
    ,`Shooting` integer
    ,`Passing` integer
    ,`Dribbling` integer
    ,`Defense` integer
    ,`Physical` integer
    ,`SkillMoves` integer
    ,`WeakFootAbility` integer
    ,`OffensiveWorkRate` text
    ,`DeffensiveWorkRate` text
    ,`PreferredFoot` text
    ,`TotalStats` integer
    ,`HeightInches` integer
    ,`CreatedOn` date DEFAULT (datetime('now','localtime'))
    ,`IsDeleted` integer not null default 0
    ,FOREIGN KEY (SiteId) REFERENCES Site(SiteId)
);