#!/usr/bin/env python
# coding: utf-8

# In[1]:


import qrcode
import os
import json
def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(json.dumps(data))
    qr.make(fit=True)

    os.makedirs("Qrs", exist_ok=True)

    filename = os.path.join("Qrs", f"{data['Name']}.jpg")

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

    print(f"QR code saved as {filename}")

if __name__ == "__main__":
    text = {"Name":"Jack1","id":"10","auth_code":"2c957c40d719e6e134a6c1fc7086f269992017537125ed9f6d6b496c50328081d608020215180585ddd78c4566f2180c1562c1c6320d8fba4e368584b72724a4"}
    generate_qr(text)


# In[ ]:




