from ntpath import realpath
import socket, threading
import datetime as dt 
import os
import sys
import time

from numpy import size


#   /************************
#    * Param: 연결된 클라이언트와 소캣의 주소를 파라미터로 가져옵니다
#    * Description: 클라이언트와 연결되는 부분이며 명령문과 비 명령문으로 구분하여 처리하였습니다.
#    ************************/
def binder(client_socket, addr):
    index=1
    uploadCount=1
    try:
        while True:
            file = client_socket.recv(1024);
            data = file.decode("utf-8")
            print("client :",data)
            data = data.split()

            ####################################################################################
            # orderList에 들어있는 명령문을 입력시 어떤 명령어를 입력했는지 나눠 서비스를 제공합니다.#
            # 만약 orderList에 없는 값이 들어올 경우 맨 아래 else문에서 단순 채팅으로 답장합니다.   #
            ####################################################################################
            if data[0] in orderList:
                
                ############################################################
                # 명령문 help 를 입력한 경우로 명령 리스트를 보내줍니다. #
                ############################################################
                if data[0]=="help":
                    client_socket.sendall(orderList.encode("utf-8"))       

                ##################################################################
                # 명령문 cd를 입력한 경우로 서버의 현재 작업 디렉토리를 변경해줍니다. #
                ##################################################################
                elif data[0]=='cd':
                    print("##서버의 CWD 변경 명령##")
                    nowLocation = os.getcwd()
                    nowLocation = "##명령어 입력 완료##\n현재 위치 : ["+ nowLocation + "]" + "\n#변경위치를 입력해주세요 (뒤로가기 : back)#"  
                    client_socket.sendall(nowLocation.encode("utf-8"))       
                    
                    while True:
                        file = client_socket.recv(1024);
                        data = file.decode("utf-8")
                        
                        if data == "back":
                            nowLocation = "##이전으로##\n"+ orderList  
                            client_socket.sendall(nowLocation.encode("utf-8"))
                            break             
                        try:
                            os.chdir(data)
                            nowLocation = os.getcwd()
                            nowLocation = "#변경 완료#\n현재 위치 : "+ nowLocation  
                            client_socket.sendall(nowLocation.encode("utf-8"))
                            break
                        except Exception as err:
                            print(err,"발생")
                            Err = "#입력 오류#\n다시 입력해 주세요 (뒤로가기:back)" 
                            client_socket.sendall(Err.encode("utf-8"))
                            
                ##################################################################################
                # 명령문 lcd가 들어온 경우로 클라이언트쪽 변경 문제기 때문에 서버는 관여하지 않습니다. #
                ##################################################################################
                elif data[0]=='lcd':
                    # default=""
                    # client_socket.sendall(default.encode("utf-8"))
                    pass
                    
                ############################################################################################
                # 명령문 ls가 들어온 경우로 서버 파일 목록 중 디렉토리를 제거한 값들을 클라이언트에게 전달합니다. #
                ############################################################################################
                elif data[0]=='ls':
                    print("##서버의 CWD 파일 목록 출력 명령 ##")
                    fileList = os.listdir(os.getcwd())
                    notDirecList = fileList[:]
                    for file in fileList:
                        if os.path.isdir(file)==True:
                            notDirecList.remove(file)
                    stringList = "##명령어 입력 완료##\n\n현재 위치 파일 리스트 [  "
                    for i in notDirecList:
                        stringList+=i+", "
                    stringList+="]"
                    client_socket.sendall(stringList.encode("utf-8"))


                ########################################################################
                # 명령어 get이 들어온 경우로 서버의 파일 중 디렉토리를 제외한 값을 보여주고,#
                # 원하는 파일 이름을 회신받아 서버쪽에서 찾은 후 해당파일을 보내줍니다.     #
                # 클라이언트에게 단순 보여주기만 하는 기능까지 구현했습니다. 
                ########################################################################
                elif data[0]=='get':
                    while True:
                        try:
                            fileList = os.listdir(os.getcwd())
                            
                            notDirecList = fileList[:]
                            for file in fileList:
                                if os.path.isdir(file)==True:
                                    notDirecList.remove(file)
                            
                            print("##지정 파일 다운로드 명령 ##")
                            returnMsg = """##명령어 입력 완료##\n\n
# 현재 있는 파일 목록 : {} #\n
#다운로드할 파일 이름을 입력해주세요 (뒤로가기 : back)#\n""".format(notDirecList)  
                            client_socket.sendall(returnMsg.encode("utf-8"))
                            
                            file = client_socket.recv(1024);
                            data = file.decode("utf-8")
                            
                            if data == "back":
                                nowLocation = "#이전으로#\n"+ orderList  
                                client_socket.sendall(nowLocation.encode("utf-8"))
                                break

                            downloadStart = time.time() 
                            returnFile = "##전송 완료##\n\n# 파일 이름 : {} #\n\n# 파일내용 #\n".format(data)
                            myFile = open(data,"r",encoding="utf-8")
                            while True:
                                line = myFile.readline()
                                if not line: break
                                returnFile+=line  
                            print(returnFile)       
                            client_socket.sendall(returnFile.encode("utf-8"))
                            print("#파일 전송 완료#\n")
                            index = getFile(data,downloadStart,index)
                            break
                        except:
                            returnMsg = "오류입니다. 다시 입력해주세요."
                            client_socket.sendall(returnMsg.encode("utf-8"))
                            print(returnMsg)


                ###################################################################################    
                # put 명령어가 들어온 경우로 클라이언트 쪽에서 원하는 파일을 업로드 합니다.
                # 파일 이름과 내용을 수신 받아 서버쪽 디렉토리에 저장한 후, 로그파일로 기록을 남깁니다.
                ###################################################################################
                elif data[0]=='put':
                    while True:
                        try:
                            print("##지정 파일 업로드 명령 ##")
                            returnMsg = "#파일 업로드 대기중. 파일 이름을 입력해 주세요.(뒤로가기 : back)#"  
                            client_socket.sendall(returnMsg.encode("utf-8"))
                            fileName = client_socket.recv(1024)
                            fileName = fileName.decode("utf-8")
                            if fileName == "back":
                                print("client : back")
                                break
                            fileData = client_socket.recv(8000)
                            fileData = fileData.decode("utf-8")
                            uploadStart = time.time() 
                            myFile = open("{}_{}_clientUploadFile".format(fileName, uploadStart),"w",encoding="utf-8")
                            myFile.write(fileData)
                            myFile.close()
                            fileSize = sys.getsizeof(myFile.name)
                            index = putFile(myFile.name,uploadStart,index,fileSize)  
                            print("#파일 업로드 완료#\n")
                            Return = "#파일 업로드 완료#\n"    
                            client_socket.sendall(Return.encode("utf-8"))
                            break
                        except:
                            returnMsg = "잘못된 입력입니다. 다시 입력해주세요."
                            client_socket.sendall(returnMsg.encode("utf-8"))
                            print(returnMsg)
                    
                elif data[0]=='back':
                    msg = input("server : ") 
                    client_socket.sendall(msg.encode("utf-8"))

                    
            else:
                msg = input("server : ") 
                msg = "#명령어 입력 실패#\n{}".format(msg)
                client_socket.sendall(msg.encode("utf-8"))

    except Exception as err:
        print("err :",err)
    finally:
        print("##{} 클라이언트와 연결이 종료됨##".format(addr))
        print("")

