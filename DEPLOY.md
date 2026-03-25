# Specific Guide: Vercel (Frontend) + Render (Backend)

Follow these exact steps to get your AI Agent live.

## 1. Backend: Deploying to Render.com
Render is great for hosting your FastAPI backend.

### Steps:
1.  **Sign up** at [Render.com](https://render.com/) and connect your GitHub.
2.  **Create a New Web Service**:
    - Select your `nextdot-agent` repository.
    - **Name**: `nextdot-backend` (or similar).
    - **Language**: `Python 3`.
    - **Build Command**: `pip install -r requirements.txt`.
    - **Start Command**: `python server.py`.
3.  **Environment Variables**: Go to the **Environment** tab and add:
    - `ANTHROPIC_API_KEY`: `your_key_here`
    - `GEMINI_API_KEY`: `your_key_here`
    - `OPENAI_API_KEY`: `your_key_here`
    - `PORT`: `10000` (Render usually sets this automatically, but our code will pick it up).
4.  **Copy the URL**: Once deployed, Render will give you a URL like `https://nextdot-backend.onrender.com`. **Save this.**

---

## 2. Frontend: Deploying to Vercel
Vercel is the best home for Next.js apps.

### Steps:
1.  **Sign up** at [Vercel.com](https://vercel.com/) and connect your GitHub.
2.  **Import Project**:
    - Select your `nextdot-agent` repository.
3.  **Project Settings**:
    - **Framework Preset**: `Next.js`.
    - **Root Directory**: Click "Edit" and select the `frontend` folder.
4.  **Environment Variables**: Add a new variable:
    - **Key**: `NEXT_PUBLIC_API_URL`
    - **Value**: `https://nextdot-backend.onrender.com` (The URL you copied from Render).
5.  **Deploy**: Click "Deploy". Vercel will build and launch your frontend.

---

## 3. Important Notes
- **CORS**: If you see "Access Denied" or CORS errors, check `server.py`. I've set it to `allow_origins=["*"]`, which works everywhere but is "open". For better security, you can change `*` to your Vercel URL later.
- **Sleep/Spin up**: Render's free tier "sleeps" after 15 minutes of inactivity. The first request after a long time might take 30-60 seconds to "wake up". This is normal for free hosting.
