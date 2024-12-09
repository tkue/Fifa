SELECT ClubId FROM Club WHERE Name = 'olympique lyonnais'
SELECT LeagueId FROM League WHERE Name = 'ligue 1 conforama'
SELECT CountryId FROM Country WHERE Name = 'dominican republic'
SELECT PositionId FROM Position WHERE Name = 'ST'

INSERT INTO Player (
    PositionId
    ,CountryId
    ,LeagueId
    ,ClubId
    ,Name
    ,Overall
)
VALUES (
    16
    ,46
    ,5
    ,22
    ,'Mariano'
    ,90
);


