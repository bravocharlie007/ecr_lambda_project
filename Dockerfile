#FROM python:3.9


FROM public.ecr.aws/lambda/python:3.8

RUN echo $WORKDIR

#COPY requirements.txt .

COPY build/ .

#RUN pip install -r requirements.txt

RUN pip3 install -r requirements.txt

CMD ["python", "github_lambda.py"]