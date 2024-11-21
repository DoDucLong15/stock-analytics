# Sử dụng image Python cơ bản
FROM python:latest

# Cài đặt các package cần thiết
RUN pip3 install requests
RUN pip3 install pandas
RUN pip3 install plotly==5.3.1
RUN pip3 install retrying==1.3.3
RUN pip3 install confluent-kafka
RUN pip3 install vnstock
RUN pip3 install beautifulsoup4
RUN pip3 install packaging
RUN pip3 install ipython

# Copy file Python của bạn vào container
COPY ./crawl.py /app/crawler.py

# Chạy file Python khi container được khởi động
CMD ["bash", "-c", "python /app/crawler.py && tail -f /dev/null"]