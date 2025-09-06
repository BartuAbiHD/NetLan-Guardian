"""
DPI Bypass Engine
GoodbyeDPI tabanlı DPI bypass çözümü
"""

import socket
import random
import time
import threading
import struct
from urllib.parse import urlparse
import ssl
import requests
import subprocess
import sys
import os
from typing import List, Dict, Tuple, Optional

# Eğer bu modül doğrudan çalıştırılıyorsa path ayarı yap
if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from .goodbyedpi_wrapper import GoodbyeDPIWrapper
    from .zapret_wrapper import ZapretWrapper
except ImportError:
    from goodbyedpi_wrapper import GoodbyeDPIWrapper
    from zapret_wrapper import ZapretWrapper


class DPIBypass:
    def __init__(self, config_manager=None):
        """DPI Bypass engine'i başlat"""
        self.config = config_manager
        self.active = False
        self.running = False  # GUI uyumluluğu için
        
        # GoodbyeDPI wrapper'ı
        self.goodbyedpi = GoodbyeDPIWrapper()
        
        # Zapret wrapper'ı
        self.zapret = ZapretWrapper(config_manager)
        
        # GoodbyeDPI ayarları
        self.bypass_mode = 5  # Pasif DPI bypass modu
        self.ttl_value = 5    # GoodbyeDPI varsayılan TTL
        self.fragment_size = 2  # HTTP isteği parçalama boyutu
        self.fake_packet_count = 3  # Sahte paket sayısı
        self.request_delay = 0.1  # İstek gecikme süresi
        
        # DNS ayarları (Yandex DNS - GoodbyeDPI varsayılan)
        self.dns_servers = [
            '77.88.8.8',      # Yandex DNS primary
            '77.88.8.1',      # Yandex DNS secondary
            '8.8.8.8',        # Google DNS fallback
            '8.8.4.4',
            '1.1.1.1',        # Cloudflare DNS fallback
            '1.0.0.1'
        ]
        self.dns_port = 1253  # GoodbyeDPI özel DNS portu
        
        # DPI bypass teknikleri
        self.techniques = {
            'fragment_http_request': True,   # HTTP isteği parçalama
            'modify_ttl': True,              # TTL değiştirme
            'fake_packets': True,            # Sahte paket gönderme
            'dns_over_https': True,          # DoH kullanma
            'tcp_md5_option': False          # TCP MD5 option (gelişmiş)
        }
        
    def start_bypass(self, progress_callback=None):
        """DPI bypass'ı başlat - Seçilen araca göre"""
        if self.active:
            return False
            
        try:
            # Seçili DPI aracını al
            dpi_tool = self.config.get_dpi_tool() if self.config else 'goodbyedpi'
            
            # Seçili ülke kodunu al
            country_code = self.config.get_country_code() if self.config else 'TR'
            
            # Blacklist dosyası ayarları - Her zaman güncel tut
            blacklist_file = None
            if self.config:
                bypass_sites = self.config.get_bypass_sites()
                
                if bypass_sites:
                    # Blacklist dosyasını her başlatmada güncelle
                    blacklist_file = self.config.create_blacklist_file(bypass_sites)
                    print(f"📝 DPI Bypass sadece {len(bypass_sites)} belirtilen siteye uygulanacak")
                    print(f"   Blacklist dosyası güncellendi: {blacklist_file}")
                    print("   (Diğer siteler normal erişim)")
                else:
                    print("📝 Hiç site belirtilmedi - DPI bypass devre dışı")
                    print("   (Liste boş olduğu için hiçbir siteye bypass uygulanmayacak)")
            
            # Seçilen araca göre başlat
            if dpi_tool == 'zapret':
                # Zapret için admin kontrolü
                if not self._is_admin():
                    print("⚠️  Zapret yönetici yetkisi gerektiriyor!")
                    print("   Programı 'Yönetici olarak çalıştır' ile başlatın.")
                
                # Zapret'i kullan
                if not self.zapret.ensure_zapret(progress_callback):
                    print("❌ Zapret indirilemedi!")
                    return False
                
                success, message = self.zapret.start_bypass(blacklist_file, country_code)
                if success:
                    self.active = True
                    self.running = True
                    print(f"✅ DPI Bypass (Zapret) başarıyla başlatıldı!")
                    return True
                else:
                    print(f"❌ Zapret başlatılamadı: {message}")
                    return False
            else:
                # GoodbyeDPI'yi kullan (varsayılan)
                if not self.goodbyedpi.ensure_goodbyedpi(progress_callback):
                    print("❌ GoodbyeDPI indirilemedi!")
                    return False
                
                params = self.goodbyedpi.get_recommended_params_for_country(country_code)
                
                if self.goodbyedpi.start(params, blacklist_file):
                    self.active = True
                    self.running = True
                    print("✅ DPI Bypass (GoodbyeDPI) başarıyla başlatıldı!")
                    return True
                else:
                    print("❌ GoodbyeDPI başlatılamadı!")
                    return False
                
        except Exception as e:
            print(f"❌ DPI Bypass başlatma hatası: {e}")
            return False
        
    def stop_bypass(self):
        """DPI bypass'ı durdur - Seçilen araca göre"""
        if not self.active:
            return True
            
        try:
            # Seçili DPI aracını al
            dpi_tool = self.config.get_dpi_tool() if self.config else 'goodbyedpi'
            
            success = False
            
            if dpi_tool == 'zapret':
                # Zapret'i durdur
                success, message = self.zapret.stop_bypass()
                if success:
                    self.active = False
                    self.running = False
                    print("✅ DPI Bypass (Zapret) durduruldu!")
                else:
                    print(f"⚠️ Zapret durdurma: {message}")
                    # Zorla durdurmayı dene
                    self.active = False
                    self.running = False
                    success = True
            else:
                # GoodbyeDPI'yi durdur (varsayılan)
                if self.goodbyedpi.stop():
                    self.active = False
                    self.running = False
                    success = True
                    print("✅ DPI Bypass (GoodbyeDPI) durduruldu!")
                else:
                    print("❌ GoodbyeDPI durdurulamadı!")
                    
            return success
                
        except Exception as e:
            print(f"❌ DPI Bypass durdurma hatası: {e}")
            return False
        
    def _bypass_worker(self):
        """Bypass worker thread"""
        while self.active:
            time.sleep(1)
            
    def _is_admin(self):
        """Windows admin yetkisi kontrolü"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def _configure_windows_dns(self):
        """Windows DNS ayarlarını değiştir"""
        try:
            # Mevcut DNS ayarlarını kaydet
            result = subprocess.run([
                'netsh', 'interface', 'ip', 'show', 'dns'
            ], capture_output=True, text=True, shell=True)
            
            # Yandex DNS'i ayarla
            primary_dns = self.dns_servers[0]  # 77.88.8.8
            secondary_dns = self.dns_servers[1]  # 77.88.8.1
            
            # Ana network interface'ini bul
            interfaces = self._get_network_interfaces()
            
            for interface in interfaces:
                try:
                    # DNS sunucularını ayarla
                    subprocess.run([
                        'netsh', 'interface', 'ip', 'set', 'dns', 
                        f'name="{interface}"', f'source=static', f'addr={primary_dns}'
                    ], check=False, shell=True)
                    
                    subprocess.run([
                        'netsh', 'interface', 'ip', 'add', 'dns',
                        f'name="{interface}"', f'addr={secondary_dns}', 'index=2'
                    ], check=False, shell=True)
                except:
                    continue
                    
        except Exception as e:
            print(f"DNS konfigürasyonu hatası: {e}")
            
    def _configure_windows_proxy(self):
        """Windows proxy ayarlarını ayarla (opsiyonel)"""
        try:
            # Şimdilik proxy kullanmıyoruz, sadece DNS yeterli
            pass
        except Exception as e:
            print(f"Proxy konfigürasyonu hatası: {e}")
            
    def _restore_windows_settings(self):
        """Windows ayarlarını geri al"""
        try:
            # DNS ayarlarını otomatik yap
            interfaces = self._get_network_interfaces()
            
            for interface in interfaces:
                try:
                    subprocess.run([
                        'netsh', 'interface', 'ip', 'set', 'dns',
                        f'name="{interface}"', 'source=dhcp'
                    ], check=False, shell=True)
                except:
                    continue
                    
        except Exception as e:
            print(f"Ayar geri alma hatası: {e}")
            
    def _get_network_interfaces(self):
        """Aktif network interface'lerini al"""
        try:
            result = subprocess.run([
                'netsh', 'interface', 'show', 'interface'
            ], capture_output=True, text=True, shell=True)
            
            interfaces = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'Connected' in line and 'Dedicated' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        interface_name = ' '.join(parts[3:])
                        interfaces.append(interface_name.strip())
                        
            # Varsayılan interface'ler
            if not interfaces:
                interfaces = ['Wi-Fi', 'Ethernet', 'Local Area Connection']
                
            return interfaces
            
        except:
            return ['Wi-Fi', 'Ethernet']
            
    def check_connection(self, url: str, timeout: int = 5) -> bool:
        """Site bağlantısını kontrol et - GoodbyeDPI aktif iken"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
            
            # GoodbyeDPI çalışıyor mu kontrol et
            if self.active and self.goodbyedpi.is_running():
                # GoodbyeDPI aktif, normal istek at
                response = requests.get(
                    url, 
                    timeout=timeout,
                    headers=self._get_goodbyedpi_headers(),
                    allow_redirects=True,
                    verify=False  # SSL sertifika kontrolünü geç
                )
                return response.status_code == 200
            else:
                # GoodbyeDPI pasif, farklı yöntemler dene
                return self._test_connection_without_goodbyedpi(url, timeout)
                
        except Exception:
            try:
                # HTTP ile deneme
                if url.startswith('https://'):
                    url = url.replace('https://', 'http://')
                response = requests.get(
                    url, 
                    timeout=timeout,
                    headers=self._get_goodbyedpi_headers()
                )
                return response.status_code == 200
            except Exception:
                return False
                
    def _test_connection_without_goodbyedpi(self, url: str, timeout: int) -> bool:
        """GoodbyeDPI olmadan bağlantı testi"""
        try:
            # Önce DoH ile deneme
            if self._test_doh_connection(url, timeout):
                return True
                
            # Normal istek
            response = requests.get(
                url, 
                timeout=timeout,
                headers=self._get_goodbyedpi_headers(),
                verify=False
            )
            return response.status_code == 200
            
        except Exception:
            return False
                
    def _test_fragmented_connection(self, url: str, timeout: int) -> bool:
        """GoodbyeDPI benzeri fragmentli bağlantı testi"""
        try:
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            path = parsed.path or '/'
            
            # Socket bağlantısı
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            if parsed.scheme == 'https':
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=host)
                
            sock.connect((host, port))
            
            # GoodbyeDPI benzeri fragmentli HTTP isteği
            request_parts = self._create_goodbyedpi_request(host, path)
            
            for part in request_parts:
                sock.send(part)
                time.sleep(0.01)  # Küçük gecikme (GoodbyeDPI benzeri)
                
            response = sock.recv(1024)
            sock.close()
            
            return b'HTTP' in response and b'200' in response
            
        except Exception:
            return False
            
    def _test_doh_connection(self, url: str, timeout: int) -> bool:
        """DNS over HTTPS ile bağlantı testi"""
        try:
            # Cloudflare DoH kullan
            doh_url = "https://1.1.1.1/dns-query"
            
            parsed = urlparse(url)
            hostname = parsed.hostname
            
            # DNS sorgusu hazırla
            import base64
            
            # Basit A record sorgusu
            query = self._create_doh_query(hostname)
            
            headers = {
                'Accept': 'application/dns-message',
                'Content-Type': 'application/dns-message'
            }
            
            response = requests.post(
                doh_url,
                data=query,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                # IP adresi alındıysa, site erişilebilir
                return len(response.content) > 12
                
        except Exception:
            pass
            
        return False
        
    def _create_goodbyedpi_request(self, host: str, path: str) -> List[bytes]:
        """GoodbyeDPI benzeri fragmentli HTTP isteği oluştur"""
        headers = self._get_goodbyedpi_headers()
        
        # HTTP request oluştur
        request_line = f"GET {path} HTTP/1.1\r\n"
        host_header = f"Host: {host}\r\n"
        
        other_headers = ""
        for k, v in headers.items():
            if k.lower() != 'host':
                other_headers += f"{k}: {v}\r\n"
        
        full_request = request_line + host_header + other_headers + "\r\n"
        
        # GoodbyeDPI benzeri parçalama
        fragments = []
        request_bytes = full_request.encode('utf-8')
        
        # İlk fragment (GET ve Host header'ın bir kısmı)
        first_fragment = request_bytes[:self.fragment_size]
        fragments.append(first_fragment)
        
        # Kalan fragmentler
        remaining = request_bytes[self.fragment_size:]
        while remaining:
            fragment_size = min(len(remaining), self.fragment_size * 2)
            fragments.append(remaining[:fragment_size])
            remaining = remaining[fragment_size:]
            
        return fragments
        
    def _create_doh_query(self, hostname: str) -> bytes:
        """DNS over HTTPS sorgusu oluştur"""
        try:
            # Basit DNS query (A record)
            query_id = random.randint(1, 65535)
            
            # DNS header
            header = struct.pack('!HHHHHH', query_id, 0x0100, 1, 0, 0, 0)
            
            # Question section
            question = b''
            for part in hostname.split('.'):
                question += struct.pack('!B', len(part)) + part.encode()
            question += b'\x00'  # Null terminator
            question += struct.pack('!HH', 1, 1)  # A record, IN class
            
            return header + question
            
        except:
            return b'\x00' * 32  # Dummy query
        
    def _get_goodbyedpi_headers(self) -> Dict[str, str]:
        """GoodbyeDPI benzeri HTTP header'ları"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
                
    def test_site_access(self, site: str) -> Dict[str, bool]:
        """Site erişimini test et"""
        results = {
            'direct': False,
            'http': False,
            'https': False,
            'fragmented': False
        }
        
        try:
            # Direkt erişim testi
            results['direct'] = self.check_connection(site)
            
            # HTTP testi
            http_url = f'http://{site}' if not site.startswith('http') else site.replace('https://', 'http://')
            results['http'] = self.check_connection(http_url)
            
            # HTTPS testi
            https_url = f'https://{site}' if not site.startswith('http') else site.replace('http://', 'https://')
            results['https'] = self.check_connection(https_url)
            
            # Fragmented erişim testi
            results['fragmented'] = self._test_fragmented_access(site)
            
        except Exception:
            pass
            
        return results
        
    def _test_fragmented_access(self, site: str) -> bool:
        """Fragmented packet testi"""
        try:
            parsed = urlparse(f'https://{site}' if not site.startswith('http') else site)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            
            # Socket bağlantısı
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            if parsed.scheme == 'https':
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)
                
            sock.connect((host, port))
            
            # Fragmented HTTP isteği
            request = self._build_fragmented_request(host, parsed.path or '/')
            
            for fragment in request:
                sock.send(fragment)
                time.sleep(0.01)  # Küçük gecikme
                
            response = sock.recv(1024)
            sock.close()
            
            return b'HTTP' in response
            
        except Exception:
            return False
            
    def _build_fragmented_request(self, host: str, path: str) -> List[bytes]:
        """Fragmented HTTP isteği oluştur"""
        headers = self._get_goodbyedpi_headers()
        header_lines = [f'{k}: {v}' for k, v in headers.items()]
        
        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "\r\n".join(header_lines) + "\r\n\r\n"
        
        # İsteği parçalara böl
        fragments = []
        request_bytes = request.encode('utf-8')
        
        for i in range(0, len(request_bytes), self.fragment_size):
            fragment = request_bytes[i:i + self.fragment_size]
            fragments.append(fragment)
            
        return fragments
        
    def _get_goodbyedpi_headers(self) -> Dict[str, str]:
        """DPI bypass için özel header'lar"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
    def fragment_requests(self, enable: bool = True):
        """Request fragmentation tekniği"""
        self.techniques['fragment_requests'] = enable
        
    def modify_headers(self, enable: bool = True):
        """Header modifikasyon tekniği"""
        self.techniques['modify_headers'] = enable
        
    def fake_packets(self, enable: bool = True):
        """Fake packet tekniği"""
        self.techniques['fake_packets'] = enable
        
    def domain_fronting(self, enable: bool = True):
        """Domain fronting tekniği"""
        self.techniques['domain_fronting'] = enable
        
    def ttl_modification(self, enable: bool = True):
        """TTL modification tekniği"""
        self.techniques['ttl_modification'] = enable
        
    def set_fragment_size(self, size: int):
        """Fragment boyutunu ayarla"""
        if 1 <= size <= 1500:
            self.fragment_size = size
            
    def set_fake_packet_count(self, count: int):
        """Fake packet sayısını ayarla"""
        if 1 <= count <= 10:
            self.fake_packet_count = count
            
    def set_ttl_value(self, ttl: int):
        """TTL değerini ayarla"""
        if 1 <= ttl <= 255:
            self.ttl_value = ttl
            
    def get_status(self) -> Dict[str, any]:
        """Mevcut durumu al"""
        goodbyedpi_status = self.goodbyedpi.get_status()
        
        return {
            'active': self.active,
            'running': self.running,  # GUI uyumluluğu için
            'active_threads': threading.active_count(),  # Aktif thread sayısı
            'goodbyedpi_available': goodbyedpi_status['available'],
            'goodbyedpi_running': goodbyedpi_status['running'],
            'admin_required': goodbyedpi_status['admin_required'],
            'techniques': self.techniques.copy(),
            'fragment_size': self.fragment_size,
            'fake_packet_count': self.fake_packet_count,
            'ttl_value': self.ttl_value,
            'dns_servers': self.dns_servers.copy()
        }
        
    def resolve_dns(self, domain: str) -> Optional[str]:
        """DNS çözümleme"""
        try:
            # Rastgele DNS sunucusu seç
            dns_server = random.choice(self.dns_servers)
            
            # Socket ile DNS sorgusu
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # Basit DNS sorgusu (A record)
            query_id = random.randint(1, 65535)
            query = self._build_dns_query(domain, query_id)
            
            sock.sendto(query, (dns_server, 53))
            response, _ = sock.recvfrom(512)
            sock.close()
            
            ip = self._parse_dns_response(response, query_id)
            return ip
            
        except Exception:
            try:
                # Fallback: sistem DNS'i kullan
                return socket.gethostbyname(domain)
            except Exception:
                return None
                
    def _build_dns_query(self, domain: str, query_id: int) -> bytes:
        """DNS sorgusu oluştur"""
        # DNS header
        header = struct.pack('!HHHHHH', query_id, 0x0100, 1, 0, 0, 0)
        
        # Domain name encoding
        question = b''
        for part in domain.split('.'):
            question += struct.pack('!B', len(part)) + part.encode()
        question += b'\x00'  # Null terminator
        
        # Query type (A record) ve class (IN)
        question += struct.pack('!HH', 1, 1)
        
        return header + question
        
    def _parse_dns_response(self, response: bytes, query_id: int) -> Optional[str]:
        """DNS cevabını parse et"""
        try:
            # Header parse et
            header = struct.unpack('!HHHHHH', response[:12])
            
            if header[0] != query_id:  # Query ID kontrolü
                return None
                
            if header[3] == 0:  # Answer count
                return None
                
            # Basit IP parsing (sadece A record için)
            # Skip question section ve answer'a git
            offset = 12
            
            # Question section'ı atla
            while response[offset] != 0:
                offset += 1
            offset += 5  # Null terminator + type + class
            
            # Answer section
            offset += 2  # Name pointer
            rtype, rclass, ttl, rdlength = struct.unpack('!HHIH', response[offset:offset+10])
            offset += 10
            
            if rtype == 1 and rdlength == 4:  # A record
                ip_bytes = response[offset:offset+4]
                ip = '.'.join(str(b) for b in ip_bytes)
                return ip
                
        except Exception:
            pass
            
        return None
        
    def proxy_requests(self, url: str, proxy_list: List[str] = None) -> Optional[str]:
        """Proxy üzerinden istek gönder"""
        if not proxy_list:
            proxy_list = [
                'socks5://127.0.0.1:9050',  # Tor
                'http://127.0.0.1:8080',    # Local proxy
            ]
            
        for proxy in proxy_list:
            try:
                proxies = {'http': proxy, 'https': proxy}
                response = requests.get(
                    url,
                    proxies=proxies,
                    timeout=10,
                    headers=self._get_goodbyedpi_headers()
                )
                
                if response.status_code == 200:
                    return response.text
                    
            except Exception:
                continue
                
        return None
        
    def get_available_tools(self):
        """Mevcut DPI araçlarını döndür"""
        tools = {}
        
        # GoodbyeDPI durumu
        goodbyedpi_info = self.goodbyedpi.get_info()
        tools['goodbyedpi'] = {
            'name': 'GoodbyeDPI',
            'available': True,  # Her zaman mevcut (indirilir)
            'running': self.goodbyedpi.is_running(),
            'description': 'DPI circumvention aracı - Türkiye için optimize edilmiş',
            'version': goodbyedpi_info.get('version', 'Bilinmiyor'),
            'path': goodbyedpi_info.get('path', 'Otomatik indirilecek')
        }
        
        # Zapret durumu
        zapret_info = self.zapret.get_info()
        tools['zapret'] = {
            'name': 'Zapret',
            'available': True,  # Otomatik indirildiği için daima mevcut
            'running': zapret_info['running'],
            'description': zapret_info['description'],
            'version': zapret_info['version'],
            'path': zapret_info['path'] or 'Otomatik indirilecek'
        }
        
        return tools
    
    def get_current_tool(self):
        """Şu anda seçili olan DPI aracını döndür"""
        return self.config.get_dpi_tool() if self.config else 'goodbyedpi'
    
    def set_current_tool(self, tool):
        """DPI aracını değiştir"""
        if self.config:
            return self.config.set_dpi_tool(tool)
        return False
    
    def get_tool_status(self, tool=None):
        """Belirtilen DPI aracının durumunu döndür"""
        if not tool:
            tool = self.get_current_tool()
            
        if tool == 'zapret':
            return self.zapret.get_status()
        else:
            is_running = self.goodbyedpi.is_running()
            return is_running, f"GoodbyeDPI {'çalışıyor' if is_running else 'çalışmıyor'}"
