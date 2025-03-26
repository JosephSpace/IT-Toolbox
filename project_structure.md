# IT Toolbox Projesi Dosya Yapısı

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

## Dosya ve Klasörlerin Açıklamaları

### Ana Klasör Dosyaları
- **app.py**: Flask web uygulamasının ana dosyası. Tüm route'lar ve uygulama mantığı burada tanımlanmıştır.
- **models.py**: Kullanıcı modeli ve repository sınıflarını içerir.
- **requirements.txt**: Projenin bağımlılıklarını listeler (Flask, python-ldap, flask-login, vb.).
- **README.md**: Proje hakkında genel bilgiler ve kategori listesi.
- **users.db**: SQLite veritabanı dosyası, kullanıcı bilgilerini ve aktivitelerini saklar.

### Static Klasörü
- **auth.css**: Kimlik doğrulama sayfalarının stil dosyası.
- **auth.js**: Kimlik doğrulama sayfalarının JavaScript dosyası.
- **avatar.svg**: Varsayılan profil resmi.
- **logo.svg**: Uygulama logosu.
- **profiles.css**: Profil sayfasının stil dosyası.
- **styles.css**: Genel stil dosyası, tüm sayfalarda kullanılan ortak stiller.

#### Static/Data Klasörü
- **programs.json**: Programlar ve kategoriler hakkında bilgileri içeren JSON dosyası.

#### Static/Uploads Klasörü
- Kullanıcıların profil resimleri bu klasörde saklanır.

### Templates Klasörü
- **auth.html**: Giriş yapma ve kayıt olma formlarını içeren sayfa.
- **edit_user.html**: Kullanıcı bilgilerini düzenleme sayfası.
- **index.html**: Ana sayfa, program kategorilerini ve programları listeler.
- **manage_users.html**: Admin kullanıcılar için kullanıcı yönetim sayfası.
- **profiles.html**: Kullanıcı profil sayfası.
- **security.html**: Güvenlik ayarları sayfası (2FA, aktivite günlükleri, vb.).
- **setup_2fa.html**: İki faktörlü kimlik doğrulama kurulum sayfası.