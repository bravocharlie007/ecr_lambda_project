FROM python:3.9

RUN echo $WORKDIR

#COPY requirements.txt .

COPY build/ .

RUN pip install -r requirements.txt

CMD ["python", "github_lambda.py"]