import json
import base64
from client import Client
#from client import Client
from storage import Storage
from client_anon import AnonymousClient


def get_svc_test(client):
    response = client.get_service("cowsay")
    print(response)

def cowsay_test_anon(client):
    text = {"message": "blyat"}
    tk = '38919156059e55805f66b81f74e8f6b59e0ba9e1f987900ed0a6eb0eb0aed82e'
    response = client.run_service("cowsay", token=tk, input=json.dumps(text))
    print(response.text)

def cowsay_test_text(client):
    text = "blyat"
    response = client.run_service("cowsay", input=text)
    print(response.text)

def plants_test_anon(client):
    tk = "201d9c9c252a47d70e61dacbf02353074921ddd4a39aaef16440949b604c2e26"
    image_in = "/home/calarcon/Pictures/plant2.jpg"
    response = client.run_service("ai4eosc-service", token= tk, input=image_in, timeout=400)
    print(response)

def text_to_speech_test(client):
    file_in = "/home/caterina/Documentos/text-to-speech-coqui/text.txt"
    file_out = "/home/caterina/Documentos/text-to-speech-coqui/test-python-run-out.mp3"
    response = client.run_service("text-to-speech-coqui", input="si vose volve a desir uwu", output="test-tes-test.mp3", timeout=100)
    #print(response.text)

def plants_sync_test(client):
    image_in = "/home/caterina/Documentos/egi_conference_2023/plants_example/images/cerezos.jpg"
    response = client.run_service("plant-classification", input=image_in, timeout=400)

    
def grayify_test(client):
    response = client.run_service("grayify", input="/home/caterina/Documentos/imagemagick_example/images")

def create_service_test(client):
    path = "/home/caterina/Documentos/imagemagick_example/imagemagick.yaml"
    return client.create_service(path)

def json_definition_example():
    return {
        "name": "grayify",
        "memory": "1Gi",
        "cpu": "1.0",
        "total_memory": "1Gi",
        "total_cpu": "1.0",
        "log_level": "CRITICAL",
        "image": "ghcr.io/grycap/imagemagick",
        "alpine": True,
        "script": "#!/bin/bash \necho \'SCRIPT: Invoked Image Grayifier. File available in $INPUT_FILE_PATH\' \nFILE_NAME=`basename \'$INPUT_FILE_PATH\'` \nOUTPUT_FILE=\'$TMP_OUTPUT_DIR/$FILE_NAME\' \necho \'SCRIPT: Converting input image file $INPUT_FILE_PATH to grayscale to output file $OUTPUT_FILE\' \nconvert \'$INPUT_FILE_PATH\' -type Grayscale \'$OUTPUT_FILE\'",
        "image_pull_secrets": [
        ],
        "input": [
            {
                "storage_provider": "minio.default",
                "path": "grayify/input",
                "suffix": [
                    ""
                ],
                "prefix": [
                    ""
                ]
            }
        ],
        "output": [
            {
                "storage_provider": "minio.default",
                "path": "grayify/output",
                "suffix": [
                    ""
                ],
                "prefix": [
                    ""
                ]
            },
            {
                "storage_provider": "webdav.dcache",
                "path": "/Users/calarcon/grayify",
                "suffix": [
                    ""
                ],
                "prefix": [
                    ""
                ]
            }
        ],
        "storage_providers": {
            "minio": {
                "default": {
                    "endpoint": "http://console.minio.wizardly-lamport0.im.grycap.net",
                    "region": "us-west-1",
                    "secret_key": "a1b2c3d4",
                    "access_key": "minio",
                    "verify": True
                }
            },
            "webdav": {
                "dcache": {
                    "hostname": "prometheus.desy.de",
                    "login": "calarcon",
                    "password": "v5vsYhd2"
                }
            }
        }
    }

def ai4eosc_test(client):
    service = {
        "log_level": "CRITICAL",
        "memory": "1Gi",
        "cluster_id": "oscar-cluster",
        "name": "test2",
        "cpu": "1.0",
        "vo": "vo.ai4eosc.eu",
        "image": "deephdc/deep-oc-plants-classification-tf",
        "alpine": False,
        "script": "#!/bin/bash",
        "allowed_users" : []
    }
    res = client.create_service(service)
    print(res.text)

def get_service_base_definition():
    """
    Base parameters of an OSCAR service

    """
    return {

    "log_level": "CRITICAL",
    "alpine": False,
    "script": "#!/bin/bash \nFILE_NAME=`basename $INPUT_FILE_PATH` \
                \nOUTPUT_FILE=\"$TMP_OUTPUT_DIR/$FILE_NAME\"\
                \necho \"SCRIPT: Invoked deepaas-predict command. File available in $INPUT_FILE_PATH.\" \
                \deepaas-predict -i $INPUT_FILE_PATH -o $OUTPUT_FILE"
    }

