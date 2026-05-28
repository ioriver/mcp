FROM python:3.12-alpine3.21 AS base

ENV APP_HOME /app

WORKDIR $APP_HOME

# Install pipenv
RUN pip install pipenv

# Copy source
COPY . $APP_HOME/
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --system --deploy

ENV PORT=3000
EXPOSE 3000

CMD ["python", "src/main.py"]