#   /***********************
#    * Param: 메시지 내용과, 다운로드 시작한 시간, 인덱스를 가져옵니다.
#    * Description: 로그파일에 파일 경로, 파일 확장자, 파일 전송 소요 시간 추가를 하는 함수
#    * Return: 인덱스 값에 +1을 해서 클라이언트와 통신 중 몇번째 저장인지 기록합니다.
#    ************************/
def getFile(massage,downloadStart,index):
    datatime = dt.datetime.now()
    fileLocation = realpath(massage)
    path, ext = os.path.splitext(massage)
    downloadEnd = time.time()
    logFile = open("logFile_{}_{}_{}.txt".format(datatime.hour, datatime.minute, index),"w",encoding="utf-8")
    logFile.write("""다운로드 요청 시간 : {}\n파일 경로 : {}\n파일 확장자 : {}\n파일 전송 소요 시간 : {}\n""".format(datatime,fileLocation,ext,downloadEnd-downloadStart))
    return index+1


#   /***********************
#    * Param: 파일 이름, 다운로드 시작한 시간, 인덱스, 파일 크기를 가져옵니다.
#    * Description: 업로드 요청 시간, 파일 크기, 파일 확장자, 파일 업로드 소요 시간을 추가를 하는 함수
#    * Return: 인덱스 값에 +1을 해서 클라이언트와 통신 중 몇번째 저장인지 기록합니다.
#    ************************/
def putFile(fileName,uploadStart,index,fileSize):
    print("fileName :",fileName)
    datatime = dt.datetime.now()
    path, ext = os.path.splitext(fileName)
    uploadEnd = time.time()
    logFile = open("logFile_{}_{}_{}.txt".format(datatime.hour, datatime.minute, index),"w",encoding="utf-8")
    logFile.write("""업로드  요청 시간 : {}\n파일 크기 : {}\n파일 확장자 : {}\n파일 업로드 소요 시간 : {}\n""".format(datatime,fileSize,ext,uploadEnd-uploadStart))
    return index+1

orderList=["help","cd","lcd","ls","get","put","quit"] 
orderList = """help : 명령어 재출력
cd   : 서버CWD변경                   lcd  : client의CWD변경
ls   : 서버의CWD파일목록 디스플레이  myls : 클라이언트의 CWD파일목록 디스플레이
put  : 지정파일업로드                get  : 지정파일다운로드
back : 뒤로가기                     quit  : 서버의 연결해제 후 종료\n
## 명령어만 입력해주시면 서버에서 안내합니다. ##
## 명령어 인식 오류 시 서버가 1대1채팅으로 인식합니다. ##"""                  


print("server 실행")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
server_socket.bind(('', 9999));
server_socket.listen();

try:
  while True:
      client_socket, addr = server_socket.accept();
      print("<",addr,"클라이언트 연결을 요청 >")
      th = threading.Thread(target=binder, args = (client_socket,addr));
      th.start();
except:
  print("except");
finally:
  server_socket.close();