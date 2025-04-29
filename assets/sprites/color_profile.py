from PIL import Image

img1 = Image.open("Mystic.png")
img2 = Image.open("Mayhem.png")
img3 = Image.open("enter.png")

img1.save("mystic_fixed.png", icc_profile=None)
img2.save("mayhem_fixed.png", icc_profile=None)
img3.save("enter_fixed.png", icc_profile=None)