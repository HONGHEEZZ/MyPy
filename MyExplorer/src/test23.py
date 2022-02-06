import matplotlib.image as img
import matplotlib.pyplot as pp
fileName = "D:\\__pic_test\\2018-10-08\\20181008_074510 (경상북도 경주시 불국동 산72-27).jpg"
ndarray = img.imread(fileName)
pp.imshow(ndarray)
pp.show()


