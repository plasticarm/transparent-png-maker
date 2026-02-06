import requests

# REPLACE THIS with your actual Render URL
url = "https://transparent-png-maker.onrender.com/process-image" 

# Create a dummy image or use a real one (make sure 'test.jpg' exists in your folder)
try:
    # We'll assume you have a file named 'test.jpg' or change this to a file you have
    files = {'image': open('G:/WebApps/transparent-png-maker/test.jpg', 'rb')} 
    
    data = {
        'hex_color': '#00FF00', 
        'tolerance': '30'
    }

    print(f"Pinging {url}...")
    response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        print("✅ SUCCESS! The server accepted the image.")
        print(f"Received {len(response.content)} bytes back.")
        with open('success_alpha.png', 'wb') as f:
            f.write(response.content)
            print("Saved 'success_alpha.png'")
    else:
        print(f"❌ ERROR {response.status_code}")
        print(f"Server said: {response.text}")

except FileNotFoundError:
    print("⚠️ make sure you have a 'test.jpg' file in this folder to send!")