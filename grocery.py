import tkinter as tk
from tkinter import ttk, messagebox
import google.generativeai as genai
import json

# ================== CONFIG ==================
# GET YOUR FREE KEY HERE → https://aistudio.google.com/app/apikey
GEMINI_API_KEY = "AQ.Ab8RN6IBsBBlDRd1nj3VSaoM_93MfZefxwI2-dpREn8J9MNNPw" # ←←← REPLACE THIS

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# ================== HARDCODED DATA ==================
products = [
{"name": "flour", "site": "BigBasket", "price": 120},
{"name": "flour", "site": "Amazon", "price": 140},
{"name": "flour", "site": "Blinkit", "price": 115},
{"name": "sugar", "site": "BigBasket", "price": 50},
{"name": "sugar", "site": "Amazon", "price": 55},
{"name": "sugar", "site": "Blinkit", "price": 52},
{"name": "baking powder", "site": "BigBasket", "price": 35},
{"name": "baking powder", "site": "Amazon", "price": 40},
{"name": "baking powder", "site": "Blinkit", "price": 30},
{"name": "butter", "site": "BigBasket", "price": 200},
{"name": "butter", "site": "Amazon", "price": 210},
{"name": "butter", "site": "Blinkit", "price": 190},
{"name": "soap", "site": "BigBasket", "price": 40},
{"name": "soap", "site": "Amazon", "price": 45},
{"name": "soap", "site": "Blinkit", "price": 38},
{"name": "shampoo", "site": "BigBasket", "price": 300},
{"name": "shampoo", "site": "Amazon", "price": 320},
{"name": "shampoo", "site": "Blinkit", "price": 290},
]

# ================== AI SMART SEARCH ==================
def ai_smart_search(query: str, budget_str: str):
products_json = json.dumps(products, indent=2)

prompt = f"""You are an expert grocery shopping assistant.
Available products (only use these, never invent new items):

{products_json}

User request: "{query}"
Budget: {budget_str if budget_str else "No budget specified"} ₹

Tasks:
1. Understand what the user actually needs.
2. Match only items from the database above.
3. For every matched item, find the cheapest option.
4. Calculate total cost.
5. Check budget if provided.

Return **ONLY** valid JSON (no markdown, no extra text) with this exact structure:

{{
"success": true,
"items": [
{{
"name": "item name",
"best_site": "site name",
"best_price": number,
"all_options": [
{{"site": "site", "price": number}},
...
]
}}
],
"total_cost": number,
"budget_analysis": "WITHIN BUDGET" or "OVER BUDGET by ₹X" or "NO BUDGET SPECIFIED"
}}

If nothing matches or error: {{"success": false, "message": "short explanation"}}
"""

try:
response = model.generate_content(
prompt,
generation_config=genai.GenerationConfig(
response_mime_type="application/json"
)
)
return json.loads(response.text.strip())
except Exception as e:
print(f"Gemini Error: {e}")
return {"success": False, "message": "AI service unavailable. Please check your API key."}


# ================== UI & SEARCH ==================
def search_products():
query = search_entry.get().strip()
budget_str = budget_entry.get().strip()

if not query:
messagebox.showwarning("Input Error", "Please enter what you need!")
return

result_text.delete(1.0, tk.END)
result_text.insert(tk.END, "🪄 AI is analyzing the best deals...\n")
root.update_idletasks()

ai_result = ai_smart_search(query, budget_str)

result_text.delete(1.0, tk.END)

if not ai_result.get("success", False):
result_text.insert(tk.END, f"❌ {ai_result.get('message', 'Unknown error')}")
return

items = ai_result.get("items", [])
if not items:
result_text.insert(tk.END, "❌ No matching items found in our database.")
return

# Display each item
for item in items:
result_text.insert(tk.END, f"📦 {item['name'].upper()}\n", "header")

for opt in item.get("all_options", []):
tag = "best" if opt["site"] == item["best_site"] else ""
result_text.insert(tk.END, f" • {opt['site']}: ₹{opt['price']}\n", tag)

result_text.insert(
tk.END,
f" ✅ Best Deal: {item['best_site']} (₹{item['best_price']})\n\n"
)

# Summary
total = ai_result.get("total_cost", 0)
result_text.insert(tk.END, "-" * 40 + "\n")
result_text.insert(tk.END, f"💰 TOTAL ESTIMATE: ₹{total}\n", "total")

budget_analysis = ai_result.get("budget_analysis", "")
if "WITHIN" in budget_analysis:
result_text.insert(tk.END, f"🟢 {budget_analysis}", "success")
elif "OVER" in budget_analysis:
result_text.insert(tk.END, f"🔴 {budget_analysis}", "error")
else:
result_text.insert(tk.END, budget_analysis)


# ================== GUI SETUP ==================
# ---------------- UI SETUP (DARK MODE) ---------------- #
root = tk.Tk()
root.title("🛒 Smart Grocery Assistant")
root.geometry("560x750")
root.configure(bg="#111827") # Deep Navy/Black Background

# Header
main_frame = tk.Frame(root, bg="#111827", padx=30, pady=20)
main_frame.pack(expand=True, fill="both")

tk.Label(main_frame, text="Smart Grocery Optimizer", font=("Helvetica", 22, "bold"),
bg="#111827", fg="#60a5fa").pack(pady=15) # Light Blue Title

# Input Section
input_frame = tk.Frame(main_frame, bg="#111827")
input_frame.pack(fill="x", pady=10)

# Search Entry
tk.Label(input_frame, text="What do you need today?", bg="#111827", fg="#9ca3af", font=("Arial", 10, "bold")).pack(anchor="w")
search_entry = tk.Entry(input_frame, font=("Arial", 14), bg="#1f2937", fg="white",
insertbackground="white", relief="flat", borderwidth=10)
search_entry.pack(fill="x", pady=8)

# Budget Entry
tk.Label(input_frame, text="Your Budget (₹)", bg="#111827", fg="#9ca3af", font=("Arial", 10, "bold")).pack(anchor="w")
budget_entry = tk.Entry(input_frame, font=("Arial", 14), bg="#1f2937", fg="white",
insertbackground="white", relief="flat", borderwidth=10)
budget_entry.pack(fill="x", pady=8)

# Button - Vibrant Green
tk.Button(main_frame, text="🔍 Find Best Prices & Deals", command=search_products,
bg="#10b981", fg="white", font=("Arial", 13, "bold"),
activebackground="#059669", activeforeground="white",
relief="flat", cursor="hand2", padx=30, pady=10).pack(pady=20)

# Results Area - Slate Grey Background
result_text = tk.Text(main_frame, height=20, width=60, font=("Consolas", 11),
padx=15, pady=15, bg="#1f2937", fg="#e5e7eb",
relief="flat", borderwidth=0)
result_text.pack(fill="both", expand=True)

# --- STYLING TAGS (The most important part for visibility) ---
result_text.tag_config("header", font=("Arial", 12, "bold"), foreground="#fbbf24") # Gold for item names
result_text.tag_config("best", foreground="#34d399", font=("Arial", 11, "bold")) # Bright green for prices
result_text.tag_config("total", font=("Arial", 14, "bold"), foreground="white") # Big white total
result_text.tag_config("success", foreground="#34d399", font=("Arial", 12, "bold")) # Budget Success
result_text.tag_config("error", foreground="#f87171", font=("Arial", 12, "bold")) # Budget Error (Red)

root.mainloop()