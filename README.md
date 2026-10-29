# Telemetri Seri Arayüzü

Bu uygulama, bilgisayara USB-UART dönüştürücüsü ile bağlanan iki telemetri modülüyle
seri bağlantı kurar. Her telemetri için COM portu, baud hızı, veri biti, parite,
dur biti ve akış kontrolü seçilebilir. Gelen veri HEX ve okunabilir metin olarak
gösterilir; mesaj gönderme alanından A veya B portuna UTF-8 metin gönderilebilir.

## Calistirma

Windows'ta Python 3 kurulu olmalıdır. PowerShell'de proje klasöründe:

```powershell
py -m pip install -r requirements.txt
py telemetry_gui.py
```

Uygulama portları otomatik bulur; modüllerin seri ayarlarını cihaz dokümanındaki
değerlere göre seçin. A ve B'ye bağlandıktan sonra gönderen telemetriyi seçip
mesajı yazın. CR+LF seçeneği açıksa mesajın sonuna satır sonu eklenir.

Bu araç genel seri terminalidir: seçilen COM portuna ham UTF-8 metin yazar ve
gelen baytları izler. Telemetri modülleri kablosuz olarak eşleştirilmişse, bir
modeme gönderilen mesaj diğer eşleştirilmiş uçtan alınabilir. Uygulama A'dan B'ye
otomatik seri köprüsü kurmaz; RF ayarlarının modele özel okunması/yazılması bu
genel seri arayüzünün kapsamı dışındadır. MAVLink gibi ikili protokoller için
metin alanı yerine protokole uygun mesaj aracı kullanılmalıdır.
