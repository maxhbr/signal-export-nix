FROM python:3.12.2-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/usr/local/lib
WORKDIR /app

RUN apt-get update && \
    apt-get install -y git gcc libsqlite3-dev tclsh libssl-dev libc6-dev make

RUN git clone --depth=1 --branch=master https://github.com/sqlcipher/sqlcipher.git && \
  cd sqlcipher && \
  ./configure --enable-tempstore=yes \
    CFLAGS="-DSQLITE_HAS_CODEC" LDFLAGS="-lcrypto -lsqlite3" && \
  make && \
  make install

COPY requirements.lock ./
RUN sed -i '/^-e file:/d' requirements.lock
RUN pip install -r requirements.lock

COPY . .
RUN --mount=source=.git,target=.git,type=bind pip install --no-cache-dir .

ENTRYPOINT ["sigexport", "--source=/Signal"]
CMD ["--print-data"]
