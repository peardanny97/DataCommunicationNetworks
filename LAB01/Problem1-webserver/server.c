#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <string.h>

#include <sys/select.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>

#include "base64.c"

#define PORT 25000 // You can change port number here

int respond (int sock);
int authorization (int sock, char *token);
char usrname[] = "2017-11621";
//char usrname[] = "username";
char password[] = "password";
#include <stdint.h>
#include <stdlib.h>

#include <string.h>


//Problem 1 of project 1:simple webserver with authentification
//Both Problem 1 and 2 was tested on WSL enviroments, Linux, and M1 mac
//But If you still have problems on running codes please mail us
//Most importantly please comment your code

//If you are using mac
//You can install homebrew here :https://brew.sh
//And open terminal and type
//sudo brew install gcc
//sudo brew install make
//Type make command to build server
//And server binary will be created
//Use ifconfig command to figure out your ip(usually start with 192. or 172.)
//run server with ./server and open browser and type 192.x.x.x:25000



//If you are using Linux or WSL
//You just need to run "make"(If you are using WSL you may need to install gcc and make with apt)
//And server binary will be created
//Use ifconfig command to figure out your ip(usually start with 192. or 172.)
//run server with ./server and open browser and type 192.x.x.x:25000


//It will be better if you run virtual machine or other device to run server
//But you can also test server with opening terminal and run it on local IP

void sendMessage(int sock, char* message) {
  int length = strlen(message);
  int bytes;
  while(length > 0) {
    bytes = send(sock, message, length, 0);
    length = length - bytes;
  }
}

void checkExtension(char* extension, char* HTTP_CONTENT) {
  if(strcmp(extension, "html") == 0)
    strcpy(HTTP_CONTENT, "Content-Type: text/html;");
  else if(strcmp(extension, "png") == 0)
    strcpy(HTTP_CONTENT, "Content-Type: image/png;");
  else if(strcmp(extension, "css") == 0)
    strcpy(HTTP_CONTENT, "Content-Type: text/css;");
  else if(strcmp(extension, "js") == 0)
    strcpy(HTTP_CONTENT, "Content-Type: text/js;");
  else{
    printf("error\n");
    return;
  }
  printf("HTTP_CONTENT is %s\n",HTTP_CONTENT);
}


int main( int argc, char *argv[] ) {
  int sockfd, newsockfd, portno = PORT;
  socklen_t clilen;
  struct sockaddr_in serv_addr, cli_addr;
  clilen = sizeof(cli_addr);

  printf("encoding start \n");// We have implemented base64 encoding you just need to use this function
  char *token = base64_encode("2017-11621:password", strlen("2017-11621:password"));//you can change your userid
  printf("encoding end \n");

  //browser will repond with base64 encoded "userid:password" string
  //You should parse authentification information from http 401 responese and compare it


  /* First call to socket() function */
  sockfd = socket(AF_INET, SOCK_STREAM, 0);

  if (sockfd < 0) {
    perror("ERROR opening socket");
    exit(1);
  }

  // port reusable
  int tr = 1;
  if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &tr, sizeof(int)) == -1) {
    perror("setsockopt");
    exit(1);
  }

  /* Initialize socket structure */
  bzero((char *) &serv_addr, sizeof(serv_addr));
  serv_addr.sin_family = AF_INET;
  serv_addr.sin_addr.s_addr = INADDR_ANY;
  serv_addr.sin_port = htons(portno);

  /* TODO : Now bind the host address using bind() call. 10% of score*/
  if ( bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1 ){
    perror("bind error");
    exit(1);
  }
    //it was mostly same as tutorial

  /* TODO : listen on socket you created  10% of score*/
  if ( listen(sockfd, 10) == -1 ){
    perror("listen error");
    exit(1);
  }


  printf("Server is running on port %d\n", portno);

    //it was mostly same as tutorial
    //in the while loop every time request comes we respond with respond function if valid

    //TODO: authentication loop 40 % of score
    while(1){
      newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
      if ( newsockfd == -1 ){
        perror("accept error");
        exit(1);
       }
      if(authorization(newsockfd, token)) break;
      //TODO: accept connection
      //TODO: send 401 message(more information about 401 message : https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication) and authentificate user
      //close connection


    }
    //Respond loop
    while (1) {
        newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
        if ( newsockfd == -1 ){
          perror("accept error");
          exit(1);
        }
        //printf("test");
        respond(newsockfd);
      }

  return 0;
}

