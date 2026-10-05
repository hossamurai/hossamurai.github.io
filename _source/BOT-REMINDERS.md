# Renewal reminders — website form + n8n

The **Renewal reminders** card (About page and Help page) links an account to a WhatsApp number.
The customer can also add a friend's account on the friend's number.

- The customer types **username + password + WhatsApp number**. All three are always required,
  because some usernames are shared by more than one account. This is the same rule the WhatsApp
  bot uses in its "Link Account" step.
- The form posts to the n8n webhook **`site-link`** (`N8N_WEBHOOK` in `content.py`). It uses the same
  request style as the order form: `p=<JSON>` in a form-encoded POST.
- **All data stays in n8n.** The website stores nothing (no cookies, no browser storage, nothing in this
  repo). It sends the three fields once, shows the answer, and clears the password box.
- Never commit the n8n workflow exports or the Customers table to this repo. It is public, and the
  exports contain your WhatsApp API key.

## What the webhook does (Website Data API workflow → "Renewal reminders form" nodes)

1. **Read Link Request:** checks the request came from hossamservices.com or hossamurai.github.io,
   cleans the username (lowercase, no spaces) and turns the phone into international digits. Egyptian
   local numbers like `01012345678` become `201012345678`.
2. **Limits:** 8 tries per internet connection per day, 300 for the whole site. These are counted in
   `AI_Rate_Limit` with `sender = link:<ip>`.
3. **Find Website Account / Match Website Account:** gets all Customers rows with that username, then
   keeps the one whose password matches. This uses the bot's "Check Password" rule (not case-sensitive;
   leading zeros ignored for number-only passwords).
4. **Found:** saves the number on that account (`whatsapp_id = <digits>@s.whatsapp.net`, `phone = <digits>`).
   It then sends a WhatsApp confirmation to that number from the bot, logs a `link` event in
   `Bot_Events`, and answers `{ ok: true, status: "linked" }`.
   **Not found:** answers `{ ok: false, status: "not_found" }`.
5. It never sends account details (plan, expiry, password) back to the website.

The existing **Daily Reminder Check** (13:00) already messages every account with a `whatsapp_id`
0–5 days before expiry, so there is nothing more to set up for the reminders themselves.

Website answers: `linked`, `not_found`, `limited`, `invalid` (bad input or wrong origin, HTTP 400).
If n8n can't be reached, the form says so and points to the bot's WhatsApp, +20 101 311 3996
(`BOT_WHATSAPP`).
