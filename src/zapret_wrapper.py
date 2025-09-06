#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zapret Wrapper
Zapret DPI bypass aracı için Python wrapper sınıfı
"""

import subprocess
import threading
import time
import os
import signal
import psutil
import requests
import zipfile
import tempfile
import shutil
from pathlib import Path
import logging
import requests
import zipfile
import shutil

class ZapretWrapper:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.process = None
        self.is_running = False
        self.zapret_path = self.find_zapret_executable()
        self.logger = logging.getLogger(__name__)
        
        # Zapret için varsayılan parametreler (minimal ve güvenli)
        self.default_params = [
            '--filter-tcp=80,443'
        ]
        
    def find_zapret_executable(self):
        """Zapret executable dosyasını bul"""
        base_dir = Path(__file__).parent.parent
        possible_paths = [
            # Zapret-win-bundle yapısı (güncellenmiş)
            base_dir / "external" / "zapret" / "zapret-winws" / "winws.exe",
            base_dir / "external" / "zapret" / "winws.exe", 
            base_dir / "external" / "zapret" / "zapret.exe",
            # Genel sistem yolu
            "winws.exe",
            "zapret.exe"
        ]
        
        for path in possible_paths:
            if isinstance(path, Path) and path.exists():
                return str(path)
            elif isinstance(path, str):
                # System PATH'de ara
                import shutil
                found = shutil.which(path)
                if found:
                    return found
        
        return None
        
    def is_available(self):
        """Zapret'in kullanılabilir olup olmadığını kontrol et"""
        return self.zapret_path is not None
    
    def ensure_zapret(self, progress_callback=None):
        """Zapret'in varlığını sağla, yoksa indir"""
        if self.zapret_path:
            return True
            
        if progress_callback:
            progress_callback("🔄 Zapret bulunamadı, indiriliyor...", 0)
        else:
            print("🔄 Zapret bulunamadı, indiriliyor...")
        return self.download_zapret(progress_callback)
    
    def download_zapret(self, progress_callback=None):
        """Zapret'i GitHub'dan indir"""
        try:
            base_dir = Path(__file__).parent.parent
            external_dir = base_dir / "external"
            zapret_dir = external_dir / "zapret"
            
            # Klasörleri oluştur
            external_dir.mkdir(exist_ok=True)
            zapret_dir.mkdir(exist_ok=True)
            
            # Download URL
            download_url = "https://github.com/bol-van/zapret-win-bundle/archive/refs/heads/master.zip"
            zip_path = zapret_dir / "zapret-master.zip"
            
            if progress_callback:
                progress_callback(f"📥 İndiriliyor: Zapret", 5)
            else:
                print(f"📥 İndiriliyor: {download_url}")
            
            # İndir
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Dosyaya kaydet
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = min(90, 5 + (downloaded / total_size) * 85)  # 5-90% arası
                            if progress_callback:
                                progress_callback(f"📥 İndiriliyor... {percent:.1f}%", percent)
            
            if progress_callback:
                progress_callback(f"📦 İndirme tamamlandı", 90)
            else:
                print(f"📦 İndirme tamamlandı: {zip_path}")
            
            # ZIP'i çıkart
            if progress_callback:
                progress_callback("📂 Dosyalar çıkartılıyor...", 95)
            else:
                print("📂 Dosyalar çıkartılıyor...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(zapret_dir)
            
            # ZIP dosyasını sil
            zip_path.unlink()
            
            # Executable'ı tekrar ara
            self.zapret_path = self.find_zapret_executable()
            
            if self.zapret_path:
                if progress_callback:
                    progress_callback(f"✅ Zapret başarıyla kuruldu!", 100)
                else:
                    print(f"✅ Zapret başarıyla kuruldu: {self.zapret_path}")
                return True
            else:
                if progress_callback:
                    progress_callback("❌ Zapret kuruldu ama executable bulunamadı!", 100)
                else:
                    print("❌ Zapret kuruldu ama executable bulunamadı!")
                return False
                
        except requests.RequestException as e:
            error_msg = f"❌ İndirme hatası: {e}"
            if progress_callback:
                progress_callback(error_msg, 0)
            else:
                print(error_msg)
            return False
        except zipfile.BadZipFile:
            error_msg = "❌ İndirilen dosya geçersiz ZIP!"
            if progress_callback:
                progress_callback(error_msg, 0)
            else:
                print(error_msg)
            return False
        except Exception as e:
            error_msg = f"❌ Zapret kurulum hatası: {e}"
            if progress_callback:
                progress_callback(error_msg, 0)
            else:
                print(error_msg)
            return False
        
    def build_command(self, blacklist_file=None, country_code="TR"):
        """Zapret komutunu oluştur - Ülke bazlı konfigürasyon"""
        if not self.zapret_path:
            raise Exception("Zapret executable bulunamadı")
            
        cmd = [self.zapret_path]
        
        # Fake TLS ve QUIC dosya yolları
        zapret_dir = Path(self.zapret_path).parent
        fake_quic_file = zapret_dir / "files" / "quic_initial_www_google_com.bin"
        
        # Ülke bazlı konfigürasyon parametrelerini al
        country_config = self.get_country_config(country_code)
        
        # Windivert filtre ayarları
        cmd.extend(['--wf-tcp=80,443', '--wf-udp=443'])
        
        if blacklist_file and os.path.exists(blacklist_file):
            # Blacklist dosyasının gerçek içerik içerip içermediğini kontrol et
            has_domains = False
            try:
                with open(blacklist_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Yorum satırı değilse ve boş değilse
                        if line and not line.startswith('#'):
                            has_domains = True
                            break
            except Exception:
                pass
                
            if not has_domains:
                raise Exception("❌ Blacklist dosyası boş veya sadece yorum satırları içeriyor! Lütfen en az bir domain ekleyin.")
            
            # Ülke bazlı konfigürasyonu uygula
            if country_config['use_hostlist']:
                # HTTPS (port 443) - Ana filtre - ülke konfigürasyonuna göre
                cmd.extend([
                    '--filter-tcp=443',
                    '--hostlist', blacklist_file,
                    '--dpi-desync=' + country_config['tcp_443']['desync_method'],
                    '--dpi-desync-ttl=' + str(country_config['tcp_443']['ttl']),
                    '--dpi-desync-fooling=' + country_config['tcp_443']['fooling'],
                    '--new',
                    
                    # HTTP (port 80) - ülke konfigürasyonuna göre
                    '--filter-tcp=80',
                    '--hostlist', blacklist_file,
                    '--dpi-desync=' + country_config['tcp_80']['desync_method'],
                    '--dpi-desync-autottl=' + str(country_config['tcp_80']['autottl']),
                    '--new',
                    
                    # QUIC/HTTP3 (UDP 443) - ülke konfigürasyonuna göre
                    '--filter-udp=443',
                    '--hostlist', blacklist_file,
                    '--dpi-desync=' + country_config['udp_443']['desync_method']
                ])
                
                # Ek parametreleri ekle
                if country_config.get('extra_params'):
                    cmd.extend(country_config['extra_params'])
            else:
                # Hostlist kullanmayan ülke konfigürasyonu
                cmd.extend(country_config['global_params'])
        else:
            # Hostlist olmadan Zapret çalıştırmayı engelle
            raise Exception("❌ Zapret için domain listesi gerekli! Lütfen en az bir site ekleyin.")
            
        return cmd
        
    def get_country_config(self, country_code="TR"):
        """Ülke bazlı Zapret konfigürasyon parametrelerini döndür"""
        country_configs = {
            "TR": {  # Türkiye - YouTube, Discord, vs. için optimize
                "use_hostlist": True,
                "tcp_443": {
                    "desync_method": "fake",
                    "ttl": 0,
                    "fooling": "md5sig"
                },
                "tcp_80": {
                    "desync_method": "fake", 
                    "autottl": 2
                },
                "udp_443": {
                    "desync_method": "fake"
                },
                "extra_params": []
            },
            "RU": {  # Rusya - Daha agresif ayarlar
                "use_hostlist": True,
                "tcp_443": {
                    "desync_method": "split2",
                    "ttl": 1,
                    "fooling": "badseq"
                },
                "tcp_80": {
                    "desync_method": "split2",
                    "autottl": 1
                },
                "udp_443": {
                    "desync_method": "fake"
                },
                "extra_params": ["--dpi-desync-split-pos=1"]
            },
            "CN": {  # Çin - Çok agresif ayarlar
                "use_hostlist": True,
                "tcp_443": {
                    "desync_method": "disorder2",
                    "ttl": 1,
                    "fooling": "badsum"
                },
                "tcp_80": {
                    "desync_method": "disorder2",
                    "autottl": 1
                },
                "udp_443": {
                    "desync_method": "fake"
                },
                "extra_params": ["--dpi-desync-split-pos=2"]
            },
            "IR": {  # İran - Özel ayarlar
                "use_hostlist": True,
                "tcp_443": {
                    "desync_method": "fake,disorder",
                    "ttl": 6,
                    "fooling": "md5sig"
                },
                "tcp_80": {
                    "desync_method": "fake",
                    "autottl": 3
                },
                "udp_443": {
                    "desync_method": "fake"
                },
                "extra_params": []
            },
            "US": {  # Amerika - Minimal ayarlar (çoğu ISP bypass gerektirmez)
                "use_hostlist": True,
                "tcp_443": {
                    "desync_method": "fake",
                    "ttl": 4,
                    "fooling": "none"
                },
                "tcp_80": {
                    "desync_method": "fake",
                    "autottl": 4
                },
                "udp_443": {
                    "desync_method": "fake"
                },
                "extra_params": []
            },
            "GB": {  # İngiltere - Orta düzey
                "use_hostlist": True,
                "tcp_443": {
                    "desync_method": "fake",
                    "ttl": 3,
                    "fooling": "md5sig"
                },
                "tcp_80": {
                    "desync_method": "fake",
                    "autottl": 3
                },
                "udp_443": {
                    "desync_method": "fake"
                },
                "extra_params": []
            },
            "DEFAULT": {  # Varsayılan - Türkiye ile aynı
                "use_hostlist": True,
                "tcp_443": {
                    "desync_method": "fake",
                    "ttl": 0,
                    "fooling": "md5sig"
                },
                "tcp_80": {
                    "desync_method": "fake",
                    "autottl": 2
                },
                "udp_443": {
                    "desync_method": "fake"
                },
                "extra_params": []
            }
        }
        
        return country_configs.get(country_code, country_configs["DEFAULT"])
    
    def start_bypass(self, blacklist_file=None, country_code="TR"):
        """Zapret DPI bypass başlat"""
        if self.is_running:
            return True, "Zapret zaten çalışıyor"
            
        # Zapret'in varlığını sağla
        if not self.ensure_zapret():
            return False, "Zapret indirilemedi veya kurulamadı."
            
        try:
            # Domain listesi kontrolü
            bypass_sites = self.config_manager.get_bypass_sites()
            if not bypass_sites:
                return False, "❌ Zapret için en az bir domain gerekli! Lütfen site listesine domain ekleyin."
            
            # Blacklist dosyasını oluştur/güncelle
            if blacklist_file:
                self.config_manager.create_blacklist_file(bypass_sites)
                
                # Dosyanın gerçekten oluşturulduğunu kontrol et
                if not os.path.exists(blacklist_file) or os.path.getsize(blacklist_file) == 0:
                    return False, "❌ Blacklist dosyası oluşturulamadı veya boş!"
            else:
                return False, "❌ Blacklist dosyası belirtilmedi!"
            
            # Komut oluştur - ülke kodu ile
            cmd = self.build_command(blacklist_file, country_code)
            
            # Zapret'i başlat
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # Kısa süre bekle ve kontrol et
            time.sleep(2)
            
            if self.process.poll() is None:
                self.is_running = True
                return True, f"✅ Zapret başarıyla başlatıldı (PID: {self.process.pid})"
            else:
                stdout, stderr = self.process.communicate()
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "Bilinmeyen hata"
                return False, f"❌ Zapret başlatılamadı: {error_msg}"
                
        except PermissionError:
            return False, "❌ Yönetici yetkisi gerekiyor. Programı 'Yönetici olarak çalıştır' ile başlatın."
        except OSError as e:
            if e.winerror == 740:
                return False, "❌ Yönetici yetkisi gerekiyor. Programı 'Yönetici olarak çalıştır' ile başlatın."
            else:
                return False, f"❌ Sistem hatası: {str(e)}"
        except Exception as e:
            return False, f"❌ Zapret başlatma hatası: {str(e)}"
            
    def stop_bypass(self):
        """Zapret DPI bypass durdur"""
        if not self.is_running:
            return True, "Zapret zaten durdurulmuş"
            
        try:
            # Process'i sonlandır
            if self.process and self.process.poll() is None:
                try:
                    # Windows'ta CTRL+C gönder
                    self.process.send_signal(signal.CTRL_C_EVENT)
                    
                    # 5 saniye bekle
                    try:
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Force kill
                        self.process.terminate()
                        try:
                            self.process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            self.process.kill()
                            
                except Exception:
                    # Fallback: force terminate
                    try:
                        self.process.terminate()
                        self.process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        
            # Alt process'leri de temizle
            self.cleanup_zapret_processes()
            
            self.is_running = False
            self.process = None
            
            return True, "✅ Zapret başarıyla durduruldu"
            
        except Exception as e:
            self.is_running = False
            self.process = None
            return False, f"⚠️ Zapret durdurma hatası: {str(e)} (Büyük ihtimalle zaten durmuş)"
            
    def cleanup_zapret_processes(self):
        """Zapret ile ilgili tüm process'leri temizle"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    name = proc.info['name'].lower()
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    
                    if ('zapret' in name or 'winws' in name or 
                        'zapret' in cmdline.lower()):
                        proc.terminate()
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.warning(f"Zapret process temizleme uyarısı: {e}")
            
    def get_status(self):
        """Zapret durumunu kontrol et"""
        if not self.process:
            return False, "Zapret çalışmıyor"
            
        if self.process.poll() is None:
            return True, f"Zapret çalışıyor (PID: {self.process.pid})"
        else:
            self.is_running = False
            return False, "Zapret durmuş"
            
    def install_zapret(self):
        """Zapret'i otomatik indir ve kur"""
        if self.is_available():
            return "✅ Zapret zaten kurulu!"
        
        print("🔄 Zapret otomatik olarak indiriliyor...")
        
        if self.download_zapret():
            return "✅ Zapret başarıyla kuruldu!"
        else:
            return """
❌ Zapret otomatik kurulumu başarısız!

🔧 Manuel Kurulum Talimatları:
1. https://github.com/bol-van/zapret-win-bundle/archive/refs/heads/master.zip
2. İndirilen dosyaları şu klasöre çıkartın:
   {}/external/zapret/

Gerekli dosyalar:
- winws.exe veya zapret.exe
- Diğer DLL ve konfigürasyon dosyaları

Kurulumdan sonra programı yeniden başlatın.
            """.format(Path(__file__).parent.parent)
    
    def download_zapret(self, progress_callback=None):
        """Zapret'i GitHub'dan indir"""
        zapret_url = "https://github.com/bol-van/zapret-win-bundle/archive/refs/heads/master.zip"
        
        try:
            if progress_callback:
                progress_callback("🔄 Zapret indiriliyor...", 5)
            else:
                print("🔄 Zapret indiriliyor...")
            
            # Temp dizini oluştur
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                zip_path = temp_path / "zapret.zip"
                
                # İndir
                response = requests.get(zapret_url, stream=True, timeout=30)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                percent = min(90, 5 + (downloaded / total_size) * 85)
                                if progress_callback:
                                    progress_callback(f"📥 İndiriliyor... {percent:.1f}%", percent)
                
                if progress_callback:
                    progress_callback("📦 Zapret dosyaları çıkartılıyor...", 95)
                else:
                    print("📦 Zapret dosyaları çıkartılıyor...")
                
                # ZIP'i çıkart
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Zapret dizinini bul (zapret-win-bundle-master/)
                extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir() and 'zapret' in d.name.lower()]
                
                if not extracted_dirs:
                    raise Exception("Zapret dosyaları bulunamadı")
                
                source_dir = extracted_dirs[0]
                
                # Hedef dizini temizle ve oluştur
                base_dir = Path(__file__).parent.parent
                target_dir = base_dir / "external" / "zapret"
                
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Dosyaları kopyala
                for item in source_dir.iterdir():
                    if item.is_file():
                        shutil.copy2(item, target_dir)
                    elif item.is_dir():
                        shutil.copytree(item, target_dir / item.name)
                
                # Zapret executable'ını yeniden bul
                self.zapret_path = self.find_zapret_executable()
                
                if self.zapret_path:
                    if progress_callback:
                        progress_callback("✅ Zapret başarıyla kuruldu!", 100)
                    else:
                        print(f"✅ Zapret başarıyla kuruldu: {self.zapret_path}")
                    return True
                else:
                    error_msg = "❌ Zapret kuruldu ancak çalıştırılabilir dosya bulunamadı"
                    if progress_callback:
                        progress_callback(error_msg, 100)
                    else:
                        print(error_msg)
                    return False
                    
        except Exception as e:
            error_msg = f"❌ Zapret kurulum hatası: {e}"
            if progress_callback:
                progress_callback(error_msg, 0)
            else:
                print(error_msg)
            return False
    
    def ensure_zapret(self, progress_callback=None):
        """Zapret'in mevcut olduğundan emin ol, yoksa indir"""
        if self.is_available():
            return True
        
        if progress_callback:
            progress_callback("📥 Zapret bulunamadı, otomatik kurulum başlatılıyor...", 0)
        else:
            print("📥 Zapret bulunamadı, otomatik kurulum başlatılıyor...")
        return self.download_zapret(progress_callback)
        
    def get_info(self):
        """Zapret bilgileri"""
        info = {
            'name': 'Zapret',
            'version': 'Bilinmiyor',
            'path': self.zapret_path,
            'available': self.is_available(),
            'running': self.is_running,
            'description': 'Zapret DPI bypass aracı - Rusya merkezli gelişmiş DPI circumvention'
        }
        
        return info
