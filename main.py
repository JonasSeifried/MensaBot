from time import sleep
from meal_plan import get_meal_plan_str
import pywhatkit
import traceback
import os
from dotenv import load_dotenv
import logging

load_dotenv()
URL = os.getenv('URL')
ERROR_PHONE_NUMBER = os.getenv('ERROR_PHONE_NUMBER')
TARGET_GROUP_ID = os.getenv('TARGET_GROUP_ID')

#TODO: pip install pyperclip benutzen statt TK und die ganze lib forken und gescheit machen :D
if __name__ == '__main__':
    try:
        meal_plan = get_meal_plan_str(URL, showAllergies=False)
        if TARGET_GROUP_ID:
            pywhatkit.sendwhatmsg_to_group_instantly(TARGET_GROUP_ID, meal_plan, 0, False, 2)
  
    except Exception as e:
        traceback_str = traceback.format_exc()
        logging.error(traceback_str)
        if ERROR_PHONE_NUMBER:
            pywhatkit.sendwhatmsg_instantly(ERROR_PHONE_NUMBER.strip(), traceback_str, 5, True, 2)



