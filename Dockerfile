FROM python:3.9

RUN echo $WORKDIR

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "github_lambda.py"]