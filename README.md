
![Kayıt 2025-03-27 013519](https://github.com/user-attachments/assets/3f5b6e68-219a-4aa2-b937-65a0b34c6231)

This GitHub repository contains a list of various software and tools that IT professionals may need to make their daily work easier. The content is divided into various categories such as system administration, security, network management, data analysis, and more. This resource is designed as a useful reference source for those working in the IT field.

# The content is divided into the following categories:

1. System Tools
2. Security Software
3. Browsers
4. Office and Productivity Tools
5. Developer Tools
    
## This resource is a useful reference for those working in the IT field.

## Setup

`pip install -r requirements.txt` You can download all libraries quickly and effortlessly.

```
pip install requirements.txt
```
When you run the `app.py` file, it opens a page for you. When you **Ctrl + Left Click** on the page, it redirects you to the login page.

```
python app.py
```

After the server starts, open any browser window and type the following URL: `http://127.0.0.1:5000/`. You will then be redirected to the homepage.

### Project Directory Structure
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

---
## License

MIT

The included Freeboard code is redistributed per its MIT License.
