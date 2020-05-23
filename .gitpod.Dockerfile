FROM debian:sid-slim
                    
USER gitpod

RUN sudo apt-get update -y
RUN sudo apt-get install python3-dev python3-pip
