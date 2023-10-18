# Módulo de ejemplo
# Autor: SistemaRayoXP
# Fecha de Creación: 18/10/2023
#
# Copyright (c) 2023 Edson Armando Alvarez
#
# Licenciado bajo la Licencia MIT.
# Consulta el archivo LICENSE para obtener más detalles.

from siiauscraper import LoginScraper

scraper = LoginScraper("123456789", "contrasenya")

print(f"Sesión iniciada: {scraper.isLogged()}")

if scraper.isLogged():
    params = {
        "p_sistema_c": "ALUMNOS",
        "p_sistemaid_n": "3",
        "p_menupredid_n": "3",
        "p_pidm_n": scraper.getSession(),
        "p_majr_c": scraper.getSession(),
    }
    print(scraper.getAplication("gupmenug", "menu", params=params).text)

scraper.logout()

print("Saliendo...")
