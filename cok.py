import base64

with open("cookies.txt", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

print(encoded)  # Copy hasilnya
