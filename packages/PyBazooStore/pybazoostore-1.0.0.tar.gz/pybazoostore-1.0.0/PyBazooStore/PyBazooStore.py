import requests



BaseURL = "https://bazoostore.ir"

def GetBestBots(
        offset : str | int = 1
    ):
    "برای دریافت بازو هایی که جز برترین بازو ها هستند به کار می رود"
    try:
        return {
            "ok" : True,
            "result" : list(
                requests.post(
                    f"{BaseURL}/best",
                    json={
                        "offset" : str(offset)
                    }
                ).json()["value"]
            )
        }
    except:
        return {
            "ok" : False
        }




def GetNewBots(
        offset : str | int = 1
    ):
    "برای دریافت بازو هایی که جدیدا به بازو استور اضافه شدند به کار می رود"
    try:
        return {
            "ok" : True,
            "result" : list(
                requests.post(
                    f"{BaseURL}/bot",
                    json={
                        "offset" : str(offset)
                    }
                ).json()["value"]
            )
        }
    except:
        return {
            "ok" : False
        }


def GetRandomBazoo():
    "برای دریافت ربات های تصادفی استفاده می شود"
    try:
        return {
            "ok" : True,
            "result" : list(
                requests.get(
                    f"{BaseURL}/random"
                ).json()["value"]
            )
        }
    except:
        return {
            "ok" : False
        }




def SearchBazoo(
        NameBazoo : str,
        searched_by : str = "name"
    ):
    """
    برای جستجوی ربات در بازو استور به کار می رود\n
    در صورتی که می خواهید بر اساس توضیحات ، ربات مورد نظرتان را جستجو کنید :\n
    searched_by = "caption"\n
    """
    try:
        return {
            "ok" : True,
            "result" : list(
                requests.post(
                    f"{BaseURL}/search",
                    json={
                        "search_params" : str(NameBazoo),
                        "searched_by" : str(searched_by)
                    }
                ).json()["value"]
            )
        }
    except:
        return {
            "ok" : False
        }
    



def GetDataBot(
        UsernameBot : str
    ):
    try:
        DataBot = requests.get(
            f"{BaseURL}/random/{UsernameBot}"
        ).json()["value"]
        return {
            "ok" : True,
            "result" : {
                "id" : DataBot[0]["id"],
                "name" : DataBot[0]["name"],
                "chat_id" : DataBot[0]["chat_id"],
                "username" : DataBot[0]["username"],
                "description" : DataBot[0]["description"],
                "photo" : DataBot[0]["photo"],
                "track_id" : DataBot[0]["track_id"],
                "created_at" : DataBot[0]["created_at"],
                "average" : DataBot[1]["average"],
                "count" : DataBot[1]["count"]
            }
        }
    except:
        return {
            "ok" : False
        }
    

