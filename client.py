import socket
import datetime as dt
import os
HOST = '127.0.0.1'  
PORT = 9999 

orderList = """help : 명령어 재출력
cd   : 서버CWD변경                   lcd  : client의CWD변경
ls   : 서버의CWD파일목록 디스플레이  myls : 클라이언트의 CWD파일목록 디스플레이
put  : 지정파일업로드                get  : 지정파일다운로드
back : 뒤로가기                     quit  : 서버의 연결해제 후 종료\n
## 명령어만 입력해주시면 서버에서 안내합니다. ##
## 명령어 인식 오류 시 서버가 1대1채팅으로 인식합니다. ##"""                  

print("")
print("<푸름 소캣통신 명령어 리스트>")      
print(orderList)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

while True:
      #메시지 입력 후 서버로 전송
      print("")
      msg = input("client : ") 
      print("")
      print("     ##################################")
      print("     #...서버의 응답을 기다려주세요...#")
      print("     ##################################")
      print("")
      
      #########################
      #프로세스 종료를 위한 부분#
      #########################
      if msg == "quit": 
            print("#실행 종료#")
            quit()
      
      #####################################################
      # 추가한 기능인 myls을 명령하면 본인 CWD 파일 목록 출력#
      #####################################################   
      elif msg == "myls":
            print("##클라이언트의 CWD 파일 목록 출력 명령 ##\n")
            fileList = os.listdir(os.getcwd())
            print('myfileList : {}'.format(fileList))
            continue
      
      ##########################
      # 나의 CWD 변경 명령 부분 #
      ##########################
      elif msg == "lcd":
            print("##클라이언트의 CWD 변경 명령##")
            nowLocation = os.getcwd()
            nowLocation = "현재 위치 ["+ nowLocation + "]"  
            print(nowLocation)
            print("")
            while True:
                  try:
                        data = input("#변경위치를 입력해주세요# : ")
                        os.chdir(data)
                        nowLocation = os.getcwd()
                        nowLocation = "\n#변경 완료#\n현재 위치 : "+ nowLocation  
                        print(nowLocation)
                        break
                  except:
                        print("잘못입력하셨습니다.")
            continue

      client_socket.sendall(msg.encode('utf-8'))
      data = client_socket.recv(1024)
      print('sever :',data.decode('utf-8'))
      
      ##########################################
      # 서버에서 put 응답이 올 경우 여기서 처리함 #
      # 버퍼 크기를 8000바이트로 제한하였습니다.  #
      ##########################################
      if data.decode("utf-8") == "#파일 업로드 대기중. 파일 이름을 입력해 주세요.(뒤로가기 : back)#":
            while True:
                  try:
                        fileList = os.listdir(os.getcwd()) 
                        notDirecList = fileList[:]
                        for file in fileList:
                              if os.path.isdir(file)==True:
                                    notDirecList.remove(file)
                              
                        print("# 현재 있는 파일 목록 : {} #".format(notDirecList))
                        fileName = input("8000바이트 이하의 파일 이름 (뒤로가기:back) : ")
                        
                        if fileName == "back":
                              data = "back"
                              client_socket.sendall(data.encode('utf-8'))
                              break

                        myFile = open(fileName,"r",encoding="utf-8")
                        returnFile = ""
                        while True:
                              line = myFile.readline()
                              if not line: break
                              returnFile+=line       
                        client_socket.sendall(fileName.encode("utf-8"))
                        client_socket.sendall(returnFile.encode("utf-8"))
                        print("#파일 전송 완료#")
                        data = client_socket.recv(1024)
                        
                        if data.decode('utf-8') == "잘못된 입력입니다. 다시 입력해주세요.":
                              print("# err입니다 다시 입력해주세요 #")
                              continue
                        
                        print('sever :',data.decode('utf-8'))
                        break
                  except:
                        print("파일을 찾을 수 없습니다. 다시 입력해 주세요.(뒤로가기 : back)")
                        print("")
            
