CREATE TABLE IF NOT EXISTS candidatures (
    id SERIAL PRIMARY KEY,
    job_ref VARCHAR(100) NOT NULL,

    -- Identification
    lastname VARCHAR(100) NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    birthdate DATE,
    

    -- Documents (FK -> cv_files / autres fichiers)
    cv_file_id INT REFERENCES cv_files(id) ON DELETE SET NULL,
    lm_file_id INT,
    diplomes_zip_id INT,

    -- Parcours & compétences
    last_job VARCHAR(150),
    last_company VARCHAR(150),
    exp_years INT,
    skills JSONB,
    langs_lvl JSONB,
    mobility_sites JSONB,

    -- Conditions & disponibilité
    avail_date DATE,
    sal_expectation NUMERIC(12,2),
    contract_accepted VARCHAR(50),
    work_permit_status VARCHAR(50),

    -- Consentement
    consent_bool BOOLEAN DEFAULT FALSE,

    -- Métadonnées
    parsed_json JSONB,
    score NUMERIC(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
