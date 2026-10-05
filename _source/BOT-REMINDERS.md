# Renewal reminders — what the WhatsApp bot needs to do

The website's **Renewal reminders** card (About page and Help page) does not send anything to n8n.
It opens WhatsApp on the customer's phone with a ready message to **+20 111 725 0227**
(`WHATSAPP` in `content.py`). The customer taps Send, so the message comes **from their own
number**. That proves the number is theirs, and nobody can sign up someone else's phone.

## The message

English:

```
Hi Hossam TV, please send renewal reminders to this WhatsApp number.
Username: ahmed123
#remind ahmed123
```

Arabic:

```
مرحباً Hossam TV، أرجو إرسال تنبيهات التجديد على رقم الواتساب هذا.
اسم المستخدم: ahmed123
#remind ahmed123
```

The last line is the same in both languages. Match it with:

```
#remind\s+([a-z0-9._@-]{2,64})
```

The website lowercases the username, removes spaces and only allows `a-z 0-9 . _ @ -`.

## What to add in n8n

1. **In the WhatsApp message workflow:** when an incoming message matches the pattern above:
   - Check that the username exists (in your panel or customer sheet). If it doesn't, reply that the username wasn't found.
   - Save `username`, the sender's WhatsApp number and the date to a "reminders" sheet or table. If the username is already linked, replace the number.
   - Reply with a confirmation, for example: "Done ✅ We'll remind you before *ahmed123* expires."
   - Optional: only accept it if the sender is the number you originally sent the login to, or ask Hossam to approve it.
2. **A new scheduled workflow (once a day):**
   - For each linked username, get its expiry date from your panel or records.
   - When it is 3 days (and 1 day) before expiry, send the customer a WhatsApp message with the renewal options.
   - Remember which reminders were already sent so nobody gets the same one twice.
3. **Let customers stop:** if someone replies `STOP` / `إيقاف`, remove their number from the reminders list.
