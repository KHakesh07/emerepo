--------Events table----------------
CREATE TABLE
IF NOT EXISTS Events
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

--- Materials Table
CREATE TABLE IF NOT EXISTS Materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    Category TEXT NOT NULL,
    Weight REAL NOT NULL,
    Quantity REAL NOT NULL,
    Emission REAL NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
);

-- Transport Emissions Table
CREATE TABLE IF NOT EXISTS transport_data (
                        event TEXT NOT NULL,
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mode TEXT NOT NULL,
                        type TEXT NOT NULL,
                        origin TEXT NOT NULL,
                        destination TEXT NOT NULL,
                        distance REAL NOT NULL,
                        Emission REAL NOT NULL);

-- Electric Vehicles Consumption Table
CREATE TABLE IF NOT EXISTS ElectricConsumption (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    Vehicle TEXT NOT NULL,
    ConsumptionPerKm REAL NOT NULL,  -- kWh per km
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
);

-- Electricity Emissions Table
CREATE TABLE IF NOT EXISTS ElectricityEmissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    Usage TEXT NOT NULL,  -- Type of electricity use (e.g., Lighting, Cooling, Heating)
    Value REAL NOT NULL,  -- Consumption in kWh
    Emission REAL NOT NULL,  -- Emissions in kg CO₂
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
);


-- HVAC Emissions Table
CREATE TABLE IF NOT EXISTS HVACEmissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    Refrigerant TEXT NOT NULL,
    MassLeak REAL NOT NULL,
    Emission REAL NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
);

------ Logistics Emissions Table
CREATE TABLE IF NOT EXISTS logistics_emissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Event TEXT NOT NULL,
    material TEXT NOT NULL,
    transport_mode TEXT NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    distance_km REAL NOT NULL,
    weight_kg REAL NOT NULL,
    total_emission REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Food Emissions Table
CREATE TABLE IF NOT EXISTS food_choices (
                        event TEXT NOT NULL,
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        dietary_pattern TEXT NOT NULL,
                        food_item TEXT NOT NULL,
                        emission REAL NOT NULL,
                        FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE);



-- Scope 1 Table
CREATE TABLE IF NOT EXISTS Scope1 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    fuels TEXT NOT NULL,  -- Store multiple fuel types as JSON
    consumptions TEXT NOT NULL,  -- Store multiple consumption values as JSON
    emissions TEXT NOT NULL,  -- Store multiple emissions as JSON
    total_emission REAL NOT NULL,  -- Store total emission
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
);



---------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS EmissionsSummary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Event TEXT NOT NULL,
    Category TEXT CHECK (Category IN ('Scope 1', 'Scope 2', 'Scope 3')) NOT NULL,
    SourceTable TEXT NOT NULL,
    Emission REAL NOT NULL,
    FOREIGN KEY (Event) REFERENCES Events(name) ON UPDATE CASCADE
);
-- Trigger to insert into EmissionsSummary

-- Scope 1 Emissions (HVAC and Scope1 Table)
CREATE TRIGGER IF NOT EXISTS insert_scope1_emissions
AFTER INSERT ON HVACEmissions
FOR EACH ROW
BEGIN
    INSERT INTO EmissionsSummary (Event, Category, SourceTable, Emission)
    VALUES (NEW.event, 'Scope 1', 'HVACEmissions', NEW.Emission);
END;

CREATE TRIGGER IF NOT EXISTS insert_scope1_emissions_scope1
AFTER INSERT ON Scope1
FOR EACH ROW
BEGIN
    INSERT INTO EmissionsSummary (Event, Category, SourceTable, Emission)
    VALUES (NEW.event, 'Scope 1', 'Scope1', NEW.total_emission);
END;

-- Scope 2 Emissions (Electricity Consumption)
CREATE TRIGGER IF NOT EXISTS insert_scope2_emissions
AFTER INSERT ON ElectricityEmissions
FOR EACH ROW
BEGIN
    INSERT INTO EmissionsSummary (Event, Category, SourceTable, Emission)
    VALUES (NEW.event, 'Scope 2', 'ElectricityEmissions', NEW.Emission);
END;

-- Scope 3 Emissions (Transport, Food, Materials)
CREATE TRIGGER IF NOT EXISTS insert_scope3_transport
AFTER INSERT ON transport_data
FOR EACH ROW
BEGIN
    INSERT INTO EmissionsSummary (Event, Category, SourceTable, Emission)
    VALUES (NEW.event, 'Scope 3', 'transport_data', NEW.Emission);
END;

CREATE TRIGGER IF NOT EXISTS insert_scope3_materials
AFTER INSERT ON Materials
FOR EACH ROW
BEGIN
    INSERT INTO EmissionsSummary (Event, Category, SourceTable, Emission)
    VALUES (NEW.event, 'Scope 3', 'Materials', NEW.Emission);
END;

CREATE TRIGGER IF NOT EXISTS insert_scope3_food
AFTER INSERT ON food_choices
FOR EACH ROW
BEGIN
    INSERT INTO EmissionsSummary (Event, Category, SourceTable, Emission)
    VALUES (NEW.event, 'Scope 3', 'food_choices', NEW.emission);
END;


CREATE TRIGGER IF NOT EXISTS insert_scope3_logistics
AFTER INSERT ON logistics_emissions
FOR EACH ROW
BEGIN
    INSERT INTO EmissionsSummary (Event, Category, SourceTable, Emission)
    VALUES (NEW.event, 'Scope 3', 'logistics_emissions', NEW.total_emission);
END;