int authorization(int sock, char *token){
  int offset, bytes;
  char buffer[9000];
  bzero(buffer,9000);

  offset = 0;
  bytes = 0;
  do {
    // bytes < 0 : unexpected error
    // bytes == 0 : client closed connection
    bytes = recv(sock, buffer + offset, 1500, 0);
    offset += bytes;
    // this is end of http request
    if (strncmp(buffer + offset - 4, "\r\n\r\n", 4) == 0) break;
  } while (bytes > 0);

  if (bytes < 0) {
    printf("recv() error\n");
    return 0;
  } else if (bytes == 0) {
    printf("Client disconnected unexpectedly\n");
    return 0;
  }
  buffer[offset] = 0;
  printf("buffer is: %s\n", buffer);
  char *auth_ptr = strstr(buffer, "Authorization");
  char auth_key[100];
  //first if there's no authorization key, send 401 message
  if(!auth_ptr){
    char message[] = "HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm=\"Access to the staging site\"\r\n\r\n";
    sendMessage(sock, message);
  }
  if(auth_ptr){
    char *auth_end = strstr(auth_ptr, "\r\n");
    strncpy(auth_key, auth_ptr+21, auth_end-auth_ptr-21);
    //auth key is valid. return 1
    if(strcmp(auth_key, token)==0){
      shutdown(sock, SHUT_RDWR);
      close(sock);
      return 1;
    }
    //auth key is not valid, keeps sending 401 message
    else{
      char message[] = "HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm=\"Access to the staging site\"\r\n\r\n";
      sendMessage(sock, message);
    }
  }
  shutdown(sock, SHUT_RDWR);
  close(sock);
  return 0;
}

//TODO: complete respond function 40% of score
int respond(int sock) {
  int offset, bytes;
  char buffer[9000];
  bzero(buffer,9000);

  offset = 0;
  bytes = 0;
  do {
    // bytes < 0 : unexpected error
    // bytes == 0 : client closed connection
    bytes = recv(sock, buffer + offset, 1500, 0);
    offset += bytes;
    // this is end of http request
    if (strncmp(buffer + offset - 4, "\r\n\r\n", 4) == 0) break;
  } while (bytes > 0);

  if (bytes < 0) {
    printf("recv() error\n");
    return 0;
  } else if (bytes == 0) {
    printf("Client disconnected unexpectedly\n");
    return 0;
  }

  buffer[offset] = 0;
  printf("buffer is: %s\n", buffer);

  int method_idx = 0;
  int next_start = 0;
  char METHOD[10]; // get method from http hdr
  bzero(METHOD,10);
  for (int i=0; i<9000; i++){
    if(buffer[i]==' '){
      next_start = i+1;
      break;
    }
    METHOD[method_idx] = buffer[i];
    method_idx++;
  }
  printf("method is %s\n",METHOD);

  int path_idx = 0;
  char path[1000];  // get path from http hdr
  bzero(path,1000);
  for (int i=next_start; i<9000; i++){
    if(buffer[i]==' '){
      next_start = i+1;
      break;
    }
    path[path_idx] = buffer[i];
    path_idx++;
  }
  printf("path is %s\n",path);
  // basic case change to /index.html
  if(strcmp(path,"/")==0){
    strcpy(path,"/index.html");
  }

  int ext_idx = 0;
  char extension[10];  // get extension from path
  bzero(extension,10);
  for (int i=0; i<strlen(path); i++){
    if(path[i]=='.'){  // extension will be .xxx
      next_start = i+1;
      break;
    }
  }
  for (int i=next_start; i<strlen(path); i++){
    extension[ext_idx] = path[i];
    ext_idx++;
  }
  printf("extension is %s, length is %lu\n",extension, strlen(extension));

  /*
     now we have method, path, extension
     to use this information we need to make HTTP HDR
     make HTTP response
  */
  char HTTP_CONTENT[50];
  bzero(HTTP_CONTENT, 50);

  checkExtension(extension, HTTP_CONTENT);

  char HTTP_HDR[200];
  bzero(HTTP_HDR, 200);


  char file_path[100];
  bzero(file_path, 100);
  snprintf(file_path, sizeof(file_path), ".%s", path);
  printf("file path is %s\n",file_path);

  FILE *file = fopen(file_path, "rb");
  /* if requested file is not present, response with 404 error */
  if(!file){
    printf("ERROR: file is empty!\n");
    char message[] = "HTTP/1.1 404 Not Found\r\n\r\n";
    sendMessage(sock, message);
    shutdown(sock, SHUT_RDWR);
    close(sock);
    return 0;
  }


  sprintf(HTTP_HDR,"HTTP/1.1 200 OK\r\n%s\r\n\r\n",HTTP_CONTENT);
  /* send HTTP_HDR */
  sendMessage(sock, HTTP_HDR);
  /*
    file can be big!(for this case png)
    divide file by block with size 9000
    send all of block until eof
  */
  char HTTP_BLOCK[9000];

  while(!feof(file)){
    int cur_size = fread(HTTP_BLOCK, 1, 9000, file);
    send(sock, HTTP_BLOCK, cur_size, 0);
    bzero(HTTP_BLOCK, 9000);
  }
  sendMessage(sock, "\r\n\r\n");
  fclose(file);

  shutdown(sock, SHUT_RDWR);
  close(sock);

  return 0;
}

