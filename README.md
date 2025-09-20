## Personal Assistant Telegram Bot

This project provides a Telegram bot that reads Serbian fiscal receipt QR codes
and exports the structured receipt data into a user-managed Google Sheet. The
bot guides users through linking a sheet, scanning receipts, and preparing the
sheet with the required tables.

### Key Capabilities

- 📸 **QR Code Processing** – Accepts receipt photos, extracts the receipt URL,
  and parses items and voucher data before appending them to Google Sheets.
- 📄 **Google Sheet Management** – Lets each user link a sheet they own or join
  an existing one, and can reset/prepare tabs with default headers and
  formatting.
- 🔐 **Per-User Storage** – Stores user metadata (Telegram ID, sheet key,
  ownership) so each user’s receipts are kept in the correct sheet.

### Available Commands

| Command | Description |
| --- | --- |
| `/start` | Initializes the conversation, loads or creates the user profile, and displays the main keyboard with the available actions. |
| `/hello` | Sends a friendly greeting – useful to confirm that the bot is online. |
| `/scan_qrcode` | Starts the receipt scanning flow. The bot will ask for a QR code image, extract the receipt data, and append the parsed rows to the linked Google Sheet. Alias: `/scan_qr`. |
| `/cancel` | Cancels the current QR scanning conversation and returns to the main menu. |
| `/add_googlesheet` | Prompts the user for a Google Sheet link, saves it as the user’s primary sheet, and automatically prepares the sheet (resets tabs and headers). Alias: `/add_google_sheet_key`. |
| `/join_googlesheet` | Allows non-owners to join an existing sheet that has been shared with them. |
| `/prepare_sheet` | Re-runs the sheet preparation workflow (reset, prepare, initialize tables) for the linked sheet. |
| `/sheet_key` | Replies with the currently linked Google Sheet key. |

> **Tip:** Before scanning receipts, make sure you have linked a sheet via
> `/add_googlesheet` (owners) or `/join_googlesheet` (collaborators), and that
> the service account `personal-assistant@sheetsapi-460823.iam.gserviceaccount.com`
> has *Editor* access to the sheet.

### TODO

- [x] Remove disc IO between assistants
- [x] Rewrite exporter as class, to allow objects with per user sheets IDs
- [x] Move processed QR code tracking to DB
