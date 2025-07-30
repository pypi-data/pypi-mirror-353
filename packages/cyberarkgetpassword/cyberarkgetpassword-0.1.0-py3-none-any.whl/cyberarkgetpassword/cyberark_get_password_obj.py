""""
This python script will fetch the password of any privileged account from CyberArk

Author: Surendra Kumar
Version: v1.2
Date: 2024-05-15

We will keep cyberark service account username, password and private account in secret manager on ATR

History:
v1.0 - 2024-04-19 - The final version before prod deployment
v1.1 - 2023-05-15 - updated the condition if retrieved password is blank
"""

import requests
import json
import warnings
import sys
import time
from datetime import datetime
from logger import create_my_log
warnings.filterwarnings("ignore")

class CyberArkPassword():
    def __init__(self,cyberark_username,cyberark_password):
        self.vaulturl = "https://pim.cmhc-schl.gc.ca/PasswordVault"

        #vaulturl = "https://eddv1vmpasapp01.cmhc-schl.gc.ca/PasswordVault"  ## just for test lab
        self.logonurl = self.vaulturl+"/API/Auth/LDAP/Logon"
        self.logoffurl = self.vaulturl+"/API/Auth/Logoff"

        self.cyberark_username=cyberark_username ## cyberark dev safe
        print("CyberArk login account:  ",self.cyberark_username)
        self.cyberark_password=cyberark_password
        self.data_user_pass=json.dumps({'username':self.cyberark_username,'password': self.cyberark_password})
        self.cyberark_token=self.get_token()

    def get_token(self):
        token_data=""
        headers = {
                "Content-Type": "application/json",
                "Authorization": None
            }
        r = requests.post(self.logonurl, data=self.data_user_pass, headers=headers,verify=False)
        if r.status_code==200:
            token_data = json.loads(r.text)
            print(f"{datetime.now()} - CyberArk - Token returned Successfully")
        else:
            print(f"{datetime.now()} - CyberArk - Token return Failed")

        return token_data

    def get_pimvault_id(self,headers,privaccount):
        pimvault_id=""
        try:            
            searchurl = self.vaulturl+"/api/Accounts?search="+privaccount
            l = requests.get(searchurl, headers=headers,verify=False)
            if l.status_code==200:
                data2=json.loads(l.text)
                pimvault_id=data2['value'][0]['id']
                print(f"{datetime.now()} - CyberArk - Pimvault Id returned Successfully for Private Account: {privaccount} and response code is: {l.status_code}")
            else:
                print(f"{datetime.now()} - CyberArk - Pimvault Id returned Failed for Private Account: {privaccount} and response code is: {l.status_code} {l.text}")            
        except Exception as ex:
            print(f"{datetime.now()} - CyberArk - Pimvault Id returned Failed: {str(ex)}")

        return pimvault_id
    
    def get_password(self,privaccount,cyberark_token=""):
        is_password_retrieved=False
        pass_data=""
        count=1
        try:
            if cyberark_token=="":
                cyberark_token=self.cyberark_token

            headers_getid = {
                    'Content-Type':'application/x-www-form-urlencoded',
                    "Authorization": cyberark_token
                }
            
            while count<=3:
                acc_pimvault_id=self.get_pimvault_id(headers_getid,privaccount)
                passurl = self.vaulturl+"/api/Accounts/"+acc_pimvault_id+"/Password/Retrieve"
                pass_res = requests.post(passurl, data=self.data_user_pass, headers=headers_getid,verify=False)
                if pass_res.status_code==200:
                    is_password_retrieved=True
                    pass_data = json.loads(pass_res.text)
                    print(f"{datetime.now()} - CyberArk - Password returned Successfully for Private Account: {privaccount} in attempt {count} ")
                    create_my_log(f"CyberArk - Password returned Successfully for Private Account: {privaccount} in attempt {count} ")
                else:
                    is_password_retrieved=False
                    print(f"{datetime.now()} - CyberArk - Password returned Failed for Private Account: {privaccount} in attempt {count} and response code is: {pass_res.status_code}")
                    create_my_log(f"CyberArk - Password returned Failed for Private Account: {privaccount} in attempt {count} and response code is: {pass_res.status_code}")

                if is_password_retrieved:
                    break
                else:
                    self.cyberark_logoff(self.cyberark_token)
                    time.sleep(5)
                    new_token=self.get_token()
                    self.cyberark_token=new_token
                    headers_getid = {
                    'Content-Type':'application/x-www-form-urlencoded',
                    "Authorization": new_token
                }

                count+=1

            return pass_data        

        except Exception as ex:
            print(f"{datetime.now()} - CyberArk - Exception occured for Private Account: {privaccount}: {str(ex)}")
            return ""

    def cyberark_logoff(self, cyberark_token=""):
        if cyberark_token=="":
                cyberark_token=self.cyberark_token
        
        headers_logoff = {
                    'Content-Type':'application/json',
                    "Authorization": cyberark_token
                }
        try:
            time.sleep(5)
            logoff_res = requests.post(self.logoffurl, headers=headers_logoff,verify=False)
            if logoff_res.status_code==200:
                print(f"{datetime.now()} - CyberArk - logoff successful : {logoff_res.status_code}")
                create_my_log(f"CyberArk - logoff successful : {logoff_res.status_code}")
            else:
                print(f"{datetime.now()} - CyberArk - logoff failed : {logoff_res.status_code}")  
                create_my_log(f"CyberArk - logoff failed : {logoff_res.status_code}")  
        except Exception as ex:
            print(f"{datetime.now()} - CyberArk - Logoff - Exception occured : {str(ex)}")
        ######################################################################################



if __name__=="__main__":
    print("CyberArk - get password - main function - Starts")
   
  
    #print(cyberark_obj.get_password("SVC_ATR_SNOW_DEV"))
    #print(cyberark_obj.get_password("CyberarkTEST"))
    #print(cyberark_obj.get_password("svc_kitesecfold_dev@kwsvccmhc.com"))
    # print(cyberark_obj.get_password("ATR_ADMIN_DEV"))
    # print(cyberark_obj.get_password("SVC_ATRMIDAAAUTO_DEV"))
    # print(cyberark_obj.get_password("SVC_ATRD365AUTO_DEV"))
    # print(cyberark_obj.get_password("SVC_SHAREFOLDER_DEV"))
    # print(cyberark_obj.get_password("SVC_ATR_SNOW_PRD")) 
    # print(cyberark_obj.get_password("svc_kitesecfold_prod@kwsvccmhc.com"))
    # print(cyberark_obj.get_password("SVC_ATRMIDAAAUTO_PPD"))
    # print(cyberark_obj.get_password("SVC_ATRD365AUTO_PPD"))
    # print(cyberark_obj.get_password("SVC_ATRGuestWIFI_PRD"))
    # print(cyberark_obj.get_password("ATR_ADMIN_PRD"))    
    # print(cyberark_obj.get_password("no-reply-atr@cmhc-schl.gc.ca")) 
    #cyberark_obj.cyberark_logoff()   

