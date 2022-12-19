import argparse
from time import sleep
from PIL import Image, UnidentifiedImageError
from pyzbar.pyzbar import decode
import requests
from io import BytesIO
from bs4 import BeautifulSoup
import qrcode

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', required=True)
parser.add_argument('-o', '--output', default="MyQRCodeWoop.png", required=False)
args = parser.parse_args()

root_link = args.url
output_image_path = args.output

print("Retrieving barcodes...")
image_idx = 1
barcodes = []
valid_url = True
while valid_url:
    url = f"{root_link}{image_idx:06d}.png"
    print(url)
    response = requests.get(url)
    try:
        img = Image.open(BytesIO(response.content))
        code = decode(img)[0].data.decode("utf-8")
        barcodes.append(code)
        image_idx += 1
    except UnidentifiedImageError:
        valid_url = False


def is_valid_code(code):
    total = 0
    for character in code:
        if character.isdigit():
            total += int(character)

    if total in [0, 1]:
        return False

    for factor in range(2, total):
        if total % factor == 0:
            return False
    return True


def get_letters(code):
    output = ""
    for character in code:
        if character.isalpha():
            output += character
    return output


def get_digits(code: str):
    output = ""
    for character in code:
        if character.isdigit():
            output += character
    return output


print("Processing barcodes...")
key = ""
first_found = False
paragraph_id = None
for code in barcodes:
    is_valid = is_valid_code(code)
    if is_valid:
        letters = get_letters(code)
        key += letters
        if not first_found:
            digits = get_digits(code)
            paragraph_id = digits
            first_found = True

print(f"Found key: {key}")
print(f"Found paragraph id: {paragraph_id}")
print("Retrieving html...")
link = root_link + key
req = requests.get(link)
soup = BeautifulSoup(req.content, 'html.parser')
paragraph = soup.find("p", {"id": paragraph_id})

print("Setting paragraph info in qr code")
qrcode_img = qrcode.make(str(paragraph))
print(f"Saving {output_image_path}")
qrcode_img.save(output_image_path)
print("Done!")
sleep(5)
