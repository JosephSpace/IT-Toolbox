
![Kayıt 2025-03-27 013519](https://github.com/user-attachments/assets/817f66c1-72b1-40dd-b059-2c9ee2ec7118)

# IT Toolbox

Bu GitHub deposu, IT profesyonellerinin günlük işlerini kolaylaştırmak için gereksinim duyabilecekleri çeşitli yazılım ve araçların bir listesini içerir. İçerik, sistem yönetimi, güvenlik, ağ yönetimi, veri analizi ve daha fazlası gibi çeşitli kategorilere ayrılmıştır. Bu kaynak, IT alanında çalışanlar için faydalı olabilecek bir referans kaynağı olarak tasarlanmıştır.

# The content is divided into the following categories:

* System Tools
* Security Software
* Browsers
* Developer Tools
* Multimedia Tools
* Virtualization Tools
* Business Intelligence Tools
    
## This resource is a useful reference for those working in the IT field.

## Setup

`pip install -r requirements.txt` This download is designed for you to download all libraries at once.

```
pip install -r requirements.txt
```
When you run the `app.py` file, it opens a page for you. When you **Ctrl + Left Click** on the page, it redirects you to the login page.

```
cd it-toolbox-main
python app.py
```

After the server starts, open any browser window and type the following URL: `http://127.0.0.1:5000/`. You will then be redirected to the homepage.

Mail address: hi@admin.com Password: 123 

## Project Structure

```
it-toolbox-main/                # Ana proje klasörü
├── app.py                     # Ana uygulama dosyası (Flask web uygulaması)
├── models.py                  # Kullanıcı modeli ve repository sınıfları
├── requirements.txt           # Proje bağımlılıkları
├── README.md                  # Proje açıklaması
├── users.db                   # SQLite veritabanı dosyası
├── static/                    # Statik dosyalar klasörü
│   ├── auth.css               # Kimlik doğrulama sayfası stilleri
│   ├── auth.js                # Kimlik doğrulama sayfası JavaScript kodları
│   ├── avatar.svg             # Varsayılan profil resmi
│   ├── logo.svg               # Uygulama logosu
│   ├── profiles.css           # Profil sayfası stilleri
│   ├── styles.css             # Genel stil dosyası
│   ├── data/                  # Veri dosyaları klasörü
│   │   └── programs.json      # Programlar ve kategoriler verisi
│   └── uploads/               # Kullanıcı yüklemeleri klasörü
│       ├── user_1.jpg         # Örnek kullanıcı profil resmi
│       └── user_2.jpg         # Örnek kullanıcı profil resmi
└── templates/                 # HTML şablonları klasörü
    ├── auth.html              # Kimlik doğrulama sayfası (giriş/kayıt)
    ├── edit_user.html         # Kullanıcı düzenleme sayfası
    ├── index.html             # Ana sayfa
    ├── manage_users.html      # Kullanıcı yönetim sayfası (admin)
    ├── profiles.html          # Kullanıcı profil sayfası
    ├── security.html          # Güvenlik ayarları sayfası
    └── setup_2fa.html         # İki faktörlü kimlik doğrulama kurulum sayfası
```
## Maintainer

https://github.com/JosephSpace

## Credits

https://github.com/JosephSpace/IT-Toolbox

## Contact

- İnstagram: https://www.instagram.com/joseph.ddf/
- LinkedIn: https://www.linkedin.com/in/yusuf-aşkın-56015b232/
- Mail: yusufaliaskin@gmail.com

MIT

The included Freeboard code is redistributed per its MIT License.
