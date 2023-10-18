# Módulo platform
# Autor: SistemaRayoXP
# Fecha de Creación: 18/10/2023
#
# Copyright (c) 2023 Edson Armando Alvarez
#
# Licenciado bajo la Licencia MIT.
# Consulta el archivo LICENSE para obtener más detalles.

import sys

def getPlatformUserAgent():
    platform = sys.platform.lower()
    if "darwin" in platform:
        return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    elif "linux" in platform:
        return "Mozilla/5.0 (X11; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0"
    else:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
