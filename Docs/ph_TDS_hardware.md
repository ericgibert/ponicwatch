Gravity: Analog TDS Sensor/Meter for Arduino
============================================

https://www.dfrobot.com/product-1662.html



Code at https://www.dfrobot.com/wiki/index.php/Gravity:_Analog_TDS_Sensor_/_Meter_For_Arduino_SKU:_SEN0244

      float compensationCoefficient=1.0+0.02*(temperature-25.0);    //temperature compensation formula: fFinalResult(25^C) = fFinalResult(current)/(1.0+0.02*(fTP-25.0));
      float compensationVolatge=averageVoltage/compensationCoefficient;  //temperature compensation
      tdsValue=(133.42*compensationVolatge*compensationVolatge*compensationVolatge - 255.86*compensationVolatge*compensationVolatge + 857.39*compensationVolatge)*0.5; //convert voltage value to tds value
      //Serial.print("voltage:");
      //Serial.print(averageVoltage,2);
      //Serial.print("V   ");
      Serial.print("TDS Value:");
      Serial.print(tdsValue,0);
      Serial.println("ppm");


Gravity: Analog pH Sensor / Meter Kit For Arduino
=================================================

https://www.dfrobot.com/product-1025.html

  float phValue=(float)avgValue*5.0/1024; //convert the analog into millivolt
  phValue=3.5*phValue;                    //convert the millivolt into pH value