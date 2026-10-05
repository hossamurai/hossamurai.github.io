# Renewal reminders — what the WhatsApp bot needs to do

The website's **Renewal reminders** card (About page and Help page) does not send anything to n8n.
It opens WhatsApp on the customer's phone with a ready message to the **bot's number,
+20 101 311 3996** (`BOT_WHATSAPP` in `content.py`). Every other WhatsApp link on the site still goes to
the main number, +20 111 725 0227. The customer taps Send, so the message comes **from their own
number**. That proves the number is theirs, and nobody can sign up someone else's phone.

The card asks for the **username and the password**, because some usernames are shared by more
than one account. Use the pair to find the right account.

## The message

English:

```
Hi Hossam TV, please send renewal reminders to this WhatsApp number.
Username: ahmed123
Password: 4Xk9pQ
#remind ahmed123 4Xk9pQ
```

Arabic:

```
مرحباً Hossam TV، أرجو إرسال تنبيهات التجديد على رقم الواتساب هذا.
اسم المستخدم: ahmed123
كلمة المرور: 4Xk9pQ
#remind ahmed123 4Xk9pQ
```

The last line is the same in both languages. Match it with:

```
#remind\s+([a-z0-9._@-]{2,64})\s+(\S{1,64})
```

- Group 1 is the username. The website lowercases it, removes spaces and only allows `a-z 0-9 . _ @ -`.
- Group 2 is the password, exactly as typed with spaces removed. Its case is kept. If your panel's
  passwords are lowercase, compare without case so a capital letter from the phone keyboard
  still matches.

## What to add in n8n

1. **In the bot's WhatsApp message workflow (+20 101 311 3996):** when an incoming message matches the pattern above:
   - Look up the account by **username and password together** (in your panel or customer sheet).
     If no account matches, reply that the details weren't found and ask them to check.
   - Save the account (its unique ID from the panel, plus username), the sender's WhatsApp number
     and the date to a "reminders" sheet or table. **Don't store the password there.** It's only
     needed for the lookup. If the account is already linked, replace the number.
   - Reply with a confirmation, for example: "Done ✅ We'll remind you before *ahmed123* expires."
2. **A new scheduled workflow (once a day):**
   - For each linked account, get its expiry date from your panel or records.
   - When it is 3 days (and 1 day) before expiry, send the customer a WhatsApp message with the
     renewal options.
   - Remember which reminders were already sent so nobody gets the same one twice.
3. **Let customers stop:** if someone replies `STOP` / `إيقاف`, remove their number from the
   reminders list.
