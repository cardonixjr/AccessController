print("[INFO] Importing packages")
import pandas as pd
import mysql.connector
import datetime

def set0():
     db = mysql.connector.connect(
          host="localhost",
          user="root",
          passwd="root",
          database="accessController0"
     )
     cursor = db.cursor()
     totalPeople = 0
     now = datetime.datetime.now()
     cursor.execute("INSERT INTO Trackers (direction, total, weekday, datetime) VALUES (%s,%s,%s,%s)",('saindo', totalPeople, now.weekday(),now))
     db.commit()


def weekdayAverage(df):
     dailyAverage = list()
     for a in range(7):
          dailyDf = df[df["weekday"]==a]
          average=0
          for val in dailyDf["total"]:
               average +=val
          try:average/=len(dailyDf)
          except ZeroDivisionError: average=0
          dailyAverage.append(int(average))
     return(["Segunda-feira","Terça-feira","Quarta-feira","Quinta-feira","Sexta-feita","Sábado","Domingo"],dailyAverage)

def dailyAverage(df):
     days=list()
     dailyAvg=list()
     dailyNum=list()
     for datetime in df["datetime"]:
          if datetime.date() not in days:
               days.append(datetime.date())
               dailyAvg.append(0)
               dailyNum.append(0)
     
     for i in range(len(df)):
          entry = df.iloc[i]
          if entry.datetime.date() in days:
               dailyAvg[days.index(entry.datetime.date())] += entry.total
               dailyNum[days.index(entry.datetime.date())] += 1
               
     for i in range(len(dailyAvg)):
          try: dailyAvg[i] = int(dailyAvg[i]/dailyNum[i])
          except ZeroDivisionError: dailyAvg=0

     for i in range(len(days)): days[i] = days[i].strftime('%d/%m/%y')
     return(days,dailyAvg)
     
def hourFlow(df):
     avg = [0]*24
     denom = [0]*24
     for i, row in df.iterrows():
          avg[row["datetime"].hour] += row["total"]
          denom[row["datetime"].hour] += 1

     for a in range(len(avg)):
          try: avg[a] = int(avg[a]/denom[a])
          except ZeroDivisionError: average=0

     return (list(range(6,22)), avg[6:22])

def getTodayFlowIn(db):
     query = "SELECT COUNT(total) FROM Trackers WHERE direction='entrando' AND DATE(datetime) = DATE(NOW())"
     df = pd.read_sql(query,db)
     return df.values[0][0]

def getCurrentTotal(df):
     return df.tail(1).values[0][4]

def avgEntries(db):
##     query = "SELECT DATE(datetime) FROM Trackers WHERE direction='entrando'"
     query = "SELECT DATE(datetime), COUNT(total) FROM Trackers WHERE direction='entrando' group by DATE(datetime)"
     df = pd.read_sql(query,db)

     days = [value for value in df["DATE(datetime)"]]
     totals = [value for value in df["COUNT(total)"]]

     return (days, totals)
          

def getCurrentData(df):
     return df.tail(1).values[0][1]
     

if __name__ == "__main__":
     db=mysql.connector.connect(host="localhost",user="root",passwd="root",database="accessController0")
     cursor=db.cursor()     
     # Geting data from mysql database
     #df = pd.read_sql("SELECT direction, DATE(datetime) FROM Trackers WHERE direction='entrando' AND DATE(datetime) = DATE(NOW())",db)
     
     x,y = avgEntries(db)
     print(x)
     print(y)
     db.close()
