INSERT INTO PositionCategory (
    `Name`
)
VALUES
    ('Defender')
    ,('Midfielder')
    ,('Attacker');

INSERT INTO Position (
    `Name`
)
VALUES
    ('GK')
    ,('RWB')
    ,('RB')
    ,('CB')
    ,('LB')
    ,('LWB')
    ,('CDM')
    ,('RM')
    ,('CM')
    ,('LM')
    ,('CAM')
    ,('RF')
    ,('CF')
    ,('LF')
    ,('RW')
    ,('ST')
    ,('LW');

UPDATE Position
SET
    PositionCategoryId = (SELECT PositionCategoryId FROM PositionCategory WHERE Name = 'Defender')
WHERE
    Name IN ('RWB', 'RB', 'CB', 'LB', 'LWB');

UPDATE Position
SET
    PositionCategoryId = (SELECT PositionCategoryId FROM PositionCategory WHERE Name = 'Midfielder')
WHERE
    Name IN ('CDM', 'RM', 'CM', 'LM', 'CAM');

UPDATE Position
SET
    PositionCategoryId = (SELECT PositionCategoryId FROM PositionCategory WHERE Name = 'Defender')
WHERE
    Name IN ('RF', 'CF', 'LF', 'RW', 'ST', 'LW');


INSERT INTO PlayerCostType (
    `Name`
)
VALUES
    ('Low')
    ,('High')
    ,('Median');


INSERT INTO Site (Name, Url)
VALUES ('WebApp', 'https://www.easports.com/fifa/ultimate-team/web-app/');

INSERT INTO Site (Name, Url)
VALUES ('FutHead', 'https://www.futhead.com/');