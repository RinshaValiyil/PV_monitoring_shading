import conf, json, time, math,statistics
from boltiot import Sms, Bolt, Email


frame_size=req.FRAME_SIZE
Minimum_limit=req.Minimum_limit

    
mybolt = Bolt(req.API_KEY, req.DEVICE_ID)
sms = Sms(req.SSID, req.AUTH_TOKEN, req.TO_NUMBER, req.FROM_NUMBER)
mailer = Email(req.MAILGUN_API_KEY, req.SANDBOX_URL, req.SENDER_EMAIL, req.RECIPIENT_EMAIL)
history_data=[]

while True:
    response = mybolt.analogRead('A0')
    data = json.loads(response)
    if data['success'] != 1:
        print("There was an error while retriving the data.")
        print("This is the error:"+data['value'])
        time.sleep(10)
        continue

    print ("This is the value "+data['value'])
    sensor_value=0
    try:
        sensor_value = int(data['value'])
    except e:
        print("There was an error while parsing the response: ",e)
        continue
    if len(history_data)>=frame_size :
        del history_data[0:len(history_data)-frame_size]
        Mn=statistics.mean(history_data)
    else:
        required_data_count=req.FRAME_SIZE-len(history_data)
        print("Not enough data to compute mean. Need ",required_data_count," more data points")
        history_data.append(int(data['value']))
        time.sleep(10)
        continue

    try:

        if Mn > Minimum_limit :
            print ("The incidence level is normal")
            response1= mybolt.digitalWrite('0','LOW')
            print("The motor is not activated",response1)
        elif Mn < Minimum_limit :
            print ("The light level decreased suddenly. Sending an SMS.")
            response= mybolt.digitalWrite('0','HIGH')
            print("The motor activation response",response)
            response1 = sms.send_sms("Shading happened and changing PV panel alignment")
            print("This is the SMS response ",response1)
            print("Making request to Mailgun to send an email")
            response = mailer.send_email("Alert", "Shading happened and changing PV panel alignment " +str(sensor_value))
            response_text = json.loads(response.text)
            print("Response received from Mailgun is: " + str(response_text['message']))
        history_data.append(sensor_value);
    except Exception as e:
        print ("Error",e)
    time.sleep(10)