def main(): 
     
    #client.remove_service(svc_name)
    #local_client = Client("oscar-test","http://localhost", "oscar", "MTY5Yjc0", False)

    # Options for basic auth login
    options_basic_auth = {'cluster_id':'oscar-egi-cluster',
                'endpoint':'https://funny-kalam8.im.grycap.net',
                'user':'oscar',
                'password':'oscar123',
                'ssl':'True'}
    
    options_egi = {'cluster_id':'oscar-cluster',
                'endpoint':'https://oscar.test.fedcloud.eu/',
                'shortname':'calarcon',
                'ssl':'True'}
    
    SERVICE_NAME = "grayify"
    token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJQVVlPaXJBM1ktZF9kR3BkajRpSkRIdzR6SGE4SVktYmhaZGFFajByamJVIn0.eyJleHAiOjE3MTY4MDMwMDksImlhdCI6MTcxNjc5OTQwOSwiYXV0aF90aW1lIjoxNzE2Nzk1NDgzLCJqdGkiOiI0OTBmNDdlNy00NTc2LTRjODYtYWUyMy00ZjIxNDUzZDEzMjMiLCJpc3MiOiJodHRwczovL2FhaS5lZ2kuZXUvYXV0aC9yZWFsbXMvZWdpIiwic3ViIjoiNjJiYjExYjQwMzk4ZjczNzc4YjY2ZjM0NGQyODIyNDJkZWJiOGVlM2ViYjEwNjcxN2ExMjNjYTIxMzE2MjkyNkBlZ2kuZXUiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJpbS1kYXNoYm9hcmQiLCJzZXNzaW9uX3N0YXRlIjoiMjhiMjU5OGUtYmQ2YS00Y2UzLWI4MDUtNDgyNWRmNGQ2ZjM0Iiwic2NvcGUiOiJvcGVuaWQgb2ZmbGluZV9hY2Nlc3MgZWR1cGVyc29uX2VudGl0bGVtZW50IHByb2ZpbGUgZW1haWwiLCJzaWQiOiIyOGIyNTk4ZS1iZDZhLTRjZTMtYjgwNS00ODI1ZGY0ZDZmMzQiLCJhdXRoZW50aWNhdGluZ19hdXRob3JpdHkiOiJodHRwczovL3d3dy5yZWRpcmlzLmVzL3Npci91cHZpZHAifQ.aZib2Rypqy-XGjPn4ycmEA4u1nlNUb45zz4ry8yZevAdna3lNzEIvxsfwYpjgAvmiDEzrJMYRNAm2652EgvCPUK4bnn9qJuzPhEfSpRbam_jDxmG9MiX6XlKSIO-UqlJQLuDxAAAGuxhdvfqffaT9rZ10042w6-0qTvSiXtNOvFkusc4iVHp8eBcr469txMFvEcWoV8uPXtTL6bl8rbEQMEo2KT1p9twzVpL1WQNIa0XrVa4pfIS3V_IDCKjcDl8PmV3N7KKKkIiQEFg13FS6TSLEs2peszi8eqSAXX2Lq27eSxl0pPH3ZTcrA7vI5dyTKSi7qoK7lsKtHZJOvOCvw"
    options_egi_oidc = {'cluster_id':'oscar-egi-oidc',
            'endpoint':'https://inference.cloud.ai4eosc.eu',
            'oidc_token': token,
            'ssl':'True'}

    #client = Client("oscar-cluster","https://sleepy-brown8.im.grycap.net", "oscar", "oscar123", True)
    anon_client = AnonymousClient({
                     'cluster_id':'oscar-cluster',
                     'endpoint':'https://funny-kalam8.im.grycap.net',
                     'ssl':'true'
         })

    #get_svc_test(anon_client)

    try:
         client = Client(options = options_egi)
         print("Client created!!")
    except:
         print("Error creating OSCAR client!!!!11")

    # res = client.run_service(SERVICE_NAME, input="/home/calarcon/Pictures/cat.jpg", output=".")
    # print(res)
    storage = client.create_storage_client()
    print(storage.storage_providers)
    print("------------------------")
    storage = client.create_storage_client("grayify")
    print(storage.storage_providers)
    #cowsay_test_text(client)
    #get_svc_test(client)   
    #grayify_storage = client.create_storage_client(svc_name)
    #stablediff_storage = client.create_storage_client("stable-diffusion")
    
    # Download files test 
    #res = stablediff_storage.download_file("minio.default", "/home/caterina/Documentos/oscar_python_package", "stable-diffusion/out/text1.zip")
    #res = grayify_storage.download_file("minio.default", "/home/caterina/Documentos/oscar_python_package", "gray/output/image1.jpg")
    
    # Upload files test 
    #res = stablediff_storage.upload_file("minio.default", "/home/caterina/Documentos/txt_to_img/text1.txt", "stable-diffusion/in")
    #res = grayify_storage.upload_file("minio.default", "/home/caterina/Documentos/imagemagick_example/images/image2.jpeg", "gray/input")

if __name__ == "__main__":
    main()
