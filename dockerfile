FROM python:3.9

RUN pip install --upgrade pip

# Install requirements
WORKDIR /home/app
COPY shinyapp/requirements.txt ./
RUN pip install -r requirements.txt

# Copy the app
WORKDIR /home/app
COPY shinyapp .

# Add user an change working directory and user
RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /home/app
RUN chown app:app -R /home/app
USER app

# Run app on port 8080
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]