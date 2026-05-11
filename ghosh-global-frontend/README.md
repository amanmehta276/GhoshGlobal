# Ghosh Global Services — Website

## Folder Structure
```
ghosh-global/
├── frontend/
│   ├── index.html        ← Public website (deploy to Netlify)
│   ├── admin.html        ← Admin dashboard (same Netlify deploy)
│   └── images/           ← PUT ALL YOUR IMAGES HERE
│       ├── hero-bg.jpg           ← Hero background (1920×1080px min)
│       ├── logo.png              ← Company logo (200×200px, transparent bg)
│       ├── proprietor.jpg        ← Debasis Ghosh photo (400×400px)
│       ├── favicon.ico           ← Browser tab icon (32×32px)
│       ├── favicon-32x32.png
│       └── apple-touch-icon.png  ← iOS icon (180×180px)
└── backend/              ← Deploy to Render (built next)
```

## Step 1 — Add Your Images
Place images in `frontend/images/` folder before deploying.

## Step 2 — Deploy Frontend to Netlify
1. Go to netlify.com → New site → Deploy manually
2. Drag the entire `frontend/` folder onto the deploy area
3. Site goes live at something like `ghoshglobal-xyz.netlify.app`

## Step 3 — Deploy Backend to Render (Python)
(Backend code coming separately)
1. Push `backend/` folder to a GitHub repo
2. Go to render.com → New Web Service → connect GitHub repo
3. Set environment: Python, start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add env variable: `ADMIN_PASSWORD=your_secret_password`
5. Copy the Render URL (e.g. `https://ghosh-global-api.onrender.com`)

## Step 4 — Connect Frontend to Backend
In BOTH `index.html` and `admin.html`, find this line near the bottom:
```js
const API_BASE = 'https://your-render-app.onrender.com';
```
Replace with your actual Render URL.

## Step 5 — Connect Custom Domain
1. Buy `ghoshglobal.com` on Namecheap
2. In Netlify: Site Settings → Domain → Add custom domain
3. Copy Netlify's nameservers → paste into Namecheap
4. Wait 1–24 hours → site live at ghoshglobal.com

## Step 6 — Set Up Business Emails (Zoho Free)
1. Go to zoho.com/mail → Free plan
2. Add domain `ghoshglobal.com`
3. Add MX records to Namecheap DNS (Zoho will show you exactly what to add)
4. Create 5 emails:
   - debasis@ghoshglobal.com
   - info@ghoshglobal.com
   - sales@ghoshglobal.com
   - service@ghoshglobal.com
   - accounts@ghoshglobal.com

## Admin Panel Access
- URL: `https://ghoshglobal.com/admin.html`
- Password: whatever you set as ADMIN_PASSWORD on Render
- Can update: clients, partners, turnover, images, view enquiries
