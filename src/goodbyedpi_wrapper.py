"""
GoodbyeDPI Wrapper
GoodbyeDPI executable'ını Python üzerinden yönetme
"""

import os
import sys
import subprocess
import threading
import time
import requests
import zipfile
import tempfile
from pathlib import Path
from typing import Optional, List, Dict


class GoodbyeDPIWrapper:
    def __init__(self):
        """GoodbyeDPI wrapper'ı başlat"""
        self.base_dir = Path(__file__).parent.parent
        self.external_dir = self.base_dir / "external"
        self.goodbyedpi_dir = self.external_dir / "goodbyedpi"
        
        # Önce x86_64 sonra x86 sonra genel arama
        possible_paths = [
            self.goodbyedpi_dir / "goodbyedpi-0.2.2" / "x86_64" / "goodbyedpi.exe",
            self.goodbyedpi_dir / "goodbyedpi-0.2.2" / "x86" / "goodbyedpi.exe",
            self.goodbyedpi_dir / "goodbyedpi.exe"
        ]
        
        self.goodbyedpi_exe = None
        for path in possible_paths:
            if path.exists():
                self.goodbyedpi_exe = path
                break
        
        # Varsayılan path (eğer hiçbiri yoksa)
        if not self.goodbyedpi_exe:
            self.goodbyedpi_exe = possible_paths[0]  # x86_64 öncelikli
        
        self.process = None
        self.running = False
        self.log_thread = None
        
        # GoodbyeDPI parametreleri
        self.default_params = [
            "-5",  # Modern modeset (most recommended)
            "--dns-addr", "77.88.8.8",
            "--dns-port", "1253",
            "--dnsv6-addr", "2a02:6b8::feed:0ff",
            "--dnsv6-port", "1253"
        ]
        
        # İndirme URL'si
        self.download_url = "https://github.com/ValdikSS/GoodbyeDPI/releases/latest/download/goodbyedpi-0.2.2.zip"
        
    def is_available(self) -> bool:
        """GoodbyeDPI mevcut mu kontrol et"""
        if not self.goodbyedpi_exe:
            return False
        return self.goodbyedpi_exe.exists()
        
    def download_goodbyedpi(self, progress_callback=None) -> bool:
        """GoodbyeDPI'yi GitHub'dan indir"""
        try:
            if progress_callback:
                progress_callback("GoodbyeDPI indiriliyor...", 0)
            else:
                print("GoodbyeDPI indiriliyor...")
            
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
                # İndir
                response = requests.get(self.download_url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            if progress_callback:
                                progress_callback(f"İndiriliyor... {percent:.1f}%", percent)
                            else:
                                print(f"\rİndirme: {percent:.1f}%", end='')
                
                tmp_path = tmp_file.name
                
            if progress_callback:
                progress_callback("Dosya çıkartılıyor...", 95)
            else:
                print(f"\nDosya çıkartılıyor: {self.goodbyedpi_dir}")
            
            # Klasörü oluştur
            self.goodbyedpi_dir.mkdir(parents=True, exist_ok=True)
            
            # ZIP'i çıkart
            with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                zip_ref.extractall(self.goodbyedpi_dir)
            
            # Geçici dosyayı sil
            os.unlink(tmp_path)
            
            # Executable'ı bul
            exe_files = []
            # x86_64 klasöründe ara (öncelik)
            x64_path = self.goodbyedpi_dir / "goodbyedpi-0.2.2" / "x86_64" / "goodbyedpi.exe"
            if x64_path.exists():
                exe_files.append(x64_path)
            
            # x86 klasöründe ara
            x86_path = self.goodbyedpi_dir / "goodbyedpi-0.2.2" / "x86" / "goodbyedpi.exe"
            if x86_path.exists():
                exe_files.append(x86_path)
                
            # Genel arama (önceki aramalar boşsa)
            if not exe_files:
                exe_files = list(self.goodbyedpi_dir.rglob("goodbyedpi.exe"))
                
            # Dosya bulundu mu kontrol et
            if exe_files:
                # İlk bulunanı kullan (x64 öncelikli)
                src_exe = exe_files[0]
                self.goodbyedpi_exe = src_exe  # Path'i güncelle
                
                if progress_callback:
                    progress_callback("✅ GoodbyeDPI başarıyla indirildi!", 100)
                else:
                    print(f"✅ GoodbyeDPI başarıyla indirildi: {self.goodbyedpi_exe}")
                return True
            else:
                if progress_callback:
                    progress_callback("❌ GoodbyeDPI executable bulunamadı!", 100)
                else:
                    print("❌ GoodbyeDPI executable bulunamadı!")
                return False
                
        except Exception as e:
            error_msg = f"❌ GoodbyeDPI indirme hatası: {e}"
            if progress_callback:
                progress_callback(error_msg, 0)
            else:
                print(error_msg)
            return False
            
    def ensure_goodbyedpi(self, progress_callback=None) -> bool:
        """GoodbyeDPI'nin mevcut olduğundan emin ol"""
        # İlk kontrol - mevcut path'te var mı?
        if self.is_available():
            return True
            
        # Mevcut değil, indirmeye çalış
        if progress_callback:
            progress_callback("GoodbyeDPI bulunamadı. İndiriliyor...", 0)
        else:
            print("GoodbyeDPI bulunamadı. İndiriliyor...")
            
        # İndir ve path'i güncelle
        success = self.download_goodbyedpi(progress_callback)
        
        if success:
            # İndirme başarılıysa path'i yeniden kontrol et ve güncelle
            self._update_executable_path()
            
        return success
    
    def _update_executable_path(self):
        """Executable path'ini güncelle"""
        possible_paths = [
            self.goodbyedpi_dir / "goodbyedpi-0.2.2" / "x86_64" / "goodbyedpi.exe",
            self.goodbyedpi_dir / "goodbyedpi-0.2.2" / "x86" / "goodbyedpi.exe",
            self.goodbyedpi_dir / "goodbyedpi.exe"
        ]
        
        for path in possible_paths:
            if path.exists():
                self.goodbyedpi_exe = path
                break
        
    def start(self, params: Optional[List[str]] = None, blacklist_file: Optional[str] = None) -> bool:
        """GoodbyeDPI'yi başlat"""
        if self.running:
            return False
            
        if not self.ensure_goodbyedpi():
            return False
            
        try:
            # Admin yetkisi kontrolü
            if not self._is_admin():
                print("⚠️  UYARI: GoodbyeDPI yönetici yetkileri gerektirir.")
                print("💡 Çözüm:")
                print("   1. PowerShell'i 'Yönetici olarak çalıştır'")
                print("   2. Bu programı yeniden başlatın")
                print("   3. Veya programın kısayoluna sağ tıklayıp 'Yönetici olarak çalıştır'")
                print("\n🔄 Şimdi admin olmadan test modunda çalıştırılacak...")
                
                # Admin olmadan test et
                return self._start_test_mode(cmd)
            
            # Executable kontrolü
            if not self.goodbyedpi_exe.exists():
                print(f"❌ GoodbyeDPI executable bulunamadı: {self.goodbyedpi_exe}")
                return False
            
            if not os.access(self.goodbyedpi_exe, os.X_OK):
                print(f"❌ GoodbyeDPI executable çalıştırma izni yok: {self.goodbyedpi_exe}")
                return False
            
            print(f"✅ GoodbyeDPI executable mevcut: {self.goodbyedpi_exe}")
            
            # Komut oluştur
            cmd = [str(self.goodbyedpi_exe)]
            
            if params:
                cmd.extend(params)
            else:
                cmd.extend(self.default_params)
                
            # Blacklist dosyası varsa ekle
            if blacklist_file and os.path.exists(blacklist_file):
                cmd.extend(["--blacklist", blacklist_file])
            else:
                cmd.extend(["--blacklist", blacklist_file])
                #print("⚠️  UYARI: Blacklist dosyası belirtilmedi veya bulunamadı.")
                #print("   Tüm trafiğe DPI bypass uygulanacak (daha fazla kaynak kullanabilir).")
            
            print(f"GoodbyeDPI başlatılıyor: {' '.join(cmd)}")
            
            # Process'i başlat
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            
            self.running = True
            
            # Log thread'i başlat
            self.log_thread = threading.Thread(target=self._log_output, daemon=True)
            self.log_thread.start()
            
            # Kısa bekleme - başlatma kontrolü
            time.sleep(3)
            
            if self.process.poll() is None:
                print("✅ GoodbyeDPI başarıyla başlatıldı")
                return True
            else:
                # Hata detaylarını al
                exit_code = self.process.returncode
                try:
                    output = self.process.stdout.read()
                    print(f"❌ GoodbyeDPI başlatılamadı (Exit code: {exit_code})")
                    if output:
                        print(f"🔍 Hata çıktısı: {output}")
                except:
                    print(f"❌ GoodbyeDPI başlatılamadı (Exit code: {exit_code})")
                
                self.running = False
                return False
                
        except Exception as e:
            print(f"❌ GoodbyeDPI başlatma hatası: {e}")
            return False
            
    def stop(self) -> bool:
        """GoodbyeDPI'yi durdur"""
        if not self.running or not self.process:
            return True
            
        try:
            self.running = False
            
            # Process'i sonlandır
            self.process.terminate()
            
            # Kısa bekleme
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Zorla sonlandır
                self.process.kill()
                self.process.wait()
                
            print("✅ GoodbyeDPI durduruldu")
            return True
            
        except Exception as e:
            print(f"❌ GoodbyeDPI durdurma hatası: {e}")
            return False
            
    def is_running(self) -> bool:
        """GoodbyeDPI çalışıyor mu"""
        if not self.process or not self.running:
            return False
        return self.process.poll() is None
        
    def get_status(self) -> Dict[str, any]:
        """GoodbyeDPI durumunu al"""
        return {
            'available': self.is_available(),
            'running': self.is_running(),
            'exe_path': str(self.goodbyedpi_exe),
            'admin_required': not self._is_admin()
        }
        
    def create_blacklist_file(self, sites: List[str]) -> str:
        """
        Site listesi için GoodbyeDPI blacklist dosyası oluştur
        
        ÖNEMLI: GoodbyeDPI blacklist mantığı:
        - Blacklist'te OLAN sitelere DPI bypass uygulanır
        - Blacklist'te OLMAYAN siteler normal erişim yapar
        """
        blacklist_path = self.external_dir / "blacklist.txt"
        
        try:
            with open(blacklist_path, 'w', encoding='utf-8') as f:
                f.write("# GoodbyeDPI Blacklist - DPI bypass uygulanacak siteler\n")
                f.write("# Bu listedeki sitelere bypass uygulanır, diğerleri normal erişim\n\n")
                
                for site in sites:
                    # Domain'i temizle
                    domain = site.strip()
                    if domain.startswith(('http://', 'https://')):
                        from urllib.parse import urlparse
                        parsed = urlparse(domain)
                        domain = parsed.hostname
                    
                    # www. prefix'ini kaldır
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    
                    if domain:  # Boş değilse ekle
                        f.write(f"{domain}\n")
                    
            print(f"📝 GoodbyeDPI blacklist dosyası oluşturuldu: {blacklist_path}")
            print(f"   → Listedeki {len(sites)} siteye DPI bypass uygulanacak")
            return str(blacklist_path)
            
        except Exception as e:
            print(f"Blacklist dosyası oluşturma hatası: {e}")
            return ""
            
    def _is_admin(self) -> bool:
        """Windows admin yetkisi kontrolü"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def _start_test_mode(self, cmd) -> bool:
        """Admin yetkisi olmadan test modu"""
        print("🧪 Test Modu: GoodbyeDPI'yi admin olmadan başlatma denemesi...")
        
        try:
            # Önce executable'ın çalışıp çalışmadığını test et
            test_cmd = [str(self.goodbyedpi_exe), '--help']
            test_result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if test_result.returncode == 0:
                print("✅ GoodbyeDPI executable çalışabiliyor")
                print("⚠️  Ancak DPI bypass için admin yetkisi şart!")
                
                # Simüle edilmiş çalışma
                self.running = True
                print("🔄 Test modunda çalışıyor (gerçek bypass yok)")
                return True
            else:
                print(f"❌ GoodbyeDPI executable test hatası: {test_result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Test modu hatası: {e}")
            return False
            
    def _log_output(self):
        """GoodbyeDPI çıktısını logla"""
        if not self.process:
            return
            
        try:
            while self.running and self.process.poll() is None:
                line = self.process.stdout.readline()
                if line:
                    print(f"[GoodbyeDPI] {line.strip()}")
        except:
            pass
            
    def get_recommended_params_for_country(self, country_code: str = "TR") -> List[str]:
        """Ülkeye göre önerilen parametreler"""
        country_params = {
            "RU": ["-1", "--dns-addr", "77.88.8.8", "--dns-port", "1253"],
            "IR": ["-9", "--dns-addr", "178.22.122.100"],
            "CN": ["-6", "--dns-addr", "8.8.8.8"],
            "TR": ["-5", "--dns-addr", "77.88.8.8", "--dns-port", "1253"],  # Türkiye için
            "DEFAULT": ["-5", "--dns-addr", "77.88.8.8", "--dns-port", "1253"]
        }
        
        return country_params.get(country_code, country_params["DEFAULT"])
        
    def test_connection(self, url: str = "https://www.google.com") -> bool:
        """Bağlantı testi"""
        try:
            import requests
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_info(self):
        """GoodbyeDPI bilgileri"""
        return {
            'name': 'GoodbyeDPI',
            'version': '0.2.2',
            'path': str(self.goodbyedpi_exe) if self.goodbyedpi_exe else 'Yüklenmemiş',
            'available': self.goodbyedpi_exe.exists() if self.goodbyedpi_exe else False,
            'running': self.is_running(),
            'description': 'DPI circumvention aracı - Türkiye için optimize edilmiş'
        }
