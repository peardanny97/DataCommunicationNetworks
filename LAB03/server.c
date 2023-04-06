#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <string.h>

#define PORT 7777
#define BUFFER_SIZE 1000000

void forward (int sock);
int send_all(int socket, void *buffer, size_t size);

int main( int argc, char *argv[] ) {
  int sockfd, newsockfd, portno = PORT;
  socklen_t clilen;
  struct sockaddr_in serv_addr, cli_addr;
  clilen = sizeof(cli_addr);

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
  
  /* Now bind the host address using bind() call.*/
  if ( bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1 ){
    perror("bind error");
    exit(1);
  }

  /* listen on socket you created */
  if ( listen(sockfd, 10) == -1 ){
    perror("listen error");
    exit(1);
  }

  printf("Server is running on port %d\n", portno);

  while (1) {
    newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
    
    if ( newsockfd == -1 ){
      perror("accept error");
      exit(1);
    }
    forward(newsockfd);
  }

  return 0;
}

/* 
  TODO (1): Forward received HTTP request to the web server
      Hint 1:
          The HTTP request has a hostname in the path. 
          Take the IP address with the hostname and open a socket with the address.
          (use gethostbyname() function)
      
      Hint 2:
          You should modify the path in the request header before forwarding it to a web sever.
          ex) "GET http://snu.nxclab.org:9000/index.html HTTP/1.1" -> "GET /index.html HTTP/1.1"

  TODO (2): Receive responses from the web server and forward them to the browser
  TODO (3): Modify HTML before forwarding response message to browser.
            Replace 20xx-xxxxx to your student id (ex. 20xx-xxxxx --> 2012-34567)
            And change the order of image displayed in browser
      
 */
void forward(int sock) {
  int offset, bytes;
  char buffer[9000];
  bzero(buffer,9000);

  offset = 0;
  bytes = 0;
  do {
    bytes = recv(sock, buffer + offset, 1500, 0);
    offset += bytes;
    
    if (strncmp(buffer + offset - 4, "\r\n\r\n", 4) == 0) break;
  } while (bytes > 0);

  if (offset < 0) {
    printf("recv() error\n");
    return;
  } else if (bytes == 0) {
    printf("Client disconnected unexpectedly\n");
    return;
  }
  
  printf("-----------------------------------\n");
  printf("%s\n", buffer);

  /* TODO (1): Forward received HTTP request to the web server */
  char* tmp = NULL;
  char requestLine[2000] = {0};
  char httpContent[2000] = {0};
  int first=0;
  tmp = strtok(buffer, "\r\n");
  while (tmp != NULL){
      if(first == 0){
        strcpy(requestLine, tmp);
        first = 1;
      }
      else{
        char *aptr;
        if((aptr = strstr(tmp,"Accept-Encoding:"))){
          strcat(httpContent, "Accept-Encoding: identity\r\n");
        }
        else{
          strcat(httpContent, tmp);
          strcat(httpContent,"\r\n");
        }

      }
      tmp = strtok(NULL,"\r\n");
  }

  char method[100];
  char uri[1000];
  char version[1000];
  // ex) GET http://snu.nxclab.org:9000/ HTTP/1.1
  sscanf(requestLine, "%s %s %s", method, uri, version);

  if(strcmp(method,"GET")!=0) return;

  char hostname[100];
  char path[100];
  int port;

  char *url = strstr(uri, "http://");
  if(url) {
    url += 7;  //subtract http:// part
    sscanf(url, "%[^:]:%i%s", hostname, &port, path);
  }

  char requestHttp[3000];
  sprintf(requestHttp,"%s %s %s\r\n", method, path, version);
  strcat(requestHttp, httpContent);
  strcat(requestHttp, "\r\n\r\n");


  //printf("request is\n%s\n",requestHttp);

  /* TODO (2): Receive responses from the web server and forward them to the browser */

  struct hostent *host_entry;
  host_entry = gethostbyname(hostname);
  if(!host_entry){
    printf("gethostbyname Failed\n");
  }

  struct sockaddr_in hostaddr;
  hostaddr.sin_family = AF_INET;
  memcpy(&hostaddr.sin_addr, host_entry->h_addr_list[0], host_entry->h_length);
  hostaddr.sin_port = htons(port);
  int hostSocket = socket(AF_INET, SOCK_STREAM, 0);

  /* need to connect to host */
  if(connect(hostSocket, (struct sockaddr *)&hostaddr, sizeof(hostaddr)) < 0){
    printf("Connect error\n");
    return;
  }

  if (write(hostSocket, requestHttp, strlen(requestHttp)+1) < 0){
    printf("Send request error\n");
  }
  char reply[BUFFER_SIZE];
  bzero(reply,BUFFER_SIZE);

  offset = 0;
  bytes = 0;
  do {
    bytes = recv(hostSocket, reply + offset, 1500, 0);
    offset += bytes;
    if (strncmp(reply + offset - 4, "\r\n\r\n", 4) == 0){
        break;
    }
  } while (bytes > 0);

  /* TODO (3): Modify HTML before forwarding response message to browser.
            Replace 20xx-xxxxx to your student id (ex. 20xx-xxxxx --> 2012-34567)
            And change the order of image displayed in browser */

  /* change 20xx-xxxxx to 2017-11621 */
  char *IDptr = strstr(reply, "20xx-");
  if(IDptr){
    strncpy(IDptr, "2017-11621",10);
  }
  /* change image 1 and image 2 */
  char *pic1p = strstr(reply, "image1.jpg");
  char *pic2p = strstr(reply, "image2.jpg");
  if(pic1p && pic2p){
    strncpy(pic1p, "image2.jpg",10);
    strncpy(pic2p, "image1.jpg",10);
  }
  printf("new reply is \n%s\n\n",reply);

  while(offset > 0){
    bytes = send(sock, reply, offset, 0);
    offset -= bytes;
  }
  close(hostSocket);
  close(sock);

  return;

}

