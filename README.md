# Gaudete Fams Finance Tracker

A Streamlit app for the family finance tracker, backed by the [V5.1 Google Sheet](https://docs.google.com/spreadsheets/d/1vgc0UOTGvCLC0FVW5fSmoPq_CZk01xMd3K9Q3PaWvn0/edit) (`Accounts`, `Categories`, `Transactions`, `Budgets`).

This README assumes you're setting everything up from an iPhone — no laptop needed. Every step below happens in **mobile Safari/Chrome**, not the GitHub app (the GitHub mobile app can't upload a whole folder of files).

## What this app does

- **Dashboard** — net worth, this month's income/expense, spending by category (pie), budget vs actual (progress bars), account balances, recent activity.
- **Add** — a form that adapts to what you're logging: pick Expense/Income/Transfer first, and only the relevant fields appear.
- **Transactions** — browse and **void** (soft-delete) entries. Voiding never deletes the row, so nothing is ever truly lost and account balances stay correct.
- **Budgets** — set a monthly budget per category. Past months are preserved, never overwritten.

All the "hard" calculations (category lookup, month tagging, account running balance) are **formulas already living in the Google Sheet** — the app reads their computed results. This means the Sheet is always the source of truth, and you can sanity-check any number by opening it directly.

---

## 1. Get the files onto GitHub (phone-only)

1. Unzip the folder I gave you using the iPhone **Files** app (tap the `.zip` → it extracts automatically into a folder).
2. Open **github.com** in mobile Safari (not the GitHub app) and sign in.
3. Tap **+ → New repository**. Name it (e.g. `family-finance-tracker`), set it to **Private** (recommended — this holds real financial data), and create it **without** a README (you already have one).
4. On the new empty repo's page, tap **"uploading an existing file"**.
5. Tap **choose your files**, then in the file picker switch to **Browse → Files app**, navigate to the extracted folder, and select **all files and subfolders** (iOS lets you multi-select and it preserves folder paths on upload).
6. Scroll down, write a commit message like "Initial commit", and tap **Commit changes**.
7. Confirm `services/`, `utils/`, `views/`, `app.py`, `requirements.txt` etc. all show up with their folder structure intact.

> If Safari's uploader ever drops the folder structure, upload one subfolder at a time (create the folder path by typing it in the filename box, e.g. `services/accounts_service.py`, when using "Add file → Create new file" instead).

## 2. Create a Google Cloud service account (so the app can read/write the Sheet)

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → create a project (or use an existing one).
2. **APIs & Services → Library** → enable **Google Sheets API** and **Google Drive API**.
3. **APIs & Services → Credentials → Create Credentials → Service account**. Give it any name.
4. Open the new service account → **Keys → Add Key → Create new key → JSON**. This downloads a `.json` file — it contains everything needed for the `[gcp_service_account]` block in secrets.
5. Copy the service account's email (looks like `xxx@yyy.iam.gserviceaccount.com`).
6. Open your Google Sheet → **Share** → paste that email in → give it **Editor** access.

## 3. Deploy on Streamlit Community Cloud (also phone-friendly)

1. Go to [share.streamlit.io](https://share.streamlit.io) → sign in with GitHub.
2. **New app** → pick your `family-finance-tracker` repo → main file path: `app.py` → Deploy.
3. Once it's building, go to the app's **Settings → Secrets** and paste in the contents of `.streamlit/secrets.toml.example`, filled in with:
   - `app.password` — pick your own family password.
   - `sheet.url` — already filled in with your Sheet's URL.
   - `gcp_service_account.*` — copy each field from the JSON key file you downloaded in step 2. The `private_key` field needs to keep its `\n` characters exactly as in the JSON.
4. Save. The app will restart and should load the password screen.

## 4. Day-to-day use

- First screen: family password.
- Second screen: "Who's logging in?" (Suami/Istri) — asked once per browser session, auto-fills `EnteredBy` on every transaction after that.
- Everything else works the same as any web page — add it to your iPhone home screen (Safari → Share → Add to Home Screen) for an app-like icon.

## Project structure

```
family-finance-tracker/
├── app.py                      # entry point, nav, login/user gate
├── requirements.txt
├── .streamlit/
│   ├── config.toml             # theme
│   └── secrets.toml.example    # template — real secrets go in Streamlit Cloud, never committed
├── services/                   # all Google Sheets read/write logic
│   ├── sheets_client.py        # gspread connection + generic helpers
│   ├── accounts_service.py
│   ├── categories_service.py
│   ├── transactions_service.py
│   └── budgets_service.py
├── utils/
│   ├── auth.py                 # password gate + user selector
│   ├── formatting.py           # Rp currency formatting
│   └── dates.py
└── views/                      # one file per page
    ├── dashboard.py
    ├── add_transaction.py
    ├── transactions.py
    └── budgets.py
```

## Notes on the data model

- The Sheet already contains formulas for `Accounts.CurrentBalance`, `Transactions.MainCategory`, and `Transactions.TransactionMonth`. The app **re-writes** the `MainCategory`/`TransactionMonth` formulas on every new row it inserts (rather than relying on them being pre-filled), so it keeps working correctly no matter how many rows you add.
- Voiding a transaction sets `IsVoided = TRUE` rather than deleting the row — `CurrentBalance` already excludes voided rows, so balances stay accurate.
- Budgets are keyed by `SubCategory + EffectiveMonth`, so re-saving a budget this month updates it in place, while last month's figure is left untouched.
