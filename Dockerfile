FROM joyzoursky/python-chromedriver:3.7-selenium

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install the dependencies
RUN pip install -r requirements.txt

# Run the program
CMD ["python3", "-u", "main.py"]
