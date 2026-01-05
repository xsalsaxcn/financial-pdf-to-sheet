from extract_pdf import extract_text
from parse_pl import detect_period, extract_pl_block, parse_profit_loss

text = extract_text("report.pdf")

print("===== PERIOD =====")
print(detect_period(text))

print("\n===== PL BLOCK (FIRST 1000 CHARS) =====")
pl_block = extract_pl_block(text)
print(pl_block[:1000])

print("\n===== PARSED P&L =====")
print(parse_profit_loss(text))
