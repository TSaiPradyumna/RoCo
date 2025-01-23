from PyQt5.QtWidgets import QApplication,QWidget,QLineEdit,QPushButton,QLabel,QVBoxLayout
from api_key import my_key
import requests

class Home(QWidget):
    def __init__(self):
        super().__init__()
        self.settings()
        self.initUI()
        self.api_key=my_key
        self.submit.clicked.connect(self.search_click)
    
    def settings(self):
        self.setWindowTitle('OpenWeather')
        self.setGeometry(250,250,500,500)

    def initUI(self):
        self.title =QLabel("Weather Engine")
        self.input_box=QLineEdit()
        self.input_box.setPlaceholderText("Enter Location.....")

        self.output=QLabel("Information will be displayed here:")
        self.submit=QPushButton("Search")    

        self.master=QVBoxLayout()
        self.master.addWidget(self.title)
        self.master.addWidget(self.input_box)
        self.master.addWidget(self.output)
        self.master.addWidget(self.submit)

        self.setLayout(self.master)

    def search_click(self):
        self.result = self.getWeather(self.api_key,self.input_box.text())
        self.output.setText(self.result)


    def getWeather(self,api_key,city,country=''):
        base_url = "https://api.openweathermap.org/data/2.5/weather?"
        params = {'q': f'{city},{country}','appid':api_key}

        try:
            res = requests.get(base_url,params=params)
            data = res.json()

            if res.status_code == 200:
                city_name = data['name']
                country_code = data['sys']['country']

                temperature_kelvin= data['main']['temp']
                temperature_celsius = temperature_kelvin - 273.15

                weather = data['weather'][0]['description']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                wind_direction = data['wind']['deg']

                weather_info =(f"Weather in {city_name}({country_code})\n"
                               f"Temperature: {temperature_celsius}°C\n"
                               f"Weather: {weather}\n"
                               f"Humidity: {humidity}%\n"
                               f"Wind Speed: {wind_speed}m/s\n"
                               f"Wind Direction: {wind_direction}°\n")
                return weather_info
            else:
                return 'Error'
        except:
            return 'Error'
        




if __name__ in "__main__":
    app = QApplication([])
    home = Home()
    home.settings()
    home.show()
    app.exec_()

