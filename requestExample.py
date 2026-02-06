import requests

# Replace with the URL Render gave you
url = "https://transparent-png-maker.onrender.com/" 

# Use a local image to test
files = {'image': open('test_image.jpg', 'rb')}
data = {
    'hex_color': '#00FF00', 
    'tolerance': '40',
    'choke_pixels': '1', 
    'feather_pixels': '2'
}

print("Sending image...")
response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    with open('result.png', 'wb') as f:
        f.write(response.content)
    print("Success! 'result.png' saved.")
else:
    print(f"Error: {response.text}")