-- Lista de fans (POST /signup, signup.js). Sin IP, sin user agent. contact es único: un alta repetida no duplica.
CREATE TABLE IF NOT EXISTS mto_fans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contact TEXT NOT NULL UNIQUE,                       -- correo en minúsculas, o número de WhatsApp solo con dígitos (con 52)
  kind TEXT NOT NULL CHECK (kind IN ('email', 'whatsapp')),
  city TEXT,
  consent_version TEXT NOT NULL,                      -- versión del aviso de privacidad que aceptó
  created_at TEXT NOT NULL DEFAULT (datetime('now'))  -- UTC
);
