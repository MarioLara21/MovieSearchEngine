import requests 
import json 

def getJobs(): 
    jobDictionary = {
        "jobId": "1",
        "pageSize": "100", 
        "sleep": "100"
    }
    return jobDictionary

def kafkaGenerate(): 
    direccion = 'https://api.biorxiv.org/details/biorxiv/2018-08-21/2024-02-04/45'

    resp = requests.get(direccion)

    job = getJobs()

    if resp.status_code == 200: 
        datos = resp.json()
        messages = datos["messages"]
        total = messages[0]["total"]
        splitSize = total // int(job["pageSize"])

        #print("Split size: ",splitSize)

        kafka_dict = {
            "jobId" : job["jobId"], 
            "pageSize" : job["pageSize"], 
            "sleep" : job["sleep"], 
            "splitNumber" : str(splitSize)
            
        }
        return kafka_dict

    else: 
        print('Error')


def makeJDoc(dicc, filename):
    with open(filename, "w") as json_file: 
        json.dump(dicc, json_file, indent=4)


def main(): 
    kfk = kafkaGenerate()
    makeJDoc(kfk, 'kafka.json')
    print(kfk)
        
if __name__ == "__main__":
    main()
