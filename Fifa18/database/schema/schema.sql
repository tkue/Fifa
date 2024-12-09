CREATE TABLE IF NOT EXISTS `PositionCategory` (
    PositionCategoryId integer primary key autoincrement
    ,`Name` text not null
    ,`Description` text
    ,CONSTRAINT positioncategory_unique_name UNIQUE (`Name`)
);

CREATE TABLE IF NOT EXISTS `Position` (
    PositionId integer primary key autoincrement
    ,PositionCategoryId integer
    ,`Name` text not null
    ,`Description`
    ,CONSTRAINT position_unique_name UNIQUE (`Name`)
    ,FOREIGN KEY (PositionCategoryId) REFERENCES PositionCategory(PositionCategoryId)
);

CREATE TABLE IF NOT EXISTS `Site` (
    `SiteId` integer NOT NULL PRIMARY KEY AUTOINCREMENT
    ,`Name` text not null
    ,`Url` text
    ,`CreatedOnUTC` date DEFAULT (datetime('now'))
    ,CONSTRAINT site_unique_name UNIQUE (`Name`)
);

CREATE TABLE IF NOT EXISTS `FifaVersion` (
    `FifaVersionId` integer NOT NULL PRIMARY KEY AUTOINCREMENT
    ,`Name` text not null
    ,`CreatedOnUTC` date DEFAULT (datetime('now'))
    ,CONSTRAINT fifaversion_unique_name UNIQUE (`Name`)
);

CREATE TABLE IF NOT EXISTS `Country` (
    `CountryId` integer NOT NULL PRIMARY KEY AUTOINCREMENT
    ,`Name` text not null
    ,CONSTRAINT country_unique_name UNIQUE (`Name`)
);

CREATE TABLE IF NOT EXISTS `League` (
    `LeagueId` integer NOT NULL PRIMARY KEY AUTOINCREMENT
    ,`Name` text not null
    ,CONSTRAINT league_unique_name UNIQUE (`Name`)
);

CREATE TABLE IF NOT EXISTS `Club` (
    ClubId integer NOT NULL PRIMARY KEY AUTOINCREMENT
    ,`Name` text not null
    ,CONSTRAINT name_unique_name UNIQUE (`Name`)
);

CREATE TABLE IF NOT EXISTS `Player` (
    `PlayerId` integer NOT NULL PRIMARY KEY AUTOINCREMENT
    ,`SiteId` integer
    ,`FifaVersionId` integer
    ,`PositionId` integer
    ,`CountryId` integer
    ,`LeagueId` integer
    ,`ClubId` integer
    ,`Url` text
    ,`Name` text
    ,`Nickname` text
    ,`General_Cost` text
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
    ,`ChemistryStyle` text
    ,`CreatedOnUTC` date DEFAULT (datetime('now'))
    ,`IsDeleted` integer not null default 0
    ,FOREIGN KEY (SiteId) REFERENCES Site(SiteId)
    ,FOREIGN KEY (FifaVersionId) REFERENCES FifaVersion(FifaVersionId)
    ,FOREIGN KEY (PositionId) REFERENCES Position(PositionId)
    ,FOREIGN KEY (CountryId) REFERENCES Country(CountryId)
    ,FOREIGN KEY (LeagueId) REFERENCES League(LeagueId)
    ,FOREIGN KEY (ClubId) REFERENCES Club(ClubId)
);

CREATE TABLE IF NOT EXISTS `PlayerCostType` (
    PlayerCostTypeId integer NOT NULL PRIMARY KEY AUTOINCREMENT
    ,`Name` text NOT NULL
    ,CONSTRAINT playercosttype_unique_name UNIQUE (`Name`)
);

CREATE TABLE IF NOT EXISTS `PlayerCost` (
    PlayerCostId integer NOT NULL PRIMARY KEY AUTOINCREMENT
    ,PlayerId integer
    ,`Cost` integer
    ,DateCostObtained date
    ,`CreatedOnUTC` date DEFAULT (datetime('now'))
    ,IsDeleted not null default 0
    ,FOREIGN KEY (PlayerId) REFERENCES Player(PlayerId)
);

CREATE TABLE IF NOT EXISTS `Formation` (
    FormationId integer NOT NULL PRIMARY KEY AUTOINCREMENT
    ,`Name`
    ,`CreatedOnUTC` date DEFAULT (datetime('now'))
    ,CONSTRAINT formation_unique_name UNIQUE (`Name`)
);



