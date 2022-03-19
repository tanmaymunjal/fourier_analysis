# make all necessary imports
from flask import Flask, jsonify
import statistics
import numpy as np
import pyaudio
from matplotlib import pyplot as plt
from scipy.fft import fft, fftfreq, ifft
import mysql.connector

# make a mysql object and make initial database and table

mydb = mysql.connector.connect(
    host="localhost",
    user="yourusername",
    password="yourpassword"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE mydatabase")

mycursor.execute("CREATE TABLE music (name VARCHAR(255), lyrics_in_dataform VARCHAR(MAX))")

# make a pyaudio object

pa = pyaudio.PyAudio()

#make flask object

app=Flask(__name__)
@app.route('/')


#initialise flask route for api creation

@app.route('/music/<string:anwser>')

def music(anwser):
  if anwser=="functional":

    # set parameters for audio collection

   stream_in = pa.open(
     rate=48000,
     channels=2,
     format=pyaudio.paInt16,
     input=True,  # input stream flag
     input_device_index=1,  # input device index
     frames_per_buffer=1024
   )
   rate = 48000
   time = int(input("Pleae input how many minutes your performance will last: ")) * 60

   # ask user name of music to be recorded

   name = input("Please input name of music to be added: ")

   # listen to "time" seconds of the input stream

   print("Speak!!!!")
   input_audio = stream_in.read(time * rate)
   print('Audio recorded')
  
   # change collected audio to string for further processing

   input_audio_2 = str(input_audio)
   audio = []
   y = 0
   
   # change bytes type object to int tuple for further manipulation

   for n in range(0, len(input_audio)):
     t = r"\""
     if input_audio_2[n] == t[0] and y != n - 4:
        y = n
        a = int.from_bytes(input_audio[n + 1:n + 8], "big")
        audio.append(a)

    # add audio to sql database for use in further date


   sql = "INSERT INTO music (name, lyrics_in_dataform) VALUES (%s, %s)"

   val = (name, audio)

   mycursor.execute(sql, val)

   mydb.commit()

   print("The auido has been added to table music in list form under the name provided")

    # normalise collected data points as pre-processing step

   normalized_tone = []

   for n in range(len(audio)):
         x = np.int16((audio[n] / max(audio)) * 32767)
         normalized_tone.append(x)

    # Number of samples in normalized_tone

   N = rate * time

    # do a fast fourier transformation and plot it

   yf = fft(normalized_tone)

   xf = fftfreq(N, 1 / rate)

   plt.plot(xf, np.abs(yf))

   plt.plot.show()
    
    # def basic functionality for program

   def back_to_audio(fft_of_lyrics_normalised_array):
     yf2 = ifft(fft_of_lyrics_normalised_array)

     # read data (based on the chunk size)

     data = yf2.readframes(N)

     # play stream (looping from beginning of file to the end)

     while data != '':

        # writing to the stream is what *actually* plays the sound.

        stream_in.write(data)
        data = yf2.readframes(N)

   def mean_of_audio():

        return statistics.mean(normalized_tone)

   def variance():

        return statistics.variance(normalized_tone)

   def variance_tone(tone):

        a = 0
        for n in range(len(normalized_tone)):
            a = a + (normalized_tone[n] - tone[n]) ** 2
        return a


   question = input("Do you want to find mean,variance, difference in tone with another tone, or turn a given fast fourier transformation back to audio: M/V/D/T: ") 
   if question == "M":
     print(jsonify(mean_of_audio()))
   elif question == "V":
     print(jsonify(variance()))
   elif question == "D":
     tone = input("Please copy and paste the normalised tone array with which you want to find the difference: ")
     print(jsonify(variance_tone(tone)))
   elif question == "T":
     input_fft = input("Please enter fft output of lyrics to be reconstructed: ")
     print("Note: Some time series information will be lost in the process of audio to fft and then back to audio, "
          "make sure that the audio is as uniform as possible and take into account some natural discrepancies with "
          "original source at all times")
     print(jsonify(back_to_audio(input_fft)))
   else:
     print("You have given an incorrect input")


    # command to delete all entries from table to save memory and minimise name clashes in future
    # for temporary purposes in computer project , not to be imported in production model for obvious reasons

   sql = "DROP music"

   mycursor.execute(sql)

   mydb.commit()

    # close all earlier made objects and processes

   stream_in.close()

   pa.close()

   mycursor.close()
