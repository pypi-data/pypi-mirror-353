# src/Terminal/Terminal.py

import sys
import time
from datetime import datetime, timedelta
from colorama import Fore, init, Style
from pathlib import Path

class Terminal:
    def __init__(self, dev:bool=False):
        """
        Inicializa la clase Terminal, configura el modo desarrollador y el inicio de ejecución.
        
        :param dev: Si es True, activa el modo desarrollador (esperas más cortas).
        """
        self.dev = dev
        self.log_activo = False
        init()
        self.inicio_ejecucion(self.get_carpeta_raiz())
        
    def set_carpeta_raiz(self, carpeta_raiz:str) -> None:
        """
        Establece la carpeta raíz para el log.
        
        :param carpeta_raiz: Ruta de la carpeta raíz donde se guardará el log.
        """
        self.carpeta_raiz = carpeta_raiz
        
    def get_carpeta_raiz(self) -> str:
        """
        Obtiene la carpeta raíz donde se guardará el log.
        
        :return: Ruta de la carpeta raíz.
        :rtype: str
        """
        return self.carpeta_raiz if hasattr(self, 'carpeta_raiz') else ""

    def obtener_hora_actual(self, format:str) -> str: 
        """ 
        Obtiene la hora actual en el formato especificado.
        
        :param format: Formato de fecha y hora, por ejemplo "%Y-%m-%d %H:%M:%S".
        :return: Hora actual formateada como cadena.
        :rtype: str
        """
        fecha = datetime.now()
        return fecha.strftime(format)

    def mostrar(self, mensaje:str, isError: bool=False) -> None:
        """
        Muestra un mensaje en consola con color y lo guarda en el log.
        
        :param mensaje: Mensaje a mostrar.
        :param isError: Si es True, muestra el mensaje en rojo (error).
        """
        color_fecha = Fore.GREEN if not isError else Fore.RED
        print(color_fecha + f"[{self.obtener_hora_actual(r"%Y-%m-%d %H:%M:%S")}]" + Style.RESET_ALL + f"\t{mensaje}")
        self.__guardar_en_log(mensaje)
        
    def inicio_ejecucion(self, carpeta_raiz:str = "") -> None:
        """
        Marca el inicio de la ejecución, inicia el log y muestra mensaje de inicio.
        """
        self.tiempo_inicio = self.obtener_hora_actual(r"%Y-%m-%d %H:%M:%S")
        self.log_activo = self.__iniciar_log(carpeta_raiz)
        self.mostrar("Iniciando ejecución")
        
    def fin_ejecucion(self) -> None:
        """
        Marca el fin de la ejecución y muestra mensaje de finalización.
        """
        self.tiempo_fin = self.obtener_hora_actual(r"%Y-%m-%d %H:%M:%S")
        self.mostrar("Ejecución finalizada")
        
    def demora(self, tiempoEspera:int=5) -> None:
        """
        Realiza una pausa en la ejecución.
        
        :param tiempoEspera: Tiempo de espera en segundos (por defecto 5, o 1 si está en modo dev).
        """
        if self.dev: tiempoEspera = 1
        time.sleep(tiempoEspera)
        
    def obtener_duracion_ejecucion(self) -> str:
        """
        Calcula la duración total de la ejecución.
        
        :return: Duración de la ejecución como cadena.
        :raises ValueError: Si la ejecución no ha sido iniciada correctamente.
        """
        if not hasattr(self, 'tiempo_inicio'):
            raise ValueError("La ejecución no ha sido iniciada correctamente.")
        
        if not hasattr(self, 'tiempo_fin'):
            self.tiempo_fin = self.obtener_hora_actual(r"%Y-%m-%d %H:%M:%S")
            
        self.duracion_ejecucion = datetime.strptime(self.tiempo_fin, r"%Y-%m-%d %H:%M:%S") - datetime.strptime(self.tiempo_inicio, r"%Y-%m-%d %H:%M:%S")
        
        return str(self.duracion_ejecucion)
    
    def __iniciar_log(self, carpeta_raiz: str = "") -> bool:
        """
        Inicializa el archivo de log en la carpeta 'logs', creando la carpeta si no existe.
        """
        
        
        try:
            if carpeta_raiz != "":
                base_path = Path(carpeta_raiz)
            else:
                base_path = Path(__file__).parent.parent if not hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
        
            logs_dir = base_path / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            fecha_actual = self.obtener_hora_actual(r"%Y%m%d")
            numero_log_diario = len(list(logs_dir.glob(f"{fecha_actual}*.txt"))) + 1
            self._ruta_archivo_log = logs_dir / f"{fecha_actual}_{numero_log_diario}.txt"
            return True if self._ruta_archivo_log.exists() else False
        
        except Exception as e:
            self.mostrar(f"Error al iniciar el log: {e}", isError=True)
            return False
        
    def __guardar_en_log(self, mensaje:str, reintentos:int = 0) -> None:
        """
        Guarda un mensaje en el archivo de log. Reintenta hasta 3 veces en caso de error.
        
        :param mensaje: Mensaje a guardar.
        :param reintentos: Número de intentos realizados (para control interno).
        """
        if not self.log_activo: 
            print("El archivo log no está activo, no se guardará el mensaje")
            return         
        
        if reintentos > 3:
            print("Error al guardar en el log después de varios intentos")
            return
        
        try:
            with open(self._ruta_archivo_log, 'a', encoding='utf-8') as log_file:
                log_file.write(f"[{self.obtener_hora_actual(r'%Y-%m-%d %H:%M:%S')}] {mensaje}\n")
        except Exception as e:
            print(f"Error al guardar en el log: {e}")
            self.__guardar_en_log(mensaje, reintentos + 1)