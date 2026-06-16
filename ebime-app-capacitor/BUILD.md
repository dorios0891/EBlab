# EBIME — Generar el APK

Tu app web ya está completa. Aquí tienes **dos caminos** para obtener el `.apk` instalable. No requieren cambios en el código.

---

## Opción A · La más rápida (sin instalar nada) — PWABuilder

Como la app ya es una PWA válida (manifest + service worker + íconos), puedes empaquetarla en la web:

1. Sube los archivos de `www/` a tu GitHub Pages (o cualquier hosting HTTPS), de modo que el `index.html` quede en la raíz y el sitio abra, por ejemplo, en `https://ebimelab.github.io/`.
2. Entra a **https://www.pwabuilder.com** y pega esa URL.
3. Pulsa **Package for stores → Android**.
4. Descarga el paquete: incluye el **APK firmado** (para instalar/probar) y el **.aab** (para Play Store), más un `assetlinks.json`.
5. (Opcional, para que la app no muestre barra de URL) sube el `assetlinks.json` que te da PWABuilder a `https://TU-DOMINIO/.well-known/assetlinks.json`.

Esto produce una **TWA (Trusted Web Activity)** firmada en minutos. Es la vía recomendada.

---

## Opción B · Build local con Capacitor + Android Studio

Genera el APK en tu máquina a partir de este proyecto.

### Requisitos
- **Node.js LTS** (18+)
- **Android Studio** con el SDK de Android y un JDK 17 (Android Studio lo trae).

### Pasos
```bash
cd ebime-app
npm install                 # instala Capacitor
npx cap add android         # crea el proyecto Android nativo (carpeta android/)

# (opcional) genera íconos/splash a partir de resources/
npx capacitor-assets generate --android

npx cap sync                # copia www/ al proyecto Android
npx cap open android        # abre el proyecto en Android Studio
```

En Android Studio:
- **APK de prueba (debug):** `Build → Build Bundle(s) / APK(s) → Build APK(s)`.
  Resultado: `android/app/build/outputs/apk/debug/app-debug.apk`
- **APK firmado (release):** `Build → Generate Signed Bundle / APK… → APK`, crea/usa tu keystore y firma.

O por línea de comandos (debug):
```bash
cd android
./gradlew assembleDebug      # Windows: gradlew.bat assembleDebug
# APK en: android/app/build/outputs/apk/debug/app-debug.apk
```

### Notas
- `appId`: `co.ebime.vascular` y `appName`: `EBIME` (editables en `capacitor.config.json`).
- El service worker funciona dentro del WebView; la app abre offline tras el primer arranque porque los assets viajan dentro del APK (`www/`).
- Para Play Store usa **.aab firmado** (`Build → Generate Signed Bundle… → Android App Bundle`).

---

## Contenido de este proyecto
```
ebime-app/
├─ package.json              # dependencias Capacitor
├─ capacitor.config.json     # appId, nombre, webDir
├─ www/                      # tu app (index.html, manifest, sw.js, íconos)
└─ resources/
   ├─ icon.png               # 1024×1024 para generar íconos
   └─ icon-foreground.png    # versión a sangre (adaptive icon)
```
