import time
from tkinter import *
from tkinter import ttk
from PIL import Image,ImageTk
import pyproj
import serial


CONSTANT_CAMPUS = 1.48
CONSTANT_INSIA = 2.41

LAT_CAMPUS = 4470696.42
LONG_CAMPUS = 445999.78

LAT_INSIA = 4470673.26
LONG_INSIA = 446142.34

pathCampus = "/Users/carlosdeantonio/Documents/UNIVERSIDAD/GPS/Practica 2/Python/campusSur.png"
pathInsia = "/Users/carlosdeantonio/Documents/UNIVERSIDAD/GPS/Practica 2/Python/insia.png"

def set_pixel_position(Latitude, Longitude, imPath):
    image = Image.open(imPath)
    pixelPosition = image.load()

    print ("Calculating..")
    if imPath == pathCampus:
      alto = int(1029 - (Latitude - LAT_CAMPUS) * CONSTANT_CAMPUS)
      ancho = int((Longitude - LONG_CAMPUS) * CONSTANT_CAMPUS)
    else:
      alto = int(1029 - (Latitude - LAT_INSIA) * CONSTANT_INSIA)
      ancho = int((Longitude - LONG_INSIA) * CONSTANT_INSIA)

    pixelPosition[ancho, alto] = (255, 0, 0, 255)
    print(ancho)
    print(alto)

    image.save(imPath)


if __name__ == '__main__':
    serialPort = serial.Serial(port='/dev/tty.usbserial', baudrate=4800, parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

    windowMap = Tk()
    windowMap.title('Speed Map')
    windowMap.geometry('800x800')
    windowMap.resizable(width=True, height=True)

    ttk.Button(windowMap, text='Exit', command=quit).pack(side=BOTTOM)

    # CREATION OF GUI LABEL WITH IMAGE
    #img = ImageTk.PhotoImage(file=pathCampus)
    img = ImageTk.PhotoImage(file=pathInsia)
    label = ttk.Label(windowMap, image=img)
    label.pack()


    try:
        print("Abriendo puerto ..")
        serialPort.isOpen()
        print("Puerto abierto ..\n")



        while True:
            print("leyendo..")

            lineGPS = serialPort.readline()
            data = lineGPS.decode().split(',')  # Split each GGA data

            if data[0] == "$GPGGA":
                print("Formato GCA")
                print(lineGPS)
                print("transformando..\n")

                gcaLatitude = data[2]
                gcaLongitude = data[4]

                degreeLatitude = float(gcaLatitude[0:2]) + (float(gcaLatitude[2:9]) / 60)  # GGA to Degrees
                degreeLongitude = float(gcaLongitude[0:3]) + (float(gcaLongitude[3:9]) / 60)

                # North or South
                if data[3] == "S":
                    degreeLatitude *= -1.0

                # East or West
                if data[5] == "W":
                    degreeLongitude *= -1.0

                # Transforming degrees into UTM
                p1 = pyproj.Proj(init="epsg:4326")
                p2 = pyproj.Proj(init="epsg:32630")
                utmLongitude, utmLatitude = pyproj.transform(p1, p2, degreeLongitude, degreeLatitude)

                # DECIMAL format
                print("\nFormato Decimal")
                print("  Latitud Decimal : " + str(degreeLatitude))
                print("  Longitud Decimal : " + str(degreeLongitude))

                # UTM format
                print("\nFormato UTM")
                print("  Latitud UTM : " + str(utmLatitude))
                print("  Longitud UTM : " + str(utmLongitude))

                #set_pixel_position(utmLatitude, utmLatitude, pathCampus)
                set_pixel_position(utmLatitude, utmLongitude, pathInsia)

                # UPDATING IMAGE IN GUI
                #img_2 = ImageTk.PhotoImage(file=pathCampus)
                img_2 = ImageTk.PhotoImage(file=pathInsia)
                label.configure(image=img_2)
                label.image = img_2

                windowMap.update()


        windowMap.mainloop()
        
    except Exception as e:
        #serialPort.close()
        #print("\nPuerto cerrado")
        #exit()
        print(e)
        traceback.print_exc()
