FROM  mcr.microsoft.com/playwright:v1.25.0-focal

RUN apt update
RUN apt install -y make python3 python3-venv python3-pip
