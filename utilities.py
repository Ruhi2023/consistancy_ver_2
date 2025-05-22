import Consistancy_tables_with_orm as db
import hashlib
import os
from langchain_google_genai import ChatGoogleGenerativeAI
ses =db.create_session()


class Authentication:
    def __init__(self):
        pass

    def add_user_to_database(self, name, username, password):
        # hash and hex the password
        password_hashed = hashlib.pbkdf2_hmac("sha256",password=password.encode('utf-8'),salt=username[:17].encode('utf-8'),iterations=100000)
        password = password_hashed.hex()
        try:
            ses.add(db.User(name=name, username=username, passwd=password))
            return {"message": "Username added successfully",
                    "status": "success"}
        except Exception as e:
            
            return {"message": f"An exception occured while adding user to database: {e}",
                    "status": "error"}
        finally:
            ses.commit()
            ses.close()

    def check_user(self, username, password):
        # hash and hex the password
        password_hashed = hashlib.pbkdf2_hmac("sha256",password=password.encode('utf-8'),salt=username[:17].encode('utf-8'),iterations=100000)
        password = password_hashed.hex()
        res= ses.query(db.User).filter(db.User.username == username, db.User.passwd == password).first()
        print(res)
        if res is None:
            return {"message": "could not find user",
                    "status": "error",
                    "user": None}
        
        return {"message": "user found",
                "status": "success",
                "user": res}
    

    def update_last_login(self, user_id):
        ses.query(db.User).filter(db.User.user_id == user_id).update({db.User.last_login: db.func.now()})
        ses.commit()

class GoogleGenAIUtilities:
    def __init__(self):
        self.api_key = None
        self.api_key = self.get_mykey()
    def get_mykey(self):
        """ Function for getting api key"""
        if self.api_key is not None:
            return self.api_key
        else:
            found = 0
            dir_per =""
            for dirpath, dirnames, filenames in os.walk(os.getcwd()):
                if "api_key.txt" in filenames:
                    found = 1
                    dir_per = dirpath
                    break
            if found >= 1:
                with open(os.path.join(dir_per, "api_key.txt")) as f:
                    api_k = f.readlines()
                self.api_key = api_k[0].replace("\n","")
                return self.api_key
            else:
                raise Exception("No api_key.txt found")
    def give_the_chatmodel(self):
        """we will congigure and return this thing's chat model"""
        if self.api_key is not None:
            return ChatGoogleGenerativeAI(model= "gemini-2.0-flash", GOOGLE_API_KEY=self.api_key)
        else:
            raise Exception("No api_key.txt found")

